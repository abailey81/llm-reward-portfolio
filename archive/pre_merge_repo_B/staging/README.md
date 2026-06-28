# `archive/pre_merge_repo_B/staging/` — superseded pre-merge B-line freeze staging

This folder is the **pre-merge B-line pre-registration staging area**, preserved for provenance (ADR-022,
no-loss rule) and **no longer live**. It was moved here wholesale from `docs/staging/` because it is a
**freeze hazard** against the post-merge canonical design:

- **`PREREGISTRATION_v1.0_FINAL.md`** — a pre-merge B-line *draft* pre-registration whose §1 RQ and §4
  algorithms row still assert the **IQN / IQN-SAC** line that the audit **rejected** in favour of the live
  off-critic **empirical+EVT** measurement (`src/feedback/measurement.py`) + SB3 **SAC + TQC** agents
  (ADR-022). It is **NOT** the canonical pre-registration. The canonical, A-line pre-registration is the
  repo-root **`PREREGISTRATION.md`** — that file is the single source of truth and must never be overwritten
  by this draft.
- **`FREEZE_RUNBOOK.md`** — the B-line freeze procedure that staged the file above. Its step 2 instructed
  `cp docs/staging/PREREGISTRATION_v1.0_FINAL.md PREREGISTRATION.md`, which at freeze would have
  **clobbered the canonical root `PREREGISTRATION.md`** with the superseded IQN draft. It also called a
  `make freeze-design` target that the root `Makefile` does not define (the real target is `make freeze`).

**Going forward**, the corrected, forward-going freeze procedure lives at **`docs/FREEZE_RUNBOOK.md`**: it
operates on the canonical root `PREREGISTRATION.md` in place (no `cp` overwrite) and calls the real `make
freeze` target. Use that one, not these.

See `DECISIONS.md` ADR-022 (repository unification; A's audited science is canonical, B's pre-audit science
preserved here) and the `../README.md` successor map.
