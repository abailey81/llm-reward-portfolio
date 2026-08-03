# ANALYSIS LANE — session 4 (2026-08-01, from ~11:00Z)

**Owner:** the ANALYSIS lane, session `e210234f`. Held path: `llm-reward-portfolio/docs/analysis/**`
(claimed on the bus 11:18Z). Session `0ed8c09f` still holds `docs/ANALYSIS_LANE_2026-08-01.md` and is
still LIVE, so this session writes here rather than into that file — **not a fork of any fact**: A1–A33
stay the record of record and every reference below points at them.

**Lane discipline.** Read-only over `src/ scripts/ config/ prompts/ docs/ops/ outputs/ paper/`.
**Effect-blind:** no arm-vs-arm contrast and no p-value on any hypothesis. §A38 reads baseline
(comparator) test outcomes as a data-quality check and **logs that it looked**, per the blinding rule.

**Method.** Every number below was re-derived first-hand from the archive by executing something —
walking the tree, or running the archived reward program itself. Where an existing instrument reports
the same quantity, both are shown. Every check that reports a CLEAN was shown to be capable of firing.

---

## SUMMARY — what changed in the campaign's risk picture

| # | finding | severity | owner |
|---|---|---|---|
| **A34** | The three constant `test_components` are settled: **two distinct mechanisms**, both measured. One is a policy-independent reward term; the other is a reward whose entire stateful mechanism **never once engaged in 400,000 training steps** — and that program **won its arm**. | mechanism material | writeup |
| **A35** | The D17 state-reset limit cycle has a **sub-floor half its own instrument cannot see**, and there it **inverts D17's stated consequence**: the harness rescues a permanently-broken reward into a ~9 % trickle that **passes R115**. | disclose; instrument gap | ops · writeup |
| **A36** | **R115's 0.10 floor sits exactly ON an atom** of the distribution it thresholds (0.10 = 1/10). One candidate is admitted by **14 calls in 400,000**. | fragility, disclose only | writeup |
| **A37** | The periodic class is **not arm-differential** (permutation p = 0.668) and the **core confirmatory line is 0/188 = 0.00 % [0.00, 2.00]**. | reassurance, with its interval | writeup |
| **A38** | **Two confirmatory canon units DO substitute SAFE_DEFAULT in their TEST trainings** — 5 calls each in 12,000,000 — and they are exactly the two rewards A13's scale account predicts. Immaterial, but it makes one commonly-written sentence false. | precision correction | writeup |
| **A39** | **Two panels of this lane's own primary instrument were dead**, including the whole determinism envelope. Repaired, with a 13-case falsification suite. The envelope itself is **genuinely clean**. | instrument defect, fixed | analysis |
| **A42** | **A16 SETTLED AND IMPLEMENTED.** Not a three-way disagreement — an implementation gap against a ratified spec. Decided effect-blind, timestamped `11:38:39Z`, and shipped by ops inside the window. **A42-bis records the full arc**, including my concession and its withdrawal. | resolved | ops (shipped) |
| **A47** | **Three of the five registered search-adequacy instruments did not exist.** Built, 25 falsification cases, run. **The search did NOT saturate** (sat99 ≈ n on every arm) but **was adequate** (99 % chance of a top-decile reward at 30) and shows **no K-collapse** (0.27 similarity). | mechanism + disclosure | ops (wire) · writeup |
| **A48** | **The lineage's selection budget, read first-hand.** Eureka/REvolve/DrEureka/Text2Reward all select on **1 seed per candidate**; they report on **2–5** seeds. **This study reports on 30–568.** | methodological position | writeup |
| **A41** | **R115 bound exactly twice and both times on a limit cycle.** It caught a candidate scoring **400× its arm** on a half-dead reward — a strong positive result — and on the other arm it **substituted a period-11 cycle for a period-5 one**. Its operative content in RUN 4 is a **period** threshold, not a contamination threshold. | positive result + one disclosure | writeup |
| **A40** | **D16 DISCHARGED.** All four re-runs landed on the correct Xeon 6240; **30/30 seeds, one CPU model**, verified by me from the archive at 13:47Z. **A12-bis fully closed** — no weak IUT leg. | ✅ closed | — |

**Nothing here damages a confirmatory result.** Every confirmatory-path check in this session came
back clean, and the three items that touch confirmatory data (A38, A40, and the A36 threshold) are a
precision correction, an open ops item, and a disclosure respectively.

---

## STANDING CYCLE — pass 1 (11:0x–11:2xZ)

| quantity | value | how |
|---|---|---|
| records, recursive walk | **2,376** at 11:24Z (2,370 → 2,376 during the session) | `results_cycle.py --full` |
| **reconciled three ways** | 2,337 at depth 4 (the cycle's `campaign_guards` authority, which read 2,336 at 11:00Z) **+ 32** depth-3 frozen markers **+ 2** depth-5 D18 nested duplicates **= 2,371** at the moment of the walk | probe 01 |
| tiers | frozen 32 · search 1,352 · test_core 356 · test_h3_singleshot 560 · test_leg 76 | — |
| **outcome fields** | `test_sharpe` / `test_cvar05`: **0 absent, 0 null, 0 non-finite** on all **992** test-tier records | probe 08 |
| **determinism envelope** | **16** test-tier comparison units · **0** span >1 `env_fingerprint.label` · **0** span >1 CPU model · **992/992** records on `Intel Xeon Gold 6240` | probe 07 (positive control fires) |
| seed sets, 12 core units | **2**: eleven at 30 (0–29 complete), `baseline_volatility_scaled_return` at 26 | probe 07 |
| `train_safe_call_count` | **exactly 400,000 on all 2,341** records that carry it (the other 32 are the frozen markers, which carry no R115 fields) | probe 08 |
| always-null fields | **0** | probe 08 |
| spend | $44.2626 | ops cycle log |

**Blinding log.** I observed outcome RANGES while checking finiteness — `test_sharpe` spans
(−0.910, +1.463) on test_core, (−0.305, +1.323) on test_leg, (+0.911, +1.558) on h3_singleshot.
**I looked; no inference is drawn from it and no contrast was computed.**

---

## ★★★★ A34 — THE ASSIGNED LEAD, SETTLED BY EXECUTION. Two mechanisms, not one.

**The question inherited:** `metrics.test_components.{effective_risk, vol_cluster_factor, vol_penalty}`
are constant where present — *inert by construction, or inert because something upstream never fires?*

**First, the framing was wrong and that mattered.** The handoff read these as "populated on only 22–24
of 992 test records". They are not sparse: **`test_components` is non-empty on 992/992 test records**,
carrying **45 distinct component names**, because the names are author-chosen per reward program and
each program owns one comparison unit. The right denominator is the **unit**, not the tier. All three
constants belong to two units on one report-only leg:

| component | unit | n | distinct values |
|---|---|---|---|
| `effective_risk` | `test_leg_qwen3_5_9b/placebo_shuffled` | 22 | **1** (0.013024702627623218) |
| `vol_cluster_factor` | `test_leg_qwen3_5_9b/placebo_shuffled` | 22 | **1** (exactly 1.0) |
| `vol_penalty` | `test_leg_qwen3_5_9b/placebo` | 24 | **1** (1.2355402706136254e-05) |

Their *siblings in the same records* vary across all 22/24 seeds (`convex_adjustment` 22 distinct,
`concentration_penalty` 24 distinct), so the unit is not degenerate — only these terms are.

`test_components` is the **per-component MEAN over the 1,571-step test path**
(`src/orchestration/test_leg.py:178`). A term identical across 22 independent seeds therefore has a
per-step value that does not depend on the policy at all.

### (a) `effective_risk` and `vol_penalty` — POLICY-INDEPENDENT BY CONSTRUCTION

Established by running each archived reward twice on the **same** `returns` with **different**
`weights`/`prev_weights` (probe 03):

```
placebo_shuffled-g0-c3   effective_risk   0.008104272139477096  vs  0.008104272139477096   IDENTICAL
                         convex_adjustment -0.605308005625035   vs -0.7597785821175829     varies
placebo-g3-c1            vol_penalty       9.819020191391599e-06 vs 9.819020191391599e-06  IDENTICAL
                         risk_adj_return  -0.042037387337024994 vs -0.0396654768061492     varies
```

The programs' own comments say why: `effective_risk` is *"the dispersion of absolute returns in the
current step"* and `vol_penalty` is `risk_aversion * step_vol**2` where `step_vol` is the market
cross-section's volatility. **Both are statistics of the asset panel, not of the portfolio.** Over a
fixed test window their mean is the same number for every seed — hence the constancy — and inside the
optimisation they are an **additive constant with no gradient**: the agent cannot reduce its own
"risk penalty" by acting differently.

**This is mechanism material, not a defect.** It is a clean, small, measured instance of an LLM reward
designer writing a *risk term the agent cannot influence* — a specification error invisible to any
fitness-based check, because the program runs, returns finite values, and scores normally.

### (b) `vol_cluster_factor = 1.0` — INERT BECAUSE THE UPDATE PATH IS THE CRASH PATH

The program keeps a stateful step counter and guards its volatility-clustering update behind
`if n_steps > 10:` … `else: vol_clustering_factor = 1.0`. Inside the guarded branch it computes
`prev_avg = current_sq_sum - current_sq_returns` — a **scalar minus an array** — so
`vol_clustering_factor` becomes an array and the later `if reward_state[...] < 1.2:` raises
`ValueError: truth value of an array … is ambiguous`. `safe_call` swallows it and returns
`(SAFE_DEFAULT, {}, None)` — **including the `None` state** (`src/sandbox/executor.py:828`), which
resets the program's own counter.

**Four predictions, all falsifiable, all confirmed by executing the archived program through the
repo's own AST gate and a loop mirroring `portfolio_env.step` exactly (probe 03):**

| prediction | result |
|---|---|
| failures at a fixed period | steps **11, 22, 33, 44, …**; **distinct gaps = {11}** |
| fraction → 1/11 = 0.090909 | **20/220 = 0.090909**; the archive says **36,339/400,000 = 0.0908475** |
| `vol_cluster_factor` = 1.0 on every logged step | **200 successes, 1 distinct value, 1.0** |
| **negative control** — same loop without round-tripping state | **0 failures / 220**, i.e. the detector can return a different answer |

**⇒ The component is inert because the branch that would move it is the branch that kills the call.**
And the archive corroborates it independently and exactly: **all 22 test seeds of that unit report
`train_safe_default_count = 36,339 / 400,000`, bit-identical to the search-stage value and to each
other.** A failure fraction that is invariant to the last digit across 23 independent trainings can
only be set by a deterministic reset cycle, never by data.

> **CREDIT, and it is not mine.** The limit-cycle mechanism is **D17**, established
> 2026-07-30 in `docs/ops/probe_safe_default_cycle.py`: *"period = warm-up calls + 1 … the fraction
> encodes the RESET PERIOD, not the severity."* I re-derived it from the source before reading that
> file; the repo was ahead of me, for the sixth time across four lanes. What is new is §A35.

---

## ★★★★ A35 — THE SUB-FLOOR HALF OF D17, WHERE THE HARNESS RESCUES A BROKEN REWARD THROUGH R115

**The gap, stated structurally.** `probe_safe_default_cycle.py::breaching_units()` filters
`dflt/calls >= 0.10`. Since a period-*k* cycle produces a fraction of 1/*k*, that filter enumerates
**only periods k ≤ 10**. Every longer period is below the floor and invisible to it. Verified by
running the probe: it reports exactly **17 units, lowest 11.11 %**.

**Five periodic candidates sit below the floor** (full census, probe 04 / the repaired cycle panel):

| line | arm | candidate | fraction | period | R115 |
|---|---|---|---|---|---|
| qwen3_5_9b | placebo | `placebo-g2-c2` | 0.099965 | **1/10** | **ADMITTED by 0.0035 pp** |
| **qwen3_5_9b** | **placebo_shuffled** | **`placebo_shuffled-g0-c3`** | **0.090847** | **1/11** | **ADMITTED — and it WON its arm** |
| haiku_4_5 | distributional | `distributional-g4-c2` | 0.049982 | 1/20 | ADMITTED |
| kimi_k3 | distributional | `distributional-g3-c2` | 0.004310 | 1/232 | ADMITTED |
| deepseek_v4_pro | placebo_shuffled | `placebo_shuffled-g0-c4` | 0.004032 | 1/248 | ADMITTED |

**And there the harness's effect INVERTS.** D17's stated consequence 2 is that the reset *"converts a
one-step transient into a PERMANENT 50 % failure, biasing that model's measured authoring reliability
DOWNWARD."* Running D17's own two replays (shipped = reset-on-failure, preserved = the counterfactual)
on the sub-floor set gives the mirror case:

| unit | archive | replay (shipped) | replay (state preserved) | verdict |
|---|---|---|---|---|
| `qwen3_5_9b/placebo_shuffled-g0-c3` | 9.0847 % | 8.25 % | **90.00 %** | **RESET-RESCUED → reliability biased UPWARD, R115 evaded** |
| `haiku_4_5/distributional-g4-c2` | 4.9982 % | 5.00 % | **81.00 %** | **RESET-RESCUED → biased UPWARD, R115 evaded** |
| `qwen3_5_9b/placebo-g2-c2` | 9.9965 % | 100 % | 100 % | INCONCLUSIVE — replay does not reproduce the archive |
| `kimi_k3/distributional-g3-c2` | 0.4310 % | 0 % | 0 % | INCONCLUSIVE — replay produced no failure |
| `deepseek_v4_pro/placebo_shuffled-g0-c4` | 0.4032 % | 4.84 % | 4.32 % | INCONCLUSIVE — replay does not reproduce |

**⇒ For a reward broken from step *k* onward, the state reset converts a PERMANENT failure into a
1/(k+1) trickle. At k ≥ 10 that trickle is below the R115 floor and the candidate is eligible to win.
One did.** `frozen_leg_qwen3_5_9b/placebo_shuffled-winner` = `placebo_shuffled-g0-c3`. Its H2 pair-test
ladder on that leg (22 seeds, 799,458 substituted calls) is computed from trainings in which the
program's volatility-clustering mechanism — its entire stated design idea — **never once operated**,
and the archive proves it: `vol_cluster_factor` is 1.0 on 100 % of 22 seeds × 1,571 logged steps.

**Two consequences, both disclose-only.**

1. **A wording correction ops owns.** `docs/ops/cycle.py:545` tells the operator a manifested sandbox
   gap *"reads ~50 % fallback (the state-reset limit cycle), so **R115 will have excluded it**."* That
   inference is valid for short periods and **false for long ones** — two of the five sub-floor
   members are exactly this class and R115 admitted both. Suggested wording: *"a short-period cycle
   reads ≥ 10 % and R115 excludes it; a long-period cycle reads below the floor and R115 does not."*
2. **Report-only leg (R80), so no confirmatory result is damaged** — stated plainly so the severity is
   not overstated. But the leg's own H2 numbers carry this qualification, and CH6 should say so.

> ⚠ **DO NOT CHANGE `safe_call`, `SAFE_DEFAULT`, the 1e6 bound, or R115 mid-run.** Any of them splits
> RUN 4 into two arithmetic regimes and breaks CRN pairing. Every item here is disclosure.

---

## ★★★ A36 — R115's FLOOR SITS EXACTLY ON AN ATOM OF THE STATISTIC IT THRESHOLDS

The periodic class does not produce a smooth distribution — it produces **point masses at 1/k**. The
registered floor is **0.10, which is 1/10 exactly**, so it lands *on* an atom rather than between two.
Measured (probe 05), the neighbourhood of the floor:

| fraction | period | margin to the 0.10 floor | outcome |
|---|---|---|---|
| 0.111110 | 1/9 | **+1.1110 pp** | EXCLUDED |
| **0.099965** | **1/10** | **−0.0035 pp** | **ADMITTED** |
| 0.090847 | 1/11 | −0.9153 pp | ADMITTED (and won its arm) |

**The period-10 candidate is admitted by fourteen calls out of 400,000** — the deficit from an exact
1/10 caused by episode-boundary truncation. Nothing else in the whole non-zero distribution lies within
1 pp of the floor: the bands are [0, 0.005) → 32, [0.005, 0.05) → 13, [0.05, 0.09) → 4,
[0.09, 0.0999) → 1, [0.0999, 0.1001) → **1**, [0.1001, 0.20) → 3, [0.20, 1.01] → 14.

**Consequence, stated without inflation.** *In fact* nothing turns on it: `placebo-g2-c2` did **not**
win its arm, so no selected object depended on the coincidence. But a threshold placed exactly on a
point mass of its own statistic is a **fragile linchpin** — had that candidate topped its arm, its
eligibility would have been decided by a rounding artefact of episode length. This is precisely the
class the non-fragile-backbone rule exists to surface, and it is far better volunteered by us than
found by a referee. **→ WRITE-UP: an Appendix-B sensitivity line. Never a mid-run change.**

---

## ★★★ A37 — THE PERIODIC CLASS IS NOT ARM-DIFFERENTIAL, AND THE CORE LINE IS CLEAN

Identification would be threatened if the harness's failure semantics bit unequally across arms.

| arm | periodic / candidates | rate (Wilson 95 %) |
|---|---|---|
| distributional | 5/307 | 1.63 % [0.70, 3.76] |
| scalar | 4/285 | 1.40 % [0.55, 3.55] |
| placebo | 2/248 | 0.81 % [0.22, 2.90] |
| scalar_cvar5 | 2/224 | 0.89 % [0.25, 3.20] |
| placebo_shuffled | 5/217 | 2.30 % [0.99, 5.28] |
| **pooled** | **18/1,281** | **1.41 %** |

**χ² = 2.443; Monte-Carlo permutation p = 0.668 over 200,000 draws.** All five intervals overlap.
**No evidence of arm-differentiality; the guard cannot manufacture a between-arm effect.**

**By line — and this is the number that matters most:**

| line | periodic / candidates | rate (Wilson 95 %) |
|---|---|---|
| qwen3_5_9b | 5/21 | 23.81 % [10.63, 45.09] |
| qwen3_6_27b | 5/117 | 4.27 % [1.84, 9.62] |
| nemotron_3_super | 2/97 | 2.06 % [0.57, 7.21] |
| deepseek_v4_pro | 2/120 | 1.67 % [0.46, 5.87] |
| haiku_4_5 | 2/130 | 1.54 % [0.42, 5.44] |
| glm_5_2 | 1/112 | 0.89 % [0.16, 4.88] |
| kimi_k3 | 1/128 | 0.78 % [0.14, 4.29] |
| **core confirmatory (Opus)** | **0/188** | **0.00 % [0.00, 2.00]** |
| h3_singleshot (node N3) | 0/30 | 0.00 % [0.00, 11.35] |
| gemini_2_5_flash · gpt_5_6_luna · sonnet_5 | 0/127, 0/143, 0/135 | 0.00 % |

The concentration on `qwen3_5_9b` is directionally consistent with A25's capability gradient (84.2 %
reject rate) but its denominator is only 21 accepted candidates, so the interval is wide — **a
consistent observation, not an independent finding.**

---

## ★★★ A38 — TWO CONFIRMATORY CANON UNITS *DO* SUBSTITUTE SAFE_DEFAULT IN THEIR TEST TRAININGS

**Nobody had looked.** R115 is a **search-stage** eligibility rule, but every test seed retrains for
400,000 steps under the selected reward and every test record carries its own counters. Sweeping all
16 test-tier units (probe 09 / the new cycle panel):

| unit | seeds with any substitution | total substituted calls | of |
|---|---|---|---|
| `test/baseline_differential_downside_ratio` | **4/30** | **5** | 12,000,000 |
| `test/baseline_differential_sharpe` | **5/30** | **5** | 12,000,000 |
| `test_leg_qwen3_5_9b/placebo_shuffled` | 22/22 | 799,458 | 8,800,000 |
| the other 13 units, incl. all of `h3_singleshot` (560) and `random_search` | 0 | **0** | — |

**The mechanism is the one already registered, confirmed by a third independent instrument.** Ranking
the twelve core units by median `raw_rms_max`:

| canon unit | median `raw_rms_max` | PopArt engages | substituted calls |
|---|---|---|---|
| `differential_downside_ratio` | **3,101.4** | yes | **5** |
| `differential_sharpe` | **2,382.9** | yes | **5** |
| `return_minus_drawdown` | 2.03 | yes | **0** |
| the nine others (0.022 – 0.917) | — | no | **0** |

Only the two rewards with a **running-scale denominator** ever reach the 1e6 contract bound — R41's
`unbounded_magnitude` class and A13's reward-SCALE account, now evidenced on the **hand-written canon**
rather than on LLM code. Note `return_minus_drawdown` engages PopArt yet never breaches, so the
discriminating quantity is the **tail of the reward magnitude**, not PopArt engagement — exactly what
the scale account predicts and the functional-form account does not.

**QC check, and the blinding log.** *(I read baseline test outcomes. No contrast, no p-value.)* Five
substituted calls in 12,000,000 predicts no visible effect, and there is none: the affected seeds rank
**11, 17, 21, 25** of 30 and **1, 8, 20, 21, 30** of 30 by within-unit `test_sharpe` — spread across
the distribution, not clustered.

**⇒ The precision correction, which is the whole point of this section.** The true statements are
*"**zero R115 breaches** on the confirmatory line"* and *"zero periodic limit cycles on the core line
(0/188)"*. The statement *"no confirmatory training ever used SAFE_DEFAULT"* is **false** — ten calls
across two canon units did. The distinction costs nothing to state and a marker can check it.
**→ WRITE-UP: use the precise form; it is also the more interesting one, because it arrives with its
mechanism attached.**

---

## ★★★ A39 — TWO PANELS OF THIS LANE'S OWN PRIMARY INSTRUMENT WERE DEAD. Repaired, with falsification.

`docs/analysis/results_cycle.py` was handed over as the standing results cycle. Two of its five
mandated computations were not computing.

**(1) The determinism envelope — the entire panel — could never report anything.**
`panel_homogeneity` read `r.get("env_fingerprint")`, but `r` is the **flattened** record and
`env_fingerprint` is a **dict** (`{env_json_sha256, label}`), which `flatten()` expands to
`env_fingerprint.label` / `env_fingerprint.env_json_sha256`. The lookup returned `None` on every
record. Measured before the fix, on the live archive:

```
panel_homogeneity over 2373 records ->  units seen: 0   split_fingerprint: {}   device_mix: {}
```

**Because the panel prints only when it finds something, `units = 0` read as "every unit is
homogeneous".** This is the **third** time this tool has committed the exact error it exists to
detect — after reading `val_fitness` on the wrong tier and globbing at a fixed depth.

**(2) `panel_sanity` computed `missing` and `main()` discarded it.** An outcome field that is *absent*
is invisible to every other check: it is not non-finite (that needs a value) and it never enters the
degeneracy grouping. Currently `missing = 0`, so nothing was being hidden today — **stated in that
direction deliberately; overstating a risk is as inaccurate as understating one.**

**(3) The arm-differential alarm compared point estimates.** The rule was `max(rate) > 2 × min(rate)`.
Applied to the periodic sub-class it declared **"ARM-DIFFERENTIAL, INVESTIGATE"** where the permutation
test returns p = 0.668. That is CLAUDE.md's scope-clause consequence 1 — *comparing a point estimate
against nothing is itself a defect* — committed by the alarm meant to protect identification.

**Repairs, all in `docs/analysis/results_cycle.py` (analysis-owned; nothing else touched):**
key corrected to `env_fingerprint.label` · a **fail-loud guard** so `units == 0` now shouts instead of
staying silent · `missing` printed · the alarm rewritten to fire only when the extreme arms' **Wilson
intervals are disjoint** · two new panels earning their place (the periodic census on **both** sides of
the R115 floor, and substitution inside the test trainings) · **a `--selftest` with 13 falsifying
cases.**

**And the selftest was itself a false green at first.** Its fixture was keyed on the very constant it
was testing, so it passed with the pre-fix key still in place. Rebuilt from the **real nested schema**
through `flatten()`, it now discriminates in both directions:

```
correct key `env_fingerprint.label`        -> ALL 13 PASS
pre-fix key `env_fingerprint`              -> FAILS "sees the unit at all" + "FIRES on a device split"
wrong key   `...env_json_sha256` (my P137) -> FAILS "clean on a homogeneous unit"   (the false alarm it causes)
```

**The envelope itself, re-derived by hand on the correct key, is CLEAN:** 16 test-tier comparison
units, **0** spanning more than one fingerprint label, **0** spanning more than one CPU model, all
**992** test-tier records on `Intel Xeon Gold 6240`. The D16 heterogeneity is fully gone from the
archive. **The instrument was broken; the campaign was not.**

---

## ★★★★ A41 — WHAT R115 ACTUALLY DID: it bound exactly twice, and BOTH times on a limit cycle

Cross-checked against two of the repo's own instruments, run this session — **independent routes, and
they agree with my census exactly**:

- `docs/ops/integrity_gate.py` → **I1–I6 all clean**, including **I4 selection** (every frozen winner
  is the max-fitness **R115-eligible** candidate of its arm). *Selection is correct under the
  registered rule; nothing below says otherwise.*
- `docs/ops/science_watch.py` → **17 R115 breaches**, matching my census (13 periodic + 4 aperiodic)
  and the cycle log's `r115=17B`. **R115 IS BINDING on two arms**, both on `qwen3_5_9b`.

**The two binding cases, ranked by validation fitness (probe 11):**

| arm | rank | val_fitness | candidate | safe_default | period | status |
|---|---|---|---|---|---|---|
| `distributional` | 1 | **+0.233582** | `distributional-g3-c3` | 0.499830 | **1/2** | **INELIGIBLE** |
| | 2 | +0.000589 | `distributional-g5-c0` | 0.078535 | aperiodic | eligible — **WON** |
| | 3 | +0.000124 | `distributional-g4-c3` | 0.000000 | — | eligible |
| | 4 | +0.000079 | `distributional-g0-c2` | 0.000000 | — | eligible |
| `placebo_shuffled` | 1 | +0.004550 | `placebo_shuffled-g5-c3` | 0.199933 | **1/5** | **INELIGIBLE** |
| | 2 | +0.004249 | `placebo_shuffled-g0-c3` | 0.090847 | **1/11** | eligible — **WON** |
| | 3 | +0.003652 | `placebo_shuffled-g4-c0` | 0.005280 | aperiodic | eligible |
| | 4–6 | +0.003264 … +0.000005 | three more | ≤0.000280 | — | eligible |

### Three things follow, and the first is strongly in our favour

**(1) R115 caught a textbook degenerate-fitness case, and the number is spectacular.** The excluded
`distributional-g3-c3` scored **+0.233582 — roughly 400× the next-best candidate on its arm** while
returning `SAFE_DEFAULT = 0.0` on **half** of its calls. A reward that stops responding to the policy
produces an enormous apparent validation fitness. **That is exactly the specification-gaming failure
R115 was registered to stop, it stopped it, and the margin is not subtle.** This is a rigour exhibit
that can be shown rather than asserted (Okhrati D5), and it belongs in CH6.

**(2) But on `placebo_shuffled` the floor substituted one limit cycle for another.** It removed a
period-5 cycle and selected a period-11 cycle — **the same pathology, differing only in which side of
0.10 its period puts it** — passing over `placebo_shuffled-g4-c0` at 0.53 % contamination for a 14 %
fitness gap. Together with §A36 this gives the sharpest available characterisation of the parameter:

> **In RUN 4, R115's operative content is a PERIOD threshold, not a contamination threshold.** Both
> candidates it removed are limit cycles (1/2, 1/5); the two it admitted nearest the floor are limit
> cycles (1/10, 1/11); and one of those won its arm. It excludes k ≤ 10 and admits k ≥ 11. The
> quantity it was designed to bound — the fraction of training spent on a null reward — is in practice
> a proxy for the reset period of a failure mode the design named separately (R41).

**(3) The confirmatory line is untouched, and that must be said with equal prominence.** All three
core-line frozen winners are exactly **0.000000**; the core line carries **0/188** periodic candidates
[0.00, 2.00]; R115 has never bound on it. **Everything in this section is on one report-only
replication leg (R80).** Overstating this would be as inaccurate as missing it.

**→ WRITE-UP:** (1) is a positive result and should lead. (2) is an Appendix-B sensitivity, stated
voluntarily. (3) is the sentence that keeps both honest. **→ No code change; R115 must not move
mid-run.**

---

## ★★★★★ A47 — THE REGISTERED SEARCH-ADEQUACY PACKAGE WAS THREE-FIFTHS UNBUILT. IMPLEMENTED, FALSIFICATION-TESTED, RUN.

**Origin.** Tamer asked why the search uses **30 candidates** when Eureka uses 80–400, and whether
that makes the winner untrustworthy. The frozen config answers it with a named defence —
`budget_decision: keep_and_instrument`, *"the **coverage_vs_k** instrument is a STRONGER defence than
a bigger raw K, at ZERO seed cost"*. **I audited that package against the code. Three of its five
members did not exist.**

| registered instrument | status before this session |
|---|---|
| `oracle_headroom` | ✅ implemented as `src/inference/headroom.py` (`validation_headroom`) |
| plateau rule | ✅ `scripts/determine_design.recommend_candidates` |
| `within_generation_diversity` | ⚠ AST primitive only, no named instrument |
| `executable_valid_rate` | ⚠ reject ledger only, no named instrument |
| **`coverage_vs_k_extrapolation`** | ❌ **NO CODE ANYWHERE** |

**This is the A16 pattern a third time** — registered, marked `reported`, never coded — and the
missing one is exactly the instrument that answers the first question a referee asks about K=5.

### Built: `docs/analysis/search_adequacy.py` (analysis-owned; nothing else touched)

**Effect-blind by construction:** search-stage `metrics.val_fitness` + `reward_source` only. **No
sealed outcome, no contrast, no p-value.** Selection adequacy is a property of the *search*, so it is
answerable now and its answer cannot move when the test lands.

**Exact, not sampled** — both curves are order statistics over a finite pool, so they have closed
forms and are computed exactly (no Monte Carlo ⇒ bit-identical replay):
`coverage(k;τ) = 1 − C(n−m,k)/C(n,k)` and `E[max|k] = Σᵢ x₍ᵢ₎·C(i−1,k−1)/C(n,k)`.
**25 falsification cases, all passing**, including `b = 1.0000` recovered exactly on an i.i.d. curve
and `b = 0.500` on a diminishing-returns curve.

### ★ THE RESULTS — and they partly vindicate the concern

**(1) THE SEARCH DID NOT SATURATE.** `sat99` = the smallest *k* whose **expected best** reaches 99 %
of the full pool's:

| arm | sat99 / n | | arm | sat99 / n |
|---|---|---|---|---|
| distributional | **25 / 28** | | scalar_cvar5 | **22 / 22** |
| scalar | **24 / 27** | | placebo_shuffled | **22 / 24** |
| placebo | **26 / 26** | | random_search | **30 / 30** |

**Saturation sits at essentially the full pool on every arm — the expected-best curve was still
rising when the budget ran out. More candidates would still have found better rewards.** That is
measured, it is uncomfortable, and it must be disclosed rather than argued away.

**(2) BUT THE BUDGET WAS ADEQUATE, NOT EXHAUSTED.** With-replacement extrapolation (the honest one),
against τ = the 90th percentile of all 1,408 authored candidates' validation fitness = **0.160409**:

| arm | qualify rate (95 % CI) | K=5 | K=16 (Eureka) | K=30 |
|---|---|---|---|---|
| distributional | 0.143 [0.057, 0.315] | 0.568 | 0.915 | **0.990** |
| scalar | 0.074 [0.021, 0.234] | 0.342 | 0.708 | 0.901 |
| placebo | 0.038 [0.007, 0.189] | 0.192 | 0.466 | 0.692 |

At 30 candidates the treatment arm had a **99 %** chance of having surfaced a top-decile reward.
*(The per-arm rates have overlapping intervals — **no arm difference is established** and none is
claimed.)*

**(3) EFFECTIVE WIDTH = 88.4 % [86.8, 89.9]** — 1,408 accepted of 1,592 attempts (184 gate rejects).
The nominal 30 delivered ≈ 26.5 usable candidates.

**(4) ★ NO K-COLLAPSE — a clean positive.** Mean pairwise **structural** similarity between the K=5
candidates within a generation, using the repo's own identifier- and literal-invariant
`structural_similarity` (and honouring its `has_structure` precondition, repo issue #117):
**distributional 0.274 · placebo 0.275 · placebo_shuffled 0.277 · scalar 0.279 · scalar_cvar5 0.270.**
**The nominal width IS the real width** — the K=5 are genuinely distinct programs, not
prompt-variation near-duplicates.

**(5) AND ONE THING DELIBERATELY NOT REPORTED.** Brown et al.'s correlated-sampling correction needs
**independent restarts** of the whole search (Eureka runs 5 per environment; this design runs 1 per
arm). **It is NOT ESTIMABLE here**, and the module returns `correlation_estimable: False` rather than
fitting something it cannot support.

### ⚠ TWO INTERPRETATION ERRORS IN MY OWN FIRST VERSION — P151, P152

**P151 — I fitted a power law to the wrong curve and would have reported the opposite conclusion.**
The first run returned **b > 1 on every single arm** (1.27–1.33), which reads as *accelerating*
returns to width. It is an artefact: the **without-replacement** curve reaches exactly 1.0 once the
non-qualifying candidates are exhausted, so it is steeper than any i.i.d. curve **by construction**.
That `b` measures **finite-pool truncation, not sample correlation.** **Caught by the tell this lane
has now paid for seven times: a result that is uniform across every arm is a claim about the
instrument.** Replaced with the with-replacement extrapolation, which needs no fit; the finite-pool
fit is retained, clearly labelled, and carries a do-not-extrapolate warning **inside the returned
object** so the caveat travels with the number.

**P152 — I flagged four arms as "K-COLLAPSE" that cannot collapse.** `random_search`, `bayes_opt`,
`cma_es` and `tpe` do not author code — they sample **parameters** inside one fixed reward template,
so every source is the same program with different literals and an identifier-and-literal-INVARIANT
similarity correctly returns exactly **1.000**. A false positive on **four of nine arms**. The flag is
now scoped to code-authoring arms with the reason carried in the result.

### → THE ASK

**Wire the three instruments into `analyze_campaign`'s registered `out[...]` key set**, so they enter
the enumerated scope, `WHY_REGISTER` and the pre-submission gate — the exact remedy A30 prescribed
for per-arm PopArt and A45 for `benchmark_floor`. Until then they exist but are not registered
outputs, which is the "AUTHORED but not WIRED" state the write-up lane named.

---

## A40 — D16: **DISCHARGED** (was: not restored at ~9 h)

**Closed 2026-08-01 ~13:16Z and re-verified independently by me at 13:47Z**, by reading the archive
rather than any lane's alarm: `test/baseline_volatility_scaled_return` holds **30 seeds, missing
NONE**, and **one distinct CPU model — `Intel(R) Xeon(R) Gold 6240`** — across all thirty. All four
re-runs (s14 13:04:33Z, s17 13:07:30Z, s15 13:08:29Z, s16 13:16:37Z) landed on the correct fenced
substrate, so **the D16 defect did not recur**.

**⇒ A12-bis is fully discharged.** The concern was that `paired_seed_difference_test` operates over
**shared** seeds, so an N6 IUT leg computed at n=26 while its ten siblings used 30 would silently
carry a weak leg — and in an IUT the **max-over-legs** rule makes the weakest leg disproportionately
likely to decide the node. **There is now no weak leg**, and the ratified
`cpu_randomised_device_block` premise (device homogeneity within every CRN comparison unit) **holds
as measured fact rather than assertion**.

## A40-bis — the ORIGINAL D16 status, retained as the record of what was open

`test/baseline_volatility_scaled_return` holds **n = 26**, missing exactly **[14, 15, 16, 17]** — no
over-reach, no collateral. Two distinct seed sets across the twelve core units. Until they land, an
N6_h1 IUT leg computes on **26 pairs while its eleven siblings use 30**, and in an IUT the node
p-value is the **max over legs**, so the reduced-power leg is disproportionately likely to decide N6.
**Re-verification conditions on restore are unchanged (A12-bis):** seeds 0–29 complete, one shared seed
set across all twelve, and all thirty on the 6240. The cycle now checks the second condition
automatically for the first time.

---

## ★★★★ A46 — A SECOND DEAD SPOT IN MY OWN INSTRUMENT, FOUND BY MY OWN ERROR — AND FIXING IT MADE THE TOOL RE-DISCOVER A11 UNAIDED

**How it was found — by committing P141 and then suspecting myself.** Re-verifying the evaluation
window at the current record count I probed `record["val_returns"]` and got **`None` on all 1,373
search records**. A perfect 100 % null is the lane's own tell, so before writing it down I dumped the
record schema: **`val_returns` lives at `metrics['val_returns']`, not at top level.** Measured
correctly it is **`list[694]` on 1,373 / 1,373, zero `None`, across all twelve lines.** No defect.
*(P141 — reading a field at the wrong nesting level, the exact class this lane logged as P110's
sibling. My alarm, my error, caught before it reached a document.)*

### ★ AND THE CORRECT MEASUREMENT INDEPENDENTLY SETTLES THE A16 MARGIN — from the DATA this time

**Every archived validation series is exactly 694 periods long**, and
`scripts/power_analysis.VALIDATION_TRACK_LENGTH = 694`. So the DSR that the frozen SESOI is expressed
in **is computed on a 694-period series, as archived**, and `k(694) = 0.661571 ⇒ margin 0.0756` is the
right conversion. **The 1,571 reading is the TEST length and is definitively wrong.** That is a
**third independent route** to coord's number — config, code, and now the archive — and it is the
strongest of the three because it is measured rather than read.

### THE INSTRUMENT DEFECT THE ERROR EXPOSED

`flatten()` collapsed every `BULKY` field to a shape tag: `None` became the **string** `"<bulk>"` and
`""` became `"<str:0>"`. The always-null sweep tests `val is None or val == "" or val == {}` — so
**neither form was ever counted as null.** `feedback_block` is itself in `BULKY`. **⇒ The sweep was
structurally incapable of finding A11 (`feedback_block` empty on 100 % of search records) — this
lane's own best historical finding, and the second of the three the standing note is built on.**

**Fixed:** an empty or null BULKY leaf now keeps its real value (visible to the sweep); a non-empty
one is still summarised so a 1,571-element series is never compared for constancy. **Three new
falsifying cases** added, and verified in both directions:

```
against the FIXED flatten     -> ALL 16 PASS
against the PRE-FIX flatten   -> FAIL "null sweep sees an EMPTY bulky field (feedback_block == '')"
                                 FAIL "null sweep sees a NULL bulky field (val_returns is None)"
```

**★ AND THE REAL POSITIVE CONTROL, FROM THE LIVE ARCHIVE.** Before the fix the sweep printed
`always-null (0): []`. After it, on 2,399 records:

```
always-null (1): ['feedback_block']
```

**The repaired tool re-discovered A11 unaided.** That is stronger than any synthetic case: it found a
known-true, independently-established finding that it had been silently blind to. *(It also confirms
A11 still holds at 2,399 records — the experiment's independent variable is still not a first-class
archived field.)*

> **THIS IS THE THIRD AND FOURTH DEAD PANEL IN THIS ONE INSTRUMENT** (after `panel_homogeneity` and
> the discarded `missing` list). The pattern is now unmistakable and worth stating as a rule:
> **every summarisation step in a defect detector is a place where the defect can hide.** The shape
> tag existed for a good reason — don't compare 1,571-element arrays — and it silently swallowed
> exactly the case the detector was built for.

---

## ★★★★★ A45 — I RAN THE CONFIRMATORY ANALYSIS END-TO-END, BLIND. IT COMPLETES — AND FOUR REGISTERED OUTPUTS WILL SILENTLY BE ABSENT UNLESS ONE FILE IS WRITTEN.

**Nothing verified that `scripts/analyze_campaign.py` can RUN on the live archive.** Ops found a
`NameError` *inside* the confirmatory analysis this morning and caught it only by executing it
("parsing would not have caught it"). A crash discovered when the campaign stops is discovered too
late, so I executed the whole pipeline against the live archive.

**BLINDNESS DISCIPLINE — the run cannot unblind me, by construction.** I called `analyze()`
**directly** and never `write_report`, so **nothing was written anywhere**, least of all into ops'
archive. The script prints **only key names, container types, lengths and error text** — never a
numeric value. *(Deliberate: `write_report` writes `campaign_overfitting.{md,json}` into the archive
ROOT, which is ops-held and live. The archive is 638.7 MB so I did not copy it, and I did **not** use
directory junctions — CLAUDE.md records a 2026-07-27 junction incident that nearly destroyed the
licensed gold.)*

### 1. THE GOOD NEWS, AND IT IS WORTH STATING

```
STATUS: COMPLETED WITHOUT RAISING          out[...] keys produced: 34
all six confirmatory nodes: located=False, each with a NAMED reason
   N1/N2  "at least one leg has no usable p-value (an IUT cannot certify)"   n_legs=3
   N3     no dict at out["h3"]["difference"]        N4  no non-empty 'tests' at out["h4"]
   N5     no dict at out["h2_structure"]["cvar"]    N6  no dict at out["h1_beat_human"]["iut"]
```

**The pipeline executes to completion on the live archive and degrades GRACEFULLY** — every node
reports `untestable` with a named reason rather than crashing or, worse, certifying from a missing
value. That is the fail-safe `validity_tier.py`'s docstring promises, verified against real data for
the first time. **All six `located=False` is exactly correct at this stage:** no core-line H2 arm has
test records, so no leg is computable. *(This is also an independent re-confirmation of the A42
blindness precondition, from the analysis pipeline's own mouth.)*

### 2. ★ THE FINDING — FOUR REGISTERED OUTPUT KEYS ARE NOT PRODUCED, AND THE CAUSE IS ONE MISSING FILE

Comparing the **32** `out["…"] = …` assignments in the source against the **34** keys actually
produced, **five registered keys are absent**:

| key | why it vanished |
|---|---|
| **`benchmark_floor`** | in the `panel is not None` block — **the DeMiguel 1/N floor** |
| **`attribution`** | same block — the Fama–French factor attribution |
| **`h2_rf_robustness`** | same block — the risk-free-rate sensitivity on H2 |
| **`regime_stratified`** | same block — the regime-stratified analysis |
| `variance` | needs `--variance-runs`; **expected**, not a defect |

**All four share one cause.** `main()` populates `panel` / `cfg` / `test_window` / `winner_n_trials`
**only by reading `campaign_summary.json` at the archive root** (`:6847`). And:

> **THERE IS NO `campaign_summary.json` FOR RUN 4, UNDER ANY NAME, ANYWHERE UNDER `outputs/`.**
> A recursive search finds exactly six, all from the pre-launch rehearsals
> (`campaign_dryrun`, `rehearse2`–`rehearse6`), dated 2026-07-27/28.

`benchmark_floor` is not a minor exhibit: it is the **"9 published allocators, one costed
environment"** table — which is **already wired into the PDF** and appears in the compiled document
at the ToC (p15) and p150.

### 3. CREDIT WHERE IT IS DUE, AND THE THREE GAPS THAT REMAIN

**P7 (2026-07-13) already fixed the silent half of this**, and the comment says so in terms:
*"was a SILENT blanket except — the benchmark-floor exhibit vanished without a word when
`campaign_summary.json` was absent (the cluster mirror never had one)"*. There **is** now a loud
print. **Three gaps survive it:**

1. **The warning names only the benchmark floor.** `attribution`, `h2_rf_robustness` and
   `regime_stratified` vanish in the same block and are **not named anywhere** — so even a reader who
   sees the warning does not learn that three further registered outputs are gone.
2. **It is a print, not a gate.** The analysis exits **0**. Nothing downstream asserts that the
   registered key set is complete.
3. **`run_campaign_cluster.py` DOES have `_write_campaign_summary` (`:214`, added by that same P7),
   and RUN 4 still has no summary** — so either it is written only at a stage not yet reached, or the
   tiered path's `--root-suffix` naming puts it somewhere `--root` will never look
   (`campaign_summary_<suffix>.json` in `args.output_dir`, `:1422`).

### 4. THE ASK — ops, cheap, zero-risk, and it must precede the final analysis

**Confirm that RUN 4 will write `campaign_summary.json` AT `outputs/campaign_cluster_run4/`**, and if
it will not, arrange that one is produced **by the campaign machinery**. ⚠ **It must NOT be
hand-authored: it carries `test_window`, and a wrong window makes the analysis silently score the
floor on the wrong slice** — strictly worse than having no floor. Then make the completeness a
**gate**: assert the registered key set is present, and name every missing member.

**This is entirely pre-emptable now and unrecoverable later** — the floor cannot be back-computed once
the campaign is torn down and the panel/test-window provenance is gone.

### 5. A SMALLER INCONSISTENCY IN THE MACHINE-DEFINED SCOPE — writeup's `WHY_REGISTER` rests on it

CLAUDE.md's scope clause pins the enumeration to *"the **35** `out["…"]` keys of
`scripts/analyze_campaign.py`"*. **Measured: 32 `out[...] =` assignments, plus 7 set via a dict
literal (`archive_integrity`, `h2`, `n_blocks`, `n_records`, `pbo`, `pbo_dsr`, `winner_dsr` — the
literal-assignment form A17 already flagged), and 34 produced on the live archive.** **35 matches
none of those three counts.** Since `docs/WHY_REGISTER.md` is *generated from the analysis key set*
and the pre-submission gate fails on incomplete rows, the generator should derive the set
**programmatically from `analyze()`'s return** rather than from a literal in prose. Low severity,
trivial fix, and it is the difference between a machine-defined scope and a remembered number.

---

## ★★ A44 — A THIRD KIND OF INERT REWARD TERM, ON A CONFIRMATORY NODE. The taxonomy is now complete enough to be a finding.

**The h3_singleshot reward** — node **N3**'s arm, one program run at **560 seeds** — logs a
concentration penalty `conc_pen` that is **exactly 0.0 on 551 of 560 seeds (98.4 %)**, while all
eleven of its sibling components vary across all 560. Non-zero on 9 seeds, max |value| **2.15e-05**.

**Cause, read from the archived source (`distributional-g0-c17`):**

```python
hhi      = float(np_.sum((wr / s) ** 2)) if s > 1e-9 else 1.0
conc_pen = max(0.0, hhi - 0.14)
cc_pen   = -0.030 * conc_pen
```

The unit's own logged `hhi` component averages **≈0.063** — an effective breadth of ~16 assets —
against a trigger at **0.14** (~7 assets). **The threshold sits far above the realised range, so the
guard never binds.** Not a defect, not a failure: an authored term with no effect.

### ⇒ Three distinct mechanisms for "a reward term that does nothing", all measured today

| # | mechanism | evidence | where |
|---|---|---|---|
| 1 | **policy-independent** — computed from the market cross-section only, so it is an additive constant with no gradient | identical under different weights, same returns (executed) | A34(a) |
| 2 | **update path is the crash path** — the branch that would move it raises, and the harness resets the state | period-11 limit cycle, 22 seeds bit-identical (executed) | A34(b) |
| 3 | **threshold above the realised range** — a guard whose trigger the policy never reaches | `hhi ≈ 0.063` vs a 0.14 trigger, 551/560 seeds at exactly 0 | A44 |

**None is visible to any fitness-based check** — every one of these programs runs, returns finite
values and scores normally. **→ WRITE-UP: this is a small, clean, three-case taxonomy of *inert
authored objective terms*, measured rather than asserted, effect-blind, and directly on the
mechanism question ("does showing the LLM the downside change the reward CODE it writes?"). It is
also a practitioner's-checklist item: *log your reward's components and check that each one moves.***

*(Scope, stated so it is not over-read: (1) and (2) are on one report-only leg; (3) is on the
confirmatory h3ss line but is a property of the LLM's authored design, not of our harness, and it
changes no verdict — the term contributes at most ~2e-05 to a reward of order 1e-2.)*

---

## MY OWN ERRORS THIS SESSION — P136–P141, P151, P152 (all arbiter-allocated)

> **Eight errors, none of which reached a conclusion Tamer or another lane acted on.** Six were
> caught by the standing tells (an impossible clean, a uniform result, a 100 % null); two — P138 and
> the M156 unit error — were caught by *another lane*, which is the countermeasure that actually
> worked all day. **P151/P152 are in A47; the M156 unit error is in A42-bis.**

**P136 — I sliced a prefix that was not there, twice.** `top[len("search_leg_"):]` applied
unconditionally renamed `search_h3_singleshot` to **"ingleshot"**; the same shape applied to
`frozen_h3_singleshot` left that marker **UNRESOLVED** in the winner census. No number changed, but a
mislabelled line in a table is a defect. **Found by:** a line called "ingleshot" is impossible.
**Lesson:** slice a prefix only after testing for it.

**P137 — I grouped comparison units by the WHOLE `env_fingerprint` and got "30 distinct fingerprints"
on all twelve confirmatory units.** That would have been a catastrophic false alarm — "CRN pairing is
broken on every H1 leg". `env_json_sha256` hashes `env.json`, which carries the **seed**, so it is
distinct per record *by design*. **Found by:** 30-of-30 is impossible. **Lesson:** the standing rule
again — reading a value whose MEANING was not what its NAME implied — and it is now encoded as a
selftest case that fails on exactly that key.

**P138 — I read a counterfactual off a replay that never reproduced the original.** My sub-floor
classifier labelled three candidates "genuinely broken" when the synthetic replay disagreed with the
archived fraction by 10× and 12×. D17's own guard (`if shipped < FLOOR: INCONCLUSIVE`) exists for this;
I had not generalised it. Corrected to **INCONCLUSIVE**, which is what §A35 now reports. **Lesson:** a
replay must be shown to reproduce the artefact before any counterfactual is read off it.

**P139 — my arm-differential alarm fired a false positive on my own data**, declaring the periodic
class arm-differential from a point-estimate ratio at 18 events across five arms. The permutation test
says p = 0.668. **The heuristic came from the inherited tool and I ran it without calibrating it.**
Fixed to a disjoint-interval test. **Lesson:** an alarm that compares point estimates is the defect it
is supposed to catch.

**P140 — I told Tamer "D16 has started landing" from a DIRECTORY count.** The unit showed 27
directories against 26 records, so I reported a re-run seed had arrived. **The 27th is `_env`, the
launcher sidecar — dated 2026-07-28, and documented in A21 as 1 per (test lane, arm).** The directory
count was always 27; my earlier record-based measurement (n = 26) was right all along. **Corrected to
Tamer in the same turn. Lesson:** when a record-based measure and a directory-based measure disagree,
the record-based one is the measurement — a directory is not a result.

**P141 — I probed `record["val_returns"]` and got a perfect `None` on all 1,373 search records.** It
lives at `metrics['val_returns']`; measured correctly it is `list[694]` on every one. **Caught by the
100 %-null tell before it reached a document** — and chasing it produced A46, so the error was worth
more than the check that would have avoided it. **Lesson:** the wrong nesting level is this codebase's
single most repeated measurement error, across three lanes now.

**And one that did not become an error only because I checked:** my `--selftest` passed against the
pre-fix code (above). Had I shipped it, the repair would have carried a certificate that certified
nothing. **A test built from the constant it tests cannot detect a wrong constant.**

---

## ★★★★★ A42 — **A16 IS SETTLED.** It was never a three-way design disagreement. It is a single implementation gap against a ratified spec, and the fix needs no amendment, no unfreeze, and no Okhrati conversation.

> **AUTHORITY.** Tamer, 2026-08-01, verbatim: *"I wont send anything to Okhrati, I give you full
> permissions, and ratify your actions."* Recorded under [[feedback-full-delegation-2026-07-13]]
> (ratify-on-his-behalf, conditioned on ultrathink + strict priorities). **Reversible on a word from him.**

### 1. THE PRIOR FRAMING WAS WRONG, AND THAT CHANGES THE DECISION

A16 states that three artefacts disagree and *"one of the three must change."* **I read all three
first-hand and that is not what they say.**

| artefact | what it ACTUALLY says |
|---|---|
| `config/preregistration.yaml:287` (**hash-bound, RATIFIED R108 by Tamer AND Okhrati**) | `N2_h2_ra: {test: h2_ra_iut_or_tost, metric: sharpe, direction: one_sided_dist_better, equivalence: tost_0.05_dsr}` with the rationale *"TOST IS an IUT (bergerhsu1996equivalence) → a valid node p-value, so equivalence and superiority mix in one graph"* |
| `config/preregistration.yaml:293` (edges, same block) | *"alpha recycled on ANY rejection (**superiority OR equivalence**)"* |
| `PREREGISTRATION.md` (**hash-bound**) | :108 *"reported via TOST equivalence"* — about how the **epistemic credit for a null** is reported, contrasting with a bare p>0.05. :300 *"does not determine the thesis"* — inside a paragraph titled *"Robustness to the σ_D pilot"*, about the **MECHANISM headline** being independent of whether H2 lands as equivalence or non-rejection. :43-46 defers the tier's specification to the yaml (*"`config/preregistration.yaml: inference.validity_tier.status: ratified`"*) and **nowhere specifies N2's test.** |
| the CODE | `NODE_SOURCES["N2_h2_ra"] = {"path": ("h2",), "legs": "legs", "key": "pvalue_one_sided"}` — superiority only. No equivalence branch anywhere (`tier_node_pvalues` read in full, `validity_tier.py:77-118`). |

**⇒ The two frozen artefacts AGREE, and neither is contradicted. The hash-bound prose speaks about the
THESIS; the hash-bound yaml specifies the GRAPH, and it registers the disjunction explicitly, twice.
The code simply never implemented it.** This is an **implementation gap against a ratified
specification** — a bug — not a design ambiguity. **Nothing frozen has to change.**

**Why that matters practically:** the nine hash-bound files are `PREREGISTRATION.md`,
`config/preregistration.yaml`, `config/{inference,environment,data,arms}.yaml`, `prompts/{system,
initial_generation}.txt`, `src/feedback/schema.py`. **`src/inference/validity_tier.py` and
`scripts/analyze_campaign.py` are NOT among them, and neither is in `run_one.py`'s training closure.**
So the repair touches **no frozen byte, needs no unfreeze, moves no `deployed-archive`, and requires no
relaunch.** The freeze and the campaign's quality are not in tension here at all.

### 2. THE BLINDNESS PRECONDITION — VERIFIED, TIMESTAMPED, AND IT IS THE LOAD-BEARING FACT

Captured **2026-08-01T11:38:39Z**, HEAD `3bb9b999`. The confirmatory H2-RA contrast is
`distributional` vs {`scalar`, `placebo`, `scalar_cvar5`} on the **core** line. Core-line per-arm test
units holding records: **eleven baselines + `random_search` only.**

```
H2-RA arm distributional -> ABSENT      H2-RA arm scalar       -> ABSENT
H2-RA arm scalar_cvar5   -> ABSENT      H2-RA arm placebo      -> ABSENT
=> 0 of the 3 H2-RA legs are computable on the confirmatory line.
```

**No H2 outcome exists. I have computed no H2 contrast, on the core line or on any leg.** The decision
is therefore taken while completely blind — the epistemic position that is available *now* and not
afterwards. ⏳ **`frozen/placebo-winner` froze at 11:24Z and the core line is 3/5 LLM arms done; two to
go.** This was decided with roughly hours of margin, not days.

### 3. THE DECISION

> **N2's node p-value is the per-leg NON-INFERIORITY intersection–union test at the frozen margin
> δ = `inference.equivalence_margin` = 0.05:**
> **p(N2) = max over the three H2-RA legs of the one-sided p-value for H0_j : θ_j ≤ −δ**,
> where θ_j is the same per-seed paired IQM bootstrap difference the superiority legs already use.
> **Rejecting means: on every registered comparator, the tail-fed arm is not worse than the comparator
> by more than the SESOI.**

**Five reasons, in order of weight.**

**(a) It IMPLEMENTS the registration rather than amending it.** `{θ > 0} ∪ {−δ < θ < δ} = {θ > −δ}` —
"superiority **or** equivalence" is not a disjunction of two tests, it is **one** hypothesis. So
`h2_ra_iut_or_tost` at margin `tost_0.05_dsr` *is* a non-inferiority test at δ. The registered name gets
the registered value it always needed (the R84 lesson), pre-data.

**(b) It is provably valid, and it introduces ZERO new validity risk — this is an identity, not a
simulation.** IQM is translation-equivariant, so shifting one arm by δ shifts both the estimate and
every bootstrap replicate by exactly δ; the NI test at boundary −δ is therefore *algebraically the same
test* as the superiority test at boundary 0. Measured over 3,000 Monte-Carlo trials per cell, the two
sizes are **bit-identical at every n**:

| n | superiority leg at θ = 0 (the EXISTING rule) | non-inferiority leg at θ = −δ (the PROPOSAL) |
|---|---|---|
| 30 | **0.0703** | **0.0703** |
| 100 | **0.0607** | **0.0607** |
| 400 | **0.0570** | **0.0570** |

**(c) It costs nothing in power and strictly dominates the alternatives.** `p_NI` **is** the lower TOST
test, and the null moves left, so `p_NI ≤ min(p_sup, p_TOST)` pointwise — **verified, 0 violations over
400 synthetic legs.** It therefore rejects whenever *either* registered route would, and beats an
α-split by a factor of two. That matters enormously: the yaml's own note calls the tier *"BORDERLINE to
activate"* (n\* ≈ 173 against an expected rung of 100–189); an α-split would have killed it outright,
and requiring both TOST bounds roughly doubles the n needed versus one.

**(d) The α-inflation objection that blocked this for days is measured, and it is not the real effect.**
A16 warned that `min(p_sup, p_TOST)` *"inflates the node's type-I error"*. Measured over a grid of
least-favourable configurations, the naive rule's worst observed size is **0.0760** — against the
**existing** superiority machinery's own **0.0703** at the same n. **The gap between the naive rule and
a valid one is far smaller than the gap between the bootstrap's nominal and actual size.** The objection
was directionally right and quantitatively minor; it should not have been the blocker it became.

**(e) The claim it certifies is the one the science needs.** H2-RA's job is to establish that adopting
tail feedback does not *cost* risk-adjusted performance. "Not meaningfully worse on every comparator"
**is** that claim.

### 4. WHAT MUST BE REPORTED DIFFERENTLY — the honest cost, stated up front

**⚠ `⋂_j {θ_j > −δ}` is strictly WEAKER than `(⋂_j {θ_j > 0}) ∪ (⋂_j {|θ_j| < δ})`.** With three legs
the union is not the intersection of the per-leg unions: the NI test also rejects at configurations like
"superior on two legs, mildly inferior on the third". So:

1. **N2's claim must be WRITTEN as one-sided non-inferiority at the SESOI, never as "superior or
   equivalent."** The tier's conjunctive-validity sentence in CH4/CH6 must say so.
2. **The two-sided TOST stays exactly as it is** — `h2_tost` / `h2_tost_dsr`, report-only, tier 2, the
   bankable-null bound. Nothing about the bankable-null statement changes.
3. **Registered sensitivity, pre-specified here and now:** also report the strictly-faithful α-split
   disjunction `p = min(1, 2·min(p_sup, p_TOST))`. If it *also* rejects, the stronger "superior or
   equivalent" claim is available; if only the NI test rejects, only non-inferiority is claimed. **The
   primary is fixed in advance — which one rejects cannot select the claim.**

### 5. THE IMPLEMENTATION, SPECIFIED EXACTLY (ops owns the files; this is the whole change)

1. `scripts/analyze_campaign.py`, inside the H2-RA leg loop (`:1523`), add one line per leg beside the
   existing superiority test, reusing the **same** `rng`, `n_boot` and statistic:
   `ni = paired_seed_difference_test(a + delta, b, statistic=iqm, n_boot=n_boot, rng=rng)` →
   emit `"pvalue_non_inferiority": float(ni["pvalue_one_sided_greater"])` and `"ni_margin": delta`
   on the Sharpe legs, with `delta = _frozen_equiv_margin()` (**read from config, never a literal**).
   The units question is settled by the registration: the node names `tost_0.05_dsr`, so the margin is
   applied in the **DSR units** `h2_tost_dsr` already maps into — and because that map is a documented
   linear **upper bound** on ΔDSR, using it makes the NI test **conservative on the binding side**.
2. `src/inference/validity_tier.py:51` → `"N2_h2_ra": {"path": ("h2",), "legs": "legs",
   "key": "pvalue_non_inferiority"}`, and update the NODE MAP table in the module docstring.
3. **Tests that FAIL against the pre-fix code** (non-negotiable): a leg set with all θ_j ∈ (−δ, 0)
   must make N2 reject under the new key and NOT reject under `pvalue_one_sided`; and the
   `test_graphical_alpha.py:112` case must be re-pointed so it exercises `tier_node_pvalues` rather
   than bypassing it — **that bypass is why no test ever caught this** (A24).
4. **Also fix the reporting, which is needed under any option:** the verdict currently returns
   `not_rejected=[all six]`, `untestable=[]`, so it **cannot distinguish "tested and failed" from
   "never testable"**. That is truth-in-reporting, not a design change (coord's option 5).

**Nothing here is urgent for the RUNNING campaign** — no relaunch, no frozen byte, no archive move. **The
DECISION is what expires, and it is now taken, dated, and evidenced.** The code can land in ops' next
controlled deploy.

### ★★★★★ A42-bis — THE FULL ARC: I CONCEDED, THEN WITHDREW THE CONCESSION, AND THE DECIDING SENTENCE WAS ONE NOBODY HAD READ

**This is the most instructive sequence of the session and it must not be compressed into "A16 was
fixed".** Four lanes argued one question for six hours. Every lane was wrong at least once. The
resolution came from a line in the frozen document that none of us had opened.

| step | what happened |
|---|---|
| **M156** | I posted the decision + an exact patch, arguing the two frozen artefacts AGREE (:43-46 defers the tier to the yaml; :108/:300 are about the null's epistemic credit and the mechanism headline). |
| **M162** | Ops and coord both declined. I refuted their three premises with evidence. |
| **M170** | **I CONCEDED** — ops' seniority argument checked out: `freeze.py:6-7` calls `PREREGISTRATION.md` *"the human-readable prose record"* and the yaml *"its machine-readable **mirror**"*, and `assert_prose_matches_yaml` makes the prose senior on any disagreement. |
| **M172/M174** | **Coord found `PREREGISTRATION.md:1051`** — amendment R105, hash-bound: *"**TOST is itself an IUT** (Berger-Hsu 1996), so our predicted CVaR-tail-win + Sharpe-**equivalence** legitimately activates the tier (α flows on a TOST rejection = 'equivalence proven')."* Plus :398, *"the Sharpe-leg TOST is decisive"*. |
| **M176** | **I WITHDREW THE CONCESSION**, having read :1051 and grepped independently for every hash-bound line registering TOST as an alpha route. **The hash-bound PROSE registers the route itself ⇒ there is no disagreement, so no seniority rule is ever invoked.** My M156 framing was right, on evidence I had not had. |
| **M187/M195** | Ops decided and implemented, inside the blind window, as a timestamped pre-specification. |

**★ THE LESSON, AND IT IS THE ONE FOR THE QC APPENDIX:** every lane, including me, argued the
question over **three sentences** (:43-46, :108, :300) and **not one of us asked what the prose says
where it actually REGISTERS the tier.** A six-hour, four-lane dispute was settled by reading the
amendment row that creates the object under dispute. *Argue from the registration row, not from the
paragraphs that mention the topic.*

### ⚠ AND THE ERROR THAT WAS MINE — a specification whose PROSE and CODE disagreed

**M156 §5(i) gave ops this patch line:** `ni = paired_seed_difference_test(a + delta, b, ...)` with
`delta = _frozen_equiv_margin()`. That function returns **0.05 in VALIDATION-DSR units** — its own
docstring says so — while `a`/`b` at that call site are **per-seed ANNUALISED SHARPE**. **The line
adds a DSR number to Sharpe data.** My accompanying prose said the right thing (*"apply the margin in
the DSR units `h2_tost_dsr` already maps into"*); **my code line contradicted my own prose, and the
implementer types the code.** Coord's synthetic legs show it is outcome-relevant: **p(N2) = 0.0065
(REJECTS) vs 0.5515 (does not).** Owned in M176.

**⇒ THE RULE, now in the execution record at ops' request:** *a specification whose prose and code
disagree is a defect **even when the prose is right**.*

### THE MARGIN — settled at 0.075578 by FIVE independent routes

Three lanes derived this in **both** directions within thirty minutes. Every competing figure is
formally withdrawn on the bus (coord M164 → withdrawn; my M170 concession → withdrawn; my M156 patch
line → owned and retracted).

| route | evidence |
|---|---|
| **CONFIG** | `sesoi_derivation.dsr_per_ann_sharpe = 0.6616`, `sesoi_ann_sharpe_equiv = 0.0756` (hash-bound) |
| **CODE** | `h2_tost_dsr` defaults `track_length` to `VALIDATION_TRACK_LENGTH = 694` when None — read in source |
| **DATA (mine)** | every `metrics['val_returns']` is **`list[694]` on 1,373/1,373** search records, all twelve lines, zero exceptions |
| **R104 BAND** | the frozen block binds 0.0055 < **0.0756** < 0.10 **in annualised Sharpe** with verdict `sesoi_inside_band` — were the margin 0.0502 the frozen block would no longer describe the executed number |
| **EXECUTED WINDOWS** (ops) | the campaign's own `resolve_windows` returns val **(3081, 3775) = 694**, test (3835, 5406) = 1571 |

**Why T=1571 is a scope error, not an alternative reading:** the SESOI is registered *"in
validation-DSR units"* and `held_out_fitness` **refuses** to compute on anything but the validation
split (`src/selection/fitness.py:103`). 694 IS the validation track length; 1571 is the TEST length.

**⚠ DIRECTION, STATED AGAINST OURSELVES:** 0.0756 is the **more permissive** margin — a wider
non-inferiority band makes the node **easier** to reject. It is adopted because it is the value the
frozen config records *and prices*, not because it is conservative. **That tension belongs in the
amendment, with both numbers and both directions named.** The conservative 0.050212 reading and the
superiority-only rule are both pre-specified as reported sensitivities (ops M195 §6 ships all three
verdicts unconditionally — *"a sensitivity you have to request is one you can decline to request
after seeing the primary"*).

**AND THE GUARD, endorsed by two lanes and now shipped:** a test asserting the executed margin equals
`inference.sesoi_derivation.sesoi_ann_sharpe_equiv` to 4 dp, reading **both sides from config**. It
**fails against my patch line as written**, which is exactly what makes it worth having — and it
protects `h2_tost_dsr`, which SHIPS as report-only and carries the bankable-null bound, from anyone
later "correcting" the track length to 1571.

**AND THE BYPASS WAS TWO TESTS, NOT ONE (ops M195 §5).** A24 named
`tests/test_graphical_alpha.py:112`. Re-pointing it exposed
`tests/test_validity_tier_assembly.py::test_predicted_null_branch_activates_the_tier_via_the_TOST` —
which fed N2 a **superiority** p and asserted the equivalence route had opened the tier. **It has the
word TOST in its name and had been passing for eight days against code with no TOST route at all.**

### 6. A BY-PRODUCT WORTH MORE THAN THE FIX — the size of the confirmatory tests is a FUNCTION OF n

The repo already knows the paired percentile bootstrap is anti-conservative and says so honestly
(`tests/test_inference.py:774` asserts the prose may never claim a "certified" size; the recorded figure
is **0.0573 two-sided / 0.0613 one-sided** at production settings; `power_analysis.py:58` cites Colas on
the two-sample bootstrap below N≈50). **I am not claiming that.** What I add is that **it is a function
of n and I measured the curve**: **0.0703 at n = 30 → 0.0607 at n = 100 → 0.0570 at n = 400** (3,000
trials/cell, normal DGP, one-sided, nominal 0.05).

**Two consequences.** (i) The **tier-0 floor n = 30 is the worst point of the whole ladder** — the real
one-sided size there is ~7 %, not 5 % — which is an independent, quantitative argument for the seed
ladder that has nothing to do with power. (ii) It is the natural companion to Okhrati's **D2**
seed-trajectory duty: a **size-versus-n curve** printed beside the estimate-versus-n curve turns a known
limitation into a rigour exhibit. **→ WRITE-UP.** Caveat stated: measured under a normal DGP, so it
bounds the shape, not the exact number on the real per-seed Sharpe distributions.

*(IUT note, so this is not over-read: an intersection–union test is conservative overall. With all three
legs at the boundary the node's measured rejection rate was **0.0000**; the ~0.070 applies to the
least-favourable "one binding leg" configuration. The node's true size lies between.)*

---

## ★★★★★ A43 — THE COMPILED DISSERTATION, INDEPENDENTLY VERIFIED. Coord's finding is REAL and their fix is REAL — and a per-character fix list will NOT close it.

Coord (M151/M153/M154) found that the PDF had not built since 13 July, fixed four defects, and
reported 73 silently-dropped glyphs. **They verified their own repair, so I re-measured everything
from the artefact.** Every number below is mine, from the built PDF.

### 1. CONFIRMED, EXACTLY

```
paper/_build/dissertation.pdf   629,385 bytes   %PDF-1.5   %%EOF present   230 pages
extracted text 373,315 chars    U+FFFF (dropped-glyph marker) = 73    U+FFFD = 0
literal U+03B1 GREEK SMALL LETTER ALPHA surviving in the PDF text = 0
U+1D6FC MATHEMATICAL ITALIC SMALL ALPHA                          = 36
```

**73 dropped glyphs across 44 distinct pages.** `$\alpha$` renders; a bare `α` does not. Coord's
count, cause and mechanism are all correct.

### 2. ★ THE PART THAT CHANGES THE FIX — A CHARACTER LIST CANNOT DRIVE THIS

I built the per-character census (13 characters, **57** prose occurrences in the assembled
`paper/_build/dissertation.md`) and then **matched each of the 73 markers back to its source
character positionally.** The two disagree, and the disagreement is the finding:

| | |
|---|---|
| dropped markers in the PDF | **73** |
| occurrences the character census predicts | **57** |
| markers I could positionally resolve | 37 (the rest defeated by PDF hyphenation, e.g. `co- primar`) |

**Resolved characters include ones the census scored as SURVIVING:** `≈` (4 markers, census said
10/10 survive), `≥` (2 markers, census said 3/3 survive), plus `*` (3) and a backtick (1) from the
math/markdown-escape class coord already fixed one instance of.

**⇒ The same character renders in one font context and is dropped in another** — math spans are
re-encoded, code/monospace uses a different face, body prose uses `lmroman`. So a substitution list
built from the source is **provably incomplete**, and a fix driven by it will leave damage behind
while reporting success. *(This is the wrong-denominator error I have flagged in three other places
today, and my own first census committed it.)*

> **THE ONLY VALID ACCEPTANCE TEST: rebuild, extract the text, assert the U+FFFF count is ZERO.**
> Not "all the alphas are fixed". Not "the grep is clean". **Zero markers in the built artefact.**

### 3. THE DAMAGE, RANKED BY WHAT IT COSTS — the full 73-passage list with pages is in my scratchpad and available on request

**Substantively destructive (a number or a rule becomes unreadable or ambiguous):**

| page | rendered text | what is lost |
|---|---|---|
| **158** | `scored 7.8 × 10￿￿ and eliminated itself` | **the EXPONENT — a reported number is unreadable** |
| **197** | `fell back to the harness default on ￿10 % of calls` | **the `≥` in R115's eligibility rule — a decision rule made ambiguous** |
| **109** | `Markowitz quadratic utility r −½￿·var` | **the λ — the utility is wrong as printed** |
| **141** | `rewards of the form return / (variance + ￿)` | **the ε in R41's REGISTERED formula** |
| **100** | `half-L1-drifted turnover 0.5·‖w −w_held‖￿` | **the `₁` subscript — the norm loses its order** |
| **214** | `the ￿²-upper confidence bound on ￿_D` (×6 on this page) | **χ² and σ_D** |
| **112** | `weights ￿0 summing to 1` | **the `≥` — the simplex constraint** |

**Communication-critical (UCL rubric dimension 4, the non-specialist second marker):**

| page | rendered text |
|---|---|
| **9** | glossary: `VaR … The loss threshold that is exceeded only ￿% of the time` |
| **10** | glossary: `CVaR … The average loss in that worst-￿% tail` |
| 38, 83 | `left-tail mass beyond −2￿` (σ) |
| 135, 150 | `one-sided at ￿= 0.05` |
| 200 | `(￿_seed = 0.244)` |
| 146 | `Spearman ￿[FROM CAMPAIGN: ￿, n legs, p]` (ρ) |

**The two glossary entries are the worst single item in the document.** They define the study's two
central risk measures, they are the first thing a non-specialist second marker reads, and both are
broken in the same way.

**Structurally embarrassing:** the A16 disclosure passage — the thing this bus spent the morning
getting right — is among the worst hit: **p92 ×4, p93, p104 ×3, p223 ×5**, every `α` a blank.

### 4. TWO NEGATIVES, STATED BECAUSE OVERSTATING A RISK IS AS INACCURATE AS UNDERSTATING ONE

**(a) THE BIBLIOGRAPHY IS CLEAN. Harvard referencing is NOT damaged.** The `References` heading is
on **p162**; the reference list runs to ~p194 and carries **ZERO dropped markers** (every marker at
p195+ is appendix body text). Accented author names render correctly — verified in the PDF text:
**`Šidák`, `Théate`, `López`, `Bäuerle`** all intact. Nobody should spend a minute on refs.bib.

**(b) A LATENT RISK THERE, THOUGH, THAT NOBODY HAS NAMED.** `paper/refs.bib` contains **11 CJK
ideographs** (`数理解析研究所講究録` — a RIMS Kôkyûroku entry). It produces **zero** markers today,
which means the entry is **currently uncited**. `lmroman` has no CJK coverage, so **the moment that
entry is cited its title will render as a row of gaps in the reference list.** Cheap to pre-empt now,
expensive to discover at submission.

### 5. THE DURABLE FIX — I endorse coord's, and add the acceptance test

1. **Fail on any control byte** (`< 0x20` other than tab/LF/CR) anywhere in `paper/**/*.md` — this
   is what made a fatal defect invisible for nineteen days.
2. **Fail on any `U+FFFF` in the BUILT PDF's extracted text.** ← the one that actually closes A43,
   because §2 proves the source-side check cannot.
3. **Run the FULL build in the gate, never `--md-only`.** Every lane — including me, until I checked
   — has been reporting the paper green on a proxy that exits before pandoc.

**→ WRITEUP owns paper/**. I have touched nothing in it and will not.

---

## LIVE EVENTS DURING THIS SESSION, AND ONE WATCH ITEM (claiming nothing)

**A NEW CORE-LINE WINNER FROZE AT 11:24Z: `frozen/placebo-winner` ← `placebo-g3-c3`.** The core
confirmatory line is now **3/5 LLM arms frozen** (`distributional`, `scalar`, `placebo`; plus
`random_search`, an H4 optimiser arm). `scalar_cvar5` and `placebo_shuffled` remain in search.
**Checked on arrival, as the standing cycle requires: `frac = 0.000000`, and so is every one of the
26 candidates in that arm's pool. All four core-line frozen winners remain exactly 0.000000.**

> **⏳ THIS MOVES A16'S DEADLINE CLOSER.** Stage C2's `h2_pair_test` launches after the core arms
> drain, and coord's W7 watch fires on the first record from the core H2 test arms. Two arms to go.

**WATCH, NOT A FINDING — the H4 optimiser arms' depth spread.** Accepted candidates per core-line arm
right now: `random_search` 30 · `distributional` 28 · `scalar` 27 · `placebo` 26 · `placebo_shuffled`
21 · `scalar_cvar5` 21 · `bayes_opt` 17 · `tpe` 15 · `cma_es` 7. **Five of those nine arms are STILL
SEARCHING, so every one of these numbers is an in-progress snapshot and no imbalance can be claimed
from them** — asserting one would be exactly the P116/P119 error (reading a bound off a moving
quantity). Recorded because the H4 node is an IUT over the optimiser arms and a starved comparator
shifts E[max] in the direction that *favours our own hypothesis*; **it must be re-derived on the
completed campaign**, alongside the H2 arm-depth argument already carried in `APPENDIX_B` B.8.9/B.8.10
(whose projection of 28/27/25/24/24 remains live and is not yet falsifiable).

---

---

## ★★★★ A48 — THE LINEAGE'S ACTUAL SELECTION BUDGET, READ FIRST-HAND FROM THE CORPUS

**Origin.** Tamer: *"they have far more candidates than we do?"* Nobody had checked what the lineage
actually spends. I read the PDFs rather than answer from memory.

| paper | candidates | **seeds per candidate for SELECTION** | seeds for the **REPORTED** result |
|---|---|---|---|
| **Eureka** (Ma et al. 2023) | 80/run (5 iters × K=16), ×5 restarts = 400 | **1** | 5 independent runs |
| **REvolve** (2024) | 112 (7 gens × K=16) | **1** | **2** |
| **DrEureka** (2024) | — | **1** | **3** |
| **Text2Reward** (ICLR'24) | — | **1** | **5** |
| **THIS WORK** | 30 (6 gens × K=5) | **1** | **30 → 568** |

**Verbatim, Eureka's own algorithm box (p.4):** `7: s₁ = F(R₁), ..., sₖ = F(Rₖ)` … `9: … best =
arg maxₖ s₁,...,sₖ` — **one fitness evaluation per candidate, then argmax.** And: *"EUREKA conducts 5
independent runs per environment, and for each run, searches for 5 iterations with K = 16 samples per
iteration."* REvolve: *"Due to these extensive computational demands, we report results using **two**
random seeds."* DrEureka: *"we train policies using **3** random seeds."* Text2Reward: *"calculated
across **five** different random seeds."*

**⇒ TWO CLAIMS THE WRITE-UP CAN NOW MAKE, BOTH EVIDENCED:**

1. **Single-seed selection is the lineage standard**, established by the paper that founded it. This
   study follows the field's protocol; it does not cut a corner.
2. **On the number that is actually REPORTED, this study is 6–15× deeper than anything in the
   lineage.** They publish on 2–5 seeds; this publishes on 30 minimum, climbing to 568, with a
   pre-registered SESOI, equivalence testing and an exogenous stop. **To our knowledge the first in
   this lineage to do so.**

**Stated honestly in both directions:** Eureka runs **5 independent restarts** of the whole search
(400 candidate evaluations) and this design runs **one per arm** — real robustness we do not have.
But the allocation is a design necessity, not a shortcut: our budget goes to **nine arms across
eleven models** (~2,970 candidate evaluations, ~7× Eureka's total) because the **identification
principle** requires the controls. Eureka buys restarts; this buys the controls that license a causal
claim. **Different allocations, and only one of them supports an attribution.**

**→ WRITE-UP:** this converts the K=5 worry into a *stated methodological position* with five
first-hand citations behind it. Pair it with A47's measurements and the answer to *"why not K=16?"*
stops being an argument and becomes a table.

---

## OPEN, UNCHANGED, AND NOT ALLOWED TO GO STALE

- **A16 — the N2/TOST node mapping. For Tamer with Dr Okhrati, settleable only pre-data.** Nothing in
  this session touched it; it remains the single most consequential open item and it expires when the
  core H2 ladder unblinds. Full statement: `docs/ANALYSIS_LANE_2026-08-01.md` §A16 + the decision brief.
- **R106** (uniform reasoning-off was never in force) · **the kimi "strongest pin" wording** · **the
  four unregistered evidence-of-validity quantities** · **spend ~$81 vs a registered advisory $30** —
  all as stated in that document's decision brief, none re-litigated here.
