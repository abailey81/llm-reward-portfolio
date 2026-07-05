"""FAST tests for the pre-registration freeze GATE (Rank 9, scripts/freeze.py).

These are import-light (no torch) and never run the REAL freeze. They pin the load-bearing
guarantees of the gate:

  - ``--check`` PASSES on the CURRENT, consistent prereg: the hash computes, the
    prose<->yaml assertion holds on all six frozen fields, and the Phase-0 precondition is met;
  - the prose<->yaml assertion RAISES on a deliberately-mismatched fixture (yaml sesoi 0.05 vs
    a prose 0.20; an m mismatch; a seed-count mismatch);
  - the Phase-0 precondition RAISES when the marker is absent/blank;
  - the canonical hash is DETERMINISTIC (same inputs -> same digest) and ORDER-SENSITIVE
    (swapping prose<->yaml changes it) and LINE-ENDING invariant (CRLF == LF);
  - ``--check`` does NOT mutate any file (frozen stays false, freeze_hash stays null).

The mismatch / precondition / write-path cases operate on a COPY of the two real artifacts in
``tmp_path`` (via ``freeze.<fn>(root=...)``), so the live PREREGISTRATION.md /
config/preregistration.yaml are never edited by the suite.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import freeze  # noqa: E402

REPO = freeze.repo_root()


# --------------------------------------------------------------------------- #
# Helpers / fixtures                                                            #
# --------------------------------------------------------------------------- #
def _mini_repo(tmp_path: Path) -> Path:
    """A throwaway repo root holding a COPY of the two real freeze artifacts.

    ``config/`` + ``pyproject.toml`` + ``docs/`` are created so ``repo_root``-style code and
    the write path resolve, but only the two prereg files carry real content.
    """
    (tmp_path / "config").mkdir()
    (tmp_path / "docs").mkdir()
    (tmp_path / "pyproject.toml").write_text("[tool]\n", encoding="utf-8")
    shutil.copyfile(REPO / freeze.PREREG_MD, tmp_path / freeze.PREREG_MD)
    shutil.copyfile(REPO / freeze.PREREG_YAML, tmp_path / freeze.PREREG_YAML)
    shutil.copyfile(REPO / freeze.DECISION_LOG, tmp_path / freeze.DECISION_LOG)
    # config/data.yaml carries the gold.suffix the data_panel cross-check binds (batch-6 M2, 2026-07-03:
    # the check now reads root/config/data.yaml, so the mini-repo must supply it — copied from the real
    # one so it mirrors the prereg's frozen headline, which lets the drift test below edit it hermetically).
    shutil.copyfile(REPO / "config" / "data.yaml", tmp_path / "config" / "data.yaml")
    return tmp_path


@pytest.fixture
def mini(tmp_path: Path) -> Path:
    return _mini_repo(tmp_path)


def _edit(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"fixture precondition: {old!r} not found in {path.name}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# --------------------------------------------------------------------------- #
# 1. --check PASSES on the current, consistent prereg                           #
# --------------------------------------------------------------------------- #
def test_check_passes_on_live_prereg():
    """The real prereg verifies: hash computes, gate holds, Phase-0 met, exit 0."""
    rc = freeze.main(["--check"])
    assert rc == 0


def test_verify_live_returns_full_status():
    status = freeze.verify(REPO)
    assert len(status.hash) == 64
    int(status.hash, 16)  # hex
    assert status.phase0_marker.strip()
    assert not status.already_frozen
    assert status.recorded_hash is None  # freeze_hash: null pre-freeze
    # FIFTEEN frozen checks on the LIVE repo: the 6 original + the 3 2026-06-24 amendments
    # (lambda/tf32/reflect) + the §3 arm-roster prose guard + the V1 cross-file executed-arms guard
    # (campaign.yaml/arms.yaml rosters == frozen prereg arms) + the §18 h1_baselines cross-file guard
    # (audit H-L2, 2026-07-02) + the data_panel.headline == config/data.yaml gold.suffix cross-check
    # (pre-freeze audit H1, 2026-07-02: R73's univ3->univ5 flip had left the yaml mirror stale) + the
    # train_steps_per_candidate executed<->frozen B* guard (batch-6 M1, 2026-07-03: B* was the one
    # headline number with no executed<->frozen check — budget_mirror pairs campaign<->algos only) + the
    # tail_diagnostic_set §4 prose<->yaml guard (batch-6 M5, 2026-07-03: the frozen tail set had no
    # pre-freeze prose<->yaml contradiction guard, unlike sesoi/m/grid) + the seeds + matched_budget
    # executed<->frozen guards (DEEP_SWEEP E-F1, 2026-07-04: campaign.yaml seeds/candidates_per_arm bound to
    # the frozen prereg — the seed count is the power/equivalence knob, previously unguarded exactly like B* was).
    # + the 2026-07-05 hardening trio (search-splits cross-assert, R38 prompt tail-neutrality, and the
    # bound-file existence assert on the real root) -> 20 checks. The canonical hash is UNCHANGED by
    # these (guards are code, never hashed content).
    assert len(status.checks) == 20
    assert any("executed arms:" in c for c in status.checks)
    assert any("h1_baselines" in c for c in status.checks)
    assert any("search splits:" in c for c in status.checks)
    assert any("tail-neutrality" in c for c in status.checks)
    assert any("bound-file existence" in c for c in status.checks)
    assert any("data_panel.headline" in c for c in status.checks)
    assert any("train_steps_per_candidate" in c for c in status.checks)
    assert any("tail_diagnostic_set" in c for c in status.checks)
    assert any("frozen prereg seeds" in c for c in status.checks)
    assert any("matched_budget:" in c for c in status.checks)


def test_all_frozen_fields_are_checked():
    checks = " ".join(freeze.verify(REPO).checks)
    for token in ("seeds", "arms", "testing_family.m", "difference_tests", "sesoi",
                  "equivalence_margin", "cost_sweep.grid_bps",
                  "fitness.lambda_cvar", "agent_numerics.tf32", "search.reflect_protocol_default"):
        assert token in checks


# --------------------------------------------------------------------------- #
# 1c. V1 cross-file guard: executed configs (campaign.yaml/arms.yaml) roster   #
#     must equal the FROZEN prereg roster (the placebo_shuffled 6-vs-7 drift).  #
# --------------------------------------------------------------------------- #
_FROZEN_ARMS = [
    "distributional", "scalar", "placebo", "scalar_cvar5",
    "placebo_shuffled", "random_search", "bayes_opt",
]


def _write_campaign_yaml(root: Path, arms: list[str]) -> None:
    # Mini campaign.yaml carries the frozen §18 h1_baselines family too (the H1 guard fail-louds on a
    # campaign.yaml that OMITS the family once the prereg yaml declares it — audit H-L2, 2026-07-02).
    (root / "config" / "campaign.yaml").write_text(
        "arms: [" + ", ".join(arms) + "]\ncandidates_per_arm: 30\n"
        "train_steps_per_candidate: 200000\n"
        "h1_baselines: [raw_return, return_minus_variance, return_minus_cvar, differential_sharpe]\n"
        "seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]\n",
        encoding="utf-8",
    )


def _write_arms_yaml(root: Path, arms: list[str]) -> None:
    body = "arms:\n" + "".join(f"  {a}: {{feedback: x}}\n" for a in arms)
    (root / "config" / "arms.yaml").write_text(body, encoding="utf-8")


def test_executed_arms_guard_present_on_live():
    """The live repo carries campaign.yaml + arms.yaml, so the executed-arms guard runs and AGREES."""
    line = freeze.assert_executed_arms_match(freeze.load_yaml(REPO), REPO)
    assert line is not None and "campaign.yaml" in line and "arms.yaml" in line
    # The frozen roster is the seven arms incl. the R32 structure-vs-content control.
    for arm in _FROZEN_ARMS:
        assert arm in line


def test_executed_arms_guard_skips_when_configs_absent(mini: Path):
    """A minimal prereg-only root (no campaign.yaml/arms.yaml) verifies; the guard returns None."""
    assert freeze.assert_executed_arms_match(freeze.load_yaml(mini), mini) is None
    # verify() still passes end-to-end on the minimal root (the guard is a no-op there).
    assert freeze.verify(mini).hash


def test_h1_baselines_guard_present_on_live():
    """The live repo carries the frozen §18 family in BOTH prereg yaml and campaign.yaml; the guard AGREES."""
    line = freeze.assert_h1_baselines_match(freeze.load_yaml(REPO), REPO)
    assert line is not None and "h1_baselines" in line
    for name in ("raw_return", "return_minus_variance", "return_minus_cvar", "differential_sharpe"):
        assert name in line


def test_h1_baselines_guard_skips_when_campaign_absent(mini: Path):
    """The minimal prereg-only root has no campaign.yaml -> the H1 guard is a no-op (returns None)."""
    assert freeze.assert_h1_baselines_match(freeze.load_yaml(mini), mini) is None


def test_h1_baselines_drift_raises(mini: Path):
    """A campaign.yaml whose h1_baselines drifts from the frozen §18 family must fail loud."""
    (mini / "config" / "campaign.yaml").write_text(
        "arms: [a]\nh1_baselines: [raw_return, differential_sharpe]\n", encoding="utf-8"
    )
    import pytest

    with pytest.raises(freeze.FreezeConsistencyError, match="h1_baselines"):
        freeze.assert_h1_baselines_match(freeze.load_yaml(mini), mini)


def test_data_panel_drift_raises(mini: Path):
    """config/data.yaml gold.suffix diverging from the frozen prereg headline -> raises (batch-6 M2).

    Hermetic now that the check reads root/config/data.yaml (was a CWD-relative read that no mini-repo
    could exercise): rewrite the mini's gold.suffix away from the prereg's frozen headline and assert
    the data_panel cross-check fails loud rather than freezing a record<->execution contradiction.
    """
    # Minimal known-drifted data.yaml (avoids _edit's first-occurrence ambiguity — the real file names
    # the suffix in several places): gold.suffix is unambiguously the drifted value here.
    (mini / "config" / "data.yaml").write_text("gold:\n  suffix: univ5_DRIFTED\n", encoding="utf-8")
    with pytest.raises(freeze.FreezeConsistencyError, match="data_panel.headline mismatch"):
        freeze.verify(mini)


def test_train_steps_drift_raises(mini: Path):
    """campaign.yaml + algos.yaml B* diverging from the frozen prereg B* -> raises (batch-6 M1).

    The one headline number that previously had no executed<->frozen guard. A coordinated edit of BOTH
    executed mirrors (which passes preflight's campaign<->algos budget-mirror) must still fail the freeze
    because it leaves the hashed prereg behind.
    """
    (mini / "config" / "campaign.yaml").write_text(
        "arms: [a]\ntrain_steps_per_candidate: 250000\n", encoding="utf-8"
    )
    (mini / "config" / "algos.yaml").write_text("train_steps_per_candidate: 250000\n", encoding="utf-8")
    with pytest.raises(freeze.FreezeConsistencyError, match="train_steps_per_candidate"):
        freeze.assert_train_steps_match(freeze.load_yaml(mini), mini)


def test_seeds_drift_raises(mini: Path):
    """campaign.yaml seeds diverging from the frozen prereg seed set -> raises (DEEP_SWEEP E-F1).

    The seed count is the knob the power/equivalence headline hinges on; a post-freeze seed edit
    (30 -> a cherry-picked block) must fail the freeze because it leaves the hashed prereg behind.
    """
    (mini / "config" / "campaign.yaml").write_text(
        "seeds: [0, 1, 2, 3, 4]\ncandidates_per_arm: 30\n", encoding="utf-8"
    )
    with pytest.raises(freeze.FreezeConsistencyError, match="frozen prereg seeds"):
        freeze.assert_seeds_match(freeze.load_yaml(mini), mini)


def test_matched_budget_drift_raises(mini: Path):
    """campaign.yaml candidates_per_arm diverging from the frozen prereg matched_budget -> raises (E-F1)."""
    (mini / "config" / "campaign.yaml").write_text(
        "candidates_per_arm: 60\n", encoding="utf-8"
    )
    with pytest.raises(freeze.FreezeConsistencyError, match="matched_budget"):
        freeze.assert_matched_budget_match(freeze.load_yaml(mini), mini)


def test_campaign_arms_drop_raises(mini: Path):
    """campaign.yaml missing the R32 placebo_shuffled control (6 vs the frozen 7) -> raises (V1)."""
    _write_campaign_yaml(mini, [a for a in _FROZEN_ARMS if a != "placebo_shuffled"])
    with pytest.raises(freeze.FreezeConsistencyError, match="placebo_shuffled"):
        freeze.verify(mini)


def test_campaign_arms_extra_raises(mini: Path):
    """campaign.yaml carrying an UNFROZEN extra arm -> raises (the roster must match exactly)."""
    _write_campaign_yaml(mini, [*_FROZEN_ARMS, "sneaky_eighth_arm"])
    with pytest.raises(freeze.FreezeConsistencyError, match="sneaky_eighth_arm|executed arm roster"):
        freeze.verify(mini)


def test_arms_yaml_rename_raises(mini: Path):
    """arms.yaml (roster = mapping KEYS) with one arm renamed -> raises (cross-file disagreement)."""
    _write_arms_yaml(mini, [a if a != "scalar_cvar5" else "scalar_cvar_FIVE" for a in _FROZEN_ARMS])
    with pytest.raises(freeze.FreezeConsistencyError, match="config/arms.yaml"):
        freeze.verify(mini)


def test_matching_executed_configs_pass(mini: Path):
    """campaign.yaml AND arms.yaml declaring exactly the frozen roster -> verify passes, guard reported."""
    _write_campaign_yaml(mini, _FROZEN_ARMS)
    _write_arms_yaml(mini, _FROZEN_ARMS)
    status = freeze.verify(mini)
    assert any("executed arms:" in c for c in status.checks)


def test_config_with_no_arms_field_raises(mini: Path):
    """An executed roster config that declares no usable 'arms' roster -> raises (not silently skipped)."""
    (mini / "config" / "campaign.yaml").write_text("candidates_per_arm: 30\n", encoding="utf-8")
    with pytest.raises(freeze.FreezeConsistencyError, match="no usable 'arms' roster"):
        freeze.verify(mini)


# --------------------------------------------------------------------------- #
# 2. The gate RAISES on deliberate prose<->yaml mismatches                      #
# --------------------------------------------------------------------------- #
def test_sesoi_mismatch_raises(mini: Path):
    """yaml sesoi 0.05 but a prose SESOI of 0.20 -> FreezeConsistencyError."""
    _edit(mini / freeze.PREREG_MD, "SESOI = **0.05 validation-DSR units**",
          "SESOI = **0.20 validation-DSR units**")
    with pytest.raises(freeze.FreezeConsistencyError, match="SESOI"):
        freeze.verify(mini)


def test_equivalence_margin_mismatch_raises(mini: Path):
    """yaml equivalence_margin 0.05 but a prose ±0.20 DSR -> raises."""
    _edit(mini / freeze.PREREG_MD, "**±0.05 DSR**", "**±0.20 DSR**")
    with pytest.raises(freeze.FreezeConsistencyError, match="equivalence_margin"):
        freeze.verify(mini)


def test_seed_count_mismatch_raises(mini: Path):
    """Drop a seed from the yaml list so len != the prose headline count -> raises."""
    _edit(mini / freeze.PREREG_YAML,
          "seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, "
          "21, 22, 23, 24, 25, 26, 27, 28, 29]",
          "seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, "
          "21, 22, 23, 24, 25, 26, 27, 28]")
    with pytest.raises(freeze.FreezeConsistencyError, match="seed count"):
        freeze.verify(mini)


def test_testing_family_m_mismatch_raises(mini: Path):
    """A prose 'm = 9' (an UNDECLARED family size) -> raises (the multiple-testing family must agree)."""
    _edit(mini / freeze.PREREG_MD, "**m = 6**", "**m = 9**")
    with pytest.raises(freeze.FreezeConsistencyError, match="testing_family m"):
        freeze.verify(mini)


# --------------------------------------------------------------------------- #
# 2b. R25 — the two co-primary IUT sub-families (H2-RA m=3 + H2-Tail m=3)        #
# --------------------------------------------------------------------------- #
def test_two_co_primary_iut_families_validate_on_live():
    """The live prereg carries the R25 two-family structure and the gate reports the union + sub-sizes."""
    yml = freeze.load_yaml(REPO)
    fam = yml["inference"]["testing_family"]
    assert fam["m"] == 6
    assert set(fam.get("families", {})) == {"h2_ra", "h2_tail"}
    assert fam["families"]["h2_ra"]["m"] == 3
    assert fam["families"]["h2_tail"]["m"] == 3
    # The gate check line names testing_family.m and mentions the IUT sub-families.
    line = next(c for c in freeze.verify(REPO).checks if "testing_family.m" in c)
    assert "IUT sub-families" in line


def test_sub_family_m_mismatch_raises(mini: Path):
    """A sub-family whose declared m != its member count -> FreezeConsistencyError (R25 partition guard)."""
    # H2-RA declares m: 3 but we keep 3 members and flip its m to 2 -> count != m.
    _edit(mini / freeze.PREREG_YAML, "h2_ra:                                    # risk-adjusted-performance IUT (DEEP_H2 §7.1)\n        m: 3",
          "h2_ra:                                    # risk-adjusted-performance IUT (DEEP_H2 §7.1)\n        m: 2")
    with pytest.raises(freeze.FreezeConsistencyError, match="families.h2_ra.m"):
        freeze.verify(mini)


def test_sub_families_not_partitioning_union_raises(mini: Path):
    """A sub-family member that is NOT in the m=6 union -> the partition check fails-loud (R25)."""
    # Corrupt one H2-RA member's comparator so it no longer matches any union member.
    _edit(
        mini / freeze.PREREG_YAML,
        "          - {arm_a: distributional, arm_b: scalar,       metric: sharpe, level: null}\n"
        "          - {arm_a: distributional, arm_b: placebo,      metric: sharpe, level: null}\n"
        "          - {arm_a: distributional, arm_b: scalar_cvar5, metric: sharpe, level: null}",
        "          - {arm_a: distributional, arm_b: BOGUS,        metric: sharpe, level: null}\n"
        "          - {arm_a: distributional, arm_b: placebo,      metric: sharpe, level: null}\n"
        "          - {arm_a: distributional, arm_b: scalar_cvar5, metric: sharpe, level: null}",
    )
    with pytest.raises(freeze.FreezeConsistencyError, match="partition"):
        freeze.verify(mini)


def test_difference_test_relabel_raises(mini: Path):
    """A silent yaml relabel whose prose anchor is absent -> raises."""
    _edit(mini / freeze.PREREG_YAML,
          "difference_tests: [sharpe_recentred_bootstrap, cvar_difference]",
          "difference_tests: [sharpe_studentized_ledoit_wolf, cvar_difference]")
    with pytest.raises(freeze.FreezeConsistencyError, match="difference_tests"):
        freeze.verify(mini)


def test_cost_grid_mismatch_raises(mini: Path):
    """yaml grid != the prose grid -> raises."""
    _edit(mini / freeze.PREREG_YAML,
          "cost_sweep: {grid_bps: [0, 5, 10, 25, 50]",
          "cost_sweep: {grid_bps: [0, 5, 10, 25, 100]")
    with pytest.raises(freeze.FreezeConsistencyError, match="grid_bps"):
        freeze.verify(mini)


# --------------------------------------------------------------------------- #
# 3. Phase-0 precondition                                                       #
# --------------------------------------------------------------------------- #
def test_phase0_precondition_raises_when_absent(mini: Path):
    """Blank the Phase-0 marker -> FreezePreconditionError (refuse to freeze)."""
    _edit(mini / freeze.PREREG_YAML,
          'phase0_smoke_passed_log_id: "DECISION_LOG.md#PHASE-0 (GREEN 2026-06-17)"',
          'phase0_smoke_passed_log_id: null')
    with pytest.raises(freeze.FreezePreconditionError, match="Phase-0"):
        freeze.verify(mini)


def test_phase0_precondition_met_on_live():
    status = freeze.verify(REPO)
    assert "PHASE-0" in status.phase0_marker


# --------------------------------------------------------------------------- #
# 4. Canonical hash: deterministic, order-sensitive, line-ending invariant      #
# --------------------------------------------------------------------------- #
def test_hash_is_deterministic():
    """Same inputs -> same digest, every call."""
    assert freeze.canonical_hash(REPO) == freeze.canonical_hash(REPO)


def test_hash_order_sensitive(mini: Path):
    """Swapping the prose<->yaml concatenation order changes the hash (order is load-bearing)."""
    md = freeze._normalize_bytes((mini / freeze.PREREG_MD).read_bytes())
    # mirror canonical_bytes: the two MUTABLE freeze-state fields are blanked before hashing.
    yml = freeze._strip_freeze_state(
        freeze._normalize_bytes((mini / freeze.PREREG_YAML).read_bytes()).decode("utf-8")
    ).encode("utf-8")
    # canonical_bytes also appends each present _BOUND_CONFIG after the prereg pair; in the mini fixture
    # that is config/data.yaml (added to _mini_repo for the data_panel check, 2026-07-03), so the manual
    # reconstruction must include it to equal canonical_hash(mini).
    data = freeze._normalize_bytes((mini / "config" / "data.yaml").read_bytes())
    forward = freeze.sha256_bytes(md + b"\n" + yml + b"\n" + data)
    reversed_ = freeze.sha256_bytes(yml + b"\n" + md + b"\n" + data)
    assert forward == freeze.canonical_hash(mini)
    assert forward != reversed_


def test_hash_invariant_to_freeze_flip(mini: Path):
    """The canonical hash must NOT change when 'frozen: false->true' and 'freeze_hash: null-><d>' are set
    (else `--check` reports DRIFT forever post-freeze — the self-defeating bug; critical-review 2026-06-20)."""
    before = freeze.canonical_hash(mini)
    yml_path = mini / freeze.PREREG_YAML
    text = yml_path.read_text(encoding="utf-8")
    text = text.replace("frozen: false", "frozen: true", 1).replace("freeze_hash: null", f"freeze_hash: {before}", 1)
    yml_path.write_text(text, encoding="utf-8")
    assert freeze.canonical_hash(mini) == before  # invariant to the freeze act


def test_hash_invariant_to_line_endings(mini: Path):
    """A CRLF/BOM-rewritten checkout hashes identically to the LF one (the norm step)."""
    before = freeze.canonical_hash(mini)
    for name in (freeze.PREREG_MD, freeze.PREREG_YAML):
        p = mini / name
        raw = p.read_bytes()
        p.write_bytes(b"\xef\xbb\xbf" + raw.replace(b"\n", b"\r\n"))
    assert freeze.canonical_hash(mini) == before


def test_normalize_bytes_collapses_doubled_cr_idempotently():
    """Direct guard on the R52/V16 line-ending fix: a doubled ``\r\r\n`` (a CRLF checkout re-rewritten
    CRLF) collapses to a SINGLE LF regardless of the on-disk files' line endings — the hash-invariance
    test above only exercises this when the materialized fixture is CRLF. BOM-strip + idempotent too."""
    assert freeze._normalize_bytes(b"a\r\r\nb") == b"a\nb"
    assert freeze._normalize_bytes(b"a\r\nb") == b"a\nb"
    assert freeze._normalize_bytes(b"a\rb") == b"a\nb"
    assert freeze._normalize_bytes(b"\xef\xbb\xbfa\r\r\nb") == b"a\nb"
    once = freeze._normalize_bytes(b"x\r\r\ny")
    assert freeze._normalize_bytes(once) == once


def test_hash_changes_when_content_changes(mini: Path):
    """A real content change moves the hash (it actually covers the bytes)."""
    before = freeze.canonical_hash(mini)
    _edit(mini / freeze.PREREG_YAML, "matched_budget: 30", "matched_budget: 31")
    assert freeze.canonical_hash(mini) != before


# --------------------------------------------------------------------------- #
# 4b. The freeze hash binds the TREATMENT (arms.yaml + the loaded prompts; R62) #
# --------------------------------------------------------------------------- #
def _add_treatment_files(root: Path) -> None:
    """Copy the live treatment files (arms.yaml + the two LOADED prompts) into a mini root."""
    (root / "prompts").mkdir(exist_ok=True)
    shutil.copyfile(REPO / "config" / "arms.yaml", root / "config" / "arms.yaml")
    for name in ("system.txt", "initial_generation.txt"):
        shutil.copyfile(REPO / "prompts" / name, root / "prompts" / name)


def test_treatment_files_are_bound_into_hash(mini: Path):
    """Editing arms.yaml OR a LOADED prompt changes the canonical hash (R62, 2026-06-28): the
    manipulated variable's text is inside the frozen design, so a post-freeze tamper trips --check."""
    _add_treatment_files(mini)
    base = freeze.canonical_hash(mini)
    # 1) the per-arm feedback spec
    _edit(mini / "config" / "arms.yaml", "scalar_only", "scalar_only_TAMPERED")
    assert freeze.canonical_hash(mini) != base
    # 2) the system prompt (restore arms.yaml first)
    _add_treatment_files(mini)
    base2 = freeze.canonical_hash(mini)
    _edit(mini / "prompts" / "system.txt", "REWARD FUNCTIONS", "REWARD FUNCTIONS (tampered)")
    assert freeze.canonical_hash(mini) != base2
    # 3) the initial-generation prompt
    _add_treatment_files(mini)
    base3 = freeze.canonical_hash(mini)
    _edit(mini / "prompts" / "initial_generation.txt", "risk-adjusted return", "raw return only")
    assert freeze.canonical_hash(mini) != base3


def test_treatment_absent_is_skipped(mini: Path):
    """A minimal prereg-only root (no arms.yaml / prompts) still hashes — absent treatment files are
    skipped exactly like absent bound configs, so the prereg-only freeze fixtures stay valid."""
    assert not (mini / "prompts").exists()
    assert not (mini / "config" / "arms.yaml").exists()
    assert freeze.canonical_hash(mini)  # computes without error


def test_live_hash_binds_arms_and_prompts():
    """On the LIVE repo the canonical bytes include arms.yaml + the two loaded prompts (R62)."""
    blob = freeze.canonical_bytes(REPO)
    assert b"placebo_shuffled" in blob          # arms.yaml content is present
    assert b"REWARD FUNCTIONS" in blob          # prompts/system.txt content is present
    # The dead reflection prompt is NOT a bound treatment file (R63). We assert the STRUCTURE (the path is
    # absent from _BOUND_TREATMENT), not the byte-string: "reflection.txt" can legitimately appear in the
    # bound PROSE (e.g. the R62/R63 amendment rows in PREREGISTRATION.md), which would false-trip a
    # substring check on the blob.
    assert "prompts/reflection.txt" not in freeze._BOUND_TREATMENT
    assert "prompts/system.txt" in freeze._BOUND_TREATMENT
    assert "prompts/initial_generation.txt" in freeze._BOUND_TREATMENT
    assert "config/arms.yaml" in freeze._BOUND_TREATMENT


# --------------------------------------------------------------------------- #
# 5. --check does NOT mutate any file                                           #
# --------------------------------------------------------------------------- #
def test_check_does_not_mutate_live_files():
    """--check is read-only: the live yaml's frozen/freeze_hash are untouched."""
    yaml_path = REPO / freeze.PREREG_YAML
    md_path = REPO / freeze.PREREG_MD
    log_path = REPO / freeze.DECISION_LOG
    before = (yaml_path.read_bytes(), md_path.read_bytes(), log_path.read_bytes())

    rc = freeze.main(["--check"])
    assert rc == 0

    after = (yaml_path.read_bytes(), md_path.read_bytes(), log_path.read_bytes())
    assert before == after, "--check must not write to any artifact"
    # And the pre-freeze state is intact.
    yml = freeze.load_yaml(REPO)
    assert yml["frozen"] is False
    assert yml["freeze_hash"] is None


def test_check_reports_nonzero_on_drift(mini: Path, capsys):
    """If freeze_hash is recorded but the bytes drift, --check exits non-zero (CI guard)."""
    # Simulate a frozen-but-drifted repo: record a stale hash, then change content.
    _edit(mini / freeze.PREREG_YAML, "freeze_hash: null", "freeze_hash: deadbeef")
    _edit(mini / freeze.PREREG_YAML, "matched_budget: 30", "matched_budget: 31")
    status = freeze.verify(mini)
    assert status.recorded_hash == "deadbeef"
    assert status.recorded_hash != status.hash  # drift detected by verify()


# --------------------------------------------------------------------------- #
# 6. The WRITE path is implemented (smoke-tested on a COPY; never the real repo) #
# --------------------------------------------------------------------------- #
def test_set_yaml_frozen_flips_only_the_two_scalars(mini: Path):
    """The line-level write flips frozen+freeze_hash and preserves everything else."""
    digest = "a" * 64
    before = (mini / freeze.PREREG_YAML).read_text(encoding="utf-8")
    freeze._set_yaml_frozen(mini, digest)
    after = (mini / freeze.PREREG_YAML).read_text(encoding="utf-8")
    assert "frozen: true" in after
    assert f"freeze_hash: {digest}" in after
    # Only two lines changed.
    diff = [(a, b) for a, b in zip(before.splitlines(), after.splitlines()) if a != b]
    assert len(diff) == 2
    # The comments + amendment notes survive byte-for-byte (sample a load-bearing one).
    assert "Amendment D2" in after


def test_append_decision_log_records_hash_utc_sha(mini: Path):
    """The ADR-005 slot gains a dated FREEZE-DONE entry with hash + UTC + git SHA."""
    digest = "b" * 64
    freeze._append_decision_log(mini, digest, "2026-06-19T12:00:00Z", "cafef00d")
    log = (mini / freeze.DECISION_LOG).read_text(encoding="utf-8")
    assert "FREEZE-DONE" in log
    assert digest in log
    assert "2026-06-19T12:00:00Z" in log
    assert "cafef00d" in log
    # Appended below the marker (append-only audit log).
    assert log.index("<!-- amendments appended below this line -->") < log.index("FREEZE-DONE")


# --------------------------------------------------------------------------- #
# 2026-07-05 hardening guards: hermetic drift tests                            #
# --------------------------------------------------------------------------- #
def test_prompt_tail_neutrality_drift_raises(tmp_path):
    """A base prompt gaining tail vocabulary must fail the gate (R38 construct validity)."""
    (tmp_path / "prompts").mkdir()
    (tmp_path / "prompts" / "system.txt").write_text(
        "You design reward functions. Weigh return against risk and CVaR.", encoding="utf-8"
    )
    with pytest.raises(freeze.FreezeConsistencyError, match="cvar"):
        freeze.assert_prompt_tail_neutrality(tmp_path)
    # "tail" fires as a whole word (singular and plural) ...
    for phrase in ("mind the tail of returns", "heavy tails matter"):
        (tmp_path / "prompts" / "system.txt").write_text(
            f"You design reward functions. {phrase}.", encoding="utf-8"
        )
        with pytest.raises(freeze.FreezeConsistencyError, match="tail"):
            freeze.assert_prompt_tail_neutrality(tmp_path)
    # ... but NOT as a substring of benign words (2026-07-06 audit: a wording edit adding
    # "detailed"/"retail" must not false-block the freeze).
    (tmp_path / "prompts" / "system.txt").write_text(
        "Provide detailed reasoning; retail investors entail curtailed budgets.", encoding="utf-8"
    )
    assert "tail-neutrality" in freeze.assert_prompt_tail_neutrality(tmp_path)
    # 2026-07-06 completeness: the fed vector's MOMENT vocabulary is guarded too — "skewness"/
    # "kurtosis" fire (substring-safe) and bare "VaR" fires as a word...
    for phrase in ("penalize the skewness", "watch the kurtosis", "keep VaR small"):
        (tmp_path / "prompts" / "system.txt").write_text(f"You design rewards. {phrase}.", encoding="utf-8")
        with pytest.raises(freeze.FreezeConsistencyError):
            freeze.assert_prompt_tail_neutrality(tmp_path)
    # ... while "variance"/"varying" (containing 'var' without word boundaries) stay benign.
    (tmp_path / "prompts" / "system.txt").write_text(
        "Weigh return against variance under varying conditions.", encoding="utf-8"
    )
    assert "tail-neutrality" in freeze.assert_prompt_tail_neutrality(tmp_path)
    # a neutral prompt passes with the summary line
    (tmp_path / "prompts" / "system.txt").write_text(
        "You design reward functions. Weigh return against risk.", encoding="utf-8"
    )
    assert "tail-neutrality" in freeze.assert_prompt_tail_neutrality(tmp_path)


def test_search_splits_drift_raises(tmp_path):
    """An executed search window (prototype.yaml val_end) drifting from data.yaml must fail (map P23)."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "data.yaml").write_text(
        "splits:\n  train: {start: 2005-01-01, end: 2016-12-31}\n"
        "  val: {start: 2017-01-01, end: 2019-12-31}\n", encoding="utf-8"
    )
    (cfg / "prototype.yaml").write_text(
        'data:\n  val_end: "2017-12-31"\n  train_end: "2016-12-31"\n', encoding="utf-8"
    )
    with pytest.raises(freeze.FreezeConsistencyError, match="drifted"):
        freeze.assert_search_splits_match(tmp_path)
    (cfg / "prototype.yaml").write_text(
        'data:\n  val_end: "2019-12-31"\n  train_end: "2016-12-31"\n', encoding="utf-8"
    )
    assert "search splits" in freeze.assert_search_splits_match(tmp_path)


def test_bound_files_exist_real_root_only(tmp_path):
    """The existence assert fires only on a REAL root (a .git dir present — mini fixtures create
    pyproject.toml but never .git) with a bound file missing."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='x'\n", encoding="utf-8")
    assert freeze.assert_bound_files_exist(tmp_path) is None  # fixture root (no .git) -> skipped
    (tmp_path / ".git").mkdir()
    with pytest.raises(freeze.FreezeConsistencyError, match="MISSING"):
        freeze.assert_bound_files_exist(tmp_path)
