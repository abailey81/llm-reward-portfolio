# Campaign overfitting — PBO / CSCV (PREREGISTRATION §10; primary guard)

CSCV blocks S = 16 (`config/inference.yaml: pbo.n_blocks`). PBO is computed PER ARM over that arm's candidates' per-period validation returns (`src.inference.overfitting.pbo`). PBO near/above 0.5 = severe overfitting; near 0 = in-sample-best stays good out-of-sample.

| arm | n candidates | T_val | PBO | status |
|---|---|---|---|---|
| distributional | 39 | 695 | 0.188 | ok |
| scalar | 40 | 695 | 0.072 | ok |
| placebo | 40 | 695 | 0.483 | ok |
| scalar_cvar5 | 40 | 695 | 0.088 | ok |
| random_search | 40 | 695 | 0.344 | ok |
| bayes_opt | 40 | 695 | 0.542 | ok |

## Second PBO ranked on the DSR-proxy (per-block Sharpe) — guards the SELECTION rule (R36; M3)

CSCV blocks S = 16. The frozen PRIMARY PBO (`src.inference.overfitting.pbo`, UNCHANGED) ranks IS/OOS on the MEAN validation return; winner SELECTION used the validation **DSR** (`src.selection.fitness`, monotone in per-series Sharpe at the frozen λ=0). This SECOND column ranks on the per-block annualised SHARPE — the DSR-proxy. Close agreement ⇒ the mean-return proxy empirically guards the rule the campaign actually USED (DEEP_STATS A3 point 2). Report-only, additive; the frozen guard is the mean-return column.

| arm | n candidates | PBO (mean-return, PRIMARY) | PBO (per-block Sharpe / DSR-proxy) | |Δ| | status |
|---|---|---|---|---|---|
| distributional | 39 | 0.188 | 0.164 | 0.024 | ok |
| scalar | 40 | 0.072 | 0.104 | 0.032 | ok |
| placebo | 40 | 0.483 | 0.438 | 0.045 | ok |
| scalar_cvar5 | 40 | 0.088 | 0.091 | 0.003 | ok |
| random_search | 40 | 0.344 | 0.322 | 0.021 | ok |
| bayes_opt | 40 | 0.542 | 0.530 | 0.012 | ok |

# Campaign headline Deflated Sharpe — canonical cross-trial variance (Rank 16; secondary)

Per arm: the WINNER's validation Deflated Sharpe recomputed with the empirical cross-candidate Sharpe dispersion `var_sr = Var(per-candidate val Sharpes, ddof=1)` (canonical Bailey-Lopez de Prado) versus the within-series `var_sr=None` proxy the WIRED selection path records. DSR is SECONDARY (PBO/CSCV is primary).

| arm | n candidates | winner | winner Sharpe | var_sr | DSR (canonical) | DSR (proxy) | status |
|---|---|---|---|---|---|---|---|
| distributional | 39 | distributional-g3-c0 | 0.3847 | 0.0005 | 0.2498 | 0.0614 | ok |
| scalar | 40 | scalar-g7-c3 | 0.5826 | 0.0005 | 0.3547 | 0.1100 | ok |
| placebo | 40 | placebo-g4-c1 | 0.1486 | 0.0004 | 0.2003 | 0.0260 | ok |
| scalar_cvar5 | 40 | scalar_cvar5-g0-c4 | 0.5282 | 0.0006 | 0.2855 | 0.0947 | ok |
| random_search | 40 | random_search-c3 | 0.3392 | 0.0006 | 0.1837 | 0.0518 | ok |
| bayes_opt | 40 | bayes_opt-c2 | 0.0793 | 0.0006 | 0.1082 | 0.0198 | ok |

## H2 (distributional feedback) — neither (null) (BH)

Two CO-PRIMARY intersection-union tests (R25; DEEP_H2 §7.1), each decided ONE-SIDED at α=0.05 in the predicted direction with NO leg correction (the conjunction IS the correction — Berger 1982). Per-seed rliable inference (IQM + paired across-seed bootstrap; Agarwal et al. 2021).

- **H2-RA (risk-adjusted, Sharpe IUT):** NOT supported
- **H2-Tail (tail outcome, CVaR-0.05 IUT):** NOT supported — corroborated (not gated) by the FZ0/(VaR,ES) comparative ES backtest where available.

### H2-RA — risk-adjusted (Sharpe) legs

| contrast | reject (1-sided) | direction_ok | leg_supported |
|---|---|---|---|
| distributional>scalar | False | False | False |
| distributional>placebo | False | False | False |
| distributional>scalar_cvar5 | False | False | False |

### H2-Tail — tail-outcome (CVaR-5%) legs

| contrast | reject (1-sided) | direction_ok | leg_supported |
|---|---|---|---|
| distributional>scalar | False | False | False |
| distributional>placebo | False | False | False |
| distributional>scalar_cvar5 | False | False | False |

Missing contrasts (unsupported, not fabricated): distributional>scalar, distributional>placebo, distributional>scalar_cvar5

## H2 TOST equivalence (DEEP_H2 §5.3) — n/a

no H2 contrast has >= 2 shared test seeds

## Structure-vs-content control (R32) — n/a

placebo_shuffled has no test record sharing >= 2 seeds with distributional

## H3 — iterative reflection vs single-shot (DEEP_H3) — n/a

single-shot archive absent (test_h3_singleshot/<arm> not provided — a separate manually-launched run, DEEP_H3 §2.3/§2.4)

*(H3 is a separate, manually-launched single-shot run; absent ⇒ skipped, not fabricated.)*

## H4 — LLM vs search controls (DEEP_H4) — n/a

LLM winner arm 'distributional' has < 2 test seeds (test/baseline stage not run?)

## DSR sensitivity — raw N vs effective N under sequential-reflective correlation (DEEP_STATS A1)

Winner arm `distributional`. The reflect-on-best search makes the N=39 candidates correlated (mean pairwise validation-return correlation ρ̄), so the i.i.d. expected-max-Sharpe assumption is violated. N_eff = N/(1+(N−1)·ρ̄) is the mean-correlation surrogate (ONC is canonical).

- ρ̄ (mean off-diagonal candidate correlation): **0.7980**
- N (naïve) = 39 → DSR = **0.2498**
- N_eff = 1 → DSR = **0.7376**

Direction is benign: ρ̄>0 ⇒ N_eff<N ⇒ smaller deflation ⇒ higher DSR, so the naïve N is the CONSERVATIVE choice and any floor/H1 PASS at naïve N is robust to the trial-count dispute (DEEP_STATS A8).

## Delisting-return sensitivity band (R33; §7) — n/a

delisting band needs the univ3 panel + audit log: [Errno 2] No such file or directory: 'C:\\Users\\User\\Desktop\\dissertation_papers\\llm-reward-portfolio\\data\\clean\\shumway_audit_log_univ3.parquet'

## EVT-consistency guard — fed CVaR estimator across tail-fed arms — CONSISTENT

Re-derived per arm winner's validation distribution: which estimator the FED CVaR level routes to ('evt' / 'empirical' / 'empirical(fallback)' = the `alpha>fu`/degenerate-fit fallback in `_evt_cvar`). Inconsistency across tail-fed arms means the distributional-vs-scalar_cvar5 tail comparison mixes estimators (DEEP_H2 §6.3). Report-only — logged, never raised.

| arm | CVaR 0.05 path | CVaR 0.01 path |
|---|---|---|
| distributional | evt | evt |
| scalar_cvar5 | evt | evt |

Per-level consistency: CVaR 0.05 = True, CVaR 0.01 = True.

## Training-divergence diagnostic — diverged-RUN count + rate (R34; report-only, DISJOINT)

Anomaly monitoring writes every `critic_explosion` event to one append-only `anomalies.jsonl` per run, so the LINE count over-states how many distinct RUNS diverged. Events are clustered into RUNS by step-reset (a step that goes backwards = a new training). Report-only: the trainer is unchanged.

- Anomaly LINES (`critic_explosion`): **64**
- Diverged RUNS (clustered by step-reset): **6**  (of which 3 single-step/transient)
- Divergence rate (runs / 210 candidate-trainings): **0.0286 (2.86%)**
- NO winner's training diverged  *(attribution: unavailable (anomaly schema carries no candidate_id))*

**Disclosure.** The reward is UNBOUNDED on purpose (`norm_reward=False` is DELIBERATE — the reward is the object of study, so its scale is left as authored), so a mis-scaled candidate can transiently blow the critic loss up. But a diverged candidate scores POORLY on the held-out validation fitness and LOSES selection, so divergence biases toward NOISE in the dropped tail, NOT toward the H2 headline (a diverged candidate becomes a winner only if it ALSO posted a strong sealed validation Sharpe).

## Compute-accounting — candidates + token usage per arm (R35; report-only, DISJOINT)

Per arm, from the archived `failures.jsonl` + `llm_calls.jsonl`: candidates ATTEMPTED / ACCEPTED (passed the gate + evaluated) / FAILED the gate, and total prompt (input) tokens. Report-only; DISJOINT from the frozen m=6 family.

| arm | kind | LLM calls | accepted | failed | attempted | resamples? | prompt tok | completion tok | tail-fed |
|---|---|---|---|---|---|---|---|---|---|
| distributional | llm | 40 | 39 | 1 | 40 | no | 23040 | 51549 | yes |
| scalar | llm | 40 | 40 | 0 | 40 | no | 19750 | 47008 | no |
| placebo | llm | 40 | 40 | 0 | 40 | no | 22445 | 46944 | no |
| scalar_cvar5 | llm | 40 | 40 | 0 | 40 | no | 20205 | 48875 | yes |
| random_search | search | 0 | 40 | 0 | 40 | yes | 0 | 0 | no |
| bayes_opt | search | 0 | 40 | 0 | 40 | yes | 0 | 0 | no |

Totals: accepted **239**, failed **1**, prompt-tokens **85,440**, completion-tokens **194,376**.

**Disclosure.** (i) LLM arms BURN a budget slot on a gate failure (src/llm/loop.py ~338,380) while search arms RESAMPLE to a full valid slate (src/search/random_search.py ~259), so search gets strictly MORE valid candidates per matched budget — a handicap on the LLM arms, conservative for the H2 headline. (ii) Tail-aware blocks send ~8 feedback lines vs scalar's 1; that token-count difference is controlled by the inert placebo leg in the H2 placebo contrast.

## Cross-hypothesis multiplicity — Bonferroni-across-4 SENSITIVITY (DEEP_STATS A4; report-only)

Per-hypothesis families are PRIMARY (pre-registered separate estimands); this programme-wide Bonferroni-across-4 is a REPORTED sensitivity only (DEEP_STATS A4/C4), not the headline gate.

Programme-wide Bonferroni level α/4 = 0.0125 (per-hypothesis α = 0.05).

| hypothesis | headline p | primary decision | survives Bonferroni-4 | note |
|---|---|---|---|---|
| H1 | — | (skipped) | n/a | descriptive panel, no inferential p (DEEP_H1 R-REF) — Bonferroni n/a |
| H2 | — | neither (null) | n/a | max one-sided p over the two co-primary IUT leg sets (the conjunction's binding leg) |
| H3 | — | (skipped) | n/a | one-sided iterative>single-shot difference p (if the single-shot archive was present) |
| H4 | — | (skipped) | n/a | max one-sided p over {H4a, H4b} |

## H1 — beat-the-human (Eureka-style; §1 / §9) — n/a

no test records for the LLM winner arm 'distributional' (baseline stage / records-only?)
