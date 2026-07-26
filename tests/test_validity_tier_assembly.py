"""Assembly of the six confirmatory node p-values + the ratified graphical verdict.

Companion to tests/test_graphical_alpha.py: that tests the RULE, this tests the BRIDGE from
analyze_campaign's result dict to it (write-time registry row 36).

The fixtures below mirror the REAL shapes, each verified against the producing code — h2's
legs/tail_legs, h3's nested "difference", h4's "tests", h2_structure's "cvar" sub-result, and
h1_beat_human's precomputed "iut_pvalue" with its all_baselines_present gate. That verification
mattered: 4 of 6 first-guess paths (taken from docstrings) were WRONG.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.inference.validity_tier import tier_node_pvalues, tier_verdict  # noqa: E402

NODES = {"N1_h2_tail", "N2_h2_ra", "N3_h3", "N4_h4", "N5_structure", "N6_h1"}


def _legs(*ps: float) -> list[dict]:
    return [{"pvalue_one_sided": p} for p in ps]


def _out(**kw) -> dict:
    """A well-formed result dict in the REAL shapes, null everywhere (p = 0.9)."""
    base = {
        "h2": {"tail_legs": _legs(0.9, 0.9, 0.9), "legs": _legs(0.9, 0.9, 0.9)},
        "h3": {"difference": {"pvalue_one_sided": 0.9}},
        "h4": {"tests": _legs(0.9, 0.9, 0.9, 0.9)},
        "h2_structure": {"cvar": {"pvalue_one_sided": 0.9}},
        "h1_beat_human": {"iut": {"iut_pvalue": 0.9, "all_baselines_present": True}},
    }
    base.update(kw)
    return base


def test_all_six_nodes_resolve_in_the_real_shapes() -> None:
    n = tier_node_pvalues(_out())
    assert set(n) == NODES
    unresolved = {k: v["reason"] for k, v in n.items() if v["pvalue"] is None}
    assert not unresolved, unresolved
    assert n["N4_h4"]["n_legs"] == 4          # the 9-arm migration's 4-comparator portfolio


def test_iut_node_p_is_the_MAX_over_legs() -> None:
    """Berger 1982: an intersection-union test's p-value is the MAX of its leg p-values."""
    n = tier_node_pvalues(_out(h4={"tests": _legs(0.001, 0.02, 0.30, 0.004)}))
    assert n["N4_h4"]["pvalue"] == 0.30


def test_n6_uses_the_precomputed_iut_p_and_honours_its_gate() -> None:
    """N6 reuses beat_human_baseline's own iut_pvalue, and CANNOT certify with a member missing."""
    ok = tier_node_pvalues(_out())["N6_h1"]
    assert ok["pvalue"] == 0.9

    gated = tier_node_pvalues(_out(
        h1_beat_human={"iut": {"iut_pvalue": 0.001, "all_baselines_present": False}}
    ))["N6_h1"]
    assert gated["pvalue"] is None
    assert "all_baselines_present" in gated["reason"]


def test_missing_or_reshaped_node_is_UNTESTABLE_not_assumed() -> None:
    """A shape mismatch must surface, never silently become a pass or a fail."""
    out = _out()
    del out["h3"]
    n = tier_node_pvalues(out)
    assert n["N3_h3"]["pvalue"] is None and n["N3_h3"]["reason"]
    assert 'out["h3"]["difference"]' in n["N3_h3"]["source"]   # the path searched is reported
    v = tier_verdict(out)
    assert "N3_h3" in v["untestable"] and "N3_h3" not in v["rejected"]


def test_iut_with_one_untestable_leg_cannot_certify() -> None:
    legs = _legs(0.001, 0.001)
    legs.append({"pvalue_one_sided": None})
    n = tier_node_pvalues(_out(h4={"tests": legs}))
    assert n["N4_h4"]["pvalue"] is None and "cannot certify" in n["N4_h4"]["reason"]


def test_verdict_rejects_nothing_under_the_global_null() -> None:
    v = tier_verdict(_out())
    assert v["registered_rule"] == "bonferroni_weighted_graph"
    assert v["rejected"] == [] and set(v["nodes"]) == NODES


def test_headline_rejection_propagates_alpha_downstream() -> None:
    """A confirmed tail headline RAISES a downstream node's local level — the cascade the tier buys."""
    v = tier_verdict(_out(h2={"tail_legs": _legs(0.001, 0.001, 0.001), "legs": _legs(0.9, 0.9, 0.9)}))
    assert "N1_h2_tail" in v["rejected"]
    assert any(v["local_alpha"][n] > 0.0 for n in ("N4_h4", "N5_structure")), v["local_alpha"]


def test_predicted_null_branch_activates_the_tier_via_the_TOST() -> None:
    """The REGISTERED prediction is the NULL branch: N1 ties, and N2 rejects by proving equivalence.
    That path alone must open the tier — which is why bergerhsu1996equivalence is load-bearing."""
    v = tier_verdict(_out(h2={"tail_legs": _legs(0.9, 0.9, 0.9), "legs": _legs(0.001, 0.001, 0.001)}))
    assert "N2_h2_ra" in v["rejected"]
    assert any(v["local_alpha"][n] > 0.0 for n in ("N3_h3", "N6_h1")), v["local_alpha"]


def test_analyze_campaign_WIRES_the_ratified_rule() -> None:
    """The pipeline must actually CALL the ratified rule — this fails if the call site is removed.

    Row 36 existed because the rule was ratified (R108) with no implementation AND no call path, so the
    registered primary inference could not be produced. A unit-tested module that nothing invokes is the
    exact failure R16 already fixed once for `h2_conjunction`; this lock exists so it cannot recur.
    """
    src = (Path(__file__).resolve().parents[1] / "scripts" / "analyze_campaign.py").read_text(
        encoding="utf-8"
    )
    assert "from src.inference.validity_tier import tier_verdict" in src
    assert 'out["validity_tier"] = tier_verdict(out)' in src
    # It must run AFTER every node producer, or nodes would be spuriously untestable.
    for producer in ('out["h2_structure"] =', 'out["h1_beat_human"] ='):
        assert src.index(producer) < src.index('out["validity_tier"] = tier_verdict(out)'), (
            f"the tier verdict must be computed after {producer}"
        )
