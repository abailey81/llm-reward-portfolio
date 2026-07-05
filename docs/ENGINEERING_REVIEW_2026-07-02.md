# Design & Engineering Review — 2026-07-02 (the standalone assessment the user asked for)

> Scope: every engineering and design layer of the project, graded honestly, with the upgrade list —
> executed items marked. Companion to the two adversarial CODE-review workflows (fresh-code
> wf_f0d8597f-6f5 · full-surface wf_f786dab7-d31 — resumable with cache; they verify line-level
> correctness; THIS doc assesses architecture and closes structural gaps).

## A. Layer-by-layer assessment

| Layer | State | Grade | Gaps found → action |
|---|---|---|---|
| **Experiment engine** | config-single-source, seeded determinism end-to-end, archive-replay contract, anonymised env, AST-gated untrusted rewards | Strong | config-cache staleness over week-long runs → review dim `io-utils` |
| **Resilience stack** | supervisor (bounded restarts+backoff) · ONSTART re-entry (**fixed 07-02: stale parallel args → serial headline; clock-lock re-apply added**) · guardian thermal/RAM governor · preflight gauntlet incl. live API probe · deadman ping · THREE resume caches (serial/parallel/farm — the farm cache had its first REAL fire 07-02 and skipped exactly the archived cells) · atomic `os.replace` writes · EXIT_INCOMPLETE gate + selection floor · budget-mirror guard · freeze gate 13 checks | Exceptional | (1) **launch-gate-only resource policing** — nothing polices RAM/VRAM DURING a run (the 07-02 incident): → EXCLUSIVE-PHASE RULE codified in runbook §0b; campaign watcher gains a RAM/VRAM alert line (post-σ_D, touches monitor.py). (2) **Archive redundancy: NONE until today** → `scripts/mirror_archive.ps1` (below) |
| **Data engineering** | vault write-once + manifest/lineage/checksums + PIT membership replay + splice/overlap gates + purge tooling + POSIX-relpath fix | Exemplary (twice audited) | full-surface review dim `data-pipeline-full` stress-tests the replay edge cases |
| **Statistical engineering** | IUT/TOST/severity/BF01/MCS/PBO/FZ0 stack; honest `executed:False` degradation pattern; report-only DISJOINT discipline | Strong | conventions (signs/one-sided/annualisation) under adversarial review in dim `inference-stack` |
| **LLM engineering** | provider-neutral transport (+OpenRouter/Qwen 07-02) · provenance records (+`served_model` anchor) · tenacity retry · resume caches · budget accounting · sandbox AST gate + SAFE_DEFAULT accounting | Strong | Qwen cost-table entries (campaign window); sandbox under review dim `sandbox-security` |
| **Observability** | monitor.py progress + `--follow-campaign` · read-only watcher (stall/error/token-$/ntfy) · deadman (host-death) · onstart/mirror logs | Strong | RAM/VRAM alert line (above) |
| **Repro engineering** | capture_env · audit_reproducibility (7P/1W/0F) · pinned pandoc/Tectonic · prereg bundle · model card · datasheet · CITATION.cff · `.python-version` | Strong | capture_env must record the GPU DRIVER version (556.12 now pinned-relevant) → review dim `operational-scripts` verifies |
| **Test engineering** | ~1,500 behaviour tests; hermetic pipeline tests; regression-pinned fixes | Strong | test-suite QUALITY audit (tautology hunt) = review dim `test-quality` |

## B. Design assessment (the experiment itself)
Completed 2026-07-02 across the novelty campaign: the design carries the 7-arm content manipulation,
the P3 encoding ablation (→ the content×encoding factorial), FOUR newly registered instruments
(information-utilization gap · validation-headroom bound · the 4-account × 6-instrument MECHANISM
FINGERPRINT · the reflection FUNNEL), the SQ3b two-accounts adjudication, the distance moderator, and
the severity presentation — all ex-ante, all report-only-disjoint, all inside the identification
principle. Verdict: the design's additive space is CLOSED (the 07-02 stopping analysis: every axis
closed by decision, principle, or data-exhaustion); design depth now converts to grade only through
execution (freeze speed, write-up foregrounding, ONE-named-audit presentation, P3 run quality).

## C. Upgrades executed 2026-07-02 (this review's output)
1. **ONSTART task fixed** — two real defects: default args commanded the SUPERSEDED parallel protocol
   (a reboot would have resumed the campaign on the WRONG protocol); no clock-lock re-application
   (a reboot would have resumed at degraded, non-uniform speed). Both fixed in
   `scripts/install_onstart_task.ps1` (+ SupervisorGpu default 2→3).
2. **`scripts/mirror_archive.ps1` NEW** — robocopy /MIR of the irreplaceable set (campaign + pilot
   archives, tables, manifest ledgers) to the second physical drive; bounded retries; logged passes;
   6-hourly scheduled-task one-liner documented. First pass runs after the σ_D farm exits; the
   campaign runs it on schedule. Closes the single-disk catastrophic-loss exposure.
3. **EXCLUSIVE-PHASE RULE** — runbook §0b: no agent fleets / test suites / torch side-processes during
   any farmed leg (the 07-02 incident's law).
4. Queued precisely (post-σ_D, exclusive rule): resume both review workflows (cached) → fix confirmed
   findings; verify/finish the instruments build (information_gap.py + headroom.py partials);
   power_analysis hang investigation (three runs hung for hours — found 07-02) + doc regen; the
   monitor RAM-alert line; P3.
