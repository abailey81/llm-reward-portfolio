# M2 — the cross-LLM numeracy + responsiveness survey: protocol v1 (pre-registered 2026-07-12)

> The Stage-2 FLAGSHIP (`STAGE2_PUBLISHABILITY_PLAN` TIER M). **Registered ex-ante: no Stage-1
> campaign data exists at the time of writing** (the pre-registration is freeze-ready, the campaign
> has not run). Descriptive survey with CIs; OUTSIDE every confirmatory family; no member of m = 6.
> Supervisor status: full delegated permission (Tamer, 2026-07-12, after Okhrati's email).
> Changes after Stage-1 unblinding require a dated amendment note here.

## 1. The question (one sentence)

Is the SQ1 responsiveness failure **general across LLMs and graded by capability** — i.e. does a
model's ability to *discriminate* close tail values predict whether its authored reward code *uses*
them — as the numeracy-bottleneck hypothesis (PREREG §2a) predicts?

## 2. Model roster (spanning labs AND the capability range — the gradient is the evidence)

Frontier: Claude Opus 4.8 · GPT-5.5-class · Gemini-class. Mid: Claude Sonnet 4.6 · Qwen3-Coder ·
Kimi-K2 · GLM-class · Llama-large · Mistral-large. **Deliberately weak:** Haiku-class · small open
models (7–9B). Final ids pinned at execution with served-snapshot archival (the Qwen pattern).
**Per-model gates before inclusion:** live smoke; contamination screen (cutoff-stratified); capability
floor = produces contract-valid reward code ≥ 50% of attempts (motivating datum: the 2026-07-11 live
rehearsal measured Qwen3-Coder producing sandbox-rejected code — e.g. `UnboundLocalError` — at a
nonzero rate; the reject rate per model is itself reported).

## 3. Probe families (each mirrors a frozen Stage-1 operationalization)

- **P-A Numeracy (discrimination):** "which of these two CVaR-5% values indicates worse tail risk?" —
  pairs of signed decimals in the fed format. **Difficulty anchored to the EMPIRICAL fed-delta
  distribution** (instrument (h) on the archived candidate tail vectors: |Δ| quantiles at
  {0.1, 0.25, 0.5, 0.75, 0.9} define the difficulty rungs), plus format variants from M3 (raw float /
  basis points / rank / CI-annotated). ~40 items/model.
- **P-B Ordering:** rank 4 candidates by a stated tail criterion from their 6-vectors (~10 items).
- **P-C Responsiveness-in-code:** the Stage-1 reflection prompt VERBATIM (same contract, same block
  schema) with controlled fed-vector deltas between consecutive turns → does the authored code change
  in the direction of the delta (SQ1's code-feature statistic, same extractor)? ~8 turns/model.
  placebo-shuffled variant on 2 turns as the within-survey control.
- All calls temperature-0 where the API honors it (else provider default, disclosed); every
  prompt/completion archived; one repetition of a 20% item sample for self-consistency.

## 4. Pre-named analysis (all descriptive, bootstrap-over-items 95% CIs)

1. Per-model **discrimination accuracy vs |Δ| rung** (the psychophysics curve) and vs format (the M3
   legibility lever, cross-model).
2. Per-model **responsiveness score** from P-C (the SQ1 statistic).
3. **The headline figure:** responsiveness (y) against numeracy accuracy (x) across models — Spearman
   rank correlation + CI. The numeracy-bottleneck prediction: strong positive association, with the
   fed-value difficulty regime (the −0.0577-vs−0.0582 zone) sitting in the low-accuracy region for
   most models.
4. A5 cross-read: accuracy on CI-ANNOTATED items minus raw items, per model (rational-insensitivity
   predicts annotation helps usage more than it helps accuracy; A2 predicts the reverse).
5. Reject-rate table (capability floor exhibit).

## 5. Cost, timing, safety

~12 models × ~60 calls ≈ 700–800 calls, short prompts → **≈ $5–10** (OpenRouter for open models;
native APIs otherwise). No agent, no seeds, no GPU. Runs the moment Stage 1 banks (M2 needs no
campaign outcome — but the fed-delta anchoring uses the campaign's ARCHIVED search vectors, so it
executes post-bank on Stage-1's own stimuli; a prototype-anchored dry run MAY be used to validate the
harness, marked directional-only). Touches nothing frozen; no forking paths (no confirmatory family
membership; every analysis above is pre-named here).
