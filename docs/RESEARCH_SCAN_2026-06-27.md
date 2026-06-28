# Research scan — 2026-06-27 (6-agent web + repo + tooling sweep)

**Status:** WRITE-ONLY capture. Nothing here changes the frozen experimental design (CLAUDE.md PD-2/PD-3).
Every item is tagged for one of: Related Work, Future Work, robustness/methods-defensibility prose, or a
safe engineering hardening. Every 2024–2026 reference is `% VERIFY` until checked against the source; the
search-listing-only IDs in §6 must **not** enter `paper/refs.bib` as confirmed.

This scan was run as six parallel agents (new-tech, GitHub-repos, Claude-Code/tooling, structure, test-gaps,
V1–V19 status). It corroborates the stored 24-agent literature sweep and `RELATED_WORK_WATCH.md`: **the
novelty conjunction is intact.**

---

## 1. Headline — novelty holds

No published work (paper or public repo) occupies the exact intersection:
*LLM authors the reward-function **code** × risk-sensitive **portfolio** RL × multi-level **EVT/GPD tail**
feedback ablation (scalar vs tail-profile) × fixed SB3 **SAC/TQC** agent.*

The two adjacent families live apart, confirmed from both the paper and code-landscape angles:
- **LLM-writes-reward-code** work is robotics/control (Eureka, Text2Reward, CARD, REvolve, Auto-MC-Reward,
  LEARN-Opt) — none financial, none distributional-tail-fed.
- **LLM-in-finance-RL** work injects *numeric signals* into a *fixed human-written reward* (FinRL-DeepSeek) —
  never synthesises the reward program.

## 2. SCOOP-RISK — must cite + fence in Related Work (verified first-hand)

| Item | id / repo | Why close | Why we survive it |
|---|---|---|---|
| **FinRL-DeepSeek** | arXiv:2502.07393 (Feb 2025); `benstaf/FinRL_DeepSeek` (~329★, MIT) | LLM + risk-sensitivity (CPPO/CVaR) + stock trading | LLM emits sentiment/risk **scores** into a **fixed** reward; **PPO/CPPO not SAC**; single-level CVaR, no closed-loop tail feedback. **The one mandatory "this isn't us" paragraph** — and it doubles as a natural ablation baseline. |
| **CARD** | arXiv:2410.14660 (Oct 2024) | LLM Coder/Evaluator generates reward **code** with structured feedback | Robotics; **does not ablate feedback-richness (scalar vs multi-level)** — which IS H2. Fence on domain + the controlled ablation. |
| **Risk-sensitive RL via Convex Scoring Functions** (Han, Liu, Yu) | arXiv:2505.04553 (May 2025) | Ties elicitability / Fissler–Ziegel to RL objectives incl. CVaR/ES/EVaR; stat-arb application | Targets the optimisation *objective* via convex scoring; we make the LLM *author the reward program*. Closest neighbour on the elicitability axis — pre-empt "isn't this just convex-scoring risk RL?". |
| **URDP** | arXiv:2507.02256 (Jul 2025) | Eureka-lineage uncertainty-aware reward design + uncertainty-aware BO | Not financial, not CVaR; overlaps our GP-EI selection (R29). Cite for currency. NB a prior WebFetch falsely claimed URDP "feeds CVaR to the LLM" — **FALSE**; do not repeat. |

## 3. METHODS-STRENGTHEN — zero-compute, examiner-respected (Okhrati profile)

- **LEARN-Opt** (arXiv:2511.19355, Nov 2025): LLM-reward-design **performance decreases as the number of
  metrics increases** — independent external corroboration of our predicted H2 null. *Strongest single gift
  for the registered-null framing (Mayoian severity).* [Related Work + Discussion]
- **Fissler, Liu, Wang & Wei** (arXiv:2404.14136; *Math. Finance* 2025): generalises Fissler–Ziegel (2016)
  to a broad class of tail risk measures. **Upgrade the stale 2015/2016 elicitability cites to this.**
- **Coronéo & Iacone 2024** (arXiv:2409.12662): DM test loses power / spurious rejections under strong serial
  correlation of loss differentials — one sentence next to the HLN correction in the ES-backtest section.
- **López de Prado, Lipton & Zoonekynd 2025** (SSRN 5520741): DSR-originator's closed-form Sharpe sampling
  distribution under jointly non-Normal + serially-correlated returns. Refresh the DSR/PSR cite to 2025.
- **Hué, Hurlin & Lu 2024** (arXiv:2405.02012): ES backtest decomposing violations into duration vs severity
  (finite-sample friendly). [Future Work / robustness]
- **AdaStop** (arXiv:2306.10882; **TMLR Dec 2024**): adaptive group-sequential how-many-seeds with FWER
  control — freshest peer-reviewed work in the seed-budget lane (R31); cite AND differentiate (we are
  pre-registered fixed-N rliable, not frequentist-sequential).
- **PyTorch determinism notes + Nagarajan et al.** (arXiv:1809.05676): seeds ≠ bit-identity across
  hardware/GPU — citable basis for the device-pin/TF32 amendment and for bounding the reproducibility claim.
- **Sandbox honesty corpus** — pysandbox (author: in-process sandboxing is impossible), RestrictedPython's
  own "not a sandbox" disclaimer, Pyodide CVEs (WASM ≠ boundary): grounds the disclosure that *the AST
  allowlist is a correctness/determinism hygiene gate, not a security boundary* (the generator is our own
  non-adversarial Claude model on a private machine). Already implemented; cite to make it deliberate.

## 4. CITE / DEPEND vs REIMPLEMENT (licensing-driven — document the choice)

- **Depend + cite (permissive, pin versions):** rliable (Apache-2.0, archived = stable), pyextremes
  (MIT, EVT/GPD), sb3-contrib / SB3 / d3rlpy (MIT).
- **Reimplement + cite the papers (a *necessary* engineering choice, not optional):** FZ0/ES backtest —
  `esback`/`esreg` are **GPL-3, R-only**; DSR/PBO-CSCV — `mlfinlab` went **commercial/All-Rights-Reserved**,
  `pypbo` is **viral AGPL-3**. So the hand-written FZ0/ES + DSR/PBO code is *forced* by licensing; frame it
  as defensible and **validate against the R/AGPL references on fixtures** (a robustness exhibit).
- **Patterns only (frozen scope — borrow design, not code):** CleanRL seeding recipe; Reflexion
  memory-mode framing; Auto-MC-Reward critic-gate; Hydra resolved-config-per-run snapshot; on the Linux GPU
  host optionally wrap reward-eval in bubblewrap/nsjail (Linux-only; N/A on the Windows laptop).

## 5. Safe engineering hardenings (NON-frozen surfaces only)

- **Pin tool versions:** pre-commit hook `rev:`s are already tag-pinned (v4.6.0 / ruff v0.5.7 / mypy v1.11.1);
  consider `required-version` in `[tool.ruff]` to match (only if local ruff == 0.5.7, else it self-blocks).
- **Determinism block + replay test:** ensure `torch.use_deterministic_algorithms(True)`,
  `cudnn.deterministic=True/benchmark=False`, `CUBLAS_WORKSPACE_CONFIG`, seeded DataLoader workers — and a
  test asserting bit-identical repeat output (covered by the new `tests/test_seeding.py` additions).
- **Academic-signaling (presentation, zero risk):** Papers-with-Code 5-item README spine; `CITATION.cff`
  (present) → Zenodo release DOI; name the ADR format (Nygard/MADR); shields.io badges; cite the ML
  Reproducibility Checklist (Pineau) + The Turing Way in Methods.
- **Explicitly REJECTED (scope/licence/determinism):** repo restructure to a new src layout pre-submission;
  Snowflake/DVC/W&B-cloud (LSEG derived-data licence); any LLM step inside the CI/reproducibility gate;
  adding new estimators (e.g. nsEVDx non-stationary GPD, Troop UPOT) to the frozen pipeline → all **Future
  Work**.

## 6. Integrity — UNVERIFIED IDs (do NOT cite as confirmed)

Search-listing-only; confirm against arXiv/journal before any use: reward-modeling survey "2602.09305",
Rubric-Grounded RL "2605.08061", quantile-RM "2409.10164" (abstract-only), Wang & Liu JRFM 2025 (journal,
RePEc not arXiv), Grant et al. multi-horizon DM (J. Forecasting 2026), "Lambda-ES" 2512.23139, LdP "New
Standard" SSRN 5950754 (slides only), MadEvolve 2605.23007, qlib release date. Vendor sandbox growth figures
(E2B/Modal/Daytona) are vendor-sourced. Anything `% VERIFY` in `paper/refs.bib` stays so until checked.

## 7. Three cheapest grade-moving moves (all PDF prose, for later)

1. Build the FinRL-DeepSeek + CARD + convex-scoring-RL fences in Related Work.
2. Lean on LEARN-Opt as independent corroboration of the predicted null.
3. Upgrade elicitability cites to Fissler-Liu-Wang-Wei 2024 and add the Coronéo–Iacone DM-power caveat.
