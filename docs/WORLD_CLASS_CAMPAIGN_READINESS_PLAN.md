# World-class / campaign-readiness 50-phase plan (2026-06-28)

Goal: make the dissertation **publishable at a top venue** and the design **flawlessly ready for the full
campaign run**, while holding the hard constraints — **determinism** (byte-identical replay), the **LSEG data
licence** (no third-party cloud, no new data without the user), **citation integrity** (every paper-attributed
reward/benchmark/protocol verified first-hand — no fabrication), and the pre-registration discipline (changes
are made *pre-freeze, pre-results*; report-only comparators are NOT new confirmatory IUTs). Each phase is a
real, freeze-safe deliverable. Foundation Phases 1–3 + P31 run as background research; downstream phases
execute on their *verified* output.

## GROUP I — Deep-research foundation
1. Publication-readiness gap analysis (what a top venue has that mine should). `[running]`
2. Human-designed reward fns + allocator benchmarks from real papers — exact formulas + verified cites. `[running]`
3. External-validity / datasets / reporting-standards (feasible vs user-gated). `[running]`
4. Citation-verification pass — confirm every surfaced DOI/arXiv first-hand; DO-NOT-CITE fence.
5. Synthesize research → one prioritized, verified ADD-NOW worklist.
31. First-hand on-disk paper extraction (PyMuPDF over `01_literature/`) → `docs/PAPER_BENCHMARK_EXTRACTIONS.md`. `[running]`

## GROUP II — Benchmark / "beat-the-human" panel (panel already has 9 rewards + 10 allocators → completeness + verified gaps)
6. Complete primary-paper citations for the 9 existing `REWARD_CANON` rewards.
7. Complete primary-paper citations for the 10 existing allocators.
8. Implement verified *genuinely-missing* reward baselines (prospect-theory/loss-averse, vol-targeting, spectral-risk) — verified-only, report-only.
9. Implement verified *genuinely-missing* allocators (Black-Litterman, time-series momentum, 60/40, cap-weight) — verified-only, report-only.
10. Register the expanded panel pre-freeze (PREREGISTRATION R62, report-only H1 comparators) + `eureka_loop.yaml`.
11. `docs/BENCHMARKS_CATALOG.md` — every baseline · formula · primary cite (publication table).

## GROUP III — Test & rigor maximization
12. Strict tests for every new reward baseline (contract/determinism/monotonicity/known-value).
13. Strict tests for every new allocator (simplex/scale/permutation/determinism).
14. Extend the mutation exhibit to `fitness.py`, `deflated_sharpe.py`, the new baselines.
15. Property-based + metamorphic tests for reward-family parity + allocator invariances.
16. Re-measure + hold coverage **≥90%** (close any new gaps honestly).

## GROUP IV — Statistical reporting & external validity (feasible, no new data)
17. rliable completeness: IQM + probability-of-improvement + stratified-bootstrap CIs + performance profiles.
18. Regime-conditional robustness (calm/stress/crisis) reporting completeness.
19. Sub-period / rolling-window descriptive robustness exhibit (report-only).
20. Crisis-window (2008/2020) stress descriptive exhibit.
21. Multi-model-LLM external-validity disclosure + honest claim-scoping.
22. Performance-profile / score-distribution figure spec for the PDF.

## GROUP V — Reproducibility & publication artifacts
23. Datasheet (Gebru) — verify/strengthen `DATASHEET_v1.md`.
24. Model card (Mitchell) for the SAC agent + the LLM reward-designer.
25. Papers-with-Code reproducibility checklist + a `make reproduce` entry point.
26. README publication spine + `CITATION.cff` / Zenodo-DOI readiness.
27. Related-work completeness pass (fold verified neighbours into the dossier).

## GROUP VI — Verification, validation, documentation, handoff
28. Adversarial verification of all new code (security/correctness/determinism) + citation-integrity audit.
29. Full validation gate: `freeze --check` (hash) · ruff · mypy · full suite · coverage ≥90% · mutation 100% core.
30. Comprehensive docs + memory + `CAMPAIGN_READINESS.md` checklist + the explicit user-gated items.

## GROUP VII — Paper-by-paper deep integration (read first-hand → verify/port method+benchmark+protocol → cite → integrate)
32. Eureka (Ma et al. 2024, arXiv:2310.12931) — port the beat-the-human reward-design comparison protocol + metric.
33. Moody & Saffell (2001, IEEE TNN) — verify `differential_sharpe` == the paper's Dₜ online recursion; cite.
34. Markowitz (1952, J. Finance) — mean-variance foundation; verify the MV reward/allocator; cite.
35. Rockafellar & Uryasev (2000, J. Risk) — CVaR formulation; verify `return_minus_cvar` + EVT-CVaR; cite.
36. DeMiguel, Garlappi & Uppal (2009, RFS) — adopt the Sharpe/CER/turnover benchmark-comparison protocol for the allocator table.
37. Maillard, Roncalli & Teiletche (2010, JPM) — verify `risk_parity` == equal-risk-contribution; cite.
38. López de Prado (2016, JPM) — verify the `hrp` 3-step algorithm (clustering → quasi-diag → recursive bisection); cite.
39. Black & Litterman (1992, FAJ) — implement the BL allocator (verified-missing); cite.
40. Jiang, Xu & Liang (2017, arXiv:1706.10059, EIIE) — portfolio-RL setup/reward contrast; related work.
41. Zhang, Zohren & Roberts (2020) — deep-RL-for-trading reward/eval; related work (+ a verified reward variant if apt).
42. Deng et al. (2016/2017, IEEE TNNLS) — direct/recurrent-RL reward lineage; related work.
43. rliable / Agarwal et al. (2021, NeurIPS, arXiv:2108.13264) — port the exact aggregate-metric protocol into reporting.
44. Henderson et al. (2018, AAAI, arXiv:1709.06560) — satisfy + cite the reproducibility/reporting checklist.
45. Fissler & Ziegel (2016, Annals of Stats, arXiv:1503.08123) — confirm the FZ0 joint (VaR,ES) elicitability backbone; cite (distinct from the Risk note 1507.00244).
46. FinRL / FinRL-Meta — data-integrity pitfalls + benchmark-env positioning; survivorship/PIT disclosure.
47. FinRL-DeepSeek (2502.07393) / CARD (2410.14660) / convex-scoring-RL (2505.04553) — verified cite-and-fence Related-Work paragraphs.
48. DSAC + spectral-risk "Beyond CVaR" (2501.02087) — secondary-critic + future-work framing.
49. Singh-Sorg (optimal reward) / Hadfield-Menell (IRD) — the ORP theory licence (designed reward for a bounded agent); theory spine.
50. López de Prado AFML / DSR / PBO — verify purge/embargo/CPCV/DSR/PBO == the implemented methods; cite.

> **50 phases is the ceiling of genuinely useful decomposition.** Beyond this, value comes from the research
> landing + verified implementation, not finer subdivision. Integrity gates every paper-attributed addition:
> verified first-hand or it does not enter `refs.bib`/`src/`.

## Atomic execution units (P52–P100) — granular decomposition
> These are the *atomic* execution units behind the strategic phases above. The count reflects granularity
> (196 corpus papers + 19 baselines + ~10 test modules + the chapters), **not** added scope or rigor: each is
> a concrete, freeze-safe, integrity-gated deliverable. Strategic tracking stays at P1–P51; these are worked
> as the research lands.

### GROUP VIII — Per-cluster corpus deep-read + integration (each: first-hand read → integration-map rows → fold into Related Work/Methods + flag cite gaps) — driven by workflow `corpus-deep-read`
- P52 `00_core_pillars` · P53 `A_reward_design_lineage` · P54 `B_closest_neighbours` (scoop watch) · P55 `C_signals_into_rewards` · P56 `D_evolve_trading_code` · P57 `E_distributional_RL_finance` · P58 `F_distributional_reward_for_LLMs` · P59 `G_contamination_lookahead` · P60 `H_foundational_canon` · P61 `H_manual_journal` · P62 `I_also_mentioned` · P63 `J_additional_relevant` · P64 `K_final_sweep`

### GROUP IX — Per-baseline first-hand verify + primary-cite + test (one per baseline)
- Rewards: P65 raw_return · P66 return_minus_variance · P67 return_minus_cvar · P68 differential_sharpe · P69 mean_variance_utility · P70 return_minus_drawdown · P71 return_minus_downside · P72 return_minus_turnover · P73 log_growth
- Allocators: P74 spy_buy_and_hold · P75 equal_weight (DeMiguel) · P76 mean_variance (Markowitz) · P77 risk_parity ⚠ **re-acquire the REAL Maillard-Roncalli-Teiletche paper** (on-disk file is mislabeled Cagna-Casuccio 2014) · P78 hrp · P79 minimum_variance · P80 inverse_volatility · P81 maximum_diversification (Choueifaty) · P82 cross_sectional_momentum · P83 Black-Litterman (NEW; master posterior verified in 1992 FAJ original)

### GROUP X — Reproducibility artifacts, atomic
- P84 datasheet refresh (Gebru) · P85 model card (Mitchell) · P86 `CITATION.cff` · P87 requirements/lockfile repro step · P88 `make reproduce` · P89 Zenodo-DOI prep · P90 ML-reproducibility-checklist doc (Pineau)

### GROUP XI — Per-module mutation + property exhibit (extend the kill-rate table module-by-module)
- P91 deflated_sharpe `[in progress]` · P92 inference/bootstrap · P93 inference/contamination · P94 inference/ood_stress · P95 inference/attribution · P96 regimes/definition · P97 env + sandbox

### GROUP XII — Per-chapter integration writeback (fold verified citations + benchmarks into the PDF)
- P98 Intro + Related Work fold-in · P99 Methods + Theory fold-in · P100 Discussion + Limitations fold-in

## GROUP XIII — Per-paper deep-dive (P101–P296: one phase per corpus paper) — workflow `wb8qcpkx5`
One agent per corpus PDF (196), each reading the paper FIRST-HAND and extracting: methodology, datasets,
software packages, the **GitHub repo** (web-checked), and an **integrity-gated IMPLEMENTABILITY verdict** for
THIS project (gates: determinism · LSEG licence · frozen-SAC scope · relevance). Outputs:
`docs/IMPLEMENTABILITY_SHORTLIST.md` (the gated actionable payload), `docs/PAPER_PACKAGES_GITHUB_INDEX.md`,
`docs/PAPER_DEEPDIVE_TABLE.md`, + an arXiv ACQUISITION-GAP list. Honest expectation (consistent with the
cutting-edge sweep that found NO technique passing the gate): mostly RELATED-WORK / FUTURE-WORK / USER-GATED-DATA,
with at most a small IMPLEMENT-NOW set (likely tooling/packages or report-only diagnostics).
- **P297 — Acquisition follow-up**: download the genuinely-relevant freely-available (arXiv) missing papers the
  synthesis flags into `01_literature/L_deepdive_additions/`, add them to `RELATED_WORK_WATCH.md`, and stage
  `% VERIFY` refs.bib entries (verified first-hand from the downloaded PDF) — never fabricated.

## User-gated (prepared by me, executed by the user)
New market/region/asset-class dataset (external validity) · the campaign run · Dr Okhrati sign-off (framing +
pivot) · the pre-submission reference round · `pip install pip-audit`.
