# Nomenclature

> **Status: structural scaffold (2026-06-28).** Notation and abbreviations used across the Theory (Ch. 3),
> Methods (Ch. 4), Prototype (Ch. 5), Results (Ch. 6) and Discussion (Ch. 7) chapters.
> **To be reconciled against the theory chapter's exact sign conventions at compile** — in particular the sign of
> CVaR / left-tail quantities (this document follows the convention in which a *more negative* CVaR_α denotes a
> *worse* left tail, consistent with realised-return losses), the orientation of robust skew, and the exact
> definition of the SESOI units. Where Chapter 3 or Chapter 4 fixes a convention, that chapter governs.

---

## Notation (symbols)

| Symbol | Definition | First use |
|---|---|---|
| $\lambda$ | Risk-aversion weight in the candidate-selection fitness; **$\lambda=0$ = tail-blind selector** (the pre-registered choice, so any tail effect must arise from the feedback channel, not the selector). | Ch. 3 (§3.7), Ch. 4 (§4.6) |
| $\mathrm{CVaR}_\alpha$ | Conditional value-at-risk (expected shortfall) at level $\alpha$ of the realised-return **lower tail**; fed at $\alpha\in\{5\%,10\%,25\%,1\%\}$; tested headline at $\alpha=5\%$. | Ch. 3 (§3.3), Ch. 4 (§4.4) |
| $\mathrm{VaR}_\alpha$ | Value-at-risk at level $\alpha$ (the $\alpha$-quantile of the loss); appears jointly with $\mathrm{CVaR}_\alpha$ in the elicitability argument. | Ch. 3 (§3.5) |
| $\xi$ | Extreme-value (generalised-Pareto, GPD) **shape** parameter of the peaks-over-threshold tail fit; empirical fallback used in the non-regular region $\xi \le -0.5$. | Ch. 4 (§4.4) |
| $E$ | **Embargo** length at split boundaries = **21** trading sessions. | Ch. 4 (§4.2) |
| $L$ | Feature **lookback** window = **60** trading sessions (also the loss in the Blackwell argument; disambiguated by context — Ch. 3 uses $L$ for loss, Ch. 4 for lookback). | Ch. 4 (§4.2) |
| purge | Boundary purge $=\max(\text{embargo}=21,\ \text{lookback}=60)=\mathbf{60}$ sessions; must cover the feature lookback, not merely the embargo. | Ch. 4 (§4.2) |
| $d$ | **Delisting-return band** applied to affected cells: $d\in\{0,-30,-55,-100\}\%$; headline panel uses $d=0$ (zero-fill, conservative). | Ch. 4 (§4.2) |
| $\theta$ | Index of the state of nature (features of the realised-return law) about which the feedback experiment is informative. | Ch. 3 (§3.3) |
| $P_\theta,\ Q$ | Realised-return law(s) under state $\theta$; $P,Q$ as "benign-tail" vs "adverse-tail" laws in the divergence argument. | Ch. 3 (§3.3–3.4) |
| $E_{\mathrm{vec}},\ E_{\mathrm{scalar}}$ | The two feedback experiments: the multi-level tail **vector** vs the **scalar** summary ($E_{\mathrm{scalar}}=g\circ E_{\mathrm{vec}}$, a garbling). | Ch. 3 (§3.3) |
| $\mathbf c(P_\theta)$ | The fed six-component tail vector: $(\mathrm{CVaR}_{5\%,10\%,25\%,1\%},\ \text{left-tail mass beyond }-2\sigma,\ \text{robust left-tail skew})$. | Ch. 3 (§3.3), Ch. 4 (§4.4) |

---

## Abbreviations

| Abbreviation | Definition | First use |
|---|---|---|
| SESOI | Smallest effect size of interest; pre-registered at **±0.05 Deflated-Sharpe (DSR) units** for the TOST equivalence margin. | Ch. 4 (§4.7) |
| MDE | Minimum detectable effect (at 80% power); disclosed to exceed the SESOI, so a clean equivalence rests on the interval. | Ch. 4 (§4.7) |
| DSR | Deflated Sharpe ratio (Sharpe corrected for multiplicity/non-normality of the search). | Ch. 4 (§4.6) |
| IQM | Interquartile mean (robust per-seed score reduction in the `rliable` protocol). | Ch. 4 (§4.7) |
| FZ0 | Fissler–Ziegel (FZ0) jointly-elicitable scoring function for the VaR/ES comparative backtest. | Ch. 4 (§4.7) |
| DM-HLN | Diebold–Mariano comparison with the Harvey–Leybourne–Newbold small-sample correction. | Ch. 4 (§4.7) |
| PBO / CSCV | Probability of backtest overfitting, via combinatorially symmetric cross-validation (primary overfitting guard). | Ch. 4 (§4.7) |
| IUT | Intersection–union test; the H2 conjunction is size $\le\alpha$ by construction (the multiplicity correction). | Ch. 4 (§4.7) |
| TOST | Two one-sided tests; the equivalence procedure reporting a null as a bounded equivalence vs the SESOI. | Ch. 4 (§4.7) |
| EPIC / STARC | Regret-bounded reward pseudometrics for quantifying distance between authored reward functions. | Ch. 3 (§3.2), Ch. 6 (§6.5) |
| PIT | Point-in-time (universe construction; no security enters before it was constituent). | Ch. 4 (§4.2) |
| SAC | Soft actor–critic (the fixed reinforcement-learning agent, held byte-identical across arms). | Ch. 4 (§4.3) |
| TQC | Truncated-quantile critic (named secondary: mean critic vs quantile critic). | Ch. 4 (§4.3) |
| PopArt | Adaptive value-target normaliser applied uniformly across arms (manages reward-scale heterogeneity; preserves realised-return series). | Ch. 4 (§4.3) |
| EVT / GPD | Extreme-value theory / generalised-Pareto distribution (peaks-over-threshold tail estimation). | Ch. 4 (§4.4) |
| ES | Expected shortfall (used interchangeably with CVaR for the tail; FZ0 backtest target). | Ch. 4 (§4.4, §4.7) |
| rliable | Reliable RL-evaluation protocol (IQM, stratified bootstrap, per-seed intervals). | Ch. 4 (§4.7) |

*(Compile note: where a symbol is overloaded — notably $L$ for loss vs lookback, and the sign of CVaR/skew —
state the convention once at first use and key this table to the governing chapter.)*
