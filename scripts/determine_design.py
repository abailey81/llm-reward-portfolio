"""Design Determination Pipeline (DDP) — resolve every campaign parameter to its METHODOLOGICALLY-CORRECT
value, by the right procedure for its class, and report freeze-readiness.

Why this exists (read this before "optimising" anything)
--------------------------------------------------------
This is a CONTROLLED experiment: the agent is a fixed instrument and the *feedback channel* is the only
manipulated variable. A system that searched parameters to MAXIMISE the headline result would be the garden
of forking paths industrialised — it manufactures false positives and is unpublishable (and it cannot even
help a corroborated-NULL headline). So the DDP never optimises for performance. It assigns each parameter to
one of four classes and determines it by that class's CORRECT criterion:

  * MEASURE   — optimise for ADEQUACY (a diagnostic plateau), not performance: B* (convergence), n_seeds
                (power), candidates (search saturation). These are the ONLY "tuned" parameters.
  * CALIBRATE — set ONCE, identically across arms, by a principled procedure on PRE-TEST data only:
                λ (pre-2015 fitness calibration), SESOI, embargo, multiplicity, the DSR trial count.
  * FIX       — hold at sensible literature defaults, IDENTICAL across arms; tuning would CONFOUND the
                channel contrast: all SAC/LLM hyperparameters, learning_starts, PopArt.
  * REALISTIC — credible real-world values, not result-maximising: universe, lookback, costs, splits,
                delisting, the cash rate.

INVARIANT: nothing here touches the sealed test split (2018-2025). Determination uses train+val (or
pre-2015 sub-folds) only; the test is opened ONCE, post-freeze, for the confirmatory inference.

What it produces
----------------
``docs/DESIGN_DETERMINATION.md`` (+ a json) — for every material parameter: its class, the method that fixes
it, the current value, the determination status, and the evidence pointer. A FREEZE-READY verdict is emitted
when every MEASURE/CALIBRATE parameter is resolved (no PENDING / FIX_NEEDED). This table is the methods-section
justification ("every design parameter, the principled procedure that set it, and the evidence").

This module is a reporter/orchestrator: the heavy determinations live in their own engines
(``scripts/learning_curve.recommend_budget``/``project_campaign``, ``scripts/power_analysis``); the one engine
that lived nowhere — search-saturation — is :func:`recommend_candidates` here.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

__all__ = [
    "ParamClass",
    "Status",
    "ParamSpec",
    "REGISTRY",
    "recommend_candidates",
    "best_so_far_curves",
    "determine",
    "main",
]


class ParamClass(str, Enum):
    MEASURE = "MEASURE"        # optimise for adequacy (plateau), not performance
    CALIBRATE = "CALIBRATE"    # set once, identically across arms, on pre-test data
    FIX = "FIX"                # held constant for experimental control (do NOT tune)
    REALISTIC = "REALISTIC"    # credible real-world value, not result-maximising


class Status(str, Enum):
    DETERMINED = "DETERMINED"  # value resolved with evidence
    PENDING = "PENDING"        # awaits a pilot/calibration before freeze
    FIX_NEEDED = "FIX_NEEDED"  # current value is wrong and must change
    VERIFY = "VERIFY"          # plausibly fine; confirm with an existing test
    FIXED = "FIXED"            # locked by design/convention; no action


@dataclass(frozen=True)
class ParamSpec:
    name: str
    klass: ParamClass
    method: str            # how "best" is decided for this parameter
    determination: str     # where the value comes from / what to run
    blocks_freeze: bool    # True if the campaign must not be frozen while this is unresolved


# The material parameters. Class + method are metadata; current values are read from config at runtime so
# this never duplicates the single source of truth (CLAUDE.md: code reads config, never hardcodes).
REGISTRY: tuple[ParamSpec, ...] = (
    # ---- MEASURE (the only optimised parameters; optimise for adequacy) ----
    ParamSpec("train_steps_per_candidate", ParamClass.MEASURE,
              "eval-return knee (convergence)", "scripts/learning_curve.recommend_budget", True),
    ParamSpec("n_seeds", ParamClass.MEASURE,
              "paired-CRN power at the SESOI", "scripts/power_analysis + sigma_seed pilot", True),
    ParamSpec("candidates_per_arm", ParamClass.MEASURE,
              "search saturation (best-fitness plateau)", "determine_design.recommend_candidates", True),
    # ---- CALIBRATE (set once, identically across arms, on pre-test data) ----
    ParamSpec("lambda_frozen", ParamClass.CALIBRATE,
              "pre-2015 fitness calibration fold", "config/inference.yaml fitness.calibration_fold", True),
    ParamSpec("sesoi", ParamClass.CALIBRATE,
              "smallest practically-relevant edge", "frozen 0.05 DSR (~0.07 ann-Sharpe)", False),
    ParamSpec("embargo_trading_days", ParamClass.CALIBRATE,
              "purge >= feature lookback + horizon", "verify effective purge >= lookback (60)", False),
    ParamSpec("multiplicity", ParamClass.CALIBRATE,
              "family-wise / FDR error control", "IUT within H2 + BH/RW across the union", False),
    ParamSpec("dsr_trial_count_rule", ParamClass.CALIBRATE,
              "selection-aware deflation", "per_arm_candidates (Bailey-Lopez de Prado)", False),
    # ---- FIX (held constant for control; tuning confounds the channel) ----
    ParamSpec("sac_hyperparameters", ParamClass.FIX,
              "SB3 defaults, identical across arms", "config/algos.yaml (null = SB3 default)", False),
    ParamSpec("learning_starts", ParamClass.FIX,
              "Phase-0 validated stability", "1000 (not SB3's 100)", False),
    ParamSpec("popart", ParamClass.FIX,
              "critic value-scale normalisation", "on (explosion fix)", False),
    ParamSpec("llm_decoding", ParamClass.FIX,
              "held identical; only feedback varies", "Opus 4.8, K=16, max_tokens 4096", False),
    # ---- REALISTIC (credible, not result-maximising) ----
    ParamSpec("n_assets", ParamClass.REALISTIC, "diversified tradable book", "30 from 953 PIT pool", False),
    ParamSpec("lookback_days", ParamClass.REALISTIC, "feature window", "60", False),
    ParamSpec("headline_bps", ParamClass.REALISTIC, "realistic large-cap cost", "10 bps proportional", False),
    ParamSpec("data_splits", ParamClass.REALISTIC, "sealed temporal holdout", "10y/3y/8y train/val/test", False),
    ParamSpec("delisting_returns", ParamClass.REALISTIC, "survivorship-free", "retain", False),
    ParamSpec("cash_daily_rate", ParamClass.REALISTIC, "risk-free accrual on cash", "risk-free series (R20)", False),
)


def best_so_far_curves(records: list[dict[str, Any]], *, fitness_key: str = "val_fitness") -> dict[str, list[float]]:
    """Reduce raw run records to per-arm best-fitness-so-far curves indexed by generation.

    Each record carries ``arm``, ``generation`` and ``metrics[fitness_key]``. Returns ``{arm: [best after
    gen 0, best after gen 1, ...]}`` (monotone non-decreasing) — the input :func:`recommend_candidates` reads.
    """
    by_arm_gen: dict[str, dict[int, float]] = {}
    for r in records:
        arm = r.get("arm")
        gen = r.get("generation")
        val = (r.get("metrics") or {}).get(fitness_key)
        if arm is None or gen is None or not isinstance(val, (int, float)):
            continue
        g = int(gen)
        cur = by_arm_gen.setdefault(str(arm), {})
        cur[g] = max(cur.get(g, float("-inf")), float(val))
    curves: dict[str, list[float]] = {}
    for arm, gen_best in by_arm_gen.items():
        best = float("-inf")
        curve: list[float] = []
        for g in sorted(gen_best):
            best = max(best, gen_best[g])
            curve.append(best)
        curves[arm] = curve
    return curves


def recommend_candidates(
    best_so_far: dict[str, list[float]],
    *,
    candidates_per_gen: int,
    patience: int = 2,
    rel_tol: float = 0.0,
) -> dict[str, Any]:
    """Objective search-saturation detector — the candidate-budget analogue of ``recommend_budget``.

    Given each arm's best-fitness-SO-FAR curve over generations, an arm is SATURATED when its best has not
    improved over the last ``patience`` generations (by more than ``rel_tol`` of its own range). The
    recommended ``candidates_per_arm`` is set by the SLOWEST arm to saturate (matched compute across arms):
    ``(first generation at which that arm reached its final plateau + 1) * candidates_per_gen``. If ANY
    reflection arm is still improving at the last generation, ``saturated=False`` with a loud reason — the
    search budget is too small and the arms' "best" is budget-limited, biasing the channel contrast.

    Returns ``{recommended_candidates, saturated, reason, per_arm}``. ``saturated`` is ``None`` when no arm
    has enough generations (``< patience + 1``) to judge. Diagnostic only — it INFORMS the (amendment-gated)
    ``candidates_per_arm``; no number enters the dissertation.
    """
    judged: dict[str, dict[str, Any]] = {}
    still_rising: list[str] = []
    sat_gens: list[int] = []
    for arm, curve in best_so_far.items():
        if len(curve) < patience + 1:
            judged[arm] = {"saturated": None, "reason": "too few generations to judge"}
            continue
        rng = max(curve[-1] - curve[0], abs(curve[-1]) * 1e-9, 1e-12)
        tol = float(rel_tol) * rng
        recent_gain = curve[-1] - curve[-1 - patience]
        is_sat = recent_gain <= tol
        # First generation at which this arm reached (within tol) its final plateau value.
        final = curve[-1]
        sat_gen = next((g for g, v in enumerate(curve) if v >= final - tol), len(curve) - 1)
        judged[arm] = {"saturated": bool(is_sat), "saturation_gen": int(sat_gen),
                       "recent_gain": float(recent_gain)}
        if is_sat:
            sat_gens.append(sat_gen)
        else:
            still_rising.append(arm)

    decidable = [a for a, j in judged.items() if j.get("saturated") is not None]
    if not decidable:
        return {"recommended_candidates": None, "saturated": None,
                "reason": "no arm has enough generations to judge saturation", "per_arm": judged}
    if still_rising:
        return {"recommended_candidates": None, "saturated": False,
                "reason": (f"arms still improving at the last generation: {sorted(still_rising)} — the search "
                           "budget is too small (their best is budget-limited); EXTEND candidates_per_arm"),
                "per_arm": judged}
    # All decidable arms saturated: the slowest setter fixes the matched budget (+1 -> count, not index).
    rec = (max(sat_gens) + 1) * int(candidates_per_gen)
    return {"recommended_candidates": int(rec), "saturated": True,
            "reason": (f"all arms saturated by generation {max(sat_gens)} "
                       f"(x{candidates_per_gen} candidates/gen = {rec} candidates)"),
            "per_arm": judged}


def determine(evidence: dict[str, Any]) -> dict[str, Any]:
    """Overlay dynamic determination STATUS onto the registry from available evidence (pure; no IO).

    ``evidence`` keys (all optional; missing -> the parameter reports its default status):
      ``recommended_budget``  -> B* resolved (DETERMINED) else PENDING.
      ``candidates_saturated``-> True/False/None from :func:`recommend_candidates`.
      ``lambda_frozen``       -> None/null -> PENDING (calibration not run) else DETERMINED.
      ``cash_daily_rate``     -> 0.0 -> FIX_NEEDED (silently compounds cash) else DETERMINED/FIXED.
      ``sigma_seed_pilot``    -> True if the seed-variance pilot has run (n_seeds DETERMINED) else PENDING.

    Returns ``{rows, freeze_ready, blockers}``: one row per registry entry with its resolved status, and a
    freeze-readiness verdict (ready iff no freeze-blocking parameter is PENDING/FIX_NEEDED).
    """
    def status_for(spec: ParamSpec) -> Status:
        n = spec.name
        if n == "train_steps_per_candidate":
            return Status.DETERMINED if evidence.get("recommended_budget") else Status.PENDING
        if n == "candidates_per_arm":
            sat = evidence.get("candidates_saturated")
            return Status.DETERMINED if sat is True else (Status.PENDING if sat in (False, None) else Status.PENDING)
        if n == "n_seeds":
            return Status.DETERMINED if evidence.get("sigma_seed_pilot") else Status.PENDING
        if n == "lambda_frozen":
            return Status.DETERMINED if evidence.get("lambda_frozen") is not None else Status.PENDING
        if n == "cash_daily_rate":
            cdr = evidence.get("cash_daily_rate")
            return Status.FIX_NEEDED if (cdr is not None and float(cdr) == 0.0) else Status.DETERMINED
        if n == "embargo_trading_days":
            return Status.VERIFY
        if spec.klass in (ParamClass.FIX, ParamClass.REALISTIC) or spec.klass is ParamClass.CALIBRATE:
            return Status.FIXED
        return Status.FIXED

    rows = []
    blockers: list[str] = []
    for spec in REGISTRY:
        st = status_for(spec)
        rows.append({"name": spec.name, "class": spec.klass.value, "method": spec.method,
                     "determination": spec.determination, "status": st.value})
        if spec.blocks_freeze and st in (Status.PENDING, Status.FIX_NEEDED):
            blockers.append(spec.name)
    return {"rows": rows, "freeze_ready": not blockers, "blockers": blockers}


def _write_markdown(result: dict[str, Any], evidence: dict[str, Any], path: Path) -> None:
    order = {ParamClass.MEASURE.value: 0, ParamClass.CALIBRATE.value: 1,
             ParamClass.FIX.value: 2, ParamClass.REALISTIC.value: 3}
    rows = sorted(result["rows"], key=lambda r: (order[r["class"]], r["name"]))
    verdict = "✅ FREEZE-READY" if result["freeze_ready"] else f"⛔ BLOCKED on {result['blockers']}"
    lines = [
        "# Design Determination — every parameter, its method, and its status",
        "",
        "Generated by `scripts/determine_design.py`. \"Best\" means *methodologically-correct and frozen with "
        "evidence*, **not** performance-maximal — optimising parameters to maximise the result would be the "
        "garden of forking paths and is never done here. The sealed test (2018-2025) is touched by nothing in "
        "this determination.",
        "",
        f"**Status: {verdict}**",
        "",
        "| Parameter | Class | Method (how 'best' is decided) | Determination source | Status |",
        "|-----------|-------|--------------------------------|----------------------|--------|",
    ]
    for r in rows:
        lines.append(f"| `{r['name']}` | {r['class']} | {r['method']} | {r['determination']} | {r['status']} |")
    if not result["freeze_ready"]:
        lines += ["", "## Blocking actions before freeze", ""]
        lines += [f"- `{b}`" for b in result["blockers"]]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _gather_evidence() -> dict[str, Any]:
    """Best-effort read of current config values + any pilot outputs already on disk (no GPU, no test data)."""
    ev: dict[str, Any] = {}
    try:
        from src.utils.config import load_config

        inf = load_config("inference")
        ev["lambda_frozen"] = (inf.get("fitness") or {}).get("lambda_frozen")
        env = load_config("environment")
        ev["cash_daily_rate"] = (env.get("state") or {}).get("cash_daily_rate")
    except Exception:  # noqa: BLE001 - the reporter must run even if config import is unavailable
        pass
    lc = Path("outputs/tables/learning_curve.json")
    if lc.exists():
        try:
            data = json.loads(lc.read_text(encoding="utf-8"))
            ev["recommended_budget"] = (data.get("convergence") or {}).get("recommended_budget")
        except Exception:  # noqa: BLE001
            pass
    return ev


def main() -> None:
    p = argparse.ArgumentParser(description="Design Determination Pipeline — parameter resolution + freeze-readiness.")
    p.add_argument("--out", default="docs/DESIGN_DETERMINATION.md", help="Determination report path.")
    args = p.parse_args()

    evidence = _gather_evidence()
    result = determine(evidence)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    _write_markdown(result, evidence, out)
    (out.with_suffix(".json")).write_text(
        json.dumps({"evidence": evidence, **result}, indent=2), encoding="utf-8")

    print("=" * 72)
    print("[determine_design] Design Determination Pipeline")
    for r in sorted(result["rows"], key=lambda r: r["class"]):
        print(f"  [{r['class']:9s}] {r['name']:28s} -> {r['status']}")
    print("-" * 72)
    print("FREEZE-READY" if result["freeze_ready"] else f"BLOCKED on: {result['blockers']}")
    print(f"wrote {out}")
    print("=" * 72)


if __name__ == "__main__":
    main()
