# `docs/ops/watch/` — the monitoring ledger

Created 2026-07-31 on Tamer's standing order: **monitor everything, constantly, every 2 minutes.**

| file | written by | what it is |
|---|---|---|
| `STATE.json` | `docs/ops/cycle.py` | the full state as of the last cycle, including the previous cycle's record count so the DELTA is computable |
| `CYCLE_LOG.md` | `docs/ops/cycle.py` (append) | one line per cycle. This is the audit trail that makes "I monitored continuously" a checkable claim instead of an assertion |
| `FINDINGS.md` | the session (append) | confirmed, evidence-graded science findings — the raw material CH4/CH5 are written from |

**The cycle is one command:**

```bash
python docs/ops/cycle.py --note "what you are doing this cycle"    # ~7 s
python docs/ops/cycle.py --ssh --note "..."                        # + cores/jobs off Myriad
```

Exit `0` all clear · `1` something changed, look · `2` a real problem, named on the line.

It checks, in this order: `docs/REMOTE_CONTROL.md` (Tamer's channel — flagged loudly the cycle it
changes) · the `STOP_CAMPAIGN` lever · `campaign_guards.py … all` · `arm_coverage.py` (the six repo
guards **cannot** see a missing arm — defect D14) · `budget_watch.py` · driver-log freshness · drift
against the sha the live drivers were launched from · records and spend, **with the delta**.

Verdicts already investigated and consciously accepted live in `docs/ops/acknowledged_alarms.txt`
and are reported as `known` rather than RED. That is deliberate alarm hygiene, not leniency: D15
survived ten hours because a CRITICAL sat unnoticed beside six green guards, and the countermeasure
is to make the known quiet so the new is loud. **Never add an entry there for something you have not
run to ground** — each entry carries its own explicit RE-TRIAGE trigger, and those triggers have
already fired once (the truncation guard, when a second model truncated).

The protocol itself — what to do with each verdict — is in `docs/RUN7_SESSION_PROMPT.md` §MONITORING
and `docs/HANDOFF.md` §1.
