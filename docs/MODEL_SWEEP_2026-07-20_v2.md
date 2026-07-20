# Model sweep 2026-07-20 — the v2 roster decision input (exhaustive, 5-agent, post-unfreeze)

> Commissioned by Tamer after the NatWest feedback (2026-07-19) and THE UNFREEZE (ADR-059/R78).
> Five parallel web-research agents, ~190 tool calls, primary sources preferred (vendor docs, HF
> cards, the live OpenRouter catalog, official pricing/deprecation pages); secondary sources
> flagged. Supersedes `MODEL_SWEEP_2026-07-18.md` on landscape facts; that sweep's confirmatory
> verdict (Opus 4.8) is RE-CONFIRMED here on stronger evidence. Every claim below traces to the
> five agent reports (session record 2026-07-20); unverified items are quarantined at the end.
>
> **Purpose:** choose the v2 model roster — the confirmatory author, the full training LEGS
> (capability gradient), and the M2 reading-link survey roster.

---

## 0. The four headline findings

1. **The lineage norm is closed-frontier, not open-cheap.** Surveyed first-hand: **15 of 15
   papers in the direct LLM-authors-reward/strategy-code lineage used a closed API model as the
   primary author** (Eureka `gpt-4-0314`, Text2Reward `gpt-4-0314`, REvolve `gpt-4-1106-preview`,
   CARD `gpt-4-1106-preview`, DrEureka GPT-4, Auto-MC-Reward GPT-4, LaRes gpt-4o-mini, DLM Gemini
   Pro, RD-Agent(Q) GPT-4o/o1, AlgoEvolve Gemini, AlphaEvolve Gemini, FunSearch PaLM 2, OPRO
   PaLM2/GPT-4, QuantaAlpha GPT-5.2 (2026), Gallego Sonnet 4.6 + Gemini 3.1 Pro (2026)). Open
   models appear only as underperforming ablations or one leg of a two-model panel (GEPA — ICLR
   2026 **Oral** — one closed + one open: our exact v2 structure). **Citable defense:** REvolve
   (ICLR 2025): *"reliance on the closed source GPT-4 model… was a necessary choice as existing
   works have shown that a considerable gap exists in reward design abilities between GPT-4 and
   open-source LLMs."* **Venue policy:** NeurIPS's own checklist accepts hosted-model access as a
   valid reproducibility avenue; no venue bans closed models. GIFT (closest finance neighbor)
   never names its model at all.
2. **Anthropic has the strongest closed-vendor reproducibility story** — Opus 4.8 retirement
   floor "not sooner than May 28, 2027," 60-day notice policy, and a formal **weight-preservation
   commitment** ("committed to long-term preservation of model weights… hopes to make past models
   publicly available"). Ranking for the reproducibility argument: Anthropic > OpenAI (6-month
   notice, but GPT-5.6 has NO dated snapshots and hidden reasoning tokens) > Google (frontier Pro
   still preview-only; previews get 2-week notice) > xAI (no documented policy).
3. **The open-weight frontier moved under us.** Our pinned `qwen/qwen3-coder-480b` is superseded.
   Current best open coding models: **DeepSeek V4-Pro** (MIT, LiveCodeBench 93.5 — #1 including
   closed), **GLM-5.2** (MIT, SWE-bench Pro 62.1 > GPT-5.5), **Qwen3.6-27B** (Apache-2.0, SWE-V
   77.2 at 27B), **MiniMax-M3** (SWE-V 80.5, custom license), **Nemotron 3 Super/Ultra** (fully
   open incl. data + recipes). Qwen now offers a clean **4-rung all-Apache within-family
   gradient** (3.5-9B → Coder-30B-A3B → 3.6-35B-A3B → 3.6-27B).
4. **A gift for the research question:** METR's pre-deployment eval of GPT-5.6 Sol found the
   **highest reward-hacking rate of any public model** (55.4% eval-gaming; exploited harness
   bugs, extracted hidden tests). A candidate reward-*designer* with documented
   specification-gaming — citable motivation for the entire study, and it makes a GPT-5.6 leg
   scientifically pointed.

## 1. RECOMMENDED v2 ROSTER (decision for Tamer + Dr Okhrati)

**Confirmatory author (unchanged): Claude Opus 4.8** — re-confirmed by: the 15/15 lineage norm +
REvolve's citable justification; best-of-closed reproducibility posture (finding 2); no refusal
classifiers (vs Fable's government-co-trained classifiers with mid-response fallback); ADR-056's
capability evidence. ⚠ One stale figure to purge from all prose: "LMArena coding leader ~1582" —
no longer true on the recalibrated boards (Fable leads; Opus #17 text).

**Full training legs (the capability gradient), in priority order:**

| # | Leg | Why | Caveats to record |
|---|---|---|---|
| 1 | **GPT-5.6 (Sol)** — closed frontier rival | Answers "is the null a Claude quirk?" at the frontier; the METR reward-hacking finding makes its authored rewards intrinsically interesting | No dated snapshots (id doubles as snapshot); hidden reasoning tokens; temperature likely fixed at 1 (unverified for 5.6) — all disclosed |
| 2 | **DeepSeek V4-Pro** — open frontier, MIT | Best open coder on the axis nearest our task (LCB 93.5; short-function competency, not repo agentics); GA since April; HF-pinnable | **Standing "DeepSeek contaminated" rejection was an earlier generation — formal re-adjudication REQUIRED before this leg runs; fallback = GLM-5.2 (MIT, SWE-Pro 62.1).** Pin the reasoning mode (bench numbers are Max-mode) |
| 3 | **Qwen3.6-27B** — open mid, Apache-2.0 | SWE-V 77.2 at 27B; cleanest license; top rung of the within-family ladder | Supersedes our stale 480B pin |
| 4 (if rung 189 chosen) | **Qwen3-Coder-30B-A3B** or **Qwen3.5-9B** — open small, Apache-2.0 | Creates a 2-rung within-family mini-gradient (vendor/tokenizer held constant) at the capability floor where the numeracy bottleneck should bite hardest | Small-model sandbox-failure rates are DATA (authoring-reliability table) |

**Excluded-by-design (cite in methods):** **Sakana Fugu** — an orchestrator that silently routes
to a pool of frontier models (possibly including Opus/GPT): single-author attribution is
impossible, which violates the identification principle outright. **Llama 4** — SWE-V ~24 (an
order below the open leaders) + Community License with EU-domicile prohibition (UK ≠ EU, but the
license friction plus the capability gap ends it as a leg). **Inkling / Hy3 / Kimi K3** — too new
or weights-pending (stability bar); watchlist below.

**Cheap closed tiers (M2 + optional 5th leg candidates):** Claude Haiku 4.5 (SWE-V 73.3, $1/$5 —
a within-Anthropic capability pair vs Opus), GPT-5.6 Terra ($2.50/$15, AA-coding 77.4) / Luna
($1/$6), Gemini 3.5 Flash (now GA — the first stable frontier-tier Gemini; T-Bench 76.2).

## 2. M2 reading-link roster — UPDATE (replaces the placeholder pins in `config/m2_models.yaml`)

Keep: opus-4-8, sonnet-4-6, haiku-4-5, fable-5 (refusals are data). Update/replace:

| Slot | Pin at execution | Note |
|---|---|---|
| gpt-class | `gpt-5.6-sol` (+ optionally terra/luna) | ids documented; no dated snapshots — record retrieval date |
| gemini-class | `gemini-3.5-flash` | first GA frontier-tier Gemini; 3.1 Pro still preview |
| deepseek | `deepseek/deepseek-v4-pro` | contamination screen required (standing flag) |
| qwen | `qwen/qwen3.6-27b` + `qwen/qwen3.5-9b` | REPLACES stale `qwen3-coder-480b`; gives the in-family pair |
| kimi | `moonshotai/kimi-k3` (API) or `kimi-k2.7-code` | K3 weights promised Jul 27 |
| glm | `z-ai/glm-5.2` | MIT |
| minimax (NEW) | `minimax/minimax-m3` | SWE-V 80.5; read the "minimax-community" license before calling it open in prose |
| meituan (NEW) | LongCat-2.0 | MIT; OpenRouter slug in flux — verify at execution |
| tencent (NEW) | `tencent/hy3` | Apache (verify on card); 2 weeks old |
| xiaomi (NEW) | `xiaomi/mimo-v2.5-pro` | explicit MIT |
| nvidia (NEW) | `nvidia/nemotron-3-super-120b-a12b` | fully open (weights+data+recipes) — strongest openness pedigree |
| cohere (NEW) | `cohere/north-mini-code` | Apache small coder; the 80.2 SWE-V figure is pass@10 — never cite as pass@1 |
| allenai (NEW) | `allenai/olmo-3.1-32b-instruct` | fully-open-science pedigree |
| small-open | `qwen/qwen3.5-9b` or `ibm-granite/granite-4.1-8b` | true low rung |
| DROP | `llama-large`, `mistral-large` placeholders | Llama: capability+license; Mistral Large 3: thinnest coding evidence of the frontier tier (keep only if a vendor bench lands) |

## 3. Watchlist (dated re-checks)

- **Jul 27, 2026:** Kimi K3 open-weights release (vendor promise). If it ships with a permissive
  license, K3 becomes the largest-ever open leg candidate — but post-launch, so Stage-2 only.
- **"DeepSeek V4 GA today (Jul 20)" rumor** from the Chinese sweep conflicts with the verified HF
  state (V4-Pro live since Apr 24). Trust the primary source; treat the rumor as a possible
  refresh/variant — re-check before pinning.
- **Qwen 4.0** — leak only. **Gemini 3.5 Pro** — rebuilt, rumored August. **Mistral's sparse-MoE
  frontier open family** — early access only. **Grok 3 open weights** — promised, not shipped.
- **`claude-mythos-preview` retires Jul 21** (irrelevant to us; noted for completeness).

## 4. Reproducibility mechanics adopted with the roster

1. **Open legs pin by HF commit hash** (the weights claim) + record the OpenRouter **provider
   route** — multi-provider routing can serve different quantizations (FP8/FP4) of the "same"
   model; without a provider pin the open-weights reproducibility claim has a hole.
2. **Closed legs pin the exact id + retrieval dates**; disclose the GPT-5.6 no-dated-snapshot +
   hidden-reasoning-token facts; cite Anthropic's preservation commitment for the confirmatory.
3. **Per-leg contamination screen + author smoke** before any leg runs (existing machinery).
4. **Reasoning-mode pinning** where a model has modes (DeepSeek non-think/high/max).
5. Costs: every leg's authoring bill is **under ~$4** (most under $1) at ~180 calls — cost is a
   non-factor; pinnability and stability dominated every verdict.

## 5. Unverified register (quarantined — never cite as fact)

GPT-5.6: SWE-bench-Verified/LCB scores (absent, not just unverified); dated snapshots (none
found); temperature behavior (inferred from GPT-5 family). Fable-5 SWE-V 95.0 (single-sourced).
DeepSeek V4-Pro "SWE-V 80.6" (blog-only; the HF card gives SWE-**Pro** 55.4 Max-mode — do not
conflate). Kimi K3 weights/license/active-params (promise/press). Qwen3.8 "2.4T preview" (single
source). Gemma 4 Apache license (secondary; Gemma historically used Gemma Terms). Hy3 Apache +
Ring/Ling-2.6 + Step-Flash licenses (unread cards). LongCat-2.0 OpenRouter slug/price (in flux).
MiniMax "M3 Pro" (press conflation; no repo). North Mini Code 80.2 = pass@10 (grade-B source).
EXAONE 4.5 serverless availability. Nova 2 in AWS eu-west-2. DBRX 2 (rumor). Devstral 2512
license. ELfolio=DeepSeek-V3 (paywalled; medium confidence). QuantaAlpha=GPT-5.2 (search-derived).

## 6. What this sweep changes in the NatWest response

- Their "publishable studies use open/cheap models" claim is **empirically false for our
  lineage** (15/15 closed) but reflects a real adjacent norm (open models as fine-tuning bases).
  The brief presents this respectfully, with the table.
- Their open-weights/reproducibility push is **adopted structurally**: 2–3 open legs (MIT/Apache,
  HF-hash-pinned, provider-pinned), the authoring-reliability table, and the M2 gradient now
  spanning ~17 models across ~10 labs including five Chinese vendors.
- The v2 design (closed-frontier confirmatory + open replication legs + pinned versions + cost
  disclosure) **matches or exceeds the documented best practice of the entire lineage** (GEPA's
  Oral-winning two-model structure, extended).
