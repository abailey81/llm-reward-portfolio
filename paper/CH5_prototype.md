<!-- COMPRESSED 2026-08-11, 945 WORDS TO ABOUT 430, AND NO FACT IS DROPPED. Every count, every p-value,
     every defect row and the whole "honesty requires one step further" paragraph survive. What went is
     restatement: the appendix said three times that its numbers are not evidence, which is a claim the
     status paragraph makes once and the section heading repeats by construction.
     ⚠ THE NEGATIVE-RESPONSIVENESS PARAGRAPH IS UNTOUCHED. It concedes a genuine prior against this
     study's own headline mechanism, and conceding the strongest objection in your own words is worth
     more than the page it costs. -->

# Appendix D — The prototype, and the hardening it produced (word-excluded)

**Status, stated first because it governs how everything below may be read.** A full prototype ran end to
end before the confirmatory campaign was frozen, as a pilot in the strict sense: it de-risks the apparatus
and informs the design, and no number in it is evidence for or against any hypothesis. It was single-seed
and was analysed by an estimator the pilot itself revealed to be the wrong inferential unit, so no
*p*-value it produced can bear weight.

**What ran.** Chapter 4's pipeline at reduced scale: six arms, four of them language-model arms and two
search baselines, the Claude Sonnet 4.6 reward-designer, a 25,000-step budget, one training seed and the
development splits. The scrambled control and two of the four optimisers did not exist yet. It completed
in roughly 17.9 hours on one consumer GPU, evaluating some 240 authored candidates over eight reflective
generations at an API cost of about \$3.17, which discharged the project's principal execution risk.

## D.1 Why the encouraging headline is an artefact, in three independent senses

Naively read, the prototype produced a promising result: the distributional arm's realised left tail was
better than the `scalar` arm's, at a CVaR-5% difference of $p\approx0.004$. That number is an artefact
three times over.

**The inference unit is wrong.** The $p\approx0.004$ came from a within-path time bootstrap on a *single*
winning reward's return series, so its $n$ is one strategy's autocorrelated days and it carries only
market-path sampling error. A feedback-channel claim needs the reward population across seeds, which a
single-seed pilot cannot supply.

**The signal reverses under control.** Against the zero-information `placebo`, the distributional arm's
tail is significantly *worse*, at $p\approx0.0005$ in the same output. The winners' CVaR ordering tracks
the risk-return frontier rather than tail-information content, and the placebo has the safest tail of six.

**The mechanism points the wrong way.** Responsiveness, the rank correlation between movements in the fed
tail and changes in the authored code, is *negative*, and an interpretability gate intended to detect
tail-aware code saturated across every arm including the baselines that are never fed a tail. Read through
Appendix C the three facts are coherent, and they are the signature of the Null branch: under a tail-blind
selector and a non-responsive designer, the dominance envelope is not realised.

**Honesty requires one step further.** Taken at face value, the negative responsiveness is a genuine prior
against this study's own headline mechanism claim rather than merely an instrument reading to discount. A
designer whose authored code moves opposite the fed tail is evidence that the link this dissertation was
built to detect may be weak or absent, and it is not explained away here. The confirmatory design confronts
it instead, carrying responsiveness as a pre-registered report-only measure scored across seeds, with the
saturated binary gate replaced by a quantitative reward-program differential. Whether the negative sign is
an artefact or a boundary condition is left to the powered analysis, prejudged in neither direction.

## D.2 From pilot defect to frozen design

Every correction below was recorded against the pre-registration before the freeze, and the sealed leg
was never touched: the design was hardened by defects, not tuned toward an outcome.

| The defect the pilot exposed | The correction carried into the frozen design |
|---|---|
| two instruments could not measure what they were for: the inference unit was a single path, and a binary tail-usage gate discriminated nothing | per-seed `rliable` inference, being a winner-seed ladder with interquartile-mean reduction and a paired stratified bootstrap [`agarwal2021rliable`], and a regret-bounded reward-distance measure scored against the fed signal [`gleave2021epic`; `skalse2024starc`] |
| a Benjamini–Hochberg-over-a-conjunction headline double-corrected | two co-primary intersection–union tests, each its own multiplicity correction, with BH-over-six demoted to a sensitivity |
| no control isolated *information* from *format* | the scrambled control: an identical block with the values deranged, entering as a disjoint control |
| the shared prompt named "tail" and "CVaR", so every arm wrote tail-aware code | that vocabulary was removed from every shared source, so only the treatment's *feedback* introduces the tail |
| the survivorship-corrected panel surcharged M&A exits indiscriminately, fabricating left-tail losses | the headline reverted to the conservative zero-fill panel, with the surcharge retained only as the heavy end of a disclosed band (§3.4) |
| late critic-loss explosions in a minority of trainings | a uniform PopArt value-target normaliser, which preserves the realised-return series byte-identically as a tested invariant [`vanhasselt2016popart`] |
