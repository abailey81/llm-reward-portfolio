# CAMPAIGN EXECUTION RECORD — the confirmatory run

**Purpose.** The single write-up-ready account of what was run, what is running, and what will run.
Every number here was MEASURED on the live system and is attributed to its source; nothing is
inferred silently. Where a fact is inferred rather than observed, it says so. Ops chronology lives in
`CHANGELOG.md` (items ①–⑳ of the 2026-07-28 block); this document is the narrative the dissertation
draws on.

**Status at 2026-07-28 13:00 UTC: RUN 1 HALTED at T+11.9 h. A defect in the driver invalidated the
LLM search on every line.** All 12 lines were stopped deliberately at ~12:35 UTC. The freeze is
INTACT and unaffected — the defect is in driver transport/bookkeeping code, not in the frozen design
(`freeze.py --check` RC=0, canonical hash still `4f90ecc47cc6a779…`). §11 is the incident account;
§12 is the relaunch plan. Everything below §11 that describes RUN 1 as healthy is retained as the
*dated* record of what was believed at the time, with the retractions marked inline.

> **★★ RUN 3 LAUNCHED 2026-07-28 15:19:27 UTC — the run of record.** Roots
> `outputs/campaign_cluster_run3` + `~/Scratch/llmrp3`, under the **v2.1** freeze
> `3ca6f01ab7724d47…` (tag `prereg-v2.1`, seal commit `b9c2be5`). Gates: full suite **2,866 passed /
> 3 skipped / 0 failed** with the source-tree hash recorded IDENTICAL before and after ·
> `freeze --check` **RC=0, recorded hash MATCHES** · preflight **14/14, VERDICT GO** · `--dry-run`
> **RC=0 on all five** line invocations (core, h3, three legs) · every one of the 16 live processes
> verified on the RUN 3 roots, **0 on the old ones**. Verified in the first two minutes: remote tree
> created under `/home/ucestes/Scratch/llmrp3`, gold sha256 re-verified against the frozen manifest,
> `h_rt=15:0:0`, the C0 canary shield running, and arrays submitting (`c1_tpe_startup` 10,
> `c1_bayes_opt_startup` 5, `c1_cma_es_c0` 1). **~970 cores were freed for it** by draining 118
> campaign jobs from the two discarded runs — the 20 `p6cpu` B\*-ladder jobs that feed figure F11
> were identified and deliberately PRESERVED. Guards armed on the new root: collision guard
> (`0 spurious`) + transport-degradation guard. **STOP LEVER:**
> `outputs\campaign_cluster_run3\STOP_CAMPAIGN`.
>
> ⛔ **RUN 2 (below) is SUPERSEDED** — halted at T+1.3 h to register R115; it ran under v2.0 and
> produced zero records. RUN 1 is invalidated (§11). Both trees are preserved as evidence.

> **RUN 2 LAUNCHED 2026-07-28 12:59:01 UTC** into fresh roots (`outputs/campaign_cluster_run2`,
> `~/Scratch/llmrp2`) after the 20-item pre-relaunch gate passed (§12.3). Verified in the first
> two minutes: all 12 supervised lines up, the core driver carrying BOTH new roots, the remote tree
> created under `/home/ucestes/Scratch/llmrp2`, **the licensed gold re-verified sha256-equal to the
> frozen manifest**, `h_rt=15:0:0`, and the C0 canary shield running so no frontier spend is at risk
> until the production path is proven. RUN 1's residual jobs drain alongside, fenced by the disjoint
> roots. A dedicated collision guard now asserts every `permanent_node_reject` traces to its own
> sub-root and is reporting `0 spurious`.

> **The one-paragraph version.** `driver.run_batch` decided which candidates were permanently
> rejected with a MIRROR-WIDE lookup over the single output tree that all twelve supervised lines
> share, keyed on the bare candidate id (`scalar-g1-c0`) that every line reuses. So one line's reject
> marker silently condemned every other line's identically-named candidate — never submitting it,
> never judging it, and ledgering it so no resume would retry it. Measured: **439 of 498 abandonments
> (88 %) were spurious**, **402 of them caused by `qwen3.5-9b` alone** — the deliberately weakest
> model in the suite — and **36 of 36 on the confirmatory `claude-opus-5` core line**. The search was
> not merely slowed; on most lines it was sterilised.

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

### 3.1 THE TRANSPORT CONSTRAINT — ⚠ THE DIAGNOSIS BELOW IS WRONG; SEE §11.1

> ⛔ **RETRACTED 2026-07-28 12:15 UTC.** The claim in this subsection that "two of the three failing
> operations scale with the archive so this worsens as the campaign grows" is **empirically false**.
> Measured on the live cluster: the `find` over the whole outputs tree returns 703 records in
> **0.046 s**, and `qstat -r` completes in **2 s** (and in ~2.5 s even at 16 concurrent). Neither is
> archive-bound at any plausible scale. The real cause was a **resource leak in our own driver**
> (§11.1), and the real scaling variable was our own connection fan-out, not the archive. The text
> below is kept as the dated record of a wrong diagnosis that a later session must not build on.

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

#### THE ANTHROPIC KEY — the binding balance, and why it is the one to watch

The $30 figure is a TOTAL-spend ceiling across all providers. The number that can actually stop the
campaign is the **Anthropic key balance**, because FOUR lines bill it and one of them is the
confirmatory arm:

| line | calls | spent | arms done | projected at 5 arms |
|---|---|---|---|---|
| `c1` — **Opus, CORE confirmatory** | 18 | $1.47 | authoring now | **~$12.3** (150 calls × $0.0814) |
| `h3ss` — Opus, H3 single-shot | 30 | $2.58 | appears complete | ~$2.6 |
| `leg8` — sonnet-5 | 90 | $1.61 | ~1 of 5 | **~$8** |
| `leg5` — haiku-4.5 | 90 | $0.51 | ~1 of 5 | ~$2.5 |
| | | **$6.17 now** | | **≈ $25.4 projected** |

**BALANCE: $34.84** (confirmed by Tamer, 2026-07-28), against a projected **≈ $25.4**. Headroom
**≈ $9.4**, and Tamer monitors and tops up. **This is comfortable — it is a WATCH item, not a risk.**

**Why it is nonetheless the balance to watch.** If this key were ever to run dry, the line that stops
is `c1` — the H2 headline, which began only at 11:40 UTC. Everything else running is replication or
comparator work. And it would fail SILENTLY by design: R83's ledger warns at 80 %/100 % but **never
refuses a call**, so no hard gate would catch it. The OpenRouter key carries no such exposure (all
six of those legs together are ~$2.50).

**★ WHY LLM SPEND CANNOT RUN AWAY — state this in the write-up.** Spend is bounded by the SEARCH
phase, **not** by the seed ladder. Authoring happens once per arm (30 candidates); the rungs
100 → 568 then re-test the ALREADY-FROZEN winner at more seeds with **zero new LLM calls**. So cost
is front-loaded: once every arm has a frozen winner, LLM spend goes to **zero** and only compute
continues for the remaining ~3–4 days. Verified burn shape: `c1` went 18 → 39 calls in 15 min
(~1.4 calls/min, $0.0844/call), i.e. ~79 min and ~$9.4 remaining to reach ~150 calls ≈ $12.66 — on
projection. `h3ss` has been idle 637 min (complete). This is the honest cost band Raad/Stefan asked
to see reported prominently, and it compares favourably with the lineage (RD-Agent <$10,
AI-Scientist <$15/paper).

**Correction to my own earlier figure:** I first projected "≈ $19.53 total", which UNDERSTATED the
Anthropic exposure because it counted only the core line's Opus cost and omitted the four remaining
arms on each of the two Anthropic-billed replication legs (`leg8` sonnet-5, `leg5` haiku-4.5). The
table above is the corrected basis. Note the leg figures are extrapolated from ~1 arm each and carry
the widest uncertainty of anything in this document — re-read them from the ledger rather than
trusting the extrapolation.

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

> ⛔ **(a) AND (c) ARE RETRACTED (2026-07-28 13:00 UTC) — see §11.4.** Both rest on
> reject-counts-by-generation, and the collision defect made those counts an artefact: from g3
> onward essentially every line's candidates were condemned by `qwen3.5-9b`'s markers rather than
> judged on their own merits, and `qwen3.5-9b` reaches the deep generations FASTEST precisely
> because its own candidates fail fast. The apparent "reflection depth drives failure" gradient is
> therefore confounded with "the weakest model gets to g4/g5 first and poisons everyone". The text
> is preserved verbatim below as the dated record of a claim I made and withdrew; it must NOT enter
> the dissertation unless it reproduces on RUN 2 data.

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
   `docs/evidence/node_authoring_rejects_<run-root>.jsonl` (RUN 1's is the committed
   `…_latest.jsonl`; the harvester became root-scoped on 2026-07-28 so RUN 2 cannot overwrite it)
   — **Scratch is purge-eligible, so this must
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

---

## 11. RUN 1 POST-MORTEM — the two defects, both in OUR code, both found by measurement

Session of 2026-07-28 11:50–13:00 UTC. Every number below was measured on the live system before any
change was made; each fix carries a regression test PROVEN to fail against the pre-fix code.

### 11.1 The transport degradation was a resource leak in our own driver, not the cluster

**What was believed** (§3.1): a cluster/transport constraint that "scales with the archive" and had
"self-healed".

**What was measured.** The failing operations are not archive-bound at all — the `find` over the
entire remote outputs tree returns 703 records in **0.046 s**, and `qstat -r` completes in **2 s**
(≈2.5 s even at 16 concurrent). Yet the driver logs carried **1,904 genuine 300-second timeouts**,
and the failure rate was climbing monotonically:

| hour (BST) | 02 | 04 | 07 | 09 | 11 | 12 |
|---|---|---|---|---|---|---|
| timeout rate | 5.2 % | 6.8 % | 10.8 % | 33.6 % | 39.4 % | **55.3 %** |
| good poll cycles / h | 962 | 1,446 | 1,202 | 444 | 377 | **224** |

**The cause.** `poll._default_fetch` (and its twin `submit.push_batch`) placed `proc.wait()` AFTER
the `try/finally`, so any exception on the consuming side skipped it and left the `ssh` child running
forever. A stalled pull raises `TimeoutExpired` by construction, so the leak fired on exactly the path
that mattered. Found live: **13 leaked children — 8 of them pulls still running 1.1–6.7 h past their
own 3600 s timeout** — each holding an established session (and a remote `tar`) on the SHARED UCL
login node. Login-node session pressure is what makes the NEXT pull stall, so this is a positive
feedback loop: precisely why the rate rose monotonically, and why nothing in the environment needed to
change for it to worsen.

**Proof of causation, not correlation.** Reaping the 13 leaked children and changing nothing else took
the failure rate from **53.3 % to 16.3 % in the very next 10-minute bucket**, and the driver's worst
failure counter from **62/240 to 36/240**.

**Fixed** in `submit.reap` plus both call sites; four regression tests, every one verified to FAIL
against the pre-fix code.

**Two methodological notes worth keeping.** (i) My first three probes measured the WRONG ssh client —
Git Bash's OpenSSH 10.2p1 rather than the `C:\Windows\System32\OpenSSH` 9.5p2 that Python actually
resolves — so they characterised a real but irrelevant phenomenon (MaxStartups random early drop:
~29 % of connections refused at fan-out 48, but refused in 0.1 s and therefore harmless).
(ii) The obvious client-side remedy, `ConnectionAttempts` / `ConnectTimeout`, was A/B-tested over
three paired rounds BEFORE being applied and is **REFUTED** — 8/72 failures in the control against
9/72 in the treatment. It was not adopted. Both are recorded because the tempting fix was the wrong
one, and because the same session had already retracted one diagnosis for exactly this reason.

### 11.2 ★ THE RUN-INVALIDATING DEFECT — one line's reject marker condemned every other line's candidate

**The mechanism.** `driver.run_batch` resolved permanent rejects with
`permanent_reject_ids(local_archive_root)`. `local_archive_root` is the ONE tree all twelve supervised
lines share (`outputs/campaign_cluster` — it is where `driver_status/` and `ledger/` live). That
function walks `**/_rejects/*.json` and keys on the **bare candidate id** (`scalar-g1-c0`), and
**every line reuses that id scheme**. So a marker written by any line condemned the identically-named
candidate of all eleven others — without submitting it, without judging it, and ledgered as permanent
so that no resume would ever retry it.

**This is the same defect class the 2026-07-19 35-agent audit called "CONFIRMED critical" and fixed
for `pending_specs`**, where completion truth was scoped to each spec's own archive sub-root precisely
to stop run-id collisions from fabricating an H3 null. Reject truth was left mirror-wide. The
asymmetry between the two is the whole bug.

**Measured damage, whole archive, before any change:**

| | abandonments | own-marker (legitimate) | FOREIGN marker (spurious) |
|---|---|---|---|
| **core line (`claude-opus-5`, the confirmatory H2 headline)** | 36 | **0** | **36 (100 %)** |
| h3 single-shot | 4 | 0 | 4 |
| the 10 replication legs | 458 | 59 | 399 |
| **TOTAL** | **498** | **59** | **439 (88 %)** |

Marker owners responsible for the spurious kills: **`qwen3.5-9b` 402**, `qwen3.6-27b` 47,
`haiku-4.5` 16, `gpt-5.6-luna` 8, `deepseek-v4-pro` 8, `nemotron-3-super` 7, `glm-5.2` 6.

**The irony that makes this a write-up point.** `qwen3.5-9b` is in the suite *deliberately*, as the
capability-gradient bottom anchor; its ~17 % authoring gate-pass is a registered FINDING, not a fault.
Its 47 entirely legitimate rejects sterilised the search of all eleven other lines, including the
frontier confirmatory model. A design feature became, through one unscoped lookup, a global failure.

**Fixed** by `poll.permanently_rejected_specs`, which scopes reject truth through the same
`spec_local_root` helper that completion truth now uses, so the two can never again disagree about
which archive a spec belongs to. Two regression tests, both verified to fail pre-fix, assert the
collision in both directions: a foreign marker must not condemn, an own marker still must.

### 11.3 Why RUN 1 cannot be salvaged for the LLM arms

1. **The confirmatory headline authored nothing usable.** Every one of the 36 core candidates was
   discarded unrun. `scalar` burned generations g0, g1, g2 and g3 in about 35 minutes with **zero**
   completions — and the Eureka loop reflects on the PREVIOUS generation's results, so g4 and g5 would
   have been authored from an empty history. The search *process*, not merely its output, is invalid.
2. **The eight frozen leg winners are contaminated by selection.** Each was chosen as
   `max(val_fitness)` from a candidate pool that had been non-randomly truncated by a different
   model's failures. That is a deviation from the registered selection protocol and is not repairable
   after the fact.
3. **The generation ladders are corrupted on every line**, and the spurious rows are ledgered
   permanent, so a plain `--resume` would inherit the damage rather than repair it.

**What is genuinely uncontaminated** — and this is why the relaunch is cheap — are the 330 scored
H1-baseline test records and the four derivative-free arms (`random_search`, `tpe`, `bayes_opt`,
`cma_es`). Those rewards are hand-defined or algorithmic rather than LLM-authored, and the audit found
**zero** spurious abandonments among them. They are nonetheless being DISCARDED in the relaunch (§12):
retaining them would save under a day of a four-day run while handing a reviewer a question we do not
need to answer.

### 11.4 What this retracts from the "findings already established"

* **§6(a) "reflection depth drives state-contract violation" — RETRACTED.** The by-generation reject
  gradient is exactly what the collision manufactures: `qwen3.5-9b` reaches g4/g5 first (its own
  candidates fail fast), writes markers there, and those markers then kill every other line's g4/g5.
  The damage audit shows `scalar-g4` and `scalar-g5` spuriously wiped five-for-five on nearly every
  leg. The claim may yet be true; it is simply not evidenced by RUN 1.
* **§6(c) "per-model authoring reliability" — RETRACTED as a rate.** The node-side reject *reasons*
  remain genuine (those candidates really did run and fail), but every denominator is wrong, because
  most candidates were never submitted at all.
* **§7(2) "search depth is effectively 4 generations, not 6" — RETRACTED**, same cause.
* **§6(b) (ratio-form baselines are numerically fragile) and §5 (execution-quality evidence) STAND.**
  Both concern H1 baselines and scored test records, which the defect never touched. The weight
  simplex holding exactly across 15,312 snapshots, the identical 1571-step window on all records, and
  the `differential_sharpe` / `differential_downside_ratio` fallback concentration are unaffected.

---

## 12. RUN 2 — the relaunch plan

**Shape.** A clean relaunch into a FRESH output root, with the RUN 1 tree preserved untouched as the
evidence base for §11 — it is the primary artefact behind a disclosure the dissertation will carry.
Nothing carries over: no purge logic to get wrong, and no retained-record question for a reviewer.

**Preconditions, in order.**

1. Both fixes committed with their falsifiable regression tests, full suite green, and
   `freeze.py --check` RC=0 with the canonical hash unmoved. **The freeze does not move and must
   not** — neither defect lives in a hash-bound file, so RUN 2 executes the SAME pre-registered design
   under `4f90ecc47cc6a779…`. This is a re-execution, not a redesign, and therefore not a forking
   path.
2. Re-deploy the driver-side fixes. The node-side tree does not change: `poll.py` and `driver.py` are
   laptop-side, so the `deployed-archive:ce27dfc…` provenance stamp is unaffected.
3. ~~Top up the Anthropic balance~~ **RESOLVED — no top-up needed.** Console balances confirmed by
   Tamer: Anthropic **$31.96**, OpenRouter **$19.31**, against a projected $18.72 / $5.28. See §12.1
   for why the earlier "14 % margin, too tight" reading was wrong.
4. **Fence RUN 1's still-running cluster jobs — do NOT drain them.** 161 were still running at the
   halt. They are fenced for free by the fresh root: they archive into RUN 1's Scratch tree and
   RUN 2 never reads it, and `_enforce_kill_switch` reads `<root>/ledger`, so a fresh root also
   means RUN 1's task deaths are invisible to RUN 2's killswitch. Draining them by `qdel` would do
   the opposite of help — it replays exactly the mass-death-across-many-hosts signature that
   produced the 01:00 admin-kill incident and hard-blocked submission, and it forfeits the queue
   reservations. Capacity is not a reason either: the job cap is 1,000 and RUN 1 holds 161, so
   RUN 2 can submit alongside them from the start.

### 12.1 The budget, and why it is too tight to launch on

The $30 ceiling is ADVISORY (R83 warns, never refuses). The **binding** constraint is the real
Anthropic balance: if it empties mid-run, `claude-opus-5` stops authoring and the confirmatory
headline dies silently. Projected from measured per-call cost and measured GENUINE (post-fix) reject
rates:

| | projected need | balance (Tamer, console, 2026-07-28) | margin |
|---|---|---|---|
| **Anthropic** (opus-5 core $12.57 + h3 $2.58 + sonnet-5 $2.70 + haiku-4.5 $0.87) | **$18.72** | **$31.96** | **$13.24 (41 %)** |
| **OpenRouter** (the six open-weight legs) | **$5.28** | **$19.31** | **$14.03 (73 %)** |
| total | $24.00 | $51.27 | |

**No top-up is required; the budget is not a constraint on RUN 2.** An earlier version of this
section put the Anthropic margin at 14 % and called it too tight to launch on. That was wrong, and
the reason is worth keeping: it derived "remaining" as *recorded funding minus ledgered spend*, and
**the ledger is an ESTIMATE** — every row is stamped `estimated-from-planning-prices`, i.e. computed
from the price table rather than read back from the provider. The console balance is ground truth and
the derived figure was $10 pessimistic. **Lesson for the write-up's cost reporting: quote the ledger
as an estimate, never as billed spend, and reconcile it against the console at least once.**

RUN 1's own $12.92 bought nothing recoverable on the LLM arms, and $6.07 of it was burnt directly on
candidates the collision discarded unrun.

*The earlier projection in §3.2 (≈$19.53 all-in) was too low for two reasons now corrected: it omitted
the h3 single-shot line, which also authors on `claude-opus-5`, and it assumed exactly one authoring
call per candidate.*

### 12.1a The fresh root must be REMOTE as well as local — and it already is supported

RUN 1's 161 in-flight jobs archive into `~/Scratch/llmrp/outputs`. If RUN 2 shared that remote root,
its archive-truth resume would ADOPT their records — the identical hazard the 2026-07-27 launch gate
caught when 8 foreign probe records sat in the confirmatory search root. So RUN 2 must move BOTH:

* `--remote-root ~/Scratch/llmrp2` (the flag exists, defaults to `~/Scratch/llmrp`, and
  `run_campaign_cluster.py:1244` already documents a fresh remote root as a supported mode)
* `--output-dir outputs/campaign_cluster_run2`

Neither the deployed code tree (`~/llmrp`) nor the licensed gold (`--gold-dir` on ACFS) moves, so the
`deployed-archive:ce27dfc…` provenance stamp and the gold sha256 are unchanged — RUN 2 is the same
code on the same data under the same frozen hash.

**One edit is required before launch:** `scripts/mode_d_supervisor.ps1:64` hardcodes
`$outDir = "outputs\campaign_cluster"` and passes no `--remote-root`. Both must become parameters
threaded from `mode_d_launch.ps1`. (ASCII-only + `Parser::ParseFile`-validated, per the standing PS1
rule.)

### 12.2 What RUN 2 should do better, operationally

* Run the persistent leaked-ssh reaper until every line is confirmed to be on the fixed code — the fix
  is in the file, but a running driver keeps the code it imported at start.
* Watch the **spurious-abandonment counter directly**: with the fix in place, every
  `permanent_node_reject` must trace to a marker under the line's OWN sub-root. A single foreign one
  is a regression and should stop the run.
* Keep the makespan expectation from §4 unchanged — it was never the problem, and none of it is
  retracted.

### 12.3 THE PRE-RELAUNCH GATE — every item verified by running it (2026-07-28 13:55 UTC)

Tamer's instruction was that everything be flawless *before* the relaunch, so nothing below is
asserted from reading code; each row names what was executed and what it returned.

| # | check | how | result |
|---|---|---|---|
| 1 | full test suite | `pytest tests/ -q`, redirected not piped | **2,852 passed / 3 skipped / 0 failed, PYTEST_RC=0** |
| 2 | the 6 new regression tests are FALSIFIABLE | checked out HEAD, re-ran, restored | **all 6 FAIL pre-fix**; the three source files restored byte-identical (hashes compared) |
| 3 | the collision fix on REAL data | replayed `permanently_rejected_specs` over the RUN 1 archive | condemns **59**, rescues **439** — reproduces the independent damage audit **exactly** |
| 4 | freeze integrity after every edit | `freeze.py --check` | **RC=0**, canonical `4f90ecc47cc6a779…` **MATCHES** the recorded hash |
| 5 | lint | `ruff check src scripts tests` | **All checks passed** |
| 6 | pre-flight gauntlet | `preflight.py --gpu 0` | **14/14 OK, VERDICT: GO** (incl. gold checksum, author pin `max_tokens=16384 thinking=disabled`, freeze) |
| 7 | RUN 2 wiring, core line | `--dry-run` on the fresh roots | **DRY-RUN OK** — 9 arms resolved from frozen config, 568 seeds, 7 tiers, jobscript renders |
| 8 | RUN 2 wiring, leg lines | `--dry-run` for deepseek-v4-pro, qwen3.5-9b, kimi-k3 | **RC=0 each** — 5 arms, 568 seeds |
| 9 | RUN 2 wiring, h3 line | `--dry-run --h3-singleshot` | **RC=0** — 1 arm, 30 candidates/gen |
| 10 | node-side code is untouched | AST import graph from `run_one` | **NONE** of poll/driver/submit is reachable → no re-deploy, `deployed-archive` stamp unchanged |
| 11 | the deployed tree is still the frozen one | `cat ~/llmrp/GIT_COMMIT` | **`ce27dfc5fb7503e8673b544e5498cd20ce34de64`** — the seal commit, 2,710 files present |
| 12 | RUN 2's remote root is clean | `ls ~/Scratch/llmrp2` | **does not exist** — no adopted state possible |
| 13 | licensed gold reachable | `ls /acfs/users/ucestes/gold` | present; checksum re-verified locally by check 6 |
| 14 | cluster venv | `ls ~/venvs/llmrp/bin/python` | OK |
| 15 | capacity | `qstat -u ucestes`, Scratch `du` | RUN 1's 161 jobs draining; 243 MB used of Scratch; job cap 1,000 |
| 16 | all campaign PS1 scripts | `Parser::ParseFile` + byte scan | **0 parse errors, 0 non-ASCII, no BOM** on all four |
| 17 | no leaked ssh children remain | the reaper's own log | `ssh_total=0 reaped=0` for consecutive cycles |
| 18 | RUN 1 is fully stopped | process inventory | **0 supervisors, 0 drivers**; monitors deliberately left up |
| 19 | RUN 1 evidence preserved | record count + git | **621 records** on disk, untouched; reject evidence committed |
| 20 | budget | Tamer's console | Anthropic **$31.96** / OpenRouter **$19.31** vs $18.72 / $5.28 needed |

**Four defects were found and fixed by this gate itself** — they would each have damaged RUN 2
silently, and none was visible from reading the launch command:

1. `mode_d_watchdog.ps1` restarted dead lines with the supervisor's DEFAULT roots, so under a
   fresh-root run ONE restart would have pointed that line back at RUN 1's local mirror and Scratch
   root. The watchdog restarts lines every 300 s, so this was near-certain to fire.
2. `campaign_backup.ps1` hardcoded `outputs\campaign_cluster`, so the only off-machine copy of the
   irreplaceable RUN 2 archive would have kept mirroring the halted run and never touched RUN 2.
3. The same script harvested node logs from RUN 1's Scratch and **overwrote** its output file, so
   RUN 2's rows would have destroyed the RUN 1 reject evidence this post-mortem rests on. The
   filename is now root-scoped.
4. `mode_d_supervisor.ps1` passed no `--remote-root` at all, so RUN 2 would have shared RUN 1's
   Scratch tree and its archive-truth resume would have adopted the halted run's records.

### 12.4 THE RUN 2 LAUNCH COMMAND

```
powershell -ExecutionPolicy Bypass -File scripts\mode_d_launch.ps1 `
  -OutDir outputs\campaign_cluster_run2 -RemoteRoot ~/Scratch/llmrp2
```

Then, with the SAME roots (each defaults to RUN 1's paths, so passing them is not optional):

```
powershell -ExecutionPolicy Bypass -File scripts\mode_d_watchdog.ps1 `
  -IntervalSecs 300 -OutDir outputs\campaign_cluster_run2 -RemoteRoot ~/Scratch/llmrp2
powershell -ExecutionPolicy Bypass -File scripts\campaign_backup.ps1 `
  -SrcRoot outputs\campaign_cluster_run2 -RemoteRoot ~/Scratch/llmrp2
python scripts/sentinel.py outputs/campaign_cluster_run2 --watch --interval 300
python scripts/allocation_advisor.py --host myriad --watch 900 --archive-root outputs/campaign_cluster_run2
```

---

## 13. AFTER THE RELAUNCH — what the sweep found, and where the 300 s actually goes

Written 2026-07-28 13:50 UTC, RUN 2 at T+0.9 h. Two further findings, both from continuing to
measure rather than from reading code. **Certified after both fixes: full suite 2,856 passed / 3 skipped / 0 failed, PYTEST_RC=0** (reconciles exactly as 2,852 + 3 gate tests + 1 timeout test), ruff clean, freeze hash unmoved.

### 13.1 A SECOND cross-line collision — the review gate

Having found one unqualified filename in a shared root, the obvious question is whether there are
others. There was one more, and it is worse than a cosmetic clash. `read_root` is shared by all
twelve supervised lines, and the C3 review gate put two unqualified files in it:

* **`TIER1_APPROVED` was ONE file for twelve gates — and passing the gate CONSUMES it** (`unlink`,
  so the next passage needs its own approval). An approval granted after reviewing line A's report
  could therefore be eaten by whichever line reached its gate first: **that** line proceeding to the
  expensive C4 sweep on a review it never had, while line A still stopped. Five leg lines *did* stop
  at this gate during RUN 1, so the path was live, not theoretical.
* **`tier1_integrity.json` was likewise one file**, rewritten by every line. The report a reviewer
  read was whichever line wrote last, and the gate's staleness test — approval mtime ≥ report mtime
  — raced against *other* lines' report writes, silently invalidating legitimate approvals.

Confirmed on the RUN 1 archive: exactly one `tier1_integrity.json`/`.md` existed for all twelve
lines. Both are now scoped by a new `ClusterRun.line_tag()`, derived from the archive sub-root that
already keeps lines disjoint. The rename **fails closed** — a pre-existing unqualified
`TIER1_APPROVED` is now ignored, so a gate stops rather than passing unreviewed.

**The sweep is complete, and the negative result is worth recording so it is not re-audited.** Every
other write into the shared root was already scoped: pull staging is per-PID (the 2026-07-22 audit
caught that one), `campaign_summary` is root-suffixed, `batches/` `driver_status/` `ledger/` and
`spend_ledger_*` are tag-prefixed, the archive sub-roots are disjoint by construction, and
`pull_archive` keys on relative PATHS rather than ids. `permanent_reject_ids` and these two gate
files were the *only* unscoped consumers.

> **The pattern, for CH4.** All three defects are one shape: *a resource shared by twelve concurrent
> lines, keyed by an identifier that is only unique within one line.* The codebase had been audited
> for exactly this (the 2026-07-19 and 2026-07-22 audits each caught an instance and left a comment
> saying so) — and it still shipped two more. That is a statement about concurrent-system testing,
> not about carelessness: ~2,800 tests all exercise ONE line, so no test could see a collision that
> requires twelve.

### 13.2 The "300 s ssh timeout" is not an ssh timeout

RUN 2 kept logging `timed out after 300 seconds` even with the leak fixed, so I measured where the
time actually goes rather than assuming the message.

| what | measured |
|---|---|
| the remote command | `qstat -r` **1.2 s** (3 consecutive), `find` over the whole outputs tree **0.046 s**, `mkdir -p` trivial |
| the login node | load **3.4**, 67 users, only **5** of our sessions |
| the client | sustained 8-concurrent A/B, Windows OpenSSH 9.5p2 vs Git 10.2p1: **80/80 ok on both**, worst case 6.0 s vs 2.5 s |
| **the ssh children themselves** | **55 samples over 3 min: 8 distinct children, NOT ONE aged past 10 s** |

…while the driver logged a 300 s timeout roughly every five minutes, on ops as trivial as
`mkdir -p`. The timeouts also arrive *exactly 300 s apart*, which is a retry period, not a
population of independent stalls.

**So the wait is happening in the PARENT — `subprocess.run`'s pipe reader never observing EOF — and
the log message misattributes it to the remote command.** This is the fifth instrument in this
project found to report something other than what it measures, and the campaign was correct every
time.

The exact parent-side mechanism is **not yet identified**, so the response is an honest BOUND rather
than a cure: the driver ssh timeout drops 300 s → **120 s**, about 20× the measured worst-case real
latency, returning a parked batch thread to work 2.5× sooner. Recorded as an open question rather
than a solved one.

**Two remedies were tested and NOT adopted**, because the tempting fix was the wrong one both times:
`ConnectionAttempts`/`ConnectTimeout` client hardening (A/B over three paired rounds: 8/72 control
vs 9/72 treatment — refuted), and ssh multiplexing (unusable regardless: the server's `MaxSessions`
default of 10 would cap us *below* the ~40 concurrent ops the twelve lines need).

### 13.3 The leak fix, confirmed under production load

RUN 1 accumulated 13 leaked ssh children and climbed from 5.2 % to 55.3 % transport failures over
ten hours. RUN 2, on the fixed code, holds at **5–6 live ssh children with `reaped=0`** across
consecutive reaper cycles — the leak is gone, not merely reduced.

### 13.4 The watchdog fix, validated in production

The watchdog's own root-scoping fix was exercised for real: the core line was deliberately stopped
at 14:35 (local) to reload the fixed code, and the watchdog detected `DEAD lines: core` and
restarted it **with the RUN 2 roots**, inside its 300 s cycle. A `verify_roots` sweep then confirmed
12/12 supervisors and every monitor on the correct roots, **0 on the old ones**.

---

## 14. THE v2.1 RE-FREEZE — closing the selection-validity hole while it was still free to close

**2026-07-28, ~14:15 UTC.** RUN 2 was halted at T+1.3 h and the pre-registration LIFTED and re-frozen
to register a **winner-eligibility execution floor** (amendment **R115**, decision record
**ADR-062**). This section exists because a post-launch change to a pre-registration is the single
most scrutinised act in a pre-registered study, and it must be defensible on the page, not just in
the repo.

### 14.1 The hole

Selection was `max(val_fitness)` with **no execution-quality condition**. `train_safe_default_count`
recorded the steps on which the authored reward RAISED and the neutral R66 fallback stood in — it was
archived and reported, and gated nothing. So a candidate whose reward executed on only part of its
training could be frozen as an arm's winner, and the sealed leg would then **re-train that same
reward** and inherit the contamination.

That is not a data-quality nuisance; it is an **identification hole**. H2 requires the arms to differ
ONLY in the authored reward. A winner that trained half on the R66 fallback confounds the arm
contrast with execution quality — and in the limit the contrast becomes the fallback measured
against itself.

**Measured** over the full RUN 1 archive (613 records carrying the counter; this supersedes an
earlier 136-candidate snapshot that saw only two severe cases):

| band | n | detail |
|---|---|---|
| clean (0 fallback steps) | **594** | |
| trace (<1 %) | **16** | worst **0.41 %** (1,650/400,000) |
| **SEVERE (≥1 %)** | **3** | `qwen3.6-27b/scalar-g1-c4` **53.66 %** · `qwen3.5-9b/distributional-g1-c2` **50.02 %** · `glm-5.2/placebo_shuffled-g0-c0` **39.40 %** |

All three are open-weight legs, and **zero frozen winners carried any fallback**. But across ~55
arm-instances the chance that at least one winner is contaminated is **not** negligible, which is why
detection alone was judged insufficient.

### 14.2 Why the RUN 1 measurement is still usable

RUN 1's *search* was invalidated by the cross-line reject collision (§11.2). This measurement is
unaffected, and the distinction is exact: `train_safe_default_count` is a **per-training execution
statistic of a candidate that actually ran**, while the collision only decided which candidates were
*allowed* to run. Nothing about the counter depends on the selection that was broken.

### 14.3 Why this is PRE-DATA, on the project's own established test

ADR-059 (the v1.0 unfreeze) set the standard: *"The forking-paths/pre-registration sin is POST-DATA
design change; a documented, dated, PRE-DATA revision … is the pre-registration discipline working as
intended."* At the moment of the lift:

* RUN 1's search was invalidated by a **defect**, not by its results, and is **discarded wholesale** —
  no RUN 1 result enters any analysis;
* **RUN 2 held ZERO records** (verified: the run-2 tree contained no `record.json` at all);
* the sealed 2020–2026 test leg was **untouched** by any LLM arm;
* and decisively — **NO arm contrast of any kind had ever been computed.** Only H1 baselines ever had
  scored records, so no ranking, no effect and no ordering existed that a rule could be steered
  toward. §5 recorded that property as "effect-blind" *before* this amendment was contemplated.

That window closed permanently once `claude-opus-5` began authoring candidates with real
`val_fitness` values, so the registered-by-construction option existed **only** at this moment. It
was taken.

### 14.4 The rule, and why it cannot be gamed

A candidate is **eligible** iff `train_safe_default_count / train_safe_call_count < 0.10`; the winner
is `max(val_fitness)` **among the eligible**; an arm with **no** eligible candidate **fails loud**
rather than silently promoting the least-bad contaminated one.

* **Effect-blind by construction.** The filter reads an execution counter and never `val_fitness`,
  `test_sharpe`, `test_cvar` or any performance quantity. A test asserts this by inspecting the
  function source, so the property is enforced rather than promised.
* **Threshold-insensitive, not tuned.** The distribution is strongly bimodal — worst trace 0.41 %,
  mildest severe 39.40 %, a **96× empty gap** — so any value in ~1–35 % partitions the data
  identically. 0.10 sits in that gap.
* **Honest caveat, stated not hidden.** RUN 1's data motivated the rule's EXISTENCE; it did not set
  its VALUE. The insensitivity above is what makes that distinction verifiable rather than merely
  asserted.
* **Common-mode.** The floor applies identically to every arm and every leg, so every contrast is
  affected identically; it changes only whether a candidate whose reward *did not actually run* may
  represent its arm.
* **Cannot drift silently.** The value lives in the hash-bound `config/preregistration.yaml` and is
  read from there at selection time — so any change to it moves the canonical hash and fails
  `freeze --check`. That is a stronger guarantee than a mirror check.

### 14.5 The freeze chain, preserved

`freeze.py` **forbids re-freezing** by design ("post-freeze changes go through a dated amendment"), so
this went through the documented lift: `frozen: true → false`, `freeze_hash → null`, amend, then a
fresh freeze. Every prior record survives as history — tags `prereg-v1.0`, `prereg-freeze-ce5db62c`,
**`prereg-v2.0`**, and `docs/prereg-v2.0.sha256`. The chain now reads:

| version | hash | frozen | fate |
|---|---|---|---|
| v1.0 | `ce5db62c` | 2026-07-18 | lifted 07-20 pre-data (ADR-059/R78) |
| — | `ccf2e76f` | 2026-07-22 | lifted same day (R93/R94) |
| **v2.0** | `4f90ecc47cc6a779…` | 2026-07-28 00:05Z | **lifted 07-28 pre-data (R115/ADR-062)** — RUN 1 + RUN 2 ran under it; both discarded |
| **v2.1** | `3ca6f01ab7724d47…` | 2026-07-28 | the design RUN 3 executes |

**Verified at the lift:** `freeze.py --check` **RC=0, 23/23** with the new canonical hash recomputed
and `freeze_hash: null` correctly reported as not-yet-frozen; ruff clean; the R115 tests proven to
FAIL against the pre-R115 selector (4 of 7 — the other three assert unchanged behaviour and correctly
pass either way), with `scripts/run_campaign.py` restored byte-identical afterwards.
