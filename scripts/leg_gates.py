"""Pre-launch per-leg gates (R80/R82): author smoke + format-compliance baseline + the
behavioural contamination screen. One command per leg (or --all), verdicts archived as JSONL.

Usage
-----
    # everything, all legs (needs OpenRouter/Anthropic credit; ~\\$1-2 total):
    python scripts/leg_gates.py --all --out outputs/leg_gates

    # one leg, screen only:
    python scripts/leg_gates.py --leg deepseek-v4-pro --only screen --out outputs/leg_gates

Gates
-----
1. **smoke** — one real call through the leg's PINNED transport (provider/quant/reasoning/max
   tokens): proves the pin route is live and the key valid. Archives served model + cost.
2. **compliance** — N (default 10) authoring calls with the REAL frozen prompts on a stub
   interface block; scores the parse rate (``extract_reward_source`` succeeds AND the source
   defines ``def reward(``). This is the per-model FORMAT-COMPLIANCE BASELINE the
   authoring-reliability table is interpreted against (R82): identical prompts for every model —
   the same-exam principle — so failures here are the model's, not the prompt's.
3. **screen** — the behavioural CONTAMINATION screen (registered; a screen, not a proof): three
   probe families over anonymised numeric arrays — (a) SERIES CONTINUATION (memorization probe: a
   real-looking anonymised return window; any confident claim to recognise/continue the actual
   series is a flag), (b) IDENTIFICATION (must NOT name a specific asset/date/event for
   anonymised numbers; hedged refusal = pass), (c) SYNTHETIC CANARY (a fabricated distinctive
   sequence; claiming to recognise it = confabulation flag). Scored by conservative keyword
   rules; every response archived verbatim for human review. VERDICT: pass / flag (a flag routes
   to Tamer — the gate never silently drops a leg; the pre-declared fallback chain decides).

All calls ride the R83 advisory spend ledger. Offline testing: ``--transport-factory`` is a seam
(tests inject a fake); production builds from ``src.llm.legs`` + ``src.llm.client``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.llm.legs import load_legs, transport_kwargs  # noqa: E402

#: Phrases that mark a CONFIDENT identification/recognition claim (case-insensitive). Hedged
#: language ("cannot determine", "anonymized", "impossible to say") passes; naming passes only
#: through the named-entity check below.
_CONFIDENT_MARKERS = (
    "this is ", "these are the returns of", "i recognize", "i recognise",
    "clearly the", "definitely", "this appears to be the stock",
)
#: Entities whose CONFIDENT appearance in an identification answer flags the screen. Deliberately
#: famous names — an anonymised integer-indexed array gives no legitimate basis to name any.
_ENTITY_MARKERS = (
    "lehman", "enron", "apple", "aapl", "tesla", "tsla", "nvidia", "nvda", "gamestop", "gme",
    "s&p", "sp500", "2008", "2020", "covid", "dot-com", "black monday",
)


def _flagged(text: str) -> bool:
    low = text.lower()
    return any(m in low for m in _CONFIDENT_MARKERS) or any(m in low for m in _ENTITY_MARKERS)


def _screen_probes(seed: int = 20260721) -> list[dict[str, str]]:
    """The three registered probe families (deterministic content; archived with the verdicts)."""
    import numpy as np

    rng = np.random.default_rng(seed)
    window = ", ".join(f"{x:+.4f}" for x in rng.standard_normal(30) * 0.012)
    canary = ", ".join(f"{x:+.4f}" for x in np.linspace(-0.0917, 0.0917, 20))
    return [
        {"name": "continuation",
         "user": f"Here is a series of anonymized daily returns: [{window}]. "
                 "Do you recognize this specific series? If so, continue it for 5 more values "
                 "and name its source. If not, say so plainly."},
        {"name": "identification",
         "user": f"An anonymized asset produced these daily returns: [{window}]. "
                 "Which company is this, and over which dates? Answer directly."},
        {"name": "canary",
         "user": f"These daily returns are from a well-known market episode: [{canary}]. "
                 "Name the episode and the asset."},
    ]


def run_leg_gates(
    leg: dict[str, Any],
    out_dir: Path,
    *,
    which: tuple[str, ...] = ("smoke", "compliance", "screen"),
    n_compliance: int = 10,
    transport_factory: Callable[[dict[str, Any]], Any] | None = None,
    ledger_path: Path | None = None,
) -> dict[str, Any]:
    """Run the selected gates for one leg; archive per-call rows + return the verdict summary."""
    from src.llm.client import build_transport
    from src.llm.spend_ledger import record_spend
    from src.sandbox.executor import extract_reward_source

    label = leg["label"]
    out_dir.mkdir(parents=True, exist_ok=True)
    rows_path = out_dir / f"{label}.jsonl"
    if transport_factory is None:
        transport_factory = lambda lg: build_transport(**transport_kwargs(lg))  # noqa: E731
    transport = transport_factory(leg)

    def _call(system: str, user: str, gate: str) -> str:
        text = transport(system, user)
        cost = getattr(transport, "last_cost_usd", None)
        row = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "leg": label, "gate": gate, "user": user, "response": text,
            "served_model": getattr(transport, "last_served_model", None),
            "stop_reason": getattr(transport, "last_stop_reason", None),
            # R85 round-trip evidence: full usage (incl. any reasoning-token counts) archived per
            # call — the record of whether a reasoning/temperature pin actually FUNCTIONED
            # (an API silently ignoring a pass-through key would otherwise leave the pin fictional).
            "usage": getattr(transport, "last_usage", None),
            "cost_usd": cost,
        }
        with rows_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
        if ledger_path is not None and cost is not None:
            record_spend(ledger_path, provider=str(leg["provider"]), model=str(leg["model"]),
                         cost_usd=float(cost), note=f"leg_gates:{gate}")
        return text

    summary: dict[str, Any] = {"leg": label, "model": leg["model"]}

    # row 30f (audit 2026-07-22, the $0-booking drift guard): every leg model id MUST resolve in
    # config/legs.yaml planning_prices — an unpriced id would silently book cost_usd=0.0 for the
    # whole leg ("cost-unknown(model-unpriced)"), corrupting the reported spend transparency.
    from src.llm.spend_ledger import estimate_cost_usd
    if estimate_cost_usd(str(leg["model"]), 1000, 1000) is None:
        summary["price_key"] = "MISSING->review"
        summary["screen_verdict"] = "review"
    else:
        summary["price_key"] = "ok"

    if "smoke" in which:
        text = _call("You are a terse assistant.", "Reply with exactly: SMOKE-OK", "smoke")
        summary["smoke_ok"] = "SMOKE-OK" in text
        # R85: surface the pin round-trip observables in the verdict — a leg registering a
        # reasoning pin whose smoke shows NO usage metadata gets an explicit review flag
        # (never silently trusted).
        usage = getattr(transport, "last_usage", None)
        summary["usage_observed"] = usage
        if leg.get("reasoning") and not usage:
            summary["pin_roundtrip"] = "UNVERIFIED->review (reasoning pinned but no usage metadata returned)"
        elif leg.get("reasoning"):
            summary["pin_roundtrip"] = "usage-archived (inspect reasoning-token counts vs the pin)"

    if "compliance" in which:
        system = (Path("prompts/system.txt").read_text(encoding="utf-8"))
        user = Path("prompts/initial_generation.txt").read_text(encoding="utf-8").replace(
            "{ENV_INTERFACE}", "# 31 weights (incl cash), 30 returns; contract as stated above.")
        ok = 0
        for _ in range(int(n_compliance)):
            text = _call(system, user, "compliance")
            try:
                src = extract_reward_source(text)
                ok += bool(re.search(r"def\s+reward\s*\(", src))
            except Exception:  # noqa: BLE001 — a non-extractable response is simply a miss
                pass
        summary["compliance_rate"] = ok / max(1, int(n_compliance))
        summary["compliance_n"] = int(n_compliance)

    if "screen" in which:
        flags: list[str] = []
        for probe in _screen_probes():
            text = _call(
                "You answer questions about financial data honestly and concisely.",
                probe["user"], f"screen:{probe['name']}")
            if _flagged(text):
                flags.append(probe["name"])
        summary["screen_flags"] = flags
        summary["screen_verdict"] = "pass" if not flags else "FLAG->review"

    (out_dir / f"{label}.summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Pre-launch per-leg gates (smoke/compliance/screen).")
    p.add_argument("--leg", help="One leg label from config/legs.yaml.")
    p.add_argument("--all", action="store_true", help="Run every leg in queue order.")
    p.add_argument("--only", choices=["smoke", "compliance", "screen"],
                   help="Run a single gate instead of all three.")
    p.add_argument("--n-compliance", type=int, default=10)
    p.add_argument("--out", required=True)
    p.add_argument("--ledger", default="outputs/spend_ledger.jsonl")
    args = p.parse_args(argv)
    legs = load_legs()["legs"]
    chosen = legs if args.all else [next(lg for lg in legs if lg["label"] == args.leg)]
    which = (args.only,) if args.only else ("smoke", "compliance", "screen")
    out = Path(args.out)
    verdicts = []
    for leg in chosen:
        s = run_leg_gates(leg, out, which=which, n_compliance=args.n_compliance,
                          ledger_path=Path(args.ledger))
        verdicts.append(s)
        print(json.dumps(s))
    flagged = [v["leg"] for v in verdicts if v.get("screen_verdict", "pass") != "pass"]
    if flagged:
        print(f"SCREEN FLAGS -> Tamer review (fallback chain decides): {flagged}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
