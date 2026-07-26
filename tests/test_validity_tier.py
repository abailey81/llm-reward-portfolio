"""R105: bind the graphical-multiplicity VALIDITY TIER (A3) so its structure is VERIFIED, not asserted.

Checks the registered `inference.validity_tier` is a well-formed Bretz-Maurer-Brannath-Posch (2009)
alpha-graph: all alpha starts on the two H2 co-primaries (the tier costs the headline zero power); every
node's out-edges sum to <= 1; H1 (the snooped beat-human comparison) is EXCLUDED; every tier node is
reachable from the headline; the block is ratification-pending (NOT a silent override of the R31 stance);
and the 2026-07-26 content-over-format upgrade (N5 = placebo_shuffled) is present.
"""
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _tier() -> dict:
    prereg = yaml.safe_load((ROOT / "config" / "preregistration.yaml").read_text(encoding="utf-8"))
    return prereg["inference"]["validity_tier"]


def test_tier_is_ratification_pending_not_a_silent_override():
    t = _tier()
    assert t["status"] == "registered_pending_supervisor_ratification"
    assert t["supersedes_on_ratification"] == "cross_hypothesis_multiplicity"   # R31 stays the default until ratified


def test_all_initial_alpha_starts_on_the_headline():
    # activate-on-upstream-success => the H3/H4/N5 tier costs the H2 headline ZERO power
    w = _tier()["initial_weights"]
    assert w["N1_h2_tail"] == 0.5 and w["N2_h2_ra"] == 0.5
    assert all(v == 0.0 for n, v in w.items() if n not in ("N1_h2_tail", "N2_h2_ra"))
    assert abs(sum(w.values()) - 1.0) < 1e-9


def test_every_node_out_edges_sum_to_at_most_one():
    for src, outs in _tier()["edges"].items():
        assert sum(outs.values()) <= 1.0 + 1e-9, (src, outs)


def test_snooped_h1_excluded_but_desnooped_h1_is_node_n6():
    # 2026-07-26 (Tamer, nothing-frozen): H1 PROMOTED to a confirmatory node via the de-snoop + full canon.
    t = _tier()
    assert "H1_snooped_test_max" in t["excludes"]   # the max-over-the-sealed-TEST snoop has no valid p-value
    assert "N6_h1" in t["nodes"]                     # the DE-SNOOPED (val-selected) H1 IS a confirmatory node
    n6 = t["nodes"]["N6_h1"]
    assert n6["selection"] == "val" and n6["scoring"] == "sealed_test"   # de-snoop: champion on val, scored on test
    assert n6["champion"] == "max_over_h1_baselines_canon"               # the FULL canon champion (not a 4-subset)


def test_every_tier_node_is_reachable_from_the_headline():
    t = _tier()
    edges = t["edges"]
    reached = {"N1_h2_tail", "N2_h2_ra"}   # the headline nodes hold the initial alpha
    changed = True
    while changed:
        changed = False
        for src in list(reached):
            for dst in edges.get(src, {}):
                if dst not in reached:
                    reached.add(dst)
                    changed = True
    assert set(t["nodes"]) <= reached, f"unreachable nodes: {set(t['nodes']) - reached}"


def test_n5_is_the_content_over_format_upgrade():
    n5 = _tier()["nodes"]["N5_structure"]
    assert n5["arm_b"] == "placebo_shuffled"
    assert n5["direction"] == "one_sided_content_over_format"
