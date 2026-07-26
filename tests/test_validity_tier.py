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


def test_tier_ratification_is_RECORDED_not_silent():
    """R108 (2026-07-26): the tier was signed off by Tamer AND Okhrati — exactly the precondition
    the `status` field named. The guard is NOT removed, it is RE-POINTED: a ratified tier must
    still carry WHO ratified it and WHEN, so activation can never be a silent edit. It still
    declares what it supersedes (R31), and it is still not frozen."""
    t = _tier()
    assert t["status"] == "ratified"
    assert set(t["ratified_by"]) == {"tamer", "okhrati"}, "activation requires a NAMED sign-off"
    assert t["ratified_utc"], "a ratification without a date is not auditable"
    assert t["supersedes_on_ratification"] == "cross_hypothesis_multiplicity"   # R31 now superseded
    assert t["ratification_pending"] == [], "nothing may remain pending once status is ratified"
    assert len(t["ratification_completed"]) >= 7, "the completed set must record what was signed"


def test_all_initial_alpha_starts_on_the_headline():
    # activate-on-upstream-success => the H3/H4/N5 tier costs the H2 headline ZERO power
    w = _tier()["initial_weights"]
    assert w["N1_h2_tail"] == 0.5 and w["N2_h2_ra"] == 0.5
    assert all(v == 0.0 for n, v in w.items() if n not in ("N1_h2_tail", "N2_h2_ra"))
    assert abs(sum(w.values()) - 1.0) < 1e-9


def test_every_node_out_edges_sum_to_at_most_one():
    for src, outs in _tier()["edges"].items():
        assert sum(outs.values()) <= 1.0 + 1e-9, (src, outs)


def test_snooped_h1_excluded_but_h1_is_confirmatory_node_n6_via_iut():
    # 2026-07-26 (Tamer, nothing-frozen + "make it smart + sound"): H1 PROMOTED to a confirmatory node via a
    # SNOOP-FREE intersection-union test over the full canon (beat EVERY member one-sided at alpha == beat the
    # best human, since best = max), SUPERSEDING the val-select framing (dead code: the campaign archives
    # val_fitness=NaN, so beat_human_baseline already fell back to the test-snoop) — the IUT selects no
    # comparator, so there is nothing to snoop and no fragile baseline val-roll is needed.
    t = _tier()
    assert "H1_snooped_test_max" in t["excludes"]   # the max-over-the-sealed-TEST snoop has no valid p-value
    assert "N6_h1" in t["nodes"]                     # H1 IS a confirmatory node (snoop-free IUT)
    n6 = t["nodes"]["N6_h1"]
    assert n6["test"] == "llm_beats_best_human_reward"
    assert n6["method"] == "intersection_union_over_canon"       # berger1982iut: beat-all <=> beat-best, no selection
    assert n6["comparator"] == "full_11name_hand_reward_canon"   # the FULL canon (not a 4-subset)
    assert "selection" not in n6                                 # NO comparator selected -> nothing to snoop (dissolved)
    assert n6["endpoint"] == "sharpe_annualized", (
        "N6 must register the endpoint the code actually computes. It previously registered "
        "deflated_sharpe while scripts/analyze_campaign.py built the IUT legs from annualised "
        "Sharpe; a DSR endpoint would score the winner against an E[max SR] benchmark of ~0.83 "
        "annualised (n_trials=30) and each hand reward against 0.0 (n_trials=1), i.e. different "
        "nulls per arm, and the winner would lose every leg even at an equal true Sharpe "
        "(deep review 2026-07-26, loop 5)."
    )


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
