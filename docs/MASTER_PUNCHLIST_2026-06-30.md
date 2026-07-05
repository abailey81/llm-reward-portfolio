# MASTER PUNCH-LIST — whole-project consistency sweep (2026-06-30)

Consolidates four first-hand sweeps (config/scripts · docs · src/tests · paper) of the entire repo
against this session's decisions (laptop-only compute · B\* pilot-set ~250–350k · buffer cap 50k · the
mechanism-headline reframe · the 4-front paper audit · `frozen: false`). **Identification only — no edits
made in the sweep.** Classification = when/whether to act. The live truth is CLAUDE.md (★ PRIORITIES +
CURRENT STATE + Grade strategy); dated decision records (ADRs, DECISION_LOG, dated audits) are
**append-only — do NOT rewrite them**.

---

## ⚠ THE 2 MOST DANGEROUS IF SHIPPED AS-IS
1. **Theory M3a/M3b — Le Cam deficiency direction errors** (`paper/02_CHAPTER_theory.md:115` formula;
   `:119–123` Cor 3.3). As typed the deficiency is *identically zero* and the corollary names the
   wrong-direction deficiency — it **inverts the central quantitative theorem** in front of the exact
   probabilist examiner most able to catch it. CATASTROPHIC. Fix carefully (correct math).
2. **Suspicious / placeholder citations** — `kvasiuk2026madevolve` (CH2:72, possible hallucination),
   `heavytailsDM2026` (CH7:160), `numeracy_cluster` (CH7:127, a placeholder not a key),
   `distributionalrewardshaping2022` (CH2:97). A co-author examiner catching a fabricated cite is a
   credibility hit. **Verify or cut** at the reference round.

---

## SAFE-NOW (no downside, no sequencing dependency)
- `config/inference.yaml:22` `lambda_frozen: null` → **`0.0`** (ratified λ=0; mirrors prereg
  `fitness.lambda_cvar:0.0`). Flips `determine_design` n_seeds-blocker off. *(NB: inference.yaml is in the
  freeze hash — fine pre-freeze; do with the λ cleanup.)*
- `scripts/determine_design.py` — re-label `cash_daily_rate==0.0` → **DETERMINED** (not FIX_NEEDED, `:229–231`)
  and the `lambda_frozen` method string (`:92`) → "ratified λ=0"; resolves once inference.yaml set.
  *(If taking the script route, update `tests/test_determine_design.py:67–69`.)*
- **Honesty edits (paper prose, no math risk):** C1 "isolates the channel" → "isolates the feedback
  **content** (endogenous; coupled reward→policy→measurement loops)" — `00_FRAMING:31`, `CH1:82`,
  `CH2:90–93`. C2 add the **INCONCLUSIVE** branch — `00_FRAMING:41`, `CH1:90–94`. C3 move the
  bounded-realisation caveat into the bullet — `00_FRAMING:48–54`, `CH1:95–100`. "the first" → "the first
  **of which we are aware**" — `CH4:195`, `CH1:75`, `CH2:78`. Add the **K=5 search-width** limitation —
  `CH7` §B.3 + §7.2.
- `paper/FRONT_MATTER.md` — reconcile the **dual title strings** (`:20–24`) to one; add the **Ethics /
  "no human subjects" / data-governance** statement; fill the **AI-assistance disclosure** stub (`:75–77`).
- `N-6`: C3's "off-critic non-closedness" pillar (`00_FRAMING:48`) is not developed in the theory chapter
  — strike the phrase or add the pillar.

## PHASE-A (engineering pass — do now, tested)
- **Buffer-cap wiring** (the silent OOM trap): add to `config/campaign.yaml` an `agent:` block with
  `buffer_size: 50000`. Honored by `run_campaign.py:1093` guard — but **second edit site**
  `src/orchestration/parallel.py:277` hardcodes `buffer_size=train_steps` with **no cfg override** → add a
  cap read there too. Split the coupled assert `tests/test_run_campaign.py:336–362`; add a new
  decoupled-at-300k test. (The *value* B\* is PILOT-GATED; the *cap wiring* is now.)
- **B1 — gate-failure budget asymmetry** (`src/llm/loop.py:377–394` **and** `parallel.py:645–657` vs
  `random_search.py:259–291`): bounded resample-on-`SandboxError` so each LLM arm yields N **valid**
  candidates (config-driven cap). New test needed. Affects paid Opus call counts → note in compute
  accounting.
- **B2 — reflect-protocol doc/code mismatch** (DOC-ONLY; code is already reflect-on-**best** in both paths,
  `loop.py:482–493`): rename `preregistration.yaml:180` `serial_reflect_on_last` → `serial_reflect_on_best`;
  fix CLI help `run_campaign.py:1430`, `parallel.py:100` comment, prereg/doc strings; confirm
  `freeze.py:488` prose guard still passes; the stale `eureka_loop.yaml`/`prompts/reflection.txt` already
  self-banner as dead.
- **§B1 — candidate-archive winner-resume** (`run_campaign.py:1127`, inside `if winner is None:`): resume
  from archived candidate_ids / select winner from a complete archive without re-billing Opus. New test.
  (Avoids re-paying all 30 Opus calls on a mid-arm crash over the ~2-week run.)
- `config/campaign.yaml` cosmetics: `campaign: rented_rtx_4090` → `rtx_4050` (`:16`); stale `overflow`
  (`:17`); `auto_shutdown_on_complete: true → false` (`:46`, laptop-hostile + the run_campaign banner).
- `scripts/learning_curve.py`: docstring budget default drift (`:43`); `parallelism` default `2 → 3` (`:148`,
  projection only). `config/prototype.yaml:27` stale "rented 4090/50k" comment.

## PILOT-GATED (only after the convergence + σ_D pilots)
- `config/campaign.yaml:12` `train_steps_per_candidate: 50000` → **B\*** (convergence pilot). Update
  `config/algos.yaml:16` documentary value in lockstep. Pin `agent.buffer_size:50000` in the **same** commit.
- `scripts/power_analysis.py:160` `DIRECTIONAL_SIGMA_SEED=0.36` → replaced via `sigma_seed_pilot.py`
  (`--sigma-seed`). Regenerate `docs/DESIGN_DETERMINATION.md` (machine-generated — fix the generator
  default, don't hand-edit).

## PRE-FREEZE (legitimate design edits; land BEFORE `make freeze`)
- **The mechanism-headline reframe** in `config/preregistration.yaml` (`:8` hypotheses framing; `:92–114`
  demote the H2-RA Sharpe IUT to reported-context) **with `freeze.py:347–383` partition assertion updated
  in lockstep** so the prose↔yaml gate passes. Mirror in `PREREGISTRATION.md` + `paper`.
- λ cleanup: delete the inert `inference.yaml` `lambda_grid` (`:21`) + `calibration_fold` (`:23`) (changes
  the freeze hash → must precede the freeze).
- `docs/CAMPAIGN_DESIGN_AND_EXECUTION_PLAN.md` 200k → pilot-set band; σ_D "0.10" → SESOI-derived rule;
  mechanism as the spine (it's pre-freeze methods feedstock).

## WRITING-PASS (the focused editing pass; in parallel with the campaign)
- Theory **intuition-before-machinery** — one plain "the idea is…" sentence before each result
  (`theory:96, 150, 188, 211`).
- Front matter: **ToC / List of Figures / List of Tables** (missing); **inline the real abstract** from
  `00_FRAMING §3` into `FRONT_MATTER:98`.
- **Promote Data to its own chapter that MOTIVATES the method** (move `CH4 §4.2` out; the kurtosis/Hill EDA
  → why a scalar can't convey the tail → the hypothesis) + renumber + fix cross-refs.
- **CH5 Prototype breaks Methods→Results order** — fold into Methods or appendix.
- **"Related Work" → "Literature Review"** (`CH2:1` + cross-refs).
- **De-pre-disclose the result** (foreshadow→predict→deliver; it's stated ~5× before CH6) and **relocate the
  Mayo/Rubin severity argument** out of CH1 (`:118–122`) → CH7 §7.1 (`:29`).
- **Cross-reference every figure/table** (F1–F9, T1–T6) in prose; number the §1a prediction table.
- Strip all literal `% VERIFY` strings, the per-chapter "Citation keys introduced" footers, and the
  `Status: DRAFT` banners from compiled prose.
- Report **wall-clock compute** in prose (Okhrati docks its absence) — `CH6:41` slot + a CH4 sentence.

## REFERENCE-ROUND (pre-submission; HIGH-impact given the co-author examiner)
- **~43 dangling citation keys** (cited in prose, absent from refs.bib) — verify or cut each. Full list in
  the paper-sweep output; load-bearing ones to prioritise: **`song2025reward`** (CH2:52, the counter-claim
  the §2.1 rebuttal hinges on), the 4 suspicious keys above.
- **Key-name mismatches / duplicates:** `sun2024card` cited vs `sun2025card` defined; duplicate Kusuoka
  (`kusuoka2001law` vs `kusuoka2001lawinvariant`); `belzile2020improved` vs `belziledavison2022`; duplicate
  Snoek; orphan `bergstra2012randomsearch` (never cited for the random_search arm).
- **Add `gneiting2011making`** (canonical "ES not elicitable") at `theory §3.5:166–168`.
- Verify the **Claude model version strings** ("Opus 4.8", "Sonnet 4.6") vs ADR-038 (`CH4:107`,
  `FRONT_MATTER:70`, `CH5:24`).

## LEAVE-AS-DATED-RECORD (do NOT rewrite — append-only history)
- `DECISIONS.md` (ADR-023 rented-4090), `docs/DECISION_LOG.md`, `CHANGELOG.md`, all `DEEP_AUDIT_*` /
  `SESSION_LOG_*` / dated reports, `00_planning/_superseded/*`, `config/prototype.yaml` values,
  `config/environment.yaml:13` (cash=0.0 is correct), `config/preregistration.yaml frozen:false`.

## DOCS — NEEDS-SUPERSESSION-NOTE (add a dated top banner, don't rewrite)
- `docs/COMPUTE_AND_TRAINING_TIME.md` (self-labelled "authoritative"; recommends rented 4090; 50k unit),
  `docs/SUPERCOMPUTER_RUNBOOK.md` (UCL-HPC premise rejected), `docs/OPTION_A_compute_enabled_expansion.md`
  (HPC branch; stale 50k baseline), `docs/CAMPAIGN_preflight.md`, `docs/CAMPAIGN_SPEC_ram_thermal.md` +
  `_run_robustness.md` (50k unit; capped-buffer interaction).

## DOCS — SAFE-NOW (live docs that give WRONG current instructions)
- `docs/CAMPAIGN_RUNBOOK.md` — **most likely to be literally executed**; rented-4090 + `--gpu 8` + n_gpu=4
  + 50k commands → re-point to **laptop-only n_gpu=3 + capped buffer + pilot-set steps**; demote rented
  commands to a historical appendix. (Flag the external `~/.claude/plans/toasty-crafting-quill.md` it cites
  as "DEFINITIVE" — verify it's not also stale.)
- `llm-reward-portfolio/README.md` — front door; freeze-as-next-action + CUDA/rented env + non-mechanism
  headline → laptop path + freeze-behind-pilots-and-reframe + mechanism framing.
- Root `dissertation_papers/README.md` — "740+ tests" (stale, now ~1,500); status table + next-action.

---

**Cross-cutting:** the dominant single defect is the hardcoded **`50k`/`50,000`-step unit** across the
operational docs (RUNBOOK, preflight, ram_thermal, run_robustness, COMPUTE) — now *doubly* stale (vs the
200k determination AND the new pilot-set band) and load-bearing (it feeds the DSR trial-count + matched-
compute language). A pre-existing internal contradiction (design docs say 200k, ops docs say 50k) was never
reconciled; the pilot decision is the moment to unify both onto the pilot-set band.
