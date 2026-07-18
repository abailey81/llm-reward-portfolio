# FREEZE RUNBOOK — pre-registration freeze (forward-going; corrected post-merge)

The act of freezing the design. After it, PREREGISTRATION.md is FROZEN (CLAUDE.md R3 / R1): any later change
is a **deviation** requiring a dated ADR + supervisor notification + dissertation disclosure.

> **What changed vs the old B-line runbook (now archived).** The superseded
> `archive/pre_merge_repo_B/staging/FREEZE_RUNBOOK.md` froze a *staged copy*
> (`docs/staging/PREREGISTRATION_v1.0_FINAL.md`) by `cp`-ing it over the root file — which would have
> **clobbered the canonical root `PREREGISTRATION.md`** with the abandoned IQN draft (ADR-022). This runbook
> freezes the **canonical root `PREREGISTRATION.md` in place** (no `cp`, no staged overwrite) and calls the
> real Makefile target **`make freeze`** (the old runbook called `make freeze-design`, which the root
> `Makefile` does not define).

## Step 0 — DECISIONS REQUIRED before freezing (resolve any PREREG ↔ config mismatch first)

Before freezing, confirm `PREREGISTRATION.md` and `config/*.yaml` agree on every number that the freeze
locks (the search/compute budgets in §4 are the Deflated-Sharpe trial count). In particular:

1. **Per-algorithm hyperparameters.** If §4 cites "hyperparameters from `config/`", confirm the referenced
   file exists (`config/algos.yaml`); otherwise re-word to "library-default hyperparameters at the pinned
   package versions, echoed into every run sidecar". Do not freeze a pointer to a file that does not exist.
2. **Arm budgets.** Confirm the arm roster + per-candidate budget in §3/§4 equal the EXECUTED
   `config/campaign.yaml` (roster) + `config/campaign.yaml`/`config/algos.yaml` (`train_steps_per_candidate`
   = B* = 400,000, R77 (supersedes R74's 200,000; matches config/campaign.yaml + config/algos.yaml)). Do NOT consult `config/eureka_loop.yaml` — it is documentary only ("NOT loaded by
   the live run"; it still carries the legacy 240 budget). The freeze gate now binds all three cross-file:
   `assert_executed_arms_match` (roster), `assert_train_steps_match` (B*, batch-6 M1), and the
   preflight budget-/model-mirror checks — so a drift here fails `make freeze-check` rather than freezing.
3. **Compute venue.** Confirm §12 / compute references match the CURRENT decision (2026-07-13, ADR-053): the
   confirmatory campaign runs on the **UCL Myriad HPC cluster** (SGE arrays; `scripts/run_campaign_cluster.py`),
   with the owned RTX 4050 laptop as the **certified fallback** (Turbo + n_gpu=3 + buffer capped 50k; full
   cross-substrate science parity). Both the older "rented RTX 4090" framing (ADR-023) and the 2026-06-30
   "LAPTOP-ONLY" decision are **superseded** by ADR-053.

Edit `PREREGISTRATION.md` (and config, if a number moves) directly to resolve any mismatch — there is no
staging copy to apply.

## Steps (run in order, from the repo root)

```bash
# 1. Resolve any Step-0 mismatch by editing PREREGISTRATION.md (and config/*.yaml if a number moves).

# 2. Review exactly what will freeze.
git diff PREREGISTRATION.md config/

# 3. Gate (tests must be green before the freeze commit).
make test

# 4. The freeze commit (THE act — after this, deviations require an ADR).
git add PREREGISTRATION.md config/      # include config only if Step-0 touched it
git commit -m "Freeze pre-registration v1.0"

# 5. Capture the freeze hash.
make freeze                              # prints the freeze hash + date (scripts/freeze.py)
#    NOTE: `make freeze` (scripts/freeze.py) ALSO auto-appends a dated "FREEZE-DONE — content hash" entry
#    to docs/DECISION_LOG.md (the ADR-005 audit slot) — so the machine record is written for you.

# 6. Record it in DECISIONS.md (the root, forward-authoritative log) — open the freeze ADR, replace the
#    placeholder line with the printed "Freeze hash: …" line, and change its heading from (PENDING…) to
#    (FROZEN <date>). This is the HUMAN-curated ADR; docs/DECISION_LOG.md (step 5) is the auto-appended
#    audit trail — they are two DIFFERENT files, both intended (do not try to merge them).

# 7. Commit the record.
git add DECISIONS.md docs/DECISION_LOG.md && git commit -m "Record pre-registration freeze hash"

# 8. Notify the supervisor (paste into the meeting email / message):
#    "Design pre-registration frozen today (commit <hash>); hypotheses, budgets, splits and inference
#     rules are now locked — any later change will reach you as a flagged deviation."
```

**Abort rule:** if anything in the `git diff` at step 2 surprises you, stop — `PREREGISTRATION.md` is still
the canonical file at that point and nothing is locked until the commit at step 4.
