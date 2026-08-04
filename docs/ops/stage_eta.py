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
# ⚠ F5: the ceiling was a magic 568 repeated at seven sites, unlinked from RUNGS. A ladder change
# would have desynchronised the go-forward exclusion, the missing-unit pricing and the handover
# disclosure silently, and no assertion would have noticed. ONE source of truth.
CEILING = RUNGS[-1]
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


def _registered_arms(root: str, line: str) -> set:
    """Arms `line` is registered to run, from its `frozen*/` winner dirs (F11). Lower bound."""
    fp = os.path.join(root, "frozen" + line[len("test"):])
    if not os.path.isdir(fp):
        return set()
    return {x[: -len("-winner")] for x in os.listdir(fp) if x.endswith("-winner")}


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
            # ⚠ F11: ANY subdirectory used to become a registered unit. A stray `logs/` or marker
            # dir would then be priced as owing a FULL rung, and once `len(cells) > 71` the page
            # prints the nonsensical "N of the 71 registered units" with `missing` pinned at 0.
            # A real arm either HOLDS RECORDS or is a REGISTERED frozen winner; a stray dir is
            # neither. The same two-signal rule as S15's C6, deliberately, so the two instruments
            # cannot disagree about what an arm is.
            # ⚠ The test is on RECORDS HELD, not on directory naming. My first version required a
            # child matching `-s<N>`, which is the live archive's shape but not the only one this
            # walk supports -- it dropped every selftest fixture and six assertions failed at once.
            # A rule that reads the payload survives a layout it did not anticipate; a rule that
            # reads the filename does not.
            if not mts and arm not in _registered_arms(root, d):
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


def chain_remaining_days(root: str, floor_total: float) -> tuple[float | None, str]:
    """How much of the SERIAL DFO chain is genuinely LEFT, measured from the archive.

    ⚠ GEN-5 DEFECT (P245, found by an auditor 2026-08-03). This was
    ``max(0.0, floor_total - elapsed_d)`` -- pure wall-clock decay, which assumes the serial chain
    has been consuming time since LAUNCH and never checks that it has. Because elapsed (6.9 d)
    exceeded the 4.64 d floor, it returned exactly 0.00, the clamp in ``eta_from_rate`` became a
    no-op at every row, and the page printed *"critical-chain floor: 4.64 d total, 0.00 d still to
    run"* while ``search/bayes_opt`` held 26 of its 30 candidates and ``tpe`` 25 of 30. Four to five
    strictly-serial trainings -- about 0.9 d -- were reported as finished. Elapsed time is not
    progress; only records are.

    Counted in RECORDS against ``SERIAL_CHAIN_BUDGET``, never against ``SERIAL_CHAIN_STEPS``: that
    exact unit confusion is D27 (record s.101.2), where the sentinel read "cma_es 9/4" and declared
    the campaign's longest chain COMPLETE.

    Returns ``(days_left, note)``; ``days_left`` is **None** when the search tree cannot be read.
    A missing measurement must not be reported as zero remaining work -- that is the verdict-channel
    rule this file already learned once (P230/P232): reserve a value for "I could not tell".
    """
    from src.cluster.lanes import SERIAL_CHAIN_BUDGET, SERIAL_CHAIN_STEPS

    sp = os.path.join(root, "search")
    if not os.path.isdir(sp):
        return None, "search tree unreadable -- remaining chain UNKNOWN, NOT zero"

    # One serial step costs the same on every DFO arm (identical B*), so the binding arm's
    # step length prices them all.
    per_step_d = floor_total / max(1, max(SERIAL_CHAIN_STEPS.values()))

    worst_arm, worst_left = None, 0
    for arm, budget in sorted(SERIAL_CHAIN_BUDGET.items()):
        ap = os.path.join(sp, arm)
        if not os.path.isdir(ap):
            continue
        done = sum(1 for d in os.listdir(ap)
                   if os.path.isfile(os.path.join(ap, d, "record.json")))
        left = max(0, budget - done)
        if left > worst_left:
            worst_arm, worst_left = arm, left
    if worst_arm is None:
        return 0.0, "every DFO arm has spent its full candidate budget"
    return worst_left * per_step_d, (f"{worst_arm} owes {worst_left} of "
                                     f"{SERIAL_CHAIN_BUDGET[worst_arm]} candidates")


def render(measured: int | None, modelled: int = 830, root: str = DEFAULT_ROOT,
           page: bool = False) -> str:
    # ⚠ F9: THE WALK COMES FIRST, THEN THE CLOCK. Sampling `now_epoch` before walking a 30k-record
    # tree gives records that land DURING the walk an mtime greater than `now_epoch`: they are then
    # excluded from every window and from `k`, while still counting in `len(mts)` -- so they inflate
    # the backlog side and deflate the `-1h` decrement. Walking first makes every mtime we hold <=
    # the clock we compare it against. Small and self-limiting, but free to get right.
    cells = test_cells(root)

    # ⚠ ONE CLOCK, AND IT IS time.time(). See gen-2 defect 1.
    now_epoch = time.time()
    now = dt.datetime.utcfromtimestamp(now_epoch)
    elapsed_d = (now - LAUNCH).total_seconds() / 86400.0
    days_left = (STOP - now).total_seconds() / 86400.0
    tp = throughput(cells, now_epoch)
    on_disk = sum(len(m) for m in cells.values())

    chain = plan_lanes(rung=CEILING, cpu_cores=modelled, chain_threads=CHAIN_THREADS)
    floor_total = chain.critical_chain_days
    floor_left, floor_note = chain_remaining_days(root, floor_total)

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

    # ⚠ F8: THE COMPOSITION WARNING MUST DESCRIBE THE WINDOW THE ETA IS ACTUALLY PRICED FROM.
    # This was hardcoded to 12 h while `eh2` below falls back to 24 h when the 12 h window is empty
    # -- so in exactly the state where one line's dominance matters most, the warning went SILENT
    # while a 24 h-priced ETA was published. Resolved once, here, and reused for `eh2`.
    _rates = [(h, tp[h][1]) for h in WINDOWS_H if tp[h][0] > 0 and h >= MIN_ETA_WINDOW_H]
    eta_window_h = min(h for h, _ in _rates) if _rates else MIN_ETA_WINDOW_H
    conc = concentration(cells, now_epoch, eta_window_h)
    if conc:
        top, topn = conc[0]
        tot12 = sum(v for _, v in conc) or 1
        L.append(f"    {eta_window_h} h rate is {100.0 * topn / tot12:.0f}% from ONE line ({top}); "
                 f"{len(conc)} line(s) contributed at all")

    # ⚠ ETA BOUNDS COME ONLY FROM WINDOWS >= MIN_ETA_WINDOW_H (P237). Shorter windows are printed
    # above as a stall indicator and are deliberately NOT allowed to price the deadline: the arrival
    # quantum is a 15 h pack-8 job, so a 1 h reading measures the gap between bursts.
    rates = _rates   # F8: resolved once above so the concentration line and the ETA agree
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
            if k and (CEILING - len(mts)) <= PACK:
                ending += k
                ending_lines[d] = ending_lines.get(d, 0) + k
        if tot and ending:
            who = ", ".join(sorted(ending_lines, key=lambda x: -ending_lines[x])[:2])
            L.append(f"    !! {100.0 * ending / tot:.0f}% of the {eh} h window came from cell(s) now "
                     f"within {PACK} records of rung {CEILING} ({who}) -- that rate STOPS. The ETA below "
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
        # ⛔ SUPERSEDED BY P239b -- THE SEVEN LINES BELOW DESCRIBE CODE THAT NO LONGER EXISTS.
        # They are kept as the provenance of the next paragraph's correction, NOT as a description
        # of behaviour. The live divisors are FLEET-WIDE (see `fleet_rate`/`goforward_rate` ~20
        # lines down), and the go-forward test is against the fixed ceiling 568, never "toward R".
        # A reader who stops here concludes the columns are per-rung rates, which is exactly the
        # refuted model. Flagged by an auditor 2026-08-03 (it had been left unmarked once already).
        #   FAST(R) = records in the window that landed in cells still BELOW R
        #             -> work that actually reduces R's backlog; assumes perfect redirection
        #   SLOW(R) = records in the window from cells that still owe MORE THAN ONE PACK toward R
        #             -> cells that will keep reducing R after their current job; assumes none
        # ⇩ STILL LIVE (implemented in the GATED branch further down), unlike the two lines above:
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
                             for mts in cells.values() if (CEILING - len(mts)) > PACK) / eh2

        # ⚠⚠ THE CAPTION NOW DESCRIBES WHAT THE COLUMNS ACTUALLY COMPUTE (auditor, 2026-08-04).
        # It previously said `latest` "assumes the finishing line's slots are NOT reused", i.e. it
        # advertised a NO-REDIRECTION bound. It is not one: at the low rungs ~99% of that divisor
        # comes from cells hundreds of records ABOVE the rung, which can only contribute under
        # redirection. A genuine no-redirection bound is the per-cell max, and that is degenerate
        # here (45 of 51 owing cells produce nothing, so it is infinite for every rung). Rather than
        # publish a fourth model, BOTH columns are now labelled as what they are -- two fleet-rate
        # projections that differ only in whether near-complete cells are counted -- and the
        # Aug-27 column is explicitly NOT an assurance verdict.
        L.append("EMPIRICAL ETA -- BOTH columns divide total remaining by a FLEET-WIDE rate, so both")
        L.append("    assume freed slots are REDIRECTED to whatever still owes work. earliest uses")
        L.append(f"    the whole fleet ({fleet_rate:.0f} rec/h); latest excludes cells already within")
        L.append(f"    {PACK} of the ceiling ({goforward_rate:.0f} rec/h). Window {eh2} h.")
        L.append("    !! NEITHER IS AN UPPER BOUND. Without redirection the true bound is the")
        L.append("    slowest owing cell, which is INFINITE for every rung while most owing cells")
        L.append("    produce nothing -- see the stage-barrier line below. Read 'Aug-27?' as")
        L.append("    'is this plausible on current throughput', NOT as an assurance verdict.")
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
        gated_from: int | None = None   # F1: first gated rung; every higher rung inherits it
        for rung in RUNGS:
            rem, _missing = backlog(rung, cells)
            # how much this rung's backlog actually fell in the last hour
            # ⚠ CORRECTED (auditor, 2026-08-04). This was `if len(mts) <= rung`, which counts ALL of
            # a cell's window records when the cell ends at or below the rung and ZERO when the cell
            # CROSSED the rung inside the window. A record only reduces rung R's backlog if the cell
            # was below R when that record landed. Measured error at rung 279: printed 187 against a
            # true 229 (18% low), and a rung whose entire hour of progress came from crossing cells
            # printed 0 -- reintroducing the "reads frozen" appearance this column exists to remove.
            # For a cell now at length L with k records in the window, the count that reduced R is
            # min(k, R - (L - k)) floored at 0: the overlap of (L-k, L] with (-inf, R].
            d1 = 0
            for mts in cells.values():
                k = sum(1 for m in mts if lo1 <= m <= now_epoch)
                if k:
                    d1 += max(0, min(k, rung - (len(mts) - k)))
            if rem == 0:
                L.append(f"    {rung:>5}  {rem:>10,}  {d1:>6}  {'REACHED':<16}  {'REACHED':<16}  yes")
                continue
            # ⚠⚠ A ROW MAY ONLY BE DATED IF THE CELLS THAT OWE IT ARE ACTUALLY PRODUCING
            # (auditor, 2026-08-04). Both divisors are fleet-wide, which is what makes the table
            # monotonic -- but applying a fleet rate to a rung whose OWING cells are idle produces a
            # confident date for work that has not started. Measured: rung 30 was printed as landing
            # within ~3 hours while 14 of the 15 units owing it sat at ZERO behind the C1/C3 barrier,
            # mis-priced by 56-86x. That is the shape `WITHDRAWN_CLAIMS.md` W3 was withdrawn for.
            # So a rung whose owing cells produced NOTHING in the window is reported GATED rather
            # than dated: the honest statement is "waiting on a stage barrier", not a timestamp.
            owing_rate = sum(
                sum(1 for m in mts if lo2 <= m <= now_epoch)
                for mts in cells.values() if len(mts) < rung) / eh2
            # ⚠⚠ F1 — GATED IS ABSORBING UPWARD, AND WITHOUT THIS THE TABLE COULD CONTRADICT ITSELF.
            # `owing_rate` is computed per rung, so a LOW rung whose few owing cells are idle gates
            # while a HIGHER rung, which has the busy cells below it too, gets a confident date.
            # Reaching rung 568 on every unit REQUIRES reaching rung 279 on every unit, so
            # "279 = waiting on a barrier" and "568 = a date" cannot both be true. Raised by an
            # auditor 2026-08-04; the shape was NOT live (every row was dated) but the monotonicity
            # assertions filter GATED rows out before comparing, so the selftest was blind to it BY
            # CONSTRUCTION and it would have shipped silently the first time the fleet composition
            # changed. Once gated, every higher rung is gated.
            if owing_rate <= 0 or gated_from is not None:
                if gated_from is None:
                    gated_from = rung
                tag = "barrier" if gated_from == rung else f"barrier>={gated_from}"
                L.append(f"    {rung:>5}  {rem:>10,}  {d1:>6}  {'GATED':<16}  {'GATED':<16}  "
                         f"{tag}")
                continue
            # An UNKNOWN chain floor must not silently become a zero clamp.
            clamp = 0.0 if floor_left is None else floor_left
            e_fast, _ = eta_from_rate(rem, fleet_rate, now, clamp)
            e_slow, _ = eta_from_rate(rem, goforward_rate, now, clamp)
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
        _, missing = backlog(CEILING, cells)
        if missing:
            # ⚠⚠ F6 -- THE ONE ASYMMETRY IN THIS TABLE, STATED RATHER THAN LEFT IMPLIED. A missing
            # unit has no directory, so it is NOT in `cells`; it contributes its FULL rung to every
            # row's `remaining`, and it can NEVER contribute to `owing_rate`. The gate therefore
            # cannot see it: a rung can be dated off the cells that do exist while a share of its
            # priced backlog belongs to units that have produced nothing BY DEFINITION and are not
            # merely idle. Gating on it was considered and REJECTED -- with 8 units missing it would
            # gate every rung at every hour and the table would carry no information at all (the
            # same degeneracy that killed the per-cell max). So the bound is stated instead, and it
            # is one-sided in a known direction: both columns are OPTIMISTIC by exactly this much.
            L.append(f"    (+{missing} registered unit(s) have no directory yet; each owes a FULL "
                     f"rung and is counted in 'remaining' above)")
            L.append(f"    !! those {missing} unit(s) are NOT in the rate's denominator and CANNOT "
                     f"be -- they have produced nothing at all, so no window contains them.")
            L.append("       Both columns are OPTIMISTIC by that share until those units start.")

        # ⚠ THE STAGE-BARRIER DISCLOSURE (auditor F3). A large share of the backlog can sit on a line
        # that has not entered C4 at all -- the core line's 9 arms plus the 11 H1 canon arms are
        # gated by the serial C1 DFO chain AND the C3 review gate (src/cluster/campaign.py), so NO
        # amount of redirected throughput starts them. Measured when this was written: 10,910 of
        # 32,106 records (34%) were behind that barrier while both ETA columns implicitly assumed it
        # could begin immediately. Reported as a share of the rung-568 backlog that produced NOTHING
        # in the window, which is the observable proxy for "not started".
        idle_rem = sum(max(0, CEILING - len(mts)) for mts in cells.values()
                       if not any(lo2 <= m <= now_epoch for m in mts))
        rem568, miss568 = backlog(CEILING, cells)
        idle_rem += miss568 * CEILING
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
    left_txt = "UNKNOWN" if floor_left is None else f"{floor_left:.2f} d"
    L.append(f"    critical-chain floor: {floor_total:.2f} d total, {left_txt} still to run"
             f"   ({floor_note})")
    L.append("    (measured from candidate RECORDS on disk, never from elapsed wall-clock -- P245)")
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

    # A0. THE CHAIN FLOOR IS MEASURED FROM RECORDS, NOT FROM ELAPSED WALL-CLOCK (P245).
    # Every case here FAILS against the pre-fix `max(0.0, floor_total - elapsed_d)`, which
    # returned exactly 0.00 once elapsed exceeded the floor no matter what was on disk.
    import tempfile as _tf
    from src.cluster.lanes import SERIAL_CHAIN_BUDGET as _BUD
    with _tf.TemporaryDirectory() as _td:
        _sp = os.path.join(_td, "search")
        for _arm, _done in (("bayes_opt", 26), ("cma_es", 29), ("tpe", 25)):
            for _c in range(_done):
                _d = os.path.join(_sp, _arm, f"{_arm}-c{_c}")
                os.makedirs(_d, exist_ok=True)
                with open(os.path.join(_d, "record.json"), "w", encoding="utf-8") as _fh:
                    _fh.write("{}")
        _left, _note = chain_remaining_days(_td, 4.64)
        # tpe owes 5 of 30, the worst of the three -> 5 steps at 4.64/25 d each.
        ck("A0a an UNFINISHED chain reports work LEFT, not 0.00", round(_left, 2),
           round(5 * 4.64 / 25.0, 2))
        ck("A0b and it names the arm that binds", "tpe owes 5 of 30 candidates" in _note, True)
        # Spend every budget: only NOW is the chain genuinely done.
        for _arm in _BUD:
            for _c in range(_BUD[_arm]):
                _d = os.path.join(_sp, _arm, f"{_arm}-c{_c}")
                os.makedirs(_d, exist_ok=True)
                with open(os.path.join(_d, "record.json"), "w", encoding="utf-8") as _fh:
                    _fh.write("{}")
        ck("A0c a FULLY SPENT budget reports 0.0", chain_remaining_days(_td, 4.64)[0], 0.0)
    with _tf.TemporaryDirectory() as _td:
        # No search tree at all: UNKNOWN, never 0. A missing measurement is not an answer.
        ck("A0d an unreadable search tree is None (UNKNOWN), NOT zero",
           chain_remaining_days(_td, 4.64)[0], None)
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
    # ⚠ F7: E1 WAS HOST-DEPENDENT AND FAILED EXACTLY WHERE THE DEFECT IS IMPOSSIBLE. On a host whose
    # local time IS UTC (the cluster, any CI box) `skew == 0.0`, so the suite reported a defect on
    # the one configuration that cannot have it. The TRAP is real and P235 is real; what varies is
    # only whether THIS host exhibits it. So the observation is reported, and the portable
    # invariant -- that the code does not USE utcnow().timestamp() -- is what gets asserted.
    skew = dt.datetime.utcnow().timestamp() - time.time()
    ck("E1 the host's utcnow() skew is measured, and either value is legitimate",
       isinstance(skew, float), True)
    if abs(skew) > 1.0:
        print("  note  this host DOES exhibit the P235 trap: utcnow().timestamp() - time.time() "
              "= %.1f s" % skew)
    else:
        print("  note  this host is on UTC, so the P235 trap is dormant here; E2-E5 are the "
              "portable control")
    # The precise, portable invariant: no WINDOW BOUND is ever built from utcnow(). Checking for
    # the bare substring was my own defect -- it matched this module's own docstring, which
    # DOCUMENTS the trap, and the line doing the checking. An assertion that fires on its own
    # explanation is a false positive generator.
    with open(os.path.abspath(__file__), encoding="utf-8") as _fh:
        _code = [ln for ln in _fh.read().splitlines()
                 if "utcnow" in ln and "=" in ln and not ln.lstrip().startswith("#")]
    _bound = [ln for ln in _code
              if any(ln.lstrip().startswith(v) for v in ("now_epoch", "lo1", "lo2", "base_t"))]
    ck("E1b NO window bound in this file is built from utcnow()", _bound, [])

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
        # A cell BELOW rung 30 that produces. Without it, rung 30 has no owing producer, gates,
        # and (since F1) absorbs every higher rung -- leaving J1/J2 comparing empty lists. Caught
        # by J3 failing the moment absorption landed, which is what J3 is for.
        low = os.path.join(tmp2, "test_leg_y", "placebo", "c0")
        os.makedirs(low)
        for i in range(20):
            p_ = os.path.join(low, f"r{i}")
            os.makedirs(p_)
            f_ = os.path.join(p_, "record.json")
            open(f_, "w", encoding="utf-8").close()
            aged = base_t - (2 * 3600 + (i / 20.0) * 9 * 3600)
            os.utime(f_, (aged, aged))
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
    except Exception as exc:  # noqa: BLE001
        # F10: section J had a bare `finally:` with no handler, so an exception here aborted the
        # whole selftest before the pass/fail summary printed -- inconsistent with F/G/H, and it
        # hides every other result behind one traceback.
        bad.append(f"J section raised: {type(exc).__name__}: {exc}")
    finally:
        _sh2.rmtree(tmp2, ignore_errors=True)

    # ---------------------------------------------------------------------------------------
    # K. THE GO-FORWARD EXCLUSION (F2). Untested until now, and worse than disclosed: DELETING the
    #    clause AND INVERTING it both scored 38/38, because the only fixture reaching it had a
    #    single cell, which made goforward_rate == fleet_rate either way.
    #
    #    The fixture separates them by construction: the NEAR-CEILING cell is the HIGH producer.
    #      correct  -> it is EXCLUDED, goforward is tiny, `latest` lands far after `earliest`
    #      deleted  -> goforward == fleet, latest == earliest                      -> CAUGHT
    #      inverted -> ONLY it is counted, goforward ~= fleet, latest ~= earliest  -> CAUGHT
    # ---------------------------------------------------------------------------------------
    tmp3 = _tf2.mkdtemp(prefix="stage_eta_goforward_")
    try:
        def _plant(arm, n_records, n_in_window):
            cand = os.path.join(tmp3, "test_leg_z", arm, "c0")
            os.makedirs(cand, exist_ok=True)
            base_t = time.time()
            for i in range(n_records):
                p = os.path.join(cand, f"r{i}")
                os.makedirs(p, exist_ok=True)
                f = os.path.join(p, "record.json")
                open(f, "w", encoding="utf-8").close()
                # the last n_in_window records sit inside the 12 h window; the rest are older
                aged = (base_t - (2 * 3600 + (i / max(1, n_records)) * 9 * 3600)
                        if i >= n_records - n_in_window else base_t - 40 * 3600)
                os.utime(f, (aged, aged))

        _plant("scalar", CEILING - PACK, 40)      # 560 records: CEILING-560 == PACK, so EXCLUDED
        _plant("distributional", 300, 2)          # 300 records: 268 > PACK, so INCLUDED
        _plant("placebo", 20, 2)                  # below rung 30, so rung 30 has an owing producer
        c4 = test_cells(tmp3)
        ck("K1 fixture: the near-ceiling cell is exactly at the exclusion boundary",
           sorted(len(m) for m in c4.values()), [20, 300, CEILING - PACK])
        out_k = render(1000, root=tmp3)
        rows_k = []
        # ⚠ ONLY the empirical table. The REGISTERED MODEL block below it ALSO prints rows whose
        # first token is a rung, and swallowing both is how L2 first reported six false rows.
        for ln in out_k.split("REGISTERED MODEL")[0].splitlines():
            parts = ln.split()
            if len(parts) >= 6 and parts[0].isdigit() and int(parts[0]) in RUNGS:
                # rung remaining -1h earliest_date earliest_time latest_date latest_time verdict
                if len(parts) >= 8 and parts[3][:2] == "20" and parts[5][:2] == "20":
                    rows_k.append((parts[3] + " " + parts[4], parts[5] + " " + parts[6]))
        ck("K2 the go-forward fixture produced dated rows", len(rows_k) >= 1, True)
        # ⚠ A0e -- render() must CONSUME chain_remaining_days(), not just have it available. The
        # mutation proof caught this: reverting the CALL SITE to `floor_total - elapsed_d` left
        # A0a-A0d passing, because they call the function directly. This fixture has no `search/`
        # tree, so an honest render says UNKNOWN; the elapsed formula would print a number.
        ck("A0e render() prices the chain from the archive -- no search tree means UNKNOWN",
           "UNKNOWN still to run" in out_k, True)
        if rows_k:
            e_k, l_k = rows_k[0]
            ck("K3 latest is STRICTLY later than earliest -- the exclusion is doing work "
               "(deleting OR inverting the predicate collapses this)", l_k > e_k, True)
            # ⚠ K4 IS A RATIO, NOT A GAP, AND THE MUTATION PROOF IS WHY. The first version asserted
            # "gap > 24 h", and the INVERTED predicate still cleared it: on a ~90-day horizon a
            # rate of 40 vs 44 still separates the two columns by days. Only the RATIO separates
            # the three cases. Fixture rates: fleet 44 in-window, correct go-forward 4 (the 560
            # cell excluded), inverted 40, deleted 44.
            #   correct  -> latest/earliest ~ 11      inverted -> ~1.1      deleted -> 1.0
            now_k = dt.datetime.utcfromtimestamp(time.time())
            he = (dt.datetime.strptime(e_k, "%Y-%m-%d %H:%M") - now_k).total_seconds()
            hl = (dt.datetime.strptime(l_k, "%Y-%m-%d %H:%M") - now_k).total_seconds()
            ck("K4 and the SEPARATION is large by ratio, which is the only thing that "
               "distinguishes the correct predicate from an inverted one",
               he > 0 and (hl / he) > 3.0, True)
    except Exception as exc:  # noqa: BLE001
        bad.append(f"K section raised: {type(exc).__name__}: {exc}")
    finally:
        _sh2.rmtree(tmp3, ignore_errors=True)

    # ---------------------------------------------------------------------------------------
    # L. GATED IS ABSORBING UPWARD (F1). A rung can only be reached if every lower rung is, so
    #    "279 waiting on a barrier" and "568 has a date" cannot both be true. The monotonicity
    #    assertions in J filter GATED rows OUT before comparing, so they are blind to this by
    #    construction -- which is why it needs its own check on the RENDERED text.
    # ---------------------------------------------------------------------------------------
    tmp4 = _tf2.mkdtemp(prefix="stage_eta_gated_")
    try:
        cand = os.path.join(tmp4, "test_leg_w", "scalar", "c0")
        os.makedirs(cand)
        base_t = time.time()
        # One cell ABOVE rung 30 with all its production inside the window: the cells owing rung 30
        # produce nothing, so rung 30 gates, while higher rungs see this cell and would be dated.
        for i in range(120):
            p = os.path.join(cand, f"r{i}")
            os.makedirs(p)
            f = os.path.join(p, "record.json")
            open(f, "w", encoding="utf-8").close()
            aged = base_t - (2 * 3600 + (i / 120.0) * 9 * 3600)
            os.utime(f, (aged, aged))
        out_l = render(1000, root=tmp4)
        states = []
        for ln in out_l.split("REGISTERED MODEL")[0].splitlines():
            parts = ln.split()
            if len(parts) >= 4 and parts[0].isdigit() and int(parts[0]) in RUNGS:
                states.append((int(parts[0]), "GATED" in ln, "REACHED" in ln))
        ck("L1 the gated fixture produced a full ladder", len(states) == len(RUNGS), True)
        first_gate = next((r for r, g, _ in states if g), None)
        if first_gate is not None:
            after = [(r, g) for r, g, reached in states if r > first_gate and not reached]
            ck(f"L2 once rung {first_gate} is GATED, every higher rung is GATED too "
               "(a lower barrier cannot coexist with a higher date)",
               [r for r, g in after if not g], [])
        else:
            ok.append("L2 no rung gated on this fixture -- absorption vacuously holds")
    except Exception as exc:  # noqa: BLE001
        bad.append(f"L section raised: {type(exc).__name__}: {exc}")
    finally:
        _sh2.rmtree(tmp4, ignore_errors=True)

    # ⚠ F15 (found by this selftest failing to report its own failure, 2026-08-04). A `ck` value can
    # carry RENDERED page text, and rendered text contains non-ASCII. The console here is cp1251, so
    # printing such a line raised UnicodeEncodeError INSIDE the reporter -- the run died with a
    # traceback and NOT ONE pass/fail line, so a failing selftest could not tell anyone what failed.
    # A reporter that crashes on the content it exists to report is the worst possible failure mode.
    def _ascii(s: str) -> str:
        return str(s).encode("ascii", "backslashreplace").decode("ascii")

    # ---------------------------------------------------------------------------------------
    # M. THE UNTESTED SURFACE (F3, F4, F8, F11). Every one of these was reachable-but-unasserted,
    #    which is the same class as F2: code that runs in production and that no mutation would
    #    disturb. `_parse_cores` in particular carries a PRODUCTION contract -- publish_status.sh
    #    passes `?` when its ssh failed and `0` when everything is queued.
    # ---------------------------------------------------------------------------------------
    ck("M1 _parse_cores: '?' is None, not a crash (publish_status.sh passes it on ssh failure)",
       _parse_cores("?"), None)
    ck("M2 _parse_cores: '0' is None (every job queued is not 'zero cores are usable')",
       _parse_cores("0"), None)
    ck("M3 _parse_cores: a negative is None", _parse_cores("-4"), None)
    ck("M4 _parse_cores: None in, None out", _parse_cores(None), None)
    ck("M5 _parse_cores: a real count survives", _parse_cores("1632"), 1632)

    _now = 1_000_000.0
    _cells_c = {("test_leg_a", "x"): [_now - 600, _now - 1200],
                ("test_leg_a", "y"): [_now - 900],
                ("test_leg_b", "x"): [_now - 300],
                ("test_leg_c", "x"): [_now - 99 * 3600]}   # outside any window
    ck("M6 concentration sums per LINE and sorts descending",
       concentration(_cells_c, _now, 12), [("test_leg_a", 3), ("test_leg_b", 1)])
    ck("M7 concentration drops lines with zero in-window records rather than listing them at 0",
       [k for k, _ in concentration(_cells_c, _now, 12)], ["test_leg_a", "test_leg_b"])
    ck("M8 a wider window pulls the old line back in",
       dict(concentration(_cells_c, _now, 120)).get("test_leg_c"), 1)

    tmp5 = _tf2.mkdtemp(prefix="stage_eta_stray_")
    try:
        real = os.path.join(tmp5, "test_leg_q", "scalar", "scalar-s0")
        os.makedirs(real)
        open(os.path.join(real, "record.json"), "w", encoding="utf-8").close()
        os.makedirs(os.path.join(tmp5, "test_leg_q", "logs"))          # a stray dir
        os.makedirs(os.path.join(tmp5, "test_leg_q", "_scratch"))      # another
        c5 = test_cells(tmp5)
        ck("M9 F11: a stray subdirectory is NOT promoted to a registered unit",
           sorted(a for _, a in c5), ["scalar"])
        # ...but a REGISTERED arm with no records still counts, because it genuinely owes a rung
        os.makedirs(os.path.join(tmp5, "frozen_leg_q", "distributional-winner"))
        os.makedirs(os.path.join(tmp5, "test_leg_q", "distributional"))
        c5b = test_cells(tmp5)
        ck("M10 F11: but a REGISTERED arm holding no records IS still a unit",
           sorted(a for _, a in c5b), ["distributional", "scalar"])
    except Exception as exc:  # noqa: BLE001
        bad.append(f"M stray section raised: {type(exc).__name__}: {exc}")
    finally:
        _sh2.rmtree(tmp5, ignore_errors=True)

    # F8 -- the composition warning must name the window the ETA is PRICED from. A fixture whose
    # 12 h window is EMPTY but whose 24 h window is busy is the exact state where the hardcoded 12
    # went silent while a 24 h-priced ETA was published.
    tmp7 = _tf2.mkdtemp(prefix="stage_eta_window24_")
    try:
        cand7 = os.path.join(tmp7, "test_leg_s", "scalar", "c0")
        os.makedirs(cand7)
        base7 = time.time()
        for i in range(60):
            q = os.path.join(cand7, f"r{i}")
            os.makedirs(q)
            f7 = os.path.join(q, "record.json")
            open(f7, "w", encoding="utf-8").close()
            aged = base7 - (13 * 3600 + (i / 60.0) * 10 * 3600)   # 13-23 h ago: 12 h window EMPTY
            os.utime(f7, (aged, aged))
        c7 = test_cells(tmp7)
        tp7 = throughput(c7, time.time())
        ck("M13 fixture: the 12 h window is empty and the 24 h window is busy",
           (tp7[12][0], tp7[24][0] > 0), (0, True))
        out_w = render(1000, root=tmp7)
        ck("M14 F8: the concentration line names the 24 h window the ETA is actually priced from",
           "24 h rate is" in out_w, True)
        ck("M15 F8: and never claims 12 h when the 12 h window held nothing",
           "12 h rate is" in out_w, False)
    except Exception as exc:  # noqa: BLE001
        bad.append(f"M window section raised: {type(exc).__name__}: {exc}")
    finally:
        _sh2.rmtree(tmp7, ignore_errors=True)

    # F3 -- the EXACT -1h decrement on a cell that CROSSES the rung inside the hour. Both older
    # fixtures had an empty 1 h window by construction, so `d1` was identically 0 everywhere and
    # `d1 = 0` scored full marks. A cell at 32 with 5 records in the hour was at 27 an hour ago:
    # rung 30 saw its backlog fall by 3 (30-27), rung 100 by the full 5.
    tmp6 = _tf2.mkdtemp(prefix="stage_eta_d1_")
    try:
        cand6 = os.path.join(tmp6, "test_leg_r", "scalar", "c0")
        os.makedirs(cand6)
        base6 = time.time()
        for i in range(32):
            q = os.path.join(cand6, f"r{i}")
            os.makedirs(q)
            f6 = os.path.join(q, "record.json")
            open(f6, "w", encoding="utf-8").close()
            aged = base6 - (600 if i >= 27 else 5 * 3600)   # last 5 inside the hour
            os.utime(f6, (aged, aged))
        out_m = render(1000, root=tmp6).split("REGISTERED MODEL")[0]
        d1 = {}
        for ln in out_m.splitlines():
            pr = ln.split()
            if len(pr) >= 3 and pr[0].isdigit() and int(pr[0]) in RUNGS:
                d1[int(pr[0])] = int(pr[2].replace(",", ""))
        ck("M11 F3: a cell CROSSING rung 30 in the hour reports the crossing part only", d1.get(30), 3)
        ck("M12 F3: and a rung it is entirely below reports the full 5", d1.get(100), 5)
    except Exception as exc:  # noqa: BLE001
        bad.append(f"M d1 section raised: {type(exc).__name__}: {exc}")
    finally:
        _sh2.rmtree(tmp6, ignore_errors=True)

    for line in ok:
        print("  pass  " + _ascii(line))
    for line in bad:
        print("  FAIL  " + _ascii(line))
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
