# Figure & Table Manifest

> **Status: structural scaffold (2026-06-28).** A numbered manifest of the figures and tables the dissertation
> needs, each with a one-line "what it shows" and its data source. Figures whose data depend on the unrun
> confirmatory campaign are marked **[CAMPAIGN]**; figures buildable now from the frozen panel, the design files,
> or static schematics are marked **[NOW]**. Numbering is indicative; reconcile to final chapter order at compile.
> Cross-references: methods design in `CH4_methods.md`; results placeholders in `CH6_results.md`; prediction table
> in `02_CHAPTER_theory.md` §C.7.

## Figures

| # | Title | What it shows | Data source | Chapter | Status |
|---|---|---|---|---|---|
| F1 | System / off-critic decoupling diagram | The full loop: LLM reward-designer → fixed SAC agent → off-critic tail estimator → feedback block; with the three-way decoupling (fed on train, selected on tail-blind validation DSR, tested on sealed CVaR) called out. | Static schematic from `CH4_methods.md` §4.4–4.6. | 4 | **[NOW]** |
| F2 | Prediction-branch diagram | The §C.7 Strict / Weak / Null branches and the mechanism conditions (selection sensitivity, designer responsiveness, agent attainability) that route to each. | Static schematic from `02_CHAPTER_theory.md` §C.7. | C | **[NOW]** |
| F3 | Panel stylised facts | Four-panel EDA of the frozen panel's TRAIN window (BUILT 2026-07-02, `src/viz/eda.py`): (a) return density vs matched Normal with excess-kurtosis and −3σ/−5σ exceedance ratios; (b) the empirical-vs-Normal CVaR curve across α (the crossover — no single scalar represents the tail); (c) volatility clustering with shaded stress episodes; (d) cross-sectional co-crash fractions calm-vs-stress. Motivates the multi-level tail feedback directly from the data. Re-render on univ5 post-rebuild is one command. | Frozen panel train window (`build_f3`). | 4 (Data) | **[NOW]** |
| F4 | Splits timeline | Train (2005–2016) / validation (2017–2019) / sealed test (2020–2026H1) — SPLIT C — with the 60-session purge bands and the COVID/2022 regime-shift markers. | Design constants from `CH4_methods.md` §4.2. | 4 | **[NOW]** |
| F5 | rliable headline interval | Per-seed IQM intervals (stratified bootstrap) for the H2 contrasts across the 9 arms — the headline visual. | `[CAMPAIGN]` archive (rliable). | 5 (§5.2) | **[CAMPAIGN]** |
| F6 | TOST equivalence | The two co-primary equivalence bounds (H2-RA, H2-Tail) plotted against the ±0.05-DSR SESOI band — equivalence-first. | `[CAMPAIGN]` archive (TOST). | 5 (§5.2) | **[CAMPAIGN]** |
| F7 | Controls overlay | Placebo and placebo_shuffled overlaid on the same axes as the distributional arm (tail and Sharpe), so the effect is read against its own controls. | `[CAMPAIGN]` archive. | 5 (§5.3) | **[CAMPAIGN]** |
| F8 | Mechanism / responsiveness | Fed-tail change vs authored-reward change (responsiveness, with sign); EPIC/STARC reward-distance between arms. | `[CAMPAIGN]` archive (mediation + reward metrics). | 5 (§5.5) | **[CAMPAIGN]** |
| F9 | Learning curves / training budget | Critic-loss and return trajectories vs the 400,000-step budget across arms — the training-budget diagnostic (incl. the extended ladder). | `[CAMPAIGN]` archive (per-candidate logs). | 5 (§5.5) | **[CAMPAIGN]** |
| F10 | 3-link mechanism chain | The paper's spine as one image: fed tail signal -> authored code -> trained policy -> realised tail, with SQ1/SQ2/H2-Tail as the arrows and the red cut glyph on the MEASURED severed link (outcome-neutral: built now, annotations + cut position filled at the bank gate). BUILT 2026-07-13 (`schematics.mechanism_chain`, both variants render). | Scaffold NOW; `[CAMPAIGN]` fills SQ1 rho, a*b, the cut. | 1 (par 1) + 5 (par 5.5) | **[NOW + CAMPAIGN fill]** |
| F11 | The measured budget curve (R77 MANDATORY) | Per-seed validation-DSR vs training budget, 100k-1.6M (16x), both authored winners; thin lines = CRN seeds (the honest fan-out), thick = seed mean; B*marked at the measured knee. BUILT 2026-07-18 (viz.figures.budget_curve_exhibit; rendered on the real 30-point grid). Campaign version re-renders on the dose-response tier. | Curve grid NOW; dose-response tier at the gate. | 4 (design) + 6 (exhibit) | **[NOW + CAMPAIGN re-render]** |
| F12 | Cross-leg forest (v2) | Per-leg (dist − scalar) CVaR-5% mean diff + 90% seed-bootstrap CI at the floor tier, one row per replication leg; T0-floor-excluded legs greyed + annotated as authoring/search failures (never votes); the pooled-mean row at the bottom with the joint-flip permutation *p*. Engine-built `cross_leg_forest` (2026-07-21). | `[CAMPAIGN]` leg archives via `leg_aggregate` + `cross_model`. | 5 (§5.7–5.8) | **[CAMPAIGN]** |
| F13 | Capability-gradient scatter (v2) | Per-leg SQ1 responsiveness vs the pre-declared external capability composite (M2 score = secondary axis option); the two family pairs (Qwen 9B↔27B open, Haiku↔Opus closed) connected as within-family segments; Spearman ρ annotated; the registered monotone prediction read directly off the picture. Engine-built `capability_gradient` (2026-07-21). | `[CAMPAIGN]` + `capability_regression`. | 5 (§5.8) | **[CAMPAIGN]** |
| F14 | Authoring-reliability heatmap (v2) | Models × reliability metrics (format compliance, sandbox pass, violation taxonomy share, refusal/truncation, code diversity) as an annotated rate heatmap — the practitioner's "which models write executable objective code" picture. Engine-built `reliability_heatmap` (2026-07-21). | `[CAMPAIGN]` ledger + pre-launch compliance baselines (`leg_gates`). | 5 (§5.7) | **[CAMPAIGN]** |
| F15 | Ten-winners annotated code exhibit (v2) | One winning reward program per model, side-by-side monospace panels with tail-construct lines highlighted — the qualitative "what do different model families write" exhibit (per-model taxonomy made visible). Engine-built `ten_winners_exhibit` (2026-07-21). | `[CAMPAIGN]` winner archives. | 5 (§5.7) | **[CAMPAIGN]** |
| F16 | Reward-code embedding (3-D) | Classical-MDS (Torgerson) embedding of the pairwise AST-distance matrix over authored winners, coloured by arm — shows whether reward PROGRAMS cluster by arm (content) or cut across it (the mechanism's structural signature). Engine-built `viz.advanced.reward_embedding_3d`. | `[CAMPAIGN]` winner sources → `reward_code_distance`. | **TBD — placement is Tamer's call** | **[CAMPAIGN]** |
| F17 | Search landscape (CVaR × generation × Sharpe, 3-D) | Per-candidate search trajectories in (CVaR, Sharpe) across generations — the optimisation dynamics converging onto the shared null neighbourhood. Engine-built `viz.advanced.risk_return_generation_3d`. | `[CAMPAIGN]` per-candidate archive. | **TBD — placement is Tamer's call** | **[CAMPAIGN]** |
| F18 | Search-evolution keyframes | Cumulative generation-by-generation keyframes of the same search (the static, print-safe counterpart to the supplementary GIF). Engine-built `viz.advanced.search_evolution_keyframes`. | `[CAMPAIGN]` per-candidate archive. | **TBD — placement is Tamer's call** | **[CAMPAIGN]** |
| F19 | Delisting-band robustness (figure) | The headline contrasts re-estimated across the delisting band $d\in\{0,-30,-55,-100\}\%$ with CIs, shown against the ±SESOI corridor — the FIGURE counterpart to T3's table row. Engine-built `viz.figures.delisting_robustness`. | `[CAMPAIGN]` archive re-scored per band. | **TBD — placement is Tamer's call** | **[CAMPAIGN]** |

| F20 | **Seed-trajectory panel** (Okhrati D2) | Every headline statistic as a **running estimate against seed count $n=1\ldots N$** with its uncertainty band — small multiples over *every* seeded unit (all canon members, all core arms, all leg arms, the H2 contrast, each H1 IUT leg, H3, H4 and the seeded mechanism statistics), plus the per-seed-block variant that doubles as a heterogeneity audit. Answers *"has your estimate converged, do you understand your own noise, and is your conclusion an artefact of where you stopped?"* — answerable here because the ladder is cumulative and CRN-paired, so every prefix is itself a valid complete study | per-seed test outcomes (intact; **not** `metrics.train_curve.return`, which is empty — B.8.12) | 5 | **SPECIFIED — generator is drift-fenced (ops item 15d); caption rules below are BINDING** |

> ## ⚠⚠ F20 IS INVALID UNLESS ITS CAPTION CARRIES ALL FOUR CONDITIONS
>
> A running-estimate curve invites a reader to eyeball *"where it settled"* — which is exactly the
> optional-stopping logic the pre-registration forbids. Done right this is the strongest rigour exhibit in
> the document; done wrong it hands a referee a weapon. Three conditions come from the standing D2 rule; the
> fourth was measured on 2026-08-01 and is the one most likely to be got wrong in implementation.
>
> 1. **Seeds in the REGISTERED order.** Never ordered by outcome value — that would manufacture the trend.
> 2. **The exogenous stopping rule stated in the caption**, with the terminal rung marked.
> 3. **An explicit statement that no inference was drawn at any prefix.**
> 4. **★ ORDER BY SEED INDEX, NOT BY ARRIVAL — and say so in the caption.** The C4 seed ladder **executes in
>    PACK order, not seed order**: measured on the qwen3.5-9b leg, `scalar_cvar5`'s first two completed seeds
>    are **11 and 12, not 0 and 1**. A curve built from the archive as records land is therefore a curve over
>    an **arbitrary seed subsequence chosen by the cluster scheduler** — precisely the optional-stopping
>    artefact condition 1 exists to prevent. Every unit's seed set is exactly $\{0,\ldots,29\}$, verified, so
>    the registered order *is* ascending seed index.
>
> **Conditions 1 and 4 read as contradictory and are not — the distinction is load-bearing.** "Never sorted"
> forbids sorting by *value*; condition 4 requires sorting by *seed index*, which is not a re-ordering at all
> but the **restoration** of the registered order that scheduling had scrambled. Anyone implementing this
> must not resolve the apparent conflict by leaving arrival order in place.

> **⚠ F16–F19 added 2026-07-26 (deep review loop 101, finding #79) — INVENTORY RECONCILIATION ONLY.**
> `scripts/make_figures.py` already BUILDS all four (`render_advanced` emits F16/F17/F18; `render_all`
> emits F19), and its module docstring states the two static 3-D figures "go IN the PDF" — yet the
> manifest, whose stated job is enumerating "the figures and tables the dissertation needs", listed none
> of them, so no chapter cross-referenced them. They would have been silently dropped from the PDF, or
> inserted without the manifest ID/cross-reference discipline. These rows record only what the engine
> DEMONSTRABLY produces; the **chapter placement — and whether F18/F19 belong in the body, an appendix,
> or supplementary material at all — is a writing decision left to Tamer**, deliberately not made here.
> (Numbering follows this file's own "numbering is indicative; reconcile at compile" convention.)

## Tables

| # | Title | What it shows | Data source | Chapter | Status |
|---|---|---|---|---|---|
| T1 | Run ledger | Arms × seeds × candidate budget, total candidates/steps, freeze hash, deviation count, realised compute, rejection/divergence counts. | `[CAMPAIGN]` archive + `PREREGISTRATION.md` hash. | 5 (§5.1) | **[CAMPAIGN]** |
| T2 | IUT results | Per-leg one-sided IUT *p* and TOST equivalence bounds for H2-RA and H2-Tail (distributional vs scalar / placebo / scalar_cvar5), plus the FZ0/DM-HLN ES backtest. | `[CAMPAIGN]` archive. | 5 (§5.2) | **[CAMPAIGN]** |
| T3 | Robustness | Delisting band $d\in\{0,-30,-55,-100\}\%$, cost sweep, PBO (CSCV), Deflated-Sharpe cross-check, BAB/QMJ factor attribution. | `[CAMPAIGN]` archive. | 5 (§5.3) | **[CAMPAIGN]** |
| T4 | Secondary hypotheses | H1 (confirmatory node N6: IUT dominance over the 11-name hand-reward canon, reported with the per-baseline dominance profile), H3 (TOST-bounded equivalence), H4 (LLM vs the best of the optimiser portfolio {random_search, bayes_opt, cma_es, tpe} at matched compute; node N4). | `[CAMPAIGN]` archive. | 5 (§5.4) | **[CAMPAIGN]** |
| Table 4.1 | Rigour ledger (in-body, CH4 §4.7) | Examiner-facing map of each named threat to validity → the design element that guards it (leakage, self-grading, format confound, overfitting, reward-scale, etc.). | `docs/RIGOUR_LEDGER.md` (static; rendered as the in-body Table 4.1 — the former "T5 / Appendix A — Rigour ledger" plan was consolidated to the in-body table on 2026-07-04). | 4 (§4.7) | **[built]** |
| T5 | Arms specification | The 9 arms and the single manipulated variable (feedback block) per arm: distributional, scalar, placebo, scalar_cvar5, placebo_shuffled, random_search, bayes_opt, cma_es, tpe. | Static from `CH4_methods.md` §4.5. | 4 | **[NOW]** |
| T6 | Per-leg contrasts (v2) | One row per replication leg: (dist − scalar) CVaR-5% and Sharpe floor-30 contrasts + 90% CIs, T0-floor verdict, completed/truncated status, per-leg bank-gate verdict. | `[CAMPAIGN]` leg archives (`leg_aggregate`). | 5 (§5.7) | **[CAMPAIGN]** |
| T7 | Authoring reliability (v2) | Per model: pre-launch format-compliance baseline, sandbox pass rate, contract-violation taxonomy, refusal/truncation rates, code diversity, taxonomy cluster — the reliability-as-finding table (failed legs report HERE, never as synthesis votes). | `[CAMPAIGN]` ledger + `leg_gates` baselines. | 5 (§5.7) | **[CAMPAIGN]** |

*(Compile note: F1–F4, F2's branch labels, and T5 (Arms specification) are buildable now — the rigour ledger is the in-body Table 4.1 — and should be drafted ahead of the
campaign; all `[CAMPAIGN]` items must remain unrendered placeholders until the frozen run completes. Keep figure
numbering keyed to `CH6_results.md` cross-references.)*

## Figure engine (2026-06-29) — `src/viz/` + `scripts/make_figures.py`

A deterministic, publication-grade renderer now exists for the data-driven headline figures (report-only;
reads results, never gates a hypothesis). Built on matplotlib 3.11 + seaborn 0.13.2 (no new deps), Okabe-Ito
colourblind-safe palette with redundant marker/hatch encoding (greyscale-print safe), 600-dpi PNG + vector
PDF. `scripts/make_figures.py --demo` (default) renders the whole suite on **synthetic NULL-shaped data** so
the engine is validatable NOW; post-campaign, the same `src/viz.figures` functions take the real per-seed +
inference outputs and re-render identical figures. **No demo number is a result.** Built renderers (each a
function in `src/viz/figures.py`, tested in `tests/test_viz.py`):

| Renderer (`src.viz.figures`) | Manifest item | Honest-null device |
|---|---|---|
| `rliable_intervals` | **F5** | per-arm IQM + 95% stratified-bootstrap CIs; overlap ⇒ consistent with H0 |
| `equivalence_forest` | **F6** | 90% TOST interval vs the shaded ±0.05-DSR SESOI band; filled=equivalent / open=inconclusive (never reads a null off a p) |
| `risk_return_clouds` | **NEW (F-D)** | the 9 arms' per-seed (CVaR, Sharpe) clouds collapse onto one neighbourhood — the whole-story null image |
| `evidence_for_null` | **NEW (F-E)** | JZS Bayes-factor gauge (Jeffreys bands) + Model-Confidence-Set membership strip — positive evidence FOR H0 |
| `reward_code_similarity` | **F8 (mechanism)** | AST-distance clustered heatmap + dendrogram + arm sidebar — clusters cut ACROSS arms (the placebo writes the same code) |
| `cross_leg_forest` | **F12 (v2)** | per-leg CIs vs the zero line, excluded legs greyed-not-hidden, pooled-mean row carries the only inferential number (the permutation *p*) |
| `capability_gradient` | **F13 (v2)** | family-pair segments make the controlled contrast visible; a flat cloud = the capability-independence honest-null image |
| `reliability_heatmap` | **F14 (v2)** | rates annotated in-cell; a full-compliance column renders unremarkably (no rhetorical scaling) |
| `ten_winners_exhibit` | **F15 (v2)** | verbatim code, mechanical highlight rule (registered tail-construct regexes) — no cherry-picked lines |

The honesty discipline (§5 reporting rules in `CH6_results.md`): plot effect size + interval against the
SESOI band, never a p-value or a bare bar of means; captions must distinguish "equivalent to within ±0.05
DSR" (the claim) from "no effect exists" (not the claim) and "inconclusive". Remaining headline figures to
wire post-campaign (data only): controls raincloud (F7), responsiveness/prompt-leak scatter (F8b), learning
curves (F9). Static `[NOW]` schematics are ENGINE-BUILT (`src/viz/schematics.py`: F1 `system_diagram`,
F2 `prediction_branch`, F4 `splits_timeline`); F1, F2 and F4 are all engine-built, tested, and rendered to `outputs/figures/`. F3 stylised facts IS engine-built (`src/viz/eda.py::build_f3`, 2026-07-02; see
the F3 row above) and rendered 2026-07-02 from the ACTIVE **univ5** Split-C train window (excess kurtosis
15.25; empirical/Normal CVaR crossover ×0.84→×1.66; stress co-crash 19.7%).

## 2026-07-26 additions — corpus-standard figures (G1–G5) + tables (G7–G9) + the capture layer

Added after a deep sweep of ~20 lineage/finance papers' figure/table archetypes + the rliable / Ten-Simple-
Rules standards (`docs/METRICS_AND_FIGURES_COMPLETENESS_2026-07-26.md`). All report-only, engine-built + tested.

| # | Title | What it shows | Renderer (`src.viz.figures`) | Status |
|---|---|---|---|---|
| G1 | Performance profiles | per-arm run-score distribution P(score>τ) — the 2nd rliable-quartet member; overlap = null | `performance_profile` | **[NOW engine / CAMPAIGN data]** |
| G2 | Probability of improvement | per-arm P(arm>baseline)+CI vs the 0.5 no-effect line (rliable A.28/29) | `probability_of_improvement` | **[NOW engine / CAMPAIGN data]** |
| G3 | Return / tail distribution | per-arm realized-return ECDF with the α-VaR marked + left tail shaded (the risk story) | `return_tail_distribution` | **[NOW engine / CAMPAIGN data]** |
| G4 | Equity + drawdown | log growth-of-1 + underwater drawdown over the sealed test (finance staple) | `equity_drawdown` | **[NOW engine / CAMPAIGN data]** |
| G5 | Allocation heatmap | top-K holdings' weights over time + 'other' residual (learned-policy exhibit) | `allocation_heatmap` (from `exposure.alloc_snapshots`) | **[NOW engine / CAMPAIGN data]** |

| # | Title | What it shows | Source | Status |
|---|---|---|---|---|
| G7 | Fixed agent+training+env config | every held-fixed knob (SAC, B*=400k, seed ladder, env) — reproducibility artifact | `docs/PAPER_TABLES_G7_G9_2026-07-26.md` (from config, verified) | **[NOW]** |
| G8 | Novelty matrix | us vs Eureka/Text2Reward/DrEureka/REvolve/CARD/DLM/GIFT/ELfolio/RD-Agent × the 5 conjunctive-cell dims | same doc (corpus-verified) | **[NOW]** |
| G9 | Frozen-prompt reference | the 3 hash-bound prompts + the single-substitution identification hinge | same doc + `prompts/` | **[NOW]** |

**Capture layer (M1–M4, pre-freeze, determinism-safe; `docs/METRICS_AND_FIGURES_COMPLETENESS_2026-07-26.md`).**
The frozen-winner TEST record now archives (inside `metrics{}`, report-only, best-effort): `test_exposure`
(M1), `test_alloc` (M1b → G5), `test_components` (M3), `train_curve` (M2 → F9). These are the data G3/G4/G5 +
F9 need — a frozen, replay-only campaign can only plot what it logged. Byte-exact determinism verified
(`scripts/reproduce_synthetic.py --check` reproduces the golden with the recorders attached).

### Tables added 2026-07-30 (built; all excluded from the word count)

| # | Title | What it shows | Source file | Chapter | Status |
|---|---|---|---|---|---|
| T10 | Literature positioning matrix | 9 neighbours x 6 dimensions with our row last; the pre-registration column is the lead claim | `paper/tables/T_literature_positioning.md` | CH2 | **BUILT** |
| T11 | Design decisions | choice / alternatives / rationale / **cost**, incl. two rows that bias AGAINST our own hypothesis | `paper/tables/T_design_decisions.md` | CH4 | **BUILT** |
| T12 | Scale and difficulty | components, tests, models, trainings, core-hours, off-the-shelf vs written | `paper/tables/T_scale_and_difficulty.md` | Appendix | **BUILT** |
| T13 | The nine arms | feedback content per arm + the role each control plays | `paper/tables/T_arms_and_hypotheses.md` | CH4 | **BUILT** |
| T14 | Environment specification | 30+cash, PIT selection, 60-session lookback, simplex, 10 bps | same file | CH4 | **BUILT** |
| T15 | Confirmatory decision rules | the six nodes N1-N6 with direction and equivalence backstop | same file | CH4 | **BUILT** |
| T16 | Model suite with pins | 11 models, HF commit pins, reasoning off, caps matched at 16,384 | `paper/tables/T_models_and_reward_canon.md` | CH4 | **BUILT** |
| T17 | The eleven-reward canon | each objective with its literature source; the turnover row carries a result | same file | CH4 | **BUILT** |

### Prose sections added 2026-07-30

| Ref | Title | Purpose | Source file |
|---|---|---|---|
| S1 | Numbered contributions C1-C6 | each claim with its evidence and section; C6 (the confirmatory answer) marked PENDING. ⚠ LANDED 2026-08-01 as **Table 1.3** in `paper/CH1_introduction.md`, which is the compiled artefact; `paper/sections/CH1_contributions.md` is NOT in `build_paper.ASSEMBLY` and is now the stale copy. Two of its rows (the turnover finding, the evaluation lesson) have NOT been carried across and remain open | `paper/CH1_introduction.md` (live) · `paper/sections/CH1_contributions.md` (stale source) |
| S2 | Severity paragraph | pre-registration does not confer Popperian severity (R61) | `paper/sections/CH3_severity_paragraph.md` |
| S3 | Wider context | three MEASURED findings that generalise past finance | `paper/sections/CH7_wider_context.md` |
| S4 | Quality-control record | the machinery, organised analytically not chronologically | `paper/appendices/A_quality_control_record.md` |

⚠ **Reconcile at compile:** numbering above is provisional (T10+ to avoid colliding with T1-T3 already
listed). The existing `paper/NOMENCLATURE.md` already satisfies the notation-table requirement and
`paper/APPENDIX_B_limitations.md` the limitations register — **neither was rebuilt**, both were extended.
