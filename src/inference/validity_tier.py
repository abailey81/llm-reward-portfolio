"""Assemble the six confirmatory node p-values and run the RATIFIED graphical decision rule.

This is the bridge between what ``scripts/analyze_campaign.py`` already computes and
``multiple_testing.graphical_alpha_propagation`` — the rule ratified on 2026-07-26 (R108:
``primary_rule: bonferroni_weighted_graph``, superseding R31).

WHY IT IS A SEPARATE MODULE. The rule itself must be executable and testable WITHOUT campaign data, and
the graph must be READ from the registered config rather than copied (``forking_path_guard`` declares it
FROZEN). Keeping the assembly here means ``analyze_campaign`` needs exactly one call, and this logic can
be unit-tested against synthetic result dicts today — before any results exist, which is precisely when
a decision rule is allowed to be written.

FAIL-SAFE BY CONSTRUCTION. A node whose p-value cannot be located is reported ``untestable`` and can
never reject; it is NEVER silently treated as a passing (or failing) test. Every key searched is
recorded in ``nodes[...]["searched"]`` so a shape mismatch is visible in the artifact instead of
producing a confidently wrong verdict — the worst possible failure for a confirmatory analysis.

NODE MAP (each node supplies exactly ONE valid level-alpha p-value; Berger 1982 makes an IUT's max-p
valid, which is why the H2 co-primaries need no further within-family correction):

    N1_h2_tail    max one-sided p over the CVaR-5% legs        out["h2"]["tail_legs"]
    N2_h2_ra      max one-sided p over the Sharpe legs         out["h2"]["legs"]
    N3_h3         iterative > single-shot                      out["h3"]
    N4_h4         max over the 4 search comparators (IUT)      out["h4"]
    N5_structure  distributional > placebo_shuffled            out["structure_control"]
    N6_h1         max over the 11-name canon (IUT)             out["h1"]["iut"]
"""
from __future__ import annotations

import math
from typing import Any

from src.inference.multiple_testing import graphical_alpha_propagation, registered_alpha_graph

__all__ = ["NODE_SOURCES", "tier_node_pvalues", "tier_verdict"]

#: Per node: (path into ``out``, leg-list key or None, candidate p-value keys tried in order).
#: A leg-list key means the node is an INTERSECTION-UNION test and its p is the MAX over the legs.
NODE_SOURCES: dict[str, tuple[tuple[str, ...], str | None, tuple[str, ...]]] = {
    "N1_h2_tail":   (("h2",), "tail_legs", ("pvalue_one_sided", "pvalue_one_sided_greater", "pvalue")),
    "N2_h2_ra":     (("h2",), "legs",      ("pvalue_one_sided", "pvalue_one_sided_greater", "pvalue")),
    "N3_h3":        (("h3",), None,        ("pvalue_one_sided", "pvalue_one_sided_greater", "pvalue")),
    "N4_h4":        (("h4",), "legs",      ("pvalue_one_sided", "pvalue_one_sided_greater", "pvalue")),
    "N5_structure": (("structure_control",), "legs",
                     ("pvalue_one_sided", "pvalue_one_sided_greater", "pvalue")),
    "N6_h1":        (("h1", "iut"), "legs", ("pvalue_one_sided", "pvalue_one_sided_greater", "pvalue")),
}


def _dig(out: dict[str, Any], path: tuple[str, ...]) -> Any:
    node: Any = out
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node


def _first_finite(d: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for k in keys:
        v = d.get(k)
        if v is None:
            continue
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        if math.isfinite(f):
            return f
    return None


def tier_node_pvalues(out: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Extract one p-value per confirmatory node from an ``analyze_campaign`` result dict.

    Returns ``{node: {"pvalue": float|None, "source": str, "n_legs": int|None, "searched": [...]}}``.
    ``pvalue is None`` means NOT TESTABLE — reported, never rejectable, never assumed.
    """
    found: dict[str, dict[str, Any]] = {}
    for node, (path, legs_key, pkeys) in NODE_SOURCES.items():
        blob = _dig(out, path)
        rec: dict[str, Any] = {
            "pvalue": None, "source": "/".join(path), "n_legs": None, "searched": list(pkeys),
        }
        if not isinstance(blob, dict):
            rec["reason"] = f"no dict at out[{']['.join(repr(p) for p in path)}]"
            found[node] = rec
            continue
        if legs_key is None:
            rec["pvalue"] = _first_finite(blob, pkeys)
            if rec["pvalue"] is None:
                rec["reason"] = f"none of {pkeys} present/finite"
        else:
            legs = blob.get(legs_key)
            if not isinstance(legs, list) or not legs:
                rec["reason"] = f"no non-empty {legs_key!r} list"
            else:
                ps = [_first_finite(leg, pkeys) for leg in legs if isinstance(leg, dict)]
                rec["n_legs"] = len(ps)
                if any(p is None for p in ps):
                    # An IUT with an untestable leg CANNOT certify dominance — mirrors
                    # beat_human_baseline's `all_baselines_present` gate.
                    rec["reason"] = "at least one leg has no usable p-value (IUT cannot certify)"
                else:
                    rec["pvalue"] = max(ps)          # the IUT p-value is the MAX over legs
                    rec["rule"] = "max over legs (intersection-union, Berger 1982)"
        found[node] = rec
    return found


def tier_verdict(out: dict[str, Any], root: Any = None) -> dict[str, Any]:
    """Run the ratified graphical rule over an ``analyze_campaign`` result dict.

    The graph (initial weights, edges, alpha) is READ from the registered config — never hardcoded.
    Returns the propagation result plus the per-node extraction record, so a shape mismatch is visible
    rather than silently producing a verdict.
    """
    weights, edges, alpha = registered_alpha_graph(root)
    nodes = tier_node_pvalues(out)
    pvalues: dict[str, float | None] = {n: nodes.get(n, {}).get("pvalue") for n in weights}
    result = graphical_alpha_propagation(pvalues, weights, edges, alpha)
    result["nodes"] = nodes
    result["method"] = "graphical_bretz_maurer_brannath_posch_2009"
    result["registered_rule"] = "bonferroni_weighted_graph"
    return result
