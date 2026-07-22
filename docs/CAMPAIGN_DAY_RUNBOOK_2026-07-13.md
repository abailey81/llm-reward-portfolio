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
# 1. FREEZE (stamps the recorded hash = the canonical at GO; RECOMPUTED live — the R93 ccf2e76f
#    stamp is history: R95-R97 moved the would-be hash since, and any further pre-GO amendment
#    moves it again; the GO freeze stamps the then-current value + fresh bundle — R93/R94:
#    the freeze executes AT the full-campaign approval, never before) + verify:
python scripts/freeze.py            # the one irreversible act
python scripts/freeze.py --check    # recorded == canonical, frozen: true
# 2. Provenance anchors:
git tag prereg-v2.0 prereg-freeze-<hash8> && python scripts/make_prereg_bundle.py  # bundle sha -> CHANGELOG
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

## 9. THE V2 LEG QUEUE (R80/R82 — the 9 replication legs; report-only, behind the core)

> Legs run the identical FIVE LLM arms at the tier-30 floor (seeds 0–29 = the core's floor
> subset — the common-30 CRN pairing the pair-DiD estimator requires), byte-identical prompts,
> pinned transports. Queue order is FROZEN (`model_suite.queue_order`); truncate — never
> reorder — at the calendar gate **2026-08-14T23:59Z**. Nothing here gates H1–H4.

**(a) Pre-launch gates (once, needs OpenRouter credit ~$1–2; verdicts archived):**

```bash
python scripts/leg_gates.py --all --out outputs/leg_gates
# smoke (pin route live) + compliance baseline (10 authoring calls/model) + contamination screen.
# DeepSeek screen FAIL -> GLM-5.2 absorbs seat 1 (pre-declared); any flag routes to Tamer.
```

**(b) The per-leg launch line** (one invocation per leg, in queue order; `--leg` forces the
disjoint `leg_<label>` roots + the pinned author from `config/legs.yaml` — provider pin,
quantization, reasoning mode, max-tokens, and the usage-cost request all ride automatically):

```bash
MSYS_NO_PATHCONV=1 python scripts/run_campaign_cluster.py --leg deepseek-v4-pro \
    --arms distributional scalar scalar_cvar5 placebo placebo_shuffled \
    --seeds 0-29 --pass-mode B --priority -200 \
    --pack 5 --cores-per-training 1 --pool EF --seed-pool-blocks "EF:0-14,L:15-29" \
    --batch-tag leg1 --poll-secs 180 --chunk-tasks 1 \
    --output-dir outputs/campaign_cluster --resume
# Queue (frozen): deepseek-v4-pro -> glm-5.2 -> qwen3.6-27b -> qwen3.5-9b -> haiku-4.5
#              -> gpt-5.6-luna -> nemotron-3-super -> sonnet-5 -> gemini-3.5-flash  (R90/R92)
# Per leg: change --leg and --batch-tag (leg2, leg3, ...). No --baselines (H1 is core-only);
# no --tiered (legs are floor-tier by design). Priority -200 = legs only backfill idle GPUs.
```

**(c) Per-leg monitoring:** the same `campaign_monitor.sh` + sentinel watch the shared
`outputs/campaign_cluster` mirror — leg records live under `search_leg_<label>/`,
`test_leg_<label>/`, `frozen_leg_<label>/` and batch names are `leg_<label>_*`-prefixed, so the
state-class monitor's per-batch rows separate them at a glance. A leg model authoring garbage is
a FINDING (reliability table), not an incident: the T0 floor + selection floor handle it.

**(d) Spend reporting (R83, advisory):** every authored call (core AND legs) now records
per-call realized cost (OpenRouter `usage.cost`) or the tokens×planning-prices estimate
(Anthropic) to `outputs/spend_ledger.jsonl` automatically. Report any time:

```bash
python -c "from src.llm.spend_ledger import spend_summary; import json; print(json.dumps(spend_summary('outputs/spend_ledger.jsonl'), indent=2))"
# Warns in the driver log at 80%/100% of the $30 ADVISORY ceiling — never refuses (R83).
# The realized total is a CH4/CH6 reported number + the NatWest-brief line.
```

**(e) Per-leg bank gate:** before a leg's numbers enter any table, its archive root passes the
same write→verify integrity gate as the campaign root (`model_suite.per_leg_bank_gates`); the
gate log is archived with the leg's tables (write-time registry item 12). Aggregation:
`src.inference.leg_aggregate.leg_results_for_synthesis` (leg label → root map) feeds
`src.inference.cross_model` — the CH6 §6.7–6.8 numbers come ONLY through that path.

**(f) ⚠ v2 top-up sizing (2026-07-21 deep-sweep correction):** the "$25 Anthropic" recommendation
was sized 07-18 for OPUS ALONE (expected $5.95 / worst $15.86). v2 adds the Haiku (+~$1.2 exp)
and Sonnet (+~$3.6 exp / ~$9–11 worst) legs on the SAME key: Anthropic worst-case total ≈ $28–30.
**Recommend Anthropic ≥ $35** (or accept a possible mid-leg pause-for-top-up — legitimate under
advisory R83, but plan it). OpenRouter ~$25 remains comfortable (6 legs ≈ $5–8 expected; Luna's
cap bounds its tail). Also per ADR-060 addendum: **enable OpenRouter's account-level
do-not-log/train privacy setting BEFORE the gates run.**

**(g) ⚠ Freeze-day decision (G8):** `leg_calendar_gate: 2026-08-14T23:59Z` was sized for a
~Jul-28 launch. At the freeze (whenever Tamer calls it), CONFIRM or RE-FIX the gate date once,
pre-freeze — still calendar-fixed and exogenous; never moved after launch. Also fill the R85
`hf_pin` placeholders (5 open legs) from the official HF cards — `freeze.py` refuses while any
remain — and run the R84 anchor-value retrieval (SWE-bench-Verified per the registered rule,
sources archived).

**(h) The SECONDARY hand-reward panel (R97; POST-HEADLINE, report-only, rock-bottom priority).**
After the headline banks, run the SIX secondary canon members (the H1 four already ran with the
campaign; this completes the ten-name §9 panel, incl. the R97 `differential_downside_ratio`) at
the tier-30 floor seed set, on the cluster, via the EXISTING baselines flood + resume machinery
(no new code path — `--resume` makes the named arm a no-op, so only the six baselines submit):

    python scripts/run_campaign_cluster.py --arms distributional --resume \
      --baselines differential_downside_ratio mean_variance_utility return_minus_drawdown \
                  return_minus_downside return_minus_turnover log_growth \
      --seeds 0-29 --priority -310 --batch-tag secondary_panel

(-310 = strictly below every leg and rung line; 6 rewards × 30 seeds = 180 seeded-deterministic
trainings, zero LLM spend, resume-safe by run_id. Baseline names validate against REWARD_CANON
up front — fail-before-ssh. Laptop parity/fallback: `run_campaign.py --baselines-only
--baselines <names>`, whose `--baselines` flag refuses to run without `--baselines-only`, so the
headline's frozen `h1_baselines` path cannot be altered by it. If the deadline truncates the
set, CH6 §6.7's slot DISCLOSES the executed subset — never a silent narrowing.)

## 10. MODE D — MAXIMUM-PARALLEL LAUNCH (R88; supersedes §9(b)'s one-leg-at-a-time operation)

> **The global-minimum configuration** (2026-07-21 analysis): every driver line starts at L+0;
> the SGE priority ladder enforces the REGISTERED queue natively (core search/floor/tier-100 →
> legs −200…−280 in queue order → tier-189+ blocks from −300); search waves run the pack-2
> LATENCY lane (the 6-generation reflection chains are the critical path — pack-2 ≈ halves
> their wall time; tight auto-sized walltimes make them prime backfill); winner/rung bursts
> keep pack-5 THROUGHPUT; C4 rungs are pipelined (no drain bubbles). All ops-only (R88):
> identical seeds, steps, budgets, stopping rules. Expected vs §2+§9 serial operation:
> **all 10 legs ~L+4.5–5.5, tier-403 ~L+13–14.5, floor (BO-bound) ~L+1.5–1.8, mechanism ~L+0.7** (R95-updated).

**The ONE command (after the v2 freeze, on Tamer's LAUNCH word):**

```powershell
powershell -ExecutionPolicy Bypass -File scripts\mode_d_launch.ps1
# Spawns 12 supervised lines (core + h3 + 10 legs), each self-healing (relaunch-on-death), each with
# its own log: outputs\campaign_cluster\supervisor_<line>.log. Poll phases staggered 20s apart.
# Stop everything: create outputs\campaign_cluster\STOP_CAMPAIGN.
```

The core line = the §2 canonical line + `--search-pack 2 --search-poll-secs 45 --pipeline-rungs`;
each leg line = the §9(b) line + `--search-pack 2 --search-poll-secs 45` with its ladder priority
(deepseek −200 … sonnet-5 −270, gemini −280; R90/R92) — both embedded in `scripts/mode_d_supervisor.ps1`, which is the
single source of the exact argument lists (keep it in lockstep with §2/§9 on any flag change).
The launcher starts legs ~1h after the core (the CANARY SHIELD: most path breakage the C0 canary
exists to catch surfaces before any leg authoring is billed). Monitoring unchanged
(campaign_monitor.sh + sentinel over the shared mirror; per-line batch prefixes separate rows).
**P17 note (accepted trade, documented):** with pipelined rungs a block failure no longer halts
later blocks' already-queued work — exposure is bounded GPU-hours (priorities keep later blocks
behind), and BANKING is unaffected: a rung banks only when it and every rung below are complete.

**(2026-07-21d addition — the MODE-D SYNTHETIC MINI-REHEARSAL, a named pre-launch step):** the
12-line launcher has never run END-TO-END concurrently (each line dry-runs green; the
CONCURRENCY — shared mirror, poll staggering, per-batch locks under 12 pollers — is what is
unrehearsed). Once the VPN is up and BEFORE the freeze: run a ~30-minute synthetic mini
(`--synthetic`, tiny steps, pass A stub — zero spend) with the core + 2 leg lines via
`mode_d_supervisor.ps1`, confirm three clean supervisor logs + no lock/poll contention, then
STOP_CAMPAIGN. Cheap insurance against launch-day multi-driver surprises.

**(2026-07-21c addition — the H3 line):** the launcher now includes an **"h3" line** (12 lines total under R95: core + h3 + 10 legs):
the H3 single-shot FLOOR unit (`--h3-singleshot --seeds 0-29`) launches day-0 — the 12-unit tier
math includes H3, and it was previously a MANUAL post-headline invocation, i.e. the last human
dependency on every rung bank; single-shot has no reflection chain, so the floor unit lands ~L+1.
**The H3 LADDER COMPLETION is a follow-up invocation** (run it once the legs are in flight; it
must never jump the legs in the registered queue): the §3 line with `--seeds 0-567 --resume` and
`--priority -300` — archive-truth skips the done seeds. Also noted: the C3 gate releases C4 only
after ALL core units complete, so the gate-release time ≈ the BO chain (~L+1.7–2) — a deliberate
protection (the effect-blind integrity report reads a complete floor before mass compute);
per-unit rung pipelining was considered and REJECTED to keep it.

**(2026-07-21b additions — the training-speed pass):**
- **The floor's TRUE critical path is the bayes_opt chain** (30 inherently-sequential GP
  proposals ≈ 30 × [1.1h training + queue-wait + poll-notice]): the honest floor-bank estimate
  is **~L+1.5–1.8** (was ~L+1.7–2 before the 2026-07-21c canary-concurrency fix, and NOT the
  throughput-only L+1.3): the canary now runs CONCURRENTLY with the no-spend family arms — the
  30-step BO chain starts at L+0 instead of waiting ~5h for a gate that only protects Opus
  authoring (which still waits, spend-protection intact; canary-covered baselines are no longer
  double-submitted). Two fixes shave it: `bayes_opt` is HOISTED to
  `-p 0` (`_core_priority` — an array-of-1 every ~70 min costs nothing; at −100 every one of its
  30 steps could queue behind H2 waves, ×30), and `--search-poll-secs 45` cuts up to 180s of
  driver-notice latency per chain step (~1h+ on the BO chain alone; search-generation handoffs
  likewise). Fast polling runs ONLY while small chain batches are outstanding.
- **Launch-day pool-stripe tune:** an A100 (L) slot is worth ~1.7–2.2× a V100 (EF) slot. The
  seed-pool stripe ratio is a FREE pre-launch choice (device homogeneity per CRN seed is what
  matters, not the ratio): at GO, check `qstat -g c` for both pools' load and, if L has headroom,
  shift the stripe toward L before launching. Fixed once, pre-launch — never mid-flight.
- **Evaluated and REJECTED (keep them dead):** `torch.compile` on the cluster — the pack curve
  (1→102 / 5→253 agg steps/s) proves trainings are NOT GPU-bound (the Python env loop dominates),
  so compile buys ~nothing and costs re-certification; **pre-gate baseline flooding** — the only
  window it could fill (L+0→gate) is already saturated by the 9 leg lines' ~225 search tasks.
