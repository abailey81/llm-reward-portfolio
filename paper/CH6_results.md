# Chapter 6 — Results

## Reporting rules (apply throughout this chapter)

These rules are pre-committed and govern every result statement below:

1. **Present every null as a bounded equivalence with a confidence interval — never as "p > 0.05".** A
   non-rejection is reported as a TOST equivalence against the pre-registered ±0.05-DSR SESOI, with the
   equivalence bound stated; "inconclusive" is reserved for the case where the bound is wider than the SESOI.
2. **Lead with TOST.** For each co-primary leg, state the equivalence result *first* (the bound vs the SESOI),
   and only then the one-sided IUT *p*-value. The equivalence is the headline; the IUT is the confirmatory check.
3. **Show controls visually.** The placebo and placebo_shuffled controls are presented as an overlay on the same
   axes as the manipulated arm, so that a reader sees the null/effect against its own controls, not in a separate
   table.
4. **A null with a mechanism is a finding.** A confirmed null is reported as a corroborated §3.7 prediction and is
   always accompanied by the §6.5 mechanism evidence (responsiveness, reward-code differential, reward-distance),
   never as a bare absence of effect.
5. **Rung-freshness tagging (v2 convention — machine-checked).** Every campaign-derived number, when filled,
   carries an invisible freshness tag: numbers computed on the E1 core ladder append `<!--RUNG:n-->` (n = the
   rung the number was computed at); replication-leg numbers append `<!--LEG-TIER:30-->` (legs run at the
   floor tier by design and never refresh on the ladder). `scripts/check_rung_freshness.py --achieved N`
   fails on any core tag whose rung ≠ the achieved rung (a stale number surviving a rung refresh);
   `--final` additionally fails on any remaining unfilled `[FROM CAMPAIGN…]` slot. While the ladder climbs,
   interim drafts are labelled provisional at the chapter head; the single confirmatory look is unaffected
   (the tags govern prose freshness, never data collection).

---

## 6.1 Campaign execution and integrity

This section establishes that the reported campaign is the frozen, pre-registered one and that it ran without
material deviation, before any inferential result is shown. It presents the run ledger (arms × seeds × candidate
budget), confirms the freeze hash matches the pre-registration, and reports the count and disposition of any
logged deviations. It also records the realised compute, the per-candidate PopArt normalisation-scale range, and
the count of critic-divergence / candidate-rejection events, so the reader can judge execution adequacy before
interpreting effects.

- Frozen design hash (must match `PREREGISTRATION.md`): `[FROM CAMPAIGN: freeze SHA-256]`.
- Arms run: **7** (distributional, scalar, placebo, scalar_cvar5, placebo_shuffled, random_search, bayes_opt);
  seeds per arm: `[FROM CAMPAIGN: n_seeds; E1 ladder [30,100,189,279,340,403,568], primary target 403, stopping tier reached]`; candidate budget per arm: `[FROM CAMPAIGN: 30 = 6 gen × 5]`.
- Total candidates evaluated: `[FROM CAMPAIGN: N]`; total environment steps: `[FROM CAMPAIGN: N × 400,000]`.
- Logged deviations (append-only log): `[FROM CAMPAIGN: count]`; disposition: `[FROM CAMPAIGN: summary]`.
- Realised wall-clock / cost: `[FROM CAMPAIGN: hours / $]`; serial-parallel byte-equivalence: `[FROM CAMPAIGN: confirmed?]`.
- Untrusted-code screen rejections: `[FROM CAMPAIGN: count]`; critic-divergence events: `[FROM CAMPAIGN: count]`.
- **E1 achieved rung + realised power (v2 slot):** rung reached at the bank gate `[FROM CAMPAIGN: rung of
  [30,100,189,279,340,403,568]]`; assurance at that rung `[FROM CAMPAIGN: %]`; the rung-100 σ_D re-estimate at
  B\* = 400k `[FROM CAMPAIGN: σ_D; vs the 200k pilot value]`. Every §6.2–§6.6 number is tagged `RUNG:` at this
  achieved rung (reporting rule 5); leg numbers (§6.7–§6.8) are `LEG-TIER:30` by design.
- Replication-leg execution (v2): legs completed by the 2026-08-14T23:59Z calendar gate `[FROM CAMPAIGN: k of
  9 + the truncated-by-calendar list, in queue order]`; per-leg bank-gate verdicts `[FROM CAMPAIGN: pass
  list]`; realised total LLM spend vs the $30 advisory ceiling (R83) `[FROM CAMPAIGN: $ per provider, summed]`.

*Table 6.1 (run ledger) — see `FIGURE_TABLE_MANIFEST.md` T1.*

## 6.2 Primary result — the two co-primary H2 IUTs (equivalence-first)

This is the headline. Following the reporting rules, each co-primary intersection–union test is presented
equivalence-first: the TOST bound against the ±0.05-DSR SESOI, then the one-sided IUT *p* per leg. **H2-RA**
(risk-adjusted, Sharpe contrast) and **H2-Tail** (left tail, CVaR-5% contrast) are each an IUT over three legs —
distributional vs *scalar*, *placebo* and *scalar_cvar5* — one-sided at α = 0.05. The section leads with the
`rliable` IQM interval figure (headline interval, per-seed, stratified-bootstrap) and the TOST equivalence figure,
then tabulates the per-leg statistics.

**H2-RA (Sharpe legs).**

- TOST equivalence vs ±0.05 SESOI: `[FROM CAMPAIGN: 90% CI / equivalence bound in DSR units]` →
  `[FROM CAMPAIGN: EQUIVALENT / INCONCLUSIVE / NON-EQUIVALENT]`.
- One-sided IUT *p* (max over legs): `[FROM CAMPAIGN: p]`; per-leg *p*: scalar `[FROM CAMPAIGN]`,
  placebo `[FROM CAMPAIGN]`, scalar_cvar5 `[FROM CAMPAIGN]`.

**H2-Tail (CVaR-5% legs).**

- TOST equivalence vs ±0.05 SESOI: `[FROM CAMPAIGN: 90% CI / equivalence bound]` →
  `[FROM CAMPAIGN: EQUIVALENT / INCONCLUSIVE / NON-EQUIVALENT]`.
- One-sided IUT *p* (max over legs): `[FROM CAMPAIGN: p]`; per-leg *p*: scalar `[FROM CAMPAIGN]`,
  placebo `[FROM CAMPAIGN]`, scalar_cvar5 `[FROM CAMPAIGN]`.
- Corroborating FZ0 / DM-HLN Expected-Shortfall backtest: `[FROM CAMPAIGN: DM stat, p, with size/power caveat]`; loss-differential Hill tail-index (B.5.2 heavy-tail size check): `[FROM CAMPAIGN: hill_alpha, flag]`.

*Figure 6.1 (rliable IQM headline interval) — manifest F5; Figure 6.2 (TOST equivalence) — manifest F6;
Table 6.2 (IUT per-leg results) — manifest T2.*

## 6.3 Controls and robustness

This section defends the primary result against construct-validity and specification threats, shown visually per
the reporting rules. The placebo (receiving-any-feedback confound) and placebo_shuffled (format-vs-information
confound, a **disjoint** control, not a fourth IUT leg) are overlaid on the same axes as the manipulated arm.
Robustness sweeps follow: the delisting-return band $d\in\{0,-30,-55,-100\}\%$, a transaction-cost sweep, and the
overfitting guards (PBO via CSCV, with the Deflated-Sharpe cross-check). The pre-registered BAB/QMJ factor
attribution rules out a low-volatility-beta explanation of any headline.

- Placebo overlay: `[FROM CAMPAIGN: placebo tail/Sharpe vs distributional]`; placebo_shuffled overlay:
  `[FROM CAMPAIGN: shuffled tail/Sharpe vs distributional]` (format artefact ruled `[in/out]`).
- Delisting band sensitivity: pooled test CVaR-5% moves by `[FROM CAMPAIGN: ~pp]` across the band; hypothesis
  ordering `[FROM CAMPAIGN: invariant?]`.
- Cost sweep: `[FROM CAMPAIGN: ordering across cost levels]`.
- PBO (CSCV): `[FROM CAMPAIGN: probability]`; Deflated-Sharpe cross-check: `[FROM CAMPAIGN: value]`.
- Factor attribution (CAPM→6-factor + BAB/QMJ, Newey–West): `[FROM CAMPAIGN: alphas/loadings]`.
- Regime-conditional analysis (calm/normal/stress VIX strata on the median-tail-seed realized path,
  promised in §1.6/§3.7): `[FROM CAMPAIGN: per-regime CVaR-5%/Sharpe by arm; episode-count power bound]`.
- Synthetic-null falsification (the identical inference stack on shuffled labels must return null):
  `[FROM CAMPAIGN: null-calibration verdict]`.
- Model-Confidence-Set membership + the triangulated Bayesian null evidence (JZS BF, ROPE):
  `[FROM CAMPAIGN: MCS members at 90%; BF01; ROPE mass]` — Figures 6.4–6.5 (manifest F-D/F-E).

*Figure 6.3 (controls overlay) — manifest F7; Figure 6.4 (per-seed risk–return clouds) — manifest F-D;
Figure 6.5 (Bayesian null-evidence gauge, MCS membership) — manifest F-E; Table 6.3 (robustness) — manifest T3.*

## 6.4 Secondary hypotheses

This section reports H1, H3 and H4, each scoped exactly as pre-registered.

**H1 — beat-the-human (descriptive only).** Whether the best LLM reward beats the maximum over four hand-designed
rewards on the sealed leg. We report this in the Eureka "beat-the-human-baseline" tradition, but it carries a
**data-snooping bias that we make explicit and refuse to launder into an inferential claim**, for two reasons
that push in *opposite* directions:

- *(i) Comparator selection on the sealed leg (anti-conservative for the baseline).* The comparator is the
  **maximum** over four hand-designed rewards evaluated on the very leg it is then reported on. Taking a maximum
  over several candidates on the test sample inflates the comparator's apparent performance by the usual
  selection (multiple-comparisons) mechanism — it borrows the most favourable test-set noise. This biases the
  comparison **against** our H1 claim (it makes the human baseline look better than a held-out estimate would),
  so it is *conservative* for "the LLM beats the human" and *anti-conservative* for the baseline itself.
- *(ii) Un-tuned baselines (favourable to our claim).* The hand-designed rewards are fixed, un-tuned reference
  specifications, not the output of a matched hyper-parameter search; any gap is therefore **not** a like-for-like
  optimisation comparison, and this bias runs the *other* way — it flatters the LLM.

Because these two biases are of unknown relative magnitude, the **net sign is unidentified**, and H1 is therefore
reported as a **descriptive observation only**: it is excluded from the frozen `m=6` multiplicity family, never
enters any TOST/IUT decision, and no *p*-value is attached to it. It is context for the headline mechanism result,
not evidence for it. (The clean, pre-registered, inference-bearing comparisons are H2/H3/H4, which select on the
validation leg and are scored once on the sealed leg.)

- `[FROM CAMPAIGN: best-LLM vs max-baseline on sealed leg, descriptive — gap and direction only, no test]`.

**H3 — reflection vs single-shot (TOST-bounded equivalence).** Whether iterative reflection beats single-shot
best-of-N at matched budget; reported as a TOST-bounded equivalence against the SESOI, not as a bare *p*.

- TOST equivalence: `[FROM CAMPAIGN: bound vs SESOI]` → `[FROM CAMPAIGN: EQUIVALENT / INCONCLUSIVE / NON-EQ]`.

**H4 — LLM vs random-search / bayes-opt (matched compute).** Whether the LLM designer beats the random-search and
Gaussian-process expected-improvement baselines at the matched 30-candidate budget.

- `[FROM CAMPAIGN: LLM vs random_search]`; `[FROM CAMPAIGN: LLM vs bayes_opt]`.

*Table 6.4 (secondary hypotheses) — manifest T4.*

## 6.5 Mechanism

This section supplies the mechanism that turns a null into a finding (reporting rule 4). It estimates
**responsiveness** — the change in the authored reward code as a function of the change in the fed tail signal
(the mediation/indirect-effect quantity of §3.7 [`imai2010identification`; `mackinnon2000equivalence`]) — and
reports its sign. It quantifies the **reward-program
differential** across arms with the EPIC/STARC reward pseudometrics (do tail-fed arms author measurably different
reward code?). Finally it presents the **learning-curve / training-budget diagnostic**, disclosing the budget verdict
at the 400,000-step budget and interpreting all arm differences as differences *at a fixed, matched budget*.
Figure 6.6 renders the paper's three-link chain — fed tail signal → authored reward code → trained policy →
realised tail — as a single spine, with the cut glyph marking the link the evidence severs.

- Responsiveness (fed-tail change → authored-reward change): `[FROM CAMPAIGN: estimate, sign, CI]`.
- Mediation (fed → code → realized tail; a·b indirect effect): `[FROM CAMPAIGN: a, b, indirect, CI]`.
- §2a(f) fingerprint rows (per-arm responsiveness incl. the scalar arm's own-scalar row — the A4
  discriminator — and the placebo_shuffled floor): `[FROM CAMPAIGN: table]`.
- Reward-program differential (EPIC/STARC distances between arms): `[FROM CAMPAIGN: distances]`;
  prompt-leak fingerprint / tail-construct count by arm: `[FROM CAMPAIGN: counts]`.
- Learning-curve / training-budget diagnostic: `[FROM CAMPAIGN: critic-loss trajectory, budget verdict, extended-ladder verdict]`.
  The measured per-seed validation-DSR-versus-budget curve, with $B^\*$ marked at the empirical knee, is shown in
  Figure 6.9 (manifest F11, the R77-mandatory budget exhibit).

*Figure 6.6 (three-link mechanism chain) — manifest F10; Figure 6.7 (mechanism / responsiveness) — manifest F8;
Figure 6.8 (learning curves) — manifest F9; Figure 6.9 (measured training-budget curve, R77) — manifest F11.*

## 6.6 Summary against the §3.7 prediction table

This closing section maps the realised results onto the three pre-registered mechanism branches (Strict / Weak /
Null) of the Chapter 3 §3.7 table, stating which branch the evidence corroborates and why. The verdict is read off
the conjunction of the four signature columns — H2-RA (Sharpe), H2-Tail (CVaR-5%), responsiveness sign, and the
reward-code differential — exactly as pre-registered (Table 6.5), so the outcome is a *decided prediction* of either
sign rather than a bare measurement.

| §3.7 signature | Pre-registered prediction (Null branch) | Realised | Branch corroborated |
|---|---|---|---|
| H2-RA (Sharpe legs) | tie (equivalence) | `[FROM CAMPAIGN]` | `[FROM CAMPAIGN]` |
| H2-Tail (CVaR-5% legs) | tie (equivalence) | `[FROM CAMPAIGN]` | `[FROM CAMPAIGN]` |
| Responsiveness | $\le 0$ | `[FROM CAMPAIGN]` | `[FROM CAMPAIGN]` |
| Reward-code differential | none / reversed | `[FROM CAMPAIGN]` | `[FROM CAMPAIGN]` |

*Table 6.5 — Realised results mapped onto the §3.7 pre-registered prediction branches (Strict / Weak / Null); the
corroborated branch is read off the conjunction of the four signature columns, as pre-registered.*

Verdict: `[FROM CAMPAIGN: Strict / Weak / Null branch corroborated]`, with `[FROM CAMPAIGN: one-line theory-tied
interpretation per §3.7]`.

## 6.7 The model replication suite (v2 — report-only)

Nine further models author the identical five LLM arms under byte-identical prompts at the 30-seed floor tier
(R80/R82): the executed roster, pins (provider / quantization / reasoning mode / output caps), queue order and
the 2026-08-14T23:59Z calendar gate are frozen in `model_suite`. **Nothing in this section or §6.8 gates
H1–H4** — the suite is the registered external-validity and capability-gradient instrument wrapped around the
confirmatory core, and every number here is floor-tier by design (`LEG-TIER:30`; claims are calibrated to
floor power and stated as such). Each leg's archive passed the same write→verify bank gate as the campaign
root before its numbers entered any table.

- Legs completed vs truncated-by-calendar (queue order): `[FROM CAMPAIGN: k of 9; truncated list]`; the
  DeepSeek contamination-gate disposition (pass, or GLM-5.2 absorbed seat 1 as pre-declared):
  `[FROM CAMPAIGN: verdict + archived screen pointer]`.
- Per-leg headline contrasts (distributional − scalar, CVaR-5% and Sharpe, floor-30, 90% CI): Table 6.6
  `[FROM CAMPAIGN]`.
- T0-floor inclusion (the registered leg-inclusion criterion): included `[FROM CAMPAIGN: list]`; excluded as
  authoring/search failures — **a finding, never a vote** — `[FROM CAMPAIGN: list + failure mode]`.
- Authoring reliability (Table 6.7, the practitioner-facing table): pre-launch format-compliance baseline,
  sandbox pass rate, contract-violation taxonomy, refusal/truncation rates, code diversity, and the per-model
  reward-program taxonomy: `[FROM CAMPAIGN: per-model rows]`. **Fairness note (binding on the table and
  Figure 6.12): per-leg registered output caps differ (2,048 tokens for gpt-5.6-luna and gemini-3.5-flash vs
  4,096 elsewhere, R82) — truncation rates are conditional on each leg's cap and the caps are annotated in
  the table, so a capped model is never misread as an unreliable one.**
- The ten winners side-by-side (one annotated winning reward program per model, tail-constructs highlighted):
  Figure 6.13 `[FROM CAMPAIGN]` — the qualitative exhibit of *what different model families write*.

*Figure 6.10 (cross-leg forest) — manifest F12; Figure 6.12 (authoring-reliability heatmap) — manifest F14;
Figure 6.13 (ten-winners annotated code exhibit) — manifest F15; Table 6.6 (per-leg contrasts) — manifest T6;
Table 6.7 (authoring reliability) — manifest T7.*

## 6.8 Cross-model synthesis and the capability gradient (v2 — report-only)

The legs share the market panel and the CRN seed set *by design* (pairing), so they are not independent
replications and are never counted as if they were (the registered dependence discipline). The synthesis has
two tiers — a descriptive count and a dependence-honest permutation test — plus the two registered
capability instruments. Any starred statement in this section survives BH across the nine-leg report-only
family.

- Descriptive replication count (CVaR-leg contrast, T0-filtered — the Sharpe leg is predicted-tie for every
  model and is not counted): `[FROM CAMPAIGN: k dist-safer of n included]`.
- The per-seed joint-flip permutation test (statistic = the POOLED MEAN difference; 10,000 reps, one-sided
  toward dist-safer; shared-seed/panel dependence inside the null): observed pooled mean
  `[FROM CAMPAIGN]`; *p* `[FROM CAMPAIGN]`.
- **The bounded-effect statement (R86 — the synthesis's equivalence-first tier):** the 90% seed-block-bootstrap
  CI on the pooled mean CVaR-5% difference: `[FROM CAMPAIGN: CI in daily-return units]`, i.e.
  `[FROM CAMPAIGN: CI as % of the scalar-arm pooled CVaR level]` — *"across the included models the pooled
  content effect on the realized tail is bounded within this interval."*
- The three-signature gradient adjudication (R87: capacity = rising / representational = flat-at-zero, the
  registered prediction / echo = decreasing): `[FROM CAMPAIGN: signature corroborated + the A1–A5
  fingerprint read]`; the ex-ante sonnet-bridge direction (≤ 0, the pilot's direction):
  `[FROM CAMPAIGN: replicated?]`.
- Family-pair difference-in-differences (the content-effect × capability interaction, common floor-30 CRN
  seeds, seed-paired 90% bootstrap CI): open pair (Qwen 27B − 9B) `[FROM CAMPAIGN: estimate, CI]`; closed
  pair (Opus − Haiku, Opus restricted to its first 30 shared seeds) `[FROM CAMPAIGN: estimate, CI]`;
  **the generation pair (R90: Sonnet 5 − Sonnet 4.6, same vendor and tier, one generation apart —
  the content-effect × generation interaction; tokenizer change disclosed as a covariate)**
  `[FROM CAMPAIGN: estimate, CI]` `[+ the conditional Opus 4.8 − Opus 5 pair if R91's rule fired]`.
- Capability regression (registered primary = the pre-declared external composite anchor; M2 reading score
  secondary): Spearman ρ `[FROM CAMPAIGN: ρ, n legs, p]`; the registered monotone-non-decreasing gradient
  prediction `[FROM CAMPAIGN: corroborated / not]`.
- Generation-indexed responsiveness (does feedback-use strengthen across the loop's six generations?):
  per-generation SQ1 + trend Spearman `[FROM CAMPAIGN]`.

The suite traces the envelope–realization gap $g(\text{capability})$ — the Blackwell envelope of Chapter 3
binds every author; the legs measure the realized distance to it along the capability axis, with the numeracy
bottleneck as the registered hypothesized shape (the interpretation is developed in §7). Whatever this
section shows, it cannot alter the §6.6 confirmatory verdict: the suite refines *where* the mechanism story
generalises, not *whether* the pre-registered result stands.

*Figure 6.11 (capability-gradient scatter) — manifest F13.*
