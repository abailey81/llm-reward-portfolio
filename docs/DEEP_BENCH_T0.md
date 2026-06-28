# DEEP_BENCH_T0 — exhaustive scrutiny of the classical-allocator benchmark floor (Tier-0)

**Status:** read-only deep-audit dossier (no code edited). Prepared as a portfolio-construction /
asset-allocation reviewer making the Tier-0 floor **bulletproof, fair, and defensible** for a PDF-only
MSc grade (supervisor Dr Okhrati; citations checked). **Date:** 2026-06-25. **Repo:**
`llm-reward-portfolio`. **Verifier env:** `.venv\Scripts\python.exe`.

**Scope.** The eight published allocators that form the floor any LLM-designed reward winner must clear:
`equal_weight` (1/N), `mean_variance`, `risk_parity`, `hrp`, `minimum_variance`,
`maximum_diversification`, `inverse_volatility`, `cross_sectional_momentum`
(`src/baselines/strategies.py::STRATEGY_CANON` → `_BENCHMARK_NAMES`), the gate logic
(`scripts/analyze_campaign.py::benchmark_floor`, L1264–1431; `WeightPolicy`, L1157–1230), the env that
prices them (`src/env/portfolio_env.py`), the Deflated-Sharpe statistic
(`src/inference/deflated_sharpe.py`), PREREGISTRATION §9 (R19) / §10, and `docs/CAMPAIGN_benchmarks.md`.

**Everything below was verified first-hand** — the code was read line-by-line and the allocators were RUN
on the real gold panel (`data/gold/returns_panel_univ3.parquet`, 5283×953, survivorship-free PIT). No
claim here is inferred from documentation alone.

---

## 0. Bottom line up front (BLUF)

The floor is **already strong, correctly implemented, and unusually honest** (the de-duped 1/N, the
delisted-name masking, the constrained long-only QPs, the median-per-seed DSR). The eight allocators all
compute valid simplex weights and rank sanely on the real panel. **There is no correctness defect.**

But "fair + bulletproof + defensible" is a higher bar than "correct," and under that bar there are **four
real, citable threats** the dissertation must either fix or disclose, ranked by severity:

| # | Threat | Severity | Direction of bias | Fixable pre-freeze? |
|---|---|---|---|---|
| **T0-A** | **Daily re-estimation imposes 1.7–3.1%/yr turnover cost on the parametric/structure allocators** (vs ~0.16%/yr for 1/N), measured on the real panel. This is far above the practitioner 0.5–2%/yr band and is NOT how these allocators are run in the literature (monthly). | **HIGH** | Handicaps the *sophisticated* allocators → makes the floor artificially **lower** than a fair monthly-rebalanced floor → **flatters the winner** | **Yes** (disclose + add a monthly/no-cost robustness floor) |
| **T0-B** | **Asymmetric Deflated-Sharpe deflation:** winner DSR is deflated by N=30 trials, each benchmark by N=1. On an identical return path the benchmark scores DSR≈0.89 while the winner scores ≈0.20 — a ~4.5× handicap. | **HIGH** | Handicaps the **winner** → makes the floor **harder** to clear → conservative *for a "clears the floor" claim*, but a "fails the floor" outcome is then partly a deflation artifact | Already implemented + defensible; needs **explicit framing**, not a fix |
| **T0-C** | **Estimation window = 60 trading days for a 30-asset covariance** (T/N = 2). The sample covariance is near-singular; `mean_variance`/`minimum_variance` concentrate to effective-N ≈ 5–7 (verified). This is exactly DeMiguel's "estimation error cripples optimization" regime — and it weakens the parametric allocators *relative to 1/N*. | **MEDIUM** | Weakens parametric allocators → 1/N harder, sophisticated allocators easier-to-beat → mixed; mostly **flatters the winner vs the parametric arms** | Partly (lengthen window / shrinkage is already used for `mean_variance`; disclose) |
| **T0-D** | **"30 seeds" is meaningless for deterministic allocators.** The per-seed-DSR-for-the-winner vs single-path-DSR-for-the-benchmark comparison is the *correct* like-for-like, but it must be stated that benchmarks are run **once** (they have no training RNG) and the comparison is median-of-30-winner-paths vs one-benchmark-path. | **MEDIUM** | Neutral if framed; a naive reader assumes symmetry | Framing only |

None of these is fatal. T0-A and T0-B are the two that a hostile examiner will press hardest, and both
have a **clean, defensible answer** that this document supplies (§4, §5). The single highest-value
pre-freeze action is **adding a monthly-rebalanced (or zero-cost) floor as a robustness row** so the
headline "clears the classical floor" is not vulnerable to "you just taxed the benchmarks to death."

---

## 1. Is the comparison fair? — the env, costs, rebalancing, constraint (T0 mechanics)

**Verified: the allocators are rolled through the byte-identical `PortfolioEnv` as the LLM winner.**
`benchmark_floor` (L1338–1351) constructs, for each allocator, a `WeightPolicy` shim and a fresh
`PortfolioEnv(panel, cfg, _passthrough, start, end)` over the **same** `test_window`, then calls the
**same** `rollout_port_returns`. Concretely, every benchmark inherits, with no asymmetry:

- **the same 30-asset PIT universe** (`panel.N`), the same anonymised survivorship-free returns;
- **the same transaction-cost model** — `cost = headline_bps(10) × 1e-4 × turnover`, with
  `turnover = 0.5·‖w − w̃‖₁` on the **half-L1-DRIFTED** prior weights (`portfolio_env.step`, L265–286).
  The cost is charged *after* the action, identically for agent and benchmark;
- **the same long-only simplex projection** — the `WeightPolicy._action_for` (L1201–1219) inverts the
  frozen `softmax` projection (returns `log w`, since `softmax(log w) = w`), so the env reconstructs the
  allocator's intended weights **exactly**; for `l1_normalize_of_clipped` it returns `w` directly;
- **the same test window** `[start, end)` (the campaign's resolved 2018–2025 leg), and the same lagged
  observation contract (the env's `_obs` packs `returns[t−60:t]` as the leading block, which the shim
  reshapes back to the strategy's input window — `WeightPolicy._window`, L1196–1199). **No look-ahead:**
  the strategy only ever sees strictly-past returns, identical to the agent.

This part is **genuinely fair and is the floor's strongest feature.** A benchmark that holds 1/N pays the
genuine cost-charged 1/N return on the same leg the winner is measured on — there is no "the benchmark got
a free pass on costs" attack surface. **Verdict: the *environment* is symmetric. ✓**

The fairness problems are NOT in the env; they are in **how the deterministic allocators are *driven*
through it** (daily re-estimation → T0-A) and **how the resulting paths are *scored*** (asymmetric
deflation → T0-B). Those are §4 and §5.

### 1.1 The deterministic-allocator / "30 seeds" question (T0-D)

The allocators are **pure functions of the returns window** — `equal_weight` ignores the window entirely;
the rest read only `returns`. They carry **no training RNG, no network init, no stochastic policy.** So
"30 seeds" simply **does not apply** to them: each benchmark produces **one** deterministic test path, run
**once**. The code reflects this correctly — `benchmark_floor` rolls each benchmark a single time and
reports a single-path DSR (L1349).

The gate (L1366–1376) then does the **right** thing for the winner: it takes the winner's **per-seed**
test paths (`winner_test_returns_per_seed`), computes a DSR for each seed (deflated by `winner_n_trials`),
and gates the **median-per-seed** DSR against the best benchmark's single-path DSR. The docstring (L1361–
1365) is explicit that averaging the seed paths *first* would shrink variance ~√S and inflate the DSR —
the same anti-conservatism the H2 amendment (R16) removed — so median-per-seed is deliberate and correct.

**This is the like-for-like comparison: one realised winner path (the median seed) vs one realised
benchmark path.** It is valid. The only requirement is **disclosure** — the write-up must state that the
benchmarks are deterministic (run once), and that the "30 seeds" applies to the *winner's training
stochasticity* only, reduced to a representative single realisation via the median. A reader who assumes
"both sides got 30 seeds" is wrong; the document must pre-empt that. **Verdict: valid, needs one sentence
of framing. ✓ (with disclosure)**

---

## 2. Verification table — each allocator: computes? sane? fair? (run first-hand)

Run on `data/gold/returns_panel_univ3.parquet`, a 60-row (lookback) test-era window, 30 live columns
(finite & σ>1e-6). **T/N = 2.0** — the estimation-stress regime (see T0-C). HHI = Σwᵢ² (concentration);
eff-N = 1/HHI.

| Allocator | Canonical reference (verified) | Computes? | Simplex valid (Σw=1, w≥0)? | Sanity on real panel (verified this run) |
|---|---|---|---|---|
| `equal_weight` | DeMiguel, Garlappi & Uppal (2009), *RFS* 22(5):1915–1953 | ✅ | ✅ Σ=1.0000 | exactly uniform: all 1/30, HHI 0.033, eff-N **30.0**. The floor. |
| `mean_variance` (Ledoit-Wolf + long-only tangency QP) | Markowitz (1952); Ledoit & Wolf (2004) | ✅ | ✅ Σ=1.0000 | max 0.339, **10 names**, eff-N **5.6** — concentrates (the estimation-error signature, T0-C); shrinkage applied, long-only max-Sharpe QP (not Σ⁻¹μ projection) |
| `risk_parity` (convex ERC, Spinu/Maillard) | Maillard, Roncalli & Teïletche (2010); Spinu (2013) | ✅ | ✅ Σ=1.0000 | **all 30 names**, eff-N **25.3**, spread 0.04–0.09; risk-only, stays diversified — sits between min-var and 1/N exactly as Maillard et al. predict |
| `hrp` | López de Prado (2016), *JPM* 42(4):59–69 | ✅ | ✅ Σ=1.0000 | all 30 names, eff-N **20.0**; clustering→quasi-diag→bisection; no covariance inversion → robust at T/N=2 |
| `minimum_variance` (constrained long-only GMV) | Clarke, de Silva & Thorley (2011); Markowitz (1952) | ✅ | ✅ Σ=1.0000 | max 0.201, **15 names**, eff-N **7.1** — concentrated & beta-driven (matches Clarke et al. "~12% of universe"); long-only QP |
| `maximum_diversification` (GMV-of-correlation, de-scaled) | Choueifaty & Coignard (2008), *JPM* 35(1):40–51 | ✅ | ✅ Σ=1.0000 | max 0.135, **19 names**, eff-N **13.3** |
| `inverse_volatility` (naive RP) | Leote de Carvalho et al. (2012) | ✅ | ✅ Σ=1.0000 | all 30 names, eff-N **27.1**; wᵢ∝1/σᵢ, dead names excluded |
| `cross_sectional_momentum` (top-tertile, long-only) | Jegadeesh & Titman (1993), *JF* 48(1):65–91 | ✅ | ✅ Σ=1.0000 | **10 names** @ 0.10 (top tertile of 30 live), eff-N 10.0 |

**Cross-allocator structural sanity (independently re-verified this audit, and by `tests/test_baselines.py`):**
GMV variance < 1/N variance; max-div ratio > 1/N ratio; ERC equalises risk contributions to <1e-3; **no
collapse to <3 names** (the removed Euclidean-projection footgun); delisted (σ≈0) names get ~0 weight; HRP
finite on zero-variance columns. All hold.

**`spy_buy_and_hold`** is in `STRATEGY_CANON` but is an **honest exact 1/N duplicate** (the anonymised
panel has no index/caps) and is **correctly excluded** from `_BENCHMARK_NAMES` (R19) to avoid
double-counting the floor. This is good practice — many projects would have silently shipped it as a fake
"market benchmark." ✓

---

## 3. Are these the RIGHT eight, correctly implemented? — completeness & robustness

**The set is canonical and well-chosen.** It spans the four standard families a portfolio-construction
examiner expects: (i) **naive** (1/N); (ii) **mean-variance** (Markowitz + shrinkage, GMV); (iii)
**risk-based** (ERC, inverse-vol, max-diversification); (iv) **hierarchical/ML** (HRP); plus one **active
signal** (momentum). Each is the citation-anchored representative of its family. **This is a broader,
fairer floor than the DeMiguel paper's own suite for the risk-only families** (DeMiguel 2009 is
mean-variance-centric; this suite adds the modern risk-parity/HRP line that the 2009 paper predates).

**Implementation quality is high and the engineering is *defensive in the right places*:**

- The long-only optima are solved as **constrained convex QPs** (`_long_only_min_variance`,
  `_long_only_max_sharpe`), not by the naive "project the unconstrained Σ⁻¹μ/Σ⁻¹1 onto the simplex" trick
  that **collapses to a single asset** — the code documents this footgun was found and removed
  (L132–135, 149–153). This is exactly the Michaud "estimation-error-maximizer" failure mode being
  pre-empted. Strong.
- Every covariance/vol allocator runs on a `_live_mask` sub-panel (σ>1e-10) so the `liquidate_to_cash`
  zero-fill of delisted names cannot capture ~100% weight via 1/σ→∞ (L138–146). Correct and necessary on
  a survivorship-free panel.
- `mean_variance` uses **Ledoit-Wolf shrinkage** (the only family-appropriate estimation-error control in
  the suite), which is the right call at T/N=2 (Ledoit & Wolf 2004: shrinkage guarantees invertibility and
  pulls in error-laden extreme coefficients when T is small relative to N).

**Missing canonical allocators — assessed, none is a defect:**

- **Black-Litterman (1992):** correctly **omitted** — it requires equilibrium market-cap weights + a
  views/forecast layer; the anonymised, caps-free panel cannot support it. Note it as fundamentals-gated.
- **Jagannathan-Ma (2003)** no-short min-var and **DeMiguel-Garlappi-Nogales-Uppal (2009)**
  norm-constrained portfolios: these are *exactly* the strategies the literature shows **can** beat 1/N
  (norm constraint regularizes estimation error, *Management Science* 55(5):798–812). They are **already
  implicitly present**: the long-only constraint in `_long_only_min_variance` IS the Jagannathan-Ma
  no-short constraint, and is the strongest single estimation-error control. So the toughest published
  family is represented. ✓
- **Equal-risk-budgeting variants, CVaR/min-CDaR optimal portfolios:** out of scope — CVaR-optimal would
  blur the line with the *reward* baselines (`REWARD_CANON`), which is the right separation.
- **A genuine market benchmark (SPX-TR / cap-weighted):** the one real gap, but it is a **gated data**
  addition (needs a non-anonymised pull) and is honestly documented as such. `market_reference` already
  prices a full-universe EW proxy + the winner's β/α/IR additively (outside the same-universe gate). This
  is an acceptable, disclosed limitation — and the headline claim is comparative ("distributional vs
  scalar"), not "beats the market," so it does not undercut the thesis.

**Overfitting of the allocators themselves (hidden hyperparameters)? — VERIFIED: none.** Grepping
`strategies.py`, **no allocator reads any `cfg` field.** `cfg` is accepted for signature uniformity and
**ignored entirely**: `mean_variance` does not read a risk-aversion λ (it solves the parameter-free
long-only tangency, GMV-fallback); the lookback is fixed by the env (60), not tuned per allocator; HRP's
linkage method (`single`), momentum's tertile (`//3`), and the shrinkage intensity (Ledoit-Wolf's
*analytically optimal* δ̂, not a tuned knob) are the standard textbook defaults, frozen in code. **There is
no free parameter to overfit, and none was tuned on the test leg.** This is a genuine fairness strength:
the floor cannot be accused of being a strawman tuned to lose. The *only* embedded constants are
numerical guards (1e-8 jitter, 1e-12 floors) that do not affect rankings. ✓

---

## 4. THREAT T0-A (HIGH) — daily re-estimation taxes the sophisticated allocators

**This is the most important finding in this document.** I measured the realised **daily-rebalancing
turnover** of each allocator on a ~200-step real test slice (each day: re-estimate on the trailing 60-day
window, compute new target weights, drift the prior weights by realised returns, pay
`0.5·‖w−w̃‖₁` turnover). Annualised cost at the headline 10 bps:

| Allocator | mean daily turnover | annualised cost @ 10 bps |
|---|---|---|
| `equal_weight` | 0.0062 | **0.16 %/yr** |
| `inverse_volatility` | 0.0089 | 0.23 %/yr |
| `risk_parity` | 0.0140 | 0.35 %/yr |
| `maximum_diversification` | 0.0671 | 1.69 %/yr |
| `minimum_variance` | 0.0721 | 1.82 %/yr |
| `cross_sectional_momentum` | 0.0784 | 1.97 %/yr |
| `hrp` | 0.0865 | 2.18 %/yr |
| `mean_variance` | 0.1226 | **3.09 %/yr** |

**The problem.** 1/N is essentially **costless** (it only trades to correct drift, 0.16%/yr), while the
covariance-driven allocators pay **10–20× more** because they **re-estimate the covariance every single
day** and chase the resulting weight jitter. `mean_variance` at **3.09%/yr** is *above* the entire
practitioner cost band, and at the 50 bps stress grid point it would bleed ~15%/yr — annihilating it.

**Why this is a fairness threat, not just a fact.** In the founding literature these allocators are run
**monthly, on monthly data** (DeMiguel-Garlappi-Uppal 2009 explicitly use monthly rebalancing with a
120-month window; the turnover/cost literature confirms 0.5–2%/yr is the *expected* band for *sensibly
rebalanced* risk allocators). **Daily re-estimation is not how anyone runs a Markowitz or HRP book** — it
is an artifact of plugging a daily-frequency RL env's per-step cadence into an estimator designed for
low-frequency rebalancing. The covariance barely moves day-to-day, so the daily weight changes are
**mostly estimation noise being traded against at full cost.**

**Direction of the bias: this *flatters the winner*.** By taxing the sophisticated allocators 10–20×
harder than a fair monthly implementation would, the floor those allocators set is **artificially
depressed**. A hostile examiner's attack is precise and damaging: *"Your winner doesn't beat real
risk-parity; it beats a deliberately over-traded, cost-crippled caricature of risk-parity. Run them
monthly and the floor rises."* The 1/N floor itself is unaffected (it barely trades), so **the DeMiguel
floor is safe** — but the *seven other* allocators' contribution to "best benchmark" is compromised, and
since the gate uses `max` over all eight, if the winner is being compared against a cost-crippled
`mean_variance` as "best benchmark," the comparison is soft.

**Note the subtlety that partially mitigates:** because the gate takes the **best** benchmark DSR, and the
low-turnover allocators (1/N, inverse-vol, risk-parity at 0.16–0.35%/yr) are *not* cost-crippled, the
"best benchmark" will very likely be one of the **cheap, diversified risk allocators**, not the
cost-bled `mean_variance`. So the floor is probably set by a *fairly-costed* allocator anyway. But this
must be **shown**, not assumed — the write-up needs the per-benchmark cost/turnover table to prove the
binding benchmark is not a cost artifact.

**Literature anchor.** DeMiguel-Garlappi-Uppal (2009) *RFS* 22(5):1915–1953 (monthly rebalancing, 120-mo
window); the turnover-cost band (0.5–2%/yr) — *Frontiers in Applied Math & Stats* (2025) "On transaction
costs in minimum-risk portfolios"; risk-parity turnover 5–18% per rebalance — arXiv:2106.09055.

---

## 5. THREAT T0-B (HIGH) — the asymmetric Deflated-Sharpe deflation

**Verified numerically.** On an *identical* return path (~Sharpe 0.8 annualised, 1900 steps):

- benchmark-style DSR (`n_trials = 1`) = **0.89**
- winner-style DSR (`n_trials = 30`) = **0.20**

The mechanism: `expected_max_sharpe(var, 1) = 0.0` exactly (the N=1 branch, L118), so a benchmark's DSR is
just PSR-vs-0 — "what is the probability this single un-searched strategy's true Sharpe > 0." The winner's
DSR is PSR vs `E[max Sharpe over 30 trials]` (≈0.21 per-period units here), a much higher bar. **The same
realised performance scores ~4.5× higher for a benchmark than for the winner.**

**Is this correct? — Yes, and it is the *theoretically right* asymmetry.** The winner was **selected as the
best of a 30-candidate search**, so its observed Sharpe is an order statistic and must be deflated by the
search multiplicity (Bailey & López de Prado 2014 — this is the entire point of the Deflated Sharpe
Ratio). The benchmarks were **not searched** — each is one pre-specified published rule — so N=1 is
correct for them. The code comment (L1358–1360) states this precisely. **This is the conservative,
defensible choice.**

**But it has a sharp two-edged framing consequence the dissertation MUST handle explicitly:**

- **If the winner CLEARS the floor** under this asymmetry, the claim is **very strong** — "even after
  deflating the winner for 30× search multiplicity while giving the benchmarks the full undeflated benefit
  of the doubt, the winner still wins." This is the **strongest defensible framing** and the document
  recommends leaning into it (§8).
- **If the winner FAILS the floor**, it is **not** safe to conclude "the winner is worse than the
  benchmarks" — a substantial part of the gap is the 4.5× deflation handicap, *not* realised performance.
  The honest report must then **also** show the **undeflated** (N=1 vs N=1) comparison and the raw
  Sharpe/CVaR side-by-side, so the reader can separate "lost on performance" from "lost on the
  multiplicity penalty." Hiding the undeflated comparison would be the kind of selective reporting the
  DSR machinery exists to prevent.

**Recommendation:** report **both** the deflated gate (headline, N=30 vs N=1) **and** an undeflated
companion (N=1 vs N=1, and raw Sharpe/CVaR/MaxDD) for the winner-vs-best-benchmark pair, in one table, so
the deflation's effect is transparent. Already partly present (the per-benchmark table has raw Sharpe);
the missing piece is the winner's **N=1** DSR alongside its N=30 DSR.

---

## 6. THREAT T0-C (MEDIUM) — the 60-day estimation window (T/N = 2)

The env lookback is **60 trading days** (`config/environment.yaml: state.lookback_days: 60`), and the
`WeightPolicy` feeds exactly this 60×N window to the allocators. For the parametric allocators this means
estimating a **30×30 covariance (465 free parameters) from 60 observations** — **T/N = 2**, an order of
magnitude below the textbook **T ≳ 10·N** guideline for a usable sample covariance (MOSEK Portfolio
Optimization Cookbook §4). At T/N=2 the sample covariance is **near-singular and severely ill-conditioned**;
its inverse is dominated by estimation noise.

**Verified consequence:** `mean_variance` concentrates to **eff-N ≈ 5.6** and `minimum_variance` to **≈
7.1** on the real window (§2) — the classic Michaud (1989) "estimation-error-maximizer" concentration. The
risk-only allocators that **don't invert** the covariance (HRP eff-N 20, risk-parity 25, inverse-vol 27)
stay diversified, which is *why* HRP and risk-parity exist (López de Prado 2016: HRP beats Markowitz OOS
precisely by avoiding the ill-conditioned inverse).

**Is this unfair?** It is a **double-edged** estimation regime:

- It **weakens the parametric allocators** (`mean_variance`, `minimum_variance`, `maximum_diversification`)
  — they would be stronger with a longer window. This **lowers their floor** → flatters the winner *vs
  those three arms*.
- It **strengthens 1/N relatively** — DeMiguel's core result is that short windows + estimation error make
  1/N hard to beat; the *critical* window for sample mean-variance to beat 1/N is ~3,000 months (N=25) /
  ~6,000 months (N=50). At 60 *days* we are astronomically below that, so **1/N is at its hardest here**,
  which makes the floor's binding constraint (1/N or a cheap risk allocator) **genuinely tough** — good
  for credibility.

**Crucial fairness point — symmetry with the agent:** the LLM agent **also** sees only the 60-day window
(same `_obs`), so neither side gets a longer estimation history. The window is a **property of the shared
env**, applied identically. So T0-C is *not* an asymmetry between winner and benchmark; it is a statement
about *which* benchmarks are strong. The defensible position: the 60-day window is the **frozen env
contract** (the agent's information set), and running the allocators on the *same* information set is the
**fair** choice — giving the allocators a 10-year covariance the agent never sees would be the *unfair*
one. **Disclose it; do not "fix" it by giving the benchmarks privileged data.**

The one mitigation worth offering as a robustness check: report the parametric allocators at a **longer
estimation window (e.g. 252 days)** as a *separate, clearly-labelled "best-case benchmark"* row — to show
the floor does not rise above the winner even when the parametric allocators are given their fairest shot.
This pre-empts "you starved Markowitz of data." (`mean_variance` already uses Ledoit-Wolf shrinkage, the
correct small-T control, so it is not maximally starved.)

**Literature anchor.** DeMiguel-Garlappi-Uppal (2009) critical-window result; Michaud (1989) *FAJ*
45(1):31–42 (error maximization); Ledoit & Wolf (2004) *JPM* 30(4):110–119 (shrinkage for small T/N);
Jobson & Korkie (1981) (sample MVO underperforms 1/N OOS); T≳10N rule — MOSEK Cookbook §4.

---

## 7. Secondary / minor observations (LOW severity — verified, mostly non-issues)

- **Momentum re-formed daily on a 60-day window.** `cross_sectional_momentum` re-ranks the top tertile
  every day on the trailing 60-day cumulative return. Jegadeesh-Titman (1993) use **3–12 month formation
  with monthly holding and a short skip** (1 week in the original; the 1-month skip is the later FF
  convention). The 60-day (~3-month) window is the **short end** of standard formation, there is **no skip**
  (so it eats some short-term reversal), and daily re-formation drives the 1.97%/yr turnover in T0-A. This
  is a *defensible* design (it is the env's native cadence), but the write-up should label it
  "daily-rebalanced 3-month momentum, no skip" rather than imply the canonical J-T spec. **Not a defect —
  a labelling precision point.** It is also the allocator least likely to be the binding "best benchmark,"
  so the impact on the gate is small.
- **`WeightPolicy` 1/N fallback on degenerate windows** (L1209–1210, 1226–1229). If a strategy raises or
  returns non-finite/short weights on a pathological window, the shim substitutes uniform 1/N. On the real
  panel this **never fires** for the live-masked windows (verified: all eight return finite simplex weights
  every step). It is a correct safety net, but note it means a *failing* allocator silently degrades to the
  floor rather than crashing — which is the right behaviour (it cannot make a benchmark *spuriously strong*,
  only fall back to 1/N). ✓
- **CVaR/MaxDD reported but not gated.** `benchmark_floor` reports each benchmark's CVaR(α=0.05) and MaxDD
  but the **gate is DSR-only** (L1377–1387). Given the thesis is tail-aware, consider *reporting* (not
  gating) the winner-vs-best-benchmark **tail** comparison (CVaR, MaxDD) alongside the DSR gate, so a
  reader sees the floor is cleared on the risk dimension the contribution is about, not only on
  Sharpe-derived DSR. This is additive reporting, fully consistent with the frozen gate.
- **`market_reference` is wrapped in a bare `except Exception` (L1428).** Correct (a reporting reference
  must never break the gate), and it degrades to `None` on synthetic installs. No issue.
- **No allocator uses the `cfg` risk-aversion / lookback knobs** (re-stated from §3): a *strength* (no
  overfitting surface), but the module docstring (L24) advertises "cfg (risk aversion, shrinkage flags,
  lookback)" which is **stale** — `cfg` is unused. A one-line docstring correction would prevent a reviewer
  thinking a hidden λ is in play. (Docstring-only; no behavioural impact.)

---

## 8. The strongest defensible "clears the classical floor" framing

When the campaign runs and the winner clears the floor, frame it in this exact order — each clause
pre-empts an examiner attack:

> **"The LLM-designed winner clears a floor of eight published allocators — including the
> DeMiguel-Garlappi-Uppal (2009) 1/N benchmark that ~14 optimizing models failed to consistently beat —
> evaluated through the *identical* costed, long-only, survivorship-free PIT environment on the same
> sealed 2018–2025 test leg.** The gate is deliberately conservative against the winner on two axes: (i)
> the winner's Deflated Sharpe is penalised for its full 30-candidate search multiplicity, while each
> benchmark is credited at N=1 (an ~4.5× DSR handicap on the winner for identical realised performance,
> §5); and (ii) the winner is reduced to its *median* per-seed path (no variance-shrinking seed-averaging,
> R16). The binding benchmark is a **fairly-costed, diversified risk allocator** (1/N / risk-parity /
> inverse-vol, turnover 0.16–0.35%/yr), **not** a cost-crippled artifact — confirmed by the per-benchmark
> turnover table. We additionally report the floor under (a) a longer 252-day estimation window for the
> parametric allocators and (b) zero / monthly-rebalanced costing, and the winner clears it in every case.
> Estimation error at the env's 60-day window (T/N=2) is applied **symmetrically** — the agent sees the
> same information set — so the floor reflects the same data the winner had, not a privileged history. The
> one absent comparator, a cap-weighted SPX-TR market line, is fundamentals-gated by the anonymised panel
> and reported additively (β/α/IR) outside the same-universe gate; the headline claim is comparative
> (distributional vs scalar feedback), not 'beats the market.'"**

This framing is **bulletproof** because it (1) names the toughest published floor and why it is tough,
(2) *volunteers* the two handicaps that work against the winner (turning potential attacks into evidence
of conservatism), (3) proves the binding benchmark is not a cost artifact, (4) shows robustness to the
two estimation/cost choices an examiner would challenge, and (5) honestly scopes the one gated limitation.

---

## 9. PRIORITIZED concrete pre-freeze hardening

Ordered by value-for-effort. Items 1–2 are the ones that convert the two HIGH threats into *strengths*.

1. **[HIGH, ~1 hr, additive reporting — do this] Per-benchmark turnover/cost panel + prove the binding
   benchmark is fairly costed.** Add the realised mean-turnover and annualised-cost-at-headline column to
   the `benchmark_floor` output table (the data is already in `info['turnover']` per step — `rollout_port_
   series` already exposes it). This directly defuses T0-A: it *shows* that the "best benchmark" the winner
   must beat is a low-turnover diversified allocator (0.16–0.35%/yr), not the 3.09%/yr cost-bled
   `mean_variance`. Without this table, "you taxed the benchmarks to death" is unanswerable; with it, the
   attack collapses. **This is the single highest-value action.**

2. **[HIGH, ~1 hr, additive — do this] Report the winner's UNDEFLATED (N=1) DSR and raw
   Sharpe/CVaR/MaxDD alongside the deflated gate.** One extra column in the gate dict
   (`winner_dsr_n1 = median_per_seed deflated by N=1`). Makes T0-B fully transparent: the reader can
   separate "won/lost on performance" from "the 4.5× multiplicity penalty." Protects against a "fails the
   floor" outcome being misread as a pure-performance loss, and strengthens a "clears the floor" outcome
   (won *despite* the handicap). Pre-registration-safe (additive report, gate unchanged).

3. **[MEDIUM, ~1–2 hr, robustness row — strongly recommended] A monthly-rebalanced (or zero-cost) floor
   variant.** Re-roll the benchmarks rebalancing only every ~21 steps (hold target between rebalances) OR
   at `cost_bps=0`, as a *clearly-labelled robustness floor*. This is the literature-faithful way to run
   these allocators (DeMiguel monthly), and showing the winner clears even the *monthly, fairly-costed*
   floor closes T0-A permanently. The cost-sweep machinery (`scripts/cost_sweep.py`, `grid_bps`) already
   re-prices analytically — the zero-cost variant is nearly free; the monthly variant needs a hold-between-
   rebalances wrapper on `WeightPolicy`. **Note:** this is a *new reported floor variant*, so if the
   headline gate definition is already frozen in PREREGISTRATION §9/§10, add it as an **amendment-logged
   secondary robustness floor**, not a change to the frozen primary gate.

4. **[MEDIUM, ~1 hr, robustness — recommended] A 252-day-estimation-window "best-case parametric" row.**
   Re-run `mean_variance`/`minimum_variance`/`maximum_diversification`/`hrp` on a 252-day window (requires
   feeding the allocators a longer history than the 60-day obs — a *separate* benchmark-only rollout, not
   the agent's env) as a labelled "parametric allocators at their fairest estimation window." Pre-empts
   "you starved Markowitz." Lower priority than #3 because Ledoit-Wolf already mitigates small-T for
   `mean_variance`, and because giving benchmarks privileged data is itself debatable (frame it explicitly
   as a *generosity* check, not the headline).

5. **[LOW, additive reporting] Winner-vs-best-benchmark tail comparison (CVaR, MaxDD) reported beside the
   DSR gate.** The thesis is tail-aware; show the floor is cleared on the tail dimension, not only
   Sharpe-DSR. Data already computed per benchmark; just surface the winner's CVaR/MaxDD next to the best
   benchmark's. Reporting only — gate unchanged.

6. **[LOW, ~5 min, hygiene] Fix two stale docstrings.** (a) `strategies.py` module docstring claims `cfg`
   carries "risk aversion, shrinkage flags, lookback" — `cfg` is unused; correct it to avoid a reviewer
   inferring a hidden tunable λ. (b) Label `cross_sectional_momentum` as "daily-rebalanced ~3-month
   formation, no skip" in its docstring so it is not conflated with the canonical J-T (J,K) + skip spec.
   No behavioural change; pre-registration-safe.

7. **[LOW, documentation] State the deterministic-benchmark / "30 seeds" asymmetry in the methods text.**
   One sentence: benchmarks are deterministic (run once); "30 seeds" applies to the winner's training RNG
   only and is reduced to the median per-seed path. Closes T0-D.

**Do NOT do** (would *reduce* fairness or break the freeze): tune any allocator hyperparameter on the test
leg; give the benchmarks expected-return forecasts they don't have; drop the N=30 deflation on the winner
(it is the correct, conservative choice); silently change the frozen primary gate definition; add
Black-Litterman/forecast-based allocators the anonymised panel cannot support.

---

## 10. Literature grounding (precise, verified)

- **DeMiguel, V., Garlappi, L., & Uppal, R. (2009).** "Optimal Versus Naive Diversification: How
  Inefficient is the 1/N Portfolio Strategy?" *Review of Financial Studies* 22(5):1915–1953,
  doi:10.1093/rfs/hhm075. — **14 models, 7 datasets, none consistently beats 1/N** on Sharpe / CEQ /
  turnover; estimation error offsets the optimization gain; **critical estimation window ~3,000 months
  (N=25) / ~6,000 months (N=50)** for sample MVO to beat 1/N; **baseline window 120 months** (robustness
  60/240). Monthly rebalancing. *The 1/N floor's entire justification.*
- **Jobson, J. D., & Korkie, B. (1981).** "Putting Markowitz Theory to Work," *JPM* 7(4):70–74. — sample
  plug-in MVO performs so poorly OOS that equal-weight beats it. (Distinct from the J-K 1981 *Journal of
  Finance* Sharpe-ratio test, later corrected by Memmel 2003.)
- **Michaud, R. (1989).** "The Markowitz Optimization Enigma: Is 'Optimized' Optimal?" *FAJ* 45(1):31–42. —
  MVO as **estimation-error maximizer**; small input errors → extreme unstable weights. *Justifies the
  long-only QP and the observed `mean_variance`/`minimum_variance` concentration (eff-N 5.6 / 7.1).*
- **Kan, R., & Zhou, R. (2007).** "Optimal Portfolio Choice with Parameter Uncertainty," *JFQA*
  42(3):621–656. — parameter uncertainty breaks two-fund separation; three-fund rule adds the GMV (which
  doesn't depend on the badly-estimated mean).
- **Ledoit, O., & Wolf, M. (2004).** "Honey, I Shrunk the Sample Covariance Matrix," *JPM* 30(4):110–119. —
  Σ̂ = δF + (1−δ)S; **shrinkage guarantees invertibility and regularizes extreme coefficients when T is
  small relative to N.** *The estimation control `mean_variance` actually uses.*
- **Maillard, S., Roncalli, T., & Teïletche, J. (2010).** "The Properties of Equally Weighted Risk
  Contribution Portfolios," *JPM* 36(4):60–70. — ERC definition; **σ(min-var) ≤ σ(ERC) ≤ σ(1/N)**; needs
  only the covariance. *Matches the verified eff-N ordering (min-var 7.1 < ERC 25.3 < 1/N 30).*
- **Choueifaty, Y., & Coignard, Y. (2008).** "Toward Maximum Diversification," *JPM* 35(1):40–51. —
  Diversification Ratio = (Σwᵢσᵢ)/σ_portfolio; the MDP maximizes it; covariance-only.
- **López de Prado, M. (2016).** "Building Diversified Portfolios that Outperform Out of Sample," *JPM*
  42(4):59–69. — HRP (cluster → quasi-diagonalize → recursive bisection); **beats Markowitz/CLA and IVP
  OOS in Monte Carlo by NOT inverting the (ill-conditioned) covariance** — the exact T/N=2 regime here.
- **Clarke, R., de Silva, H., & Thorley, S. (2011).** "Minimum-Variance Portfolio Composition," *JPM*
  37(2):31–45. — long-only min-var is concentrated/beta-driven (~12% of universe). *Matches min-var's 15
  names / eff-N 7.1.*
- **Jegadeesh, N., & Titman, S. (1993).** "Returns to Buying Winners and Selling Losers," *JF*
  48(1):65–91. — cross-sectional momentum; 3–12 mo formation × 3–12 mo holding; original **1-week skip**
  (1-month skip is the later FF convention). *The 60-day, no-skip, daily-rebalanced spec is the short end —
  label precisely.*
- **DeMiguel, V., Garlappi, L., Nogales, F. J., & Uppal, R. (2009).** "A Generalized Approach to Portfolio
  Optimization: Improving Performance by Constraining Portfolio Norms," *Management Science* 55(5):798–812,
  doi:10.1287/mnsc.1080.0986. — **norm-constrained (incl. long-only) portfolios reduce estimation error and
  CAN beat 1/N.** *The long-only constraint in `_long_only_min_variance` IS this estimation control →
  the toughest published family is represented.* (Common DB miscite "*J. Management Science* 107:592–606"
  is **wrong**.)
- **Bailey, D. H., & López de Prado, M. (2014).** "The Deflated Sharpe Ratio: Correcting for Selection Bias,
  Backtest Overfitting, and Non-Normality," *Journal of Portfolio Management* 40(5):94–107. — DSR deflates
  for trial multiplicity; **N=30 for the searched winner vs N=1 for the un-searched benchmarks is the
  correct, conservative asymmetry (§5).**
- **Transaction-cost band (T0-A):** *Frontiers in Applied Mathematics & Statistics* (2025), "On transaction
  costs in minimum-risk portfolios" (cost impact 0.5–2%/yr; MVO costs > risk-parity); risk-parity turnover
  5–18%/rebalance — arXiv:2106.09055. — *Confirms the measured 1.7–3.1%/yr daily-rebalance cost is ABOVE
  the band for sensibly (monthly) rebalanced allocators.*
- **T≳10·N rule of thumb (T0-C):** MOSEK Portfolio Optimization Cookbook §4 (sample covariance singular for
  T≤N, ill-conditioned for small T/N). *T/N=2 here is an order of magnitude below the guideline.*

---

## Appendix — provenance of every claim in this document

**Code read first-hand:** `src/baselines/strategies.py` (all 8 allocators + `spy` alias + `_BENCHMARK_NAMES`
mapping; the live-mask, the long-only QPs, the HRP internals; verified **no `cfg` field is read**);
`scripts/analyze_campaign.py::{benchmark_floor L1264–1431, WeightPolicy L1157–1230, _BENCHMARK_NAMES
L1240–1249, winner_dsr L299+, analyze L1497–1597}`; `src/env/portfolio_env.py` (cost/turnover/projection
timing, 60-day lookback obs); `src/env/runner.py` (`rollout_port_returns`, `rollout_port_series`,
EnvBundle test-seal); `src/inference/deflated_sharpe.py` (PSR/DSR/`expected_max_sharpe` N=1 branch);
`config/environment.yaml` (lookback 60, headline 10 bps, softmax, grid_bps); `config/campaign.yaml` (30
seeds, 30 candidates/arm); `PREREGISTRATION.md` §9 (R19) / §10 (+ R16, R18, R20 amendments);
`tests/test_baselines.py`; `docs/CAMPAIGN_benchmarks.md`.

**First-hand execution on `data/gold/returns_panel_univ3.parquet` (5283×953):** all 8 allocators on a real
60-day, 30-live-asset test-era window (every one simplex-valid; eff-N ordering 1/N 30 > inv-vol 27 > RP 25
> HRP 20 > max-div 13 > min-var 7 > MV 5.6); **daily-rebalance turnover/cost measured** over 200 real steps
(1/N 0.16%/yr … mean_variance 3.09%/yr); **DSR asymmetry measured** (same path: benchmark N=1 DSR 0.89 vs
winner N=30 DSR 0.20; `expected_max_sharpe(·,1)=0.0` confirmed).

**Web sources (verified this audit):** DeMiguel-Garlappi-Uppal (2009) headline + critical-window + monthly
rebalancing (SSRN 1376199, RePEc, RFS); transaction-cost band (Frontiers 2025; arXiv:2106.09055);
T≳10N (MOSEK Cookbook); the full citation set in §10 cross-checked against primary venues (flagged where
only secondary corroboration was available: DeMiguel exact 3000/6000-month figures, Maillard inequality
wording, López de Prado Monte Carlo decimals — all consistent across independent sources).
