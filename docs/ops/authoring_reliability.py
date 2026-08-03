"""AUTHORING RELIABILITY - the per-model reject rate, read from the COMPLETE failure record.

WHY THIS EXISTS (2026-08-03, RUN 17, execution record s.125).

"Which models can write executable objective code at all" is a NAMED deliverable of this study
(the per-model authoring-reliability table; Raad/Stefan point 5, and the empirical half of the
registered numeracy-bottleneck prediction R87). The number therefore has to be right.

The panel that has been quoted in every handover brief comes from
`scripts/campaign_guards.py::rejects_guard`, whose own module comment says it is "what should
actually be read". It computes

    reject_rate = len(<line>/_rejects/*.json) / (len(<line>/_rejects/*.json) + n_records)

and that has TWO defects, both MEASURED here rather than argued:

  1. THE `_rejects/` MARKER SET OMITS THE AUTHOR-SIDE REJECTIONS. Campaign-wide on 2026-08-03
     there were 191 markers against 272 permanent rows in `search*/*/failures.jsonl`. The 81
     missing rows are dominated by `author_reject: ast_gate (unsafe construct)` - a model emitting
     a construct outside our numpy allowlist - which is not a side issue but PRECISELY the
     "did the model write admissible reward code" signal the table claims to report. The
     understatement is NON-UNIFORM (gemini-2.5-flash 2.8% -> 7.9%, i.e. 2.8x; sonnet-5 unchanged
     at 0%), so it distorts the ORDERING of a capability gradient, not just its level.

  2. IT GLOBS `search_leg_*` ONLY, so the CONFIRMATORY CORE LINE (`search/`, author
     claude-opus-5) does not appear in the panel at all.

THE CONFIRMATORY ANALYSIS IS NOT AFFECTED, and that distinction is the whole point of writing this
down rather than alarming: `scripts/analyze_campaign.py::compute_accounting` already reads
`n_failed = _count_jsonl_lines(prov / "failures.jsonl")`, i.e. the complete record. The defect is
confined to the MONITORING layer - but the monitoring layer is what the handover briefs quote, so
an uncorrected number would reach the write-up through the documentation rather than through the
code.

`scripts/**` is DRIFT-FENCED while the campaign is live, so the guard is not edited; this file is
the corrected reading, and the fix to the guard is queued in `docs/DEFERRED_FIXES_RUN4.md`.

WHAT IT COUNTS, stated exactly so a passing run cannot be over-read:

    accepted  = candidate directories holding a record.json at EXACTLY <line>/<arm>/<cand>/,
                so the D18 nested duplicates (<cand>/<cand>/record.json) and the `.pull_tmp`
                staging dirs are both excluded by construction.
    failed    = rows of <line>/<arm>/failures.jsonl. Verified 2026-08-03: 272 rows, 272 distinct
                candidate_ids, zero duplicates, every row `permanent: true`.
    attempted = accepted + failed  -- the PER-ATTEMPT denominator, the same one
                `analyze_campaign.compute_accounting` uses.
    slots     = |candidate_ids of accepted UNION candidate_ids of failed| -- the PER-SLOT
                denominator, i.e. per REGISTERED CANDIDATE.

BOTH DENOMINATORS ARE PRINTED, because they are different questions and the per-attempt one is
biased HIGH. An independent auditor established (2026-08-03) that 17 candidate slots campaign-wide
carry BOTH a record.json and a permanent `author_reject` row: the slot was authored twice, with
different `reward_source` hashes. The proof is arithmetic, not inference -- the core line's
`placebo` reads 26 accepted + 7 failed = 33 against a REGISTERED BUDGET OF 30, and subtracting its
3 overlaps lands it exactly on 30. Every leg's slot count comes out at exactly 150 = 5 arms x 30
(nemotron 145, still mid-search). `PER-SLOT` is therefore the number to quote when the question is
"what fraction of its registered candidates did this model fail to deliver"; `PER-ATT%` is the
number to quote when the question is "what fraction of its authoring attempts failed".

!! AND `failures.jsonl` IS NOT A COMPLETE RECORD OF FAILURE *EVENTS* -- a claim this file made in its
first version and which the same auditor refuted. It is one row per candidate SLOT, latest attempt
wins: at least 16 node-reject EVENTS (15 qwen3.5-9b, 1 nemotron) exist only as a `_rejects/` marker
with no ledger row of their own, from a slot that was re-authored after a node reject that never got
ledgered. So the two sets are NOT nested in either direction, and neither is a superset of failure
events. What IS true, and is all this file needs, is that `failures.jsonl` holds every PERMANENT
per-slot outcome including the author-side ones the markers structurally cannot hold.

WHY A MARKER CAN NEVER EXIST FOR AN AUTHOR-SIDE REJECT -- the structural proof, which is stronger
than the counts: `_write_reject_marker` lives in `src/cluster/run_one.py:40-64` and runs ON THE NODE.
The author-side gate is DRIVER-side (`src/cluster/campaign.py:906-916`): it writes the ledger row and
`continue`s, so the candidate is never shipped to a node and no node ever runs to write a marker.

It also reports, per (line, arm), the LLM calls that hit our own 16,384-token output cap
(`stop_reason == "length"` in `llm_calls.jsonl`), because a candidate lost to OUR cap is an
instrument artefact rather than a capability datum - the standing analysis-time obligation
recorded against `guard:truncation` in `docs/ops/acknowledged_alarms.txt`.

EFFECT-BLIND BY CONSTRUCTION: it reads error strings, stop reasons and directory names. It never
opens `val_fitness`, `test_sharpe`, `test_cvar` or any performance quantity, and it never compares
arms on an outcome, so it cannot leak a treatment result.

FAILS LOUD ON AN EMPTY INPUT SET (exit 2). "Found nothing wrong" and "looked at nothing" are
indistinguishable in a green board and only one of them is true - P213/P197.

    python docs/ops/authoring_reliability.py
    python docs/ops/authoring_reliability.py --root <archive>
    python docs/ops/authoring_reliability.py --by-arm
    python docs/ops/authoring_reliability.py --selftest
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import tempfile

# docs/ops/authoring_reliability.py -> docs/ops -> docs -> repo. THREE dirname calls: taking two
# lands on `docs` and every path below points at a directory that does not exist, which is exactly
# how a new layer once reported CLEAN having inspected zero records (P213).
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_ROOT = os.path.join(REPO, "outputs", "campaign_cluster_run4")

#: The five LLM-authored arms. The core line also runs four derivative-free optimiser arms
#: (random_search, bayes_opt, cma_es, tpe) which author no code at all and must NOT enter an
#: authoring-reliability denominator.
LLM_ARMS = ("distributional", "scalar", "placebo", "scalar_cvar5", "placebo_shuffled")


def classify(error: str) -> str:
    """Bucket a `failures.jsonl` error string by WHERE the candidate died.

    AUTHOR-side means the model's own output never became a runnable reward: it tripped the AST
    gate, or no top-level `reward` binding could be parsed from the completion at all. NODE-side
    means admissible code that then failed when executed - it crashed in the sandbox, or it
    returned something that is not the registered `(total, components, state)` triple.

    Both are authoring failures for the purposes of the reliability table; the split matters
    because only the AUTHOR-side ones are missing from the `_rejects/` marker set.
    """
    e = str(error or "")
    if e.startswith("author_reject: ast_gate"):
        return "author_ast_gate"
    if e.startswith("author_reject: no top-level"):
        return "author_no_binding"
    if e.startswith("author_reject"):
        return "author_other"
    if "did not return an unpackable" in e:
        return "node_contract"
    return "node_sandbox"


def _accepted_ids(arm_dir: str) -> set:
    """Candidate dirs under `arm_dir` holding a record.json at EXACTLY one level down.

    Deliberately NOT `rglob`: a recursive walk re-admits the D18 nested duplicate
    (`<cand>/<cand>/record.json`) and the `.pull_tmp` staging copies, which is how ~20 instruments
    silently double-counted before D18 was found. Returns the candidate IDs, not just a count,
    because the per-SLOT denominator needs the set intersection with the failure ledger.
    """
    ids = set()
    try:
        entries = os.listdir(arm_dir)
    except OSError:
        return ids
    for d in entries:
        if d.startswith(".") or d.startswith("_"):
            continue
        if os.path.isfile(os.path.join(arm_dir, d, "record.json")):
            ids.add(d)
    return ids


def _read_jsonl(path: str) -> list:
    rows = []
    if not os.path.isfile(path):
        return rows
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            try:
                rows.append(json.loads(ln))
            except ValueError:
                # A torn append is a fact about the archive, not something to swallow silently.
                rows.append({"_torn": True, "error": ""})
    return rows


def scan(root: str) -> dict:
    """Per (line, arm) accepted / failed / failure-class / truncation counts, plus the marker count.

    Returns ``{"lines": {line: {...}}, "totals": {...}}``. Every count is an integer read from the
    filesystem; no value is inferred from another.
    """
    out = {"lines": {}, "totals": {"accepted": 0, "failed": 0, "markers": 0, "truncated": 0,
                                   "torn": 0, "slots": 0, "lost": 0, "reauthored": 0}}
    for line in sorted(os.listdir(root)):
        line_dir = os.path.join(root, line)
        if not line.startswith("search") or not os.path.isdir(line_dir):
            continue
        rec = {"arms": {}, "accepted": 0, "failed": 0, "markers": 0, "truncated": 0, "torn": 0,
               "classes": {}, "slots": 0, "lost": 0, "reauthored": 0}
        rec["markers"] = len(glob.glob(os.path.join(line_dir, "_rejects", "*.json")))
        for arm in sorted(os.listdir(line_dir)):
            arm_dir = os.path.join(line_dir, arm)
            if arm.startswith(("_", ".")) or not os.path.isdir(arm_dir):
                continue
            acc_ids = _accepted_ids(arm_dir)
            fails = _read_jsonl(os.path.join(arm_dir, "failures.jsonl"))
            calls = _read_jsonl(os.path.join(arm_dir, "llm_calls.jsonl"))
            fail_ids = {f.get("candidate_id") for f in fails if f.get("candidate_id")}
            torn = sum(1 for f in fails if f.get("_torn"))
            trunc = sum(1 for c in calls if str(c.get("stop_reason", "")).lower() == "length")
            cls = {}
            for f in fails:
                k = classify(f.get("error"))
                cls[k] = cls.get(k, 0) + 1
            # A slot the model was GIVEN. A slot that also holds a record was RE-AUTHORED after
            # its failure and is NOT a lost candidate -- counting it as one is what biases the
            # per-attempt rate high (core `placebo` reads 33 attempts against a budget of 30).
            reauth = len(acc_ids & fail_ids)
            rec["arms"][arm] = {"accepted": len(acc_ids), "failed": len(fails), "truncated": trunc,
                                "llm_calls": len(calls), "classes": cls, "torn": torn,
                                "slots": len(acc_ids | fail_ids), "lost": len(fail_ids - acc_ids),
                                "reauthored": reauth, "is_llm": arm in LLM_ARMS}
            if arm in LLM_ARMS:
                rec["accepted"] += len(acc_ids)
                rec["failed"] += len(fails)
                rec["truncated"] += trunc
                rec["torn"] += torn
                rec["slots"] += len(acc_ids | fail_ids)
                rec["lost"] += len(fail_ids - acc_ids)
                rec["reauthored"] += reauth
                for k, v in cls.items():
                    rec["classes"][k] = rec["classes"].get(k, 0) + v
        if rec["arms"]:
            out["lines"][line] = rec
            for k in ("accepted", "failed", "markers", "truncated", "torn", "slots", "lost",
                      "reauthored"):
                out["totals"][k] += rec[k]
    return out


def _rate(failed: int, accepted: int) -> float:
    att = failed + accepted
    return (failed / att) if att else 0.0


def report(scanned: dict, by_arm: bool = False) -> int:
    """Print the table. Returns 0 clean, 2 if the input set was EMPTY or an archive row was torn."""
    lines = scanned["lines"]
    if not lines:
        print("*** NO SEARCH LINES FOUND. This check inspected NOTHING and is therefore VACUOUS.")
        print("    A vacuous pass banks a property that was never tested (P197/P213). Exiting 2.")
        return 2
    if scanned["totals"]["accepted"] + scanned["totals"]["failed"] == 0:
        print("*** ZERO candidates and ZERO failures across every line. Nothing was inspected.")
        return 2

    print("=== PER-MODEL AUTHORING RELIABILITY (LLM arms only) ===")
    print("  PER-SLOT% = lost registered candidates / registered slots  <- quote THIS one")
    print("  PER-ATT%  = failure rows / (accepted + failure rows)       <- biased HIGH by re-authoring")
    print("  guard%    = what scripts/campaign_guards.py::rejects_guard prints (markers only)")
    print()
    print("%-32s %6s %6s %6s %8s %8s | %7s %7s %7s %7s | %7s %5s" % (
        "line", "slots", "lost", "accept", "PER-SLOT", "PER-ATT",
        "authAST", "authNoB", "nodeSbx", "nodeCtr", "guard%", "trunc"))
    rows = []
    for line, rec in sorted(lines.items(), key=lambda kv: _rate(kv[1]["lost"], kv[1]["slots"] - kv[1]["lost"])):
        c = rec["classes"]
        slot_rate = 100.0 * (rec["lost"] / rec["slots"]) if rec["slots"] else 0.0
        att_rate = 100.0 * _rate(rec["failed"], rec["accepted"])
        # The guard's own arithmetic, reproduced so the gap is visible rather than asserted.
        # It counts markers over (markers + records) and never restricts to the LLM arms.
        all_acc = sum(a["accepted"] for a in rec["arms"].values())
        guard_rate = 100.0 * _rate(rec["markers"], all_acc)
        rows.append((line, slot_rate, guard_rate))
        print("%-32s %6d %6d %6d %7.2f%% %7.2f%% | %7d %7d %7d %7d | %6.2f%% %5d" % (
            line, rec["slots"], rec["lost"], rec["accepted"], slot_rate, att_rate,
            c.get("author_ast_gate", 0), c.get("author_no_binding", 0) + c.get("author_other", 0),
            c.get("node_sandbox", 0), c.get("node_contract", 0), guard_rate, rec["truncated"]))

    t = scanned["totals"]
    print("-" * 128)
    print("TOTALS  slots=%d  lost=%d  accepted=%d  failure_rows=%d  markers=%d  truncated=%d"
          % (t["slots"], t["lost"], t["accepted"], t["failed"], t["markers"], t["truncated"]))
    print("  %d slot(s) hold BOTH a record and a permanent failure row = RE-AUTHORED after failing;"
          % t["reauthored"])
    print("  they inflate the PER-ATT column and are the reason PER-SLOT is the one to quote.")
    gap = t["failed"] - t["markers"]
    print("  the `_rejects/` MARKER set holds %d of the %d permanent failures; %d are missing"
          % (t["markers"], t["failed"], gap))
    print("  (the marker set is what `scripts/campaign_guards.py::rejects_guard` counts, and the")
    print("   missing rows are dominated by `author_reject: ast_gate` -- see this file's docstring)")

    worst = max(abs(tr - gr) for _, tr, gr in rows) if rows else 0.0
    print("  largest per-line PER-SLOT-minus-guard discrepancy: %.2f percentage points" % worst)

    if by_arm:
        print()
        print("=== BY (line, arm) ===")
        print("%-32s %-18s %7s %7s %7s %7s" % ("line", "arm", "accept", "failed", "calls", "trunc"))
        for line, rec in sorted(lines.items()):
            for arm, a in sorted(rec["arms"].items()):
                if not a["is_llm"]:
                    continue
                print("%-32s %-18s %7d %7d %7d %7d" % (
                    line, arm, a["accepted"], a["failed"], a["llm_calls"], a["truncated"]))

    print()
    print("TWO STANDING QUALIFICATIONS -- print them beside the table or the table misleads:")
    print("  1. TRUNCATION. A candidate lost because OUR 16,384-token cap cut the completion is an")
    print("     instrument artefact, not a capability datum, and the registered obligation")
    print("     (`guard:truncation` in docs/ops/acknowledged_alarms.txt) is to exclude those calls")
    print("     from every authoring-reliability denominator. The `trunc` column is that count. It")
    print("     CANNOT be subtracted exactly: llm_calls.jsonl carries no candidate_id and")
    print("     failures.jsonl carries no timestamp, so the exclusion is bounded at (line, arm),")
    print("     never per candidate. Quote it as an UPPER BOUND on the correction.")
    print("  2. AST-GATE IS OURS, NOT THE MODEL'S. Execution record s.87.2: 12 of 20 core-line")
    print("     ast_gate rejects examined were `.resize` missing from a 338-name attribute")
    print("     allowlist -- our gate over-rejecting safe numpy, direction UNFAVOURABLE to us. So")
    print("     the authAST column is NOT interchangeable with 'the model wrote bad code'. Report")
    print("     the author/node split, never a bare single rate.")
    print()
    print("EFFECT-BLIND: error strings, stop reasons and directory names only. No performance")
    print("quantity was opened, returned or compared.")

    if t["torn"]:
        print("*** %d TORN row(s) in failures.jsonl -- the archive is not fully parseable." % t["torn"])
        return 2
    return 0


# --------------------------------------------------------------------------------------------
# SELFTEST. Every case is a MUTATION: it must FAIL against a wrong implementation, or it verifies
# nothing. Case E is the one that matters most -- it is the defect this whole file exists for.
# --------------------------------------------------------------------------------------------
def _mk(root: str, line: str, arm: str, accepted: int, failures: list,
        markers: int = 0, calls: list = ()) -> None:
    d = os.path.join(root, line, arm)
    os.makedirs(d, exist_ok=True)
    for i in range(accepted):
        cd = os.path.join(d, "%s-g0-c%d" % (arm, i))
        os.makedirs(cd, exist_ok=True)
        with open(os.path.join(cd, "record.json"), "w", encoding="utf-8") as fh:
            fh.write("{}")
    if failures:
        with open(os.path.join(d, "failures.jsonl"), "w", encoding="utf-8") as fh:
            for j, e in enumerate(failures):
                cid = e[0] if isinstance(e, tuple) else "%s-gF-c%d" % (arm, j)
                err = e[1] if isinstance(e, tuple) else e
                fh.write(json.dumps({"candidate_id": cid, "error": err,
                                     "permanent": True}) + "\n")
    if calls:
        with open(os.path.join(d, "llm_calls.jsonl"), "w", encoding="utf-8") as fh:
            for c in calls:
                fh.write(json.dumps(c) + "\n")
    if markers:
        md = os.path.join(root, line, "_rejects")
        os.makedirs(md, exist_ok=True)
        for k in range(markers):
            with open(os.path.join(md, "m%d.json" % k), "w", encoding="utf-8") as fh:
                fh.write(json.dumps({"candidate_id": "m%d" % k}))


def selftest() -> int:
    ok = 0
    fail = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal ok, fail
        if cond:
            ok += 1
            print("  PASS  %s" % name)
        else:
            fail += 1
            print("  FAIL  %s  %s" % (name, detail))

    # A. an EMPTY root must exit 2, never 0. The P213 shape.
    with tempfile.TemporaryDirectory() as td:
        rc = report(scan(td))
        check("A empty root exits 2 (a vacuous pass is worse than a failure)", rc == 2, "rc=%d" % rc)

    # B. a root with LINES but ZERO candidates must also exit 2.
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "search_leg_x", "distributional"), exist_ok=True)
        rc = report(scan(td))
        check("B lines present but zero candidates exits 2", rc == 2, "rc=%d" % rc)

    # C. classification of every real error string seen in the archive.
    cases = {
        "author_reject: ast_gate (unsafe construct)": "author_ast_gate",
        "author_reject: no top-level 'reward' binding (empty/refused/truncated completion)":
            "author_no_binding",
        "node reject: sandbox: reward crashed during validation: ValueError(x)": "node_sandbox",
        "node reject: sandbox: reward did not return an unpackable (total, components, state)":
            "node_contract",
        "sandbox: reward crashed during validation: TypeError(x)": "node_sandbox",
    }
    bad = [k for k, v in cases.items() if classify(k) != v]
    check("C every observed error string classifies correctly", not bad, str(bad))

    # D. D18 nested duplicates and .pull_tmp must NOT inflate `accepted`.
    with tempfile.TemporaryDirectory() as td:
        _mk(td, "search_leg_x", "distributional", accepted=3, failures=[])
        nested = os.path.join(td, "search_leg_x", "distributional",
                              "distributional-g0-c0", "distributional-g0-c0")
        os.makedirs(nested, exist_ok=True)
        with open(os.path.join(nested, "record.json"), "w", encoding="utf-8") as fh:
            fh.write("{}")
        pt = os.path.join(td, "search_leg_x", "distributional", ".pull_tmp", "x")
        os.makedirs(pt, exist_ok=True)
        with open(os.path.join(pt, "record.json"), "w", encoding="utf-8") as fh:
            fh.write("{}")
        s = scan(td)
        got = s["lines"]["search_leg_x"]["accepted"]
        check("D nested D18 dir and .pull_tmp do not inflate accepted", got == 3, "got %d, want 3" % got)

    # E. THE DEFECT THIS FILE EXISTS FOR: an author-side failure with NO marker must still be
    #    counted. Against the guard's marker-only arithmetic this line reads 0% reject; the true
    #    rate is 50%. If this case ever passes with rate 0, the file has regressed into the guard.
    with tempfile.TemporaryDirectory() as td:
        _mk(td, "search_leg_x", "distributional", accepted=1,
            failures=["author_reject: ast_gate (unsafe construct)"], markers=0)
        s = scan(td)
        rec = s["lines"]["search_leg_x"]
        true_rate = _rate(rec["failed"], rec["accepted"])
        guard_rate = _rate(rec["markers"], rec["accepted"])
        check("E an unmarked author_ast_gate failure IS counted (true 50% vs guard 0%)",
              abs(true_rate - 0.5) < 1e-9 and guard_rate == 0.0,
              "true=%.3f guard=%.3f" % (true_rate, guard_rate))

    # F. the four DFO arms author nothing and must not enter the denominator.
    with tempfile.TemporaryDirectory() as td:
        _mk(td, "search", "distributional", accepted=2, failures=["author_reject: ast_gate (x)"])
        _mk(td, "search", "random_search", accepted=30, failures=[])
        _mk(td, "search", "tpe", accepted=20, failures=[])
        s = scan(td)
        acc = s["lines"]["search"]["accepted"]
        check("F derivative-free search arms are excluded from the LLM denominator",
              acc == 2, "accepted=%d, want 2 (LLM arms only)" % acc)

    # G. truncation is attributed to the (line, arm) that made the call.
    with tempfile.TemporaryDirectory() as td:
        _mk(td, "search_leg_x", "placebo", accepted=1, failures=[],
            calls=[{"stop_reason": "stop"}, {"stop_reason": "length"}, {"stop_reason": "length"}])
        s = scan(td)
        check("G stop_reason=length is counted per arm",
              s["lines"]["search_leg_x"]["arms"]["placebo"]["truncated"] == 2,
              str(s["lines"]["search_leg_x"]["arms"]["placebo"]))

    # I. THE AUDITOR'S CORRECTION (2026-08-03): a slot that was RE-AUTHORED after failing holds
    #    BOTH a record and a failure row. Per-ATTEMPT reads 1 of 3 failed; per-SLOT reads 0 of 2
    #    lost, because both registered candidates were ultimately delivered. Quoting the
    #    per-attempt number as "the model's reject rate" overstates it, which is exactly how the
    #    core line's `placebo` came to read 33 attempts against a registered budget of 30.
    with tempfile.TemporaryDirectory() as td:
        _mk(td, "search_leg_x", "distributional", accepted=2,
            failures=[("distributional-g0-c0", "author_reject: ast_gate (unsafe construct)")])
        s = scan(td)
        rec = s["lines"]["search_leg_x"]
        check("I a re-authored slot counts as DELIVERED per-slot, FAILED per-attempt",
              rec["slots"] == 2 and rec["lost"] == 0 and rec["reauthored"] == 1
              and rec["failed"] == 1 and rec["accepted"] == 2,
              "slots=%d lost=%d reauth=%d failed=%d acc=%d"
              % (rec["slots"], rec["lost"], rec["reauthored"], rec["failed"], rec["accepted"]))

    # J. a slot that failed and was NEVER re-authored is LOST on both denominators.
    with tempfile.TemporaryDirectory() as td:
        _mk(td, "search_leg_x", "scalar", accepted=2,
            failures=[("scalar-g9-c9", "author_reject: ast_gate (unsafe construct)")])
        rec = scan(td)["lines"]["search_leg_x"]
        check("J a never-re-authored failure is LOST on both denominators",
              rec["slots"] == 3 and rec["lost"] == 1 and rec["reauthored"] == 0,
              "slots=%d lost=%d reauth=%d" % (rec["slots"], rec["lost"], rec["reauthored"]))

    # H. a torn failures.jsonl row must turn the run RED, not be swallowed.
    with tempfile.TemporaryDirectory() as td:
        _mk(td, "search_leg_x", "scalar", accepted=1, failures=["node reject: sandbox: x"])
        with open(os.path.join(td, "search_leg_x", "scalar", "failures.jsonl"), "a",
                  encoding="utf-8") as fh:
            fh.write("{not json\n")
        rc = report(scan(td))
        check("H a torn archive row exits 2 rather than being swallowed", rc == 2, "rc=%d" % rc)

    print("\nselftest: %d passed, %d failed" % (ok, fail))
    return 0 if fail == 0 else 1


def main(argv) -> int:
    ap = argparse.ArgumentParser(
        description="Per-model authoring reliability from the COMPLETE failure record.")
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--by-arm", action="store_true", help="also print the per-(line, arm) table")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not os.path.isdir(a.root):
        print("*** archive root does not exist: %s" % a.root)
        return 2
    return report(scan(a.root), by_arm=a.by_arm)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
