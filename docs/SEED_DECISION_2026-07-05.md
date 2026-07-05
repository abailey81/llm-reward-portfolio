# The seed-count decision — precise analysis for ratification (2026-07-05)

**Bottom line (recommendation unchanged, now independently re-derived and sharpened):**
**arm-adaptive seeds — `distributional` = `scalar` = seeds 0..349 (n=350); every other arm + H1 baselines +
H3 single-shot = seeds 0..29 (n=30).** Sized by **equivalence-test (TOST) power at the SESOI, evaluated at
the 90% χ² upper confidence bound of the pilot σ_D**, with the seed pilot being **effect-blind** (it compared
two hand-written rewards, so it carries zero information about any H2 contrast — textbook legitimate
nuisance-parameter re-estimation, no forking paths). SESOI, arms, candidate budget, splits, λ, B\* all
unchanged. One coordinated amendment + ONE hash move. **~23-day campaign; every day past ~Jul 10 eats the
write-up buffer 1:1.**

---

## 1. What the pilot established (all numbers re-verified this session)

| Quantity | Value | Check |
|---|---|---|
| σ_seed (per-seed SD of test ann-Sharpe, fixed reward) | 0.244 | pilot JSON |
| σ_D (SD of per-seed Sharpe DIFFERENCE, 15 CRN pairs) | **0.369** | internally consistent: σ_D² = 2σ²(1−ρ) = 2·0.244²·1.141 → 0.369 ✓ |
| ρ (CRN pairing correlation, Sharpe) | −0.141 (n.s. at n=15; 95% CI ≈ [−0.6,+0.4]) | ADD-3: a one-line methods note, never mechanism evidence |
| cvar_05 leg | σ_D = 0.0015, ρ = +0.47 | the tail leg is tight — see §5 |
| MDE @ 30 seeds | 0.181 ann-Sharpe ≈ 0.120 DSR | vs SESOI 0.05 DSR — 2.4× short |
| SESOI crossing (point σ̂_D) | n ≈ 189 | authoritative MC tool |
| Powering at the χ² upper CI of σ_D (df=14) | 80%→279 · **90%→340** · 95%→403 | re-derived exactly: σ_up = σ̂·√(14/χ²_{γ,14}) → factors 1.216/1.341/1.460; 189×factor² = 279/340/403 ✓ |

The pre-registered "30→50 if σ_D>0.10" band is dead on arrival: σ_D=0.369 fires it, and **even n=50 gives
MDE ≈ 0.055 DSR > SESOI**. `determine_design` now correctly BLOCKS on n_seeds until the amendment lands
(fixed 2026-07-05).

## 2. Get the criterion exactly right (this is where precision matters)

Three different "n"s get conflated; the amendment must name the right one:

- **(i) Superiority power** (detect a true SESOI-sized effect, one-sided 80%): n = ((z₀.₀₅+z₀.₂)·σ_D/δ_S)²
  ≈ **148** at point σ̂_D (δ_S = SESOI mapped to Sharpe units ≈ 0.05/0.663 ≈ 0.0754; k=0.663 at T=694).
- **(ii) TOST equivalence power at true-zero** (the branch we PREDICT): declare equivalence iff
  |D̄| ≤ δ − 1.645·SE, so P(declare | true 0) = 2Φ(δ/SE − 1.645) − 1 → 80% needs δ/SE = 2.93 → n ≈ **205**;
  90% needs δ/SE = 3.29 → n ≈ 259 (point σ̂_D). **This is the criterion that matters** — the deliverable is
  the equivalence statement, and it is *more* demanding than superiority power.
- **(iii) Pure AIPE** (expected CI half-width ≤ δ): n ≈ 65–80 — too weak (a CI can be narrow yet sit
  half-outside the margin); do **not** size by this, only *name* AIPE as the precision-criterion family
  (ADD-2 wording: "a precision criterion distinct from, and here more demanding than, power" — keep, but the
  amendment states the exact rule below).

The committed MC tool's n≈189 sits between (i) and (ii) because it simulates the REAL pipeline (IQM trimming,
paired bootstrap, IUT) rather than the normal approximation — treat the tool as authoritative and my closed
forms as the sanity band (140–260 ✓).

**The rule to register verbatim:** *"The winner-seed count for the two TOST-registered arms is chosen so the
pre-registered TOST (90% CI within ±0.05 validation-DSR) declares equivalence with ≈90% probability when the
true difference is zero, with σ_D evaluated at the upper 90% χ² confidence bound of the 15-pair pilot estimate
(0.369 → 0.449): n = 340, rounded to 350 as an operational buffer for failed seed-trainings. The analysis uses
the intersection of successfully completed shared seeds; a shortfall below 340 shared pairs is disclosed."*

## 3. Why this is severity-clean (the examiner defence — put it in the amendment AND the paper)

1. **Effect-blind by construction.** The pilot compared `differential_sharpe` vs `return_minus_cvar` — two
   hand-written rewards, neither an arm contrast. It reveals *nothing* about the direction or size of any H2
   effect. Re-sizing n on a **nuisance parameter** (σ_D) estimated from effect-blind data is the classic
   internal-pilot design (Wittes–Brittain class); it does not touch Type-I error and is not a forking path.
2. **SESOI untouched.** Adapting the *margin* to the pilot would be a moved goalpost; adapting *n* to hit the
   pre-registered margin is the opposite — it protects the original question. (Explicitly rejected: raising
   the SESOI.)
3. **Both branches stay pre-committed.** If realized campaign σ_D > pilot, the TOST CI is wider → the
   pre-committed bounded-effect branch; if smaller → tighter equivalence. Validity never depends on the pilot
   being right; only *achievability* does — the upper-CI sizing is insurance on achievability.
4. **Honest proxy caveat.** The pilot's two hand rewards proxy the unknown LLM-authored winners; the upper-CI
   buffer partially covers proxy error, and the caveat is disclosed rather than hidden.
5. **σ_seed-dominance stays a first-class finding** (ADD-1): we *measured* that seed noise is ~3× the SESOI
   and then *powered through it* — a stronger story than either ignoring it or surrendering to it.

## 4. Why arm-adaptive (and its disclosed asymmetries)

The registered TOST is **distributional vs scalar only** (R12). Powering only those two arms costs
(350−30)×2 = 640 extra trainings ≈ 906 GPU-h ≈ ~12.6 wall-days at 3 workers; uniform-350 across 7 arms would
add ~5×320 more and blow past 1 Sep. Controls at 30 remain valid for their roles:

- **IUT legs 2/3** (dist>placebo, dist>scalar_cvar5) pair on the 30 shared seeds (0..29 ⊂ 0..349 — CRN
  preserved by making the control seed set a SUBSET). Under the predicted null they simply don't reject. Under
  a surprise positive, legs 2/3 at n=30 are less powered → the conjunction gets *harder* to pass → the
  asymmetry biases AGAINST declaring H2 supported = conservative. **Disclose this in the amendment.**
- **H3** (iterative-vs-single-shot) pairs at 30 — report-only with a TOST bound that stays wide; consistent
  with its pre-committed descriptive role. Disclose.
- **H1 baselines / placebo_shuffled / search arms**: descriptive/report-only → 30.

## 5. The tail leg is already paid for

cvar_05 σ_D = 0.0015 with ρ=+0.47: at n=30 the 90% CI half-width ≈ 1.645·0.0015/√30 ≈ 0.00045 — comfortably
inside even the honest **fractional** tail margin (0.25·|scalar CVaR| ≈ 0.0125), let alone the registered raw
±0.05. So H2-Tail precision needs NO extra seeds; the Sharpe leg is the only expensive one — which is exactly
why arm-adaptive works. (This also makes resolving the M11 tail-margin registration in the same amendment the
right move: with the fractional margin registered ex-ante, the tail equivalence claim is both honest and
achievable at n=30.)

## 6. What must be ENGINEERED before this can freeze (the A-F3 gap — real work, do carefully)

The ~350 sizing is **not yet implemented in code**; ratification is not just editing numbers:

1. **Per-arm seed schema** — `config/campaign.yaml` today has ONE flat `seeds: [0..29]`; the driver, the
   TEST-leg farmer, and the freeze gate all assume it. Needs e.g. `seeds` (default) + `seeds_h2:` (or
   `seeds_by_arm:`) read by `run_campaign`'s test leg, with controls' set a strict subset of the H2 set.
2. **Freeze-gate updates** — two checks currently assert "seeds n=30 == prose"; they must assert the NEW
   structure (H2 arms 350 / controls 30) against the amended prose + yaml mirrors.
3. **`estimate_seed_count` fold-in (P18)** — the χ² upper-CI sizing must live in committed, tested code
   (`sigma_seed_pilot.py`/`power_analysis.py`), not a changelog sentence; regenerate `docs/CAMPAIGN_power.md`
   from the fixed generator (M02) so the doc is reproducible.
4. **`determine_design` evidence read** — my 2026-07-05 gate reads `len(campaign.seeds)`; under a per-arm
   schema it must read the H2-arm count (else it stays PENDING forever).
5. **Paired-intersection checks** — verify `paired_seed_difference_test`/analyze paths take seed
   intersections (350∩350, 350∩30) as expected; add a small test for the asymmetric case.
6. **Prereg amendment (dated, e.g. D3/R77)** — §6 + §12 prose + `preregistration.yaml` mirror; batch with the
   other agreed hash-bound items (tail-margin registration, R76 wording, gate guards) into **ONE hash move**.
7. Re-run: full freeze `--check`, targeted tests, `determine_design` (must flip to FREEZE-READY truthfully).

Estimated effort: ~half a day of careful implementation + tests. **Do not freeze until 1–7 are green.**

## 7. Explicitly rejected alternatives (record, so they're never re-litigated)

- **Stay at 30** — pre-pilot it was defensible ignorance; post-pilot it is a *knowing* choice to run an
  underpowered design when a feasible fix exists. MDE 0.120 vs SESOI 0.05; the equivalence branch dies. Reject.
- **n=50** (the old band's ceiling) — MDE ≈ 0.055 DSR, still misses the SESOI. Reject.
- **Uniform 350 across all arms** — ~2× the campaign; misses 1 Sep. Reject.
- **95% assurance (n=403)** — +3 days for a modest gain over 90%. Reject (ceiling stays ~400 if Tamer wants it).
- **80% assurance (n=279)** — saves ~4 days but a 1-in-5 chance the design under-delivers the precision it was
  sized for. Reject.
- **Adaptive/sequential (run 150, look, extend)** — optional stopping without a pre-registered group-sequential
  design = the forking-paths trap; would taint the severity story. Reject.
- **Raise the SESOI** — a moved goalpost, the exact sin the pre-registration exists to prevent. Reject loudly.

## 8. Schedule reality

Ratify + engineer (~0.5–1 d) → freeze (~Jul 8–10) → 23-day campaign → done ~Jul 31–Aug 2 → analysis ~1 wk →
write-up to ~Aug 25 → submit ~Aug 29. Feasible with near-zero slack: **the seed decision is the critical path,
and delay converts 1:1 into lost write-up days.** Okhrati's advice was requested in the sent email; given the
clock, the defensible move is to ratify now and note to him that the schedule required proceeding, with the
design adjustable on his advice up to the freeze.

8. **Paper prose sweep (2026-07-06 review):** update every hard-coded 'thirty seeds/30-seed' statement in the GRADED chapters to the ratified arm-adaptive design — CH2:68, CH4:215, CH4 Table 4.1 row ('Thirty seeds'), CH5:65, CH5:75, APPENDIX_B:33 (B.2.4), CH6:32 fill-hint — plus the MDE numbers keyed to n=30. The freeze gate asserts prereg prose only; without this item the Methods chapter would describe a design the run ledger contradicts.
