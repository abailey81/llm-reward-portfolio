# LAUNCH READINESS — 2026-07-27 (overnight review lane; Tamer asleep)

**Read this first.** Tamer's instruction: *"close absolutely all gaps, and make us 100% ready for a
campaign run."* This states exactly what is verified, what is still running, and what only he can
close. Every claim below was OBSERVED by running the thing; nothing is inferred.

---

## 1. VERDICT

**The engineering is ready. The campaign is not launchable yet, and every remaining blocker is a
decision or an operator action — none is a code defect.**

| | |
|---|---|
| Code / tests | **READY** |
| Data + backups | **READY** |
| Cluster wiring | **READY** |
| Crash-resume | **CERTIFIED** |
| Live authoring path | **VERIFIED** |
| **The freeze** | **TAMER — GO step 1 (R94). No lane may do this.** |
| **Two leg-gate flags** | **TAMER — they route to him by design** |
| **VPN / SSH / admin items** | **TAMER — runbook items 5–8** |

---

## 2. WHAT WAS VERIFIED (all observed, with the command that produced it)

### Code
- **Full suite: 2,726 passed · 3 skipped · 0 failed · `PYTEST_RC=0`** — unpiped, RC written INTO the
  log, **pinned `--randomly-seed=20260727`** so the certification is itself reproducible (this closes
  the long-standing #68 caveat that the previous green was shuffle-seed dependent).
- `ruff src scripts tests` **RC=0** · `check_citations.py` **RC=0** · `build_paper.py` **RC=0**
  (8 chapters + 1 appendix; word-budget tests pass).
- `freeze.py --check` **RC=0, 23/23, `freeze_hash: null`** — correctly STILL UNFROZEN.

### The launch gate itself
- `pretrain_validate.py --self-test` → **9/9 checks PROVEN FALSIFIABLE** (each handed a known-bad
  input and required to FAIL). A green gate nobody has watched go red certifies nothing.
- `first_seed_sanity.py` → proven falsifiable: **RC=2 `GARBAGE: wall_clock is 0.0`** on the dry-run
  archive, honest `no_records` on a non-campaign layout.

### Cluster
- `run_campaign_cluster.py --dry-run` on the **FULL 9-arm frozen roster**: **RC=0** — 568 seeds,
  5 candidates/gen, windows `((60,3021),(3081,3775),(3835,5406))`. **The R18 purge is exactly 60
  sessions at BOTH split boundaries.**
- The runbook's own keyless **`--synthetic`** dry-run (7-arm list): **RC=0**.
- **The rendered jobscript was READ, not counted:** `#$ -p 0` (full fair-share standing), `-notify`,
  `-r y`, absolute `-wd`/`-o`, the `mkdir -p` that fixed the 2026-07-24 rc=255-every-dispatch crash,
  TMPDIR gold staging with an ACFS fallback, and the `PYTHONPATH` export that fixed the per-task
  `ModuleNotFoundError`. The renderer also **refuses** a `$HOME`-relative `remote_root` with the exact
  SGE reason — verified by triggering it.

### Crash-resume — the guarantee a 23-day run rests on
- `crash_rehearsal.py` **PASS/RC=0**: the CONTROL run is **identical to the REFERENCE**, so this
  environment is verified deterministic; a run hard-killed at 1 record resumes to an archive whose
  **science fields are byte-identical** to an uninterrupted run.
- The runbook calls the multi-point kill-storm "optional belt-and-braces". It was run anyway:
  **kill at 2, 3 and 5 records — ALL PASS.** Resume from ANY point reproduces the archive.

### Live authoring
- `author_smoke.py` **RC=0** — `provider=anthropic model=claude-opus-5`, key valid, 2.6 s. The
  confirmatory seat is live.

### Data (after the 01:56 deletion incident)
- **SHA-256: 1,170 / 1,170 verified, 0 missing, 0 corrupt** against a manifest FIRST confirmed
  byte-identical to git HEAD (so it predates the deletion and cannot be a self-fulfilling check).
- Coverage is complete: the 1,182 "uncovered" files are exactly 1,170 `.provenance.json` sidecars
  (1:1), 4 `.gitkeep`, 6 manifest files. **Zero real data files unverified.**
- `verify_inventory` RC=0 · `archive_integrity` sealed roots matched (`prototype` 239 records,
  `sigma_pilot` 30) · `verify_gold` PASS · `outputs/` **0-diff vs HEAD**.
- **SEMANTIC** confirmation, not just bytes: the F3 stylised facts reproduce **exactly** through
  `src/viz/eda.py::stylised_fact_stats` — skew **+0.2096**, excess kurtosis **15.2486**, −5σ ratio
  **10,392.9**.
- **Fresh verified backup:** `D:\llm_rp_backup_2026-07-27\` — 3,858 files, 1.14 GB, `robocopy /XJ`,
  **sha256-verified 1,170/1,170**.
- **No launch dependency on the lost files:** `frozen_root` is `output_dir/"frozen"`, CREATED by the
  run, not read from a prior archive. The 482 unrecovered files are historical run artifacts.

### Power (the seed-count justification)
- Re-run at the **MEASURED** pilot inputs (σ_seed 0.244, ρ −0.140 — not the 0.360 proxy):
  **MDE @ 80 % = 0.0473 Sharpe = 0.031 validation-DSR ≤ SESOI 0.050.** The design IS adequately
  powered at n = 568 and the pre-registered INCONCLUSIVE branch does not fire.

---

## 3. STILL RUNNING AT THE TIME OF WRITING

| Job | Purpose | What to do when it lands |
|---|---|---|
| `leg_gates.py --all` | restores the 2 SKIPped gate checks + regenerates the destroyed per-model authoring evidence | re-run `pretrain_validate.py` and expect **0 SKIPs** |
| full suite with `-rs` | runbook item 2 requires the skip report be **READ**, not just counted | confirm the 3 skips are the permanent platform ones |
| `power_analysis.py` full regeneration | final ρ sweep into `docs/CAMPAIGN_power.md` | commit the regenerated doc |

---

## 4. WHAT ONLY TAMER CAN CLOSE

1. **THE FREEZE.** R94: it executes as GO step 1 *together with* full-campaign approval. No lane may
   do it, and this one never has (`freeze_hash: null` throughout).
2. **Two leg-gate flags — they route to him BY DESIGN** ("the gate never silently drops a leg"):
   - `deepseek-v4-pro` — compliance **0.90**, below the 1.0 strictness floor → `LOW→review`; screen
     `review+UNVERIFIED` (2 probes unusable on length).
   - `qwen3.6-27b` — screen **`FLAG→review` (canary)**, i.e. a confabulation flag.
   - (`glm-5.2` clean: compliance 1.0, screen pass.)
3. **#96 — the queue-priority conflict.** `--priority` accepts any int with no guard while this
   script's own help instructs `-200`/`-300` per runbook §14.3, against the ABSOLUTE rule never to
   lower our priority. **The default resolves to 0 and the jobscript renders `-p 0`, so the
   confirmatory launch is SAFE AS CONFIGURED.** A loud runtime warning now fires on any negative
   value. The runbook-vs-rule contradiction is his to arbitrate.
4. **The two TREATMENT-surface changes** from loop 117 (`_HEADER` `.2f`→`.6f`, `_fmt` `.3f`→`.4f`) —
   accept or revert.
5. **Runbook items 5–8** (VPN/SSH remote state, disable sleep, pause Windows Update, cluster calendar).
   ⚠ Calendar note: **Myriad maintenance = 2nd Tuesday (Aug 11)**, and from a ~Jul-27 GO the tier-403
   rung lands ~Aug 8–11, straddling it. Jobs requeue idempotently by design; plan for it.

---

## 5. OPERATIONAL NOTE EARNED TONIGHT

`preflight.py` currently says **NO-GO**, and all three reasons are correctly NOT code defects:
`ram`/`commit` failed on a snapshot taken while this session ran five heavy python jobs with four
concurrent agent sessions resident (commit-free 3.31 GB; ArmouryCrate, the known leaker, was not even
in the top 12) — transient and self-inflicted; `freeze` failed because `frozen: false`, which is GO
step 1. Confirmed by reading the call graph that **`preflight.py` is NOT invoked by
`run_campaign_cluster.py`**, so laptop RAM cannot block a Myriad launch.

**Run the final gates on a QUIET box.** This is the #75 lesson: spawn starvation made that gate return
RC=1 for 21 consecutive loops and RC=0 on a quiet box with its bytes unchanged. A gate run under load
measures the load, not the code.
