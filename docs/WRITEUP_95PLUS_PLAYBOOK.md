# THE 95%+ WRITE-UP PLAYBOOK (2026-07-18) — the writing month's operating orders

> Written from the strict zero-bias audit (2026-07-18): trajectory lands ~86–90 by default;
> the last 5–10 points live in FOUR specific moves below. This file is the plan of record for
> the writing month — read it FIRST when the write-up begins. Companion: the grade decomposition
> in `docs/SESSION_2026-07-11_GRADE_STRATEGY_AND_HANDOFF.md` and the fix registers in CLAUDE.md.

## The four moves that buy 88 → 95 (in priority order)

### MOVE 1 — CH2 becomes an ARGUMENT, not a catalogue (dim 1: ~76 → 88+)
The audit's finding: CH2 distinguishes 196 papers accurately but does not yet ARGUE. Rewrite to a
three-act thesis the corpus is made to PROVE:
  (i) *Reward design is the bottleneck* (safety + finance strands converge on it);
  (ii) *LLM reward-authorship changed the bottleneck's nature — from designing rewards to
       designing the DESIGNER'S EVIDENCE* (Eureka lineage → the feedback channel is the frontier:
       RDA's visual turn, Gallego's "feedback aliasing", GIFT's rule libraries are all
       feedback-channel moves — none instruments it);
  (iii) *Finance is the arena where evidence-use is checkable against decision theory*
       (coherent risk gives the normative yardstick no other domain has).
Technique: every paragraph ends by NEEDING the next; every cited paper does WORK (premise,
contrast, or boundary); kill any paragraph whose deletion loses no argument. The neighbor
distinctions (GIFT four-axis, Gallego, ELfolio) move INTO the argument as act-two evidence.

#### MOVE 1 addendum — the OPTIMAL-CONTROL BRIDGE (added 2026-07-19, from Tamer's aerospace
#### conversation; ~1 paragraph in CH2 or CH3's opening + 2–3 cites; zero scope, pure depth)

The dissertation currently never says what a control theorist would see instantly: the portfolio
task IS a discrete-time stochastic optimal-control problem (state = features + holdings; control =
weights; the reward = the COST FUNCTIONAL), whose classical solution — Merton's HJB treatment —
requires KNOWN dynamics. With unknown, sampled, non-stationary dynamics the modern solution is
model-free RL: SAC solves the entropy-regularized Bellman equation (the sampled-data HJB) from
data. Write the bridge paragraph and then land the reframe that makes the contribution legible to
ANY technical reader: *in optimal control, the cost functional is the designer's entire lever —
everything else is optimization. This study asks who writes the cost functional (an LLM), and
what MEASUREMENT of the closed-loop system that writer needs (a scalar vs the realized tail
profile) to write it well.* The feedback channel becomes the "sensor" on a design loop — an
instrumentation question, which is exactly what the mechanism kernel instruments. Payoffs: (a)
Okhrati is a mathematical probabilist — Merton/HJB is home ground and the mapping is INTUITION,
not machinery (his #1 criterion); (b) the second marker from any engineering discipline gets the
whole design in one paragraph; (c) it deepens the CH3 sufficiency spine (the fed tail as a
sufficient statistic OF THE CLOSED LOOP for tail-aware cost design). Cites: Merton 1969/1971
(VERIFY first-hand before adding — prime directive 4); `chow2015risk` (already in refs.bib —
CVaR-MDP, the risk-sensitive control lineage); optionally Ruszczyński 2010 (Markov risk measures;
VERIFY). SAC-as-max-entropy-control is already covered by `haarnoja2018sac` — frame it, don't
re-cite. **DO NOT IMPLEMENT classical control machinery** (LQR/Merton baselines, model-based
trajectory optimization): the design is FROZEN; the agent is FIXED by the identification
principle; a Merton baseline needs estimated drift/covariance — the estimation-risk trap that
DeMiguel's 1/N result (already our floor) exists to warn about; and the contribution is the
feedback channel, not the control algorithm. This is a WRITE-TIME paragraph, nothing more.

### MOVE 2 — The mechanism is the headline; write it as a DETECTIVE STORY (dim 3: ~85 → 92+)
- Chapter order of emphasis: the 3-link chain figure (F10) appears in CH1; CH6's mechanism
  section is the longest results section; the H2 equivalence is the "rigorous backdrop" (the
  registered framing) — never let the null read as the point.
- The FIVE severity exhibits, written explicitly as design-discipline-in-action (Okhrati's 5/5
  register — each gets its own paragraph-length telling):
  1. The pre-committed B\* rule FIRING AGAINST the analyst's own prior recommendation (200k
     defended on 2026-07-13 EVENING; the rule, registered that MORNING, overturned it on
     2026-07-18 — the timeline is documented and is the strongest severity story we own).
  2. The knee migration 200k→400k with the 16× curve exhibit (F11).
  3. The hot-seed episode: how CRN pairing rescued an inference unpaired analysis would have
     botched (seed 2: 0.248 at 200k — tell it).
  4. The channel-dependent budget response (dist ≫ scal at every rung) — if it replicates on
     campaign winners, a first-class novel observation; if not, an honest scope note.
  5. The M2 psychophysics gradient (responsiveness vs numeracy across ~12 models).
- Claims stay tightened to the conjunctive cell + the four affirmative contributions
  (instrument / protocol / theory envelope / mechanism audit). NEVER claim more than the cell.

### MOVE 3 — The 10k surgery is DISTILLATION, not amputation (dim 4: ~70 → 88+)
Decision procedure, applied paragraph-by-paragraph to the 15.5k body:
  (a) Does the FULL result/analysis live in an appendix or figure? → the body keeps ONE
      sentence + a pointer (appendices/math/figures/tables are word-EXEMPT — the escape hatch).
  (b) Does the paragraph defend against an examiner attack? → keep, compressed to the attack
      + the defense (the "what each control defends against" TABLE absorbs most of these).
  (c) Is it methodology narration (how we built things)? → CUT or one clause; the repo is the
      record, the PDF is the argument.
  Foreshadow-predict-deliver: each result is promised ONCE (CH1), predicted ONCE (CH3/4),
  delivered ONCE (CH6) — the audit found 4–5× pre-disclosures; kill them.
- The plain-language spine: the CH1 60-second paragraph (done) + one plain-English opening
  sentence per chapter + the D5 worked micro-example REBUILT from CAMPAIGN records (never
  prototype numbers) + captions readable standalone (the second marker may be a historian).
- Faultless mechanics sweep (Okhrati's named docks): every figure/table cross-referenced in
  prose; realized wall-clock + GPU-h + API cost reported (the 2.03B-step / 2,476 GPU-h numbers
  + realized C); Harvard refs compiled through the pinned CSL; 16 sections in order; ZERO
  "% VERIFY" strings; the AI-disclosure + ethics statements final (done 07-13).

### MOVE 4 — Results/Discussion written to the pre-registered skeleton (dim 2 exhibited)
- CH6 fills the EXISTING shells ([FROM CAMPAIGN] slots) — no new structure invented post-data;
  say so explicitly ("this chapter's structure predates its data").
- CH7 grades the work against its own RQs one by one (the audit found it doesn't yet); the
  deviations log is printed IN FULL (an exhibit of discipline, not a confession).
- Every number's provenance: bank-gate outputs only; evidence-ledger grades enforced (A or
  stated); the D̄/σ_D realized-vs-planned power paragraph (rung-100 re-estimate vs the E1 plan).

## Order of operations for the writing month (~28 days if campaign ends ~Jul 31)
1. Days 1–2: bank gate + analyze + all figures rendered (F5–F11 + M2 slot).
2. Days 3–5: CH6 Results into the shells (numbers-first pass).
3. Days 6–9: CH7 Discussion (mechanism verdict, RQ grading, limitations final).
4. Days 10–13: MOVE 1 (CH2 synthesis rewrite).
5. Days 14–18: MOVE 3 (the 10k distillation + spine + mechanics sweep) — full-document pass.
6. Days 19–20: M2 runs + its figure + CH6 §M2 (can swap earlier if gate opens early).
7. Days 21–23: foreshadow/de-densify/cross-ref audits; compile; READ THE PDF END-TO-END ALOUD.
8. Days 24–25: the MANDATORY pre-submission fence sweep (+ ELfolio full-text) + final gate.
9. Days 26–28: buffer. NOTHING new enters after day 23 except fixes.

## Standing constraints (do not re-litigate at write time)
- No prototype number in the dissertation (D5 rebuilds from campaign records).
- "Dr" Okhrati; never misattribute the CVaR-elicitability chain; VaR fails SUBADDITIVITY
  specifically; (VaR,ES) jointly elicitable (Fissler–Ziegel), ES alone not (Gneiting 2011).
- The disclosure-as-tactic reasoning stays OUT of the PDF.
- Keep breadth in appendices; depth in the body. Never silently drop a pre-registered result.
