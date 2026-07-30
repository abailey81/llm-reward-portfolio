"""Ask OpenRouter what THIS key's limit and usage actually are.

Six legs are parked on `403 Key limit exceeded (total limit)` while the ledger shows only ~$0.32 of
OpenRouter spend, which points at a per-key spending cap rather than an empty balance. Rather than
tell Tamer "raise the limit", read the numbers off the provider so the fix is exact.

Read-only: GET /api/v1/key returns the key's label, usage, limit and remaining. No completion is
requested, so this costs nothing and cannot spend.

The key is read from .env and NEVER printed.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

# NOT a bash-style "/c/Users/..." path: on Windows, Python resolves that to "\c\Users\..." which
# does not exist, and the script then reports "key not found" when the key is present. Use a real
# Windows path.
REPO = Path(r"C:\Users\User\Desktop\dissertation_papers\llm-reward-portfolio")

# .env is the only place the key lives; load just this one variable.
key = None
env = REPO / ".env"
if env.is_file():
    for line in env.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if s.startswith("export "):
            s = s[len("export "):]
        name, _, val = s.partition("=")
        if name.strip() == "OPENROUTER_API_KEY":
            key = val.strip().strip('"').strip("'")
            break
key = key or os.environ.get("OPENROUTER_API_KEY")
if not key:
    print("OPENROUTER_API_KEY not found in .env or the environment")
    sys.exit(1)

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/key",
    headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))
except Exception as exc:  # noqa: BLE001 - report, never mask
    print(f"query failed: {type(exc).__name__}: {exc}")
    sys.exit(2)

d = data.get("data", data)
print("OPENROUTER KEY STATUS (key itself never printed)")
for field in ("label", "usage", "limit", "limit_remaining", "is_free_tier", "is_provisioning_key",
              "rate_limit"):
    if field in d:
        print(f"  {field:18s} = {d[field]}")

usage, limit = d.get("usage"), d.get("limit")
print()
if limit is None:
    print("  -> no per-key limit set; the 403 must then be an ACCOUNT-level credit issue")
else:
    try:
        print(f"  -> per-key cap ${float(limit):.2f}, used ${float(usage or 0):.4f}, "
              f"remaining ${float(limit) - float(usage or 0):.4f}")
        print("  -> THIS is the field to raise on the OpenRouter dashboard (Keys -> edit -> limit)")
    except (TypeError, ValueError):
        print(f"  -> limit={limit!r} usage={usage!r}")
