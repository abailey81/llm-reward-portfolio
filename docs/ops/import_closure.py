"""Do the RUNNING processes import the files I just changed?

The drift invariant exists to guarantee that what executes matches what is committed. When a file
under src/ or scripts/ changes mid-campaign, the question is whether the DRIVER can reach it: if it
cannot, the executed experiment is untouched, the change is safe to land live, and RUNNING_SHA can
be re-based without a relaunch (each relaunch costs real Anthropic budget and real wall-clock).

That is a claim about the import graph, so it gets tested rather than asserted. Static closure over
the two entry points, following only first-party `src.*` / `scripts.*` imports.

⚠ GENERALISED 2026-08-01 (RUN 11). This script previously hard-coded the two files ONE session
happened to be changing, and its verdict line said "neither changed file is reachable" whatever you
ran it on. A later caller with a different change would have got a reassuring, specific-sounding
sentence about somebody else's files — the "reassuring comment" tell, in executable form. The
targets are now DERIVED: by default, every changed file under src/ or scripts/ in the working tree
AND every one committed since RUNNING_SHA, so the answer is about YOUR change or the tool says it
had nothing to check. Explicit paths/modules may still be passed on argv.

    python docs/ops/import_closure.py                       # the live diff, both arms
    python docs/ops/import_closure.py scripts/build_paper.py src/foo/bar.py
"""
import ast
import os
import re
import subprocess
import sys
from collections import deque

REPO = "."
ENTRIES = ["scripts/run_campaign_cluster.py", "src/cluster/run_one.py"]

#: RUNNING_SHA is owned by docs/ops/cycle.py; read it there rather than restating it, so the two
#: can never disagree about which commit the live processes were launched from.
def _running_sha() -> str | None:
    try:
        text = open(os.path.join(REPO, "docs", "ops", "cycle.py"), encoding="utf-8").read()
    except OSError:
        return None
    m = re.search(r"RUNNING_SHA\s*=\s*[\"']([0-9a-f]{7,40})[\"']", text)
    return m.group(1) if m else None


def _git(*args: str) -> list[str]:
    try:
        out = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8",
                             errors="replace", cwd=REPO, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [ln for ln in out.splitlines() if ln.strip()]


def _changed_files() -> tuple[list[str], list[str]]:
    """(uncommitted, committed-since-RUNNING_SHA) paths under src/ or scripts/."""
    uncommitted = [ln[3:].strip().strip('"') for ln in _git("status", "--porcelain", "--",
                                                            "src", "scripts")]
    sha = _running_sha()
    committed = _git("diff", "--name-only", f"{sha}", "HEAD", "--", "src", "scripts") if sha else []
    return uncommitted, committed


def _to_module(path: str) -> str | None:
    p = path.replace("\\", "/")
    if not p.endswith(".py"):
        return None
    p = p[: -len("/__init__.py")] if p.endswith("/__init__.py") else p[:-3]
    return p.replace("/", ".")


if len(sys.argv) > 1:
    RAW = list(sys.argv[1:])
    SOURCE = "argv"
else:
    _unc, _com = _changed_files()
    RAW = sorted(set(_unc) | set(_com))
    SOURCE = f"live diff (uncommitted={len(_unc)}, committed-since-RUNNING_SHA={len(_com)})"

TARGETS = {m for m in (_to_module(r) if r.endswith(".py") else r for r in RAW) if m}
_SKIPPED = [r for r in RAW if not (_to_module(r) if r.endswith(".py") else r)]


def module_to_path(mod: str) -> str | None:
    p = os.path.join(REPO, mod.replace(".", os.sep) + ".py")
    if os.path.exists(p):
        return p
    p2 = os.path.join(REPO, mod.replace(".", os.sep), "__init__.py")
    return p2 if os.path.exists(p2) else None


def imports_of(path: str) -> set[str]:
    try:
        tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
    except Exception:
        return set()
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                out.add(a.name)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            out.add(node.module)
            for a in node.names:
                out.add(node.module + "." + a.name)
    return {m for m in out if m.startswith(("src.", "scripts."))}


seen: set[str] = set()
queue: deque[str] = deque()
origin: dict[str, str] = {}

for e in ENTRIES:
    for m in imports_of(e):
        if m not in seen:
            seen.add(m)
            origin[m] = e
            queue.append(m)

while queue:
    mod = queue.popleft()
    path = module_to_path(mod)
    if not path:
        continue
    for m in imports_of(path):
        if m not in seen:
            seen.add(m)
            origin[m] = mod
            queue.append(m)

print("entry points:", ENTRIES)
print("first-party modules reachable:", len(seen))
print("targets from:", SOURCE)
for s in _SKIPPED:
    print("  (not a python module, not import-reachable by construction): %s" % s)
print()
if not TARGETS:
    # An empty target set is NOT a pass. Say which it is.
    if _SKIPPED:
        print("VERDICT: nothing importable changed under src/ or scripts/; the %d non-Python "
              "path(s) above cannot enter the driver's import graph." % len(_SKIPPED))
        sys.exit(0)
    print("VERDICT: NOTHING TO CHECK — no changed file under src/ or scripts/ was found. "
          "This is not evidence that a change is safe; it is evidence that no change was seen.")
    sys.exit(0)

hit = False
for t in sorted(TARGETS):
    reached = [m for m in seen if m == t or m.startswith(t + ".")]
    if reached:
        hit = True
        print("*** REACHED: %s  (via %s)" % (t, origin.get(reached[0], "?")))
    else:
        print("NOT reachable from the running entry points: %s" % t)
print()
if hit:
    print("VERDICT: a driver restart IS required - the running code imports a changed file.")
    sys.exit(1)
print("VERDICT: none of the %d checked target(s) is reachable from the driver or the on-node "
      "entry point: %s" % (len(TARGETS), ", ".join(sorted(TARGETS))))
print("The executed experiment is untouched; no restart is needed for correctness.")
