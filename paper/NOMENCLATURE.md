# Glossary and abbreviations

For the reader from another discipline. Each term is defined the way it is used here. Every symbol is
also defined where it is first used. Sign convention: returns are signed, so a more negative CVaR denotes
a worse left tail, and where Chapter 4 or Appendix C states a convention, that chapter governs.

| Term | Meaning here | First use |
|---|---|---|
| Agent, policy | the trained decision-maker, and its rule mapping observations to portfolio weights | §4.3 |
| Arm | one experimental condition. Nine arms run: five language-model and four search-optimiser | §4.5 |
| Bootstrap | estimating uncertainty by resampling the observed data | §4.7 |
| Canon | the eleven hand-written reward functions that set the human bar. The word names those eleven programs and nothing else | §4.6 |
| Coherent risk measure | a measure satisfying the four standard axioms, including rewarding diversification | §C.5 |
| CVaR, ES | conditional value-at-risk, used interchangeably with expected shortfall: the average loss in the worst $\alpha$% tail. Fed at $\alpha \in \{1, 5, 10, 25\}$%, tested at 5% | §4.4 |
| DM-HLN | Diebold-Mariano comparison with the Harvey-Leybourne-Newbold small-sample correction | §4.7 |
| DSR | deflated Sharpe ratio: Sharpe corrected for how many strategies were tried and for fat tails, so lucky search winners are not mistaken for skill | §4.6 |
| The eleven-line grid | the 70 (line, arm) cells the confirmatory contrasts are drawn from. The H3 single-shot cell is a 71st and sits outside the grid | §5.1 |
| Elicitability | whether a risk measure can be validated by scoring point forecasts. ES alone cannot; (VaR, ES) jointly can | §C.5 |
| EPIC, STARC | regret-bounded pseudometrics for the distance between two authored reward functions | §5.5 |
| EVT, GPD | extreme-value theory and the generalised-Pareto peaks-over-threshold tail estimator | §4.4 |
| Feedback block | the short text of performance numbers shown to the model after each attempt. The only thing that differs between arms | §4.5 |
| FZ0 | the Fissler-Ziegel jointly elicitable scoring function for the VaR and expected-shortfall backtest | §4.7 |
| IQM | interquartile mean, the robust per-seed reduction the `rliable` protocol prescribes | §4.7 |
| IUT | intersection-union test: a claim required to hold against every comparator at once, so the conjunction is size $\le\alpha$ by construction | §4.7 |
| LLM | the text model that authors the reward code and revises it from feedback | §4.5 |
| MDE | minimum detectable effect at 80% power, disclosed to exceed the SESOI | §4.7 |
| PBO, CSCV | probability of backtest overfitting, via combinatorially symmetric cross-validation. The primary overfitting guard | §4.7 |
| PIT | point-in-time construction: no security enters the tradable set before it was a constituent | §3.1 |
| Placebo, scrambled control | the two control arms whose feedback carries no genuine information: six inert constants under neutral labels, and the six real tail values deranged across their labels. Together they isolate content from format | §4.5 |
| PopArt | the adaptive value-target normaliser applied uniformly across arms | §4.3 |
| Pre-registration | the analysis plan, frozen and hash-stamped before the decisive experiment, so results cannot quietly reshape the questions | §4.8 |
| Reflection loop | the generate, train, measure, feed back and revise cycle in which the model improves its reward code | §4.5 |
| Reinforcement learning | training a decision-maker by trial and error against a numerical reward | §4.3 |
| Replay buffer | the agent's rolling memory of past experience that training samples from | §4.3 |
| Responsiveness, transmission, specificity | the three mechanism sub-questions: does feedback change the code, do code changes reach realised risk, and is any change driven by genuine tail information | §5.5 |
| Reward function | the formula scoring each of the agent's actions during training. Here it is written as Python code by a language model | §4.5 |
| `rliable` | the reinforcement-learning evaluation protocol supplying the IQM, the stratified bootstrap and per-seed intervals | §4.7 |
| SAC | soft actor-critic, the fixed learner held byte-identical across arms | §4.3 |
| Sealed test set | the final years of data, untouched during development and used exactly once | §4.2 |
| SESOI | smallest effect size of interest, pre-registered at $\pm0.05$ DSR units for the equivalence margin | §4.7 |
| Sharpe ratio | average return divided by its volatility. Every Sharpe in this document is labelled gross or net | §4.6 |
| Survivorship bias, point-in-time | the error of studying only companies that survived, avoided by using membership as it was known on each historical day | §3.1 |
| TOST | two one-sided tests: the procedure that reports a null as a bounded interval against the SESOI, which is evidence for a null and not a failure to reject | §4.7 |
| TQC | truncated-quantile critic, the named secondary experiment against a mean critic | §4.3 |
| VaR | value-at-risk: the $\alpha$-quantile of the realised-return lower tail, appearing jointly with CVaR in the elicitability argument | §4.9 |
| Walk-forward backtest | evaluating strictly forward in time, so no future information leaks backwards | §4.6 |
