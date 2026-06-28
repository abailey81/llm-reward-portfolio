# Prototype analysis — DIRECTIONAL (plumbing only; no number enters the dissertation)

**Verdict: AMBER** (MASTER_EXECUTION_PLAN §6.1; Henderson 1-seed = directional).

## Per-arm (winner validation Deflated Sharpe + rliable IQM of the candidate population)
| arm | n | winner fitness | IQM | IQM 95% CI |
|---|---|---|---|---|
| bayes_opt | 40 | +0.01981 | +0.00215 | [+0.00116, +0.00375] |
| distributional | 39 | +0.06015 | +0.00273 | [+0.00134, +0.00541] |
| placebo | 40 | +0.02598 | +0.00178 | [+0.00119, +0.00295] |
| random_search | 40 | +0.05180 | +0.00274 | [+0.00112, +0.00481] |
| scalar | 40 | +0.10999 | +0.00278 | [+0.00144, +0.00470] |
| scalar_cvar5 | 40 | +0.09473 | +0.00224 | [+0.00116, +0.00417] |

## Interpretability (the mechanism gate)
- distributional winner uses tail/risk terms: **True** (found: cvar, drawdown, min(, sort, std, var)

## Difference tests (LLM-arm winners; stationary-bootstrap)
- **distributional_vs_scalar**: Sharpe Δ p=0.411 (stat -0.821); CVaR Δ p=0.004 (stat +2.903)
- **distributional_vs_placebo**: Sharpe Δ p=0.281 (stat +1.052); CVaR Δ p=0.000 (stat -4.277)
- **distributional_vs_scalar_cvar5**: Sharpe Δ p=0.508 (stat -0.651); CVaR Δ p=0.150 (stat +1.456)

## Notes
- PBO/CSCV and the FZ comparative-ES forecast backtest are campaign tools (CPCV folds / common test set) — implemented in `src/inference/` and run in the campaign, not on this 1-seed prototype.
- Delisting=`liquidate_to_cash` + the held 2005 cohort bias the measured tails (review M3/M4): this verdict is a go/no-go on the mechanism, not a result.