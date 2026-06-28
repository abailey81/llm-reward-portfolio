# Documentation index

A reader's map to `docs/`. Files are **not** physically reorganised (paths are stable so the freeze gate,
paper cross-references, and `scripts/freeze.py`'s `docs/DECISION_LOG.md` write target are untouched); this
index groups them by purpose. Start with the root [README.md](../README.md) and [CLAUDE.md](../CLAUDE.md).

## Frozen design (authoritative — read first)
- [../PREREGISTRATION.md](../PREREGISTRATION.md) — the FROZEN prose record (hypotheses, the seven arms, seeds, inference plan, splits, amendments). Machine mirror: [../config/preregistration.yaml](../config/preregistration.yaml).
- [../DECISIONS.md](../DECISIONS.md) — authoritative ADRs (001–024+); new decisions go here.
- [DECISION_LOG.md](DECISION_LOG.md) — A-line audit/impl record + the freeze hash slot (ADR-005). *Freeze-write target — do not move.*
- [FREEZE_RUNBOOK.md](FREEZE_RUNBOOK.md) — how to run `scripts/freeze.py`. [RIGOUR_LEDGER.md](RIGOUR_LEDGER.md) — amendment ledger R11–R60.

## Run / operate the campaign
- [CAMPAIGN_RUNBOOK.md](CAMPAIGN_RUNBOOK.md) · [CAMPAIGN_preflight.md](CAMPAIGN_preflight.md) · [RUN_READINESS_2026-06-19.md](RUN_READINESS_2026-06-19.md) · [SUPERCOMPUTER_RUNBOOK.md](SUPERCOMPUTER_RUNBOOK.md)
- [COMPUTE_AND_TRAINING_TIME.md](COMPUTE_AND_TRAINING_TIME.md) — wall-clock / cost / run-count accounting (7-arm).
- [CAMPAIGN_SPEC_run_robustness.md](CAMPAIGN_SPEC_run_robustness.md) · [CAMPAIGN_SPEC_ram_thermal.md](CAMPAIGN_SPEC_ram_thermal.md)

## Specifications
- [ARCHITECTURE_BLOCKS.md](ARCHITECTURE_BLOCKS.md) · [environment_spec_v1.md](environment_spec_v1.md) · [distributional_feedback_schema.md](distributional_feedback_schema.md)
- [CAMPAIGN_power.md](CAMPAIGN_power.md) · [CAMPAIGN_variance.md](CAMPAIGN_variance.md) · [POWER_ANALYSIS.md](POWER_ANALYSIS.md)

## Theory & design (the "why")
- [DEEP_H1.md](DEEP_H1.md) · [DEEP_H2.md](DEEP_H2.md) (headline) · [DEEP_H3.md](DEEP_H3.md) · [DEEP_H4.md](DEEP_H4.md)
- [DEEP_STATS_backbone.md](DEEP_STATS_backbone.md) · [DEEP_FRAMING_discipline.md](DEEP_FRAMING_discipline.md)
- [ANALYSIS_METHODS_AND_FUTURE_WORK.md](ANALYSIS_METHODS_AND_FUTURE_WORK.md) — what backtest/inference machinery is implemented (incl. Monte-Carlo/CSCV/PBO/DSR) + labelled rolling-window/MC Future Work.
- [CAMPAIGN_benchmarks.md](CAMPAIGN_benchmarks.md) · [CAMPAIGN_contamination_ood.md](CAMPAIGN_contamination_ood.md) · [CAMPAIGN_attribution.md](CAMPAIGN_attribution.md) · [PROPOSAL_PIVOT_DISCLOSURE.md](PROPOSAL_PIVOT_DISCLOSURE.md)

## Audits & verification (assurance)
- [DEEP_AUDIT_2026-06-25_13agent.md](DEEP_AUDIT_2026-06-25_13agent.md) · [DEEP_AUDIT_2026-06-26_round6_freeze_ready.md](DEEP_AUDIT_2026-06-26_round6_freeze_ready.md) · [DEEP_AUDIT_2026-06-26_verification.md](DEEP_AUDIT_2026-06-26_verification.md)
- [CODE_QUALITY_audit.md](CODE_QUALITY_audit.md) · [DEEP_SYSTEM_redteam.md](DEEP_SYSTEM_redteam.md) · [EXAMINER_grade_audit.md](EXAMINER_grade_audit.md)
- [TEST_RIGOR.md](TEST_RIGOR.md) — coverage (82%), property/metamorphic/adversarial depth, and the mutation-score exhibit (100% kill on metrics.py via `scripts/mutation_probe.py`).
- [EXAMINER_OBJECTIONS_AND_DEFENCES.md](EXAMINER_OBJECTIONS_AND_DEFENCES.md) — deep-research (adversarially verified) examiner red-team: top objections + best-practice defences + verified citations; arms the Discussion/Limitations. Flags the Popperian→Mayoian framing decision (§1c).

## Benchmarks & results
- [DEEP_BENCH_T0.md](DEEP_BENCH_T0.md) · [DEEP_BENCH_T4.md](DEEP_BENCH_T4.md) · [CAMPAIGN_freeze_decisions.md](CAMPAIGN_freeze_decisions.md)

## Literature & novelty
- [RESEARCH_SCAN_2026-06-27.md](RESEARCH_SCAN_2026-06-27.md) — latest 6-agent tech/repo/tooling scan (novelty intact; cite/fence list).
- [../RELATED_WORK_WATCH.md](../RELATED_WORK_WATCH.md) — standing novelty-surveillance log.
- [LIT_gap_llm_reward_optimizer.md](LIT_gap_llm_reward_optimizer.md) · [LIT_gap_risk_distributional_portfolio.md](LIT_gap_risk_distributional_portfolio.md) · [EUREKA_gap_analysis.md](EUREKA_gap_analysis.md) · [REFERENCES.md](REFERENCES.md)

## Data & transparency
- [DATASHEET_v1.md](DATASHEET_v1.md) · [DATA_ENTITLEMENTS.md](DATA_ENTITLEMENTS.md) · [DATA_REPULL_DELISTING.md](DATA_REPULL_DELISTING.md)
- [INFRASTRUCTURE_ASSESSMENT.md](INFRASTRUCTURE_ASSESSMENT.md) — strict tools/database adopt-reject matrix (verdict: parquet+manifest+checksum is correct; zero databases needed).

## Pre-submission & oversight
- [SESSION_LOG_2026-06-27_to_28.md](SESSION_LOG_2026-06-27_to_28.md) — full narrative record of the 2026-06-27/28 session (research, audit discharge, methodology upgrade, coverage→90.4%, what's still user-only).
- [CITATION_VERIFICATION_TODO.md](CITATION_VERIFICATION_TODO.md) — ranked RED/YELLOW reference-verification list + the DO-NOT-CITE fence.
- [SUPERVISOR_REVIEW_NOTE.md](SUPERVISOR_REVIEW_NOTE.md) — Dr Okhrati courtesy review: the Mayoian reframe + pending pivot-disclosure sign-off.

## Planning / contingency
- [ADVANCEMENT_AND_CLEANUP_PLAN.md](ADVANCEMENT_AND_CLEANUP_PLAN.md) · [OPTION_A_compute_enabled_expansion.md](OPTION_A_compute_enabled_expansion.md) · [RESEARCH_RESOURCES.md](RESEARCH_RESOURCES.md)
