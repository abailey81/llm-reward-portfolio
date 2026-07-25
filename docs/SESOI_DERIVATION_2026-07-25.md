# SESOI derivation — from asserted to grade-A (2026-07-25, A4 / R104)

**Problem (both backbone auditors, the #1 grade-capping link):** the equivalence backdrop hung on an
**asserted** SESOI (0.05 DSR), with no derivation, a unit-mismatch (margin in val-DSR, headline test in
test-Sharpe), and an **unregistered** CVaR-tail margin. This document DERIVES the SESOI from the real
panel + the economic primitives, so the linchpin is grade-A, not fiat. All numbers computed first-hand
from `data/gold/returns_panel_univ5` (equal-weight book, the registered T0 benchmark).

## The three anchors (a defensible band, not a point guess)
The SESOI = the smallest performance difference (distributional-fed vs scalar-fed arm) that would be
**materially of interest** — bracketed below by economic exploitability and above by practitioner relevance.

1. **Lower bound — transaction-cost breakeven (exploitable-after-costs).** Our environment charges
   `c = 10 bps` one-way turnover cost. The equal-weight book runs **σ = 20.2%/yr** and **112%/yr one-way
   turnover** (measured), so the annual cost drag is `10bps × 112% = 0.112%/yr`. A Sharpe edge whose
   annual return is smaller than that drag is un-exploitable → the breakeven floor is
   `0.112% / 20.2% = 0.0055 ann-Sharpe`. **A difference below 0.0055 Sharpe is economically null.**
2. **Upper bound — practitioner-material scale.** The portfolio-choice literature (DeMiguel, Garlappi &
   Uppal 2009, "Optimal Versus Naive Diversification: 1/N is hard to beat") places *materially
   distinguishable* Sharpe differences at ~**0.10–0.20 ann-Sharpe**. A difference a practitioner would
   *act on* (deploy the tail-feedback feature over the scalar) lives at or above this scale.
3. **Statistical reference — Harvey-Liu t>3 (multiple-testing hurdle).** Over the ~12-year fed window the
   t>3 absolute-Sharpe hurdle is ≈0.87 (a reference for a "real" effect under multiple testing, Harvey,
   Liu & Zhu 2016), corroborating that our SESOI is deliberately *sub-significance* (a strict equivalence).

## The verdict
The registered **SESOI = 0.05 DSR ≈ 0.0756 ann-Sharpe** sits INSIDE the defensible band:
- **13.7× ABOVE** the cost-breakeven floor (0.0055) → any smaller difference cannot be exploited after
  costs → economically negligible ⇒ correctly "of no interest";
- **conservatively BELOW** the practitioner-material floor (0.10) → we are NOT calling a
  practitioner-relevant edge "negligible"; the equivalence claim is strict, not permissive.

So 0.05 DSR is the **smallest edge that is simultaneously exploitable-after-costs and conservative** — a
principled, DERIVED threshold, not an assertion. (The value is retained; what changes is that it is now
*justified*.)

## Two registration fixes that ship with the derivation (R104)
1. **Unit consistency (native DSR).** The SESOI is on the DSR scale; the H2-RA co-primary is therefore
   run as a **TOST natively in val-DSR units** against ±0.05 DSR (not converted through Sharpe), removing
   the val-DSR-vs-test-Sharpe mismatch. Equivalently, where a Sharpe-scale reading is reported it is
   labeled bounded-effect-only, in Sharpe units, with the delta-method map disclosed.
2. **Register the tail margin.** The H2-Tail equivalence margin — the fractional CVaR band **0.25 ·
   |scalar-arm CVaR-5%|** — was prose-only (a forking path). It is now pinned as a **frozen numeric** in
   `config/preregistration.yaml` (`h2_tail_equivalence_margin_frac: 0.25`) so both halves of the
   equivalence are hash-bound before freeze.

## Power consequence (ties A4 → A2)
MDE ∝ 1/√n; MDE@30 ≈ 0.120 DSR. The equivalence becomes achievable (MDE < SESOI = 0.05) at
**n\* ≈ 173 seeds**. So at the fair-share floor (~100–189) it is borderline, and at the CPU-lane reach
(~280–400) it is comfortably achievable. **Driving the seed rung (A2) and the derived SESOI (A4) close
the equivalence gap together.** Below n\*, the Sharpe co-primary is reported honestly as *inconclusive*
(the bounded-effect CI is the deliverable); never assert "equivalence" below the achieved-rung power.

## Reproduce
`python D:/…/scratchpad/sesoi_inputs.py` (equal-weight book from the frozen panel; σ, turnover,
cost-breakeven, n\* all recomputed). Numbers above are the 2026-07-25 run.
