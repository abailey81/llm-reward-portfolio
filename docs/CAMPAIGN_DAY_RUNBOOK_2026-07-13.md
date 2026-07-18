# CAMPAIGN-DAY RUNBOOK — the single, final launch sequence (2026-07-13)

> **This document is the campaign.** Every command below is final, copy-paste, and carries the
> ratified flags (CHANGELOG [2026-07-13] delegated ratifications). If a command here disagrees
> with an older doc, THIS document wins. Substrate: **UCL Myriad** (Tamer's directive); the
> laptop is the certified fallback only.

## 0. Preconditions (all must be TRUE before step 1)

| # | Precondition | How verified |
|---|---|---|
| 0.1 | 30-point B\* curve verdict applied (pre-committed rule, EVIDENCE_LEDGER) | ledger claim 8 shows the verdict + any amendment ratified |
| 0.2 | Post-verdict wording batch landed (incl. the hash-bound PREREG/yaml lines) | commit exists; gate re-run green |
| 0.3 | **FROZEN**: `scripts/freeze.py` run (delegated; announced loudly) | `freeze.py --check`: frozen=true, recorded==canonical |
| 0.4 | p4detb leg-2 complete → cluster checkout synced to HEAD | `git archive HEAD \| ssh myriad tar -x -C ~/llmrp` AFTER leg-2, never before |
| 0.5 | Bank-gate rehearsal passed on the pm2 archive | `bank_gate.py --archive outputs/proto_myriad --rehearsal` output |
| 0.6 | Anthropic balance sufficient for ~$50 authoring (+$70 top-up if low) | step 4 smoke + Tamer's console |

## 1. Pre-flight checklist (run in order; each must pass)

```bash
# 1. Freeze gate — 21/21 green, recorded hash matches canonical:
python scripts/freeze.py --check

# 2. Full test suite (background, ~10 min) — 0 failures AND the skip report shows ONLY the
#    3 permanent Windows/POSIX skips (2026-07-13: a transient made 66 tests skip once — the
#    -rs report makes any recurrence self-documenting; skips are fail-safe but must be READ):
python -m pytest tests/ -q -rs

# 3. Keyless wiring dry-run of the EXACT campaign shape (no ssh, no spend):
python scripts/run_campaign_cluster.py --dry-run --synthetic \
    --arms distributional scalar scalar_cvar5 placebo placebo_shuffled random_search bayes_opt

# 4. ONE-call Opus smoke through the campaign's own plumbing (~$0.01; live-verified 2026-07-13, 3.1s):
python scripts/author_smoke.py

# 5. Remote state: VPN up, home resolved, gold staged, venv/apptainer certified:
ssh myriad "ls ~/Scratch/llmrp /acfs/users/ucestes/gold 2>/dev/null | head; qstat | head -3"

# 6. Laptop driver host: disable sleep (the driver runs for days), check disk:
powercfg /change standby-timeout-ac 0   # (admin shell)
```

## 2. THE LAUNCH (tiered ladder: C0 canary → C1–C3 core → gate → C4 rungs)

> **LAUNCH VIA THE SUPERVISOR (2026-07-18, the VPN-outage hardening).** The 07-17 outage
> measured the failure mode: the driver's ops-failure count cap (72 × poll interval) tripped at
> 6.5 h and both drivers died loudly-but-unattended. Two fixes are live: (i) the count cap now
> defaults to 240 (= the 12 h wall bound at poll 180 s); (ii) **`scripts\campaign_supervisor.ps1`
> relaunches the driver on ANY nonzero exit** (idempotent by design: archive-truth resume, P12
> lock auto-break, no authoring re-billed) — a driver death now costs only the backoff, and
> RUNNING ARRAYS ON MYRIAD ARE NEVER AFFECTED by laptop-side outages. Stop deliberately via
> `outputs\campaign_cluster\STOP_CAMPAIGN`. Exit 0 = complete OR a C3 RED-gate stop — the
> supervisor stops there too, correctly: a RED gate needs a human before `--approve-tier1`.
>
> ```powershell
> powershell -ExecutionPolicy Bypass -File scripts\campaign_supervisor.ps1
> ```
> (The raw single-shot line below remains valid for manual runs; the supervisor embeds it —
> keep them in lockstep.) Also set ssh keep-alives in `~/.ssh/config` (`ServerAliveInterval 60`,
> `ServerAliveCountMax 10`) to ride out brief VPN blips without connection resets.

The **striped seed-pool blocks** (ratified 2026-07-13): both pools engaged at EVERY ladder rung
(the old contiguous split idled the A100s until seed 284). Halves of each rung range; CRN pairs
stay device-homogeneous per seed (the blocked-design invariant); parser merges per pool.

```bash
MSYS_NO_PATHCONV=1 python scripts/run_campaign_cluster.py --tiered \
    --arms distributional scalar scalar_cvar5 placebo placebo_shuffled random_search bayes_opt \
    --baselines raw_return return_minus_variance return_minus_cvar differential_sharpe \
    --pass-mode B --llm-from campaign \
    --pack 5 --cores-per-training 1 --pool EF \
    --seed-pool-blocks "EF:0-14,L:15-29,EF:30-64,L:65-99,EF:100-143,L:144-188,EF:189-233,L:234-278,EF:279-308,L:309-339,EF:340-370,L:371-402,EF:403-484,L:485-567" \
    --batch-tag c1 --poll-secs 180 --chunk-tasks 1 \
    --output-dir outputs/campaign_cluster --resume
```

Notes: `--resume` is SAFE on a fresh dir and MANDATORY on any restart (F2 guard refuses a dirty
non-resume start). h_rt auto-sizes from the measured worst-rate curve. The C0 canary (first 3
baselines × 30 core seeds) runs first and HARD-STOPS the campaign on any failure — before any
Opus spend. The C3 gate auto-proceeds on green execution health (effect-blind); on a stop:
review `outputs/campaign_cluster/tier1_integrity.md`, then re-run the SAME line + `--approve-tier1`.

## 3. C5 — the H3 single-shot control (after, or alongside, the headline)

```bash
MSYS_NO_PATHCONV=1 python scripts/run_campaign_cluster.py --h3-singleshot \
    --pass-mode B --llm-from campaign --pack 5 --cores-per-training 1 --pool EF \
    --seed-pool-blocks "EF:0-14,L:15-29,EF:30-64,L:65-99,EF:100-143,L:144-188,EF:189-233,L:234-278,EF:279-308,L:309-339,EF:340-370,L:371-402,EF:403-484,L:485-567" \
    --batch-tag c1 --poll-secs 180 --chunk-tasks 1 --output-dir outputs/campaign_cluster --resume
```

Roots are disjoint by construction (`*_h3_singleshot/`), batch names `h3ss_*`, priority −100.

## 4. C6 — D1 curve levels (report-only, POST-bank-gate, never day-1)

Any re-search invocation MUST pass `--root-suffix` (the P4 hazard class — enforced at the CLI):

```bash
# example: the 10-candidate saturation level
MSYS_NO_PATHCONV=1 python scripts/run_campaign_cluster.py \
    --arms distributional --candidates 10 --generations 1 \
    --root-suffix curve_c10 --priority -200 \
    --pass-mode B --llm-from campaign --batch-tag c1d1 \
    --output-dir outputs/campaign_cluster --resume
```

## 5. Monitoring (arm all three at launch)

```bash
# (a) Fleet monitor — state-class qstat diff + record counts + Eqw (the proven v3 pattern):
#     run as a background loop; alert classes: Eqw (P1 handles, watch anyway), record stalls.
ssh myriad qstat   # manual spot-check form
# (b) Driver heartbeats (staleness = driver problem, not cluster):
ls outputs/campaign_cluster/driver_status/   # per-batch JSON, ts field
# (c) C measurement (the one unknown; read at +24h and +48h):
ssh myriad "qstat -s r | grep ' r ' | wc -l"   # concurrent running tasks ≈ C
# (d) Authoring spend: count llm_calls.jsonl rows vs the auto-cap (2×arms×candidates+60):
find outputs/campaign_cluster/search -name llm_calls.jsonl -exec wc -l {} +
```

Decision aids: C≥12 → n=403 in ~7–9 days (on plan). C∈[4,8) → still fine via rung banking.
C<4 for 48h → the E1 exogenous-stop reading: bank the highest CLEAN rung; do NOT chase 403.

## 6. Resume / abort / rollback

- **Resume anything**: re-run the SAME command line (+`--approve-tier1` only after a gate stop).
  Completion is archive-truth; nothing re-trains, ledger-permanent failures never resubmit.
- **Driver crash/reboot**: same line again. The P12 lock auto-breaks for a dead owner.
- **Abort an array**: `ssh myriad qdel <jobid>` — the drain machinery treats it as a purge
  (P13: no retry-bump without qacct evidence).
- **NEVER**: launch two drivers with the same `--batch-tag`+arms (P12 refuses); reuse an
  output dir for a different experiment without `--root-suffix`; edit hash-bound files
  post-freeze (amendments only).

## 7. At the end: the bank gate

`python scripts/bank_gate.py --archive outputs/campaign_cluster --seeds <realized rung>` — the
rehearsed six-step runsheet (archive integrity → resume audit → analyze → variance → fed-delta
SNR → prereg bundle). Then and only then: numbers into the PDF (evidence-ledger grades enforced).
