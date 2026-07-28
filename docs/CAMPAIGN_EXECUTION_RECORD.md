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

---

## 15. THE COLLISION ALSO SILENTLY DISABLED THE REFLECTION LOOP — and the fed block is where you think it isn't

Found 2026-07-28 ~16:30 UTC while verifying, on RUN 3, that the manipulated variable actually
varies. It does — but checking it surfaced two things the earlier post-mortem had not.

### 15.1 Construct validity HOLDS: the fed tail vector really is delivered

Sampled from the live archive, a `distributional` reflection prompt reads:

```
Reflect on the previous candidate's results and propose an improved reward function.
Feedback from the previous candidate:
Your previous reward scored: 0.066737 (validation Deflated Sharpe).
Realized-return tail diagnostics (training period):
  CVaR 5%: -0.0296      CVaR 10%: -0.0216     CVaR 25%: -0.0129
  CVaR 1%: -0.0530  (high-variance estimate)
  left-tail mass: +0.0230        left-tail skew: -0.0547
```

That is the manipulated variable, in the prompt, at the `.4f` precision R114 registered. The
construct-validity hinge holds from both sides now: the base prompts are tail-NEUTRAL (pinned by an
existing test) **and** the fed block carries the six-scalar tail vector the tail arms are defined by.

### 15.2 ⚠ The fed block is NOT in `record.json["feedback_block"]` — read `prompt.txt`

**Measured: all 621 RUN 1 records carry an EMPTY `feedback_block`,** at every generation. The field
exists in the record schema and the cluster path never populates it (`parallel.py` writes `""`
literally). The fed block is archived in the candidate's **`prompt.txt`**, which contains
`REFLECTION_PREAMBLE + prev_block` verbatim.

This is a provenance REDUNDANCY gap, not a science gap — nothing is lost, it is simply stored in the
other file. It is left as-is deliberately: populating the field means editing node-side code, which
forces a re-deploy and would move the `deployed-archive` stamp mid-run, a real cost for a duplicate
of something already archived.

> **ANALYSIS-TIME OBLIGATION — and it is ALREADY MET by the shipped pipeline.** Every fed-block
> analysis must read the **prompt**, not `feedback_block`. Verified rather than assumed:
> `src/inference/information_gap.py` (the mechanism module — the surface-echo-vs-genuine-use audit,
> i.e. the originality kernel) already does exactly that: `fed_text = str(r.get("prompt") or "")`,
> with `feedback_block` retained only as a legacy fallback for pre-Rank-14 archives. That ordering
> was fixed on 2026-07-05 (M14) for an independent and better reason — a record's own
> `feedback_block` is the block built FROM that candidate and fed to the NEXT generation, so a
> block-first read computed the redundancy on an off-by-one-generation sequence and defeated the
> sibling de-duplication.
>
> And the prompt is genuinely there: `load_run` embeds `prompt` IN the record (`prompt.txt` is a
> byte-verified sidecar, so "analysis never depends on a separate file"). Measured on RUN 1: **241
> records carry a non-empty embedded prompt** — exactly the count of `prompt.txt` files — while the
> 380 without one are the family/DFO search arms and sealed test records, which legitimately have no
> authored prompt.
>
> So this is a **verified negative**, recorded so it is not re-investigated: the shipped mechanism
> analysis is safe. The warning applies only to any ad-hoc analysis written later that reaches for
> `feedback_block` because the schema advertises it — that path returns empty strings and would
> silently conclude the designer was shown nothing.

### 15.3 ★ The collision did not merely discard candidates — it disabled the reflection loop

`run_search_arm` builds each generation's prompt as

```python
user = prompts.initial if prev_block is None else f"{_REFLECTION_PREAMBLE}\n{prev_block}"
```

and `prev_block` is set **only** when that generation produced an accepted candidate
(`if best is not None:`). So a generation that completes **nothing** leaves `prev_block` as `None`,
and the NEXT generation authors from the **INITIAL** prompt — with no error, no warning, and a
perfectly normal-looking record.

That is exactly what the cross-line reject collision caused. Measured on the RUN 1 archive:

| | |
|---|---|
| archived `prompt.txt` files | **241** |
| carrying the reflection preamble | **10 (4 %)** |
| arms that ever reflected | **`distributional` only** |

**So RUN 1's "six-generation reflective search" was, in fact, repeated independent draws from the
same initial prompt for essentially every arm.** The reflection loop is the mechanism H2 exists to
study, and the collision switched it off silently while every counter stayed green.

This is a materially stronger statement of the damage than "the search was sterilised", and it
closes the last question about salvage: even the candidates that DID complete were, in most arms,
not products of the registered reflective process at all.

It also retro-explains §6(a) more completely. The retracted "reflection depth drives state-contract
violation" gradient was not merely confounded by which candidates were allowed to run — for most
arms **there was no reflection depth**, because generation g was authored from the same prompt as
generation 0.

### 15.4 A monitoring gap, now closed

Nothing watched this. A starved reflection loop produces valid-looking records, a green suite, and a
healthy sentinel — the failure is invisible by construction. RUN 3 therefore runs a
**reflection-starvation guard**: of the candidates at generation > 0, what fraction were shown a
reflection block? It reports the per-arm breakdown when that fraction falls below 80 %, so the
mechanism degrading is now an alert rather than a discovery made months later at write-up.

---

## 16. WHY CANDIDATES GET REJECTED — separating the FINDING from a DEFECT

Asked directly during RUN 3 ("why do these errors appear?"), and it deserves a precise answer,
because two things that look identical in a log must never be conflated.

### 16.1 The rejects are the phenomenon under study, not a fault

A live RUN 3 example:

```
{"failed": "scalar-g0-c1",
 "error": "sandbox: reward crashed during validation:
           UnboundLocalError('cannot access local variable rolling_std ...')"}
```

An LLM wrote Python with a genuine bug. **That is what this dissertation measures.** The per-model
AUTHORING-RELIABILITY table is a registered deliverable (Raad/Stefan point 5 — "which models write
executable objective code at all"), and the numeracy-bottleneck thesis is the paper's central
mechanism claim. Removing these failures would erase the measurement, exactly as §6(a) already says
of the state-contract rejects: *it must not be "fixed"*.

The cost is negligible and was measured on RUN 1: a reject is caught by the sandbox **in seconds,
before training starts** — 73 rejected/aborted tasks came to 1.50 core-hours against 1,626, i.e.
**0.092 % of all compute**.

### 16.2 The question that actually mattered: is it OUR machinery?

A **truncated** completion is indistinguishable from a model that cannot write the code — both
surface as `source defines no callable named 'reward'`. So truncation does not merely lose a
candidate: it **contaminates the reliability table itself**. This is not hypothetical. R106 exists
because the confirmatory author had no registered cap and fell back to 4096 while Opus emits
5,008–6,412-token completions, so ~20 % of its candidates would have truncated **silently** and been
scored as authoring failures.

Tested directly on RUN 3 against the registered 16,384 cap:

| line | calls | max out | p95 | % of cap |
|---|---|---|---|---|
| **leg7 `nemotron`** | 25 | **14,454** | 1,360 | **88.2 %** |
| h3ss (`claude-opus-5`) | 30 | 4,584 | 3,631 | 28.0 % |
| every other line | 25 each | ≤ 3,691 | ≤ 2,864 | ≤ 22.5 % |

**No truncation is occurring.** Every reject observed is the MODEL, not our machinery — so the
authoring-reliability numbers RUN 3 produces are clean measurements of capability.

### 16.3 One live fragility this exposed, now guarded

`nemotron` produced a single **14,454-token** completion against a p95 of **1,360** — a ~10×
rambling outlier sitting **11.8 % below the cap**. It did not truncate. But if one ever exceeds
16,384, that model's reliability figure would be contaminated by OUR cap rather than its capability,
and it would look exactly like a model failure.

That is not a defect today, and the considered answer is **NOT to raise the cap**. Four reasons,
each verified rather than assumed:

1. **The cap is HASH-BOUND.** `model_suite.max_tokens_pins` lives in `config/preregistration.yaml`,
   inside the canonical hash — so raising it means unfreeze → re-freeze → **discard RUN 3 and
   relaunch as RUN 4**. That price was worth paying once, for R115's identification hole; paying it
   again for an event that has never occurred would be poor judgement.
2. **16,384 is already the verified ceiling across all eleven providers.** R106 tested acceptance
   LIVE on every model precisely because "a provider that capped lower would 400 the confirmatory
   path". Raising further risks a **400 on the confirmatory path** — categorically worse than one
   truncated leg completion.
3. **Caps must be MATCHED** (R106: "with unequal caps a capability contrast is not a capability
   contrast"), so `nemotron` cannot be raised alone; all eleven would move and all eleven would need
   re-verifying live.
4. **It has never happened, and it would not be silent if it did.**
   `client._warn_if_incomplete` fires on any `stop_reason` in {`max_tokens`, `refusal`, `length`,
   `content_filter`}, and `run_campaign_cluster` configures the root logger at INFO, so the event
   lands in the ARCHIVED driver log. Measured across RUN 1, RUN 2 and RUN 3: **0 occurrences** of
   `llm_incomplete_completion`.

So a truncated candidate is **identifiable** and can be reported as **cap-limited** rather than an
authoring failure — the reliability table stays clean either way. The response is therefore to WATCH
the definitive signal rather than buy headroom: the truncation guard now alerts on
`llm_incomplete_completion` appearing in the driver logs (the provider saying so outright) as well
as on the token margin (a heuristic that only ever approximates it).

⚠ **One residual, recorded rather than fixed.** `stop_reason` is captured by the client and logged,
but is NOT persisted into the structured spend ledger on the cluster path — so attribution at
analysis time is a driver-log grep, not a field join. Fixing that means editing the authoring hot
path that all twelve lines use, during a live run, for an event that has never occurred: the risk of
the edit exceeds the risk it removes. Worth doing at the next natural restart, and noted here so the
choice is a decision rather than an oversight.

### 16.4 The discriminator, for the write-up

When the reliability table is written, each reject class must be attributed correctly:

| reject class | attribution |
|---|---|
| `reward crashed during validation: <Exception>` | **the model** — a genuine bug in authored code |
| `invalid return` | **the model** — contract violation |
| `source defines no callable named 'reward'` | **ambiguous** — the model produced prose/nothing, OR our cap truncated it. Resolve by the completion's `tokens_out` against the cap; only a completion well below the cap is attributable to the model |
| `NoneType` at reset (state contract) | **the model** — the registered §6(a) mechanism finding |

The `tokens_out` field in the spend ledger is what makes that third row resolvable at all, which is
why it is worth saying explicitly here rather than leaving it to be re-derived later.

---

## 17. IDENTIFICATION-VALIDITY AUDIT — the five load-bearing assumptions, verified by EXECUTION

Run 2026-07-28, RUN 3 at T+3 h, against the standing requirement that this work be publishable. Each
item below is something a referee can and should attack, and each was checked by RUNNING it rather
than by reading the code that implements it. Two of the five were checked because I suspected a
defect; both cleared, and the negative results are recorded here so they are not re-litigated.

### 17.1 The arms differ EXACTLY as H2 claims — the dose-response ladder plus two orthogonal controls

`schema.build_block` was called for all five LLM arms with **identical** inputs (fitness 0.066737 and
one fixed tail vector) and the rendered text diffed:

| arm | what the designer sees | role |
|---|---|---|
| `scalar` | the fitness line only | **0** tail numbers — the H2 comparator |
| `scalar_cvar5` | fitness + `CVaR 5%: -0.0296` | **1 of 6** — the dose-response midpoint |
| `distributional` | fitness + all six tail statistics | the treatment |
| `placebo` | fitness + six lines reading `reference value N: +0.0000`, labelled *"Reference constants (inert; no diagnostic content)"* | identical STRUCTURE, **zero information** |
| `placebo_shuffled` | fitness + the **same six numbers permuted onto the wrong labels** | real numbers, **destroyed information** |

Checks, all PASS:

1. all five arms render **distinct** blocks;
2. `placebo` contains **none** of `distributional`'s tail numbers (no information leak into the
   control);
3. `placebo_shuffled` carries the **same multiset** of numbers in a **different order** (set-equal
   TRUE, text-identical FALSE) — so it controls for *having real numbers* while destroying *what
   they mean*;
4. `scalar` contains **no** tail vocabulary at all (cvar/tail/skew/downside/drawdown);
5. `scalar_cvar5` is a **strict subset** of `distributional` (1 number vs 6).

This is the identification: a monotone information ladder (0 → 1 → 6) with a **structure** control
and a **content** control isolating the two ways a "tail effect" could be spurious.

### 17.2 CRN pairing holds — and it survives a reward that consumes RNG

Every paired contrast (H1's IUT, H2's arm differences) subtracts arm A's score from arm B's at the
SAME seed and attributes the difference to the reward. That is valid only if everything else at that
seed is identical.

**The subtle risk, stated because it is not obvious.** `_test_seed_worker` runs
`set_global_seed(seed)` → `validate_once(reward_source)` → build env → `make_agent_trainer(cfg, seed)`.
`validate_once` **executes the authored reward** on a fixture, and an authored reward is free to call
`np.random`. If the agent were initialised from the ambient global RNG, an arm whose reward draws and
an arm whose reward does not would begin training from **different network weights at the same
seed** — and every paired p-value in the dissertation would be wrong in a way no downstream check
could see.

**Verified it cannot happen.** `resolve_agent_kwargs(cfg, seed)` places the seed **into the SB3 model
kwargs** (`seed: 7`), so the model re-seeds at construction. Demonstrated directly: drawing 1,000
random numbers between the global seeding and the resolution leaves the resolved seed — and the
entire kwargs dict — **byte-identical**. The agent's initialisation is therefore arm-independent by
construction.

### 17.3 B1 matched budget — the sealed leg really does train at B\*

The search specs carry `train_steps: 400000`, but the **test/sealed specs carry `None`** at both the
top level and inside `agent_cfg`, which raises the obvious question of whether the scored leg
silently falls back to a smaller default (the agent block's own default is 50,000 — an 8× shortfall
that would invalidate every scored record).

**It does not.** `train_safe_call_count` records one reward call per training step, so it reveals the
budget actually executed. Across **330 of 330 scored records: exactly 400,000.** The `None` is
resolved downstream from the registered configuration, and B1's matched budget holds in fact, not
merely in intent.

### 17.4 The mechanism pipeline reads what the designer SAW

Covered in §15.2: `information_gap.py` (the originality kernel) reads `r.get("prompt")` first, and
the prompt is embedded in the record itself — 241 records carry a non-empty one, exactly matching the
241 `prompt.txt` sidecars. The empty `feedback_block` field is a redundancy, not a gap.

### 17.5 No truncation is contaminating the authoring-reliability finding

Covered in §16: `0` provider-confirmed `llm_incomplete_completion` events across RUN 1, RUN 2 and
RUN 3, with the worst completion at 88.2 % of the registered 16,384 cap. Every observed reject is
attributable to the MODEL, so the reliability table measures capability rather than our budget.

---

**What this audit does NOT cover, stated plainly rather than implied:** the statistical machinery
(DSR, PBO, the BH-FDR family, the IUT nodes) and the data layer (PIT correctness,
survivorship-freeness, the embargo) were audited in earlier sessions and are not re-verified here.
This section covers only the five assumptions that connect the *running campaign* to the *claims* —
the layer where this session has repeatedly found silent defects.

---

## 18. THE OPEN-DEFECT REGISTER — every known issue, its state, and the evidence

Compiled 2026-07-28 by working the FULL list rather than the interesting parts: this session's own
findings plus every item still marked open in the handoff from earlier review lanes. Each row says
what was actually run. Nothing here is "believed fine".

### 18.1 CLOSED — verified fixed or not applicable

| # | issue | state | evidence |
|---|---|---|---|
| A | **Cross-line reject collision** (killed RUN 1) | **FIXED** | `permanently_rejected_specs` scopes by sub-root; replayed over the real RUN 1 archive it condemns exactly 59 and rescues 439, matching an independent audit; 2 falsifiable tests; live collision guard reports **0 spurious** on RUN 3 |
| B | **C3 gate's `TIER1_APPROVED` + `tier1_integrity.json` shared across 12 lines** | **FIXED** | scoped by `ClusterRun.line_tag()`, fails CLOSED; 3 falsifiable tests |
| C | **ssh child leaked on every failed pull** | **FIXED** | `submit.reap` at both sites; 4 falsifiable tests; RUN 3 holds 0–6 live children with `reaped=0` vs RUN 1's 13 accumulating |
| D | **watchdog / backup / supervisor hardcoded RUN 1's roots** | **FIXED** | all take `-OutDir`/`-RemoteRoot`; watchdog restart verified live on the RUN 3 roots; harvest is root-scoped (`node_authoring_rejects_campaign_cluster_run3.jsonl` confirmed separate) |
| E | **R115 raise broke `run_arm_pipeline`'s no-raise contract** | **FIXED** | `NoEligibleWinnerError` caught at all 3 sites → `no_eligible_winner`, distinct from `no_winner`; C3 gate catches the incompleteness |
| F | **#52 H4 turnover space two-way vs a one-way rationale** | **CLOSED, ratified 2026-07-26** | the range STAYS [0, 0.02]; the *prose* was corrected. Narrowing a registered search space to satisfy a sizing heuristic would be changing the science to fit the documentation |
| G | **`monitor.py` absent state file reads healthy forever** | **ALREADY FIXED** | LATCH-ONCE-SEEN (`state_seen`, 2026-07-26) distinguishes "not started" from "vanished" |
| H | **#58 killswitch window vs ledger freshness** | **NOT APPLICABLE at our configuration** | window 300 s > `--poll-secs` 180 s > `min_pull_interval` 60 s, so the ledger is always fresher than the window. The false-negative needed the 600 s default we do not use |
| I | **Malformed batch result judged fail-OPEN** | **FIXED this session** | `res.get("ok", True)` → `False` at both sites, ending a genuine disagreement with the launcher's `bool(out.get("ok"))`; every producer sets `ok` today so behaviour is provably unchanged; pinned by a test |

### 18.2 OPEN — with the exposure stated exactly

| # | issue | exposure | why it is not closed |
|---|---|---|---|
| J | **The 300 s "ssh timeout" mechanism is UNIDENTIFIED** | throughput only — **no effect on any recorded number** | see §18.3 |
| K | **`stop_reason` not persisted to the structured spend ledger** | attribution of a truncation is a driver-log grep, not a field join | the event has **never occurred** (0 across three runs) and the fix edits the authoring hot path all 12 lines use, mid-run. Deferred to the next natural restart |
| L | **Factor ladder forward-fills 21 of 1,631 test sessions** | **report-only**; headline unaffected | **unfixable by re-pulling** — French has not published past 2026-05-29. Verified by running the real loaders: `load_ff_factors` n_extrapolated **21**, `load_market_proxy_returns` **0**, `load_risk_free_daily` **0** |
| M | **Tag is annotated, not signed; no OpenTimestamps proof** | external anchor is the commit + tag on origin | no GPG key; the OTS client crashes on Windows. Already disclosed; the write-up must not imply otherwise |
| N | **174 legacy `Co-Authored-By` trailers in pre-2026-07-26 history** | attribution hygiene | needs a history rewrite + force-push on a shared branch — Tamer's call, never unilateral |

> **On (L), the analysis-time obligation.** The factor-attribution ladder must be computed over
> sessions with REAL factor data (through 2026-05-29) or report the 21 extrapolated sessions
> explicitly. The guard `_extrapolated_after` already logs the exact count and exposes it on the
> result object, so this is a reporting discipline, not a detection problem. **The headline Sharpe is
> clean**: the risk-free series resolves through `_REFRESHED_RAW` to `fred_macro_x26.csv` and returns
> **0** extrapolated sessions.

### 18.3 (J) THE TRANSPORT STALL — five hypotheses tested, five refuted, and why it does not touch the science

This is the one genuinely unexplained defect, so the honest thing is to state exactly what is known,
what was eliminated, and why it is nonetheless not a threat to the result.

**What is established.** The driver logs `timed out after 300 seconds`, arriving *exactly* 300 s
apart, on operations as trivial as `mkdir -p`.

| hypothesis | test | verdict |
|---|---|---|
| the archive grew too large | `find` over the whole remote outputs tree | **REFUTED** — 0.046 s for 703 records |
| SGE qmaster congestion | 16 concurrent `qstat -r` | **REFUTED** — 14/16 ok at ~2.5 s |
| OpenSSH `MaxStartups` drops | fan-out ramp to 48 | **REAL but IRRELEVANT** — ~29 % refused, all in 0.1 s, never a timeout |
| the ssh client | sustained 8-concurrent A/B, Windows 9.5p2 vs Git 10.2p1 | **REFUTED** — 80/80 ok on both |
| GIL starvation from ~60 threads | 60 threads × 12 rounds of a LOCAL `echo` | **REFUTED** — 720 calls, max 0.599 s, 0 timeouts |
| inherited stdin (ssh reads it without `-n`) | A/B, inherited vs `stdin=DEVNULL`, fan-out 40 × 3 | **REFUTED** — no difference in stalls |

And decisively: sampling every 3 s for 3 minutes found **8 ssh children, not one aged past 10 s**,
while the driver was logging 300 s timeouts. **The wall-clock is spent in the PARENT and the message
misattributes it to the remote command.**

**Why it does not threaten the result.** A stalled poll delays *reconciliation*, never computation:
the cluster job runs to completion regardless, writes its record, and the next poll picks it up. No
recorded number depends on how quickly the driver noticed. The measured consequence is throughput —
and the compounding version of it (the leak, item C) *is* fixed and proven: RUN 1 climbed 5.2 % →
55.3 % over ten hours; RUN 3 sits at **4 %** with a flat failure counter.

**What was done rather than guessed.** The bound was lowered 300 s → **120 s** (~20× the measured
worst-case real latency), which returns a parked batch thread to work 2.5× sooner. That is an honest
bound, not a cure, and it is labelled as such. The remaining hypothesis worth testing at the next
restart is Windows pipe-handle inheritance across concurrently-spawned children — a known CPython
race that would produce exactly this signature (child exits, parent's reader never sees EOF).

---

## 19. RUN 3 — what it PROVED, and why it was nonetheless halted

RUN 3 was launched on the v2.1 freeze at **16:19:30** and halted at **19:45:45** on 2026-07-28 —
**3 h 26 min** of twelve-line operation. It was never intended to be the confirmatory run; it was the
*evidence* that the RUN 1 fixes work under real twelve-line concurrency, which no single-line test can
show. Every number below was harvested from the archive after the halt, not read off a monitor.

### 19.1 What it measured

| quantity | RUN 3 | what it proves |
|---|---|---|
| lines up | **12 / 12** for the whole 3 h 26 min | the root-scoped launch path is sound |
| task specs submitted | **405** | real cluster load, not a smoke test |
| records archived | 9 (+ 9 authored `reward.py`) | the write path is intact end to end |
| LLM calls | **280** across all 11 models | the authoring path is live on every leg |
| `stop_reason` | 80 `end_turn` + 200 `stop`, **0 truncated** | the 16,384 cap is not clipping anyone |
| **spurious abandonments** | **0** | ← **the RUN 1 killer is dead** |
| reject markers, whole archive | **1**, in its own sub-root | nothing to collide with, and correctly scoped |
| driver log levels, all 12 lines | 881 INFO · 41 WARNING · **0 ERROR** | no line ever entered a bad state |
| transport warnings | 41, **max 2 consecutive**, always self-healed | vs RUN 1's monotonic climb to 55 % |
| core-line spend | **$0.00** | the canary shield held — the confirmatory seat never paid |
| leg spend | **$3.81** | within projection |

The **0 spurious abandonments** figure is the one that matters. RUN 1 abandoned 439 candidates that
had never been submitted or judged; RUN 3, on identical concurrency, abandoned none. That is the fix
demonstrated rather than argued.

### 19.2 Why it was halted anyway

Three driver fixes landed in commit `18dead8` **after** RUN 3's drivers had already started, so its
running processes carried the older code:

1. `stdin=DEVNULL` on all three ssh spawn sites,
2. the `ssh_timeout_diagnostic` that will localise the stall on its next occurrence,
3. structural `stop_reason` persistence in the spend ledger.

The evidence is visible in the archive: RUN 3's `spend_ledger_*.jsonl` rows carry **no** `stop_reason`
field at all (the truncation evidence above comes from `llm_calls.jsonl`, which the client has always
written), and **0** `ssh_timeout_diagnostic` lines appear in any driver log. A run whose processes are
a commit behind its own repository is exactly the ambiguity Tamer's standing instruction forbids.
So RUN 3 was stopped and RUN 4 will start on the complete fix set, with every line running code that
matches HEAD.

### 19.3 How it was halted (and what was deliberately preserved)

Order matters — the watchdog restarts dead lines every 300 s, so it dies first:

1. `STOP_CAMPAIGN` written into `outputs/campaign_cluster_run3/`;
2. **watchdogs killed first** (2), verified 0 remaining;
3. 12 supervisors → 24 drivers → backup → 2 sentinels → 2 advisors, verified **0 remaining**;
4. on the cluster: **342 campaign jobs deleted by explicit job ID**, and the **20 `l16xx` p6-ladder
   jobs preserved** — confirmed by a post-delete `qstat` showing exactly 20 jobs, all `l16xx`. A
   blanket `qdel -u ucestes` would have destroyed the B\*-ladder recovery cells that feed figure F11.

### 19.4 The three-run spend, from the ledgers

| run | LLM calls | spend | core (Opus) line |
|---|---|---|---|
| RUN 1 | 925 | **$11.65** | $4.19 (c1) + $2.58 (h3ss) |
| RUN 2 | 156 | **$1.29** | $0.00 — no `c1` ledger was ever created |
| RUN 3 | 280 | **$3.81** | $0.00 c1; $2.51 h3ss |
| **total** | **1,361** | **$16.75** | |

The pattern worth knowing before RUN 4: **the canary shield works** — across two relaunches the
confirmatory `c1` line never spent a cent, because it does not author until its canary clears. The
recurring relaunch cost is the **h3 single-shot** (~$2.5 per launch, Opus), which re-authors from
scratch every time. Budget three relaunches' worth of h3ss, not three campaigns' worth.

---

## 20. THE COMPLETE CROSS-RUN POST-MORTEM — every mistake, its cause, its fix, its lesson

Written at Tamer's explicit instruction (2026-07-28): *"make sure you document everything from all
previous runs, so we know mistakes and etc."* This is the consolidated ledger — **machine defects and
my own process errors together**, because the second kind cost real time and would otherwise vanish
from the record. Nothing here is softened.

### 20.1 The defects that were IN THE MACHINE

| # | defect | run(s) | root cause | how it was found | fix | lesson |
|---|---|---|---|---|---|---|
| **D1** | **Cross-line reject-marker collision** — 439 of 498 abandonments (88 %) spurious, **36/36 on the confirmatory core**, 402 traced to `qwen3.5-9b` alone | RUN 1 (**fatal**) | `driver.run_batch` resolved permanent rejects with a **mirror-wide** `permanent_reject_ids(local_archive_root)`; markers are keyed on the bare candidate id (`scalar-g1-c0`), which **all twelve lines reuse** | measurement, not inspection: counted abandonments per line and asked why the weakest model's rejects were killing the strongest model's candidates | `poll.permanently_rejected_specs` + `poll.spec_local_root`, scoping to each spec's OWN sub-root; replayed over the real RUN 1 archive it condemns exactly **59** and rescues exactly **439** | **A resource shared by N concurrent lines, keyed by an id unique only within ONE line, is a collision waiting to happen.** ~2,870 tests all exercise a single line, so no test could see it |
| **D2** | **Reflection starvation** — only **10 of 241** archived prompts carried the reflection preamble, all `distributional` | RUN 1 | a *consequence* of D1: `prev_block` is set only when a generation produces an accepted candidate, so wiped generations made the next generation fall back to the **initial** prompt | audited the archived prompts directly rather than trusting the loop's design | fixed by D1 | **A bug can silently disable the mechanism under study.** H2's whole object is the reflection loop; it was off and nothing alarmed. Hence the standing `reflection_guard` monitor |
| **D3** | **Leaked ssh children** — 13 alive, 8 of them 1.1–6.7 h past their own 3600 s timeout; transport failures climbed **5.2 % → 55.3 %** over ten hours | RUN 1 | both tar-over-ssh pipes put `proc.wait()` **after** the `try/finally`, so a failed pull returned without reaping | process-table sampling during a degradation, then a causal test: reaping the 13 took failures **53.3 % → 16.3 %** and the counter 62 → 36/240 | `submit.reap(proc, grace=…)` at both sites, `drained` flag distinguishing the two grace periods | **Degradation that compounds over hours is a leak until proven otherwise.** And: prove causation by *acting* on the suspect, not by correlating |
| **D4** | **Watchdog, backup and supervisor hardcoded RUN 1's roots** | RUN 1→2 | paths were literals, not parameters. The watchdog was worst: it restarted dead lines with **defaults** every 300 s, so a relaunch on new roots would have been silently poisoned by lines pointed at the old ones | caught while planning the RUN 2 relaunch — *before* it could do damage | `-OutDir` / `-RemoteRoot` (and `-SrcRoot`) on every entrypoint; defaults still reproduce RUN 1 exactly, so nothing silently changed meaning | **An automatic restarter is a second launcher.** Anything that can start a line must take the same parameters as the thing that started it |
| **D5** | **C3 gate collision** — `TIER1_APPROVED` and `tier1_integrity.json` were single SHARED files, and passing the gate **CONSUMES** the approval (`unlink`) | latent in RUN 1–2 | same class as D1: one file, twelve writers | found by sweeping for *every other* instance of D1's pattern instead of stopping at the one that hurt | scoped by `ClusterRun.line_tag()`, and now fails **CLOSED** | **When you find one instance of a defect class, enumerate the whole class.** One line could have eaten another's approval and walked into C4 unreviewed |
| **D6** | **No execution-quality floor on winner selection** — a candidate whose authored reward RAISED on half its steps (R66 fallback standing in) could be frozen and re-trained by the sealed leg | latent, all runs | selection was `max(val_fitness)`, full stop | the identification-validity audit: H2 requires arms to differ **only** in the authored reward — a 53 % fallback candidate is not the arm it claims to be | **R115**, registered pre-data under a fresh **v2.1** freeze: eligible iff `train_safe_default_count / train_safe_call_count < 0.10` | **An identification hole is a defect even when no test fails.** Measured over 613 records: 594 clean, 16 trace (<1 %), **3 severe** (53.66 %, 50.02 %, 39.40 %) |
| **D7** | **Fail-OPEN on a malformed batch result** — `res.get("ok", True)` | latent | a default that assumes success | code read during the D1 sweep | → `False` at both sites | **Never default a health check to healthy.** Every producer sets `ok` today, so behaviour is provably unchanged — which is exactly when it is free to fix |
| **D8** | **`stop_reason` captured but only WARN-logged** | all runs | it was never given a structured home | asked how the per-model authoring-reliability table would distinguish "the model failed" from "our cap truncated it" — and found it could not | persisted on every `record_spend` row, `None` included | **A field that exists only in a log line does not exist for analysis.** Truncation arrives at the sandbox as `defines no callable named 'reward'` — identical to genuine model failure |
| **D9** | **The 300 s transport stall** | all runs | **UNIDENTIFIED** — seven hypotheses tested and refuted (§18.3) | 55 process samples over 3 min: 8 ssh children, **none aged past 10 s**, while 300 s timeouts were being logged → **the wait is in the PARENT** | bounded 300 → **120 s**; `ssh_timeout_diagnostic` installed to settle it on the next occurrence | **Bound what you cannot yet explain, instrument it, and say plainly that it is unexplained.** It affects reconciliation latency only — no recorded number depends on it |

### 20.2 The mistakes that were MINE — process errors, and what they cost

Recorded because the next session inherits the habits, not just the code.

| # | what I got wrong | how it surfaced | the rule it produced |
|---|---|---|---|
| P1 | Measured the **wrong ssh client** — probed with Git Bash OpenSSH 10.2p1 while the drivers use `C:\Windows\System32\OpenSSH` 9.5p2 | the A/B came out meaningless | **Reproduce the exact call path**, binary included, before drawing a conclusion from a probe |
| P2 | Proposed `ConnectionAttempts`/`ConnectTimeout` as the transport fix | A/B tested over 3 paired rounds **before** applying: 8/72 control vs 9/72 treatment — **refuted** | **The tempting fix is often wrong.** Test it before you ship it; a plausible mechanism is not evidence |
| P3 | Reported a process as **GONE** when it was alive — PowerShell hashtable keyed by `UInt32`, looked up with `Int32` | re-ran with explicit `[int]` casts and got the opposite answer | **A negative result from a script you just wrote is a claim about your script first** |
| P4 | Said the suite was green when **`PYTEST_RC=1`** — read the background wrapper's exit code, not pytest's | caught on re-read of the log | **Always read `PYTEST_RC` from the log.** Never a pipe's or a wrapper's exit code |
| P5 | Produced a **false RED** in `test_cluster_bayes_chain` by editing `campaign.py` *during* a certification run — line numbers shifted under `inspect.getsource` | the failure did not reproduce on a clean re-run | **Never edit source during certification.** Record a source-tree hash **before and after** every run and require them identical |
| P6 | **Introduced a crash path** with R115 — a bare `raise` broke `run_arm_pipeline`'s documented "never raises for a no-winner arm" and would have hot-looped the supervisor at 600 s | found by reading the contract of the function I had just changed | **When you add a raise, re-read every caller's contract.** A fix that changes failure semantics is a new defect |
| P7 | Reported **"41 extrapolated sessions"** for the factor ladder — read the canonical raw file instead of the refreshed one the loader actually resolves | running the real loaders gave **21/1631** | **Run the loader, do not read the file it might have used** |
| P8 | **Overstated** §15.2's analysis obligation as UNMET when `information_gap.py` had read `prompt` first since the M14 fix (2026-07-05) | re-checked the source before writing it into the record | **Overstating an open risk is its own inaccuracy.** Verify, then state — in both directions |
| P9 | Put backtick/escape content in a bash heredoc **twice**, against a standing rule; the shell mangled it | verified nothing was corrupted (freeze hash matched), then redid it via the Write tool | **Structured file edits go through Write/Edit, never a shell heredoc** |
| P10 | A PowerShell process filter matched **my own shell** — the search string was in my own command line — so it killed itself, reported exit 255, and then reported "1 watchdog remaining" that was the next shell counting itself | the count did not fall to 0 no matter how many kills ran | **Any process query that greps command lines must exclude `$PID`**, or it will find and kill itself and lie about the result |

### 20.3 The single structural lesson

**All three collisions (D1, D5, and the 2026-07-19 `pending_specs` case the earlier audit fixed) are
one shape:** a resource shared by twelve concurrent lines, keyed by an identifier that is unique only
*within* one line. The suite cannot see it because every test exercises one line. The only reliable
detector is a **live invariant** — hence the standing `collision_guard`, which asserts that every
`permanent_node_reject` traces to its own sub-root and treats a single foreign one as a stop-the-run
regression.

**The second lesson, aimed at the write-up:** every one of D1–D9 was found by *measuring the running
system* — counting abandonments per line, sampling the process table, replaying the archive, running
the real loaders. None was found by reading code alone. That is worth a sentence in CH4's execution
narrative, and it is the honest answer to "how do you know the campaign machinery was correct?"

---

## 21. RUN 4 — the launch-ready state, handed to a fresh session

RUN 4 is **prepared but deliberately NOT launched**: Tamer's instruction is that a new session takes
it from there, prepares deeply, and launches. This section is the state that session inherits.

### 21.1 Certified state at handoff

| item | value | how verified |
|---|---|---|
| freeze | **v2.1 `3ca6f01ab7724d47bd5d01bc9e73b4d3150c049e1048dd86a864b400a230432f`**, tag `prereg-v2.1` | `freeze.py --check` → RC=0, recorded hash **MATCHES** |
| full suite | **2,870 passed · 3 skipped · 0 failed** | `PYTEST_RC=0` read **from the log**; source-tree hash `cc3f758b…` recorded **identical before and after** the run |
| lint | clean | `ruff check src scripts tests` → All checks passed |
| HEAD | `18dead8`, pushed to `origin/backup-2026-07-28` | `git rev-parse` + remote head confirmed |
| cluster deploy | `~/llmrp` = `ce27dfc5fb7503e8673b544e5498cd20ce34de64` | **no re-deploy needed** — every fix is laptop-side (`run_one` imports none of `poll`/`driver`/`submit`/`campaign`) |
| cluster jobs | **20**, all `l16xx` p6-ladder | post-halt `qstat` |
| local processes | **0** campaign processes | inventory excluding `$PID` |
| budget | Anthropic $31.96 · OpenRouter $19.31 (Tamer's console, 2026-07-28); $16.75 consumed across RUNs 1–3 | RUN 4 projection ≈ $18.72 / $5.28 |

### 21.2 The launch commands — both root flags are MANDATORY

Every entrypoint **defaults to RUN 1's paths**, so omitting a flag silently rejoins the old run:

```
powershell -ExecutionPolicy Bypass -File scripts\mode_d_launch.ps1 `
  -OutDir outputs\campaign_cluster_run4 -RemoteRoot ~/Scratch/llmrp4
```

then, with the **same** roots:

```
scripts\mode_d_watchdog.ps1 -IntervalSecs 300 -OutDir outputs\campaign_cluster_run4 -RemoteRoot ~/Scratch/llmrp4
scripts\campaign_backup.ps1 -SrcRoot outputs\campaign_cluster_run4 -RemoteRoot ~/Scratch/llmrp4
python scripts/sentinel.py outputs/campaign_cluster_run4 --watch --interval 300
python scripts/allocation_advisor.py --host myriad --watch 900 --archive-root outputs/campaign_cluster_run4
```

**STOP LEVER**: create `outputs\campaign_cluster_run4\STOP_CAMPAIGN`.

### 21.3 The pre-launch gate — §12.3's 20 items, every one EXECUTED

Re-run rather than inherited, because the repository moved since §12.3 was written: full suite with
`PYTEST_RC=0` read from the log and a tree hash identical both ends · `freeze --check` RC=0 with the
hash MATCHING · `ruff` clean · `preflight --gpu 0` 14/14 GO · `--dry-run` RC=0 on **all five** line
invocations · every process verified on the RUN 4 roots and **0 on the old ones** · the remote root
virgin · no stale `STOP_CAMPAIGN`.

### 21.4 Monitors to re-arm on the RUN 4 root

`close_watch` (180 s) · `collision_guard` (**stop the run** on a single foreign reject) ·
`reflection_guard` (<80 % of generation>0 candidates shown a reflection block = the mechanism is
starving) · `transport_guard` · `truncation_guard` · `sentinel --watch`.

> ⚠ **SUPERSEDED 2026-07-28 — this row used to end "the scripts live in the previous session's
> scratchpad; copy them into the new session's scratchpad rather than depending on the old path."**
> That instruction was a symptom, not a solution. The guards now live IN THE REPO as
> **`scripts/campaign_guards.py`** (§23.6), so there is nothing to copy and nothing to lose:
> `python scripts/campaign_guards.py outputs/campaign_cluster_run4 all`, exit 2 = stop the run.

### 21.5 What RUN 4 must watch that RUN 3 could not

1. **`ssh_timeout_diagnostic`** — the first occurrence settles D9. If `child_already_exited=True`, the
   wall-clock was spent in the parent's pipe read and the remaining hypothesis (Windows pipe-handle
   inheritance) is confirmed; if `False`, the remote command genuinely hung and the search moves
   cluster-side.
2. **`stop_reason` in the spend ledger** — RUN 4 is the first run where the field exists. It should be
   `end_turn`/`stop` throughout; anything in `{max_tokens, length, refusal, content_filter}` means our
   cap is contaminating the authoring-reliability finding and must be reported as such.
3. **The 1,000-job / 4,000-core saturation** — never observed on this account. RUN 3 held 365 jobs /
   827 slots. Past rung 30 it should saturate; if it does not, the makespan model is wrong and the
   forecast needs redoing from the measurement, not the model.

---

## 22. THE RUN 4 PRE-LAUNCH SESSION — what a fresh pass found that the handoff did not

Written 2026-07-28 evening by the session Tamer designated to "prepare deeply and launch". The
handoff was accurate and the gate it prescribed was the right gate. What follows is what re-running
every item **by execution** turned up anyway — one new machine defect, three corrections to recorded
figures, and one guard that would have watched nothing.

**The method that produced all of it is the same one §20.3 names:** measure the running system.
Every item below came from reading the RUN 1–3 *archives* and the *live cluster*, not from reading
code or trusting the previous session's summary.

### 22.1 D10 — the spend ledger mis-attributed EVERY non-Anthropic call

| | |
|---|---|
| **what** | All **1,361** spend rows across RUNs 1–3 are stamped `provider: "anthropic"` — including rows whose `model` is plainly an OpenRouter id: `deepseek/deepseek-v4-pro` (147), `openai/gpt-5.6-luna` (175), `google/gemini-2.5-flash` (149), `qwen/qwen3.6-27b` (124), `nvidia/nemotron-3-super-120b-a12b` (108), `moonshotai/kimi-k3-20260715` (99), `qwen/qwen3.5-9b` (94), `z-ai/glm-5.2` (59) |
| **root cause** | Both production authors — `campaign._build_cluster_author` and `parallel._drive_llm_arm` — construct `LLMClient({"model": …, "spend_ledger": …})` with **no `provider` key**, so `client.py:952`'s `cfg_get(cfg, "provider", "anthropic")` **default** was stamped on every row |
| **NOT affected** | **Routing.** `build_transport` is called with the real `opts["provider"]`, so the legs genuinely reached OpenRouter. No API call went to the wrong vendor, no model is misidentified (`model` is correct throughout), and **no recorded scientific result is touched** |
| **IS affected** | Cost attribution **by provider** — a reported artifact. Any per-provider cost table would have charged ~$5 of OpenRouter spend to Anthropic, and a budget monitor keyed on provider would track the wrong balance |
| **how found** | computing the provider split of RUNs 1–3 to check the RUN 4 headroom, and noticing that a run using eleven models across two vendors reported **one** vendor |
| **why it survived** | `test_realized_cost_recorded_per_call` asserts `row["provider"] == "openrouter"` — but it **passes `provider` in explicitly**. It proves the client records what it is GIVEN, while production gave it nothing. A mechanism test over a call-site defect |
| **fix** | `"provider": opts["provider"]` threaded at both sites, with two tests: one behavioural (`_build_cluster_author` → `llm.provider`, then a real ledger row) and one **structural AST lock** asserting every production `LLMClient(` cfg carries the key, since `_drive_llm_arm` is too heavy to instantiate. **Both proven to FAIL against the pre-fix code** with the exact diagnostics they were written to give |
| **freeze** | **UNMOVED** — `3ca6f01ab7724d47…` still MATCHES. Neither file is hash-bound, so RUN 4 executes the identical registered v2.1 design |

**The lesson, and it generalises past this bug:** *a unit test that supplies the input the production
call site forgets cannot detect that the call site forgot it.* Test the wiring, not only the widget.
This is the same shape as D1 (tests exercise one line; the defect needs twelve) and R106 (a ratified
decision that reached no config): **our tests check that a value is honoured, and are blind to a
value never passed.**

### 22.2 Corrections to figures recorded in §19

Each was found by re-deriving the number rather than restating it. None changes RUN 3's verdict —
the fixes held, 0 spurious abandonments stands — but the record must be right.

| § | recorded | actual | why the difference |
|---|---|---|---|
| 19.1 | "881 INFO · 41 WARNING · **0 ERROR** across all twelve driver logs" | **7,776 INFO · 798 WARNING · 1 ERROR** | The driver logs carry **two** logging formats (`\| WARNING \|` and `TIMESTAMP WARNING logger:`). The recorded count matched only the first. The single ERROR is in the *second* format, which is why it read as zero |
| 19.1 | "41 transport warnings, **max 2 consecutive**" | **647 timeout events, max 5 consecutive** (621 at the 120 s bound) | same cause; the timeout WARNINGs are nearly all in the uncounted format |
| 19.1 | "0 ERROR" | the 1 ERROR is **legitimate** | it is `driver.py:446` announcing the ONE genuine, correctly-scoped permanent reject on `leg5` (haiku) — the system reporting a real event, not a fault |

**What this changes for RUN 4.** RUN 3's transport was materially noisier than recorded: ~15 timeout
events per line per hour, each costing up to 120 s of a batch thread. That is D9, still fully
present, and it remains throughput-only — no recorded number depends on reconciliation latency. It
also means the `ssh_timeout_diagnostic` will fire early and often, so **D9 should be settled within
the first hour of RUN 4** rather than eventually.

### 22.3 The collision guard would have watched nothing

The `collision_guard` was written against `batches/*/*.permanent.jsonl`. The real path is
`driver.py:346` → **`batches/<base_name>.permanent.jsonl`**, flat. The glob matched zero files, so
the guard reported `ledgered_abandonments=0 foreign=0` on the RUN 1 archive — **a clean bill of
health for the run the defect invalidated.**

It was caught only by **falsifying the guard against data where the defect is known to exist**. With
the path corrected the guard reports, on RUN 1, `ledgered_abandonments=498 foreign=439` — **exactly**
the 498 abandonments and 439 spurious ones the independent damage audit measured and the fix replay
rescues. Three independent routes now agree on 439. On RUN 3 it reports 1 abandonment, 1 marker,
`foreign=0`.

> **A monitor is code, and unfalsified code is unverified code.** A guard that cannot fire is worse
> than no guard: it manufactures confidence. Every guard here was run against RUN 1 (defect present)
> and RUN 3 (defect absent) before being trusted.

### 22.4 The deployed tree — the inherited claim was true, but narrower than it read

§12.3 item 10 recorded "**NONE** of poll/driver/submit is reachable → no re-deploy". Recomputing the
AST import closure from `run_one` confirms that clause exactly — but three **changed** files *are*
reachable: `src/llm/client.py`, `src/llm/spend_ledger.py`, `src/selection/fitness.py`. The
conclusion survives for a more precise reason:

* all three diffs are **purely additive** (a new kwarg, a new ledger field, a new exception class);
* `held_out_fitness` — the only fitness symbol `train_candidate` imports — is **unchanged**; R115
  added `NoEligibleWinnerError`, a class, touching no code path;
* `LLMClient` is imported only inside `_drive_llm_arm`, which is **laptop-side** and which `run_one`
  never calls.

**The tree was refreshed anyway, and this is the reasoning.** RUN 3 was halted for exactly one
thing: processes a commit behind their own repository. A behaviour-equivalence *argument* is weaker
than byte identity, and every RUN 4 record stamps `deployed-archive:<sha>` as its code provenance —
so a stale tree means a reviewer gets two answers to "what code produced this?".

* **Before refreshing, the deploy was verified to have ZERO drift** from its stated commit: a full
  2,645-file sha256 manifest against `git archive ce27dfc5`. (A first attempt reported 214 differing
  files; that was the comparison hashing the **Windows working tree** — CRLF — against `git archive`
  LF blobs. A surprising negative result is a claim about your script first.)
* Refreshed by `rsync` from a staged `git archive HEAD`, which writes each file to a temp name and
  **renames it into place** — atomic on POSIX, so the 20 running `l16xx` ladder jobs could only ever
  see a whole old file or a whole new one. `--delete` deliberately not used.
* Old tree backed up to `~/llmrp_backup_ce27dfc5.tar.gz` (8.0 M) first.
* **After: `DIFFER=0  MISSING=0`** across all 2,648 tracked files; `GIT_COMMIT` stamped
  `b445f4e3450017d9643525261841b1ca497f8962`; `run_one` re-verified importable inside the container;
  **all 20 ladder jobs still running.**

### 22.5 Gate 14 was passing on a check that could not fail

§12.3 item 14 verified the cluster venv with `ls ~/venvs/llmrp/bin/python` → "OK". That path is a
**dangling symlink on the login node** (→ `/usr/local/bin/python`, which exists only *inside* the
Apptainer container), and `ls` succeeds on a dangling symlink. Re-done by **executing** it:

```
apptainer exec ~/python311.sif ~/venvs/llmrp/bin/python -V   -> Python 3.11.15
  numpy 1.26.4 · torch 2.6.0+cu124 · sb3 2.8.0 · gymnasium 1.2.3 · pandas 2.3.3
PYTHONPATH=~/llmrp ... -c "import src.cluster.run_one"       -> RUN_ONE_IMPORT_OK
```

### 22.6 The RUN 4 budget headroom, recomputed

The record quotes Anthropic **$31.96** / OpenRouter **$19.31** from Tamer's console at ~13:55 —
which **pre-dates RUN 3** (16:19–19:45). Subtracting RUN 3's ledgered spend:

| provider | quoted | − RUN 3 | available | projected | margin |
|---|---|---|---|---|---|
| Anthropic | $31.96 | $3.81 | **$28.15** | $18.72 | **50 %** |
| OpenRouter | $19.31 | $0.00 | **$19.31** | $5.28 | **266 %** |

⚠ Two caveats, both material. **(1)** Because of D10 the ledger's provider split is not usable as
recorded — the table above charges all of RUN 3 to Anthropic, which is the *conservative* direction
(true Anthropic spend was lower, so real headroom is larger). **(2)** §12.1's standing rule applies:
**the ledger is an ESTIMATE**, every row stamped `estimated-from-planning-prices` or `realized`, and
it once ran $10 pessimistic against the console. Quote it as an estimate, never as billed spend.

### 22.7 The pre-launch gate as re-executed

Every item run fresh; nothing inherited.

| # | check | result |
|---|---|---|
| 1 | full suite | **2,870 passed · 3 skipped · 0 failed**, `PYTEST_RC=0` read from the log; tree hash `b95d7564…` identical both ends. *(This certification PRE-DATES the D10 fix — the one covering it is §22.10, and the one covering D11 is §23.10.)* |
| 2 | new tests falsifiable | both D10 tests **FAIL** against pre-fix code with their intended diagnostics |
| 3 | collision fix on real data | guard replay: RUN 1 `foreign=439` of 498 — matches the independent audit exactly |
| 4 | freeze | `--check` **RC=0**, `3ca6f01ab7724d47…` **MATCHES**, and still matches after the D10 fix |
| 5 | lint | `ruff check src scripts tests` → All checks passed |
| 6 | pre-flight | `preflight.py --gpu 0` → **14/14 OK, VERDICT: GO** |
| 7–9 | wiring | `--dry-run` **RC=0 on all five** line invocations against the RUN 4 roots: core 9 arms/568 seeds/7 tiers, h3 1 arm/30 candidates, three legs 5 arms each. Tier sizes `[30,70,89,90,61,63,165]` sum to **568** and are exactly the increments of the registered ladder |
| 10 | node-side closure | recomputed and **refined** — see §22.4 |
| 11 | deployed tree | full manifest: 0 drift from `ce27dfc5`, then **refreshed to HEAD**, `DIFFER=0 MISSING=0` |
| 12 | RUN 4 remote root | `~/Scratch/llmrp4` **VIRGIN** (re-checked after the dry runs — they left no side effects on either root) |
| 13 | licensed gold | 10 files on ACFS; checksum verified locally by check 6 |
| 14 | cluster venv | **executed**, not `ls`-ed — see §22.5 |
| 15 | capacity | 20 jobs (all `l16xx`), `max_u_jobs 1000`, 1,010 G free on Scratch |
| 16 | campaign PS1s | all four: **0 parse errors, 0 non-ASCII bytes, no BOM** |
| 17 | leaked ssh | login-node process table: **no orphans**; 0 campaign processes locally |
| 18 | prior runs stopped | 0 campaign processes (inventory excluding `$PID`) |
| 19 | evidence preserved | RUN 1 **621 records** intact, RUN 2 and RUN 3 trees untouched |
| 20 | budget | see §22.6 |

### 22.8 Two entries in the §18.2 open-defect register are STALE — both are already closed

Re-checked rather than carried forward. Overstating an open risk is its own inaccuracy (P8).

| # | register says | actual |
|---|---|---|
| **K** | "`stop_reason` not persisted to the structured spend ledger … deferred to the next natural restart" | **CLOSED.** It landed in `18dead8`; §19.2 records it as one of the three fixes that halted RUN 3. The register was written before that commit and never updated. RUN 4 is the first run where the field exists — `truncation_guard` asserts every ledger row carries it, and treats an absent key as a STALE-DRIVER stop condition |
| **N** | "174 legacy `Co-Authored-By` trailers in pre-2026-07-26 history … needs a history rewrite + force-push" | **CLOSED.** Measured across **all 565 commits on every local ref: 0** attribution trailers. The 2026-07-26 rewrite held. The 36 commit bodies that merely contain the string "claude" are references to `CLAUDE.md`, to the model id `claude-opus-5` (the research *subject*), and to the removal work itself — none is an authorship claim |

**One cosmetic residue, and it is Tamer's call, not mine:** 2 of the 565 commits carry the author
name `abailey81` against Tamer's own email `t.ates232004@gmail.com` (`a3f6963`, `0e080dc` — the
2026-06 repo-unification pair). Not a Claude attribution; an old local `user.name`. Fixing it means
another history rewrite + force-push on a shared branch, so it is surfaced and left alone.

### 22.9 R115 and the arm contrast, re-derived rather than restated

Two load-bearing claims were reproduced from scratch, because a conclusion this central should not
rest on a previous session's summary of it.

**R115 is wired at every site and is effect-blind.** `select_winner` filters on
`train_safe_default_count / train_safe_call_count` against a ceiling **read from the
pre-registration** (`_winner_fallback_ceiling`, never hardcoded), records with no counters stay
eligible, and if every candidate is contaminated it raises `NoEligibleWinnerError` rather than
promoting one. `campaign.py:1370` catches it by TYPE → `no_eligible_winner`, distinct from
`no_winner`.

**The arms differ exactly as H2 claims.** Calling `build_block` with one fixed input set:

| arm | tail numbers | block |
|---|---|---|
| `scalar` | **0** | the scalar DSR alone (67 chars) |
| `scalar_cvar5` | **1** | + `CVaR 5%: -0.0480` (86) |
| `distributional` | **6** | the full tail block (275) |
| `placebo` | 0 real | six inert `+0.0000` reference constants (293) |
| `placebo_shuffled` | 6, **deranged** | set-equal to `distributional`, **not** text-identical (275) |

All six shuffled values moved off their own labels — a **true derangement**, not a partial shuffle.
The only number `placebo` shares with `distributional` is the scalar DSR itself, which every arm
receives by design, so there is **no tail leak**. The three six-line blocks are 275/293/275 chars,
keeping token count controlled across the contrast that matters.

### 22.10 Certification of the D10 fix

Recorded separately because the §22.7 row-1 certification pre-dates the fix and must not be read as
covering it.

| check | result |
|---|---|
| full suite | **2,872 passed · 3 skipped · 0 failed**, `PYTEST_RC=0` read from the log |
| count reconciliation | 2,870 **+ exactly the 2 new tests** = 2,872 — no test silently lost or added |
| source-tree hash | `17ce5fc5…`, **identical before and after** the run (366 files) — nothing moved mid-certification (P5) |
| falsifiability | both new tests **FAIL** against the pre-fix code, with the diagnostics they were written to emit |
| lint | `ruff check src scripts tests` → All checks passed |
| freeze | `--check` RC=0, `3ca6f01ab7724d47…` **MATCHES** — the fix touches no hash-bound file |
| blast radius | the archived `ProvenanceRecord` uses `self.model` and transport-derived fields and **never** `self.provider`, so `llm_calls.jsonl` and every candidate record are byte-unchanged in shape. Only the spend ledger's `provider` field changes, and only for the eight OpenRouter legs — the `anthropic` lines were already writing the correct value |
| stub path | `default_key_env` is total (a `.get` with a fallback, no raise), and `api_key_env` is consumed only in the lazy-transport branch production never reaches, so a `provider: "stub"` cfg cannot break Pass-A |

### 22.11 Further verification, beyond the inherited gate

Run because the instruction was to be certain, not to be finished. Each is an INDEPENDENT
re-derivation of something already believed true — the point is a second route to the same answer,
not a second reading of the same claim.

| what | how | result |
|---|---|---|
| **the licensed gold the CLUSTER reads** | sha256 of all four ACFS panel files vs the frozen manifest | **all four MATCH** (`7cf5d988…`, `18fcb242…`, `fe8cb27b…`, `8a16557c…`). The old default's decoy dir `~/Scratch/llmrp/inputs` confirmed **empty** |
| **the Anthropic key is live** | `scripts/author_smoke.py` | **OK in 2.4 s**, `claude-opus-5` — the confirmatory seat answers |
| **the OpenRouter key is live AND the R106 pin round-trips** | `leg_gates.py --leg gemini-2.5-flash --only smoke` (output to scratchpad, so it cannot contaminate gate resolution) | `smoke_ok: true`, **`reasoning_tokens: 0`**, `pin_roundtrip: verified` |
| **CRN — a chatty reward cannot shift agent init** | resolve kwargs, burn 1,000 draws on numpy-legacy + numpy-Generator + `random` + torch, resolve again | **byte-identical**; `seed` IS inside the SB3 kwargs; seed 8 ≠ seed 7 (guards against a vacuous test). Also re-confirms `train_steps=400000`, `buffer_size=50000`, `learning_starts=1000` live |
| **the leg roster across all four files that name it** | prereg `queue_order` vs `legs.yaml` vs `mode_d_launch.ps1` vs `mode_d_supervisor.ps1` | **all four identical**, `leg1..leg10` in order, 12 launcher lines — the R106 drift mode is closed |
| **the shared-root collision surface** | enumerated every path built from the shared archive root, then checked the real archives | **1,874 artifacts across two twelve-line runs (RUN 1 `batches/ledger/driver_status` = 776/417/150, RUN 3 = 463/10/58): every single one line-tagged, ZERO exceptions.** Empirical closure, stronger than the code-reading argument |
| **the killswitch cannot inherit RUN 1's incident** | `incident_blocks_submission(root)` reads `<root>/MYRIAD_KILL_INCIDENT.json` | root-scoped; RUN 4's root is fresh. (RUN 1's incident file still sits in its own tree) |
| **the watchdog cannot poison a fresh-root run** | read `mode_d_watchdog.ps1:76-81` | it passes **both** `-OutDir` and `-RemoteRoot` on every restart — the D4 fix is real |
| **freeze anchors** | `docs/prereg-v2.1.sha256`, `docs/prereg-v2.0.sha256`, both tags | v2.1 anchor matches the live hash; **v2.0's anchor preserved un-overwritten**; both tags present **on origin** (`prereg-v2.1` → seal `b9c2be5`), so the external anchor claim holds |
| **attribution hygiene** | all 565 commits on every local ref | **0** `Co-Authored-By`/"Generated with" trailers. The 36 bodies containing "claude" reference `CLAUDE.md`, the model id, or the removal work itself |
| **the laptop survives a 30-day run** | registry pause expiry vs the exogenous stop | Windows Update paused to **2026-09-10**, i.e. **14 days past the Aug-27 stop**; `RebootPending=False`; sleep disabled on AC. A forced reboot mid-run would kill all twelve drivers, so the window must be covered end to end — it is |
| **the STOP lever's real scope** | read every consumer | `STOP_CAMPAIGN` is honoured by the supervisors, watchdog and backup, and **NOT by a running driver**. It is a "do not restart" lever, not an instant brake: a full halt is STOP file → kill watchdogs → supervisors → drivers, in that order (§19.3). Worth knowing precisely *before* needing it in a hurry |

**Launch ordering, stated because getting it wrong duplicates every line.** The launcher must run
BEFORE the watchdog. The watchdog restarts any line whose `mode_d_supervisor` process is missing, so
starting it first would spawn twelve supervisors that the launcher would then duplicate. All twelve
supervisor processes exist immediately at launch — it is the *supervisor* that sleeps through the leg
stagger, not the launcher — so launcher → verify 12 up → watchdog is safe.

---

## 23. D11 — FIXING D1 ARMED A RUN-STOPPER, AND ONLY THE ARCHIVE COULD SHOW IT

**This is the most consequential finding of the pre-launch session, and RUN 4 would have hit it in
the first hours, overnight, on the weakest leg.**

### 23.1 The defect

`killswitch.classify_task_deaths` counts **every** epilogue row with `rc != 0` as a task death. If
≥ 8 deaths land across ≥ 4 distinct hosts inside a 300 s window and none is walltime-proximate, the
verdict is `admin_kill` → `retreat`: it writes `MYRIAD_KILL_INCIDENT.json`, and
`incident_blocks_submission` then raises on **every batch of every one of the twelve lines** until a
human clears the file.

But `run_one.main` ends with `return 0 if n_ok == len(rows) else 1`, and its own comment records
that a sandbox/contract reject "surfaced as a bare rc=1". **So an LLM writing reward code that fails
the sandbox — the phenomenon this study exists to measure — produces exactly the signature the
detector calls an administrative qdel:** fast (≈5 s), multi-host, bursty.

### 23.2 Why it is worse AFTER the D1 fix, not better

| | |
|---|---|
| RUN 1's worst 300 s burst of `rc=1` deaths | **7 deaths across 6 hosts** — ONE under `MIN_DEATHS=8`, already past `MIN_DISTINCT_HOSTS=4` |
| how much of RUN 1 actually reached a node | **61 %.** 621 records + 59 genuine rejects = **680 of ~1,119** candidate slots; the collision suppressed **439 (39 %)** *unsubmitted and unjudged* |
| therefore | RUN 1 sat one death under the threshold **because it was broken**. Fixing D1 restores the full flow — **~1.65× the candidate stream** — so the reject burst gets denser and the threshold is crossed |
| the dominant source | `qwen3.5-9b`, measured gate-pass ~17 % ⇒ ~83 % reject **by design**; it produced 47 of RUN 1's 60 markers |

Measured on the real archive, per leg: `qwen3_5_9b` **47 rejects / 2 records = 96 %**, against
deepseek 3 %, gpt-luna 3 %, haiku 7 %, nemotron 9 %, glm 20 %, qwen3.6-27b 26 %, and sonnet / kimi /
gemini at 0 %. The capability gradient is the finding; the detector was reading it as an outage.

### 23.3 The division-of-labour hole that hid it

`ledger.host_task_counts` **already excludes** `rc=1` from the bad-node detector
(`_NOT_A_NODE_FAULT_RC = {1, 126, 137, 143, 152}`), with a comment deferring such codes to
"`killswitch.classify_task_deaths`, which already owns them". The killswitch, in turn, counted
`rc=1` as an unexplained death. **Neither owner treated it as what it is** — our own application
verdict on the model's code.

### 23.4 The fix, and why it cannot weaken the detector

`_APPLICATION_EXIT_RC = {1}` is filtered out of the death population before the burst test.

This is not a trade-off. **An administrative `qdel` cannot produce `rc=1`**: it terminates by signal
(`rc` 137/143) or the job never starts (126/127). A clean `1` can only come from our own
`return 1`, so it carries no evidence about administrative action in either direction — including it
could only ever generate false positives. Transient application failures remain fully handled: the
driver retries them and ledgers `retries_exhausted`, and permanent ones leave a `_rejects` marker.

Excluded is **not** silent: a `killswitch_APPLICATION_EXITS_EXCLUDED` WARNING names the count and
host spread, so a mass self-inflicted failure — the one signal that would otherwise fall between the
two detectors — stays greppable.

*(On its frequency, checked rather than assumed: an earlier draft of this section called the warning
"rate-limited", which it is not — there is no throttle in the code. It fires from `_enforce_kill_switch`,
which runs on the **shared** pull path, itself throttled to `min_pull_interval` 60 s and shared across
all twelve lines rather than per-line. Combined with the 300 s window, that means it can only speak
about rejects from the last five minutes, and rejects arrive in bursts at generation boundaries with
~8 h of training between them. So it is naturally occasional, not a stream. The wording was corrected
rather than a throttle added, because adding one would have meant editing source during a running
certification — the P5 rule — to fix a problem the measurement says does not exist.)*

### 23.5 Falsification

Three new tests, all proven to FAIL against the pre-fix code, then the file restored
**byte-identically** (sha256 compared before and after):

| test | pre-fix result |
|---|---|
| a burst of authoring rejects is NOT an admin kill | **FAILED**: `classified 'admin_kill'/'retreat' — this hard-blocks submission on every line until a human intervenes` |
| rejects must not be counted as evidence alongside a real kill | **FAILED**: `assert 40 == 10` — the 30 rejects were being counted with the 10 genuine signal deaths |
| the exclusion is logged, never silent | **FAILED**: no such warning existed |

**And then re-verified against the REAL epilogue rows, not fixtures** — replaying RUN 1's actual
deaths through the fixed classifier:

| replay | verdict |
|---|---|
| all **50 real `rc=1` rejects**, across **37 hosts**, packed into one 300 s window (the shape a denser RUN 4 flow produces) | **`ok` / `continue`** — "no infrastructure task deaths in the window (50 application exit(s) excluded)". Pre-fix this is unambiguously an admin kill: 50 ≥ 8 deaths, 37 ≥ 4 hosts |
| the real **24 `rc=126` deaths across 23 hosts** (the previous session's own `qdel`) | **`admin_kill` / `retreat`** — the detector still detects |
| both together | `admin_kill`, **`n_deaths=24`, not 74** — rejects do not pad the evidence for a genuine kill |

The pre-existing `test_any_nonzero_rc_counts_as_a_death` was **corrected, not deleted**: it keeps
asserting retreat for 137/143/127/255/126, and `rc=1` moved to a test asserting the opposite. The
stale premise in the constants' own comment — *"8 tasks dying across 4 nodes inside 5 minutes has no
benign explanation"* — was rewritten, because there is now a documented benign explanation and it is
a registered deliverable.

### 23.6 The guards now live IN THE REPO — `scripts/campaign_guards.py`

§21.4 told the next session to "copy them into your own scratchpad rather than depending on the old
path". That instruction is a symptom: **a standing monitor that exists only in one operator's temp
directory is not a standing monitor**, and the guards are the only detector for the defect class
that invalidated RUN 1. So they are committed.

Six guards, one entry point, exit code 2 = stop-the-run:

| guard | asserts |
|---|---|
| `collision` | every ledgered `permanent_node_reject` traces to a marker in its OWN sub-root |
| `reflection` | ≥80 % of generation>0 candidates were actually shown a reflection block (D2) |
| `truncation` | 0 provider-confirmed truncations **and** every spend row carries `stop_reason` (a missing key = a driver running pre-`18dead8` code — the ambiguity that halted RUN 3) |
| `transport` | log levels across BOTH formats, timeout events, worst consecutive-failure depth, and the `ssh_timeout_diagnostic` verdict that settles D9 |
| `rejects` | per-model reject rate against each model's **own** measured baseline — the FINDING/DEFECT discriminator |
| `status` | records, authored rewards, and spend by line (the canary shield shows as `c1 = $0.00`) |

Falsified against real data before being trusted, and re-verified after every edit: on the RUN 1
archive `collision` returns **RC=2 with `foreign=439`**; on RUN 3 it returns **RC=0**.

### 23.7 Two monitoring inputs are ROOT-LEVEL and carry the previous runs' data

The same shared-state class as D1/D5/D11, found by asking where each monitor's inputs come from:

```
telemetry.py:352  _STATE_PATH = <repo>/outputs/allocation_state.json
telemetry.py:353  _LOG_PATH   = <repo>/outputs/myriad_telemetry.jsonl
```

Both are **hardcoded at the outputs root**, not scoped by run root, and both hold RUN 1–3 data:
`myriad_telemetry.jsonl` carries **34 samples spanning 00:16 → 18:36 on 2026-07-28** (all three
runs), and `allocation_state.json` holds a GPU-era plan (`search_pool: "L"`,
`seed_pool_blocks: "L:0-19,EF:20-29,…"`) with `lane_expected_cores: 2438`.

**Consequence, and why it matters more than it looks.** These feed `capacity_accumulation`, which
divides the measured late-mean cores by the DECLARED forecast. Computed over foreign samples and
against a foreign forecast, that verdict is simply wrong — and it is exactly the check §21.5 item 3
relies on to answer the one open operational question RUN 4 exists to settle: *does the account
actually saturate to ~1,000 jobs / ~4,000 cores?* A polluted input does not make the monitor loud,
it makes it **confidently wrong**.

**Not a code change.** Both files are advisory, feed no submission decision, and the advisor rewrites
`allocation_state.json` on its first 900 s cycle. **Both are archived aside at launch** (renamed,
never deleted — they are RUN 1–3 evidence) so RUN 4's capacity measurement starts from zero.

### 23.8 EXPECTED OPERATIONAL EVENT — weak legs may stop at the C3 review gate

Not a defect; recorded so it is not mistaken for one at 2 a.m. The C3 gate reads **only**
`health_ok = all_complete and crn_consistent and not mixed_winner_units` — an effect-blind
execution-health census (hashes and completeness, never a performance value). A line whose arm
produced **no eligible winner** can leave a test unit incomplete, and the gate then **stops that line
before the expensive C4 sweep** and waits for an explicit human approval.

That is the conservative, correct behaviour, and on the weakest legs it is a plausible outcome of
the study rather than a machine fault: `qwen3.5-9b` archived **2 records against 47 rejects** in
RUN 1. **A leg that cannot author a usable reward is a FINDING**, and R115 adds `no_eligible_winner`
as a distinct outcome from `no_winner`.

**To clear it:** read `tier1_integrity_<line_tag>.md`, then create
`<read_root>/TIER1_APPROVED_<line_tag>` — the file is **staleness-checked** (an approval that
predates the report it claims to approve is IGNORED) and **consumed on passage** (`unlink`), so each
gate passage needs its own explicit approval. Both are per-line since the D5 fix; an unqualified
`TIER1_APPROVED` is now ignored rather than silently passing an unreviewed line.

### 23.9 ⚠ READ BEFORE APPLYING THE "PROCESSES A COMMIT BEHIND" RULE TO RUN 4

RUN 3 was halted because **CODE** fixes landed after its drivers started. That rule must not be
applied mechanically to RUN 4, because the situation is different in the way that matters.

**RUN 4's executing code is `b9e6df5` on BOTH sides** — the laptop drivers started from it, and the
cluster tree was verified byte-identical to it (`DIFFER=0 MISSING=0` over 2,649 files) *before*
launch. Commits after `b9e6df5` on this branch are **documentation only** (`docs/HANDOFF.md`,
`docs/CAMPAIGN_EXECUTION_RECORD.md`, `CHANGELOG.md`), which is the standing obligation to document
as it happens — not a code drift.

**The test to apply is therefore `git diff <running-sha> HEAD -- src scripts config prompts`, not
`git rev-parse HEAD`.** If that returns nothing, the run is executing exactly the code it claims to.
If it returns a source file, apply the RUN 3 rule and stop.

### 23.10 Certification of the D11 fix — the tree that actually launches

| check | result |
|---|---|
| full suite | **2,875 passed · 3 skipped · 0 failed**, `PYTEST_RC=0` read from the log |
| count reconciliation | 2,870 (pre-D10) → **2,872** (+2 D10 tests) → **2,875** (+3 D11 tests). The parametrised `rc` case kept 5 params — `1` was swapped for `126`, not removed — and adding `scripts/campaign_guards.py` added NO case, because `test_cli_help_strings` loops over the CLI paths inside one test rather than parametrising them. **Predicted 2,875 before running it; got 2,875** |
| source-tree hash | `86cfe11e…` (367 files), **identical before and after** — nothing moved mid-certification (P5) |
| lint | `ruff check src scripts tests` → All checks passed |
| freeze | `--check` RC=0, `3ca6f01ab7724d47…` **MATCHES** — neither changed file is hash-bound, so RUN 4 runs the identical registered v2.1 design |
| production-code footprint, whole session | **two `provider` kwargs** (D10, `campaign.py` + `parallel.py`) and **one filter block** (D11, `killswitch.py`). Everything else is tests, one standalone monitoring script, and documentation |

### 23.11 HOW TO DEPLOY TO THE CLUSTER — the full-tree extract is the wrong tool

Operational, and it will recur. The deploy path documented everywhere is
`git archive HEAD | ssh myriad tar -x -C ~/llmrp`. On a **contended login node** that is impractical:
extracting the 2,649-file tree was moving **~40 files/minute** (94 files in the first minutes), i.e.
an hour-plus, while the whole point was to update **five** files. The first refresh of the night ran
to completion only because the node happened to be quieter.

**What to do instead when the deployed commit is already close to HEAD:**

1. `git diff --name-only <deployed-sha> HEAD` — usually a handful of files.
2. Copy those paths out of an extracted `git archive HEAD` (**not** the working tree — on Windows it
   is checked out CRLF and every text file would mismatch the LF blobs the cluster holds; a first
   manifest attempt reported 214 spurious differences for exactly this reason).
3. `tar` just those, ship, extract to a staging dir, and `mv` each into place — a rename within one
   filesystem is atomic, so a running job's lazy import sees a whole file either way.
4. Stamp `GIT_COMMIT` atomically (temp + `mv`).
5. **Prove it the same way a full deploy is proven**: re-run the full sha256 manifest against
   `git archive HEAD` and require `DIFFER=0 MISSING=0`. The shortcut is in HOW the bytes get there,
   never in whether they are verified.

Killing the half-finished extract was safe because it dies **before** its rsync stage: verified after
the kill that `GIT_COMMIT` still read the old sha and the file count was unchanged, i.e. the deploy
tree had not been touched at all.

### 23.12 The sentinel's global gate-failure rate is expected to sit at WARN/CRIT — that is not a fault

`check_gate_failure_rate` (warn 10 %, crit 40 %) was calibrated on the prototype's ~2.5 %, which was
**one strong model**. Across an eleven-model capability gradient containing a deliberate ~17 %-pass
anchor, the aggregate will sit above warn for the whole run. It is **advisory** — it blocks nothing —
so the code is left alone rather than churned before launch, but the interpretation rule matters: a
permanently-on CRITICAL is how an operator learns to ignore a panel. **Read the per-model reject
rates instead** (`run4_watch.py <root> rejects`), which flag a leg only when it does far worse than
its own measured baseline. `qwen3.5-9b` at ~83 % reject is the study working; `deepseek` at 83 %
would be the study broken.
