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
| 0.4 | Cluster checkout synced to HEAD **+ the GIT_COMMIT marker written** (2026-07-18: the archive deploy is not a work-tree — without the marker every record's code identity is None) | `git archive HEAD \| ssh myriad tar -x -C ~/llmrp && git rev-parse HEAD \| ssh myriad "cat > ~/llmrp/GIT_COMMIT"` |
| 0.5 | Bank-gate rehearsal passed on the pm2 archive | `bank_gate.py --archive outputs/proto_myriad --rehearsal` output |
| 0.6 | Anthropic balance: MEASURED need (2026-07-18, from 160 archived calls x $5/$25) = expected **$5.95** (180 calls), worst-case-at-caps **$15.86** (480); recommended top-up **$25**; **SINGLE-KEY PLAN (2026-07-20, Tamer's decision — supersedes the same-day two-key/failover plan):** ONE funded key in `ANTHROPIC_API_KEY`, minimum **$16** (covers the $15.86 worst-case at the spend caps), recommended **$25**. `ANTHROPIC_API_KEY_FALLBACK` stays **UNSET** — the transport's failover mechanism (2a46f5d, test-locked byte-identical when unconfigured) remains in the code as dormant insurance only. If the key dies mid-run anyway: the authoring loop SKIPS the slot loudly (never a permanent rejection), the monitor screams, and a top-up + supervisor relaunch `--resume`s exactly the unauthored slots — zero waste by the archive-replay construction | step 4 smoke + Tamer's console |

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

# 4. ONE-call Opus smoke through the campaign's own plumbing (~$0.01; live-verified 2026-07-13, 3.1s).
#    (SINGLE-KEY PLAN 2026-07-20: no fallback key is configured; `author_smoke.py --fallback` exists
#    but is NOT part of pre-flight — run it only if a fallback is ever deliberately set.)
python scripts/author_smoke.py

# 5. Remote state: VPN up, home resolved, gold staged, venv/apptainer certified:
ssh myriad "ls ~/Scratch/llmrp /acfs/users/ucestes/gold 2>/dev/null | head; qstat | head -3"

# 6. Laptop driver host: disable sleep (the driver runs for days), check disk:
powercfg /change standby-timeout-ac 0   # (admin shell)

# 7. PAUSE WINDOWS UPDATE for the campaign window (2026-07-18 threat audit: an auto-update
#    reboot kills the supervisor+driver silently — resume is one command but unattended hours
#    are lost). Settings -> Windows Update -> Pause for 5 weeks (Tamer's click; admin).
#    On any reboot: just re-run the supervisor (idempotent).

# 8. Cluster calendar (2026-07-18 audit): Myriad's maintenance day = the SECOND TUESDAY of
#    every month (at-risk from 08:00; next: Aug 11). The Jul-19 launch finishes n=403 ~Aug 1,
#    clear of it; if rungs run past Aug 10, treat Aug 11 as a planned at-risk day — running
#    jobs may die and REQUEUE (idempotent; no data loss by design); the supervisor rides it.
#    Scratch headroom verified 2026-07-18: 97 MB used / 1 TB filesystem.

# 9. COMMIT-CHARGE headroom (2026-07-18 forensics; enforced by preflight.py check_commit_headroom,
#    FAIL < 6 GB): exhausted system commit stalls every spawned validation child for minutes in the
#    numpy DLL load (the ArmouryCrate.UserSessionHelper leak held 7.61 GB for 8 days; headroom hit
#    0.37 GB). Preflight now gates this; if it FAILs: find the leaker
#    (Get-Process | sort PrivateMemorySize64 -desc | select -First 8) — the known offenders are
#    ArmouryCrate.UserSessionHelper (kill; Turbo re-applies at boot) and a bloated StateRepository
#    svchost (admin restart — Tamer). Durable improvement (Tamer, admin, optional): set a FIXED
#    16 GB pagefile on D: (C: free space caps commit growth).
```

## 2.0 THE GO SEQUENCE (executed by Claude on Tamer's OFFICIAL GO — in this exact order)

```bash
# 1. FREEZE (stamps the recorded hash = canonical ce5db62c) + verify:
python scripts/freeze.py            # the one irreversible act
python scripts/freeze.py --check    # recorded == canonical, frozen: true
# 2. Provenance anchors:
git tag prereg-freeze-ce5db62c && python scripts/make_prereg_bundle.py  # bundle sha -> CHANGELOG
# 3. Sync freshness (marker included; a no-op if HEAD unchanged since the last sync):
git archive HEAD | ssh myriad "tar -x -C ~/llmrp" && git rev-parse HEAD | ssh myriad "cat > ~/llmrp/GIT_COMMIT"
# 4. LAUNCH (two commands, then hands off):
powershell -ExecutionPolicy Bypass -File scripts\campaign_supervisor.ps1   # (PowerShell window)
bash scripts/campaign_monitor.sh &                                          # (Git Bash window)
```

The C0 canary fires first and HARD-STOPS everything before any Opus spend if the path is
unsound. First records expected within hours; the C measurement reads at +24 h / +48 h.

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

## 5. Monitoring (arm (a) the state-class monitor [+ntfy push] and (e) the sentinel at launch; (b)–(d) are read-on-demand)

```bash
# (a) THE CAMPAIGN MONITOR (start at launch — the proven v3 state-class pattern, pointed at
#     the campaign roots; run as a background loop, ~300 s cadence):
#     watches: qstat state-class diffs for c1_*/h3ss_* names, records under
#     outputs/campaign_cluster/{search,test}, Eqw appearance, driver_status staleness >15 min.
#     PUSH ALERTING (2026-07-18): export NTFY_URL=https://ntfy.sh/<private-topic> before
#     starting it and every state-change line is pushed to the phone (Priority: high on Eqw or
#     a stale heartbeat — the two states that need a human). Pick the topic at launch; treat it
#     as a secret (anyone with the topic name can read it).
NTFY_URL=https://ntfy.sh/<private-topic> bash scripts/campaign_monitor.sh &
ssh myriad qstat   # manual spot-check form
# (b) Driver heartbeats (staleness = driver problem, not cluster):
ls outputs/campaign_cluster/driver_status/   # per-batch JSON, ts field
# (c) C measurement (the one unknown; read at +24h and +48h):
ssh myriad "qstat -s r | grep ' r ' | wc -l"   # concurrent running tasks ≈ C
# (d) Authoring spend: count llm_calls.jsonl rows vs the auto-cap (2×arms×candidates+60):
find outputs/campaign_cluster/search -name llm_calls.jsonl -exec wc -l {} +

# (e) THE SENTINEL (2026-07-18 readiness pass: it was built+certified 07-06 but never armed in
#     this runbook). 17 read-only invariant checks incl. the MYRIAD DRIVER LEASE deadman (stale
#     driver heartbeat → WARN at ~40 min, CRITICAL at ~90 min — visible within minutes, not at
#     the end), divergence clustering, disk fill-rate forecast, error taxonomy. Verified against
#     the cluster mirror pre-launch (2026-07-18: runs clean).
.venv/Scripts/python.exe scripts/sentinel.py --watch outputs/campaign_cluster &
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

## 8. THE CAMPAIGN-WINDOW QUEUE (2026-07-18 completeness sweep — the report-only items whose
## scheduled slot IS the ~11 GPU-busy days; none is freeze-bound, none gates the headline)

| # | Item | When | Invocation / plan | Registered where |
|---|---|---|---|---|
| 1 | **Dose-response tier** (R77-ii): CAMPAIGN winners × {200k, 400k, 800k} × 10 CRN seeds, report-only | after the C3 review gate (winners frozen) | the p6 ladder machinery pointed at the CAMPAIGN frozen winners (`scripts/p6_authored_ladder.py` `--singles` pattern; budgets 200000,400000,800000; seeds 0-9; `-p -200` so it only ever backfills idle GPUs; `--root-suffix dose` for namespaced roots) | PREREGISTRATION R77(ii); F11 campaign re-render |
| 2 | **P3 sub-experiments** (SQ3 named-vs-blinded + legible-format): small authored probes | any API-quiet day during the window | `python scripts/run_subexperiment.py --mode named` and `--mode legible` (launch-ready, rehearsed keyless; small Opus spend, covered by the $25 top-up margin) | mechanism protocol §SQ3; 2026-07-02i |
| 3 | **FTSE-100 lite panel build** (ADR-047, rescheduled 2026-07-02i to this window): acquire + build the survivorship-free FTSE-100 panel via `data_pipeline/` (PowerShell + `.venv-lseg`; NEVER from the Bash tool) | the GPU-busy / operator-quiet days | panel build only during the window; the U4b **zero-shot replication** (frozen winners re-tested on the FTSE panel, no authoring) runs post-bank as Stage-2.A free depth | ADR-047; GRADE_SECURITY 2.A |
| 4 | **M2 model-fleet survey** (real run on campaign stimuli) | post-bank (needs the campaign fed-delta quantiles) | `scripts/m2_survey.py` + `config/m2_models.yaml` (harness validated 2026-07-13) | M2 protocol v1 (registered 2026-07-12) |
| 5 | **D6/U5 algorithm robustness** (TQC / PPO / TD3 critics on frozen winners, no authoring) | post-bank, free depth | `run_test_leg` on the frozen Stage-1 winners with the alternate agent configs | GRADE_SECURITY 2.A |

Everything above is REPORT-ONLY and disjoint from the frozen m=6 family: it can deepen the
story, never gate or contaminate the headline. Items 1–3 belong to the campaign window itself;
4–5 wait for the bank gate by construction.
