# DEEP AUDIT — 13-agent first-hand sweep (2026-06-25)

Independent, first-hand audit (13 ultrathinking agents, each reading source/data/docs directly and
re-running statistics where possible). Severity: **CRIT / HIGH / MED / LOW**. Novelty: **NEW** =
not in the prior known-issue register; **CONF** = confirms/sharpens a known issue; **REFUTES** =
overturns a believed fact. Every claim is backed by `file:line` in the agent transcripts.

---

## META VERDICT

The **engineering and design rigour is genuinely top-decile** for an MSc (verified, not asserted:
purge/embargo, off-critic 3-way estimator decoupling, IUT conjunction, byte-tamper-evident
provenance, steelman baselines, oracle-pinned statistical primitives, exemplary `% VERIFY` citation
discipline). The grade is **not** capped by the science *as conceived*.

It is capped by five things, in priority order:

0. **The prototype "tail signal" does not survive the project's own controls** (REFUTES a stored
   belief). This is the single most important finding and reframes the whole results narrative.
1. **Integrity-of-pre-commitment**: the design is *not actually frozen*, was restructured the same
   day the directional pilot was known, and the proposal→delivery change is a *replacement*
   mis-described as a *narrowing*.
2. **A live sandbox RCE** that defeats the central safety claim in one line.
3. **Construct overclaim in the prose** ("distribution" vs six tail scalars; "scalar" arm is
   actually risk-primed) — the easiest marks to lose, on the most-read paragraph.
4. **The document does not exist yet** and the rigour is largely *invisible* (in code/tests the
   examiner never reads).

Realistic ceiling on current trajectory: **low-to-mid 80s**. Reachable ceiling with the fixes
below: **88–92**. The decisive lever is no longer "more rigour" — it is **honest framing + closing
the theory→code→outcome (mechanism) loop on data already on disk**.

---

## TIER 0 — THE FINDING THAT CHANGES THE STORY

### T0. [CRIT][REFUTES] The headline "distributional CVaR p=0.004" is a wrong-unit artifact and REVERSES under the placebo control
First-hand recomputation from the archived winner paths (`outputs/prototype/**`):

- **Reversal under control.** Winner CVaR-5%: **placebo −0.01711 (safest)** > scalar_cvar5 −0.01981
  > **distributional −0.01896** > scalar −0.02113. `analysis.json:118-123` itself reports
  `distributional_vs_placebo` CVaR `stat=-4.277, p=0.0005` — distributional's tail is *significantly
  worse* than the zero-information placebo's. The CVaR ordering tracks the **vol / risk-return
  frontier** (lower-vol winners have smaller tails), not tail-information content. The stored belief
  "distributional best … floor-raising" is **not supported — placebo raised the floor more.**
- **Wrong inference unit.** `analyze_results.py:133-141` runs `cvar_difference_test` on a *single
  winner's* 695-step path — a within-path time bootstrap whose "n" is one strategy's autocorrelated
  days, *exactly the anti-pattern the campaign code documents as invalid* (`bootstrap.py:117-122`).
  The valid unit (reward population / per-seed paired bootstrap) was **never run** — the campaign
  re-analysis correctly *skips* every H2 leg ("no shared test seeds").
- **Mechanism points the wrong way.** Responsiveness Spearman is **negative** (distributional −0.053,
  scalar_cvar5 −0.068): the LLM changed its code *less* when the fed distribution moved more. The
  `uses_tail` interpretability gate is **saturated at 1.00 across all arms** (incl. random_search and
  placebo, which are never fed a tail) — it discriminates nothing.
- **Unidentifiable from the prototype.** Variance decomposition (`σ²_search`) was **never run**
  (K=1); candidate correlation ρ̄≈0.80 ⇒ N_eff≈1 reward per arm. The cross-arm comparison is a single
  draw vs single draw.

**Consequence.** Read correctly, the prototype is a weak single-draw **null leaning slightly against
the mechanism**. Any dissertation sentence presenting p=0.004 as a "promising directional tail
signal" will be dismantled by an expert examiner in 30 seconds from the same JSON.

**What to do.** (a) Stop citing dist-vs-scalar CVaR in isolation; always report the full ordering
*with placebo*. (b) Treat all `analyze_results.py` p-values as descriptive-path-only (the header
already says "no number enters the dissertation" — enforce it). (c) The campaign is the only thing
that can upgrade this, and only if it runs the 30-seed test stage + K≥2 variance decomposition +
joint placebo legs. (d) **This is survivable** — a clean, well-disclosed null was always the bankable
Distinction path; the danger is *believing the artifact*, not the null itself.

---

## TIER 1 — INTEGRITY / BLOCKERS (fix before freeze + before submission)

### T1.1 [CRIT][NEW] The proposal pivot is a *replacement*, not a *narrowing*, and the disclosure mis-frames it
The approved proposal (`UCL_Deep_RL_Dissertation_Proposal_v2.docx`) is a **10-component framework,
RQ1–RQ7**, with the LLM as a **FinBERT sentiment encoder**. Full-text search returns **0** for
`eureka`, `reward design`, `reward function`, `reward code`, `distributional feedback`. The current
headline does not appear anywhere in it. `PROPOSAL_PIVOT_DISCLOSURE.md:12-28` calls this "narrowing /
de-scoping / keeping two threads" — and is itself **DRAFT, unsigned** by the supervisor. A marker who
reads the February proposal sees a near-total substitution dressed as a trim.
**Fix.** Reframe honestly as a *supervisor-approved change of research question driven by
identifiability* (bigger candour reads as more independence, not less). Get Okhrati's written
sign-off **before** submission. Never use "narrows."

### T1.2 [CRIT][CONF] The design is NOT frozen, and the headline rules were rewritten the day the pilot was known
`config/preregistration.yaml:4-5`: `frozen: false`, `freeze_hash: null`; no git tag, no OTS, the
DECISION_LOG freeze slot is still the template. The freeze *machinery is wired and would refuse to
run* (good), but freezing has never been performed. Worse, the headline-defining amendments are dated
**2026-06-25** and uncommitted: **R25** (rebuilt the H2 rule into two co-primary IUTs, elevating
CVaR-5% to co-primary), **R32** (added `placebo_shuffled`), **R33** (univ3→univ4 headline panel) —
after the 2026-06-21 prototype showed the directional CVaR pattern. The "bankable pre-registered
null" claim is currently **literally false**.
**Fix.** Run `freeze.py` now (hash + tag + OTS), commit, fill the DECISION_LOG slot, **before** the
campaign. In Methods, include a *pre-registration provenance* paragraph: all R-amendments are
pre-freeze refinements dated before any sealed-test number; defend R25 as theory-driven with the
pilot disclosed as corroborating-not-causal. Ship a clean frozen v2 with the 39-amendment log as an
appendix.

### T1.3 [CRIT][NEW] `from numpy import *` / `from numpy import load` fully bypasses the AST sandbox → confirmed RCE
`executor.py:464-472` checks only the **root module** on `ImportFrom`, never the imported *names*;
the `_BANNED_ATTRS` allowlist only fires on `ast.Attribute`, so a bare-name import skips it. Verified
end-to-end through `validate_once`: `from numpy import load` + `load(evil.npy, allow_pickle=True)`
executed `os.system` (marker file written) — the exact `np.load` pickle-RCE the banlist exists to
stop. No test covers it.
**Fix (~5 lines + 3 regression tests).** In `ast_gate`: reject `ImportFrom` whose names include a
banned/non-allowlisted symbol; reject wildcard `import *`; simplest robust form — forbid
`from … import` entirely (reward code only needs `import numpy as np`).

### T1.4 [HIGH][CONF→sharpened] The H2 contrast is "Sharpe-scalar vs Sharpe-scalar + tail shape," not "distribution vs scalar"
The "scalar" arm's header is *validation Deflated Sharpe* (`schema.py:44,112-113`) and `system.txt:22-23`
instructs **every** arm to "optimize risk-adjusted performance." So the scalar arm is risk-primed and
fed a risk-adjusted number; the distributional arm's only *additional* content is the tail block —
which is also **~8× longer** (1 line vs 8). Whichever pair you headline, the other is confounded
(information vs token-length). Verified separately: the g7 distributional and scalar **winners wrote
nearly identical** online-Sharpe + CVaR-10% + drawdown + turnover + Herfindahl code.
**Fix (write-up only — the clean control already exists).** Headline **distributional vs placebo**
(length-matched, information-isolated, `schema.py:128-135`); state H2 as "the tail *shape* adds value
over a held-constant risk-adjusted scalar header." Add a manipulation check: grep the archived
`reward_source` of winners for whether distributional code references tail stats *more* than scalar.

### T1.5 [HIGH][NEW] The frozen `inference.yaml` pre-registers `scheme: walk_forward`; the campaign runs a single contiguous split
`config/inference.yaml:9` freezes `splits.evaluation.scheme: walk_forward`; `run_campaign.py:31-34`
states walk-forward folds are **DEFERRED** and the test leg is ONE 2018–2025 window. A flat
contradiction between the frozen pre-registration and the executed code — the most dangerous unstated
discrepancy for a López-de-Prado-literate examiner.
**Fix.** Amend the prereg / annotate the field `# NOT RUN — single sealed-split headline; walk-forward
deferred` before freeze.

### T1.6 [HIGH][NEW] The construct retitle is mandated but NOT propagated — README/contribution still say "distribution"
`DEEP_FRAMING_discipline.md:108-122` mandates retitling "distribution" → "multi-level tail-risk
feedback" everywhere (the vector is six left-tail scalars: no mode, no right tail, no quantile grid).
But `README.md:8,13` still claim "the **realized-return distribution**" / "N1: first to feed a
return-distribution signal" — the exact overclaim the framing doc calls "the easiest construct hit
available," surviving on the most-read line.
**Fix.** Global-replace the contribution statement, abstract, and README to "multi-level tail-risk
feedback"; add the one-paragraph "what is / isn't in the vector" disclosure.

---

## TIER 2 — MAJOR (rigour / grade levers)

### T2.1 [HIGH][CONF] Training adequacy is asserted, never demonstrated — the convergence gate was built and never run
`scripts/learning_curve.py` (the undertraining gate) exists and is unit-tested but produced **zero
output artifacts** (glob confirms none). The only convergence evidence in the pipeline is "critic
loss is finite after 3k steps" (`smoke_test.py:194-200`, explicitly *not* gated on the loss falling).
The campaign trains 50k steps at 1 gradient step/env step on a 1,893-dim obs; the ladder went to
200k *because* 50k is suspect, yet was never executed. Without a plateau plot, any H2 effect (or
null) is attributable to under-training noise.
**Fix.** Run the existing `learning_curve.py` at `--budgets 25000,50000,100000,200000 --seeds 0,1,2`
on the campaign GPU; put the eval-IQM-vs-budget + terminal-critic-loss plot in Methods. A few
GPU-hours converts the biggest methods liability into a figure that *strengthens* the chapter.

### T2.2 [HIGH][CONF] H1 baselines are un-tuned (λ=1.0, η=0.1, α=0.05) and the "validation-selection" fix is inert
`portfolio_env.py:293-297` injects no hyperparameters into baseline rewards → all run at arbitrary
defaults. `beat_human_baseline` prefers a validation-selected human bar, but baselines archive
`val_fitness=NaN` (`run_campaign.py:654`) so the code **always falls back to test-median selection**
(`val_snoop_caveat=True`) — the human bar is in fact test-selected (White 2000 data-snoop). "You
searched 30 LLM candidates against a human frozen at λ=1.0" is the referee's sentence.
**Fix.** Either implement a budget-matched validation-selected λ/η/α sweep for the 3 parameterised
baselines (the reward fns already read `info.get("lambda")`), or correct `PREREGISTRATION.md:22` and
foreground the disclosure. H1 is descriptive/disjoint, so disclosure is the floor; tuning is the
strong fix.

### T2.3 [HIGH][NEW] Nearest-neighbour prior art (DLM, Behari 2024) is absent from the core bib; supervisor's own paper is under-cited
`docs/LIT_gap_llm_reward_optimizer.md:161-170` correctly identifies **DLM (Behari et al., NeurIPS
2024, arXiv:2402.14807)** — an LLM proposing reward *code*, iterating on *simulation feedback*, shown
a *distribution* — as the true nearest neighbour, but it is **not in `paper/refs.bib`**. Separately,
**Khraishi & Okhrati 2022** (supervisor's own paper) is cited as a bare arXiv preprint though it is
**ICAIF '22, DOI 10.1145/3533271.3561682** (externally confirmed) — citing your supervisor's
peer-reviewed paper as a preprint reads as carelessness.
**Fix.** Promote DLM + Qu 2025 (ACL Industry) + GEPA + OPRO + Singh/Sorg + IRD + CARD into
`refs.bib` with `% VERIFY`, each with its cite-and-distinguish sentence in Related Work; convert
Khraishi–Okhrati to `@inproceedings{... ICAIF, doi=10.1145/3533271.3561682}`.

### T2.4 [MED][NEW] PopArt's one-sided shrink is reward-magnitude-dependent → latent H2 confound
`popart.py:95-96,137` clamps `sigma ≥ 1.0`, so PopArt is the identity for unit-scale rewards and a
≫1 divisor for large ones. The arms author rewards of *different natural scales*, and `ent_coef=auto`
re-adapts to the normalised scale — so two "fixed-agent" arms get effectively different entropy
regularisation. Undisclosed.
**Fix.** Disclose; log per-candidate `sigma` and show the cross-arm distribution; cheapest — a 1-seed
`popart=False` ablation on the winners showing the H2 ordering is unchanged.

### T2.5 [MED][NEW] The bankable null rests entirely on TOST, and the study is underpowered against its own SESOI
Live power: MDE@80% = 0.256 Sharpe; SESOI = 0.05 **DSR**. The power doc flags the unit mismatch but
**never reconciles them**, so there is no power statement in SESOI units — 0.256 Sharpe is almost
certainly ≫ 0.05 DSR (underpowered for the SESOI, rescued only by TOST equivalence). A non-rejection
therefore licenses "inconclusive," not "no effect ≥ SESOI," unless the TOST CI lands inside ±0.05.
**Fix.** Compute and report the MDE in DSR/SESOI units; get the clean seeds-on-winners σ before
freezing the power claim; pre-state the fallback narrative for the inconclusive branch.

### T2.6 [MED][NEW] The document doesn't exist, the disclosure strategy doesn't fit the word budget, and the EDA numbers are inconsistent
`paper/` contains only `refs.bib` — no abstract, title, or chapters; the only title strings on record
are stale ("distributional feedback"). The grade strategy is "self-disclosure," but Discussion is
budgeted at **700 words** against **19 limitations (L1–L19)**, and the data chapter is unwritten with
contradictory stylised facts (median excess kurtosis **11.5** in one doc vs **49.9** in another;
every other number `⟨TBD⟩`, sourced from a *superseded* IQN-SAC brief).
**Fix.** Write the canonical title + abstract + contribution statement **now** (bankable regardless
of campaign outcome) with the retitled construct and method-contribution-plus-bankable-null framing;
move L1–L19 into a word-excluded Limitations appendix/table and lift Discussion to ~1,000 words;
regenerate EDA numbers from the frozen gold panel and reconcile the kurtosis figure.
> **RESOLVED (kurtosis, 2026-06-26):** the "11.5 vs 49.9" was a **false conflict**, not two competing
> medians. Recomputed first-hand from the frozen `data/gold/returns_panel_univ3.parquet`
> (`scipy.stats.kurtosis(fisher=True)`, dropna per name, n≥30; estimator-identical to `data_pipeline/src/data/eda.py`):
> **median per-asset excess kurtosis = 11.58 over the 30-name development cohort** (reproduces
> `eda_universe_dev30.md` per-name values exactly) and **13.16 over all 953 RICs** (952 names; `ACV.N^K06`
> has 4 obs and is dropped by the n≥30 guard). Both robust to `bias` (±0.02). **49.9 is the single-name
> *maximum* (Citigroup `C.N`, 49.76 dev-30)**, used legitimately as an "up to ~50" headline example — it
> was never a median. So `reports/data_chapter_seeds.md` "median 11.5" was **CORRECT for dev-30, not stale**;
> the only defect was the missing cohort qualifier, now added (with the 953-name figure and the C.N
> clarification). No EDA table value changed.

### T2.7 [MED][CONF] Delisting surcharge is reason-blind; keep univ3 (0%) as headline
The −30/−55% surcharge (`membership.py:172-192`) fires on every non-M&A delisting, but `reason` is
`None` on the whole vault, so on the traded dev cohort DELL (premium 2013 buyout) and TWX (2018 AT&T
deal) would be surcharged −55/−30% — fabricated left-tail mass in the *training* split the
distributional channel measures. univ3 (`liquidate_to_cash`, 0%) does not surcharge.
**Fix.** Headline univ3; report univ4 only inside the disclosed {0,−30,−55,−100} band; state the
surcharge is reason-blind and over-penalises M&A; show the band leaves H2 ordering invariant.

### T2.8 [MED][NEW] Two estimator/robustness gaps in the tail machinery
(a) `_evt_cvar` has no guard for `xi ≤ −0.5` (non-regular GPD MLE) — fires essentially never on real
returns but invites the question. (b) `exceed_frac` is data-dependent, so the *fed* CVaR-5% can
silently switch EVT↔empirical per candidate. **Fix.** Add a `xi ≤ −0.5 → empirical` branch (mirror
the `xi ≥ 1` guard); assert/log a consistent estimator across candidates for the fed headline levels.

---

## TIER 3 — THE UPSIDE (highest-leverage, scope-safe deepening)

### T3.1 [HIGH LEVER] Close the theory→code→outcome loop: the reward-program differential
The theory spine (`H2_THEORY_SPINE_2026-06-21.md`: Blackwell garbling, Kusuoka/Acerbi
CVaR-sufficiency, Rowland off-critic, Skalse–Abate) is PhD-grade and proves an **envelope**; the
empirics produce a **number**; the **mechanism** between them is never measured. All 239 archived
reward programs + their `components` dicts + fed feedback blocks are on disk. Build a per-arm
characterisation (term prevalence, CVaR-level count, coefficient magnitudes, the never-analysed
`components` activity). This is descriptive forensics over frozen data — **fully scope-safe** — and it
de-risks *every* outcome: a win is explained, a null becomes *mechanistic* ("the fed numbers left no
code-level signature"), corroborated by `placebo_shuffled`. Verified premise: the g7 winners across
arms wrote strikingly similar code, so the differential is a real open question whose answer is
load-bearing either way.

### T3.2 [HIGH LEVER] Make the theory a *predictive instrument* — pre-register a prediction table
Terminate the theory chapter in an explicit prediction table mapping each strict/weak/null condition
to its observable signature (Sharpe leg, CVaR leg, responsiveness, generations-to-winner). Stating
"we predict a tie on Sharpe and separation on CVaR-5% because λ=0 selection is tail-blind" *before*
the sealed leg is the Popperian move that elevates a result of any sign from a measurement to a
confirmed/refuted prediction.

### T3.3 [MED LEVER] Make the rigour legible — it's currently invisible to a PDF-only examiner
The deepest rigour lives in code/611 tests the examiner never reads. Add: (a) a one-page **system
diagram** (data → fixed SAC → reward-slot ← LLM-designer ← feedback block ← off-critic measurement →
λ=0 fitness → sealed test → inference); (b) a **rigour ledger** table (one row per defended threat:
conjunction×BH→IUT, EVT bias, units-matched TOST, single-seed-winner asymmetry, each with its
one-line resolution); (c) transcribe the theory's rigorous-vs-hand-wavy demarcation verbatim.

### T3.4 [MED LEVER] Upgrade H3/H4 from horse-races to mechanism decompositions
H4: promote the already-implemented in-family random-search reference to a *reported* baseline so H4
reads as a C-procedure vs C-richness decomposition (not a nested-space horse-race), and add a TOST
bound (H4 currently has no equivalence margin, unlike H3). H3: promote to a paired placebo-relative
uplift-difference test so a null becomes "reflection left no information-tracking signature."

---

## GENUINELY STRONG — BANK THESE, DON'T OVER-CORRECT (all verified first-hand)

- **Purge/embargo + causal timing is exemplary.** `max(embargo, lookback)=60` purge double-guarded;
  the val window's first lookback slice (`returns[2517:2577]`) starts one row after the last train
  row — no observation window crosses a split. VIX prelag verified in the live data (`cash.vix[t] =
  raw VIXCLS[t-1]/100`, row 0 NaN). Anonymisation clean (integer ids only).
- **The off-critic 3-way decoupling is the real methodological contribution.** Fed = EVT/GPD on
  *training* returns; selected = tail-blind validation DSR (λ=0); tested = empirical CVaR on the
  *sealed* split. The thing the channel is fed is neither what it's selected on nor the estimator it's
  graded by — so any tail effect is attributable to the channel, not a self-grading artifact. Most
  prior work conflates ≥2 of these three; this separates all three and unit-tests the separation.
- **IUT conjunction is correctly conservative** (measured size 0.007 at the least-favourable null);
  PSR/DSR/E[maxSR] match Bailey–López de Prado to machine precision; BH exact-equals statsmodels;
  IQM/PoI match rliable at 1e-9; the per-seed rliable anti-conservativeness fix (~21%→~5%) is genuine.
- **Provenance/replay is publication-grade.** Atomic fsync+replace writes; byte-for-byte
  tamper-evident sidecar verification; deterministic load order; frozen-winner hash desync guard.
  Parallel TEST-leg == serial is genuinely byte-identical on a fixed device.
- **Baselines are a true steelman.** Long-only convex QPs (no Σ⁻¹μ collapse), Ledoit-Wolf shrinkage,
  delisted-name masking, identical costed env, zero tunable overfitting surface — broader/fairer than
  DeMiguel 2009. "You only beat a weak baseline" is not available to the examiner.
- **`% VERIFY` citation discipline is exemplary** — every 2025–26 entry flagged, arXiv ids quoted
  from on-disk PDFs, venue-printed vs venue-inferred separated. Freeze gate is wired and refuses to
  run unfrozen. Sandbox is adversarially tested (modulo the import-escape above). Statistical
  primitives that *can* be pinned are pinned to oracles, not shapes.

---

## ACTION PLAN (ordered by leverage)

**Before the campaign / freeze:**
1. Fix the sandbox import-escape (T1.3) + 3 regression tests. *(~1 hr)*
2. Run `learning_curve.py` at the campaign budget; decide if 50k is adequate (T2.1). *(GPU-hours)*
3. Reconcile `inference.yaml` walk_forward vs single-split (T1.5); add `arm`/`candidate_id` to the
   anomaly schema; wire variance-decomposition (K≥2) and the H3/H4 difference+TOST tests into
   `analyze_campaign.py`. *(~1 day)*
4. **Freeze** (hash + git tag + OTS), commit, fill DECISION_LOG (T1.2).

**Write-up (bankable regardless of campaign outcome):**
5. Canonical title + abstract + contribution statement with the **retitled construct** and the
   **distributional-vs-placebo** headline (T1.4, T1.6). *(hours, highest downside-protection)*
6. Honest pivot disclosure + supervisor sign-off (T1.1); pre-registration provenance paragraph.
7. Promote DLM/GEPA/OPRO/Singh/IRD/CARD + fix Khraishi–Okhrati venue (T2.3).
8. Build the **reward-program differential** + **prediction table** + **system diagram** + **rigour
   ledger** (T3.1–T3.3) — the move from high-Distinction to publishable.
9. Move L1–L19 to an appendix; regenerate and reconcile EDA numbers (T2.6).

**Frame the result honestly (T0):** present the prototype as a directional *null* (reversed under
placebo, wrong-unit p-value, negative responsiveness, unidentified variance); let the *campaign* —
run through the existing correct machinery — be the only confirmatory evidence.
