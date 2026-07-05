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
  seeds per arm: `[FROM CAMPAIGN: n_seeds, target 30]`; candidate budget per arm: `[FROM CAMPAIGN: 30 = 6 gen × 5]`.
- Total candidates evaluated: `[FROM CAMPAIGN: N]`; total environment steps: `[FROM CAMPAIGN: N × 200,000]`.
- Logged deviations (append-only log): `[FROM CAMPAIGN: count]`; disposition: `[FROM CAMPAIGN: summary]`.
- Realised wall-clock / cost: `[FROM CAMPAIGN: hours / $]`; serial-parallel byte-equivalence: `[FROM CAMPAIGN: confirmed?]`.
- Untrusted-code screen rejections: `[FROM CAMPAIGN: count]`; critic-divergence events: `[FROM CAMPAIGN: count]`.

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
- Corroborating FZ0 / DM-HLN Expected-Shortfall backtest: `[FROM CAMPAIGN: DM stat, p, with size/power caveat]`.

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

*Figure 6.3 (controls overlay) — manifest F7; Table 6.3 (robustness) — manifest T3.*

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
reward code?). Finally it presents the **learning-curve / convergence diagnostic**, disclosing training adequacy
at the 200,000-step budget and interpreting all arm differences as differences *at a fixed, matched budget*.

- Responsiveness (fed-tail change → authored-reward change): `[FROM CAMPAIGN: estimate, sign, CI]`.
- Reward-program differential (EPIC/STARC distances between arms): `[FROM CAMPAIGN: distances]`;
  prompt-leak fingerprint / tail-construct count by arm: `[FROM CAMPAIGN: counts]`.
- Learning-curve / convergence diagnostic: `[FROM CAMPAIGN: critic-loss trajectory, convergence verdict]`.

*Figure 6.4 (mechanism / responsiveness) — manifest F8; Figure 6.5 (learning curves) — manifest F9.*

## 6.6 Summary against the §3.7 prediction table

This closing section maps the realised results onto the three pre-registered mechanism branches (Strict / Weak /
Null) of the Chapter 3 §3.7 table, stating which branch the evidence corroborates and why. The verdict is read off
the conjunction of the four signature columns — H2-RA (Sharpe), H2-Tail (CVaR-5%), responsiveness sign, and the
reward-code differential — exactly as pre-registered, so the outcome is a *decided prediction* of either sign
rather than a bare measurement.

| §3.7 signature | Pre-registered prediction (Null branch) | Realised | Branch corroborated |
|---|---|---|---|
| H2-RA (Sharpe legs) | tie (equivalence) | `[FROM CAMPAIGN]` | `[FROM CAMPAIGN]` |
| H2-Tail (CVaR-5% legs) | tie (equivalence) | `[FROM CAMPAIGN]` | `[FROM CAMPAIGN]` |
| Responsiveness | $\le 0$ | `[FROM CAMPAIGN]` | `[FROM CAMPAIGN]` |
| Reward-code differential | none / reversed | `[FROM CAMPAIGN]` | `[FROM CAMPAIGN]` |

Verdict: `[FROM CAMPAIGN: Strict / Weak / Null branch corroborated]`, with `[FROM CAMPAIGN: one-line theory-tied
interpretation per §3.7]`.
