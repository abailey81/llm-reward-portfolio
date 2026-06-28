# Compute & Training-Time Plan

**Authoritative compute reference** for the campaign. Supersedes the earlier "$50 Colab" (MASTER_PLAN
Part VI) and "RTX 4090 + UCL Myriad" (FINAL_PLAN Part I) assumptions, because: (a) the student has **no
UCL Myriad access**, (b) the owned machine is an **RTX 4050 laptop**, and (c) **Azure-for-Students GPU is
effectively unavailable** (quota blocked — see §6). Committed scope: **30 candidates × 1 search seed**, with
**per-arm winners re-run at 30 seeds** (decisions AMEND-ORIG-1 + **amendment D2, 2026-06-19**: winner seeds
5→30 for the H2 IQM/CI; Henderson 2018, Colas et al. ≥20). **Only the seeds-on-winners count changes** — the
SEARCH budget is untouched, so matched compute holds. The numbers below are recomputed as **winners × 30**.

> **The one unmeasured quantity is `m` = minutes per full 50k-step SAC run.** Every wall-clock/cost figure
> below is `runs × m`, computed for an explicit per-GPU band. The **Phase-0 smoke test**
> (`scripts/smoke_test.py`, ~30 min on the 4050) measures `m` and collapses all bands to exact numbers.
> Run it first.

---

## 1. What "training everything" is — run-count accounting (seeds-on-winners; winners × 30 — amendment D2)

The **recommended** (and committed) protocol is **seeds-on-winners**: each candidate trains at **1 seed
during the search**, and only the per-arm **winners are re-run at 30 seeds** (amendment D2, 2026-06-19 —
was 5; raised for the H2 IQM/CI). The full 5-seeds-on-every-candidate grid is retained only as a costed
alternative (§3 "Full SAC").

| Component | Trainings | Note |
|---|---|---|
| **Prototype** — Phase-0 smoke (SAC + TQC, ~5k steps) | ~2 short (~0.2 full-run-equiv) + one-time setup | the gate |
| Light pilot (3 arms × 5 cand × 1 seed) | ~15 | optional sanity gate |
| **Search** — 7 arms × 30 candidates × **1 seed** | **210** | matched-compute search (untouched by D2) |
| **Winner re-runs** — 7 per-arm winners × **30 seeds** (amendment D2; was 6 × 5 = 30) | **210** | the H2 IQM/CI legs |
| Hand-designed baselines (4 reward canon × **30 seeds**, H1; was × 5 = 20) | **120** | re-run at the winner seed count |
| Benchmark strategies (1/N, MV-shrinkage, risk-parity, HRP, SPY) | **0** | analytic allocators — no GPU training |
| CPCV on winners (inference on the existing performance matrix) | **0** | no retraining (audit B-3) |
| PPO/TD3 robustness on winners (2 algos × winners × 30; was ~20 at 5 seeds) | ~120 | small models, but now × 30 seeds |
| **→ Lean SAC program subtotal (seeds-on-winners, winners × 30)** | **≈ 600 full-run-equivalents** (≈ 7/6× the 6-arm tally) | (was ≈ 205 at 5 winner-seeds) |
| *Optional* secondary SAC-vs-TQC critic experiment (2 winners × 30 seeds; was 2 × 30 cand × 5) | +60 winner-seeds | only if Phase-0 TQC is green |
| *Alternative* — full 5-seeds-on-every-candidate core (6 × 30 × 5) | 900 | the costed "Full SAC" grid (§3), NOT the committed path |

> **What "~210 runs" is — and is NOT, the elementary-test count.** The **210** figure is the per-arm
> **winner re-runs** (seeds-on-winners: 7 winners × 30 seeds = 210), and the **search** legs are a separate
> 210 (7 arms × 30 candidates × 1 seed). Neither is the headline **elementary-test count**: the H2 inference
> runs **6 tail statistics × 30 seeds = 180** elementary tests per arm-contrast. Do not conflate the run-count
> (training budget) with the test-count (multiplicity unit). For the authoritative, reconciled accounting of
> all three quantities, `compute_accounting` (`scripts/analyze_campaign.py`) is authoritative — these
> doc-tables are descriptive.

**Note (amendment D2).** Raising the winner seed count 5→30 leaves the **search** legs (210) unchanged, so
matched-compute holds; it grows the **winner/baseline/robustness re-runs** ~6× (those re-runs were the small
tail of the lean path). The recommended lean program is now **≈ 600 winner-equivalent runs** (vs ≈ 205 at 5
winner-seeds); still far below the 900-run full grid, and the rented-4090 budget below scales linearly.
(7 arms × 30 since R32/R54 added placebo_shuffled; the lean subtotal scales proportionally.)

---

## 2. Per-run cost `m` (one 50k-step SAC training)

- **Environment is NOT the bottleneck** — measured at **12,654 steps/sec** on the synthetic 30-asset panel
  → 50k env-steps = **~4 seconds** with no network. All cost is the SAC gradient updates.
- The observation is **1,893-dimensional** (30 assets × 60-day lookback + vol + lagged VIX + cash + prev
  weights), so the SAC MLPs' first layer and the 50k×1,893 replay buffer (~380 MB; fits 6 GB VRAM) carry
  the cost.
- **SAC is overhead-bound, not FLOPS-bound** for these small nets — so per-run times across a 4050 laptop, a
  Colab T4, and an A100 land within ~1.5× of each other. **Parallelism and session limits matter far more
  than GPU tier.** (Anchor: SB3 SAC ≈ 70–77 steps/s on a small env → ~11 min/50k; adjusted up for the wide obs.)

**Estimated `m` by GPU (central, pending Phase-0):**

| GPU | `m` (min / 50k-step run) |
|---|---|
| RTX 4090 (rented) | ~10–12 |
| RTX 3090 (rented) | ~12–16 |
| RTX 4050 laptop (owned) | ~12–25 (central ~18) |
| T4 / P100 (Kaggle, Colab free) | ~15–25 |
| L4 (Colab Pro+) | ~10–18 |
| A100 (datacenter — overkill) | ~8–12 |

---

## 3. GPU-hours and wall-clock by scenario

GPU-hours = `runs × m`. Lean = seeds-on-winners with **winners × 30** (~600 runs, amendment D2); Full = 5
seeds on every candidate (~955 runs).

| | Lean (~600 runs) | Full SAC (~955 runs) | Full + TQC (~1,255) |
|---|---|---|---|
| on a **4090** (m≈11) | **~110 GPU-hr** | ~175 GPU-hr | ~230 GPU-hr |
| on a **4050** (m≈18) | ~180 GPU-hr | ~285 GPU-hr | ~377 GPU-hr |
| on a **T4/P100** (m≈20) | ~200 GPU-hr | ~317 GPU-hr | ~418 GPU-hr |

*(Pre-amendment, the lean path at 5 winner-seeds was ~205 runs ≈ 38 GPU-hr on a 4090; raising the winner
seeds to 30 — amendment D2 — lifts it to ~600 runs ≈ 110 GPU-hr. **NB: there is no GPU-hour cap** — the
`hard_budget_gpu_hours` limit was removed 2026-06-28; all GPU-hour figures in this doc are informational
wall-clock/cost estimates, not a budget.)*

**Serial wall-clock (one GPU):** GPU-hours ÷ 24.
**Parallel:** GPU-hours ÷ (number of concurrent GPUs).

---

## 4. Every viable platform (2026 prices)

| Option | GPU / free limit | Lean (~600, winners×30) | Full 30×5 (~955) | Cost | Verdict |
|---|---|---|---|---|---|
| **Vast.ai — rent RTX 4090** | ~$0.29–0.40/hr (marketplace; interruptible ~$0.30) | **~4.6 days / ~$32–44** (1 GPU); ~half a day parallel | ~7 days / ~$68 | pay-as-you-go | ⭐ best value + speed, no quota |
| **RunPod — rent RTX 4090** | $0.34/hr community ($0.59 secure) | ~4.6 days / **~$37** | ~7 days / ~$60 | pay-as-you-go | ⭐ clean UX, same tier |
| Rent **RTX 3090** (Vast) | ~$0.20–0.25/hr | ~6 days / **~$26–33** | ~9 days / ~$45–50 | cheapest paid | ✅ if patient |
| **RTX 4050 laptop** (owned) | free | ~7.5 days | ~12 days | free | ✅ free; ties up laptop (heat/throttle) — best for prototype + dev |
| **Kaggle** | **30 GPU-hr/wk** free (P100 16 GB; 9 h sessions) | ~2.5 wk free | too slow alone | free | ✅ best free building block |
| **Colab free** | ~15–30 hr/wk (T4, not guaranteed) | with Kaggle ~1.5–2 wk | impractical | free | ✅ stack with Kaggle |
| **Lightning AI** | **~80 GPU-hr/mo** free | most of a lean run | partial | free | ✅ third free GPU |
| **Stacked free** (Kaggle+Colab+Lightning+laptop) | **~50–60 GPU-hr/wk** | **~3–4 weeks, $0** | ~5–6 weeks | free | ✅ zero-cost if you'll babysit |
| Colab **Pro+** | L4, 24 h background exec | ~1 week | ~3–4 wk (units cap) | ~$50/mo | △ slow/metered |
| Lambda / datacenter **A100** | ~$1.3–2/hr | ~$50+ | ~$280+ | $$ | ✗ overkill for tiny SAC nets |
| **Azure for Students** ($100) / **GCP $300** | — | — | — | "free" credit | ✗ **GPU quota blocked/denied** (§6) |
| GitHub Student Pack credits | DigitalOcean/etc. | — | — | free credits | △ same GPU-quota problem; not a reliable GPU source |

---

## 5. THE DECISION (what to proceed with)

1. **Prototype → RTX 4050 laptop, first, ~30 min, free.** Run `scripts/smoke_test.py`; it measures `m` and
   confirms SAC (+TQC) train. Nothing downstream runs until this is GREEN.
2. **Campaign → rent an RTX 4090 on RunPod or Vast.ai, with seeds-on-winners (winners × 30, amendment D2).**
   **≈ $32–44 and ~4.6 days on one GPU** — or rent ~4–8 in parallel for **~half a day** at the same total cost.
   No quota approval, a 4090 suits SAC, fully reproducible from the frozen config. *(At the pre-amendment 5
   winner-seeds this was ≈ $13–16 / ~1.5 days; the winner-seed lift to 30 grows the lean program ~3×.)*
3. **Free alternative (if the ~$40 matters more than the calendar):** stack **Kaggle (30 h/wk) + Lightning
   (~80 h/mo) + Colab + the laptop overnight** → the lean program in **~3–4 weeks, $0**, with checkpointing.
4. **If you insist on full 5-seeds-on-every-candidate:** ~$60 / ~7 days on one rented 4090, or ~hours across
   several; or ~12 days free on the laptop.

**Primary recommendation: rented RTX 4090 + seeds-on-winners, winners × 30 (~$32–44, ~4.6 days serial / ~half
a day across several GPUs).**

Cost discipline for rented GPUs: use **spot/interruptible** + **auto-shutdown on completion** +
**checkpoint** (the campaign is resumable, `run_campaign.py --resume`) so an interruption is harmless and you
never pay for idle time.

---

## 6. Why Azure-for-Students (and GCP free) do NOT work for this
- Azure for Students gives **$100 / 12 months, no card** — real — **but**: student/free subscriptions default
  to a **3-vCPU quota** (too small for any GPU VM), and **GPU quota-increase requests on free/benefit/student
  subscriptions are routinely denied** (Microsoft prioritises paying customers for scarce GPU SKUs). Confirmed
  widespread. GCP's $300 free trial has the **same** GPU-quota catch. AWS has no free GPU tier.
- Net: treat these credits as usable for *non-GPU* bits only; **not** a path for the training campaign.

---

## 7. The hard dependency
Every day/cost figure here is linear in `m`. **Run the Phase-0 smoke test on the 4050 first (~30 min)** — it
prints the measured minutes-per-run, after which these bands become exact numbers and the choice between
"full 30×5" and "seeds-on-winners" can be made on real data.

*Sources (2026): Vast.ai RTX-4090 pricing (vast.ai/pricing/gpu/RTX-4090); Vast-vs-RunPod 4090 (synpixcloud);
Kaggle 30 h/wk, Colab free tier, Lightning ~80 h/mo (gmicloud / freerdps free-GPU guides); Azure-Students GPU
quota denials (Microsoft Q&A). SB3 SAC throughput anchor (~70–77 steps/s) from SB3 issue #122 / skrl benchmarks.*
