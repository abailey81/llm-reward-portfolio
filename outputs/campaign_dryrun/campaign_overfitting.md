# Campaign overfitting — PBO / CSCV (PREREGISTRATION §10; primary guard)

CSCV blocks S = 16 (`config/inference.yaml: pbo.n_blocks`). PBO is computed PER ARM over that arm's candidates' per-period validation returns (`src.inference.overfitting.pbo`). PBO near/above 0.5 = severe overfitting; near 0 = in-sample-best stays good out-of-sample.

| arm | n candidates | T_val | PBO | status |
|---|---|---|---|---|
| distributional | 4 | 200 | 0.390 | ok |
| scalar | 0 | 0 | n/a | skipped (need >= 2 candidates with validation vectors; got 0) |
| placebo | 0 | 0 | n/a | skipped (need >= 2 candidates with validation vectors; got 0) |
| scalar_cvar5 | 0 | 0 | n/a | skipped (need >= 2 candidates with validation vectors; got 0) |
| random_search | 0 | 0 | n/a | skipped (need >= 2 candidates with validation vectors; got 0) |
| bayes_opt | 0 | 0 | n/a | skipped (need >= 2 candidates with validation vectors; got 0) |

# Campaign headline Deflated Sharpe — canonical cross-trial variance (Rank 16; secondary)

Per arm: the WINNER's validation Deflated Sharpe recomputed with the empirical cross-candidate Sharpe dispersion `var_sr = Var(per-candidate val Sharpes, ddof=1)` (canonical Bailey-Lopez de Prado) versus the within-series `var_sr=None` proxy the WIRED selection path records. DSR is SECONDARY (PBO/CSCV is primary).

| arm | n candidates | winner | winner Sharpe | var_sr | DSR (canonical) | DSR (proxy) | status |
|---|---|---|---|---|---|---|---|
| distributional | 4 | distributional-g0-c1 | -0.7821 | 0.0000 | 0.2470 | 0.0423 | ok |
| scalar | 0 | n/a | n/a | n/a | n/a | n/a | skipped (need >= 2 candidates with validation vectors for a cross-trial variance; got 0) |
| placebo | 0 | n/a | n/a | n/a | n/a | n/a | skipped (need >= 2 candidates with validation vectors for a cross-trial variance; got 0) |
| scalar_cvar5 | 0 | n/a | n/a | n/a | n/a | n/a | skipped (need >= 2 candidates with validation vectors for a cross-trial variance; got 0) |
| random_search | 0 | n/a | n/a | n/a | n/a | n/a | skipped (need >= 2 candidates with validation vectors for a cross-trial variance; got 0) |
| bayes_opt | 0 | n/a | n/a | n/a | n/a | n/a | skipped (need >= 2 candidates with validation vectors for a cross-trial variance; got 0) |

## H2 (distributional feedback) — NOT supported (BH)

Per-seed rliable inference (IQM + paired across-seed bootstrap); conjunction over the three legs.

| contrast | sharpe_reject | direction_ok | leg_supported |
|---|---|---|---|
| distributional>scalar | False | False | False |
| distributional>placebo | False | False | False |
| distributional>scalar_cvar5 | False | False | False |

Missing contrasts (unsupported, not fabricated): distributional>scalar, distributional>placebo, distributional>scalar_cvar5

## H1 — beat-the-human (Eureka §18-19) — n/a

no test records for the LLM winner arm 'distributional' (baseline stage / records-only?)
