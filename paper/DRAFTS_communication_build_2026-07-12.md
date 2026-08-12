# Communication-dimension build — DRAFTS FOR TAMER'S REVIEW (2026-07-12)

> **Status UPDATE (2026-07-13, delegated permission): D1 -> CH1 (plain-terms paragraph), D2 -> FRAMING §4
> (softened "first" -> "to our knowledge" per the honesty register), D3 -> BUILT (`schematics.mechanism_chain`,
> manifest row F10), D4 -> reconciled into APPENDIX_B (new B.2.0 endogeneity, B.5.6 conventions incl. verified
> `lo2002statistics`, B.5.7 single-look, B.6.6 prototype-not-evidence; K=5/cohort/CVaR-1% were already covered).
> ⚠ D5 DEFERRED BY RULE: it quotes real PROTOTYPE numbers and the standing rule is that no prototype number
> enters the dissertation — it will be re-instantiated verbatim-in-form from CAMPAIGN sibling records at the
> bank gate. Original status:**NEW draft prose/specs, not yet wired into any chapter. Per the handoff §4 build plan and
> the deep-analysis §5: these are the four highest-EV dimension-4 artifacts, drafted under the
> delegated full permission. Nothing existing was rewritten; hash-bound files untouched. Numbers
> marked ⟨CAMPAIGN⟩ are placeholders the bank gate fills; every other number is real and sourced.

---

## D1. The plain-language contribution paragraph (the 60-second version — before any formalism)

> When people ask an AI to write software that pursues a goal, the goal itself has to be written down
> as a score the software optimises — and in investing, the score that matters most is the one that
> captures rare, catastrophic losses, not average performance. This dissertation asks a simple
> question with an uncomfortable answer: **if you show the AI detailed information about those rare
> losses, does it actually *use* that information when it writes the score?**We built a controlled
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
  SAC agent, 400k steps (B\*, R77)"; outcome = "out-of-sample CVaR-5% across the seed ladder".
- **Arrow annotations:** SQ1 carries "Spearman ρ = ⟨CAMPAIGN⟩ [CI]"; SQ2 carries "indirect effect
  a·b = ⟨CAMPAIGN⟩ [CI]"; arrow 3 carries "co-primary H2-Tail IUT".
- **The cut:** a break symbol on the SQ1 arrow with the caption line: *"the chain is severed at its
  first joint: the fed numbers do not reliably enter the code"*⟨conditional on the predicted null⟩.
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

# RAISED-BAR BUILD (2026-07-21) — registry rows 18–23 drafted; grade-inflation adjustment
# (supervisor-confirmed: last year's distinction ≈ this year's merit — every dimension needs
# unambiguous evidence). D6–D10 below are NEW drafts for Tamer's review; nothing existing rewritten.

## D6. The SESOI justification paragraph (registry row 19 → CH4, beside the TOST spec)

> The equivalence margin of ±0.05 Sharpe units is not a statistical convenience but a materiality
> threshold, chosen before any data on three grounds. First, decision-relevance: the question a
> practitioner brings to this study is whether building a distributional-feedback pipeline is worth
> its engineering and maintenance cost, and an improvement smaller than 0.05 annualised Sharpe —
> roughly the effect of a few basis points of execution slippage — would not survive that
> cost–benefit comparison in any allocation process we are aware of. Second, operational
> resolvability: run-to-run seed variation in this training regime is measured at σ ≈ 0.24 Sharpe
> units, so an effect below one-fifth of that noise floor could not be exploited reliably by a
> deployer even if it existed, because detecting it would require more independent training runs
> than any production pipeline performs. Third, conservatism relative to the literature: published
> strategy improvements that survive selection-aware deflation are typically an order of magnitude
> larger; halving the smaller of those figures errs on the side of calling small-but-real effects
> inconclusive rather than dismissing them. The margin is symmetric because neither direction of
> deviation is privileged ex ante.

*(Raised-bar purpose: converts the one assertable number in the confirmatory spec into an argued
one — the exact class of borderline item a harsh marker rounds down.)*

## D7. H4 prominence + the Coache–Jaimungal differentiation (registry row 20)

**(a) CH2 differentiation paragraph:**

> Distributional risk objectives inside reinforcement learning are not new: Coache and Jaimungal,
> in particular, optimise dynamic risk measures directly within the learning algorithm, treating
> the *agent* as the object of design. This dissertation holds the agent fixed and asks a question
> that line of work does not: when the reward function itself is *authored by a language model*,
> does the risk information shown to the author change what it writes? The distributional content
> therefore enters one step earlier in the pipeline — at the specification stage, through a
> natural-language-and-numbers interface — and the appropriate comparison class is not a better
> risk-sensitive algorithm but a better *reward search*: hence the matched-compute random-search
> and Bayesian-optimisation arms. No published work, to our knowledge, has tested whether an LLM
> reward-designer outperforms matched non-LLM search at all — so hypothesis H4 is not a robustness
> check but the empirical answer to whether the LLM layer earns its place in this pipeline.

**(b) CH6/CH7 framing note (write-time):** H4 is a NAMED result with its own table row and
paragraph, both branches meaningful — an edge is the lineage's first such evidence; no edge is an
honest boundary that the mechanism chapter explains. Never bury it as a secondary footnote.

## D8. The independence narrative (registry row 22 → CH1 close or CH7 opening; ~120 words)

> The design reported here is the product of a documented sequence of the author's decisions. A
> February proposal sketched a ten-component system; it was deliberately narrowed — a shift the
> module guidelines explicitly sanction — to the single identified question a controlled experiment
> could answer to depth. That design was frozen, hash-bound, as version 1.0. When industry
> supervisors subsequently challenged its model coverage and reproducibility permanence, the
> registration was unfrozen *before any data existed*, revised into the ten-model design, and
> re-frozen with every change recorded as a dated amendment — the pre-registration discipline
> working as intended rather than being worked around. The amendment table (R1–R88) and the
> decision log are appended in full: each records what changed, why, and on whose call.

*(Raised-bar purpose: under an AI-assistance disclosure, this paper trail — pivot, freeze,
feedback, documented pre-data revision — is the auditable evidence of independence of thought.)*

## D9. Publishability made demonstrable (registry row 23 → abstract tail + CH7)

> The full pre-registration — hypotheses, decision rules, model roster, and analysis plan — was
> deposited publicly with a DOI before launch and is citable independently of this dissertation.
> The study was designed to decompose into four self-contained papers (the main controlled study;
> the cross-model numeracy survey; the open-weight replication suite; the evaluation protocol),
> and an interim results pack was reviewed by industry supervisors at NatWest's AI research group
> during the campaign.

*(Placement: two sentences of this in CH7's significance paragraph; the DOI line in the abstract's
final sentence. Purpose: the 90–100 descriptor is "publishable in a peer-reviewed journal" — this
makes the claim verifiable rather than asserted.)*

## D10. The why-ten-models plain-language paragraph (registry row 18 → CH6 §6.7 opening)

> One model can tell us whether the most capable AI available uses the risk information it is
> shown; it cannot tell us whether the answer is a quirk of that one system. So ten further
> models — from four different developer ecosystems, five of them fully open so that anyone can
> re-run them indefinitely — each repeat the identical experiment at a smaller scale: same market
> data, same prompts, same rules, differing only in which model writes the reward code. Reading
> the outcome needs no statistics: the forest plot shows one arrow per model — do the arrows
> agree? — and a single pre-registered number summarises how large any across-model effect could
> be, given everything observed. Models that failed to produce working code at all are reported in
> their own table, because *that*, too, is an answer a practitioner needs.

---
*Next in the build order (handoff §4 + playbook): the M2 survey figure slot; the scannable tables
(CVaR-leg conclusiveness, assurance ladder, ablation). D1–D4 are wired; D5 refills from campaign
records at the bank gate; D6–D10 await Tamer's review, then wire into CH1/CH2/CH4/CH6/CH7.*
