#!/usr/bin/env python3
"""THE CONFIRMATORY-PATH INTEGRITY GATE — every invariant that must hold for the results to mean anything.

WHY THIS EXISTS (2026-08-01, record §100.32). On 2026-08-01 a long audit verified, BY HAND, that the
search→frozen→test code chain is bit-exact, that every frozen winner is the best R115-eligible
candidate, and that every decoding pin round-trips. **All of it was one-shot.** The campaign runs to
2026-08-27 and nobody re-runs a hand audit daily, so any of those invariants could break tomorrow and
NOTHING would say so. Tamer's instruction was explicit: everything must be flawless **now and in the
future**. A verification that ran once is a snapshot; only an automated gate is an assurance.

**Every check below was RUN BY HAND FIRST and returned clean**, so this file encodes verified-true
invariants rather than hopeful ones — and any future failure is therefore a real regression, not a
mis-specified check. That distinction is why the baseline matters: *a gate that has never been green
against known-good data cannot tell you anything when it goes red.*

THE INVARIANTS
  I1  SELF-HASH        every record's ``reward_source_hash`` == sha256 of its own ``reward_source``.
                       Breaks => the archive's identity link is corrupt.
  I2  SEARCH -> FROZEN every frozen winner's source hash equals that of the search candidate it was
                       selected from. Breaks => the winner is not the thing that won.
  I3  FROZEN -> TEST   every test record's source hash equals its arm's frozen winner. Breaks => the
                       sealed leg scored code that was never selected. **This is the one that would
                       invalidate the headline result.**
  I4  SELECTION        every frozen winner is the MAX-``val_fitness`` candidate among the
                       R115-ELIGIBLE members of its own arm. Breaks => selection is not what the
                       pre-registration says it is. (Reads SEARCH fitness only — never a sealed-test
                       outcome, so EFFECT-BLINDNESS is preserved.)
  I5  MODEL PIN        requested ``model`` == ``served_model`` on every archived LLM call.
                       ⚠ ``moonshotai/kimi-k3-20260715`` is a KNOWN, DISCLOSED exception (§100.26):
                       the dated slug is absent from OpenRouter's catalogue and comes back undated.
                       It is allow-listed by exact string so a NEW mismatch is still loud.
  I6  DECODING PIN     ``max_tokens`` and ``temperature`` as archived match the registered value for
                       that model. Breaks => a leg ran on decoding settings nobody registered.

SEVERITY. A breach on the CONFIRMATORY path (core line / h3_singleshot) is **CRITICAL** and returns 2.
A breach confined to a report-only leg (R80) is **ATTN** and returns 1. Clean is 0. The distinction is
deliberate: report-only legs never gate H1–H4, and treating their breaches as run-stoppers is the
cry-wolf failure that makes real alarms ignorable.

Read-only. Imports nothing from ``src/`` except to read the registered pins.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

#: Lanes whose records feed a CONFIRMATORY estimand. Everything else is report-only under R80.
CORE_LINES = {"core", "h3_singleshot"}

#: R115 eligibility floor: a candidate whose reward fell back on >= this fraction of calls is
#: INELIGIBLE to be frozen. Mirrors the registered value; a candidate at/above it must never win.
R115_FLOOR = 0.10

#: §100.26 — DISCLOSED, NOT SILENCED. OpenRouter has no catalogue entry for the dated kimi slug, so it
#: answers with the undated family id on every call. Allow-listed by EXACT (requested, served) pair so
#: any OTHER model substitution stays loud. Do not widen this to a prefix match.
KNOWN_MODEL_ALIASES = {("moonshotai/kimi-k3-20260715", "moonshotai/kimi-k3")}


#: Any list longer than this is replaced by its LENGTH at load time (see `_shrink`).
_BIG = 64


def _shrink(obj):
    """Replace every long list inside a parsed record with its LENGTH, recursively.

    ⚠ P291, 2026-08-04. MEASURED: this file peaked at **6,899 MB** during a seven-layer run, second
    only to `results_audit`'s 8,032 MB, on a 15.64 GB box hosting ~30 driver and supervisor
    processes; free RAM fell to 0.46 GB. It was not in P270's list at all, so P270's serialisation
    mitigation never covered it. The cause is three accumulators in one walk -- `every`, `frozen`
    and `test` -- each holding FULL records, and a sealed test record is ~477 KB of JSON.

    ⚠ SAFE BECAUSE THE FIELD SET WAS ENUMERATED RATHER THAN ASSUMED. Every field this file reads is
    a scalar or a string: max_tokens, model_snapshot, temperature, train_safe_call_count,
    train_safe_default_count, arm, reward_source_hash, candidate_id, reward_source, val_fitness. A
    grep for `test_returns|per_period_pnl|train_curve|test_exposure|test_alloc` finds NOTHING here,
    and `_shrink` touches only LISTS, so `reward_source` (a string) is untouched.

    Structural rather than a field whitelist, so a schema that grows a new array is covered without
    anyone remembering. A future `len()` or index on one raises; ⚠ but a guard written as
    `isinstance(x, (int, float))` ACCEPTS the replacement int, so the claim is 'raises on
    indexing', NOT 'fails loudly everywhere' -- corrected by P297 after an auditor found the
    over-claim. The direction is benign (such a guard admits more, suppresses nothing).
    """
    if isinstance(obj, list):
        if len(obj) > _BIG:
            return len(obj)
        return [_shrink(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _shrink(v) for k, v in obj.items()}
    return obj


def _lane(top: str) -> str:
    for p in ("search_", "frozen_", "test_"):
        if top.startswith(p):
            return top[len(p):]
    return "core" if top in ("search", "frozen", "test") else top


def _stage(top: str) -> str:
    for s in ("search", "frozen", "test"):
        if top == s or top.startswith(s + "_"):
            return s
    return "?"


def load(root: Path) -> tuple[dict, list, list, list]:
    """Walk the archive once. Returns (search_by_key, frozen, test, all_records)."""
    search: dict[tuple[str, str], dict] = {}
    frozen: list[dict] = []
    test: list[dict] = []
    every: list[dict] = []
    for dirpath, _dn, filenames in os.walk(root):
        if "record.json" not in filenames:
            continue
        rel = os.path.relpath(dirpath, root).replace("\\", "/")
        parts = rel.split("/")
        if any(s.startswith((".pull_tmp", "_quarantine")) for s in parts):
            continue
        try:
            rec = json.loads(Path(dirpath, "record.json").read_text(encoding="utf-8"))
        except Exception:                                # noqa: BLE001
            continue
        # ⚠ P294: `_shrink` runs OUTSIDE the `try` above, deliberately. My P291 patch put it INSIDE,
        # so a `_shrink` failure would have been swallowed by the same `except` that catches an
        # unreadable file -- silently dropping a record from I1-I4 while the gate still printed
        # "all clean". Wrong file to have that in: this is the CONFIRMATORY-path gate. `results_audit`
        # and `science_watch` both call it outside their try; this now matches them, and a `_shrink`
        # failure raises loudly instead of costing a record.
        rec = _shrink(rec)
        rec["_lane"] = _lane(parts[0])
        rec["_stage"] = _stage(parts[0])
        rec["_top"] = parts[0]
        every.append(rec)
        if rec["_stage"] == "search":
            search[(rec["_lane"], str(rec.get("candidate_id")))] = rec
        elif rec["_stage"] == "frozen":
            frozen.append(rec)
        elif rec["_stage"] == "test":
            test.append(rec)
    return search, frozen, test, every


def _fallback_fraction(rec: dict) -> float:
    m = rec.get("metrics") or {}
    d, c = m.get("train_safe_default_count"), m.get("train_safe_call_count")
    if isinstance(d, (int, float)) and isinstance(c, (int, float)) and c:
        return d / c
    return 0.0


def check(root: Path) -> list[dict]:
    """Run every invariant. Returns a list of breach dicts (empty == clean)."""
    search, frozen, test, every = load(root)
    breaches: list[dict] = []

    def fail(inv: str, lane: str, detail: str) -> None:
        breaches.append({"invariant": inv, "lane": lane,
                         "confirmatory": lane in CORE_LINES, "detail": detail})

    # ⚠ P296: ZERO IS NOT CLEAN, and this gate was missed when that guard went into the seven
    # gated layers -- because I looked at the LAYER LIST rather than at everything that walks the
    # archive. `rglob` over a missing or empty tree returns an empty iterator and raises nothing, so
    # an absent archive used to print "I1 ... I6 -- all clean" and return 0. The archive is a PULL
    # MIRROR, so "not here yet" is reachable, and this is the CONFIRMATORY-path gate.
    # It is raised as a BREACH rather than a bare exit because that is this file's own contract: an
    # empty breach list means "every invariant held", and it did not hold -- it was never evaluated.
    if not every:
        fail("I0 vacuity", "-",
             "ZERO records found under the archive root: I1-I6 were NEVER EVALUATED. "
             "This is NOT a clean result.")
        return breaches

    # I1 -- SELF-HASH
    for rec in every:
        src, h = rec.get("reward_source"), rec.get("reward_source_hash")
        if not src or not h:
            continue
        if hashlib.sha256(src.encode("utf-8")).hexdigest() != h:
            fail("I1 self-hash", rec["_lane"],
                 f"{rec['_top']}/{rec.get('run_id')}: hash does not match its own source")

    # I2 -- SEARCH -> FROZEN
    for rec in frozen:
        key = (rec["_lane"], str(rec.get("candidate_id")))
        origin = search.get(key)
        if origin is None:
            continue                                     # unresolved is not a breach (may not be pulled yet)
        if origin.get("reward_source_hash") != rec.get("reward_source_hash"):
            fail("I2 search->frozen", rec["_lane"],
                 f"{rec.get('arm')}/{key[1]}: frozen source differs from the search candidate it won as")

    # I3 -- FROZEN -> TEST   (the one that would invalidate the headline)
    fz = {(r["_lane"], r.get("arm")): r.get("reward_source_hash") for r in frozen}
    for rec in test:
        k = (rec["_lane"], rec.get("arm"))
        if k not in fz or not rec.get("reward_source_hash"):
            continue                                     # baselines carry a marker, not a program
        if fz[k] != rec.get("reward_source_hash"):
            fail("I3 frozen->test", rec["_lane"],
                 f"{rec.get('arm')}/{rec.get('run_id')}: TEST scored code that is not the frozen winner")

    # I4 -- SELECTION (search fitness only; effect-blind)
    pool: dict[tuple[str, str], list[dict]] = collections.defaultdict(list)
    for key, rec in search.items():
        pool[(key[0], rec.get("arm"))].append(rec)
    for rec in frozen:
        k = (rec["_lane"], rec.get("arm"))
        elig = [c for c in pool.get(k, [])
                if _fallback_fraction(c) < R115_FLOOR
                and isinstance((c.get("metrics") or {}).get("val_fitness"), (int, float))
                and math.isfinite((c.get("metrics") or {}).get("val_fitness"))]
        if not elig:
            continue
        best = max(elig, key=lambda c: (c.get("metrics") or {})["val_fitness"])
        if str(best.get("candidate_id")) != str(rec.get("candidate_id")):
            fail("I4 selection", rec["_lane"],
                 f"{rec.get('arm')}: frozen {rec.get('candidate_id')} but best ELIGIBLE is "
                 f"{best.get('candidate_id')} (fitness {(best.get('metrics') or {})['val_fitness']:.6f})")

    # I5 / I6 -- PINS, from the per-call ledger
    reg = _registered_pins()
    for dirpath, _dn, filenames in os.walk(root):
        if "llm_calls.jsonl" not in filenames:
            continue
        rel = os.path.relpath(dirpath, root).replace("\\", "/")
        parts = rel.split("/")
        if any(s.startswith((".pull_tmp", "_quarantine")) for s in parts):
            continue
        lane = _lane(parts[0])
        seen_bad: set[tuple] = set()
        for line in Path(dirpath, "llm_calls.jsonl").read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:                            # noqa: BLE001
                continue
            req, srv = str(row.get("model")), str(row.get("served_model") or "")
            if srv and req != srv and (req, srv) not in KNOWN_MODEL_ALIASES:
                if (("I5", req, srv)) not in seen_bad:
                    seen_bad.add(("I5", req, srv))
                    fail("I5 model pin", lane, f"requested {req} but {srv} answered")
            want = reg.get(req)
            pins = row.get("request_pins") or {}
            if want and isinstance(pins, dict):
                if pins.get("max_tokens") != want["max_tokens"]:
                    if ("I6mt", req) not in seen_bad:
                        seen_bad.add(("I6mt", req))
                        fail("I6 decoding pin", lane,
                             f"{req}: max_tokens {pins.get('max_tokens')} != registered {want['max_tokens']}")
                if pins.get("temperature") != want["temperature"]:
                    if ("I6t", req) not in seen_bad:
                        seen_bad.add(("I6t", req))
                        fail("I6 decoding pin", lane,
                             f"{req}: temperature {pins.get('temperature')!r} != registered "
                             f"{want['temperature']!r}")
    return breaches


def _registered_pins() -> dict[str, dict]:
    """model id -> {max_tokens, temperature} from config/legs.yaml + config/campaign.yaml."""
    out: dict[str, dict] = {}
    try:
        import yaml                                      # noqa: PLC0415
        legs = yaml.safe_load((REPO / "config" / "legs.yaml").read_text(encoding="utf-8")) or {}
        for leg in legs.get("legs") or []:
            if leg.get("model"):
                out[str(leg["model"])] = {"max_tokens": leg.get("max_tokens"),
                                          "temperature": leg.get("temperature")}
        camp = yaml.safe_load((REPO / "config" / "campaign.yaml").read_text(encoding="utf-8")) or {}
        llm = camp.get("llm") or {}
        if llm.get("model_snapshot"):
            out[str(llm["model_snapshot"])] = {"max_tokens": llm.get("max_tokens"),
                                               "temperature": llm.get("temperature")}
    except Exception:                                    # noqa: BLE001
        return {}                                        # no registration readable -> skip I6, never fake it
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Confirmatory-path integrity gate.")
    ap.add_argument("root", nargs="?", default="outputs/campaign_cluster_run4")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    breaches = check(Path(args.root))
    crit = [b for b in breaches if b["confirmatory"]]

    if breaches and not args.quiet:
        by = collections.Counter(b["invariant"] for b in breaches)
        for inv, n in by.most_common():
            print(f"[integrity] {inv}: {n} breach(es)")
        for b in breaches[:25]:
            tag = "CONFIRMATORY" if b["confirmatory"] else "report-only"
            print(f"   [{tag}] {b['invariant']} | {b['lane']} | {b['detail']}")

    if crit:
        print(f"[integrity] CRITICAL: {len(crit)} breach(es) on the CONFIRMATORY path -- the headline "
              f"result cannot be trusted until this is run to ground. Record §100.32.")
        return 2
    if breaches:
        print(f"[integrity] ATTN: {len(breaches)} breach(es), all on report-only legs (R80). "
              f"They never gate H1-H4, but find the cause.")
        return 1
    print("[integrity] OK: I1 self-hash | I2 search->frozen | I3 frozen->test | I4 selection | "
          "I5 model pin | I6 decoding pin -- all clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
