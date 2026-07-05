# CAMPAIGN_attribution — factor attribution & difference-in-alpha (Door-C secondary)

**Module:** `src/inference/attribution.py` · **Tests:** `tests/test_attribution.py` (18, green)
**Status:** built, ruff+mypy clean, real-data sanity-checked. **Reporting-layer only** — touches no
env, reward, agent, or treatment. **Separate declared secondary family; the frozen m=6 is untouched.**

This is the answer to the **#1 un-planned reviewer hole** (`CAMPAIGN_DEEP_RESEARCH_FINDINGS_2026-06-21.md`
Part 7 red-team #6; §5.10): *"the agent's edge is just low-vol / betting-against-beta (BAB) beta, not
the reward channel."* We re-price each arm's **realized test returns** against a ladder of published
factor models and report the **difference in alpha** (distributional minus comparator) after the
factor controls, into the **same per-seed paired bootstrap** the headline H2 uses.

---

## 1. Method

### 1.1 The single-series regression — `factor_alpha(returns, factors, hac_lag=None)`

For one realized daily return series `r_t` (a frozen-winner test path) and a factor matrix `F_t`
(each column a long/short factor return in decimals), ordinary least squares:

```
(r_t − rf_t) = alpha + Σ_k beta_k · F_{k,t} + eps_t
```

* `Mkt-RF` is itself an excess return, so it enters raw. The **left-hand side uses excess returns**
  `r − rf`, so `alpha` is **Jensen's alpha** (the average return left unexplained by the factors).
  `alpha` is reported per period; **annualised alpha `= alpha · 252`**.
* `risk_free=None` (the default) is the frozen-headline `rf = 0` convention (byte-identical to the
  headline). Pass the per-period rf vector to report the excess-return variant.

**Standard errors — Newey & West (1987) HAC, Bartlett kernel.** Daily portfolio residuals are
serially correlated (volatility clustering, momentum/mean-reversion), so plain OLS SEs understate
sampling error. We use HAC SEs with the Bartlett kernel `w_l = 1 − l/(L+1)`. The truncation lag is
the **Newey & West (1994) automatic-lag rule of thumb**:

```
L = floor( 4 · (T/100) ^ (2/9) )          # newey_west_hac_lag(T)
```

* **Cite Newey-West (1994) for the *automatic-lag rule*; Newey-West (1987) for the *estimator*.** (The
  `4(T/100)^{2/9}` rule is Newey-West 1994, *not* Schwert 1989 — Schwert's `12(T/100)^{1/4}` is a
  different, ADF unit-root, lag rule that is not used here.)
* statsmodels' `OLS.fit(cov_type="HAC", cov_kwds={"maxlags": L, "use_correction": False})` applies
  exactly this Bartlett-kernel HAC; its `nlags` default **is** this floored Newey-West value. We pass `L`
  explicitly so it is logged/reproducible, and `newey_west_hac_lag` + a hand-rolled `_newey_west_cov`
  (Bartlett, `use_correction=False`) are unit-tested to **equal** statsmodels bit-for-bit
  (`test_statsmodels_hac_equals_hand_rolled_newey_west`). The hand-rolled estimator is also the
  statsmodels-free fallback, so the module never hard-depends on a statsmodels internal.
* For `T ≈ 1571` (the real 2020–2026H1 daily test leg under Split C, R73) the Newey-West (1994) lag
  is **7** — unchanged from the pre-Split-C 2018–2025 leg (`T ≈ 2087`), which also floored to 7.

**Graceful degradation (never raises):** `status="skipped"` with a `reason` — and `alpha=None`,
never a fabricated number — when the series is too short for the parameter count, non-finite, or the
design is rank-deficient (a constant/collinear factor). `status="ok"` otherwise, returning
`alpha, alpha_t, alpha_p, alpha_se, alpha_ann, betas{}, betas_t{}, r2, n, hac_lag`.

### 1.2 The headline — `difference_in_alpha(...)` (per-seed, paired, across-seed)

We do **not** pool the two arms into one series. Mirroring the frozen per-seed rliable inference
(Agarwal et al. 2021; `src.inference.bootstrap.paired_seed_difference_test`):

1. For each arm, fit the factor model **per seed** (one frozen-winner test path per training seed) →
   that seed's `alpha`.
2. Run the **paired across-seed bootstrap** on the per-seed alpha differences
   `alpha_a(seed) − alpha_b(seed)` over the **shared training seeds**, with the **IQM** central
   tendency — identical machinery to the headline Sharpe/CVaR legs.

This carries the **across-seed (training-RNG) variance** — the dominant uncertainty in a multi-seed
RL evaluation — exactly as the headline does. A single-path regression on the seed-pooled series
would collapse that variance and be anti-conservative (the same `#9/#14` trap the headline H2 fix
removed). `effect > 0` ⇒ the distributional arm keeps the higher factor-adjusted alpha. The bootstrap
is two-sided; the directional call is the recorded sign of `effect`. Skips (never raises) when fewer
than two shared seeds yield a usable per-seed alpha for **both** arms.

### 1.3 The driver — `campaign_attribution(records, factors, ...)`

Shaped to the per-`(arm, seed)` frozen-winner TEST records `scripts/run_campaign.py` writes (each
carrying `metrics['test_returns']` — read via the same `_test_returns` contract as
`analyze_campaign`). For each contrast `(arm_a, arm_b)` and each **factor-ladder rung** whose columns
are all present, it runs `difference_in_alpha`, then **Benjamini-Hochberg-corrects** the two-sided
p-values at `q` **across the whole secondary family** (every `contrast × rung` cell that ran).

* **Contrasts** = the three H2 contrasts (mirrored locally to avoid importing the torch-adjacent
  analysis script): `distributional > {scalar, placebo, scalar_cvar5}`.
* **The factor ladder** (`FACTOR_LADDER`, deep-research §5.10):

  | rung | factor columns | constructable today? |
  |---|---|---|
  | `capm` | `Mkt-RF` | **yes** (on disk) |
  | `ff3` | `Mkt-RF, SMB, HML` | **yes** (on disk) |
  | `carhart4` | `+ Mom` (UMD) | **yes** (on disk) |
  | `ff5` | `+ RMW, CMA` | needs a Ken-French pull |
  | `ff6` | `FF5 + Mom` | needs a Ken-French pull |
  | `ff6_bab` | `+ BAB` | needs an AQR pull |
  | `ff6_bab_qmj` | `+ QMJ` | needs an AQR pull |

  **BAB is the headline rival** ("is the edge just betting-against-beta?"); `Mom`=momentum;
  `SMB`=size-from-simplex-spreading; `QMJ`=quality. The per-factor read is the standard "**rival
  killed if β≈0 while α survives**" table.

**Graceful degradation (the whole point — never crashes):**

* `factors=None` or `{}` → `status="skipped"`, `available=False`, `cells=[]` (synthetic-only install,
  no factor data).
* a rung's columns not all present → that **cell** is `skipped` with the missing columns named
  (so FF5/FF6/BAB/QMJ are reported skipped until pulled, not silently dropped).
* a contrast's arms have no test records → that **contrast** is skipped (a missing comparator arm is a
  credible null, never fabricated).

### 1.4 Disjoint keys — why `assert_realized_family_matches_frozen` stays green

The frozen H2 family keys on `(arm_a, arm_b, metric, level)`
(`scripts/analyze_campaign.assert_realized_family_matches_frozen`). This secondary's cells use
**disjoint discriminators** — `family="factor_attribution_difference_in_alpha"`, and per cell
`rung` / `factor` / `alpha_diff` / `seed` — and **never carry `metric` or `level`**
(`test_result_keys_are_disjoint_from_frozen_h2_family`). It therefore **cannot** be mistaken for a
frozen-family member, the m=6 is never mutated, and the fail-loud guard never fires on it
(deep-research Part 2, "amendment-free additions"; §5.10 "one declared family each, corrected
internally"). This is an **appendix/robustness** family — report it separately; do **not** merge it
into the headline conjunction.

---

## 2. Factor-data sources — on disk vs needs-pull

### 2.1 On disk today (`data/raw/`, daily decimals, 2005-01-03 → 2026-04-30)

> **⚠ Split-C coverage gap (2026-07-02).** The sealed test leg now ends **2026-06-30** (Split C, R73)
> but the two on-disk French CSVs end **2026-04-30** (verified first-hand) — May–Jun 2026 is uncovered.
> The 2026-07-02 rebuild refreshed the FRED series to the cutoff (`refresh_fred_2026.py`) but **not**
> the French factors: refresh both French files to ≥ 2026-06-30 (percent→decimal `/100` on the fresh
> pull) before running the ladder on the full Split-C test leg, else the tail of the window is
> forward-filled/misaligned rather than priced.

| column(s) | file | loaded by |
|---|---|---|
| `Mkt-RF, SMB, HML, RF` | `french_F-F_Research_Data_Factors_daily.csv` | `market_reference.load_ff_factors` (FF3) + `attribution.load_factor_panel` (RF) |
| `Mom` (UMD) | `french_F-F_Momentum_Factor_daily.csv` | `attribution.load_factor_panel` |

`load_factor_panel(dates)` aligns every column to the panel's own session axis via the existing
no-future-leak forward-fill (`market_reference._aligned_series`), returning
`{"factors": {...}, "available": bool, "present": [...], "needs_pull": [...], "rf": ndarray|None}`.
**Verified on the real 2018–2025 (pre-Split-C) window:** `present = [HML, Mkt-RF, Mom, SMB]`, `rf`
present → **CAPM, FF3, Carhart-4 estimable today**; `needs_pull = [RMW, CMA, BAB, QMJ]`. (Re-verify on
the 2020–2026H1 Split-C leg after the French refresh above.)

* **Source / format (Ken-French Data Library):**
  <https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html> — daily CSV inside a
  zip; header rows precede a `Date,Mkt-RF,SMB,HML,RF` (research factors) / `Date,Mom` (momentum)
  block; **values are in PERCENT** in the raw French download (e.g. `0.53` = 0.53%). **The repo's
  on-disk copies are already converted to DECIMALS** (confirmed: `Mkt-RF` rows are `±0.01`-scale, and
  `market_reference.load_ff_factors` treats them as decimals). Any *fresh* pull must divide the
  French percent columns by 100 before use.
* **RF caveat.** The Ken-French daily `RF` is piecewise-constant within each month; the campaign's
  canonical risk-free is **FRED `DGS3MO`** via `market_reference.load_risk_free_daily` (ADR-038, R20).
  The `rf` returned by `load_factor_panel` is the French `RF` (handy when pricing alongside French
  factors); for consistency with the headline, **pass FRED `DGS3MO` as `risk_free`** to
  `campaign_attribution` (see the wiring spec). The excess-return LHS choice is reported, not frozen.

### 2.2 Needs a pull (reported `needs_pull`; rungs skip until added)

* **FF5 `RMW`, `CMA`** — Ken-French *Fama/French 5 Factors (2x3) [Daily]*:
  `https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip`
  (daily CSV, percent; header `Date,Mkt-RF,SMB,HML,RMW,CMA,RF`). Adding this unlocks `ff5` + `ff6`.
* **AQR `BAB`** — Frazzini & Pedersen (2014), *Betting Against Beta: Equity Factors, Daily*:
  <https://www.aqr.com/Insights/Datasets/Betting-Against-Beta-Equity-Factors-Daily> (xlsx; use the
  **USA** long/short column; the workbook has metadata header rows). Unlocks `ff6_bab`.
* **AQR `QMJ`** — Asness, Frazzini & Pedersen (2019), *Quality Minus Junk: Factors, Daily*:
  <https://www.aqr.com/Insights/Datasets/Quality-Minus-Junk-Factors-Daily> (xlsx; **USA** column).
  Unlocks `ff6_bab_qmj`. **QMJ is not constructable from the anonymised panel** (needs fundamentals).

**How to add them without touching this module's signature:** pass a
`factor_provider(dates) -> {name: series}` to `load_factor_panel` (its columns are merged on top and
override), e.g. a small loader that reads the pulled FF5/AQR files, aligns them to `dates`, and
returns `{"RMW": ..., "CMA": ..., "BAB": ..., "QMJ": ...}`. The ladder then runs the higher rungs
automatically. Pulled-file conventions to honour: French percent→decimal `/100`; AQR daily decimals
already; align with the **same forward-fill / no-future-leak** contract as the on-disk columns.

### 2.3 Citations (for `paper/refs.bib` / `docs/REFERENCES.md`)

* **Newey, W. K., & West, K. D. (1987).** A Simple, Positive Semi-Definite, Heteroskedasticity and
  Autocorrelation Consistent Covariance Matrix. *Econometrica* 55(3), 703-708. — the HAC estimator.
* **Newey, W. K., & West, K. D. (1994).** Automatic Lag Selection in Covariance Matrix Estimation.
  *Review of Economic Studies* 61(4), 631-653. — the `4(T/100)^{2/9}` automatic truncation-lag rule.
* **Fama, E. F., & French, K. R. (1993).** Common risk factors in the returns on stocks and bonds.
  *JFE* 33(1), 3-56. — FF3 (`Mkt-RF, SMB, HML`).
* **Carhart, M. M. (1997).** On Persistence in Mutual Fund Performance. *Journal of Finance* 52(1),
  57-82. — the momentum (`Mom`/UMD) factor → Carhart-4.
* **Fama, E. F., & French, K. R. (2015).** A five-factor asset pricing model. *JFE* 116(1), 1-22. —
  FF5 (`RMW, CMA`).
* **Frazzini, A., & Pedersen, L. H. (2014).** Betting against beta. *JFE* 111(1), 1-25. — `BAB`.
* **Asness, C. S., Frazzini, A., & Pedersen, L. H. (2019).** Quality minus junk. *Review of
  Accounting Studies* 24(1), 34-112 (DOI 10.1007/s11142-018-9470-2). — `QMJ`. **Venue is *Review of
  Accounting Studies*, NOT Review of Finance** (deep-research citation-ledger correction).

---

## 3. EXACT `analyze_campaign.py` wiring spec (for the maintainer to apply)

> This module is **standalone and tested**. Per the task scope it does **not** edit
> `scripts/analyze_campaign.py`. The wiring below is the spec to apply when you want the secondary in
> the campaign report. All hooks already exist in `analyze()` / `write_report()`; the additions are
> purely additive (no frozen path changes).

**Where.** `analyze_campaign.analyze(...)` already loads `records = load_campaign_records(root)` and,
on the production path, resolves `panel`, `cfg`, `test_window` (so `panel.dates[start:end]` is the
exact test-leg session axis — the same axis `benchmark_floor` uses). Add the secondary right after
the `h2` block, guarded so a records-only / synthetic install still runs.

**1) Import (top of the panel-dependent block in `analyze`, lazy like the others):**

```python
from src.inference.attribution import campaign_attribution, load_factor_panel
```

**2) Compute the secondary inside `analyze(...)`, only when the panel/test_window are present**
(so factors can be aligned to the real test dates), reusing the FRED rf already loaded for R20:

```python
# Door-C secondary: factor attribution / difference-in-alpha (SEPARATE declared family; NOT m=6).
if panel is not None and test_window is not None:
    try:
        win_dates = np.asarray(panel.dates)[int(test_window[0]):int(test_window[1])]
        fp = load_factor_panel(win_dates)                    # on-disk FF3 + Mom; needs_pull reported
        # Use the headline FRED DGS3MO rf for the excess-return LHS (consistency with H2 R20).
        from src.data.market_reference import load_risk_free_daily
        rf = load_risk_free_daily(win_dates)
        out["attribution"] = campaign_attribution(
            records,
            fp["factors"] if fp["available"] else None,
            risk_free=(rf.daily if rf.available else None),
            q=q_level,                                       # SAME BH level object as H2 (its OWN family)
            n_boot=int(load_config("inference").get("sharpe_test", {}).get("n_boot", 2000)),
            rng=np.random.default_rng(0),
        )
    except Exception as exc:  # noqa: BLE001 - a reporting secondary must never break the analysis
        out["attribution"] = {"status": "error", "error": str(exc)}
```

Notes:
* `campaign_attribution` reads `metrics['test_returns']` per `(arm, seed)` itself — pass the **full**
  `records` list (it filters by arm/seed internally), exactly like `collect_family_pvalues`.
* `q_level` is the `multiplicity.q` already read in `analyze`. The attribution BH runs **inside its
  own family** (disjoint keys) — this is *not* double-correcting the m=6.
* On a records-only call (`panel is None`) the block is skipped and no attribution is reported —
  identical degradation to the floor/R20 blocks.

**3) Render in `write_report(...)`** (append after the existing fragments):

```python
from src.inference.attribution import attribution_markdown
if result.get("attribution"):
    md = md + "\n" + attribution_markdown(result["attribution"])
```

`attribution_markdown` emits a `## Factor attribution — difference-in-alpha (Door-C secondary)` table
(one row per `contrast × rung`: annualised alpha diff, two-sided across-seed p-value, `direction_ok`,
`reject_bh`, `n_seeds`, status) and lists skipped contrasts with reasons. The JSON dump in
`write_report` already serialises `result["attribution"]` via `json.dumps(..., default=str)` — no
change needed.

**4) (Optional) console line in `main()`**, mirroring the H2 print:

```python
attr = result.get("attribution") or {}
if attr.get("cells"):
    ok = [c for c in attr["cells"] if c.get("status") == "ok"]
    print(f"  attribution (diff-in-alpha, BH q={attr.get('q')}): {len(ok)} runnable cell(s); "
          f"rungs needing a pull are reported skipped")
```

**Result-shape contract** (for any downstream reader / `default=str` JSON dump):

```
result["attribution"] = {
  "status": "ok" | "skipped" | "error",
  "family": "factor_attribution_difference_in_alpha",
  "q": float, "n_family": int, "available": bool,
  "rungs": ["capm", ...],
  "cells": [ {contrast, arm_a, arm_b, rung, factor[], status,
              alpha_diff, alpha_diff_ann, pvalue, stat, ci_low, ci_high,
              direction_ok, reject_bh, n_seeds, alpha_a_iqm, alpha_b_iqm, [reason]}, ... ],
  "skipped": [ {contrast, reason}, ... ],
}
```

---

## 4. What this defends, and the honest caveats

* **Defends:** "the edge is just BAB/low-vol/size beta." If the distributional arm's `alpha_diff`
  stays positive and BH-significant up the ladder (and BAB's β is small once pulled), the edge is
  **not** a known-factor tilt. This is the difference-in-alpha the red-team demanded.
* **Caveat — BAB/QMJ require a pull.** Until the AQR files are added, the `ff6_bab` / `ff6_bab_qmj`
  rungs report `skipped`; the BAB-specific rebuttal is only *complete* after that pull. CAPM/FF3/
  Carhart-4 already remove market, size, value, and **momentum** — momentum is the most common
  "it's just a known factor" alternative and is covered today.
* **Caveat — alpha is a point estimate per seed; power is finite.** The across-seed bootstrap carries
  the right variance, but with `n_seeds≈30` and a daily test leg the difference-in-alpha has the same
  finite-power ceiling as the headline; report the n_seeds and CI alongside every cell.
* **Not a treatment.** This re-prices the *dependent variable*; it does not change the search, the
  agent, or the reward. It is Door C, reported as a robustness appendix — never the headline number.
```
