## The classical-allocator floor: what nine published estimators earn in the same costed environment

<!-- REWRITTEN 2026-08-11. THE FILE CARRIED ~1,050 WORDS OF RUNNING ARGUMENTATIVE PROSE, WHICH IS THE
     INTEGRITY EXPOSURE CLAUDE.md 95+ DOCTRINE §2 NAMES: prose in a wired `paper/tables/*.md` file is
     not counted by word_budget.BODY_CHAPTERS, so the honest in-body prose total sat above the
     instrument's figure. The doctrine's own instruction is to "close it by CUTTING the
     meta-commentary rather than by relying on it", and that is what this rewrite does.
     WHAT WENT: the "what the table establishes" essay, the "honest caveats" list and the
     "why this matters for the thesis" paragraph, all three of which restated in prose what the
     panels already show. WHAT STAYED, because each is a claim a marker must be able to check and
     none is derivable from the numbers alone: environment soundness, the DeMiguel reading, the
     estimation-error account of min_cvar, the gross-against-net mechanism, the interval caveat, and
     the two-uncertainties caveat. Each is now one sentence, in a caption, where the guide's own
     word-count clause puts it.
     PANELS B AND C WERE MERGED. Panel C repeated Panel B's whole net column and added gross with two
     intervals; one panel now carries gross, net, the net interval and the three risk columns. The
     gross interval and the CI-width column went: the argument is about the net column, and a width
     is the difference of two numbers printed beside it. -->

Each allocator is rolled through the identical costed environment the learned agents trade in, over the archive's own 1,571-session evaluation window, read from the records' `env_fingerprint` and never from a calendar filter. Every Sharpe is annualised and raw, in the original reward-to-variability sense [`sharpe1966mutualfund`], and every one is labelled gross or net. Views-based construction, where a subjective forecast is blended with an equilibrium prior [`black1992litterman`], is excluded on identification grounds, because it introduces an exogenous input the learned agents do not receive.

---

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 5.9 — Nine published allocators, one costed environment.** The allocator that estimates nothing ties the top of the net column while the tail-optimal one finishes last, so what a strategy pays to trade separates the column more than what it estimates.
```{=latex}
\par\endgroup
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Panel A — what each allocator estimates, and the published estimator it comes from.**
```{=latex}
\par\endgroup
```

| Allocator | What it estimates | Source |
|---|---|---|
| **`equal_weight`** (1/N) | **nothing** | [`demiguel2009naive`] |
| `maximum_`\allowbreak`diversification` | the diversification ratio | [`choueifaty2008maxdiv`] |
| `inverse_`\allowbreak`volatility` | per-asset volatility only (correlation-blind) | [`maillard2010erc`] |
| `risk_parity` | equal risk contributions | [`maillard2010erc`; `spinu2013riskparity`] |
| `cross_`\allowbreak`sectional_`\allowbreak`momentum` | past-return ranks | [`jegadeesh1993momentum`] |
| `mean_variance` | the full covariance matrix, shrunk | [`markowitz1952portfolio`; `ledoit2004honey`] |
| `hrp` | a clustering of the correlation matrix | [`lopezdeprado2016hrp`] |
| `minimum_variance` | the full covariance matrix | [`clarke2011minvar`] |
| **`min_cvar`** (tail-optimal) | **the 5% tail — from 3 of 60 observations** | [`rockafellar2000cvar`] |

```{=latex}
\begingroup\tabcaptionstyle
```
**Panel B — what each one earned, gross and net, with the net interval.** CVaR-5% is the mean daily loss over the worst 5% of sessions and turnover is the fraction of the book traded per session. Bold marks the best in a column and italic the worst. Every interval is about 1.4 Sharpe units wide, which is wider than the spread of the column, so the ordering of the top eight is not statistically separated and nothing in this dissertation rests on it. What the intervals do support is the environment-soundness claim: eight of the nine exclude zero, on the same environment on which ten of the eleven hand-written rewards lose money net. The separation lives between gross and net. `maximum_diversification` is the best allocator gross and only ties `equal_weight` net, because it trades 7.1% of the book a day against 0.5%, which is this dissertation's own mechanism reproduced on published estimators no language model wrote.
```{=latex}
\par\endgroup
```

| Allocator | Gross | Net | 95% CI (net) | CVaR-5% | MaxDD | Turn/day |
|------|---:|---:|---:|---:|---:|---:|
| **`equal_weight`** (1/N) | 1.283 | **1.274** | [+0.580, +1.967] | −0.0194 | 0.199 | **0.5%** |
| `maximum_`\allowbreak`diversification` | **1.403** | **1.274** | [+0.535, +2.016] | −0.0187 | **0.164** | 7.1% |
| `inverse_`\allowbreak`volatility` | 1.214 | 1.199 | [+0.499, +1.892] | −0.0201 | 0.207 | 0.8% |
| `risk_parity` | 1.218 | 1.193 | [+0.493, +1.886] | −0.0198 | 0.202 | 1.4% |
| `cross_`\allowbreak`sectional_`\allowbreak`momentum` | 1.240 | 1.102 | [+0.379, +1.816] | −0.0228 | 0.210 | 9.1% |
| `mean_variance` | 1.232 | 1.054 | [+0.277, +1.810] | −0.0235 | 0.294 | 11.7% |
| `hrp` | 1.145 | 0.979 | [+0.263, +1.698] | −0.0186 | 0.199 | 8.8% |
| `minimum_variance` | 1.047 | 0.907 | [+0.145, +1.667] | **−0.0174** | 0.187 | 7.0% |
| **`min_cvar`** (tail-optimal) | *0.737* | *0.602* | [−0.178, +1.340] | −0.0197 | 0.228 | 7.6% |

Four passive references run over the same 1,571 sessions, each named with its universe, its rebalancing rule and its cost treatment, because two different portfolios have been called equal-weight buy-and-hold elsewhere and they do not carry the same number. The same 30 names bought once and never rebalanced earn +1.258 with realised turnover of $2.1\times10^{-5}$ a session, so the rebalancing convention is worth about 0.025 Sharpe. The equal-weighted 963-name universe proxy earns +1.166 uncosted and the S&P 500 total-return index +1.130 uncosted. Two exclusions are recorded: `spy_buy_and_hold` duplicates the 1/N floor, so nine allocators enter and not ten, and these single deterministic paths carry a block-bootstrap interval over one realised window, which answers a different question from the agents' seed intervals and must not be read as though it carried the same uncertainty.

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 5.9b — The estimation-error test behind `min_cvar`'s last place.** In-sample against out-of-sample CVaR-5% at the registered 60-session lookback, ordered by how much estimation each allocator performs, computed on the panel's own returns so that estimation is isolated from the costs and projection Table 5.9 also applies.
```{=latex}
\par\endgroup
```

| | in-sample CVaR | out-of-sample | **degradation** |
|---|---|---|---|
| `min_cvar` (optimises 3 of 60 obs) | −0.0105 **(rank 1)** | −0.0197 (rank 3) | *88%* |
| `minimum_variance` (covariance, all 60) | −0.0133 | **−0.0173 (rank 1)** | 30% |
| `risk_parity` | −0.0179 | −0.0198 | 10% |
| `equal_weight` (**estimates nothing**) | −0.0186 | −0.0193 | **4%** |

The best strategy in the table fits no parameter. The environment is not the problem, and the rewards' blindness to movement is.