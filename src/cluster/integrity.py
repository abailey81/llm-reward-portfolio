"""The EFFECT-BLIND integrity report for the C3 review gate (PLAN §13: "counts-only monitoring;
single-look discipline"; control cascade §13.3 "effect-blind by construction").

Tamer's review checkpoint between the all-arms n=30 design floor (C3) and the uniform-n sweep (C4)
must NOT look at results — conditioning continuation on observed effects is optional stopping and
would invalidate the pre-registered single-look inference. What it CAN (and should) verify, very
carefully, is EXECUTION: did every unit train, complete, and archive exactly as designed?

This module writes that report: completeness counts (search candidates vs the matched budget,
k-seed integrity, test seeds vs the core set), failure censuses (F5 ledgers), and homogeneity
censuses (device + env-fingerprint labels across the sealed leg). It NEVER reads ``val_fitness``,
``test_sharpe``, ``test_cvar05``, ``test_returns``, or ``tail_stats`` values — only presence.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

__all__ = ["write_integrity_report"]

_BLIND_HEADER = (
    "EFFECT-BLIND EXECUTION-INTEGRITY REPORT — contains NO performance statistics.\n"
    "Reviewing results before the sweep would be optional stopping (a forking path); this gate\n"
    "verifies EXECUTION only. The single confirmatory look stays at the pre-declared date.\n"
)


def _count_lines(path: Path) -> int:
    if not path.is_file():
        return 0
    return sum(1 for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip())


def _search_census(arm_root: Path, expected_candidates: int, k_seeds: int) -> dict[str, Any]:
    """Counts for one arm's SEARCH sub-root: records vs budget×k + the F5 failure ledger."""
    from src.io.results import load_all

    records = load_all(str(arm_root)) if arm_root.is_dir() else []
    n_records = len(records)
    n_failures = _count_lines(arm_root / "failures.jsonl")
    expected_records = expected_candidates * max(1, k_seeds)
    # Reflection-archival census (2026-07-12 upgrade; instrument (g) dies silently without it):
    # the funnel content analysis codes the designer's archived COMPLETIONS, so the gate counts
    # llm_calls rows and how many carry an EMPTY response — counts only, never the text itself
    # (effect-blind). A tail-fed arm with archived candidates but zero/empty completions is an
    # archival defect to fix before C4, not at the bank gate.
    llm_calls = 0
    empty_completions = 0
    calls_path = arm_root / "llm_calls.jsonl"
    if calls_path.is_file():
        for line in calls_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            llm_calls += 1
            try:
                if not str(json.loads(line).get("response", "")).strip():
                    empty_completions += 1
            except ValueError:
                empty_completions += 1  # a torn/unparseable row cannot be coded either
    return {
        "records": n_records,
        "ledgered_failures": n_failures,
        "expected_records": expected_records,
        "matched_budget_ok": (n_records + n_failures * max(1, k_seeds)) >= expected_records,
        "llm_calls_archived": llm_calls,
        "empty_completions": empty_completions,
        "reflection_archive_ok": llm_calls == 0 or empty_completions == 0,
    }


def _record_device(arm_root: Path, run_id: str) -> str:
    """The GPU model that trained this record, from its replayable ``env.json`` (S6).

    Source: ``env.json → nvidia_smi.gpus[0]`` (e.g. ``'550.127.05, Tesla V100-PCIE-32GB'`` →
    ``'Tesla V100-PCIE-32GB'``), else ``'<absent>'`` — which the CRN-consistency check treats as a
    WILDCARD (laptop/legacy records without a GPU capture must not fail the gate)."""
    try:
        env = json.loads((arm_root / run_id / "env.json").read_text(encoding="utf-8"))
        gpus = (env.get("nvidia_smi") or {}).get("gpus") or []
        if gpus:
            return str(gpus[0]).split(",", 1)[-1].strip()
    except (OSError, ValueError):
        pass
    return "<absent>"


def _test_census(arm_root: Path, arm: str, seeds: list[int]) -> dict[str, Any]:
    """Presence census for one unit's sealed-leg records at the given seeds (+ homogeneity fields)."""
    from src.io.results import load_all

    records = load_all(str(arm_root)) if arm_root.is_dir() else []
    have = {str(r.get("run_id")) for r in records}
    missing = [s for s in seeds if f"{arm}-s{s}" not in have]
    devices: dict[str, int] = {}
    env_labels: dict[str, int] = {}
    per_seed_device: dict[str, str] = {}
    popart_present = 0
    safe_default_total = 0
    for r in records:
        m = r.get("metrics", {}) or {}
        dev = str(m.get("device", "<absent>"))
        devices[dev] = devices.get(dev, 0) + 1
        fp = r.get("env_fingerprint")
        label = fp.get("label", "<dict>") if isinstance(fp, dict) else str(fp)[:60]
        if not isinstance(label, str):
            # 2026-07-13 audit (defense-in-depth for the run_one nested-dict bug, fixed at source):
            # a non-str label must never crash the gate — coerce deterministically instead.
            label = json.dumps(label, sort_keys=True, default=str)[:60]
        env_labels[label] = env_labels.get(label, 0) + 1
        if r.get("seed") is not None:
            per_seed_device[str(r["seed"])] = _record_device(arm_root, str(r.get("run_id")))
        if m.get("popart_scale") is not None:
            popart_present += 1
        if m.get("train_safe_default_count") is not None:
            safe_default_total += int(m["train_safe_default_count"])
    return {
        "present": len(seeds) - len(missing),
        "expected": len(seeds),
        "missing_seeds": missing[:25],
        "device_census": devices,
        "device_homogeneous": len([d for d in devices if d != "<absent>"]) <= 1,
        "per_seed_device": per_seed_device,
        "env_label_census": env_labels,
        "popart_scale_present": popart_present,
        "train_safe_default_total": safe_default_total,
    }


def write_integrity_report(
    run: Any,
    *,
    arms: list[str],
    h2_arms: list[str],
    baseline_names: list[str],
    core_seeds: list[int],
    opts_for: Callable[[str], dict],
    winners: dict[str, dict] | None = None,
    out_dir: str | Path | None = None,
) -> tuple[dict[str, Any], Path, Path]:
    """Write the effect-blind integrity report (JSON + MD) under ``out_dir`` (default: read_root).

    Returns ``(report, json_path, md_path)``. Every GATE check is a COUNT or a CENSUS — never a
    statistic of a performance metric — so the auto-proceed decision is effect-blind. When
    ``winners`` is given, an additional **SEALED-SAFE SELECTION** section carries each arm's chosen
    reward CODE (the authored source — the mechanism headline "does the fed tail change the code?"),
    which is sealed from the confirmatory test leg; it is DESCRIPTIVE and does NOT gate continuation.
    NO ``val_fitness``/``test_sharpe``/``test_cvar``/``tail_stats`` VALUE is ever written.
    """
    out_root = Path(out_dir) if out_dir is not None else Path(run.read_root)
    out_root.mkdir(parents=True, exist_ok=True)

    report: dict[str, Any] = {"blind": True, "core_n": len(core_seeds), "search": {}, "test": {}}
    for arm in arms:
        opts = opts_for(arm)
        k = max(1, int(opts.get("search_seeds_per_candidate", 1)))
        report["search"][arm] = _search_census(
            run.search_read() / arm, int(opts.get("candidates", 0)), k
        )
        report["test"][arm] = _test_census(run.test_read() / arm, arm, core_seeds)
    for nm in baseline_names:
        unit = f"baseline_{nm}"
        report["test"][unit] = _test_census(run.test_read() / unit, unit, core_seeds)

    all_complete = all(
        t["present"] == t["expected"] for t in report["test"].values()
    ) and all(s["matched_budget_ok"] for s in report["search"].values())
    all_homogeneous = all(t["device_homogeneous"] for t in report["test"].values())
    # CRN-pair device consistency (2026-07-12; implements the device-stratified seed-block
    # ratification, CHANGELOG [2026-07-11c]). Under seed-pool blocks a unit legitimately spans
    # devices, so per-UNIT homogeneity is the WRONG invariant — the paired inference needs every
    # unit at seed s on the SAME device class (the device then cancels in D_s). '<absent>' is a
    # wildcard. Single-pool runs satisfy this trivially, so the gate is strictly more correct.
    seed_devices: dict[str, set[str]] = {}
    for t in report["test"].values():
        for s, dev in t.get("per_seed_device", {}).items():
            if dev != "<absent>":
                seed_devices.setdefault(s, set()).add(dev)
    crn_violations = {s: sorted(devs) for s, devs in seed_devices.items() if len(devs) > 1}
    crn_consistent = not crn_violations
    report["verdict"] = {
        "all_units_complete": all_complete,
        "device_homogeneous_everywhere": all_homogeneous,  # informational under seed-pool blocks
        "crn_pair_device_consistent": crn_consistent,
        "crn_device_violations": dict(list(crn_violations.items())[:10]),
        # the GATE reads ONLY this — execution health, never a performance statistic
        "health_ok": bool(all_complete and crn_consistent),
        "h2_arms": h2_arms,
    }

    # SEALED-SAFE SELECTION (descriptive; NOT a gate input) — each arm's authored winner reward CODE,
    # which is sealed from the confirmatory test leg. This is the mechanism headline the reviewer
    # actually wants to see; it carries NO performance number.
    if winners:
        report["selection"] = {
            arm: {"winner_id": w.get("candidate_id"),
                  "reward_source": str(w.get("reward_source", ""))[:4000]}
            for arm, w in winners.items()
        }

    json_path = out_root / "tier1_integrity.json"
    json_path.write_text(json.dumps(report, indent=1, sort_keys=True), encoding="utf-8")

    lines = ["# Tier-1 (C3 design floor) integrity report", "", _BLIND_HEADER, ""]
    lines += [f"- core n = {len(core_seeds)} seeds; arms = {', '.join(arms)}",
              f"- ALL UNITS COMPLETE: **{all_complete}**",
              f"- DEVICE HOMOGENEOUS EVERYWHERE: **{all_homogeneous}**", "", "## Search", ""]
    lines += ["| arm | records | ledgered failures | expected | matched budget |",
              "|---|---|---|---|---|"]
    for arm, s in report["search"].items():
        lines.append(f"| {arm} | {s['records']} | {s['ledgered_failures']} | "
                     f"{s['expected_records']} | {'OK' if s['matched_budget_ok'] else 'SHORT'} |")
    lines += ["", "## Sealed test leg", "",
              "| unit | present/expected | missing | devices | popart | safe-defaults |",
              "|---|---|---|---|---|---|"]
    for unit, t in report["test"].items():
        lines.append(
            f"| {unit} | {t['present']}/{t['expected']} | {len(t['missing_seeds'])} | "
            f"{t['device_census']} | {t['popart_scale_present']} | {t['train_safe_default_total']} |")
    if winners:
        lines += ["", "## Selection (SEALED-SAFE — authored winner reward code; NOT a gate input)", ""]
        for arm, sel in report["selection"].items():
            lines += [f"### {arm} — winner `{sel['winner_id']}`", "", "```python",
                      sel["reward_source"], "```", ""]
    lines += ["", "Gate proceeds AUTOMATICALLY on green health (no manual wait). It stops only on a "
              "real execution problem, or when `--hold-at-gate` is set — then create `TIER1_APPROVED` "
              "next to this report and re-run with `--resume`."]
    md_path = out_root / "tier1_integrity.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report, json_path, md_path
