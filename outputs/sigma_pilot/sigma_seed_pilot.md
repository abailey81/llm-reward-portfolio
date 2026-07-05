# σ_D / ρ pilot — clean seeds-on-winners power measurement

Two FIXED rewards (`differential_sharpe`, `return_minus_cvar`) re-trained across a SHARED seed set (Common Random Numbers). Measures the per-arm seed SD (σ_seed, the `power_analysis --sigma-seed` input), the paired-difference SD (σ_D), and the pairing correlation (ρ, the `--rho` input). The seed-count decision keeps `n_seeds = 30` iff the 80%-power MDE maps below the 0.05-DSR SESOI; otherwise it raises n, or reports bounded-effect/INCONCLUSIVE.

| statistic | n | σ_a | σ_b | σ_seed | σ_D | ρ | CRN helps (ρ>0) |
|---|---|---|---|---|---|---|---|
| sharpe | 15 | 0.2579 | 0.2297 | 0.2442 | 0.3688 | -0.141 | NO (ρ≤0) |
| cvar_05 | 15 | 0.0016 | 0.0012 | 0.0014 | 0.0015 | 0.467 | yes |

## Seed-count decision (Sharpe / H2-RA leg)
k₈₀(ρ=-0.141) = 0.710 · SESOI = 0.050 DSR · T = 694.

| n_seeds | MDE@80% (Sharpe) | MDE@80% (DSR) | ≤ SESOI? |
|---|---|---|---|
| 30 | 0.1734 | 0.1147 | — |
| 35 | 0.1605 | 0.1062 | — |
| 40 | 0.1502 | 0.0993 | — |
| 45 | 0.1416 | 0.0937 | — |
| 50 | 0.1343 | 0.0889 | — |

**Decision: equivalence NOT achievable on the seed grid** → report a rigorous **bounded-effect / INCONCLUSIVE** result (the pre-committed null framing), not equivalence. (Raising seeds further has diminishing returns; the binding quantity is σ_seed/SESOI, not n.)

> ⚠ Measured ρ ≤ 0: Common Random Numbers provide **no** variance reduction here (σ_D ≥ √(σ_a²+σ_b²)). The closed-form preview understates the MDE — trust the Monte-Carlo `power_analysis.py` figure below (its simulator draws the measured NEGATIVE ρ exactly since the signed-ρ fix, 2026-07-03; it previously clamped ρ to 0 and would have understated too).

## Authoritative MDE (Monte-Carlo)
Re-run the real paired-bootstrap power simulator with the measured inputs to finalise `docs/CAMPAIGN_power.md`:
```bash
python -m scripts.power_analysis --sigma-seed 0.2442 --rho -0.1409 --n-seeds 30 --out docs/CAMPAIGN_power.md
```
