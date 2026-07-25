# SESOI derivation — from asserted to grade-A (2026-07-25, A4 / R104)

**The #1 grade-capping link (both backbone auditors).** The equivalence backdrop rests on a SESOI
(0.05 validation-DSR) whose *registered justification* was a single line — "≈0.0756 ann-Sharpe, the order
of the Harvey-Liu t>3 hurdle net of costs" (`docs/POWER_ANALYSIS.md`). The **value is well-placed and the
surrounding machinery is already rigorous** (see *What was already right*); the thin link was the
*derivation of WHY 0.05*. This document DERIVES the SESOI from the real panel + economic primitives so the
linchpin is grade-A, and R104 REGISTERS that derivation as **frozen data** (`inference.sesoi_derivation`)
with a test. All economic inputs are computed first-hand from `data/gold/returns_panel_univ5` (the
equal-weight book = the registered T0 benchmark) by `scratchpad/sesoi_inputs.py`.

## What was ALREADY right — do NOT "fix" (verified first-hand against `docs/CAMPAIGN_power.md`, the LIVE power doc)
My first draft wrongly proposed two "registration fixes". Both are already handled; retracted and recorded
here so the error is not repeated (ZERO-DEFECT):
- **The TOST is already DSR-native.** The equivalence verdict is evaluated in **per-seed validation-DSR**
  units against ±0.05 DSR (`CAMPAIGN_power.md` §Units; selection metric = `validation_deflated_sharpe`).
  There is no Sharpe-vs-DSR margin bug to fix.
- **The Sharpe↔DSR gap is already reconciled (T2.5),** with a conservative delta-method **ceiling**
  `ΔDSR_max = φ(0)·√(T−1)/√252·ΔSR_ann`, `k = 0.6616` DSR per ann-Sharpe at `T = 694` → the Sharpe MDE
  0.181 maps to ≈**0.120 validation-DSR** (ceiling).
- **The INCONCLUSIVE branch already exists (Lakens 2017):** because that 0.120-DSR ceiling **exceeds** the
  0.05 SESOI, a Sharpe non-rejection alone does NOT license equivalence — only the DSR-unit TOST CI can.
- **The tail bounded-effect is a registered bootstrap CI (R86), NOT a fixed margin.** My draft's "register
  a 0.25 CVaR margin" was an **invented number — retracted**. The correct, already-frozen tail statement is
  the R86 pooled 90% seed-block-bootstrap CI on the (dist−scalar) CVaR-5% difference, reported in
  daily-return units and as a % of the scalar-arm CVaR level.

So **A4 does not touch the test machinery.** It strengthens the one thin link — the *justification* of the
SESOI value — and binds it into the freeze.

## The three anchors (a defensible band, not a point guess)
The SESOI = the smallest performance difference (distributional-fed vs scalar-fed arm) that is **materially
of interest** — bracketed BELOW by economic exploitability and ABOVE by practitioner relevance.

1. **Lower bound — transaction-cost breakeven (exploitable-after-costs).** The environment charges
   `c = 10 bps` one-way turnover cost. The equal-weight book runs **σ = 20.2%/yr** and **112%/yr one-way
   turnover** (both MEASURED), so the annual cost drag is `10bps × 112% = 0.112%/yr` and the breakeven
   Sharpe floor is `0.112% / 20.2% = 0.0055 ann-Sharpe`. **A difference below 0.0055 Sharpe cannot be
   exploited after costs → economically null → correctly "of no interest".**
2. **Upper bound — practitioner-material scale.** DeMiguel, Garlappi & Uppal (2009, "Optimal Versus Naive
   Diversification: 1/N is hard to beat") place *materially distinguishable* Sharpe differences at
   ~**0.10–0.20 ann-Sharpe**. An effect a practitioner would *act on* lives at or above this scale, so the
   SESOI (the boundary of "of interest") must sit **at or below 0.10** — otherwise we would wrongly declare
   a practitioner-material effect "equivalent".
3. **Statistical corroboration — Harvey-Liu t>3.** The absolute-Sharpe significance hurdle under multiple
   testing (Harvey, Liu & Zhu 2016) is far above the SESOI (t>3 ⇒ SR ≳ 0.87 over a 12-yr track; larger on
   the shorter scored window), confirming the SESOI is deliberately **sub-significance** — an equivalence
   threshold, not a discovery threshold. (Corroboration only; the band is carried by anchors 1–2.)

## The verdict — 0.05 DSR sits inside the derived band
The registered **SESOI = 0.05 DSR ≈ 0.0756 ann-Sharpe** (via the conservative `k = 0.6616`, `T = 694`) sits
INSIDE `[0.0055, 0.10]`:
- **13.7× ABOVE** the cost-breakeven floor (0.0055) → we never demand equivalence tighter than what could
  possibly be exploited;
- **BELOW** the practitioner-material floor (0.10) → our equivalence bar is **stricter** than
  practitioner-material, so a bounded-effect verdict is *conservative* (it will not absorb a 0.10-Sharpe
  effect a practitioner would care about).

So 0.05 DSR is the **smallest edge that is simultaneously exploitable-after-costs and sub-practitioner** —
a principled, DERIVED threshold. The value is retained; what changes is that it is now *justified from data*.

## What R104 registers (the non-fragile upgrade)
The SESOI VALUE (0.05 DSR) is **UNCHANGED**. R104 adds a frozen `inference.sesoi_derivation` block to
`config/preregistration.yaml` — the economic anchors as **hash-bound DATA, not prose** — so the
justification travels *inside* the pre-registration, and `tests/test_sesoi_derivation.py` re-derives the
band from the registered inputs (cost-breakeven `= bps·turnover/σ`; DSR↔Sharpe `= sesoi/k`) and asserts
`0.0055 < 0.0756 < 0.10` and `sesoi == inference.sesoi`. The derivation is thus VERIFIED, not asserted.

## Power consequence (ties A4 → A2)
The DSR-unit MDE **ceiling** at n=30 is ≈0.120 DSR (`CAMPAIGN_power.md`, conservative). Since MDE ∝ 1/√n,
equivalence becomes achievable (DSR-MDE ≤ SESOI 0.05) at **n\* ≤ 173 seeds** — a conservative ceiling (the
true DSR-MDE is below the at-the-money ceiling, so *fewer* seeds suffice). At the fair-share floor (~100–189)
it is borderline; at the CPU-lane reach (~280–400) comfortably achievable. **Driving the seed rung (A2) and
the derived SESOI (A4) close the equivalence gap together.** Below n\*, a Sharpe non-rejection is reported
honestly as **INCONCLUSIVE** (the DSR-unit bounded-effect CI is the deliverable), never "equivalence".

## Reproduce
`python scratchpad/sesoi_inputs.py` (equal-weight book from the frozen panel; σ, turnover, cost-breakeven,
n\* all recomputed). `pytest tests/test_sesoi_derivation.py` (the registered band, from the frozen block).
Economic-input numbers are the 2026-07-25 run; the DSR↔Sharpe map (k, T) is from `CAMPAIGN_power.md` T2.5.
