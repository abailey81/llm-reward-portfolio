# Stage 2, rebalanced for PUBLISHABILITY (2026-07-11)

> **Supersedes the internal ordering of `GRADE_SECURITY_AND_TIER_DESIGN_2026-07-08.md` §4.1 (the 4-tier
> armor 2.A–2.D).** The *machinery* and the *armor principle* (§4.0: Stage 2 can never hurt the grade;
> report-only; prunable to zero; no forking paths) are unchanged and still govern. What changes is the
> **value ordering and emphasis**: Stage 2 is re-centred on MECHANISM DEPTH (the publishable contribution)
> and the cross-everything robustness breadth is demoted to a thin, prunable shell. This touches nothing
> frozen — the Stage-1 confirmatory design (m=6, arms, splits, seeds) and its report-only mechanism
> instruments (SQ1–SQ3, the legibility differential) are already frozen; Stage 2 only EXTENDS them.

## 0. Why this rewrite — the priorities and Okhrati's revealed taste both point one way

The project priorities (CLAUDE.md ★) put **depth, intuition, mechanism, and genuine originality OVER
breadth and textbook machinery**, and demand a **publishable** contribution. Okhrati's revealed grading
function says the same, sharply: **"do less, go more in depth"** (depth > breadth; he *docks* scatter),
**intuition over technical correctness**, **honesty rewarded** (his 5/5 — the null is this), **originality
foregrounded**, and — decisively — his own research is **LLM-risk-behaviour** (Hartley…Okhrati 2025 ACL:
*do models use the risk they are shown?*), which is *this dissertation's exact mechanism question*.

The old Stage-2 (run the study on another market / algorithm / critic / model) is mostly **breadth** —
a spread of robustness tables, each adding one appendix table and deepening nothing. That is precisely
what Okhrati penalises, and it is not what makes a null publishable.

## 1. The publishable thesis (one sentence — the paper's spine)

> Feeding an LLM reward-designer fine-grained distributional risk information does **not** improve the
> reward code it writes — because current LLMs cannot reliably use the close numerical tail values they
> are shown (a **representational numeracy bottleneck**, not a capability one) — and this failure is
> **general across LLMs** and **partially reversible** by re-representing the information legibly.

A null becomes a *contribution* only when it is **mechanism-explained, general, and lever-identified**.
Those three are the three mechanism instruments below. Everything else is support.

## 2. Stage 2 rebalanced — three tiers by PUBLISHABILITY value

### TIER M — the MECHANISM SPINE (the contribution; invest the effort here)

- **M1 — Locate the break (frozen Stage-1 instruments, report-only).** The 3-link chain
  `fed tail —SQ1→ authored code —SQ2→ trained policy → realized tail`. Report responsiveness (Spearman,
  bootstrap CI; `responsiveness.py`) ≈ 0 at **link 1**: the chain is cut at the first joint, so the
  equivalence is *explained*, not merely observed. This is the honest null-as-boundary-condition.
- **M2 — Explain the break: the cross-LLM NUMERACY + RESPONSIVENESS SURVEY (NEW — the flagship).** The
  numeracy hypothesis (LLMs ~50–70% accurate comparing close small floats; the fed CVaR values −0.0577
  vs −0.0582 sit in that regime) is a claim about LLMs *broadly*, and it can be tested **without a single
  RL training** — cheaply, on a *bunch* of models:
  - (a) **Numeracy probe:** feed each model batteries of close tail-value pairs, ask which is worse →
    per-model discrimination accuracy vs the near-degeneracy of the fed values.
  - (b) **Responsiveness probe:** feed each model the tail block, ask it to author a reward → does the
    authored code *use* the tail (vs surface-echo)?
  - Run across a **dozen+ models spanning labs and the full capability range** (Opus, Qwen, Kimi-K2,
    GLM, Gemini, GPT, Grok, Llama, Mistral, and deliberately some *weak* ones — the capability GRADIENT
    is the evidence). No agent, no seeds → **~$5–10 total**. Result: "no LLM across the range reliably
    uses close tail floats, and each model's responsiveness tracks its numeracy." Grounds directly in the
    numeracy corpus (tokenizer-fragments-numbers, FinVerBench, Bradford-Levy 2026 JAR, value-aware
    embeddings) — cite-and-USE. **This is the headline mechanism figure and the paper's originality.**
- **M3 — The lever (D2+ (i)/(iii) + the frozen `legible_format_responsiveness_differential`).** Re-render
  the *same* tail information legibly — integer basis points, ordinal decile ranks, CI-annotated — and
  test whether responsiveness/use rises. If it rises, the bottleneck is **representational** (and here is
  the fix); if not, it is deeper. Either way the null gains a mechanism *and a lever* — the difference
  between "it didn't work" and a contribution.

### TIER R — RIGOR (honesty = Okhrati's 5/5; cheap, keep all)

- **D3 variance decomposition** — σ_seed dominance (~5–7× the effect) is itself a first-class finding.
- **D4 winner's-curse shrinkage** · **D9 specification-curve + permutation** — the result is not a
  selection or spec artifact.
- **D5 calibration fleet** (laptop, keyless) — the pipeline's realized α really is 0.05.
All CPU/laptop, ~$0, run at/around the bank gate on the just-banked data.

### TIER G — THIN GENERALIZATION SHELL (minimal external validity; PRUNABLE, not foregrounded)

- **U3 — one open-family replication (Qwen; optionally Kimi-K2).** Enough to say "not Opus-specific."
  This is the *only* full-replication we foreground.
- **D6 TQC · U5 PPO/TD3 · U4/U4b FTSE · D7 GPT-5.6 (supersedes GPT-5.5, Jul 2026; ADR-056)-class** → **CH7 FUTURE WORK by default.** Run ONLY if
  trivially free (frozen winners on an already-built panel); never foreground. A second market and a
  third algorithm are the breadth Okhrati would rather see spent on M2/M3. If pruned, **zero holes**.

## 3. What changed vs the old 4-tier armor

| Old (§4.1) | New emphasis |
|---|---|
| 2.A "free depth" = D3/D4/D9 **+ D6 TQC + U5 PPO/TD3 + U4b FTSE** (robustness) | Split: analyses → **TIER R (rigor)**; TQC/PPO/TD3/FTSE → **TIER G (prunable future-work)** |
| 2.B = U3 Qwen + D2+ lean grid | U3 → **TIER G (one replication)**; D2+ → **TIER M (mechanism spine)** |
| 2.D premium = U2b + **D7 GPT-5.6 (supersedes GPT-5.5, Jul 2026; ADR-056)** + U4 (\$72–135) | **Dissolved.** Third family = a *capable open* model (Kimi/GLM, ~\$3); the "bunch of LLMs" goes into the cheap **M2 survey**, not expensive replications. Premium tier ≈ gone. |
| (none) | **NEW M2 — the cross-LLM numeracy survey: the flagship publishable instrument.** |

## 4. Publication path

- **TMLR** — welcomes rigorous negative/mechanism results; the numeracy-bottleneck story + rigor fit.
- **ICAIF (main)** — the finance-AI framing (risk-sensitive reward design).
- **LLM-reasoning / LLM-agents workshops** — the numeracy-in-reward-design angle.
The dissertation is written spine-first (M1→M2→M3) so it reduces cleanly to a paper.

## 5. Alignment (every element earns its place)

| Element | Priority served | Okhrati rule |
|---|---|---|
| M1 locate-the-break | 3 deep · 1 grade | null-as-mechanism (honesty 5/5) |
| **M2 numeracy survey** | 2 publishable · 3 deep · 4 novel+corpus | originality; his ACL LLM-risk work; motivate-with-data |
| M3 legibility lever | 3 deep · 2 cutting-edge | intuition (why + the fix) |
| TIER R (D3/D4/D9/D5) | 1 grade | honesty; mechanics (compute/calibration) |
| TIER G (thin) | 1 grade (defensive) | minimal external validity; **avoids the breadth he docks** |

## 6. Cost, safety, timing

- **Cost:** M2 ~\$5–10 · M3/D2+ ~\$9–18 · TIER R ~\$0 · U3 (done) + Kimi ~\$3 → **Stage 2 ≈ \$20–30 total**
  (was \$93–178). The premium shelf is gone; the value went UP and the cost went DOWN.
- **Safety:** all report-only, post-bank-gate, **touches nothing frozen**. Stage-1 mechanism instruments
  (SQ1–SQ3, legibility differential) are already frozen; M1/M3 report them, M2 is a new authoring-only
  probe outside the confirmatory family (no forking paths — descriptive survey with CIs, no m-family).
- **Timing:** M2 + TIER R can run the moment Stage 1 banks (M2 needs no GPU); M3/D2+ overlap the write-up.
  None is on the critical path. Model verification (live smoke + contamination check + capability floor,
  per the Qwen pattern) precedes any new model in M2.

## 6b. Grounded in the ACTUAL marking guidelines (IFTE0008 2025–26, read 2026-07-11)

The four marking dimensions are **equally weighted**, and dimension 3 carries the threshold that *defines*
the absolute-max band — this is the load-bearing fact for grade maximisation:

- **90–100% (Distinction top) = "publishable in a peer-reviewed JOURNAL."**
- **80–89% (A) = "publishable in an international CONFERENCE."**

**Implication (decisive):** robustness breadth is at best *conference*-grade ("it also holds elsewhere");
a **mechanism contribution is *journal*-grade** (TMLR is a journal). So the M-spine rebalance is not a
preference — **it is the specific lever from the A-band into the 90–100 band.**

**Novelty defence the guidelines explicitly flag:** Coache–Jaimungal already do distributional (CVaR) RL
on portfolios, so "the LLM-reward-designer layer must earn its place." The **mechanism reframe resolves
this**: their contribution is the RL; ours is *whether an LLM can use distributional risk when it authors
the reward* (LLM-numeracy-in-reward-design) — a question they do not touch. Depth on the mechanism makes
the novelty *unquestionable* rather than incremental.

**Map to the four dimensions (all four; absolute-max needs all):**
| Dimension (equal weight) | Distinction descriptor | Served by |
|---|---|---|
| 1 Background + independence | "considerable extra-curricular reading; original interpretation; exceptional insight" | 196-paper corpus (cite-and-USE, **selective/critical**, not a catalogue) + the numeracy-corpus grounding of M2 |
| 2 Research design | "faultless execution; entirely appropriate methods; **unquestionable originality**" | pre-registration + replay-not-regenerate + the mechanism instruments (the A+ lever) |
| **3 Novelty & significance** | "**publishable in a peer-reviewed journal**" (90–100) | **the M-spine: mechanism-explained, general, lever-identified null** — the journal contribution |
| 4 Communication | "excellent, highly readable, **faultless presentation of data**" | **must present M faultlessly:** the numeracy-survey figure, the 3-link mechanism diagram, the legibility-lever result, a plain-language contribution paragraph *before* any formalism, scannable tables — for the **any-discipline second marker** (the guidelines' "single biggest risk") |

**Guideline compliance the M-spine must not break:** 10,000-word body (maths/code/figures/tables/appendices
EXCLUDED → push the survey protocol + formalism into excluded blocks); 16-section order; core
(Method+Results+Discussion) ≈ 60%; a **dedicated Limitations subsection** (exemplar best practice — the
cross-period single-look limitation lives here); an **ablation table isolating the contribution**; Harvard
refs, ~90 cited selectively. Dimension 4 is *earned in the writing* and is the parallel priority to the
Stage-2 science.

## 7. The bottom line

Stage 2 stops being "look how many ways it still holds" (breadth Okhrati penalises) and becomes **"here
is *why* distributional risk feedback fails, that it fails *generally*, and the *lever* that changes it"**
(depth Okhrati rewards, and a publishable contribution). Same guardrails, a fraction of the cost, and it
is now aimed squarely at the top band and a paper.
