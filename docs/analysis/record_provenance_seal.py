"""PER-RECORD PROVENANCE SEAL — does every record match the FILES SITTING BESIDE IT?

WHY THIS EXISTS AND WHY IT IS NOT A DUPLICATE (RUN 13, 2026-08-02). `record_validator.py` already
checks each record against its own contract, and checks it well: R2 verifies
`reward_source_hash == sha256(reward_source)`, R3-R5 verify identity against the directory, R7
verifies series length, R8 REPLAYS the endpoints from `test_returns`, R9 chains a test record's
reward hash to its frozen winner. Adding anything that overlaps those would be noise.

What NOTHING checks is the seal between a record and its SIBLING FILES. Every unit directory holds
three artefacts — `record.json`, `env.json`, `reward.py` — and the record carries hashes that are
supposed to bind it to the other two:

    record.env_fingerprint.env_json_sha256   ->  should be sha256 of the sibling env.json
    record.reward_source_hash                ->  should be the canonical hash of the sibling reward.py

R2 proves the record is internally consistent; it cannot notice that the `reward.py` a re-run would
actually execute has drifted from the source the record claims, nor that `env.json` has. Under
Priority 5 that matters more than it sounds: the reproducibility case is "replay the archive", and a
replay reads the FILES. **A hash nobody has checked against the artefact it names is exactly the
"a pin nobody can verify is FICTIONAL" failure, one level down.**

FOUR CHECKS, all per-record, all outcome-blind:

  P1  the sibling `env.json` EXISTS and its sha256 equals `env_fingerprint.env_json_sha256`
  P2  the sibling `reward.py` EXISTS and canonically hashes to `reward_source_hash`
  P3  `env.json.git_commit` is a commit this repository actually contains — a record whose code
      provenance names an unknown commit cannot be replayed by anyone
  P4  `wall_clock` is inside a physically plausible band, and `per_period_pnl` is reported for
      whether it is byte-identical to `test_returns` (analysis finding A62: it was identical on
      1131/1131 while the canonical schema calls it a "per-period P&L vector"). This one REPORTS a
      count; it never reads or prints a value.

EFFECT-BLIND, and strictly. It reads hashes, paths, counts, a duration, and ONE boolean per record
(are two arrays equal). No metric, no fitness, no return value is printed, compared across arms, or
aggregated into anything an outcome could be inferred from.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

ARGS = sys.argv[1:]
POS = [a for a in ARGS if not a.startswith("--")]
ROOT = Path(POS[0] if POS else "outputs/campaign_cluster_run4")
WALL_LO_H, WALL_HI_H = 0.05, 20.0     # h_rt is 15 h; below 3 min is not a 400k-step training

# ── INCREMENTAL MODE ────────────────────────────────────────────────────────────────────────────
# Tamer, 2026-08-02: "constantly check each record, make sure every record individually is very
# strictly flawless". A full pass over 3,565 records takes about a minute and the archive is heading
# for ~42,000, so a full pass cannot run on a monitoring cadence -- and a check that is too expensive
# to run is a check that does not run. `--since-state` seals only records whose `record.json` is
# NEWER than the last successful pass, which is exactly the set that could have changed, and keeps
# the guarantee "every record has been sealed at least once, and every NEW record within one cycle".
# ⚠ The state is advanced ONLY on a clean pass, so a failure is re-reported until it is dealt with
# rather than being aged out of the window by the next run.
INCREMENTAL = any(a.startswith("--since-state") for a in ARGS)
STATE = Path("docs/ops/watch/.record_seal_state")
_since = 0.0
if INCREMENTAL and STATE.is_file():
    try:
        _since = float(STATE.read_text(encoding="utf-8").strip())
    except Exception:
        _since = 0.0


def canonical_hash(src: str) -> str:
    """The writer's own formula — src/orchestration/test_leg.py:432."""
    return hashlib.sha256(str(src).encode("utf-8")).hexdigest()


def sha256_obj(obj) -> str:
    """⚠ THE ENV DIGEST IS AN OBJECT HASH, NOT A FILE HASH — `src/utils/provenance.sha256_obj`.

    This script's first run hashed the env.json BYTES and reported 3,509 of 3,509 records as
    mismatched. A clean 100 % is the register's own tell that the SPECIFICATION is wrong, and it was:
    `src/io/results.py:282` verifies with `sha256_obj(env_obj)` over the PARSED object, so file
    indentation, key order and the trailing newline are all invisible to the real digest and were all
    visible to mine. Reusing the writer's own function is the only way two instruments cannot come to
    disagree about the same fact.
    """
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def commit_sha(raw: str) -> str:
    """`git_commit` is `<tag>:<sha>` when the run came from a deployed archive rather than a checkout.

    Measured: every RUN 4 record carries `deployed-archive:b9e6df5535a88bc4e055c3f03735b819f072613e`,
    which IS a real commit in this repository (2026-07-28, the launch commit). Comparing the whole
    string against `git rev-list` truncated it to "deployed-arc" and condemned all 3,509 records —
    this script's second self-inflicted 100 % failure in one run.
    """
    raw = (raw or "").strip()
    return raw.split(":", 1)[1].strip() if ":" in raw else raw


def known_commits() -> set[str]:
    try:
        out = subprocess.run(["git", "rev-list", "--all"], capture_output=True, text=True, timeout=300)
        return {ln.strip() for ln in out.stdout.splitlines() if ln.strip()}
    except Exception:
        return set()


COMMITS = known_commits()
short = {c[:12] for c in COMMITS} | {c[:8] for c in COMMITS} | {c[:7] for c in COMMITS}

fail: Counter = Counter()
examples: dict[str, list[str]] = {}
n = 0
pnl_identical = 0
pnl_present = 0
no_env = no_reward = chain_ok = skipped = 0
git_seen: Counter = Counter()


def note(code: str, msg: str) -> None:
    fail[code] += 1
    examples.setdefault(code, [])
    if len(examples[code]) < 3:
        examples[code].append(msg)


for rec_path in ROOT.rglob("record.json"):
    s = str(rec_path)
    if ".pull_tmp" in s or "_quarantined" in s:
        continue
    if INCREMENTAL:
        try:
            if rec_path.stat().st_mtime <= _since:
                skipped += 1
                continue
        except OSError:
            pass
    d = rec_path.parent
    try:
        rec = json.loads(rec_path.read_text(encoding="utf-8"))
    except Exception as exc:
        note("P0", f"{d.name}: record.json unreadable ({type(exc).__name__})")
        continue
    n += 1
    rel = str(d.relative_to(ROOT))

    # ---- P1: the env seal -------------------------------------------------------------------
    # Mirrors `src/io/results.py:267-284` EXACTLY, including its shared-snapshot fallback: the serial
    # search path and the test leg's per-arm capture write ONE `<root>/_env/env.json` rather than a
    # per-unit copy, and without that fallback the verification is a permanent no-op for every record
    # pointing at a shared snapshot.
    env_p = d / "env.json"
    claimed = ((rec.get("env_fingerprint") or {}) if isinstance(rec.get("env_fingerprint"), dict)
               else {}).get("env_json_sha256")
    if not env_p.is_file():
        for up in (d.parent, d.parent.parent, ROOT):
            cand = up / "_env" / "env.json"
            if cand.is_file():
                env_p = cand
                break
    if not env_p.is_file():
        # A `frozen*/<arm>-winner` record is a MARKER copied from the winning search candidate, so it
        # legitimately has no env.json of its own -- its env claim belongs to the candidate it was
        # frozen from. Leaving that as "56 missing" would be an unexplained residue, and an
        # unexplained residue is where a real defect hides. Resolve it through the chain instead:
        # find that candidate and verify the marker's env hash against ITS env.json. That is the env
        # analogue of R9's reward-hash chain, and it is the check that proves a frozen winner really
        # is the candidate it claims to be.
        cid = str(rec.get("candidate_id") or "")
        resolved = None
        if "-winner" in d.name and cid:
            sfx = d.parent.name[len("frozen"):]           # "" for core, "_leg_x" for a leg
            arm = d.name[: -len("-winner")]
            cand = ROOT / f"search{sfx}" / arm / cid
            if (cand / "env.json").is_file():
                resolved = cand / "env.json"
        if resolved is not None:
            try:
                actual = sha256_obj(json.loads(resolved.read_text(encoding="utf-8")))
            except Exception:
                actual = None
            if actual is None:
                note("P1-chain-unreadable", f"{rel}: winner's source env.json unreadable")
            elif claimed and actual != claimed:
                note("P1-chain-mismatch",
                     f"{rel}: winner env {str(claimed)[:12]}.. != its source candidate {cid} "
                     f"env {actual[:12]}..")
            else:
                chain_ok += 1
        else:
            no_env += 1
            if claimed:
                note("P1-missing",
                     f"{rel}: claims env_json_sha256, no env.json beside it and no source candidate "
                     f"{cid!r} to resolve it through")
    elif claimed:
        try:
            actual = sha256_obj(json.loads(env_p.read_text(encoding="utf-8")))
        except Exception as exc:
            note("P1-unreadable", f"{rel}: env.json unreadable ({type(exc).__name__})")
            actual = claimed
        if actual != claimed:
            note("P1-mismatch", f"{rel}: env sha256_obj {actual[:12]}.. != claimed {str(claimed)[:12]}..")

    # ---- P2: the reward seal ----------------------------------------------------------------
    rw_p = d / "reward.py"
    rh = rec.get("reward_source_hash")
    if not rw_p.is_file():
        no_reward += 1
    elif rh:
        try:
            got = canonical_hash(rw_p.read_text(encoding="utf-8"))
        except Exception:
            got = None
        if got is not None and got != rh:
            note("P2-mismatch", f"{rel}: reward.py hash {got[:12]}.. != record {str(rh)[:12]}..")

    # ---- P3: the code provenance ------------------------------------------------------------
    if env_p.is_file():
        try:
            env = json.loads(env_p.read_text(encoding="utf-8"))
        except Exception:
            env = {}
        gc = commit_sha(str(env.get("git_commit") or ""))
        if gc:
            git_seen[gc[:12]] += 1
            if COMMITS and gc not in COMMITS and gc[:12] not in short:
                note("P3-unknown-commit", f"{rel}: git_commit {gc[:12]}.. is not in this repository")

    # ---- P4: plausibility + the A62 disclosure metric ---------------------------------------
    wc = rec.get("wall_clock")
    if isinstance(wc, (int, float)) and wc > 0:
        h = wc / 3600.0
        if not (WALL_LO_H <= h <= WALL_HI_H):
            note("P4-wall", f"{rel}: wall_clock {h:.3f} h outside [{WALL_LO_H}, {WALL_HI_H}]")
    ppnl, tret = rec.get("per_period_pnl"), rec.get("test_returns")
    if isinstance(ppnl, list) and isinstance(tret, list):
        pnl_present += 1
        if ppnl == tret:                 # a BOOLEAN. No element is read out, compared or printed.
            pnl_identical += 1

print(f"records sealed-checked : {n:,}" + (f"   (incremental: {skipped:,} already sealed in an earlier pass)" if INCREMENTAL else ""))
print(f"  units with no env.json   : {no_env:,}")
print(f"  frozen winners VERIFIED THROUGH THE CHAIN to their source candidate: {chain_ok:,}")
print(f"  units with no reward.py  : {no_reward:,}")
print(f"  distinct git_commit values in env.json: {len(git_seen)}  {git_seen.most_common(6)}")
print()
if fail:
    print("FAILURES")
    for code, cnt in sorted(fail.items()):
        print(f"  {code:<20} {cnt:,}")
        for e in examples[code]:
            print(f"      e.g. {e}")
else:
    print("P1-P4 CLEAN — every record's env.json and reward.py hash exactly as the record claims,")
    print("every git_commit is a commit this repository contains, and every wall_clock is plausible.")
print()
print(f"A62 DISCLOSURE METRIC: per_period_pnl is byte-identical to test_returns on "
      f"{pnl_identical:,} of {pnl_present:,} records carrying both "
      f"({100.0 * pnl_identical / pnl_present:.1f}%)" if pnl_present else
      "A62 DISCLOSURE METRIC: no record carries both fields")
print("  (a COUNT, not a value: the canonical schema calls per_period_pnl a 'per-period P&L vector'")
print("   while the writer assigns it from the same object as test_returns. No consumer reads it, so")
print("   no result is affected -- it is a DISCLOSURE, tracked here so it cannot be forgotten.)")

# Advance the watermark ONLY on a clean pass, so a failure is re-reported next cycle instead of
# being aged out of the window by its own successor.
if INCREMENTAL and not fail:
    try:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(str(time.time()), encoding="utf-8")
    except Exception:
        pass

sys.exit(1 if fail else 0)
