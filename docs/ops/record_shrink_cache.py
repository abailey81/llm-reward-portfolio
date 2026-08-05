"""SWEEP-1: the incremental record cache the cycle has been asking for since 2026-08-03.

WHY THIS EXISTS, AND WHY IT COULD NOT WAIT
------------------------------------------
`cycle.py` runs `science_watch.py` and `results_audit.py` on EVERY sweep, and each of them parses
every `record.json` in the archive from scratch. Since P270 serialised the pair (`max_workers=1`,
to stop two multi-gigabyte processes coexisting on a 15.64 GB box) the sweep pays for both in
series, and the sweep has been growing linearly with an archive heading for ~42,128 records.

**MEASURED 2026-08-05 07:39:24Z: a sweep of 903.5 s, and a gap of 933 s between consecutive
`CYCLE_LOG.md` lines.** `session_preflight.check_cycle_log` declares the monitoring loop DEAD above
900 s, so a perfectly healthy loop is now inside the window where the board reports a false
run-killer. That is precisely the pre-committed trigger `cycle.py:478-487` wrote down:

    "THE REAL FIX IS THE INCREMENTAL CACHE ... TRIGGER: a `cycle_log` FAIL on a loop that is
     demonstrably alive."
    "The durable fix is the INCREMENTAL cache keyed on (path, mtime, size) described below."

⛔ AND IT IS NOT THE OTHER FIX. Raising the 900 s cap is forbidden by the ledger's own first rule:
the cap is what makes a genuinely dead loop visible, and widening a check to make it pass is the one
move this campaign does not permit.

WHAT THIS IS, PRECISELY
-----------------------
Memoisation of a PURE function over an APPEND-ONLY archive. The two tools never consume a raw
record: each immediately reduces it with an identical `_shrink`, which replaces every list longer
than 64 elements by its LENGTH. Measured on a 120-record sample, the shrunken form is **23.0 KB
against a 416.7 KB raw record, 5.51 %** — so >94 % of every byte parsed each sweep is discarded
microseconds later.

This caches the SHRUNKEN form, keyed on `(path, mtime_ns, size)`. A cache hit returns exactly the
object a full parse would have produced, so **every aggregate computed downstream is bit-identical
to a full pass.** That is the whole safety argument, and it is why this is memoisation rather than
sampling: nothing is skipped, nothing is approximated, no threshold moves.

⚠ THE FAILURE MODE THIS FILE IS WRITTEN AGAINST. `cycle.py:440-444` names it exactly: *"these two
tools ARE the science verdict, and a caching bug would produce a reassuring `sci=OK` from an
instrument that cannot fire, which is the worst failure mode this project has."* Four structural
defences, in the order they matter:

  1. **THE SHRINK FUNCTION'S SOURCE IS PART OF THE CACHE KEY.** The signature is
     `sha256(inspect.getsource(shrink))[:12]` and it names the cache FILE. Change `_shrink` in
     either tool, change `_BIG`, or hand a different reducer in, and the cache misses everything
     and rebuilds. A stale cache cannot outlive the definition it was built under.
  2. **EVERY ABNORMAL PATH IS LOUD AND FALLS BACK TO A FULL PARSE.** An unreadable cache, a torn
     line, a failed write: each prints to STDERR and proceeds with a complete re-parse. There is no
     branch on which a cache problem produces fewer records than a full pass would.
  3. **SILENT WHEN HEALTHY.** Nothing is printed on the normal path, and nothing is EVER printed to
     stdout. `cycle.py:201` merges stderr into the blob it regex-parses, so a chatty cache would
     land in the science verdict's own text. The rule is: absent when fine, unmissable when not.
  4. **A KILL SWITCH.** `RECORD_SHRINK_CACHE=0` in the environment disables it entirely and takes
     the original full-parse path. That is what `falsify_record_shrink_cache.py` uses to prove the
     two paths agree, and it is what an operator uses if this file is ever suspected.

DISK, MEASURED RATHER THAN ESTIMATED (W3 tracks disk against a 20 GB CRITICAL floor):
    0.348 GB at today's 15,881 records · 0.657 GB at 30,000 · **0.922 GB at the 42,128-record end
    state**, against 38.5 GB free. Under 5 % of the headroom, and one file that can be deleted at
    any moment with no consequence beyond one slow sweep.

Usage (from a tool that already has its own `_shrink`):

    from record_shrink_cache import load_shrunken_records
    records, errors = load_shrunken_records(ROOT, _shrink)

`records` is a list of `(posix_path, shrunken_record)`; `errors` is a list of `(posix_path, exc)`
for records that could not be read, so each caller keeps the error behaviour it already had —
`science_watch` drops them, `results_audit` reports them as UNREADABLE hard failures.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Callable

#: Directory segments that every archive walk in this repo excludes, per the convention
#: `scripts/sentinel.py:1348` established after three separate instruments tripped on them.
#: `.pull_tmp.<pid>/` is a pull's in-flight staging tree holding byte-identical copies of records
#: that already exist canonically (D18); `_quarantined*` holds records set aside from an EARLIER
#: run, whose mtimes survive the move.
EXCLUDED_PREFIXES = (".pull_tmp", "_quarantined")

CACHE_DIR = Path("docs/ops/watch")


def _enabled() -> bool:
    """The kill switch. Anything other than an explicit "0" leaves the cache on."""
    return os.environ.get("RECORD_SHRINK_CACHE", "1") != "0"


def _warn(msg: str) -> None:
    """Abnormal paths only. STDERR, never stdout — see defence 3 in the module docstring."""
    print(f"[record_shrink_cache] {msg}", file=sys.stderr)


def shrink_owner(shrink: Callable) -> str:
    """Which tool's reducer this is, so two callers cannot fight over one cache file.

    ⚠ THE TWO REAL REDUCERS ARE NOT TEXTUALLY IDENTICAL. `science_watch._shrink` and
    `results_audit._shrink` have the same BEHAVIOUR and different docstrings, so their source hashes
    differ and each correctly gets its own cache. That is the safe outcome — a shared file would have
    to trust that two separately-maintained functions stay in step — and its whole cost is disk:
    0.35 GB each today, ~0.92 GB each at the 42,128-record end state.

    The owner is also what makes STALE-cache cleanup safe. Sweeping every file whose signature is not
    the current one would have each tool delete the other's cache on every run, which is a
    perpetual-rebuild bug wearing the costume of hygiene.

    ⚠⚠ THE OWNER IS (MODULE, FUNCTION NAME), NOT THE MODULE ALONE, AND MY OWN FALSIFIER PROVED WHY.
    With the module as the owner, two reducers defined in ONE file share an owner namespace, so the
    second one's stale-sweep deletes the first one's cache — and the falsifier, which deliberately
    defines `_shrink` and `_shrink_variant` side by side to test exactly this, went red with a
    FileNotFoundError. The two production tools live in different files and would never have shown
    it. Identity is (module, name); VERSION is the source hash. Sweeping may only ever remove an old
    version of the SAME identity.
    """
    name = getattr(shrink, "__qualname__", None) or getattr(shrink, "__name__", "fn")
    name = "".join(c if c.isalnum() or c == "_" else "-" for c in name)
    try:
        mod = inspect.getmodule(shrink)
        path = getattr(mod, "__file__", None)
        if path:
            return f"{Path(path).stem}.{name}"
    except (OSError, TypeError):
        pass
    return f"anon.{name}"


def shrink_signature(shrink: Callable) -> str:
    """Identify the reducer by its SOURCE, so a cache cannot outlive the definition it was built under.

    ⚠ `inspect.getsource` can fail (a callable defined in a REPL, a C builtin, a stripped .pyc).
    That is not a reason to fall back to a name-based key, because a name-based key is exactly the
    stale-cache failure this function exists to prevent. It falls back to a signature that can never
    match a real one, which forces a full parse — slow and correct rather than fast and wrong.
    """
    try:
        src = inspect.getsource(shrink)
    except (OSError, TypeError):
        _warn("could not read the shrink function's source; caching DISABLED for this run "
              "(a full parse is slow, a stale cache is wrong)")
        return ""
    return hashlib.sha256(src.encode("utf-8")).hexdigest()[:12]


def _archive_paths(root: Path) -> list[str]:
    """Every canonical `record.json` under `root`, POSIX-separated, exclusions applied.

    ⚠ THE EXCLUSION IS EVALUATED ON THE PATH RELATIVE TO `root`, which is `results_audit`'s form.
    `science_watch` evaluates it on the FULL path, which additionally excludes an archive whose
    ANCESTOR directory happens to be named `.pull_tmp*` or `_quarantined*`. The two agree here and
    the assertion below is what makes that a checked fact rather than an assumption: if an ancestor
    ever does match, this raises instead of quietly returning a different record set to one of the
    two callers.
    """
    root = Path(root)
    ancestors = [seg for seg in root.resolve().parts]
    bad = [seg for seg in ancestors if seg.startswith(EXCLUDED_PREFIXES)]
    if bad:
        raise SystemExit(
            f"[record_shrink_cache] REFUSING TO RUN: the archive root {root} sits under an "
            f"excluded directory {bad!r}. science_watch and results_audit would then walk "
            f"DIFFERENT record sets, and this cache would serve one of them the other's answer."
        )
    out: list[str] = []
    for path in root.rglob("record.json"):
        rel = path.relative_to(root).as_posix().split("/")[:-1]
        if any(seg.startswith(EXCLUDED_PREFIXES) for seg in rel):
            continue
        out.append(path.as_posix())
    return out


def _shards(cache_file: Path) -> list[Path]:
    """This cache's per-process append shards, oldest first, so LAST WINS is well defined."""
    pattern = cache_file.name[: -len(".jsonl")] + ".shard*.jsonl"
    try:
        return sorted(cache_file.parent.glob(pattern), key=lambda p: p.stat().st_mtime_ns)
    except OSError:
        return []


def _read_cache(cache_file: Path) -> tuple[dict[str, tuple[int, int, dict]], int]:
    """`({path: (mtime_ns, size, shrunken)}, lines_on_disk)`. Any problem yields an EMPTY cache, loudly.

    Reads the compacted BASE file and then every per-process SHARD, oldest first. LAST LINE WINS on a
    repeated path, which is what makes the append-only write path correct: a re-pulled record simply
    gets a newer line and the older one becomes dead weight rather than a wrong answer. The line
    COUNT is returned because it is the only honest measure of how much dead weight is carried — the
    entry count cannot see duplicates it has already merged away.

    ⚠⚠ THE SHARDS EXIST BECAUSE A SINGLE APPEND-TARGET IS NOT CONCURRENCY-SAFE, AND THE LIVE PROOF
    CAUGHT IT RATHER THAN THEORY. `cycle.py` runs these tools every sweep while a session may run
    them by hand, and two processes appending ~23 KB lines to ONE file interleave mid-line: the first
    live run reported **710 unparseable cache line(s)**. It was FAIL-SAFE — torn lines are ignored
    and those records re-parsed, which is exactly what unit case F asserts — but a cache that shreds
    itself whenever two instances overlap is a cache that does not work. One append target per
    PROCESS removes the interleaving entirely, with no lock and no retry.
    """
    entries: dict[str, tuple[int, int, dict]] = {}
    torn = 0
    lines = 0
    files = ([cache_file] if cache_file.is_file() else []) + _shards(cache_file)
    if not files:
        return {}, 0
    for path in files:
        try:
            with path.open("r", encoding="utf-8") as fh:
                for raw in fh:
                    raw = raw.strip()
                    if not raw:
                        continue
                    lines += 1
                    try:
                        row = json.loads(raw)
                        entries[row["p"]] = (int(row["m"]), int(row["s"]), row["r"])
                    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                        torn += 1
        except OSError as exc:
            _warn(f"cache part unreadable ({path.name}: {exc}); those records will be re-parsed")
    if torn:
        # A torn tail is the expected shape of an interrupted write. Those records simply miss and
        # are re-parsed; the run stays correct. Say so, because silence here would be the start of a
        # cache that decays without anyone noticing.
        _warn(f"{torn} unparseable cache line(s) ignored; those records are being re-parsed")
    return entries, lines


def _line(path: str, mtime: int, size: int, rec: dict) -> str:
    return json.dumps({"p": path, "m": mtime, "s": size, "r": rec},
                      separators=(",", ":"), default=str) + "\n"


def _shard_path(cache_file: Path) -> Path:
    """This PROCESS's own append target. See the concurrency note in `_read_cache`."""
    return cache_file.with_name(cache_file.name[: -len(".jsonl")] + f".shard{os.getpid()}.jsonl")


def _append_cache(cache_file: Path, new: dict[str, tuple[int, int, dict]]) -> None:
    """APPEND the entries that are new or changed. Nothing else is rewritten.

    ⚠⚠ THIS REPLACED A FULL REWRITE, AND THE FULL REWRITE WAS A DEFECT I SHIPPED AND THEN MEASURED
    DOING HARM. Rewriting the whole cache whenever anything changed meant **439 MB per tool per
    sweep**, and both tools run every sweep, on a box that also hosts every driver and supervisor.
    `budget_watch` had timed out **3 times in 5,195 cycles** before this file existed and **6 times
    in the four hours after it**, which is the W6 trigger firing on my own change. Trading 340 s of
    CPU for 0.9 GB of disk writes every five minutes is not an optimisation, it is moving the cost.

    Appending is CORRECT here rather than merely cheap, because `_read_cache` merges by path with
    LAST-LINE-WINS, and the reader validates every entry against the file's live `(mtime, size)`
    anyway. A superseded line is dead weight, never a wrong answer. Compaction removes the weight.
    """
    if not new:
        return
    shard = _shard_path(cache_file)
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with shard.open("a", encoding="utf-8") as fh:
            for path, (mtime, size, rec) in new.items():
                fh.write(_line(path, mtime, size, rec))
    except OSError as exc:
        _warn(f"could not append to the cache ({exc}); those records will be re-parsed next run")


def _compact_cache(cache_file: Path, entries: dict[str, tuple[int, int, dict]]) -> None:
    """Full atomic rewrite, run ONLY when the file has accumulated enough dead lines to be worth it."""
    tmp = cache_file.with_suffix(cache_file.suffix + f".tmp{os.getpid()}")
    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with tmp.open("w", encoding="utf-8") as fh:
            for path, (mtime, size, rec) in entries.items():
                fh.write(_line(path, mtime, size, rec))
        os.replace(tmp, cache_file)
    except OSError as exc:
        _warn(f"could not compact the cache ({exc}); it stays as it is and remains correct")
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        return
    # The shards are now folded into the base, so drop them. A shard another process still has open
    # refuses to unlink on Windows and is simply LEFT: its entries are already in the base, so the
    # only cost is that they are read twice next time. Losing a shard we could not read is equally
    # harmless — an absent entry is a re-parse, never a wrong answer.
    for shard in _shards(cache_file):
        try:
            shard.unlink()
        except OSError:
            pass


def load_shrunken_records(
    root: str | Path,
    shrink: Callable,
    *,
    cache_dir: Path | None = None,
) -> tuple[list[tuple[str, dict]], list[tuple[str, Exception]]]:
    """Every archived record, reduced by `shrink`, reusing an unchanged record's earlier reduction.

    Returns `(records, errors)` where `records` is `[(posix_path, shrunken_record), ...]` in the
    order `rglob` yielded them, and `errors` is `[(posix_path, exception), ...]` for records that
    could not be read this run. Callers keep whatever error behaviour they already had.

    ⚠ THE ONE BEHAVIOURAL DIFFERENCE FROM A FULL PARSE, STATED RATHER THAN HIDDEN. A cache HIT does
    not open the file, so a record that became corrupt *without* changing either its mtime or its
    size would be served from the cache instead of raising. On this archive that is not reachable in
    practice — records are written once and pulled in whole, and any rewrite moves mtime — but it is
    a real difference and it is recorded here rather than discovered later. `RECORD_SHRINK_CACHE=0`
    forces the full-parse path if that ever needs ruling out.
    """
    root = Path(root)
    paths = _archive_paths(root)
    sig = shrink_signature(shrink)
    owner = shrink_owner(shrink)
    use_cache = _enabled() and bool(sig)

    # `RECORD_SHRINK_CACHE_DIR` lets a falsification run keep its cache OUT of the live one, so a
    # proof can never disturb, or be disturbed by, the cache the running cycle depends on.
    _env_dir = os.environ.get("RECORD_SHRINK_CACHE_DIR", "").strip()
    cdir = cache_dir or (Path(_env_dir) if _env_dir else CACHE_DIR)
    cache_file = cdir / f".record_shrink_cache.{owner}.{sig}.jsonl"
    cached, _lines_read = _read_cache(cache_file) if use_cache else ({}, 0)

    # Sweep THIS owner's superseded caches, and only this owner's. A reducer that changes leaves a
    # ~0.35 GB orphan behind otherwise, and an orphan nobody deletes is how a disk floor gets eaten
    # by hygiene debt on a box that already tracks disk against a 20 GB CRITICAL line (W3).
    if use_cache:
        # ⚠ THE PREFIX TEST IS LOAD-BEARING: the current signature's own SHARDS are named
        # `<base-stem>.shard<pid>.jsonl` and match the same glob. A bare `!= cache_file` test would
        # delete this cache's own pending appends on every run — a cache that erases itself while
        # looking tidy. Only files belonging to a DIFFERENT signature are superseded.
        keep_prefix = cache_file.name[: -len(".jsonl")]
        for stale in cdir.glob(f".record_shrink_cache.{owner}.*.jsonl"):
            if not stale.name.startswith(keep_prefix):
                try:
                    stale.unlink()
                    _warn(f"removed a superseded cache for {owner}: {stale.name}")
                except OSError as exc:
                    _warn(f"could not remove the superseded cache {stale.name} ({exc})")

    records: list[tuple[str, dict]] = []
    errors: list[tuple[str, Exception]] = []
    fresh: dict[str, tuple[int, int, dict]] = {}
    hits = 0

    for path in paths:
        try:
            st = os.stat(path)
        except OSError as exc:
            # The file vanished between the walk and the stat: a pull moving a staging tree, say.
            errors.append((path, exc))
            continue
        key = (st.st_mtime_ns, st.st_size)
        hit = cached.get(path)
        if use_cache and hit is not None and (hit[0], hit[1]) == key:
            records.append((path, hit[2]))
            fresh[path] = hit
            hits += 1
            continue
        try:
            with open(path, encoding="utf-8") as fh:
                raw = json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            errors.append((path, exc))
            continue
        reduced = shrink(raw)
        records.append((path, reduced))
        fresh[path] = (key[0], key[1], reduced)

    if use_cache:
        # APPEND the misses; never rewrite what is already correct on disk. On a steady sweep this is
        # a handful of new records (~23 KB each) instead of the whole 0.44 GB file.
        _append_cache(cache_file, {p: v for p, v in fresh.items() if p not in cached
                                   or cached[p][:2] != v[:2]})
        # COMPACT on whichever of three bounds trips first. The line ratio catches dead weight from
        # re-pulled or deleted records; it scales with the archive rather than firing constantly late
        # in the ladder, and `_lines_read` counts what was on DISK so a cache that merged duplicates
        # away cannot hide behind its entry count.
        #
        # ⚠⚠ THE OTHER TWO BOUNDS EXIST BECAUSE THE LINE RATIO ALONE LEAKS FILES, WHICH WAS OBSERVED
        # LIVE RATHER THAN REASONED. A shard is per PROCESS and every cycle is a new process, so the
        # live cache reached **eight shards per tool within an hour** while the line count sat at
        # ~18,000 against a 22,430 threshold that would not trip for days — roughly 288 files per
        # tool per day, each one re-opened on every read. Correctness was never at risk (last-wins
        # merge) but a cache that quietly accretes files is a cache that will one day be the reason
        # something is slow, and finding that later is strictly worse than bounding it now.
        shard_paths = _shards(cache_file)
        try:
            shard_bytes = sum(p.stat().st_size for p in shard_paths)
        except OSError:
            shard_bytes = 0
        base_bytes = cache_file.stat().st_size if cache_file.is_file() else 0
        if (_lines_read > max(2048, int(1.25 * len(fresh)))
                or len(shard_paths) > 32
                or (base_bytes and shard_bytes > 0.05 * base_bytes)):
            _compact_cache(cache_file, fresh)

    return records, errors
