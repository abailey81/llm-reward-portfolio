# Deep review + council + data/benchmark/lit sweeps — 2026-07-05

**Mandate (Tamer).** "Very deeply understand the whole project; install & use the Claude Council; deeply
review/fix everything (code, logic, files, lines); then deeply mine the corpus + fresh deep-research for
anything missing / any way to make the dissertation deeper/more advanced. Priorities first. Nothing frozen.
Add a deep DATA sweep + an advanced BENCHMARK sweep. Do it sequentially, be careful with tokens. Document
everything at the end."

**Verified invariant at end of session:** freeze gate **17/17 GREEN @ hash `1c6b76b6`** (UNCHANGED — no
hash-bound file was touched), `frozen: false`; ruff clean on all touched files; the 3 touched test files +
their new tests **46 green**; PDF `paper/_build/dissertation.pdf` **315 KB, 0 pandoc warnings**;
`check_citations` **0 dangling / 0 verify-in-use / 0 literal**.

---

## 1. What was done

1. **Claude Council installed** (from `reshadat/claude-ai-council`, MIT; vetted — no injection, no network/shell
   beyond Claude Code subagents). Adapted to this repo: `.claude/commands/council.md` + personas in
   `.claude/agents/` (skeptical-architect, generative-architect, **examiner-okhrati**, **statistics-referee** —
   the last two authored for this project). Invoke with `/council`.
2. **Disaster-proofing:** committed 6 days of pre-freeze WIP as protective snapshot `cbe269c` (564 files,
   no secrets/licensed payloads staged — gold/raw parquets stay ignored); `.gitignore` hygiene
   (`.venv-lseg`, logs, scratch); deleted recorded scratch (`scripts/_seed_mde_sweep.py`, `outputs/_bytecheck`);
   `mirror_archive.ps1` first pass verified (15 MB → `D:\llm_rp_archive_mirror`). **Push is Tamer-gated** (remote
   is `abailey81/llm-reward-portfolio`).
3. **Personal deep read** (per Tamer): whole `.claude/` tree, all run logs, `PREREGISTRATION.md` (all amendments
   D2→R75), `DECISIONS.md` (ADR-001→051 incl. the ADR-049 false-positive register), `CHANGELOG`, the key `docs/`
   ledgers, and the UCL guidelines + marking-criteria PDFs (read first-hand via PyMuPDF).
4. **13-auditor deep-understanding map** (read-only fan-out, adversarially evidenced): **0 critical, 19 major,
   63 minor** candidate findings, each with file:line + the concrete failure it causes.
5. **Council #1** (4 seats) deliberated the 5 contested design calls; **data sweep**, **advanced-benchmark
   sweep**, and **fresh-literature deep-research** ran as scoped workflows. (Some sub-agents aborted on an
   Anthropic session limit ~mid-run; the load-bearing findings all returned.)
6. **Fix wave** — 10 verified fixes applied (below); heavier/gated items routed to the brief
   (`docs/SESSION_BRIEF_2026-07-05.md`).

---

## 2. Fixes applied this session (all verified, all NON-hash-bound → hash unchanged)

| # | Finding | Fix | Verify |
|---|---------|-----|--------|
| M03 | **Sandbox AST gate ignored expression context** — `np.mean = ...`, `del np.mean`, `np.pi += 1` passed the allowlist and executed in-process; numpy is process-global + workers are reused → cross-candidate poisoning / determinism break. | `ast_gate` now rejects any `ast.Attribute` whose ctx is not `Load` (`src/sandbox/executor.py`). +3 mutation-vector regression tests. | `test_audit_regressions` 26 pass |
| M18 | **`purge_suffix.py` destructive-tool guard asymmetry** — protected/active guards compared by equality but victim selection was substring, so `--suffix _univ --yes` passed the guards yet matched EVERY universe artifact incl. the frozen headline panel. | Require a digit-bearing suffix + match on a token boundary regex (`_univ5s?(?=[._]|$)`), applied to victims AND ledger-drop. | live: `--suffix _univ` REFUSED; `--suffix _univ5` REFUSED (active) |
| M06 | **`determine_design` false FREEZE-READY** — reported n_seeds DETERMINED (and the chain FREEZE-READY) at the pre-pilot 30-seed placeholder although measured σ_D=0.369 fires the pre-registered ">0.10 → raise seeds" trigger. | Gate n_seeds PENDING when the trigger fired AND config seeds ≤30 (the placeholder); clears when amended past 30 or if σ_D≤0.10. Regenerated `DESIGN_DETERMINATION.md` → now BLOCKED on `n_seeds`. +1 test. | `test_determine_design` 12 pass; live BLOCKED |
| — | **`mirror_archive.ps1` leaked robocopy's success code** (1 = "files copied") as a failing script exit. | Map robocopy 0–7 → exit 0; reserve non-zero for a real ≥8 failure. | re-run → exit code **0** |
| — | **`freeze_guard.py` hook out of sync** — didn't protect `config/algos.yaml` (became B\*-assert-bound in batch-6 M1). | Added `config/algos.yaml` to `_BOUND_RELPATHS`. | `--selftest` all cases pass |
| — | **UCL presentation compliance** — build used LaTeX defaults, not the mandated 1.5 line spacing / Helvetica-family ≥10pt. | `build_paper.py` +`linestretch=1.5` +`helvet` sans default (portable, Tectonic-cached). | PDF rebuilds 0-warn |
| M05 | **Runbook would make an operator kill a CORRECT launch** — GO/NO-GO said verify `steps=50000`; frozen B\*=200,000. Wall-clock figured at 50k (2.6 days). | Banner + GO/NO-GO → `steps=200000` (flag 50k as the mis-config to catch); wall-clock block marked SUPERSEDED (→ ~23 days at ~350 seeds). | — |
| — | **Runbook internal contradictions** — §10 post-run checklist said "PopArt absent" (contradicts §5 "ON since R42" → would seed a false limitation); §8 said "univ4r the correct re-pull" (superseded by univ5s). | Both reconciled. | — |
| M09 | **CH4 delisting-band unit ×20 overstatement** — "moves CVaR-5% by ~two percentage points"; the measured move is ~2% RELATIVE (≈0.11 pp). Baked into the CH6 fill contract. | CH4 → "about two percent in relative terms (of order a tenth of a percentage point)". | PDF rebuilds |
| M16 | **Legible sub-experiment is INERT + would burn ~1,500 paid Opus calls** — at `generations=1` the legible rendering only changes the archived block, never a prompt, so the SQ3b differential is ~0 by construction. | Fail-loud money guard in `run_subexperiment` (refuses `mode=legible` unless `allow_inert_legible=True`, set only in mocked tests). Full redesign → brief. | `test_subexperiment` 8 pass |

---

## 3. Deep DATA sweep — verdict (litmus: identification-safe, report-only, examiner-value)

**Premise corrections from the on-disk verifier (first-hand):** BAB/QMJ/FF5 are **NOT on disk** (only FF3 +
Momentum); the brief's earlier "BAB/QMJ on disk" was wrong. Three genuinely **licensed-and-already-pulled but
zero-consumer** assets are the high-value wins (all report-only, no identification impact, no prereg amendment
for report-only rows):

- **TIER A — `.SPXTR` S&P 500 total-return index** (`data/raw/rf_spxtr*.csv`, 2005→2026-06-30, on disk, no
  consumer): closes the self-reported "no cap-weighted market benchmark" limitation (audit P29). One loader +
  one reporting row → market-relative alpha/beta/IR next to the `market_ew` line. **Best single data win.**
- **TIER A — bid/ask spread panels** (`rf_bid_*`/`rf_ask_*`, 963 RICs, pulled for "cost_calibration", zero
  consumer): a report-only EDA figure of realised half-spread over the test window (incl. 2020-03 stress)
  **grounds the pre-registered [0,5,10,25,50] bps cost grid in the study's own data** — exactly Okhrati's
  motivate-with-data. Grid stays frozen; this only evidences it.
- **TIER B — pull BAB/QMJ + FF5 daily** (free AQR + Ken-French, URLs in `docs/CAMPAIGN_attribution.md:166`):
  **fulfils the already-frozen** `factor_attribution.controls_for = [betting_against_beta, quality]` prose (no
  amendment needed) — without them the ff5/ff6/ff6_bab/ff6_bab_qmj attribution rungs report "skipped", and
  BAB is the pre-registered "headline rival" (the low-beta-harvest objection). ~1h.
- **MINOR code fix (recorded):** `attribution.py:738,746` reads RF/Mom from the canonical French CSVs (end
  2026-04-30), bypassing the `_x26` refresh (end 2026-05-29) → 2 of 78 test months stale-ffilled. One dict
  entry in `_REFRESHED_RAW` + route through `_raw_path`; re-run `refresh_french_2026.py` at analysis time.
- **REJECTED:** anything feeding the agent new state (identification); pre-2005 / options / more-candidates
  (settled NOs).

## 4. Advanced BENCHMARK sweep — verdict

**Ground truth (repo verifier, first-hand):** all **8** frozen allocators + all **9** hand-written rewards are
**implemented and tested** (`src/baselines/{strategies,rewards}.py`), correctly (Ledoit-Wolf tangency, convex
Spinu ERC, HRP, Choueifaty-Coignard MDP with the right algebra). So the panel is NOT strawman-thin.

- **The single best addition = a min-CVaR (Rockafellar-Uryasev 2000 LP) allocator** — genuinely MISSING and the
  natural tail-aware comparator in a CVaR-feedback study; analysis-time (pure portfolio LP at analyze time),
  ~free compute, closes the "no tail-aware benchmark" attack. Needs a one-line §9 amendment to register it.
- **The §9 nine-vs-four gap (MAJOR):** frozen §9 promises the NINE hand rewards are "reported as a secondary
  panel"; the executed pipeline trains/reports only the **4-name** H1 family (the other 5 are implemented but
  unrun). **Council (both seats): "B+C fused"** — amend §9 pre-freeze to register a two-tier design (4-name
  confirmatory @ full seeds unchanged; the 5 extras — drawdown, downside/Sortino, log-growth/Kelly are the 3
  genuinely-distinct shapes; MV-utility + turnover near-duplicates — as a registered **descriptive panel @ ~10
  seeds**, excluded from H1 best-of selection, asymmetry disclosed ex-ante). ~1 trailing GPU-day. → Tamer
  decision (compute + hash-bound §9 edit).

## 5. Fresh LITERATURE deep-research (2026-06-20 → 07-05) — verdict

**No scoop.** ~9 new **fence neighbours** (all robotics / non-finance / not-reward-code / not-pre-registered),
none occupying the conjunctive cell. Highest-priority fence addition: **`2605.28918` "When LLM Reward Design
Fails"** — a *controlled comparison of feedback given to a reward-authoring LLM* (metrics-only vs failure-mode
taxonomy), MiniGrid/MuJoCo, no finance/tail/pre-reg → convergent non-finance evidence that feedback content is a
live causal variable; qualify any "first controlled comparison" claim with the finance/portfolio/tail cell and
cite this as convergent support. Others: RDA (`2606.01672`), LLM-ALSO (`2605.29293`), FORGE, CARD (`2410.14660`),
Moira pair-trading (`2605.01954`), LM-guided-RL-trading (`2508.02366`), AlphaMemo (`2606.20625`), a reflexivity
forecasting content-manipulation study (`2606.00061`). All → the pre-submission fence pass (verify first-hand
before citing; the adversarial-verify leg aborted on the session limit, so treat these as **unverified leads**).

---

## 6. Routed to `docs/SESSION_BRIEF_2026-07-05.md` (Tamer decisions / gated / careful work)

Freeze-gate additions (council: adopt, as ONE batched hash move) · the mechanism-kernel rewire (M13/M14 — the
originality instrument measures own-tail-not-fed-tail; report-only, post-campaign timing, deserves careful
implementation + prototype-archive validation) · TOST tail margin (M11) · §9 two-tier panel + min-CVaR
allocator · R76 hash-bound wording batch (M17 log-returns, inference.yaml header) · H3-pooling verification
(M15) · H1/H3 parallel-husk status (M19) · the write-up prose items (Table 3.1 drift M10, CH7 scorecard, CH6
slot contract M12, LIMITATIONS_REGISTER staleness M01, repo-filename leaks) · the corpus-priority-4 citation
gaps (troop2021 in prose, duan2021dsac in CH2) · P4 algos-explicit · the ~60 minor doc/comment staleness items.
