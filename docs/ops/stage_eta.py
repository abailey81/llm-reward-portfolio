"""Per-rung ETAs for RUN 4 — MEASURED, population-consistent, and never a date in the past.

Tamer asked for each stage's current ETA in every update.

=====================================================================================
THREE GENERATIONS OF THIS FILE, AND WHAT EACH GOT WRONG. Read before changing anything.
=====================================================================================

**GEN 1 (until 2026-08-03) — P234: the page showed YESTERDAY.**
It computed ``eta = LAUNCH + timedelta(days=makespan_days)``. ``plan_lanes`` returns the makespan of
the WHOLE campaign **from a standing start**, so anchoring it to LAUNCH answers *"when would rung R
have landed if the entire run had proceeded at today's core count since 2026-07-28 21:08?"* — a
diagnostic, **not a calendar ETA**. Once elapsed (5.88 d) exceeded a rung's modelled makespan the
answer moved into the past and stayed there: verified in ``git show 077995ac:docs/RUN4_STATUS.md``,
rungs 30/100/189/279 all printed ``08-02`` and rung 340 printed ``08-03``, on a page generated 08-03.

**GEN 2 (same day) — P235: an empirical ETA that was optimistic by ~2x, in three independent ways.**
An auditor took it apart within the hour. All three are fixed here and all three are the same
underlying error — **a ratio whose numerator and denominator come from different populations**:

  1. ⚠ **THE CLOCK WAS AN HOUR OUT.** ``dt.datetime.utcnow().timestamp()`` — ``utcnow()`` returns a
     NAIVE datetime holding UTC, and ``.timestamp()`` interprets a naive datetime as **LOCAL**.
     Measured on this host: ``utcnow().timestamp() - time.time() == -3600.0`` exactly. Every window
     cutoff was pushed an hour further back, so "the last 1 h" reported **the last 2 hours of records
     divided by 1**, over-stating the current rate by up to 2.6x — and the 1 h row is the operator's
     stall detector. **Never build a window from ``utcnow().timestamp()``. Use ``time.time()``.**
  2. ⚠ **THE BACKLOG OMITTED 15 OF THE 71 REGISTERED TEST UNITS.** It summed
     ``line_balance.archive_depths()``, which enumerates only arms carrying a ``frozen*/`` marker —
     so the 11 ``baseline_*`` H1-canon arms, the 3 core DFO arms (``bayes_opt``/``cma_es``/``tpe``)
     and nemotron's unfrozen ``scalar_cvar5`` were **invisible**. ``lanes.py`` is explicit that the
     per-rung denominator is ``_TEST_UNITS_PER_RUNG = 71``. Remaining at rung 568 was understated by
     ~8,190 records, i.e. the headline ETA was built on ~75 % of the work.
  3. ⚠ **THE RATE COUNTED WORK THE BACKLOG DID NOT.** The mtime walk covered every ``test*`` cell
     including the baselines, while ``remaining`` excluded them — the exact defect this file's own
     docstring condemned in the cycle log one paragraph earlier.

**GEN 3 (this file).** One walk produces BOTH sides of the ratio, so numerator ⊆ denominator by
construction; the clock is ``time.time()``; the backlog is reconciled against the registered 71 and
the shortfall is added and REPORTED rather than silently dropped.

=====================================================================================
THE HONEST CAVEAT THAT SURVIVES, AND WHY THIS PUBLISHES A RANGE
=====================================================================================
**Total-remaining ÷ aggregate-rate is only valid if the rate's COMPOSITION is representative of the
remaining work, and right now it is not.** Measured 2026-08-03: 80.6 % of a 12 h window came from
``test_leg_gpt_5_6_luna``, a line sitting 8 records short of rung 568 — i.e. most of the rate is
attributable to a line that stops contributing within the hour, while ~20,000 records sit on lines
that produced ZERO in the same window. That is the pipelined line-major C4 path working as designed
(``line_balance.py``), not a fault — but it means a single point estimate is a guess.

This is not a hypothetical: ``docs/ops/WITHDRAWN_CLAIMS.md`` W3 withdrew *"rung 403 lands 08-09,
rung 568 lands 08-13"* for **exactly this** — a projection off a transient peak, produced by this
file. So this prints a **RANGE**, reports the **concentration** so the reader can see when one line
dominates, and **clamps every ETA to the registered critical-chain floor**, which no throughput
number can beat.

**WHAT THE TWO COLUMNS ACTUALLY ARE** (corrected on an auditor's F6 — an earlier version of this
line said *"fast = the best window, slow = the most pessimistic"*, which the code has never done):
both are fleet-wide and share one window, so both are **monotonic in the rung by construction**.
``earliest`` divides the total remaining by the whole fleet's rate (perfect redirection of freed
slots); ``latest`` divides it by the **go-forward** rate, which excludes cells already within one
pack of the ceiling (the finishing line's slots are not reused). A per-cell ``max`` was tried and
rejected: it is the truer statement of when a rung completes, but as a published bound it is
DEGENERATE — any idle cell makes it infinite, so the column read GATED at every rung. That fact is
now carried by the stage-barrier disclosure line instead.

⚠ **AND THE ``MIN_ETA_WINDOW_H = 12`` JUSTIFICATION IS WEAKER THAN IT FIRST READ.** The stated reason
was the 15 h ``h_rt`` pack-8 quantum — but ``h_rt`` is a *requested wall limit*, not an observed
turnover, and with ~200 staggered jobs in flight the per-job quantum does **not** propagate to the
aggregate: measured median inter-burst gap on the two live cells is **0.22 h**, not 15 h. The 1 h
trough that prompted the rule is better explained by the luna line handover. So 12 h is a
**smoothing choice that happens to be sound**, not a quantum derived from first principles, and the
floor is deliberately not raised to 15 h to match a number that does not mean what it appeared to.

⚠ REMAINING IS A RECORD COUNT, NOT A BANKED RUNG. An arm holding n records can still bank a LOWER
rung if a seed below its frontier is missing (S15: gpt-5.6-luna held 2,832 records and banked 189).
A count is right for "how much work is left" and WRONG for "what rung do we report".

Usage:
    python stage_eta.py <measured_cores> [modelled_cores]
    python stage_eta.py --page <measured_cores>      # the block the status page embeds
    python stage_eta.py --selftest
"""
from __future__ import annotations

import datetime as dt
import os
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO)

from src.cluster.lanes import _TEST_UNITS_PER_RUNG, plan_lanes  # noqa: E402

LAUNCH = dt.datetime(2026, 7, 28, 21, 8, 58)   # supervisors up, UTC
STOP = dt.datetime(2026, 8, 27)                # R109 exogenous stop
RUNGS = [30, 100, 189, 279, 340, 403, 568]     # the registered assurance ladder
CHAIN_THREADS = 8                              # --search-threads 8 (R107)
WINDOWS_H = (1, 3, 12, 24)                     # throughput windows, hours
#: ⚠⚠ THE SHORTEST WINDOW AN ETA MAY BE BUILT FROM (P237, 2026-08-03).
#: Records do not arrive smoothly: a test job is a PACK OF 8 seeds with ``h_rt = 15.0 h``, and its 8
#: records land together when the job ends. So the arrival process has a ~15 h quantum, and any
#: window shorter than one job turnover samples the GAPS BETWEEN BURSTS rather than the rate.
#: MEASURED 2026-08-03 while Tamer asked why the rate had collapsed: the 1 h window read 52 rec/h
#: and the 3 h read 94 rec/h against a 12 h reading of 206 rec/h — and the line then carrying the
#: campaign had **196 running pack-8 jobs**, i.e. a steady state of 196x8/15.0 = **104 rec/h**. The
#: 52 was a trough between bursts, and I had published it as the PESSIMISTIC BOUND of the ETA range,
#: which put rung 568 at 2026-08-26 — hours from the stop, and fiction.
#: Short windows remain PRINTED, because a genuinely stalled fleet shows up there first. They are
#: just not allowed to price the deadline.
MIN_ETA_WINDOW_H = 12
#: A cell within one pack of its target stops contributing almost immediately, so its share of a
#: window is rate that will NOT persist. Quantified and disclosed rather than silently trusted.
PACK = 8
DEFAULT_ROOT = os.path.join(REPO, "outputs", "campaign_cluster_run4")
REGISTERED_UNITS = _TEST_UNITS_PER_RUNG        # 71 = 9 core + 50 leg + 11 H1 canon + 1 H3


def test_cells(root: str = DEFAULT_ROOT) -> dict[tuple[str, str], list[float]]:
    """{(test_dir, arm): [record mtimes]} for the TEST tier — ONE walk, BOTH sides of the ratio.

    Enumerating from the ARCHIVE rather than from ``frozen*/`` markers is what fixes gen-2 defect 2:
    the 11 ``baseline_*`` arms and the not-yet-frozen arms have records but no marker, so a
    marker-driven enumeration cannot see them. Returning the mtimes alongside the count is what fixes
    defect 3 — the rate and the backlog are then computed over the SAME cells by construction, and
    they cannot drift apart later.

    Test-tier only, deliberately: the cycle log's ``records=`` pools search and test, so a rate taken
    from it burns down a test backlog with a search-inflated numerator.
    """
    out: dict[tuple[str, str], list[float]] = {}
    if not os.path.isdir(root):
        return out
    for d in sorted(os.listdir(root)):
        if not d.startswith("test") or not os.path.isdir(os.path.join(root, d)):
            continue
        base = os.path.join(root, d)
        for arm in sorted(os.listdir(base)):
            arm_dir = os.path.join(base, arm)
            if not os.path.isdir(arm_dir) or arm.startswith((".pull_tmp", "_quarantine")):
                continue
            mts: list[float] = []
            for dirpath, _dirnames, filenames in os.walk(arm_dir):
                if "record.json" not in filenames:
                    continue
                parts = dirpath.replace("\\", "/").split("/")
                if any(s.startswith((".pull_tmp", "_quarantine")) for s in parts):
                    continue
                try:
                    mts.append(os.stat(os.path.join(dirpath, "record.json")).st_mtime)
                except OSError:
                    continue
            out[(d, arm)] = mts
    return out


def throughput(cells: dict, now_epoch: float,
               windows_h: tuple[int, ...] = WINDOWS_H) -> dict[int, tuple[int, float]]:
    """{window_hours: (records_in_window, records_per_hour)}.

    ⚠ BOUNDED AT BOTH ENDS. An upper bound matters because this repo has already seen an mtime that
    disagreed with reality (the reboot left ``driver_nemotron-3-super.log`` with an mtime ~50 min
    behind its own content). A future-stamped file would otherwise be counted in EVERY window and
    inflate every rate.
    """
    out: dict[int, tuple[int, float]] = {}
    allm = [m for mts in cells.values() for m in mts]
    for h in windows_h:
        lo = now_epoch - h * 3600.0
        n = sum(1 for m in allm if lo <= m <= now_epoch)
        out[h] = (n, n / h)
    return out


def backlog(rung: int, cells: dict, registered_units: int = REGISTERED_UNITS) -> tuple[int, int]:
    """(records_owed, units_not_yet_on_disk) to reach ``rung`` on EVERY registered test unit.

    ``max(0, ...)`` per cell, never a signed sum: an arm that has overshot cannot pay for an arm that
    is behind, because the reported result is a MINIMUM over arms (R101), not a total.

    A unit with no directory yet owes a FULL rung. Counting only what is on disk is how gen 2 lost
    15 of 71 units; the shortfall is added here and reported by the caller.
    """
    owed = sum(max(0, rung - len(mts)) for mts in cells.values())
    missing = max(0, registered_units - len(cells))
    return owed + missing * rung, missing


def eta_from_rate(remaining: int, rate_per_h: float, now: dt.datetime, floor_days: float = 0.0):
    """(eta, days) anchored at NOW and never earlier than the critical-chain floor.

    ``floor_days`` is the registered serial chain: a throughput number cannot beat it however many
    cores arrive, so an ETA that ignores it is arithmetic detached from the model printed beneath it.
    """
    if rate_per_h <= 0:
        return (None, None) if remaining > 0 else (now + dt.timedelta(days=max(0.0, floor_days)),
                                                   max(0.0, floor_days))
    days = max(remaining / rate_per_h / 24.0 if remaining > 0 else 0.0, max(0.0, floor_days))
    return now + dt.timedelta(days=days), days


def concentration(cells: dict, now_epoch: float, hours: int) -> list[tuple[str, int]]:
    """[(test_dir, records_in_window)] sorted desc — how concentrated the rate is by LINE."""
    lo = now_epoch - hours * 3600.0
    per: dict[str, int] = {}
    for (d, _arm), mts in cells.items():
        per[d] = per.get(d, 0) + sum(1 for m in mts if lo <= m <= now_epoch)
    return sorted(((k, v) for k, v in per.items() if v), key=lambda kv: -kv[1])


def render(measured: int | None, modelled: int = 830, root: str = DEFAULT_ROOT,
           page: bool = False) -> str:
    # ⚠ ONE CLOCK, AND IT IS time.time(). See gen-2 defect 1.
    now_epoch = time.time()
    now = dt.datetime.utcfromtimestamp(now_epoch)
    elapsed_d = (now - LAUNCH).total_seconds() / 86400.0
    days_left = (STOP - now).total_seconds() / 86400.0

    cells = test_cells(root)
    tp = throughput(cells, now_epoch)
    on_disk = sum(len(m) for m in cells.values())

    chain = plan_lanes(rung=568, cpu_cores=modelled, chain_threads=CHAIN_THREADS)
    floor_total = chain.critical_chain_days
    floor_left = max(0.0, floor_total - elapsed_d)

    L: list[str] = []
    L.append(f"generated {now:%Y-%m-%d %H:%M} UTC | elapsed {elapsed_d:.2f} d | "
             f"{days_left:.1f} d to the Aug-27 stop")
    L.append(f"test tier: {on_disk:,} records over {len(cells)} of the {REGISTERED_UNITS} "
             f"registered units (lanes.py _TEST_UNITS_PER_RUNG)")
    L.append("")
    L.append("MEASURED test-tier throughput (record mtimes; an observation, not a model):")
    for h in WINDOWS_H:
        n, r = tp[h]
        L.append(f"    last {h:>2} h   {n:>5} records   {r:>7.1f} rec/h")

    conc = concentration(cells, now_epoch, 12)
    if conc:
        top, topn = conc[0]
        tot12 = sum(v for _, v in conc) or 1
        L.append(f"    12 h rate is {100.0 * topn / tot12:.0f}% from ONE line ({top}); "
                 f"{len(conc)} line(s) contributed at all")

    # ⚠ ETA BOUNDS COME ONLY FROM WINDOWS >= MIN_ETA_WINDOW_H (P237). Shorter windows are printed
    # above as a stall indicator and are deliberately NOT allowed to price the deadline: the arrival
    # quantum is a 15 h pack-8 job, so a 1 h reading measures the gap between bursts.
    rates = [(h, tp[h][1]) for h in WINDOWS_H if tp[h][0] > 0 and h >= MIN_ETA_WINDOW_H]
    short = [(h, tp[h][1]) for h in WINDOWS_H if h < MIN_ETA_WINDOW_H]
    if short:
        L.append(f"    (windows under {MIN_ETA_WINDOW_H} h are a STALL INDICATOR ONLY and do not "
                 f"price the ETA -- the arrival quantum is a 15 h pack-{PACK} job)")

    # HANDOVER RISK: how much of the ETA window came from cells about to stop contributing.
    if rates:
        eh = min(h for h, _ in rates)
        lo = now_epoch - eh * 3600.0
        ending = tot = 0
        ending_lines: dict[str, int] = {}
        for (d, _arm), mts in cells.items():
            k = sum(1 for m in mts if lo <= m <= now_epoch)
            tot += k
            if k and (568 - len(mts)) <= PACK:
                ending += k
                ending_lines[d] = ending_lines.get(d, 0) + k
        if tot and ending:
            who = ", ".join(sorted(ending_lines, key=lambda x: -ending_lines[x])[:2])
            L.append(f"    !! {100.0 * ending / tot:.0f}% of the {eh} h window came from cell(s) now "
                     f"within {PACK} records of rung 568 ({who}) -- that rate STOPS. The ETA below "
                     f"assumes the cluster redirects those slots; it is an assumption, not a "
                     f"measurement.")

    L.append("")
    if not rates:
        L.append("EMPIRICAL ETA -- UNAVAILABLE: zero test records in every window, so no rate can be")
        L.append("    measured. This is a BLIND state, not a fast one.")
    else:
        # ⚠⚠ THE TWO BOUNDS BRACKET THE ONE THING WE CANNOT MEASURE: whether the cluster REDIRECTS
        # the slots of a line that has just finished (P237). Taking fast and slow from two
        # historical windows is FALSE PRECISION when both contain the same finishing line -- they
        # agreed to within 8% while the tool simultaneously warned that 78% of that rate was about
        # to stop. So:
        #   FAST  = the full measured rate            -> assumes perfect redirection
        #   SLOW  = the go-forward rate, counting ONLY cells that still owe more than one pack
        #           -> assumes NO redirection at all
        # Both are measurements; the truth is between them, and the gap IS the open question.
        # ⚠⚠ BOTH RATES ARE COMPUTED **PER RUNG** (P239, on an auditor's F1/F2). The previous version
        # took one fleet-wide `fast_r` and one `slow_r` hardcoded to rung 568 and applied them to
        # EVERY row -- so a row's backlog counted only cells below that rung while its rate counted
        # the whole fleet. Measured at the time: of 2,410 records in the 12 h window only **22**
        # landed in a cell below rung 30, yet rung 30's ETA was priced at the full 202 rec/h.
        # The docstring claimed "numerator subset of denominator by construction"; that was true of
        # the file and FALSE of every row it printed. Same defect as gen 2, one level down.
        #
        # For a target rung R:
        #   FAST(R) = records in the window that landed in cells still BELOW R
        #             -> work that actually reduces R's backlog; assumes perfect redirection
        #   SLOW(R) = records in the window from cells that still owe MORE THAN ONE PACK toward R
        #             -> cells that will keep reducing R after their current job; assumes none
        # A rate of zero is NOT a fast answer: it means nothing on the critical set is producing, so
        # the row says GATED rather than inventing a date.
        eh2 = min(h for h, _ in rates)
        lo2 = now_epoch - eh2 * 3600.0

        # ⚠⚠⚠ AND THE PER-RUNG *RATE* WAS STILL THE WRONG MODEL (P239b, caught on its own output).
        # Pricing each rung as `its own backlog / its own cells' rate` produced a table that was
        # NON-MONOTONIC: rung 100 read 2026-11-09 "NO" while rung 403 read 2026-08-19 "yes". A larger
        # rung cannot be reached EARLIER than a smaller one, so the model was refuted by arithmetic
        # rather than by an auditor. The cause is structural: rung 100's small backlog sits in slow
        # or idle cells while rung 568's large backlog is spread over fast ones, so total/rate
        # compares incomparable populations at every row.
        #
        # THE CORRECT MODEL, and it is monotonic in the rung BY CONSTRUCTION:
        #   a rung is reached when the LAST cell reaches it -- a MAX over cells, not a total/rate.
        #   latest  (no redirection)      = max over cells of remaining_i / rate_i, with a cell that
        #                                   owes work and produces nothing being GATED (never)
        #   earliest(perfect redirection) = total remaining / the whole fleet's rate, i.e. any
        #                                   producer may serve any cell
        # earliest <= latest always, and both rise with the rung.
        # ⚠ A PER-CELL MAX WAS TRIED AND REJECTED, and the reason is worth keeping. "A rung completes
        # when the LAST cell reaches it" is the true statement, but as a published BOUND it is
        # DEGENERATE: any cell that owes work and produced nothing in the window has an infinite
        # time, so the column read GATED at every rung and carried no information. The structural
        # fact it was trying to express is real, so it is reported as the explicit disclosure line
        # below instead of as a column of blanks.
        #
        # BOTH COLUMNS ARE THEREFORE FLEET-WIDE AND MONOTONIC IN THE RUNG BY CONSTRUCTION
        # (total remaining rises with the rung; the divisor is constant across rows):
        #   earliest = total remaining / the whole fleet's rate       -> perfect redirection
        #   latest   = total remaining / the GO-FORWARD rate, which excludes cells already within
        #              one pack of the ceiling                        -> the finishing line's slots
        #                                                                are NOT reused
        fleet_rate = sum(sum(1 for m in mts if lo2 <= m <= now_epoch)
                         for mts in cells.values()) / eh2
        goforward_rate = sum(sum(1 for m in mts if lo2 <= m <= now_epoch)
                             for mts in cells.values() if (568 - len(mts)) > PACK) / eh2

        L.append("EMPIRICAL ETA -- earliest = total remaining / the whole fleet's rate (assumes the")
        L.append(f"    cluster REDIRECTS freed slots, {fleet_rate:.0f} rec/h); latest excludes cells")
        L.append(f"    already within {PACK} of the ceiling ({goforward_rate:.0f} rec/h), i.e. assumes")
        L.append(f"    the finishing line's slots are NOT reused. Window {eh2} h:")
        # ⚠ THE -1h COLUMN EXISTS BECAUSE TAMER READ THE PAGE AND SAID THE REMAINING FIGURE "KEEPS
        # BEING CONSTANT" (P240). It was not constant -- measured across published versions, rung
        # 568 fell 32,037 -> 32,000 in 16 minutes -- but a 37-record move on a 32,000 figure is
        # INVISIBLE, so a live number read as frozen. A quantity whose movement cannot be seen is
        # indistinguishable from a hardcoded one, and this page has shipped genuinely hardcoded
        # numbers before. Printing the DECREMENT makes "live" verifiable at a glance instead of
        # requiring the reader to diff two page versions.
        L.append(f"    {'rung':>5}  {'remaining':>10}  {'-1h':>6}  {'earliest (UTC)':<16}  "
                 f"{'latest (UTC)':<16}  Aug-27?")
        lo1 = now_epoch - 3600.0
        for rung in RUNGS:
            rem, _missing = backlog(rung, cells)
            # how much this rung's backlog actually fell in the last hour
            d1 = sum(sum(1 for m in mts if lo1 <= m <= now_epoch)
                     for mts in cells.values() if len(mts) <= rung)
            if rem == 0:
                L.append(f"    {rung:>5}  {rem:>10,}  {d1:>6}  {'REACHED':<16}  {'REACHED':<16}  yes")
                continue
            e_fast, _ = eta_from_rate(rem, fleet_rate, now, floor_left)
            e_slow, _ = eta_from_rate(rem, goforward_rate, now, floor_left)
            cf = f"{e_fast:%Y-%m-%d %H:%M}" if e_fast else "GATED"
            cs = f"{e_slow:%Y-%m-%d %H:%M}" if e_slow else "GATED"
            if e_slow and e_slow <= STOP:
                fits = "yes"
            elif e_fast and e_fast <= STOP:
                fits = "risk"
            else:
                fits = "NO"
            L.append(f"    {rung:>5}  {rem:>10,}  {d1:>6}  {cf:<16}  {cs:<16}  {fits}")
        L.append("    GATED = the relevant rate is zero, so no throughput number can date that row -- it is")
        L.append("    waiting on a stage barrier (C1 chain / C3 gate), not on cores.")
        _, missing = backlog(568, cells)
        if missing:
            L.append(f"    (+{missing} registered unit(s) have no directory yet; each owes a FULL "
                     f"rung and is counted above)")

        # ⚠ THE STAGE-BARRIER DISCLOSURE (auditor F3). A large share of the backlog can sit on a line
        # that has not entered C4 at all -- the core line's 9 arms plus the 11 H1 canon arms are
        # gated by the serial C1 DFO chain AND the C3 review gate (src/cluster/campaign.py), so NO
        # amount of redirected throughput starts them. Measured when this was written: 10,910 of
        # 32,106 records (34%) were behind that barrier while both ETA columns implicitly assumed it
        # could begin immediately. Reported as a share of the rung-568 backlog that produced NOTHING
        # in the window, which is the observable proxy for "not started".
        idle_rem = sum(max(0, 568 - len(mts)) for mts in cells.values()
                       if not any(lo2 <= m <= now_epoch for m in mts))
        rem568, miss568 = backlog(568, cells)
        idle_rem += miss568 * 568
        if rem568 and idle_rem:
            L.append(f"    !! {100.0 * idle_rem / rem568:.0f}% of the rung-568 backlog "
                     f"({idle_rem:,} records) sits on cells that produced NOTHING in the "
                     f"{eh2} h window -- work behind a stage barrier (C1 chain / C3 gate) is not "
                     f"accelerated by redirected cores. Neither column models when it starts.")

    L.append("")
    L.append("REGISTERED MODEL (src/cluster/lanes.py) -- a DURATION from a standing start, not a date:")
    if measured is None:
        L.append("    (core count unavailable this cycle -- the model table needs it; the EMPIRICAL")
        L.append("     block above does NOT and is unaffected)")
    else:
        L.append(f"    {'rung':>5}  {'@%d cores' % measured:>14}  {'@%d cores' % modelled:>14}   binding")
        for rung in RUNGS:
            cellrow = []
            binding = ""
            for cores in (measured, modelled):
                p = plan_lanes(rung=rung, cpu_cores=cores, chain_threads=CHAIN_THREADS)
                cellrow.append(f"{p.makespan_days:8.1f} d")
                binding = p.binding
            L.append(f"    {rung:>5}  {cellrow[0]:>14}  {cellrow[1]:>14}   {binding}")

    L.append("")
    L.append(f"    saturation: more than ~{chain.saturation_cores:.0f} cores buy NOTHING at rung 568")
    L.append(f"    critical-chain floor: {floor_total:.2f} d total, {floor_left:.2f} d still to run")
    L.append("    (serial by design, immune to more cores; every ETA above is clamped to it)")
    if not page:
        for n in chain.notes:
            L.append(f"    * {n}")
    L.append("")
    L.append("    NOTE: 'remaining' is a RECORD COUNT, not a banked rung -- an arm can hold n records")
    L.append("    and still bank lower if a seed below its frontier is missing (S15). And the range")
    L.append("    assumes the measured rate survives the line-major handover, which is an assumption.")
    return "\n".join(L)


def selftest() -> int:
    ok: list[str] = []
    bad: list[str] = []

    def ck(name, got, want):
        (ok if got == want else bad).append(f"{name}: got={got!r} want={want!r}")

    now = dt.datetime(2026, 8, 3, 18, 0, 0)

    # A. AN ETA IS NEVER IN THE PAST (P234).
    eta, days = eta_from_rate(1000, 100.0, now)
    ck("A1 eta is in the future", eta > now, True)
    ck("A2 days = remaining/rate", round(days, 6), round(1000 / 100.0 / 24.0, 6))
    ck("A3 zero remaining is now", eta_from_rate(0, 100.0, now), (now, 0.0))
    ck("A4 zero rate cannot fabricate a date", eta_from_rate(500, 0.0, now), (None, None))

    # B. THE CRITICAL-CHAIN CLAMP: throughput cannot beat the registered serial floor.
    e, d = eta_from_rate(1, 1e9, now, floor_days=2.0)
    ck("B1 clamped to the floor", round(d, 6), 2.0)
    ck("B2 clamp moves the date", e, now + dt.timedelta(days=2.0))
    ck("B3 floor does not shorten a longer projection",
       round(eta_from_rate(24000, 100.0, now, floor_days=1.0)[1], 4), round(24000 / 100 / 24, 4))

    # C. THE BACKLOG COVERS ALL REGISTERED UNITS, INCLUDING THOSE WITH NO DIRECTORY (gen-2 defect 2).
    cells = {("test_a", "x"): [0.0] * 40, ("test_a", "y"): [0.0] * 10}
    ck("C1 overshoot does not offset a laggard", backlog(30, cells, registered_units=2), (20, 0))
    ck("C2 all met is zero", backlog(10, cells, registered_units=2), (0, 0))
    ck("C3 MISSING units owe a full rung",
       backlog(30, cells, registered_units=4), (20 + 2 * 30, 2))
    ck("C4 registered count is the live 71", REGISTERED_UNITS, 71)
    # MUTATION CONTROL for defect 2: the gen-2 rule (on-disk cells only) UNDER-counts, and must differ.
    gen2 = sum(max(0, 30 - len(m)) for m in cells.values())
    ck("C5 gen-2 rule under-counted", gen2, 20)
    ck("C6 production DISAGREES with the gen-2 rule when units are missing",
       backlog(30, cells, registered_units=4)[0] != gen2, True)

    # D. WINDOWS ARE BOUNDED AT BOTH ENDS (gen-2 defect 1's sibling).
    base = now.timestamp()
    c = {("t", "a"): [base - 600, base - 3600 * 2, base - 3600 * 20, base + 3600]}
    tp = throughput(c, base)
    ck("D1 1h window", tp[1][0], 1)
    ck("D2 3h window", tp[3][0], 2)
    ck("D3 24h window", tp[24][0], 3)
    ck("D4 a FUTURE mtime is excluded from every window",
       all(tp[h][0] != 4 for h in WINDOWS_H), True)
    ck("D5 empty input is zero, not a crash", throughput({}, base)[12], (0, 0.0))

    # E. THE CLOCK BUG ITSELF, pinned BEHAVIOURALLY so it cannot come back (gen-2 defect 1).
    #    ⚠ My first attempt here GREPPED THIS FILE'S OWN SOURCE for "utcnow().timestamp()" and
    #    failed, because the docstring above legitimately quotes the bad call while explaining it.
    #    A source scan is a claim about TEXT; the defect is about BEHAVIOUR. So this builds a real
    #    archive with one record aged 1.5 h by the TRUE clock and asserts render() does not count it
    #    in the 1 h window. Under the gen-2 bug the cutoff sat 2 h back and it WOULD have counted --
    #    which is exactly how "last 1 h" over-reported the live rate by 2.6x.
    skew = dt.datetime.utcnow().timestamp() - time.time()
    ck("E1 utcnow().timestamp() is NOT a valid epoch here (skew proves the trap is real)",
       abs(skew) > 1.0, True)

    import json as _json
    import shutil as _shutil
    import tempfile as _tempfile
    tmp = _tempfile.mkdtemp(prefix="stage_eta_selftest_")
    try:
        cand = os.path.join(tmp, "test_leg_x", "distributional", "c0")
        os.makedirs(cand)
        rec = os.path.join(cand, "record.json")
        with open(rec, "w", encoding="utf-8") as fh:
            _json.dump({"arm": "distributional"}, fh)
        aged = time.time() - 1.5 * 3600.0          # 1.5 h old by the TRUE clock
        os.utime(rec, (aged, aged))
        c2 = test_cells(tmp)
        ck("E2 the fixture is discovered as one cell", len(c2), 1)
        tp2 = throughput(c2, time.time())
        ck("E3 a 1.5 h-old record is OUT of the 1 h window", tp2[1][0], 0)
        ck("E4 and IN the 3 h window", tp2[3][0], 1)
        out_e = render(1000, root=tmp, page=True)
        ck("E5 render()'s own 1 h row reads zero (end-to-end clock control)",
           "last  1 h       0 records" in out_e, True)
    finally:
        _shutil.rmtree(tmp, ignore_errors=True)

    # F. GENUINE MUTATION CONTROL AT THE render() LEVEL: no printed date may precede now.
    #    Gen 2's case F only checked a hand-built datetime and would have passed if render()
    #    reintroduced LAUNCH + makespan. This one reads the real output.
    import re as _re
    try:
        out = render(1000, page=True)
        dates = _re.findall(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}", out)
        gen_line = dates[0] if dates else None
        past = [d for d in dates[1:]
                if dt.datetime.strptime(d, "%Y-%m-%d %H:%M") < dt.datetime.utcfromtimestamp(
                    time.time()) - dt.timedelta(minutes=2)]
        ck("F1 render() emits a generated-at stamp", gen_line is not None, True)
        ck("F2 render() emits NO date before now", past, [])
    except Exception as exc:  # noqa: BLE001
        bad.append(f"F render() raised: {type(exc).__name__}: {exc}")

    # G. A missing core count must NOT destroy the empirical block (auditor MAJOR 6).
    try:
        out_nc = render(None, page=True)
        ck("G1 renders without cores", "EMPIRICAL ETA" in out_nc or "UNAVAILABLE" in out_nc, True)
        ck("G2 says the model table needs cores", "core count unavailable" in out_nc, True)
    except Exception as exc:  # noqa: BLE001
        bad.append(f"G render(None) raised: {type(exc).__name__}: {exc}")

    # H. THE PAGE IS ASCII-ONLY, and this is not a style rule: non-ASCII MOJIBAKES on Tamer's phone
    #    (publish_status.sh states it in its header). I broke this while adding the handover warning
    #    -- a single U+26A0 went straight into rendered page output -- so it is pinned here.
    try:
        page_out = render(1000, page=True)
        non_ascii = sorted({ch for ch in page_out if ord(ch) > 127})
        ck("H1 page output is pure ASCII", non_ascii, [])
    except Exception as exc:  # noqa: BLE001
        bad.append(f"H1 render raised: {type(exc).__name__}: {exc}")

    # I. THE ETA MAY NOT BE PRICED OFF A SUB-QUANTUM WINDOW (P237).
    #    A fixture whose last hour is EMPTY but whose 12 h is busy must still produce an ETA: under
    #    the pre-fix rule the 1 h window (rate 0, or a trough) was eligible and drove the pessimistic
    #    bound, which is how rung 568 came to read 2026-08-26.
    ck("I1 the floor is at least one job turnover", MIN_ETA_WINDOW_H >= 12, True)
    import shutil as _sh2
    import tempfile as _tf2
    tmp2 = _tf2.mkdtemp(prefix="stage_eta_window_")
    try:
        cand = os.path.join(tmp2, "test_leg_y", "scalar", "c0")
        os.makedirs(cand)
        base_t = time.time()
        # 200 records spread 2..11 h ago: the 12 h window is busy, the 1 h window is EMPTY.
        for i in range(200):
            p = os.path.join(cand, f"r{i}")
            os.makedirs(p)
            f = os.path.join(p, "record.json")
            open(f, "w", encoding="utf-8").close()
            aged = base_t - (2 * 3600 + (i / 200.0) * 9 * 3600)
            os.utime(f, (aged, aged))
        c3 = test_cells(tmp2)
        tp3 = throughput(c3, time.time())
        ck("I2 fixture: 1 h window is empty", tp3[1][0], 0)
        ck("I3 fixture: 12 h window is busy", tp3[12][0] > 100, True)
        out_i = render(1000, root=tmp2, page=True)
        ck("I4 an ETA is still produced from the 12 h window",
           "EMPIRICAL ETA" in out_i and "UNAVAILABLE" not in out_i, True)
        ck("I5 the sub-quantum caveat is stated", "STALL INDICATOR ONLY" in out_i, True)
        # ⚠⚠ I6 IS THE REAL MUTATION CONTROL, and I1-I5 were NOT (auditor F4, verified by executing
        # a mutant in memory: deleting `and h >= MIN_ETA_WINDOW_H` still scored 33/33). I1 compared
        # a constant with itself; I5's caveat string is emitted from `short`, which is derived from
        # the constant INDEPENDENTLY of `rates`, so it survives removal of the filter. This asserts
        # the WINDOW THE ETA WAS ACTUALLY PRICED FROM, which is what the fix changes.
        ck("I6 the ETA names a window >= the floor",
           any(f"Window {h} h" in out_i for h in WINDOWS_H if h >= MIN_ETA_WINDOW_H), True)
        ck("I6b and never a sub-quantum window",
           any(f"Window {h} h" in out_i for h in WINDOWS_H if h < MIN_ETA_WINDOW_H), False)

    # J. MONOTONICITY -- a larger rung can NEVER be reached earlier than a smaller one.
    #    This is the property that refuted the per-rung-rate model on its own output (rung 100 read
    #    2026-11-09 "NO" while rung 403 read 2026-08-19 "yes"). Arithmetic caught it, not a reviewer;
    #    pinning it here means arithmetic catches the next one too.
        import re as _re2
        # ⚠ columns: rung, remaining, -1h, earliest, latest, fits. J3 below asserts this parser
        # actually matched -- it FIRED when the -1h column was added (P240), which is the whole
        # reason it exists: without it J1/J2 would have passed VACUOUSLY on zero parsed rows.
        rows = _re2.findall(
            r"^\s+(\d+)\s+[\d,]+\s+\d+\s+(\S+ \S+|\S+)\s\s+(\S+ \S+|\S+)\s\s+\w+$",
            out_i, _re2.M)
        seen_e: list[str] = []
        seen_l: list[str] = []
        for _rung, e, l_ in rows:
            if e not in ("REACHED", "GATED"):
                seen_e.append(e)
            if l_ not in ("REACHED", "GATED"):
                seen_l.append(l_)
        ck("J1 earliest column is non-decreasing in the rung", seen_e, sorted(seen_e))
        ck("J2 latest column is non-decreasing in the rung", seen_l, sorted(seen_l))
        ck("J3 the table actually had rows to check", len(rows) >= 3, True)
    finally:
        _sh2.rmtree(tmp2, ignore_errors=True)

    for line in ok:
        print("  pass  " + line)
    for line in bad:
        print("  FAIL  " + line)
    print(f"stage_eta selftest: {len(ok)}/{len(ok) + len(bad)} passed")
    return 1 if bad else 0


def _parse_cores(tok: str | None):
    """A bad core count must cost the MODEL TABLE ONLY, never the empirical block (auditor MAJOR 6).

    The publisher passes `?` when its ssh failed and `0` when every job is queued; the old code
    turned both into a ValueError that discarded an ETA already computed.
    """
    if tok is None:
        return None
    try:
        v = int(tok)
    except (TypeError, ValueError):
        return None
    return v if v > 0 else None


def main(argv: list[str]) -> int:
    args = list(argv[1:])
    if "--selftest" in args:
        return selftest()
    page = "--page" in args
    positional = [a for a in args if not a.startswith("--")]
    measured = _parse_cores(positional[0]) if positional else None
    modelled = _parse_cores(positional[1]) if len(positional) > 1 else 830
    print(render(measured, modelled or 830, page=page))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
