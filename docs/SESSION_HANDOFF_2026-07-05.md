# SESSION HANDOFF — 2026-07-05 (for a fresh Claude Code chat)

> **Purpose.** A point-in-time snapshot so a NEW chat continues seamlessly. Read this AFTER the auto-loaded
> `memory/session-current-focus.md` (the LIVE cursor) + `CLAUDE.md` (priorities/contract) + `MEMORY.md`. This is a
> **dated snapshot** and is NOT kept in sync — the cursor is the living state. Where they disagree, the cursor +
> `scripts/freeze.py --check` win.

## 0. The absolute rule
Every message you send MUST begin with **"Tamer"** (enforced in global + repo `CLAUDE.md`). No exceptions.

## 1. How to resume (mechanics)
- A new chat auto-loads: repo `CLAUDE.md`, global `CLAUDE.md`, `MEMORY.md`, `memory/session-current-focus.md`,
  and a SessionStart hook runs `scripts/resume_brief.py` (computes live git/phase state each start).
- Say **"Resuming from: <state> — next: <action>"** and CONTINUE. Do NOT ask "what would you like to do."
- Before ending substantive work, UPDATE `memory/session-current-focus.md`.
- Interpreter: use `./.venv/Scripts/python.exe` (the system Python has no numpy/torch). `.venv-lseg` is the
  Refinitiv pull env (PowerShell only). Combined full-suite pytest can rarely hit a pyarrow-vs-torch import-order
  SIGSEGV — run per-file if it bites.

## 2. Current VERIFIED invariant (2026-07-05)
- Phase: pre-registration **NOT frozen** (`config/preregistration.yaml: frozen: false`). Pre-freeze; pilots done
  (B\*=200k convergence + σ_D farm), Split-C + `univ5` panel live.
- **Freeze gate: 17/17 checks GREEN**; canonical SHA-256 =
  `1c6b76b68e2a7bbcf36608303333b6bb070cd016b1c61ee36c2493f6186edbae` (`1c6b76b6`); `frozen: false`.
- Full pytest suite: **exit 0, 0 failures** (re-confirmed 2026-07-05 after this session's edits).
- PDF `paper/_build/dissertation.pdf`: **335 KB, 0 pandoc warnings**, 8 chapters + 1 appendix (Limitations).
- Citations (`scripts/check_citations.py`): **0 dangling / 0 verify-in-use / 0 literal VERIFY**.
- `ruff`: clean on all touched files.

## 3. ⚠ THE HASH MOVED — this is EXPECTED; do NOT "restore" it
Chain: `3c2082…` → `5117d739` → `cedc576b` → `1c6b76b6`. Four **authorized pre-freeze WORDING batches** under
Tamer's explicit "make absolutely everything strictly flawless, full permission" mandate. **NO decision, number,
split, hypothesis, SESOI, seed, arm, budget, λ, or Troop-deferral changed** — only factual-accuracy wording in the
hash-bound `PREREGISTRATION.md` + `config/inference.yaml`. A fresh `freeze.py --check` shows `1c6b76b6`; that is
CORRECT. Do NOT revert toward `3c2082`.

## 4. What THIS session accomplished (the flawlessness push)
The 30-probe code sweep + 20-agent corpus dive backlog is **FULLY worked through**. Ledgers:
`docs/OVERNIGHT_DEEP_LOOP_2026-07-04.md` (rows 25–31 + the running HB row), `docs/DEEP_SWEEP_30_FINAL_2026-07-04.md`,
`docs/CORPUS_MINING_2026-07-04{,_PART2,_PART3}.md`, `CHANGELOG.md`.
- **Non-hash-bound safe applies:** P24 (`np.random.default_rng(0)`×9 in `src/inference/`); P20/P19
  (`measurement.py` EVT `try/except` + `isfinite` guards + `threshold_sensitivity.n_empirical_fallback`);
  P14-F4/F2 (strict equivalence figure + `_frozen_equiv_margin`); P23 + P10-F4 regression tests; a docstring cluster.
- **Heavier applies:** P25 repro-verifier promotion (`scripts/audit_reproducibility.py`); P28 structural (phantom
  "Appendix A" removed, References-before-Appendices order, citation-annotation leaks stripped); P30 theory
  precision ×5 (auditor-verified — Cor 3.3 **2δ not δ**, Kusuoka **atomless** precondition, RN-derivative **Q-a.s.**,
  L¹ preconditions, `acerbi2002spectral` wired); corpus bib-wiring (**6 dead orphan refs now live in the PDF**).
- **Hash-bound pre-registration WORDING:** P9 (COVID → "post-COVID-crash recovery + elevated-vol regime"; the
  19 Feb–23 Mar 2020 crash is INSIDE the val→test purge, scored window opens ~2020-03-30); P20 (the "GPD ξ≤0 for
  ~94%" Troop-deferral rationale reframed as small-sample **negative BIAS**, NOT a light-tail claim); P17 (R64
  leg-p pointer); dated **R75** amendment row.
- **TWO adversarial audit rounds caught real issues in my OWN edits → ALL corrected** (author/reviewer separation):
  - Round 1 (prereg auditor): P17 **skew direction** (halving `p_two/2` is anti-conservative under **RIGHT**-skew,
    not left; the ΔCVaR bootstrap skew is unmeasured → reworded **skew-agnostic**); P20 **SE-vs-BIAS**; the "+0.2"
    traceability.
  - Round 2 (2 auditors): the skew claim SURVIVED in 5 more sites — the **R64 row TITLE**, the **PDF appendix
    B.5.5** (+ an unsourced "0.05–0.06" size that the symmetric null-calibration cannot produce),
    `analyze_campaign.py` ×3, `power_analysis.py` "LIVE-rule" comments, `test_properties.py` — PLUS a
    `measurement.py` contradiction (still called the losses "near-light-tailed", contradicting the corrected §4).
    ALL fixed skew-agnostic / bias-framed; the untraceable "SE≈0.14 / univ5 +0.2" softened to the theoretical
    regular-variation argument.
- **Code changes this session (all non-hash-bound):** `scripts/run_campaign.py` `stage_completion_status` helper
  (fixes a **pre-existing WIP bug**: `frozen_test_deferred` was decided by re-checking `SHUTDOWN.is_set()` AFTER the
  test leg → now `n_done < n_expected`; a completed arm is correctly "tested"); `src/agents/popart.py` `raw_rms`
  instrumentation; `src/feedback/measurement.py` `n_empirical_fallback` + EVT guards + bias reframe;
  `analyze_campaign.py`/`power_analysis.py`/`test_properties.py` `p_two/2` wording. **Removed a stray junk file**
  `CH7body:"` (a botched-redirect artefact, 25 bytes).
- **Verification discipline each step:** freeze 17/17 @ the current hash, ruff clean, targeted + full pytest, PDF
  build, `check_citations`, and a completeness grep confirming **0 surviving wrong-direction CVaR-skew claims**
  (only the correct `bootstrap.py:209` precise wording + audit-trail rows remain).

## 5. ⚠ THE OVERNIGHT LOOP — decide what to do with it
- An **autonomous 10-minute-cadence idle-heartbeat loop** is running in the OLD chat (Tamer: "do it every 10 min"),
  self-scheduled via `ScheduleWakeup`. It has been **idle ~38 ticks** (the safe backlog was exhausted at row 31);
  each tick only runs `freeze.py --check` and bumps the single running HB row in `docs/OVERNIGHT_DEEP_LOOP_2026-07-04.md`.
- **It is SESSION-BOUND.** Starting a NEW chat does NOT inherit the schedule. So:
  - If Tamer wants the heartbeat to continue in the new chat → re-issue the loop (exact text in §8).
  - If not → let it lapse. The work is complete, so lapsing is the honest default (do NOT manufacture work).
  - The OLD chat's loop may keep firing until that session is closed / Tamer says "stop" there.

## 6. PENDING work (all Tamer-gated — nothing further is safe to do autonomously)
- **Compute-gated / results-changing (do NOT execute without an explicit go):**
  - **P6** — cost-ledger contemporaneous look-ahead (env-dynamics; fixing it **re-baselines** the σ_D/convergence
    pilots).
  - **P5** — PopArt `min_scale` one-sided shrink / affine control (adds compute).
  - **Seed ratification ~350** — arm-adaptive (H2 arms ~350, controls 30), ~23 days, deadline-safe. THE pending
    pre-freeze decision. Feeds the Okhrati email + the seed amendment (`config/preregistration.yaml` +
    `config/campaign.yaml` + prereg §6). See memory `project-sigma-d-verdict-and-seeds-2026-07-03`.
  - **repo-wide `ruff format`** — a pre-existing format drift (CI is green); cosmetic, touches many files.
  - **(optional)** switch `power_analysis` code `p_two/2` → the direct upper-tail statistic (NOT a defect — a
    documented symmetric-DGP approximation; would slightly shift the reported MDE).
- **USER-gated milestones:**
  - **Okhrati's email reply** — drafted + sent, awaiting his response; pivot sign-off
    (`docs/PROPOSAL_PIVOT_DISCLOSURE.md`) still owed.
  - **The FREEZE button** — `scripts/freeze.py` (no `--check`), a USER-only act, once seeds are ratified.
  - **Campaign launch** — Opus 4.8 + Qwen3-Coder, laptop-only (RTX 4050, Turbo 140 W, `n_gpu=3`, buffer cap 50k),
    ~23 days at ~350 seeds. Run-day checklist in `docs/CAMPAIGN_RUNBOOK.md` §0b.

## 7. The gate / roadmap
**freeze → run → write.** Land seed ratification + Okhrati's reply → amend seeds → `freeze.py` (USER) + OSF deposit
→ run the laptop campaign (~23 d) → write Results + Discussion + apply the fix registers. The confirmatory NULL is
pre-committed and bankable (σ_D verdict: σ_seed=0.244, σ_D=0.369, ρ=−0.141 → practical equivalence at SESOI 0.05
unreachable at small n → the **bounded-effect / mechanism headline** carries it; σ_seed dominance is itself a
finding).

## 8. Things NOT to re-do / re-litigate
- Do NOT restore hash `3c2082` (the moves are authorized — §3).
- Do NOT re-fix the skew wording — it is now skew-agnostic + correct everywhere. **`src/inference/bootstrap.py`
  (~line 209) is the GOLD-STANDARD wording** ("anti-conservative when the UPPER tail beyond +obs is the heavier
  one, conservative when the lower tail is"). Match it, don't "correct" it.
- Check the **ADR-049 false-positives register** (`DECISIONS.md`) before "re-fixing" anything an audit flags.
- Settled NOs (do not re-propose): 2000-start, options, more candidates, multi-agent/RAG/GNN/new-pipeline scope,
  cloud compute at the $50 budget, `torch.compile` (dead on native Windows).
- Novelty is TRIPLE+ confirmed intact (0 scoops across 210 corpus PDFs) — do NOT re-run the scoop sweep except the
  scheduled pre-submission one.
- Okhrati is **"Dr" not "Prof"** — the front matter is correct; leave it.
- The pre-registration is hash-bound: post-freeze, any change needs an explicit dated amendment approved by Tamer.
  Pre-freeze wording edits are legitimate but MUST keep the 17 consistency checks green and change no decision.

## 9. Re-arm text for the loop (paste into the NEW chat ONLY if Tamer wants the heartbeat to continue)
```
Overnight sequential deep-improvement loop — every 10 minutes. The concrete safe backlog is EXHAUSTED
(docs/OVERNIGHT_DEEP_LOOP_2026-07-04.md rows 25–31 + the HB row); the pre-freeze invariant is 17/17,
hash 1c6b76b6, frozen:false. Each wake: re-read the overnight log + memory/session-current-focus.md,
run ./.venv/Scripts/python.exe scripts/freeze.py --check and confirm 17/17 + hash 1c6b76b6 + frozen:false
(if not, STOP and flag — do not "fix"). If nothing genuinely new + safe, do an HONEST IDLE HEARTBEAT
(bump the single HB row in place, do not manufacture work), post a one-line status, and re-schedule this
prompt at delaySeconds 600. HOLD for Tamer's steer on the compute-gated items (P6, P5, seed ratification
~350, ruff-format) and the USER-gated milestones (Okhrati reply, freeze, campaign). Hard stops only:
gate breaks (hash ≠ 1c6b76b6 or <17 checks) or credits low.
```

## 10. Key file map
- Live cursor (read first): `memory/session-current-focus.md`
- Contract + priorities: `CLAUDE.md` (repo) + global `CLAUDE.md`; memory index: `MEMORY.md`
- Overnight pass log: `docs/OVERNIGHT_DEEP_LOOP_2026-07-04.md` (rows 25–31 + HB row)
- Deep sweep ledger: `docs/DEEP_SWEEP_30_FINAL_2026-07-04.md`; corpus mining:
  `docs/CORPUS_MINING_2026-07-04{,_PART2,_PART3}.md`
- Freeze machinery: `scripts/freeze.py`; pre-registration (hash-bound): `PREREGISTRATION.md`
- Campaign design/plan: `docs/CAMPAIGN_DESIGN_AND_EXECUTION_PLAN.md`; runbook: `docs/CAMPAIGN_RUNBOOK.md`
- σ_D verdict + seed decision: memory `project-sigma-d-verdict-and-seeds-2026-07-03`
- Decisions/ADRs: `DECISIONS.md` (root, authoritative) incl. the ADR-049 false-positives register
- Paper chapters: `paper/CH1…CH7` + `paper/02_CHAPTER_theory.md` + `paper/APPENDIX_B_limitations.md`

## 11. Project one-paragraph refresher (authoritative detail in `CLAUDE.md` + memory)
An LLM (Opus 4.8) authors reward-function **code** for a fixed SB3 SAC risk-sensitive portfolio RL agent; the single
manipulated variable is the reflection-loop feedback **content** (a multi-level left-tail CVaR/ES vector vs a scalar);
7 arms; pre-registered; the predicted **null** is reframed as a **mechanism** finding ("does showing the LLM the
downside change the reward code it writes?"). Graded **PDF-only** by Dr Ramin Okhrati (measure-theoretic
probabilist, coherent-risk / offline-RL) + a second marker; deadline **1 Sep 2026**; **10,000-word** body limit.
Four priorities: (1) 95%+ grade floor → 100%; (2) TMLR-publishable; (3) very deep/mechanistic; (4) corpus-grounded
(cite-and-USE the 196+/210-paper corpus) + genuinely novel.
