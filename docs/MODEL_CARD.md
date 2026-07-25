# Model Card — `llm-reward-portfolio`

A Model Card following the schema of Mitchell et al. 2019, "Model Cards for Model Reporting"
(FAT* 2019, arXiv:1810.03993 — % VERIFY). This card documents **two coupled models** studied in
the dissertation:

- **(a) the fixed RL portfolio agent** — a Stable-Baselines3 SAC policy that allocates over a
  30-asset long-only simplex, held architecturally + hyperparameter-fixed across all arms; and
- **(b) the LLM reward-designer** — a Claude model (Sonnet 4.6 prototype → Opus 5 campaign) that
  **authors the reward-function code** the agent then optimizes, inside an Eureka-style reflection loop.

The headline experiment varies **only the feedback channel** fed to model (b) — multi-level
tail-risk statistics vs a scalar performance number — while holding model (a) fixed. All
performance numbers are **TBD — populated after the campaign run**; the campaign has not yet been
executed (the pre-registration is not yet frozen: `config/preregistration.yaml: frozen: false`,
`freeze_hash: null`).

---

## Model Details

### (a) Fixed RL portfolio agent
- **Algorithm.** Stable-Baselines3 **SAC** (Soft Actor-Critic; Haarnoja et al. 2018), `MlpPolicy`.
  Referenced as the fixed "headline agent" (audit A-1) in `src/agents/factory.py`
  (`HEADLINE_ALGO = "SAC"`) and `src/agents/trainer.py`.
- **Secondary critic experiment (not the headline).** sb3-contrib **TQC** (truncated-quantile
  critic; `DISTRIBUTIONAL_ALGO = "TQC"`), run only if its Phase-0 smoke is green. This is the
  *mean-critic vs truncated-quantile-critic* contrast (audit A-2), reported separately from H2.
- **Resolved hyperparameters** (`src/agents/trainer.py::resolve_agent_kwargs`; live source is the
  run config, NOT `config/algos.yaml`, which is a documentation template):
  `learning_rate=3e-4`, `batch_size=256`, `gamma=0.99`, `ent_coef="auto"`,
  `learning_starts=1000` (floored at 1000 to match the Phase-0 gate; SB3's unset default is 100),
  `buffer_size = train_steps_per_candidate` (memory-safe, ADR-025 — not the 1M default that would OOM).
  Held **identical across all feedback arms** so performance differences are attributable to the
  reward, not the learner (runtime equivalence test in `src/arms/factory.py`).
- **Numerical augmentations applied uniformly across arms** (`src/agents/trainer.py`,
  `src/agents/popart.py`):
  - **PopArt-style value-target scale normalization** (default on) — divides only the critic
    learning signal by a running `sqrt(EMA[r²])` so a large-magnitude LLM-authored reward cannot
    explode the Q-target. `info["port_ret"]` (the object of study) is forwarded unchanged;
    `norm_reward` stays `False`.
  - **Train-only observation normalization** — SB3 `VecNormalize(norm_obs=True, norm_reward=False)`;
    the running statistics are frozen on the train period and re-applied at eval (no val-set leakage).
  - **TF32 matmul precision** (default on; config key `tf32`) applied identically in every training
    path (serial / SEARCH / TEST) so the winner is evaluated under the precision it was selected under.
- **Observation space.** 1,893-dim per `src/agents/trainer.py` (per-asset 60-day return lookback,
  realized-vol windows [20, 60], lagged VIX, previous weights; see `config/environment.yaml`).
- **Action space.** Pre-softmax logits in `[-10, 10]` projected to a long-only simplex over 30
  assets + cash (`config/environment.yaml: action`).

### (b) LLM reward-designer
- **Prototype author.** Claude **Sonnet 4.6** (`model_snapshot: "claude-sonnet-4-6"`,
  `config/prototype.yaml`; ADR-038), native Anthropic SDK, `temperature=1.0` for within-generation
  diversity. The prototype is **directional/plumbing-only — no prototype number enters the
  dissertation.**
- **Campaign author.** Claude **Opus 5** (`model_snapshot: "claude-opus-5"`, `config/campaign.yaml`
  + `config/llm.yaml`; ADR-038). Opus 5 rejects the `temperature` parameter, so within-generation
  diversity comes from **prompt variation** (`diversity_prompt_variation: true`), applied uniformly
  across arms (not an H2 confound).
- **Same vendor + key.** Both are the **single Claude model family**, same `ANTHROPIC_API_KEY`.
  The open-weights second-model contamination check is **pinned (2026-07-02): `qwen/qwen3-coder` via
  OpenRouter** (`config/llm.yaml`, R71; wiring + key-gated smoke built) but **not yet executed** — the
  write-up must never say "LLMs"/"models" in the plural for the authored rewards until the secondary
  Qwen panel has actually run (report-only leg).
- **Loop.** Eureka-style reflection (`src/llm/loop.py`): 6 generations × 5 candidates/generation =
  30-candidate budget per arm (`config/campaign.yaml`, `config/llm.yaml`). The H3 single-shot control
  spends the same 30-candidate budget at `generations: 1`.
- **Untrusted-code handling.** LLM-authored reward code is AST-gated once then run in-process
  (`src/sandbox/executor.py`, `src/reward/contract.py`); only anonymised arrays (no tickers, no
  dates) ever reach a reward.
- **Provenance.** Every rendered prompt, raw response, and parsed reward is archived
  (`config/llm.yaml: archive: true`, `archive_dir: outputs/runs`); results **replay from the
  archive — LLM calls are non-deterministic and are not regenerated** (audit C-2).

### Common
- **Version.** Package `0.1.0` (`pyproject.toml`).
- **License.** MIT (code); the data is licensed Refinitiv/LSEG and **not redistributable**.
- **Author / owner.** Tamer Atesyakar (UCL MSc Banking & Digital Finance, Institute of Finance and
  Technology), supervised by Dr Ramin Okhrati.
- **Pre-registration.** `PREREGISTRATION.md` + machine mirror `config/preregistration.yaml`;
  frozen by `scripts/freeze.py` (SHA-256). Currently `frozen: false` (latest computed canonical
  hash `d9204087…` is pre-freeze — it moved intentionally with the Split-C/univ5 rebuild, 3 bound
  configs + prereg changed; CHANGELOG `[2026-07-02c]`).

## Intended Use
- **Primary intended use.** A controlled research experiment for an MSc dissertation (target also:
  an ICAIF '26 paper): does feeding an LLM reward-designer **multi-level tail-risk feedback** (six
  left-tail scalars) yield rewards whose frozen winners beat scalar/placebo/single-CVaR controls
  out-of-sample, at matched compute? The headline claim is **comparative** ("distributional vs
  scalar at matched compute"), explicitly **not** "beats the market".
- **Intended users.** The author, the supervisor/examiners, and ML-reproducibility reviewers.
- **Out-of-scope / NOT intended.** Live trading, investment advice, or production allocation. The
  agent trades a fixed point-in-time 2005-cohort 30-name universe; it is a methodological probe, not
  a deployable strategy. No multi-agent system, RAG, sentiment pipeline, options, or other asset
  classes (scope is frozen — `CLAUDE.md`).

## Factors
- **Feedback channel (the studied factor).** The 7 arms (`config/arms.yaml`,
  `config/preregistration.yaml`): `distributional`, `scalar`, `placebo` (length/field-matched inert
  block), `scalar_cvar5` (scalar + one downside number), `placebo_shuffled` (distributional's exact
  block, values deranged — the structure-vs-content control, DISJOINT from the m=6 family),
  `random_search` (H4a, search over code), `bayes_opt` (H4b, BO over a fixed parametric template).
- **Market regime.** Regime labelling (`src/regimes/`) feeds the power analysis; the test span
  (2020–2026H1, Split C) spans the 2020 COVID stress, the 2022 hiking cycle, the 2023–25 rally, and
  settled H1-2026.
- **Seeds.** 30 winner seeds `[0..29]` (Amendment D2; Henderson 2018, Colas et al. ≥20) carry the
  across-seed (training-RNG) variance into the inference.
- **Delisting-return assumption.** A pre-registered sensitivity band d ∈ {0, −30%, −55%, −100%}
  (`analyze_campaign.delisting_band`) over the 333 delisting cells. The 2026-07-02 observed-terminal
  audit (ADR-051) found the vendor daily series already carries the realised terminal for **all 333**
  dead names — the corrected Shumway panel (univ5s) equals the zero-fill headline on returns, and the
  band now brackets residual post-delisting value loss (univ4 = the disclosed contaminated heavy end).

## Metrics
Pre-registered (`PREREGISTRATION.md` §10, `config/preregistration.yaml: inference`); all numbers TBD
post-campaign.
- **Headline H2 — two co-primary intersection–union tests** (R25): **H2-RA** (3-leg IUT on Sharpe
  IQM, distributional vs each of scalar/placebo/scalar_cvar5, one-sided α=0.05) and **H2-Tail**
  (parallel 3-leg IUT on CVaR-5%), corroborated (not gated) by the FZ0/(VaR, ES) Diebold–Mariano
  comparative backtest (Fissler–Ziegel 2016; Nolde–Ziegel 2017).
- **Risk-adjusted performance:** out-of-sample **Sharpe (IQM across seeds)**.
- **Tail outcome:** realized **CVaR at 5%** (CVaR-1% retained but flagged high-variance).
- **Overfitting guards:** **PBO/CSCV** (primary), **Deflated Sharpe** (secondary).
- **Difference tests:** per-seed IQM + paired stratified bootstrap over shared training seeds
  (re-centred basic stationary block bootstrap, Politis–Romano 1994);
  bespoke two-sample CVaR-difference test (size certified by `null_calibration`).
- **Multiplicity:** Benjamini–Hochberg FDR q=0.05 (primary) / Romano–Wolf (FWER alternative) over the
  frozen m=6 union, **reported as sensitivity** — the IUT conjunction is the headline correction
  (Berger 1982). Harvey–Liu–Zhu t>3 hurdle scoped to absolute-alpha claims only.
- **Equivalence (bankable null):** TOST against SESOI = 0.05 DSR units (Lakens et al. 2018).
- **Seed reporting:** rliable IQM, probability of improvement, stratified-bootstrap CIs.

## Training Data
See **`docs/DATASHEET_v1.md`** (datasheet following Gebru et al. 2021 — % VERIFY) for full
provenance; not duplicated here. In brief: a single survivorship-free **point-in-time Refinitiv/LSEG**
US large-cap equity panel, `data/gold/returns_panel_univ5.parquet` (**5,406 × 963**), 2005-01-03 →
2026-06-30 (settled cutoff; ADR-051, prereg R73). Headline panel is **univ5** (zero-fill /
`liquidate_to_cash` — no fabricated delisting losses; the R44 semantics carried forward), selected by
the hash-bound `config/data.yaml: gold.suffix: univ5`; **univ3** (5,283 × 953, 2005–2025) is the
frozen pre-Split-C reference, reproduced byte-exactly on the overlap (0 changed cells).
**Train split (SPLIT C): 2005–2016** (agent learns + tail feedback measured here). Inter-split purge =
max(embargo 21, lookback 60) = **60 sessions** (López de Prado 2018); resolved windows are fail-loud
asserted against `expected_windows.univ5` (`config/inference.yaml`). Data is **licensed and not
redistributable** — the repo ships SHA-256 checksums + the acquisition pipeline + a synthetic panel
of identical shape.

## Evaluation Data
- **Validation 2017–2019** (Split C; executed start 2017-03-30 after the 60-session purge) — winner
  selection via **validation Deflated Sharpe** (reward-independent; λ_cvar = 0.0, tail-blind). Fed
  signal (train returns) and selection signal (val returns) are on different splits.
- **Test 2020–2026H1** (2020-01-01 → 2026-06-30 settled cutoff; executed start 2020-03-30 after the
  purge) — **untouched until final inference**; the sealed leg on which all reported numbers are
  computed. The test leg trades the **2005-cohort PIT top-30** (a disclosed composition limitation,
  R17 — names delisted by the test era are held at 0%; not dev→test leakage, splits are disjoint +
  embargoed). A point-in-time walk-forward universe re-evaluation
  (`load_gold_panel(phase="walk_forward", …)`) is available as a gated robustness check.

## Quantitative Analyses
**TBD — populated after the campaign run.** No campaign numbers exist yet. The analysis entry point
is `scripts/analyze_campaign.py` (the headline `h2_conjunction` is wired into `write_report`, R16).
The pre-registered predictions (frozen before the sealed test) state the observable signature for
each mechanism branch — Strict / Weak / Null — so a result of any sign is a confirmed or refuted
prediction. The Sonnet prototype (directional, exploratory) showed negative responsiveness (≈ −0.05)
and an un-beaten placebo, predicting the **clean-null branch** the campaign will confirm or refute;
**no prototype number is reported.** Epistemic credit for a null rests on Mayoian error-statistical
severity (licensed by the frozen, deviation-free protocol; Rubin 2025) + garden-of-forking-paths
avoidance (Gelman & Loken 2014), reported via TOST equivalence — not a bare p>0.05.

## Ethical Considerations
- **Not financial advice.** Outputs must not be used for trading or allocation decisions; the model
  is a research instrument on a frozen historical universe.
- **Data licensing.** The underlying equity panel is licensed (Refinitiv/LSEG) and contractually
  non-redistributable; only checksums, the pipeline, and a synthetic panel are shipped.
- **Untrusted code execution.** The LLM authors executable reward code; it is AST-gated and run only
  on anonymised arrays. Reward code remains untrusted by design.
- **LLM contamination.** Reward-design priors are the **object of study** (H4), not a defended
  weakness; contamination is handled by structural blinding (anonymised arrays, no tickers/dates) and
  cutoff-stratified evaluation. A cross-family + open-weights model **panel** (Opus 5 primary + GPT-5.5 +
  Qwen3-Coder; ADR-039) is specified, to be ratified into the pre-registration before freeze.
- **Survivorship & delisting bias.** Honestly disclosed and since sharpened (ADR-051, 2026-07-02):
  the observed-terminal audit recovered the realised terminal for all 333 dead names from the vendor
  daily series, so the zero-fill headline (univ5, formerly univ3) already carries the realised
  delisting tail; univ4's unconditional Shumway surcharges both fabricate M&A losses AND double-count
  terminals already in the series — handled via a reported sensitivity band (univ4 = the disclosed
  contaminated heavy end), never as the headline truth.
- **Reproducibility / compute footprint.** The confirmatory campaign runs **laptop-only on the owned RTX 4050**
  (6 GB VRAM; n_gpu 2–3, TF32 on; no third-party cloud — **no cloud-compute budget**), projected at ~2–3 weeks
  for the model panel; no GPU-hour cost (owned hardware). The earlier "rented RTX 4090" framing is superseded
  (ADR-040); a WSL2/GPU speed path was probed and rejected (systematic install failure + no net benefit given the deadline).

## Caveats & Recommendations
- **All performance numbers are TBD** until the campaign runs; the pre-registration is **not yet
  frozen** (`frozen: false`, `freeze_hash: null`).
- **Likely-null headline, framed as such.** The study is powered + pre-registered to make a null a
  credible, bankable finding (TOST/severity), not a moved goalpost.
- **"Critic-agnostic" ≠ "agent-independent."** The fed tail is measured on the trained policy's own
  realized returns under the candidate reward — endogenous to the agent it steers. H2 compares two
  coupled reward→policy→measurement loops. Never write "works on any agent."
- **"Fixed agent" is fixed architecture + hyperparameters, not a fixed effective regulariser** —
  with `ent_coef="auto"` + PopArt, the effective entropy regularisation can vary with reward
  magnitude (made auditable by per-candidate `sigma_max` logging + the `popart=False` ablation).
- **Single model family.** One vendor (Claude), so the LLM-generality claim is limited; phrase
  accordingly.
- **Composition limitation.** Fixed 2005-cohort universe on the sealed test leg (R17), disclosed as a
  headline limitation with a gated PIT-walk-forward robustness check available.
- **Determinism is statistical, not bitwise** across CPU↔GPU / different-GPU / torch-release
  boundaries; report mean ± error bars over N seeds and replay LLM calls from the archive.
