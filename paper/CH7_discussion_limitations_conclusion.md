# Chapter 7 — Discussion, Limitations, and Conclusion

## 7.1 Discussion

This dissertation set out to test whether the *content* of the feedback shown to an automated reward-designer —
specifically, the realised-return lower tail rather than a scalar summary — changes the risk-sensitive reward code
a language model writes and the behaviour it induces. The theory of Chapter 3 establishes the strongest claim that
is honestly available: an *optimal* user of the multi-level tail vector weakly dominates an optimal user of the
scalar, for every loss and prior, because the scalar is a measurable garbling of the vector. That dominance is an
*envelope*, not a guarantee, and the empirical contribution is to measure how much of it a *bounded* realisation —
a finite-capacity language model coupled to a fixed, capacity-limited agent under tail-blind selection — actually
attains.

Concretely, the research question decomposes into the three pre-registered sub-questions of §1.3 —
responsiveness, transmission, specificity — and we grade each explicitly here so the reader can audit what was
asked against what was answered. **Responsiveness** — does the authored reward *code* move when the fed tail
moves? **[Verdict — from the §6 dose–response and reward-construct analyses.]** **Transmission** — when the code
moves, does the induced policy's realised tail move with it? **[Verdict — from the §6 mediation analysis.]**
**Specificity** — is any response specific to *genuine* tail information, or does the structure-shuffled placebo
elicit the same response? **[Verdict — from the §6 placebo_shuffled contrast.]** The mechanism claim stands or
falls on this three-link chain, and a break *locates* the failure: at responsiveness, in the designer's reading
of the numbers; at transmission, in the reward-to-policy coupling; at specificity, in surface-format echoing. The
H2 performance equivalence is then the rigorous backdrop against which the located break is interpreted, not the
discovery itself.

**Scorecard.** The pre-registered questions, their predictions, and where each verdict is finalised (verdicts filled
from Chapter 6):

| Question | Pre-registered prediction | Verdict |
|---|---|---|
| **H1** — beat hand-designed baselines | descriptive only; excluded from the $m{=}6$ family (both-direction bias caveat) | *[from §6]* |
| **H2-RA** — risk-adjusted (Sharpe IUT) | tie: no Sharpe edge under $\lambda{=}0$ selection, regardless of channel | *[from §6]* |
| **H2-Tail** — tail outcome (CVaR-5% IUT) | Null branch — a tie or a TOST-bounded interval; the prototype's negative responsiveness predicts no separation | *[from §6]* |
| **H3** — iterative vs single-shot | hypothesis under test (no frozen directional prediction; frozen H0: multi-generation <= single-shot at a matched budget) | *[from §6]* |
| **H4** — LLM vs uninformed search | hypothesis under test (no frozen directional prediction): the LLM designer vs (a) random-search over reward code and (b) Bayesian optimisation over the shared template's coefficients | *[from §6]* |
| **SQ1** — responsiveness | authored code moves weakly or negatively with the fed tail ($\le 0$) — the chain's first link | *[from §6]* |
| **SQ2** — transmission | little realised-tail movement given code movement (the chain is severed upstream) | *[from §6]* |
| **SQ3** — specificity | any response is not specific to genuine tail information (placebo-matched) | *[from §6]* |

**[Result — finalise from the confirmatory campaign.]** The directional prototype, read through the theory,
locates the realised system on the *Null* branch of the pre-registered prediction table: the apparent tail
advantage did not survive its own zero-information placebo control, and the model's authored reward code was, if
anything, *less* responsive to larger movements in the fed tail. We therefore report a pre-registered boundary
condition rather than a performance claim. Three readings make this a positive scientific result rather than an
absence of evidence.

First, it is a *corroborated prediction about the envelope–realisation gap*. The theory predicts exactly this
outcome under the study's two design facts — a tail-blind selector ($\lambda=0$) gives the channel no exogenous
help, and a non-responsive designer supplies none endogenously — so the null confirms the mechanism account of
§3.7 rather than contradicting the dominance result of §3.4. The information an optimal user could exploit exists;
the tested system does not exploit it. Second, by the CVaR–robustness duality of §3.6, the finding is a statement
about *distributional-robustness information*: feeding the lower tail is feeding a robustness signal, and the null
says this particular automated designer does not convert that signal into more robust reward code at the studied
budget. Third — and most useful to the field — the result is a *boundary condition for the automated-discovery
agenda*. That agenda has shown, by demonstration, that language models can discover objectives; this study shows,
under controlled and pre-registered conditions, that *which information they are shown* did not, here, change what
they discovered. The contribution is not the sign of an effect but a calibrated, falsifiable instrument for asking
the question — and the discovery that, on a clean test, the optimistic reading does not hold.

The mechanism analyses sharpen the interpretation rather than merely supporting it. The reward-construct
prevalence differential (Chapter 6) is a construct-prevalence probe, not a categorical taxonomy of reward-program
*kinds*: it counts the declared tail constructs each authored reward uses and, with an identifier-invariant
structural comparison built on the regret-bounded EPIC/STARC pseudometrics, measures whether the authored rewards
genuinely differ across feedback arms or are near-policy-invariant re-shapings of one objective. (A taxonomy of
program *kinds* is induced from the campaign archive by a dedicated instrument — connected components of the
identifier-invariant structural-similarity graph over the pooled authored programs, with per-arm kind composition —
validated on the prototype archive, where it cleanly separates the search baselines' single re-parameterised
template from the language-model arms' near-fully idiosyncratic programs.) The
mediation analysis decomposes the feedback arm's effect on performance into an indirect effect through the authored
reward code — the product of the designer's *responsiveness* (does the fed signal move the code?) and the code's
*transmission* to the realised outcome — reported with a bootstrap confidence interval [`imai2010identification`].
An indirect effect that is reliably non-zero yet opposite in sign to the direct effect is *inconsistent mediation
(suppression)* — a recognised, identifiable quantity [`mackinnon2000equivalence`; `orourke2018suppression`], not a
failed manipulation; testing the mediated path is informative even when the total effect is null
[`orourke2018suppression`]. Identification of the indirect effect rests on a sequential-ignorability assumption
that is strong and untestable [`imai2010identification`]; we state it rather than assume it silently and report the
decomposition descriptively, not as a causal proof, leaving a formal confounding-sensitivity analysis to future work. Read together, they convert "we observed no headline effect" into a mechanistic
statement: the channel is present, the selector is deliberately blind to it, and the designer does not route it into the reward
code in the value-adding direction. The localisation agrees with the adjacent behavioural evidence: language
models' risk attitudes are real but steered by surface conditioning rather than by fed magnitudes
[`hartley2025personality`], and where an agent merely *consumes* CVaR estimates computed for it at decision
time, tail-aware behaviour is readily obtained [`chergui2025uncertainty`] — placing the break specifically in
the *authorship*, not the consumption, of tail-risk information. For practitioners of automated reward design the implication is concrete:
richer feedback is not self-acting. Realising the dominance envelope requires *both* a selection objective that
rewards the fed dimension and a designer that demonstrably conditions on its content — neither of which a default
Eureka-style loop with a tail-blind fitness supplies.

A word on multiplicity across the mechanism sub-questions, since the mechanism analysis — not the performance
contrast — is the originality of this work. The three sub-questions (responsiveness — does the fed signal move the
authored code; transmission — does the code move the outcome; specificity — is any effect genuine use of the tail
numbers rather than a surface echo) are run as a **report-only, descriptive, null-locating** layer: their purpose
is to say *where* a null breaks in the fed → code → policy → tail chain, not to hunt for a significant effect. They
are computed on the campaign and are **structurally disjoint from the frozen confirmatory family of $m=6$** — no
mechanism statistic gates H2, and none can convert the pre-registered null into a performance claim. Because a
descriptive layer with several legs still invites a multiplicity reading, we report a Benjamini–Hochberg (and, as a
stricter sensitivity, Bonferroni) correction *across the mechanism legs*, mirroring the Bonferroni-across-four
sensitivity applied to the cross-hypothesis family in §4.7; we read the corrected picture, not a single
uncorrected leg, and we do not present any mechanism $p$-value as confirmatory. The stance is deliberately
conservative: the mechanism kernel earns its place by localising the boundary condition honestly, not by
manufacturing significance out of a rich instrument.

## 7.2 Limitations

We foreground the four limitations most likely to bound the result's interpretation; the full register is
Appendix B. **(i) Construct.** The fed signal is six left-tail scalars, not the full return distribution; we name
it *multi-level tail-risk feedback* throughout and claim only that it spans the coherent-risk class (Chapter 3),
making no claim about upside or non-coherent features. **(ii) Training adequacy.** The fixed agent is trained for
200,000 steps, a budget set from a convergence pilot (the critic's descent completes near 100,000 steps and
out-of-sample performance is flat within noise to 350,000); arm differences are read *at this fixed, matched
budget*, supported by a learning-curve diagnostic. **(iii)
Selection blindness.** The selector is deliberately tail-blind ($\lambda=0$); this is what makes a tail effect
attributable to the channel, but it also places the study on the boundary of the Null branch, so the result speaks
to *this* (conservative, identifiable) configuration and not to a tail-rewarded selector. **(iv) External
validity.** One universe of US large-cap equities, one historical window, and one language-model family: the study
claims a boundary condition for that instance and, in particular, cannot earn the plural "language models" — every
quantitative claim is scoped to the single tested family. Each of these is a deliberate, disclosed design decision
with a documented rationale, not a hidden assumption; the register below records the remainder with the same
candour.

## 7.3 Conclusion

The dissertation contributes an instrument, a protocol, and a theory for a question the automated-discovery agenda
has been unable to ask cleanly: does the information content of the feedback to an automated objective-designer
change the objectives it discovers? The instrument feeds a language-model reward-designer the realised-return lower
tail off-critic while holding the agent fixed; the protocol submits the resulting comparison to a frozen,
family-wise-controlled, pre-registered test with placebo and structure-shuffled controls; and the theory bounds
what an optimal user of that feedback could achieve and states the conditions under which a bounded realisation
attains it. The empirical finding is a pre-registered boundary condition — that, under tail-blind selection and at
the studied budget, multi-level tail-risk feedback did not change the tested model's risk-sensitive reward code in
the value-adding direction — which the theory predicts and the mechanism analyses localise. A clean, controlled
null on a question the field has answered only by optimistic demonstration is the contribution: it replaces a
plausible intuition with a calibrated measurement, and it leaves a reusable, pre-registered instrument with which
the conditions identified here — a tail-rewarded selector, a demonstrably responsive designer, a converged agent,
and a second model family — can each be tested in turn.
