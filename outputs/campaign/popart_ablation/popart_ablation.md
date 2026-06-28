# PopArt scale-dependence ablation (`popart=False`; T2.4)

Frozen winners RE-TRAINED with the PopArt value-target scaler DISABLED, at a SINGLE seed (seed=0), then evaluated on the sealed test leg once per arm. The question: is the H2 ordering (`distributional` > `scalar`) an effect of the reward, or an artefact of the scale-dependent entropy regularisation PopArt induces (`ent_coef=auto` adapts to `raw/sigma`)? If the ordering holds with PopArt removed, the headline is robust to the wrapper.

## H2 ordering verdict (primary contrast: distributional vs scalar)

- Sharpe: `distributional − scalar` = **+0.0000** (FLIPPED ✗)
- CVaR-0.05: `distributional − scalar` = **+0.00000** (FLIPPED ✗)

**Overall: H2 ordering NOT preserved without PopArt.**

## Per-arm metrics without PopArt

| arm | test Sharpe | test CVaR-0.05 | n steps |
|---|---|---|---|
| distributional | -1.0215 | -0.01779 | 180 |
| scalar | -1.0215 | -0.01779 | 180 |
| placebo | — | — | — |
| scalar_cvar5 | — | — | — |

Sharpe ranking (best→worst): distributional > scalar

CVaR-0.05 ranking (best→worst): distributional > scalar

## Skipped arms (no usable frozen winner)

- `placebo`: no frozen winner with an executable reward_source
- `scalar_cvar5`: no frozen winner with an executable reward_source

## Realised PopArt scale at the ablation seed (audit)

The `popart=True` re-train's realised `sigma_max` per arm (1.0 ⇒ the wrapper was the identity for that reward ⇒ no scale-driven entropy-regularisation difference):

| arm | sigma_max | sigma_last |
|---|---|---|
| distributional | 1 | 1 |
| scalar | 1 | 1 |
