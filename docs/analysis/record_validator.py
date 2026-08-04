"""PER-RECORD VALIDATOR -- every record, against its own contract. Plus a LIVE mode.

Everything else this lane built is AGGREGATE: distributions, censuses, collisions.
Tamer, 2026-08-01: "check absolutely each record produced, and being produced in live."
This validates each record INDIVIDUALLY against the contract it was written under, and can
tail the archive to validate new records as they land.

THE CHECKS (each is per-record; R9 is cross-record):

  R1  REQUIRED_FIELDS present -- src/io/results.py:38, the writer's own contract
  R2  reward_source_hash == sha256(reward_source)
      *** THE ONE NOBODY HAD RUN. *** The canonical formula is
      hashlib.sha256(str(reward_source).encode("utf-8")).hexdigest()
      (src/orchestration/test_leg.py:432). That guard fires ONCE PER WINNER in the driver,
      never per record. If any archived hash disagreed with its own source, the P5
      winner-swap refusal, the frozen-winner identity chain and every "the same reward was
      re-trained" claim would be comparing a value against a fiction.
  R3  identity: run_id / candidate_id / arm vs the directory the record sits in
  R4  seed agrees with the -s<N> suffix (test tier)
  R5  generation agrees with the -g<N>-c<M> token (search tier)
  R6  train_safe_default_count <= train_safe_call_count (a fraction > 1 is impossible)
  R7  all per-step series in a record share ONE length
  R8  endpoint replay: test_sharpe / test_cvar05 recompute from test_returns
  R9  cross-tier hash chain: a test record's reward hash == its frozen winner's

EFFECT-BLIND. R8 touches the endpoints but reports only the RECOMPUTATION ERROR -- never a
value, an arm aggregate or a contrast. Every other check reads identifiers, counters,
lengths and hashes.

ASCII-ONLY BY POLICY, and the selftest enforces it. This file was corrupted once by a
PowerShell `Get-Content | Set-Content -Encoding utf8` round-trip that re-encoded its
non-ASCII characters through the ANSI codepage and left a stray byte before the docstring,
which is a syntax error. Pure ASCII makes that impossible.

Usage:
    python docs/analysis/record_validator.py --selftest
    python docs/analysis/record_validator.py                 # whole archive
    python docs/analysis/record_validator.py --live 40 45    # 40 polls, 45 s apart
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ARCHIVE = REPO / "outputs" / "campaign_cluster_run4"
STATE = Path(__file__).resolve().parent / ".record_validator_seen.json"

REQUIRED_FIELDS = ("run_id", "arm", "seed", "fold", "candidate_id", "generation",
                   "reward_source_hash", "feedback_block", "metrics", "wall_clock",
                   "env_fingerprint")
SERIES = ("test_returns", "per_period_pnl", "test_gross", "test_turnover")
SEED_RE = re.compile(r"-s(\d+)$")
GEN_RE = re.compile(r"-g(\d+)-c\d+$")


def canonical_hash(src: str) -> str:
    """EXACTLY the writer's formula -- src/orchestration/test_leg.py:432."""
    return hashlib.sha256(str(src).encode("utf-8")).hexdigest()


def validate(rel: Path, rec: dict, winners: dict | None = None) -> list[str]:
    """Return a list of violation strings for ONE record. Empty list means clean."""
    bad: list[str] = []
    parts = rel.parts
    tier = parts[0]
    leaf = parts[-2] if len(parts) >= 2 else ""

    # R1 ------------------------------------------------------------------------------
    for f in REQUIRED_FIELDS:
        if f not in rec:
            bad.append(f"R1 missing required field '{f}'")

    # R2 ------------------------------------------------------------------------------
    src = rec.get("reward_source")
    h = rec.get("reward_source_hash")
    if isinstance(src, str) and src.strip() and isinstance(h, str) and len(h) == 64:
        actual = canonical_hash(src)
        if actual != h:
            bad.append(f"R2 hash MISMATCH: recorded {h[:12]}.. actual {actual[:12]}..")

    # R3 ------------------------------------------------------------------------------
    # THE REAL CONTRACT, read off the archive rather than assumed. This check first fired on
    # 1,295 violations across 1,244 of 2,717 records = 46%, which is the uniform-result tell
    # that the CHECK is wrong, not the data:
    #   run_id       identifies THIS RUN and DOES equal its directory, on every tier.
    #   candidate_id identifies WHICH CANDIDATE the run used, and is NOT the directory
    #                except on the search tier:
    #                  search : the candidate dir              distributional-g5-c1
    #                  test   : the UNIT / frozen winner       baseline_x   (dir is ...-s0)
    #                  frozen : the ORIGINAL winning candidate distributional-g5-c1,
    #                           in a marker dir named <arm>-winner
    # So requiring candidate_id == directory everywhere asserts a contract the writer never
    # made. Only run_id is universal.
    rid = rec.get("run_id")
    if isinstance(rid, str) and leaf and rid != leaf:
        bad.append(f"R3 run_id={rid!r} != directory {leaf!r}")
    cid = rec.get("candidate_id")
    if tier.startswith("search") and isinstance(cid, str) and leaf and cid != leaf:
        bad.append(f"R3 candidate_id={cid!r} != directory {leaf!r} (search tier)")
    # THE RELAXATION ABOVE MUST NOT BECOME A HOLE. Dropping the candidate_id check off the
    # search tier was correct (test/frozen legitimately carry a DIFFERENT object), but the
    # first version then checked NOTHING, so a test record whose candidate_id named a
    # DIFFERENT UNIT passed clean -- found by suppression_audit.py S3b.
    #
    # THE REAL CONTRACT, read off the archive after my first attempt over-constrained it and
    # flagged 957 healthy records: on the TEST tier `candidate_id` identifies WHICH CANDIDATE
    # was tested, and that is
    #     an LLM winner  -> "<arm>-g<N>-c<M>"   e.g. test/placebo/... carries placebo-g3-c3
    #     a canon baseline -> the unit name      e.g. baseline_differential_downside_ratio
    # I had generalised "candidate_id == the unit" from BASELINE records alone, because at
    # that time the LLM arms had no test records at all. The correct predicate is membership
    # of the arm, not equality with it -- and it still catches S3b, where a record in
    # test/placebo/ names 'distributional'.
    if isinstance(cid, str) and cid and len(parts) >= 3:
        parent = parts[1]
        base = parent[: -len("-winner")] if parent.endswith("-winner") else parent
        belongs = (cid == base) or cid.startswith(f"{base}-")
        if (tier.startswith("test") or tier.startswith("frozen")) and not belongs:
            bad.append(f"R3 candidate_id={cid!r} does not belong to arm {base!r} ({tier} tier)")
    arm = rec.get("arm")
    if isinstance(arm, str) and len(parts) >= 3:
        parent = parts[1]
        # frozen markers live in <arm>-winner; strip that decoration before comparing.
        base = parent[: -len("-winner")] if parent.endswith("-winner") else parent
        if arm != base:
            bad.append(f"R3 arm={arm!r} inconsistent with parent dir {parent!r}")

    # R4 ------------------------------------------------------------------------------
    if tier.startswith("test"):
        m = SEED_RE.search(leaf)
        if m and rec.get("seed") is not None and int(m.group(1)) != int(rec["seed"]):
            bad.append(f"R4 seed={rec['seed']} != directory suffix -s{m.group(1)}")

    # R5 ------------------------------------------------------------------------------
    if tier.startswith("search"):
        m = GEN_RE.search(leaf)
        g = rec.get("generation")
        if m and g is not None and int(m.group(1)) != int(g):
            bad.append(f"R5 generation={g} != candidate id token -g{m.group(1)}-")

    # R6 ------------------------------------------------------------------------------
    mt = rec.get("metrics") or {}
    calls, dflt = mt.get("train_safe_call_count"), mt.get("train_safe_default_count")
    if isinstance(calls, (int, float)) and isinstance(dflt, (int, float)):
        if dflt > calls:
            bad.append(f"R6 safe_default {dflt} > safe_call {calls} (fraction > 1)")
        if dflt < 0 or calls < 0:
            bad.append(f"R6 negative counter: default={dflt} calls={calls}")

    # R7 ------------------------------------------------------------------------------
    lens = {f: len(rec[f]) for f in SERIES if isinstance(rec.get(f), list) and rec.get(f)}
    lens.update({f: len(mt[f]) for f in SERIES
                 if isinstance(mt.get(f), list) and mt.get(f)})
    if len(set(lens.values())) > 1:
        bad.append(f"R7 series length disagreement: {lens}")

    # R8 ------------------------------------------------------------------------------
    tr = rec.get("test_returns")
    if isinstance(tr, list) and tr and "test_sharpe" in mt and "test_cvar05" in mt:
        xs = [float(v) for v in tr]
        n = len(xs)
        mu = sum(xs) / n
        sd = math.sqrt(sum((x - mu) ** 2 for x in xs) / n)
        sh = 0.0 if sd == 0 else mu / sd * math.sqrt(252)
        k = math.ceil(0.05 * n)
        cv = sum(sorted(xs)[:k]) / k
        if abs(sh - float(mt["test_sharpe"])) > 1e-9:
            bad.append("R8 test_sharpe does not reproduce "
                       f"(|d|={abs(sh - float(mt['test_sharpe'])):.3e})")
        if abs(cv - float(mt["test_cvar05"])) > 1e-9:
            bad.append("R8 test_cvar05 does not reproduce "
                       f"(|d|={abs(cv - float(mt['test_cvar05'])):.3e})")

    # R9 ------------------------------------------------------------------------------
    if winners is not None and tier.startswith("test") and len(parts) >= 2:
        sfx = "" if tier == "test" else tier[len("test"):]
        wh = winners.get((sfx, parts[1]))
        if wh and isinstance(h, str) and h and wh != h:
            bad.append(f"R9 reward hash {h[:12]}.. != frozen winner {wh[:12]}..")
    return bad


def load_winners(root: Path) -> dict:
    out = {}
    for fz in root.glob("frozen*"):
        if not fz.is_dir():
            continue
        sfx = "" if fz.name == "frozen" else fz.name[len("frozen"):]
        for mk in fz.glob("*-winner/record.json"):
            try:
                out[(sfx, mk.parent.name[: -len("-winner")])] = json.loads(
                    mk.read_text(encoding="utf-8")).get("reward_source_hash")
            except Exception:
                pass
    return out


def iter_paths(root: Path):
    for p in root.rglob("record.json"):
        rel = p.relative_to(root)
        if rel.parts[0].startswith(".pull_tmp") or "_env" in rel.parts:
            continue
        yield p, rel


def sweep(root: Path, only: set | None = None, quiet: bool = False):
    winners = load_winners(root)
    n = 0
    viol: Counter = Counter()
    offenders = []
    for p, rel in iter_paths(root):
        if only is not None and str(rel) not in only:
            continue
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except Exception as exc:
            offenders.append((str(rel), [f"R0 UNREADABLE: {exc}"]))
            viol["R0"] += 1
            continue
        n += 1
        bad = validate(rel, rec, winners)
        if bad:
            offenders.append((str(rel), bad))
            for b in bad:
                viol[b.split()[0]] += 1
    if not quiet:
        print(f"  validated {n} record(s) against 9 per-record checks")
        if offenders:
            print(f"  !! {len(offenders)} record(s) with violations; by check: {dict(viol)}")
            for rel, bad in offenders[:25]:
                print(f"     {rel}")
                for b in bad:
                    print(f"        {b}")
        else:
            print("  CLEAN -- every record satisfies R1-R9")
    return n, offenders


def live(polls: int, interval: int) -> int:
    """Tail the archive and validate each NEW record as it lands.

    ! EVERY print here FLUSHES. Python buffers stdout when it is not a TTY, so without this
    a backgrounded live monitor emits NOTHING until the process EXITS -- i.e. it would report
    an incident half an hour after it happened. A live monitor whose output is not live is
    not a live monitor. (Found by backgrounding it and reading an empty log, 2026-08-01.)
    """
    def say(msg: str) -> None:
        print(msg, flush=True)

    seen = set()
    if STATE.exists():
        try:
            seen = set(json.loads(STATE.read_text(encoding="utf-8")))
        except Exception:
            seen = set()
    if not seen:
        seen = {str(rel) for _, rel in iter_paths(ARCHIVE)}
        STATE.write_text(json.dumps(sorted(seen)), encoding="utf-8")
        say(f"[live] baseline established at {len(seen)} records; "
            f"watching for NEW ones ({polls} polls x {interval}s)")
    rc = 0
    for i in range(polls):
        time.sleep(interval if i else 0)
        now = {str(rel) for _, rel in iter_paths(ARCHIVE)}
        new = now - seen
        if new:
            say(f"[live {i+1}/{polls}] {len(new)} NEW record(s) -- validating each:")
            _n, off = sweep(ARCHIVE, only=new, quiet=True)
            if off:
                rc = 2
                for rel, bad in off:
                    say(f"   !! {rel}")
                    for b in bad:
                        say(f"      {b}")
            else:
                for r in sorted(new)[:12]:
                    say(f"   OK  {r}")
                if len(new) > 12:
                    say(f"   ... and {len(new)-12} more, all clean")
            seen = now
            STATE.write_text(json.dumps(sorted(seen)), encoding="utf-8")
        else:
            say(f"[live {i+1}/{polls}] no new records ({len(seen)} total)")
    return rc


def _selftest() -> int:
    ok = True

    def case(name, cond):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok = ok and cond

    good_src = "def reward(a,b,c,d,e):\n    return 0.0, {}, None"
    base = {"run_id": "arm-s3", "arm": "arm", "seed": 3, "fold": "test",
            "candidate_id": "arm-s3", "generation": 0,
            "reward_source_hash": canonical_hash(good_src), "feedback_block": "",
            "metrics": {"train_safe_call_count": 100, "train_safe_default_count": 5},
            "wall_clock": 1.0, "env_fingerprint": {"label": "x"},
            "reward_source": good_src}
    rel = Path("test/arm/arm-s3/record.json")
    case("clean record -> no violations", validate(rel, dict(base)) == [])

    r = dict(base)

    del r["fold"]
    case("R1 FIRES on a missing required field",
         any(v.startswith("R1") for v in validate(rel, r)))
    r = dict(base)
    r["reward_source_hash"] = "0" * 64
    case("R2 FIRES on a hash/source mismatch",
         any(v.startswith("R2") for v in validate(rel, r)))
    r = dict(base)
    r["run_id"] = "somethingelse"
    case("R3 FIRES on run_id != directory",
         any(v.startswith("R3") for v in validate(rel, r)))
    r = dict(base)
    r["arm"] = "wrongarm"
    case("R3 FIRES on arm != parent dir",
         any(v.startswith("R3") for v in validate(rel, r)))
    r = dict(base)
    r["candidate_id"] = "other-g1-c2"
    case("R3 FIRES on candidate_id != dir ON THE SEARCH TIER",
         any(v.startswith("R3") for v in validate(
             Path("search/arm/arm-s3/record.json"), r)))
    case("R3 does NOT fire when candidate_id names the UNIT on the TEST tier",
         not any(v.startswith("R3") for v in validate(
             Path("test/arm/arm-s3/record.json"), dict(base, candidate_id="arm"))))
    case("R3 does NOT fire on a frozen marker dir <arm>-winner",
         not any(v.startswith("R3") for v in validate(
             Path("frozen/arm-winner/record.json"),
             dict(base, run_id="arm-winner", candidate_id="arm-g5-c1"))))
    r = dict(base)
    r["seed"] = 99
    case("R4 FIRES on seed != -sN suffix",
         any(v.startswith("R4") for v in validate(rel, r)))
    r = dict(base)
    r["generation"] = 4
    case("R5 FIRES on generation != -gN- token",
         any(v.startswith("R5") for v in validate(
             Path("search/arm/arm-g1-c0/record.json"), r)))
    r = dict(base)
    r["metrics"] = {"train_safe_call_count": 10,
                                    "train_safe_default_count": 99}
    case("R6 FIRES on default > call count",
         any(v.startswith("R6") for v in validate(rel, r)))
    r = dict(base)
    r["test_returns"] = [0.1, 0.2, 0.3]
    r["per_period_pnl"] = [0.1, 0.2]
    case("R7 FIRES on series length disagreement",
         any(v.startswith("R7") for v in validate(rel, r)))

    xs = [0.01, -0.02, 0.03, 0.0, -0.01] * 20
    n = len(xs)
    mu = sum(xs) / n
    sd = math.sqrt(sum((x - mu) ** 2 for x in xs) / n)
    k = math.ceil(0.05 * n)
    r = dict(base)
    r["test_returns"] = xs
    r["per_period_pnl"] = xs
    r["metrics"] = {"test_sharpe": mu / sd * math.sqrt(252),
                    "test_cvar05": sum(sorted(xs)[:k]) / k}
    case("R8 CLEAN on a faithful endpoint",
         not any(v.startswith("R8") for v in validate(rel, r)))
    r2 = dict(r)
    r2["metrics"] = dict(r["metrics"])
    r2["metrics"]["test_sharpe"] += 0.5
    case("R8 FIRES on a corrupted endpoint",
         any(v.startswith("R8") for v in validate(rel, r2)))
    case("R9 FIRES on a winner-hash mismatch",
         any(v.startswith("R9") for v in validate(
             rel, dict(base), {("", "arm"): "f" * 64})))
    case("R9 CLEAN when the winner hash agrees",
         not any(v.startswith("R9") for v in validate(
             rel, dict(base), {("", "arm"): base["reward_source_hash"]})))

    case("this file is pure ASCII (immune to codepage round-trips)",
         all(b < 128 for b in Path(__file__).read_bytes()))

    print(f"\nselftest: {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(_selftest())
    if "--live" in sys.argv:
        j = sys.argv.index("--live")
        p = int(sys.argv[j + 1]) if len(sys.argv) > j + 1 else 10
        s = int(sys.argv[j + 2]) if len(sys.argv) > j + 2 else 30
        raise SystemExit(live(p, s))
    print("=== PER-RECORD VALIDATION (R1-R9) over the whole archive ===")
    _n, off = sweep(ARCHIVE)
    print(f"\n  VERDICT: {'VIOLATIONS' if off else 'CLEAN'}")
    raise SystemExit(2 if off else 0)
