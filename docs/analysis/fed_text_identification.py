"""S11 — THE IDENTIFICATION CHECK: is each arm actually FED what the design says it is fed?

★ WHY THIS IS THE DEEPEST RECORD CHECK IN THE PROJECT (RUN 14, 2026-08-02).
The entire contribution rests on ONE manipulation. Every arm's agent, data, budget, seeds and
evaluation are held fixed; the only thing that varies is the TEXT fed back to the reward-designing
LLM. The identification principle states it directly: *only the reward may vary across arms*, and the
manipulated variable is the feedback CONTENT.

**Nothing else audits that text.** `record_validator` (R1-R9) checks the record's contract,
`record_provenance_seal` (P1-P4) checks it against the files beside it, and `record_science_audit`
(S1-S10) checks that the numbers are scientifically sensible. A campaign in which the distributional
arm was silently fed the scalar block -- or in which the placebo arm was fed real diagnostics -- would
pass ALL of them and would not be measuring what the dissertation claims.

★ WHERE THE FED TEXT ACTUALLY LIVES, AND THE TRAP I FELL INTO FIRST.
A record's `feedback_block` is the block built FROM that candidate and fed to the NEXT generation
(`src/inference/information_gap.py:154`). The text a candidate RECEIVED is assembled in
`src/llm/loop.py:409` as `preamble + prev_feedback_block` and archived in that record's **`prompt`**.
So `feedback_block` is EMPTY on every g>=1 record by design, and reading it as "the feedback was
never fed" is a false alarm -- I raised exactly that alarm before checking, which is the P178 pattern
(the field you want is not the field you reached for).

★ THE REGISTERED SHAPES, verified against the archive on 2026-08-02:

    every arm      : the same reflection preamble, the same scalar line
                     ("Your previous reward scored: X (validation Deflated Sharpe)"),
                     and the same exploration directive
    scalar         : NOTHING further                      -> 0 diagnostic lines
    scalar_cvar5   : one CVaR line                        -> 1
    distributional : the m=6 tail vector                  -> 6   (4 CVaR levels + left-tail mass
                                                                  + left-tail skew)
    placebo        : 6 "reference value" lines, explicitly labelled inert
    placebo_shuffled: the same 6 tail labels as distributional, values shuffled

★ EFFECT-BLIND BY CONSTRUCTION. Every numeric literal is masked before anything is compared or
printed, so this reads the SHAPE of the fed text and never a value, a ranking, or a contrast.

USAGE
    python docs/analysis/fed_text_identification.py            # whole archive
    python docs/analysis/fed_text_identification.py --selftest
EXIT 0 = every arm fed its registered shape, 1 = an identification breach, 2 = could not run.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

NUM = re.compile(r"-?\d+\.?\d*(?:[eE][-+]?\d+)?")
#: A g>=1 prompt longer than this and lacking the scalar line is the INITIAL prompt, i.e. the
#: documented no-feedback fallback. The archived base prompt is 2,602 chars; a reflection prompt is
#: 456-682. The threshold sits far from both so it cannot misclassify either.
BASE_PROMPT_MIN_CHARS = 1500


def _is_d18_nested(p, root) -> bool:
    """True for a D18 `shutil.move` NESTED duplicate: a unit dir whose name equals its parent's.

    D18 is root-caused in DEFERRED_FIXES_RUN4: `shutil.move` into an EXISTING directory nests, and
    the guard cannot close a TOCTOU race on a `read_root` shared by twelve drivers. Measured on
    2026-08-02: exactly TWO such directories exist archive-wide, both in the SEARCH tier, and both
    hold a record BYTE-IDENTICAL to the outer copy -- so no value diverges. But every `rglob`
    instrument counts them TWICE, so they are skipped here exactly as dot-prefixed `.pull_tmp`
    directories are. Skipped, never deleted: the archive is append-only evidence.
    """
    parts = p.parts
    return any(parts[i] == parts[i - 1] for i in range(1, len(parts) - 1))

def _gen_of(path: Path) -> int | None:
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("generation")
    except Exception:
        return None

#: Registered count of DIAGNOSTIC lines fed to each arm, after the shared scalar line.
REGISTERED_DIAGNOSTIC_LINES = {
    "scalar": 0,
    "scalar_cvar5": 1,
    "distributional": 6,
    "placebo": 6,
    "placebo_shuffled": 6,
}
#: The label families. `placebo` must be INERT-labelled; the tail arms must carry real diagnostics.
TAIL_LABEL = re.compile(r"^\s*(CVaR\s|left-tail\s)", re.I)
INERT_LABEL = re.compile(r"^\s*reference value", re.I)
SCALAR_LINE = re.compile(r"previous reward scored", re.I)


def classify(prompt: str) -> dict:
    """Shape of one fed text. Numbers are masked FIRST so nothing numeric can leak."""
    masked = NUM.sub("#", prompt)
    lines = masked.splitlines()
    return {
        "has_scalar_line": any(SCALAR_LINE.search(ln) for ln in lines),
        "tail_lines": sum(1 for ln in lines if TAIL_LABEL.match(ln)),
        "inert_lines": sum(1 for ln in lines if INERT_LABEL.match(ln)),
        "masked": masked,
    }


def audit(root: Path) -> tuple[int, list[str], dict]:
    per = defaultdict(lambda: {"n": 0, "bad": 0, "shapes": set(), "tail": defaultdict(int),
                               "inert": defaultdict(int), "no_scalar": 0, "fallback": 0})
    problems: list[str] = []
    for p in sorted(root.rglob("record.json")):
        if any(x.startswith(".") for x in p.parts):
            continue
        if _is_d18_nested(p, root):
            continue
        if not p.relative_to(root).parts[0].startswith("search"):
            continue
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:                      # noqa: BLE001 -- unreadable IS a finding
            problems.append(f"S11 unreadable record: {p} ({exc})")
            continue
        arm, gen = rec.get("arm"), rec.get("generation")
        if arm not in REGISTERED_DIAGNOSTIC_LINES:
            continue
        if not isinstance(gen, int) or gen < 1:
            continue                                   # g0 has no feedback BY DESIGN
        prompt = rec.get("prompt") or ""
        if not prompt:
            problems.append(f"S11 {arm} g{gen} has an EMPTY prompt -- the reflection text that was "
                            f"fed to the model is not archived: {p}")
            per[arm]["bad"] += 1
            continue
        # ★ THE NO-FEEDBACK FALLBACK IS BY DESIGN, NOT A BREACH (verified 2026-08-02).
        # `src/llm/loop.py:406-409`: the reflection prompt is built from `prev_feedback_block`,
        # which is seeded from a generation's BEST candidate. If a generation yields NO usable
        # candidate -- every draw sandbox-rejected or LLM-error-skipped -- that stays None and the
        # loop correctly falls back to the INITIAL prompt. Confirmed on the archive: the three
        # records that carry a base prompt at g>=1 all sit in `search_leg_qwen3_5_9b` (the ~17 %
        # authoring-reliability bottom anchor) and each one's PRECEDING generation has ZERO archived
        # candidates. Classifying that as an identification breach would be a false alarm; it is a
        # DISCLOSURE, and a scientifically interesting one -- the numeracy bottleneck visible in the
        # fed text itself.
        if len(prompt) > BASE_PROMPT_MIN_CHARS and not SCALAR_LINE.search(prompt):
            prev_n = sum(
                1 for q in p.parent.parent.iterdir()
                if q.is_dir() and (q / "record.json").is_file()
                and _gen_of(q / "record.json") == gen - 1
            )
            d = per[arm]
            d["n"] += 1
            d["fallback"] += 1
            if prev_n:
                problems.append(
                    f"S11 {arm} g{gen} fell back to the BASE prompt while its previous generation "
                    f"HAS {prev_n} archived candidate(s) -- the fallback fired without cause: {p}")
            continue

        c = classify(prompt)
        d = per[arm]
        d["n"] += 1
        d["shapes"].add(c["masked"])
        d["tail"][c["tail_lines"]] += 1
        d["inert"][c["inert_lines"]] += 1
        if not c["has_scalar_line"]:
            d["no_scalar"] += 1
            problems.append(f"S11 {arm} g{gen} fed text is MISSING the shared scalar line -- the "
                            f"arms no longer share a common baseline: {p}")
        want = REGISTERED_DIAGNOSTIC_LINES[arm]
        got = c["inert_lines"] if arm == "placebo" else c["tail_lines"]
        if got != want:
            d["bad"] += 1
            problems.append(f"S11 {arm} g{gen} was fed {got} diagnostic line(s), the design "
                            f"registers {want} -- THE MANIPULATION IS NOT WHAT IT CLAIMS: {p}")
        # a placebo fed REAL tail labels, or a tail arm fed INERT labels, is a swap
        if arm == "placebo" and c["tail_lines"]:
            problems.append(f"S11 placebo g{gen} was fed {c['tail_lines']} REAL tail-diagnostic "
                            f"line(s) -- the information-free control is contaminated: {p}")
        if arm in ("distributional", "placebo_shuffled") and c["inert_lines"]:
            problems.append(f"S11 {arm} g{gen} was fed INERT reference lines -- the tail arm is not "
                            f"receiving diagnostics: {p}")
    return (1 if problems else 0), problems, per


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="outputs/campaign_cluster_run4")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    root = Path(args.root)
    if not root.is_dir():
        print(f"root {root} does not exist", file=sys.stderr)
        return 2
    rc, problems, per = audit(root)

    print("=== S11 FED-TEXT IDENTIFICATION -- is each arm fed what the design registers? ===")
    print(f"{'arm':20s} {'n(g>=1)':>8s} {'registered':>11s} {'observed diagnostic lines':>28s} "
          f"{'shapes':>7s}")
    for arm in ("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled"):
        d = per.get(arm)
        if not d or not d["n"]:
            print(f"{arm:20s} {'0':>8s} {REGISTERED_DIAGNOSTIC_LINES[arm]:>11d} "
                  f"{'(no g>=1 records yet)':>28s} {'-':>7s}")
            continue
        counts = d["inert"] if arm == "placebo" else d["tail"]
        obs = ", ".join(f"{k}x{v}" for k, v in sorted(counts.items()))
        print(f"{arm:20s} {d['n']:8d} {REGISTERED_DIAGNOSTIC_LINES[arm]:>11d} {obs:>28s} "
              f"{len(d['shapes']):7d}")
    fb_total = sum(d["fallback"] for d in per.values())
    if fb_total:
        print(f"  DISCLOSURE: {fb_total} record(s) at g>=1 carry the BASE prompt because their")
        print("  PRECEDING generation produced no usable candidate at all, so there was nothing to")
        print("  reflect on (src/llm/loop.py:406-409). By design, and a direct observation of the")
        print("  authoring-reliability bottleneck in the fed text.")
        for _a, _d in sorted(per.items()):
            if _d["fallback"]:
                print(f"     {_a:20s} {_d['fallback']} fallback record(s)")
    print()
    if problems:
        print(f"!! {len(problems)} IDENTIFICATION BREACH(ES) -- these invalidate the manipulation:")
        for m in problems[:40]:
            print(f"  - {m}")
        if len(problems) > 40:
            print(f"  ... and {len(problems)-40} more")
    else:
        print("S11 CLEAN -- every arm was fed EXACTLY its registered shape:")
        print("  scalar 0 diagnostic lines | scalar_cvar5 1 | distributional 6 tail |")
        print("  placebo 6 INERT reference lines | placebo_shuffled 6 tail (shuffled),")
        print("  and every arm shares the same scalar baseline line.")
        print("  => the manipulated variable is the feedback CONTENT and nothing else.")
    print()
    print("EFFECT-BLIND: numbers masked before comparison; no value, ranking or contrast printed.")
    return rc


def selftest() -> int:
    """Each mutant must trip the check; the clean control must not."""
    base = ("Reflect on the previous candidate's results.\n"
            "Your previous reward scored: 0.12 (validation Deflated Sharpe).\n")
    tail6 = ("Realized-return tail diagnostics (training period):\n"
             "  CVaR 5%: -0.03\n  CVaR 10%: -0.02\n  CVaR 25%: -0.01\n"
             "  CVaR 1%: -0.05  (high-variance estimate)\n"
             "  left-tail mass: +0.11\n  left-tail skew: -0.4\n")
    inert6 = ("Reference constants (inert; no diagnostic content):\n"
              + "".join(f"  reference value {i}: +0.1\n" for i in range(6)))
    cases = [
        ("clean scalar", "scalar", base, True),
        ("clean distributional", "distributional", base + tail6, True),
        ("clean placebo", "placebo", base + inert6, True),
        ("distributional fed only the scalar line", "distributional", base, False),
        ("scalar fed the tail vector", "scalar", base + tail6, False),
        ("placebo fed REAL tail diagnostics", "placebo", base + tail6, False),
        ("missing the shared scalar baseline", "distributional",
         "Reflect.\n" + tail6, False),
    ]
    passed = failed = 0
    for name, arm, text, want_ok in cases:
        c = classify(text)
        want = REGISTERED_DIAGNOSTIC_LINES[arm]
        got = c["inert_lines"] if arm == "placebo" else c["tail_lines"]
        contaminated = (arm == "placebo" and c["tail_lines"]) or \
                       (arm in ("distributional", "placebo_shuffled") and c["inert_lines"])
        ok = (got == want) and c["has_scalar_line"] and not contaminated
        if ok == want_ok:
            passed += 1
            print(f"  ok    {name}")
        else:
            failed += 1
            print(f"  FAIL  {name}: ok={ok}, expected {want_ok} (got={got} want={want} "
                  f"scalar={c['has_scalar_line']})")
    # masking must remove every digit
    m = classify(base + tail6)["masked"]
    if any(ch.isdigit() for ch in m):
        failed += 1
        print("  FAIL  masking left a digit in the text")
    else:
        passed += 1
        print("  ok    masking removes every numeric literal")
    print(f"\nselftest: {passed} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
