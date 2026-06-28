# DEVIATIONS — post-freeze deviation log

This file is an **append-only** record of every departure from the frozen pre-registration
(`PREREGISTRATION.md`) made **after** the Phase-1 freeze.

`PREREGISTRATION.md` is FROZEN after Phase 1 (CLAUDE.md prime directive 3): the hypotheses,
candidate budget, seeds, fitness, the frozen tail-diagnostic set, splits, embargo, benchmark suite,
and analysis plan cannot be silently edited. Where the executed work must diverge from the frozen
plan — whether a forced change, a discovered defect, or an approved amendment — the deviation is
logged **here** rather than by rewriting the pre-registration, so the frozen document stays a true
record of what was committed to in advance and this log stays a true record of what actually
happened and why.

Rules:
- **Append only.** Never edit or delete an existing row; correct a row by appending a new one that
  supersedes it (reference the original date).
- **One row per deviation.** Record the date (UTC, `YYYY-MM-DD`), the pre-registration section
  affected, what changed, the rationale, and whether the user explicitly approved it (a change to a
  frozen decision requires sign-off — CLAUDE.md directive 3 / stop-and-ask trigger).
- An empty table below means **no post-freeze deviations have been recorded yet** (the executed work
  matches the frozen pre-registration).

| Date (UTC) | Prereg section | Deviation | Rationale | Approved by |
| ---------- | -------------- | --------- | --------- | ----------- |
