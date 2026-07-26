"""Assembly of the six confirmatory node p-values + the ratified graphical verdict.

Companion to tests/test_graphical_alpha.py: that one tests the RULE, this one tests the BRIDGE from
analyze_campaign's result dict to it. Both exist because the 2026-07-26 deep review found the ratified
primary rule (R108) had no implementation and no call path (write-time registry row 36).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.inference.validity_tier import tier_node_pvalues, tier_verdict  # noqa: E402


def _legs(*ps: float) -> list[dict]:
    return [{"pvalue_one_sided": p} for p in ps]


def _out(**kw) -> dict:
    base = {
        "h2": {"tail_legs": _legs(0.9, 0.9, 0.9), "legs": _legs(0.9, 0.9, 0.9)},
        "h3": {"pvalue_one_sided": 0.9},
        "h4": {"legs": _legs(0.9, 0.9, 0.9, 0.9)},
        "structure_control": {"legs": _legs(0.9)},
        "h1": {"iut": {"legs": _legs(*([0.9] * 11))}},
    }
    base.update(kw)
    return base


def test_iut_node_p_is_the_MAX_over_legs() -> None:
    """Berger 1982: an intersection-union test's p-value is the MAX of its leg p-values."""
    n = tier_node_pvalues(_out(h4={"legs": _legs(0.001, 0.02, 0.30, 0.004)}))
    assert n["N4_h4"]["pvalue"] == 0.30
    assert n["N4_h4"]["n_legs"] == 4


def test_all_six_nodes_are_located_in_a_well_formed_result() -> None:
    n = tier_node_pvalues(_out())
    assert set(n) == {"N1_h2_tail", "N2_h2_ra", "N3_h3", "N4_h4", "N5_structure", "N6_h1"}
    assert all(v["pvalue"] is not None for v in n.values()), {k: v.get("reason") for k, v in n.items()}
    assert n["N6_h1"]["n_legs"] == 11          # the full canon, not a subset


def test_missing_node_is_UNTESTABLE_not_assumed() -> None:
    """A shape mismatch must surface, never silently become a pass or a fail."""
    out = _out()
    del out["h3"]
    n = tier_node_pvalues(out)
    assert n["N3_h3"]["pvalue"] is None and "reason" in n["N3_h3"]
    assert n["N3_h3"]["searched"]              # the keys tried are recorded for diagnosis
    v = tier_verdict(out)
    assert "N3_h3" in v["untestable"] and "N3_h3" not in v["rejected"]


def test_iut_with_one_untestable_leg_cannot_certify() -> None:
    """Mirrors beat_human_baseline's all_baselines_present gate: a missing leg blocks dominance."""
    legs = _legs(0.001, 0.001)
    legs.append({"pvalue_one_sided": None})
    n = tier_node_pvalues(_out(h4={"legs": legs}))
    assert n["N4_h4"]["pvalue"] is None
    assert "cannot certify" in n["N4_h4"]["reason"]


def test_verdict_runs_on_the_registered_graph_and_rejects_nothing_under_the_null() -> None:
    v = tier_verdict(_out())
    assert v["registered_rule"] == "bonferroni_weighted_graph"
    assert v["rejected"] == []
    assert set(v["nodes"]) == {"N1_h2_tail", "N2_h2_ra", "N3_h3", "N4_h4", "N5_structure", "N6_h1"}


def test_headline_rejection_propagates_alpha_downstream() -> None:
    """A confirmed tail headline must RAISE a downstream node's local level — the cascade the tier buys."""
    out = _out(h2={"tail_legs": _legs(0.001, 0.001, 0.001), "legs": _legs(0.9, 0.9, 0.9)})
    v = tier_verdict(out)
    assert "N1_h2_tail" in v["rejected"]
    assert any(v["local_alpha"][n] > 0.0 for n in ("N4_h4", "N5_structure")), v["local_alpha"]
