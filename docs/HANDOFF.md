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

## §1 STATE SNAPSHOT (regenerated 2026-07-22, session end)

| Fact | Value |
|---|---|
| Design state | **UNFROZEN** (`frozen: false`; R94 standing order: **the freeze executes together with Tamer's full-campaign-run approval — GO step 1 — never before**) |
| Canonical hash | `ccf2e76f…` (state scalars are hash-excluded → the GO-day freeze re-stamps this same hash if no design change lands; bundle `prereg_bundle_ccf2e76f.zip` already valid) |
| Amendments | through **R96** (R93 freeze-prep evidence retained · R94 lift · R95 K3 seated · R96 the OPTIONAL M2 psychometric module, not activated) |
| Roster | **11 full-loop** = Opus 4.8 confirmatory + **10 legs** (queue: deepseek → glm → qwen27 → qwen9 → haiku → luna → nemotron → sonnet-5 → gemini → kimi-k3); ~35 distinct models with M2 (25+9) |
| Rule-driven upside | K3 → open-class on the Jul-27 weights (`kimi_k3_upgrade_rule`) · Opus-5 conditional seat (attribution-gated) · the R96 module (Tamer's write-time activation, registry row 25) |
| Execution | MODE D final: **12 launch lines** via `scripts/mode_d_launch.ps1` (core + h3 + 10 legs; ladder −200…−290; pack lanes; pipelined rungs; canary-concurrent; 45s chain polls) |
| Timings from GO | mechanism ~L+0.7 · **floor ~L+1.5–1.8** (BO-bound) · all legs ~L+4.5–5.5 · **tier-403 ~L+13–14.5** · 99% rung likely from a ≤Jul-25 GO |
| Verification | freeze gate **21 OK** · **10 full-suite certifications** (all exit 0) · citations clean · rung-freshness green · both PS1s parse 0 · backup branch `backup-2026-07-21` == HEAD |
| Money | expected **~$28 all-in** (campaign) · top-ups: **Anthropic ≥$35 · OpenRouter ≥$25** + the do-not-log toggle · the R96 module = a separate ~$25–35 P2 line if activated |
| NOT done, by order | **NOT frozen · NOT launched · gates NOT run** (need OpenRouter credit; pre-launch per R93e) |
| Tamer's pending items | ① Okhrati email (draft + the meeting brief ready) ② top-ups + toggle ③ Windows-Update pause ④ UCL password rotation ⑤ the force-push decision (backup branch protects meanwhile) ⑥ **the full-campaign approval** → fires freeze→gates→launch |
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
| The design of record | `config/preregistration.yaml` (`model_suite` + amendment mirrors) + `PREREGISTRATION.md` §14 + rows R79–R96 |
| The executed leg config | `config/legs.yaml` (gate-bound == model_suite; HF pins FILLED) |
| The roster, prices, pins, functions | `docs/MODEL_ROSTER_2026-07-22.md` |
| Launch mechanics | `docs/CAMPAIGN_DAY_RUNBOOK_2026-07-13.md` — §2.0 GO sequence · §9 legs · **§10 MODE D** (the one command) |
| Write-time obligations | `docs/V2_WRITE_TIME_REGISTRY.md` (rows 1–25; none may silently drop) |
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
(freeze=GO-step-1) · R95 K3 seated · R96 the optional psychometric module.

## §5 FIRST ACTIONS FOR A FRESH SESSION

1. Read per the §0 read order; state "Resuming from: … — next: …".
2. `./.venv/Scripts/python.exe -m pytest -p no:cacheprovider -p no:warnings -q` → expect exit 0;
   `freeze.py --check` → 21 OK, `frozen: false`.
3. If Tamer's credit landed → run the leg gates (`scripts/leg_gates.py --all`). If he gives the
   full-campaign approval → runbook §2.0 (freeze first) then §10 (`mode_d_launch.ps1`). If
   neither → the writing month (see §1 last row). NEVER freeze or launch without the words.
4. Before ending substantive work: regenerate §1 here, prepend a SHORT cursor ▶ NOW entry
   (≤15 lines, pointing here), update CHANGELOG if commits were made, push the backup branch.
