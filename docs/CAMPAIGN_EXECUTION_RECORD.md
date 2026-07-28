# CAMPAIGN EXECUTION RECORD — the confirmatory run

**Purpose.** The single write-up-ready account of what was run, what is running, and what will run.
Every number here was MEASURED on the live system and is attributed to its source; nothing is
inferred silently. Where a fact is inferred rather than observed, it says so. Ops chronology lives in
`CHANGELOG.md` (items ①–⑳ of the 2026-07-28 block); this document is the narrative the dissertation
draws on.

**Status at 2026-07-28 11:41 UTC:** running, T+10.6 h, 12/12 lines alive, freeze intact, suite green.
No relaunch performed and none warranted (§8). **★ THE CONFIRMATORY H2 HEADLINE IS NOW LIVE** — the
canary gate cleared at 11:39:43 UTC (`ok: True, completed: 90`), the C0 analysis-smoke gate passed, and
`claude-opus-5` began authoring the five core LLM arms at 11:40 UTC.

---

## 1. WHAT IS BEING RUN — the frozen object

| property | value | how verified |
|---|---|---|
| pre-registration hash | `4f90ecc47cc6a779d63b74fdaa9667f967473365863fb615401694131ca136fd` | `freeze.canonical_hash()` re-derived live |
| freeze tag | `prereg-v2.0` → commit `0f6221b`; seal commit `ce27dfc` | git |
| executing code | `deployed-archive:ce27dfc5fb7503e8673b544e5498cd20ce34de64` | stamped in EVERY record's `env.json` |
| gold panel | `returns_panel` sha256 `7cf5d98843c53cd6…` | stamped in every record; matches the frozen manifest |
| arms (core) | 9 — `distributional`, `scalar`, `placebo`, `scalar_cvar5`, `placebo_shuffled`, `random_search`, `bayes_opt`, `cma_es`, `tpe` | `config/campaign.yaml` |
| H1 baselines | 11 | `config/campaign.yaml` |
| candidates per arm | **30** — `config/campaign.yaml`. The "6 generations of 5" split is EMPIRICALLY observed (g0…g5 present in the live archive), not read from a top-level config key |
| seed ladder (R101) | 30 → 100 → 189 → 279 → 340 → 403 → **568** | `config/campaign.yaml` |
| replication legs | 10 models × 5 LLM arms | live archive roots |

**Substrate (the determinism envelope), read from a live scored record:**

```
cpu          Intel(R) Xeon(R) Gold 6240 @ 2.60GHz, 36 logical cores/node
threads      OMP_NUM_THREADS=1, torch num_threads=1      (SCORED leg)
cuda         cuda_available = False
python       3.11.15   numpy 1.26.4
schema       capture_env/4
```

The search/chain leg runs 8 threads (R107); the **scored** leg is uniformly 1 thread. That asymmetry
is deliberate and is why CRN pairing is safe: every scored comparison unit shares one thread regime.

**Total work at the deepest rung** — 71 scored units per seed:
core (9 arms + 11 baselines) = 20, legs (10 × 5) = 50, h3 single-shot = 1.

> **40,328 scored units = 326,254 core-hours** at the measured 8.09 h per scored training.

---

## 2. TIMELINE — WHAT HAPPENED (past)

**2026-07-27 (pre-launch).** A launch-gate audit caught **eleven defects**, four individually fatal —
the documented launch command would have run 2 arms with a stub author; `autosize_h_rt` granted 6 h to
a training needing 8.55 h; `--gold-dir` pointed at an empty directory; and eight foreign pre-campaign
records sat in the confirmatory search root where archive-truth resume would have adopted them as
generation zero. All closed and locked by regression tests before GO. (CHANGELOG `[2026-07-27d]`.)

**00:05 UTC — FREEZE.** Hash re-derived and verified; tag `prereg-v2.0`; sealed at `ce27dfc`.

**01:08 UTC — LAUNCH** of 12 supervised lines (core + h3 + 10 legs), staggered to 02:12. Deploy
proven **630/630 files byte-identical** to the committed blobs at the frozen commit.

**~01:00–02:00 — THE KILL INCIDENT (the one materially consequential event).** A `qdel` I issued
during cleanup produced 24 task deaths across 23 hosts, which the killswitch correctly classified as
an admin-kill and used to BLOCK submission. Consequences, measured:

* **128 of the generation-0 `cluster training failed` rows are jobs that NEVER RAN.** This is why g0
  yield is uniformly poor across *every* model (nemotron 0/15, qwen3.6-27b 0/16, gpt-5.6-luna 1/16,
  sonnet-5 3/18, deepseek 7/27, gemini 13/29) and then jumps to ~56–62 % at g1 for all of them.
* Five leg lines exited permanently at the C3 review gate (a gate stop returns 0, which the
  supervisor could not distinguish from "line complete"). `scripts/mode_d_watchdog.ps1` was written
  during the launch to restore any dead line; all 12 have stayed up since.

**02:00 → 11:30 — steady execution.** 580 records, 12/12 lines alive continuously, spend $7.19.

**10:21 → 11:39 UTC — THE CANARY STALL, and its resolution.** The canary reached 88/90 at 10:21 and
did not advance for ~78 min. Its cluster work was already COMPLETE (23 epilogue `rc=0`, 0 jobs
remaining, final part `{"n": 4, "ok": 4}` after `step 400000/400000 … rate 11.1 steps/s`), so the two
outstanding units were a RECONCILIATION problem, not a compute one — the blocker was transport
(§3.1). **It self-healed:** two consecutive pull failures, then success.

**11:39:43 UTC — THE CANARY GATE CLEARED.** `[c1_canary] batch complete: {'ok': True, 'completed':
90}`, immediately followed by `[C0] analysis-smoke: all canary records parse + full seed …`. The C0
gate passed.

**11:40 UTC — ★ THE CONFIRMATORY H2 HEADLINE BEGAN.** `spend_ledger_c1.jsonl` was created and
`claude-opus-5` began authoring the five core LLM arms (first 2 calls, $0.1397). Until this moment the
confirmatory arms had produced NOTHING — which is precisely why the kill incident (§2) could not have
touched them.

> ⚠ **Correction of record.** An earlier version of this document stated the gate cleared at 11:21 on
> the strength of my own watcher. That was wrong twice over: the driver log is LOCAL time (BST =
> UTC+1), so `11:21` was `10:21 UTC`; and the watcher coerced a `pull_outage` heartbeat's
> `pending: None` to `0` and announced a false reconciliation. The gate actually cleared at 11:39:43
> UTC, verified three independent ways (driver log `ok: True, completed: 90`; the C0 analysis-smoke
> line; the c1 spend ledger appearing). Recorded in CHANGELOG item ㉑.

---

## 3. WHAT IS RUNNING NOW

**Snapshot at 2026-07-28 11:41 UTC** (these counters move continuously; the live view comes from
`scripts/sentinel.py` and the watch instruments, not from this table):

| | |
|---|---|
| lines | 12/12 alive since launch |
| records | **586** — 330 scored, 41 core search, 208 leg search, 7 frozen winners |
| cores held | ~1,400 (the rung-30 transient; see §4 for why this is correct, not a shortfall) |
| spend | **$7.34** of the $30 advisory ceiling ($4.70 Anthropic + the first Opus core calls) |
| Opus core authoring | **LIVE** — `claude-opus-5`, 2 calls, $0.1397 |
| failure counter | 60 / 240 fatal bound (self-healing; resets on success) |
| freeze | intact — `design_drift OK` every poll |
| test suite | `PYTEST_RC=0`, zero FAILED/ERROR |

**Phase.** The core line is running its 4 derivative-free comparator arms (`random_search` 25 records,
`tpe` 7, `bayes_opt` 6, `cma_es` 1), all 11 H1 baselines, and — **since 11:40 UTC — the five core LLM
arms under `claude-opus-5`**, i.e. the confirmatory H2 contrast is now authoring. The 10 legs work
through their 5 arms **sequentially**: `scalar` is 9–15 records deep and all 7 frozen winners so far
are `scalar`, with the other four arms behind it.

### 3.1 THE TRANSPORT CONSTRAINT — it blocked the gate for 78 min, then self-healed

Measured from the core driver log:

```
[c1_canary] pull failed: ssh ... "find .../outputs -path '*/_rejects/*.json' -type f"
                          timed out after 300 seconds
[c1_canary] pull failed: ['tar', '-xf', '-'] timed out after 3600.0 seconds
[c1_random_search_search] queue op failed (8 consecutive, 56 min): 'qstat -r' timed out
```

Twelve supervised lines with ~5 batch threads each produce up to ~60 concurrent ssh sessions against
one login node. **Two of the three failing operations scale with the archive** — the `find` over the
whole outputs tree and the `tar` of the pull — so this worsens as the campaign grows rather than
settling.

**ssh multiplexing is NOT available** (tested, not assumed): on OpenSSH_10.2p1 the master socket is
created but the session fails with `mux_client_request_session: read from master failed: Connection
reset by peer`. The remaining levers are lower polling frequency or fewer concurrent lines, both of
which require a line restart — now CHEAP, because hundreds of completed trainings mean re-authoring
replays from the archive rather than re-billing Opus.

**The judgement call, and its outcome.** A 12-line restart with slower polling was the available
remedy, and it had become CHEAP (re-authoring now replays from the archive). It was deliberately NOT
taken: the campaign was still progressing, the counter self-heals on success, and a restart injects a
burst of startup probes — the exact load that was failing. **The gate then cleared on its own at
11:39:43 UTC**, vindicating the hold. The lesson for the write-up is that the driver's retry
discipline absorbed a 78-minute transport outage on the critical path without intervention or data
loss.

⚠ **The constraint has NOT gone away.** Two of the three failing operations scale with archive size,
so it will recur and worsen as the campaign grows toward 40,328 units. It is bounded by the driver's
240-consecutive-failure / 12-hour limits (currently 60/240), and the remedy remains available.

---

### 3.2 LLM SPEND — measured and projected (report this prominently; Raad/Stefan point 2)

| | |
|---|---|
| spend to date | **$7.69** |
| Opus core authoring (the confirmatory arm) | 6 calls, $0.4931 — **mean $0.0822/call** |
| projection for the core line | 5 LLM arms × 30 candidates = 150 calls ≈ **$12.33** |
| **projected campaign total** | **≈ $19.53** against the **$30** advisory ceiling |
| headroom | ≈ $10.47 |

The ceiling is **advisory, not enforcing** (R83): `src/llm/spend_ledger.py` captures per-call cost and
warns at 80 %/100 % but **never refuses a call** — the exogenous stops that actually protect the design
are the seed-rung rule and the leg calendar gate. The write-up must not claim a hard spend gate the
code does not implement.

*Caveat on the projection:* it assumes 150 authoring calls for the core line. The observed per-leg
rate is ~15–20 calls per arm mid-run, so the true total will land near this figure but should be
re-read from the ledger at write-up time rather than quoted from here.

---

## 4. WHAT WILL HAPPEN (future) — the forecast and why

**The makespan is `max(serial chain, fill)`.**

* **Serial-chain floor:** `bayes_opt` runs **25 sequential** GP-EI steps at a measured **3.59 h**
  each = **89.8 h ≈ 3.7 days**. A serial chain is immune to additional cores by construction. `tpe`
  is 20 × 3.60 h ≈ 3.0 d and `cma_es` 4 × 3.76 h ≈ 0.6 d, both running in parallel.
* **Fill time** depends only on cores held:

| cores | fill | makespan |
|---|---|---|
| 1,400 (rung-30 transient) | 9.7 d | 9.7 d |
| **4,000** = pack 4 × the 1,000-job cap | 3.4 d | **3.7 d — the chain binds** |
| 8,000 | 1.7 d | 3.7 d — **no gain** |

> **The current configuration is exactly right.** pack 4 × 1,000 jobs = 4,000 cores, which is
> precisely where fill stops being the constraint. Raising pack buys nothing.

**Why utilisation is low now and will self-correct.** At 71 units/seed, the rung 30→100 step alone
releases 70 × 71 = **4,970 units = 1,243 jobs**, beyond the 1,000-job cap. Every rung from 100 upward
saturates on its own. Today's ~1,400 cores is the rung-30 transient plus incomplete leg searches, not
a capacity limit — measured directly: only **181 tasks pending** across 33 running batches with 55
already queued, against a 1,000-job cap we are using 277 of.

**Expected sequence from here:** core LLM arms author → their winners freeze → the ladder advances
past rung 30 → utilisation rises toward ~1,000 jobs / ~4,000 cores → the fill completes in ~3.4 d →
the campaign is chain-bound, finishing as `bayes_opt`'s 25th step lands. **Idle capacity while waiting
on the chain is expected and costs nothing.** Exogenous stop: 2026-08-27, i.e. ~29.6 d available
against a ~4–5 d landing.

---

## 5. EXECUTION-QUALITY EVIDENCE (for CH4 / reproducibility)

Every item below is a measurement on live campaign data, not an assertion.

**Determinism envelope.** All scored records are `dev=cpu` on **ONE substrate**
(`cpu=Xeon Gold 6240 | omp=1 | torch_threads=1 | cuda=False`). Verified across 248 records at the
time of audit. Because `capture_env/4` records `cpu.model_name`, this is a *proof* of CPU-model
homogeneity, not an assumption — and it is the property CRN paired-contrast bit-exactness rests on.

⚠ **`-ac allow=d` does NOT pin a CPU model.** Measured: the SEARCH leg held 108 records on a Gold
6240 and **1 on a Gold 6140** — different microarchitectures. The scored leg is clean, and a new
`check_substrate_fields` monitor now raises CRITICAL on any scored-leg mix within one poll. Myriad
exposes no schedulable CPU-model resource (`qhost` cannot even distinguish them: both 36-core /
2-socket), so detection-and-remediate is the only available control.

**Provenance.** Every record stamps the frozen seal commit and the gold-panel sha256. No record older
than the 01:08 launch exists in any live root (checked explicitly) — nothing foreign was adopted.

**Scored-result plausibility** (effect-blind: only baseline comparators had scored records, so no arm
contrast was computable and no ranking was produced):

| quantity | observed | verdict |
|---|---|---|
| test window | **1571 steps on all 268** | identical → paired contrasts valid |
| `test_sharpe` | −0.910 … +1.421 (median −0.243), all finite | plausible band |
| `test_cvar05` | −0.0344 … −0.0161, **all ≤ 0** | correct sign for a loss quantile |
| daily σ | 0.0075–0.0144 → **~12–23 % annualised** | textbook equity-portfolio vol |
| max daily move | 4.5 %–18.2 % | consistent with the 2020–26 window |
| degenerate (all-cash) policies | **0** | none collapsed |
| turnover | 0.0000–1.0000, **0 violations** | exactly the long-only simplex bound |
| effective N | 1.000–30.859 (median 4.03), **0 violations** | within [1, 31] |
| **portfolio weights** | **15,312 snapshots: min weight 0.000e+00, worst \|Σw−1\| 0.000e+00** | the simplex holds EXACTLY |

**Compute cost of rejected candidates:** 73 rejected/aborted tasks = 1.50 core-hours against 314
completed trainings = 1,626 core-hours → **0.092 % of all compute.** A reject is caught by the
sandbox in seconds, before training starts.

---

## 6. FINDINGS THAT BELONG IN THE WRITE-UP

**(a) Reflection depth drives state-contract violation — the mechanism finding.**
The frozen system prompt states the contract explicitly:
`info["reward_state"] carries YOUR state across steps (or None at reset)`, and the validation fixture
mirrors production reset exactly. Node-side reject class by generation:

| gen | dominant reject class |
|---|---|
| g0 | `no reward fn` 10, `UnboundLocal` 9 — empty/truncated completions |
| g1 | **NoneType/state 7 of 8** |
| g2 | NoneType 5 |
| g3 | NoneType 3 |
| g4 | **NoneType 4 of 5** |
| g5 | bad-return 3 |

As the Eureka loop reflects, models write progressively more **stateful** rewards, and stateful code
trips the documented `None`-at-reset case on the first call. By g4/g5 essentially every candidate
fails this way. **Every frozen winner therefore comes from g1–g3** (`scalar-g1-c0`, `g2-c4`, `g3-c1`,
`g3-c2`): the search converges by g3 and the last two generations contribute nothing. This is a
concrete, quantified failure mode of LLM-in-the-loop reward design — the reflection mechanism itself
pushes models into a code pattern they handle unreliably. **It must not be "fixed":** the prompt is
freeze-bound and softening it would erase the signal being measured.

**(b) Ratio-form hand-designed baselines are numerically fragile — one cause, two symptoms.**
All scored-leg fallback contamination is confined to exactly two of eleven H1 baselines:

| arm | contaminated scored records | worst | reward `raw_rms` |
|---|---|---|---|
| `baseline_differential_sharpe` | 5/30 (16.7 %) | 1 step | 16,324 |
| `baseline_differential_downside_ratio` | 4/30 (13.3 %) | 2 steps | 28,774 |
| the other **9 of 11** | **0** | — | 0.015–2.33 |

Both are differential/ratio forms whose denominator approaches zero, which simultaneously (i) inflates
reward magnitude by 4–5 orders and (ii) occasionally raises, triggering the R66 safe-default. Worst
case is 2 steps in 400,000 (0.0005 %) — negligible in magnitude, valuable as explanation. It converts
the P5 reward-scale spread from a hand-wave into a mechanism, and it is a quantified statement about
the numerical robustness of the very comparators H1 tests against.

**(c) Per-model authoring reliability — the capability gradient, observed live.**
Node-side reject census (n=40 campaign candidates at snapshot): 27 reward crashed during validation ·
10 source defines no `reward` · 3 invalid return. Crash exceptions: TypeError 12, AttributeError 7,
NameError 3, UnboundLocalError 2, ValueError 2, IndexError 1. `qwen3.5-9b` sits at the bottom (1
record across 5 arms; 36 rejects) exactly as its pre-measured ~17 % gate-pass predicted — the
numeracy-bottleneck thesis in action, and a registered FINDING rather than a fault.

**(d) The campaign is design-paced, not resource-limited.** Five capacity levers were measured and
all are already optimal or immaterial: tmpfs (nodes advertise 1.1–1.3 TB, we stage 71 MB) · `-p -100`
(all queued jobs sit at identical normalised priority ~1.809) · `-ac allow=d` (we use 14 % of a class
that is 81 % of the cluster) · job cap (277 of 1,000) · SGE reservation (**already enabled** by
UCL's JSV — `qalter -R y` is refused as a modification). Recorded so the finding is not re-chased.

---

## 7. DISCLOSURES AND LIMITATIONS (write these into CH4/CH7)

1. **The kill incident contaminated generation 0.** 128 g0 rows are jobs that never ran. The
   per-model authoring-reliability table **must exclude them** or it will understate every model
   (§9). The confirmatory headline is unaffected — the core LLM arms had authored nothing at the time.
2. **Search depth is effectively 4 generations, not 6**, for most legs, because g4/g5 candidates fail
   the state contract. Report the effective candidate count, not the registered 30.
3. **Reward-scale spread across H1 baselines is 4.4 × 10⁵**, driven by the two ratio-form arms. This
   is a latent entropy-regularisation difference (the P5 confound). H1 is an intersection-union test,
   so the binding comparator is the STRONGEST baseline — a poorly-scaled baseline that underperforms
   does not flatter the claim.
4. **A microarchitecture mix (Gold 6240/6140) exists on the SEARCH leg.** Scored leg is clean and
   monitored. Search-leg substrate affects only WHICH candidate is selected, never a measured
   quantity (the R107/R108 argument).
5. **B\* and σ_D were calibrated on GPU/TF32; the campaign executes on CPU/fp32.** Pre-existing,
   already in the evidence ledger; the decisions do not move but the unbroken-envelope CLAIM does.
6. **No OpenTimestamps proof** — the client crashes on Windows. The external anchor is the signed
   commit + tag pushed to origin. The write-up must not imply otherwise.
7. **`train_safe_default_count` does not gate winner selection** (§10).

---

## 8. WHY NO RELAUNCH WAS PERFORMED

Relaunch permission was granted and the case was examined seriously. **The decisive argument:** at the
moment of the incident the five CORE LLM arms — the confirmatory H2 headline — had authored **zero**
candidates. They sat behind the canary, which cleared only at 11:39:43 UTC. **The headline is therefore
pristine and untouched.** The legs are replication (secondary); their winners came from clean
post-incident generations g1–g3; and the incident-affected rows are analytically identifiable (§9).
A relaunch would discard ~10 h and ~$7, re-run the same models under the same frozen prompt, and
reproduce the same failure structure — while gaining nothing the analysis cannot already separate.

One hypothesised defect was investigated and **refuted**: g4/g5 showing 0/5 with `rounds=0` batches
looked like a transport failure silently voiding whole generations. The driver log disproves it —
`ERROR [leg8_leg_sonnet_5_scalar_g4] 5 permanent node reject(s) abandoned` — the specs were built,
the jobs ran, and the sandbox rejected all five permanently, so the driver correctly declined to
re-ship invalid source.

---

## 9. ANALYSIS-TIME OBLIGATIONS (do not lose these)

1. **Exclude g0 never-ran rows** from every authoring-reliability denominator. Discriminator:
   generation 0 **and** error `cluster training failed` **and** absent from the node logs.
2. **Mine the node logs for true reject reasons.** The ledger row degrades to a generic
   `cluster training failed` because the node's reject marker is mirrored back by a LATER pull (the
   P9 race). The node logs are the authoritative source and are harvested every 15 min into
   `docs/evidence/node_authoring_rejects_latest.jsonl` — **Scratch is purge-eligible, so this must
   not wait until write-up.**
3. **Re-run the substrate census over the FULL archive** at analysis time. A second distinct
   substrate signature is the tripwire and must be investigated, never averaged over.
4. **Report effective search depth and effective candidate count**, not the registered figures.
5. **Report wall-clock compute** (Okhrati docks for its absence): measured 8.09 h per scored
   training, 3.59 h per chain step, 326,254 core-hours for the full ladder.

---

## 10. OPEN DECISION FOR TAMER

**Winner-eligibility floor.** `train_safe_default_count` is archived and reported but **never gates
selection** — the winner is `max(val_fitness)`. A candidate whose authored reward raised on 50 %+ of
steps can therefore be frozen, and the sealed leg would re-train that same reward and inherit the
contamination. Measured: of 136 search candidates, 127 clean, 4 at 0.1–1 %, and **2 SEVERE**
(`qwen3.6-27b/scalar-g1-c4` 53.7 %, `qwen3.5-9b/distributional-g1-c2` 50.0 %), both in weak
open-weight legs.

**Current exposure is zero** — every one of the 7 frozen winners traces to a source candidate with
**0/400,000** fallback, and `check_winner_execution_quality` now verifies this every poll.

**Recommendation: detection over amendment.** A dated amendment adding an effect-blind execution floor
is defensible, but detection-plus-remediation achieves the same outcome (re-run the offending unit)
without a post-data protocol change and without inviting the "you changed the rules mid-run"
objection. The pre-registration is silent on a threshold; that silence is now a *documented* gap
rather than an unnoticed one.
