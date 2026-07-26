"""Assemble the six confirmatory node p-values and run the RATIFIED graphical decision rule.

Bridges what ``scripts/analyze_campaign.py`` already computes to
``multiple_testing.graphical_alpha_propagation`` — the rule ratified 2026-07-26 (R108:
``primary_rule: bonferroni_weighted_graph``, superseding R31).

WHY A SEPARATE MODULE. The rule must be executable and testable WITHOUT campaign data, and the graph
must be READ from the registered config rather than copied (``forking_path_guard`` declares it FROZEN).
So ``analyze_campaign`` needs exactly one call, and this logic is unit-tested today — before any results
exist, which is precisely when a decision rule is allowed to be written.

FAIL-SAFE BY CONSTRUCTION. A node whose p-value cannot be located is reported ``untestable`` and can
never reject; it is NEVER silently treated as a pass or a fail. Every path searched is recorded, so a
shape mismatch surfaces in the artifact instead of producing a confidently wrong confirmatory verdict —
the worst possible failure here.

NODE MAP — every path below was VERIFIED against the producing code, not inferred from docstrings
(the 2026-07-26 deep review found 4 of 6 first-guess paths wrong, which is why this is spelled out):

===============  ==========================================================  =======================
node             source in ``out``                                            rule
===============  ==========================================================  =======================
N1_h2_tail       ``out["h2"]["tail_legs"][*]["pvalue_one_sided"]``            MAX over legs (IUT)
N2_h2_ra         ``out["h2"]["legs"][*]["pvalue_one_sided"]``                 MAX over legs (IUT)
N3_h3            ``out["h3"]["difference"]["pvalue_one_sided"]``              single test
N4_h4            ``out["h4"]["tests"][*]["pvalue_one_sided"]``                MAX over legs (IUT)
N5_structure     ``out["h2_structure"]["cvar"]["pvalue_one_sided"]``          single test (metric: cvar)
N6_h1            ``out["h1_beat_human"]["iut"]["iut_pvalue"]``                ALREADY the MAX over the
                                                                              canon, gated on
                                                                              ``all_baselines_present``
===============  ==========================================================  =======================

N5 reads the **cvar** sub-result because the registered node is
``{test: distributional_gt_placebo_shuffled, metric: cvar, level: 0.05}``. N6 reuses the pipeline's own
``iut_pvalue`` and honours ``all_baselines_present``: dominance is certifiable only when every canon
member is testable, so a missing member yields ``untestable`` rather than a cheaper claim.
"""
from __future__ import annotations

import math
from typing import Any

from src.inference.multiple_testing import graphical_alpha_propagation, registered_alpha_graph

__all__ = ["NODE_SOURCES", "tier_node_pvalues", "tier_verdict"]

#: node -> spec. ``legs`` = MAX over that list (intersection-union, Berger 1982); ``key`` = a single
#: value at ``path``; ``require`` = a boolean flag at ``path`` that must be True to certify.
NODE_SOURCES: dict[str, dict[str, Any]] = {
    "N1_h2_tail":   {"path": ("h2",), "legs": "tail_legs", "key": "pvalue_one_sided"},
    "N2_h2_ra":     {"path": ("h2",), "legs": "legs", "key": "pvalue_one_sided"},
    "N3_h3":        {"path": ("h3", "difference"), "key": "pvalue_one_sided"},
    "N4_h4":        {"path": ("h4",), "legs": "tests", "key": "pvalue_one_sided"},
    "N5_structure": {"path": ("h2_structure", "cvar"), "key": "pvalue_one_sided"},
    "N6_h1":        {"path": ("h1_beat_human", "iut"), "key": "iut_pvalue",
                     "require": "all_baselines_present"},
}


def _dig(out: Any, path: tuple[str, ...]) -> Any:
    node = out
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node


def _finite(value: Any) -> float | None:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def tier_node_pvalues(out: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Extract ONE p-value per confirmatory node from an ``analyze_campaign`` result dict.

    Returns ``{node: {"pvalue": float|None, "source": str, "rule": str, "n_legs": int|None,
    "reason": str|None}}``. ``pvalue is None`` means NOT TESTABLE — reported, never rejectable.
    """
    found: dict[str, dict[str, Any]] = {}
    for node, spec in NODE_SOURCES.items():
        path: tuple[str, ...] = spec["path"]
        pkey: str = spec["key"]
        source = 'out["' + '"]["'.join(path) + '"]'
        rec: dict[str, Any] = {
            "pvalue": None, "source": source, "n_legs": None, "reason": None,
            "rule": "max over legs (intersection-union, Berger 1982)" if spec.get("legs") else "single test",
        }
        blob = _dig(out, path)
        if not isinstance(blob, dict):
            rec["reason"] = f"no dict at {source}"
            found[node] = rec
            continue
        if spec.get("require") and not blob.get(spec["require"]):
            # e.g. N6: dominance is certifiable ONLY when every canon member is testable.
            rec["reason"] = f"{spec['require']} is not True — the node cannot certify"
            found[node] = rec
            continue
        if spec.get("legs"):
            legs = blob.get(spec["legs"])
            if not isinstance(legs, list) or not legs:
                rec["reason"] = f"no non-empty {spec['legs']!r} list at {source}"
            else:
                ps = [_finite(leg.get(pkey)) if isinstance(leg, dict) else None for leg in legs]
                rec["n_legs"] = len(ps)
                if any(p is None for p in ps):
                    rec["reason"] = "at least one leg has no usable p-value (an IUT cannot certify)"
                else:
                    rec["pvalue"] = max(ps)
        else:
            rec["pvalue"] = _finite(blob.get(pkey))
            if rec["pvalue"] is None:
                rec["reason"] = f"{pkey!r} absent or non-finite at {source}"
        found[node] = rec
    return found


def tier_verdict(out: dict[str, Any], root: Any = None) -> dict[str, Any]:
    """Run the ratified graphical rule over an ``analyze_campaign`` result dict.

    The graph (initial weights, edges, alpha) is READ from the registered config — never hardcoded, so
    the executed rule cannot drift from the frozen one. Returns the propagation result plus the
    per-node extraction record, so a shape mismatch is visible rather than silently decisive.
    """
    weights, edges, alpha = registered_alpha_graph(root)
    nodes = tier_node_pvalues(out)
    pvalues: dict[str, float | None] = {n: nodes.get(n, {}).get("pvalue") for n in weights}
    result = graphical_alpha_propagation(pvalues, weights, edges, alpha)
    result["nodes"] = nodes
    result["method"] = "graphical_bretz_maurer_brannath_posch_2009"
    result["registered_rule"] = "bonferroni_weighted_graph"
    result["supersedes"] = "R31 separate-estimands (ratified 2026-07-26, R108)"
    return result
