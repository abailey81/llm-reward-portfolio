# Chapter 3 — The Information Value of Tail-Risk Feedback (Theory)

## 3.1 Overview

This chapter develops the theory that motivates and disciplines the central experiment. The empirical question —
*does feeding a language-model reward-designer the multi-level lower tail of the realised-return distribution lead
it to write better risk-sensitive reward code than feeding it a scalar summary?* — is, at root, a question about
the **value of information** supplied to an automated decision-maker. We make this precise in four steps.

First (§3.2) we situate the design within the *optimal reward problem*: for a bounded learning agent, the
reward that best guides behaviour need not coincide with the designer's own objective, which is what licenses
delegating reward authorship at all. Second (§3.3–3.4) we cast the feedback channel as a *statistical experiment*
supplied to the reward-designer and prove that the tail vector **weakly dominates** the scalar for every loss and
prior, via the Blackwell–Sherman–Stein theorem, with a quantitative excess-risk bound from Le Cam deficiency.
Third (§3.5–3.6) we justify the specific signal — why a *vector* of conditional value-at-risk (CVaR) levels rather
than a single number (sufficiency and joint elicitability), and why feeding the tail is, by a duality, feeding a
*distributional-robustness* signal whose payoff should appear precisely under the out-of-sample distribution shift
our sealed test induces. Fourth (§3.7) we descend from the envelope to the realised system, stating three
mechanism conditions and the pre-registered, falsifiable prediction that follows from each.

The chapter's contribution is therefore not a claim that richer feedback *must* help — it is a precise account of
*when it can*, *why it might not*, and *what each outcome would look like*. The dominance result is an upper bound
on what an optimal user of the signal could achieve; the realised pipeline couples a finite-capacity language
model to a fixed, capacity-limited reinforcement-learning agent, so the bound is an envelope, not a guarantee. The
distance between envelope and realisation is exactly what Chapters 5–6 estimate.

## 3.2 Reward design for a bounded agent

Let an agent interact with a Markov decision process $\mathcal M = (\mathcal S, \mathcal A, P, \gamma)$ and let
$F$ denote the *designer's objective* — the quantity we ultimately care about, here a risk-adjusted measure of
realised portfolio performance on held-out data. Classical reinforcement learning identifies the agent's reward
$r$ with (a surrogate for) $F$. The **optimal reward problem** of Singh, Lewis and Barto observes that this
identification is a convenience, not a necessity: when the agent is *bounded* — limited in representational
capacity, optimisation budget, or planning horizon — the reward that maximises the designer's expected $F$ "need
not bear a direct relationship to the fitness function but may confer significant advantages over rewards based
only on fitness" [`singh2009where`; `sorg2011optimal`; `sorg2010internal`]. A single reward function otherwise
conflates two distinct roles: *expressing the designer's preferences* and *shaping a tractable learning signal for
this particular agent*. Decoupling them is precisely what reward design exploits.

This frames our object of study. We hold the agent fixed (a soft actor–critic learner; Chapter 4) and delegate
the authorship of the behaviour-guiding reward $r$ to a language model, the *reward-designer*. The designer is
not handed $F$ directly; it is handed *feedback* — a statistic of the return distribution its previous reward
induced — and asked to revise the reward code. The scientific question is whether the **content** of that
feedback changes the rewards it writes and, through them, realised performance. Because the agent is demonstrably
capacity-limited (Chapter 4 documents that the critic is far from its convergence regime at the training budget),
the optimal-reward-problem premise holds with force: there is, in principle, room for a well-chosen reward to
compensate for the agent's boundedness, and therefore room for *better information to the designer* to matter.

Two remarks fix scope. The designed reward is generally **not** a potential-based shaping of $F$, so by the
necessary-and-sufficient invariance theorem of Ng, Harada and Russell it can change the optimal policy
[`ng1999policy`]: the arms are genuinely different objectives, not benign re-parameterisations of one. And reward
authorship is intrinsically under-determined — many rewards induce the same optimal policy [`skalse2023invariance`]
— which is *why* reward design is a non-trivial search problem and why differences between authored rewards must
be measured rather than assumed (we quantify them in Chapter 6 using the regret-bounded EPIC/STARC pseudometrics
of [`gleave2021epic`; `skalse2024starc`]).

## 3.3 The feedback channel as a statistical experiment

We now formalise "feeding the designer information about the return distribution". Let $\theta$ index the unknown
state of nature relevant to the decision the designer faces — concretely, the features of the realised-return law
$P_\theta$ that bear on how the reward should weight the downside. A **statistical experiment** in the sense of
Blackwell is a Markov kernel $E:\Theta \rightsquigarrow \mathcal Z$ mapping each $\theta$ to a distribution over an
observation space $\mathcal Z$ [`blackwell1951comparison`; `blackwell1953equivalent`]. The reflection loop supplies
the designer with one of two experiments:

- $E_{\mathrm{vec}}$ emits the **multi-level tail vector** $\mathbf c(P_\theta) = \big(\mathrm{CVaR}_{\alpha_1},
  \dots, \mathrm{CVaR}_{\alpha_k}, \text{left-tail mass}, \text{robust left-tail skew}\big)$ measured on the
  training-split realised returns;
- $E_{\mathrm{scalar}}$ emits a **scalar summary** $s = g(\mathbf c(P_\theta))$ — in the experiment, a held-out
  risk-adjusted performance number.

The two experiments differ in exactly one respect, which is the entire manipulation: the scalar is a fixed
measurable function of the vector. Writing $g$ for that reduction (a degenerate Markov kernel),
$$ E_{\mathrm{scalar}} \;=\; g \circ E_{\mathrm{vec}}. $$
In the vocabulary of comparison of experiments, $E_{\mathrm{scalar}}$ is a **garbling** of $E_{\mathrm{vec}}$ —
a post-processing of the more informative experiment by a Markov kernel. Here that kernel is *deterministic*: a
noiseless coarsening that collapses the $k$ tail coordinates onto one — the degenerate, noise-free limit of
Blackwell post-processing, not the addition of stochastic noise [`blackwell1953equivalent`]. This single structural fact —
that the scalar carries no information about $\theta$ beyond what the vector already carries — is what the next
section converts into a dominance theorem.

## 3.4 Dominance: the tail vector Blackwell-dominates the scalar

A decision problem for the reward-designer is a pair $(L, \pi)$ of a (bounded) loss $L$ and a prior $\pi$ over
$\theta$; the designer chooses an action — a reward to author — as a function of the observation, and incurs
Bayes risk $\mathrm{Risk}_{L}^{\pi}(E)$ — equivalently, the designer maximises the expected *objective* $U = -L$,
and we take $L$ bounded with $\lVert L\rVert_\infty \le 1$ throughout, so that "lower Bayes risk" and "higher
expected objective" are one statement. The intuition behind what follows is elementary: a designer free to *ignore*
part of what it is shown can never be made worse off by being shown more — anything it could do with the scalar it
could also do with the vector, by first discarding the extra coordinates. Blackwell's theorem makes this precise,
and proves the converse. The foundational result is:

> **Theorem 3.1 (Blackwell–Sherman–Stein).** *Let $E$ and $E'$ be experiments on the same parameter space. The
> following are equivalent: (i) $E'$ is a garbling of $E$, i.e. $E' = K\circ E$ for some Markov kernel $K$; (ii)
> $\mathrm{Risk}_{L}^{\pi}(E) \le \mathrm{Risk}_{L}^{\pi}(E')$ for every bounded loss $L$ and prior $\pi$; (iii)
> $\int v \, d(E\pi) \ge \int v\, d(E'\pi)$ for every convex $v$ on the posterior simplex.* [`blackwell1953equivalent`;
> `sherman1951theorem`; the third party to the equivalence, Stein, is unpublished and attributed in
> `blackwell1953equivalent`.]

Because $E_{\mathrm{scalar}} = g\circ E_{\mathrm{vec}}$ with $g$ a (deterministic) kernel, Theorem 3.1(i)$\Rightarrow$(ii)
applies immediately:

> **Proposition 3.2 (Dominance of tail feedback).** *For every bounded loss $L$ and prior $\pi$,*
> $$ \mathrm{Risk}_{L}^{\pi}\!\big(E_{\mathrm{vec}}\big) \;\le\; \mathrm{Risk}_{L}^{\pi}\!\big(E_{\mathrm{scalar}}\big). $$
> *An optimal reward-designer supplied with the multi-level tail vector attains weakly higher expected designer
> objective than one supplied with the scalar summary, uniformly over loss functions and priors.*

Proposition 3.2 is the theoretical core of the dissertation's hypothesis: *if the designer uses its information
optimally*, tail feedback can only help. The qualitative statement can be sharpened into a *quantitative* one using
Le Cam's notion of **deficiency**, which measures how much worse one experiment can be made to perform than
another. With $\delta(E', E) = \inf_K \sup_\theta \lVert (K\circ E')_\theta - E_\theta\rVert_{\mathrm{TV}}$, where
$\lVert\cdot\rVert_{\mathrm{TV}}$ denotes the $L^1$ total variation $\int\lvert\mathrm{d}\mu-\mathrm{d}\nu\rvert\in[0,2]$
(so that, with $\lVert L\rVert_\infty\le 1$ and hence oscillation $\le 2$, the risk-transfer bound below holds with
constant exactly $1$), the deficiency of $E'$ relative to $E$ — how closely $E'$ can be post-processed by a kernel $K$ to reproduce $E$,
and hence $0$ exactly when $E'$ is Blackwell at-least-as-informative as $E$ (the standard Le Cam/Torgersen
orientation, in which the *first* argument is the experiment that is garbled) — Le Cam's randomisation criterion
gives a uniform risk-transfer bound
[`lecam1964sufficiency`; `lecam1986asymptotic`; `torgersen1991comparison`]:

> **Corollary 3.3 (Worst-case price of the scalar).** *For every loss $L$ with $\lVert L\rVert_\infty \le 1$ and
> every prior, the excess Bayes risk incurred by the scalar over the vector is at most the deficiency*
> $\delta\big(E_{\mathrm{scalar}}, E_{\mathrm{vec}}\big)$ *— the deficiency of the scalar relative to the vector,
> i.e. how closely the scalar can be post-processed to reproduce the vector — which is strictly positive whenever
> the tail levels carry information about $\theta$ that the scalar does not, i.e. whenever $E_{\mathrm{vec}}$ is
> not itself a garbling of $E_{\mathrm{scalar}}$.*

The same conclusion admits an information-theoretic restatement that we record because it makes the mechanism
transparent. Treating the reduction $g$ as a channel, the **data-processing inequality** for $f$-divergences
guarantees that $g$ cannot increase the statistical separation between any "benign-tail" law $P$ and any
"adverse-tail" law $Q$: $D_f\!\big(g_\# P \,\Vert\, g_\# Q\big) \le D_f(P\Vert Q)$, with equality — for *strictly convex* $f$ — if and only
if $g$ is sufficient for the dichotomy $\{P, Q\}$ (equivalently, the likelihood ratio $\mathrm{d}P/\mathrm{d}Q$ admits a
$\sigma(g)$-measurable version, $Q$-a.s.) [`polyanskiiwu2024it`, Thm 7.4 and Thm 2.17; `liese2006divergences`]. For a two-hypothesis (dichotomy) version of the designer's problem, Blackwell dominance
is equivalent to domination in **every** $f$-divergence simultaneously (equivalently, in all convex losses)
[`raginsky2011shannon`], so §3.4 is one theorem told in two languages. This bilingual framing is not ornamental: the divergence form is what connects the abstract claim
to the concrete observation that a single CVaR level discards exactly the cross-level tail shape that a heavy- vs
light-tailed market would reveal.

**The load-bearing caveat.** Theorem 3.1 and Proposition 3.2 concern *information structures* and *optimal* Bayes
users. Our realised system is neither: the designer is a finite-capacity language model that may fail to extract or
act on the tail content, and it feeds a fixed, capacity-limited SAC agent that may fail to convert a better reward
into better behaviour. Proposition 3.2 therefore upper-bounds the *attainable* improvement; it does not assert that
the *realised* pipeline will exhibit any. A further gap is *structural* rather than behavioural: the idealised
garbling $E_{\mathrm{scalar}} = g\circ E_{\mathrm{vec}}$ treats the scalar as a measurable reduction of the *same*
observation, whereas the realised comparator scalar is a held-out-split risk-adjusted number computed on a
*different* sample than the training-split tail vector (§3.3; Chapter 4); the garbling diagram thus commutes
*exactly* for the idealised information structure but only *approximately* for the realised, split-mismatched
implementation (the scalar and vector are correlated but distinct statistics) — one further reason the realised
pipeline can fall short of the envelope. The realised comparator is, moreover, a *Deflated Sharpe ratio*
(Chapter 4), which embeds skewness and excess kurtosis and is therefore **not perfectly tail-blind**: the idealised
$E_{\mathrm{scalar}}$ as a plain risk-adjusted number is an approximation, and the realised scalar already carries
*part* of the tail information the vector supplies — which *narrows* rather than widens the contrast under test,
biasing against (not towards) a measured distributional advantage. Finally, the experiment is not exogenous: the
state of nature $\theta$ indexes features of the realised-return law $P_\theta$, yet that law is generated by the
policy trained under the very reward being designed, so $E_{\mathrm{vec}}$ is re-measured on the trained policy's
own returns each generation rather than being a fixed, exogenous Blackwell experiment — the endogeneity Chapter 1
makes explicit (coupled reward→policy→measurement loops); the conditional-on-$\theta$ dominance survives, and only
the closedness idealisation is relaxed. Stating the theorem honestly as an envelope — and then measuring the
gap — is the methodological posture of the chapter and the thesis. We make the conditions under which the envelope
is (and is not) attained explicit in §3.7.

## 3.5 Why a vector? Sufficiency and elicitability of the fed statistics

> **Sign convention (used throughout this chapter).** Returns $Z$ are signed — gains positive, losses negative —
> so the lower tail is the *adverse* direction and $\mathrm{CVaR}_\alpha(Z)=\min_{\xi\in\mathcal U_\alpha} \mathbb E_\xi[Z]$ (with $\mathcal U_\alpha$ the risk envelope of §3.6) is a (low,
> typically negative) *return*: a **more negative CVaR is worse**. The mirror loss convention $\ell=-Z$ (under
> which CVaR is a positive loss and the Rockafellar–Uryasev dual is a $\max$) is noted once in §3.6;
> `NOMENCLATURE.md` keys to this orientation.

Proposition 3.2 shows a richer signal cannot hurt an optimal user, but it does not by itself justify *this* signal.
Two results establish that the multi-level CVaR vector is a principled — indeed, in a precise sense canonical —
representation of the lower tail, rather than an arbitrary collection of numbers.

**It spans the coherent-risk class.** By the Kusuoka representation (on an atomless probability space; stated in the mirror loss orientation $\ell=-Z$ of §3.6), every law-invariant
*coherent* risk measure is a supremum over mixtures of CVaR (average value-at-risk) across confidence levels, and every *comonotonic*
law-invariant coherent risk measure is a single, unique such mixture — a spectral risk measure
[`kusuoka2001law`; `shapiro2013kusuoka`, eqns (10),(30),(42)]. The atomless idealisation is not load-bearing for the fed quantity: on the *atomic* empirical return measure the finite-support discrete spectral estimator we actually compute is coherent at every sample size $N$ [`acerbi2002spectral`, Thm 5.3]. A finite vector of CVaR levels is
therefore the finite-support basis from which this entire class is assembled: the scalar summary collapses the
mixing measure to a point mass, while the vector retains the spectrum. Adding levels strictly increases the
spectral resolution of the tail the designer can "see".

**It is a well-defined, jointly elicitable learning target — and a scalar is not.** A statistic is *elicitable* if
it minimises the expectation of some strictly consistent scoring function (it is a legitimate forecasting/learning
target) and *identifiable* if it admits a strict identification function (its calibration is testable). CVaR alone
is **not** elicitable [`gneiting2011making`]; indeed expectiles are the *only* law-invariant coherent risk measures that are elicitable as
scalars [`ziegel2016coherence`; `bellini2015elicitable`]. This is not a technicality — it is the formal reason a
single coherent tail number cannot serve as a clean target, and hence why a *vector* is necessary rather than
stylistic. The escape is *higher-order* joint elicitability: the pair $(\mathrm{VaR}_\alpha, \mathrm{CVaR}_\alpha)$
is jointly elicitable, and a finite multi-level spectral measure *together with its quantiles* is jointly
elicitable of finite (higher) order, with an essentially unique identification function by Osband's principle
[`fissler2016higherorder`, Cor. 5.5; with the published correction `fisslerziegel2021correction`;
`frongillokash2021complexity`]. The most recent generalisation extends this to the whole tail-risk class via a
generator construction [`fissler2025tail`]. We therefore
state the fed signal's status precisely, keeping **two distinct properties apart** (they are commonly, and wrongly,
welded). First, the vector is *sufficient relative to the scalar* — this is the garbling fact of §3.4 (the scalar is
a measurable reduction of the vector), and it is what the value-of-information argument rests on; it is **not** an
absolute sufficiency claim for the full return law, which six tail scalars do not deliver. Second, and
*independently* of sufficiency, the vector is a jointly identifiable, jointly (higher-order) elicitable
finite-dimensional representation of the lower tail of the spectral class — which is what makes the fed quantity a
legitimate, calibration-testable learning and forecasting target (it is what licenses the strictly consistent
FZ0/$(\mathrm{VaR},\mathrm{CVaR})$ tail backtest of Chapter 6), **not** what establishes the dominance. The scalar
is neither sufficient relative to the vector nor a coherent elicitable target.

## 3.6 CVaR feedback as a distributional-robustness signal

A second, independent pillar answers a question Proposition 3.2 leaves open: *why should tail information help
specifically out of sample?* The answer is a duality. For an integrable return $Z\in L^1$ (i.e. $\mathbb E\lvert Z\rvert<\infty$;
the minimum is then attained on the weak\*-compact envelope $\mathcal U_\alpha\subset L^\infty$), the CVaR admits the dual representation
$$ \mathrm{CVaR}_\alpha(Z) \;=\; \min_{\xi \in \mathcal U_\alpha} \mathbb E_\xi[Z], \qquad
   \mathcal U_\alpha = \Big\{ \xi = \mathrm{d}Q/\mathrm{d}P \ge 0 : \xi \le \tfrac1\alpha\ P\text{-a.s.},\; \mathbb E_P[\xi] = 1 \Big\}, $$
where $Z$ is a *return* (the lower tail is the adverse direction), so the CVaR is the worst-case — i.e. the
**minimum** — expectation of $Z$ over the **CVaR risk envelope** $\mathcal U_\alpha$: the set of re-weightings whose
likelihood ratio $\xi = \mathrm{d}Q/\mathrm{d}P$ is bounded above by $1/\alpha$. This is a sup-norm ($L^\infty$)
constraint on the density — *not* a $\phi$-divergence ball: CVaR is precisely the coherent/spectral case whose dual
ambiguity set is the likelihood-ratio-bounded simplex, a different geometry from the divergence balls of general
$\phi$-divergence distributionally-robust optimisation [`rockafellar2000cvar`; `shapiro2013kusuoka`; cf. the
contrasting $\phi$-divergence ambiguity sets of `bental2013robust`]. (Under the loss convention $\ell = -Z$ the same
envelope gives the Rockafellar–Uryasev dual as a *maximum*; we use the return convention throughout.) In the sequential setting this lifts to a statement about modelling error:
optimising CVaR equals guaranteeing the best worst-case expected return under a *budgeted perturbation of the
data-generating process* [`chow2015risk`, Prop. 1; cf. robust MDPs `iyengar2005robust`; `nilim2005robust`].
Feeding the designer the realised lower tail is therefore feeding it a **distributional-robustness** signal: it
informs the reward about performance under adverse re-weightings of the return law. Our evaluation is a sealed
out-of-sample test spanning a regime shift (2020–2026, spanning the post-COVID-crash volatility regime, the 2022
bear market, and the 2023–25 rally; the crash itself falls in the boundary purge — Chapter 4) — i.e. precisely a
distribution-shift evaluation. The robustness duality thus yields a sharper,
testable corollary than Proposition 3.2 alone: if tail feedback helps at all, its benefit should be **concentrated
where the distribution shifts**, motivating the regime-conditional analysis of Chapter 6. This is the deepest
answer to "why CVaR, and why might it matter precisely on the held-out leg".

## 3.7 From envelope to realisation: mechanism conditions and pre-registered predictions

Sections 3.4–3.6 establish that an *optimal* user of tail feedback weakly dominates, that the fed vector is a
*sufficient* tail representation, and that its payoff should surface under *distribution shift*. Whether the
*realised* pipeline attains any of this depends on three conditions, which we state and bind to observable
signatures **before** the sealed test is unblinded (the pre-registered prediction table, reproduced from
`PREREGISTRATION.md` §1a). This converts the study from a measurement into a *severe* test in the error-statistical sense (Mayo): because
the frozen, deviation-free protocol fixes each prediction before the sealed test is unblinded, a result of *either*
sign confirms or refutes a stated prediction under controlled error probabilities (pre-registration alone does not
sharpen a *Popperian* test — the basis is severity plus forking-paths avoidance; §1a).

1. **Selection sensitivity.** Candidate rewards are selected on a fitness $F$. If $F$ is tail-blind — as it is
   here by deliberate pre-registration (the selection metric is a validation Deflated Sharpe with risk-aversion
   weight $\lambda = 0$; Chapter 4) — then the *selector* — the same for every arm — gives no *between-arm* advantage to tail-aware rewards (its only
   tail sensitivity, the Deflated Sharpe's second-order term, is common-mode; §3.4), and any tail benefit must
   arise endogenously from the designer's *use* of the fed signal, not from the selection pressure.
   This is a conservative design choice: it makes a tail result, if observed, attributable to the feedback channel
   rather than to a tail-favouring selector.
2. **Designer responsiveness.** The benefit requires the language model to *condition* the reward code it writes
   on the fed tail content. Whether it does is an empirical, not assumed, property (Chapter 6 estimates it as the
   indirect effect of the feedback arm on performance through the authored reward code, a mediation quantity).
3. **Agent attainability.** Even a tail-aware reward only helps if the bounded SAC agent converts it into
   tail-protective behaviour within the training budget. A *structural* obstruction operates here beyond mere
   undertraining: a mean-critic agent maximises the *expectation* of whatever reward it is given, and a static CVaR
   penalty embedded in a per-step reward is *time-inconsistent* — the expectation of a CVaR-penalised reward is not
   the CVaR of the policy's return distribution, so expectation-maximising SAC is not guaranteed to recover a
   CVaR-optimal policy even from a perfectly tail-aware reward (the static-vs-dynamic CVaR distinction;
   `bodafilar2006time`). The obstruction is sharper than time-inconsistency alone: optimising a *static* CVaR
   objective in an MDP requires augmenting the state with a running VaR-level component [`bauerle2011markov`],
   and the optimal static-CVaR policy is in general *non-Markovian* — history-dependent — so no per-step reward
   on a fixed state interface can encode it exactly [`lim2022cvar`]. Two consequences follow. Under the frozen
   agent and interface of this design — where state augmentation is deliberately excluded so that only the
   reward may vary across arms — the reward channel is the *forced* injection point for tail-risk information,
   a design necessity rather than a convenience; and, by the same results, that channel is structurally unable
   to guarantee CVaR-optimality. The principled remedy — a distributional/quantile critic — is exactly the
   secondary TQC experiment of Chapter 4. The Null branch is therefore *over-determined*: the envelope can fail to
   be realised at the *agent* stage for this structural reason, independent of the designer's responsiveness.

The pre-registered mapping of mechanism conditions to observable signatures is given in **Table 3.1**.

**Table 3.1 — Pre-registered mapping of mechanism conditions to observable signatures** (reproduced from `PREREGISTRATION.md` §1a).

| Mechanism condition | $H_2$-RA (Sharpe legs) | $H_2$-Tail (CVaR-5% legs) | Responsiveness | Reward-code differential |
|---|---|---|---|---|
| **Strict** ($\lambda>0$ selection **and** responsive designer) | separation possible | **separation** | $>0$ | tail constructs $\uparrow$ in distributional arm |
| **Weak** (acceleration only; matched compute) | tie | tie at the budget | $\ge 0$ | small/none |
| **Null** ($\lambda=0$ tail-blind selection **and** non-responsive designer) | **tie** | **tie** | $\le 0$ | none / reversed |

Under the frozen design, selection is tail-blind ($\lambda = 0$), which places the study on the boundary between
the Strict and Null branches and makes *designer responsiveness* the pivotal unknown. The directional prototype
exhibited *negative* responsiveness and a tail differential that reversed under the zero-information placebo control
(Chapter 5), which is the **signature of the Null branch**. We therefore pre-register the Null branch as the
predicted outcome, with the explicit, theory-derived reason: a tail-blind selector combined with a designer that
does not condition on the fed magnitudes leaves no channel through which the dominance envelope of §3.4 can be
realised. A confirmed Null is then not an absence of evidence but a *corroborated prediction about the gap between
the information-theoretic envelope and its bounded realisation* — and, by the robustness duality of §3.6, a
statement that the tested language model does not, at this budget, exploit available distributional-robustness
information. This is the sense in which the theory makes a clean null a positive scientific result.

## 3.8 Summary of theoretical contributions

The chapter contributes a self-contained account of the value of tail-risk feedback to an automated reward
designer, organised around four results. (i) *Dominance*: because the scalar is a measurable garbling of the tail
vector, the vector Blackwell-dominates it for every loss and prior (Prop. 3.2), with a Le Cam-deficiency bound on
the scalar's worst-case excess risk (Cor. 3.3) and an equivalent data-processing-inequality form. (ii)
*Sufficiency*: the multi-level CVaR vector spans the coherent-risk class (Kusuoka), is sufficient *relative to the
scalar* (the garbling fact), and is — separately — a jointly (higher-order) elicitable, identifiable target that a
single coherent number provably cannot be (§3.5). (iii)
*Robustness*: by CVaR duality, tail feedback is a distributional-robustness signal whose benefit is predicted to
concentrate under the sealed out-of-sample distribution shift (§3.6). (iv) *Falsifiable realisation*: the dominance
is an envelope attainable only under stated selection-sensitivity, responsiveness and attainability conditions,
which we bind to a pre-registered prediction table, yielding a study whose null and non-null outcomes are each a
decided prediction (§3.7). Together these convert "richer feedback ought to help" from an intuition into a precise,
honest, and testable theory — one that frames the empirical chapters not as a search for a win but as a measurement
of the distance between what an optimal user of the lower tail could achieve and what a bounded language-model
reward-designer, coupled to a fixed agent under tail-blind selection, actually does.
