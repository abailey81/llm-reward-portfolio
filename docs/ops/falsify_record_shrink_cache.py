"""FALSIFIER for `record_shrink_cache.py` — written BEFORE the cache was wired into anything.

RUN 22's lesson, paid for four times in one session: *every fix that shipped with a falsifying test
survived its audit; every fix that shipped without one was found defective within the hour.* And
`cycle.py:440-444` names the specific danger this cache carries: *"a caching bug would produce a
reassuring `sci=OK` from an instrument that cannot fire, which is the worst failure mode this
project has."* So this file exists before the wiring does.

TWO MODES, and both must pass before the cache is trusted:

    python docs/ops/falsify_record_shrink_cache.py           # unit cases, seconds, synthetic archive
    python docs/ops/falsify_record_shrink_cache.py --live    # byte-identity on the REAL archive, ~25 min

The unit cases are all falsification-shaped: each asserts something that is FALSE against a
deliberately-broken cache, and the `--mutants` run proves that by breaking it on purpose and
requiring the named case to go RED.

    python docs/ops/falsify_record_shrink_cache.py --mutants  # mutation control

EXIT: 0 only if every case in the selected mode passes.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(__file__).resolve().parent))

import record_shrink_cache as rsc  # noqa: E402

REPO = Path(__file__).resolve().parents[2]

_BIG = 64


def _shrink(obj):
    """A byte-for-byte copy of the reducer both science tools use, minus their docstrings.

    ⚠ It is a COPY on purpose. Importing theirs would make this falsifier agree with them by
    construction; keeping an independent one means a divergence between the two real tools shows up
    here as a signature mismatch rather than as silence.
    """
    if isinstance(obj, list):
        if len(obj) > _BIG:
            return len(obj)
        return [_shrink(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _shrink(v) for k, v in obj.items()}
    return obj


def _shrink_variant(obj):
    """Same behaviour, different SOURCE. Case E needs a reducer whose signature differs."""
    if isinstance(obj, list):
        if len(obj) > _BIG:
            return len(obj)
        return [_shrink_variant(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _shrink_variant(v) for k, v in obj.items()}
    return obj


# ── synthetic archive ────────────────────────────────────────────────────────────────────────────

def _record(run_id: str, big_len: int = 200, extra: str = "x") -> dict:
    return {
        "run_id": run_id,
        "arm": "distributional",
        "seed": 7,
        "metrics": {"test_sharpe": 1.25},
        "reward_source": f"def reward(): return 0  # {extra}",
        "test_returns": [0.001 * i for i in range(big_len)],
        "small_list": [1, 2, 3],
    }


def _build(root: Path) -> None:
    for i, (lane, arm, cid) in enumerate(
        [("search", "distributional", "c1"), ("search", "scalar", "c2"), ("test", "distributional", "c3")]
    ):
        d = root / lane / arm / cid
        d.mkdir(parents=True, exist_ok=True)
        (d / "record.json").write_text(json.dumps(_record(f"r{i}")), encoding="utf-8")
    # Both excluded trees, so the exclusion is exercised rather than assumed.
    for skip in (".pull_tmp.999", "_quarantined_run3"):
        d = root / skip / "distributional" / "c9"
        d.mkdir(parents=True, exist_ok=True)
        (d / "record.json").write_text(json.dumps(_record("SHOULD-NOT-APPEAR")), encoding="utf-8")


def _ids(records) -> list[str]:
    return sorted(r["run_id"] for _, r in records)


# ── the cases ────────────────────────────────────────────────────────────────────────────────────

def unit_cases(mutate: str = "") -> list[tuple[str, bool, str]]:
    """Each returns (name, passed, detail). `mutate` names a deliberate break for the control run."""
    results: list[tuple[str, bool, str]] = []
    tmp = Path(tempfile.mkdtemp(prefix="rsc_falsify_"))

    # ── THE M1 MUTANT: key on the PATH ALONE, i.e. pretend a record's bytes never change ──────────
    # ⚠ THREE VERSIONS OF THIS MUTANT WERE WRONG BEFORE THIS ONE, AND EACH FAILURE IS A DIFFERENT
    # WAY A MUTATION TEST CAN LIE, SO THEY ARE RECORDED RATHER THAN DELETED:
    #   (i)   replacing `os.stat` wholesale broke `Path.resolve()` inside the cache's own guard, so
    #         the run died on a TypeError and produced NO red case at all;
    #   (ii)  patching only around case D made the mutant MISS every entry instead of serving a
    #         stale one, because the cache had been written with real stats and (0, 0) matched
    #         nothing — the "mutant" then proved the exact opposite of what it claimed;
    #   (iii) freezing stat for the whole sequence DID turn case D red, but took five other cases
    #         with it. A mutant with cross-talk cannot tell you WHICH assertion has the power.
    # This version mutates the key and nothing else: it rewrites each cached entry's (mtime, size)
    # to whatever the file says RIGHT NOW, which is precisely what a path-only key would do, and it
    # never touches `os.stat`, the walk, or the write path.
    _orig_read_cache = rsc._read_cache
    if mutate == "M1":
        def _path_only_key(cache_file):
            entries, lines = _orig_read_cache(cache_file)
            out = {}
            for p, (_m, _s, rec) in entries.items():
                try:
                    st = os.stat(p)
                    out[p] = (st.st_mtime_ns, st.st_size, rec)
                except OSError:
                    out[p] = (_m, _s, rec)
            return out, lines

        rsc._read_cache = _path_only_key  # type: ignore[assignment]
    try:
        root = tmp / "archive"
        cache_dir = tmp / "cache"
        cache_dir.mkdir(parents=True)
        _build(root)

        def load():
            return rsc.load_shrunken_records(root, _shrink, cache_dir=cache_dir)

        # A — a cold cache returns exactly the archive, and the excluded trees are absent.
        cold, err = load()
        ok = _ids(cold) == ["r0", "r1", "r2"] and not err
        results.append(("A cold pass sees every canonical record and NO excluded one", ok,
                        f"ids={_ids(cold)} errors={len(err)}"))

        # B — the long list really was replaced by its LENGTH (the property the whole cache rests on).
        rec = dict(cold)[str((root / "search" / "distributional" / "c1" / "record.json").as_posix())]
        ok = rec["test_returns"] == 200 and rec["small_list"] == [1, 2, 3]
        results.append(("B shrink is applied and SHORT lists survive intact", ok,
                        f"test_returns={rec['test_returns']!r} small_list={rec['small_list']!r}"))

        # C — a warm pass is IDENTICAL to the cold one. This is the core claim.
        warm, _ = load()
        ok = {p: json.dumps(r, sort_keys=True) for p, r in warm} == \
             {p: json.dumps(r, sort_keys=True) for p, r in cold}
        results.append(("C warm pass is byte-identical to the cold pass", ok,
                        f"{len(warm)} vs {len(cold)} records"))

        # D — a CHANGED record must be re-read. This is the case a broken key gets wrong, and it is
        #     the one the M1 mutant must turn red.
        target = root / "search" / "scalar" / "c2" / "record.json"
        time.sleep(0.01)
        target.write_text(json.dumps(_record("r1-EDITED", extra="yyyy")), encoding="utf-8")
        after, _ = load()
        ok = "r1-EDITED" in _ids(after) and "r1" not in _ids(after)
        results.append(("D an EDITED record is re-read, not served stale", ok, f"ids={_ids(after)}"))

        # E — a different shrink SOURCE must not read the other's cache.
        var, _ = rsc.load_shrunken_records(root, _shrink_variant, cache_dir=cache_dir)
        sig_a = rsc.shrink_signature(_shrink)
        sig_b = rsc.shrink_signature(_shrink_variant)
        ok = sig_a != sig_b and _ids(var) == _ids(after)
        results.append(("E a different reducer gets its own cache file and the same answer", ok,
                        f"sig={sig_a} vs {sig_b}"))

        # F — a TORN cache still yields a COMPLETE result (fail-safe, never fail-quiet-and-short).
        # The name is BUILT from the module's own helpers rather than spelled out here: when the
        # cache file gained an owner segment, a hardcoded name in this test turned two cases into
        # FileNotFoundError instead of into a red case, which is a test that fails for the wrong
        # reason and therefore proves nothing.
        # ⚠ IT MUST FIND THE PART THAT ACTUALLY EXISTS. Writes go to a per-process SHARD and the
        # compacted BASE file only appears once compaction fires, which a three-record archive never
        # reaches — so a test hardcoding the base name fails with FileNotFoundError instead of
        # producing a verdict. That is a test failing for the wrong reason, which proves nothing.
        parts = sorted(cache_dir.glob(".record_shrink_cache.*.jsonl"))
        assert parts, "no cache part was written; the earlier cases cannot have passed"
        cfile = parts[0]
        cfile.write_text(cfile.read_text(encoding="utf-8")[:-40] + "\n{not json\n", encoding="utf-8")
        torn, _ = load()
        ok = _ids(torn) == _ids(after)
        results.append(("F a TORN cache still returns every record", ok, f"ids={_ids(torn)}"))

        # G — an UNREADABLE cache part (a directory where the file should be) falls back to a full parse.
        cfile.unlink(missing_ok=True)
        cfile.mkdir()
        unreadable, _ = load()
        ok = _ids(unreadable) == _ids(after)
        results.append(("G an UNREADABLE cache falls back to a FULL parse", ok,
                        f"ids={_ids(unreadable)}"))
        shutil.rmtree(cfile)

        # H — the kill switch really disables it: no cache file is created.
        for stale in cache_dir.glob(".record_shrink_cache.*"):
            stale.unlink()
        os.environ["RECORD_SHRINK_CACHE"] = "0"
        try:
            off, _ = load()
        finally:
            os.environ.pop("RECORD_SHRINK_CACHE", None)
        ok = _ids(off) == _ids(after) and not list(cache_dir.glob(".record_shrink_cache.*"))
        results.append(("H RECORD_SHRINK_CACHE=0 disables it and writes NO cache file", ok,
                        f"files={[p.name for p in cache_dir.glob('.record*')]}"))

        # I — a DELETED record disappears from the answer and from the cache.
        load()  # re-warm
        (root / "test" / "distributional" / "c3" / "record.json").unlink()
        gone, _ = load()
        ok = _ids(gone) == ["r0", "r1-EDITED"]
        results.append(("I a DELETED record leaves the result", ok, f"ids={_ids(gone)}"))

        # J — TWO CONCURRENT WRITERS GET TWO SEPARATE APPEND TARGETS.
        # This is the defect the first live proof found: with ONE append target, two processes
        # writing ~23 KB lines interleave mid-line and the next read reported 710 unparseable
        # lines. The property that makes shards safe is simply that the target carries the PID, so
        # that is what is asserted — and it is FALSE of the single-file design this replaced.
        base = cache_dir / f".record_shrink_cache.{rsc.shrink_owner(_shrink)}.{sig_a}.jsonl"
        real_pid = rsc.os.getpid
        try:
            rsc.os.getpid = lambda: 111111  # type: ignore[assignment]
            shard_a = rsc._shard_path(base)
            rsc.os.getpid = lambda: 222222  # type: ignore[assignment]
            shard_b = rsc._shard_path(base)
        finally:
            rsc.os.getpid = real_pid  # type: ignore[assignment]
        ok = shard_a != shard_b and shard_a.name.endswith(".shard111111.jsonl")
        results.append(("J two writers get two separate append targets (no interleaving)", ok,
                        f"{shard_a.name} vs {shard_b.name}"))

        # K — a read MERGES base + every shard, newest winning, and the stale-sweep does NOT eat
        #     the current signature's own shards (a bare `!= cache_file` test would have).
        for stale in cache_dir.glob(".record_shrink_cache.*"):
            stale.unlink()
        load()                                        # cold: writes a shard
        shards_before = list(cache_dir.glob(".record_shrink_cache.*.shard*.jsonl"))
        merged, _ = load()                            # warm: must READ that shard, not delete it
        shards_after = list(cache_dir.glob(".record_shrink_cache.*.shard*.jsonl"))
        ok = bool(shards_before) and bool(shards_after) and _ids(merged) == _ids(gone)
        results.append(("K the current signature's own shards survive the stale-sweep and are read",
                        ok, f"shards {len(shards_before)} -> {len(shards_after)}, ids={_ids(merged)}"))
    finally:
        rsc._read_cache = _orig_read_cache  # type: ignore[assignment]
        shutil.rmtree(tmp, ignore_errors=True)
    return results


# ── the live byte-identity proof ─────────────────────────────────────────────────────────────────

def live_proof(baseline_dir: Path) -> int:
    """Require the CACHED tools to print byte-identical STDOUT to the PRE-CHANGE tools.

    ⚠⚠ THE BASELINE IS THE ORIGINAL CODE, NOT THE NEW CODE WITH CACHING DISABLED, AND THE
    DIFFERENCE IS THE WHOLE POINT. The original walked with `glob.glob(**, recursive=True)`; the
    cache walks with `Path.rglob`. Several printed lines are ENCOUNTER-ORDERED example slices
    (`bad[:3]`, `oor[:3]`, `list(dupes)[:3]`), so a walk returning the same SET in a different ORDER
    changes stdout — and a cache-on-versus-cache-off comparison could never see it, because both
    sides would use the new walk. Comparing against `git show HEAD:` of each tool is the only test
    that covers the whole change. (The orders were also checked directly and agree on all 15,902
    paths; this is the belt to that braces.)

    ⚠ STDOUT ONLY, and deliberately. `cycle.py:201` merges stderr into the blob it parses, and the
    cache is silent on the healthy path, so the merged blob is unchanged too in the normal case. But
    the SCIENCE VERDICT is stdout, and that is the thing that must not move by one byte.

    ⚠ THE ARCHIVE IS LIVE AND GROWS DURING THE RUN, so a naive comparison would fail on the record
    COUNT alone. Each pair is therefore run BACK TO BACK and the comparison is reported per line
    with the count line called out, so a difference that is only archive growth is distinguishable
    from a difference that is a defect. A clean proof needs the counts to match; if they do not, the
    run is inconclusive and says so rather than passing.
    """
    pairs = [
        ("science_watch", baseline_dir / "orig_science_watch.py", REPO / "docs/ops/science_watch.py"),
        ("results_audit", baseline_dir / "orig_results_audit.py", REPO / "docs/ops/results_audit.py"),
    ]

    # ⚠ A PRIVATE CACHE DIRECTORY, SO THE PROOF CANNOT DAMAGE THE LIVE ONE. The first version cleared
    # `docs/ops/watch`, which is the cache the RUNNING CYCLE depends on: it forced the next real
    # sweeps back to a full parse, and it DIED on a `PermissionError` when the cycle held a part open
    # mid-unlink. A verification step that degrades the thing it is verifying is not a verification
    # step. The live cache is now never touched.
    private = REPO / "docs" / "ops" / "watch" / "_falsify_cache_tmp"
    private.mkdir(parents=True, exist_ok=True)

    def run(script: Path, label: str, clear_cache: bool = False) -> tuple[int, str, float]:
        if clear_cache:
            for f in private.glob(".record_shrink_cache.*"):
                try:
                    f.unlink()
                except OSError as exc:
                    print(f"      (could not clear {f.name}: {exc}; the COLD run is partly warm)")
        env = dict(os.environ)
        env["RECORD_SHRINK_CACHE_DIR"] = str(private)
        t0 = time.time()
        p = subprocess.run([sys.executable, str(script)], cwd=REPO, capture_output=True,
                           encoding="utf-8", errors="replace", env=env, timeout=2400)
        dt = time.time() - t0
        print(f"  {label:28s} rc={p.returncode} {dt:7.1f}s stdout={len(p.stdout or ''):,}B "
              f"stderr={len(p.stderr or ''):,}B")
        if p.stderr:
            print(f"      STDERR (empty is the healthy path): {p.stderr.strip()[:300]}")
        return p.returncode, p.stdout or "", dt

    bad = 0
    for name, orig, new in pairs:
        if not orig.is_file():
            print(f"  *** NO BASELINE for {name} at {orig} -- cannot prove anything. ***")
            bad += 1
            continue
        print(f"--- {name} ---")
        b_rc, b_out, b_dt = run(orig, f"{name} BASELINE (HEAD)")
        c_rc, c_out, c_dt = run(new, f"{name} cached-COLD", clear_cache=True)
        w_rc, w_out, w_dt = run(new, f"{name} cached-WARM")
        for phase, rc, txt, dt in (("cold", c_rc, c_out, c_dt), ("warm", w_rc, w_out, w_dt)):
            if txt == b_out and rc == b_rc:
                print(f"  IDENTICAL  {name} {phase}  ({b_dt:.1f}s -> {dt:.1f}s, "
                      f"{b_dt / dt:.1f}x)" if dt > 0 else "")
                continue
            diffs = [(i, a, b) for i, (a, b) in
                     enumerate(zip(b_out.splitlines(), txt.splitlines())) if a != b]
            growth_only = bool(diffs) and all("records" in a for _, a, _ in diffs)
            verdict = "INCONCLUSIVE (archive grew mid-run)" if growth_only else "*** DIFFERS ***"
            print(f"  {verdict}  {name} {phase}  rc {b_rc}->{rc}, {len(diffs)} differing line(s), "
                  f"{b_dt:.1f}s -> {dt:.1f}s")
            for i, a, b in diffs[:4]:
                print(f"      line {i}:\n        baseline: {a}\n        {phase:8s}: {b}")
            bad += 1
        print()
    return bad


def static_proof(baseline_dir: Path, workdir: Path, n: int = 400) -> int:
    """EXACT byte-identity on a FROZEN copy of real records — the proof `--live` structurally cannot give.

    ⚠ WHY THIS MODE EXISTS. The live archive gains a record every ~24 s while each tool takes 130-200 s
    to run, so a baseline run and a cached run NEVER see the same record set: the first live proof
    differed on three lines and all three were record COUNTS. That is honest evidence but it is not a
    proof, and calling it one would be the "0 means no defects" mistake this repository has already
    paid for. Copying a slice of a COMPLETE line gives a root that does not move, so the comparison
    becomes exact and any difference is a defect rather than arithmetic.

    The slice is real archive data, not a fixture: complete lines (`gemini-2.5-flash`, `gpt-5.6-luna`,
    `h3`, `qwen3.5-9b`, `sonnet-5`) are finished and static, so copying from one cannot race a writer.
    """
    src_root = REPO / "outputs" / "campaign_cluster_run4"
    donors = ["test_leg_sonnet_5", "test_leg_qwen3_5_9b", "test_leg_gemini_2_5_flash"]
    donor = next((d for d in donors if (src_root / d).is_dir()), None)
    if donor is None:
        print(f"  *** no COMPLETE donor line found under {src_root}; cannot build a static root ***")
        return 1

    static_root = workdir / "static_archive"
    if not static_root.is_dir():
        picked = 0
        for rec in sorted((src_root / donor).rglob("record.json")):
            if picked >= n:
                break
            rel = rec.relative_to(src_root)
            dest = static_root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(rec, dest)
            picked += 1
        print(f"  built a static root from {donor}: {picked} record(s) at {static_root}")
    else:
        print(f"  reusing the static root at {static_root}")

    cache_dir = workdir / "static_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    pairs = [
        ("science_watch", baseline_dir / "orig_science_watch.py", REPO / "docs/ops/science_watch.py"),
        ("results_audit", baseline_dir / "orig_results_audit.py", REPO / "docs/ops/results_audit.py"),
    ]

    def run(script: Path, label: str, clear: bool = False) -> tuple[int, str, float]:
        if clear:
            for f in cache_dir.glob(".record_shrink_cache.*"):
                try:
                    f.unlink()
                except OSError:
                    pass
        env = dict(os.environ)
        # The tools default their cache to docs/ops/watch; point them at a private directory so the
        # proof cannot disturb, or be disturbed by, the LIVE cache the running cycle is using.
        env["RECORD_SHRINK_CACHE_DIR"] = str(cache_dir)
        t0 = time.time()
        p = subprocess.run([sys.executable, str(script), str(static_root)], cwd=REPO,
                           capture_output=True, encoding="utf-8", errors="replace",
                           env=env, timeout=1800)
        dt = time.time() - t0
        print(f"  {label:30s} rc={p.returncode} {dt:6.1f}s stdout={len(p.stdout or ''):,}B "
              f"stderr={len(p.stderr or ''):,}B")
        if p.stderr:
            print(f"      STDERR: {p.stderr.strip()[:300]}")
        return p.returncode, p.stdout or "", dt

    bad = 0
    for name, orig, new in pairs:
        if not orig.is_file():
            print(f"  *** NO BASELINE for {name}; cannot prove anything ***")
            bad += 1
            continue
        print(f"--- {name} (static root) ---")
        b_rc, b_out, _ = run(orig, f"{name} BASELINE")
        c_rc, c_out, _ = run(new, f"{name} cached-COLD", clear=True)
        w_rc, w_out, _ = run(new, f"{name} cached-WARM")
        for phase, rc, txt in (("cold", c_rc, c_out), ("warm", w_rc, w_out)):
            if txt == b_out and rc == b_rc:
                print(f"  BYTE-IDENTICAL  {name} {phase}  ({len(b_out):,} B)")
                continue
            bad += 1
            diffs = [(i, a, b) for i, (a, b) in
                     enumerate(zip(b_out.splitlines(), txt.splitlines())) if a != b]
            print(f"  *** DIFFERS ***  {name} {phase}  rc {b_rc}->{rc}, {len(diffs)} line(s)")
            for i, a, b in diffs[:5]:
                print(f"      line {i}:\n        baseline: {a}\n        {phase:8s}: {b}")
        print()
    return bad


def main() -> int:
    args = sys.argv[1:]
    if "--live" in args:
        # The baseline directory holds `git show HEAD:docs/ops/<tool>.py` from BEFORE the change.
        # It is a required argument rather than a default, because a proof that silently skips its
        # own baseline is the "0 means no defects" failure this repo has already paid for once.
        try:
            bdir = Path(args[args.index("--baseline") + 1])
        except (ValueError, IndexError):
            print("usage: --live --baseline <dir with orig_science_watch.py, orig_results_audit.py>")
            print("  produce it with:  git show HEAD:docs/ops/science_watch.py > <dir>/orig_science_watch.py")
            return 2
        if "--static" in args:
            try:
                wdir = Path(args[args.index("--static") + 1])
            except (ValueError, IndexError):
                print("usage: --live --static <workdir> --baseline <dir>")
                return 2
            print("=== STATIC BYTE-IDENTITY PROOF on a FROZEN copy of real records ===")
            bad = static_proof(bdir, wdir)
            print()
            print("STATIC PROOF: PASS -- byte-identical to the pre-change tools" if bad == 0
                  else f"STATIC PROOF: {bad} MISMATCH(ES) -- DO NOT BANK THIS")
            return 0 if bad == 0 else 1
        print("=== LIVE BYTE-IDENTITY PROOF against the PRE-CHANGE tools (the real archive) ===")
        bad = live_proof(bdir)
        print()
        print("LIVE PROOF: PASS" if bad == 0 else f"LIVE PROOF: {bad} MISMATCH(ES) -- DO NOT BANK THIS")
        return 0 if bad == 0 else 1

    if "--mutants" in args:
        print("=== MUTATION CONTROL: break the cache on purpose, require the EXPECTED SET to go red ===")
        # ⚠ THE CONTROL IS AN EXACT SET, NOT A COUNT, AND NOT JUST "D WENT RED".
        # A count says nothing about WHICH assertion has the power, and "D went red" would still pass
        # if the mutant had detonated the whole suite (an earlier version of it did exactly that, and
        # looked like a success). The cases are CHAINED — E, F, G and H all compare their result to
        # `after`, the post-edit answer — so a mutant that makes `after` stale necessarily moves some
        # of them too. Naming the exact set makes the mutant's blast radius part of the assertion, so
        # it fails if the radius grows OR shrinks.
        #   D  red: the edited record is served stale. THIS is the assertion with the power.
        #   E  red: it compares ids against `after`, which is now stale.
        #   G  red: same, after the cache is made unreadable and the record is re-read for real.
        #   H  red: same, with the cache disabled.
        #   A, B, C, F, I stay GREEN: A and B never touch a warm cache, C compares two equally-stale
        #      passes, F compares stale to stale, and I runs after case H deleted the cache file.
        expected = {
            "M1": {
                "D an EDITED record is re-read, not served stale",
                "E a different reducer gets its own cache file and the same answer",
                "G an UNREADABLE cache falls back to a FULL parse",
                "H RECORD_SHRINK_CACHE=0 disables it and writes NO cache file",
            }
        }
        rc = 0
        for mutant, expect_red in expected.items():
            rows = unit_cases(mutate=mutant)
            red = {name for name, ok, _ in rows if not ok}
            print(f"  {mutant}: red = {sorted(red) or 'NONE'}")
            if red == expect_red:
                print(f"        EXACTLY the expected set ({len(red)} case(s)) -> CAUGHT")
            else:
                print(f"        *** MISMATCH. missing={sorted(expect_red - red)} "
                      f"unexpected={sorted(red - expect_red)} ***")
                rc = 1
        print()
        print("MUTATION CONTROL: PASS" if rc == 0 else "MUTATION CONTROL: FAIL")
        return rc

    print("=== UNIT CASES (synthetic archive) ===")
    rows = unit_cases()
    for name, ok, detail in rows:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        print(f"         {detail}")
    bad = sum(1 for _, ok, _ in rows if not ok)
    print()
    print(f"{len(rows) - bad}/{len(rows)} unit case(s) passed")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
