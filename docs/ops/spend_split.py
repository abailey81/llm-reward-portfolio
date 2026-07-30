"""Provider-split spend across RUNs 1-3, from the ledgers.

The record quotes Anthropic $31.96 / OpenRouter $19.31 from Tamer's console at ~13:55 on
2026-07-28 -- BEFORE RUN 3 ran (16:19-19:45). So the balance available to RUN 4 is the quoted
figure minus whatever RUN 3 (and any un-included part of RUN 2) spent with that provider. Compute
it rather than assume it.

Standing caveat from §12.1, which applies to every number here: the ledger is an ESTIMATE, every
row stamped `estimated-from-planning-prices`. It is computed from the price table, not read back
from the provider, and it ran ~$10 PESSIMISTIC against the console once already. Quote it as an
estimate, never as billed spend.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOTS = {
    "RUN 1": Path("outputs/campaign_cluster"),
    "RUN 2": Path("outputs/campaign_cluster_run2"),
    "RUN 3": Path("outputs/campaign_cluster_run3"),
}

grand: dict[str, float] = defaultdict(float)
for label, root in ROOTS.items():
    per_provider: dict[str, float] = defaultdict(float)
    calls = 0
    for led in sorted(root.glob("spend_ledger_*.jsonl")):
        for line in led.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            calls += 1
            per_provider[str(row.get("provider"))] += float(row.get("cost_usd") or 0.0)
    total = sum(per_provider.values())
    print(f"{label}: calls={calls} total=${total:.4f}")
    for p in sorted(per_provider):
        print(f"    {p:12s} ${per_provider[p]:.4f}")
        grand[p] += per_provider[p]

print()
print("ACROSS RUNS 1-3 (ledger ESTIMATE):")
for p in sorted(grand):
    print(f"    {p:12s} ${grand[p]:.4f}")
print(f"    {'TOTAL':12s} ${sum(grand.values()):.4f}")

# The console figures were quoted before RUN 3 ran; RUN 3's spend is therefore NOT reflected in
# them and must be subtracted to get what RUN 4 can actually draw on.
run3: dict[str, float] = defaultdict(float)
for led in sorted(ROOTS["RUN 3"].glob("spend_ledger_*.jsonl")):
    for line in led.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        run3[str(row.get("provider"))] += float(row.get("cost_usd") or 0.0)

QUOTED = {"anthropic": 31.96, "openrouter": 19.31}
NEEDED = {"anthropic": 18.72, "openrouter": 5.28}
print()
print("RUN 4 HEADROOM (quoted console MINUS RUN 3, which post-dates the quote):")
for p in ("anthropic", "openrouter"):
    avail = QUOTED[p] - run3.get(p, 0.0)
    margin = (avail - NEEDED[p]) / NEEDED[p] * 100 if NEEDED[p] else float("nan")
    print(
        f"    {p:12s} quoted ${QUOTED[p]:.2f} - run3 ${run3.get(p, 0.0):.2f} "
        f"= ${avail:.2f} available vs ${NEEDED[p]:.2f} projected  (margin {margin:.0f}%)"
    )
