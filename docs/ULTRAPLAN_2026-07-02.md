# ULTRAPLAN — the master execution plan to submission (authored 2026-07-02)

> **The single authoritative plan.** Supersedes scattered phase notes; every prior decision it
> builds on is cited (ADR / memory / CHANGELOG). Update THIS file when the plan changes — a plan
> change without a dated edit here is a process defect. Owner legend: **[U]** = only Tamer can do
> it; **[C]** = Claude executes; **[U→C]** = Tamer gates, Claude executes.

---

## §0 North star + standing protocols (non-negotiable)

**Priorities (CLAUDE.md ★★★):** (1) grade 95%+ floor → 100 (UCL top band); (2) world-class /
journal-publishable (TMLR+); (3) very deep — mechanism, intuition, originality. Every step below
exists because it serves at least one of these; anything that serves none gets cut.

**Standing protocols (apply to every phase):**
1. **Document everything, always** (user directive 2026-07-02): every session ends with a
   CHANGELOG entry; every decision gets an ADR in `DECISIONS.md`; the memory cursor
   (`session-current-focus.md`) is updated before ending substantive work; every operational
   change lands in `docs/CAMPAIGN_RUNBOOK.md`; long operations get a `docs/SESSION_LOG_*` entry.
   Nothing happens undocumented.
2. **Verify, then claim** — no "done" without the command + real output; subagent work is always
   independently re-verified (no self-grading).
3. **The false-positives register** (ADR-049) is checked before "re-fixing" anything an audit
   flags — several past findings are deliberate design choices with documented rationale.
4. **Identification litmus** (ADR-047): only the reward-feedback block may vary across arms; any
   proposal feeding the agent a new state/reward input is identification-breaking creep → reject.
5. **Freeze discipline:** pre-freeze, ambitious changes are legitimate; post-freeze, only dated
   amendments. The freeze gate is currently 12 checks and must stay green at every commit.

---

## §1 Verified current state (2026-07-02, evening)

* **Correctness: audit-clean.** 8-front literature-validated audit + 4 fixer waves: no
  critical/high code defect; statistics literature-exact; sandbox default-deny sound; pipeline
  leakage-free (ADR-049; CHANGELOG [2026-07-02]). Freeze gate 12/12 OK, hash `843b84c3…`,
  `frozen: false` (correct — pre-freeze).
* **The deliverable pipeline EXISTS** (new today): `scripts/build_paper.py` → pandoc 3.10 +
  Tectonic 0.16.9 (pinned, portable, `tools/`) → `paper/_build/dissertation.pdf` compiles with
  **0 warnings**, 118 citation groups resolved through the Harvard CSL, References section, and
  the new non-specialist Glossary. First compile surfaced and fixed: 18 missed citation forms +
  the C:-drive-full crisis.
* **Word budget QUANTIFIED** (new today): `scripts/word_budget.py` → main body = **16,815 (re-measured 2026-07-06; was 15,532) words
  vs the 10,000 hard limit** (theory 3,433 · CH4 2,967 · CH7 2,603 · CH1 2,124 · CH2 1,873 ·
  CH5 1,342 · CH6 1,190-and-will-grow). ~6k words must move to appendices/math — a scheduled
  workstream (P7), not a final-week scramble.
* **External timestamp machinery built** (new today): `scripts/make_prereg_bundle.py` emits the
  OSF-deposit zip of the exact hash-bound file set (dry-run verified: `prereg_bundle_843b84c3.zip`).
* **Run-day ops: 3 run-killers found; fixes in flight.** The ops audit (2026-07-02) found: C1
  tenacity absent → **every API call single-attempt** (tenacity 9.1.4 NOW INSTALLED + verified;
  pin + preflight probe landing); C2 Windows Update live-unmitigated + no reboot re-entry; C3
  exit-0 husk-runs (no all-arms-tested gate; partial candidate pools can freeze winners). Plus
  M4-M9/m10-m17 (serial-resume not threaded; blind test-leg telemetry; dormant thermal governor;
  supervisor gaps; preflight can't see the .env key; disk floor too low). Ops-fixer running.
* **Disk:** C: was at **0 bytes free**; recovered to ~6 GB by purging caches. Still thin —
  **[U] free ≥ 20 GB on C:** before the campaign (pagefile + Windows Update live there).
* **In flight:** reward-program taxonomy tooling (validated on the 252-program prototype
  archive) + the ops fixes — both land under my independent verification.
* **Decided-not-yet-executed** (ADR-043/044/045/046/047): the coordinated data rebuild, Split C,
  B\*≈200k (provisional, re-derive on the new panel), FTSE-100 lite, Qwen3-Coder second LLM.

---

## §2 Phases, gates, verification

### P0 — Finish the hardening wave (NOW; parallel) [C]
* Land + independently verify: taxonomy tooling; ops fixes (C1-residual…M9, minors); then
  re-run: touched suites, ruff, `freeze.py --check`, `build_paper.py` (0 warnings), word_budget.
* Ledger: CHANGELOG entry + ADR-050 (ops hardening + deliverable pipeline) + cursor + memory.
* **Exit criterion:** all suites green; freeze gate green; PDF compiles; ops register CRITICALs closed.

### P1 — The coordinated data rebuild [U→C] — **GATE: Tamer's GO + settled-2026 cutoff date**
* One pull (PowerShell + `.venv-lseg`, NEVER Bash — ADR-048): forward-2026 settled returns +
  delisting-terminal corrections + pre-lagged bid-ask + BAB/QMJ factors → **new panel suffix**.
* Verify: `scripts/verify_gold.py` byte-diff vs univ3 (only intended cells changed);
  `data_pipeline` validation; record the new suffix's `expected_windows` in
  `config/inference.yaml`; extend the checksum manifest; `gold.suffix` flip.
* Split C lands with the rebuild (train 2005-16 / val 17-19 / test 20-25→cutoff): the 12-file
  execution-time punchlist moves TOGETHER (configs + prereg + paper §§), then full suite +
  freeze-check + a byte-diff review.
* **Exit criterion:** new panel validated; windows recorded; whole suite green; docs reconciled.
* Estimated effort: pull ~30 min–2 h; validation + punchlist ~half a day.

### P2 — Pilots on the NEW panel (GPU) [C, U watches cost/time]
* B\* convergence ladder (`scripts/learning_curve.py`, ≥3 seeds, budgets to 350k+; the 50k
  buffer cap mirrored) → `recommend_budget` must return `converged=True`; ADR + amendment set
  `train_steps_per_candidate` in BOTH campaign.yaml and algos.yaml (the new preflight
  budget-mirror guard enforces the pair).
* σ_D pilot (`sigma_seed_pilot`) → seeds stay 30 or rise to 50 (σ_D>0.10 rule, ADR-043).
* `determine_design.py` must then report **FREEZE-READY** (λ is FIX-class since 2026-07-02).
* **Exit criterion:** B\* + seeds set by dated amendment; determine_design green.

### P3 — The numeracy/legible-format sub-experiment [U→C] — **GATE: budget (~150 Opus calls ≈ $10–30; campaign LLM spend later ≈ $30–80, scaled from the $3.17 Sonnet prototype at Opus pricing)**
* Already BUILT (`scripts/run_subexperiment.py`, GAP-B seams). Run BEFORE the campaign: its
  result shapes the numeracy-bottleneck framing (the headline mechanism) while staying
  report-only/disjoint. Analysis legs flip `no_data→ok` automatically.

### P4 — FREEZE [U executes; C prepares]
* Pre-freeze checklist: P0-P3 exit criteria met; `docs/CAMPAIGN_freeze_decisions.md` reconciled;
  word-budget run recorded; full suite + ruff green; `freeze.py --check` 12/12.
* **[U] run `scripts/freeze.py`** (write path) → hash recorded, `frozen: true`.
* Immediately: `scripts/make_prereg_bundle.py` → **[U] deposit on OSF** (account needed) +
  push the `prereg-v1.0` git tag / dated GitHub release → record DOI/URL in `DECISIONS.md` →
  cite in CH4 §4.8 ("pre-registered and frozen on <date>; OSF <link>; SHA-256 <hash>").

### P5 — The confirmatory campaign (~2-3 weeks, unattended) [U launches; C monitors/verifies]
* **Run-day §0 checklist** (being written into the runbook by the ops-fixer): pause Windows
  Updates 5 weeks; verify Turbo ~140 W after every reboot; lid-close = Do Nothing on AC;
  Defender still off (or exclusions); ≥20 GB free on C: (`preflight --min-disk-gb 20`);
  register the ONSTART supervisor task + the external deadman ping; preflight ALL-GREEN
  (now incl. tenacity, pending-reboot, budget-mirror, live key probe).
* Launch command A (serial reflect-on-last, ratified) under the supervisor with `--resume`.
* Monitoring: watcher (now loop-tolerant) + ntfy + deadman; mid-run checks at day 2/7/14.
* Qwen3-Coder leg (ADR-046) runs after/alongside per budget; reduced scope acceptable.
* **Exit criterion:** all 7 arms tested (the new all-arms gate exits non-zero otherwise);
  archives complete; provenance stamped.

### P6 — Analysis + robustness riders [C]
* `analyze_campaign.py` full stack (m=6 + every report-only block incl. the taxonomy, mechanism
  kernel, ES/Bayes/MCS, mechanism-multiplicity) → verification subagent pass over the outputs.
* Riders: buffer-robustness re-run (one arm, larger buffer — bounds the 50k-cap effect);
  FTSE-100 lite replication (ADR-047); attribution sanity (R26).
* **Figure-standards pass** (publication grade: font sizes, colorblind-safe palettes, consistent
  style across the 9+ headline figures) + an **integration rehearsal**: analyze → figures →
  numbers-into-CH6 → `build_paper.py` run once end-to-end on the first completed arm's data
  before the full campaign finishes, so the P6→P7 seam breaks early if it breaks.
* **Exit criterion:** headline verdicts + all report-only blocks rendered; independent check done.

### P7 — Write-up to the ceiling [C drafts; U reviews] — *starts NOW for non-results chapters*
* **The word surgery IS the depth pass** (amended 2026-07-02): cutting 15,532 → ≤9,500 rewrites
  ~40% of the body — executed with Okhrati's compass applied paragraph-by-paragraph (does this
  paragraph carry intuition, mechanism, or honesty the grade needs? else appendix or cut), so
  compliance and the communication upgrade are ONE workstream, not two. Per-chapter targets:
  CH3 → ~1,900 (formal apparatus into display math + a proofs appendix); CH4 → ~2,300
  (robustness detail → appendix); CH5 → ~550 (fold highlights into CH4/CH6); CH7 → ~2,000;
  CH1 → ~1,800; CH2 → ~1,500; leaves ~1,400+ headroom for CH6 growth. Tracked by
  `word_budget.py` on every edit.
* **CH1 mechanism-led opening = the next focused block** (the highest-leverage 300 words in the
  project; anchors every downstream prose decision — do FIRST, not in August).
* **EDA/Data argument (Okhrati's motivate-with-data, his explicit ask):** F3 stylised-facts
  figure BUILT from the real panel (launched 2026-07-02; re-render post-rebuild is one command)
  + a figure-led ~600-word Data section arranged as an argument — the tail facts a scalar
  cannot convey → the hypothesis falls out. Replaces weaker CH4 §4.2 prose (net word-negative).
* Data/EDA promotion (Okhrati's motivate-with-data), CH1 mechanism-led opening, de-pre-disclose
  pass, figures embedded + cross-referenced (manifest), compute wall-clock + energy line,
  CH6 results + CH7 verdict slots + Abstract result sentence, ToC manual-vs-auto reconcile,
  word-count statement filled from the tool.
* **Examiner red-team on the compiled PDF** (fresh agents, post-CH6): probabilist pass +
  non-specialist second-marker pass + citation re-verify (`/verifying-citations` + 0 pandoc
  warnings).
* **[U] Okhrati sign-off** on the pivot disclosure; ethics/data-protection forms per handbook.

### P8 — Submission (target ≥1 week before the 1 Sep deadline) [U]
* Final `build_paper.py` (0 warnings) → final word-budget PASS → submission pack checklist
  (declaration, AI-disclosure, forms) → submit ~Aug 24-29.

---

## §3 Timeline vs 1 Sep (with slack)

| Window | Work | Slack notes |
|---|---|---|
| Jul 2-5 | P0 hardening close-out + ledger; **[U] disk cleanup**; **[U] rebuild GO** | — |
| Jul 5-7 | P1 rebuild + Split C + reconcile | pull is hours, not weeks (ADR-048) |
| Jul 7-11 | P2 pilots (GPU-days) | ladder extension = +2-3 days worst case |
| Jul 9-13 | P3 sub-experiment (budget-gated) + P7 early chapters | parallel with P2 |
| Jul 13-15 | P4 freeze + OSF deposit | — |
| Jul 15 – Aug 5 | P5 campaign (21 days worst case) | overrun contingency: Qwen leg reduced |
| Aug 5-12 | P6 analysis + riders | — |
| Aug 5-22 | P7 write-up intensive (CH6/CH7/budget workstream/red-team) | overlaps P6 |
| Aug 24-29 | P8 submit | **≥1 week hard buffer** |

Total slack ≈ 1.5-2 weeks. Contingency triggers: σ_D>0.10 → 50 seeds (+~40% test-leg time →
start campaign ≤ Jul 17); campaign crash-days → supervisor resumes (idempotent); API outage →
resume; C: fills → preflight refuses (fix space first).

## §4 Risk register (top; full ops detail in the 2026-07-02 audit + runbook)

| Risk | Sev | Owner | Mitigation (status) |
|---|---|---|---|
| API single-attempt calls (C1) | CRIT | C | tenacity installed+verified; pin+probe landing (P0) |
| Windows Update mid-run restart (C2) | CRIT | C+U | probes + pause + ONSTART re-entry landing (P0/P5) |
| Exit-0 husk run / partial-pool winner (C3) | CRIT | C | all-arms gate + selection floor landing (P0) |
| C: disk (pagefile+WU live there) | ~~HIGH~~ CLOSED | U | **20.5 GB freed + verified 2026-07-02**; preflight --min-disk-gb 20 stays as the guard |
| Word budget 15,532/10,000 | HIGH | C | P7 workstream, tool-tracked per edit |
| σ_D large → power short | MED | C | 50-seed rule pre-committed (ADR-043) |
| Blind test-leg telemetry (M5) | MED | C | watcher loop + deadman landing; runbook |
| Sub-experiment unrun before campaign | MED | **U** | budget GO (~tens of $) |
| Okhrati sign-off outstanding | MED | **U** | ask early (P7) |
| Examiner red-team surprises | LOW | C | scheduled on the compiled PDF (P7) |

## §5 Tamer's gates (everything only YOU can do, in order)

1. ~~**Free ≥ 20 GB on C:**~~ **DONE 2026-07-02** (verified: 20.5 GB free).
2. **Rebuild GO + the settled-2026 cutoff date** (or I default to the latest settled trading day).
3. **Sub-experiment budget GO** (~150 Opus calls).
4. **Run `scripts/freeze.py`** at P4 + **create the OSF account/deposit** (10 min).
5. **Campaign launch day** (run-day checklist together) + keep the laptop on AC/network.
6. **Okhrati sign-off** on the pivot disclosure; ethics forms.
> **P7 target arithmetic corrected (2026-07-06 review):** the previous per-chapter targets (1,800+1,500+1,900+2,300+550+2,000 = 10,050) exceeded the 10,000 hard limit BEFORE any CH6 word. Corrected budget: non-CH6 chapters must sum to <= ~8,100 (the 9,500 PASS ceiling minus a realistic ~1,400-word CH6) — i.e. ~1,950 additional words of cuts beyond the old plan, allocated at write-time.
