# THE MODEL ROSTER OF RECORD — 2026-07-22 (post-R95)

> **What this is.** The single authoritative view of every model in the study, organised by
> scientific function. Executed truth = `config/legs.yaml` == `model_suite` (gate-verified,
> n=10); amendment trail R79–R95. Prices are the ledger's planning table (realized per-call cost
> is the authority at run time). Sizes are stated only where the vendor discloses them.
> **Feeds:** the CH4 model-suite section (registry row 2), the Okhrati/NatWest conversations.

---

## 1. The design in one sentence

One frontier model answers the confirmatory question under full rigor; ten replication legs
answer *"is it general?"* at the 30-seed floor; ~35 survey rows (R99) answer *"can models read the
numbers at all?"* — and three controlled instruments (two capability pairs + a conditional
generation pair) turn model differences into identified contrasts instead of anecdotes.

## 2. The full-loop roster (11 models — these train real RL agents)

| # | Model | Status | Pin (grade) | Open? | Arch / size | $/MTok in–out | Leg cost (exp.) | Scientific function |
|---|---|---|---|---|---|---|---|---|
| ★ | **Claude Opus 4.8** | **CONFIRMATORY** | `claude-opus-4-8` (dateless-immutable, ADR-016; retirement floor ≥ May-2027 + weight-preservation) | ✗ | undisclosed | 5.00–25.00 | ~$6 (full ladder) | The one frontier author; gates H1–H4; the E1 seed ladder; the mechanism kernel reads its archives |
| 1 | DeepSeek V4-Pro | leg (open) | HF `deepseek-ai/DeepSeek-V4-Pro@b5968e91` (**weights-hash**) + reasoning mode: pro pinned (provider renamed think-high, 2026-07-23) | ✅ MIT | MoE 1.6T / 49B active | 0.435–0.87 | ~$0.4 | Open frontier #1; the contamination-gated seat (GLM absorbs on fail) |
| 2 | GLM-5.2 | leg (open) | HF `zai-org/GLM-5.2@b4734de4` (**weights-hash**) | ✅ MIT | MoE 744B | 0.97–3.04 | ~$0.8 | Open frontier #2 + DeepSeek's pre-declared fallback (open replication ≠ one lab) |
| 3 | Qwen 3.6-27B | leg (open) | HF `Qwen/Qwen3.6-27B@6a9e13bd` + SiliconFlow-fp8 provider-pin | ✅ Apache | **dense** 27B | 0.45–2.70 | ~$0.5 | **Open capability pair — TOP** (same provider+quant as its sibling: the confound-free contrast) |
| 4 | Qwen 3.5-9B | leg (open) | HF `Qwen/Qwen3.5-9B@c2022362` + SiliconFlow-fp8 provider-pin | ✅ Apache | **dense** 9B | 0.10–0.15 | ~$0.1 | **Open capability pair — FLOOR**: where the numeracy bottleneck is predicted to bite; failure-is-a-finding |
| 5 | Haiku 4.5 | leg (closed) | `claude-haiku-4-5-20251001` (**dated snapshot**) | ✗ | undisclosed | 1.00–5.00 | ~$1.2 | **Closed capability pair — FLOOR** (vs Opus): the second ecosystem's controlled contrast |
| 6 | GPT-5.6 Luna | leg (closed) | `openai/gpt-5.6-luna` (undated; disclosed) + effort-low + 2k cap | ✗ | undisclosed | 1.00–6.00 | ~$1.4 | The cross-vendor check: "is the null an Anthropic quirk?" |
| 7 | Nemotron 3 Super | leg (open) | HF `nvidia/…-A12B-BF16@d51eab0d` (**weights-hash**) | ✅ NVIDIA OML* | LatentMoE 120B / 12B active | 0.08–0.45 | ~$0.1 | The data-transparency seat (only model with major portions of training data released) + US-open + architecture diversity |
| 8 | Sonnet 5 | leg (closed) | `claude-sonnet-5` (undated; disclosed) | ✗ | undisclosed | 2.00–10.00† | ~$2.9 | The latest-generation seat (released 2026-06-30) |
| 9 | Gemini 3.5 Flash | leg (closed) | `google/gemini-3.5-flash` (undated; reasoning at provider default, disclosed) + 2k cap | ✗ | undisclosed | 1.50–9.00 | ~$1.6 | Big-three closed coverage; stretch seat |
| 10 | **Kimi K3** | leg (closed→open upgrade) | `moonshotai/kimi-k3-20260715` (**dated snapshot** — strongest pin among the closed-class legs); weights due 2026-07-27 → HF-hash by rule | (✅ pending) | MoE 2.8T (largest ever open, on upgrade) | 3.00–15.00 | ~$5–11 at the 8192 cap (R97a; worst ~$22; always-on thinking) | The frontier-class open-upgrade seat; 4th-ranked frontier on independent testing |

\* NVIDIA Open Model License — open weights, *not* Apache; "major portions of the training data
released, some subsets gated" (phrase exactly). † Sonnet-5 introductory pricing through
2026-08-31 (covers the campaign window); $3/$15 after.

**Truncation order at the Aug-14 calendar gate (last = first cut):** …Nemotron → Sonnet-5 →
Gemini → **K3**. Under mode-D all ten legs land ~L+4.5–5.5 (R95-updated), so truncation is unlikely at any
plausible launch date.

## 3. The three controlled instruments (where model differences become inference)

| Instrument | Members | What it identifies |
|---|---|---|
| **Open capability pair** | Qwen 9B ↔ 27B (one vendor, one provider, one quantization, both dense) | content-effect × capability, open ecosystem |
| **Closed capability pair** | Haiku 4.5 ↔ Opus 4.8 (one vendor; Opus restricted to the common 30 seeds) | content-effect × capability, closed ecosystem |
| **Generation pair** (conditional) | Opus 4.8 ↔ Opus 5 — fires only if R91's rule triggers (GA + API id + verifiable attribution by launch-GO) | content-effect × one model generation, vendor+tier fixed |

Capability anchor (R84, discretion-free): SWE-bench-Verified from the official card —
at-freeze values {Qwen-27B: 77.2, Haiku: 73.3}; **all other legs MISSING by rule** (no
conflation: DeepSeek's circulating 80.6 is Max-mode, not our pinned pro mode — née think-high,
vendor-renamed 2026-07-23). The registered
secondary (M2 reading score) and tertiary (within-family ordinal) anchors carry the rest.

## 4. The rule-driven seats (pre-declared; never results-contingent)

- **K3 open-class upgrade** (`kimi_k3_upgrade_rule`): weights + permissive license by launch-GO
  → hf_pin + license filled; else it runs as a closed leg on the dated snapshot.
- **Opus 5 conditional leg** (`conditional_seat_opus_5`): GA + public API id + gates + verifiable
  single-author attribution (the leaked 4.8-fallback routing FAILS it on the Fugu principle) by
  launch-GO → joins after Sonnet-5, forming the generation pair.

## 5. The M2 reading-link survey (~35 (R99 Terra) rows; no RL, ~$10 total, post-headline)

| Family group | Rows | Purpose |
|---|---|---|
| Anthropic ladder | Haiku 4.5 · Sonnet 4.6 · Opus 4.8 · **Fable 5** (+ Sonnet 5 extra) | 4–5-point closed reading ladder; Fable's refusals are data |
| Qwen ladder | 3.5-9B · 3-Coder-30B · 3.6-35B · 3.6-27B · 3-Coder-480B (+ **Qwen-4-Coder** extra) | 5–6-point open reading ladder (incl. the v1-pin continuity row) |
| Closed cross-vendor | GPT-5.6 Sol · Luna · Gemini 3.5 Flash · Grok 4.5 · Nova 2 Lite | frontier + budget closed tiers (Sol = the METR reward-hacking context) |
| Open cross-vendor | DeepSeek V4-Pro · GLM-5.2 · Nemotron · MiniMax-M3 (restricted-license, labeled) · Kimi lines · LongCat · Hy3 · MiMo · North-Mini-Code · OLMo · Ring · KAT-Coder · Mercury-2 (diffusion-arch row) · granite/nex/etc. | the breadth axis: ~10 labs, incl. architecture diversity |
| Extras (budget-permitting, in order) | sonnet-5 · qwen4-coder · olmo · mistral-large-3 · gpt-oss-20b · kat-coder-pro · inkling · laguna · nex-n2-mini | run only under ceiling headroom |

Leg models double as survey rows at zero marginal design cost. Inclusion rule: UK-callable +
smoke + contamination screen + distinct base model + not an orchestrator.

## 6. Excluded by design (cite in methods; never re-propose)

| Model | Reason |
|---|---|
| **Sakana Fugu** | orchestrator routing to a hidden model pool — single-author attribution impossible (the identification principle) |
| **Fable 5** (as author) | dual-use classifiers with mid-response fallback = a treatment-correlated interference channel; the June government-directive suspension = the permanence contradiction. M2-only, where refusals are data |
| **Llama 4** | capability (SWE-V ~24) + license friction |
| **MiniMax-M3** (as leg) | failed the primary-source license gate ($20M revenue trigger + attribution badge); M2 as "weights-available, restricted" |
| **Qwen-4-Coder** (as leg) | MoE — would break the dense–dense pair invariant; M2 row instead |
| **`~*/-latest` aliases** | reproducibility poison; hard-rejected at the transport factory |
| **Sonnet 4.6** | removed by R92 (Tamer); its bridge prediction withdrawn pre-data; retained in M2 |

## 7. The money (advisory R83; realized per-call cost is the authority)

| Bucket | Expected | Worst-at-caps |
|---|---|---|
| Anthropic key (Opus + Haiku + Sonnet-5) | ~$10 | ~$27 |
| OpenRouter key (7 legs incl. K3 + gates + M2) | ~$18 | ~$30 |
| **Whole study** | **~$28** | ~$57 (never realistically reached; under-funding pauses, never wastes) |

Top-up guidance: **Anthropic ≥ $35 · OpenRouter ≥ $25** (+ the do-not-log toggle).

---
*Provenance: every pin verified this week (HF API retrievals 2026-07-22 for the five weights
hashes; OpenRouter catalog for K3's dated slug; vendor announcements for prices). Licenses
independently re-verified at pin-retrieval: MIT / MIT / Apache / Apache / NVIDIA-OML.*
