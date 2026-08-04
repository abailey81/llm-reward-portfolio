# Excess-return Sharpe and the benchmark ladder on the sealed test window

Analysis-time only. Nothing was re-run, nothing under `src|scripts|config|prompts` was touched, and
`scripts/analyze_campaign.py` was never executed (its `WeightPolicy` shim and `_BENCHMARK_NAMES`
constant were imported as a module, so no analysis pass ran).

Read of the archive: **2026-08-04**, `outputs/campaign_cluster_run4`. The campaign is live, so the
per-arm seed counts below are a snapshot and they move. The main pass read **12,365** records;
several arms already exceeded the counts cached in `per_seed.json` earlier the same evening (for
example `test_leg_sonnet_5/distributional` 546 → 555). A second verification pass roughly twenty
minutes later read **12,431** records, and `test_leg_glm_5_2/distributional` had gone from empty to
2 records in that gap. Every number below belongs to the 12,365-record read unless it says otherwise.

---

## 0. Window, panel and rate — the identical axis everything below uses

| item | value | source |
|---|---|---|
| gold suffix | `univ5` (the FROZEN headline panel) | `src.data.loaders.gold_suffix()` |
| panel shape | T = 5,406 sessions, N = 30 assets | `load_gold_panel(phase="development", end="2026-06-30", verify_checksum=True, validate=True)` |
| panel identity | `returns_panel` sha256 `7cf5d988…6446d3` | manifest-verified on load; identical to the hash in `campaign_summary_leg_gemini_2_5_flash.json` |
| test window | `[3835, 5406)` = **1,571 sessions**, 2020-03-30 → 2026-06-30 | `scripts/run_campaign.resolve_windows` |
| every archived `test_returns` | length **1,571**, all 12,365 records, zero exceptions | measured |
| risk-free | FRED `DGS3MO`, mean **2.9876 %** annual over the window | `src.data.market_reference.load_risk_free_daily` |
| rf coverage | last real observation 2026-06-30, `n_extrapolated = 0` | no session carries a forward-filled constant |
| rf per session | mean 1.1592e-4, sd 8.506e-5 (decimal) | `(1 + DGS3MO/100)**(1/252) − 1` |
| transaction cost | **10 bps** on half-L1-drifted turnover, `proportional_turnover` | `config/environment.yaml: costs.headline_bps` |

The traded universe is the **development-phase point-in-time top-30 cohort selected at 2005-01-03**,
held fixed through the sealed window (`run_campaign.py` documents this as the accepted composition
bias). That fixed cohort is what makes "equal-weight buy-and-hold of the same universe" a
well-defined series rather than an approximation.

---

## (c) Exact conventions and field names used

**Raw Sharpe.** `src.inference.bootstrap.sharpe_ratio(v)` = `mean(v) / std(v, ddof=0) * sqrt(252)`,
applied to `record["metrics"]["test_returns"]` — the realised per-step **net** (after-cost) return
vector. Recomputing it reproduced the archived `metrics["test_sharpe"]` **bit-exactly on all 12,365
records** (max absolute difference 0.0). Confirms the archived field is raw, not excess. A separate
pass counted field presence explicitly: across 12,431 records **no** record is missing
`test_returns`, `test_sharpe`, `test_cvar05`, `test_gross` or `test_turnover`, so "all records"
means all of them and not merely all that carried the field.

**Excess Sharpe.** The registered R20 path, taken verbatim from
`scripts/analyze_campaign.py::collect_family_pvalues._sharpe_score` (lines 1533–1540) and used by
`h2_rf_robustness` (`h2_sharpe_rf_robustness`, line 1989):

```
rf = load_risk_free_daily(panel.dates[test_start:test_end]).daily     # 1,571 decimals
excess_sharpe = sharpe_ratio(test_returns[:m] - rf[:m])               # ELEMENT-WISE, m = min(len)
```

The rate is subtracted as a **vector, element by element**, not as its mean — that is the convention
the codebase registered, and it feeds both the numerator and the denominator. Annualisation is the
codebase's `sqrt(252)` with `TRADING_DAYS_PER_YEAR = 252`; the daily-rate conversion is the geometric
`(1 + DGS3MO/100)**(1/252) − 1` from `market_reference.load_risk_free_daily`. Nothing was invented.

**CVaR-5%.** `src.inference.bootstrap.cvar(v, 0.05)` = mean of the worst `ceil(0.05·T)` = 79 of the
1,571 **raw** (not excess) returns. The registered path deliberately leaves the CVaR leg on raw
returns (`h2_sharpe_rf_robustness` docstring: *"the CVaR leg, a RAW-loss tail measure, stays on raw
returns"*), so that convention is kept here. Recomputation matched the archived
`metrics["test_cvar05"]` bit-exactly on all 12,365 records. An excess-return CVaR was also computed
for the benchmarks and differs by 7.26e-5 to 8.14e-5 — the rate *averaged over the 79 tail days*,
which is below the window-wide mean rf of 1.1592e-4 because the worst days cluster in the
near-zero-rate 2020-21 stretch.

**Per-arm reduction.** Two statistics are given for every cell: the **IQM**
(`src.inference.bootstrap.iqm`, the rliable interquartile mean the H2 family uses as its per-seed
reduction) and the **plain mean ± sample sd (ddof=1)**. Every number carries its `n`.

**Loader.** Every record was read one at a time through the canonical `src.io.results.load_run`.
Peak RSS **204 MB**, 12,365 records in 115 s.

**Windows.** Resolved by `scripts/run_campaign.resolve_windows` from `config/inference.yaml: splits`
with the frozen `embargo_trading_days = 21`. The effective purge is `max(embargo, lookback) = 60`,
so the test window is `(3835, 5406)` at either value.

**Seeds.** One value per run directory. A duplicate-seed scan over all 63 arm directories found
**none**, so the directory count and the seed count coincide and the column heading "n seeds" is
literal.

---

## (a) Line × arm — raw Sharpe, excess Sharpe, CVaR-5%

**63** `(line, arm)` directories exist across the twelve test lines; **59 are populated** and **4 are
empty** at this read (`test/cma_es`, `test_leg_glm_5_2/distributional`, `test_leg_glm_5_2/scalar`,
`test_leg_nemotron_3_super/scalar_cvar5`), shown below with `—`. The core `test` line currently carries no
`distributional` or `scalar` arm directory at all; the confirmatory Opus line's own H2 pair is not
yet in the archive, and that is stated rather than worked around.

| line | arm | n seeds | raw Sharpe (IQM) | raw Sharpe (mean ± sd) | EXCESS Sharpe (IQM) | EXCESS Sharpe (mean ± sd) | CVaR-5% (IQM) | CVaR-5% (mean ± sd) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `test` | `baseline_differential_downside_ratio` | 30 | -0.1784 | -0.1710 ± 0.2076 | -0.3503 | -0.3423 ± 0.2080 | -0.024502 | -0.024662 ± 0.000984 |
| `test` | `baseline_differential_sharpe` | 30 | -0.2122 | -0.1973 ± 0.3560 | -0.3791 | -0.3664 ± 0.3559 | -0.025195 | -0.025178 ± 0.001363 |
| `test` | `baseline_log_growth` | 30 | -0.2104 | -0.2009 ± 0.2966 | -0.3562 | -0.3477 ± 0.2965 | -0.029381 | -0.029237 ± 0.001639 |
| `test` | `baseline_mean_variance_utility` | 30 | -0.3186 | -0.3003 ± 0.2447 | -0.4644 | -0.4454 ± 0.2438 | -0.029705 | -0.029588 ± 0.001876 |
| `test` | `baseline_raw_return` | 30 | -0.2886 | -0.3064 ± 0.2585 | -0.4343 | -0.4526 ± 0.2593 | -0.029097 | -0.029112 ± 0.001784 |
| `test` | `baseline_return_minus_cvar` | 30 | -0.3639 | -0.3249 ± 0.2894 | -0.5296 | -0.4904 ± 0.2926 | -0.025598 | -0.025830 ± 0.001324 |
| `test` | `baseline_return_minus_downside` | 30 | -0.2123 | -0.2024 ± 0.2694 | -0.3642 | -0.3556 ± 0.2704 | -0.027568 | -0.027675 ± 0.001736 |
| `test` | `baseline_return_minus_drawdown` | 30 | -0.2188 | -0.1992 ± 0.1856 | -0.4021 | -0.3815 ± 0.1886 | -0.023094 | -0.023040 ± 0.001009 |
| `test` | `baseline_return_minus_turnover` | 30 | +1.1535 | +1.1609 ± 0.1143 | +0.9332 | +0.9413 ± 0.1224 | -0.018274 | -0.018691 ± 0.002535 |
| `test` | `baseline_return_minus_variance` | 30 | -0.2189 | -0.2152 ± 0.2470 | -0.3633 | -0.3620 ± 0.2465 | -0.029214 | -0.029206 ± 0.001918 |
| `test` | `baseline_volatility_scaled_return` | 30 | -0.2360 | -0.2213 ± 0.2497 | -0.3752 | -0.3608 ± 0.2508 | -0.030457 | -0.030387 ± 0.001961 |
| `test` | `cma_es` | 0 | — | — | — | — | — | — |
| `test` | `placebo` | 30 | +1.1376 | +1.1454 ± 0.1426 | +0.9110 | +0.9224 ± 0.1476 | -0.018019 | -0.018342 ± 0.002145 |
| `test` | `placebo_shuffled` | 30 | +1.0943 | +1.1047 ± 0.1386 | +0.8824 | +0.8925 ± 0.1475 | -0.019342 | -0.019217 ± 0.001798 |
| `test` | `random_search` | 30 | +0.8935 | +0.9203 ± 0.2021 | +0.6374 | +0.6579 ± 0.2113 | -0.015465 | -0.015451 ± 0.001820 |
| `test` | `scalar_cvar5` | 30 | +1.1390 | +1.1558 ± 0.1752 | +0.9233 | +0.9371 ± 0.1908 | -0.018504 | -0.018656 ± 0.002229 |
| `test_h3_singleshot` | `distributional` | 568 | +1.2005 | +1.1999 ± 0.1028 | +0.9891 | +0.9874 ± 0.1075 | -0.019249 | -0.019282 ± 0.001963 |
| `test_leg_gemini_2_5_flash` | `distributional` | 568 | -0.2005 | -0.2125 ± 0.2881 | -0.3467 | -0.3588 ± 0.2903 | -0.029255 | -0.029228 ± 0.001741 |
| `test_leg_gemini_2_5_flash` | `placebo` | 568 | +0.8778 | +0.8617 ± 0.2161 | +0.6870 | +0.6704 ± 0.2203 | -0.021240 | -0.021504 ± 0.002919 |
| `test_leg_gemini_2_5_flash` | `placebo_shuffled` | 568 | +0.5717 | +0.5596 ± 0.2859 | +0.3753 | +0.3632 ± 0.2891 | -0.021137 | -0.021189 ± 0.001796 |
| `test_leg_gemini_2_5_flash` | `scalar` | 568 | +0.8059 | +0.7888 ± 0.2178 | +0.6107 | +0.5938 ± 0.2229 | -0.021228 | -0.021269 ± 0.002116 |
| `test_leg_gemini_2_5_flash` | `scalar_cvar5` | 568 | +1.0875 | +1.0893 ± 0.1631 | +0.8549 | +0.8547 ± 0.1704 | -0.017360 | -0.017389 ± 0.001956 |
| `test_leg_gpt_5_6_luna` | `distributional` | 567 | +0.8866 | +0.8815 ± 0.1936 | +0.6705 | +0.6669 ± 0.1957 | -0.019137 | -0.019127 ± 0.002189 |
| `test_leg_gpt_5_6_luna` | `placebo` | 566 | +1.1505 | +1.1485 ± 0.1309 | +0.9483 | +0.9434 ± 0.1354 | -0.020073 | -0.020101 ± 0.002374 |
| `test_leg_gpt_5_6_luna` | `placebo_shuffled` | 567 | +1.2034 | +1.2029 ± 0.0956 | +0.9816 | +0.9810 ± 0.1014 | -0.018423 | -0.018454 ± 0.001590 |
| `test_leg_gpt_5_6_luna` | `scalar` | 566 | +1.1439 | +1.1379 ± 0.1189 | +0.9627 | +0.9563 ± 0.1181 | -0.022721 | -0.022716 ± 0.002189 |
| `test_leg_gpt_5_6_luna` | `scalar_cvar5` | 566 | +1.1604 | +1.1596 ± 0.1454 | +0.9340 | +0.9326 ± 0.1512 | -0.017862 | -0.017928 ± 0.001953 |
| `test_leg_sonnet_5` | `distributional` | 555 | +1.1126 | +1.1097 ± 0.1417 | +0.9054 | +0.9003 ± 0.1470 | -0.019537 | -0.019623 ± 0.002103 |
| `test_leg_sonnet_5` | `placebo` | 556 | +1.1522 | +1.1511 ± 0.1323 | +0.9458 | +0.9431 ± 0.1364 | -0.019566 | -0.019751 ± 0.002405 |
| `test_leg_sonnet_5` | `placebo_shuffled` | 543 | +0.1283 | +0.2207 ± 0.4505 | -0.0649 | +0.0249 ± 0.4458 | -0.021556 | -0.021594 ± 0.002135 |
| `test_leg_sonnet_5` | `scalar` | 554 | +1.1895 | +1.1895 ± 0.1099 | +0.9812 | +0.9792 ± 0.1141 | -0.019436 | -0.019506 ± 0.002070 |
| `test_leg_sonnet_5` | `scalar_cvar5` | 550 | +0.9731 | +0.9715 ± 0.1850 | +0.7077 | +0.7040 ± 0.1876 | -0.015017 | -0.015041 ± 0.001403 |
| `test_leg_qwen3_5_9b` | `distributional` | 448 | -0.2785 | -0.2785 ± 0.2398 | -0.4584 | -0.4587 ± 0.2414 | -0.023502 | -0.023598 ± 0.001337 |
| `test_leg_qwen3_5_9b` | `placebo` | 446 | +1.2256 | +1.2242 ± 0.0803 | +1.0145 | +1.0126 ± 0.0829 | -0.019345 | -0.019381 ± 0.001561 |
| `test_leg_qwen3_5_9b` | `placebo_shuffled` | 446 | +0.0760 | +0.0740 ± 0.2181 | -0.1152 | -0.1170 ± 0.2212 | -0.021988 | -0.021974 ± 0.001262 |
| `test_leg_qwen3_5_9b` | `scalar` | 446 | +0.5191 | +0.5085 ± 0.2080 | +0.3106 | +0.3008 ± 0.2093 | -0.020033 | -0.020062 ± 0.000990 |
| `test_leg_qwen3_5_9b` | `scalar_cvar5` | 446 | +1.2251 | +1.2060 ± 0.0914 | +1.0056 | +0.9870 ± 0.0903 | -0.018754 | -0.018782 ± 0.000318 |
| `test_leg_haiku_4_5` | `distributional` | 39 | +1.1750 | +1.1783 ± 0.1016 | +0.9604 | +0.9685 ± 0.1034 | -0.019506 | -0.019525 ± 0.001957 |
| `test_leg_haiku_4_5` | `placebo` | 38 | +1.2262 | +1.2219 ± 0.0980 | +1.0173 | +1.0092 ± 0.1057 | -0.019248 | -0.019300 ± 0.002025 |
| `test_leg_haiku_4_5` | `placebo_shuffled` | 35 | +1.0907 | +1.1007 ± 0.1654 | +0.8686 | +0.8774 ± 0.1711 | -0.017980 | -0.018218 ± 0.002117 |
| `test_leg_haiku_4_5` | `scalar` | 41 | +0.9614 | +0.9858 ± 0.1796 | +0.7254 | +0.7482 ± 0.1862 | -0.016925 | -0.017085 ± 0.001842 |
| `test_leg_haiku_4_5` | `scalar_cvar5` | 36 | +1.0630 | +1.0759 ± 0.1639 | +0.8537 | +0.8603 ± 0.1696 | -0.018596 | -0.018947 ± 0.002463 |
| `test_leg_qwen3_6_27b` | `distributional` | 30 | +1.1285 | +1.1161 ± 0.1754 | +0.9200 | +0.9055 ± 0.1800 | -0.019689 | -0.019628 ± 0.002679 |
| `test_leg_qwen3_6_27b` | `placebo` | 30 | +1.1629 | +1.1681 ± 0.0860 | +0.9462 | +0.9512 ± 0.0958 | -0.018848 | -0.018960 ± 0.001928 |
| `test_leg_qwen3_6_27b` | `placebo_shuffled` | 30 | +1.0105 | +1.0253 ± 0.1507 | +0.8019 | +0.8175 ± 0.1551 | -0.019860 | -0.019642 ± 0.001651 |
| `test_leg_qwen3_6_27b` | `scalar` | 30 | +1.0762 | +1.0703 ± 0.1836 | +0.8671 | +0.8661 ± 0.1884 | -0.020232 | -0.020237 ± 0.002665 |
| `test_leg_qwen3_6_27b` | `scalar_cvar5` | 30 | +1.0790 | +1.0921 ± 0.1742 | +0.8477 | +0.8536 ± 0.1908 | -0.016881 | -0.017056 ± 0.002288 |
| `test_leg_kimi_k3` | `distributional` | 12 | +1.1641 | +1.1653 ± 0.1247 | +0.9330 | +0.9438 ± 0.1384 | -0.018655 | -0.018608 ± 0.002263 |
| `test_leg_kimi_k3` | `placebo` | 30 | +1.1604 | +1.1644 ± 0.0921 | +0.9425 | +0.9466 ± 0.1036 | -0.018529 | -0.018820 ± 0.002007 |
| `test_leg_kimi_k3` | `placebo_shuffled` | 30 | +1.0131 | +1.0195 ± 0.1249 | +0.8009 | +0.8051 ± 0.1279 | -0.019250 | -0.019302 ± 0.001996 |
| `test_leg_kimi_k3` | `scalar` | 12 | +1.2125 | +1.1604 ± 0.2103 | +0.9666 | +0.9359 ± 0.2162 | -0.018085 | -0.018658 ± 0.003310 |
| `test_leg_kimi_k3` | `scalar_cvar5` | 30 | +0.9428 | +0.9543 ± 0.1545 | +0.7331 | +0.7484 ± 0.1635 | -0.020088 | -0.020095 ± 0.002559 |
| `test_leg_deepseek_v4_pro` | `placebo` | 30 | +1.1493 | +1.1555 ± 0.1030 | +0.9325 | +0.9452 ± 0.1083 | -0.019497 | -0.019477 ± 0.002115 |
| `test_leg_deepseek_v4_pro` | `placebo_shuffled` | 22 | +1.1060 | +1.1159 ± 0.1140 | +0.8921 | +0.9047 ± 0.1185 | -0.019351 | -0.019376 ± 0.001786 |
| `test_leg_deepseek_v4_pro` | `scalar_cvar5` | 30 | +1.1616 | +1.1701 ± 0.1097 | +0.9507 | +0.9589 ± 0.1147 | -0.019189 | -0.019358 ± 0.002135 |
| `test_leg_glm_5_2` | `distributional` | 0 | — | — | — | — | — | — |
| `test_leg_glm_5_2` | `placebo` | 30 | +1.1610 | +1.1534 ± 0.0902 | +0.9491 | +0.9433 ± 0.0979 | -0.019582 | -0.019550 ± 0.002237 |
| `test_leg_glm_5_2` | `placebo_shuffled` | 30 | +0.8403 | +0.7864 ± 0.2872 | +0.6298 | +0.5823 ± 0.2859 | -0.020186 | -0.020267 ± 0.002168 |
| `test_leg_glm_5_2` | `scalar` | 0 | — | — | — | — | — | — |
| `test_leg_glm_5_2` | `scalar_cvar5` | 30 | +1.2110 | +1.2135 ± 0.0898 | +1.0005 | +1.0022 ± 0.0979 | -0.019515 | -0.019466 ± 0.002358 |
| `test_leg_nemotron_3_super` | `placebo` | 30 | +1.1699 | +1.1712 ± 0.1012 | +0.9548 | +0.9548 ± 0.1162 | -0.019044 | -0.019038 ± 0.002732 |
| `test_leg_nemotron_3_super` | `placebo_shuffled` | 30 | +0.7417 | +0.7130 ± 0.2285 | +0.5476 | +0.5159 ± 0.2348 | -0.020971 | -0.021024 ± 0.001712 |
| `test_leg_nemotron_3_super` | `scalar_cvar5` | 0 | — | — | — | — | — | — |

Measured across the 59 populated cells, subtracting the rate costs between **0.1391 and 0.2654
Sharpe units** (min `test/baseline_volatility_scaled_return`, max `test_leg_sonnet_5/scalar_cvar5`),
median **0.2097**. The penalty is `mean(rf)·sqrt(252)/sd`, so it is larger for the lower-volatility
cells. On a representative record
(`test_leg_qwen3_6_27b/distributional-s0`) the drop is 0.2100, against the closed-form prediction
`mean(rf)·sqrt(252)/sd(v)` = 0.2097 — the small residual is the covariance term the element-wise
subtraction carries and the mean-subtraction would not.

---

## (b) Benchmark rows — identical 1,571 sessions, identical conventions

Universe: the **same frozen headline panel** (`univ5`, manifest-hash-verified) and the **same fixed
30-name development-phase PIT cohort** the agents trade. The first two rows are rolled through the
**identical `PortfolioEnv`** at the **same 10 bps** cost, so they pay transaction costs exactly as
the agents do. Row 1 uses the `WeightPolicy` shim from `analyze_campaign.py`, the machinery the
registered `benchmark_floor` uses; row 2 uses a small never-rebalance policy written for this report
(see the note below) against the same env. The last two rows are index reference series and carry
**no transaction cost**; that asymmetry is stated rather than adjusted away.

| benchmark | n steps | raw Sharpe | EXCESS Sharpe | CVaR-5% (raw) | ann. return % | ann. vol % | cumulative % | mean turnover | ann. cost % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `equal_weight` (1/N, daily rebalanced, costed env) | 1571 | **+1.2741** | **+1.0617** | -0.019350 | +17.54 | 13.77 | +181.21 | 0.004808 | 0.1211 |
| equal-weight **BUY-AND-HOLD** (1/N at entry, never rebalanced) | 1571 | **+1.2585** | **+1.0553** | -0.020265 | +18.10 | 14.38 | +189.62 | 0.000021 | 0.0005 |
| `market_ew` (full-universe equal weight; **no** costs) | 1571 | +1.1659 | +1.0185 | -0.027239 | +23.13 | 19.84 | +274.06 | — | — |
| `.SPXTR` S&P 500 total return (cap-weighted; **no** costs) | 1571 | +1.1305 | +0.9642 | -0.025501 | +19.87 | 17.57 | +213.28 | — | — |
| risk-free `DGS3MO` itself | 1571 | — | — | — | +2.92 | — | +19.97 | — | — |

Notes on each row.

- **`equal_weight`** is the registered DeMiguel 1/N floor, one of the nine names in
  `analyze_campaign._BENCHMARK_NAMES` and in `config/preregistration.yaml: benchmarks`. It rebalances
  to 1/N every session and pays 0.1211 %/yr in turnover cost.
- **Buy-and-hold** is *not* in the codebase. `strategies.spy_buy_and_hold` is documented as an exact
  duplicate of `equal_weight` ("this function is not, and never was, SPY"), so a genuine
  never-rebalanced series had to be constructed for this report: 1/N on the 30 risky names at entry,
  then the target is the env's own drifted book every subsequent session, which makes realised
  turnover zero after entry. Mean turnover 2.05e-5 is exactly the one-off entry trade amortised over
  1,571 sessions.
- **`market_ew`** is `data/gold/market_proxy_univ5.parquet`, the equal-weight return of the full
  963-name survivorship-free PIT universe — a broader object than the 30-name sleeve, reported
  because it is the market reference already on disk. `n_extrapolated = 0`.
- **`.SPXTR`** is the cap-weighted S&P 500 total-return series from `data/raw/rf_spxtr.csv` +
  `rf_spxtr_x26.csv`, loaded by `market_reference.load_spx_total_return`. `n_extrapolated = 0`.
- The **Fama–French factors** are on disk and loadable, but they are factor returns for attribution
  rather than an investable benchmark line, so no Sharpe row is offered for them.

**One discrepancy found and explained.** `strategies.spy_buy_and_hold`'s docstring records
`market_ew` Sharpe **+1.1656** and `.SPXTR` **+1.1302** on this same 1,571-session axis. The values
here are **+1.1659** and **+1.1305**. The gap is the standard-deviation convention: with `ddof=1` the
two series give 1.1656 and 1.1302, with `ddof=0` they give 1.1659 and 1.1305. The codebase's own
`sharpe_ratio` uses `ddof=0`, and it is the function that produced every archived `test_sharpe`, so
`ddof=0` is used throughout this report and the docstring figures are the ddof=1 variant.

---

## (d) Where the agents sit relative to the benchmarks

Comparing the excess-Sharpe IQM of each populated cell against each benchmark's excess Sharpe:

| benchmark | excess Sharpe | populated cells above it |
|---|---:|---:|
| `equal_weight` (costed) | +1.0617 | **0 of 59** |
| equal-weight buy-and-hold (costed) | +1.0553 | **0 of 59** |
| `market_ew` (uncosted) | +1.0185 | **0 of 59** |
| `.SPXTR` (uncosted) | +0.9642 | **8 of 59** |

The highest agent cell on excess Sharpe is `test_leg_haiku_4_5/placebo` at **+1.0173** (n = 38),
followed by `test_leg_qwen3_5_9b/placebo` +1.0145 (n = 446) and
`test_leg_qwen3_5_9b/scalar_cvar5` +1.0056 (n = 446). The median across the 59 populated cells is
**+0.8549**. The gap to the costed equal-weight row runs from **−0.0444** (the smallest, at the top
cell) through a median of **−0.2068** to **−1.5913** (`test/baseline_return_minus_cvar`).

**Plain statement, on this measure and this window: no populated `(line, arm)` cell reaches the
equal-weight benchmark on excess Sharpe — every one of the 59 sits below it, and that holds against
both cost-charged benchmark rows as well as against the two uncosted ones.** Eight cells sit above
the uncosted cap-weighted `.SPXTR` line. The same ordering holds on raw Sharpe: the costed 1/N row
is +1.2741 and the highest agent cell is +1.2262.

On the tail measure the counts run the other way. Against `equal_weight`'s CVaR-5% of −0.019350,
**25 of 59** cells have a shallower (less negative) tail; against the uncosted `market_ew`
(−0.027239) **52 of 59** do. The cells with the shallowest tails
(`test_leg_sonnet_5/scalar_cvar5` at −0.015017, `test/random_search` at −0.015465) sit at +0.7077
and +0.6374 on excess Sharpe, well below the benchmarks. The two benchmark groups realise different
annualised volatilities (13.77 % costed 1/N, 19.84 % `market_ew`); per-cell volatilities were not
computed, so nothing is claimed about what drives the two orderings apart.

**How to read these counts.** They compare per-cell **IQM point estimates** against benchmark values
that are single deterministic paths, i.e. `n = 1` with no interval of their own. Each cell's `n` and
sample sd are in table (a); the counts themselves carry no uncertainty statement. The narrowest gap
is the top cell at −0.0444 against a per-seed sd of 0.1057 on n = 38. No test was run, no p-value
computed, no hypothesis touched, and no verdict is offered.

---

## Task 3 — transaction costs ARE charged on the sealed test path

Confirmed first-hand, four independent ways.

1. **Config.** `config/environment.yaml` lines 28–33: `costs.headline_bps: 10`,
   `model: proportional_turnover`, cost = c · turnover with turnover = 0.5·L1(w − w̃), w̃ the drifted
   previous book.
2. **Env code.** `src/env/portfolio_env.py:168` sets `self.cost = float(costs_cfg["headline_bps"]) * 1e-4`
   = 1e-3, and lines 369–374 compute `turnover = 0.5*|w − w_held|₁`, `cost = self.cost * turnover`,
   `port_ret = gross - cost`. The recorded `test_returns` are `info["port_ret"]`, i.e. **net**.
3. **No override on the test path.** `src/orchestration/test_leg.py:309` calls `make_env_builder(...)`
   without `cost_bps`, so the default `None` falls through to the config headline. The only caller
   that ever passes an override is `scripts/cost_sweep.py`, which is a separate re-pricing tool.
4. **Measured in the archive.** The identity `test_returns == test_gross − 1e-3 · test_turnover`
   holds with **maximum absolute deviation exactly 0.0** on two samples: 495 records taken at a
   uniform 1-in-25 stride through the read order, and separately one record drawn from **each
   populated arm** (60 of them by the second pass, versus 59 at the main read — see the header note
   on live drift). The per-arm sample exists because the stride alone cannot guarantee coverage of a
   12-record arm. Independently, the analytic uncosted 1/N gross return over this window is
   17.6593 %/yr against the env's net 17.5382 %/yr — a difference of 0.1211 pp, matching the
   reported annualised cost of 0.1211 % to four decimals.

**Cost level: 10 bps per unit of half-L1-drifted turnover, charged on both the agents and the two
env-rolled benchmark rows.** The two index rows (`market_ew`, `.SPXTR`) are uncosted by
construction and are labelled as such.

---

## What could not be computed, stated plainly

- **The core `test` line has no `distributional` or `scalar` arm directory**, so the confirmatory
  Opus H2 pair does not appear in the table. It is absent from the archive, not omitted here.
- **Four `(line, arm)` directories are empty** at the main read: `test/cma_es`,
  `test_leg_glm_5_2/distributional`, `test_leg_glm_5_2/scalar`,
  `test_leg_nemotron_3_super/scalar_cvar5`. Three are simply pending on a live campaign, and
  `test_leg_glm_5_2/distributional` had already filled with 2 records twenty minutes later. The
  fourth is different and should not be filed as pending:
  `outputs/campaign_cluster_run4/ARM_CRASH_leg_nemotron_3_super.json` records
  `scalar_cvar5: "RuntimeError: 240 consecutive pull failures over 3.0 h — VPN/ssh down too long"`,
  with the note that the pass stopped before C2 to protect CRN pairing. That cell is crashed and
  resumable, not merely not-yet-run.
- **A costed cap-weighted market benchmark does not exist.** `.SPXTR` is an index level series with
  no weights, so it cannot be rolled through `PortfolioEnv`; its Sharpe is therefore not
  cost-comparable with the agents' and is not adjusted to pretend otherwise.
- **Seed counts are unequal across arms and lines** (12 to 568). Cells are not pooled and no
  cross-cell comparison is weighted; each row carries its own `n`.
- The remaining **eight** registered allocators (`mean_variance`, `risk_parity`, `hrp`,
  `minimum_variance`, `maximum_diversification`, `inverse_volatility`, `cross_sectional_momentum`,
  `min_cvar`) were not rolled — the task scoped the ladder to equal weight plus available market
  references. They are computable from the same script if wanted.

## Artefacts

| file | contents |
|---|---|
| `excess_sharpe.py` | streaming per-record raw + excess Sharpe + CVaR (12,365 records, 204 MB peak) |
| `excess_per_seed.json` | every per-seed value, plus the verification counters |
| `bench_ladder.py` / `bench_ladder.json` | the benchmark rollouts and series |
| `verify.py` | the four independent cross-checks reported above |
| `verify2.py` | second pass: rf-penalty range, per-arm cost identity, field-presence and duplicate-seed scans |
| `make_report.py` | table assembly and the positional counts |

## Audit trail

A fresh read-only auditor re-derived every load-bearing number from the repo independently (its own
panel load, its own window resolution, a from-scratch numpy re-implementation of the env cost
accounting) and confirmed the conventions, the window identity, the cost claim and the benchmark
fairness. It reproduced all four benchmark rows and all of section (d)'s counts. It also found ten
minor defects in the first draft of this report — a wrong rf-penalty range, a "three cost-charged
comparisons" overstatement, an off-by-one allocator count, one causal sentence that violated the
describe-only instruction, a mis-attributed shim, a crashed cell filed as pending, two sampling
claims broader than the instrument, an imprecise CVaR-difference gloss, and a config key read by the
wrong name. Every one is corrected above, and the two that were assertions rather than measurements
were re-run as measurements (`verify2.py`).
