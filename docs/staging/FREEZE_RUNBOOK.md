# FREEZE RUNBOOK — T4, Friday 12 June 2026 (your act; nothing here has been executed)

The staged document `docs/staging/PREREGISTRATION_v1.0_FINAL.md` is the current draft with exactly three
changes folded in (all pre-recommended in ADR-010 / flagged below): the §3 λ tie-break sentence, the new
§4a naming the H4 reward family, and the §10 freeze-hash cell re-pointed to DECISIONS.md (it cannot be
filled inside the freeze commit itself). Everything else is byte-identical to the live draft.

## Step 0 — DECISIONS REQUIRED before applying (PREREG ↔ config inconsistencies found)

1. **Single-shot arm count — §4 arms row says "LLM single-shot (80 one-shot samples)";
   `config/eureka_loop.yaml` says 240.** 80 = one restart's worth (N×K = 5×16); the matched TOTAL budget
   across R=3 restarts is 240 (= the random-search and BayesOpt counts in the same row).
   *Recommendation:* edit the staged row to "LLM single-shot (240 one-shot samples = 80 × R=3 restarts)".
   Whatever you choose, make PREREG and config say the same number before freezing.
2. **§4 algorithms row says "fixed hyperparameters from `config/`" — no per-algorithm hyperparameter
   blocks exist in config/ yet.** Options: (a) add a `config/algos.yaml` with the pinned SB3/d3rlpy
   hyperparameters before freezing (cleanest), or (b) re-word to "library-default hyperparameters at the
   pinned package versions (ADR-002/003), echoed into every run sidecar". Pick one; do not freeze a
   pointer to a file that does not exist.
3. (Already folded into the staged file, listed for awareness:) §10 freeze-hash cell now points to
   DECISIONS.md ADR-005 as the single source of the hash.

## Steps (run in order, from the repo root)

```bash
# 1. Resolve Step-0 decisions by editing docs/staging/PREREGISTRATION_v1.0_FINAL.md (and config if 0.2a)

# 2. Apply the staged file
cp docs/staging/PREREGISTRATION_v1.0_FINAL.md PREREGISTRATION.md

# 3. Review exactly what will freeze (expect: §3 sentence, §4a block, §10 hash cell, your Step-0 edits)
git diff PREREGISTRATION.md

# 4. Gate
make test

# 5. The freeze commit (THE act — after this, R1 binds: changes are deviations)
git add PREREGISTRATION.md config/eureka_loop.yaml   # include config only if Step-0.1/0.2a touched it
git commit -m "T4: freeze pre-registration v1.0"

# 6. Capture the hash
make freeze-design     # prints: Freeze hash: <hash> (<date>)

# 7. Record it — open DECISIONS.md, ADR-005: replace the placeholder line with the printed
#    "Freeze hash: …" line and change the heading from (PENDING…) to (FROZEN 2026-06-12).
#    λ line stays pending (own ADR after the §3 calibration run).

# 8. Commit the record
git add DECISIONS.md && git commit -m "ADR-005: record pre-registration freeze hash"

# 9. Notify the supervisor (paste into the meeting email / message):
#    "Design pre-registration frozen today (commit <hash>, 12 Jun); hypotheses, budgets, splits and
#     inference rules are now locked — any later change will reach you as a flagged deviation."

# 10. Optional cleanup: git rm -r docs/staging/ in a follow-up commit once frozen.
```

**Abort rule:** if anything in `git diff` at step 3 surprises you, stop — the live PREREGISTRATION.md is
still untouched at that point.
