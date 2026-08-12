# Appendix C — The information value of tail-risk feedback (word-excluded)

**What this appendix adds to §4.9.** The body states the dominance result, the assumption (NI) under which
it bounds this designer, and the measured risk gap. This appendix carries the derivations behind them, the
conditions each rests on, the distributional-robustness reading that predicts *where* a benefit should
appear, and the pre-registered mapping from mechanism conditions to observable signatures that Chapter 5
grades the realised results against.

The control-theoretic reading, in one paragraph, because it makes the design legible at once. Posed that way it has a classical solution through the Hamilton-Jacobi-Bellman equation [`merton1969lifetime`; `merton1971optimum`], but that solution presumes the dynamics are known, and ours are unknown, sampled and non-stationary. In those terms the feedback channel is a sensor on a design loop, and "does tail feedback help" is an instrumentation question.

*On the numbering.* This appendix has no C.1: its opening material is the two unnumbered paragraphs above, and the numbered sequence begins with the first derivation. Nothing is missing between them.

## C.2 Reward design for a bounded agent

Let an agent interact with a Markov decision process $\mathcal M = (\mathcal S, \mathcal A, \mathcal P, r, \mu_0, \gamma)$, and let $F$ denote the *designer's objective*, here a risk-adjusted measure of realised performance on the sealed split, whose operational proxy inside the loop is the validation fitness $F_{\mathrm{val}}$. The optimal reward problem observes that this identification is a convenience rather than a necessity: when the agent is *bounded* in representational capacity, optimisation budget or planning horizon, the reward that maximises the designer's expected $F$ "need not bear a direct relationship to the fitness function but may confer significant advantages over rewards based only on fitness" [`singh2009where`; `sorg2010orp`; `sorg2011optimal`; `sorg2010internal`]. A single reward otherwise conflates two roles, expressing preferences and shaping a tractable learning signal, and decoupling them is what reward design exploits [`hadfieldmenell2017ird`; `abel2021expressivity`].

That licenses delegating authorship at all. The designed reward is generally not a potential-based shaping of $F$, so by the invariance theorem it can change the optimal policy [`ng1999policy`], and the arms are genuinely different objectives rather than benign re-parameterisations. And reward authorship is intrinsically under-determined [`skalse2023invariance`], which is why differences between authored rewards must be measured rather than assumed, using the regret-bounded pseudometrics of [`gleave2021epic`; `skalse2024starc`].

## C.3 The fed object is an estimate, and the controls sit inside the same ordering

Two properties of the experiments in §4.9 need stating exactly. Writing it as a deterministic functional would make the experiment noiseless given $\theta$, which is not the experiment the pipeline runs.

Both placebos are garblings of $E_{\mathrm{vec}}$, which is sharper than format-matching alone. **What the relabelling destroys is precise and it is not the tail information:** The unordered multiset of the six magnitudes survives intact and only the label-to-value pairing is broken, so that contrast tests whether the designer uses the *pairing*.

## C.4 Dominance, the deficiency identity, and the assumption that turns one into an envelope

> Theorem C.1 (Blackwell–Sherman–Stein). *Let $E$ and $E'$ be experiments on the same finite parameter
> space, the general case holding for dominated experiments [`torgersen1991comparison`]. The following are
> equivalent: (i) $E'$ is a garbling of $E$, that is $E' = K\circ E$ for some Markov kernel $K$; (ii)
> $\mathrm{Risk}_{L}^{\pi}(E) \le \mathrm{Risk}_{L}^{\pi}(E')$ for every bounded loss $L$ and prior $\pi$;
> (iii) $\int v \, d(E\pi) \ge \int v\, d(E'\pi)$ for every convex $v$ on the posterior simplex.*
> [`blackwell1953equivalent`; `sherman1951theorem`]

Only (i) $\Rightarrow$ (ii) is used, and §4.9's Proposition follows immediately because
$E_{\mathrm{scalar}} = \Pi\circ E_{\mathrm{vec}}$ with $\Pi$ deterministic.

**The envelope step, in full.** Write $R_{\mathrm{B}}(E)$ for the Bayes risk at a fixed $(L,\pi)$ and
$R_{\mathrm{real}}(E)$ for the risk the implemented designer incurs, with excess
$\varepsilon(E) = R_{\mathrm{real}}(E) - R_{\mathrm{B}}(E) \ge 0$. The measured quantity decomposes exactly:

$$
\begin{aligned}
R_{\mathrm{real}}(E_{\mathrm{scalar}}) - R_{\mathrm{real}}(E_{\mathrm{vec}}) \;=\;
&\big[\, R_{\mathrm{B}}(E_{\mathrm{scalar}}) - R_{\mathrm{B}}(E_{\mathrm{vec}}) \,\big] \\[2pt]
+\; &\big[\, \varepsilon(E_{\mathrm{scalar}}) - \varepsilon(E_{\mathrm{vec}}) \,\big].
\end{aligned}
$$

The first bracket is the Bayes gap, bounded below by zero. Hence (NI), $\varepsilon(E_{\mathrm{scalar}}) \le \varepsilon(E_{\mathrm{vec}})$, stated rather than assumed silently.

**Why (NI) is robust in the regime measured rather than knife-edge.** The Bayes gap $\Delta_{\mathrm{B}}$ is
a fixed property of the two experiments and does not move with the designer at all, while the realised
difference is a continuous functional of the designer's rule under a bounded loss and equals zero at the
header-only rule. So (NI) survives every deviation small enough to leave the realised difference below
$\Delta_{\mathrm{B}}$, and it can fail only if a designer converts the tail coordinates *more* effectively
than the Bayes rule does, which is the opposite of what a capacity-limited author does. It is still an
assumption, because $\Delta_{\mathrm{B}}$ is computed nowhere in this document.

> Proposition C.3 (worst-case price of the scalar). *Under Theorem C.1's regularity hypothesis, with
> $\lVert L\rVert_\infty \le 1$ and total variation as the $L^1$ distance, and the supremum over all
> bounded losses on a finite action set and all priors,*
> $$ \delta\big(E_{\mathrm{scalar}}, E_{\mathrm{vec}}\big) \;=\; \sup_{(L,\pi)}\Big\{\mathrm{Risk}_{L}^{\pi}\big(E_{\mathrm{scalar}}\big) - \mathrm{Risk}_{L}^{\pi}\big(E_{\mathrm{vec}}\big)\Big\}. $$

It is the *equality* that makes the deficiency worth stating, because it is two-sided [`lecam1964sufficiency`; `lecam1986asymptotic`; `torgersen1991comparison`]. This is a Proposition rather than a Corollary, because it rests on the Le Cam and Torgersen randomisation criterion rather than on Theorem C.1. **It is not evaluated anywhere in this document.**

### C.4.1 What §4.9's measured gap is, and what it is not

The reading is limited because the criterion is stated over Bayes risks and what is computed is not one. It is still worth having, and the asymmetry is why: a positive gap would not have certified $\delta > 0$, while a gap that cannot be separated from its own permutation null is an honest statement that this class of user extracts nothing measurable from the six extra columns at this sample size.

Two guards decide whether any measured gap means anything, and one instrument defect is recorded because it inverted the answer. An earlier version split by candidate slot, which sounded like a lineage and was not, and the effect was not cosmetic: 346 of 349 test rows had their exact feature row sitting in the training fold. A permutation null then shuffles the tail block across rows and repeats the whole procedure, and the referral probability is the proportion of permutation draws whose gap is at least as large as the measured one.

**One further composition defect, stated because it biased toward the reported null.** Two arms render all
six labelled tail lines, the treatment and the scrambled control, so a filter keyed on labels alone admits
both, and on the run-4 archive it did: 174 rows of treatment against 175 of scrambled. Rows whose labels
carry no information cannot predict. The instrument now takes the treatment arm alone and prints its
composition, and the figures in §4.9 are on those 174 rows.

**The gap is also a property of the estimator as much as of the data.** Sweeping the ridge penalty over
$\{0, 1, 10, 100\}$ moves it from $-0.0072$ to $-0.0009$ on the same rows, a factor of about eight, which
is why the penalty is printed in the instrument's own header. Across 60 to 5,000 permutation repetitions
the gap stays between $-0.0038$ and $-0.0036$ and the referral probability between $0.717$ and $0.785$, so
the verdict is stable. Reproduce with `python docs/analysis/deficiency_bound.py`, whose defaults are the
settings quoted.

**An information-theoretic restatement, recorded because it makes the mechanism transparent.** Treating
$\Pi$ as a channel, the data-processing inequality for $f$-divergences guarantees it cannot increase the
separation between any benign-tail law and any adverse-tail law, with equality for strictly convex $f$ if
and only if $\Pi$ is sufficient for the dichotomy [`polyanskiiwu2024it`; `liese2006divergences`]. For a
two-hypothesis version of the designer's problem, Blackwell dominance is equivalent to domination in
*every* $f$-divergence simultaneously [`raginsky2011shannon`], so §4.9 is one theorem told in two
languages. The divergence form is what connects the abstract claim to the concrete observation that a
single CVaR level discards exactly the cross-level tail shape a heavy- against light-tailed market would
reveal.

**Two structural qualifications, and one of them runs against the hypothesis under test.** The header is a
Deflated Sharpe ratio, which embeds sample skewness and kurtosis and is therefore not perfectly
tail-blind. Under nesting this does not leak differentially, since $s$ is common to both arms and cancels
from the contrast, but it means the quantity under test is the marginal information carried by
$\hat{\mathbf c}$ beyond what $s$ already conveys, which *narrows* the contrast and so biases against a
measured advantage. And the experiment is not exogenous: the law $P_\theta$ is generated by the policy
trained under the very reward being designed, so $E_{\mathrm{vec}}$ is re-measured on the trained policy's
own returns each generation. This is a performative setting in the precise sense
[`perdomo2020performative`]. The conditional-on-$\theta$ dominance survives and only the closedness
idealisation is relaxed.

## C.5 Coherence, and which estimator inherits it at which level

> Sign convention. Returns $Z$ are signed, so the lower tail is adverse and
> $\mathrm{CVaR}_\alpha(Z)=\min_{\xi\in\mathcal U_\alpha} \mathbb E_\xi[Z]$ is a low, typically negative
> *return*: a more negative CVaR is worse. The mirror loss convention $\ell=-Z$, under which the
> coherence axioms and the Kusuoka representation below are stated, is flagged where it occurs.

A risk measure on the loss orientation is coherent if it is monotone, translation-equivariant,
positively homogeneous and subadditive, so that diversification can never be penalised
[`artzner1999coherent`]. Value-at-risk satisfies the first three and fails subadditivity, while
CVaR satisfies all four [`rockafellar2000cvar`; `acerbi2002spectral`]. That is the formal content behind
the choice announced in Chapter 2.

Which estimator inherits coherence needs stating exactly, because it does not hold uniformly across the fed levels. We claim finite-sample coherence for the empirical levels and disclose that the two extrapolated levels rest instead on the coherence of the population functional they estimate.

The escape from CVaR's non-elicitability is *higher-order* joint elicitability. The pair
$(\mathrm{VaR}_\alpha, \mathrm{CVaR}_\alpha)$ is jointly elicitable, and a finite multi-level spectral
measure together with its quantiles is jointly elicitable of finite order with an essentially unique
identification function by Osband's principle [`fissler2016higherorder`; `fisslerziegel2021correction`;
`frongillokash2021complexity`], a result since generalised to the whole tail-risk class
[`fissler2025tail`]. The fed vector carries no quantiles, so this bounds what each level *could* be
scored against rather than what was shown.

**And two of the six coordinates are not CVaR at all.** The $-2\sigma$ tail mass estimates a tail-exceedance
probability, whose core object is a first-order elicitable, identifiable Bernoulli mean
[`gneitingraftery2007strictly`], though only for a fixed threshold, and
the implementation sets the threshold at $-2\hat\sigma$ estimated from the same sample, so the
fixed-threshold elicitability does not transfer unaltered. The robust skew is the Groeneveld-Meeden
generalised quantile-skewness coefficient [`groeneveldmeeden1984measuring`; `bowley1920elements`], a fixed
function of jointly elicitable quantiles [`koenkerbassett1978regression`], consistently estimable by
plug-in, though the ratio is not known to be elicitable, much as the variance is a non-elicitable function
of jointly elicitable moments. **The sufficiency claim is therefore relative rather than absolute:** The
tail-fed experiment is sufficient *relative to the scalar* experiment, which is the garbling fact, and six
tail scalars do not deliver sufficiency for the full return law.

## C.6 CVaR feedback as a distributional-robustness signal

A second and independent pillar answers a question dominance leaves open: *why should tail information help
specifically out of sample?* For an integrable return $Z\in L^1$, CVaR admits the dual representation

$$
\begin{aligned}
\mathrm{CVaR}_\alpha(Z) &\;=\; \min_{\xi \in \mathcal U_\alpha} \mathbb E_\xi[Z], \\
\mathcal U_\alpha &= \Big\{ \xi = \mathrm{d}Q/\mathrm{d}P \ge 0 : \xi \le \tfrac1\alpha\ P\text{-a.s.},\; \mathbb E_P[\xi] = 1 \Big\},
\end{aligned}
$$

so the CVaR is the worst-case expectation of $Z$ over the risk envelope, the set of re-weightings whose
likelihood ratio is bounded by $1/\alpha$. This is a sup-norm constraint on the density rather than a ball
of any finite-valued divergence, a different geometry from the $\phi$-divergence ambiguity sets of general
distributionally-robust optimisation [`rockafellar2000cvar`; `shapiro2013kusuoka`; cf. `bental2013robust`].
In the sequential setting this lifts to a statement about modelling error: optimising CVaR equals
guaranteeing the best worst-case expected return under a budgeted perturbation of the data-generating
process [`chow2015risk`; `iyengar2005robust`; `nilim2005robust`]. Feeding the designer the realised lower
tail is therefore feeding it a distributional-robustness signal, and since the evaluation is a sealed
out-of-sample window spanning a regime shift, the duality yields a sharper corollary than dominance alone:
if tail feedback helps at all, its benefit should be concentrated where the distribution shifts.

**Why time-consistency is not required here, and why that is a property of the design.** A reader who knows
the dynamic-risk literature will object that CVaR is not time-consistent [`bodafilar2006time`], and that
the optimal static-CVaR policy is in general non-Markovian [`lim2022cvar`]. Both are correct and neither
bears on this design, for one structural reason: the tail vector is designer feedback, not a
risk-to-go. It is a diagnostic handed to the reward author between generations. It is never composed
recursively, never used as a Bellman risk mapping and never optimised by the agent, which optimises the
authored per-step reward and so remains Markov by construction. The honest residual is narrow and worth
stating: the fed statistic is a static functional of a realised return path, so it carries no claim about
the agent's dynamic risk preferences, and none is made anywhere in this dissertation.

## C.7 From envelope to realisation: three conditions, and the prediction each licenses

Whether the realised pipeline attains any of this depends on three conditions, stated and bound to
observable signatures before the sealed test is unblinded.

It is tempting to add that pre-registration therefore makes this a severe test. Severity must be *supplied*, by a smallest effect size fixed in advance and an equivalence test able to reject an effect larger than that bound [`lakens2018tost`; `campbell2018cet`; `altman1995absence`].

**1. Selection sensitivity.** Candidates are selected on a Deflated Sharpe at $\lambda = 0$. The registered
protocol calls this selector *tail-blind*, and that wording is stronger than the estimator warrants.
The Deflated Sharpe divides by a factor embedding skewness and kurtosis, so at a positive Sharpe a more
negative skewness lowers the deflated value, and the selector does place a mild premium on
left-tail-protected candidates. **What the design secures is arm-invariance rather than
tail-insensitivity.** The identical map is applied to every arm, so its tail sensitivity is common-mode and
confers no *between-arm* advantage, which is the weaker property the inference actually requires.

**2. Designer responsiveness.** The benefit requires the model to *condition* the code it writes on the fed
tail content, which is an empirical rather than an assumed property.

**3. Agent attainability.** Even a tail-aware reward helps only if the bounded agent converts it into
tail-protective behaviour. **A structural obstruction operates here beyond mere undertraining.** A
mean-critic agent maximises the entropy-regularised *expectation* of whatever reward it is given, and CVaR
is not a linear functional of the return distribution, so a static CVaR penalty embedded in a per-step
reward does not represent the tail objective. This is a *representation* failure rather than a
time-consistency failure. It is sharper still: optimising a static CVaR objective requires augmenting the
state with a running VaR-level component [`bauerle2011markov`], and the optimal static-CVaR policy is in
general non-Markovian [`lim2022cvar`], so no per-step reward on a fixed state interface can encode it
exactly. Two consequences follow. Under this design, where state augmentation is deliberately excluded so
that only the reward may vary, the reward channel is the forced injection point for tail-risk
information, a design necessity rather than a convenience. And by the same results that channel is
structurally unable to guarantee CVaR-optimality, so the Null branch is over-determined: the envelope
can fail to be realised at the *agent* stage independently of the designer's responsiveness. Table C.1
maps each branch of that argument to the signature it predicts.

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table C.1 — Pre-registered mapping of mechanism conditions to observable signatures.** All three branches predict a tie on the Sharpe leg, so only the tail leg and the two mechanism columns can tell them apart.
```{=latex}
\par\endgroup
```

\begingroup\footnotesize

| Mechanism condition | $H_2$-RA | $H_2$-Tail | Responsiveness | Reward-program differential | Pre-registered verdict |
|--------|-----|---------|----------|-------|--------|
| **Strict** — the fed tail shapes the reward code | tie | **treatment beats all three, reject** | $>0$ | treatment code references tail statistics more | **H2-Tail supported, H2-RA not** |
| **Weak** — tail information helps but not robustly | tie | partial ($\le 2$ legs reject) | $\approx 0$ | weak or mixed differential | **inconclusive** (TOST-bounded) |
| **Null** — the designer is not a Bayes-responsive user | tie | tie (placebo not beaten) | $\le 0$ | no cross-arm code signature | **both null** |

\endgroup

Under the frozen design the selector is the same arm-invariant map in *every* branch, which is why even the Strict branch predicts an $H_2$-RA tie, and the branches separate only on the tail leg and the code-level instruments. A confirmed Null is then not an absence of evidence but a corroborated prediction about the gap between the information-theoretic envelope and its bounded realisation.