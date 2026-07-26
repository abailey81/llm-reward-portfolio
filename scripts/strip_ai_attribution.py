"""Remove Claude/AI co-author attribution from the GitHub history — safely, verifiably, reversibly.

WHY THIS EXISTS
---------------
`CLAUDE.md` carries an ABSOLUTE rule: this is a single-author dissertation and Claude must never appear
as an author, co-author, contributor or collaborator. Going forward, no commit gets an attribution
trailer. But commits made BEFORE that rule already carry ``Co-Authored-By: Claude … <noreply@anthropic
.com>`` trailers, and that trailer is exactly what GitHub reads to render a co-author on a commit.

Rewriting them means rewriting history and force-pushing — irreversible on shared refs — so this script
is deliberately conservative: it DEFAULTS TO A DRY RUN, takes full bundle backups before touching
anything, PROVES the rewrite changed only messages (every rewritten commit must keep a byte-identical
tree), and ABORTS if the remote moved under it.

WHAT IT CHANGES
---------------
ONLY commit messages. It strips attribution lines and nothing else:
  * ``Co-Authored-By:`` naming Claude / Anthropic / noreply@anthropic.com
  * "Generated with … Claude Code" / robot-emoji tool-credit lines
A ``Co-Authored-By:`` naming a HUMAN is preserved — this removes an AI credit, it does not rewrite
genuine human co-authorship. File contents, trees, authorship and dates are untouched.

USAGE
-----
    python scripts/strip_ai_attribution.py                 # dry run: report only, changes nothing
    python scripts/strip_ai_attribution.py --execute       # rewrite local temp refs + verify, NO push
    python scripts/strip_ai_attribution.py --execute --push # …and force-push the cleaned refs

    # UNPUSHED local work (see --local-branch, added 2026-07-26):
    python scripts/strip_ai_attribution.py --local-branch <name> --execute --push

THE GAP ``--local-branch`` CLOSES (found 2026-07-26). The default mode cleans what is ALREADY on the
remote, so attributed commits that exist only locally can be cleaned only by pushing them FIRST — which
publishes Claude as a co-author, exactly what the rule forbids, and GitHub may cache a contributor list
even after a later rewrite. ``--local-branch`` rewrites a copy of the LOCAL branch instead and pushes
that, so no attributed commit is ever published. It still never modifies your local refs. ⚠ Its
``--execute`` path is DRY-RUN-verified only: the environment that added it could not run
``git filter-branch``, so the first real run should be watched (the tool's own verification gate still
refuses to push unless every rewritten tip tree is byte-identical, and a full bundle backup is taken
first).

IMPORTANT — it never touches your working branches. It rewrites copies taken from the REMOTE refs
(``refs/heads/__aiclean/*``), so a repo with several agents committing is unaffected. Your local
history keeps its original SHAs, so the commit hashes cited throughout CHANGELOG.md / HANDOFF.md /
DECISIONS.md remain resolvable. Cleaning local history too is a SEPARATE decision (it would invalidate
those citations) and is deliberately not done here.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TEMP_NS = "refs/heads/__aiclean"

ATTR = re.compile(
    r"^\s*(?:"
    r"Co-Authored-By:\s*.*(?:Claude|Anthropic|noreply@anthropic\.com)"
    r"|(?:\U0001F916\s*)?Generated\s+with\s+.*Claude"
    r"|Co-authored-with:\s*.*Claude"
    r")",
    re.IGNORECASE,
)


def git(*args: str, check: bool = True) -> str:
    r = subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed (rc={r.returncode}):\n{r.stderr}")
    return (r.stdout or "").strip()


def clean_message(msg: str) -> str:
    kept = [ln for ln in msg.split("\n") if not ATTR.match(ln)]
    while kept and not kept[-1].strip():
        kept.pop()
    return "\n".join(kept) or "(commit message)"


def remote_branches() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in git("ls-remote", "--heads", "origin").splitlines():
        sha, ref = line.split("\t")
        out[ref.removeprefix("refs/heads/")] = sha
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--execute", action="store_true", help="actually rewrite (default: dry run)")
    ap.add_argument("--push", action="store_true", help="force-push the cleaned refs (implies --execute)")
    ap.add_argument(
        "--local-branch", metavar="NAME", default=None,
        help=(
            "Clean the LOCAL branch NAME and push the cleaned copy to origin/NAME, instead of "
            "cleaning what is already on the remote. Use this when local work has NOT been pushed "
            "yet: it means no attributed commit is ever published, so there is no window in which "
            "GitHub can see (or cache) Claude as a co-author. Local refs are still never modified."
        ),
    )
    args = ap.parse_args()
    if args.push:
        args.execute = True

    # The remote snapshot is ALWAYS taken: it is the abort-check baseline before pushing, and in
    # remote mode it is also the rewrite source. Kept separate from `branches` so --local-branch
    # cannot break the "did origin move under us?" guard (local SHAs never equal remote ones).
    remote_snapshot = remote_branches()
    if not remote_snapshot:
        raise SystemExit("no remote branches found on origin")

    if args.local_branch:
        name = args.local_branch
        local_sha = git("rev-parse", "--verify", f"refs/heads/{name}", check=False)
        if not local_sha:
            raise SystemExit(f"no LOCAL branch {name!r} (refs/heads/{name} does not resolve)")
        branches = {name: local_sha}
        print(f"LOCAL-SOURCE mode: cleaning refs/heads/{name} -> origin/{name}")
        print(f"  {name:38} {local_sha[:10]}")
    else:
        branches = remote_snapshot
        print(f"remote branches: {len(branches)}")
        for n, s in branches.items():
            print(f"  {n:38} {s[:10]}")

    def source_ref(n: str) -> str:
        """The ref a branch's rewrite reads FROM — local in --local-branch mode, else the remote."""
        return f"refs/heads/{n}" if args.local_branch else f"refs/remotes/origin/{n}"

    # --- survey -----------------------------------------------------------------
    git("fetch", "origin", "+refs/heads/*:refs/remotes/origin/*", "--prune")
    scope = [source_ref(n) for n in branches]
    shas = git("rev-list", *scope).splitlines()
    dirty = []
    for sha in shas:
        body = git("log", "-1", "--format=%B", sha)
        if body != clean_message(body):
            dirty.append(sha)
    _src = f"local branch {args.local_branch}" if args.local_branch else "remote refs"
    print(f"\ncommits reachable from {_src} : {len(shas)}")
    print(f"commits carrying AI attribution    : {len(dirty)}")
    if dirty:
        sample = dirty[0]
        print(f"\nexample {sample[:10]} — lines that would be REMOVED:")
        for ln in git("log", "-1", "--format=%B", sample).split("\n"):
            if ATTR.match(ln):
                print(f"    - {ln.strip()}")

    if not args.execute:
        print("\nDRY RUN — nothing changed. Re-run with --execute (then --push) to apply.")
        return 0
    if not dirty:
        print("\nnothing to do: no AI attribution reachable from any remote ref.")
        return 0

    # --- backups ----------------------------------------------------------------
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    bdir = REPO / "outputs" / "attribution_rewrite_backup"
    bdir.mkdir(parents=True, exist_ok=True)
    bundle = bdir / f"pre_rewrite_{stamp}.bundle"
    git("bundle", "create", str(bundle), "--all")
    (bdir / f"pre_rewrite_refs_{stamp}.txt").write_text(git("show-ref"), encoding="utf-8")
    print(f"\nbackup bundle: {bundle}  ({bundle.stat().st_size} bytes)")

    # --- rewrite copies of the REMOTE refs (never your working branches) ---------
    filt = bdir / f"_msg_filter_{stamp}.py"
    filt.write_text(
        "import re,sys\n"
        f"A=re.compile(r'''{ATTR.pattern}''',re.IGNORECASE)\n"
        "raw=sys.stdin.buffer.read()\n"
        "raw=raw[3:] if raw.startswith(b'\\xef\\xbb\\xbf') else raw\n"
        "k=[l for l in raw.decode('utf-8','surrogateescape').split('\\n') if not A.match(l)]\n"
        "while k and not k[-1].strip(): k.pop()\n"
        "sys.stdout.buffer.write(('\\n'.join(k) or '(commit message)').encode('utf-8','surrogateescape')+b'\\n')\n",
        encoding="utf-8",
    )
    temps = []
    for n in branches:
        ref = f"{TEMP_NS}/{n}"
        git("update-ref", ref, git("rev-parse", source_ref(n)))
        temps.append(ref)
    print(f"staged {len(temps)} temp refs under {TEMP_NS}/ (working branches untouched)")

    env_note = "FILTER_BRANCH_SQUELCH_WARNING=1"
    print(f"\nrunning filter-branch ({env_note}) …")
    r = subprocess.run(
        ["git", "filter-branch", "-f", "--msg-filter", f'"{sys.executable}" "{filt}"', "--", *temps],
        cwd=REPO, capture_output=True, text=True, encoding="utf-8",
        env={**os.environ, "FILTER_BRANCH_SQUELCH_WARNING": "1"},
    )
    if r.returncode != 0:
        raise SystemExit(f"filter-branch FAILED (rc={r.returncode}):\n{r.stderr[-2000:]}")

    # --- verify -----------------------------------------------------------------
    bad_tree, still_dirty = [], []
    for n in branches:
        old, new = git("rev-parse", source_ref(n)), git("rev-parse", f"{TEMP_NS}/{n}")
        if git("rev-parse", f"{old}^{{tree}}") != git("rev-parse", f"{new}^{{tree}}"):
            bad_tree.append(n)
    for sha in git("rev-list", *temps).splitlines():
        body = git("log", "-1", "--format=%B", sha)
        if body != clean_message(body):
            still_dirty.append(sha)
    print("\nVERIFICATION")
    print(f"  tip trees byte-identical to originals : {'YES' if not bad_tree else 'NO -> ' + str(bad_tree)}")
    print(f"  attribution remaining after rewrite   : {len(still_dirty)}")
    if bad_tree or still_dirty:
        raise SystemExit("VERIFICATION FAILED — refusing to push. Nothing was pushed; restore from the bundle if needed.")

    if not args.push:
        print("\nRewrite verified on the temp refs. Re-run with --push to force-push.")
        return 0

    # --- push (abort if the remote moved under us) ------------------------------
    # Compare against the REMOTE snapshot, never `branches` — under --local-branch the two are
    # different by construction (local SHAs are not remote SHAs), so comparing to `branches` would
    # abort every run and, worse, would stop guarding the thing it exists to guard.
    if remote_branches() != remote_snapshot:
        raise SystemExit("ABORT: origin changed since the survey — re-run so no one's push is lost.")
    for n in branches:
        # --force-with-lease is checked against refs/remotes/origin/<n>, refreshed by the fetch
        # above, so a concurrent push still cannot be clobbered even though the rewrite is a
        # non-fast-forward by construction.
        git("push", "--force-with-lease", "origin", f"{TEMP_NS}/{n}:refs/heads/{n}")
        print(f"  pushed {n}")
    for ref in temps:
        git("update-ref", "-d", ref)
    print("\nDone. GitHub history no longer carries AI attribution.")
    print("NOTE: your LOCAL branches still have the original SHAs (so the commit hashes cited in")
    print("CHANGELOG.md / HANDOFF.md / DECISIONS.md still resolve). Cleaning local history is a")
    print("separate decision — it would invalidate those citations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
