# UCL RESEARCH-COMPUTING ULTRAPLAN (conditional; 2026-07-06)

> **⚠ SUPERSEDED-AS-OPERATIONAL (2026-07-06, same day):** the executable master plan is now
> **`docs/PLAN_IF_WE_USE_UCL_MYRIAD.md`** (the single-IF, two-stage, zero-problem plan — Tamer's
> security doctrine + the researched Myriad rules/throughput model + exact costs/timings). This
> document remains the DESIGN-RATIONALE record for the U/D-series items it introduced.

**Status:** UCL research-computing request ACCEPTED; **licence for the LSEG/Refinitiv gold panel on
UCL systems CONFIRMED YES (Tamer, 2026-07-06)**. Allocation details (system, GPU model/count,
walltime, storage) not yet known → this plan is GATED, with the laptop path as the guaranteed floor.

---

## 0. The frame — what compute changes, and what it must never change

More compute serves the ★ PRIORITIES in exactly three ways:
1. **Precision** — more seeds on the SAME pre-registered contrasts (tighter CIs, full-strength
   equivalence, symmetric arms).
2. **Robustness** — the report-only hardening the corpus says reviewers attack (cross-model,
   cross-market, cross-algorithm, search-variance identification) at full strength instead of lite.
3. **Time** — the campaign compresses from ~24 laptop-days to days, handing ALL of August to the
   write-up — which the grade audit shows is where 95% is actually won or lost.

**Invariants (compute may NOT touch these — the discipline section):**
- The identification principle: only the feedback block varies across arms. No new state/reward
  inputs, no new arms, no new hypotheses.
- B\* = 200,000 — set by the convergence pilot (≥2× the critic knee, below the measured overfit
  onset). A faster machine does not move the knee. **Longer training is a science error, not an
  upgrade.**
- K = 30 candidates/arm — the pre-registered matched budget; widening it re-opens multiplicity
  (rejected-extensions register). The DSR deflation is calibrated to 30.
- SESOI = 0.05 DSR; the m = 6 family; the 7 arms; Split C; the mechanism headline; the
  bounded-effect/equivalence dual-branch null strategy. All unchanged.
- The 10,000-word limit and Okhrati's depth-over-breadth: every upgrade below lands in the SAME
  four-deep-analyses body; extra strength goes to appendices (word-excluded), never to new body
  sections.

---

## 1. Gates (nothing moves until its gate opens)

| Gate | Opens when | Output |
|---|---|---|
| **G0 — details** | Tamer forwards the allocation specifics | GPU model+count, scheduler, walltime cap, scratch quota, login-node outbound HTTPS (API calls), account/queue names |
| **G1 — certification** | The cluster port passes the full cert suite (§4) | "certified-on-cluster" verdict; the dual-track trigger becomes decidable |
| **G2 — freeze** | Tamer freezes with the dual-track section included | The campaign launches on whichever track G1 selected |

**Dual-track pre-registration (the clean way to be conditional).** The freeze includes BOTH designs
with an objective, effect-blind trigger — no forking paths, no post-hoc migration:

> *Design-C (cluster) executes iff the cluster certification suite (§4) passes by **2026-07-20**;
> otherwise Design-L (laptop, the ratified 403 arm-adaptive plan) executes. The trigger is a
> pre-declared engineering fact, independent of any outcome data. No unit runs on both platforms;
> the executing platform is recorded per record (`metrics.device` + env fingerprint).*

**One-platform rule.** CUDA numerics differ across platforms and GPU models. The ENTIRE
confirmatory campaign (search + test + H1 + H3) runs on ONE platform and ONE GPU model
(pinned via the queue resource request). No laptop/cluster mixing inside the design. The laptop
becomes Plan B (it inherits the seed-boundary migration rule); the Mac stays archive + deadman.

---

## 2. The upgrade ladder (each rung: what / why / cost / decision)

Costs assume ~0.5–0.75 h per 200k-step training on a modern data-centre GPU under Linux (no WDDM
overhead; the laptop's measured bottleneck was loop+driver latency, not FLOPs) — re-measure at G1.

### U0 — Same design, one platform, fast (ALWAYS, if G1 passes)
Run the ratified Design-L unchanged on the cluster. Search (210) + arm-adaptive test (2×403 +
5×30) + H1 (120) + H3 (60) ≈ **1,340 trainings ≈ 700–1,000 GPU-h** → 20 concurrent GPUs ≈ 2–3
days wall. Value: the entire risk window (hardware failure, thermal, 24/7 babysitting) collapses;
August is fully freed for the document. **This rung alone justifies the cluster.**

### U1 — Uniform n=403 on ALL arms + H1 (RECOMMENDED)
The arm-adaptive 403/30 split was a **laptop-compute compromise**, not a scientific preference.
Uniform n=403 across all 7 arms + the 4 H1 baselines + H3:
- every secondary contrast in the m=6 family gets full precision (dist–placebo, dist–cvar5, …);
- H4 (LLM vs random/bayes) and H1 (LLM vs human) reach the same evidential strength as H2;
- the "asymmetric-leg conservatism" disclosure disappears entirely;
- zero forking-paths risk — same tests, more data, decided PRE-freeze.
Cost: test 7×403 = 2,821 + H1 4×403 = 1,612 + H3 433 ≈ **+3,500 trainings ≈ +2,000–2,600 GPU-h**
(≈ +3–5 days at 20 GPUs). Multiplicity untouched (same family, same corrections, per-seed scores).

### U2 — Multi-seed search selection, k=3 (RECOMMENDED; the deepest scientific upgrade)
The σ_D pilot's headline finding is that **σ_seed (0.244) dominates** — which means the current
1-seed-per-candidate search selects winners through exactly that noise. Training every candidate
at k=3 seeds and selecting/reflecting on the IQM:
- attacks the single largest measured weakness of the design at its source;
- the LLM's fed tail statistics become 3-seed aggregates → a cleaner signal for the MECHANISM
  study (responsiveness to signal, not to seed noise);
- uniform across arms → no identification concern; K stays 30 → multiplicity unchanged;
- turns the σ_seed-dominance finding into a design response, not just a disclosure — exactly the
  "insight → design" move Okhrati's grading function rewards.
Cost: search 210×3 = 630 (**+420 trainings**); engineering ~1–2 days (aggregate in the loop +
feedback block semantics + prereg §6 wording + freeze-gate mirror + tests). PRE-freeze design
choice. Decision: adopt iff G1 passes by ~Jul 16 (else it risks the freeze date — drop without
regret; the 1-seed design is already defensible and disclosed).

### U2b — Search-variance identification (3 independent search replicates)
`analyze_campaign --variance-runs` is ALREADY WIRED for ≥2 independent search re-runs → identifies
σ²_search (reward-draw variance) vs σ²_seed — directly quantifying the K-width limitation that CH7
currently only names. Cost: +2 full searches (+420–1,260 trainings depending on U2) **+ ~$40–70
extra Opus authoring**. Report-only appendix; zero new analysis code. Adopt if the allocation is
generous.

### U3 — Qwen full secondary replication (RECOMMENDED)
Elevate the R71 open-weights secondary from mini-panel to full replication: Qwen3-Coder authors
all 5 LLM arms × 30 candidates; its winners tested at n≥100. A genuine **cross-model-family
generalization test of the mechanism finding** (the ADR-039 "strong-diverse panel" at full
strength; TMLR's favourite robustness). Report-only; the Opus headline is untouched. Cost: ~360
trainings + ~$1–3 API + the DashScope activation (or the OpenRouter fallback).

### U4 — FTSE-100 external replication (report-only)
The corpus-verified reviewer attack on the whole Eureka lineage is single-market evidence. A lite
FTSE-100 replication (search + winners at n=30) on a second market: cost ~600 trainings + the
LSEG data build (~1–2 days, PowerShell/.venv-lseg path, licence already cleared). Adopt if
allocation + calendar permit; drop first under pressure.

### U5 — Algorithm robustness: PPO/TD3 + TQC on the frozen winners (report-only)
Pre-registered optional; kills "SAC-specific" in one appendix table. ~240 trainings.

### Priority under pressure: **U0 > U1 > U2 > U3 > U5 > U2b > U4.**

---

## 3. Rejected upgrades (the discipline section — decided NOW so scale doesn't tempt later)

- **More seeds than 403** — 403 IS the 95%-assurance point at the σ_D upper CI; beyond it is
  vanity precision. REJECTED.
- **More candidates / wider generations** — re-opens multiplicity; changes the frozen contrast.
  REJECTED (standing rejected-extensions register).
- **Longer training than 200k** — measured mild-overfit direction. REJECTED.
- **New arms, hypotheses, asset classes, options, 2000-start, sentiment/news** — identification
  creep + the standing register. REJECTED.
- **Moving the analysis/notebooks to cluster** — CPU-cheap, stays local. No value.
- **UCL Data Safe Haven routing** — not needed (licence cleared for research computing directly).

---

## 4. Cluster architecture + certification (the engineering)

**Fit.** The engine is already filesystem-coordinated and embarrassingly parallel: every training
is an independent spec that commits ONE atomic `record.json` (sidecars-first + fsync + rename),
resume is run_id-idempotent, and replay is hash-verified. That architecture transfers to a
scheduler UNCHANGED — only the *submission* layer is new.

1. **Driver/worker split.** Compute nodes typically have NO outbound internet → the LLM authoring
   loop (Anthropic/DashScope calls) runs on the **login node** (or locally); trainings are
   submitted as **array jobs**; the driver detects completion by polling the shared-FS archive
   (the records ARE the message queue). Reflection stays sequential per arm; arms run concurrently.
2. **Scheduler adapter** (~2–3 days): `submit_batch(specs) -> job ids` + archive polling + failure
   ledger, behind the same interface `run_recycling` serves locally. SGE (`qsub -t`) or Slurm
   (`sbatch --array`) — decided at G0. Walltime per task ~2 h (generous 2× margin).
3. **Environment**: the pinned stack via the same lockfile discipline as the Plan-B container
   (conda/venv on cluster; torch cu-build matched to the node CUDA at G0). Gold panel → scratch,
   verified by SHA-256 manifest on arrival (`archive_integrity`/`verify_gold`).
4. **Single GPU model** pinned in every job (`-l gpu_type=…`); `metrics.device` + env fingerprint
   already record it per training.
5. **Certification suite (G1, all must pass ON the cluster):**
   - keyless dry-run (full 4-stage pipeline, stub author);
   - `crash_rehearsal.py` (kill→resume byte-identity ON the cluster FS);
   - determinism control: same spec twice on the pinned GPU model → byte-identical records;
   - single-arm real-data smoke (gold panel, 50k) + fps measurement (re-anchor the timeline);
   - array-job scale test (~30 concurrent) + archive-integrity verify;
   - mirror path: nightly pull of the cluster archive → laptop → D:/Mac (tar-over-ssh
     exact-incremental — the driver host has no rsync; three-site rule keeps
     holding; the campaign archive must never live only on scratch — scratch is often purged).

---

## 5. Timeline scenarios (freeze ~Jul 13–20 either way)

| Scenario | Search | Test+H1+H3 | Campaign wall | Write-up window |
|---|---|---|---|---|
| Laptop (floor, unchanged) | ~5.4 d | ~19 d | **~24 d** → results ~Aug 9 | ~2.5 wk |
| Cluster, 20 GPUs, U0–U3 | <1 d | ~4–6 d | **~5–8 d** → results ~late Jul | **~5 wk** |
| Cluster, 40 GPUs, U0–U5 | <1 d | ~4–5 d | **~5–7 d** | **~5 wk** |

The recommended core (U0+U1+U2+U3) ≈ **5,900 trainings ≈ 3,500–4,400 GPU-h** — modest by cluster
standards, transformative for this design. Compute line for the paper (Okhrati's twice-docked
item): "≈N GPU-hours on UCL research computing (⟨GPU model⟩), M wall-clock days; pilots and
development on a single RTX 4050 laptop."

**Calendar rule:** the port must never delay the freeze past ~Jul 20. The dual-track trigger makes
this self-enforcing — if certification slips, Design-L launches on the laptop and the cluster
(once certified) simply becomes the Plan-B host and the robustness-appendix engine (U3–U5 can run
cluster-side AFTER a laptop headline launch, as report-only work).

---

## 6. What this buys against the rubric (why it serves the priorities)

- **Research design "faultless execution"**: symmetric full-power arms (U1); selection noise
  engineered out in response to a measured pilot finding (U2) — design-responds-to-data, his
  explicit taste.
- **Novelty/significance "journal-publishable"**: the generalization triad (model family U3,
  market U4, algorithm U5) is precisely where the corpus shows the Eureka-lineage neighbours are
  weakest; our differentiator (statistical rigor) is exactly what scale amplifies.
- **Depth**: U2 upgrades the mechanism instrument itself (cleaner fed signal → sharper
  responsiveness/mediation estimates). Nothing here adds breadth to the body.
- **The grade's true lever**: ~5 weeks for the document instead of ~2.5. The single largest
  expected-grade effect in this whole plan is the calendar, not the GPUs.

## 7. Asks (Tamer)

1. Forward the allocation email details (G0 checklist in §1) the moment you have them.
2. One-line reply to keep on file: who confirmed the licence-on-UCL-systems "yes" (for the
   data-governance paper trail).
3. Optional but smart: tell Okhrati the allocation landed + the dual-track intent (one paragraph —
   it also signals initiative, which the rubric rewards).
4. Decisions at freeze: adopt U1/U2/U3 (recommended), U2b/U4/U5 (if generous), tier ordering, 403.

---
---

# PART II — THE MAXIMAL DEPTH PROGRAM (v2, 2026-07-06, Tamer's "no constraints" directive)

> Part I optimized under residual laptop-era caution. Part II is the ceiling: every upgrade that
> adds **depth, precision, calibration, mechanism resolution, or generalization** to the SAME
> identified design is adopted. What remains refused is refused for scientific reasons only
> (identification, multiplicity, frozen-contrast integrity) — that discipline IS the world-class
> property, per the priorities re-read (★1–★4), the IFT guidelines (10k words; publishable = the
> 90–100 descriptor), and Okhrati's revealed function (depth>breadth; design-responds-to-data;
> mechanism originality; honest nulls; a buffet is penalized).

## 8. The deep-science additions (D-series)

### D1 — Reflection dose–response: H3 becomes a CURVE (pre-freeze registration)
Generations ∈ {1, 2, 4, 6, 8} for the distributional arm at the SAME matched 30-candidate budget
(6×5 → 30 candidates redistributed per level), k=3 seeds/candidate, winners tested at n=100.
- **Why**: H3 today is a 2-point contrast (6 vs 1). A five-point curve measures the *marginal
  value of reflection* for financial reward design — unmeasured anywhere in the Eureka lineage —
  and shows whether tail feedback changes the reflection *trajectory*, not just the endpoint.
  A curve is also Okhrati-legible intuition (one figure carries it).
- **Multiplicity discipline**: the CONFIRMATORY H3 statement stays the registered 6-vs-1 contrast;
  the intermediate points register ex-ante as exploratory trend description around it.
- Cost: 3 extra search levels ×30 cand ×k3 = 270 search + 3×100 test = 300 → **~570 trainings**;
  authoring ≈ +$25–45 Opus. Engineering ~0.5 d (generations is already a config knob; H3 harness
  exists).

### D2 — The designer sensitivity probe (§2a(h), registered ex-ante; post-campaign execution)
Counterfactual re-authoring: take archived reflection states and re-issue the SAME prompt with
systematically perturbed fed blocks (e.g. cvar_05 ×2, robust_skew sign-flipped, one statistic
ablated at a time) → measure the local sensitivity of the authored CODE to each fed statistic
(AST-diff + coefficient deltas + optional training of the top-Δ responses).
- **Why**: the mechanism instruments so far are OBSERVATIONAL (what the LLM did with what it was
  fed). This is the INTERVENTIONAL complement — a trait-intervention-style experiment on the
  *designer* — the same causal genre as Okhrati's own ACL-2025 LLM-risk paper, and the cleanest
  possible answer to "WHICH statistic does the designer actually use?" WITHOUT adding arms
  (identification untouched: this is post-hoc, off-loop, report-only).
- Cost: ~150–300 authoring calls ≈ **$20–40 API**, optional +100 trainings; harness ~1–2 d
  (prompt replay exists via the archive; perturbation grid is new).

### D3 — Variance-components decomposition (the σ_seed finding becomes a contribution)
With U1 (uniform n=403) + U2 (k=3 per candidate) the data supports a proper mixed-effects
decomposition: σ²_arm vs σ²_candidate(draw) vs σ²_seed on validation and test fitness — the first
quantified variance budget for LLM reward design. Extends the R67 Bayes machinery; statsmodels
MixedLM + case bootstrap (no new deps). Analysis-only (~1 d). One body paragraph + one appendix.

### D4 — Winner's-curse shrinkage estimate (selection honesty, made quantitative)
Empirical-Bayes shrinkage of each arm's winner using the k=3 candidate replicates → report
"selection-corrected" winner effects alongside DSR/PBO. Small analysis (~0.5 d), large
sophistication-per-word; directly strengthens the H1/H4 comparisons' honesty.

### D5 — Whole-pipeline calibration study (the killer methodological answer)
~30 synthetic-null replicates of the ENTIRE procedure (stub author → search → selection → sealed
test → the full inference chain) on synthetic panels with known zero effect, plus ~10 replicates
with injected effects of known size → the empirical Type-I rate and power OF OUR EXACT PIPELINE.
- **Why**: complex pre-registered pipelines invite "is your α really 0.05?" This answers it with
  data. Almost nobody in the neighbourhood does end-to-end procedure calibration; it converts
  methodological trust from asserted to measured.
- Mirror at reduced B\*=50k on synthetic (disclosed; the inference chain consumes returns, and the
  calibration targets the CHAIN) → ~30×150 + 10×150 ≈ **6,000 stub trainings at ¼ cost ≈
  ~1,500 GPU-h**. Harness ~1–2 d (dry-run machinery + a replicate driver).

### D6 — TQC named-secondary at strength ("distributional critic vs distributional feedback")
The sanctioned secondary (CLAUDE.md; Phase-0 TQC smoke was GREEN): re-test the FROZEN winners of
the two H2 arms + placebo under a TQC agent at n=100 → one table answering "does giving the AGENT
a distributional view substitute for giving the DESIGNER one?" — conceptually pointed, report-only.
Cost: ~300 trainings; engineering ~0.5 d (TQC path exists from Phase 0).

### D7 — Three-family designer panel (restores the FULL ADR-039 vision) [API-$ gated]
Opus (confirmatory) + GPT-5.5 + Qwen3-Coder as SECONDARY replications of the 5 LLM arms → the
mechanism finding tested across two closed frontier families and one open family; a mini
meta-analysis across designers. GPT-5.5 was rejected on COST only — that constraint is Tamer's
call now. Cost: ~+$25–45 API + ~400 trainings (winners at n=100).

### D8 — The replication package (respectability infrastructure)
One-command "archive → every figure/table" replay script + pinned analysis container + OSF
deposit of the frozen bundle and (post-submission) the record archive + the model cards.
~1 d. This is what makes external researchers ADOPT the protocol — the instrument/protocol
contributions only compound if trivially reusable.

## 9. Refusals that stand even at infinite compute (unchanged, now with the "why" sharpened)
- **No ablation ARMS** (which-statistic-matters is answered interventionally by D2 without
  touching the frozen roster/identification).
- **No new hypotheses/arms/assets/markets beyond FTSE, no options, no 2000-start, no wider K, no
  longer B\*, no >403 seeds** — each breaks identification, multiplicity, or measured-optimality;
  scale is not a reason.
- **No body growth**: every D/U item = at most one body paragraph + one appendix; the body remains
  the four deep analyses. (10k words; depth>breadth is graded, not optional.)

## 10. The program at a glance (adoption tiers, costs, freeze-impact)

| Tier | Items | Trainings | GPU-h | API $ | Pre-freeze work |
|---|---|---|---|---|---|
| **P0 core design** | U0 + U1 + U2 | ~6,100 | ~3,700–4,600 | ~$35 (Opus, unchanged) | seed schema + k=3 (~2 d) |
| **P1 registered depth** | D1 + D2-registration + U3 | ~1,300 | ~800–1,000 | +$45–85 | D1 config + §2a(h) text (~1 d) |
| **P2 robustness fleet** | D3 + D4 + D6 + U5 + U2b | ~1,700 | ~1,000–1,300 | +$40–70 (U2b) | none (post-freeze, report-only) |
| **P3 meta + external** | D5 + U4 + D7 + D8 | ~7,000 (mostly ¼-cost stubs) | ~2,300–2,800 | +$25–45 (D7) | none |
| **TOTAL (everything)** | | **~16,000** | **~7,800–9,700** | **~$145–235** | ~3 d engineering |

At 40 concurrent GPUs: **~9–12 wall days for the entire maximal program**; at 20: ~2.5–3.5 weeks
(then run P0–P2 first and let P3 trail). The freeze deadline (≤ Jul 20) is untouched — only U2,
D1, and the D2/§2a(h) registration text are pre-freeze items; everything else is post-freeze
report-only by construction.

## 11. What the finished object IS (the honest ambition statement)
Not "a pre-registered null with a mechanism section," but: **the definitive controlled study of
distributional feedback in LLM reward design — identified (7-arm frozen contrast), powered
(n=403 uniform), selection-denoised (k=3 + shrinkage), variance-decomposed, pipeline-calibrated
on synthetic ground truth, mechanism-resolved both observationally (fingerprint/mediation/funnel)
and interventionally (sensitivity probe), dose-response-measured over reflection depth, and
generalization-tested across model families, a second market, and agent algorithms — with a
one-command replication package.** That is a TMLR-strong, ICAIF-main-credible object, and every
component lands as appendix armor behind the same 4-analysis, 10k-word body the rubric and the
examiner reward.
