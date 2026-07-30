"""Do the RUNNING processes import the files I just changed?

The drift invariant exists to guarantee that what executes matches what is committed. I changed two
ANALYSIS-layer files (src/data/market_reference.py, src/baselines/strategies.py). If the driver and
the on-node entry point never import them, the executed experiment is untouched and a third driver
restart would cost ~$1.25 of Anthropic budget for zero functional benefit.

That is a claim about the import graph, so it gets tested rather than asserted. Static closure over
the two entry points, following only first-party `src.*` / `scripts.*` imports.
"""
import ast
import os
import sys
from collections import deque

REPO = "."
ENTRIES = ["scripts/run_campaign_cluster.py", "src/cluster/run_one.py"]
TARGETS = {"src.data.market_reference", "src.baselines.strategies"}


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
print()
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
print("VERDICT: neither changed file is reachable from the driver or the on-node entry point.")
print("The executed experiment is untouched; no restart is needed for correctness.")
