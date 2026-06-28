# DEEP_FRAMING_discipline — the pre-freeze framing/governance disciplines that pre-empt killer critiques

**Status:** read-only governance + framing-discipline dossier (NOT dissertation prose; an integrity register
of *how the write-up must talk about the results*, derived from the deep red-team docs). No code, config, or
pre-registration edited. **Date:** 2026-06-25. **Repo:** `llm-reward-portfolio`. **Author role:** integrity
steward fixing the claim-language *before* the campaign freezes, so the PDF cannot over-reach. **PDF-only
grade, no viva** (supervisor Dr Ramin Okhrati, who co-authored backtest-statistics and RL-finance corpus
papers).

> **What this document is, and is not.** It is **not** the Limitations register (that is
> `00_planning/LIMITATIONS_REGISTER.md`, L1–L19) and it is **not** dissertation text. It is the
> **framing-discipline contract**: three disciplines the write-up must obey so that the *language* of the
> claims never out-runs what the design supports. Each discipline below names (i) the killer critique it
> defuses, (ii) the exact rule, (iii) the first-hand source in the deep docs, and (iv) struck/safe phrasing
> where useful. Every code/config assertion is sourced to a deep doc that verified it first-hand; literature
> not re-verified here is marked `% VERIFY`. Companion: the three disciplines map to limitations L15–L19 and
> several need a `PREREGISTRATION.md` cross-reference (listed in §4).

---

## 0. Bottom line up front

Three disciplines, each closing a specific killer attack the deep agents surfaced:

1. **No-SOTA-claim discipline** (`docs/DEEP_BENCH_T4.md`). "Does it work" is restricted to the **internal,
   matched ladder** (T0 classical floor / T1 = H1 hand-reward bar / T2 = H4 search) — same universe, same
   period, same costs, one pre-registered inference family. The FinRL/FinRL-Meta SOTA band is **context
   only, never a ranking**, and is governed by a "cite-the-band-against-itself" caveat block. Plus the
   project-specific **negative-prototype-Sharpe display landmine**: do not plot arms below the band naively.

2. **Construct retitle** (`docs/DEEP_H2.md`). The headline construct is retitled from **"distribution"** to
   **"multi-level tail-risk feedback"** — the operationalisation is six left-tail scalars, not a full
   distribution — defended as a *principled* tail descriptor via Artzner/Acerbi/Kusuoka coherent-risk theory.

3. **T0 fairness disclosures** (`docs/DEEP_BENCH_T0.md`). Two specific fairness asymmetries in the classical
   floor must be reported, not assumed away: the **daily-rebalance cost tax** on the sophisticated allocators
   (a per-benchmark turnover/cost table proves the *binding* benchmark is fairly costed), and the **Deflated-
   Sharpe N=1-vs-N=30 deflation asymmetry** (report the winner's *undeflated* DSR alongside the deflated gate).

None requires a campaign re-run; all are documentation/reporting disciplines plus (where flagged) a
pre-registration cross-reference.

---

## 1. The NO-SOTA-CLAIM discipline (source: `docs/DEEP_BENCH_T4.md`)

### 1.1 The killer critique it defuses
A head-to-head "competitive with / approaches / beats SOTA" claim against the FinRL band is **indefensible**:
universe, period, costs, rebalancing cadence, action space, and objective all differ between this study and
every published FinRL number — it is a cross-study, apples-to-oranges comparison (DEEP_BENCH_T4 §0.1, §1). It
is also a **multiple-testing trap with no enumerable family**: with a band spanning ~0.85–1.6 (folk-extending
to ~2.7 on reproducibility noise) one can almost always find *a* FinRL point an arm "beats," and you cannot
FDR-correct a comparison whose family you cannot enumerate (DEEP_BENCH_T4 §5). Worst, the band's own endpoints
are partly **reproducibility noise**: the FinRL ensemble's GitHub issue #190 reports the *same code, same data,
seeds fixed*, Sharpe **0.16 → 2.39** (DEEP_BENCH_T4 §0.2, §2a, verified first-hand there) — a distribution, not
a number.

### 1.2 The rule — restrict "does it work" to the internal matched ladder
"It works" is established, with internal validity, by three rungs the project controls end-to-end, all at
**matched compute, same universe, same period, same costs, inside one pre-registered inference family**
(m=6, BH q=0.05, Romano-Wolf, PBO/CSCV, DSR) — DEEP_BENCH_T4 §3:
- **T0 floor** — winner's median-per-seed DSR > best of 8 classical allocators (DeMiguel 1/N + 7), every
  benchmark paying the same cost (`benchmark_floor`, wired).
- **T1 = H1** — LLM winner > best `REWARD_CANON` hand-reward (the Eureka-style beat-the-human bar; report-only,
  see L16). *(DEEP_BENCH_T4 §3 flags T1 as the binding wiring/precondition gap — it dominates T4 in value.)*
- **T2 = H4** — LLM winner > uninformed search (random-search-over-code, BO-over-template) at matched budget.

The FinRL band enters **only** as a one-paragraph **plausibility ribbon** with the §1.4 caveat block — never
as a tier the project must win.

### 1.3 Struck-phrase / safe-phrase lists (DEEP_BENCH_T4 §3, verbatim governance)
**Struck (never write):**
- "competitive with / on par with / approaches / rivals state-of-the-art DRL"
- "beats FinRL / FinRL-Meta / the SOTA Sharpe"
- "achieves a Sharpe of X, comparable to the SOTA 1.5"
- any plot placing an arm on the same axis as a single FinRL point without the arm's seed-distribution error
  bar AND the "single-draw-from-0.16–2.39" caveat on the FinRL point
- citing the 9.56-on-15-days artifact, any crypto Sharpe, or Jiang-EIIE as a comparator (exclusions)

**Safe (the maximal honest claim):**
- "clears the DeMiguel 1/N floor and the classical-allocator floor at matched transaction cost (T0)"
- "beats the best hand-engineered reward on X% of (seed, window) cells (H1), a direct analogue of Eureka's
  83% beat-the-human result" *(once T1 is wired)*
- "beats uninformed search over the same reward space at matched budget (H4)"
- "for external context, the arms' realised OOS Sharpe falls within the ~0.85–1.6 range the published
  US-equity DRL literature reports and below the >2.0 zone the overfitting literature flags — used to locate
  plausibility, not to rank" *(only if arms are in fact ≥~0.85; else omit the band — see §1.5)*

### 1.4 The "cite-the-band-against-itself" caveat block (must accompany any band appearance)
Any appearance of the band in the PDF must be adjacent to the caveat that the same literature shows the band is
(a) not reproducible to better than ~±a factor of 15 on identical code [FinRL issue #190], (b) un-deflated for
the many trials behind it [Bailey-Borwein-López de Prado-Zhu 2014 `% VERIFY`; Deflated Sharpe, Bailey-López de
Prado 2014], and (c) regime- and cost-dependent (DEEP_BENCH_T4 §2c). The critique is *the reason the comparison
is honest*, not a hedge bolted on afterward.

### 1.5 The negative-prototype-Sharpe DISPLAY LANDMINE (project-specific, DEEP_BENCH_T4 §0.6, §9 P1)
The prototype's realised arm Sharpes are **negative** (best *mean* Sharpe ≈ −0.39, 1 seed, directional-only).
The campaign arms may also land **below** the FinRL ribbon. **Display rule:** make the band plot *conditional*
on the arms landing ≥~0.85; if they are below the credible floor, **omit the ribbon entirely** and report the
absolute result with the DeMiguel framing ("beating 1/N in a bull era is the real bar; a modest absolute Sharpe
is *expected*, not failure"). **Never** plot the arms below a "SOTA" ribbon without that framing — a naive plot
hands the examiner a false "underperforms SOTA" reading. The band is a **ceiling-of-credibility, not a
floor-of-respectability** (DEEP_BENCH_T4 §1): it can rule out the inflated >2.0 fantasy zone; it cannot be
relied on to flatter.

---

## 2. The CONSTRUCT RETITLE: "distribution" → "multi-level tail-risk feedback" (source: `docs/DEEP_H2.md`)

### 2.1 The killer critique it defuses
The *construct* is "the realized-return distribution"; the *operationalisation* is **six left-tail scalars** —
`cvar_05`, `cvar_10`, `cvar_25`, `cvar_01`, `left_tail_mass` (P(r<−2σ)), `robust_skew` (Bowley)
(`src/feedback/measurement.py::tail_stats`, `schema.py::_DIST_FIELDS`; DEEP_H2 §2.1). There is no mode, no
right tail, no full quantile grid, no vol-of-vol, no autocorrelation. An examiner can say, correctly, "you fed
*downside-risk statistics*, not 'the distribution'." Calling six left-tail numbers "the distribution" oversells
the construct and is the easiest construct hit available.

### 2.2 The rule — retitle the construct, state precisely what is and isn't in the vector
Retitle the headline construct from **"distribution"** to **"multi-level tail-risk feedback"** (equivalently
"tail/distributional risk feedback") throughout, and state in one paragraph exactly which six scalars the block
carries and which distributional features it omits (DEEP_H2 §2.1, recommended action #9). This is a
one-paragraph fix that pre-empts the construct attack.

### 2.3 The principled defence (coherent-risk theory — lead with this, do not merely concede)
The choice of CVaR-at-multiple-levels is **not arbitrary**: it is a theory-grounded spanning summary of the
*coherent* risk content of the lower tail (DEEP_H2 §2.1, §9):
- **Artzner-Delbaen-Eber-Heath (1999)** coherence (subadditivity) → CVaR over VaR.
- **Acerbi (2002)** spectral risk measures `% VERIFY` and the **Kusuoka (2001)** representation `% VERIFY`:
  every law-invariant coherent risk measure is a mixture of CVaRs across levels, so a CVaR profile at {1, 5,
  10, 25}% is a principled coordinate basis for the coherent-risk class, not a grab-bag.
- **Rockafellar-Uryasev (2000)** CVaR optimisation/tractability `% VERIFY`.

So the honest framing is: *retitle to "multi-level tail-risk feedback"* (concede the label was too broad), then
*defend the specific six as a coherent-risk-principled tail descriptor* (DEEP_H2 §2.1 calls this the framing to
lead with). Two associated disciplines the same doc requires: the scalar comparator already carries non-
normality information via the DSR, so H2 tests whether *explicit, multi-level* tail feedback adds value beyond a
higher-moment-aware scalar (DEEP_H2 §2.3); and a positive result attributes the effect to the *bundle* versus the
controls, not to any single tail statistic — an interpretability limit to disclose (DEEP_H2 §2.2).

---

## 3. The T0 FAIRNESS DISCLOSURES (source: `docs/DEEP_BENCH_T0.md`)

The classical floor's environment is symmetric and correct (same costed env, same long-only simplex, same
60-day window, same sealed leg — DEEP_BENCH_T0 §1, the floor's strongest feature). The two fairness issues are
*not* in the env; they are in how the deterministic allocators are **driven** and **scored**, and both must be
**disclosed with a specific exhibit**, not assumed away.

### 3.1 The daily-rebalance cost tax (DEEP_BENCH_T0 §4, threat T0-A, HIGH — the doc's most important finding)
**The fact (measured first-hand on the real panel, DEEP_BENCH_T0 §4):** daily re-estimation imposes annualised
cost @10 bps of **0.16%/yr for 1/N** but **3.09%/yr for `mean_variance`** (and 1.7–2.2%/yr for min-var, max-div,
momentum, HRP) — 10–20× more, because the covariance-driven allocators re-estimate every day and trade the
resulting weight jitter. This is **above** the practitioner 0.5–2%/yr band and is **not** how these allocators
are run in the founding literature (DeMiguel-Garlappi-Uppal 2009 use *monthly* rebalancing). **Direction:** it
**flatters the winner** by artificially depressing the sophisticated allocators' floor.

**The disclosure rule:** report a **per-benchmark turnover / annualised-cost table** (the data is already in
`info['turnover']` per step; DEEP_BENCH_T0 §9 item 1). The table must *prove* the **binding** benchmark — the
"best benchmark" the winner is gated against — is a **low-turnover, fairly-costed, diversified risk allocator**
(1/N / risk-parity / inverse-vol at 0.16–0.35%/yr), **not** the 3.09%/yr cost-bled `mean_variance`. Without the
table, "you taxed the benchmarks to death" is unanswerable; with it, the attack collapses. Strongly recommended
companion (DEEP_BENCH_T0 §9 item 3): a **monthly-rebalanced or zero-cost robustness floor** as a clearly-labelled
secondary row (amendment-logged, not a change to the frozen primary gate).

### 3.2 The DSR N=1-vs-N=30 deflation asymmetry (DEEP_BENCH_T0 §5, threat T0-B, HIGH)
**The fact (measured first-hand, DEEP_BENCH_T0 §5):** on an *identical* return path, a benchmark scores
DSR≈**0.89** (deflated by N=1) while the winner scores DSR≈**0.20** (deflated by its N=30 search multiplicity) —
a ~4.5× handicap. This is the **theoretically correct** asymmetry (the winner is the best of a 30-candidate
search, an order statistic that must be deflated; the benchmarks were not searched, so N=1 is right — Bailey-
López de Prado 2014). It is conservative *for a "clears the floor" claim*.

**The disclosure rule (two-edged, DEEP_BENCH_T0 §5, §9 item 2):**
- If the winner **clears** the floor under the asymmetry → lean into it: "even after deflating the winner for 30×
  search multiplicity while giving the benchmarks the full undeflated benefit of the doubt, the winner still
  wins" (the strongest defensible framing).
- If the winner **fails** → it is **not** safe to conclude "the winner is worse"; a substantial part of the gap
  is the 4.5× deflation handicap. The report must **also** show the **undeflated** companion — the winner's
  **N=1 DSR** alongside its N=30 DSR, plus raw Sharpe/CVaR/MaxDD — so the reader separates "lost on performance"
  from "lost on the multiplicity penalty." Hiding the undeflated comparison would be the selective reporting the
  DSR machinery exists to prevent.

**Concretely:** report the winner's undeflated (N=1) DSR alongside the deflated gate in one table
(`winner_dsr_n1 = median_per_seed deflated by N=1`; DEEP_BENCH_T0 §9 item 2 — additive, gate unchanged,
pre-registration-safe).

### 3.3 Two framing-only T0 disclosures that ride along (DEEP_BENCH_T0 §6, §1.1)
- **The 60-day estimation window (T/N=2; T0-C)** is applied **symmetrically** — the agent sees the same 60-day
  information set, so it is *not* a winner-vs-benchmark asymmetry but a statement about *which* benchmarks are
  strong; disclose, do not "fix" by giving benchmarks a privileged longer history (DEEP_BENCH_T0 §6).
- **The deterministic-benchmark "30 seeds" point (T0-D):** benchmarks are deterministic (run once); "30 seeds"
  applies to the *winner's training RNG* only and is reduced to the median per-seed path; the gate is
  median-of-30-winner-paths vs one-benchmark-path — valid, needs one sentence of framing (DEEP_BENCH_T0 §1.1).

---

## 4. Which entries need a PREREGISTRATION cross-reference (for the maintainer to wire)

Listed for the user to wire the prereg amendments; this doc does not touch `PREREGISTRATION.md`.

| Discipline / limitation | Prereg action needed | Source |
|---|---|---|
| **L15 BAB/low-vol attribution** | **Pre-register the FF5+Mom(+BAB) factor ladder as a declared *secondary* family**, headlining the **difference-in-α (distributional − scalar)**; name BAB; pre-empt the post-2018 decay double-edge. *(The single highest-value prereg amendment.)* | DEEP_SYSTEM §S1/G2; DEEP_BENCH_T4 (attribution) |
| **L16 untuned hand-baselines** | **Add one sentence to §1 stating H1 is a descriptive, report-only panel subordinate to H2**, with the search-budget question routed to the H4 controls; disclose canonical-not-tuned. | DEEP_H1 §4.1 / §9 Tier-A item 3 |
| **L17 measurement-noise confound** | **Scope the H2 null to "tail feedback *as operationalised by* an empirical-body + EVT-tail estimator"**; name the placebo + matched-estimator as the bounding controls. *(Wording, no hypothesis change.)* | DEEP_H2 §6.4 / §8 |
| **L18 external-validity scope** | **Insert the single-instance external-validity scope paragraph near the top of §10/Limitations** (cite Liao 2021 `% VERIFY`); scope the abstract to mechanism + method. | DEEP_SYSTEM §3 / §6 P3 item 11 |
| **L19 fixed-SAC on noisy rewards** | **Add the SAC-on-noisy-rewards limitations paragraph** (arXiv:2307.07694 `% VERIFY`; held-fixed → differenced out → no absolute SOTA claim). | DEEP_BENCH_T4 §8 / §9 P1 |
| **§1 No-SOTA discipline** | **Freeze the Tier-4 framing as "plausibility ribbon, never ranking"** in the prereg/benchmarks doc — the struck/safe phrase lists (§1.3) verbatim; the headline stays comparative (§10). | DEEP_BENCH_T4 §9 P0 |
| **§3 T0 fairness exhibits** | **If the headline floor gate is already frozen, add the monthly/zero-cost robustness floor as an *amendment-logged secondary* row** (the per-benchmark turnover table and the undeflated-DSR column are additive report-only, gate unchanged). | DEEP_BENCH_T0 §9 items 1–3 |

---

## 5. Provenance
First-hand sources, all read this session and authored by the deep red-team agents (who verified their own
code/config/literature claims first-hand, file/line cited within each): `docs/DEEP_SYSTEM_redteam.md`
(§S1/G2 BAB, §3/S6 external validity), `docs/DEEP_H1.md` (§4.1 T-UNTUNED, §9 Tier-A), `docs/DEEP_H2.md`
(§2.1 construct retitle + coherent-risk defence, §6.4 measurement-noise confound), `docs/DEEP_BENCH_T4.md`
(§0–§3 no-SOTA, §2c caveat block, §0.6/§9 display landmine, §8 SAC), `docs/DEEP_BENCH_T0.md` (§4 T0-A cost
tax, §5 T0-B deflation asymmetry, §6 T0-C, §1.1 T0-D), and `00_planning/LIMITATIONS_REGISTER.md` (L1–L14
format mirrored; L15–L19 added in lockstep with this doc). Literature not re-verified in this session is
marked `% VERIFY` per CLAUDE.md prime directive 4. No code, config, or pre-registration was modified.
