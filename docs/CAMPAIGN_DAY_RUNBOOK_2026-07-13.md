# CAMPAIGN-DAY RUNBOOK — the single, final launch sequence (2026-07-13)

> ⚠ **STALE AS OF 2026-07-31 — DO NOT COPY THE `--priority` FLAGS BELOW.** The intra-user `-p`
> ladder is RETIRED (record §54): every job now goes out at `-p 0`, and `run_campaign_cluster.py`
> **hard-exits** on a negative `--priority` unless `--allow-deprioritise` is also passed (finding
> #96). Following any `--priority -200/-300/-310` instruction in this runbook will therefore
> abort the launch rather than deprioritise it. Flagged by an independent auditor; the commands
> are left in place as dated history, but the flag must be dropped when running them.


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
| 0.6 | Anthropic balance: MEASURED need (2026-07-18, from 160 archived calls x $5/$25) = expected **$5.95** (180 calls), worst-case-at-caps **$15.86** (480); recommended top-up **$25**; **SINGLE-KEY PLAN (2026-07-20, Tamer's decision — supersedes the same-day two-key/failover plan):** ONE funded key in `ANTHROPIC_API_KEY`, minimum **$16** (covers the $15.86 worst-case at the spend caps), recommended **$25**. `ANTHROPIC_API_KEY_FALLBACK` stays **UNSET** — the transport's failover mechanism (2a46f5d, test-locked byte-identical when unconfigured) remains in the code as dormant insurance only. If the key dies mid-run anyway: the authoring loop SKIPS the slot loudly (never a permanent rejection), the monitor screams, and a top-up + supervisor relaunch `--resume`s exactly the unauthored slots — zero waste by the archive-replay construction | step 4 smoke + Tamer's console. **SIZING SUPERSEDED (audit 2026-07-24): the figures in this row are the v1 Opus-only measurement; the v2 authority = 9(f) (worst ~28-30, guidance >=35) + HANDOFF Money (FUNDED $25.91 on 2026-07-22, key live-verified; ~27 worst-at-caps by the precise calc; pauses-not-wastes).** |

## 1. Pre-flight checklist (run in order; each must pass)

```bash
# 1. Freeze gate — 23/23 green, recorded hash matches canonical (was "21/21"; the gate grew to 22
#    with the executed-TF32 mirror and to 23 since — corrected 2026-07-27, verified by running it.
#    Read the printed count, never this number: a hardcoded expectation is how a gate silently
#    stops covering its newest checks):
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
#    every month (at-risk from 08:00; next: Aug 11). From a ~Jul-27 GO, tier-403 lands ~Aug 8-11
#    (L+13-14.5, R95) — STRADDLING Aug 11: treat it as a planned at-risk day — running
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
# 4. LAUNCH — MODE D (R88, §10; audit 2026-07-22: this step previously named the LEGACY
#    single-line campaign_supervisor.ps1 — §10's mode-D launcher is the ratified launch):
# PRECEDENCE (audit 2026-07-24): the ADVISOR'S live values SUPERSEDE the embedded defaults
# for --chunk-tasks / --seed-pool-blocks / --pool — transplant them into
# scripts\mode_d_supervisor.ps1 BEFORE launching (the supervisor stays the single source of
# the exact argument lists; the advisor is where those arguments now COME FROM at GO).
powershell -ExecutionPolicy Bypass -File scripts\mode_d_launch.ps1   # 12 supervised lines (§10)
# Monitoring arms (audit 2026-07-24: step 4 previously omitted both — §5 documents them but the
# GO sequence must be executable VERBATIM): export NTFY_URL FIRST or push alerts silently
# never arm, and launch the 17-check sentinel alongside the monitor (§5 arms (a)+(e)):
NTFY_URL=https://ntfy.sh/<private-topic> bash scripts/campaign_monitor.sh &   # (Git Bash window)
.venv/Scripts/python.exe scripts/sentinel.py --watch outputs/campaign_cluster &
# 5. THE LIVE ALLOCATION WATCHER (2026-07-24 system; third window — runs for the whole campaign):
python scripts/allocation_advisor.py --watch 900 --archive-root outputs/campaign_cluster
#    every 15 min: live pools/contention -> [ALERT] on regime flips / U-V unlocks / pool shifts;
#    self-measured rate + ETAs once records land; state persists across restarts. Plan changes
#    apply at natural boundaries only (new batch/rung submissions via supervisor relaunch,
#    --resume-safe) — never mid-batch, priorities never touched.
# (campaign_supervisor.ps1 remains the single-line FALLBACK if mode-D must be abandoned mid-run.)
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
    --pass-mode B --llm-from campaign \
    --pack 5 --cores-per-training 1 --pool EF \
    --seed-pool-blocks "EF:0-14,L:15-29,EF:30-64,L:65-99,EF:100-143,L:144-188,EF:189-233,L:234-278,EF:279-308,L:309-339,EF:340-370,L:371-402,EF:403-484,L:485-567" \
    --batch-tag c1 --poll-secs 180 --chunk-tasks 1 \
    --output-dir outputs/campaign_cluster --resume
```

Notes: `--resume` is SAFE on a fresh dir and MANDATORY on any restart (F2 guard refuses a dirty
non-resume start). h_rt auto-sizes from the measured worst-rate curve. The C0 canary (first 3
baselines × 30 core seeds) runs first and HARD-STOPS the campaign on any failure — before any
Opus spend.

> **⚠ `--baselines` IS DELIBERATELY ABSENT (fixed 2026-07-26 — it was a launch-breaking defect).**
> This line used to hand-type `--baselines raw_return return_minus_variance return_minus_cvar
> differential_sharpe`, a hand-mirrored copy of a FROZEN config value — the exact bug class the
> 2026-07-18 DEFAULTS-CLASS SWEEP killed for B\*/candidates/generations. It then **drifted**: the
> H1 canon expanded **4 → 11** on 2026-07-26 and this list did not, so the headline launch would
> have run a **SUBSET** of the registered family — silently making the **N6 intersection-union
> node unsatisfiable** (its p = max over the 11 one-sided leg p-values) and **mis-sizing the C0
> canary** (which defaults to the first 3 of this list). The same stale four were live in
> `campaign_supervisor.ps1`, `mode_d_supervisor.ps1` and `install_onstart_task.ps1`.
> **Fix:** under `--tiered` the launcher now resolves the frozen `config/campaign.yaml
> h1_baselines` itself (`run_campaign_cluster.py::resolve_cluster_baselines`, the same drift-proof
> path the laptop driver has always used), and an explicitly-passed list must be EXACTLY that
> family or the launch is refused before ssh. Regression-locked by
> `tests/test_run_campaign_cluster.py::test_resolve_cluster_baselines_refuses_the_drifted_runbook_four`.
> **Never re-add a hand-typed baseline list to a launch line.** The C3 gate auto-proceeds on green execution health (effect-blind); on a stop:
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

## 9. THE V2 LEG QUEUE (R80/R82/R95 — the 10 replication legs; report-only, behind the core)

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
#              -> gpt-5.6-luna -> nemotron-3-super -> sonnet-5 -> gemini-2.5-flash -> kimi-k3  (R90/R92/R95)
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

**(h) The SECONDARY hand-reward panel (R97) — ⚠ SUPERSEDED 2026-07-26 by the H1 canon expansion.**

> The 2026-07-26 expansion made the registered H1 family **the full 11-name canon**, so the
> HEADLINE campaign now trains every member of this panel at every rung. There is no "secondary
> remainder" left to run: executing the command below would **duplicate already-banked work**, and
> the launcher now **refuses** it anyway (a partial family fails `resolve_cluster_baselines`).
> Retained only as the historical record of the R97 execution path. If a genuinely report-only
> SUBSET is ever wanted, use the R97-sanctioned laptop route (`run_campaign.py --baselines-only
> --baselines <names>`), which is scoped to report-only work by construction.

*(historical)* After the headline banks, run the SIX secondary canon members (the H1 four already ran with the
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

**Launch-day pre-checks (row 30m/30o, audit 2026-07-22):**
- **SGE job-cap check (C5):** pipelined rungs + `--chunk-tasks 1` can enqueue ~1,200 arrays from
  the core line alone. BEFORE launch run `qconf -sconf | grep -i max` and
  `qconf -srqs 2>/dev/null | head` on Myriad. PROBED 2026-07-24: max_u_jobs = 1000 (RQS clean)
  -> the C5 condition FIRES for the raw chunk-1 pipelined flood (~1,200 arrays): resolve per the
  TWO-REGIME doctrine + the advisor's chunk value (its QUIET cap-note names this exact bound); either
  raise `--chunk-tasks` (fewer, larger arrays) or drop `--pipeline-rungs` (sequential blocks) —
  both ops-only. A cap hit mid-run classes as a transport error (12h retry then fatal) — cheap to
  check, expensive to discover live.
- **H3 canary exposure (disclosed):** the h3 line starts at L+1h (the stagger shield) and authors
  ~30 Opus candidates WITHOUT waiting on the C0 canary verdict (it is a separate process). Bounded
  spend (~$1-2) and the stagger covers most path breakage; accepted as a design trade — if C0
  fails in under an hour, touch `outputs\campaign_cluster\STOP_CAMPAIGN` to stop the h3 line too.

**THE ADAPTIVE ALLOCATION SYSTEM (2026-07-24; automates every lever below):**
`python scripts/allocation_advisor.py [--probe-age-hours H] [--vram-per-training G --rate R
--remaining "tier403=6800,..."]` — ONE command that live-probes Myriad (telemetry archived to
outputs/myriad_telemetry.jsonl) and PRINTS the current-optimal settings: the §3b chunking regime,
the search-lane pool pin, the exact throughput-weighted `--seed-pool-blocks` string (CRN
block-homogeneous by construction), canary-gated pack depths, the U/V probe verdict, and
measured-rate ETAs. Advisory only (nothing submitted; priorities untouchable by construction —
test-locked). Run at GO morning, after the canary (with --vram-per-training + --rate), and daily
during the campaign for recomputed ETAs. Logic: src/cluster/{telemetry,allocation}.py;
tests/test_allocation.py (test-locked; 16+ tests); LIVE-VERIFIED 2026-07-24 against the real cluster.

**GO-DAY THROUGHPUT LEVERS (2026-07-24 deep Myriad dig — legitimate, NEVER touch priority):**
0. **BEST-HARDWARE PROTOCOL (2026-07-24; the U/V probe + the search-lane pin).**
   (a) **U/V pools (12x A100-80G)**: the JSV ACCEPTED `-ac allow=U` and `allow=V` submissions
   (probe jobs 10293/10294 queued 2026-07-24, 5-min hostname probes; control 10295 on EF).
   **★★ BOTH VERDICTS IN (2026-07-24): probe_u RAN on node-u00a-001 (qacct: smp-U, exit 0) AND
   probe_v RAN on node-v00a-002 (stdout probe_v.o10294; qacct shows job-ID reuse so the stdout
   hostname is the evidence) — BOTH while the EF control (10295) was STILL queued through a
   ~2.7k-qw jam. The A100-80G U/V pools were LESS contended for our account than the default EF
   pool. U/V SCHEDULING ACCESS = CONFIRMED (the full +12 A100-80G unlock); add both to the GO
   stripe.** What the probes did NOT prove (hostname-only stdout): GPU visibility/VRAM class — the
   GO-day canary's nvidia-smi confirms A100-80G + pack depth before striping deep (the
   already-registered canary-gated pack rule). The EF control still queuing is itself the finding:
   at GO, PREFER U/V over EF when they show free capacity.
   (b) **Search-lane pool pin**: the floor's critical path is the BO/reflection CHAIN (sequential
   trainings). If L (or U/V) has live headroom at GO, pin the CORE's SEARCH lane to the A100 pool
   (`--pool` on the search invocation): ~1.7-2.2x faster chain steps -> floor ~L+1.5-1.8 ->
   ~L+1.0-1.2. CRN note: chains are homogeneous if the whole lane pins to one pool; TEST stripes
   stay as ratified (blocks are pool-homogeneous by construction). Ops-only under the ratified
   launch-day pool-stripe clause.
1. **Pool selection (the big lever, already parameterized via `--pool` -> `-ac allow=`).** Myriad
   free GPU pools (dossier-probed): **EF** = ~19 nodes x 2 V100 (~38; larger, LESS contended);
   **L** = 6 nodes x 4 A100-40G (24; ~1.7-2.2x faster/training, MORE contended). At GO run
   `ssh myriad "qhost -F gpu | grep -B1 'gpu=[1-9]'"` to read live free-GPU headroom per pool, and
   pin whichever maximizes (availability x speed) for banked trainings — SUBJECT to the CRN
   determinism rule (a comparison unit stays on ONE gpu type; `pool_confirmatory` enforces). Default
   EF (bigger pool). Tonight: 5 EF + 3 L nodes had free GPUs while we still queued (fair-share depth).
2. **tmpfs right-sizing (unexploited — measure then cut).** The gold panel is ~35 MB yet the
   jobscript requests **tmpfs=15G** (jobscript.py default). Nodes with a free GPU but <15G free
   local scratch are EXCLUDED for us -> free GPUs sit idle while we wait. AT THE CANARY: measure the
   real tmpfs high-water mark (`df /tmpdir` on-node, or the run_one working-dir peak), then reduce
   `tmpfs=` to (peak + margin) so many more nodes qualify. DO NOT cut blind (under-provision = job
   failure; it is load-bearing for gold staging + working space). Verified legitimate, no priority.
3. **TICKET CONCENTRATION (2026-07-24 dossier — the scheduler-arithmetic lever).** Myriad's live
   config: functional tickets dominate (5e8 vs share 1e4) and `share_functional_shares TRUE`
   splits OUR per-user slice across OUR pending jobs -> few LARGE arrays beat many small ones by
   ~a 50x per-job ticket factor at campaign scale. At GO apply the TWO-REGIME
   CHUNKING DOCTRINE (dossier §3b; max_pending_tasks_per_job=1 discovered 2026-07-24): read live
   contention first — CONTENDED -> chunk BIG (priority dominates); QUIET -> keep many arrays
   (each ramps 1 task/cycle from cold; the flood IS the fast ramp). Always < 1000 pending jobs. NUANCE (live-verified): held (hqw)
   tasks accrue NO waiting time — only eligible jobs age; pipelined rungs buy concurrency, not age.
4. **Per-VRAM pack calibration at canary**: A100 pools may host ~2x the envs/GPU of pack-5;
   the jobscript already archives nvidia-smi -> measure headroom, raise pack per pool if clear.
5. Already on: pack-5 (fewer queue entries), h_rt auto-size (backfill-friendly), `reserve: y`
   (anti-starvation; NEVER kill+resubmit a reserved queued job). NOT available: self-elevation
   (fair-share; forbidden for us anyway), U/V A100-80G pools (requestability unknown — an RC
   question, Tamer's call), more free allocation (RC). Full ground truth:
   `docs/MYRIAD_EXPERT_DOSSIER_2026-07-24.md`.

**CHECK-DAY PRE-MORTEM ORDER (2026-07-23; run in THIS order — the cheap probes first):**
1. `ssh myriad "qstat | head -3; ls ~/Scratch/llmrp; qconf -sconf | grep -i max_u_jobs"` — access,
   ALLOCATION ALIVE, scratch, job-cap: learn the worst news in minute one, at $0.
2. Sync the checkout (`git archive HEAD | ssh myriad tar -x -C ~/llmrp` + GIT_COMMIT marker) —
   the cluster MUST run the post-audit code; re-run build_env/G1 cert if imports fail.
3. `python scripts/preflight.py` laptop-side (commit headroom, disk).
4. THEN: gates + mini-rehearsal + fast rehearsal in parallel.
5. Gold checksum spot-check on ACFS during the afternoon (GO-readiness, not check-critical).
REHEARSAL AUTHOR FALLBACK (pre-declared): qwen3.5-9b -> deepseek-v4-pro -> nemotron-3-super
(any cheap leg works; the rehearsal validates machinery, not the author).

**The idle-tail leg-deepening (R100; fires AFTER the core banks the 403 rung (the amended legs-first order; the 403->568 block runs LAST-if-it-fits), before the Aug-27 stop):**
per leg, in queue order, the H3-completion pattern at rung priority — e.g.
`python scripts/run_campaign_cluster.py --leg deepseek-v4-pro --arms distributional scalar scalar_cvar5 placebo placebo_shuffled --seeds 0-99 --resume --priority -300 --batch-tag leg1_t100` — cumulative rungs, resume-safe, report-only; bank each leg's highest completed rung; STOP at 2026-08-27 regardless of position (the pre-committed exogenous stop; GO-day may move it EARLIER only).
ORDER (amended 2026-07-23, Tamer): legs deepen FIRST after the core's 403 banks; the core's
403->568 block runs LAST, only if the remaining tail fits it whole (an incomplete 568 banks
nothing above 403 — the cumulative-rung rule). M2 (GPU-free) runs in parallel post-bank.

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
  window it could fill (L+0→gate) is already saturated by the 10 leg lines' ~250 search tasks.

---

## 11. ★★★★ THE COMPUTE LANE — GO-day operating rules (2026-07-26 capacity session)

> **Scope:** what to actually DO with CPU/GPU/threads at launch. The measurements behind every
> number live in `docs/MYRIAD_EXPERT_DOSSIER_2026-07-24.md` **§0-PRE** (capacity) and **§0-LIMITS**
> (the stop rules) — the owner of scheduler truth; this section owns the *launch mechanics* only and
> deliberately does not restate the evidence. Model: `src/cluster/lanes.py`.
>
> **This section SUPERSEDES §10's GPU-pool-centric framing for the CPU-lane campaign.** §10's
> pool-stripe/pack levers still apply to whatever GPU work is run.

### 11.1 The job shape — non-negotiable, all measured

```
#$ -pe smp 8          # NOT 16, NOT 32, NEVER 36
#$ -l mem=2G          # per core
#$ -l h_rt=<honest>   # walltime does NOT affect placement - size it for the real work
                      # CPU lane: NO -l gpu, NO -ac allow=
```

- **`smp 8`.** Measured placement gradient: **8 → 30/30 instantly · 16 → 2/60 in 15 min · 32 →
  0/30 over two full scheduler cycles** (with 69 d-nodes holding ≥32 free cores — so it is
  backfill/priority, not capacity). Bigger footprints lose more dispatch rate than they gain cores.
- **NEVER `-pe smp 36`.** UCL's JSV silently adds `exb=true,exd=true` when the request equals a full
  node ⇒ it needs an ENTIRELY EMPTY node and starves (job `cpucurve_d` sat queued **2+ days**).
  `render_jobscript` now **raises** on `cores == 36`. 35 is clean; 8 is best.
- **Walltime is free.** An 11 h `h_rt` placed exactly as fast as a 50 min one (15/15 vs 15/15).
  Size honestly; do NOT shorten hoping for backfill.

### 11.2 The lane split — threads where LATENCY binds, cores where THROUGHPUT binds

| lane | what runs there | threads |
|---|---|---|
| **THROUGHPUT** — test flood + H1 (97 %+ of trainings) | many small jobs, wide | **1** |
| **LATENCY** — `bayes_opt`, the 55 LLM reflection chains, TPE/CMA-ES | few jobs | **8** |
| **GPU** | opportunistic only; put the longest chain on it if one is granted | pack 1 |

Measured both ways on the same hardware: 8 cores as 8× 1-thread trainings = **~104 steps/s
aggregate** vs **~35** for one 8-thread training (1 thread ~3× better for the flood), while
8 threads = **2.72×** on a single training (better for a chain). **NEVER exceed 8 threads — 16
measurably REGRESSES** (2.11×; small-matmul oversubscription).

Sequential chains run CONCURRENTLY with each other ⇒ the critical path is the **MAX** over them,
never the sum: `bayes_opt` 25 serial · TPE ~20–30 serial · CMA-ES ~4 serial *generations* ·
LLM chains 6 serial generations.

**Why this matters more than core count:** at 1 thread the campaign is latency-bound past
**~1,640 cores** (2,000 and 3,000 cores give an *identical* makespan). Threading the chains drops
`bayes_opt` from 8.9 d to ~3.3 d, moving the binding constraint back to throughput and pushing the
saturation point to **~4,460 cores**. With 8-thread chains, adding a GPU changes the makespan by
**nothing**.

```bash
python -c "from src.cluster.lanes import plan_lanes; print(plan_lanes(rung=568, cpu_cores=2000, chain_threads=8).render())"
```

### 11.3 Footprint — take what the scheduler grants, minus a reserve

`src/cluster/killswitch.py::plan_footprint(free_cores, pending_jobs)` → 90 / 70 / 50 % of FREE cores
by live pressure, then four clamps (tightest wins): the share · **`FREE_CORE_RESERVE = 1000`
(never consume the last cores — the courtesy guarantee that makes an aggressive share defensible)** ·
`ABSOLUTE_CORE_CEILING = 8192` (a runaway-bug backstop, NOT a policy limit) · any standing retreat
cap from a kill incident (always wins until a human clears it).

**Pools: use `d` + `b` only.** EXCLUDE `t` (AMD EPYC vs Intel Xeon ⇒ different oneDNN kernels ⇒
different float reduction order ⇒ breaks CRN bit-exactness; measured no faster anyway) and EXCLUDE
the ~850 idle CPU cores on GPU nodes (harvesting them blocks GPU jobs, which request `-pe smp 4`
alongside `gpu=1` — the one case where we would genuinely impair other users). Both encoded in
`lanes.EXCLUDED_CPU_POOLS`.

### 11.4 Launch-sequence deltas (fold into §2.0)

1. **Do NOT pass `--baselines`.** Under `--tiered` the launcher now resolves the frozen
   `config/campaign.yaml h1_baselines` itself (`resolve_cluster_baselines`); an explicit partial
   list is REFUSED pre-ssh. *(The old hand-typed 4-name list drifted after the canon went 4→11 and
   would have made the N6 IUT unsatisfiable + mis-sized the C0 canary — see §2's warning box.)*
2. **`bayes_opt` runs as ONE job**, not 30. Use `entry_module="src.cluster.bayes_chain"` and pass
   `est_iter_secs` (= `train_steps / measured steps_per_s`) so each job's FIRST iteration is
   deadline-checked. A `partial` status is a **normal, successful** bounded run — resubmit until it
   reports `complete`; resume is archive replay, so every candidate trains exactly once.
   *(Previously it dispatched as 30 array-of-1 jobs = 30 queue waits — tolerable on CPU, fatal on
   GPU where our jobs queue for hours.)*
3. **Confirm no open incident** before submitting: `MYRIAD_KILL_INCIDENT.json` absent from the
   archive root (the gate in `campaign.run_batch` blocks all submission while one exists).

### 11.5 ⚠ THE ONE THING THE GO CANARY MUST MEASURE

**636 cores is a LOWER BOUND.** The ~75-concurrent-job plateau is a FLOW equilibrium
(`concurrent = dispatch_rate × job_duration`; ~3.3 jobs/min measured on 20-min probe jobs).
Campaign tasks are ~25× longer, so they **accumulate** rather than churn ⇒ the free d-pool should
saturate in ~2.3 h and the realistic steady state is **~2,000–3,000 cores**. That is a MODEL, not a
multi-hour measurement.

> **ACTION: for the first ~3 hours, log concurrent jobs/cores every ~5 min and plot the
> accumulation curve. Re-forecast the achievable rung from the OBSERVED plateau, not from the
> projection.** If it plateaus near ~636 instead of climbing, the campaign is a ~23-day run (still
> inside the window) — plan the rung accordingly and say so plainly.

### 11.6 If our jobs get killed

`killswitch.classify_task_deaths()` reads the epilogue ledger and separates: deaths on **one host**
→ node failure (requeue, correct) · `secs ≈ h_rt` → walltime kill (requeue, resize) · **many deaths
× many DISTINCT hosts × short window → ADMIN KILL → RETREAT**: stop submitting, do **NOT** requeue,
halve the cap (monotone), write `MYRIAD_KILL_INCIDENT.json`, alert a human. Blind resubmission after
an administrative `qdel` is what turns "jobs killed" into "account suspended". Release is
human-in-the-loop only (`clear_incident`). **Retreat reduces FOOTPRINT, never SGE priority.**

### 11.7 Decisions required BEFORE launch

| # | decision | owner | status |
|---|---|---|---|
| 1 | **1 → 8 threads on the chain arms** (search/chain leg ONLY; the scored test leg stays 1-thread) | Tamer | ✅ **RATIFIED 2026-07-26 → registered as amendment R107**; mirrored in `config/preregistration.yaml: execution` and BOUND to `lanes.CPU_CHAIN_THREADS` by a test so it cannot drift. **NOT frozen** (standing instruction). Disclose in CH4 as an executed-config choice. |
| 2 | **CPU as a randomised device block** (+ a parity check) | **Ramin** | ⏳ open |
| 3 | *(optional)* GPU search + CPU test split | Ramin | ⏳ open — **no longer necessary** after the thread lever; keep only if a GPU is free |

*(R106 is deliberately RESERVED for Ramin's uniform-reasoning-off call, hence the jump to R107.)*

### 11.8 Refused speed-ups — do not re-propose

Each would weaken `bayes_opt`, the **H4b CONTROL the LLM must beat**, biasing the result toward our
own hypothesis: raising `n_init` 5→15 · batch/q-EI parallel BO *(note: in Snoek et al. 2012, the
registered citation — still refused)* · a reduced search `B*`. Also dead: multi-threading the TEST
flood (breaks CRN where every scored comparison lives, and is ~3× slower for aggregate throughput
anyway) · `torch.compile`/fp16/tf32/fused Adam (change numerics) · harvesting GPU-node CPU cores.

### 11.9 The advisor now PRINTS the CPU lane — read it, don't re-derive it

`python scripts/allocation_advisor.py` emits the CPU-lane recommendation alongside the GPU plan
(`allocation.advise_cpu_lane`, composing `killswitch.plan_footprint` + `lanes.plan_lanes`).
**Verified live 2026-07-26:**

```
CPU LANE: hold ~3203 cores of 4576 free {'d': 4178, 'b': 398} | -pe smp 8 -l mem=2G (NEVER smp 36 …)
  threads: flood=1 chain=8 (threads where LATENCY binds, cores where THROUGHPUT binds)
  makespan ~4.55 d at rung 568 (BINDING: throughput; more cores stop helping past ~4453)
  why: normal cluster (1721 pending, 4576 free cores) -> 70% share = 3203
```

`telemetry.Snapshot.cpu_free` carries free CORES per node type (the `qhost`+`qstat -f` join —
hostnames MUST be normalised, or the join silently matches nothing and reports every core free).
An empty section reads as **unknown**, printing a fall-back note rather than a silent zero.
⚠ `chunking()` still returns `chunk-25` under CONTENDED, but its **justification changed**: the
ticket-concentration doctrine is REFUTED (dossier §0-PRE M5) — chunk big to stay under
`max_u_jobs = 1000`, **never to buy priority**.

### 11.10 ⚠ Certifying the suite on this laptop

Running several sessions' pytest suites concurrently produces **spurious, non-reproducible
failures** — observed twice on 2026-07-26: `WinError 1455 (paging file too small)` in
`test_cluster_pack_integration`, and `CUDA error: invalid resource handle` on three
`test_agents_deep` SAC/TQC constructions. Both passed on isolated re-run. **A red suite here can be
a FALSE red: always re-run the failing test alone before treating it as a regression** — and never
the reverse (never assume green without the unpiped `PYTEST_RC`).

### 11.11 ★★★★ WHAT THE SENTINEL NOW WATCHES ON THE LANE — and what each alert means

`scripts/sentinel.py --watch outputs/campaign` runs five CPU-lane checks alongside its existing 20
(`src/cluster/campaign_health.py`). They are **independently opt-in on their inputs**, so a laptop or
pre-launch run gets none of them and raises no false alarm. **Do not build a second monitor — read
this one.**

| check | what it means when it fires | the action |
|---|---|---|
| `capacity_accumulation` **WARN** | concurrency plateaued **below 50 %** of the forecast after the ~3 h accumulation window | the forecast was a model, this is the **measurement** — re-forecast the reachable rung from the observed number and plan against it. Do NOT re-forecast while it still reads *climbing* |
| `chain_progress` **WARN / CRIT** | a **strictly serial** search chain (`bayes_opt` 25 steps, `tpe` 20) has not advanced in 14 h / 28 h | check the CHAIN job (`bayes_chain.py`), **not** the test flood — the flood looks healthy either way, and the makespan floor slips a day per day |
| `host_failure_concentration` **WARN** | a node is failing ≥50 % of its tasks (e.g. no `apptainer` → `rc=127`) | exclude it: `-l h=!<host>`, or the run keeps feeding it work. Invisible to any global failure rate |
| `rung_forecast` **INFO** | the rung reachable by the pre-registered Aug-27 stop at the **observed** rate, and how many trainings short the next rung is | planning readout only. The stop is exogenous (calendar) — **never** stop or continue because of this number |
| `determinism_homogeneity` **CRITICAL** | the scored leg is on **more than one substrate** (CPU/CUDA, or 1/8 threads) | a **validity** failure, not a slowdown: quarantine the minority substrate and re-run it. This is the one alert that must stop the lane |

**Where each input comes from** (nothing is invented; a missing input switches its check off):
capacity ← `outputs/myriad_telemetry.jsonl` (keep the advisor's `--watch` running, or the check has
nothing to read) · chain progress + elapsed ← the archive's `record.json` mtimes · host attribution ←
`<mirror>/ledger/*.epilogue.jsonl`, mirrored by the driver's own pull · the stop + the rung ladder ←
`config/preregistration.yaml` (`model_suite.exogenous_stop`, `seeds.tiers`) · **the capacity forecast
← `lane_expected_cores` in `outputs/allocation_state.json`, written whenever the advisor runs.**

> **GO-day consequence:** run `python scripts/allocation_advisor.py` at least once at launch. Until
> it does, `capacity_accumulation` can only REPORT the measurement, never judge it against a target.

### 11.12 ★★★★ SELF-HOSTING QWEN-9B ON MYRIAD (A5) — the exact procedure, and the three traps

The A5 anchor is `qwen3.5-9b` served **bf16** from its **HF-commit-pinned** weights, so the pin is
ENFORCED at serve time (`vllm serve --revision <commit>`) rather than advisory. This is the leg that
closes the experiment-layer reproducibility gap closed models cannot (Stefan #3). It is **turnkey but
not yet executed** — the only missing input is a GPU allocation.

**PICK THE POOL FIRST — this is not a preference, it is a fit constraint.**
Qwen3.5-9B in bf16 is **~18 GB of weights**, plus KV cache and activations.

| pool | GPU | verdict |
|---|---|---|
| **U / V** | 4× A100-**80G** | ✅ **USE THIS.** Fits easily, and measured **less contended for us than EF** (probe_u on `node-u00a-001` and probe_v on `node-v00a-002` both placed while the EF control sat queued through a ~2.7k-qw jam) |
| L | 4× A100-**40G** | ✅ fallback |
| **EF (default)** | 2× V100 @ **16G *or* 32G** | ⚠ **DO NOT DEFAULT HERE.** The class is not known until the job lands, and a **16 GB V100 cannot load an 18 GB model** |

`serve_qwen_selfhost.py` now PREFLIGHTS this and refuses a too-small GPU with the pool to resubmit
onto, instead of letting vLLM die on a CUDA OOM after the allocation was already granted.

**THE PROCEDURE**

```bash
# 1. LOGIN NODE (has internet) — stage the pinned revision into a SHARED HF_HOME, once (~18 GB).
export HF_HOME=$HOME/Scratch/hf
python -m scripts.serve_qwen_selfhost --prestage --leg qwen3.5-9b

# 2. Submit the serve onto an A100 pool. h_rt=48h is ample (a floor-30 leg is an inference burst).
qsub -ac allow=U -l h_rt=48:00:00 \
     -v VLLM_LEG=qwen3.5-9b,VLLM_PORT=8000,VLLM_API_KEY=<any-non-empty>,VLLM_SIF=<vllm.sif>,HF_HOME=$HOME/Scratch/hf \
     scripts/serve_qwen_jobscript.sh

# 3. Discover the endpoint the job wrote, then point the harness at it.
cat serve-endpoint-<JOB_ID>.txt          # -> http://<node>:8000/v1
export VLLM_BASE_URL=http://<node>:8000/v1  VLLM_API_KEY=<same>
python -m scripts.selfhost_author_test --served-model-name qwen3.5-9b --n 20
```

**THE THREE TRAPS, all now guarded — each one would have burned the granted allocation:**

1. **No internet on compute nodes.** `vllm serve --revision` DOWNLOADS when the revision is not
   cached, so without step 1 the job starts, stalls, and dies on a network error that blames vLLM.
   The jobscript now exports `HF_HUB_OFFLINE=1` and the serve preflights the cache, refusing early
   and printing the exact `--prestage` command. An **empty** snapshot dir does not count as staged
   (an interrupted download would otherwise re-create the silent failure).
2. **The GPU may be too small** — see the pool table above; now preflighted.
3. **`/usr/bin/apptainer` is missing on some nodes** (measured: `node-d00a-230` → `rc=127`, because
   the venv python lives INSIDE the `.sif`). The training jobscript has guarded this since 2026-07-10;
   the SERVE jobscript now does too, and also checks the `.sif` actually exists.

**MEASURE ITS RELIABILITY FRESH — do not inherit the API number.** The OpenRouter leg is **fp8 via
SiliconFlow**; this anchor is **bf16**. Different served variant ⇒ different behaviour, so run
`selfhost_author_test.py` and report what IT measures. Useful comparators from 2026-07-26: the fp8
API leg scores **1.00** on the registered format-compliance gate but only **~25 %** of its rewards
survive 12 contract steps — so report the **executable** yield for the self-host too, not the gate
number.

**Scope note (deliberate):** the self-host is a reproducibility DEMONSTRATION, not an 11th
full-loop leg. It stays off the R101 lockstep seed ladder, so it costs no confirmatory power and the
freeze gate's leg-roster cross-check (n=10) stays green.
