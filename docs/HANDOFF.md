# ⭐ HANDOFF — the canonical session-continuation entrypoint

> **THE CONTRACT OF THIS FILE.** §1 is a STATE SNAPSHOT that every session REGENERATES (never
> appends) before ending substantive work — it must always describe NOW. §2–§5 are stable and
> change only when the facts they state change. History lives in `CHANGELOG.md` and the
> amendment table, never here. The full protocol is in CLAUDE.md → "SESSION HANDOFF PROTOCOL".
>
> **Read order for a fresh session:** the SessionStart resume-brief (auto) → this file →
> `memory/session-current-focus.md` (the cursor's ▶ NOW entry) → CLAUDE.md (PRIORITIES + the
> four-authority rule + both feedback blocks). Then say "Resuming from: … — next: …" and continue.

---

## §1 STATE SNAPSHOT (regenerated 2026-07-24, session end)

<!-- MACHINE-STATE: auto-managed by `python scripts/update_handoff.py` — the SessionStart hook
     (resume_brief.py) DIFFS this block against live reality at every boot and prints a LOUD
     staleness warning on any mismatch. Never edit by hand; rerun the script instead. -->
```yaml
handoff_state:
  regenerated_utc: "2026-07-24"
  head: "9fb413e"
  frozen: false
  legs_n: 10
  amendments_through: R101
  suite_status: "exit 0 (full suite post-cross-substrate  fixes, PYTEST_RC=0 unpiped; 6 sites + subprocess regression guard)"
  gate_checks: 21
  backup_branch: backup-2026-07-21
```

| Fact | Value |
|---|---|
| Design state | **UNFROZEN** (`frozen: false`; R94 standing order: **the freeze executes together with Tamer's full-campaign-run approval — GO step 1 — never before**) |
| Canonical hash | **recomputed at the GO-day freeze** — R95–R97 landed AFTER the R93 stamp, so the live would-be hash has MOVED off `ccf2e76f` (that stamp + bundle remain valid R93 *history*, commit `30ae72b`); the GO freeze stamps whatever the then-current design hashes to and builds a fresh bundle. Never expect `ccf2e76f` at GO. (Check live: `python -c "import sys; sys.path.insert(0,'scripts'); from freeze import canonical_hash; print(canonical_hash()[:16])"`) |
| Amendments | through **R101** (… R97a kimi cap 8192 · R98 Opus-5 full leg not exercised · R99 Sol/Terra declined, Terra in M2 · R100 idle-tail leg-deepening + the Aug-27 stop · **R101 (2026-07-24, ★ MAJOR) — Okhrati SEED-PARITY, CONFIRMED: all 11 full-loop models run IN PARALLEL AT EQUAL SEEDS, climbing ONE common ladder in LOCKSTEP; SUPERSEDES R88's Opus-above-legs priority, `leg_seed_tier:30`, and R100's idle-tail; final = the common rung banked by Aug-27 (30 guaranteed, ~100–189 expected); headline REFRAMES to mechanism + the pooled cross-model bounded-effect + CVaR-tail + the R87 gradient on a balanced 11-point panel**) |
| ★ R101 DESIGN CHANGE (2026-07-24) | **Registered + applied at the prereg/doc level; launcher/priority CONFIG propagation is GO-prep.** Sequencing: the pending Myriad check/rehearsal jobs finish FIRST → then all 11 launch in parallel → write-up starts now → 30-seed results fill Results provisionally → update in place at each checkpoint → the SINGLE confirmatory look is at the Aug-27 achieved rung. Multiplicity: pooled-primary + BH-FDR secondaries (flagged: if Okhrati wants 11 independent per-model confirmatory tests, promote the FDR family to primary). Identification + m=6 fed vector UNTOUCHED. |
| Roster | **11 full-loop, now ALL EQUAL under R101** = Opus 4.8 (frontier reference) + **10 legs**, all climbing the SAME seed ladder in lockstep (no Opus-privileged depth). Queue order retained only for search/floor ordering. ~35 distinct models with M2 (26 core + 9 extras, R99 Terra seated; 3 documented exclusions) |
| Rule-driven upside | K3 → open-class on the Jul-27 weights (`kimi_k3_upgrade_rule`) · Opus-5 conditional seat (attribution-gated) · the R96 module (Tamer's write-time activation, registry row 25) |
| Execution | MODE D final: **12 launch lines** via `scripts/mode_d_launch.ps1` (core + h3 + 10 legs; ladder −200…−290; pack lanes; pipelined rungs; canary-concurrent; 45s chain polls) |
| Timings from GO (R101-reframed) | mechanism ~L+0.7 · floor ~L+1.5–1.8 · **30-seed COMMON checkpoint (all 11) early — the first Results fill** · then all 11 deepen the common ladder together; **the Aug-27 achieved rung is throughput-bound: 30 guaranteed, ~100–189 expected at fair-share, all-11-to-403 unlikely** (the design trades single-model depth for balanced breadth — Okhrati's call). ⚠ A100 MEASURED (2026-07-24): the workload is CPU/env-bound — the A100 gives NO per-training speedup (probe: ~24 steps/s at 2 cores vs the laptop's ~100 at 4); the A100's only lever is packing/parallelism. Re-estimate the achieved rung from the GO canary's real per-node throughput |
| Verification | freeze gate **21 OK** · **17 full-suite certifications** (15 valid + the re-certified 16th + the 17th post-zero-tolerance-sweep, PYTEST_RC=0 unpiped; the first "16th" was a FALSE GREEN — a `\| tail` pipe masked pytest's RC; caught, re-run genuinely, the unpiped-RC rule now pinned in §5) · citations clean · rung-freshness green · all 3 campaign PS1s parse 0 · backup branch `backup-2026-07-21` |
| Money | expected **~$28 all-in** (campaign) · **Anthropic FUNDED: $25.91 (Tamer, 2026-07-22; key verified LIVE via author_smoke — covers expected ~$10 with 2.6×, $1.09 under the ~$27 worst-at-caps; advisory ledger pauses-not-wastes)** · **OpenRouter: toggle DONE + verified (2026-07-23, 417\|13 — all 8 pinned models route); balance $9.91 → needs exactly +$15** · the R96 module = a separate ~$25–35 P2 line if activated |
| The pre-launch check (2026-07-23/24) | **gates RAN: 10/10 leg verdicts** (catches: .env load, per-leg tolerance, deepseek pin schema-migration think-high→pro, kimi 8192 — R97a) · check jobs **queued on Myriad** (~2.7k qw jam; reserve:y; drivers alive; rehearsal lines land when slots grant) · **★★ BOTH A100-80G POOLS CONFIRMED USABLE: probe_u (10293) ran on node-u00a-001 AND probe_v (10294) ran on node-v00a-002 — while the EF control (10295) is STILL queued (the A100-80G pools were LESS contended for our account than the default EF pool). Full +12 A100-80G unlock for GO; GPU/VRAM class confirmed by the GO-day canary before deep striping** |
| NOT done, by order | **NOT frozen · NOT launched** (both fire only on Tamer's approval, R94); the check's Myriad rehearsal legs still queued |
| Tamer's pending items | ① Okhrati email (draft + the meeting brief ready) ② **OpenRouter +$15** (toggle already done) ③ Windows-Update pause ④ UCL password rotation ⑤ the force-push decision (backup branch protects meanwhile) ⑥ **the full-campaign approval** → fires freeze→gates-reverify→launch (GO ~Jul-27 MORNING) ⑦ ~~RESOLVE with Ramin: SEED-PARITY~~ **✅ RESOLVED 2026-07-24 (Tamer confirmed with Ramin) + APPLIED as R101** (all 11 parallel, equal seeds, lockstep; prereg + docs updated). |
| ★ R101 GO-PREP (config/launcher propagation, before the freeze/launch) | The prereg/docs now register R101, but the LAUNCH mechanics still encode the old asymmetry — do these carefully at GO-prep (the check must finish first): (a) `scripts/mode_d_supervisor.ps1` / `mode_d_launch.ps1` — all 11 lines at EQUAL winner-re-run priority climbing the common ladder (retire the −200…−290 Opus-above-legs ladder for the winner rungs); (b) the seed config so every leg climbs [30,100,189,…] not floor-30; (c) `docs/MODEL_ROSTER_2026-07-22.md` + runbook §9/§10 reframe (all-equal, no idle-tail); (d) the analysis: register the pooled random-effects primary + BH-FDR + the balanced-panel R87 gradient in `analyze_campaign.py`/the analysis plan. |
| Next Claude work | the WRITING month (dimension 4 = the binding constraint under the grade-inflation bar): CH2-argument skeleton, CH1/CH4 depth-passes, wiring D1–D10, the scannable tables — needs no results, no spend |

## §2 STANDING ORDERS (Tamer's, strict — violating any is a defect)

1. **Freeze ONLY with the full-campaign approval** (R94); launch ONLY on his separate explicit GO; gates need his credit.
2. Every reply begins with "Tamer". Sequential-solo, no fan-out agents for build work; verify-then-claim (run the venv pytest, show real output).
3. Spend is ADVISORY (R83) — never add a hard gate. The sealed 2020–2026 leg stays sealed.
4. Amendment rows append AFTER the previous R-row (chronological); registered names need registered VALUES (the R84 lesson).
5. **PS1 files: ASCII-only + `Parser::ParseFile` validation** (BOM-less UTF-8 + PS5.1 turns em-dashes into string-breaking smart quotes); never `git add -A` in this repo (the outputs/ sweep incident); heredocs never carry backslash content (use Write/Edit).
6. The four-authority rule (CLAUDE.md): every substantive decision checked against the PRIORITIES, Okhrati's grading function, the NatWest six, and the IFTE0008 guidelines — grade-inflation year: borderline evidence rounds DOWN.

## §3 THE AUTHORITY MAP (which file owns which truth)

| Truth | Owner |
|---|---|
| The design of record | `config/preregistration.yaml` (`model_suite` + amendment mirrors) + `PREREGISTRATION.md` §14 + rows R79–R100 |
| The executed leg config | `config/legs.yaml` (gate-bound == model_suite; HF pins FILLED) |
| The roster, prices, pins, functions | `docs/MODEL_ROSTER_2026-07-22.md` |
| Launch mechanics | `docs/CAMPAIGN_DAY_RUNBOOK_2026-07-13.md` — §2.0 GO sequence · §9 legs · **§10 MODE D** (the one command) |
| Myriad scheduler + hardware truth | `docs/MYRIAD_EXPERT_DOSSIER_2026-07-24.md` (live-probed formula, pools, two-regime chunking doctrine, dead ends, the ★ priority rule) |
| The live allocation system | `src/cluster/telemetry.py` + `src/cluster/allocation.py` (sensors + brain) · `scripts/allocation_advisor.py` (CLI/--watch; runbook §2.0 step 5) — ADVISORY-only; at GO its values supersede the supervisor's embedded defaults (step 4 precedence note) |
| Write-time obligations | `docs/V2_WRITE_TIME_REGISTRY.md` (rows 1–33; none may silently drop) |
| The optional M2 module | `docs/M2_EXTENSION_OPTIONAL_SPEC_2026-07-22.md` (R96) |
| Prose drafts awaiting wiring | `paper/DRAFTS_communication_build_2026-07-12.md` (D1–D10) |
| The writing plan | `docs/WRITEUP_95PLUS_PLAYBOOK.md` (under the raised bar; registry rows 19–24) |
| Session history | `CHANGELOG.md` (definitive per-session records) · the cursor's ▶ EARLIER entries |
| Supervisor comms | `docs/DRAFT_EMAIL_OKHRATI_2026-07-20.md` (dates made relative) · `docs/NATWEST_RESPONSE_BRIEF_2026-07-20.md` (two-credibilities) · `docs/DISSERTATION_COMPLETE_BRIEF_FOR_RAMIN_2026-07-21.md` (the meeting brief; currency-noted) |
| Dated planning references (NOT triggers) | `docs/V2_MASTER_PLAN_2026-07-20.md` · the model sweeps |

## §4 THE AMENDMENT LEDGER (one line each; full rows in PREREGISTRATION.md)

R78 unfreeze-v1 · R79 prompt format · R80 model_suite · R81 spend+protocol · R82 completeness ·
R83 spend→ADVISORY · R84 anchor+T0 pinned · R85 HF pins+temp+round-trip · R86 pooled bound ·
R87 falsifiable gradient · R88 queue=priority-ladder (mode D) · R89 M2 extras+2 · R90 sonnet-5
seat (its pair died with R92) · R91 Opus-5 conditional · R92 sonnet-4.6 removed (bridge
withdrawn) · R93 the freeze-day evidence (executed ccf2e76f) · R94 the same-day lift
(freeze=GO-step-1) · R95 K3 seated · R96 the optional psychometric module · R97 the differential
downside deviation ratio seated (Moody & Saffell 2001, first-hand) + the ten-name secondary
panel's execution path (runbook §9(h)) · R97a kimi cap 4096→8192 (gate evidence: 5/10 truncations
under always-on thinking; per-class pins, the one registered exception) · R98 the Opus-5 full leg NOT exercised (Tamer's budget decision; M2-only fallback) · R99 Sol/Terra full legs DECLINED (budget, pre-event; Terra seated in M2 — the 3-pt GPT-5.6 reading ladder; the full-loop ladder = the named first Stage-2 extension) · R100 the idle-tail deepening rule, ORDER: legs-first after 403, core 568 last-if-it-fits, stop 2026-08-27 (GO-day may only move it EARLIER).

## §5 FIRST ACTIONS FOR A FRESH SESSION

1. Read per the §0 read order; state "Resuming from: … — next: …".
2. `./.venv/Scripts/python.exe -m pytest -p no:cacheprovider -p no:warnings -q` → expect exit 0;
   `freeze.py --check` → 21 OK, `frozen: false`. **THE CERTIFICATION COMMAND IS RUN UNPIPED and
   the verdict is pytest's OWN exit code** — never `pytest | tail`-style pipes (`$?`/`$LASTEXITCODE`
   then reports the pipe tail's exit, not pytest's: the 2026-07-24 false-green lesson). Redirect to
   a log file and `tail` the FILE instead.
3. If Tamer's credit landed → run the leg gates (`scripts/leg_gates.py --all`). If he gives the
   full-campaign approval → runbook §2.0 (freeze first) then §10 (`mode_d_launch.ps1`). If
   neither → the writing month (see §1 last row). NEVER freeze or launch without the words.
4. Before ending substantive work: `python scripts/update_handoff.py --suite-status "exit 0
   (Nth certification)"` (regenerates the machine block; then review §1's prose rows by hand),
   prepend a SHORT cursor ▶ NOW entry (≤15 lines, pointing here), update CHANGELOG if commits
   were made, push the backup branch. The SessionStart hook DIFFS the block at every boot —
   skipping this step gets caught loudly next session.
