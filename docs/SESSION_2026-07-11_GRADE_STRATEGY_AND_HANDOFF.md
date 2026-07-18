# Session handoff — grade strategy (the 96%+ target) + full state (2026-07-11)

> **Purpose.** This is a complete, self-contained handoff for a fresh Claude Code session. Read this
> plus the memory cursor (`memory/session-current-focus.md`) and `CLAUDE.md`. Everything needed to
> continue without re-deriving is here. Every state claim below was verified first-hand this session
> (freeze gate re-run, git status inspected). **Nothing here changes any frozen decision.**

---

## 0. TL;DR — where we are and what to do next

- **The design/infrastructure phase is essentially DONE.** The pre-registration is **freeze-ready**
  (canonical hash `79a6db44f12c86316572840a21603ac648ded010ee2487eda95bc45f88c535ba`, gate **21/21
  GREEN**, `frozen: null` — freezing is Tamer's act alone). The Myriad cluster path is built + rehearsed.
  Stage 2 is rebalanced for publishability and committed.
- **The grade is no longer won in design — it is won in EXECUTION (running Stage 1 clean) and in
  WRITING (the communication dimension).** Neither has started.
- **Target set by Tamer this session: as close to 100% as possible, with a 96%+ FLOOR.**
- **The single highest-EV next action = build the COMMUNICATION dimension (dimension 4 of the rubric).**
  It is equally weighted with the other three, currently at ~zero built, and therefore caps the
  four-dimension average hardest. See §3 for the honest decomposition and §4 for the concrete build plan.
- **Immediate concrete step offered to Tamer (awaiting his go):** draft, in order, (1) the plain-language
  contribution paragraph, (2) the 3-link mechanism figure spec, (3) the Limitations subsection scaffold.

---

## 1. The grading context (the rubric that governs everything)

Authoritative source read this session: `../00_planning/DISSERTATION_ALIGNMENT_AND_GUIDELINES.md`
(IFTE0008 2025–26). The load-bearing facts:

- **Four marking dimensions, EQUALLY weighted.** The final mark is (effectively) their average, so the
  **weakest dimension caps the score.** 96 requires *no* soft dimension.
  1. **Background & independence** — critical, selective literature synthesis; original interpretation.
  2. **Research design** — faultless execution; entirely appropriate methods; unquestionable originality.
     (This is the project's strongest lever *if executed clean*.)
  3. **Novelty & significance** — the band definition: **90–100% = "publishable in a peer-reviewed
     JOURNAL"; 80–89% = "publishable in an international CONFERENCE."** This is the decisive threshold.
  4. **Communication** — "excellent, highly readable, faultless presentation of data," for an
     **any-discipline second marker** — the guidelines' explicitly named **"single biggest risk."**
- **Structure constraints:** 10,000-word body (**maths, code, figures, tables, appendices EXCLUDED**);
  16-section order; core (Method+Results+Discussion) ≈ 60%; Harvard refs (~90 cited selectively);
  a **dedicated Limitations subsection** is called out as exemplary best practice.
- **Examiner (Dr Ramin Okhrati) revealed grading function** (from `project-examiner-okhrati-and-grade-strategy`):
  intuition > technical correctness; **depth > breadth ("do less, go more in depth" — he DOCKS scatter)**;
  honesty rewarded (his 5/5 — our pre-registered null is this); originality foregrounded; motivate-with-data.
  His own research is **LLM-risk-behaviour** (Hartley…Okhrati 2025 ACL: *do models use the risk they are
  shown?*) — which is *this dissertation's exact mechanism question*. This is the golden neighbour.

**Decisive implication (already baked into the Stage-2 rebalance):** robustness *breadth* is at best
conference-grade ("it also holds elsewhere"); a **mechanism contribution is journal-grade** (TMLR is a
journal). So mechanism depth is the specific lever from the A-band into the 90–100 band.

---

## 2. The dissertation in one paragraph (for a cold-start session)

An LLM (Claude Opus 4.8) authors reward-function **code** for a **fixed** SAC portfolio-RL agent. The
**only** thing that varies across arms is the **risk content of the feedback** the LLM receives (a
multi-level CVaR tail vector vs a scalar). It is a 7-arm pre-registered controlled study
(arms: `distributional, scalar, scalar_cvar5, placebo, placebo_shuffled, random_search, bayes_opt`).
The headline **H2** is two co-primary intersection-union tests (h2_ra Sharpe, h2_tail CVaR-5%), frozen
family m=6, TOST equivalence at SESOI=0.05. The **predicted, pre-registered result is a bounded-effect
null**: fine-grained distributional risk feedback does **not** improve the authored reward code. The
**contribution** is the *mechanism*: the LLM cannot reliably *use* the close numerical tail values it is
shown (a **representational numeracy bottleneck**, not a capability one), the failure is **general across
LLMs**, and it is **partially reversible** by re-representing the information legibly. That mechanism story
is what makes a null a journal-grade contribution rather than "it didn't work."

---

## 3. The honest 96%+ decomposition (this session's core analytical output)

The whole point: **96 is won by lifting the weakest of four equal dimensions, not by strengthening the
strong ones.** Honest per-dimension assessment:

| Dim (equal weight) | Where we are | 96+ needs | Risk profile |
|---|---|---|---|
| **1 Background/independence** | ~strong (196-paper corpus + numeracy-corpus grounding) | *selective, critical* synthesis funnelling to the gap — **not a catalogue** (the guidelines' explicit warning) | Low; a writing task |
| **2 Research design** | strongest (**pre-registration + replay-not-regenerate + mechanism instruments**) | **faultless EXECUTION** — a clean Stage-1 run + flawless analysis | The biggest **self-inflicted** risk = a **rushed run** forced by Myriad saturation. Mitigation: use the calendar slack; don't compress the run |
| **3 Novelty/significance** | ~88–95, **conditional** | the M-spine landing: mechanism-explained, general, lever-identified null (journal-grade) | The numeracy story is a **prediction until the M2 survey confirms it** — the one factor **partly outside our control**. **Floor is protected**: an honest null + genuine mechanism attempt + stated limitations stays top-band (Okhrati rewards honesty). Only the ceiling depends on M2 landing |
| **4 Communication** | **~zero built** | plain-language contribution para, mechanism figure, faultless tables, Limitations subsection, worked micro-example — for the any-discipline second marker | **This is the weakest link and highest-EV work.** Equal weight, near zero built → caps the average until it exists. Fully in our control |

**The honest bottom line stated to Tamer:** with three dimensions at ~92–96 and one (communication) at
~zero-because-unbuilt, the *average* is capped well below 96 until the write-up exists. **No additional
science moves the ceiling as much as building dimension 4 does.** The next real work is the write-up, not
more Stage-2 science. (This is consistent with the standing memory note that the dominant grade lever is
mechanism-chapter write-up depth, not more find-fix.)

---

## 4. The concrete communication-dimension build plan (the recommended next work)

Build order, highest second-marker impact first:

1. **Plain-language contribution paragraph** — before any formalism. The second marker (any discipline)
   must grasp the finding in ~60 seconds: *what was asked, what was found, why it matters.* No jargon.
2. **The 3-link mechanism diagram** — `fed tail —SQ1→ authored code —SQ2→ trained policy → realized tail`,
   visibly **cut at joint 1** (responsiveness ≈ 0 at link 1). This is the paper's spine as one figure.
3. **The M2 numeracy-survey figure** (headline empirical object; the survey itself is Stage-2, but its
   figure slot and caption belong in the communication plan now).
4. **Faultless, scannable tables** — the CVaR-leg conclusiveness (σ_D=0.0015, ρ=+0.47, conclusive at n=30);
   the 7-rung assurance ladder; the **ablation table isolating the contribution**.
5. **Dedicated Limitations subsection** — the guidelines' exemplar practice; the cross-period single-look
   limitation lives here, stated honestly (Okhrati 5/5).
6. **Worked micro-example** — one candidate: fed CVaR −0.0577 vs −0.0582 (values that sit in the LLM's
   ~50–70%-accuracy discrimination regime), what the LLM wrote, why it did not discriminate. Makes the
   numeracy bottleneck concrete and intuitive (Okhrati: intuition > machinery).

**Guardrails on this work:** the 10k-word body EXCLUDES maths/code/figures/tables/appendices — push the
survey protocol + formalism into excluded blocks; keep the 16-section order; core ≈ 60%. **Do NOT
auto-rewrite existing graded prose or touch hash-bound files** — draft new prose/figures for Tamer's review.

---

## 5. Stage 2, rebalanced for publishability (committed this session — recap)

Committed in **7ee264f**: `docs/STAGE2_PUBLISHABILITY_PLAN_2026-07-11.md` (operative), plus a superseding
pointer added to `docs/GRADE_SECURITY_AND_TIER_DESIGN_2026-07-08.md §4.1`. The rebalance moved Stage 2
from **breadth** (more models/markets/algorithms — the breadth Okhrati docks) to **MECHANISM DEPTH**:

- **TIER M (the contribution — invest here):** M1 locate-the-break (frozen SQ1–3, report-only); **M2 =
  the NEW cross-LLM numeracy + responsiveness survey (the flagship, ~$5–10, NO RL/seeds, a dozen+ models
  incl. deliberately weak ones for the capability gradient)**; M3 the legibility lever (re-represent the
  same tail info legibly → does responsiveness rise?).
- **TIER R (rigor, ~$0, keep all):** D3 variance decomposition, D4 winner's-curse shrinkage, D9
  spec-curve + permutation, D5 calibration fleet.
- **TIER G (thin, prunable, future-work by default):** U3 one open-family replication (Qwen; optionally
  Kimi-K2); D6 TQC / U5 PPO-TD3 / U4-U4b FTSE / D7 GPT-5.5 → CH7 future work unless trivially free.
- **Cost ~$20–30** (was $93–178); value up, cost down. All report-only, post-bank-gate, touches nothing
  frozen, prunable to zero. §6b grounds it in the actual rubric.

**Model note (answering "third family — a bunch of LLMs?"):** the "bunch of LLMs" belongs in the cheap
**M2 survey** (descriptive, no RL, outside the confirmatory m-family → no forking paths), NOT in expensive
full replications. The one foregrounded full replication is U3 (Qwen). Any new model needs the Qwen-pattern
gate first: live smoke + contamination check + capability floor.

---

## 6. Full current state (verified first-hand this session)

- **Git:** branch `myriad-cluster-and-tier-system`. HEAD `7ee264f`. Tracked tree **clean**; only untracked
  scratch dirs `outputs/proto_laptop/ proto_timing/ prototype_repeat/` (prototype outputs — not for commit;
  no prototype number ever enters the dissertation).
- **Freeze:** gate **21/21 GREEN**, canonical hash **`79a6db44…`**, `frozen: null`. Seeds n=568.
  Re-verified this session via `scripts/freeze.py --check`.
- **`config/prototype.yaml`:** the TEMP Qwen smoke edit is **fully reverted** to `anthropic` /
  `claude-sonnet-4-6` and matches HEAD (the one pending "revert" item from the prior session is DONE).
- **Seed decision (Amendment E1):** 7-rung assurance ladder `{mode: tiered, tiers: [30, 100, 189, 279,
  340, 403, 568]}` (flat [0..567], headline 568, primary target 403=95%, exogenous stopping). Recorded +
  committed (79bbfd6). Rungs: 30 core / 100 σ-precision / 189 MC-point / 279=80% / 340=90% / 403=95% / 568=99%.
- **Cluster:** built + deep-audited + live-rehearsed with real Qwen (laptop, 20.7 min end-to-end). Five
  campaign-breaking bugs found + fixed (fb3fc11, 8118fb8): container launcher threading, driver load_env,
  cp1251 crash, empty gold-dir bind, and the `--cores-per-training` lever (**cores, not GPUs, gate
  placement** on Myriad — GPU nodes are CPU-saturated at load=36). G1 anchor MEASURED: **32.6 min/training**
  on a Myriad V100-PCIE-32GB (~1.87× laptop). **Still unmeasured (queue-blocked): the packing factor F and
  the live apptainer-on-node path.** Precise campaign wall-clock is owed once F is measured.
- **Campaign wall-clock (honest):** GPU-hours ~2,760 (to 403) / ~3,830 (to 568). Full-pool-packed max is
  short, but realistic fair-share is **days-to-weeks** (~11.5 days at 10 concurrent, ~2.9 days at 40, for
  403); the n=30 distinction-bankable core banks in **~1–2 days**. NOT "under a day" for the full campaign
  (that overclaim was retracted).

---

## 7. Pending — Tamer's acts ONLY (do NOT do these without his explicit per-instance go)

1. Run `.venv\Scripts\python.exe scripts\freeze.py` — stamps `frozen: true` + `freeze_hash` `79a6db44` +
   a decision-log entry. **Freezing is Tamer's act; the tool gates the write to the user.**
2. Force-push both branches (repo history already rewritten to sole-author Tamer, byte-identical trees).
3. Anthropic API top-up ~$70.
4. Rotate the UCL password.

---

## 8. Guardrails for the next session (unchanged, strict)

- **Begin every reply with "Tamer".**
- **Do NOT** freeze, push, or edit any hash-bound file without Tamer's explicit per-instance go. The 8
  hash-bound files are enumerated by the freeze gate; the canonical hash is `79a6db44`.
- **Do NOT** auto-rewrite graded prose or move the freeze hash.
- **Do NOT** reinstall/invoke the Claude Council (deactivated at Tamer's request).
- No prototype number enters the dissertation (directional/plumbing only).
- Stage 2 is report-only, post-bank-gate, prunable to zero — it can never hurt the grade.

---

## 9. The immediate next action (resume here)

Tamer set the target (96%+ floor, ceiling ambition) and asked for full documentation + handoff readiness
(this document). The identified highest-EV next work is the **communication dimension** (§4). The concrete
first step offered and awaiting his go: **draft the plain-language contribution paragraph + the 3-link
mechanism figure spec + the Limitations subsection scaffold.** If he greenlights, start with the
contribution paragraph. Do NOT start more Stage-2 science ahead of the write-up — the write-up is where 96
is won now.
