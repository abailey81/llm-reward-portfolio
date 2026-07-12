# Communication-dimension build — DRAFTS FOR TAMER'S REVIEW (2026-07-12)

> **Status: NEW draft prose/specs, not yet wired into any chapter.** Per the handoff §4 build plan and
> the deep-analysis §5: these are the four highest-EV dimension-4 artifacts, drafted under the
> delegated full permission. Nothing existing was rewritten; hash-bound files untouched. Numbers
> marked ⟨CAMPAIGN⟩ are placeholders the bank gate fills; every other number is real and sourced.

---

## D1. The plain-language contribution paragraph (the 60-second version — before any formalism)

> When people ask an AI to write software that pursues a goal, the goal itself has to be written down
> as a score the software optimises — and in investing, the score that matters most is the one that
> captures rare, catastrophic losses, not average performance. This dissertation asks a simple
> question with an uncomfortable answer: **if you show the AI detailed information about those rare
> losses, does it actually *use* that information when it writes the score?** We built a controlled
> experiment where everything is held identical — the market data, the learning algorithm, the
> budget — except the *risk information shown to the AI*, and we registered every prediction and
> decision rule in advance, so the result cannot be massaged after the fact. The answer we test for,
> and the mechanism behind it, matter far beyond finance: modern AI systems are increasingly asked to
> act on numerical evidence, and we measure — perhaps for the first time under pre-registered
> controls — whether one can tell, from the code an AI writes, that the numbers it was shown ever
> entered its reasoning.

*(Okhrati checks: no jargon; the any-discipline second marker gets the design's point (controlled +
pre-registered) and the stake (do AIs use numerical evidence) without one formula.)*

## D2. The outward contribution sentence (abstract-grade; the grade-audit's positioning lever)

> We give the first theory-grounded, pre-registered test of whether an LLM reward-designer is a
> **Bayes-responsive user of risk information**: whether the *content* of distributional feedback —
> not its format, length, or vocabulary — changes the reward code the model writes, and whether that
> change propagates to the trained agent's realised tail behaviour. The question instantiates the
> general "do LLM optimizers use feedback content?" problem in the one arena where the answer is
> checkable against decision theory, with portfolio construction as the testbed rather than the
> object: an information-theoretic envelope says the fed tail vector *cannot hurt* and generically
> helps a Bayes-responsive designer, so a pre-registered null cleanly localises a failure of
> responsiveness — which we trace mechanistically ⟨CAMPAIGN: to the first link of the chain, a
> numeracy/legibility bottleneck adjudicated among five registered rival accounts⟩.

## D3. The 3-link mechanism figure — full spec (the paper's spine as one image)

- **Layout:** one horizontal chain, four boxes, three labelled arrows; a red "cut" glyph on arrow 1
  ⟨CAMPAIGN: position per the measured SQ1⟩.
  `[fed tail signal] —SQ1: responsiveness→ [authored reward CODE] —SQ2: mediation→ [trained policy] —→ [realised tail outcome]`
- **Box annotations (small, under each):** fed signal = "6 tail statistics, e.g. CVaR-5% = −0.0305"
  (real archived value); code = "the reward function the LLM writes (AST-audited)"; policy = "fixed
  SAC agent, 200k steps"; outcome = "out-of-sample CVaR-5% across 568-seed ladder".
- **Arrow annotations:** SQ1 carries "Spearman ρ = ⟨CAMPAIGN⟩ [CI]"; SQ2 carries "indirect effect
  a·b = ⟨CAMPAIGN⟩ [CI]"; arrow 3 carries "co-primary H2-Tail IUT".
- **The cut:** a break symbol on the SQ1 arrow with the caption line: *"the chain is severed at its
  first joint: the fed numbers do not reliably enter the code"* ⟨conditional on the predicted null⟩.
- **Alt outcome discipline:** if SQ1 > 0, the same figure renders with the cut moved (or absent) —
  the figure is outcome-neutral scaffolding, built once, filled at the bank gate.
- Render: TikZ or draw.io→PDF; grayscale-safe; caption ≤ 3 sentences; referenced from CH1 AND the
  mechanism chapter (Okhrati: tidy cross-referencing).

## D4. Limitations subsection — scaffold (the exemplar practice; his 5/5 register)

Order: honesty first, each with the mitigation in the same breath; no defensive tone.

1. **Endogeneity of the fed signal.** The tail vector is measured on the trained policy's own
   realised returns — two coupled reward→policy→measurement loops, never an exogenous measurement;
   "critic-agnostic" is not "agent-independent". Mediation (SQ2) is therefore reported as a
   descriptive decomposition under sequential-ignorability caveats, never causal proof.
2. **Search width.** 30 candidates, K = 5 per generation, one serial chain per arm: the mechanism
   claim is about *this* design regime; U2b-style multi-chain replication is named future work.
3. **Tail-estimator variance at the extreme level.** CVaR-1% is EVT-extrapolated from few
   exceedances; flagged high-variance everywhere it appears; the fed-signal SNR exhibit
   (instrument (h)) quantifies exactly which fed components carried resolvable signal.
4. **Statistical conventions.** Annualised Sharpe assumes i.i.d. (Lo 2002) — descriptive only; all
   inference is the per-seed paired bootstrap. ρ(seed-pairing) = −0.141 is not significant — a
   methods note, not evidence.
5. **Single market, single cohort.** 30 US large-caps, 2005 PIT cohort held fixed for train/test
   consistency (composition bias stated; the 2020-cohort PIT robustness re-evaluation is the
   registered check). One replication family (Qwen) probes model-generality; broader markets are
   future work, deliberately not padded in.
6. **Single-look cross-period design.** One sealed test window (2020–2026H1) evaluated once at the
   exogenous ladder rung; per-regime slices are reported descriptively, never re-tested.
7. **The prototype is not evidence.** The Sonnet prototype (single-seed, 18 h) shaped engineering
   only; no prototype number appears anywhere in the results.

## D5. The worked micro-example (real archived data; the numeracy bottleneck made concrete)

> In generation 7 the designer was shown, for two sibling candidates, fed CVaR-5% values of
> **−0.0305** and **−0.0307** (archived records `distributional-g7-c3/c4`; Δ = 0.00014). Two decimal
> places in, the difference looks like noise — but because every candidate is evaluated on the *same*
> market path, the paired sampling floor at this horizon is ≈ 1×10⁻⁴ ⟨instrument (h), calibrated
> mode⟩: this gap is at the edge of genuine signal, and deeper components in the same records
> (CVaR-1%: −0.0548 vs −0.0522, Δ = 0.0026) are *unambiguously* resolvable. A Bayes-responsive
> designer should treat those numbers differently. What the designer actually wrote next
> ⟨CAMPAIGN: the authored diff + the reflection's funnel coding for this turn⟩ is the mechanism
> question in miniature — and the LLM-numeracy literature predicts precisely this regime
> (close small decimals) is where frontier models' comparisons become unreliable.

---
*Next in the build order (handoff §4): the M2 survey figure slot; the scannable tables (CVaR-leg
conclusiveness, assurance ladder, ablation). Queued behind Tamer's review of D1–D5.*
