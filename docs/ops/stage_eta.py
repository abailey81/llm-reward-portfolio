"""Per-rung ETAs for RUN 4 — MEASURED first, and never a date in the past.

Tamer asked for each stage's current ETA in every update.

⚠⚠ WHAT WAS WRONG UNTIL 2026-08-03 (P234), AND IT IS WHY THE PAGE SHOWED YESTERDAY.
This file computed ``eta = LAUNCH + timedelta(days=makespan_days)``. ``plan_lanes`` returns the
makespan of the WHOLE campaign **from a standing start**, so anchoring it to LAUNCH answers
*"when would rung R have landed if the entire run had proceeded at today's core count from
2026-07-28 21:08?"* — a diagnostic, **not a calendar ETA**. Once elapsed time exceeded a rung's
modelled makespan the answer moved into the PAST and stayed there: at 5.88 d elapsed, rungs 30, 100,
189 and 279 all printed ``08-02`` on a page generated on ``08-03``, and rung 340 printed ``08-03``,
i.e. "today" for work that is nowhere near done.

**An ETA is a statement about the FUTURE. It is anchored at NOW, and it is never a past date.**

THE THREE NUMBERS THIS PRINTS, and why all three rather than one:

  * **MEASURED THROUGHPUT** — test-tier records actually archived in the last 1/3/12/24 h, read from
    record mtimes on disk. An OBSERVATION, not a model, and the only input that reflects fair-share
    contention, the VPN outage and the reboot.
  * **EMPIRICAL ETA** — ``now + remaining_records / measured_rate``, with remaining computed per
    ``(line, arm)`` from the archive itself so work already done is subtracted. **This is the number
    that actually predicts, and the one to quote.**
  * **REGISTERED MODEL** — ``src/cluster/lanes.py``, reported as a **duration** plus the
    critical-chain floor. Kept because it is the pre-registered, auditable model and it names the
    BINDING constraint, which the empirical number cannot. It is deliberately no longer rendered as
    a calendar date.

⚠ REMAINING IS A RECORD COUNT, NOT A BANKED RUNG. ``archive_depths()`` returns ``{arm: n_records}``,
and an arm holding n records can still bank a LOWER rung if a seed below its frontier is missing
(S15 / ``record_seed_completeness.py``: gpt-5.6-luna held 2,832 records and banked 189). A count is
the right quantity for "how much work is left" and the WRONG quantity for "what rung do we report".
Both are printed, labelled, and must not be swapped.

Usage:
    python stage_eta.py <measured_cores> [modelled_cores]
    python stage_eta.py --page <measured_cores>      # the block the status page embeds
    python stage_eta.py --selftest
"""
from __future__ import annotations

import datetime as dt
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from src.cluster.lanes import plan_lanes  # noqa: E402

LAUNCH = dt.datetime(2026, 7, 28, 21, 8, 58)   # supervisors up, UTC
STOP = dt.datetime(2026, 8, 27)                # R109 exogenous stop
RUNGS = [30, 100, 189, 279, 340, 403, 568]     # the registered assurance ladder
CHAIN_THREADS = 8                              # --search-threads 8 (R107)
WINDOWS_H = (1, 3, 12, 24)                     # throughput windows, hours
DEFAULT_ROOT = os.path.join(REPO, "outputs", "campaign_cluster_run4")


def test_record_mtimes(root: str = DEFAULT_ROOT) -> list[float]:
    """Epoch mtimes of every TEST-tier record.json under ``root``.

    Test-tier ONLY, deliberately: the cycle log's ``records=`` counter pools search and test, so a
    rate derived from it burns down a test-tier backlog with a search-inflated numerator and yields
    an ETA that is optimistic by construction. Reading mtimes off disk needs no history file and is
    exact for any window.
    """
    out: list[float] = []
    if not os.path.isdir(root):
        return out
    for d in sorted(os.listdir(root)):
        if not d.startswith("test"):
            continue
        base = os.path.join(root, d)
        if not os.path.isdir(base):
            continue
        for dirpath, _dirnames, filenames in os.walk(base):
            if "record.json" not in filenames:
                continue
            parts = dirpath.replace("\\", "/").split("/")
            if any(s.startswith((".pull_tmp", "_quarantine")) for s in parts):
                continue
            try:
                out.append(os.stat(os.path.join(dirpath, "record.json")).st_mtime)
            except OSError:
                continue
    return out


def throughput(mtimes: list[float], now_epoch: float,
               windows_h: tuple[int, ...] = WINDOWS_H) -> dict[int, tuple[int, float]]:
    """{window_hours: (records_in_window, records_per_hour)}."""
    out: dict[int, tuple[int, float]] = {}
    for h in windows_h:
        cutoff = now_epoch - h * 3600.0
        n = sum(1 for m in mtimes if m >= cutoff)
        out[h] = (n, n / h)
    return out


def remaining_records(rung: int, depths: dict) -> int:
    """Test records still owed to reach ``rung`` on EVERY (line, arm).

    ``max(0, ...)`` per arm, never a signed sum: an arm that has overshot cannot pay for an arm that
    is behind, because the reported result is a MINIMUM over arms (R101), not a total.
    """
    total = 0
    for per_arm in depths.values():
        for n in per_arm.values():
            total += max(0, rung - n)
    return total


def eta_from_rate(remaining: int, rate_per_h: float, now: dt.datetime):
    """(eta_datetime, days) anchored at NOW, or (None, None) when it cannot be projected."""
    if remaining <= 0:
        return now, 0.0
    if rate_per_h <= 0:
        return None, None
    days = remaining / rate_per_h / 24.0
    return now + dt.timedelta(days=days), days


def _depths(root: str) -> dict:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import line_balance as _lb
    prev = _lb.ROOT
    try:
        _lb.ROOT = root
        return _lb.archive_depths()
    finally:
        _lb.ROOT = prev


def render(measured: int, modelled: int = 830, root: str = DEFAULT_ROOT, page: bool = False) -> str:
    now = dt.datetime.utcnow()
    now_epoch = now.timestamp()
    elapsed_d = (now - LAUNCH).total_seconds() / 86400.0
    days_left = (STOP - now).total_seconds() / 86400.0

    mtimes = test_record_mtimes(root)
    tp = throughput(mtimes, now_epoch)
    depths = _depths(root)

    L: list[str] = []
    L.append(f"generated {now:%Y-%m-%d %H:%M} UTC | elapsed {elapsed_d:.2f} d | "
             f"{days_left:.1f} d to the Aug-27 stop | {len(mtimes)} test records on disk")
    L.append("")
    L.append("MEASURED test-tier throughput (from record mtimes -- an observation, not a model):")
    for h in WINDOWS_H:
        n, r = tp[h]
        L.append(f"    last {h:>2} h   {n:>5} records   {r:>7.1f} rec/h")

    # THE PROJECTION RATE: the 12 h window unless it is empty, then the widest window that is not.
    # A 1 h window is noisy (pack-8 batches land in bursts) and a 24 h one is stale across an outage;
    # 12 h spans a full batch turnover. Stated in the output so the reader knows which was used.
    rate_h = 12
    if tp[12][0] == 0:
        for h in (24, 3, 1):
            if tp[h][0] > 0:
                rate_h = h
                break
    rate = tp[rate_h][1]

    L.append("")
    L.append(f"EMPIRICAL ETA -- remaining work / the measured {rate_h} h rate, anchored at NOW:")
    L.append(f"    {'rung':>5}  {'remaining':>10}  {'days':>6}  {'ETA (UTC)':<16}  fits Aug-27?")
    for rung in RUNGS:
        rem = remaining_records(rung, depths)
        eta, days = eta_from_rate(rem, rate, now)
        if rem == 0:
            L.append(f"    {rung:>5}  {rem:>10,}  {0.0:>6.2f}  {'REACHED':<16}  yes")
        elif eta is None:
            L.append(f"    {rung:>5}  {rem:>10,}  {'--':>6}  {'NO RATE':<16}  "
                     f"0 records in every window -- cannot project")
        else:
            fits = "yes" if eta <= STOP else "NO -- past the stop"
            L.append(f"    {rung:>5}  {rem:>10,}  {days:>6.2f}  {eta:%Y-%m-%d %H:%M}  {fits}")

    L.append("")
    L.append("REGISTERED MODEL (src/cluster/lanes.py) -- a DURATION from a standing start, not a date:")
    L.append(f"    {'rung':>5}  {'@%d cores' % measured:>14}  {'@%d cores' % modelled:>14}   binding")
    for rung in RUNGS:
        cells = []
        binding = ""
        for cores in (measured, modelled):
            p = plan_lanes(rung=rung, cpu_cores=cores, chain_threads=CHAIN_THREADS)
            cells.append(f"{p.makespan_days:8.1f} d")
            binding = p.binding
        L.append(f"    {rung:>5}  {cells[0]:>14}  {cells[1]:>14}   {binding}")

    p = plan_lanes(rung=568, cpu_cores=modelled, chain_threads=CHAIN_THREADS)
    L.append("")
    L.append(f"    saturation: more than ~{p.saturation_cores:.0f} cores buy NOTHING at rung 568")
    L.append(f"    critical-chain floor: {p.critical_chain_days:.2f} d (serial, immune to more cores)")
    if not page:
        for n in p.notes:
            L.append(f"    * {n}")
    L.append("")
    L.append("    NOTE: 'remaining' is a RECORD COUNT, not a banked rung. An arm can hold n records")
    L.append("    and still bank a lower rung if a seed below its frontier is missing (S15).")
    return "\n".join(L)


def selftest() -> int:
    ok: list[str] = []
    bad: list[str] = []

    def ck(name, got, want):
        (ok if got == want else bad).append(f"{name}: got={got!r} want={want!r}")

    now = dt.datetime(2026, 8, 3, 18, 0, 0)

    # A. AN ETA IS NEVER IN THE PAST -- the whole point of P234.
    eta, days = eta_from_rate(1000, 100.0, now)
    ck("A1 eta is in the future", eta > now, True)
    ck("A2 days matches remaining/rate", round(days, 6), round(1000 / 100.0 / 24.0, 6))

    # B. Nothing remaining => REACHED, anchored at now, never a past date.
    ck("B1 zero remaining is now", eta_from_rate(0, 100.0, now), (now, 0.0))
    ck("B2 negative remaining is now", eta_from_rate(-5, 100.0, now), (now, 0.0))

    # C. A dead rate must not fabricate a date.
    ck("C1 zero rate yields no eta", eta_from_rate(500, 0.0, now), (None, None))
    ck("C2 negative rate yields no eta", eta_from_rate(500, -1.0, now), (None, None))

    # D. remaining is a per-arm max(0), never a signed sum: an overshooting arm must not pay for a
    #    lagging one, because the reported result is a MINIMUM over arms (R101).
    d = {"test_a": {"x": 40, "y": 10}}
    ck("D1 overshoot does not offset a laggard", remaining_records(30, d), 20)
    ck("D2 all met is zero", remaining_records(10, d), 0)
    ck("D3 empty depths is zero", remaining_records(30, {}), 0)
    ck("D4 two lines add up", remaining_records(30, {"a": {"x": 0}, "b": {"y": 10}}), 50)

    # E. throughput counts only what falls inside each window.
    base = now.timestamp()
    mt = [base - 600, base - 3600 * 2, base - 3600 * 20, base - 3600 * 100]
    tp = throughput(mt, base)
    ck("E1 1h window", tp[1][0], 1)
    ck("E2 3h window", tp[3][0], 2)
    ck("E3 12h window", tp[12][0], 2)
    ck("E4 24h window", tp[24][0], 3)
    ck("E5 rate is per hour", round(tp[24][1], 6), round(3 / 24, 6))
    ck("E6 empty input is zero, not a crash", throughput([], base)[12], (0, 0.0))

    # F. MUTATION CONTROL: the pre-fix rule (LAUNCH + makespan) produced a PAST date for any rung
    #    whose modelled makespan is under the elapsed time. Pin that it DID, and that we no longer do.
    pre_fix_eta = LAUNCH + dt.timedelta(days=4.6)          # rung 30's measured makespan
    ck("F1 the pre-fix anchor WAS in the past", pre_fix_eta < now, True)
    ck("F2 production anchors at now instead", eta_from_rate(1, 1.0, now)[0] >= now, True)
    ck("F3 production DISAGREES with the pre-fix anchor",
       eta_from_rate(1, 1.0, now)[0] != pre_fix_eta, True)

    # G. A larger rung can never owe less work than a smaller one.
    d2 = {"a": {"x": 5, "y": 100}}
    ck("G1 monotone in rung", remaining_records(568, d2) > remaining_records(30, d2), True)

    for line in ok:
        print("  pass  " + line)
    for line in bad:
        print("  FAIL  " + line)
    print(f"stage_eta selftest: {len(ok)}/{len(ok) + len(bad)} passed")
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    args = list(argv[1:])
    if "--selftest" in args:
        return selftest()
    page = "--page" in args
    positional = [a for a in args if not a.startswith("--")]
    measured = int(positional[0]) if positional else 20
    modelled = int(positional[1]) if len(positional) > 1 else 830
    print(render(measured, modelled, page=page))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
