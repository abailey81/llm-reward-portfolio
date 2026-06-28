# Examiner objections & defences (deep-research, adversarially verified, 2026-06-28)

Source: two `deep-research` workflows (run `wf_3e5ea496-4d7` novelty/citations; `wf_09d241fb-b79` examiner
red-team) — each a 99–105-agent fan-out with 3-vote adversarial verification (a claim needs 2/3 refutes to
die). This doc arms the Discussion/Limitations chapters. **Verified** = survived 3-0/2-1 against primary
sources; **UNVERIFIED** = fetched but below the verify-budget, or not researched — resolve before citing.
Every citation here is to be cross-checked against `paper/refs.bib` before it enters the PDF.

> **One framing decision needs your (and ideally the supervisor's) ratification — see §1c. Do not let me
> silently rewrite the pre-registration's epistemic framing; it is freeze-relevant prose.**

---

## TOP 5 objections most likely to cost marks (ranked) + the single best mitigation each

1. **EVT/GPD tail estimate is small-sample-fragile at CVaR-5%/1%** (~7–37 exceedances on ~750 obs, below the
   ~50–100 reliability standard). → *Mitigation:* disclose it prominently as a primary limitation, report the
   cross-threshold spread diagnostic you already ship (`measurement.py::threshold_sensitivity`), and frame the
   EVT gain as *relative to crude empirical quantiles*, not absolute precision. [VERIFIED — Belzile & Davison
   2022; McNeil & Frey 2000]
2. **"Corroborated Popperian prediction" is the wrong epistemic basis for the null.** → *Mitigation:* reframe
   credit on **Mayoian/error-statistical severity** (licensed precisely by your *frozen, deviation-free*
   cryptographic protocol) + **garden-of-forking-paths avoidance**, not Popperian corroboration. [VERIFIED —
   Rubin 2025; Gelman & Loken 2014] **(§1c — needs ratification)**
3. **A bare non-significant result is not evidence for the null.** → *Mitigation:* lead the headline with the
   **TOST/equivalence** result against the pre-registered SESOI (which you already implement: `sesoi`,
   `equivalence_margin`, `h2_tost_dsr`), never with `p>0.05`. [VERIFIED — Lakens-Scheel-Isager 2018;
   Campbell-Gustafson 2018]
4. **Endogeneity: the fed tail is fitted on the policy's own returns.** → *Mitigation:* keep the honest
   "two coupled reward→policy→measurement loops" framing (already in `measurement.py`); do **not** invoke
   potential-based-shaping invariance unless the authored reward is potential-based (it is not). [VERIFIED —
   Ng-Harada-Russell 1999]
5. **Single-LLM-family + single-market external validity.** → *Mitigation:* scope every claim to "a single
   Claude family on one survivorship-free equity panel"; present multi-model/multi-market as Future Work.
   [UNVERIFIED in this run — standard expectation; resolve a citation]

---

## §1 — Publishing/grading a pre-registered NULL

**(1a) A pre-registered null IS creditable in ML.** [VERIFIED 3-0] NeurIPS 2020/2021 pre-registration
workshop (PMLR v148/v181, Bertinetto-Henriques-Albanie-Paganini-Varol): reviewers "assess … the quality of
the experimental design, rather than comparing numeric results"; "Some results will be negative, and this is
welcomed." → Your design's credit derives from design quality + countering the file-drawer problem.

**(1b) Convert the null to POSITIVE evidence via equivalence testing.** [VERIFIED 3-0] NHST alone "cannot
provide evidence in favour of the null" (Campbell & Gustafson 2018, PLOS ONE). Use TOST against a
pre-specified SESOI (Lakens, Scheel & Isager 2018, AMPPS) — SESOI must be fixed before seeing data. *You
already implement this* (`inference.sesoi=0.05`, `equivalence_margin`, `h2_tost_dsr`). Lead with it.

**(1c) ⚠ The "corroborated Popperian prediction" framing is philosophically mis-scoped.** [VERIFIED 3-0]
Rubin (2025, *Synthese* 206:111; arXiv:2408.12347): "preregistration does not improve the transparent
evaluation of severity (a) in Popper's philosophy of science or (b) in Mayo's approach when deviations are
allowed." → **Recommended reframe:** claim severity on **Mayoian/error-statistical** grounds — which your
*frozen, deviation-free* freeze-hash protocol genuinely supports (no sample-based deviations ⇒ no unknown
Type-I inflation) — and on **forking-paths** grounds (Gelman & Loken 2014: multiple-comparisons invalidity
arises *without* conscious p-hacking). **DECIDED (2026-06-28): adopt Mayoian framing.** (Was: a
write-up/PREREGISTRATION framing change flagged for decision; now ratified for the document — the change is
editorial, the TOST/SESOI machinery already implements it.)

**(1d) Forking-paths + the single-panel caveat.** [VERIFIED 3-0, one 2-1] Gelman & Loken justify
pre-registering the *whole* analysis plan. CAVEAT: a single-panel finance study cannot run an independent
confirmatory replication on fresh data, so you hold only the weaker prereg-only variant — *disclose this*,
and present your walk-forward / CPCV-on-winners / block-bootstrap as the strongest available confirmatory
substitute.

## §2 — EVT/GPD CVaR at small samples (the top technical objection)

**(2a) OBJECTION [VERIFIED 3-0]:** EVT/GPD peaks-over-threshold inference "can be badly biased" at
small/moderate samples (Belzile & **Davison** 2022, *Annals of Applied Statistics* 16(3); note: NOT
"Belzile-Neslehova"). At ~750 obs with α≤0.05 the tail holds only ~7–37 exceedances — below the ~50–100
reliability standard. **This is the single most grade-relevant unmitigated weakness at CVaR-1%/5%.**

**(2b) DEFENCE [VERIFIED 3-0]:** EVT/GPD POT remains best practice over empirical quantiles at small samples
(empirical extreme quantiles are high-variance and cannot extrapolate); McNeil & Frey (2000, *J. Empirical
Finance* 7:271–300) validated it at n=1000 (~the dissertation's order of magnitude) with k=100 exceedances
chosen by an MSE bias/variance analysis. **CRITICAL CAVEAT:** M&F fit the GPD to ~100 exceedances of
*pre-whitened AR(1)-GARCH residuals*, not raw returns. You fit raw policy returns → the *window-size*
precedent transfers, but absolute tail precision at the deepest levels does not. **Disclose the
GARCH-filtering distinction explicitly.**

**(2c) REQUIREMENT [VERIFIED 3-0]:** threshold/k selection is the central sensitivity (Scarrott & MacDonald
2012, *REVSTAT* 10(1)); best practice *propagates* threshold/estimation uncertainty into downstream tail
inferences. Your fed CVaR block currently feeds *point* estimates plus a cross-threshold *spread* diagnostic
(`threshold_sensitivity`) — present that spread as the honest substitute and list full uncertainty-propagation
(intervals in the fed block) as Future Work. Giles et al. analytic O(n⁻¹) GPD-MLE bias-correction exists but
presupposes a stable MLE (often unavailable at α=0.01). **[REFUTED 0-3: do NOT claim analytic bias-correction
is substantially superior to bootstrap.]**

## §3 — Endogeneity of the fed tail (fitted on the policy's own returns)

[VERIFIED 3-0] Ng, Harada & Russell (1999, ICML): potential-based shaping `F=γΦ(s')−Φ(s)` preserves the
optimal policy and is a *necessary* condition for invariance — *any* non-potential-based transform may yield
suboptimal policies. → **You cannot invoke this invariance** unless the LLM-authored reward is itself
potential-based (it generally is not). The defensible framing is the one you already use in
`measurement.py`: H2 compares **two coupled reward→policy→measurement loops** (scalar-fed vs tail-fed), not an
exogenous risk measurement. Keep it; do not over-claim invariance.

## §4–§7 — UNVERIFIED in this run (sources fetched, claims below verify-budget — resolve before citing)
- **(4) SAC convergence / undertraining:** Henderson et al. 2018 "Deep RL That Matters" (arXiv:**1709.06560**
  — note the earlier internal mis-id 1710.01771), Agarwal et al. 2021 rliable (arXiv:2108.13264), SAC
  (Haarnoja 1801.01290 / 1812.05905). Standard demand: show *learning curves to convergence*, not a single
  end-point; report stratified bootstrap CIs / IQM (rliable). *Open: is the agent trained to convergence?*
- **(5) Reward hacking / Goodhart:** specification-gaming literature (Krakovna et al.) — UNVERIFIED here;
  relevant mitigation is your sandbox + the held-out validation selection.
- **(6) Single-LLM-family external validity:** standard expectation is a multi-model panel; scope claims to
  the single Claude family. UNVERIFIED citation.
- **(7) Single-market external validity + backtest overfitting / survivorship / PIT:** Bailey & López de
  Prado (deflated Sharpe / PBO; `deflated-sharpe.pdf` fetched), FinRL data-integrity pitfalls (NeurIPS D&B).
  UNVERIFIED in this run; you already implement DSR + PBO/CSCV + survivorship-free PIT panel.

## Implementation cross-checks the defence depends on (verify against the repo before asserting)
1. Headline reports **TOST equivalence vs the pre-registered SESOI**, not bare p>0.05. ✔ machinery present
   (`h2_tost_dsr`).
2. Fed CVaR block ships the **threshold-sensitivity spread** diagnostic. ✔ (`measurement.py::threshold_sensitivity`).
3. Endogeneity disclosed as **coupled loops**, no agent-independent claim. ✔ (`measurement.py` docstring).
4. **EVT raw-returns vs GARCH-residual** distinction disclosed in the methods/limitations. ✖ → ADD.
5. Epistemic framing = **Mayoian severity + forking-paths**, not Popperian corroboration. ✖ → DECISION (§1c).

> Anything marked UNVERIFIED must not enter `refs.bib` as confirmed. Items 4–5 above are write-up actions
> for you to ratify, not silent edits.
