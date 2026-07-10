# Chapter 5 — The Prototype: Machinery Validation and Design Hardening

## 5.1 Purpose and status

Before the confirmatory campaign was frozen, a full prototype was run end to end. Its role is that of a *pilot* in
the strict sense: it de-risks the apparatus and informs the design, but it is **not** evidence for or against the
hypotheses. We are explicit about this for two reasons. First, the prototype was single-seed and was analysed by
an estimator that — as the pilot itself revealed — is the wrong inferential unit for the headline hypothesis (§5.3),
so no p-value it produced can bear inferential weight. Second, and more importantly for the credibility of the
pre-registration, the prototype must be shown to have shaped the design through *what it taught about the
machinery*, not through *a signal it appeared to find* — because, read correctly, it found no signal to chase
(§5.3). This chapter therefore reports the pilot honestly as a methodological instrument and catalogues the
hardening it produced.

## 5.2 Configuration and what ran

The prototype instantiated the full pipeline of Chapter 4 at reduced scale: six arms (four language-model arms —
*distributional*, *scalar*, *placebo*, *scalar_cvar5* — plus the two search baselines *random_search* and
*bayes_opt*; the confirmatory study's seventh arm, the structure-shuffled *placebo_shuffled* control, was added
only later in hardening and so did not run in the prototype), the Claude Sonnet 4.6 reward-designer,
a 25,000-step training budget, a single training seed, and the development splits. It ran to completion across all
arms at a matched candidate budget, archived every prompt, authored reward and feedback block, and produced the
full analysis stack (per-arm fitness, reward-program forensics, and the overfitting diagnostics). The headline
engineering outcome is that the apparatus works end to end — the language model authors valid reward code, the
sandbox gates it, the agent trains, the off-critic estimator produces the fed vectors, and the analysis replays
deterministically from the archive. This alone discharged the principal execution risk of the project. The run completed in approximately 17.9 hours
of wall-clock on a single consumer GPU, evaluating some 240 authored candidates across the six arms over eight
reflective generations, at an API cost of about \$3.17.

## 5.3 What the pilot actually showed — and why it is a (weak) null, not a signal

Naively read, the prototype produced an encouraging headline: the distributional arm's realised left tail was
significantly better than the *scalar* arm's (a CVaR-5% difference at $p\approx0.004$). The pilot's central
methodological lesson is that this number is an artefact, in three independent senses, and the design must not — and
did not — be steered by it.

First, the **inference unit is wrong**. The $p\approx0.004$ was computed by a within-path time bootstrap on a
*single* winning reward's return series — its "n" is one strategy's autocorrelated days, carrying only market-path
sampling error. The correct unit for a feedback-channel claim is the *reward population* across seeds, tested by a
paired across-seed bootstrap; the prototype, being single-seed, cannot supply it, and the campaign-grade
re-analysis correctly *skips* every headline leg for want of shared test seeds. Second, the signal **reverses under
control**. Against the zero-information *placebo*, the distributional arm's tail is significantly *worse*
($p\approx0.0005$ in the same analysis output): the winners' CVaR ordering tracks the risk–return frontier
(lower-volatility winners have smaller tails), not tail-information content, and the placebo — the arm fed *no* tail
— has the safest tail of all. The favourable scalar comparison is thus the single arm against which the
distributional winner happened to be lower-volatility, and it evaporates under the proper control. Third, the
**mechanism points the wrong way**: the model's responsiveness — the rank correlation between movements in the fed
tail and changes in the authored reward code — is *negative*, and an interpretability gate intended to detect
tail-aware code is saturated across *all* arms (including the search baselines that are never fed a tail), so it
discriminates nothing.

Read through the theory of Chapter 3, these three facts are coherent and they are the signature of the **Null
branch**: under a tail-blind selector and a non-responsive designer, the dominance envelope is not realised. The
prototype is therefore a *weak null leaning against the hypothesis*, not a promising directional positive — and the
honest consequence is that there was no real signal for the subsequent design to be reverse-engineered toward. This
is the crux of the pre-registration-integrity argument: the confirmatory design was hardened by the *defects* the
pilot exposed, and the sealed test leg was never touched in the process.

Honesty requires going one step further. The *negative* responsiveness is not only an instrument reading to be
discounted for its single-seed, saturated-gate limitations; taken at face value it is a genuine prior *against* the
study's own now-headline mechanism claim — that showing the designer the downside changes the reward code it writes
in a tail-improving direction. A designer whose authored code moves *opposite* the fed tail is, on its face,
evidence that the feedback→code link this dissertation is built to detect may be weak or absent, and we do not
explain it away. Instead the confirmatory design confronts it on its own terms: responsiveness is carried as a
pre-registered, **report-only** mechanism measure on the real confirmatory campaign — never as a directional result read
off the pilot — scored against the fed signal across seeds, with the saturated binary gate replaced by the
quantitative reward-program differential (§5.4). Whether the negative sign is a single-seed artefact or a real
boundary condition on the mechanism is thus left to the powered, sealed-leg analysis of Chapter 6, prejudged in
neither direction.

## 5.4 The hardening: from pilot defects to the frozen design

Each defect the pilot exposed maps to a specific correction carried into the frozen confirmatory design (Chapter 4).

- **Wrong inference unit → per-seed rliable inference.** The single-path bootstrap was replaced by a
  multi-seed design (the winner-seed ladder) with per-seed interquartile-mean reduction and a paired stratified bootstrap over shared seeds, carrying
  the across-seed variance [`agarwal2021rliable`].
- **Double-corrected conjunction → two co-primary intersection–union tests.** The original Benjamini–Hochberg-over-
  a-conjunction headline double-corrected; it was rebuilt as two co-primary IUTs (risk-adjusted and tail), each its
  own multiplicity correction, with the BH-over-six demoted to a sensitivity.
- **No format control → the structure-shuffled arm.** Because the favourable comparison turned out to be confounded
  with the risk–return frontier and there was no control isolating *information* from *format*, a structure-shuffled
  placebo (identical block, deranged values) was added as a disjoint control.
- **Prompt leakage → de-seeded prompts.** A forensic pass found the shared base prompt named "tail" and "CVaR", so
  every arm — including the placebo — wrote tail-aware code, collapsing the manipulation; the tail vocabulary was
  removed from all shared prompt sources so that only the distributional arm's *feedback* introduces the tail.
- **Fabricated tail mass → the conservative headline panel.** The survivorship-corrected panel was found to
  surcharge M&A exits indiscriminately; the headline was reverted to the conservative zero-fill panel, with the
  surcharge retained only as the heavy end of a disclosed sensitivity band (Chapter 4, §4.2).
- **Critic instability → uniform value-target normalisation.** Late critic-loss explosions in a minority of
  candidate trainings motivated a PopArt normaliser applied uniformly across arms; the normaliser preserves the
  realised-return series byte-identically (a tested code invariant), and a disabled-ablation of the frozen
  campaign winners is reported in Chapter 6 [`vanhasselt2016popart`].
- **Saturated interpretability gate → a quantitative reward-program differential.** The binary tail-usage gate that
  discriminated nothing was replaced by a regret-bounded reward-distance characterisation (EPIC/STARC) and a
  responsiveness measure scored against the *fed* signal, both reported as directional mechanism evidence
  [`gleave2021epic`; `skalse2024starc`].

The amendments were recorded against the pre-registration before the freeze, and the design was then frozen by a
cryptographic hash (Chapter 4, §4.8).

## 5.5 What the prototype establishes

The prototype establishes two things and disclaims a third. It establishes that the end-to-end machinery is
correct and reproducible, discharging execution risk. It establishes — through the defects it exposed — the
hardened, frozen design on which the confirmatory campaign runs, with a documented, integrity-preserving trail from
each defect to its correction. It disclaims any inferential reading of its own numbers: the prototype's directional
pattern is a single-seed, wrong-unit, control-reversed null, and the dissertation's empirical claims rest entirely
on the per-seed, sealed-leg, pre-registered confirmatory analysis of Chapter 6. That the directional pattern is a
null *consistent with the theory's prediction* is noted as corroboration of the mechanism account, not as evidence;
the confirmatory campaign is what tests it at power.
