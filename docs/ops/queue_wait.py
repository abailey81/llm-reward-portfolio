"""QUEUE WAIT — the term every ETA this campaign has produced was missing.

WHY THIS FILE EXISTS
--------------------
On 2026-08-06 a falsification test on the `c1` floor found that its round-1 jobs were submitted
**Aug 4 22:19Z** and did not start until **Aug 6 04:58Z** — a 30.6 h wait. Measured across all 99
running jobs at that moment:

    min 28.0h   p25 32.2h   MEDIAN 32.6h   p75 33.3h   max 37.3h
    under 1h: 0 (0%)   ·   over 24h: 99 (100%)   ·   over 30h: 97 (98%)

**Not one job started in under 28 hours.** And a grep for `submission_time` across `docs/ops/**`
and `docs/analysis/**` returned NOTHING: no instrument anywhere modelled this. The plan of record
put rung 30 at ~00:01Z on 7 August, derived as *"round 1 drains ~14:53Z, then round 2 runs
~9.12 h"* — a model with **no queue-wait term at all**. Against a 32.6 h median that lands ~8-9
August instead. A ~40 h error in the campaign's single most important forecast.

⚠ THE LESSON, AND IT IS THE REASON THIS IS AN INSTRUMENT RATHER THAN A NOTE. RUN 25 re-derived the
rung-30 date every pass, got 00:01Z every time, and read the stability as evidence of correctness.
The inputs WERE stable. The MODEL was missing a term worth thirty hours. **Re-deriving a number
every pass does not validate the model the number comes from** — only a term the model does not
have can hide there.

WHAT QUEUE WAIT ACTUALLY MEASURES
---------------------------------
It is our ticket rank made visible. Dispatch order on Myriad is decided ENTIRELY by `ntckts`
(`weight_urgency=0`, so waiting time itself earns nothing; `prior = 4.0*npprior + 1.5*ntckts`,
confirmed exact to 5 dp on a live job). `share_functional_shares=TRUE` divides our ticket pool
among our CONTENDING jobs, so a deep queue lowers every one of our jobs' rank at once. A 32 h wait
is what that looks like from the outside.

⇒ Two consequences the campaign runs on:
  * **THE FLOOR.** Its ETA is `round-1 drain + QUEUE WAIT + wall`, never `drain + wall`.
  * **THE DURATION LEVER.** If every job pays a ~32 h toll regardless of size, a job that runs 18 h
    instead of 9 h amortises that toll over twice the work. That is additive to the reason the
    lever was adopted (holding cores longer at a fair-share-capped acquisition rate).

USAGE
    python docs/ops/queue_wait.py                 # measure + the honest floor ETA
    python docs/ops/queue_wait.py --selftest      # no cluster needed
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SSH_TIMEOUT_SECS = 180
#: The measured baseline, 2026-08-06 13:46Z, n=99 running jobs. Quoted so a later reading can be
#: compared against it rather than against a memory. RE-MEASURE; never trust this constant.
BASELINE_MEDIAN_H = 32.6
#: Median SUCCESSFUL task wall, from the epilogue population. The other term in the floor ETA.
TASK_WALL_H = 9.12

_SUBMIT = re.compile(r"^submission_time:\s+(.+?)\s*$")
_JOBNUM = re.compile(r"^job_number:\s+(\d+)\s*$")
_OWNER = re.compile(r"^owner:\s+(\S+)\s*$")


# ---------------------------------------------------------------------------------------------
# pure parsing (the selftest pins all of it — no cluster required)
# ---------------------------------------------------------------------------------------------
def parse_submissions(text: str, owner: str) -> dict[str, _dt.datetime]:
    """`qstat -j '*'` -> {job_id: submission datetime} for OWNER only.

    ⚠ The record is a BLOCK, and job_number/owner/submission_time can appear in any order within
    it, so this accumulates a block and commits it at the next `job_number:`. Parsing line-by-line
    with a "current id" would mis-attribute whenever submission_time precedes job_number.
    """
    out: dict[str, _dt.datetime] = {}
    jid = own = None
    sub: _dt.datetime | None = None

    def commit() -> None:
        if jid and own == owner and sub is not None:
            out[jid] = sub

    for line in text.splitlines():
        m = _JOBNUM.match(line)
        if m:
            commit()
            jid, own, sub = m.group(1), None, None
            continue
        m = _OWNER.match(line)
        if m:
            own = m.group(1)
            continue
        m = _SUBMIT.match(line)
        if m:
            try:
                sub = _dt.datetime.strptime(" ".join(m.group(1).split()), "%a %b %d %H:%M:%S %Y")
            except ValueError:
                sub = None
    commit()
    return out


def parse_running(text: str) -> list[tuple[str, str, _dt.datetime]]:
    """`qstat -u <me> -s r` -> [(job_id, name, start datetime)]. Skips anything unparseable."""
    rows: list[tuple[str, str, _dt.datetime]] = []
    for line in text.splitlines()[2:]:
        f = line.split()
        if len(f) < 7 or not f[0].isdigit():
            continue
        try:
            start = _dt.datetime.strptime(f[5] + " " + f[6], "%m/%d/%Y %H:%M:%S")
        except ValueError:
            continue
        rows.append((f[0], f[2], start))
    return rows


def line_of(job_name: str) -> str:
    """`leg10_leg_kimi_k3_sweep_t1_p18` -> `leg10`; `c1_bayes_opt_test_p01` -> `c1`.

    ⚠ qstat TRUNCATES the name column to ten characters, so this must work on `leg10_leg_` and on
    `c1_bayes_o` alike. Splitting on the first underscore is the only field that survives that.
    """
    return job_name.split("_", 1)[0] or "?"


def quantiles(vals: list[float]) -> dict[str, float]:
    """min/p25/median/p75/max over a NON-EMPTY list. Raises on empty rather than returning zeros —
    a zero-filled summary of no data reads exactly like a fleet with no queue wait."""
    if not vals:
        raise ValueError("quantiles() on an empty sample: report 'no data', never zeros")
    s = sorted(vals)
    n = len(s)

    def q(p: float) -> float:
        return s[min(n - 1, int(n * p))]

    return {"n": float(n), "min": s[0], "p25": q(0.25), "med": q(0.50),
            "p75": q(0.75), "max": s[-1]}


def floor_eta(last_round1_start: _dt.datetime, queue_wait_h: float,
              wall_h: float = TASK_WALL_H) -> _dt.datetime:
    """When rung 30 actually lands.

    ``round-1 drain`` + ``QUEUE WAIT for round 2`` + ``one wall``. The middle term is the one the
    plan of record omitted; with it set to zero this reproduces the old ~00:01Z answer exactly,
    which is how the selftest demonstrates the size of the error.
    """
    return last_round1_start + _dt.timedelta(hours=wall_h + queue_wait_h + wall_h)


# ---------------------------------------------------------------------------------------------
# live
# ---------------------------------------------------------------------------------------------
def _ssh(host: str, cmd: str) -> str:
    p = subprocess.run(["ssh", "-o", "BatchMode=yes", host, cmd],
                       capture_output=True, encoding="utf-8", errors="replace",
                       timeout=SSH_TIMEOUT_SECS)
    if p.returncode not in (0, 1):
        raise RuntimeError("ssh rc=%d" % p.returncode)
    return p.stdout


def report(host: str = "myriad", owner: str = "ucestes") -> int:
    # ONE round trip. `qstat -j '*'` is the whole cluster (~5,400 records, ~4 s) but it is the only
    # way to get submission times in a single call, and SSH load measurably pushes the campaign's
    # own cycle sweep toward its 900 s cap.
    try:
        blob = _ssh(host, "qstat -u %s -s r; echo '===SPLIT==='; qstat -j '*'" % owner)
    except Exception as exc:  # noqa: BLE001
        print("CANNOT DECIDE -- transport: %s" % repr(exc)[:90])
        return 2
    if "===SPLIT===" not in blob:
        print("CANNOT DECIDE -- malformed response (no split marker)")
        return 2
    run_txt, sub_txt = blob.split("===SPLIT===", 1)

    running = parse_running(run_txt)
    subs = parse_submissions(sub_txt, owner)
    joined = [(jid, nm, (st - subs[jid]).total_seconds() / 3600.0)
              for jid, nm, st in running if jid in subs]

    print("=== QUEUE WAIT -- the term every ETA in this campaign was missing ===")
    if not joined:
        print("no running job could be joined to a submission time -- reporting nothing "
              "rather than guessing (%d running, %d submissions seen)" % (len(running), len(subs)))
        return 2

    waits = [w for _, _, w in joined]
    q = quantiles(waits)
    print("  n=%d running jobs joined to a submission time (%d running, %d unmatched)"
          % (len(joined), len(running), len(running) - len(joined)))
    print("  min=%.1fh  p25=%.1fh  MEDIAN=%.1fh  p75=%.1fh  max=%.1fh"
          % (q["min"], q["p25"], q["med"], q["p75"], q["max"]))
    for label, pred in (("under 1h", lambda w: w < 1), ("over 12h", lambda w: w > 12),
                        ("over 24h", lambda w: w > 24)):
        k = sum(1 for w in waits if pred(w))
        print("    %-9s %3d (%3.0f%%)" % (label, k, 100.0 * k / len(waits)))
    print("  baseline 2026-08-06 13:46Z: median %.1fh  =>  %s"
          % (BASELINE_MEDIAN_H,
             "IMPROVED" if q["med"] < BASELINE_MEDIAN_H * 0.9 else
             "WORSE" if q["med"] > BASELINE_MEDIAN_H * 1.1 else "unchanged"))

    print("\n--- per line (a line's wait IS its ticket rank made visible) ---")
    by: dict[str, list[float]] = {}
    for _, nm, w in joined:
        by.setdefault(line_of(nm), []).append(w)
    for ln in sorted(by, key=lambda k: -quantiles(by[k])["med"]):
        qq = quantiles(by[ln])
        print("  %-8s n=%3d  median=%5.1fh  (min %.1f, max %.1f)"
              % (ln, int(qq["n"]), qq["med"], qq["min"], qq["max"]))

    c1 = [(nm, w) for _, nm, w in joined if line_of(nm) == "c1"]
    if c1:
        print("\n--- THE FLOOR (c1) ---")
        for nm, w in sorted(c1, key=lambda r: r[1]):
            print("  %-12s waited %.1fh" % (nm, w))
        last = max(st for _, nm, st in running if line_of(nm) == "c1")
        # ⚠ EVERY TIME BELOW IS HOST-LOCAL (+0100), because that is what qstat prints and this
        # derives from it. Saying so on every line is not clutter: the campaign's clock convention
        # has been misread before, and a floor date is exactly the number nobody may misread.
        print("\n--- RUNG 30, both models, so the omitted term is visible (all times HOST-LOCAL, "
              "+0100 -- subtract 1 h for UTC) ---")
        print("  round-1 last start        : %s" % last.strftime("%Y-%m-%d %H:%M:%S"))
        print("  OLD model (drain + wall)  : %s   <- NO queue term. This is the plan of record."
              % floor_eta(last, 0.0).strftime("%Y-%m-%d %H:%M"))
        print("  with the MEASURED wait    : %s   <- if round 2 queues like everything else"
              % floor_eta(last, q["med"]).strftime("%Y-%m-%d %H:%M"))
        print("  with a CONCENTRATED wait  : %s   <- if the ticket hold collapses it to ~1h"
              % floor_eta(last, 1.0).strftime("%Y-%m-%d %H:%M"))
        print("  ⇒ the gap between the last two IS the value of holding the sweep: %.1f hours."
              % (q["med"] - 1.0))
    return 0


# ---------------------------------------------------------------------------------------------
def selftest() -> int:
    fails: list[str] = []
    ran = [0]

    def ck(name, got, want):
        ran[0] += 1
        if got != want:
            fails.append("%s: got %r want %r" % (name, got, want))

    # --- parse_submissions: the block-ordering hazard that a line-by-line parser gets wrong -----
    blob = (
        "job_number:                 91237\n"
        "owner:                      ucestes\n"
        "submission_time:            Tue Aug  4 23:19:34 2026\n"
        "job_number:                 91238\n"
        "submission_time:            Wed Aug  5 00:01:12 2026\n"   # submit BEFORE owner
        "owner:                      ucestes\n"
        "job_number:                 91239\n"
        "owner:                      someoneelse\n"
        "submission_time:            Wed Aug  5 00:02:00 2026\n"
    )
    subs = parse_submissions(blob, "ucestes")
    ck("both of our jobs are found", sorted(subs), ["91237", "91238"])
    ck("...including the one whose submit line PRECEDES its owner line",
       subs["91238"], _dt.datetime(2026, 8, 5, 0, 1, 12))
    ck("another user's job is excluded", "91239" in subs, False)
    # ⚠ THE MUTANT THIS KILLS: a parser that commits on `submission_time:` using a running "current
    # owner" attributes 91238 to whoever owned the PREVIOUS block. Here that is ucestes, so it
    # would look right; 91239's block proves the reverse case.
    ck("an unparseable date is dropped, not defaulted to now",
       parse_submissions("job_number: 1\nowner: ucestes\nsubmission_time: not a date\n",
                         "ucestes"), {})

    # --- parse_running: the ten-character truncation is real and load-bearing ------------------
    rtxt = ("job-ID  prior   name       user         state submit/start at     queue      slots\n"
            "------\n"
            "  91237 2.01456 c1_bayes_o ucestes      r     08/06/2026 05:58:48 Bran@n  8 1\n"
            "  90993 2.01515 leg10_leg_ ucestes      r     08/06/2026 05:07:22 Bran@n  8 1\n"
            "  bogus line that must not crash the parser\n"
            # ⚠ A SHORT junk line is the case that actually needs the length guard. Mutation
            # testing on 2026-08-06 showed that deleting `len(f) < 7` survived every assertion,
            # because the only junk fixture had EIGHT fields and was caught by the isdigit test
            # instead. A short line indexes f[5] and raises IndexError, which the `except
            # ValueError` around strptime does NOT catch -- so the parser would die on one
            # malformed qstat line rather than skip it.
            "  a b c\n"
            # ⚠ AND THE CASE THAT ACTUALLY NEEDS THE LENGTH GUARD: a line that DOES start with a
            # digit but is short (a truncated read under a transport blip). The isdigit test lets
            # it through, f[5] raises IndexError, and `except ValueError` does not catch that -- so
            # without `len(f) < 7` the parser dies on one malformed line instead of skipping it.
            "  91240 2.01 c1_short\n")
    rows = parse_running(rtxt)
    ck("two running rows parsed, all three kinds of junk skipped", len(rows), 2)
    ck("...start time is read from columns 6+7",
       rows[0][2], _dt.datetime(2026, 8, 6, 5, 58, 48))
    ck("line_of survives qstat's 10-char truncation (c1)", line_of("c1_bayes_o"), "c1")
    ck("line_of survives it for a leg too", line_of("leg10_leg_"), "leg10")
    ck("line_of on an untruncated name", line_of("leg10_leg_kimi_k3_sweep_t1_p18"), "leg10")

    # --- quantiles: must REFUSE an empty sample rather than return a zero-filled summary --------
    try:
        quantiles([])
        ck("empty sample raises", "no raise", "ValueError")
    except ValueError:
        ck("empty sample raises rather than reporting zeros", True, True)
    q = quantiles([1.0, 2.0, 3.0, 4.0])
    ck("median of 4 values", q["med"], 3.0)
    ck("min/max", (q["min"], q["max"]), (1.0, 4.0))

    # --- floor_eta: the whole point. Zero queue wait REPRODUCES the plan of record's answer, ----
    #     which is how the size of the omitted term is demonstrated rather than asserted.
    last = _dt.datetime(2026, 8, 6, 5, 46, 56)
    ck("with NO queue term this is the plan of record's ~00:0xZ on the 7th",
       floor_eta(last, 0.0).strftime("%Y-%m-%d %H:%M"), "2026-08-07 00:01")
    ck("with the MEASURED 32.6h wait it is two days later",
       floor_eta(last, 32.6).strftime("%Y-%m-%d %H:%M"), "2026-08-08 08:37")
    ck("...i.e. the omitted term is worth exactly the wait",
       round((floor_eta(last, 32.6) - floor_eta(last, 0.0)).total_seconds() / 3600.0, 1), 32.6)
    ck("a concentrated 1h wait keeps it on the 7th",
       floor_eta(last, 1.0).strftime("%Y-%m-%d %H:%M"), "2026-08-07 01:01")

    for f in fails:
        print("  " + f)
    print(("SELFTEST OK — %d assertions: block-ordered submission parsing, the 10-char truncation, "
           "empty-sample refusal, and the omitted queue term" % ran[0]) if not fails
          else "SELFTEST FAILED (%d)" % len(fails))
    return 1 if fails else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--host", default="myriad")
    p.add_argument("--owner", default="ucestes")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args(argv)
    return selftest() if a.selftest else report(a.host, a.owner)


if __name__ == "__main__":
    raise SystemExit(main())
