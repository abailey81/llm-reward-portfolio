#!/usr/bin/env python
"""EXECUTION-QUALITY REPORT -- how well did the campaign RUN? Nothing about what it FOUND.

* WHAT THIS IS, AND WHAT IT IS NOT.

This is the **quality-control appendix in instrument form** (RUN 21 s.11.3 target #4, and the report
Tamer was promised). Okhrati's D5 says rigour must be VISIBLE inside the document and must be
presented **analytically, never chronologically**: a 6,000-line execution record nobody reads scores
nothing, a scannable table of what the machine actually did scores. So every section below answers a
question of the form *did the campaign execute the registered protocol completely, and at what cost?*
-- completeness, holes, coverage, wall-clock, authoring reliability, program kinds, eligibility
exclusions, determinism evidence.

**IT IS A REPORT, NOT A GATE.** It exits 0 whatever it finds, so that it can be run on every pass
without ever becoming a thing that must be silenced. The ONLY non-zero exit is 2, "the archive could
not be read", because "looked at nothing" and "found nothing wrong" are different states and this
campaign has confused them before (P197/P213). If a section cannot be built from what exists it
prints **UNAVAILABLE** with the reason, and never an approximation.

*** THE BLINDNESS CONSTRAINT IS THE POINT OF THIS FILE.

The sealed 2020-2026 test window is a pre-registered confirmatory window and the campaign is LIVE.
Reading an arm's outcome level here would be a forking path on a frozen registration. So this file
**never reads, prints, returns or compares** `test_returns`, `val_returns`, a Sharpe, a CVaR, a
fitness, a p-value, or any per-arm outcome. It reads directory names, counts, error strings, exit
codes, durations, source code, two execution counters and one content hash.

`_assert_blind()` PROVES that over this file's own AST rather than promising it in prose, and the
proof is deliberately built the way `docs/analysis/loader_collision_watch.py` built its own, for the
reason recorded there: **a naive substring scan of this file's source FALSE-FIRES on the explanatory
prose above** -- the words `test_returns` and `val_fitness` appear in this docstring, which the file
PRINTS, and a first version of that detector raised a breach on a run that had opened nothing. The
property to check is not *does the word appear* but *is an outcome key ever LOOKED UP*. So the guard
walks the AST and collects every string used as a `.get(...)` argument or a `[...]` subscript, plus
every JSON-key BYTE literal (this file's sealed-tier pass extracts fields by byte offset, so a
string-only walk would miss exactly the reads that touch 6.1 GB of sealed records).

It then checks that set against the record schema itself, read from `src/io/results.py`
(`REQUIRED_FIELDS` + `OPTIONAL_FIELDS`) plus the observed `metrics` key universe. Any looked-up name
that IS a record field must be in :data:`ALLOWED_RECORD_FIELDS`; anything else is an internal
dictionary key and is none of the guard's business. That is stronger than an allowlist of my own
choosing, because the forbidden set is derived from the schema rather than from my memory of it --
`wall_clock` lands in the forbidden set automatically, which is correct, since section 4 must source
the compute from the ledger and not from the record (open item E-wc).

* WHAT IT REUSES, STATED SO NO DEFINITION IS SILENTLY RE-DERIVED.

  s.1-3  `docs/analysis/record_seed_completeness.py` (S15) -- `scan`, `banked_rung`,
         `registered_rungs`, `registered_arms`. The rung an arm BANKS is the largest registered rung
         whose whole seed prefix it holds; the roster is read from `frozen*/` and is a LOWER BOUND,
         so every rung printed is an UPPER BOUND. Not re-derived here, imported.
  s.5    `docs/ops/authoring_reliability.py` -- the CORRECTED per-model panel (defect D34). The
         guard's own `_rejects/` marker panel structurally CANNOT hold an author-side rejection and
         globs `search_leg_*` only, so it understates non-uniformly and re-orders the gradient.
  s.6    `src/inference/reward_taxonomy.py::taxonomy_by_arm` -- the project's own program-KIND
         instrument, grouped by MODEL LINE instead of by arm.
  s.4    the phase split of `docs/ops/watch/FLAWLESS_LEDGER.md` (SEARCH / TEST-sweep / TEST-per-arm
         / TEST-baselines / TEST-h2_pair), recomputed from `ledger/*.epilogue.jsonl`.

* MEMORY AND TIME. The sealed tier is 12,488 records at ~477 KB each (6.1 GB). Nothing is
accumulated per record beyond three small scalars, and each record is read TAIL-FIRST: the three
fields sit at 81-92 % of the file (measured over a 120-record random sample, minimum 0.813), so the
last third is read and a full read is the fallback when any field is missing. Peak RSS is MEASURED
and printed, not asserted.

    python docs/analysis/blind_quality_report.py
    python docs/analysis/blind_quality_report.py --root outputs/campaign_cluster_run4
    python docs/analysis/blind_quality_report.py --selftest

EXIT: 0 always (this is a report) * 2 the archive could not be read, or held nothing to inspect.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

DEFAULT_ROOT = REPO / "outputs" / "campaign_cluster_run4"
RECORD_NAME = "record.json"

# --------------------------------------------------------------------------------------------- #
# THE BLINDNESS ALLOWLIST -- the only record fields this file may look up.                        #
# --------------------------------------------------------------------------------------------- #
#: Identity + provenance + the two R115 execution counters. Not one of them is an outcome.
ALLOWED_RECORD_FIELDS: tuple[str, ...] = (
    "arm",                          # experimental condition (identity)
    "seed",                         # ladder position (identity)
    "candidate_id",                 # search-slot identity
    "reward_source",                # the authored PROGRAM TEXT -- s.6 classifies its structure
    "reward_source_hash",           # content hash -- s.8's determinism key
    "train_safe_call_count",        # R115 denominator: times the authored reward was called
    "train_safe_default_count",     # R115 numerator: times the R66 neutral fallback stood in
)

#: The `metrics` key universe observed in this archive (search schema UNION sealed-test schema).
#: Used only to decide which looked-up names ARE record fields; everything here that is not in
#: :data:`ALLOWED_RECORD_FIELDS` becomes forbidden.
OBSERVED_METRICS_FIELDS: tuple[str, ...] = (
    "device", "per_period_pnl", "popart_scale", "tail_stats", "test_alloc", "test_components",
    "test_cvar05", "test_exposure", "test_gross", "test_returns", "test_sharpe", "test_turnover",
    "train_curve", "train_safe_call_count", "train_safe_default_count", "val_fitness",
    "val_returns",
)

R115_FLOOR_KEY = "winner_max_fallback_frac"

_SEED_RE = re.compile(r"-s(\d+)$")
_PBATCH_RE = re.compile(r"_p\d+$")


# --------------------------------------------------------------------------------------------- #
# byte-level field extraction -- the sealed tier is 6.1 GB and must never be json.loads()'d       #
# --------------------------------------------------------------------------------------------- #
def _needle(field: str) -> bytes:
    """The exact JSON key bytes for `field` as `write_run` emits them (indent=2, sort_keys=True).

    Built from the field NAME so the blindness guard can check the needle the same way it checks a
    `.get()` argument. The unescaped `"` in the needle is what makes this safe against a false hit
    inside `reward_source`: that field is a JSON STRING, so every quote it contains is written `\\"`
    and no key pattern with bare quotes can occur inside it.
    """
    return b'"' + field.encode("ascii") + b'": '


def _scalar_after(blob: bytes, field: str):
    """The scalar value following `field`'s key in `blob`, or None if the key is absent.

    Returns a float for a number and a str for a quoted string. Deliberately tiny: it reads the one
    token after the colon and stops, so a 32,000-element array that happens to follow costs nothing.
    """
    i = blob.find(_needle(field))
    if i < 0:
        return None
    j = i + len(_needle(field))
    if j < len(blob) and blob[j : j + 1] == b'"':
        k = blob.find(b'"', j + 1)
        return blob[j + 1 : k].decode("ascii", "replace") if k > 0 else None
    k = j
    while k < len(blob) and blob[k : k + 1] not in (b",", b"\n", b"}", b"\r"):
        k += 1
    tok = blob[j:k].strip()
    try:
        return float(tok)
    except ValueError:
        return None


#: Read the last max(TAIL_MIN, size // TAIL_DIV) bytes first. Measured over a 120-record random
#: sample of the sealed tier: the EARLIEST of the three fields sits at fraction 0.813 of the file,
#: so a quarter leaves ~7 percentage points of margin on the observed worst case. A miss falls back
#: to the WHOLE file, so this optimisation can only change the I/O, never a result -- and the
#: fallback COUNT is printed, so a run in which the assumption stopped holding says so instead of
#: silently getting slower.
TAIL_DIV = 4
TAIL_MIN = 128 * 1024
#: Incremented whenever the tail read missed and the whole file had to be read. Module-level rather
#: than threaded through every signature: it is a diagnostic about the reader, not a result.
TAIL_MISSES = 0


def read_fields(path: Path, fields: tuple[str, ...]) -> tuple:
    """(size, {field: scalar}), tail-first with a whole-file fallback. Never parses JSON.

    The size is returned rather than stat()ed again by the caller: one `stat` per record over
    ~14,000 records is not free, and two would be twice as not-free for no information.
    """
    global TAIL_MISSES
    size = path.stat().st_size
    want = max(TAIL_MIN, size // TAIL_DIV)
    if want < size:
        with path.open("rb") as fh:
            fh.seek(size - want)
            blob = fh.read()
        got = {f: _scalar_after(blob, f) for f in fields}
        if all(v is not None for v in got.values()):
            return size, got
        TAIL_MISSES += 1
    blob = path.read_bytes()
    return size, {f: _scalar_after(blob, f) for f in fields}


# --------------------------------------------------------------------------------------------- #
# archive walking                                                                                 #
# --------------------------------------------------------------------------------------------- #
def _is_d18_nested(parts: tuple) -> bool:
    """A D18 `shutil.move` nested duplicate: a unit dir whose name equals its parent's.

    Skipped exactly as `docs/analysis/reward_code_audit.py` skips it, and for the same reason: every
    naive `rglob` instrument counts those records twice.
    """
    return any(parts[i] == parts[i - 1] for i in range(1, len(parts) - 1))


def iter_records(root: Path):
    """(line, arm, unit, path) for every archive record, dot-dirs and D18 nests excluded."""
    for p in root.rglob(RECORD_NAME):
        parts = p.parts
        if any(seg.startswith(".") for seg in parts):
            continue
        if _is_d18_nested(parts):
            continue
        rel = p.relative_to(root).parts
        if len(rel) < 4:                       # <line>/<arm>/<unit>/record.json
            continue
        yield rel[0], rel[1], rel[2], p


def _pct(sorted_vals: list, q: float) -> float:
    """Nearest-rank percentile on an already-sorted list (no interpolation, no numpy)."""
    if not sorted_vals:
        return float("nan")
    k = min(len(sorted_vals) - 1, int(q * len(sorted_vals)))
    return sorted_vals[k]


def _peak_rss_mb() -> str:
    """Measured peak resident set, or an honest 'unavailable' -- never a guess."""
    try:
        import psutil

        mi = psutil.Process().memory_info()
        peak = getattr(mi, "peak_wset", None)
        if peak:
            return "%.1f MB (psutil peak_wset)" % (peak / 1048576.0)
        return "%.1f MB (psutil rss at exit; no peak counter on this platform)" % (
            mi.rss / 1048576.0)
    except Exception:                                                        # noqa: BLE001
        try:
            import resource

            return "%.1f MB (getrusage maxrss)" % (
                resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0)
        except Exception:                                                    # noqa: BLE001
            return "UNAVAILABLE (no psutil and no resource module)"


# --------------------------------------------------------------------------------------------- #
# SECTIONS 1-3 -- completeness, holes, coverage. Definitions imported from S15, never re-derived.  #
# --------------------------------------------------------------------------------------------- #
def section_completeness(root: Path) -> tuple[dict, list]:
    """s.1 + s.2 + s.3, all three off ONE S15 scan. Returns (s15_data, rungs) for later reuse."""
    print("=" * 108)
    print("1. PER-LEG COMPLETENESS -- seeds held, frontier, and the rung actually BANKED")
    print("=" * 108)
    print("   DEFINITIONS REUSED VERBATIM from docs/analysis/record_seed_completeness.py (S15):")
    print("     * banked_rung(seeds)  = the largest registered rung whose ENTIRE prefix 0..r-1 is held")
    print("     * registered_arms()   = the line's roster, read from its frozen*/ winner dirs, which")
    print("                             is a LOWER BOUND, so every rung below is an UPPER BOUND")
    print("     * registered_rungs()  = seeds.tiers, READ from config/preregistration.yaml")
    print("   Nothing is re-derived here. If S15's definition changes, this table changes with it.")
    print()

    try:
        from docs.analysis import record_seed_completeness as s15
    except Exception as exc:                                                 # noqa: BLE001
        print("   UNAVAILABLE: could not import S15 (%r). Sections 1-3 are not approximated." % exc)
        return {}, []
    try:
        rungs = s15.registered_rungs()
    except Exception as exc:                                                 # noqa: BLE001
        print("   UNAVAILABLE: the registered ladder could not be read (%r)." % exc)
        return {}, []

    data = s15.scan(str(root))
    if not data:
        print("   UNAVAILABLE: S15 enumerated ZERO sealed-test arms under %s." % root)
        return {}, rungs

    print("   registered rungs: %s" % rungs)
    print("   LADDER column: one Y/. per rung in the order above; Y = that rung's whole prefix is held")
    print()
    print("   %-26s %-38s %6s %8s %6s %7s   %s" % (
        "line", "arm", "seeds", "front.", "holes", "banked",
        " ".join("%5d" % r for r in rungs)))
    by_line: dict = defaultdict(list)
    for (line, arm), v in data.items():
        by_line[line].append((arm, v))
    for line in sorted(by_line):
        for arm, v in sorted(by_line[line]):
            seeds = v["seeds"]
            banked = s15.banked_rung(seeds, rungs)
            ladder = " ".join("    Y" if all(s in seeds for s in range(r)) else "    ."
                              for r in rungs)
            print("   %-26s %-38s %6d %8d %6d %7d   %s" % (
                line, arm, v["n"], v["frontier"], len(v["holes"]), banked, ladder))
    print()

    # ---- 2. hole positions ------------------------------------------------------------------- #
    print("=" * 108)
    print("2. HOLE POSITIONS -- which seeds are missing BELOW each arm's frontier")
    print("=" * 108)
    print("   A hole is not by itself a defect: during pipelined C4 a line lands seeds out of order")
    print("   as pack-8 jobs return, so a climbing line ALWAYS shows holes. What a hole DOES do is")
    print("   demote the arm's contiguous-prefix rung, and the campaign's reported rung is a MINIMUM")
    print("   over arms -- so the 'implies rung' column is the cost, not the hole count.")
    print()
    holed = {k: v for k, v in data.items() if v["holes"]}
    if not holed:
        print("   NONE -- every started arm holds a contiguous prefix 0..n-1.")
    else:
        print("   %-26s %-20s %8s %6s %12s %13s   %s" % (
            "line", "arm", "frontier", "holes", "implies rung", "frontier-rung", "missing seeds"))
        for (line, arm), v in sorted(holed.items()):
            shown = ", ".join(str(s) for s in v["holes"][:14])
            if len(v["holes"]) > 14:
                shown += ", ... (+%d)" % (len(v["holes"]) - 14)
            print("   %-26s %-20s %8d %6d %12d %13d   %s" % (
                line, arm, v["frontier"], len(v["holes"]),
                s15.banked_rung(v["seeds"], rungs),
                s15.banked_rung(set(range(v["frontier"] + 1)), rungs), shown))
    print()

    # ---- 3. seed coverage against the registered rungs ---------------------------------------- #
    print("=" * 108)
    print("3. SEED COVERAGE against the registered rungs (config/preregistration.yaml: seeds.tiers)")
    print("=" * 108)
    units = len(data)
    started = sum(1 for v in data.values() if v["started"])
    total_seeds = sum(v["n"] for v in data.values())
    top = max(rungs)
    print("   registered ladder      : %s   (ceiling %d)" % (rungs, top))
    print("   (line, arm) units      : %d   of which STARTED %d, holding NO record %d"
          % (units, started, units - started))
    print("   sealed-test seeds held : %d   against %d x %d = %d for a full ladder on every unit"
          % (total_seeds, units, top, units * top))
    print()
    print("   %8s %14s %14s %16s" % ("rung", "units banked", "share of units", "lines all-arms"))
    line_min = {ln: min(s15.banked_rung(v["seeds"], rungs) for _a, v in arms)
                for ln, arms in by_line.items()}
    for r in rungs:
        n_units = sum(1 for v in data.values() if s15.banked_rung(v["seeds"], rungs) >= r)
        n_lines = sum(1 for m in line_min.values() if m >= r)
        print("   %8d %14d %13.1f%% %16d" % (r, n_units, 100.0 * n_units / units, n_lines))
    print()
    model_lines = {ln: m for ln, m in line_min.items() if ln != "test_h3_singleshot"}
    print("   per-line minimum over its OWN registered arms:")
    for ln in sorted(line_min, key=lambda x: (line_min[x], x)):
        tag = "   <- EXCLUDED from the R101 population (H3 single-shot control, not a model leg)" \
            if ln == "test_h3_singleshot" else ""
        print("     %-30s %4d%s" % (ln, line_min[ln], tag))
    if model_lines:
        print()
        print("   ==> COMMON RUNG over the %d full-loop MODEL lines = %d  (R101; an UPPER BOUND, for"
              % (len(model_lines), min(model_lines.values())))
        print("       the four reasons S15's own output enumerates -- unfrozen arms, absent lines,")
        print("       unreadable rosters, and the 11 baselines that never get a -winner dir)")
    print()
    return data, rungs


# --------------------------------------------------------------------------------------------- #
# SECTION 4 -- wall-clock / compute, from the epilogue ledgers (NEVER from the record: E-wc)      #
# --------------------------------------------------------------------------------------------- #
def phase_of(batch: str) -> str:
    """The FLAWLESS_LEDGER phase of an epilogue batch, decided on its generated batch NAME.

    !! THIS IS NOT `docs/analysis/compute_accounting.py::tier_of_batch`, AND THE DIFFERENCE IS A
    DEFECT IN THAT FILE, MEASURED HERE. Its test predicate is `"_test" in b or b.endswith("test")
    or "baselines" in b or "h2_pair" in b`, and the sealed-test SWEEP batches are named
    `<tag>_sweep_t<N>_p<NN>` -- which contains neither `_test` nor a trailing `test`. So the single
    largest sealed-test population in the archive is classified as SEARCH by that instrument. The
    counts this file prints beside each phase make the disagreement visible rather than asserted.
    """
    b = _PBATCH_RE.sub("", batch.lower())
    if "_sweep_t" in b:
        return "TEST / sweep (C4)"
    if "baselines" in b:
        return "TEST / baselines"
    if "h2_pair" in b:
        return "TEST / h2_pair (C2)"
    if b.endswith("_test"):
        return "TEST / per-arm"
    return "SEARCH (DFO / generation)"


def section_compute(root: Path, n_records: int) -> None:
    print("=" * 108)
    print("4. WALL-CLOCK / COMPUTE -- sourced from ledger/*.epilogue.jsonl, NEVER from the record")
    print("=" * 108)
    print("   !! WHY THE LEDGER AND NOT THE RECORD (open item E-wc). `metrics.wall_clock` is 0.0 on")
    print("     the ENTIRE sealed-test tier -- src/orchestration/test_leg.py writes the literal 0.0,")
    print("     the writer is in drift-fenced src/, and the field cannot be repaired for records")
    print("     already written. The compute is NOT lost: each generated job script carries an EXIT")
    print("     trap writing {task, host, rc, secs, ts} per task, and those ledgers are pulled back.")
    print("   Phase split follows docs/ops/watch/FLAWLESS_LEDGER.md; durations over rc==0 tasks only.")
    print()
    led = root / "ledger"
    if not led.is_dir():
        print("   UNAVAILABLE: no ledger/ directory under %s." % root)
        return
    secs: dict = defaultdict(list)
    nonzero: dict = defaultdict(int)
    torn = 0
    files = sorted(led.glob("*.epilogue.jsonl"))
    if not files:
        print("   UNAVAILABLE: ledger/ holds no *.epilogue.jsonl file.")
        return
    for p in files:
        ph = phase_of(p.name[: -len(".epilogue.jsonl")])
        for ln in p.read_text(encoding="utf-8", errors="replace").splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                d = json.loads(ln)
            except ValueError:
                torn += 1
                continue
            try:
                rc = int(d.get("rc", 0))
            except (TypeError, ValueError):
                rc = 0
            if rc != 0:
                nonzero[ph] += 1
                continue
            try:
                secs[ph].append(float(d.get("secs") or 0.0))
            except (TypeError, ValueError):
                torn += 1

    n_tasks = sum(len(v) for v in secs.values()) + sum(nonzero.values())
    print("   %-28s %7s %8s %8s %8s %8s %9s %9s" % (
        "phase", "n(rc=0)", "p10 h", "median", "mean", "p90", "total h", "rc!=0"))
    order = ["SEARCH (DFO / generation)", "TEST / sweep (C4)", "TEST / per-arm",
             "TEST / baselines", "TEST / h2_pair (C2)"]
    for ph in order + sorted(set(secs) - set(order)):
        v = sorted(x / 3600.0 for x in secs.get(ph, []))
        if not v and not nonzero.get(ph):
            continue
        if not v:
            print("   %-28s %7d %8s %8s %8s %8s %9s %9d" % (ph, 0, "-", "-", "-", "-", "-",
                                                            nonzero.get(ph, 0)))
            continue
        print("   %-28s %7d %8.2f %8.2f %8.2f %8.2f %9.1f %9d" % (
            ph, len(v), _pct(v, 0.10), _pct(v, 0.50), sum(v) / len(v), _pct(v, 0.90), sum(v),
            nonzero.get(ph, 0)))
    search = sorted(x / 3600.0 for x in secs.get("SEARCH (DFO / generation)", []))
    test = sorted(x / 3600.0 for ph, vals in secs.items() if ph.startswith("TEST") for x in vals)
    print("   %s" % ("-" * 100))
    for name, v in (("ALL SEARCH", search), ("ALL TEST (sealed leg)", test)):
        if v:
            print("   %-28s %7d %8.2f %8.2f %8.2f %8.2f %9.1f" % (
                name, len(v), _pct(v, 0.10), _pct(v, 0.50), sum(v) / len(v), _pct(v, 0.90), sum(v)))
    print()
    print("   !! THE LEDGER IS NOT A COMPLETE CENSUS OF TRAININGS, AND BOTH COUNTS ARE GIVEN SO THE")
    print("     BOUND IS VISIBLE RATHER THAN BURIED:")
    print("       epilogue tasks on disk : %6d   (%d ledger file(s))" % (n_tasks, len(files)))
    print("       archive records on disk: %6d" % n_records)
    print("       ratio                  : %6.1f%%" % (
        100.0 * n_tasks / n_records if n_records else 0.0))
    print("     READ THAT RATIO WITH ITS ASSUMPTION STATED. It is an accounted-for share only if one")
    print("     epilogue task is one training, which is what the EXIT trap writes and what the")
    print("     measured per-task durations show (a sealed-test task runs ~9.4 h, i.e. one 400,000-")
    print("     step training). Under that reading roughly three quarters of the trainings on disk")
    print("     have NO ledger row: a task still running, one whose ledger has not been pulled back")
    print("     from the cluster, and every training from a batch whose epilogue was lost are all")
    print("     ABSENT. Every figure above therefore describes THE TASKS THAT WROTE AN EPILOGUE, is")
    print("     a LOWER BOUND on total compute, and must be quoted with that sentence attached.")
    if torn:
        print("     %d torn/unparseable ledger row(s) were skipped and are counted nowhere above."
              % torn)
    print("   !! A pooled mean over both phases is MEANINGLESS and must never be quoted: SEARCH runs")
    print("     8-thread and sealed TEST runs 1-thread, so the two distributions are different")
    print("     objects. The number that governs the record rate is the TEST-phase mean.")
    print()


# --------------------------------------------------------------------------------------------- #
# SECTION 5 -- authoring reliability (the CORRECTED instrument, defect D34)                       #
# --------------------------------------------------------------------------------------------- #
def section_authoring(root: Path) -> None:
    print("=" * 108)
    print("5. AUTHORING RELIABILITY -- did the model's generated reward code pass the gates?")
    print("=" * 108)
    print("   SOURCE: docs/ops/authoring_reliability.py (imported, not reimplemented). That file is")
    print("   the CORRECTED reading; the guard's own panel (scripts/campaign_guards.py::rejects_guard)")
    print("   UNDERSTATES it -- defect D34. Two structural reasons, both proven rather than argued:")
    print("     (a) it counts `_rejects/` markers, and `_write_reject_marker` runs ON THE NODE while")
    print("         the author-side gate `continue`s DRIVER-side, so a marker for an author-side")
    print("         rejection is STRUCTURALLY IMPOSSIBLE -- and those are exactly the 'did the model")
    print("         write admissible code' signal the table claims to report;")
    print("     (b) it globs `search_leg_*` only, so the CONFIRMATORY core line never enters the panel.")
    print("   The understatement is NON-UNIFORM, so it re-orders the capability gradient.")
    print()
    try:
        from docs.ops import authoring_reliability as ar
    except Exception as exc:                                                 # noqa: BLE001
        print("   UNAVAILABLE: could not import docs/ops/authoring_reliability.py (%r)." % exc)
        return
    scanned = ar.scan(str(root))
    lines = scanned["lines"]
    if not lines:
        print("   UNAVAILABLE: no search line found under %s -- nothing was inspected." % root)
        return
    print("   PER-SLOT% = lost registered candidates / registered slots   <- QUOTE THIS ONE")
    print("   PER-ATT%  = failure rows / (accepted + failure rows)        <- biased HIGH by re-authoring")
    print("   guard%    = what rejects_guard prints today (markers only)  <- the understated number")
    print()
    print("   %-30s %6s %6s %7s %9s %9s %9s %8s %8s" % (
        "line (model)", "slots", "lost", "accept", "PER-SLOT", "PER-ATT", "guard%", "authAST", "trunc"))
    rows = []
    for line, rec in sorted(lines.items(),
                            key=lambda kv: -(kv[1]["lost"] / kv[1]["slots"] if kv[1]["slots"] else 0)):
        c = rec["classes"]
        slot = 100.0 * rec["lost"] / rec["slots"] if rec["slots"] else 0.0
        att = 100.0 * ar._rate(rec["failed"], rec["accepted"])
        all_acc = sum(a["accepted"] for a in rec["arms"].values())
        guard = 100.0 * ar._rate(rec["markers"], all_acc)
        rows.append((slot, guard))
        print("   %-30s %6d %6d %7d %8.2f%% %8.2f%% %8.2f%% %8d %8d" % (
            line, rec["slots"], rec["lost"], rec["accepted"], slot, att, guard,
            c.get("author_ast_gate", 0), rec["truncated"]))
    t = scanned["totals"]
    print("   %s" % ("-" * 100))
    print("   TOTALS  slots=%d  lost=%d  accepted=%d  failure_rows=%d  markers=%d  truncated=%d"
          % (t["slots"], t["lost"], t["accepted"], t["failed"], t["markers"], t["truncated"]))
    print("   %d slot(s) hold BOTH a record and a permanent failure row (RE-AUTHORED after failing)."
          % t["reauthored"])
    print("   the marker set holds %d of the %d permanent failures; %d are MISSING from it."
          % (t["markers"], t["failed"], t["failed"] - t["markers"]))
    if rows:
        print("   largest per-line PER-SLOT-minus-guard discrepancy: %.2f percentage points"
              % max(abs(a - b) for a, b in rows))
    print()
    print("   TWO QUALIFICATIONS THAT MUST TRAVEL WITH THIS TABLE OR IT MISLEADS:")
    print("     1. `authAST` IS OUR GATE, NOT THE MODEL'S FAILURE. Execution record s.87.2: 12 of 20")
    print("        core-line ast_gate rejects examined were `.resize` missing from a 338-name")
    print("        attribute allowlist -- our gate over-rejecting SAFE numpy, a direction")
    print("        UNFAVOURABLE to us. Never quote a bare single rate; report the author/node split.")
    print("     2. `trunc` counts calls that hit OUR OWN 16,384-token output cap. A candidate lost to")
    print("        our cap is an instrument artefact, not a capability datum, and the registered")
    print("        obligation is to exclude it. It CANNOT be subtracted exactly (llm_calls.jsonl")
    print("        carries no candidate_id), so it is an UPPER BOUND on the correction.")
    print()


# --------------------------------------------------------------------------------------------- #
# SECTION 6 -- reward-code taxonomy, per model line                                               #
# --------------------------------------------------------------------------------------------- #
def section_taxonomy(root: Path) -> None:
    print("=" * 108)
    print("6. REWARD-CODE TAXONOMY -- the program-KIND distribution per model")
    print("=" * 108)
    print("   INSTRUMENT: src/inference/reward_taxonomy.py::taxonomy_by_arm, the project's own")
    print("   program-kind instrument, grouped by MODEL LINE instead of by arm. Kinds are connected")
    print("   components of the pairwise-Jaccard graph over depth-4 canonical AST SHAPE-SETS at")
    print("   similarity >= 0.6 -- node TYPES only, so identifiers and literals never enter.")
    print("   POPULATION: the SEARCH tier, LLM-authored arms only. The sealed-test tier re-runs one")
    print("   frozen winner across up to 568 seeds, so classifying it would weight each program by")
    print("   its seed count and measure the ladder, not the authoring. Counts and shares only.")
    print()
    try:
        from docs.ops.authoring_reliability import LLM_ARMS
        from src.inference.reward_taxonomy import construct_prevalence, taxonomy_by_arm
    except Exception as exc:                                                 # noqa: BLE001
        print("   UNAVAILABLE: could not import the taxonomy instrument (%r)." % exc)
        return

    sources: dict = defaultdict(dict)
    dfo: dict = defaultdict(dict)
    for line, arm, unit, p in iter_records(root):
        if not line.startswith("search"):
            continue
        try:
            rec = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except ValueError:
            continue
        src = rec.get("reward_source") or ""
        (sources if arm in LLM_ARMS else dfo)[line]["%s/%s" % (arm, unit)] = src
    if not sources:
        print("   UNAVAILABLE: no LLM-arm search record carries a reward_source under %s." % root)
        return

    res = taxonomy_by_arm(sources)
    pooled = res["pooled"]
    print("   pooled corpus: %d program(s) over %d model line(s) -> %d KIND(S), %d singleton(s), "
          "%d unparseable" % (pooled["n_programs"], len(sources), pooled["n_kinds"],
                              pooled["n_singletons"], pooled["n_unparseable"]))
    biggest = pooled["kinds"][0] if pooled["kinds"] else None
    if biggest:
        print("   largest pooled kind: %s, %d member(s) (%.1f%% of the corpus) -- %s"
              % (biggest["kind_id"], biggest["size"],
                 100.0 * biggest["size"] / pooled["n_programs"], biggest["label"]))
    print()
    print("   %-30s %9s %8s %10s %11s %12s" % (
        "line (model)", "programs", "kinds", "singleton", "share sing.", "entropy bits"))
    for line in sorted(res["per_arm"]):
        a = res["per_arm"][line]
        n = a["n_programs"]
        counts = a["kind_counts"]
        sing = sum(1 for k, c in counts.items() if c == 1)
        ent = a["entropy_bits"]
        print("   %-30s %9d %8d %10d %10.1f%% %12s" % (
            line, n, a["n_kinds_present"], sing, 100.0 * sing / n if n else 0.0,
            "%.3f" % ent if ent is not None else "n/a"))
    print()
    print("   !! READ THAT TABLE WITH ITS CONTROL. %d of %d programs are the ONLY member of their"
          % (pooled["n_singletons"], pooled["n_programs"]))
    print("     kind, so at this threshold the LLM-authored programs are very nearly structurally")
    print("     unique and the kind partition is close to the identity. That is a MEASUREMENT about")
    print("     the corpus, not a failure of the instrument, and the control that proves it is the")
    print("     derivative-free arms, which sample ONE parameterised template:")
    if dfo:
        dres = taxonomy_by_arm(dfo)
        dp = dres["pooled"]
        print("       %d derivative-free program(s) -> %d kind(s), %d singleton(s)"
              % (dp["n_programs"], dp["n_kinds"], dp["n_singletons"]))
        if dp["kinds"]:
            print("       largest: %d of %d members (%.1f%%) in one kind -- the template collapsing"
                  % (dp["kinds"][0]["size"], dp["n_programs"],
                     100.0 * dp["kinds"][0]["size"] / dp["n_programs"]))
    else:
        print("       (no derivative-free arm present in this archive)")
    print()
    print("   THE READABLE COMPOSITION -- share of each model's programs REFERENCING each construct,")
    print("   over the same single-source-of-truth vocabulary the kind labels are built from")
    print("   (src/inference/reward_taxonomy.CONSTRUCTS, comment-stripped and case-folded):")
    names: list = []
    prev: dict = defaultdict(lambda: defaultdict(int))
    for line, progs in sources.items():
        for src in progs.values():
            got = construct_prevalence(src)
            if not names:
                names = list(got)
            for k, present in got.items():
                if present:
                    prev[line][k] += 1
    if names:
        # Construct names are long and the table is wide, so the header is printed VERTICALLY:
        # one legend line per construct with the column index it occupies. A truncated header row
        # ("cvarquantile_ drawdown...") is unreadable, and an unreadable table is a defect.
        for i, nm in enumerate(names, start=1):
            print("     col %2d = %s" % (i, nm))
        print("   %-30s %6s %s" % ("line (model)", "n",
                                   " ".join("%5d" % i for i in range(1, len(names) + 1))))
        for line in sorted(sources):
            n = len(sources[line])
            print("   %-30s %6d %s" % (line, n, " ".join(
                "%4.0f%%" % (100.0 * prev[line].get(k, 0) / n if n else 0.0) for k in names)))
    print()


# --------------------------------------------------------------------------------------------- #
# SECTIONS 7 + 8 -- one streaming pass over the whole archive                                    #
# --------------------------------------------------------------------------------------------- #
def registered_r115_floor() -> float | None:
    """`fitness.winner_max_fallback_frac`, READ from the frozen registration -- never hardcoded."""
    try:
        import yaml

        with (REPO / "config" / "preregistration.yaml").open(encoding="utf-8") as fh:
            y = yaml.safe_load(fh) or {}
        v = (y.get("fitness") or {}).get(R115_FLOOR_KEY)
        return float(v) if v is not None else None
    except Exception:                                                        # noqa: BLE001
        return None


def stream_archive(root: Path, floor: float | None) -> dict:
    """ONE tail-first pass: R115 counters + the determinism key, per record. Never json.loads().

    `floor` is the registered R115 threshold, passed in rather than re-read here so there is exactly
    one place in this file that decides what the frozen value is. When it is None (the registration
    could not be read) the eligibility COUNT is left at None and section 7 prints UNAVAILABLE rather
    than an approximation.
    """
    fields = ("train_safe_call_count", "train_safe_default_count", "reward_source_hash")
    per_line: dict = defaultdict(lambda: {"n": 0, "n_frac": 0, "worst": None,
                                          "worst_unit": "", "at_or_above": 0, "no_counters": 0})
    det: dict = defaultdict(list)
    n = 0
    bytes_read = 0
    for line, arm, unit, p in iter_records(root):
        n += 1
        size, got = read_fields(p, fields)
        bytes_read += size
        tier = "test" if line.startswith("test") else (
            "search" if line.startswith("search") else "other")
        acc = per_line[(tier, line)]
        acc["n"] += 1
        calls = got["train_safe_call_count"]
        dflt = got["train_safe_default_count"]
        if calls and calls > 0 and dflt is not None:
            frac = dflt / calls
            acc["n_frac"] += 1
            if acc["worst"] is None or frac > acc["worst"]:
                acc["worst"], acc["worst_unit"] = frac, "%s/%s" % (arm, unit)
            if floor is not None and frac >= floor:
                acc["at_or_above"] += 1
        else:
            acc["no_counters"] += 1
        if tier == "test":
            m = _SEED_RE.search(unit)
            det[(arm, int(m.group(1)) if m else -1, got["reward_source_hash"])].append(
                "%s/%s/%s" % (line, arm, unit))
    return {"per_line": per_line, "det": det, "n": n, "bytes": bytes_read}


def section_r115_and_determinism(streamed: dict, floor: float | None) -> None:
    print("=" * 108)
    print("7. R115 EXCLUSIONS -- records at or above the registered winner-eligibility floor")
    print("=" * 108)
    if floor is None:
        print("   UNAVAILABLE: config/preregistration.yaml has no fitness.%s, and this file refuses"
              % R115_FLOOR_KEY)
        print("   to hardcode a frozen value (the R84 rule: a registered NAME requires a registered")
        print("   VALUE). Section 7 is not approximated.")
    else:
        print("   RULE (amendment R115, frozen 2026-07-28, value READ from the registration):")
        print("     a candidate is ELIGIBLE to be frozen as its arm's winner iff")
        print("       train_safe_default_count / train_safe_call_count < %.2f" % floor)
        print("     i.e. the AUTHORED reward actually ran, rather than the R66 neutral fallback")
        print("     standing in for it. `at/above floor` below therefore means INELIGIBLE.")
        print("   The rule reads only these two EXECUTION counters -- never a fitness, never a test")
        print("   metric -- so it is effect-blind by construction and cannot have been steered.")
        print()
        print("   %-6s %-30s %8s %10s %14s %12s %12s" % (
            "tier", "line", "records", "w/ counters", "at/above floor", "worst frac", "margin"))
        for tier in ("search", "test", "other"):
            rows = sorted((ln, a) for (t, ln), a in streamed["per_line"].items() if t == tier)
            for ln, a in rows:
                worst = a["worst"]
                print("   %-6s %-30s %8d %10d %14d %11s %12s" % (
                    tier, ln, a["n"], a["n_frac"], a["at_or_above"],
                    "%.4f%%" % (100.0 * worst) if worst is not None else "n/a",
                    "%.4f%%" % (100.0 * (floor - worst)) if worst is not None else "n/a"))
        allw = [(a["worst"], t, ln, a["worst_unit"])
                for (t, ln), a in streamed["per_line"].items() if a["worst"] is not None]
        print()
        for tier_name, sel in (("SEARCH", "search"), ("SEALED TEST", "test")):
            sub = [x for x in allw if x[1] == sel]
            if not sub:
                print("   %s: no record carries the two counters." % tier_name)
                continue
            w = max(sub)
            print("   WORST %-11s fallback fraction: %.4f%%  (%s %s)"
                  % (tier_name, 100.0 * w[0], w[2], w[3]))
            print("     margin to the %.0f%% floor: %+.4f percentage points -- %s"
                  % (100.0 * floor, 100.0 * (floor - w[0]),
                     "INSIDE the floor" if w[0] < floor else "AT OR ABOVE the floor"))
        print()
        print("   !! A record at or above the floor is NOT a defect. It is the phenomenon the campaign")
        print("     MEASURES: an authored reward that the sandbox had to substitute out. The rule")
        print("     excludes such a candidate from WINNER SELECTION; it does not delete the record.")
    print()

    print("=" * 108)
    print("8. DETERMINISM EVIDENCE -- and the honest statement that S4 is VACUOUS here")
    print("=" * 108)
    det = streamed["det"]
    with_replicate = {k: v for k, v in det.items() if len(v) > 1}
    print("   S4 (docs/analysis/record_science_audit.py) asks whether two records sharing")
    print("   (arm, seed, reward_source_hash) produced the same test path. Recomputed here")
    print("   INDEPENDENTLY, over the sealed-test tier, counting RECORDS per key rather than")
    print("   distinct outcome digests:")
    print()
    print("     distinct (arm, seed, reward_hash) keys : %d" % len(det))
    print("     keys holding MORE THAN ONE record      : %d" % len(with_replicate))
    print("     sealed-test records keyed              : %d" % sum(len(v) for v in det.values()))
    print()
    if not with_replicate:
        print("   => THE ZERO-REPLICATE CLAIM IS CONFIRMED FIRST-HAND, AND ITS CONSEQUENCE MUST BE")
        print("     STATED PLAINLY: **S4 IS VACUOUS IN THIS ARCHIVE** (disclosure D-c). Every key")
        print("     has exactly one record, so S4's comparison NEVER FIRES and its '0 disagree'")
        print("     result tests NOTHING. A vacuous pass is not evidence of determinism.")
        print()
        print("   => DETERMINISM MUST THEREFORE BE EVIDENCED FROM THE 30/30 BIT-IDENTICAL FARM, which")
        print("     re-trains an identical (arm, seed, reward) and compares the outputs -- the only")
        print("     experiment in this project that actually tests the property. Never cite S4 for it.")
    else:
        print("   => %d key(s) DO hold a replicate, so S4 is NOT vacuous over those keys."
              % len(with_replicate))
        print("     Listed so the determinism comparison can be run against them deliberately:")
        for k, v in sorted(with_replicate.items(), key=lambda kv: str(kv[0]))[:10]:
            print("       arm=%s seed=%s hash=%s ...  %d record(s): %s"
                  % (k[0], k[1], str(k[2])[:12], len(v), ", ".join(sorted(v)[:3])))
    print()
    print("   !! AND THE INSTRUMENT ITSELF IS WORTH ONE SENTENCE, because this recomputation does not")
    print("     agree with S4's own vacuity counter by accident. S4 stores {digest -> first path}")
    print("     and `setdefault`s, so a second record that AGREES adds no entry: its")
    print("     `replicate_keys` and its `dup_keys` are computed from the same `len(v) > 1` and are")
    print("     therefore identically equal. It cannot count a replicate that agrees. The count")
    print("     above is over RECORDS and does not share that blind spot.")
    print()


# --------------------------------------------------------------------------------------------- #
# THE BLINDNESS PROOF                                                                             #
# --------------------------------------------------------------------------------------------- #
def _looked_up_names(tree: ast.Module) -> set:
    """Every string used as a `.get(...)` argument, a `[...]` subscript, or a JSON-key byte literal.

    Those are the only three ways a record field can be read in this file, and the third exists
    because the sealed-tier pass extracts by byte offset -- a string-only walk would be blind to
    exactly the reads that touch 6.1 GB of sealed records.
    """
    out: set = set()
    key_bytes = re.compile(rb'^"([A-Za-z_][A-Za-z0-9_]*)"')
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get" and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)):
            out.add(node.args[0].value)
        if (isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant)
                and isinstance(node.slice.value, str)):
            out.add(node.slice.value)
        if isinstance(node, ast.Constant) and isinstance(node.value, bytes):
            m = key_bytes.match(node.value)
            if m:
                out.add(m.group(1).decode("ascii"))
    return out


def _assert_blind(looked_up: set | None = None) -> None:
    """PROVE, over this file's own AST, that no outcome field is ever looked up.

    The forbidden set is DERIVED from the record schema (`src/io/results.py`) rather than written
    from memory, so a field I forgot cannot slip through: everything the schema knows about, minus
    the seven names in :data:`ALLOWED_RECORD_FIELDS`, is forbidden. `wall_clock` lands in it
    automatically -- which is correct and load-bearing, because section 4 must source the compute
    from the ledger and not from the record (E-wc).

    `looked_up` is injectable ONLY so the selftest can prove the guard is capable of FIRING. A
    guard that has never been seen to fail is an assertion about itself.
    """
    from src.io.results import OPTIONAL_FIELDS, REQUIRED_FIELDS

    schema = set(REQUIRED_FIELDS) | set(OPTIONAL_FIELDS) | set(OBSERVED_METRICS_FIELDS)
    forbidden = schema - set(ALLOWED_RECORD_FIELDS)
    if looked_up is None:
        looked_up = _looked_up_names(ast.parse(Path(__file__).read_text(encoding="utf-8")))
    breach = sorted(looked_up & forbidden)
    if breach:
        raise AssertionError(
            "BLINDNESS BREACH: this file looks up record field(s) %s. It may look up only: %s"
            % (breach, ", ".join(ALLOWED_RECORD_FIELDS)))
    return None


def _blind_summary() -> str:
    from src.io.results import OPTIONAL_FIELDS, REQUIRED_FIELDS

    schema = set(REQUIRED_FIELDS) | set(OPTIONAL_FIELDS) | set(OBSERVED_METRICS_FIELDS)
    return ("%d schema field(s) known, %d forbidden, %d allowed and every one non-outcome"
            % (len(schema), len(schema - set(ALLOWED_RECORD_FIELDS)), len(ALLOWED_RECORD_FIELDS)))


# --------------------------------------------------------------------------------------------- #
def selftest() -> int:
    """Every case must be able to FAIL against a wrong implementation, or it verifies nothing."""
    import tempfile

    ok = fail = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal ok, fail
        if cond:
            ok += 1
            print("  PASS  %s" % name)
        else:
            fail += 1
            print("  FAIL  %s  %s" % (name, detail))

    # A. the blindness guard must hold on this file as written.
    try:
        _assert_blind()
        check("A _assert_blind passes on this file as written", True)
    except AssertionError as exc:
        check("A _assert_blind passes on this file as written", False, str(exc))

    # B. and it must be able to FAIL -- a guard that cannot fire proves nothing.
    fake = "x = rec['test_sharpe']\ny = rec.get('val_fitness')\n"
    names = _looked_up_names(ast.parse(fake))
    check("B the AST walk SEES an outcome read (subscript and .get)",
          names == {"test_sharpe", "val_fitness"}, str(sorted(names)))

    # C. the byte-literal half: a JSON-key needle must be seen too. This is the case that fails
    #    against a string-only walk, i.e. against loader_collision_watch's version copied verbatim.
    names = _looked_up_names(ast.parse('n = b\'"test_returns": \'\n'))
    check("C the AST walk SEES a JSON-key BYTE needle (a string-only walk misses this)",
          names == {"test_returns"}, str(sorted(names)))

    # D. explanatory PROSE naming an outcome must NOT fire -- the false-positive this design exists
    #    to avoid, and the one that broke the first version of the sibling detector.
    names = _looked_up_names(ast.parse('"""we never read test_returns or val_fitness."""\n'))
    check("D prose naming an outcome does NOT fire (the substring-scan false positive)",
          names == set(), str(sorted(names)))

    # E. _scalar_after on the real on-disk shape (indent=2, sort_keys=True).
    blob = (b'{\n  "arm": "distributional",\n  "reward_source_hash": "abc123",\n'
            b'  "seed": 7,\n  "train_safe_call_count": 400000,\n'
            b'  "train_safe_default_count": 12\n}\n')
    check("E _scalar_after reads a string, an int and a trailing field",
          _scalar_after(blob, "reward_source_hash") == "abc123"
          and _scalar_after(blob, "seed") == 7.0
          and _scalar_after(blob, "train_safe_default_count") == 12.0
          and _scalar_after(blob, "nope") is None,
          str([_scalar_after(blob, f) for f in
               ("reward_source_hash", "seed", "train_safe_default_count", "nope")]))

    # F. the TAIL optimisation must never change an answer: a file whose fields sit BEFORE the tail
    #    window must still be read correctly via the whole-file fallback.
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / RECORD_NAME
        p.write_bytes(b'{\n  "reward_source_hash": "deadbeef",\n  "train_safe_call_count": 10,\n'
                      b'  "train_safe_default_count": 1,\n  "pad": "' + b"0" * 900000 + b'"\n}\n')
        _size, got = read_fields(p, ("train_safe_call_count", "train_safe_default_count",
                                     "reward_source_hash"))
        check("F fields BEFORE the tail window are still found (whole-file fallback)",
              got["reward_source_hash"] == "deadbeef" and got["train_safe_call_count"] == 10.0,
              str(got))

    # G. phase_of must classify the sealed-test SWEEP batches as TEST. This is the case that FAILS
    #    against compute_accounting.tier_of_batch, which is the defect phase_of documents.
    cases = {
        "leg9_leg_gemini_2_5_flash_sweep_t3_p01": "TEST / sweep (C4)",
        "c1_baselines_p07": "TEST / baselines",
        "leg6_leg_haiku_4_5_h2_pair_test_p02": "TEST / h2_pair (C2)",
        "leg1_leg_deepseek_v4_pro_placebo_test_p03": "TEST / per-arm",
        "leg2_leg_glm_5_2_distributional_g4_p05": "SEARCH (DFO / generation)",
        "c1_random_search_search": "SEARCH (DFO / generation)",
    }
    bad = {k: phase_of(k) for k, v in cases.items() if phase_of(k) != v}
    check("G every observed ledger batch name classifies to its FLAWLESS_LEDGER phase",
          not bad, str(bad))

    # H. _pct is nearest-rank and must not interpolate.
    v = [float(x) for x in range(1, 101)]
    check("H _pct is nearest-rank on a sorted list",
          _pct(v, 0.10) == 11.0 and _pct(v, 0.50) == 51.0 and _pct(v, 0.90) == 91.0,
          str([_pct(v, 0.10), _pct(v, 0.50), _pct(v, 0.90)]))

    # I. D18 nested duplicates must be skipped, exactly as reward_code_audit skips them.
    check("I a D18 nested unit dir is skipped and a normal one is not",
          _is_d18_nested(("a", "arm", "cand", "cand", RECORD_NAME))
          and not _is_d18_nested(("a", "arm", "cand", RECORD_NAME)))

    # K. THE GUARD MUST BE ABLE TO FIRE. A guard only ever seen to pass proves nothing about
    #    itself, and both halves are checked: an outcome field RAISES, and `wall_clock` -- the
    #    field section 4 is forbidden to use because of E-wc -- raises too, which is the case that
    #    fails if anyone widens ALLOWED_RECORD_FIELDS to make a shortcut compile.
    for name in ("test_returns", "val_fitness", "test_sharpe", "wall_clock", "per_period_pnl"):
        try:
            _assert_blind({"arm", "seed", name})
            check("K _assert_blind FIRES on a looked-up %r" % name, False, "it did not raise")
        except AssertionError:
            check("K _assert_blind FIRES on a looked-up %r" % name, True)
    try:
        _assert_blind({"arm", "seed", "reward_source_hash", "some_internal_key"})
        check("K _assert_blind does NOT fire on allowed fields + internal keys", True)
    except AssertionError as exc:
        check("K _assert_blind does NOT fire on allowed fields + internal keys", False, str(exc))

    # L. THE TWO BRANCHES THE LIVE ARCHIVE NEVER EXERCISES. Today every determinism key holds one
    #    record and every sealed-test record is inside the R115 floor, so the replicate branch and
    #    the at-or-above counter are DEAD CODE on the real input -- and dead code that has never
    #    run is code that has never been checked. A synthetic archive drives both.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for line, arm, unit, calls, dflt, h in (
                ("test_leg_a", "distributional", "distributional-s0", 1000, 1, "hh"),
                ("test_leg_b", "distributional", "distributional-s0", 1000, 1, "hh"),
                ("search_leg_a", "scalar", "scalar-g0-c0", 1000, 500, "gg"),
                ("search_leg_a", "scalar", "scalar-g0-c1", 1000, 0, "ff")):
            d = root / line / arm / unit
            d.mkdir(parents=True, exist_ok=True)
            (d / RECORD_NAME).write_text(json.dumps(
                {"arm": arm, "reward_source_hash": h, "seed": 0,
                 "train_safe_call_count": calls, "train_safe_default_count": dflt},
                indent=2, sort_keys=True), encoding="utf-8")
        st = stream_archive(root, 0.10)
        rep = {k: v for k, v in st["det"].items() if len(v) > 1}
        acc = st["per_line"][("search", "search_leg_a")]
        check("L1 two lines holding the SAME (arm, seed, reward_hash) ARE counted as a replicate",
              len(rep) == 1 and len(next(iter(rep.values()))) == 2, str(st["det"]))
        check("L2 a record AT OR ABOVE the R115 floor is counted, one below it is not",
              acc["at_or_above"] == 1 and acc["n_frac"] == 2 and abs(acc["worst"] - 0.5) < 1e-12,
              str(acc))
        check("L3 with floor=None the eligibility count stays 0 rather than guessing",
              stream_archive(root, None)["per_line"][("search", "search_leg_a")]["at_or_above"] == 0)

    # J. an EMPTY root must exit 2, never 0 -- "looked at nothing" is not "found nothing wrong".
    with tempfile.TemporaryDirectory() as td:
        rc = main(["--root", td])
        check("J an empty root exits 2 (a vacuous pass is worse than a failure)", rc == 2,
              "rc=%d" % rc)

    print("\nselftest: %d passed, %d failed" % (ok, fail))
    return 0 if fail == 0 else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Blind execution-quality report (a REPORT, not a gate).")
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()

    root = Path(a.root)
    t0 = time.time()
    print()
    print("#" * 108)
    print("# BLIND EXECUTION-QUALITY REPORT -- how well the campaign RAN, and nothing about what it FOUND")
    print("#" * 108)
    print("  root: %s" % root)
    if not root.is_dir():
        print("  *** ARCHIVE NOT READABLE at %s. This is UNKNOWN, never a clean result. Exit 2." % root)
        return 2

    # The one streaming pass, first, so an empty archive fails before any section prints.
    floor = registered_r115_floor()
    streamed = stream_archive(root, floor)
    if not streamed["n"]:
        print("  *** ZERO records enumerated under %s. Either the archive is empty or the walk is" % root)
        print("      pointed at the wrong root; both are UNKNOWN, not clean. Exit 2.")
        return 2
    print("  records enumerated: %d   (%.2f GB on disk, read tail-first)"
          % (streamed["n"], streamed["bytes"] / 1e9))
    print("  !! THE ARCHIVE IS LIVE and grows while this runs, so two sections that count the same")
    print("     population can differ by the handful of records pulled between them. Each count is")
    print("     EXACT at the moment it was taken and none is stale; do not read a small gap between")
    print("     s.3's seed total and s.8's key total as an inconsistency.")
    print()

    section_completeness(root)
    section_compute(root, streamed["n"])
    section_authoring(root)
    section_taxonomy(root)
    section_r115_and_determinism(streamed, floor)

    _assert_blind()
    print("=" * 108)
    print("EFFECT-BLIND, PROVEN OVER THIS FILE'S OWN AST: %s" % _blind_summary())
    print("  Fields looked up: %s." % ", ".join(ALLOWED_RECORD_FIELDS))
    print("  No test_returns, no val_returns, no Sharpe, no CVaR, no fitness, no p-value and no")
    print("  per-arm outcome was read, printed, returned or compared anywhere above.")
    print("  tail-read fallbacks: %d of %d record(s) needed a whole-file read"
          % (TAIL_MISSES, streamed["n"]))
    print("  peak RSS measured: %s" % _peak_rss_mb())
    print("  elapsed: %.1f s" % (time.time() - t0))
    print("  EXIT 0 -- this is a REPORT, not a gate. It never fails on what it finds.")
    print("=" * 108)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
