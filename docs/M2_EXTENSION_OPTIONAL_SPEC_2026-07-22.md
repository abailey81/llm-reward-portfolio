# M2 EXTENSION — THE OPTIONAL PSYCHOMETRIC MODULE (full pre-specification, 2026-07-22)

> **Status: OPTIONAL, registered-but-not-activated (R96).** Report-only, keys disjoint from every
> confirmatory family; can never touch H1–H4. **Activation is Tamer's dated write-time decision on
> resource/scope grounds; if activated, ALL pre-specified estimands report in full** (the
> all-or-nothing clause — no selective publication, so late activation cannot become a forking
> path). Budgeted as a SEPARATE P2-module line (~$25–35), preserving the ~$30 campaign story.
>
> **Why it exists (the Okhrati fit, stated up front).** His golden-neighbour result
> (Hartley…Okhrati, ACL'25) asks whether models *use the risk information they are shown*. This
> module asks the sharper, measurement-grade version: **what is the resolution limit of the
> numeric channel itself** — and did the campaign's fed signal sit above or below it? That is
> intuition-first (one curve, one threshold per model), depth-first (it deepens SQ1's first
> link, not the roster), data-motivated (it closes the loop the R76 SNR analysis opened), and
> honesty-compatible (estimation with CIs, pre-specified, all-or-nothing).

---

## AXIS A — Per-model discrimination thresholds (the 11 full-loop models; ~$8–12)

### The idea
Treat LLM numeric discrimination as **psychophysics**. Estimate each model's
**just-noticeable difference (JND)** for the exact class of numbers the campaign feeds
(4-decimal negative risk statistics, base magnitude ≈ −0.03), by fitting a psychometric
function to two-alternative forced-choice (2AFC) judgments across a graded delta ladder.
Then overlay the **measured distribution of fed deltas from the real campaign archives** on the
threshold: the fraction of the fed signal that sat *beneath* the model's resolution limit is the
mechanism's quantitative closure — the number behind the sentence *"the designers were shown
differences they could not resolve."*

### Stimuli (ecological + adversarially stratified)
- **Task:** 2AFC — two candidate summaries, fed blocks identical except ONE component (primary:
  CVaR-5%) differing by δ; "which candidate has the worse tail?" Chance = 50%; threshold δ75 =
  the gap yielding 75% accuracy (the psychophysics standard; response-bias-resistant).
- **Delta ladder:** 7 log-spaced levels, δ ∈ {1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2},
  spanning the R76-measured fed-delta range (paired noise floor ≈ 1e-4; sibling deltas ≈
  1e-4…8e-4). 20 items/level = **140 core items**.
- **Base values sampled + jittered from the real archives** (never verbatim; the numbers look
  exactly like production feds — ecological validity without memorization surface).
- **Counterbalancing:** worse-side randomized; A/B position randomized; **catch trials** (δ=0,
  20 items — measures position/response bias); **positive controls** (δ=0.1, 20 items — must be
  ≈100%; instrument sensitivity, sealing a null against the broken-thermometer critique).
- **The adversarial digit-length stratum:** a subset where decimal lengths differ
  (−0.0305 vs −0.03052) so string-length/lexicographic heuristics fail — separating genuine
  magnitude comparison from surface string tricks.
- **The 2×2 factors on subsets (60 items each):** FORMAT (legible re-rendering — ranked,
  percentage, comparative phrasing) and INSTRUCTION (the one-sentence guided-compare) — the
  registered m2_probes upgraded from accuracy-only to **threshold-shift** measurement: does
  legibility move the psychometric curve left, and by how much?
- **Decode settings = the leg's pinned settings** (ecological match to the campaign channel);
  a default-decode sensitivity subset disclosed.
- Total ≈ **300 calls/model** ≈ $0.10 (cheap tiers) to ~$2.50 (Opus-class) → **~$8–12 for 11**.

### Estimation (pre-specified)
Per model, fit the 2AFC logistic on log-δ: P(correct) = 0.5 + (0.5 − λ)·σ((log δ − μ)/s), lapse
λ fixed at 0.02 (free-λ sensitivity reported). Bootstrap CIs by item resampling.

| Estimand | What it answers |
|---|---|
| **A-E1** δ75 + 95% CI per model (raw format) | the model's numeric resolution limit |
| **A-E2** format shift Δlog δ75 (legible − raw), paired CI | *is the fix a renderer?* — the SQ3 lever's mechanism-level explanation |
| **A-E3** instruction shift (guided − raw), paired CI | *is the fix a sentence?* |
| **A-E4** **the overlay**: share of realized campaign fed deltas < δ75, per model | **the mechanism closure number** |
| **A-E5** δ75 vs SQ1 responsiveness across the 11 (rank corr., n=11, descriptive) | does the perceptual limit predict in-loop behaviour? |

### Threats → defenses
2AFC wrapper ≠ the in-loop channel (disclosed: measures the *perceptual limit*, bridged
correlationally via A-E5) · memorization (synthetic-jittered stimuli) · response bias (catch
trials + counterbalancing) · string heuristics (the digit-length stratum) · decode variance
(pinned settings + sensitivity subset) · multiplicity (estimation-first; BH for any starred
claim).

---

## AXIS B — The ecosystem map (~100–120 distinct bases; ~$15–25)

### The idea
Widen the instrument to the **callable population**: every distinct base model in the archived
OpenRouter census (339 models / 58 vendors, dated snapshot — itself a reproducibility artifact)
that passes the registered inclusion rule (distinct base after variant/quant dedup;
UK-callable; smoke + contamination screen; not an orchestrator; no rolling aliases). Estimated
frame ≈ 100–130. **Surveying the full eligible frame kills the sampling-bias critique**: this is
a census, not a convenience sample.

### Instrument: the calibrated short form
- **Short form:** 4 delta levels × 12 items + 12 legible + 8 controls/catches ≈ **68 calls/model**
  → δ75 with a wider CI (±0.3–0.4 log units) — sufficient to place models into resolution tiers.
- **Psychometric linking (the smart part):** the 11 full-loop models run BOTH forms → the
  short-form score is **calibrated against the long-form threshold** (anchored linking), so the
  map's tiers inherit the long form's meaning.
- Free routes first; budget-ordered; refusals/timeouts recorded as data (the refusal column).

### Estimands (pre-specified)
| Estimand | What it answers |
|---|---|
| **B-E1** the ecosystem threshold distribution (CDF; by tier and open/closed) | where does the model world stand on numeric resolution? |
| **B-E2** threshold vs **release date** | is numeric resolution improving over time? (the trend claim) |
| **B-E3** threshold vs **price** | *what does a decimal place cost?* — the practitioner's curve (the NatWest register) |
| **B-E4** within-family ladders (Qwen 5-point, Anthropic 4–5-point, …) | scaling laws of numeric resolution, vendor-controlled |
| **B-E5** the n≈100 reading↔capability regression | the cross-model law at meaningful n (ρ≈0.3 detectable; at n=34 only ρ≳0.45 was) |

### Threats → defenses
Catalog churn (dated census + slugs pinned at execution + served_model recorded per call) ·
rate limits (batched over a day, post-headline) · base-model dedup disputes (the dedup rule
written before execution; ambiguous lineages EXCLUDED and listed) · free-route quality variance
(provider recorded; paid-route sensitivity subset for the top tier).

---

## Where each axis lands (the write-time decision map)

| Outcome | Axis A | Axis B |
|---|---|---|
| **Activated + dissertation** | one figure (thresholds + the fed-delta overlay) + one mechanism paragraph in CH6/CH7; everything else appendix | at most one map figure in the appendix |
| **Activated + papers-only** | the spine of **P2** ("Do LLMs read the numbers you feed them?") | P2's survey half — its headline scale |
| **Not activated** | the registered v1 M2 probes still run (score-level, ~$10) | nothing runs beyond the 34-row core+extras |

Costs: A ≈ $8–12 · B ≈ $15–25 · both ≈ $25–35, **a separately-budgeted P2 module** (the campaign
remains the ~$30 study in every cost statement; the module is disclosed as its own line).
Timing: post-headline, API-only, ~1–2 days wall-clock, zero GPU.

## Activation protocol (the integrity clause)
Activation is a **dated decision at the write-time fork**, made on resource/scope grounds and
recorded as an amendment. **If activated, every estimand above reports in full** — the
all-or-nothing clause makes the timing of activation incapable of biasing what gets published.
The stimulus builder rides the existing `scripts/m2_survey.py` harness (a gate-week build task
if activated pre-launch; equally runnable post-campaign since the module needs no GPU and no
frozen quantity).
