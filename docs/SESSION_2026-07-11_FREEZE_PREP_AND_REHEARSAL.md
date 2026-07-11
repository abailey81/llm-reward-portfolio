# Session log 2026-07-10 (evening) → 2026-07-11 (overnight) — freeze-prep, deep sweep, live rehearsal

Everything since `docs/SESSION_2026-07-10_MYRIAD_FIRST_CONTACT.md` and CHANGELOG `[2026-07-10]`.
Chronological. Every claim was verified first-hand in-session. The pre-registration is **freeze-ready
but NOT yet frozen** — freezing is Tamer's act. Canonical hash chain this session:
`1c6b76b6 → 296a19ee → 4b116f64 → af385617 → 79a6db44` (each hop an authorized pre-freeze edit; no
decision changed except the seed count, which is Amendment E1).

---

## 1. Supervisor meeting + the seed decision

Tamer met Dr Okhrati. Outcome: **Ramin approved the design**; Tamer ratified the assurance-tier ladder
and instructed the freeze. (Beforehand I had prepared a spoken meeting script and rewritten it into a
natural human register at Tamer's request — no em dashes/semicolons, mid-level vocabulary — plus a
Qwen-explainer, all covering the seven arms, the 200k-step budget, the seed maths, the CVaR-leg
correction, and the eight questions.)

## 2. Amendment E1 — the seed decision RECORDED, then upgraded to 7 rungs

**First recording (4 rungs).** The per-arm winner seed count moved from the bare list `[0..29]` (n=30)
to the tiered schema `seeds: {mode: tiered, tiers: [30, 340, 403, 568]}` (flat `[0..567]`, headline 568,
primary target 403, exogenous stopping tier). Recorded across `config/campaign.yaml`,
`config/preregistration.yaml`, `config/inference.yaml`, and a full E1 amendment block +
amendment-table row in `PREREGISTRATION.md`; `power_analysis.ASSURANCE_TIER_BOUNDS` set to match.

**Three tiered-schema bugs caught en route** (the deep check earning its keep): `determine_design.py`
read `config_n_seeds` via a raw `len()` — on the dict schema that returns 2 (the key count), so
`n_seeds` would have stayed `PENDING` forever; `power_analysis.py` in two places silently fell back to
the literal 30 / did `list(dict)` yielding the keys. All three now resolve through
`src.utils.seeds.resolve_seeds`. Three stale freeze-test fixtures that pinned the old `[0..29]` literal
were updated to the ratified schema.

**Upgrade to 7 rungs (Tamer's insight).** Tamer flagged the **30 → 340 gap** as a real flaw: rungs are
the pre-declared fallback points if a run is truncated by the deadline or the queue, so that ~3,700-
training gap meant a truncation at, e.g., seed 250 would discard 220 completed paired seeds back to 30.
Upgraded to **`[30, 100, 189, 279, 340, 403, 568]`**. Each rung now has a pre-registered meaning:

| Rung | Meaning |
|---|---|
| 30 | distinction-bankable core (CVaR-5% leg already conclusive; mechanism complete) |
| 100 | σ-precision (the σ_D estimate itself tightens to ≈ ±10%) |
| 189 | Monte-Carlo point-estimate power (Sharpe leg decisive if σ_D is as measured) |
| 279 / 340 / 403 / 568 | 80% / 90% / **95% (primary target)** / 99% equivalence assurance (χ² upper bound on σ_D) |

Zero extra compute — tiers are order-only labels on the same seed set. The intermediate rungs cap the
worst-case seeds discarded on an exogenous truncation. Committed with the sweep fixes in **79bbfd6**.

## 3. Deep pre-freeze sweep — five independent auditors, every finding fixed

Ran five read-only auditors in parallel before freezing:

- **Statistical design (arithmetic re-derived):** Var(D) = 2·0.244²·(1−(−0.141)) = 0.1359 → σ_D =
  0.369 ✓; 189·(14/χ²) reproduces the ladder 279/340/403/568 exactly ✓; m=6 union + [3,3] IUT
  partition consistent ✓; TOST margin 0.05 consistent ✓; R64 one-sided p is the direct upper-tail
  probability ✓. Found the verbatim bankable-null statement still said "30 winner seeds" (a hash-bound
  self-contradiction against E1) and the H1/H3 seed comments in `campaign.yaml`.
- **Theory (the examiner's attack surface):** CVaR sign convention, Le Cam deficiency **direction**
  (Cor 3.3 correctly orients δ(scalar,vec) > 0), DPI equality gated on strict convexity, and the
  Fissler–Ziegel elicitability chain — all correct. No misattribution to Okhrati (only Khraishi &
  Okhrati 2022 CQL + Hartley…Okhrati 2025 ACL). CLEAN.
- **Leakage / splits / survivorship:** re-derived the 60-session purge at both boundaries (first test
  session 2020-03-30, matching the record); proved survivorship-freeness in the real headline universe
  (Wachovia and AIG retained through 2008 with true catastrophic returns; 333/963 delisted names kept);
  sealed test unreachable by selection; fed tail fitted on train returns only. EXEMPLARY.
- **Identification / arms:** only the feedback block varies across arms; the 7-arm roster is identical
  in all five locations; placebo_shuffled is a correct derangement excluded from the m=6 family and the
  mechanism pools; the base prompts are tail-neutral and covered by the freeze gate. HOLDS.
- **Paper vs frozen design:** flagged six stale "30 seeds" references in CH4/CH5/CH6/APPENDIX_B and
  three inside `PREREGISTRATION.md` itself.

**All freeze-blockers fixed** (same root cause — E1 not propagated into older passages): the hash-bound
self-contradictions in `PREREGISTRATION.md` (verbatim null, R64 invariants, sub-tests caveat, §12 D2
re-affirmation) and `config/campaign.yaml`/`config/preregistration.yaml`; **three operational
seed-default bugs** (`resume_audit.py` / `run_campaign_cluster.py` / `install_onstart_task.ps1`
defaulted `0-402` or `0-29` → would silently skip seeds 403–567; now `0-567`); superseded banners on the
arm-adaptive `SEED_DECISION` doc and `COMPUTE_AND_TRAINING_TIME.md`; the inverted "more seeds than the
campaign" comparison in `contamination.py`; and the six paper seed refs. Gate 21/21 GREEN,
`determine_design` FREEZE-READY, full suite **2095 passed**. Deferred (non-hash-bound, post-freeze):
extending the tail-neutrality scan to the in-code reflection preamble, and the bulk scattered "30 seeds"
doc comments (high false-positive — many are legitimately tier-0).

## 4. G1 anchor — the measured per-training time (committed eff0dca)

A real short SAC training on a Myriad **V100-PCIE-32GB**: **102.2 steps/s, 8.15 min/50k → ≈32.6
min/training at B\*=200k** (critic loss 418 → 0.07). **≈1.87× the laptop**, in the pre-registered
1.4–2.5× band. The launcher fix was confirmed on both a V100 and an A100-PCIE-40GB, and the A100 is
**not faster** per training (its value is denser packing for Stage 2 only). Recorded in
`docs/G0_G1_CLUSTER_CERTIFICATION_2026-07-10.md`.

## 5. Live end-to-end rehearsal — the first real run of the whole cluster path

Tamer wanted a small real prototype with LLMs to shake out every issue before the campaign. Ran
`run_campaign_cluster.py` (3 arms, 2 generations, 1 seed, 10k steps, real **Qwen3-Coder via OpenRouter**,
`--pass-mode B`, `--synthetic`, `outputs/proto_timing`, spend-capped). It was the first-ever live
execution of the campaign path (previously only dry-run + fake-cluster unit tested), and it caught
**five real campaign-breaking issues**, all fixed and committed (`fb3fc11`, `8118fb8`; ruff clean, 280
cluster tests):

1. **Container launcher not threaded** into the campaign path — the cluster venv is built inside
   `python311.sif`, so trainings must launch via Apptainer; the campaign rendered the bare-venv launcher
   → would fail on every node. Threaded `apptainer_sif` through `build_cluster_run` → `driver` →
   `render_jobscript` + a `--apptainer-sif` flag (default `~/python311.sif`).
2. **Driver didn't `load_env()`** — authoring happens on the laptop-side driver before shipping specs,
   so it needs the API key in `os.environ`; real authoring crashed "key unset". Added.
3. **cp1251 console crash** — the Russian-locale Windows default encoding crashed the ssh reader on any
   non-ASCII byte from the cluster. Pinned `ssh_runner` to utf-8/`errors=replace`.
4. **Empty gold dir under `--synthetic`** — the jobscript still `--bind`s the gold dir into the
   container and Apptainer errors if the path is absent. Create the input dir.
5. **The throughput finding + `--cores-per-training` lever (the decisive one).** Myriad GPU nodes sit at
   **load=36 — CPU-saturated — with free GPUs**, so a job's **CPU-core** request is the binding
   scheduling constraint, not the GPU. The default 4 cores/training is over-provisioned (a training uses
   <1 core), so pack=5 → 20 cores would not place. Added `cores_per_training` threaded to
   `render_jobscript` (cores = cores_per_training × pack; default unchanged) + a `--cores-per-training`
   flag, so the campaign can shrink the footprint and packed jobs actually place. **This reframes
   throughput planning: concurrency is gated by GPU-node cores, which depend on total cluster load — so
   max throughput needs a small core footprint plus off-peak timing or a CRAG reservation.**

After the fixes, Qwen authoring (`HTTP 200 OK`) and submission worked for all three arms. The run is
queued behind cluster-wide core saturation (every GPU node at load=36, zero free cores), so no training
had executed yet at session pause — the **Apptainer-on-node path is the one piece still to validate
live**, and the precise campaign-time answer is owed once a training runs and a packing probe measures
the factor F.

## 6. Overnight autonomous setup

Tamer went to sleep with "monitor everything, make it strictly flawless, fix everything." Set up:
- Laptop sleep/hibernate disabled so the driver + VPN survive the night.
- A persistent poller (`bd95x8oat`) that fires on the first training record (= live Apptainer
  validation) or a node-error log; the driver task (`bmtximiqo`) notifies on completion/crash.
- The memory cursor updated with the full state.
- Guardrails held: no freeze, no push, no venue switch to the laptop without Tamer's word.

## 7. Precise campaign-time — the framework (answer owed once the rehearsal completes + F is measured)

- Exact GPU-hours (fixed): ~2,760 to the 403 target, ~3,830 to the 568 ceiling.
- `days = GPU-hours ÷ (packing-factor F × GPUs-held × 24)`.
- Per-training time: measured (32.6 min). Total trainings: known. **F: not yet measured** (packing probe
  is queue-blocked). **GPUs-held: fair-share-variable** — the full-pool max is < 1 day; realistic is a
  few days; a CRAG reservation makes it a single guaranteed number.

## 8. Open threads

- **When the rehearsal runs:** validate the Apptainer-on-node path; fix any node bug; measure real stage
  timings; run a packing probe for F; give Tamer the precise campaign-time answer.
- **Revert** `config/prototype.yaml`'s `llm` block from the TEMP Qwen setting back to
  `anthropic`/`claude-sonnet-4-6` after the smoke (not committed).
- **Pending Tamer (his acts only):** run `scripts/freeze.py` (stamps `frozen: true` + `freeze_hash`
  `79a6db44`); force-push the two branches (history already rewritten to sole-author Tamer, byte-identical
  trees); Anthropic top-up ~$70; rotate the UCL password.
