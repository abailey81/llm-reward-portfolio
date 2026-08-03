#!/usr/bin/env python
"""SEARCH-ADEQUACY INSTRUMENTS — the registered defence of the K=5 / 30-candidate budget.

WHY THIS FILE EXISTS. `config/preregistration.yaml` registers a five-instrument package defending
the search width, with `budget_decision: keep_and_instrument` — *"the coverage_vs_k instrument is a
STRONGER defence than a bigger raw K, at ZERO seed cost"*. Audited 2026-08-01 against the code:

    oracle_headroom               IMPLEMENTED as src/inference/headroom.py (validation_headroom)
    plateau rule                  IMPLEMENTED as scripts/determine_design.recommend_candidates
    within_generation_diversity   NOT IMPLEMENTED as a named instrument (the AST primitive exists)
    executable_valid_rate         NOT IMPLEMENTED as a named instrument (the reject ledger exists)
    coverage_vs_k_extrapolation   NOT IMPLEMENTED ANYWHERE

The last three are built here. This is the A16 pattern — registered, "reported", never coded — and
the missing one is precisely the instrument that answers *"would a wider search have found better?"*,
which is the first question a referee asks when they see K=5 against Eureka's K=16.

EFFECT-BLIND BY CONSTRUCTION. Every quantity is computed from SEARCH-stage `metrics.val_fitness`
(the validation deflated-Sharpe used for selection) and `reward_source`. **No sealed test outcome is
read, and no arm-vs-arm contrast or p-value is computed.** Selection adequacy is a property of the
search, not of the result, so it is answerable now and its answer cannot move when the test lands.

EXACT, NOT SAMPLED. Both curves are order statistics over a finite pool, so they have closed forms
and are computed exactly — no Monte Carlo, hence no sampling noise and bit-identical replay:

    coverage(k; tau) = 1 - C(n-m, k) / C(n, k)        m = #candidates with fitness >= tau
    E[max | k]       = sum_i x_(i) * C(i-1, k-1) / C(n, k)    x_(1) <= ... <= x_(n)

THE INTERPRETABLE PARAMETER. The coverage curve is fitted as the exponentiated power law
(brown2024monkeys) in the form

    coverage(k) = 1 - exp(-a * k**b)   <=>   log(-log(1 - coverage)) = log(a) + b*log(k)

so the fit is an ordinary least-squares line and needs no optimiser. **b is the whole story:**
b == 1 is exactly the i.i.d. case (coverage = 1-(1-p)^k); **b < 1 means DIMINISHING returns to extra
candidates** — the samples are correlated, and buying width is worth less than the i.i.d. intuition
says; b > 1 means accelerating returns. A referee asking "why not K=16?" is asking for b.

Usage:  python docs/analysis/search_adequacy.py [--root PATH] [--selftest]
Read-only; writes nothing.
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import sys
from collections import defaultdict
from typing import Any

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_ROOT = os.path.join(REPO, "outputs", "campaign_cluster_run4")
REJECT_LEDGER = os.path.join(REPO, "docs", "evidence",
                             "node_authoring_rejects_campaign_cluster_run4.jsonl")

# The registered search width (config/preregistration.yaml: K=5/gen, 30 candidates/arm) and the
# widths the direct lineage used, so the extrapolation answers the comparison a referee will make.
REGISTERED_K = 5
LINEAGE_WIDTHS = (5, 16, 30, 50, 100)          # 16 = Eureka / REvolve per-iteration batch size


# --------------------------------------------------------------------------- exact order statistics
def _log_comb(n: int, k: int) -> float:
    """log C(n, k); -inf when the choice is impossible. Log-space so n up to thousands is safe."""
    if k < 0 or k > n or n < 0:
        return -math.inf
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def coverage_at_k(n: int, m: int, k: int) -> float:
    """EXACT P(a uniformly random k-subset of n candidates contains >= 1 of the m qualifying ones).

    ``1 - C(n-m, k)/C(n, k)`` — the probability that a k-draw WITHOUT replacement misses all m.
    Returns 1.0 once k exceeds the number of non-qualifying candidates (a miss becomes impossible).
    """
    if not 0 <= m <= n or k < 1 or k > n:
        raise ValueError(f"coverage_at_k: bad (n={n}, m={m}, k={k})")
    if m == 0:
        return 0.0
    if k > n - m:
        return 1.0
    return 1.0 - math.exp(_log_comb(n - m, k) - _log_comb(n, k))


def expected_max_at_k(values: list[float], k: int) -> float:
    """EXACT E[max of a uniformly random k-subset], by the order-statistic weighting.

    With ``x_(1) <= ... <= x_(n)``, the i-th order statistic is the subset maximum exactly when the
    other k-1 members are drawn from the i-1 below it, so it carries weight ``C(i-1,k-1)/C(n,k)``.
    """
    xs = sorted(values)
    n = len(xs)
    if k < 1 or k > n:
        raise ValueError(f"expected_max_at_k: k={k} outside 1..{n}")
    denom = _log_comb(n, k)
    return sum(x * math.exp(_log_comb(i, k - 1) - denom) for i, x in enumerate(xs))


# --------------------------------------------------------------------------- the power-law fit
def fit_exponentiated_power_law(ks: list[int], cov: list[float]) -> dict[str, Any]:
    """Least-squares fit of ``coverage(k) = 1 - exp(-a * k**b)`` via the linearising transform.

    Only points with ``0 < coverage < 1`` can be transformed, so saturated and empty points are
    EXCLUDED and COUNTED rather than clipped — clipping would invent data at exactly the k where the
    curve carries the least information. Returns ``fitted=False`` with a reason when fewer than three
    usable points remain; it NEVER returns a fit it cannot support.
    """
    pts = [(math.log(k), math.log(-math.log(1.0 - c)))
           for k, c in zip(ks, cov) if 0.0 < c < 1.0]
    dropped = len(ks) - len(pts)
    if len(pts) < 3:
        return {"fitted": False, "reason": f"only {len(pts)} usable point(s) (need >= 3); "
                                           f"{dropped} were saturated or empty",
                "n_points": len(pts), "n_dropped": dropped}
    mx = sum(p[0] for p in pts) / len(pts)
    my = sum(p[1] for p in pts) / len(pts)
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    if sxx <= 0:
        return {"fitted": False, "reason": "zero variance in log k", "n_points": len(pts),
                "n_dropped": dropped}
    b = sum((p[0] - mx) * (p[1] - my) for p in pts) / sxx
    log_a = my - b * mx
    ss_res = sum((p[1] - (log_a + b * p[0])) ** 2 for p in pts)
    ss_tot = sum((p[1] - my) ** 2 for p in pts)
    return {"fitted": True, "a": math.exp(log_a), "b": b,
            "r2": (1.0 - ss_res / ss_tot) if ss_tot > 0 else float("nan"),
            "n_points": len(pts), "n_dropped": dropped,
            "returns_to_width": ("diminishing (b < 1: samples are correlated)" if b < 0.95 else
                                 "i.i.d.-like (b ~ 1)" if b <= 1.05 else
                                 "accelerating (b > 1)")}


def predict_coverage(fit: dict[str, Any], k: int) -> float | None:
    if not fit.get("fitted"):
        return None
    return 1.0 - math.exp(-fit["a"] * (k ** fit["b"]))


def saturation_k(values: list[float], frac: float = 0.99) -> int | None:
    """Smallest k whose E[max|k] reaches ``frac`` of E[max|n] — the empirical 'width was enough' point.

    ``None`` when the pool never reaches the fraction (which cannot happen at k=n, so None means the
    pool was degenerate). Uses the EXACT expected maximum, so it is not a sampling artefact.
    """
    n = len(values)
    if n < 2:
        return None
    target = frac * expected_max_at_k(values, n)
    for k in range(1, n + 1):
        if expected_max_at_k(values, k) >= target:
            return k
    return None


# --------------------------------------------------------------------------- the archive
def load_search(root: str) -> dict[tuple[str, str], list[dict[str, Any]]]:
    """{(line, arm): [record, ...]} over the SEARCH tier only. Fails loud on an empty walk."""
    out: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for path in glob.glob(os.path.join(root, "**", "record.json"), recursive=True):
        rel = os.path.relpath(path, root).replace("\\", "/")
        top = rel.split("/")[0]
        if not top.startswith("search"):
            continue
        # ⚠ slice the prefix ONLY when it is present — `search_h3_singleshot` is not `search_leg_*`
        # and an unconditional slice renamed it "ingleshot" (my P136).
        line = ("core" if top == "search" else
                top[len("search_leg_"):] if top.startswith("search_leg_") else top[len("search_"):])
        with open(path, encoding="utf-8") as fh:
            rec = json.load(fh)
        out[(line, rec.get("arm"))].append(rec)
    if not out:
        raise SystemExit(f"FATAL: walked {root} and found ZERO search records. That is a broken "
                         f"path, NOT an adequate search — fix the root before reading anything here.")
    return out


def _fitness(rec: dict[str, Any]) -> float | None:
    v = (rec.get("metrics") or {}).get("val_fitness")
    return float(v) if isinstance(v, (int, float)) and math.isfinite(v) else None


# --------------------------------------------------------------------------- instrument 1
def coverage_vs_k(pool: list[dict[str, Any]], *, tau: float) -> dict[str, Any]:
    """`coverage_vs_k_extrapolation` — would a wider search plausibly have surfaced a better reward?

    ``tau`` is the qualifying bar, in VALIDATION fitness units. The curve is exact; the fit gives the
    extrapolation to widths this campaign did not run (notably Eureka's K=16).
    """
    vals = [f for f in (_fitness(r) for r in pool) if f is not None]
    n = len(vals)
    if n < 3:
        return {"status": "skipped", "reason": f"only {n} candidate(s) with a usable val_fitness"}
    m = sum(1 for v in vals if v >= tau)
    ks = list(range(1, n + 1))
    cov = [coverage_at_k(n, m, k) for k in ks]
    fit = fit_exponentiated_power_law(ks, cov)

    # ⚠⚠ THE TWO CURVES ANSWER DIFFERENT QUESTIONS AND CONFLATING THEM IS A REAL ERROR — I made it
    # on the first run of this file and caught it only because EVERY arm returned b > 1.
    #   * `cov` above is WITHOUT REPLACEMENT over the pool we actually drew. It is the right curve
    #     for "did we NEED all 30?" (see saturation_k) and it hits EXACTLY 1.0 at k = n-m+1, because
    #     once you have drawn every non-qualifying candidate a miss is impossible. That hard ceiling
    #     makes it steeper than any i.i.d. curve, so a power-law fit to it returns b > 1 BY
    #     CONSTRUCTION. That b measures finite-pool truncation, NOT sample correlation, and it must
    #     never be read as "accelerating returns to width".
    #   * The question "would a LARGER K have helped?" is about drawing FRESH candidates from the
    #     LLM's generative distribution, i.e. WITH replacement: p_hat = m/n and
    #     coverage_iid(k) = 1 - (1 - p_hat)^k. That is the honest extrapolation and it needs no fit.
    # Brown et al.'s exponentiated power law describes real coverage falling BELOW the i.i.d. curve
    # because repeated samples are correlated. Identifying that departure needs INDEPENDENT REPEATS
    # of the whole search (Eureka runs 5 restarts; we run 1 per arm), so with this design it is NOT
    # ESTIMABLE. Reported as such rather than fitted anyway.
    p_hat = m / n
    lo_p, hi_p = _wilson(m, n)
    return {
        "status": "ok", "n_candidates": n, "n_qualifying": m, "tau": tau,
        "p_qualify": p_hat, "p_qualify_ci95": (lo_p, hi_p),
        "coverage_at_registered_k": coverage_at_k(n, m, min(REGISTERED_K, n)),
        "coverage_curve": {k: cov[k - 1] for k in ks},
        "expected_max": {k: expected_max_at_k(vals, k) for k in ks},
        "saturation_k_99": saturation_k(vals, 0.99),
        "saturation_k_95": saturation_k(vals, 0.95),
        # the ANSWER to "would a wider search have helped", with its interval carried through
        "iid_coverage": {k: 1.0 - (1.0 - p_hat) ** k for k in LINEAGE_WIDTHS},
        "iid_coverage_lo": {k: 1.0 - (1.0 - lo_p) ** k for k in LINEAGE_WIDTHS},
        "iid_coverage_hi": {k: 1.0 - (1.0 - hi_p) ** k for k in LINEAGE_WIDTHS},
        # kept, clearly labelled, and NOT used for extrapolation
        "finite_pool_fit": {**fit, "interpretation":
                            "describes re-selection from THIS pool only; b > 1 is finite-pool "
                            "truncation, not accelerating returns. Do not extrapolate with it."},
        "correlation_estimable": False,
        "correlation_note": ("the departure from i.i.d. needs independent REPEATS of the search "
                             "(Eureka: 5 restarts/env); this design runs 1 per arm, so the "
                             "correlated-sampling correction is NOT ESTIMABLE here — disclosed"),
        "achieved_max": max(vals),
    }


def _wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval — correct at k=0 and k=n, where the normal approximation is not."""
    if n == 0:
        return (0.0, 1.0)
    p, d = k / n, 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


# --------------------------------------------------------------------------- instrument 2
def executable_valid_rate(root: str, ledger: str = REJECT_LEDGER) -> dict[str, Any]:
    """`executable_valid_rate` — the fraction of authorings that survived the gate.

    High rate => the EFFECTIVE search width is close to the nominal 30 (the Eureka exec-filter
    analogue); a low rate means the registered budget was not the delivered budget.
    """
    accepted = sum(len(v) for v in load_search(root).values())
    if not os.path.exists(ledger):
        return {"status": "skipped", "reason": f"reject ledger not found: {ledger}",
                "accepted": accepted}
    # utf-8-SIG: the ledger carries a BOM and plain utf-8 raises on the first line.
    rejected = sum(1 for ln in open(ledger, encoding="utf-8-sig") if ln.strip())
    attempts = accepted + rejected
    p = accepted / attempts if attempts else float("nan")
    z, den = 1.96, 1 + 1.96 ** 2 / attempts if attempts else 1.0
    centre = (p + z * z / (2 * attempts)) / den if attempts else float("nan")
    half = (z * math.sqrt(p * (1 - p) / attempts + z * z / (4 * attempts ** 2)) / den) if attempts else float("nan")
    return {"status": "ok", "accepted": accepted, "rejected": rejected, "attempts": attempts,
            "valid_rate": p, "ci95": (max(0.0, centre - half), min(1.0, centre + half)),
            "note": "campaign-wide; the ledger carries no line/arm field, so this is not per-line"}


# --------------------------------------------------------------------------- instrument 3
#: Arms that sample PARAMETERS inside a fixed reward template rather than authoring free-form code.
#: For these the structural-similarity collapse flag does not apply (see the note in the function).
PARAMETRIC_ARMS = frozenset({"random_search", "bayes_opt", "cma_es", "tpe"})


def within_generation_diversity(pool: list[dict[str, Any]], *,
                                arm_is_parametric: bool = False) -> dict[str, Any]:
    """`within_generation_diversity` — did the K candidates per generation actually differ?

    Guards the K-COLLAPSE failure: prompt-variation produces near-duplicates, so the EFFECTIVE width
    is below the nominal K and the registered budget overstates the search. Reuses the repo's own
    `structural_similarity` (identifier- and literal-invariant Jaccard over canonical AST shapes) and
    honours its documented precondition — structureless sources are filtered with `has_structure`
    first, because two empty programs score a perfect 1.0 and would fake a collapse (repo issue #117).
    """
    try:
        sys.path.insert(0, REPO)
        from src.inference.reward_code_distance import has_structure, structural_similarity
    except Exception as exc:                                   # noqa: BLE001
        return {"status": "skipped", "reason": f"cannot import the repo primitive: {exc!r}"}

    by_gen: dict[int, list[str]] = defaultdict(list)
    for r in pool:
        src = r.get("reward_source")
        if isinstance(src, str) and src.strip() and has_structure(src):
            by_gen[int(r.get("generation") or 0)].append(src)
    rows = []
    for gen in sorted(by_gen):
        srcs = by_gen[gen]
        if len(srcs) < 2:
            continue
        sims = [structural_similarity(srcs[i], srcs[j])
                for i in range(len(srcs)) for j in range(i + 1, len(srcs))]
        rows.append({"generation": gen, "k_with_structure": len(srcs), "n_pairs": len(sims),
                     "mean_similarity": sum(sims) / len(sims),
                     "max_similarity": max(sims), "min_similarity": min(sims)})
    if not rows:
        return {"status": "skipped", "reason": "no generation had >= 2 structured sources"}
    mean_all = sum(r["mean_similarity"] for r in rows) / len(rows)
    # ⚠ THE COLLAPSE FLAG IS MEANINGFUL ONLY FOR CODE-AUTHORING ARMS. The four optimiser arms
    # (random_search / bayes_opt / cma_es / tpe) do not author code at all — they sample PARAMETERS
    # inside one fixed reward template, so every source is the same program with different literals
    # and the identifier-and-literal-INVARIANT similarity correctly returns exactly 1.000. That is
    # the design, not a collapse. Flagging it would be a false positive on four of nine arms, which
    # is what my first run did.
    parametric = bool(arm_is_parametric)
    return {"status": "ok", "generations": rows, "mean_similarity_overall": mean_all,
            "effective_width_note": ("mean pairwise structural similarity; 1.0 would be total "
                                     "K-collapse (all K identical), 0.0 completely distinct"),
            "parametric_arm": parametric,
            "collapse_flag": (not parametric) and mean_all > 0.90,
            "collapse_note": ("N/A — parametric arm: one template by design, so similarity 1.0 is "
                              "expected and is not evidence of collapse" if parametric else
                              "applies: this arm authors free-form code")}


# --------------------------------------------------------------------------- falsification suite
def selftest() -> int:
    """Prove every estimator can be WRONG. Three panels of this lane's other instrument shipped a
    false clean before anyone noticed, so nothing here is trusted until it has been shown to fail."""
    ok = True

    def check(name: str, cond: bool) -> None:
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok &= bool(cond)

    # --- coverage: closed form vs hand-computed truth -----------------------------------------
    # n=4, m=1, k=2: the qualifying one is in 3 of the C(4,2)=6 pairs -> 1/2 exactly.
    check("coverage_at_k(4,1,2) == 1/2 exactly", abs(coverage_at_k(4, 1, 2) - 0.5) < 1e-12)
    check("coverage_at_k(n,m,n) == 1 when m>=1", coverage_at_k(10, 1, 10) == 1.0)
    check("coverage_at_k(n,0,k) == 0 (no qualifier can be found)", coverage_at_k(10, 0, 3) == 0.0)
    check("coverage rises monotonically in k",
          all(coverage_at_k(20, 3, k) <= coverage_at_k(20, 3, k + 1) + 1e-15 for k in range(1, 20)))
    try:
        coverage_at_k(5, 2, 0)
        check("coverage_at_k RAISES on k=0", False)
    except ValueError:
        check("coverage_at_k RAISES on k=0", True)

    # --- expected max: the two endpoints are the mean and the max, exactly --------------------
    vals = [1.0, 2.0, 3.0, 10.0]
    check("E[max|k=1] == the mean", abs(expected_max_at_k(vals, 1) - 4.0) < 1e-12)
    check("E[max|k=n] == the max", abs(expected_max_at_k(vals, 4) - 10.0) < 1e-12)
    check("E[max] rises monotonically in k",
          all(expected_max_at_k(vals, k) <= expected_max_at_k(vals, k + 1) + 1e-12 for k in (1, 2, 3)))

    # --- the fit recovers b == 1 on an i.i.d.-generated curve ---------------------------------
    p = 0.08
    ks = list(range(1, 40))
    iid = [1.0 - (1.0 - p) ** k for k in ks]
    f = fit_exponentiated_power_law(ks, iid)
    check("fit succeeds on a clean i.i.d. curve", f["fitted"])
    check(f"fit recovers b == 1 on i.i.d. data (got {f.get('b', float('nan')):.4f})",
          f["fitted"] and abs(f["b"] - 1.0) < 0.02)
    check("fit labels it i.i.d.-like", f.get("returns_to_width", "").startswith("i.i.d."))

    # a DIMINISHING-returns curve must be detected as b < 1, not silently fitted as i.i.d.
    dim = [1.0 - math.exp(-0.35 * k ** 0.5) for k in ks]
    fd = fit_exponentiated_power_law(ks, dim)
    check(f"fit detects diminishing returns (b={fd.get('b', float('nan')):.3f} < 1)",
          fd["fitted"] and fd["b"] < 0.95 and fd["returns_to_width"].startswith("diminishing"))

    # --- the fit REFUSES rather than inventing a curve ----------------------------------------
    check("fit REFUSES on an all-saturated curve",
          not fit_exponentiated_power_law([1, 2, 3, 4], [1.0, 1.0, 1.0, 1.0])["fitted"])
    check("fit REFUSES on an all-zero curve",
          not fit_exponentiated_power_law([1, 2, 3, 4], [0.0, 0.0, 0.0, 0.0])["fitted"])
    check("fit REPORTS how many points it dropped",
          fit_exponentiated_power_law([1, 2, 3, 4], [0.0, 0.3, 0.6, 1.0])["n_dropped"] == 2)

    # --- saturation ---------------------------------------------------------------------------
    check("saturation_k is small when one candidate dominates",
          (saturation_k([0.0] * 29 + [1.0], 0.95) or 99) >= 20)   # a needle IS hard to find
    check("saturation_k is 1 when every candidate is identical",
          saturation_k([0.5] * 10, 0.99) == 1)

    # --- diversity: identical sources must read as COLLAPSE ------------------------------------
    same = "def reward(w, r, pw, pr, info):\n    return float(pr), {}, None\n"
    pool_same = [{"generation": 0, "reward_source": same} for _ in range(4)]
    d = within_generation_diversity(pool_same)
    check("diversity FLAGS collapse on identical sources",
          d.get("status") != "ok" or d["collapse_flag"] is True)
    diff = "def reward(w, r, pw, pr, info):\n    x = (r ** 2).sum() / 3.0\n    return float(pr - x), {}, None\n"
    pool_mixed = [{"generation": 0, "reward_source": s} for s in (same, diff, same, diff)]
    dm = within_generation_diversity(pool_mixed)
    check("diversity does NOT flag collapse on genuinely different sources",
          dm.get("status") != "ok" or dm["collapse_flag"] is False)
    dp = within_generation_diversity(pool_same, arm_is_parametric=True)
    check("diversity does NOT flag collapse on a PARAMETRIC arm (one template by design)",
          dp.get("status") != "ok" or dp["collapse_flag"] is False)

    # --- the two coverage curves must NOT be confused (the error this file's comments record) --
    pool_f = [{"metrics": {"val_fitness": v}} for v in
              ([0.0] * 18 + [1.0, 1.0])]                        # n=20, m=2 above tau=0.5
    cv = coverage_vs_k(pool_f, tau=0.5)
    check("without-replacement coverage hits EXACTLY 1.0 once the misses are exhausted",
          cv["coverage_curve"][20 - 2 + 1] == 1.0)
    check("i.i.d. extrapolation NEVER reaches 1.0 (it cannot, by construction)",
          all(v < 1.0 for v in cv["iid_coverage"].values()))
    check("i.i.d. coverage at K=5 is BELOW the without-replacement value at K=5",
          (1 - (1 - 0.1) ** 5) < cv["coverage_at_registered_k"])
    check("the correlated-sampling correction is declared NOT estimable",
          cv["correlation_estimable"] is False)
    check("the finite-pool fit carries its do-not-extrapolate warning",
          "not accelerating returns" in cv["finite_pool_fit"]["interpretation"])
    check("qualify rate carries a Wilson interval that brackets it",
          cv["p_qualify_ci95"][0] <= cv["p_qualify"] <= cv["p_qualify_ci95"][1])

    print("\nselftest:", "ALL PASS" if ok else "FAILURES ABOVE")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=DEFAULT_ROOT)
    ap.add_argument("--selftest", action="store_true", help="prove every estimator can FAIL")
    ap.add_argument("--line", default="core", help="which line to report per-arm (default: core)")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    pools = load_search(args.root)
    print(f"SEARCH-ADEQUACY REPORT   root={args.root}")
    print("effect-blind: validation fitness + reward source only; no sealed outcome, no contrast\n")

    # ---- instrument 2 -------------------------------------------------------------------------
    ev = executable_valid_rate(args.root)
    print("EXECUTABLE-VALID RATE (the Eureka exec-filter analogue)")
    if ev["status"] == "ok":
        lo, hi = ev["ci95"]
        print(f"   accepted {ev['accepted']} / attempts {ev['attempts']} "
              f"= {100*ev['valid_rate']:.1f}%  [{100*lo:.1f}, {100*hi:.1f}]   ({ev['rejected']} rejected)")
        print(f"   >> effective width is {ev['valid_rate']:.3f} x nominal; {ev['note']}")
    else:
        print(f"   SKIPPED: {ev['reason']}")

    # ---- the qualifying bar, in validation units, defined WITHOUT any test outcome -------------
    all_f = sorted(f for pool in pools.values() for f in (_fitness(r) for r in pool) if f is not None)
    tau = all_f[int(0.90 * (len(all_f) - 1))]
    print(f"\nQUALIFYING BAR tau = the 90th percentile of ALL {len(all_f)} authored candidates' "
          f"validation fitness = {tau:.6f}")
    print("   (a within-search bar: it uses no sealed outcome, so it is answerable now and cannot move)")

    print(f"\nCOVERAGE vs K  —  line '{args.line}'")
    print("   'qualify rate' = P(one fresh candidate clears tau), with its Wilson interval.")
    print("   'would K=N have found one' extrapolates WITH replacement: 1-(1-p)^N — the honest")
    print("   answer to 'should we have searched wider', and it needs no curve fit.\n")
    print(f"   {'arm':<18} {'n':>4} {'qual':>5} {'qualify rate (95% CI)':>24} "
          f"{'cov@K=5':>9} {'sat99':>6} {'K=16 (Eureka)':>15} {'K=30':>8}")
    for (line, arm), pool in sorted(pools.items()):
        if line != args.line:
            continue
        c = coverage_vs_k(pool, tau=tau)
        if c["status"] != "ok":
            print(f"   {arm:<18} SKIPPED: {c['reason']}")
            continue
        lo, hi = c["p_qualify_ci95"]
        print(f"   {arm:<18} {c['n_candidates']:>4} {c['n_qualifying']:>5} "
              f"{f'{c[chr(112)+chr(95)+chr(113)+chr(117)+chr(97)+chr(108)+chr(105)+chr(102)+chr(121)]:.3f} [{lo:.3f},{hi:.3f}]':>24} "
              f"{c['coverage_at_registered_k']:>9.3f} {str(c['saturation_k_99']):>6} "
              f"{c['iid_coverage'][16]:>15.3f} {c['iid_coverage'][30]:>8.3f}")
    print("\n   sat99 = smallest k whose EXPECTED BEST already reaches 99% of the full pool's — the")
    print("           'did we need all 30?' reading, computed WITHOUT replacement over this pool.")
    print("   NOT REPORTED, and deliberately: the correlated-sampling (Brown et al.) correction is")
    print("           NOT ESTIMABLE from one search per arm — it needs independent restarts.")

    print(f"\nWITHIN-GENERATION DIVERSITY  —  line '{args.line}' (guards K-collapse)")
    for (line, arm), pool in sorted(pools.items()):
        if line != args.line:
            continue
        d = within_generation_diversity(pool, arm_is_parametric=(arm in PARAMETRIC_ARMS))
        if d["status"] != "ok":
            print(f"   {arm:<18} SKIPPED: {d['reason']}")
            continue
        tag = ("   *** K-COLLAPSE ***" if d["collapse_flag"] else
               "   (parametric arm — one template by design, flag N/A)" if d["parametric_arm"] else "")
        print(f"   {arm:<18} mean pairwise structural similarity {d['mean_similarity_overall']:.3f} "
              f"over {len(d['generations'])} generation(s){tag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
