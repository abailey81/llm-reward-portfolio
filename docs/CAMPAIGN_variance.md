# Variance Decomposition — the one-lucky-reward defence (reviewer attack #10)

**Module:** `scripts/variance_decomposition.py` · **Tests:** `tests/test_variance_decomposition.py`
**Spec:** `00_planning/CAMPAIGN_DEEP_RESEARCH_FINDINGS_2026-06-21.md` §5.8 (variance decomposition) + §5.3
(the per-seed score is the inference unit) · **Status:** built, ruff/mypy/test-green; report-only appendix.

> **Headline sentence (the deliverable):** *"the IQM gap exceeds √σ²_search, so the effect is a property of
> the distributional-feedback channel, not one lucky reward."*

---

## 1. The attack this answers

The headline H2 statistic is an **IQM gap** between two arms' per-seed test scores
(`IQM(distributional per-seed Sharpes) − IQM(scalar per-seed Sharpes)`; the rliable unit of
`scripts/analyze_campaign.py::collect_family_pvalues`). Red-team attack #10 (Part 7 of the findings):

> *"Statistical power / 5 seeds is noise — that gap is just one **lucky reward** the LLM search happened to
> draw, not a property of the channel."*

≥30 seeds + per-seed rliable inference already answer the "5 seeds is noise" half. This module answers the
**"one lucky reward"** half directly: it partitions the variance of a single per-seed test score into three
nested, identifiable sources and asks whether the observed gap is larger than the **reward-draw** noise.

## 2. The three variance components (what each is, and where the data comes from)

For ONE arm, organise the per-seed test scores as a **`(K, S)` table** — `K` independent **re-runs of the
reward search** (each yields a possibly-different winner reward) × `S = 30` training **seeds** the frozen
winner is re-trained at.

| Component | Meaning | Source | Cost |
|---|---|---|---|
| **σ²_seed** | Variance across the 30 training seeds for a *fixed* winner reward (training-RNG noise). | The within-search across-seed dispersion already in the 30 frozen-winner TEST records. | **Free** (the campaign already writes them). |
| **σ²_search** | Variance across *independent search re-runs* — the **reward-draw** variance (= the "one lucky reward" quantity). | The between-run dispersion of the `K` winners' per-seed score means. | **K≥2 re-run searches** (§5.8; see §4). |
| **σ²_market** | Sampling noise of the *single realized 2018-2025 test path itself* (independent of reward/seed). | Stationary block bootstrap of one representative winner's per-step test return series. | Free (re-uses an existing test path). |

σ²_seed and σ²_search are estimated **jointly** by a one-way random-effects ANOVA on the `(K, S)` table;
σ²_market is an orthogonal block-bootstrap of the realized path.

## 3. The estimator (one-way random-effects ANOVA, method of moments)

Model the per-seed scores `y_ks = μ + a_k + e_ks` with a **search-run effect** `a_k ~ N(0, σ²_search)` and a
**seed residual** `e_ks ~ N(0, σ²_seed)` (Searle, Casella & McCulloch 1992, *Variance Components*; Montgomery,
*Design and Analysis of Experiments*, the random-effects one-way model; PSU STAT-503 §3.5). The expected mean
squares are

```
E[MS_between] = σ²_seed + n₀·σ²_search
E[MS_within]  = σ²_seed
```

giving the **ANOVA (method-of-moments) estimators**

```
σ̂²_seed   = MS_within
σ̂²_search = max(0, (MS_between − MS_within) / n₀)
n₀        = (1/(K−1)) · (N − Σ_k S_k² / N),   N = Σ_k S_k        # = S when balanced
```

- **Negative-estimate truncation.** When the true between-search variance is ≈0, sampling noise gives
  `MS_between < MS_within` → a *negative* raw `σ̂²_search`, **truncated to 0**. A non-negative quadratic
  *unbiased* estimator of a variance component does not exist; simple truncation at 0 uniformly improves the
  raw ANOVA estimate (standard practice). The pre-truncation value is reported as `sigma2_raw` for audit.
- **σ²_market** = `Var` of the per-path statistic across `n_boot` stationary-bootstrap replications of the
  test return series (Politis & Romano 1994, random geometric block length `1/p`, `p=0.1` ⇒ expected block
  length 10), reusing `src.inference.bootstrap.stationary_bootstrap_indices`.

**The verdict.** The yardstick is the **treatment arm's** (distributional) σ²_search — the "lucky reward"
the attack invokes is a draw of the *distributional* reward. The module reports

```
gap_exceeds_sqrt_sigma2_search  :=  |IQM_gap|  >  √σ²_search
```

`True` ⇒ the channel effect exceeds one standard deviation of the reward-draw noise → *"channel, not luck."*
`False` ⇒ report INCONCLUSIVE on this axis (need more re-runs or a larger effect — never overclaim).

### Why σ²_search is the right yardstick (and NOT the headline d.f.)

This module **does not re-test H2**. The realized H2 test's degrees of freedom is **`n_seeds = 30` PAIRED
per-seed scores** (`paired_seed_difference_test`); §5.8 is emphatic that *neither* `N_block` *nor* `N_hmm` is
the headline d.f. The variance budget here is **descriptive**: σ²_search is the *scale of the reward-draw
noise*, and the verdict says whether the gap clears it. It is a **report-only appendix in its own declared
family** (result keys `component`/`generator`), disjoint from the frozen `arm_a/arm_b/metric/level` family, so
`assert_realized_family_matches_frozen` stays green (findings §2, "Amendment-free additions") — **no
pre-registration amendment is required.**

## 4. The K-search re-run requirement (extra GPU-hours)

σ²_search is the only component that costs new compute: it needs `K ≥ 2` **independent re-runs of the search**
per studied arm. The campaign's headline run is `K = 1` (re-used free); the study adds `K−1` more re-runs.

**Per extra re-run, per arm** (using the committed seeds-on-winners protocol,
`docs/COMPUTE_AND_TRAINING_TIME.md`):

| Stage | Trainings | Note |
|---|---|---|
| Search (re-run) | 30 | 30 candidates × 1 search seed (a fresh LLM reward search; matched-compute unit). |
| Winner re-run at 30 seeds | 30 | that re-run's winner re-trained at the 30 frozen seeds → its per-seed score row. |
| **per extra re-run per arm** | **60** | |

**Recommended study: `K = 3` on the distributional + scalar pair** (§5.8). The headline run supplies the
first row free, so **2 extra re-runs × 2 arms = 4 extra (search + winner) blocks**:

```
extra trainings = 4 blocks × 60 = 240 trainings
extra GPU-hours = 240 × m,   m ≈ 11 min / 50k-step SAC run on a rented RTX 4090
                ≈ 240 × 11 / 60  ≈ 44 GPU-hours   (~$3–6 on Vast/RunPod; ~2 h across 4 GPUs)
```

This is a cheap add-on (~44 GPU-hr) on top of the ~110 GPU-hr lean campaign. **There is no GPU-hour cap**
(`hard_budget_gpu_hours` was removed 2026-06-28 — never code-enforced); these figures are estimates, not a limit.

> **Note on the §5.8 "~150 extra trainings" figure.** That estimate counts the *search* re-runs only
> (≈ 30 × (K−1) × 2 arms = 120) plus a partial winner-seed allowance; the full accounting that also re-trains
> each new winner at all 30 seeds (needed for that run's per-seed score row) is the **240 / ≈44 GPU-hr** above.
> Both fit the cap. **Degrade-gracefully fallbacks** (the pre-registered scoping down-rank list, §5.8): drop to
> `K = 2` (1 extra re-run/arm = 120 trainings ≈ 22 GPU-hr), or study the distributional arm only.

**Replay/provenance.** Each re-run is a full `scripts/run_campaign.py` invocation with a **distinct top-level
`output_dir`** (e.g. `outputs/variance/run1`, `.../run2`), so the K archives are disjoint and the LLM rewards
that each search drew are archived (`reward.py` sidecars) and replayable. Point the study at them with
`--runs`.

## 5. CLI usage

```bash
# K ≥ 2 — identifies σ²_search (each root the output_dir of a full, independent search re-run):
python scripts/variance_decomposition.py \
    --runs outputs/campaign outputs/variance/run1 outputs/variance/run2 \
    --n-boot 2000 --out outputs/campaign

# K = 1 fallback (a single archive) — σ²_seed + σ²_market reported, σ²_search gracefully skipped:
python scripts/variance_decomposition.py --root outputs/campaign
```

Writes `variance_decomposition.{md,json}` to `--out` (default: the first run root). With no flags it falls
back to `config: campaign.output_dir`, then the prototype `output_dir` (always `K = 1`). The driver **never
crashes**: an unreadable run root, a records-only archive (no `test_returns`), or `K = 1` all yield
`status="skipped"` with a reason, not an exception.

## 6. `analyze_campaign.py` wiring SPEC (for the user to apply)

The variance study is **standalone** and need not touch `analyze_campaign.py`. If you want the verdict folded
into the single campaign report (`campaign_overfitting.md`), apply this **additive, opt-in** wiring. It only
runs when `K ≥ 2` run roots are supplied, and emits a disjoint `variance` key, so the frozen-family assert and
every existing test are unaffected.

> ⚠️ I did **not** edit `analyze_campaign.py` — this is a spec for you to apply by hand (the task scoped me to
> writing only the three deliverable files).

**(a)** Add an optional `variance_run_roots` parameter to `analyze(...)` (default `None`), and after the
existing `h2` block, before `return out`:

```python
# Variance decomposition (reviewer attack #10) — the one-lucky-reward defence. ADDITIVE + report-only:
# runs ONLY when >= 2 independent search re-run roots are supplied (else omitted), and writes a DISJOINT
# `variance` key (component/generator family) so the frozen arm×metric family assert is untouched.
if variance_run_roots and len(variance_run_roots) >= 2:
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import variance_decomposition as _vd  # scripts/variance_decomposition.py

        run_records = _vd._load_runs(list(variance_run_roots))
        out["variance"] = _vd.decompose_from_campaign(
            run_records, n_boot=2000, rng=np.random.default_rng(0)
        )
    except Exception as exc:  # noqa: BLE001 — a report-only appendix must never break the headline analysis
        out["variance"] = {"status": "skipped", "reason": str(exc)}
```

**(b)** In `write_report(...)`, after the `benchmark_floor` markdown append:

```python
if result.get("variance"):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import variance_decomposition as _vd
    md = md + "\n" + _vd.verdict_markdown(result["variance"])
```

**(c)** In `main()`, add a CLI flag and thread it through:

```python
p.add_argument(
    "--variance-runs", nargs="+", default=None,
    help="≥2 independent search re-run roots to identify σ²_search (reviewer attack #10). "
         "Omit to skip the variance appendix.",
)
# ... then in the analyze(...) call:
result = analyze(
    args.root, n_blocks=args.n_blocks, panel=panel, cfg=cfg,
    test_window=test_window, winner_n_trials=winner_n_trials,
    variance_run_roots=args.variance_runs,
)
```

**Invariants preserved by this wiring** (so it is safe to apply):
- The `variance` key is **disjoint** from the frozen `arm_a/arm_b/metric/level` family →
  `assert_realized_family_matches_frozen` is never triggered by it.
- It runs **only** when `≥ 2` run roots are passed; the default (no flag) reproduces the current report
  byte-for-byte. The headline H2 conjunction, PBO, DSR, and the floor are **unchanged**.
- The whole block is wrapped so a failure degrades to `status="skipped"` — it can never break the headline.

## 7. References

- Searle, Casella & McCulloch (1992), *Variance Components* — the one-way random-effects ANOVA estimators.
- Montgomery, *Design and Analysis of Experiments* — the random-effects one-way model + EMS.
- Penn State STAT-503 §3.5, *One-way Random Effects Models* — `σ̂²_τ = (MS_treatments − MS_E)/n`, the
  unbalanced `n₀` divisor, and the negative-estimate-truncated-to-zero convention.
- Politis & Romano (1994), *The Stationary Bootstrap*, JASA 89(428) — σ²_market block bootstrap.
- `00_planning/CAMPAIGN_DEEP_RESEARCH_FINDINGS_2026-06-21.md` §5.3 / §5.8 (the project spec).
