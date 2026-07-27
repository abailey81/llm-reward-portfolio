# LANE COORDINATION — 2026-07-27 overnight (READ BEFORE EDITING SHARED FILES)

Tamer is asleep and asked the REVIEW lane to *"coordinate with other claude code session, close
absolutely all gaps, and make us 100% ready for a campaign run"*. This file exists so two concurrent
sessions do not collide, after the 01:56 junction incident showed how expensive a collision is.

## Who is doing what

**REVIEW lane (this one)** — deep code review loops 117–119 + the launch-readiness pass.
Currently HOLDS and is actively editing:

| File / path | Why | Release |
|---|---|---|
| `docs/CAMPAIGN_power.md` | full-fidelity regeneration running (`power_analysis.py`, ~20 min sweeps) | on commit |
| `outputs/leg_gates/**` | `leg_gates.py --all` re-running the 10 legs to restore the 2 SKIPped gate checks | on completion |
| `outputs/spend_ledger.jsonl` | recreated by that run (the original was destroyed) | on completion |
| `CHANGELOG.md` `docs/HANDOFF.md` | session record | frequent small commits |
| `paper/CH6_results.md` `paper/CH7_*.md` `paper/APPENDIX_B_limitations.md` `paper/FIGURE_TABLE_MANIFEST.md` `PREREGISTRATION.md` | H1 → node-N6 reconciliation (**committed `7c9d26f`**) | RELEASED |
| `src/env/runner.py` `scripts/power_analysis.py` | #93/#94/#95 (**committed**) | RELEASED |

**NOT touched by this lane, deliberately:** `scripts/certify_commit.py`,
`tests/test_certify_worktree_safety.py`, `src/cluster/*`, `scripts/sentinel.py`,
`scripts/jobscript.py`, `src/cluster/killswitch.py` — the RECOVERY/CAPACITY lane's territory.

## Standing rules re-earned tonight (violating these is a defect)

1. **NEVER `git clean -xfd`.** Dry-run measured **1,264 paths** removed incl.
   `data/gold/returns_panel_univ5.parquet` and all 1,085 `data/raw` files — those dirs are gitignored,
   so `-x` sweeps exactly the licensed data. Use `git clean -fd` and dry-run with `-n` first.
2. **`git add -u` mass-stages DELETIONS** just as `-A` sweeps untracked files. Tonight it staged
   **836 files / −403,794 lines** including the whole prototype archive. ALWAYS read
   `git diff --cached --numstat` before committing a bulk stage.
3. **Never snapshot another lane's live buffer.** Check mtime; anything modified in the last few
   minutes belongs to someone.
4. **Heredocs never carry backslash/escape content** — use Write/Edit. This bit the review lane
   tonight (a `\n` became a real newline and broke `power_analysis.py`).
5. **THE FREEZE IS TAMER'S ALONE** (R94, GO step 1, with full-campaign approval). No lane freezes.

## Backups

- `D:\llm_rp_backup_2026-07-27\` — **fresh**, 3,858 files, 1.14 GB, `robocopy /XJ`,
  **sha256-verified 1,170/1,170 against the frozen manifest**. Re-take after any data change.
- `D:\llm_rp_predefender_backup\` — 2026-07-01, stale/partial; it is what saved the incident.

## Verified state at the time of writing (all OBSERVED, none assumed)

`data/` + `outputs/` integrity proven **five independent ways** (sha256 1,170/1,170 vs a manifest first
confirmed byte-identical to HEAD · `verify_inventory` RC=0 · `archive_integrity` sealed roots:
`prototype` 239 records / `sigma_pilot` 30 · `verify_gold` PASS · `outputs/` 0-diff vs HEAD), plus
SEMANTIC confirmation — the F3 stylised facts reproduce exactly (skew +0.2096, excess kurtosis 15.2486,
−5σ ratio 10,392.9) through `src/viz/eda.py::stylised_fact_stats`.

`freeze.py --check` **RC=0, 23/23, `freeze_hash: null` (STILL UNFROZEN)** · `ruff` RC=0 ·
`check_citations` RC=0 · `build_paper` RC=0 (8 chapters + 1 appendix) · word-budget tests pass ·
**cluster dry-run RC=0 with the FULL 9-arm frozen roster** (568 seeds, windows
`((60,3021),(3081,3775),(3835,5406))` — the R18 purge is exactly 60 sessions at BOTH boundaries).
