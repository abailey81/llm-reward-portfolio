"""Write RUN 4's ``campaign_summary.json`` THROUGH the campaign machinery, at teardown.

WHY THIS EXISTS
---------------
``scripts/run_campaign_cluster.py`` writes ``campaign_summary.json`` only when a line RETURNS
NORMALLY — and deliberately not at the C3 review stop, where a watcher would misread the file as
"campaign done" (its docstring says so). RUN 4's twelve lines are supervised and relaunched with
``--resume``; the campaign ends on an EXOGENOUS stop, not on ``run_campaign_tiered`` returning. So
the most likely ending is the one that writes no summary at all.

WHAT IS LOST IF IT IS MISSING (found by the analysis lane, M166, and confirmed here first-hand):
``scripts/analyze_campaign.py`` populates ``panel`` / ``cfg`` / ``test_window`` / ``winner_n_trials``
ONLY by reading that file, and FOUR registered outputs sit inside the resulting ``panel is not None``
block — ``benchmark_floor`` (the DeMiguel 1/N floor, i.e. the "nine published allocators, one costed
environment" table ALREADY WIRED INTO THE PDF), ``attribution``, ``h2_rf_robustness`` and
``regime_stratified``. They cannot be back-computed once the archive is torn down and the
panel/test-window provenance is gone.

WHY IT IS NOT HAND-AUTHORED
---------------------------
The summary carries ``test_window``. A wrong window makes the analysis silently score the benchmark
floor on the WRONG SLICE, which is strictly worse than having no floor at all. So this script does
not compose a summary: it calls ``assemble_cluster_inputs`` and ``_write_campaign_summary`` — the
same two functions the driver calls, with the same flags parsed by the same parser — so the windows
and the gold-panel provenance are derived by the identical code path. Nothing here restates a value
the campaign already knows how to compute.

WHEN TO RUN IT
--------------
AT TEARDOWN, after the lines have stopped and BEFORE the archive is disturbed — and only if no
``campaign_summary.json`` exists. Running it mid-campaign is REFUSED unless ``--i-know-it-is-live``
is passed, for two reasons: the watcher keys terminal state off this file, and
``_write_campaign_summary`` seals the archive as a side effect (``archive_integrity.write_manifest``),
which is correct at teardown and misleading before it.

The record it writes is honest about its own provenance: ``written_by`` marks it post-hoc and
``all_arms_tested`` is ``null`` — NOT ``false``, which would assert a completion status this script
has no standing to determine. Zero, false and absent are three different values.

    python docs/ops/write_campaign_summary.py --dry-run                     # print, write nothing
    python docs/ops/write_campaign_summary.py --output-dir <scratch>        # rehearse elsewhere
    python docs/ops/write_campaign_summary.py --i-know-it-is-live           # the real teardown write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import run_campaign_cluster as rcc  # noqa: E402

#: The core line's own invocation, read off the live process table 2026-08-01T12:38Z. Only the
#: arguments that reach `assemble_cluster_inputs` matter here; the cluster/ssh flags do not affect
#: the summary. Kept as a literal so a reviewer can diff it against the running command line.
CORE_LINE_ARGS = ["--tiered", "--pass-mode", "B", "--llm-from", "campaign",
                  "--output-dir", "outputs/campaign_cluster_run4"]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--output-dir", default=None,
                    help="override the archive root (use a scratch path to rehearse)")
    ap.add_argument("--dry-run", action="store_true", help="print the summary; write nothing")
    ap.add_argument("--i-know-it-is-live", action="store_true",
                    help="permit a write into an archive whose drivers are still running")
    ap.add_argument("--reason", default="post-hoc: the campaign ended by exogenous stop, so no "
                                        "line returned normally to write one",
                    help="recorded in the summary as written_by.reason")
    args = ap.parse_args(argv)

    driver_args = rcc.build_parser().parse_args(CORE_LINE_ARGS)
    _resolve_design_defaults(driver_args)
    if args.output_dir:
        driver_args.output_dir = args.output_dir
    out_dir = Path(driver_args.output_dir)
    target = out_dir / "campaign_summary.json"

    if target.exists():
        print(f"[summary] REFUSING: {target} already exists — the campaign wrote its own. "
              f"Nothing to recover.", file=sys.stderr)
        return 1

    live = _drivers_running()
    if live and not (args.dry_run or args.i_know_it_is_live or args.output_dir):
        print(f"[summary] REFUSING: {live} campaign driver(s) are still running. This file is the "
              f"watcher's terminal-state sentinel and writing it now would report a campaign that "
              f"has not finished; the write also SEALS the archive. Re-run at teardown, or pass "
              f"--output-dir <scratch> to rehearse, or --i-know-it-is-live if you mean it.",
              file=sys.stderr)
        return 2

    inputs = rcc.assemble_cluster_inputs(
        arms=list(driver_args.arms or []), seeds=rcc._parse_seeds(driver_args.seeds),
        output_dir=driver_args.output_dir, synthetic=bool(driver_args.synthetic),
        train_steps=driver_args.train_steps, n_trials=driver_args.n_trials,
        candidates=driver_args.candidates, generations=driver_args.generations,
        search_seed=driver_args.search_seed, embargo=driver_args.embargo,
        pass_mode=driver_args.pass_mode, provider=driver_args.provider, llm_cfg=None,
        resume=True,
    )
    train_w, val_w, test_w = inputs["windows"]
    print("[summary] derived windows THROUGH the campaign's own code path:")
    print(f"            train {train_w}")
    print(f"            val   {val_w}")
    print(f"            test  {test_w}")
    print(f"[summary] panel: {json.dumps(inputs['panel_descriptor'], default=str)}")
    _assert_registered_lengths(val_w, test_w)

    if args.dry_run:
        print("[summary] --dry-run: nothing written.")
        return 0

    # The freeze stamp is real provenance, so take it rather than record a null: enforce_freeze
    # reuses scripts/freeze.py's verify(), which performs NO WRITES, so this is a read even
    # mid-campaign. It raises if the design is not frozen or has drifted — which is exactly the
    # right behaviour here, because a summary is not worth writing for an un-attributable run.
    from run_campaign import enforce_freeze
    freeze_stamp = enforce_freeze(allow_unfrozen=False)
    print(f"[summary] freeze stamp: frozen={freeze_stamp.get('frozen')} "
          f"hash={str(freeze_stamp.get('freeze_hash'))[:12]}")

    rcc._write_campaign_summary(
        driver_args.output_dir, inputs, freeze_stamp=freeze_stamp,
        extra={
            "written_by": {"tool": "docs/ops/write_campaign_summary.py", "reason": args.reason},
            # null, NOT false: this script cannot determine completion, and asserting false would
            # be a claim it has no standing to make.
            "all_arms_tested": None,
            "exit_code": None,
        },
    )
    print(f"[summary] wrote {target}")
    return 0


#: The executed TEST length, registered in config/preregistration.yaml's N6 note ("MEASURED at the
#: executed test length T=1571") and independently confirmed against the live archive by the
#: analysis lane. A cross-check on the window this tool derives, never an input to it.
REGISTERED_TEST_SESSIONS = 1571
#: The VALIDATION length. src/inference/power_analysis.VALIDATION_TRACK_LENGTH, and the track length
#: at which the registered SESOI-to-Sharpe map is defined — the number the A16 margin turns on. It
#: is checked here because this is the one place the executed windows are re-derived end to end.
REGISTERED_VAL_SESSIONS = 694


def _resolve_design_defaults(driver_args: argparse.Namespace) -> None:
    """Fill the None design values from config, mirroring run_campaign_cluster.main().

    ⚠ This is the ONE piece of driver logic this tool has to restate, because the resolution block
    lives inline in ``main()`` rather than in a callable. It reads the SAME config keys — the freeze
    hash binds those files, so config-read is the frozen truth — and only ``embargo`` actually
    reaches the summary (through ``resolve_windows``). The restatement is then CHECKED rather than
    trusted: ``_assert_registered_test_length`` refuses to write a summary whose test window does
    not contain exactly the registered number of sessions, so a drifted default cannot silently
    produce a summary that scores the benchmark floor on the wrong slice.
    """
    from src.utils.config import cfg_get, load_config

    camp = load_config("campaign")
    if driver_args.candidates is None:
        driver_args.candidates = int(cfg_get(camp, "candidates_per_arm", 0) or 0)
    if driver_args.generations is None:
        driver_args.generations = int(cfg_get(cfg_get(camp, "llm", {}) or {}, "generations", 1) or 1)
    if driver_args.n_trials is None:
        driver_args.n_trials = int(driver_args.candidates)
    if driver_args.embargo is None:
        driver_args.embargo = int(cfg_get(cfg_get(load_config("inference"), "splits", {}) or {},
                                          "embargo_trading_days", 21))
    print(f"[summary] design values resolved from config: candidates={driver_args.candidates} "
          f"generations={driver_args.generations} n_trials={driver_args.n_trials} "
          f"embargo={driver_args.embargo}")


def _assert_registered_lengths(val_window: object, test_window: object) -> None:
    """Refuse to write unless the derived windows have the registered lengths.

    ``resolve_windows`` returns half-open (start, end) PANEL-ROW INDICES, not dates, so the session
    count is exact arithmetic rather than a date-range query — no calendar assumption enters.

    A wrong ``test_window`` is the one failure mode WORSE than a missing summary: the analysis would
    score the DeMiguel floor on the wrong slice and say nothing at all. The validation length is
    checked alongside it because the same derivation produces both, and because 694 is the track
    length the registered SESOI-to-Sharpe conversion is defined at — if this tool's restated
    defaults ever drift, both numbers move together and both are caught here.
    """
    n_val = int(val_window[1]) - int(val_window[0])    # type: ignore[index]
    n_test = int(test_window[1]) - int(test_window[0])  # type: ignore[index]
    bad = []
    if n_test != REGISTERED_TEST_SESSIONS:
        bad.append(f"test {n_test} != registered {REGISTERED_TEST_SESSIONS}")
    if n_val != REGISTERED_VAL_SESSIONS:
        bad.append(f"validation {n_val} != registered {REGISTERED_VAL_SESSIONS}")
    if bad:
        raise SystemExit(
            "[summary] REFUSING TO WRITE — derived window length(s) do not match the registration: "
            + "; ".join(bad) + ". A summary carrying a wrong window makes the analysis score the "
            "benchmark floor on the WRONG SLICE, silently. Resolve the discrepancy first.")
    print(f"[summary] CROSS-CHECK PASSED: validation {n_val} sessions, test {n_test} sessions — "
          f"both match the registration.")


def _drivers_running() -> int:
    """Count live ``run_campaign_cluster`` processes; -1 when the count cannot be taken.

    A count that could not be taken must not read as zero, so it is returned as -1 and treated by
    the caller as "assume live".
    """
    try:
        import subprocess
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "@(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
             "Where-Object { $_.CommandLine -like '*run_campaign_cluster*' }).Count"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
        return int(out.stdout.strip())
    except Exception as exc:  # noqa: BLE001
        print(f"[summary] could not count drivers ({type(exc).__name__}: {exc}); assuming LIVE",
              file=sys.stderr)
        return -1


if __name__ == "__main__":
    raise SystemExit(main())
