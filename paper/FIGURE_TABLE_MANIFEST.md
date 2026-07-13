# Figure & Table Manifest

> **Status: structural scaffold (2026-06-28).** A numbered manifest of the figures and tables the dissertation
> needs, each with a one-line "what it shows" and its data source. Figures whose data depend on the unrun
> confirmatory campaign are marked **[CAMPAIGN]**; figures buildable now from the frozen panel, the design files,
> or static schematics are marked **[NOW]**. Numbering is indicative; reconcile to final chapter order at compile.
> Cross-references: methods design in `CH4_methods.md`; results placeholders in `CH6_results.md`; prediction table
> in `02_CHAPTER_theory.md` §3.7.

## Figures (~9)

| # | Title | What it shows | Data source | Chapter | Status |
|---|---|---|---|---|---|
| F1 | System / off-critic decoupling diagram | The full loop: LLM reward-designer → fixed SAC agent → off-critic tail estimator → feedback block; with the three-way decoupling (fed on train, selected on tail-blind validation DSR, tested on sealed CVaR) called out. | Static schematic from `CH4_methods.md` §4.4–4.6. | 4 | **[NOW]** |
| F2 | Prediction-branch diagram | The §3.7 Strict / Weak / Null branches and the mechanism conditions (selection sensitivity, designer responsiveness, agent attainability) that route to each. | Static schematic from `02_CHAPTER_theory.md` §3.7. | 3 | **[NOW]** |
| F3 | Panel stylised facts | Four-panel EDA of the frozen panel's TRAIN window (BUILT 2026-07-02, `src/viz/eda.py`): (a) return density vs matched Normal with excess-kurtosis and −3σ/−5σ exceedance ratios; (b) the empirical-vs-Normal CVaR curve across α (the crossover — no single scalar represents the tail); (c) volatility clustering with shaded stress episodes; (d) cross-sectional co-crash fractions calm-vs-stress. Motivates the multi-level tail feedback directly from the data. Re-render on univ5 post-rebuild is one command. | Frozen panel train window (`build_f3`). | 4 (Data) | **[NOW]** |
| F4 | Splits timeline | Train (2005–2016) / validation (2017–2019) / sealed test (2020–2026H1) — SPLIT C — with the 60-session purge bands and the COVID/2022 regime-shift markers. | Design constants from `CH4_methods.md` §4.2. | 4 | **[NOW]** |
| F5 | rliable headline interval | Per-seed IQM intervals (stratified bootstrap) for the H2 contrasts across the 7 arms — the headline visual. | `[CAMPAIGN]` archive (rliable). | 6 (§6.2) | **[CAMPAIGN]** |
| F6 | TOST equivalence | The two co-primary equivalence bounds (H2-RA, H2-Tail) plotted against the ±0.05-DSR SESOI band — equivalence-first. | `[CAMPAIGN]` archive (TOST). | 6 (§6.2) | **[CAMPAIGN]** |
| F7 | Controls overlay | Placebo and placebo_shuffled overlaid on the same axes as the distributional arm (tail and Sharpe), so the effect is read against its own controls. | `[CAMPAIGN]` archive. | 6 (§6.3) | **[CAMPAIGN]** |
| F8 | Mechanism / responsiveness | Fed-tail change vs authored-reward change (responsiveness, with sign); EPIC/STARC reward-distance between arms. | `[CAMPAIGN]` archive (mediation + reward metrics). | 6 (§6.5) | **[CAMPAIGN]** |
| F9 | Learning curves / training budget | Critic-loss and return trajectories vs the 200,000-step budget across arms — the training-budget diagnostic (incl. the extended ladder). | `[CAMPAIGN]` archive (per-candidate logs). | 6 (§6.5) | **[CAMPAIGN]** |
| F10 | 3-link mechanism chain | The paper's spine as one image: fed tail signal -> authored code -> trained policy -> realised tail, with SQ1/SQ2/H2-Tail as the arrows and the red cut glyph on the MEASURED severed link (outcome-neutral: built now, annotations + cut position filled at the bank gate). BUILT 2026-07-13 (`schematics.mechanism_chain`, both variants render). | Scaffold NOW; `[CAMPAIGN]` fills SQ1 rho, a*b, the cut. | 1 (par 1) + 6 (par 6.5) | **[NOW + CAMPAIGN fill]** |

## Tables (~6)

| # | Title | What it shows | Data source | Chapter | Status |
|---|---|---|---|---|---|
| T1 | Run ledger | Arms × seeds × candidate budget, total candidates/steps, freeze hash, deviation count, realised compute, rejection/divergence counts. | `[CAMPAIGN]` archive + `PREREGISTRATION.md` hash. | 6 (§6.1) | **[CAMPAIGN]** |
| T2 | IUT results | Per-leg one-sided IUT *p* and TOST equivalence bounds for H2-RA and H2-Tail (distributional vs scalar / placebo / scalar_cvar5), plus the FZ0/DM-HLN ES backtest. | `[CAMPAIGN]` archive. | 6 (§6.2) | **[CAMPAIGN]** |
| T3 | Robustness | Delisting band $d\in\{0,-30,-55,-100\}\%$, cost sweep, PBO (CSCV), Deflated-Sharpe cross-check, BAB/QMJ factor attribution. | `[CAMPAIGN]` archive. | 6 (§6.3) | **[CAMPAIGN]** |
| T4 | Secondary hypotheses | H1 (descriptive, both caveats), H3 (TOST-bounded equivalence), H4 (LLM vs random_search / bayes_opt at matched compute). | `[CAMPAIGN]` archive. | 6 (§6.4) | **[CAMPAIGN]** |
| Table 4.1 | Rigour ledger (in-body, CH4 §4.7) | Examiner-facing map of each named threat to validity → the design element that guards it (leakage, self-grading, format confound, overfitting, reward-scale, etc.). | `docs/RIGOUR_LEDGER.md` (static; rendered as the in-body Table 4.1 — the former "T5 / Appendix A — Rigour ledger" plan was consolidated to the in-body table on 2026-07-04). | 4 (§4.7) | **[built]** |
| T5 | Arms specification | The 7 arms and the single manipulated variable (feedback block) per arm: distributional, scalar, placebo, scalar_cvar5, placebo_shuffled, random_search, bayes_opt. | Static from `CH4_methods.md` §4.5. | 4 | **[NOW]** |

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
| `risk_return_clouds` | **NEW (F-D)** | the 7 arms' per-seed (CVaR, Sharpe) clouds collapse onto one neighbourhood — the whole-story null image |
| `evidence_for_null` | **NEW (F-E)** | JZS Bayes-factor gauge (Jeffreys bands) + Model-Confidence-Set membership strip — positive evidence FOR H0 |
| `reward_code_similarity` | **F8 (mechanism)** | AST-distance clustered heatmap + dendrogram + arm sidebar — clusters cut ACROSS arms (the placebo writes the same code) |

The honesty discipline (§6 reporting rules in `CH6_results.md`): plot effect size + interval against the
SESOI band, never a p-value or a bare bar of means; captions must distinguish "equivalent to within ±0.05
DSR" (the claim) from "no effect exists" (not the claim) and "inconclusive". Remaining headline figures to
wire post-campaign (data only): controls raincloud (F7), responsiveness/prompt-leak scatter (F8b), learning
curves (F9). Static `[NOW]` schematics are ENGINE-BUILT (`src/viz/schematics.py`: F1 `system_diagram`,
F2 `prediction_branch`, F4 `splits_timeline`); F4 is rendered to `outputs/figures/`, F1/F2 render pending. F3 stylised facts IS engine-built (`src/viz/eda.py::build_f3`, 2026-07-02; see
the F3 row above) and rendered 2026-07-02 from the ACTIVE **univ5** Split-C train window (excess kurtosis
15.25; empirical/Normal CVaR crossover ×0.84→×1.66; stress co-crash 19.7%).
