# PLAN IF WE USE UCL MYRIAD — the single-IF, two-stage, zero-problem master plan

**Status:** conditional master plan, written 2026-07-06. Supersedes-as-operational
`docs/UCL_CLUSTER_ULTRAPLAN_2026-07-06.md` (which remains the design-rationale record for the
U/D-series). Grounded in: the ★ PRIORITIES (CLAUDE.md), the IFT guidelines + marking rubric +
4 sample dissertations (read first-hand 2026-07-06), Dr Okhrati's revealed grading function,
first-hand Myriad research (rc.ucl.ac.uk + T&Cs, fetched 2026-07-06), the σ_D/convergence pilots,
and the full live verification of every mechanism (2,004/2,004 tests; sandbox/inference/leakage/
resume probes ALL PASS, 2026-07-06).

---

## §0 THE BIG IF

> **THE IF: Tamer decides to go for the huge project on UCL Myriad.**
>
> Until he says GO, nothing changes anywhere: the ratified laptop **Design-L** remains the
> default and the freeze path is untouched. The moment he says GO, everything in this document
> executes as written — no further decision points except the pre-named prune points and the
> freeze-day choices listed in §9.
>
> **GO cannot harm the study**: the laptop track remains certified and auto-executes on any
> Myriad failure; all Myriad work before the freeze is reversible; and no confirmatory unit runs
> until every §6 rehearsal has passed.

- **GO means**: adopt the two-stage program below (Stage 1 SECURE → bank gate → Stage 2 ADVANCE)
  with Myriad as the compute substrate and the laptop as driver + fallback.
- **NOT-GO means**: Design-L (laptop; tier-ordered 403 arm-adaptive campaign) exactly as already
  planned in `docs/SEED_DECISION_2026-07-05.md` + `docs/CAMPAIGN_RUNBOOK.md`.

## §1 The finished object (what GO buys)

The **definitive controlled study of distributional feedback in LLM reward design**:
- **identified** — the 7-arm frozen contrast; only the feedback block varies (identification
  principle);
- **powered** — uniform n=403 (95% assurance at the σ_D upper CI; 99% option derived at freeze);
- **selection-denoised** — k=3 seeds per search candidate + winner's-curse shrinkage (D4);
- **variance-decomposed** — σ²_arm / σ²_draw / σ²_seed (D3), turning the σ_seed-dominance pilot
  finding into a quantified contribution;
- **pipeline-calibrated** — the whole procedure's empirical Type-I/power on synthetic ground
  truth (D5);
- **mechanism-resolved** — observationally (fingerprint / mediation / funnel / taxonomy /
  info-gap) AND interventionally (the D2+ designer-sensitivity probe);
- **dose-response-measured** — the reflection-value curve over generations {1,2,4,6,8} (D1),
  measured nowhere in the Eureka lineage;
- **generalization-tested** — across model families (Opus / GPT-5.5 / Qwen3-Coder), a second
  market (FTSE full + zero-shot transfer), and agent algorithms (PPO / TD3 / TQC);
- **reproducible** — one-command archive→figures replication package + OSF deposit (D8);
- all behind the SAME 4-analysis, 10,000-word body (depth-over-breadth is graded).

**Rubric mapping** (the 90–100 descriptors): symmetric full-power arms + measured-noise-responsive
design = "faultless execution"; the mechanism instruments + dose-response + interventional probe =
"unquestionable originality"; the generalization triad + calibration + replication package =
"outstanding contribution, publishable in a peer-reviewed journal" (TMLR-fit); the write-up map
(§8) + the second-marker legibility pass = "faultless communication". Okhrati's six revealed
rules are each served: intuition (one plain-language lead per result), depth-not-breadth (body
unchanged), honest null (pre-committed branches), EDA-motivates-method (F3 tail facts in the Data
section), originality foregrounded (mechanism first), mechanics (compute line, cross-refs,
section order — §8).

## §2 Invariants (non-negotiable at ANY compute)

| Invariant | Value | Reason |
|---|---|---|
| Identification | only the feedback block varies across arms | the causal contrast IS the study |
| Search width K | 30 candidates/arm | pre-registered matched budget; DSR deflation calibrated to it; multiplicity |
| Training budget B\* | 200,000 steps (unless the §3 B\*-gate moves it on measured evidence) | convergence pilot: ≥2× critic knee, below measured overfit onset |
| SESOI | 0.05 DSR | pre-registered |
| Testing family | m=6, two co-primary IUTs | pre-registered |
| Arms | the frozen 7 | frozen H2-family guard |
| Seeds | ≤403 (or the script-derived n₉₉) uniform | principled assurance sizing; >that is vanity |
| Body | 16-section order, ≤10,000 words, 4 deep analyses | guidelines + Okhrati's depth rule |

**Refusals that stand at any compute** (each answered elsewhere): no ablation arms (D2+ answers
which-statistic-matters interventionally); no new hypotheses/assets/options/2000-start; no
markets beyond FTSE; no prompt-encoding factor (future work); no >403-seeds vanity; no wider K;
no longer B\* without the gate. The rejected-extensions register applies unchanged.

## §3 THE PROGRAM — TWO STAGES (Tamer's security doctrine, 2026-07-06)

> "Secure the grade and the publishability FIRST; only then build advanced — you never know what
> will happen."

### STAGE 1 — SECURE (the initial project at FULL power; runs FIRST, alone, to completion; never pruned)

The original 7-arm study exactly as ratified, upgraded only on these axes:

1. **Uniform, NOT arm-adaptive seeds.** All 7 arms + the 4 H1 baselines + H3 at the SAME n.
   Default **n=403 (95% assurance)**. **99% option** = a derive-then-decide gate:
   `scripts/power_analysis.py` re-run at ratification for the 99% χ² upper-CI of σ_D → n₉₉
   (expected order ~500–600); adopt iff the G1-measured throughput prices it ≤ +3 days. No
   invented constants — the script derives, Tamer picks 95 or 99 at freeze.
2. **The B\* gate** ("maybe past 200k, if needed" made rigorous). A Myriad B\*-revalidation
   micro-pilot (the convergence ladder, 3 seeds × 5 budgets = 15 trainings ≈ 9 GPU-h) with the
   PRE-COMMITTED rule: B\* moves above 200k ONLY if the cluster ladder shows eval still improving
   at 350k beyond the noise band (the laptop pilot showed the opposite — mild overfit). Expected
   outcome: 200k re-confirmed by TWO independent ladders on TWO platforms = a strengthened paper
   claim. Runs inside G1, before the freeze.
3. **k=3 multi-seed search selection (Stage-1 DEFAULT).** Every search candidate trains at 3
   seeds; selection/reflection on the IQM. Attacks the MEASURED σ_seed (0.244) selection noise at
   its source; the fed tail block becomes a 3-seed aggregate (cleaner mechanism signal); strictly
   exceeds Eureka's 1-policy selection rigor; "design responds to pilot data" = Okhrati's exact
   taste. Engineering ~1–2 days in Phase A. **Hard fallback, pre-written into the freeze text**:
   if k=3 is not engineered + re-certified by day 4, Stage 1 launches with the certified 1-seed
   pipeline and k=3 moves to Stage 2 as a replicate study. The freeze date never moves for it.
4. **D1 dose-response fully in Stage 1.** All five generation levels {1,2,4,6,8} at matched
   30-candidate budget. The confirmatory H3 statement stays the registered 6-vs-1 contrast; the
   intermediate points register ex-ante as exploratory trend description. The reflection-value
   CURVE becomes a headline figure of the BANKED study.
5. **In-situ convergence snapshots (cert-gated).** A light deterministic eval at {50k,100k,150k}
   inside every training (separate seeded eval env; no training-RNG consumption). Ships ONLY if
   the G1 byte-identity certification proves the callback leaves final weights untouched;
   dropped without regret otherwise. If shipped: "critic convergence verified in situ in ALL
   confirmatory trainings" — the definitive training-adequacy answer.
6. **Internal tier ordering kept** (crash insurance within the stage): canary (the first 3 H1
   baselines through the full production path before any Opus spend) → H2 arms' search → H2 test
   → remaining arms → H1 → H3 → D1 levels. Pair-adjacent CRN scheduling; counts-only monitoring;
   single-look discipline.

### THE BANK GATE (hard; nothing in Stage 2 starts before it)

Stage 1 100% complete → mirror chain VERIFIED (Myriad→laptop→D:→Mac, `verify-mirror` exit 0) →
the SINGLE pre-declared confirmatory analysis executed together with the **zero-compute depth
bundle**: **D3** variance decomposition (computable BECAUSE of k=3), **D4** winner's-curse
shrinkage, **D9** specification-curve + arm-label permutation panel — all CPU, all on Stage-1
outputs, all landing in the same Results draft → results snapshot + prereg-results bundle
archived (OSF optional) → Results numbers drafted into the W-track.

**From this moment the dissertation is COMPLETE AND PUBLISHABLE** — and already
selection-denoised, dose-response-measured, variance-decomposed, specification-curve-robust, and
two-platform-convergence-validated. "You never know what will happen" is now a design property.

**THE BANK-GATE RUNSHEET (2026-07-08 — the exact sequence, so "compute done → dissertation complete"
is one documented procedure, not tribal knowledge). Root = `outputs/campaign_cluster`.**
```bash
# 1. INTEGRITY: seal the local archive, verify the backup + every unit is present (resume_audit)
python scripts/archive_integrity.py write outputs/campaign_cluster
python scripts/archive_integrity.py verify-mirror D:/llm_rp_archive_mirror/campaign_cluster   # exit 0
python scripts/resume_audit.py outputs/campaign_cluster --arms <7 arms> \
    --baselines <4 H1> --seeds 0-402 --candidates 30 --k-search 3 \
    --mirror D:/llm_rp_archive_mirror/campaign_cluster        # integrity_ok, remaining_test_units==0
# 2. THE SINGLE CONFIRMATORY LOOK (H2 IUT + mechanism SQ1-3 + PBO/CSCV) — inspect the result HERE
python scripts/analyze_campaign.py --root outputs/campaign_cluster
# 3. THE ZERO-COMPUTE DEPTH BUNDLE (all CPU, on the Stage-1 outputs)
python scripts/variance_decomposition.py --root outputs/campaign_cluster        # D3 (uses k=3)
#   D4 winner's-curse shrinkage + D9 spec-curve/permutation land in the analyze_campaign report + the
#   inference modules; confirm each figure/table is emitted before drafting.
# 4. ARCHIVE the prereg-results bundle (frozen design + results snapshot; OSF-depositable)
python scripts/make_prereg_bundle.py --out outputs/prereg_results_bundle
```
Each step is idempotent + inspectable; step 2 is the pre-declared single look (do NOT peek before the
sweep is banked). After step 4 the Results numbers draft into the W-track and the dissertation is done.

**STAGE-1 INDEPENDENCE (absolute, by construction — Tamer's requirement, 2026-07-06):**
- **Compute**: no Stage-1 unit depends on any Stage-2 output.
- **Statistics**: the confirmatory analysis at the bank gate uses ONLY Stage-1 data; every
  Stage-2 item is report-only/exploratory and analyzed separately.
- **Write-up**: the PDF is FINISHED from Stage 1 alone — all four body analyses plus the
  D3/D4/D9 appendix bundle come from Stage-1 outputs. **No-forward-references rule**: the
  Stage-1 text never mentions or depends on a Stage-2 result; each completed Stage-2 item only
  ADDS one appendix row + one sentence, and a missing item leaves zero holes.
- **Grade**: the entire rubric case (§1) is made on Stage-1 content. Stage 2 is strictly an
  add-on for publishability armor.

### STAGE 2 — ADD-ON (strictly optional armor; all report-only/exploratory, statistically clean after the look). Restructured 2026-07-06 into a LEAN DEFAULT + a PREMIUM SHELF after Tamer flagged the API budget.

**LEAN DEFAULT (runs unless Tamer says stop) — API total just $9–18:**
| Item | API $ | GPU-h | Why it stays |
|---|---|---|---|
| U3 Qwen full replication | $1–3 | 554 | cross-model-family generalization — the flagship add-on, nearly free |
| D2+ probes, LEAN grid (60–100 authorings on a sampled reflection set) | $8–15 | 58 | the interventional mechanism instrument at ~¼ cost, most of the value |
| D5 calibration fleet — **RUNS ON THE LAPTOP from GO-day** (platform-neutral by design: synthetic, keyless, procedure-calibration; no homogeneity concern, no Stage-1 data touched → no forking paths; ~22 laptop-days at 3 workers → all 40 replicates done ~Jul 30, entirely OFF Myriad; pauses whenever the laptop runs the battery/freeze-gate; disclosed as executed on the development platform) | $0 (keyless stub) | 876 (laptop) | the "is your α really 0.05" answer — and it now arrives BEFORE the bank gate |
| D6 TQC · U5 PPO/TD3 · U4b zero-shot FTSE | $0 | 367 | algo + market robustness without any authoring |
| D3 · D4 · D9 · D8 | $0 | CPU | analyses + replication package |
| **LEAN STAGE 2 TOTAL** | **$9–18** | **~1,855 (= 876 on the LAPTOP + ~979 on Myriad → Myriad add-on time just ~3.4 d @C=12; everything done ~Aug 3–4 central case)** | |

**PREMIUM SHELF (runs ONLY on Tamer's explicit purchase — $72–135 of API he flagged as crazy):**
U2b independent search chains ($36–69; chain-level σ²_search — D3 already decomposes
candidate-vs-seed variance from the k=3 data for FREE, so this is a luxury) · D7 GPT-5.5 third
family ($25–45; Qwen already covers the bigger closed→open generalization axis) · U4 full FTSE
re-search ($11–21; U4b's zero-shot transfer already gives the market-transfer result at $0).
Each shelf item defaults to FUTURE WORK in CH7 if not purchased.

Stage 2 uses both pools freely (per-analysis device homogeneity still enforced).

**Design-time vs execution-time:** registrations cost nothing and cannot be added later — the
freeze includes ALL of: the uniform-n schema, the 95/99 choice, the B\*-gate outcome, k=3 (+its
fallback), D1's levels, §2a(h) for D2+, the two-pool declaration, and the dual-track fallback.
Stage-2 items are pre-registered-as-exploratory but executed only after the bank gate.

### THE EXACT CATALOGUE

**Precision note:** training COUNTS are exact arithmetic. The ONE estimated input is per-training
wall time: **V100 planning constant = 35 min = 0.583 h** (laptop-measured 61 min solo on
Windows/WDDM; Linux+V100 removes the measured WDDM overhead — central 1.75× faster, honest range
1.4–2.5× = 24–44 min). D5 stubs at 50k = 0.146 h. RE-MEASURED in G1 (day 2–4); every table
re-anchors from the measured value BEFORE Tamer freezes.

| Item | Exact composition | Trainings | GPU-h | API $ | Stage |
|---|---|---|---|---|---|
| S1-search | 7 arms × 30 cand × k3 (5 LLM: 450; random 90; bayes 90) | 630 | 367 | $18–35 Opus (150 authorings × $0.12–0.23) | 1 |
| S1-H3 search (gens=1) | 30 × k3 | 90 | 52 | +30 authorings ≈ $4–7 | 1 |
| S1-D1 extra search {2,4,8} | 3 × 30 × k3 | 270 | 157 | +90 authorings = $11–21 | 1 |
| S1-test | 7 arms × 403 seeds | 2,821 | 1,645 | — | 1 |
| S1-H3 winner test | 1 × 403 | 403 | 235 | — | 1 |
| S1-D1 winners test | 3 levels × 100 | 300 | 175 | — | 1 |
| S1-H1 baselines | 4 × 403 (first 3 = the canary) | 1,612 | 940 | — | 1 |
| S1-B\* micro-pilot | 5 budgets × 3 seeds | 15 | 9 | — | 1 (G1) |
| **STAGE 1 TOTAL** | | **6,141** | **3,580** | **$33–63** | |
| U3 Qwen full | search 5×30×k3=450 + winners 5×100=500 | 950 | 554 | $1–3 | 2 |
| D2+ probes | 250–400 authorings + 100 top-Δ trainings | 100 | 58 | $20–40 | 2 |
| U2b chains | 2 × 630 | 1,260 | 735 | $36–69 (300 authorings) | 2 |
| D6 TQC | 3 arms × 100 | 300 | 175 | — | 2 |
| D5 calibration | 40 replicates × 150 stub-50k | 6,000 | 876 | $0 (keyless stub) | 2 |
| D7 GPT-5.5 full | search 450 + winners 500 | 950 | 554 | $25–45 | 2 |
| U5 PPO/TD3 | 2 algos × 3 arms × 40 | 240 | 140 | — | 2 |
| U4b FTSE zero-shot | 3 arms × 30 | 90 | 52 | — | 2 |
| U4 FTSE lite | search 3×30×k3=270 + winners 3×30=90 | 360 | 210 | $11–21 (90 authorings) | 2 |
| **STAGE 2 TOTAL** | | **10,250** | **3,354** | **$93–178** | |
| **GRAND TOTAL** | | **16,391** | **6,934** | **$126–241** | |

D3/D4/D9/D8 = CPU/analysis, 0 GPU-h, $0.

**Marginal costs:** +1 uniform seed (12 test legs) = 12 trainings = 7.0 GPU-h · 99% option at
n₉₉=550 (indicative) = +1,764 trainings = +1,029 GPU-h = +3.6 days at C=12 · 1 sustained V100 =
24 GPU-h/day.

**Stage durations (GPU-h ÷ 24C):**
| Sustained GPUs C | Stage 1 (3,580 GPU-h) | Stage 2 (3,354 GPU-h) |
|---|---|---|
| 6 | 24.9 d | 23.3 d |
| **12 (central)** | **12.4 d** | **11.6 d** |
| 18 | 8.3 d | 7.8 d |
| 24 | 6.2 d | 5.8 d |
Sensitivity: at 24 min/training Stage 1 = 8.5 d @C=12; at 44 min = 15.6 d.

> **UNPACKED bound (2026-07-08 reconciliation).** The durations above are the CONSERVATIVE, UNPACKED
> figures (one training per GPU). GPU packing is now VALIDATED (device cgroups — see
> `docs/MYRIAD_DEEP_RESEARCH_2026-07-08.md`), so the CENTRAL packed figures apply a factor F≈1.75:
> Stage 1 @C=12 ≈ **7 d** (not 12.4), and the **distinction floor banks in ~1.3 d**. The packed per-tier
> table is `docs/GRADE_SECURITY_AND_TIER_DESIGN_2026-07-08.md §3`; both bounds clear the deadline. F is
> RE-MEASURED at G1 (the 2-process pack smoke).

**Pruning** = stopping Stage 2 early in reverse value order (U4 → U4b → U5 → D7 → D5 → D6 → U2b
→ D2+ → U3). **Stage 1 is never pruned — it IS the study.**

## §3b THE EUREKA RE-READ REGISTER (pillar fidelity audit vs the PDF, 2026-07-06)

| Eureka element (§3.1–3.3) | Our design | Verdict on GO |
|---|---|---|
| Environment as context (raw env source fed to the LLM) | Contract/spec description only (anonymization + prompt-hash + channel isolation) | KEEP deviation (disclosed); probe via D2+ env-source-enriched counterfactual |
| Evolutionary search, K=16 i.i.d./iteration, mutate-the-best | Serial reflect-on-best, 5/gen × 6 gens (K=30 frozen) | KEEP (K frozen; U2b's chains = the multi-chain analogue) |
| Reward reflection = per-component reward values at training CHECKPOINTS | Scalar DSR + the arm tail block — the manipulated variable, deliberately minimal | KEEP for confirmatory; probe via D2+ telemetry-enriched counterfactual ("did withholding Eureka-style telemetry handicap the designer?") |
| 1 policy per reward candidate (selection through unexamined seed noise) | k=3 + IQM selection | **WE EXCEED Eureka's rigor — state it in the paper** |
| Executability via resampling | AST gate + sandbox validation + matched-budget failure ledger | KEEP (stricter) |

**D2+ — the expanded designer-sensitivity grid** (absorbs every "what if we fed X" arm-candidate
WITHOUT new arms; §2a(h), ex-ante, report-only): (i) per-stat perturbation (×2, sign-flip);
(ii) ablate-one-stat; (iii) full-quantile-sketch enrichment; (iv) uncertainty-annotated (CI) tail
stats; (v) Eureka-style training-curve telemetry enrichment; (vi) env-source-context enrichment.
~250–400 authorings ≈ $20–40; optional top-Δ trainings on the second pool.

**New-arms verdict:** full-distribution / uncertainty / numeracy-scaffolded / telemetry /
env-source arms — ALL rejected as confirmatory arms (late prompt-hash churn, m-family amendment,
Okhrati's breadth penalty, register spirit) and ALL absorbed as D2+ probes. The full-distribution
arm is named the #1 future-work arm in CH7.

## §4 THE MYRIAD RULES REGISTER (R1–R14; researched 2026-07-06; every rule → built-in compliance)

| # | Rule / limit (rc.ucl.ac.uk docs + T&Cs) | Compliance response |
|---|---|---|
| R1 | Myriad reachable ONLY from UCL internal network / VPN | Laptop driver over the UCL VPN; disconnect-tolerant (resume idempotency + tar-over-ssh re-entry); VPN-drop rehearsed in G1 |
| R2 | Login nodes: 1 CPU-hour per process, culprits killed | NO resident driver on login nodes; driver = laptop (default) or a chained 1-core 72h D-node job (A′, only if compute-node outbound proves out in G1) |
| R3 | Queue caps ≈100 queued (max 1,000), ~10 submits/s | ALL bulk work as SGE ARRAYS (`-t 1-N -tc <throttle>`; one array = one job); never loop qsub |
| R4 | Walltime 72h (1-core) / 48h (multi-core) | Trainings request 3h (≥2× margin); drivers 72h/1-core |
| R5 | Home==Scratch (1TB), "not the sole repository", no uptime guarantee | Nightly mirror-back Myriad→laptop→D:→Mac + post-sync verify; nothing exists only on Myriad |
| R6 | ACFS backed daily; read-write on login, READ-ONLY on compute | Gold panel + frozen prereg bundle staged on ACFS (backed + immutable-to-jobs = free input integrity); outputs on Scratch |
| R7 | 180-day post-departure retention; 15-day home backups | Account-lifecycle EVACUATION checklist (graduation-aware); never rely on retention |
| R8 | Fair use; staff may kill jobs impairing shared resources | Etiquette by construction: 1-GPU/4-core/3h backfillable jobs, throttled arrays, no login-node compute, off-peak bulk submits |
| R9 | MANDATORY publication acknowledgment | Verbatim into the dissertation Acknowledgements + the paper: *"The authors acknowledge the use of the UCL Myriad High Performance Computing Facility (Myriad@UCL), and associated support services, in the completion of this work."* |
| R10 | No commercial use; no credential sharing; UCL Computing Regs | Academic use; API keys live ONLY in the driver-side gitignored .env — never inside job scripts on shared FS |
| R11 | ~74 shared GPUs total (38 V100 E/F + 24 A100-40 L + 12 A100-80 U/V) | Sustained-concurrency planning at 6/12/24; two-pool strategy (§5); G1 queue sampling before the timeline commits |
| R12 | Central modules are OLD (CUDA 11.2/11.3, PyTorch 1.11) | Own venv (torch 2.6.0 cu-wheels bundle the runtime); node DRIVER version checked in G1; **Apptainer CONFIRMED on Myriad** (singularity→apptainer, $HOME auto-bound) = hard fallback via the existing Plan-B Dockerfile |
| R13 | `#!/bin/bash -l` shebang; `-l mem=` is PER-CORE; `$TMPDIR` needs `-l tmpfs=` | All three encoded in the job template; per-job torch caches on $TMPDIR |
| R14 | Staff data-access terms (support/security/maintenance) | Licence-compatible (UCL is the LSEG licensee — confirmed YES 2026-07-06); noted in governance |

## §4b SUSTAINED-USE LEGALITY & THE THROUGHPUT MODEL ("are we allowed to train so long non-stop?")

- **Yes — and nothing we run is "non-stop".** The campaign = 16,391 INDEPENDENT jobs of ≤3h each
  via throttled arrays. No job approaches the 48h walltime. Sustained batch use IS the cluster's
  intended model; the docs' own long-computation guidance (checkpointed short jobs) is exactly
  our shape.
- **The real constraint is THROUGHPUT, not permission**: free use is FAIR-SHARE governed —
  priority decays with recent consumption → expect a front-loaded burst then a decaying rate.
  The docs explicitly acknowledge the free-tier ceiling ("researchers may require higher
  throughput than possible with free fair-share usage").
- **The two-stage doctrine is queue-optimal**: Stage 1 rides FRESH fair-share (max priority
  exactly when the secure stage needs it); Stage 2 rides the decayed tail through August.
- **Escalation #1 (free): Additional Resource Request → CRAG** (monthly, 2nd Tuesday → ~Jul 14 /
  ~Aug 11), submitted WITH the supervisor to rc-support. Criterion: "impact on other users not
  significant or of long duration" — our job shape qualifies by construction. ON GO: a short ARR
  co-signed by Dr Okhrati describing the campaign (~7,000 GPU-h over ~6 weeks, ≤3h single-GPU
  jobs, two pools). Optional insurance — fair-share alone plausibly sustains C≈8–16 — and doubles
  as the courtesy heads-up.
- **Escalation #2 (paid, last resort): Gold priority / node purchase** — exists; almost certainly
  unnecessary; named for completeness.
- **The measurement gate**: G1 submits probe ARRAYS to both pools and MEASURES achieved
  concurrency + wait times over 24–48h. The freeze-time timeline uses the MEASURED sustained C;
  the 95/99 decision prices against it. No hope-based planning.
- ARR quotas expire after 12 months (submission blocked at expiry; data deleted 3 months later) —
  irrelevant at our ~8-week horizon; wired into the evacuation checklist anyway.

## §5 SMART USAGE

- **VRAM right-sizing**: our trainings need ~2–3 GiB → the V100-16G pool (38 GPUs; the largest,
  least contended by big-model users) is the confirmatory home. A100-80G nodes are never
  requested.
- **Two-pool partition** (×2 throughput WITHOUT breaking device homogeneity): the confirmatory
  campaign (all Stage-1 units) entirely on the pinned EF/V100 pool; the Stage-2 fleet on
  L/A100-40G. Homogeneity holds within every analysis unit; pools never mix inside a contrast;
  declared in the freeze text. G1 benchmarks may swap which pool is which.
- **Job shape**: `-l gpu=1 -pe smp 4 -l mem=8G -l tmpfs=15G -l h_rt=3:0:0` + `-ac allow=EF` (or
  `L`). Small, backfill-friendly, fair-share-friendly.
- **Job template (verbatim)**:
  ```bash
  #!/bin/bash -l
  #$ -l gpu=1
  #$ -pe smp 4
  #$ -l mem=8G
  #$ -l tmpfs=15G
  #$ -l h_rt=3:0:0
  #$ -ac allow=EF
  #$ -wd /home/<user>/Scratch/llmrp
  source ~/venvs/llmrp/bin/activate   # or: apptainer exec ~/llmrp.sif ...
  export TORCH_HOME=$TMPDIR/torch
  python -m src.cluster.run_one --spec "$SPEC_DIR/task_${SGE_TASK_ID}.json"
  # trains ONE unit, writes the atomic record.json to Scratch, exits nonzero on failure
  ```
- **Driver loop (laptop, over VPN)**: author via APIs locally → write spec batch → tar-over-ssh
  push (V9 audit 2026-07-07: the driver host has NO rsync — only scp/ssh — so ALL transfer is tar
  piped through ssh; the pull is EXACT-incremental via the remote-vs-local record-dir diff, sound
  because records are immutable after their atomic commit) →
  `ssh qsub` ONE throttled array → poll the synced archive (records ARE the message queue;
  hash-verified replay semantics unchanged — verified live 2026-07-06) → next generation.
  Arm-serial authoring caps API concurrency (rate-limit safe); the 7 arms' training arrays
  interleave freely.
- **Monitoring**: sentinel (17 checks) + journal run on the laptop against the SYNCED mirror
  (verified live to work read-only on any archive root); a `qstat` poller adds the queue panel;
  Open OnDemand gives Tamer a browser view; the healthchecks deadman is unchanged.

**MAXIMUM-PARALLELISM AUDIT (what is parallel, what binds, and the two squeeze levers):**
- **93% of the GPU-hours are embarrassingly parallel** (every test seed, every H1/H3/D1-winner
  unit, all of Stage 2): submitted as arrays with `-tc` = the POOL SIZE (38 on EF) — never
  artificially throttled; fair-share is the only governor.
- **Per-arm phased pipeline, zero barriers**: the moment ANY arm's search completes, its winner
  freezes and its full 403-seed test array fires — via SGE dependency holds (`-hold_jid` on the
  arm's search-final marker), pre-submitted at launch so there is ZERO driver latency between
  search-end and test-flood. No arm ever waits for another arm.
- **All reflection chains concurrent from minute 0**: 5 LLM arms (6 gens × 15 parallel trainings
  each) + 3 D1 chains + random_search (90 parallel) + H1 flood (1,612 parallel) + B\* pilot.
- **The only sequential kernels (algorithmic, pre-registered, cannot be parallelized without
  changing the science):** each reflection chain's generation order (longest LLM chain ≈ 6 × 37
  min ≈ 3.7 h; D1 gens=8 chain ≈ 5 h) and **bayes_opt (30 sequential GP iterations ≈ 17.5 h)**
  — all fully HIDDEN under the test flood (they bind nothing unless C > ~150).
- **The two real caps:** (1) GRANTED concurrency (fair-share — measured in G1, upgradable via
  the ARR); (2) the 38-GPU V100 pool for Stage 1 (the device-homogeneity rule caps confirmatory
  concurrency at the pool size). **Absolute Stage-1 floor = 3,580 GPU-h ÷ (38×24) ≈ 3.9 days**
  — the design saturates anything the queue grants up to the entire pool.
- **ARR lever for maximum speed**: the CRAG request explicitly asks for a short priority window
  ("~3,600 GPU-h over 7–10 days on EF") — granted priority at 24–38 sustained turns Stage 1
  into a 4–6-day affair.

## §6 ZERO-PROBLEM ENGINEERING (prevent → detect → respond → REHEARSE before go-live)

| Class | Prevent | Detect | Respond | Rehearsal (in G1) |
|---|---|---|---|---|
| Access/VPN drop | idempotent tar-over-ssh; keepalive | driver retry log | auto-reconnect; resume | kill VPN mid-batch, watch self-heal |
| Login-node policy | no resident processes | — | — | n/a (designed out) |
| Driver crash (laptop) | archive-as-truth | deadman heartbeat | relaunch `--resume` | kill driver, resume, byte-compare |
| Node/job failure | 3h walltime margin | SGE exit codes + failure ledger | auto-requeue (max 2) then ledger | inject a failing task into an array |
| Queue starvation | backfill shape; two pools | qstat panel; ETA vs plan | §3 prune ladder; laptop absorbs the Stage-1 tail | probe-array wait sampling per pool |
| Driver/CUDA mismatch | own venv; G1 driver check | import smoke per node type | swap to the Apptainer image (confirmed available) | run BOTH venv + image smokes |
| Determinism drift | one pool per contrast; pinned GPU model | same-spec-twice compare | quarantine node type; re-pin | determinism control on BOTH pools |
| Scratch loss/purge | ACFS inputs; nightly mirror-back | post-sync verify (exit 9) | restore from the laptop mirror | delete a synced record, verify restore |
| Data integrity | SHA-256 manifest on arrival | verify_gold / archive_integrity | re-stage from the laptop | corrupt a staged byte, watch it fail loud |
| API outage/limits | arm-serial authoring; tenacity backoff | error taxonomy | training arrays continue (no API needed); authoring resumes | pause the .env key mid-generation |
| Account lifecycle | evacuation checklist | calendar reminder | full archive off-cluster | dry-run the evacuation pull |
| Human error | frozen configs on read-only ACFS; freeze-guard hook | freeze gate 20/20 | dual-track: the laptop auto-executes | full keyless dry-run END-TO-END on Myriad |

**GO-LIVE RULE: the confirmatory campaign starts ONLY after every rehearsal row passes** — the
`crash_rehearsal.py` philosophy (which caught a real resume bug) extended to the whole cluster.

## §7 EXECUTION PHASES & THE DATED CALENDAR (day 0 = GO; GO assumed Jul 8; central case C=12)

- **Phase A (day 0–2, laptop)**: ✅ BUILT (2026-07-08) — scheduler adapter `src/cluster/`
  (submit/poll/requeue, ARCHIVE-AS-TRUTH driver) + the generation-level orchestrator (`campaign.py`)
  + the `run_campaign_cluster.py` entry point, deep-audited + 51 tests GREEN. Remaining Phase-A units
  (gated on Tamer's seed ratification): k=3 aggregation (B-A2) ∥ per-arm seed schema + `--assurance`
  (B-A3) ∥ D1 config. Job template + `build_env.sh` DONE.
- **Phase B (day 1–4, Myriad, overlaps A)**: VPN + keys + ACFS staging + venv/Apptainer build +
  THE FULL G1 CERT (every §6 rehearsal + keyless dry-run + crash rehearsal + determinism controls
  + fps benchmark on EF and L + 30-way array scale test + B\* micro-pilot + queue-wait sampling).
  The timeline re-anchors on the MEASURED fps + MEASURED queue waits.
- **Phase C (day 4–6)**: pre-freeze edits (§9 list) → freeze gate 20/20 → **Tamer freezes
  (hard cap Jul 20)**.
- **Phase D — STAGE 1 ONLY**: canary → H2 search (k=3) → H2 test → full design at uniform n →
  D1 levels. 3,580 GPU-h.
- **Phase D′ — THE BANK GATE** (+1 day): mirror-verified → confirmatory analysis + D3/D4/D9
  bundle → archive → Results drafted. **Dissertation complete & advanced.**
- **Phase D″ — STAGE 2**: value-ordered on both pools; runs through August in the background
  while Tamer writes; an unfinished Stage-2 item simply doesn't enter the PDF.
- **Phase E (August)**: W-track write-up (the 17k→9.5k word surgery starts NOW regardless of the
  IF) → pre-submission sweep → submit ≤ Sep 1.

| Date | Milestone | Owner |
|---|---|---|
| Jul 8–10 | Phase A engineering | me |
| Jul 9–12 | Phase B: access + staging + FULL G1 cert + fps/queue MEASURED | me (+Tamer: VPN) |
| Jul 12–14 | Phase C: pre-freeze edits + gate 20/20 → **FREEZE Jul 14** (cap Jul 20) | **Tamer** |
| Jul 14 | Stage-1 launch (canary first) | queue |
| **Jul 26–27 (±3d)** | **STAGE 1 COMPLETE** (12.4d @C=12; Jul 22 @C=18; Aug 8 @C=6) | queue |
| **Jul 28** | **BANK GATE** — complete, verified, archived, drafted | me |
| Jul 28–Aug 20 | Stage 2 (11.6d compute @C=12) ∥ **Tamer writes** | queue ∥ Tamer |
| Aug 15 | Pre-declared single-look backstop date (safety only at C≥12) | — |
| Aug 22–26 | Pre-submission sweep (fence + citations + lay-reader + `--final` gate) | me |
| **Aug 28–29** | **SUBMIT** (deadline Sep 1; 3-day buffer) | **Tamer** |

**Fallbacks:** freeze slips to Jul 20 → Stage 1 done Aug 1–2, bank gate Aug 3, submission
unchanged · C=6 worst case → Stage 1 done Aug 8, bank gate Aug 9, Stage 2 pruned, submission
unchanged · Myriad certification fails → **Design-L executes on the laptop** (Tier 1 ~Jul 26,
full 403-adaptive ~Aug 9), submission unchanged.

**Storage (precise):** gold parquet ~40 MB; per-record 1–3 MB → 16,391 records ≈ 25–50 GB
Scratch; logs ≤5 GB; ACFS ≤1 GB; nightly mirror delta ≤10 GB (~30 min at 50 Mbps VPN). All
inside the 1 TB quota with >90% headroom.

## §8 WRITE-UP INTEGRATION MAP (nothing grows the body)

| Output | Body slot (≤1 paragraph) | Appendix | Figure/Table |
|---|---|---|---|
| Stage-1 confirmatory verdicts | Results core (already budgeted) | full tables | existing headline figures |
| D1 reflection-value curve | 1 paragraph in Results | curve table | **headline figure** |
| D3 variance decomposition | 1 paragraph (Discussion) | mixed-model table | stacked-bar |
| D4 shrinkage | 1 sentence beside DSR/PBO | estimator note | column in the winners table |
| D9 spec-curve + permutation | 1 sentence (robustness) | panel | specification-curve panel |
| D5 calibration | 1 sentence ("empirical α = …") | design + results table | one table |
| U3/D7 cross-model | 1 sentence (generalization) | per-family table | one appendix table |
| U4/U4b FTSE | 1 sentence | table | one appendix table |
| U5/D6 algo robustness | 1 sentence | table | one appendix table |
| D2+ probes | 1 paragraph in the mechanism section | probe grid | sensitivity heat-strip |
| Compute reporting | 1 line: "≈N GPU-h on Myriad@UCL (⟨GPU⟩), M wall days; pilots on an RTX-4050 laptop" | — | — |
| **R9 acknowledgment** | **Acknowledgements section, verbatim** | — | — |

Plus: the 16-section mapping (explicit Data section; Discussion and Conclusions & Recommendations
split — audited 2026-07-06), per-chapter post-surgery word targets, and the second-marker
lay-reader pass as an acceptance test.

## §9 BUDGET, DECISIONS, ASKS, AND THE GO CHECKLIST

**Budget (restructured 2026-07-06; lean default):** compute **$0** (fair-share; verify no Gold
charging at G0) · API: **Stage 1 = $33–63** (Opus authoring — the study itself) + **Stage 2 lean
default = $9–18** → **DEFAULT TOTAL = $42–81**, right at the historic ~$50 Opus anchor. The
premium shelf (U2b + D7 + U4 = **$72–135**) runs ONLY on Tamer's explicit purchase and defaults
to future-work. Storage within existing quotas.

**Freeze-day decisions (Tamer, all pre-framed):** (1) 95% (n=403) or 99% (script-derived n₉₉,
priced by measured throughput); (2) k=3 in Stage 1 (default) or the pre-written 1-seed fallback;
(3) B\*-gate outcome ratification (expected: stay 200k); (4) Stage-2 API gates (U2b, D7).

**Pre-freeze edit list (Phase C):** uniform-n seed schema (config + prereg §6) · k=3 wording +
fallback clause · D1 levels registered as exploratory · §2a(h) D2+ registration · the dual-track
+ two-pool declaration · the R9 acknowledgment into the front matter · freeze-gate mirror
updates · power-doc regen.

**Asks of Tamer (to open G0):** ① forward the allocation email details (system, account, quotas,
anything granted); ② get the UCL VPN working on the laptop; ③ API budget call for U2b/D7;
④ one line for the record: who confirmed the licence-on-UCL "yes"; ⑤ optional: tell Okhrati +
co-sign the ARR.

**THE GO CHECKLIST (when every box ticks, GO triggers Phase A the same day):**
- [ ] Allocation details received (G0)
- [ ] UCL VPN works from the laptop; ssh to login12/13 OK
- [ ] Licence provenance line recorded
- [ ] API budget decision made (minimum: Stage-1 $33–63 covered)
- [ ] Qwen DashScope activated (or the OpenRouter fallback keyed) — gates U3, the lean-Stage-2 flagship
- [ ] Tamer says **GO**

## §10 RESPECT LEVERS + GAP CLOSURES (added 2026-07-06 after Tamer's "more respected" directive)

**Seed decision: 99% ADOPTED (Tamer's call)** — n₉₉ script-derived at ratification (~500–600);
+1,764 trainings ≈ +1,029 GPU-h ≈ +3.6 days @C=12 (banked ~Jul 31 central case). Amendment
carries the one reviewer-proofing sentence: the σ_D estimate is unchanged by k=3 selection
(test-leg seed variance is a property of the trained policies, not of how the winner was picked).
Honest framing kept in the paper: the respect case rests on the SIZING PRINCIPLE + achieved CI,
not the assurance label.

**Respect levers (all near-zero cost, adopted):**
1. **OSF public timestamped pre-registration deposit at freeze — MANDATORY** (upgraded from
   optional; `make_prereg_bundle.py` already builds the bundle). Verifiable beats private.
2. **Open release of the authored-reward corpus** with the paper: prompts + every LLM-written
   reward program + fitness/provenance — a community artifact nobody in the Eureka lineage
   ships. Return VECTORS licence-gated pending LSEG derived-data advice; code/prompts/rewards/
   scalars are clean.
3. **"Verify-in-30-minutes" script** inside D8: one command re-derives 2–3 headline numbers from
   the archive.
4. **Red-team disclosure appendix**: the adversarial audit registers distilled into
   defects-found-and-dispositions — the epistemic-maturity signal Okhrati grades 5/5.
5. **Reproducibility-checklist appendix** (the existing checklist, declared formally).
6. Post-submission, Okhrati-advised: arXiv preprint.

**Gap closures (added to the calendar/checklists):**
- The 17k→9.5k WORD SURGERY starts NOW — blocks on nothing, the most grade-critical open task.
- **Supervisor section-feedback slot ~Aug 12–16**: send Okhrati Results+Discussion (guidelines
  explicitly permit section feedback) — free grade improvement, now scheduled.
- AI-assistance disclosure (UCL policy) filled at write-up — compliance-critical for an
  LLM-method study; Ethics/data-governance statement confirmed slotted.
- A named non-specialist lay reader recruited for the late-August second-marker legibility pass.
- Okhrati pivot sign-off remains the one external procedural blocker — chase with the ARR note.

---

# PART II — EXECUTION (added 2026-07-07 at Tamer's request; the executing model works FROM here)

## §11 THE EXECUTION PROTOCOL — how the executing model must operate ("act like Fable")

The executor of this plan MUST work in the following style — these are binding operating
instructions, distilled from the working mode that built and verified everything above:

1. **Ultrathink by default.** Reason deeply and exhaustively on every non-trivial step BEFORE
   acting. Weigh alternatives, name trade-offs, check the invariants (§2) against every idea.
   Never take the first plausible path; take the verified one.
2. **Verify, then claim — with real commands and observed output.** Never report "works",
   "passes", "green" without having run it and seen it. Quote the actual numbers (e.g.
   "2,004/2,004, exit 0", "240/240, anomalies=0"). If something failed or was skipped, say so
   plainly and first.
3. **Sequential, yourself, NO subagents/workflows** (Tamer's standing token constraint).
   Compute runs/tests/trainings MAY run in background; the reasoning work is done in the main
   loop.
4. **Own your errors loudly.** When you cause a failure (e.g. the 2026-07-06 co-scheduling OOM
   that killed 229/240 prototype units), diagnose it, state "this was my error, not a code bug",
   fix the process, and record the lesson in §5's gotchas ledger.
5. **Measure, don't assume.** Every planning constant here re-anchors on G1 measurements
   (min/training, sustained concurrency, queue waits) BEFORE the freeze. If a number is an
   estimate, label it and give the range.
6. **Zero-defect, fix-on-sight.** Any bug/inconsistency/stale fact noticed while doing something
   else gets fixed immediately (test-code and docs) or recorded explicitly — never silently
   passed. Keep configs/docs/paper consistent when one changes.
7. **Respect the hard gates.** The FREEZE is Tamer's act alone. Commits only on Tamer's go.
   Never touch hash-bound files post-freeze without a dated, approved amendment. Never train a
   confirmatory unit off the pinned pool. Never handle Tamer's UCL password.
8. **Report at gates, batch questions.** At each phase gate: what ran, the observed result,
   what's next, and ALL pending Tamer-decisions in one batch (he is token-constrained). Begin
   EVERY message with "Tamer".
9. **Keep the cursor current** (`memory/session-current-focus.md`): update the NOW block before
   ending substantive work so any session resumes seamlessly.
10. **Honesty over comfort.** If evidence says a Tamer preference is scientifically wrong (e.g.
    ">200k steps"), say so directly with the evidence, then offer the rigorous version of his
    intent (the B\*-gate pattern). Never sycophancy; never silent compliance.

## §12 THE EXECUTION LEDGER — state, branches, build specs (self-contained; do NOT re-derive)

### 12.1 State ledger (verified 2026-07-06/07; do NOT re-verify wholesale)
- ALL systems live-verified green: 2,004/2,004 tests exit-0 · sandbox 17-malicious-rejected /
  3-benign-accepted · inference 12 estimators (TOST both directions; Romano-Wolf [T,F,T];
  ES==CVaR live) · leakage 60-session purge both boundaries on the real univ5 (5,406×963) ·
  resume tamper-detection fail-loud · crash-rehearsal CERTIFIED (kill-tree→resume
  byte-identical) · verify-mirror OK (D:/llm_rp_archive_mirror) · SAC+TQC GREEN on CUDA ·
  freeze gate 20/20 @ `1c6b76b6` (frozen:false) · PDF 320KB/0-warn · citations 0/0 · ruff clean.
- **Prototype repeat COMPLETE 2026-07-06 23:17**: Pass-A stub, --gpu 3, alone → 240/240, exit 0,
  anomalies=0, all 6 arms matched=True, 15.1h. The machinery is certified at scale on real data.
  Directional only — NO number enters the dissertation. outputs/prototype_repeat stays
  UNCOMMITTED.
- **UNCOMMITTED (one commit on Tamer's go)**: tests/test_smoke_qwen.py (config-driven rewrite),
  scripts/analyze_campaign.py (`import sys` + utf-8 stdout fix), this plan doc, the ULTRAPLAN
  supersession banner, scripts/myriad/g0_probe.sh.
- **Myriad connection STAGED, blocked on Tamer's 3 steps**: ed25519 key at
  `~/.ssh/id_ed25519_myriad`; `~/.ssh/config` Host myriad/myriad13 with `User UCL_USERNAME_HERE`
  placeholder; g0_probe.sh ready; VPN confirmed OFF (port 22 times out). Tamer must: ① give his
  UCL username, ② connect the UCL VPN, ③ run the first-login key install:
  `type %USERPROFILE%\.ssh\id_ed25519_myriad.pub | ssh <user>@login12.myriad.rc.ucl.ac.uk
  "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600
  ~/.ssh/authorized_keys"`. Access-denied ⇒ account not provisioned yet — ask him to forward the
  acceptance email.
- Open Tamer items: allocation email details (G0) · Okhrati email/pivot sign-off · Qwen
  DashScope activation (or OpenRouter fallback) · API budget ack (Stage-1 $33–63 + lean $9–18).

### 12.2 Decisions ledger (Tamer-ratified 2026-07-06 — DO NOT REOPEN)
The BIG IF (§0) · two stages with the bank gate + Stage-1 no-forward-references independence ·
**99% assurance** (n₉₉ script-derived ~500–600; if G1-measured sustained <~10 GPUs, recommend
95/403) · k=3 Stage-1 default with the day-4 1-seed fallback · B\*-gate (200k stands unless the
Myriad ladder disagrees; σ_D/n₉₉ derivation unchanged by k=3 — one amendment sentence) · D1
{1,2,4,6,8} in Stage 1 · D5 on the LAPTOP from GO-day (pauses during heavy laptop jobs) · lean
Stage 2 = $9–18 (premium shelf $72–135 only on explicit purchase) · pools: Stage 1 pinned EF/V100,
fleet on L/A100 · §10 respect levers (OSF mandatory, corpus release, 30-min verifier, red-team
appendix, repro checklist, Okhrati section-feedback ~Aug 12–16, lay reader) · the §2 refusals.

### 12.3 BRANCH A — execute NOW (no GO needed; highest grade value first)

**A1. THE WORD SURGERY — the exact protocol (top priority; blocks on nothing).**
Current: CH1 2,453 · CH2 2,753 · theory 3,826 · CH4 3,697 · CH5 1,388 · CH6 1,273 · CH7 1,624 =
**17,014 vs ≤9,500** (hard 10k limit; core Methods+Results+Discussion ≥60%).
*Order of attack (biggest %-cut, lowest risk first):* CH5 → CH2 → CH1 → theory → CH4.
*Per-chapter procedure (repeat for each):*
  1. Read the chapter END-TO-END. Produce a CUT-PLAN list: every move tagged DELETE (redundant/
     padding), CONDENSE (2+ sentences → 1), MATHIFY (prose-math → display equation, which is
     word-FREE), or APPENDIX (move block + leave "see Appendix X" pointer). Estimate words freed
     per move; sum must reach the chapter target BEFORE editing.
  2. Apply the moves with Edit. NEVER cut: pre-registered result statements, limitations,
     honesty caveats, figure/table cross-references, or any % VERIFY-resolved citation's only
     usage (orphaning a cite key breaks check_citations).
  3. Run `python scripts/word_budget.py` (chapter + total), `python scripts/check_citations.py`,
     `python scripts/build_paper.py` (must stay 0-warnings). Fix anything before the next chapter.
*Targets:* CH5→~150 words in-body (1 paragraph: "a directional prototype de-risked the machinery;
details Appendix P") + full text → new appendix · CH2→~1,500 (kill per-paper summaries; group by
CLAIM with 1-line contrasts; the fence table absorbs neighbours) · CH1→~1,400 (cut the
pre-disclosed results repetition; one crown paragraph each for question/mechanism/contributions) ·
theory→~1,200 in-body (each result = 1 intuition paragraph + display-math statement; ALL proofs +
formal machinery → the math appendix) · CH4→~2,400 (procedural detail → runbook-style appendix;
keep design rationale + identification + the controls table) · leave CH6→~2,500 / CH7→~1,500
headroom for results. End state: body ≈ 9,150 pre-results → ≈ 9,450 with results filled.

**A2. 16-section compliance batch (exact edits):**
(i) Create the explicit **Data** section: promote the F3 EDA (kurtosis 15.25, co-crash 19.7%,
CVaR crossover, −5σ ×10,393 — the univ5 Split-C refreshed numbers; skew is POSITIVE +0.21) + the
panel/provenance description out of CH4 into its own numbered section between Literature Review
and Methodology. (ii) Split CH7 → "Discussion" and "Conclusions & Recommendations" as two
numbered sections (guidelines §13/§14). (iii) Insert the official Moodle cover page slot in
FRONT_MATTER (Tamer downloads the file). (iv) Abstract: self-contained, carries the headline
effect sizes + CIs once results land — never only objectives. (v) Acknowledgements: Dr Okhrati +
LSEG/Refinitiv data + the VERBATIM R9 Myriad sentence + AI-tools acknowledgment. (vi) Fill the
AI-assistance disclosure (UCL policy; describe Claude-assisted engineering/drafting + human
review) + the ethics/no-human-subjects/data-governance statement. (vii) A one-sentence
plain-language lead before every load-bearing result (second marker = any discipline).

**A3.** Commit the 12.1 pending set on Tamer's go (single commit; message in 12.1).
**A4.** Chase the open Tamer items in ONE batched ask per session (username/VPN/key · allocation
email · Okhrati · Qwen activation · API ack).

### 12.4 BRANCH B — on Tamer's **GO**: FULL BUILD SPECS (all micro-decisions PRE-MADE below)

**B-A1. `src/cluster/` — the scheduler adapter (new package, ~2–2.5d incl. tests).**
Files: `src/cluster/__init__.py`, `spec_io.py`, `jobscript.py`, `submit.py`, `poll.py`,
`ledger.py`, `run_one.py`; tests in `tests/test_cluster_*.py`.
- `spec_io.py`: `write_specs(specs: list[dict], batch_dir: Path) -> int` — one
  `task_<i>.json` per spec (schema = EXACTLY the existing worker-spec dicts train_candidate /
  the test worker consume: arm, kind, reward/source or winner payload, cid/run_id, seed, device
  left absent [cluster jobs are 1-GPU cuda], opts subset: budget, windows, panel path [the ACFS
  path], agent_cfg, thermal OFF on cluster). `read_spec(path) -> dict`.
- `jobscript.py`: `render(batch_name, n_tasks, pool: "EF"|"L", tc: int, hold_jid: str|None,
  venv_or_sif: str) -> str` — emits the §5 template VERBATIM with `#$ -t 1-{n}`, `-tc {tc}`,
  optional `#$ -hold_jid {jid}`, `-ac allow={pool}`, and the run line
  `python -m src.cluster.run_one --spec "$BATCH_DIR/task_${SGE_TASK_ID}.json"`.
- `submit.py` (AS BUILT 2026-07-06/07): `push_batch(batch_dir, remote_specs_root)` —
  **tar-over-ssh** (V9: the driver host has NO rsync — only scp/ssh; local `tar -cf -` | ssh |
  remote `tar -xf -`; a torn push is caught at the moment of use because `read_spec` fail-closes
  on a missing index / sha mismatch); `qsub(js_path, runner) -> job_id`; `submit_marker(name,
  after_job_id, root, runner)` (the 5-min `-l h_rt=0:5:0` hold anchor, printf-built);
  `prepare_remote(root, names, runner)` (pre-creates specs/ledger/outputs/logs so `-o` opens at
  job start and the first pull reads "0 completed"); `ssh_runner(host)` shlex-quotes every word
  (V10 — the remote shell re-splits; round-trip-tested). ALL ssh via the `myriad` Host alias
  (key auth); NEVER embed credentials.
- `poll.py` (AS BUILT): `pull_archive(remote_outputs_root, local_root)` — **EXACT-incremental
  tar-over-ssh**: one ssh `find`-by-record.json lists remote-COMPLETE run dirs (record.json is
  the atomic commit marker), the remote-vs-local dir DIFF is the transfer list (exact because
  records are immutable after commit), chunks stream through `tar` into `.pull_tmp` staging and
  move into the mirror ONLY once whole (record.json verified) — the mirror never holds a torn
  dir, stale staging is swept and never counts; every 600 s from the driver. `completed_run_ids
  (local_root) -> set[str]` reads record.json presence (the archive IS the queue; run_id
  idempotency + the hash-verified `_replay` semantics in parallel.py transfer UNCHANGED).
- `driver.py` (AS BUILT 2026-07-07 — the kernel the campaign scripts call): `submit_batch(flat_specs,
  name, ...)` = write compacted specs (+§15 pack chunking) + LF-pure jobscript INSIDE the batch dir
  (one push carries both) → `prepare_remote` → tar-push → qsub → job id; `run_batch(...)` = the full
  submit→poll→requeue loop under the design law THE ARCHIVE IS THE ONLY TRUTH (every cycle: pull →
  compacted diff; scheduler state only decides WHEN to act; qacct harvested as forensics, never
  truth; SGE's own h_rt IS the stall detector — a wedged task is killed, the array drains, the next
  cycle re-emits exactly the missing run_ids, bounded 2 retries → permanent ledger). Crash/restart-
  safe (re-running resumes from the diff; a still-queued job from a dead driver is ADOPTED via the
  `qstat -r` full-jobname guard — plain qstat truncates names — so no double submit); transient
  VPN/qsub blips tolerated bounded (12 consecutive → loud); stale owed-submissions re-filtered
  against the archive so completed run_ids are never re-trained; optional `max_wall_secs` guard.
  10 fake-cluster loop tests (tests/test_cluster_driver.py) cover resume-noop / happy / compacted
  requeue / exhaustion→ledger / adoption / pull+qsub blips / wall guard / stale re-filter / packs.
- `ledger.py`: `ingest_qacct(job_id) -> list[FailRow]` via `ssh myriad "qacct -j {job_id}"`
  parse (exit_status≠0 rows); `requeue(fails, max_retries=2)` re-emits specs into a retry batch;
  ≥3rd failure → permanent ledger row (JSON-lines, same shape as the existing failures.jsonl).
- `run_one.py` (AS BUILT — runs ON Myriad): LEG-aware routing — `leg=="test"` →
  `test_leg._test_seed_worker` (sealed-leg record); else the SEARCH `parallel.train_candidate`.
  Archival is leg-appropriate (search: `parallel._archive`; test: `write_run` under the winner's
  arm dir) and the laptop-authored prompt is threaded onto the search record (provenance parity,
  directive 6). Single + §15 pack paths both leg-aware. Exit 0 iff every spec ok.
- `campaign.py` (AS BUILT 2026-07-08 — THE generation-level composition, the piece that turns the
  batch driver into the campaign): `run_search_arm` mirrors `parallel._drive_llm_arm` step-for-step
  (author cpg candidates/gen → gen-BEST by val DSR → `schema.build_block` reflection) but batches
  each generation as ONE array (candidates in a gen are independent → batching == pool-training,
  "adaptive execution, invariant design"); reuses EVERY science primitive (build_prompt_set /
  LLMClient / extract_reward_source / _diversity_directive / _spec / schema) + the F5 failures
  ledger + search-replay resume → LAPTOP↔CLUSTER PARITY by construction. `run_test_leg` = the sealed
  leg as ONE `-tc`=pool array via `build_test_specs` (single-source schema; 93% of GPU-h at max
  concurrency). `run_arm_pipeline` = SEARCH→SELECT (`select_winner`)→FREEZE (`freeze_winner`)→TEST,
  so an arm's test array FLOODS the instant its search ends. `run_campaign_on_cluster` = all arms'
  pipelines CONCURRENT (thread per arm; a shared **authoring lock** keeps the API arm-serial while
  the training arrays interleave freely; per-arm crashes isolated). `build_cluster_run` wires the
  production `ClusterRun` over `driver.run_batch` with a **shared throttled puller** (no redundant
  ssh storms across arm threads) + the hard **`spend_guard`** authoring cap. Pool pinned per contrast
  (all confirmatory arms on `pool_confirmatory`=EF → device homogeneity within every analysis unit).
- Tests (AS BUILT): 22 cluster-adapter/submit/poll/ledger + 10 driver-loop + 11 campaign
  (fake-cluster + keyless STUB author: author/select/reflect, resume-replay, F5 ledger, one-array
  test leg, per-arm pipeline, concurrent-arms authoring-lock serialisation proof, spend cap, wiring)
  + 3 staged-gold + the real §15 pack integration.
**Acceptance: the keyless dry-run drives synthetic specs through author→render→(fake)submit→run_one
→poll→ledger with byte-identical records vs the local path — GREEN in-process; the ON-CLUSTER
acceptance (real ssh/SGE) is the G1 cert. ssh hang-guard: driver calls carry
`-o BatchMode=yes -o StrictHostKeyChecking=accept-new` (never wedge on a prompt; Tamer's
interactive login untouched). Env build: `scripts/myriad/build_env.sh` (module-purge → venv →
torch 2.6.0+cu124 → requirements.lock → `--smoke` GPU check via qrsh; Apptainer fallback on driver
mismatch).**

**B-A2. k=3 multi-seed search selection (~1–1.5d). DECIDED semantics — implement exactly:**
- Seeds per candidate: `{run_seed, run_seed+1, run_seed+2}` (campaign run_seed=0 → {0,1,2}).
- Records: one per (candidate, seed): run_id `f"{cid}-s{k}"` (mirrors the test-leg pattern);
  archive layout unchanged; resume hash-verifies EACH of the 3 (extend `_replay` key loop).
- Candidate fitness for SELECTION and for the LLM reflection: **IQM of the 3 per-seed
  val_fitness** (reuse `src/inference/bootstrap.iqm`); candidate VALID iff **all 3 seeds ok**,
  else the candidate is FAILED into the matched-budget ledger (accounting unchanged).
- Fed tail block: compute the 6 stats ONCE on the **concatenation of the 3 seeds' realized
  TRAIN-window returns** (more tail data → better EVT reliability; one clean number set to feed).
  **[CORRECTED 2026-07-08, Tamer-delegated decision — this line originally said "val", a drafting
  slip]:** the single-seed fed tail is fit on the TRAIN window (`ReturnDistribution().fit(train)`;
  the estimator's signature is literally `fit(train_realized_returns)`), and the ratified construct
  is **fed in-sample / scored out-of-sample** (the named selection-overfitting defense). Feeding
  VAL-derived tails would hand the author richer information about the SELECTION set and make the
  k=1/k=3 constructs inconsistent. AS BUILT: `src.search.multiseed.aggregate_k_seeds` concatenates
  `metrics.train_returns` (worker-emitted under the k>1 specs' `emit_train_returns` flag; archived
  additively); a k>1 record lacking train returns FAILS the candidate loud (no silent val fallback).
- PBO: per-candidate val-return vector = the per-period MEAN across the 3 seeds (same T length);
  DSR n_trials stays 30. Touch points: `src/llm/loop.py` (generation loop trains 3× per
  candidate via the pool, aggregates), `src/orchestration/parallel.py` `_drive_llm_arm` +
  `_drive_search_arm` (same), `analyze_campaign` PBO assembly, freeze mirrors (12.4-C).
- Tests: IQM-selection unit; all-3-required failure path; fed-block concatenation golden; per-seed
  byte-determinism preserved; resume replays 3/3.
**Fallback trigger (pre-written): if B-A2 is not merged+re-certified by GO+4d → Stage 1 launches
1-seed; k=3 → Stage 2 replicate study. The freeze date NEVER moves for it.**

**B-A3. Uniform-n₉₉ schema + tier ordering (~0.5d). ✅ AS BUILT 2026-07-08.** `config/campaign.yaml`
`seeds:` accepts `{mode: uniform, n}` / `{mode: tiered, tiers: [30, 340, 403, 568]}` / a bare list —
`src.utils.seeds.resolve_seeds`/`seed_tiers` is the ONE resolver the campaign, entry point, and
freeze mirror bind on (freeze.py resolves both files' schemas; hash unchanged on the current list).
The emission order is implemented as **`campaign.run_campaign_tiered` — the C-ladder executable**:
C0 canary (hard-gate: a canary failure aborts BEFORE any Opus spend) → C1–C3 all-arms
search→select→freeze concurrent under the §14.3 priority ladder (H2 arrays `-p 0`, remaining arms +
H1 baselines `-p -100`; SGE serves the value order natively) with the H2 core test as ONE
**pair-adjacent interleaved** array (taskfile alternates dist-s_k, scalar-s_k — the Lv-1 CRN-pair
banking quantum) and non-H2 tests flooding per-arm at zero barrier → **the effect-blind REVIEW GATE**
(Tamer 2026-07-08: "go to tier 0 first, review everything very carefully, then proceed" —
`src.cluster.integrity.write_integrity_report` emits counts/censuses ONLY [completeness vs budget,
F5 ledgers, device/env-fp homogeneity, popart/safe-default presence]; NO performance statistic is
read, preserving the single-look discipline; approval = the `TIER1_APPROVED` file, then `--resume`
skips through the archive into C4) → C4 the uniform-n ROUND-ROBIN sweep (all 7 arms + H1 baselines,
seed-major interleave) in the assurance blocks the schema declares (30→340 @90% → 403 @95% → 568
@99% — each block boundary a complete design at that assurance). C5 H3 + C6 D1 = separate entry
invocations at `-p -100`/`-200`. Entry flags: `--tiered --canary … --approve-tier1 --no-review-gate`.
n₉₉ derivation: `python scripts/power_analysis.py --assurance` **(BUILT — reproduces 279/340/403 and
extends 99%→568; note the seed-decision doc mislabels the 90% σ_up as 0.449 — that is the 80% bound,
the 90% value is 0.495; n=340 itself is correct)**.

**B-A4. D1 levels (~0.5d).** Generalize the H3 harness: `run_campaign.py run_h3_singleshot`
already takes generations — expose `--generations {2,4,8} --out outputs/campaign/d1_g{N}`;
candidates_per_gen derived as 30//gens (30,15,7+8,4-ish → use existing derivation); winners
tested n=100 via the same cluster test path into `outputs/campaign/d1_g{N}/test`.

**B-B. PHASE-B MYRIAD RUNSHEET (execute top to bottom; each line = observed-output gate):**
1. `sed -i "s/UCL_USERNAME_HERE/<username>/" ~/.ssh/config` → `ssh myriad hostname` (key-only).
2. `ssh myriad 'bash -s' < scripts/myriad/g0_probe.sh | tee outputs/logs/g0_probe.txt` → record:
   outbound(login/compute), driver versions, gquota, apptainer, ACFS, queue snapshot.
3. Stage inputs: `scp data/gold/returns_panel_univ5.parquet data/manifest/*
   myriad:/acfs/users/<u>/llmrp-inputs/` (scp IS on the driver host; fallback `~/inputs/` if no
   ACFS) → `ssh myriad "cd ... && sha256sum returns_panel_univ5.parquet"` == local hash.
4. Env: push the repo via `git archive HEAD | ssh myriad "mkdir -p ~/llmrp && tar -x -C ~/llmrp"`
   (tracked files only — outputs/.venv/data excluded by construction; no rsync on the driver) →
   `ssh myriad "python3 -m venv
   ~/venvs/llmrp && ~/venvs/llmrp/bin/pip install -r requirements.lock torch==2.6.0 --index-url
   <cu-wheel index matching the G0 driver>"`. Import smoke via a 10-min qrsh on EACH pool.
   If driver too old for any cu-build → `apptainer build llmrp.sif docker://...` from the Plan-B
   recipe; rerun smokes with `apptainer exec`.
5. **G1 CERT (all must pass; tee logs):** keyless dry-run through the cluster adapter (B-A1
   acceptance) · `crash_rehearsal.py --work-root ~/Scratch/rehearsal` ON Myriad · same-spec-twice
   determinism on EF AND L (canonical-compare) · fps bench: 3×200k on EF + 3 on L → **write the
   measured min/training into §3's PRECISION NOTE and re-anchor every table** · 30-way array
   scale test · B\* ladder micro-pilot (15 jobs; apply the pre-committed rule) · probe arrays
   (50×30-min sleep+gpu jobs per pool) → compute achieved C + median wait from qacct → **write
   measured C into §7** · every §6 rehearsal row (VPN-kill/driver-kill/inject-fail/
   delete-restore/corrupt-byte/key-pause/evacuation-dry-run) · mirror-back: the driver's
   tar-over-ssh exact-incremental pull every
   600 s + nightly `archive_integrity verify-mirror` on laptop + D: + Mac.
6. Optional ARR email to rc-support (CC Okhrati): ~4,600 GPU-h, ≤3h 1-GPU jobs, 6 weeks, EF+L,
   priority-window ask.

**B-C. PHASE-C PRE-FREEZE EDITS — verbatim texts to paste:**
- PREREGISTRATION §6 (seeds): *"Amendment (2026-07-XX, pre-freeze): winner evaluation uses a
  UNIFORM per-arm seed count n=⟨n₉₉⟩ across all seven arms, the four H1 baselines, and H3,
  sized by `power_analysis.py` for 90% TOST power at the SESOI evaluated at the 99% χ²
  upper confidence bound of the pilot σ_D (n=15). The pilot σ_D estimate is unaffected by the
  k=3 selection change: test-leg seed variance is a property of the trained policies, not of the
  selection procedure."*
- §6 (search): *"Each search candidate is trained at k=3 seeds; selection and reflection use the
  interquartile mean of the per-seed validation fitness, and the fed tail statistics are computed
  on the pooled realized validation returns of the three seeds. Fallback (pre-declared): if the
  k=3 implementation is not certified by ⟨GO+4d⟩, the search executes at k=1 exactly as
  previously specified, and k=3 runs post-hoc as a report-only replicate."*
- §6 (budget): *"B\* remains 200,000. A pre-committed revalidation ladder on the campaign
  platform (3 seeds × 5 budgets) may raise B\* only if evaluation performance still improves at
  350k beyond the pilot noise band; outcome: ⟨fill from G1⟩."*
- New §2a(h): *"Designer sensitivity probe (exploratory, report-only, post-campaign):
  counterfactual re-authoring of archived reflection states under pre-specified feedback
  perturbations/enrichments — (i) per-statistic scaling ×2 and sign-flip, (ii) single-statistic
  ablation, (iii) full quantile-sketch enrichment, (iv) CI-annotated statistics, (v)
  training-curve telemetry enrichment, (vi) environment-source context enrichment — measuring
  authored-code sensitivity via AST features and coefficient deltas."*
- Platform/dual-track: *"Execution platform: UCL Myriad, all confirmatory units on a single GPU
  model (⟨EF/V100 or L, per G1⟩); report-only analyses may use a second pool, never mixed within
  a contrast. Dual-track fallback: if cluster certification fails by 2026-07-20, the identical
  design executes on the pre-specified laptop platform (Design-L) without further amendment. The
  D1 generation levels {2,4,8} and the exploratory instruments run as registered report-only."*
- FRONT_MATTER Acknowledgements: the verbatim R9 sentence + Okhrati + LSEG/Refinitiv + AI tools.
- freeze.py: seeds-mirror accepts the uniform schema; add k_seeds mirror; re-run `--check` → all
  green → regen power doc + `make_prereg_bundle.py` → OSF upload → **TAMER FREEZES**.

**B-D. STAGE-1 LAUNCH + DAILY OPS.** Driver: `scripts/myriad/driver.py` (new, thin): loads the
frozen config → emits spec batches per 12.4-B-A3 order → submit/hold/poll loop → LLM authoring
between generations (local .env keys) → streams the failure ledger. Daily checklist (5 min):
sentinel on the synced mirror exit-0 · qstat panel (achieved C vs plan) · gquota · mirror-verify
green ×3 sites · anomaly taxonomy empty. NEVER run heavy laptop jobs while the battery/gate runs
(D5 pauses).

**B-D′. BANK-GATE RITUAL (exact):** final `pull_archive` → `archive_integrity verify` +
`verify-mirror` on laptop/D:/Mac (all exit 0) → `python scripts/analyze_campaign.py --root
outputs/campaign --single-shot-root outputs/campaign/h3 | tee` → NEW scripts (written in Phase A,
~1d total): `scripts/variance_decomposition.py` (statsmodels MixedLM: val_fitness ~ arm +
(1|candidate) + residual-seed; + case bootstrap; one table+stacked-bar), `scripts/
shrinkage_winners.py` (empirical-Bayes: winner effect shrunk by k=3 within-candidate variance),
`scripts/spec_curve.py` (grid: {IQM,mean,median}×{empirical,EVT CVaR}×{per-seed,pooled} +
arm-label permutation p) → zip the results bundle + snapshot commit (Tamer's go) → fill the
Results numbers into CH6 → THE DISSERTATION IS COMPLETE.

**B-E. STAGE-2 LEAN SPECS.** U3: activate DashScope (or OpenRouter) → `smoke_qwen` exit 0 →
rerun the 5 LLM arms' search with `llm.provider=dashscope model=qwen3-coder-480b-a35b-instruct`
into `outputs/campaign_qwen/` (same cluster path) → winners n=100 on L → one appendix table.
D2+: `scripts/designer_probe.py` (new ~1–1.5d): sample ≤100 archived reflection states →
apply perturbations (i)–(vi) → transport call → AST-feature + coefficient deltas via the
existing taxonomy tooling → jsonl + one heat-strip figure. D6: TQC trainer factory (Phase-0
path) on frozen winners of {dist, scalar, placebo} × n=100 on L. U5: PPO/TD3 sb3 factories,
same 3 arms × 40. U4b: REQUIRES the FTSE panel (data build ~1–2d via PowerShell/.venv-lseg —
schedule only if Tamer waves it on). D8: `scripts/replicate_figures.py` (archive→every figure)
+ `scripts/verify30.py` (re-derives the H2 IQMs + one CI in <30 min). D5 (laptop, from GO-day):
`scripts/run_calibration.py` loops 40× keyless dry-run-style replicates at 50k on synthetic
panels (null + injected) → empirical α/power table.

### 12.5 Gotchas ledger (hard-won; violating any = real damage)
Login nodes kill >1 CPU-h processes (driver on the laptop) · arrays only, never qsub loops
(~100/1000 cap, ~10/s) · `-l mem=` is PER-CORE · `#!/bin/bash -l` mandatory · ACFS read-only on
compute (inputs there, outputs on Scratch) · home==Scratch UNBACKED → nightly mirror-back or lose
it · **never co-schedule heavy laptop jobs** (2026-07-06 OOM: battery+prototype together killed
229/240 units; monitoring caught it) · API keys only in the laptop .env, never on shared FS ·
VPN drops normal → everything idempotent · fair-share decays → front-load Stage 1 · one GPU
model per contrast · Qwen smoke exits 3 at the paywall until activated · sentinel/monitor/journal
run read-only on ANY archive root — point at the synced mirror.

### 12.6 Success criteria
Every gate green in order · no confirmatory unit off the pinned pool · bank-gate artifacts in all
four archive sites · Tamer never surprised (gate reports; batched questions) · body ≤9,500 words,
core ≥60% · the five §10 respect artifacts shipped · submit ≤ Sep 1 with ≥3-day buffer.

## §13 THE CASCADE ARCHITECTURE — five interlocking cascades, one self-regulating system

**The governing principle (state it in the paper's methods too): ADAPTIVE EXECUTION, INVARIANT
DESIGN.** Every adaptive mechanism below consumes ONLY operational signals (counts, rates,
durations, exit codes) and can reorder or re-route WHEN units run — never WHAT units exist, HOW
they are analyzed, or WHICH results are looked at. The design/analysis layer is frozen; the
execution layer is a feedback controller. Adaptivity therefore cannot contaminate inference —
the boundary itself is pre-registered (the dual-track + tier text in B-C).

### 13.1 The VALUE CASCADE (what runs next — greedy on grade-risk retired per GPU-hour)
Nested banking levels, each with an invariant, a banking criterion, and a degradation target:
| Lv | Unit | Banked when | Degrades to |
|---|---|---|---|
| 0 | one training | atomic record.json committed (fsync+rename) | resubmit (idempotent) |
| 1 | CRN pair | both seeds' records present (pair-adjacent scheduling makes pairs the quantum; ≤C unpaired at any instant) | the other seed requeued |
| 2 | seed-block | block complete + mirror-pulled | analysis on the intersection (verified live: `set(sa)&set(sb)`) |
| 3 | contrast | both arms' legs at current n | last complete block |
| 4 | checkpoint | C-ladder level done + verified (see below) | previous checkpoint |
| 5 | stage | STAGE-1 BANK GATE ritual (B-D′) all-sites-verified | the checkpoint ladder |
| 6 | program | Stage 2 lean done | any prefix — every item is add-on by §12.2 |
**The C-ladder (checkpoint order inside Stage 1)** = the value-per-hour greedy order: C0 canary
(3 H1 units, proves the path) → C1 H2 search (the irreplaceable core) → C2 H2 pair-tests at n=30
(minimal complete headline) → C3 all-arms search + tests n=30 (the full design floor) → C4
uniform-n completion sweep (n=30→n₉₉, pair-adjacent, all arms round-robin) → C5 H1/H3 completion
→ C6 D1 curve levels. Greedy is optimal here by the classic exchange argument: units are
independent, values additive, one resource pool — so at ANY interruption the archive holds the
maximum-value prefix money could have bought in the time spent. **That is the cascade property.**

### 13.2 The DECISION CASCADE (every branch pre-decided: trigger → owner → default)
G0 details(Tamer)→ G1 cert(me; default=laptop Design-L on failure) → 95/99(Tamer at freeze;
priced by MEASURED C; default 95 if C<10) → k=3(day-4 trigger; default 1-seed fallback) →
B\*-gate(pre-committed rule; default 200k) → FREEZE(Tamer only) → bank gate(objective ritual) →
Stage-2 prune ladder(reverse value order; default = stop, never improvise) → premium shelf
(Tamer purchase only; default future-work). No branch exists without a trigger+owner+default.

### 13.3 The CONTROL CASCADE (the feedback controller in the driver — effect-blind by construction)
- **Throughput loop**: every poll cycle compute achieved C(t) (rolling 6h) and measured
  min/training → rolling ETA per C-ladder level → if ETA(bank gate) > (Aug 15 backstop − 5d),
  fire pre-declared responses IN ORDER: (1) shift any non-confirmatory load off the EF pool;
  (2) raise `-tc` to the full pool if throttled; (3) send/escalate the ARR; (4) prune ladder on
  Stage-2 pre-work; (5) the laptop-absorb rule at a pre-declared seed boundary (Design-L
  semantics). Each response logged; none touches design.
- **Submission loop (token bucket)**: keep the queue primed at ≤ caps (R3): one array per batch,
  `-tc`=pool size, next batch submitted when running+pending < 1.5× pool — burst-harvesting by
  construction (specs are ALL pre-materialized at stage start, so a suddenly idle cluster is
  immediately consumable).
- **Failure loop**: ledger rates vs sentinel thresholds → auto-requeue(≤2) → node-type
  quarantine on clustered CUDA errors (drop `-ac` host group, re-pin) → CRIT = pause submissions
  + deadman alert. Straggler rule: requeue WITHIN the pinned pool only (homogeneity beats speed).
- **Blindness audit**: the controller's inputs are enumerable — {counts, timestamps, exit codes,
  qstat, quotas}. Effect estimates are computed EXACTLY ONCE, at the bank gate. Any tooling that
  would surface an interim effect number is forbidden by §11.7.

### 13.4 The INFORMATION CASCADE (signal → action, severity-laddered)
journal events → sentinel (17 checks, thresholds already live-verified) → driver auto-responses
(13.3) → deadman heartbeat → Tamer alert. Ownership: INFO=logged · WARN=me, same session ·
CRIT=submissions paused + Tamer pinged. Dashboards (monitor/sentinel/qstat panel/Open OnDemand)
show progress + health ONLY — counts and rungs, never effects (treatment-blind ops, verified
pattern from the runbook §5b).

### 13.5 The REDUNDANCY CASCADE (data can only die four times)
ACFS(inputs, RO, backed) → Scratch(live outputs) → laptop(pull every 600s) → D: mirror(nightly,
verified) → Mac(nightly, verified). "BANKED" at any level of 13.1 means VERIFIED AT ALL SITES
(archive_integrity exit 0 ×3 + ACFS hash match). The evacuation checklist (R7) is this cascade's
terminal drill — rehearsed in G1 before a single confirmatory unit runs.

**One-line summary of the whole architecture:** a greedy value-ordered banking ladder, executed
by an effect-blind feedback controller, guarded by a pre-decided branch tree, observed through a
severity-laddered signal chain, and persisted through a four-site verified redundancy chain —
adaptive everywhere it is safe, frozen everywhere it matters.

## §14 MYRIAD-NATIVE MAXIMIZATION — every system pushed to its ceiling USING the cluster's own primitives

The adapter (B-A1) implements ALL of the following; each line names the native primitive it
exploits. These are Phase-A engineering scope; none changes the science.

### 14.1 Resume — three native layers beneath our own
- **`#$ -r y` on every training array**: SGE itself re-runs tasks killed by NODE failure — a
  free resume layer under our run_id idempotency (our atomic records make re-runs harmless).
- **Compacted-array resume**: on any relaunch the spec emitter diffs `completed_ids()` against
  the task list and emits an array containing ONLY missing tasks (task→spec mapping file) — no
  wasted queue slots, no wasted fair-share on already-banked work.
- **`qacct` post-mortem per task**: exit_status/failed/maxvmem/wallclock harvested for every
  finished task id into the ledger — forensic resume decisions from accounting truth, not guesses.

### 14.2 Cache & I/O — Lustre-smart by construction
- **Content-addressed specs**: task files named by the sha256 of their payload → resubmitting
  identical work is a filesystem no-op; the draw→hash→replay guarantee gets a second,
  storage-level enforcement.
- **`$TMPDIR` gold staging (BUILT + LOAD-BEARING, V7 closed 2026-07-07)**: each job copies the
  gold artifacts (~45 MB) ACFS→node-local tmpfs at start (`-l tmpfs=15G` already requested) and
  exports `LLM_RP_GOLD_STAGED_DIR`, which `src/data/loaders.py::_resolve_gold_path` honours
  per file — 16k jobs generate ZERO repeated Lustre read pressure and no metadata storms; torch
  caches also pinned to `$TMPDIR`. Three safety properties BY CONSTRUCTION (hermetic tests in
  tests/test_loaders_staged.py): the suffix lives IN the staged filename (wrong-panel staging =
  filename miss → canonical fallback, never a silent masquerade); staged bytes are verified
  against the SAME frozen manifest SHA-256 (basename matching); a failed tmpfs copy falls back
  to exporting the ACFS dir itself — which ALSO closes the on-node gold-path question (a node
  has no repo `data/gold/`; the staged-dir hook is how node jobs find gold at all).
- **Directory sharding sanity**: per-arm result dirs hold ≤ ~600 run-dirs each (n₉₉ scale) —
  within Lustre's comfortable dentry range; verified at G1's 30-way scale test.

### 14.3 Scheduling — the value cascade enforced BY the scheduler itself
- **Intra-user priority ladder via `-p`** (users may self-deprioritize): canary + H2 arrays at
  `-p 0`, remaining Stage-1 at `-p -100`, D1 levels at `-p -200`, Stage-2 fleet at `-p -500` →
  even when everything is queued at once, GRID ENGINE executes our §13.1 value order natively —
  the cascade no longer depends on submission timing at all.
- **Whole-array dependencies** via marker jobs + `-hold_jid` (test arrays pre-submitted, released
  the second an arm's search marker completes); `-hold_jid_ad` (per-TASK array chaining) reserved
  for pair-adjacent block chaining if G1 shows it schedules better.
- **Token-bucket submitter** keeps running+pending < 1.5× pool under the R3 caps; `-now n`
  batch semantics everywhere; `-tc` = full pool size, never lower.

### 14.4 Monitoring — a native telemetry spine UNDER our sentinel
- **Per-task epilogue line**: the jobscript appends one JSON line (task id, host, GPU model from
  nvidia-smi, exit code, runtime) to a per-array Lustre ledger — a scheduler-independent journal
  that exists even if our record write failed; the laptop sentinel ingests it on every pull.
- **`qstat -j` pending-reason parsing**: the throughput controller distinguishes "cluster busy"
  from "we are fair-share-throttled" from "resource unschedulable" — three different §13.3
  responses, now correctly targeted.
- **Daily `qacct` harvest** → per-task wall/cpu/maxvmem distributions → feeds the paper's
  compute-reporting line EXACTLY (measured GPU-h, not estimates) and natively detects memory
  creep across the fleet.
- **Organized native logs**: `#$ -o/-e` to `Scratch/logs/<array>/$TASK_ID.{o,e}` with `-j y` —
  every task's stdout findable in one hop.
- **The determinism heartbeat (continuous, not just G1)**: an automatic DAILY pair of identical
  50k synthetic jobs on the pinned pool, canonically compared on pull; any drift = CRIT alert.
  Cost ~0.6 GPU-h/day for a campaign-long guarantee no one in the field runs.
- **Driver lease + native deadman**: the driver touches `Scratch/.driver_lease` each cycle; a
  1-core, 72h chained watchdog job (`-l h_rt=72:0:0`) alerts if the lease goes stale — an
  in-cluster deadman complementing the healthchecks one.
- **Open OnDemand** = Tamer's zero-setup browser view; `-m a -M` mail-on-abort ONLY on marker/
  watchdog jobs (never on 16k-task arrays).

### 14.5 Provenance & security — tightened natively
- `run_one` extends the env fingerprint with hostname + GPU model + driver version per record
  (sealed-leg homogeneity becomes auditable per unit, natively).
- `umask 077` in the template; `chmod 700 ~/Scratch/llmrp`; inputs on read-only-to-jobs ACFS;
  NO secret ever in a jobscript or on shared FS (keys remain laptop-only; authoring is
  driver-side by architecture).

### 14.6 The upgraded jobscript template (supersedes §5's; the adapter renders THIS)
```bash
#!/bin/bash -l
#$ -l gpu=1
#$ -pe smp 4
#$ -l mem=8G
#$ -l tmpfs=15G
#$ -l h_rt=3:0:0
#$ -ac allow=EF
#$ -r y
#$ -p {PRIORITY}
#$ -t 1-{N} -tc {POOL}
{HOLD: #$ -hold_jid {MARKER}}
#$ -wd {REMOTE_ROOT}
#$ -o {REMOTE_ROOT}/logs/{ARRAY}/$TASK_ID.o -j y
umask 077
mkdir -p "$TMPDIR/gold"                                    # node-local gold (V7 closed: the
if cp {ACFS_INPUTS}/*.parquet "$TMPDIR/gold/"; then        # loaders honour the staged dir
  export LLM_RP_GOLD_STAGED_DIR="$TMPDIR/gold"             # per file, checksum-verified)
else
  export LLM_RP_GOLD_STAGED_DIR={ACFS_INPUTS}              # copy failed -> read ACFS direct
fi
export TORCH_HOME="$TMPDIR/torch"
source ~/venvs/llmrp/bin/activate   # or: apptainer exec ~/llmrp.sif …
python -m src.cluster.run_one --spec "{REMOTE_ROOT}/specs/{ARRAY}/task_${{SGE_TASK_ID}}.json"
RC=$?
echo "{{\"task\":$SGE_TASK_ID,\"host\":\"$(hostname)\",\"gpu\":\"$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader)\",\"rc\":$RC,\"secs\":$SECONDS}}" >> {REMOTE_ROOT}/ledger/{ARRAY}.epilogue.jsonl
exit $RC
```

### 14.7 What this buys, honestly (see §15 for the multiplicative lever on top)
Zero wasted fair-share (compacted resume + content-addressed specs) · the value cascade enforced
by the scheduler itself (`-p` ladder) · I/O that cannot storm Lustre at 16k-job scale ($TMPDIR
staging) · telemetry that survives any single failure (epilogue ledger + qacct truth) · a
campaign-long continuous determinism guarantee (the daily heartbeat pair) · per-record
device-homogeneity auditability · and a measured, not estimated, compute line for the paper.
Every mechanism is a native SGE/Lustre/ACFS primitive — nothing exotic, nothing fragile, all
rehearsed in G1 before a confirmatory unit runs.

## §15 GPU-PACKING — the multiplicative parallelism lever (deep-research finding, 2026-07-07)

**The researched facts:** Myriad GPU nodes run **device cgroups (since 2022-08-10): a
`-l gpu=1` job holds EXCLUSIVE access to exactly its GPU** (jobs share nodes; nobody shares your
card). `CUDA_VISIBLE_DEVICES` is settable within a job. No MIG slicing is documented on the
A100 nodes (verify `nvidia-smi -L` at G0). ⇒ **Inside our job the GPU is entirely ours — so one
job may run N CONCURRENT trainings on its one GPU.** That is EXACTLY what the certified laptop
DevicePool already does (3 trainings on one 6 GB RTX 4050), and our byte-compare already PROVED
3-way-concurrent == serial BIT-IDENTICAL — packing is numerics-safe by our own prior evidence
(contention affects timing only; per-seed determinism is independent of co-tenants).

**The mechanism (reuses certified code):** `run_one --pack N` — the spec file carries N specs;
run_one instantiates the EXISTING DevicePool(n_gpu=N on one card, device tokens all "cuda") and
runs one wave; each training writes its own atomic record as always. Our footprint is ~2–3 GiB;
a V100-16G takes pack=3 with headroom (~9 GiB + contexts); A100-40G takes pack=4–6.

**Job shape per pack (bench-tuned at G1):** pack=3 → `-pe smp 8..12 -l mem=4G -l h_rt=1:30:0`
(one wave of 3 finishes together in ~49 min at the laptop-observed 1.39× per-training slowdown;
SHORTER jobs than pack=1 → even more backfill-friendly). Aggregate throughput per granted GPU ≈
×2.0–2.5 (laptop evidence: ×2.15; Linux V100 with 4.7× the memory bandwidth and no WDDM should
do ≥ that). **Optional MPS variant**: since the card is cgroup-exclusive, a user-space
`nvidia-cuda-mps-control` daemon inside the job is permissible — benched as a G1 variant.

**The G1 pack bench (decides everything, ~25 GPU-h):** pack ∈ {1,2,3,4} × MPS {off,on} × pools
{EF,L} → pick max aggregate trainings/hour per pool; then same-spec-twice determinism RE-CERT
under the chosen pack (expected pass — prior proof — but verified anyway); OOM guard: pack
chosen with ≥30% VRAM headroom.

**Revised Stage-1 wall-clock (7,905 trainings; granted C × pack-2.2 effective):**
| Granted GPUs | pack=1 (old) | **pack=3 @×2.2 (new)** |
|---|---|---|
| 6 | 32.0 d | **14.5 d** |
| 12 | 16.0 d | **7.3 d** — banked ~Jul 22 |
| 24 | 8.0 d | **3.6 d** |
Fair-share note: packed jobs consume more core-share per GPU-hour, but GPUs are the scarce axis —
net win. All §13/§14 machinery (arrays, -p ladder, epilogue, heartbeat) applies unchanged; the
determinism heartbeat runs UNDER the chosen pack.

## §16 THE ALL-SYSTEMS MAXIMIZATION MATRIX (completeness check — every system, its maximal form, where specified)
| System | Maximal form | Where |
|---|---|---|
| Sandbox/security | allowlist AST gate (17 attack classes live-verified) + per-job umask/cgroup isolation + keys laptop-only | verified 07-06; §14.5 |
| Feedback/measurement | 6-scalar EVT tail vector on k=3 POOLED returns (more tail data → better reliability) | §12.4 B-A2 |
| Search/LLM loop | k=3 IQM selection (exceeds Eureka) + arm-concurrent chains + D1 dose-response + D2+ interventional grid | §3, §3b |
| Inference | uniform n₉₉(99%) + IUT/TOST/Romano-Wolf/DSR/PBO + D3 variance decomposition + D4 shrinkage + D9 spec-curve/permutation + D5 whole-pipeline calibration | §3, B-D′ |
| Data/leakage | 60-session purge (live-verified) + ACFS-immutable inputs + $TMPDIR staging + SHA manifests at every hop | §14.2, §5 |
| Resume | 4 layers: SGE `-r y` → compacted arrays → run_id idempotency → hash-verified replay; crash-rehearsal certified | §14.1 |
| Cache/archival | content-addressed specs + atomic fsync-rename records + 5-site verified redundancy cascade | §14.2, §13.5 |
| Scheduling/parallelism | arrays at pool width + hold_jid pipelines + `-p` value-cascade-in-scheduler + token-bucket burst harvesting + **GPU packing ×2–2.5** + laptop D5 track | §13.3, §14.3, §15 |
| Monitoring | 17-check sentinel + journal cadence/MAD + per-task epilogue ledger + qacct harvest + qstat pending-reasons + DAILY determinism heartbeat + dual deadmen (lease job + healthchecks) + Open OnDemand + effect-blind dashboards | §13.4, §14.4 |
| Provenance/determinism | per-record host/GPU/driver fingerprints + same-spec-twice certs + continuous heartbeat + frozen-hash chain | §14.4–14.5 |
| Driver/orchestration | effect-blind feedback controller (throughput/submission/failure loops) + pre-decided branch tree | §13.2–13.3 |
| Write-up tooling | word_budget/check_citations/build_paper gates + the A1 surgery protocol + lay-reader pass + compliance batch | §12.3 |
| Respect artifacts | OSF mandatory + open reward corpus + 30-min verifier + red-team appendix + repro checklist | §10 |
| Fallbacks | dual-track laptop auto-execution + Plan-B Mac + prune ladder + evacuation drill | §0, §13.2, R7 |
NOTHING in the program lacks a maximized, Myriad-native, rehearsed form. This is the ceiling.

---
*Part I written 2026-07-06 (every Myriad fact from rc.ucl.ac.uk, fetched that day; every number
from measured anchors: 61 min/training laptop, σ_seed=0.244, σ_D=0.369, 2,004/2,004 tests, gate
20/20 @ 1c6b76b6). Part II added 2026-07-07 — the execution protocol + ledger for the model that
runs this plan.*
