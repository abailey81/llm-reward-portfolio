# ★★★★ DECISION BRIEF FOR TAMER — everything that needs YOU, in one place (as of 08:05Z)

*Written because the night produced a lot of findings and the risk is now that the decisions get lost
in the volume. Each item states what it costs, what happens if you do nothing, and when it expires.
Nothing here is urgent-before-you-wake; two are urgent-before-C4.*

| # | Decision | Cost if you act | Cost if you do nothing | Expires |
|---|---|---|---|---|
| **1** | **A16 — can confirmatory node N2 reject via TOST?** Three artefacts disagree: the yaml says activation "rests ENTIRELY" on it; the hash-bound prose says TOST "does not determine the thesis"; the code implements superiority only. | A conversation with Okhrati. Either correct the yaml note (code + hash-bound prose already agree) **or** specify a valid disjunction — `min(p_sup, p_TOST)` is **not** valid. | Under the design's own *predicted* null branch **no α propagates and N3–N6 can never be tested**. And it **blocks CH6's T2 table**, which cannot be computed until the rule is settled. | **Before the core H2 ladder unblinds.** Choosing after is a forking path. |
| **2** | **R106 amendment — "uniform reasoning-off" was never in force.** The pin was never sent on any Anthropic call; **claude-opus-5 ran with extended thinking on 315/315 confirmatory calls.** | Amend the registration to state what was executed; disclose. **Do not fix the run** — a half-and-half archive is worse than a uniformly-not-as-registered one. | A registered claim that is false, and `config/llm.yaml:30` asserts as measured fact something 315 calls contradict. | Before submission. **Identification is intact** — thinking is constant within every line (I verified per arm). |
| **3** | **The kimi "strongest pin" claim.** `legs.yaml:88`, R95, **and a brief already sent to Dr Okhrati** call the dated kimi slug "the STRONGEST PIN among the closed-class legs." It is the **only** leg whose identifier is not returned intact, and the dated slug is absent from OpenRouter's catalogue. | Correct the wording. The honest version — *effective pin is the floating alias, dated request and served identifier both recorded* — is a **better** exhibit. | A claim a referee can break in one API call, already in a supervisor's hands. | Before the PDF. |
| **4** | **Four "evidence-of-validity" quantities sit OUTSIDE the 35 registered keys** — per-arm PopArt (σ_max), the R115 census, the layer-3 pin verification, and wall-clock compute. All reach the write-up; none is gated. | A wiring task, **not** new computation (all four already exist or take seconds). But it changes the **registered reporting set**, so it is yours with the write-up lane, not a lane-level edit. | Each stays a number recomputed by hand — which is how three of tonight's defects survived. | Before the pre-submission gate. |
| **5** | **Spend: ~$81 projected against a registered $30.** R83 made the ceiling **advisory**, so this is **not a breach** and no data-collection decision was made on cost. **66 % of the remainder is one report-only leg** (qwen3.5-9b, 6.3 authoring events per accepted candidate). | Nothing, if you accept my recommendation: **do not truncate.** That leg's 17 % yield **is** the capability finding. | Realised spend lands ~2.7× the planning figure with no account attached. | Before CH6 is written. |
| **6** | **Should h3ss be capped at the rung the core line will reach?** It is consuming **85 % of throughput** while the confirmatory critical path gets 1.3 candidates/h, and **477 of its 507 seeds have no core counterpart** to pair with. | Pending ops' answer on whether core-line search is core-bound or authoring-bound. If authoring-bound, **disregard entirely**. | Possibly ~2,000 core-hours on seeds that can never pair — or nothing at all. | Before the core C4. |

**Two items are ops', not yours, and are already routed:** the **containment wrap** on the pair-test call
before the core C4 (it is the only stage outside every exception handler, and both existing pair tests
are currently unattended), and **leg4's h2_pair re-submission**.

**What does NOT need you:** everything else below is either verified clean, corrected, or queued
post-campaign with a stated reason.

---

# ★★★★★ A31 — THE CHANNEL WORKED. The fed tail reached the authored code, and the obvious aggregate HIDES it.

**The best science of the session, effect-blind, ready for CH6 now.** Detector is the **registered** one
(`scripts.inspect_rewards._construct_prevalence` over `_TAIL_CONSTRUCTS`), not a regex I invented. h3ss
excluded per A30. Authored **code** only — no sealed outcome read.

**The question nobody had asked.** The registered SQ1 instrument measures *responsiveness* — does a
**change** in the fed tail move the code across generations. It presupposes a prior question it never
answers: **did the tail-fed arms author more tail constructs AT ALL?** If not, an H2 null would be about
**non-uptake**, not about the value of tail information — a completely different finding.

### 1. The obvious aggregate is a trap

**ANY tail construct: distributional 70.4 % [64.8, 75.5] vs scalar 71.8 % [66.3, 76.7]** — almost exactly
coincident. Anyone computing that concludes the manipulation never reached the code. **That conclusion is
wrong**, and the reason is composition: `drawdown` (38.6 % vs 43.6 %, overlap) and `sortino_downside`
(44.1 % vs 47.7 %, overlap) are **generic risk constructs any competent author reaches for regardless of
what it was shown** — and they dominate the aggregate, washing the signal out.

### 2. The distinctive tail constructs track the feed — all three DISJOINT

| construct | tail-FED arms | NOT-fed arms | ratio | |
|---|---|---|---|---|
| **`cvar`** | **17.0 %** [14.3, 19.9] | **3.5 %** [2.2, 5.4] | **×4.9** | **DISJOINT** |
| **`quantile_tail`** | **20.9 %** [18.0, 24.1] | **8.5 %** [6.4, 11.2] | **×2.5** | **DISJOINT** |
| **`left_tail_mass`** | **5.9 %** [4.4, 8.0] | **1.4 %** [0.7, 2.8] | **×4.4** | **DISJOINT** |
| `drawdown` | 38.6 % | 43.6 % | ×0.9 | overlap |
| `sortino_downside` | 44.1 % | 47.7 % | ×0.9 | overlap |

**⇒ The channel H2 requires is OPEN, and this is the first time it has been measured.**

### 3. ★ The internal-validity check — the code tracks WHAT was fed, specifically

`cvar`-construct prevalence by arm:

| arm | what it was fed | `cvar` prevalence |
|---|---|---|
| **`scalar_cvar5`** | **CVaR-5 % explicitly, ONE value** | **29.0 %** [23.3, 35.5] — **highest of any arm** |
| `distributional` | a **six-value** tail vector | 11.6 % [8.3, 15.9] |
| `placebo_shuffled` | same vocabulary, **deranged** values | 11.8 % [8.1, 17.0] |
| `scalar` | no tail | 3.5 % [1.9, 6.4] |
| `placebo` | no tail | 3.4 % [1.7, 6.6] |

**The arm fed one specific CVaR number authors CVaR constructs at 2.5× the rate of the arm fed six tail
values.** The designer does not respond to "some tail stuff" — it tracks the specific statistic shown.

### 4. ★★ And format drives adoption while content does not

**`placebo_shuffled` 11.8 % is statistically indistinguishable from `distributional` 11.6 %** — same
vocabulary, **deranged values**, identical uptake. **At the code-authoring level, FORMAT drives construct
adoption and CONTENT does not.**

That is node N5's content-vs-format question answered at the **mechanism** level rather than the outcome
level, and it hands CH6 a specific, evidenced account should the outcome null hold: **the channel opened,
the vocabulary was adopted, and the information in the numbers did not differentiate the code.** A far
better story than "the tail did not help."

### Four caveats, stated because the result is strong enough to be over-read

1. This is construct **presence**, not correctness or **weight** — a program that mentions `cvar` may use
   it trivially or badly.
2. The detector is **static**; it cannot tell whether the construct is load-bearing in the returned reward.
3. `placebo_shuffled` matching `distributional` on **presence** says nothing about whether the **values**
   changed reward **behaviour** — that is what the outcome test measures, and I have not looked.
4. Prevalence is per-candidate **binary**, so an arm could adopt a construct more **often** or more
   **deeply**; this measures only the former.

**→ WRITE-UP: this is D1 material (mechanism · uncertainty · counterfactual) for the CH6 mechanism
section, ready now, effect-blind, with intervals, from the registered detector. It is also the answer to
the obvious examiner question — *"how do you know the manipulation reached the designer at all?"***

### ⚠ A31-bis — I RAN THE DISCRIMINATING TEST AND IT REVISED MY OWN HEADLINE

**What I tested.** `distributional` is fed **six** statistics — CVaR at 5/10/25/1 %, left-tail **mass**,
left-tail **skew** (read verbatim from a real archived prompt). `scalar_cvar5` is fed **CVaR-5 % only**.
So I counted which of those the **code** actually references.

**(1) `scalar_cvar5` references CVaR levels it was NEVER FED** — 0.10 in 40.8 %, 0.01 in 23.2 %, 0.25 in
14.2 %. **The designer supplies tail vocabulary from prior knowledge, not only from the feed.**

**(2) The two fed arms are barely distinguishable on level usage** — 1.34 vs 1.26 distinct levels; 0.05 at
42.2 % vs 47.4 %; 0.10 at 48.4 % vs 40.8 %. **⇒ WITHDRAWN: my claim that "the arm fed the LEAST engages
the tail MOST" as a general statement.** It holds for `cvar` **naming** and not for tail **computation**.

**(3) ★ THE RECONCILIATION IS MORE INTERESTING THAN THE ERROR.** The registered detector keys on
**NAMING** (the word `cvar` in the source); my regex keys on **PARAMETERISATION** (the numeric level). A
program can compute a conditional tail mean without ever writing "cvar", and can name a variable `cvar`
without a literal 0.05. **⇒ The arms differ in what they CALL it, not in what they COMPUTE.**
`scalar_cvar5`, fed the words *"CVaR 5 %"* attached to a number, adopts the **name** at 2.5× the rate —
while both arms compute tail quantities at similar rates and levels.

**(4) ★★ AND HERE IS WHERE THE SIX-VALUE BLOCK ACTUALLY TRANSMITS.** The only constructs separating the
two fed arms are the **two distributional-exclusive** ones: **left-tail SKEW 34.3 % vs 18.0 %** and
**left-tail MASS 3.2 % vs 0.0 %**. **The six-value block transmitted its two distinctive elements; its
four CVaR levels were redundant with vocabulary the designer already had.** That is a measured answer to
*"what did the richer feed actually buy?"*

**⚠ A CONFOUND I DID NOT NAME EARLIER AND SHOULD HAVE.** The fed block **ends with**: *"Exploration
directive 1/5: propose a reward DISTINCT from the other candidates this generation — **vary which
statistics you use**."* **Construct choice is partly PROMPT-DIRECTED.** Any "which statistic did it pick"
reading is contaminated by an instruction to vary — **including the depth result above.**

**Net: §A31's channel finding (fed vs not-fed, ×4.9 disjoint) is UNAFFECTED and stands. The
between-fed-arms comparison is revised to: naming tracks the feed, computation does not, and the richer
feed bought exactly the skew and mass terms.**

## ★★★★ A32 — THE TAIL CONSTRUCTS ARE **LOAD-BEARING**, and fed arms weight them in more often

**Closing the strongest objection to A31, which was my own caveat (1)/(2): construct PRESENCE says
nothing about WEIGHT.** A program mentioning `cvar` might use it trivially or park it in the components
dict where the agent never sees it.

**Method — AST dependency closure.** Parse each `reward_source`, locate `reward()`, build a
name → dependencies map from every `Assign`/`AugAssign`, take **the first element of the returned tuple**
(the `total` the agent actually maximises, per the contract), and compute the transitive closure of names
reaching it. Then ask whether any tail-named quantity is in that set. **This tests whether the construct
FEEDS THE REWARD or merely EXISTS IN THE FILE.**

| arm | mentions tail | reaches `total` | **load-bearing, conditional** |
|---|---|---|---|
| **distributional** | 256/277 (92 %) | 245 (88 %) | **95.7 % [92.5, 97.6]** |
| scalar_cvar5 | 192/212 (91 %) | 177 (83 %) | 92.2 % [87.5, 95.2] |
| placebo_shuffled | 193/211 (91 %) | 169 (80 %) | 87.6 % [82.2, 91.5] |
| scalar | 239/284 (84 %) | 207 (73 %) | 86.6 % [81.7, 90.4] |
| placebo | 190/237 (80 %) | 165 (70 %) | 86.8 % [81.3, 90.9] |

**⇒ Tail constructs are NOT decoration — when a program mentions one, it is load-bearing 87–96 % of the
time.**

**★ And a SECOND, INDEPENDENT axis of uptake:** distributional **95.7 %** [92.5, 97.6] vs placebo
**86.8 %** [81.3, 90.9] and vs scalar **86.6 %** [81.7, 90.4] — **both DISJOINT.** So fed arms do not
merely *mention* tail constructs more (A31); **their mentions are more often load-bearing.**
Unconditionally: **88 % of ALL distributional programs weight a tail term into the reward, against 70 %
for placebo.**

### Three caveats, the first a warning against conflating my own numbers

1. **⚠ My pattern here is BROADER than the registered `_TAIL_CONSTRUCTS`** — it includes
   `downside`/`drawdown`/`sortino`, which A31 showed do **not** separate fed from not-fed. That is why
   "mentions tail" reads 80–92 % here against 64–76 % for the registered detector. **Different
   definition, different number — never quote them side by side.** The **load-bearing ratio** is the
   finding; the mention rate under my pattern is not comparable to A31's.
2. The AST closure is **approximate** — it will miss values threaded through dict mutation, through
   `reward_state` across steps, or through control flow it cannot see. **A lower bound on reaching.**
3. **★ "REACHES" IS NOT "MATTERS."** A term entering `total` with coefficient 0.001 reaches it exactly as
   one with coefficient 10 does. This is weight in the **graph-theoretic** sense, not the **magnitude**
   sense. **Measuring magnitude is the natural next question and I have NOT done it** — stopping rather
   than extending a thread I have already had to correct twice.

**→ WRITE-UP: the load-bearing ratio converts *"the designer mentioned the tail"* into *"the designer put
the tail INTO the reward it was optimising"* — the version that actually answers the examiner's
question.**

---

# ANALYSIS LANE — 2026-08-01 (session 3: continuous results/output analysis + monitoring)

**Owner:** the ANALYSIS lane (third live session, opened 2026-08-01 ~01:10 UTC at Tamer's instruction:
*"extremely deeply and constantly analyse and monitor the campaign's results and the output… make sure
absolutely everything is strictly flawless, logical, meaningful, correct, and there are no issues with
science"*). Tamer went to sleep ~01:20 UTC and granted full freedom.

**Lane discipline.** This lane is **READ-ONLY over every other lane's holdings** — `src/ scripts/ config/
prompts/` (the drift fence), `docs/ops/**`, `outputs/**`, `docs/CAMPAIGN_EXECUTION_RECORD.md`,
`paper/**`. It owns exactly this file. Everything it finds is handed to the owning lane as a request,
never applied across a boundary. **Effect-blind throughout: no treatment arm's sealed-test outcome has
been read, and none of the analysis below requires one.**

**Method note (why these findings are trustworthy).** Every number below was re-derived first-hand from
the archive with a standalone script, not read off an instrument. Where an existing instrument reports
the same quantity, both are shown and reconciled. Where I could not establish a cause from the laptop
mirror, I say so rather than infer.

---

## 0. STATE AT OPEN (measured 2026-08-01 01:16 UTC, T+76h)

| quantity | value | source |
|---|---|---|
| lines live | 12/12 | cycle log |
| records (authority, fixed-depth) | 1,587 | `campaign_guards` glob |
| records (recursive) | 1,614 | `science_watch` / `results_audit` |
| spend | $40.71 | cycle log |
| cores | ~960 | cycle log |
| drift vs `RUNNING_SHA 16bb71b` | **0** | both `git diff` and `git status --porcelain` |
| freeze hash | `3ca6f01a` MATCHES | cycle log |
| `sci` | OK | science layer |
| R115 breaches | 13, BINDING | independently re-derived — **matches** |

---

## ★★★★ A1 — THE URGENT ONE: a confirmatory-shaped batch has been dead for 10.5 hours

**`leg4_leg_qwen3_5_9b_h2_pair_test` — the H2 treatment/control pair test, 60 units (2 arms × 30
seeds) — has produced ZERO records since 2026-07-31 14:44 UTC. That is 10 h 32 min as of 01:16 UTC.**

Evidence, all first-hand:

| fact | evidence |
|---|---|
| batch was created | `batches/leg4_leg_qwen3_5_9b_h2_pair_test_p01..p08`, mtime **Jul 31 12:12 local** |
| last driver activity on it | `driver_qwen3_5-9b.log`: `[leg4_leg_qwen3_5_9b_h2_pair_test] 0/60 done, 60 pending, round 1` at **2026-07-31 15:44:30 local** (= 14:44 UTC) |
| the blocking error | `RuntimeError: another driver (pid 34216) is already running batch 'leg4_leg_qwen3_5_9b_h2_pair_test.driver.lock'` |
| pid 34216 is NOT a driver | `Get-Process 34216` → `backgroundTaskHost`, **StartTime 2026-08-01 01:41 local** — a **recycled pid**, started long after the lock was written. The driver's staleness check tests pid EXISTENCE, not pid IDENTITY (**D20**). |
| output produced | `test_leg_qwen3_5_9b/distributional/` and `/scalar/` contain **only `_env`** — zero training records |
| the lock is now GONE | not present in `ls batches/*.lock` at 01:16 UTC |
| **but the batch still is not running** | the driver's rounds at 02:05–02:15 local list only `placebo_test`, `placebo_shuffled_test`, `scalar_cvar5_test`. **h2_pair is not re-enumerated.** |
| the trigger event | `supervisor_core.log`: `2026-07-31 15:47:11 driver exited -1` — a **campaign-wide driver crash at ~15:45 local** orphaned the locks whose pids were later recycled |
| contrast (a healthy one) | `leg9_leg_gemini_2_5_flash_h2_pair_test.driver.lock` mtime **01:56 local** (20 min old) with pack dirs created the same minute — that batch launched tonight and IS running |

**What I could NOT establish from the laptop mirror, and will not guess:** *why* the driver does not
re-enumerate the batch now that the lock is gone. That needs a live `qstat` + driver-state look on
Myriad. **→ OPS lane.**

> ### ★★★ SUPERSEDED 2026-08-01 01:55Z by the COORD lane's M19 — and their mechanism is the real one
>
> My account above ("wedged by a recycled pid, lock now gone, not re-enumerated") is **descriptively
> right and mechanistically incomplete**. Coord read the traceback at
> `driver_qwen3_5-9b.log:27084-27125` and found the actual cause:
>
> `run_campaign_tiered (campaign.py:1836)` → `run_test_leg (:1270)` → `run_batch (:356)` →
> `driver.run_batch (:267)` → `_acquire_driver_lock (:248)` → **`RuntimeError` propagating UNCAUGHT** to
> `sys.exit(main())` at `run_campaign_cluster.py:1464`.
>
> **The `"one unit must not sink the ladder"` handler at `campaign.py:1821` is INSIDE the
> `as_completed` loop, and the pair test runs AFTER that block drains.** I confirmed the structural half
> independently from the same file: `h2_present` is built from the winners *after* the drain, so the
> pair test is sequenced behind the per-arm legs and sits outside every handler.
>
> **⇒ The H2 pair test — the confirmatory contrast — is the ONE stage with no exception containment, and
> a single stale lock kills the WHOLE DRIVER rather than one batch.** That turns my "it is not being
> re-enumerated" from a puzzle into a *prediction*, and it is the crash-loop shape D20's own docstring
> describes. **The core line builds the identical array in ~16–26 h.**
>
> **The asymmetry that makes it urgent:** the D20 reaper removes the *blocker* (verified,
> positive-controlled 01:14/01:15Z) — but **nothing re-drives a pipeline whose process already died**,
> so reaper-without-containment still loses the batch.
>
> **I also accept coord's correction that "unattended, not blocked" was an inference stated as an
> observation** — I had carried the same framing, and it is softened here to what was actually measured.
> **Fix (coord's, endorsed): give the pair-test call the same containment the per-arm block already has,
> and treat it as a confirmatory-path robustness requirement, not a leg4 repair.**

### Why this matters far beyond one report-only leg

1. `qwen3_5_9b` is a **report-only** leg (R80), so **no confirmatory result is damaged.** Stated plainly
   so the severity is not overstated.
2. **The identical batch type is the vehicle for the confirmatory H2 contrast on the core line.**
   `src/cluster/campaign.py:1837` — `run_test_leg(..., name="h2_pair_test", priority=PRIORITY_CORE)` at
   stage C2 — is the same code for core and legs. If this failure path fires there, **the confirmatory
   H2 seed ladder stops silently.**
3. **★ THE MONITORING BLIND SPOT — this is the real finding.** Every live instrument read GREEN through
   all 10.5 hours: `stalest` stayed 1–10 min (it measures driver **log** age, not batch **progress**),
   records kept landing from the other three arms, `sci=OK`, `drift=0`, `arms_full=10/10`,
   `stale_driver_locks: 0` in `STATE.json`. **Nothing in the stack watches per-batch completion age.**
   A batch pinned at `0/60` for half a day is invisible to the entire monitoring surface.

### Requests to the OPS lane (in priority order)

- **A1-a (now).** Live-check on Myriad whether any `leg4…h2_pair_test` array is queued/running; if not,
  force the driver to re-enumerate it (targeted driver restart on that line only).
- **A1-b (now).** **Promote D20 out of the deferred queue** (it is currently deferred item 13). The
  evidence that a *reused pid* can permanently wedge a batch is no longer hypothetical — it has cost
  10.5 h on a real 60-unit batch. Fix = compare **pid identity** (name/cmdline/start-time), not
  existence. `REAPED_LOCKS.log` shows the reaper only handled two `ZZZ_pc_*` self-test locks at
  01:14–01:15Z; it did not reap this one.
- **A1-c (the durable fix).** Add a **per-batch stall detector** to the cycle: for every batch with a
  live lock or an open pack dir, track `done/total` and its age; alarm at (say) 90 min with no
  increment. This is the instrument whose absence let A1 run for half a day behind a green board.

---

## ★★★★ A2 — THE D16 GATE STOP: the decision, with the evidence, decided on the merits

**Measured first-hand, confirming the RUN 9 prediction exactly.** Across all 385 test-lane training
records the CPU census is:

| CPU | records |
|---|---|
| Intel Xeon Gold **6240** @ 2.60 GHz | **381** |
| Intel Xeon Gold **6140** @ 2.30 GHz | **4** |

The four are exactly `test/baseline_volatility_scaled_return-s14, s15, s16, s17`. (The 20 `AMD64 /
16-core` entries are the `_env/` Windows **launcher sidecars** — 1 per (test lane, arm) — not training
records. No training ran on Windows. Consistent with record §89.3.)

### Three facts that decide this

1. **`baseline_volatility_scaled_return` is CONFIRMATORY, not report-only.** The "H1 is descriptive"
   text (R30/R31/R49) is **superseded**. `config/preregistration.yaml` has
   `validity_tier.status: ratified` (Tamer + Okhrati, 2026-07-26, R108) with **node `N6_h1`** =
   `llm_beats_best_human_reward`, `method: intersection_union_over_canon`, comparator = the
   **full 11-name canon**, endpoint = annualised Sharpe. This unit is one of the 11 IUT legs.

2. **Device homogeneity inside a CRN comparison unit is a RATIFIED premise of that design, not a
   preference.** `ratification_completed` includes **`cpu_randomised_device_block`**, justified in the
   frozen record in these words: *"device is a nuisance factor, **every CRN comparison unit stays
   device-HOMOGENEOUS (seed-pool blocks), so the device cancels in each paired difference**"*.
   Accepting the split means shipping a confirmatory node whose own ratified justification is
   **factually false for 4 of its 30 seed pairs**.

3. **A re-run introduces NO code heterogeneity — verified, not assumed.** All **1,587** search+test
   records carry **one** deployed-archive hash, `deployed-archive:b9e6df55…072613e`, including records
   written *after* tonight's `RUNNING_SHA` re-base to `16bb71b`. The supervisor/gate fixes did not move
   the on-node training closure. A full `env.json` diff of `s14` (6140) against `s13` (6240) shows
   **2 differing keys out of 156**: `cpu.model_name` and `seed`. Everything else — torch 2.6.0+cu124,
   thread counts, BLAS, glibc, gold-panel manifest sha256s — is identical.

### ⇒ DECISION: **Option B — re-run the 4 seeds on the 6240 pool.** Rationale, and the counter-argument

Under [[feedback-full-delegation-2026-07-13]] (ratify-on-Tamer's-behalf, conditioned on ultrathink +
strict priorities) and tonight's explicit grant of full freedom, I am recording this as **ratified on
Tamer's behalf**, to be reversed on a word from him.

- **PRIORITY 5 (100 % reproducibility, strict — "a WARN counts as a FAIL") and the determinism-envelope
  rule 2 both name device homogeneity as FROZEN DESIGN, not an ops detail.** Option A accepts a known,
  measured violation of a ratified premise in a confirmatory node. That is exactly the trade the
  priorities forbid.
- **Cost is trivial:** 4 baseline trainings, **zero LLM spend** (no authoring), a few core-hours on a
  cluster where we already hold ~960 cores.
- **The strongest counter-argument, addressed honestly:** *is a post-hoc re-run a forking path?* No,
  and this is the decisive point — **the decision is being taken while completely effect-blind.** The
  trigger is a provenance invariant (D16) that reads device metadata and never touches an outcome; no
  one has looked at these seeds' results; the unit, the seed, the config and the deployed archive are
  all unchanged. It is a repair of the registered condition, not a new condition. **That epistemic
  position is available only right now.** Deferred until after unblinding, the identical repair becomes
  contestable — a referee can no longer verify that the outcomes did not motivate it.
- **Two preconditions on execution (both are why this is time-critical):**
  1. **Do it BEFORE the next deploy that touches the training closure.** The pending DEFERRED_FIXES
     (1–7, 9, 10, 12, 13) may change `deployed-archive`; re-running after that swaps a CPU-model
     heterogeneity for a **code-version** heterogeneity, which is strictly worse. Right now the hash is
     provably invariant — that window is open and will close.
  2. **Quarantine, never overwrite.** Move the four 6140 records to a `_superseded_D16_*` path, keep
     them, and disclose the substitution in the QC appendix. The honest execution narrative is itself
     distinction-grade evidence (D5).

**→ OPS lane owns execution.** I own neither `outputs/` nor the cluster and will not touch either.

> ### ⚠ TWO CORRECTIONS TO THIS SECTION FROM THE OPS LANE (M32, 2026-08-01 02:20Z) — both accepted, and I verified the first myself
>
> **The DECISION is unaffected. Both corrections are about TIMING and EXECUTION MECHANICS.**
>
> **(1) I had the window's TRIGGER WRONG. It is a NODE RE-SYNC, not the next local deploy.**
> I wrote — repeatedly, and told Tamer twice — that the clean window "closes at your next deploy that
> moves `deployed-archive`". **Verified first-hand against `src/utils/provenance.py:66-91`: ops is
> right.** `git_commit()` tries `git rev-parse` first and, on the cluster, *falls back* to reading a
> **`GIT_COMMIT` marker file at the deployed root** (`Path(__file__).resolve().parents[2] /
> "GIT_COMMIT"`), written by the sync procedure because the cluster checkout is deployed via
> `git archive | tar` and is **not a git work-tree**. So the marker tracks the **node's** deployed
> checkout. Ops' relaunch restarts **local** processes only and never touches `~/llmrp`. **⇒ The window
> does NOT close tonight, and the re-run still lands with the same sha as its 26 siblings.** My framing
> was wrong about the mechanism and **too pessimistic** about the deadline — there is more time than I
> said. *(Note the direction: overstating urgency is as much an accuracy failure as understating it.)*
>
> **(2) My "quarantine, never overwrite" spec was NOT EXECUTABLE — it was local-only.** The four 6140
> records **exist on the NODE**, so a laptop-side quarantine is silently undone by the next pull. Ops
> notes this is exactly what regressed record §28's *"THE VALIDITY FAILURE IS CLOSED"*. **True option B
> must move the REMOTE copies too.** Their script does both sides, re-verifies the 6140 CPU model
> immediately before each move, and never deletes. **That is the correct spec; mine was incomplete and
> I am adopting theirs.**
>
> **What still stands unchanged:** the census (381 × 6240, exactly 4 × 6140), N6_h1 being confirmatory,
> `cpu_randomised_device_block` registering device homogeneity as its premise, the 2-of-156-key env
> diff, the single `deployed-archive` hash across 1,588 records, and — the load-bearing point — that the
> decision is being taken **effect-blind**, which is what makes it clean and which no correction touches.

---

## A3 — D18: two double-nested duplicate records. Mitigation VERIFIED; root cause FOUND

**The archive contains two records at depth 5 instead of 4:**

```
search_leg_glm_5_2/placebo_shuffled/placebo_shuffled-g3-c4/placebo_shuffled-g3-c4/record.json
search_leg_haiku_4_5/scalar/scalar-g1-c3/scalar-g1-c3/record.json
```

- **Byte-identical to their outer siblings** (sha256 match on both pairs) and carrying the **same
  `run_id`**. Verified.
- **Root cause — a TOCTOU race in `src/cluster/poll.py:pull_archive`.** The commit loop is
  `dest = local/rel; if dest.exists(): continue; shutil.move(str(src), str(dest))`. Twelve concurrent
  driver processes each compute `missing` independently, then fetch (slow), then move. If process B
  evaluates `dest.exists()` as False microseconds before process A's move lands, B's `shutil.move` runs
  with `dest` now an **existing directory** — and `shutil.move` into an existing directory moves the
  source **inside** it, producing exactly `<cand>/<cand>/`. Two occurrences in 1,585 records is
  consistent with that narrow window.
- **The stated mitigation HOLDS, but not for the stated reason.** `results_audit.py` says
  *"analyze_campaign.py dedupes by run_id **and is depth-limited**, so the confirmatory path is safe."*
  Reading `analyze_campaign.py:1095–1118`: loading is **unconditional at every depth**; only *recursion*
  is depth-gated at `_MAX_ARCHIVE_DEPTH = 3`. The walk reaches the candidate dir at depth 3 and **does**
  load the nested copy. **`seen.setdefault(run_id, rec)` is doing 100 % of the work.** Safe today
  because the copies are byte-identical; it would NOT be safe against a nesting that carried a
  different `run_id`. Worth correcting the comment so nobody relies on the depth bound.
- **Fix suggestion (OPS, low priority, no relaunch):** make the commit atomic —
  `try: os.rename(src, dest) except FileExistsError: pass` — instead of check-then-`shutil.move`.

**Record-count triple, fully reconciled** (this closes the s.86.2 thread):
`1,614` (recursive) = `1,587` (authority, depth-4) + `27` frozen winner markers (depth-3) + `2` nested
duplicates (depth-5). Plus 1 more under `.pull_tmp.28884/`, excluded by every reader. **No record is
missing and none is double-counted in the confirmatory path.**

---

## A4 — The pooled arm-imbalance figure is MIS-SPECIFIED (the core-line one is correct)

The alert reports *"ARM DEPTH IMBALANCE 1.81x across H2's IUT arms (distributional=319 vs
scalar_cvar5=176)"* and grounds it in an **E[max]-over-the-search-pool** argument. But those counts come
from `results_audit`'s recursive walk, so they **mix three different things**: search candidates, `test`
lane records, and `frozen*/` winner markers.

Measured decomposition:

| arm | search | test | frozen marker | nested dup | reported | **search-only** |
|---|---|---|---|---|---|---|
| distributional | **307** | 0 | 12 | 0 | 319 | **307** |
| scalar | **284** | 0 | 11 | 1 | 296 | 284 |
| placebo | **199** | 24 | 1 | 0 | 224 | 199 |
| scalar_cvar5 | **175** | 1 | 1 | 0 | 177 | 175 |
| placebo_shuffled | **172** | 0 | 1 | 1 | 174 | 172 |

- **Reported spread 1.802×; the quantity the argument is actually about is 307/175 = 1.754×.**
- The alert's **direction is right** (a starved comparator raises E[max] asymmetrically → biased
  *toward* rejecting the IUT leg → toward a false positive). Only the magnitude is inflated.
- **The estimand is wrong in a second, larger way:** winner selection is **per (line, arm)** (F-0001),
  so the E[max] bias operates *within* each line. A pooled cross-line ratio is not the relevant
  quantity at all. **The core-line figure the ops lane already flags (§56.6) — 28 / 15 = 1.867× — is the
  correct and material one.**
- **Not propagated:** `grep` over `paper/`, the master plan and the execution record finds **no** use of
  the pooled figure. Contained to ops alerts. **Severity: low — correct the alert's wording, nothing else.**

---

## A5 — R115: independently re-derived, and it produces a clean confirmatory result

Re-derived `train_safe_default_count / train_safe_call_count ≥ 0.10` over all 1,587 records with a
standalone script: **13 breaches — exactly matching `science_watch`'s 13.** Two independent routes agree.

**★ All 13 are on report-only LEGS. Zero on the core confirmatory line. Zero on `h3_singleshot`.**
That is a genuinely good result and it is worth stating in CH6: no candidate in the confirmatory pool
was R115-ineligible.

> **⚠ UPDATED 02:44Z — MY OWN NUMBER WENT STALE WITHIN THE HOUR, and I am correcting it before it ships.**
> **It is now 14, not 13.** A new breach landed 08-01 02:42:33Z: `search_leg_glm_5_2/placebo/placebo-g3-c3`,
> fraction **0.1111**. Re-derived independently; the cycle agrees (`r115=14B`, having read `13B` all night).
> **The substantive claim is unchanged and is the one that matters: still ZERO on the core confirmatory
> line, zero on h3ss, all 14 on report-only legs.** But I handed the *count* to the write-up lane as if it
> were a fact — exactly the stale-number class I spent the night flagging in other people's documents
> (§44.4's PopArt band, `_env` 18-vs-20, coord's 4.2 h constant). **The fix is to write the claim in a
> form that cannot go stale:** *"every R115-ineligible candidate in the campaign sits on a report-only
> replication leg; none is on the confirmatory line"* — true regardless of the count. If a number ships,
> take it fresh at write-up time **and date it**.

**A pattern worth handing to the mechanism analysis (a lead, not yet a finding):** the default fractions
are suspiciously exact rationals — `199932/400000 = 0.4998` appears **7 times** across 5 legs and 4 arms;
also `399912` (≈1.0), `133333` (=1/3), `79973` (≈1/5). Deterministic sub-multiples like that point at a
reward failing in a fixed subset of the parallel envs or on a periodic step, not at random numerical
noise. And **the two Qwen legs account for 8 of the 13** — directionally consistent with the
numeracy-bottleneck headline and with the measured per-model authoring reliability. **→ WRITE-UP lane:**
a candidate exhibit for the capability-gradient argument, but it needs its own confound check before it
is claimed (pool sizes differ by leg).

> **⚠ CREDIT CORRECTION — I nearly presented recognised machinery as a discovery.** The exact-sub-multiple
> pattern is **already a NAMED signature**: `results_audit.py` §5's anomaly hunt tracks *"non-zero
> safe-default fractions repeating >2×"* as the **D17 signature**, with a stated mechanism — *"a fail-safe
> clearing the reward's state produces period = warm-up calls + 1."* **My contribution is only that the
> set has grown and now spans FIVE distinct rationals**: 0.4998 (≈1/2, **eight** occurrences), 0.3333
> (1/3), 0.1999 (1/5), **0.1111 (1/9, new at 02:42Z)** and 0.9998 (≈1). Reading an existing instrument's
> output and calling the pattern mine would have been the mirror image of P110 — **the repo was ahead of
> me, and that is the fifth time tonight across four lanes.** The capability-gradient reading stays
> **UNCLAIMED** until the pool-size confound is measured; I have not run that check and will not assert
> it without one.

---

## A6 — Spend: NOT an integrity problem, but it IS a write-up obligation

$40.71 realised, ~$49.3 projected, against a registered **$30**. I checked whether this is a breach:
it is not. **R83 (2026-07-21, Tamer's instruction) softened the ceiling to ADVISORY** —
`config/preregistration.yaml:481: spend_ceiling_usd: 30 # ADVISORY planning ceiling … tracked +
reported, WARNS at thresholds, NEVER refuses`. `budget_rc=2` is that WARN firing exactly as designed.
The exogenous stopping rules that protect the design (the seed-rung rule, the leg calendar gate) are
untouched, and **no data-collection decision has been made on cost.**

**→ WRITE-UP lane.** R81 registered "$30, HARD-capped, enforced in code"; R83 softened it; realised spend
will land ~65 % over the planning figure. Under Okhrati D1 (mechanism · uncertainty · counterfactual) and
the industry-supervisor obligation to report spend prominently, this needs **the number with its
account** — why it overran, that it was advisory by a *pre-data* amendment, and that it gated nothing.
Better volunteered in CH6/CH7 than discovered by a marker diffing R81 against the ledger.

---

## A7 — Where the campaign actually is (the critical path, and why the imbalance is also an ops problem)

- **H1 canon: COMPLETE.** All 11 canon rewards at **30/30** seeds, plus `random_search` 30/30 = 360
  records in `test/`. (4 of `baseline_volatility_scaled_return`'s 30 are the D16 records — A2.)
- **Core line H2 ladder: NOT STARTED, and not gate-blocked.** `src/cluster/campaign.py:1836` launches
  `h2_pair_test` at stage **C2**, after the `as_completed` drain over *all* core arms. The core line is
  2/5 frozen; `distributional` (28) and `scalar` (27) are done, but the driver is still searching
  `c1_placebo_g4`, `c1_scalar_cvar5_g3`, `c1_placebo_shuffled_g4`. **No `c1_*h2_pair*` batch exists yet.**
- **⇒ The three starved control arms are simultaneously (a) the H2 IUT bias risk and (b) the literal
  critical path to the confirmatory ladder.** Anything that accelerates `scalar_cvar5` / `placebo` /
  `placebo_shuffled` search on the core line buys both scientific balance and wall-clock. That is the
  single highest-leverage ops action available and it is fully effect-blind.
- Legs at C4/pair-test: `qwen3_5_9b` (5/5 frozen; **its h2_pair is the dead batch — A1**),
  `h3_singleshot`, and `gemini_2_5_flash` (h2_pair launched 01:56 local and running).

---

## 8. Continuous monitoring now running

A read-only watcher polls every 120 s and emits **only** actionable transitions — drift ≠ 0, `sci` ≠ OK,
verdict/guards/arms-full changes, `stalest` > 30 min, a 45-min record stall, each $1 spend band, any
`ALERTS.txt` content change, and `STATE.json` going unwritten for 10 min (i.e. the ops cycle itself
dying — the failure a log tail cannot see). It touches nothing.

**Known gap it does NOT close: per-batch progress (A1-c).** Until that instrument exists, the A1 class of
silent stall stays invisible, and I am compensating by re-deriving batch state by hand each cycle.

---

# PART II — INDEPENDENT RE-VERIFICATION OF THE SCIENCE LAYER (2026-08-01 01:30–01:45 UTC)

The ops instruments report `leaks=0 cross-arm=0 hash=0 non-finite=0`. **The author should not grade its
own work**, so I re-derived each claim by a route that shares no code with the instrument. Three
confirmations, three new findings, and one methodological correction of my own.

## A8 — CONSTRUCT VALIDITY: **CONFIRMED**, by a method that uses no keyword heuristic

`results_audit` finds the fed block by string search (`low.find("reference value")`, `find("feedback")`)
and counts decimals. That is a *heuristic*, and a heuristic cannot detect a prompt in which the thing it
searches for is **absent**. So I isolated the fed block **structurally**: within a line, take one prompt
per arm and compute the common prefix and common suffix across all five — **whatever differs IS the
manipulated variable**, by construction, with no keyword involved.

*(Methodological correction, recorded because it nearly became a false alarm: my first pass cut the
common prefix mid-number — it sliced `0.085332` into `0.` + `085332` — and reported 6 spurious
"failures" on scalar and scalar_cvar5, both off by exactly one. Snapping the cut to line boundaries
removed all six. **A boundary artifact that lands off-by-one on exactly the arms you are worried about
is the most seductive false positive there is.**)*

Corrected result, **all 11 lines, uniform**:

| arm | numbers in the fed block | tail vocabulary | what it isolates |
|---|---|---|---|
| `distributional` | **7** (1 DSR + 6 tail stats) | `cvar`, `tail` | the treatment |
| `scalar` | **1** (DSR only) | **NONE** | information vs one number |
| `placebo` | **7** | **NONE** | **information ≠ token-count** — same number count, zero tail semantics |
| `scalar_cvar5` | **2** (DSR + CVaR-5 %) | `cvar` | tail *shape* vs one downside number |
| `placebo_shuffled` | **7** | `cvar`, `tail` | **content ≠ format** (node N5) — same vocabulary, linkage destroyed |

**Everything outside the fed block is byte-identical across the five arms** (common prefix ~154 ch,
common suffix 240–266 ch). **The identification principle is directly verifiable from the archive**, and
all four contrasts are present and correctly differentiated. Then exhaustively, per record:

- **861 gen ≥ 1 records, 100 % coverage, ZERO tail-vocabulary leaks into `scalar` or `placebo`.**
  Independent corroboration of the instrument's `leaks=0`.
- Also re-derived independently and **agreeing with the instrument**: `reward_source_hash` mismatches
  **0/1,588**; identical reward program shared **across arms within a line 0**.

## ★★ A9 — 3 CANDIDATES AT GENERATION ≥ 1 RECEIVED **NO FEEDBACK AT ALL**

The structural method found what the heuristic could not: **three records whose prompt is the
generation-0 INITIAL prompt (2,602 ch, no feedback block) while their `generation` field says 2 or 3.**

```
search_leg_qwen3_5_9b  placebo       g2  placebo-g2-c2
search_leg_qwen3_5_9b  scalar_cvar5  g3  scalar_cvar5-g3-c2
search_leg_qwen3_5_9b  scalar_cvar5  g3  scalar_cvar5-g3-c4
```

**Mechanism — DESIGNED FALLBACK, not a bug.** `src/llm/loop.py:405-409`: `if prev_feedback_block is
None: <initial prompt> else: <reflection>`, and `prev_feedback_block = gen_best_block` (:729). **If a
generation yields no accepted candidate, there is nothing to reflect on, so the next generation falls
back to the initial prompt.** The census proves it exactly: qwen `placebo` has candidates only at
generations {2, 3, 5} — nothing at 0 or 1 — so g2 was still un-fed; `scalar_cvar5` has {3, 4, 5}, so
both g3 candidates were un-fed. Every other 2,602-char prompt in the archive is a genuine g0.

**Exhaustive census — 1,140 LLM-arm search records:**

| | |
|---|---|
| un-fed candidates at generation ≥ 1 | **3 (0.26 %)** |
| on the CORE confirmatory line | **0** |
| lines affected | 1 — `qwen3_5_9b`, the weakest author (17 % gate pass) |
| arms affected | `placebo` 1, `scalar_cvar5` 2 |
| **positive control** | 279 gen-0 records, **0** carry a reflection block — the detector can fail, and does not false-positive |

**Why it still matters even at 0.26 %.** A candidate labelled `generation: 2` that never saw feedback is
informationally a generation-0 re-draw, and **three analyses read `generation`**: H3 (confirmatory node
N3, iterative vs single-shot), `docs/ops/generation_learning.py`, and the mean-generations-completed
statistics in §56/F-0002. **And the fallback is arm-correlated *by construction*** — an empty generation
is likeliest in a thin pool, and the thin pools are the comparator arms. That is a structural asymmetry,
not random noise.

**⚠ I checked whether it contaminates the BANKED s.94 result ("no detectable learning") — it does NOT.**
`generation_learning.py:96` filters to `set(g) >= set(range(N_GENS))`, i.e. pools with **all six**
generations present. qwen `placebo` {2,3,5} and `scalar_cvar5` {3,4,5} both fail that filter and were
never in the n=20. **Verified by reading the filter, not assumed.**

**Disposition: no fix, disclose it as a measured bound.** "0.26 % campaign-wide, zero on the confirmatory
line, mechanism identified, arm-correlation stated" is a *stronger* QC-appendix entry than silence, and
it costs nothing. **→ OPS:** worth a standing check (`generation ≥ 1 AND prompt lacks the reflection
marker`) — it is one line and no instrument currently has it. **→ WRITE-UP:** a QC-appendix row.

## ★★ A10 — `metrics.train_curve.return` IS NaN ON 100 % OF RECORDS — root-caused

**Every one of the 385 test-leg records has an 80-point training curve whose `return` series is NaN at
every point.** Its siblings are fully populated and healthy — `actor_loss` −194 → −0.80, `critic_loss`
4.8 → 5e-5, `ent_coef` 0.30 → 8.9e-5, `step` 5 000 → 400 000. **Training genuinely ran and converged;
only the return series is empty.** No prior archive (prototype, σ-pilot, run3) has a `train_curve` at
all, so this has never worked — it is not a regression.

**Root cause, verified in source.** `src/agents/trainer.py:230`:
`self.curve["return"].append(float(np.mean([e.get("r", nan) for e in ep])) if ep else nan)` where
`ep = self.model.ep_info_buffer`. SB3 populates `ep_info_buffer` **only from `info["episode"]`, which is
injected by the `Monitor` wrapper** — and `grep "Monitor("` over `src/agents/ src/envs/
src/orchestration/` finds only an unrelated `ParallelMonitor`. **The training env is never wrapped in
`Monitor`, so the buffer is always empty and the `else nan` branch fires every time.**

**Assessment — and this one I recommend NOT fixing:**
- **Science: unaffected.** No confirmatory endpoint reads it; the recorder is read-only and
  determinism-safe. The 330 NaN `val_fitness` values I also flagged are the **registered** R49 behaviour
  for baseline test records — expected, not a defect.
- **Write-up: a real but fully substitutable gap.** For Okhrati's *"show me it converged"*, the
  loss/entropy curves are a complete — arguably better — substitute for an RL audience, and they are
  uniform across the whole archive. D2's *"how results change with increasing seeds"* was never served by
  the training curve; that is the per-seed trajectory exhibit, which is fully available.
- **★ Why fixing it now would be WRONG.** The fix touches `src/agents/trainer.py` = inside the training
  closure ⇒ a deploy ⇒ **`deployed-archive` moves**. That would (a) destroy the currently-perfect
  "all 1,588 records on one archive hash" property, which is a *reproducibility asset*; (b) close the
  clean D16 re-run window (§A2); and (c) produce a **split archive** — some records with curves, some
  without — which is strictly worse for the write-up than a uniform, disclosed absence. The 385 existing
  records cannot be back-filled either way.
- **Disposition: disclose + queue post-campaign.** One-line fix (wrap the training env in `Monitor`) for
  the next run. **A field that is structurally always NaN is a fictional field** — same class as the
  R85 "a pin nobody can verify is FICTIONAL" lesson, and it belongs in the QC appendix on those terms.

## A11 — `feedback_block` is EMPTY on all 1,203 search records

The record schema carries a first-class `feedback_block` field. It is `""` on **every** search record at
**every** generation 0–5. The fed block — **the manipulated variable of the entire experiment** — is
recoverable only by string-slicing `prompt`.

**This is why A9 was invisible.** Every construct-validity check must reconstruct the treatment by
heuristic, and a heuristic keyed on the presence of a marker cannot see a prompt where the marker is
absent. It is also the reason my structural (prefix/suffix-diff) method was worth building.

Nothing is wrong with the *data* — the manipulated variable IS in the prompt and IS correct (A8). But
**the experiment's independent variable is not stored as a first-class field**, which under PRIORITY 5
("a violation must be *detectable by audit*") is a weakness in the evidence chain rather than in the
result. **→ Post-campaign fix; disclose as-is. Do not touch `src/` mid-campaign for it.**

## A12 — EVALUATION-WINDOW HOMOGENEITY: **CONFIRMED** ⚠ *(seed-set clause SUPERSEDED at 02:40Z — see A12-bis)*

## ⚠ A12-bis — THE D16 REPAIR TRANSIENTLY BREAKS THE SEED-SET INVARIANT I CERTIFIED (correct, expected, and it must be re-verified)

Ops executed D16 option B at ~02:40Z, both sides, quarantining seeds 14–17 of
`baseline_volatility_scaled_return`. **Measured from the archive immediately after:** eleven canon units
plus `random_search` are at **n = 30, seeds 0–29 complete**; `baseline_volatility_scaled_return` is at
**n = 26, missing exactly `[14, 15, 16, 17]`** — precisely and only the four, no over-reach, no
collateral. **Execution confirmed.**

**But A12 certified *"all 12 units carry exactly seeds 0–29 … ONE shared seed set"*, and there are now
TWO.** This is the correct transient state of a correct repair — **not a fault** — and I am recording it
rather than leaving a certification standing that the archive no longer satisfies. *(A verification that
was true when written and is false now is exactly the stale-fact class we spent the night correcting:
§44.4's PopArt band, the `_env` 18-vs-20, coord's 4.2 h constant. I am not adding another.)*

**Why it needs a re-check rather than a shrug.** `paired_seed_difference_test` operates **over shared
seeds**, so until the four re-runs land, an N6 IUT leg against `volatility_scaled_return` would silently
compute on **26 pairs while its ten sibling legs use 30**. That is not *wrong* — pairing over shared
seeds is correct behaviour — but it is **silent**, and **in an IUT the p-value is the MAX over legs, so a
leg with reduced power is disproportionately likely to BE that max.**

**Re-verification conditions when the re-runs land (both halves):**
1. `baseline_volatility_scaled_return` back to **seeds 0–29 complete**, one shared seed set across all 12.
2. **The unit device-HOMOGENEOUS on 6240 for all thirty** — a re-run that lands on another 6140
   reproduces the original defect, and `--resume` gives no placement control unless the fence holds.

**Until then: treat any N6 output as provisional and say so.**

> **★ Worth recording as the best move of the night, and it is ops':** *"the re-run doubles as the
> registered bit-comparison experiment."* If seeds 14–17 on a 6240 reproduce their 6140 values
> bit-for-bit, **the device never mattered and we can say so with evidence instead of assuming it**; if
> they differ, **the D16 gate is vindicated with a number attached.** Either outcome is publishable, it
> costs nothing extra, and it turns a repair into a measurement. **A CH6 line whichever way it falls.**

All **388** test records carry a `test_returns` series of length **1571 — one distinct length
campaign-wide, zero exceptions.** CRN's structural precondition (every paired unit evaluated on an
identical window) is confirmed *present in the archive*, not merely specified. Combined with §7f's seed
audit (12 units × exactly seeds 0–29, one shared set, zero duplicates), the paired design is verified
end to end.

## ★★★ A13 — POPART: the "cannot confound H2" claim CONFIRMED **with an interval**, and §44.4's stated MECHANISM is FALSIFIED

*(Self-correction first, because it is the instructive part: my initial pass keyed engagement on
`popart_scale["popart"]` and returned a flat **0.0 % on every arm, 0/1594**. A perfect 0 % is a claim
about my own script — `popart` is a constant flag, not the scale. `results_audit`'s own docstring
records the sibling trap: *"`popart_scale` is a DICT, not a float. Type-checking for (int, float)
reports '0 records carry it'."* The correct predicate is **`sigma_max > 1.0`**.)*

Corrected, independently derived: **811 / 1594 engaged (50.9 %)** against `results_audit`'s 808 — the
gap is the 9 records added during this session. **The invariant `sigma_max == max(1.0, raw_rms_max)`
holds with 0 breaks.**

**(a) The five LLM arms — the load-bearing "cannot confound H2" claim, now with its uncertainty:**

| arm | engaged | rate |
|---|---|---|
| distributional | 196/307 | 63.8 % |
| scalar | 181/284 | 63.7 % |
| placebo | 130/224 | 58.0 % |
| scalar_cvar5 | 107/182 | 58.8 % |
| placebo_shuffled | 107/173 | 61.8 % |

Largest gap = distributional − placebo = **+5.8 pp, SE 4.3 pp, 95 % CI [−2.6, +14.2], z = 1.35 → not
distinguishable from zero.** **The claim holds and now carries the interval CLAUDE.md's
"UNCERTAINTY IS UNIVERSAL" clause requires** — §44.4 asserted symmetry without one. ⚠ **§44.4's stated
band "(62–67 %)" no longer matches the archive (58.0–63.8 %).** Rates move legitimately as data
accumulates (§44.4 was computed at 1,026 records, the archive is now 1,594) — so this is a **stale
interval that must be re-measured on the final archive before it ships**, not an error at the time.

**(b) ★ THE H1 CANON — §44.4's mechanism ("splits perfectly by ratio-form vs difference-form") is
FALSIFIED by the completed canon.** The split is perfectly bimodal — 3 rewards at 100 %, 8 at 0 %, zero
within-reward variance — but it is **not** the stated dichotomy. `raw_rms_max`, the quantity that
actually decides it:

| reward | median `raw_rms_max` | engages? |
|---|---|---|
| `differential_downside_ratio` | **3 101.4** | YES |
| `differential_sharpe` | **2 382.9** | YES |
| `return_minus_drawdown` | **2.03** | YES |
| `return_minus_turnover` | **0.917** | **no — and see below** |
| `random_search` | 0.188 | no |
| `raw_return` · `mean_variance_utility` · `return_minus_variance` · `return_minus_downside` · `return_minus_cvar` · `log_growth` | 0.058 – 0.068 | no |
| `volatility_scaled_return` | 0.022 | no |

**The functional-form story mis-predicts twice**: `return_minus_drawdown` is a *difference* form and
engages; `return_minus_turnover` is a *difference* form and does not. **The real mechanism is REWARD
SCALE.** PopArt engages iff running RMS clears the 1.0 floor, and the canon spans **five orders of
magnitude** (0.022 → 28 774). Three tiers, each with a physical reason: the two **ratio/differential**
rewards blow up because their denominator (a running volatility / downside-deviation estimate) can
approach zero; **`return_minus_drawdown`** clears the floor because drawdown is a *cumulative* quantity
living on a far larger scale than a per-step return; **everything else** is a per-step return-scale
quantity at ~0.05. *Confound check (the standing rule): the alternative account — "engagement tracks
functional form" — is refuted by two counter-examples inside the canon itself, whereas the scale account
predicts all 12 units including `random_search`, and predicts the ORDERING, not just the split.*

**★★ (c) A FRAGILITY NOBODY HAS FLAGGED — and it lands on the most important reward in the canon.**
`return_minus_turnover` sits at median **0.917**, max **0.962** — **within 4 % of the engagement floor
and never crossing it.** It is the one canon member whose normalisation regime is decided by a margin
that thin. And by §47 it is **the only reward in the canon with a positive outcome** (119× less turnover
than any other). **So the best-behaved reward in the panel is also the one sitting closest to a regime
boundary.** A modestly different cost assumption or data window flips it into the PopArt-normalised
regime, which changes its critic scaling. **This must be disclosed as a stated sensitivity** — it is
precisely the kind of un-named linchpin the non-fragile-backbone rule exists to catch, and it is far
better volunteered by us than found by a referee.

## A14 — THE CONFIRMATORY DECISION MACHINERY: audited against the FROZEN pre-registration. **CLEAN.**

The single most dangerous possible defect is a mismatch between the frozen design and the code that will
compute the verdict — it would surface only when the analysis runs, i.e. too late. Audited code-only and
effect-blind:

| check | result |
|---|---|
| Is the graph hardcoded or read from config? | **READ** — `validity_tier.py:128 registered_alpha_graph(root)`, never hardcoded |
| α round-trip config → loader | **0.05 = 0.05 MATCH** |
| initial weights round-trip | **MATCH** — `{N1 .5, N2 .5, N3 0, N4 0, N5 0, N6 0}`, sum **exactly 1.0** |
| edges round-trip (all 6 nodes) | **MATCH**, byte-for-byte |
| each node's out-edges ≤ 1 (Bretz et al.) | all **exactly 1.0000** — no α is ever lost |
| node sets (weights vs edges) | **IDENTICAL** |
| `status` / `ratification_pending` | `ratified` / `[]` |
| H2 IUT contrasts (`analyze_campaign.py:1129-1133`) | `(dist,scalar) (dist,placebo) (dist,scalar_cvar5)` = **PREREGISTRATION §1 H2** |
| **11-name canon: config vs code vs archive** | **ALL THREE IDENTICAL** (`config h1_baselines` = `src.baselines.rewards.REWARD_CANON` = the 11 `test/baseline_*` dirs) |
| N6 endpoint | config `sharpe_annualized`; code uses `{seed → annualized test Sharpe}` — **MATCH** |
| N6 method | config `intersection_union_over_canon`; code `IUT p = max leg p` (Berger 1982) — **MATCH** |
| SESOI / equivalence margin / α | 0.05 / 0.05 / 0.05 |

**This is the strongest single result of the night** and it is currently unstated anywhere: *the
confirmatory decision rule that will be executed is provably the one that was frozen.*

## ★★★ A15 — A DEFECT **INSIDE THE CONFIRMATORY OUTPUT**: stale DSR prose states the bias in the WRONG DIRECTION

The N6 computation is correct (A14). **The prose rendered beside its verdict is not.**
`analyze_campaign.py:6031-6032` emits, into the CH6 markdown:

> *"… behind (the LLM DSR is deflated by N={winner_n_trials}; each hand reward by N=1 — **the human bar
> is conservatively high**)."*

and the same claim sits in the code comment at `:5833-5834`.

**Two things are wrong with it, and the second is material:**

1. **DSR is not the endpoint.** `grep -niE "dsr|deflat"` over the entire N6 leg-computation block
   (`:5836-5885`) returns **nothing**. The legs are annualised Sharpe, paired per seed, IQM, one-sided.
   So the cited conservatism mechanism **does not exist in the computed statistic**. This is DSR-era
   prose that survived the 2026-07-26 endpoint correction.
2. **★ It states the direction of bias backwards.** The frozen config's own ⚠ CORRECTED note — the one
   that *rejected* the DSR endpoint — says the genuine residual asymmetry is the opposite: *"the LLM
   winner = best of 30 validation candidates vs each hand reward = one fixed specification … **FAVOURS
   THE LLM** and is disclosed as the un-tuned-baseline bias (CH6)."* The rendered sentence tells the
   reader the bar is conservatively **high** (i.e. against us) when the registered reasoning says the
   real selection asymmetry runs **for** us.

**Severity: no number changes — every computed quantity is correct.** But this is interpretive prose
printed beside a **confirmatory** verdict, in graded output, asserting a conservatism that both (a) does
not apply to the endpoint used and (b) points the wrong way. It is precisely the *"faultless presentation
of data"* criterion — the only thing the 90–100 band adds over 80–89 — and it is exactly the kind of
internal contradiction (code comment vs frozen config's own correction note) an examiner on his home
ground would find.

**Fix is two sentences, changes no computation:** replace the DSR-deflation clause with the registered
one — *the LLM winner is the best of N validation candidates while each hand reward is a single fixed,
un-tuned specification, an asymmetry that favours the LLM and is disclosed as the un-tuned-baseline
bias.* **→ OPS owns the file (fenced, `scripts/`); WRITE-UP owns the CH6 text it lands in.** It is
laptop-side reporting code outside `run_one.py`'s closure, so **no relaunch and no `deployed-archive`
move** — it is safe to land at the next re-base without touching the D16 window.

## ★★★★ A16 — THREE ARTEFACTS DISAGREE ABOUT WHETHER NODE N2 CAN REJECT VIA TOST. Resolvable ONLY pre-data.

**This is the most consequential finding of the session.** It changes no number that exists today —
the core H2 ladder has not started, so no H2 outcome has been produced — and that is exactly why it is
urgent: it can still be resolved while everyone is blind, and only until then.

### The three statements, each read first-hand

| artefact | what it says about TOST at node N2 |
|---|---|
| **`config/preregistration.yaml`** `validity_tier.nodes.N2_h2_ra` | `test: h2_ra_iut_or_tost` · `equivalence: tost_0.05_dsr`, and its own ⚠ note: *"Under the PREDICTED branch N1 does not reject, so **activation rests entirely on N2 rejecting via TOST (proving equivalence)** — a real pre-registered alpha source, but power-limited … the tier is BORDERLINE to activate on the design's own prediction."* Also: *"TOST IS an IUT (bergerhsu1996equivalence) → a valid node p-value, so equivalence and superiority mix in one graph."* |
| **`PREREGISTRATION.md`** (the **hash-bound** document) | TOST is *"**reported** via TOST equivalence"* (:108); the equivalence statement *"**does not determine the thesis**"* (:300); the two-tier verdict treats it as the bounded-effect **report** (:711–715) |
| **the CODE** | `NODE_SOURCES["N2_h2_ra"] = {"path": ("h2",), "legs": "legs", "key": "pvalue_one_sided"}` — the **superiority** legs only. `tier_node_pvalues` has **no** equivalence branch (read in full, `validity_tier.py:77-118`). `h2_tost` / `h2_tost_dsr` are documented *"**never a gate**"* and `grep -rn "h2_tost" src/ scripts/ tests/` shows their only consumers are `src/viz/figures.py` and their own definitions — **wired to the tier nowhere.** |

**The code is self-consistent with the hash-bound prose. The yaml node is the outlier** — and it is the
newest, most specific artefact, so it is the one a reader will believe.

### ★ The smoking gun, and why no test caught it

`tests/test_graphical_alpha.py:112` reads:

```python
p["N2_h2_ra"] = 0.001            # equivalence proven via TOST
```

**The test suite itself documents the intent** — it hand-injects a TOST equivalence p-value and asserts
the graph propagates α correctly. But it injects **directly into `graphical_alpha_propagation`,
bypassing `tier_node_pvalues`.** So the graph's *arithmetic* is tested for the TOST case, while the
*plumbing that would ever produce such a p-value* is not tested, because it does not exist. **A test
that exercises the layer below the missing one is indistinguishable from a passing test.**

### Why it matters, stated without overstatement

- **Nothing computed today is wrong.** No H2 outcome exists; the code contradicts no number.
- **But the registered conjunctive-validity claim may be unreachable under its OWN predicted outcome.**
  All α starts on N1 (0.5) and N2 (0.5); N3–N6 begin at weight 0 and activate only on upstream
  rejection. The pre-registration's specific a-priori prediction is the **null branch** (Sharpe tie AND
  tail tie). Under that branch N1 does not reject; and if N2 cannot reject via TOST either, **no α ever
  propagates and N3/N4/N5/N6 can never be tested.** The yaml calls the tier "BORDERLINE to activate";
  as implemented, under the predicted branch it is not borderline — **it is dead.**
- **The dissertation will mis-describe its own decision rule.** Whoever writes CH4/CH6 from the yaml
  will describe a tier that can activate via N2's TOST. The analysis will produce one that cannot.
  That is a mis-statement of the confirmatory rule, on the examiner's home ground.

### What I am NOT doing, deliberately

**I am not prescribing the statistical fix, and nobody should patch this casually.** "Reject if
superiority **or** equivalence" at full α is **not** automatically valid — a naive `min(p_sup, p_TOST)`
inflates the node's type-I error. A valid disjunction needs an explicit construction (a fixed sequence,
an α-split, or a designated primary with the other demoted to reporting). **That is a design decision
for Tamer and Dr Okhrati, not a code patch** — and it is plausible that the TOST was deliberately kept
out of the gate for exactly this reason, in which case **the yaml note is the artefact to correct, not
the code.**

**Either way, one of the three must change, and it must change BEFORE unblinding.** Choosing after
seeing H2 is a forking path — the precise sin the whole design exists to avoid. **→ Tamer's call, with
Okhrati; ops owns `config/` and `scripts/`, write-up owns the CH4/CH6 description.**

## A17 — CLOSING WHAT A16 OPENED: all six node paths resolve, and the R13 family guard IS armed

A16 found N2's *semantics* wrong. Completeness demands asking whether any **other** node silently fails
to resolve — a node whose source path does not exist would be reported "not testable" and would quietly
remove itself from the graph.

**All six resolve.** `out["h2"]` carries both `"legs"` and `"tail_legs"` (`:1890-1891`); `out["h3"]`
carries `"difference"`; `out["h4"]` carries `"tests"`; `out["h2_structure"]` carries `"cvar"`;
`out["h1_beat_human"]` carries `"iut"`. **The only defect is A16 — N2's route, not a missing path.**

*(Near-miss, avoided by applying P109's lesson within minutes of logging it: my first scan regexed
`out["key"] =` assignments and reported **`out["h2"]` MISSING**, which would have been a spectacular
false alarm on both headline nodes. `out["h2"]` is populated by a **dict literal** at `:4877`
(`"h2": h2,`), not an item assignment. I suspected my own script because a missing headline key is
exactly the "too big to be true" shape. **My regex was the defect.**)*

**The R13 frozen-family guard can actually fire — verified against the live config, not the docstring.**
Its stated fail-open path (*"raises nothing … if the frozen YAML lacks a `testing_family` block"*) is
the thing to check, since a guard that no-ops is the recurring failure of this whole night. It is armed:

- `inference.testing_family` **present**, `m = **6**`
- **6 members = 3 contrasts × 2 metrics**, exactly matching `H2_CONTRASTS` at `:1129-1133`:
  `distributional` vs {`scalar`, `placebo`, `scalar_cvar5`} × {`sharpe`, `cvar`@0.05}
- `structure: two_co_primary_iut` · `decision_rule: per_family_iut_one_sided_no_leg_correction` ·
  `alpha_one_sided: 0.05` · `bh_over_6: reported_sensitivity_not_gate` (BH is a reported sensitivity,
  not the gate — consistent with R31 and with the graph being primary)
- **`grep -rn "PYTHONOPTIMIZE|python -O"` over `scripts/ src/ docs/ops/ Makefile` returns NOTHING**, so
  the `assert`-based fail-loud guards are not stripped at runtime. *(Worth stating explicitly: every
  `assert`-based guard in this codebase would vanish silently under `python -O`. It isn't used — but
  that is a property to keep true, not to assume.)*

**Net: the H2 family, the six nodes, the graph, the canon, the endpoints and the margins are all
verified consistent with the frozen design. A16 is the single exception, and it is a design-level
disagreement rather than a coding error.**

## ★★★ A18 — THE FREEZE HASH, INDEPENDENTLY RECOMPUTED. **THREE-WAY MATCH.**

The frozen pre-registration is the foundation every other claim rests on, and the cycle's
`freeze 3ca6f01a MATCHES` is `scripts/freeze.py` checking its own arithmetic. So I **re-implemented the
documented recipe from scratch** — CRLF→LF normalisation, the two mutable freeze-state lines blanked, the
nine bound files joined by a single `\n` in the documented order, SHA-256 — sharing **no algorithm code**
with the freeze module (only the *file list*, which is data, was imported).

```
MY independent recomputation : 3ca6f01ab7724d47bd5d01bc9e73b4d3150c049e1048dd86a864b400a230432f
scripts/freeze.canonical_hash: 3ca6f01ab7724d47bd5d01bc9e73b4d3150c049e1048dd86a864b400a230432f
RECORDED freeze_hash (yaml)  : 3ca6f01ab7724d47bd5d01bc9e73b4d3150c049e1048dd86a864b400a230432f
cycle log (live, every ~42 s): 3ca6f01a…
```

**All nine bound files present**, in the documented order:
`PREREGISTRATION.md` (240,657 B) · `config/preregistration.yaml` (97,039) · `config/inference.yaml` ·
`config/environment.yaml` · `config/data.yaml` · `config/arms.yaml` · `prompts/system.txt` ·
`prompts/initial_generation.txt` · **`src/feedback/schema.py` (26,128 B)**.

**Worth calling out: the ninth file is the one that matters most and was the last to be bound.**
`schema.build_block` **renders** the fed text — `arms.yaml` binds *which* block an arm gets, and until
#97 (closed 2026-07-27) **nothing bound *how* its numbers were shown.** The stakes were established
empirically by finding #87: changing one format string in that file decided whether the scalar arm
received a usable signal at all (`{metric:.2f}` made 55 % of rendered headers read literally `"0.00"`).
Pre-freeze that was a legitimate fix; post-freeze the identical edit would have passed the gate
silently. **The manipulated variable's renderer is now inside the freeze envelope, and I have verified
that independently.**

⚠ **One residual, and the code is honest about it:** the git SHA recorded at freeze time is **archival,
never verified** — no gate compares it against HEAD. The content hash is what enforces tamper-evidence,
which is why binding `schema.py` mattered. Everything in the treatment surface that is *not* one of the
nine files (e.g. `src/llm/prompts._REFLECTION_PREAMBLE`) rests on that archival pin alone. **Not a
defect to fix mid-campaign — a limitation to state.**

## ★★★ A20 — PRIORITY 5 DISCHARGED BY RE-RUNNING, NOT BY ASSERTION. **All three layers, tonight.**

CLAUDE.md PRIORITY 5 sets a **strict 100 %** reproducibility score where *"a WARN counts as a FAIL"*, and
its operative rule is *"**Verify by RE-RUNNING, never by assertion**"*. The write-up lane reported
8 PASS / 0 WARN earlier; per *the author should not grade their own work*, I ran everything myself.

**`scripts/audit_reproducibility.py` — run 02:08Z, exit rc = 0:**

```
[PASS] python-version pin      3.11.9; pyproject declares requires-python
[PASS] dependency lockfile     requirements.lock (94 pinned lines)
[PASS] version pins            torch, numpy, stable-baselines3, scipy
[PASS] determinism settings    all 4 determinism knobs set in seeding.py
[PASS] seed management         seeds declared in config/campaign.yaml
[PASS] pre-registration freeze FROZEN — canonical SHA-256 re-verified (3ca6f01ab772…)
[PASS] LLM archive-replay      config/llm.yaml archive: true (non-det LLM replayed)
[PASS] data provenance         returns_panel_univ5.parquet SHA-256 re-verified vs manifest (7cf5d98843c5…)
              8 pass / 0 warn / 0 fail => OK
```

**★ Two of those checks independently re-derive exactly the artefacts I recomputed by hand in A18/A19.**
The freeze hash now has **three** independent confirmations (my from-scratch re-implementation ·
`freeze.canonical_hash` · this audit's own derivation) plus the live cycle's 42-second check. The gold
panel has three — and **the audit's is strictly stronger than mine**: I compared *recorded* hashes to
each other across 1,623 records; it re-hashed **the actual parquet on disk** against the manifest.

**`scripts/reproduce_synthetic.py --check` — the KEYLESS golden path, re-run tonight, exit rc = 0:**

```
[reproduce_synthetic] OK: 4 records reproduce the golden
                      (panel 4b14eab6284f6bd5, winner distributional-g0-c0)
```

**⇒ The three-layer statement is now DEMONSTRATED rather than claimed, with all three verified in this
session:**

| layer | evidence, first-hand tonight |
|---|---|
| **analysis** = deterministic archive replay | freeze hash 3-way match (A18) · gold panel identical on **1,623/1,623** (A19) · `reward_source_hash` **0/1,588** mismatches (A8) |
| **protocol** = re-runnable by anyone, keyless | **`reproduce_synthetic --check` RE-RUN, rc=0**, 4 records reproduce the committed golden bit-for-bit |
| **experiment** = open-weight, hash-pinned, self-hosted | one `deployed-archive:b9e6df55…` across **1,588/1,588** records, invariant across tonight's SHA re-base (A2) |

Also confirmed against the MAXIMUM-STRICTNESS clause: **`scripts/leg_gates.py:96 _COMPLIANCE_FLOOR = 1.0`**
— its strict value, not the historical 0.5 that a stale column in R103 still mentions.

**→ WRITE-UP: this is Stefan's criterion #3 ("THE CRITICAL POINT") discharged with evidence.** Quote it
as *independently re-run*, with the 02:08Z timestamp and the archive size beside it — every count in this
campaign is a moving snapshot, and dating them is the only thing that keeps them true.

## A21 — two loose ends closed (both benign, one number to date)

**`_env` launcher sidecars: 20 on disk, and record §89.3 says 18 — reconciled, not a discrepancy.**
Composition is exactly 1 per (test lane, arm): `test` 12 · `test_h3_singleshot` 1 ·
`test_leg_gemini_2_5_flash` 2 · `test_leg_qwen3_5_9b` 5 = **20**. The record's 18 was correct when
written; gemini's two started since. **→ OPS: worth dating that figure in the record**, because "18"
reads as a fixed fact and is a moving snapshot.

**Node N5 verified end to end.** Registered: `{test: distributional_gt_placebo_shuffled, metric: cvar,
level: 0.05, direction: one_sided_content_over_format, arm_b: placebo_shuffled}`. Code
(`h2_structure_control`, `:2965`) compares **distributional vs `placebo_shuffled`** at `cvar_level=0.05`,
and `NODE_SOURCES["N5_structure"]` sources `out["h2_structure"]["cvar"]` — the cvar sub-result only, as
registered. **MATCH.** *(Precision note: the function's docstring discusses rejection "on BOTH co-primary
metrics" — that is the broader reporting interpretation, not the node definition, which is cvar-only.
No conflict, but the two should not be conflated in CH6.)*

## ★★★ A22 — leg4's 60 h2_pair TASKS: "FAILED or LOST?" answered from the ARCHIVE ALONE, and the decisive next query is NOT accounting

Ops called this *"the highest-value single query on the board, because FAILED means the CORE line meets
the same thing"* — and reported that `qacct` by job id returns other users' rows (ids are reused/wrapped)
and by jobname times out at 120 s. **It is answerable, for free, from an artefact nobody had opened.**

**`driver_status/leg4_leg_qwen3_5_9b_h2_pair_test.json` — the driver's own bookkeeping:**

```json
{"done": 0, "pending": 60, "exhausted": 0, "rounds": 1,
 "pull_failures": 0, "ops_failures": 0, "phase": "running",
 "queue_names": [ …p01…p08 ], "wall_ts": → 2026-07-31 14:44:30Z}
```
Pack dirs created **2026-07-31 11:12:31Z**.

**★ THE CONTROL IS WHAT MAKES IT CONCLUSIVE — and it is the control the empty-log-dir test lacked.**
`driver_status/leg9_leg_gemini_2_5_flash_h2_pair_test.json`, the batch that is **healthy and running
right now**, reads `done=0 pending=60 exhausted=0 rounds=1 pull_failures=0 ops_failures=0
phase=running`, last written 02:29:09Z. **The two blobs are identical in every field except the
timestamp.** So leg4's status carries **no evidence of failure at all** — it is exactly the signature of
a batch mid-first-wave.

**And the timing closes it.** Packs created 11:12:31Z; driver died ~14:47Z ⇒ **3 h 35 m elapsed**, against
a single training's wall-clock of **4.2 h** (coord's figure; my own `env.json` read gives 15,710 s =
4.36 h). **The first wave could not possibly have completed yet.** Zero completions at 3 h 35 m is not a
symptom — it is the expected state. *(This is coord's record-mtime lesson applied to completions instead
of pulls.)*

**⇒ CONCLUSION, with its limit stated.** The driver observed no failure **because it died mid-first-wave,
before any unit could finish**: `exhausted: 0` means it never wrote off a task, `rounds: 1` means it
never re-polled. This proves there was no failure **up to 14:44:30Z**; it **cannot** prove what happened
on the node afterwards. **⇒ The live hypothesis is neither FAILED nor LOST but ops' own M7 one:**
submitted 11:12Z, would have begun completing ~15:20Z — *after* the driver died — and nobody was left to
pull them.

### ★ The decisive query is a REMOTE DIRECTORY LISTING, not accounting

**Does the node have `record.json` under the h2_pair test dirs?**
`src/cluster/poll.py:remote_completed_dirs()` **already does exactly this** — it is the function every
pull uses to build its transfer list. One bounded ssh call; no accounting file, no job-id reuse/wrapping,
no 120 s jobname timeout.

- **Node HAS them** ⇒ recoverable by a pull, **zero science lost**, and the whole 12 h incident is a
  **PULL gap, not a COMPUTE gap** — meaning leg4's H2 pair may be 60 units further along than any
  instrument currently believes.
- **Node has nothing** ⇒ *only then* is "did they fail?" the right question, and only then is accounting
  worth its cost.

> ### ⚠⚠ A22 AMENDED 04:40Z — MY CONTROL WAS COMPROMISED, AND I THEN COMPOUNDED IT (P123)
>
> **(1) The healthy control is no longer healthy.** `leg9_gemini_h2_pair` — the batch whose identical
> status blob I used to make leg4's diagnosis "positive rather than merely not-negative" — **is now
> itself unattended at 0/60**, last driven 03:32:15, driver alive and logging. Verified first-hand; the
> two blobs still differ in **no** substantive field. **⇒ The blob is consistent with DEAD (leg4), ALIVE
> (leg9 at 02:00Z) and UNATTENDED (leg9 now) — it cannot discriminate liveness in EITHER direction.**
>
> **What survives:** the **LOST-not-FAILED** conclusion ops acted on. It rests on `exhausted=0`,
> `rounds=1` and the 3 h 35 m-vs-4.2 h timing — none of which depends on leg9. **What does not:** the
> corroboration I hung on it. I wrote that the identity to a healthy running batch *"makes the answer
> positive rather than merely not-negative."* **An identity to a control that cannot discriminate proves
> nothing about liveness.** I dressed a valid conclusion in an invalid supporting argument — P41 in its
> most seductive form, because the conclusion was right so nobody had reason to inspect the reasoning.
>
> **(2) P123 — AND THEN I QUANTIFIED SOMEONE ELSE'S UNESTABLISHED CAUSAL CLAIM.** Coord wrote *"neither
> survived a driver restart."* I did not merely repeat it — **I computed a Wilson 95 % CI of
> [34.2 %, 100 %] on "2 of 2 orphaned by a restart" and told Tamer the true orphan rate is at least
> 34 %.** Coord then retracted the causal wording themselves. **Putting an interval on an unestablished
> causal claim does not make it more rigorous — it launders the assumption into a number**, and supplies
> exactly the false precision that stops anyone challenging the category.
>
> **The denominator was also wrong on its own terms, from data I had already printed:** leg9 last drove
> h2_pair at **03:32:15**; the restart was **03:42:47**. **leg9 stopped being driven 10.5 minutes BEFORE
> the restart**, so it cannot belong to the class "orphaned by a restart." **A rate over a mis-defined
> set, not merely an imprecise rate.**
>
> **HONEST RESTATEMENT (coord and I agree):** *2 of 2 pair tests are currently unattended at 0/60 while
> their siblings are driven every ~3 minutes.* **The cause is undetermined** between (a) the restart
> orphaned them — a defect — and (b) the driver has not reached the pair test yet, since
> `campaign.py:1832-1846` sequences it after the per-arm block drains and both legs still have arms in
> search. Both readings fit every fact; **they imply opposite actions, so choosing without evidence is
> the expensive mistake.**
>
> **What needs no causal resolution, and is why this stays time-critical:** the pair-test call is the one
> stage **outside every exception handler** *and* **sequenced last** — highest interruption exposure,
> lowest protection in the campaign. Structural, true either way, and **the core line builds the
> identical array for the CONFIRMATORY contrast at C4.** One bounded `remote_completed_dirs()` call
> settles both legs and both readings at once.
>
> **The corollary my error adds to coord's:** under time pressure the causal sentence writes itself —
> **and the QUANTIFIED causal sentence writes itself faster still, because computing an interval FEELS
> like the rigorous move while it is the step that stops anyone questioning the category.**

### Two smaller forensics, one of which is a trap I nearly fell into

- **No `leg4_leg_qwen3_5_9b_h2_pair_test.permanent.jsonl`** exists, while every other leg4 batch has one
  per generation — the permanent-abandonment ledger was never written for it, consistent with no task
  ever being written off.
- **⚠ EPILOGUE LEDGERS DO NOT DISCRIMINATE, and I nearly reported that they did.** `ledger/` holds
  **1,519** `*.epilogue.jsonl` and leg4's h2_pair packs have **zero** — which looks damning until you
  check that **leg9's h2_pair also has zero while running**. An epilogue is evidently written at pack
  **completion**, so its absence means *"not finished"*, not *"never ran"*. **That is the identical trap
  as ops' empty node-side log dir, and I only avoided it because they had published theirs** — their
  disclosure of a *non-discriminating* test directly stopped me publishing the same one. **Publishing
  what does NOT work has now paid for itself.**

## ⚠ A23 — THE FOUR D16 RECORDS EXIST IN NO LOCAL COPY (one precise question for ops, one of which is time-critical)

Searched the **whole repo**, not just `outputs/`. The only `baseline_volatility_scaled_return-s14..s17`
directories anywhere are under `outputs/campaign_cluster/`. The write-up lane identified those as RUN 1;
**I can now prove it from two fields they had not read**:

- `cpu.model_name` = **Intel Xeon Gold 6240 — not the 6140**
- `git_commit` = **`deployed-archive:ce27dfc5…`** — a *different* deployed archive from RUN 4's `b9e6df55…`

**⇒ Definitively not the D16 four.** A different substrate *and* a different code version that merely
share the unit and seed names. And **no new quarantine directory exists locally**: every
`*quarantin*` / `*superseded*` dir under `outputs/` is dated 2026-07-27/28, pre-campaign.

**⇒ As far as this lane can see, the RUN 4 Xeon-6140 records are preserved only on the NODE.** The most
likely reading of ops' *"quarantined … AND locally"* is **removed** from the local RUN 4 tree — which I
confirm (`campaign_cluster_run4` holds 26, missing exactly 14–17) — rather than **preserved** in a local
copy. That is a reasonable thing to have meant.

**Two asks, the second time-critical:**
1. List the four at their node quarantine path, so *"four copies in three places"* is verifiable rather
   than asserted.
2. **★ Confirm `--resume` CANNOT write over them.** The re-run writes new records for seeds 14–17; if the
   node-side quarantine did not move the originals clear of the write path, **the re-run destroys the one
   artefact ops' own bit-comparison experiment needs.** Old-6140 vs new-6240 is a *measurement* only
   while **both** sides exist.

## A15-bis — `analyze_campaign.py:5983` is NOT a duplicate of A15, and a blanket "fix" would INTRODUCE an error

Write-up's residue grep flagged that `:5983` still emits *"The LLM DSR is deflated by …"*. It does — in
**emitted prose**, not a comment. **But it is not the A15 defect repeated.** I read what that block
actually reports: it is the **report-only descriptive H1 panel**, and it emits *five* quantities —
best hand reward (median test **Sharpe**), LLM winner (median test **Sharpe**), Fraction beaten (per-seed
**Sharpe** > human bar), Normalised improvement (relative **Sharpe**), and then an explicit
`- **DSR:** LLM {winner_dsr} vs best-baseline {best_baseline_dsr} → beats-on-DSR`.

**So unlike N6, this block genuinely contains a deflated-DSR comparison** — `winner_dsr` really is
deflated by `n_trials` (`:3045`) and really is compared against `best_baseline_dsr`.

**⇒ The sentence is CORRECT for the DSR bullet and WRONG for the three Sharpe-based metrics.** Its defect
is **scope**: it is written as a blanket preamble characterising the whole panel, while characterising
only the one DSR line at the end — and the three quantities the panel *leads* with are Sharpe-based,
where no deflation counterweight exists and where the real asymmetry (best-of-30 vs one un-tuned
specification) **favours the LLM**.

**The correct fix is narrower than A15's: SCOPE the sentence to the DSR bullet** and state the Sharpe-side
asymmetry beside the Sharpe metrics. **Do NOT delete or invert it wholesale — that would put a false
statement on the one line where it is currently true.**

> **★ The general hazard, worth keeping:** a residue grep proves the presence of a **string**, not of a
> **defect**. "Fix everything that matches" is how a correct sentence becomes a wrong one. The grep
> rule is right; this is the caution that makes it safe to apply.

## ★★ A24 — COORD'S P117 GENERALISATION EXPLAINS WHY A16 SURVIVED, AND A16 IS ITS HIGHEST-STAKES INSTANCE

Coord found that a safety property they had documented — *"the guard never blocks an unregistered
session"* — was **false for an hour**, and that their selftest for it **passed all night and began
failing the moment ops registered a real hold**. The test did not change; **the world changed underneath
it**. Their generalisation:

> **A documented safety property that no test exercises against LIVE STATE is a CLAIM, not a GUARANTEE.**

**That is exactly the shape of A16, and A16 is the more consequential instance.**
`tests/test_graphical_alpha.py:112` hand-injects `p["N2_h2_ra"] = 0.001  # equivalence proven via TOST`
**directly into `graphical_alpha_propagation`, bypassing `tier_node_pvalues`.** The test passes — and it
passes *precisely because* it never exercises the path that would have to produce that p-value. The
registered property ("N2 can reject via TOST") is asserted in the yaml, exercised nowhere against the
real extraction layer, and **absent from the code**.

**Two independent lanes hit the same failure mode within an hour, in their own instruments.** That is
strong evidence it is a *systemic* pattern in this codebase, not two coincidences — and it is the
argument for a pre-submission sweep asking, of every registered guarantee: *which test exercises this
against live state, and would it fail if the property were removed?*

## ★★★ A25 — THE CONFOUND CHECK I PROMISED, DISCHARGED. It kills half my own lead and produces a much better exhibit.

I flagged the R115/reject concentration on the Qwen legs as *"a lead, not a finding — it needs a
pool-size confound check before it is claimed."* **Here is the check.** Effect-blind throughout:
authoring reliability is an *instrument* property; no sealed outcome is read.

**Rates with 95 % Wilson intervals, not raw counts:**

| line | attempts | reject rate (95 % CI) | R115 / accepted (95 % CI) |
|---|---|---|---|
| **`qwen3_5_9b`** | 133 | **84.2 % [77.1, 89.4]** | 4/21 = 19.0 % [7.7, 40.0] |
| `nemotron_3_super` | 112 | 20.5 % [14.1, 28.9] | 1/89 = 1.1 % [0.2, 6.1] |
| `glm_5_2` | 117 | 12.8 % [7.9, 20.1] | 2/102 = 2.0 % [0.5, 6.9] |
| **`qwen3_6_27b`** | 116 | **7.8 % [4.1, 14.1]** | 4/107 = 3.7 % [1.5, 9.2] |
| `deepseek_v4_pro` | 113 | 5.3 % [2.5, 11.1] | 1/107 = 0.9 % [0.2, 5.1] |
| `haiku_4_5` | 122 | 4.1 % [1.8, 9.2] | 1/117 = 0.9 % [0.2, 4.7] |
| `gpt_5_6_luna` | 133 | 3.0 % [1.2, 7.5] | 0/129 = 0.0 % [0.0, 2.9] |
| `gemini_2_5_flash` | 115 | 2.6 % [0.9, 7.4] | 0/112 = 0.0 % [0.0, 3.3] |
| **`search` (core, Opus)** | 107 | **0.9 % [0.2, 5.1]** | 0/106 = 0.0 % [0.0, 3.5] |
| `kimi_k3` | 114 | 0.9 % [0.2, 4.8] | 1/113 = 0.9 % [0.2, 4.8] |
| `sonnet_5` | 123 | 0.0 % [0.0, 3.0] | 0/123 = 0.0 % [0.0, 3.0] |

**(1) The confound I was worried about DOES NOT EXIST.** Attempt counts are near-uniform across legs
(**107–133**). Every leg has had a comparable number of authoring attempts, so the raw counts were
already fair on that axis.

**(2) `qwen3_5_9b` is decisively distinguishable — not an artifact.** 84.2 % [77.1, 89.4] against the
next-worst 20.5 % [14.1, 28.9]: **disjoint intervals.**

**(3) ★★ THE STRONGEST EXHIBIT IS THE QWEN PAIR, AND IT IS BETTER THAN THE GRADIENT I STARTED WITH.**
`qwen3_5_9b` **84.2 %** vs `qwen3_6_27b` **7.8 %** — **~11× apart, intervals wildly disjoint** — and R103
set an **identical reasoning configuration across the pair precisely to preserve a confound-free
capability contrast.** Same family, same provider, same serving stack, same reasoning pin, one
generation apart. **The cross-family gradient confounds provider, tokenizer, RLHF and serving stack; the
Qwen pair controls all four.** This is the numeracy-bottleneck headline's single cleanest piece of
evidence and it was sitting unused.

**(4) ⚠ AND IT KILLS HALF MY OWN LEAD — stated plainly.** I wrote that *"the two Qwen legs account for
8 of the 13 R115 breaches."* **As RATES that claim does not survive:** `qwen3_5_9b` 19.0 % [7.7, 40.0]
vs `qwen3_6_27b` 3.7 % [1.5, 9.2] — **overlapping intervals, NOT distinguishable.** The 8-of-13 framing
was a **counting artifact**: `qwen3_6_27b` has five times more *accepted* candidates, so it accrues more
breaches at a much lower rate. **⇒ The capability gradient shows up decisively in REJECT RATE and only
weakly in R115 breach rate.** Two instruments, very different sensitivity — and the one I led with was
the weaker.

**→ WRITE-UP: use the reject-rate table and the Qwen pair; do NOT use "8 of 13."** Note also the core
confirmatory line (Opus) sits at **0.9 % [0.2, 5.1]** — near-perfect authoring on the arm that gates
every hypothesis, which is worth one sentence of its own.

## ★★★ A26 — TWO FROZEN WINNERS ARE CONTAMINATED. The core line is clean; the unqualified claim is not.

The coord lane reported *"no frozen winner is contaminated,"* having verified the three core-line
winners. **The core-line half is exactly right and I confirm it. The generalisation does not hold.**

**Method matters here:** the frozen **marker** carries **no R115 fields at all** —
`train_safe_default_count` and `train_safe_call_count` are `None` on all 27 — so anything read off the
marker is not a measurement. I resolved each marker's `candidate_id` back to **its own line's** search
tree on the **composite `(line, candidate_id)` key** (coord's P120 lesson, applied), 27/27 resolved.

| frozen winner | source candidate | safe_default_frac |
|---|---|---|
| **`frozen_leg_qwen3_5_9b/distributional-winner`** | `distributional-g5-c0` | **0.078535** (31,414 / 400,000) |
| **`frozen_leg_qwen3_5_9b/placebo_shuffled-winner`** | `placebo_shuffled-g0-c3` | **0.090847** (36,339 / 400,000) |
| all 25 others — incl. `distributional-g5-c1`, `scalar-g2-c0`, `random_search-c25` | — | **exactly 0.000000** |

**⇒ The surviving statement, and it is the one that matters: ALL THREE CORE-LINE FROZEN WINNERS ARE
EXACTLY 0.000000.** The confirmatory line's selected objects are entirely uncontaminated.

**This is NOT a gate failure** — both contaminated winners are *below* the 0.10 floor, so R115 admitted
them correctly. But two things follow that nobody had said:

1. **R115's floor means a winner may carry up to 9.99 % inert training and still be selected** — and on
   `qwen3_5_9b` two arms' winners actually do. That leg is already the **84.2 % reject-rate** outlier
   (A25); its *selected* winner being ~8 % inert compounds the same capability story, and that winner is
   what carries into the leg's H2 test ladder.
2. **`placebo_shuffled-g0-c3` at 0.0908 is the second-closest candidate to the exclusion floor in the
   entire campaign — and it WON its arm.**

**Threshold sensitivity, measured, never previously stated.** The distribution is heavily bimodal —
**1,667 of 1,737 records are exactly zero**, 43 in (0, 0.01), 7 in [0.01, 0.05), 4 in [0.05, 0.09),
**2 in [0.09, 0.10)**, and 14 breaches. So R115's placement is insensitive almost everywhere —
**except that exactly one candidate sits 0.0035 pp below the line:**
`search_leg_qwen3_5_9b/placebo-g2-c2` at **39,986 / 400,000 = 0.099965**. **That is fourteen
safe-default calls out of 400,000 from exclusion** — and it is **the same candidate A9 identified as one
of only three in the campaign that received no feedback at all at generation ≥ 1.** One record, on one
report-only leg, is simultaneously the un-fed outlier and the R115 boundary case. Probably coincidence;
too pointed to leave unrecorded.

**P121 — TWO ERRORS OF MINE GETTING HERE, both caught by IMPOSSIBLE OUTPUT rather than by care.**
*(a)* I globbed `*/*/*/record.json` for the winners and got **zero** — frozen markers sit one level
**shallower**, at depth 3. **That is the identical depth trap as D18, which I root-caused six hours
earlier.** *(b)* Worse: my script defaulted a missing field to `0.0`, so it printed `frac=0.000000` for
all 27 markers and concluded **"0/27 contaminated" — a fabricated clean from an ABSENT field.** I caught
it only because *"0 frozen winners found"* is impossible, which made me re-read the glob, which exposed
the `None`. **Had the glob been right and the field still absent, I would have shipped a false all-clear
on exactly the question this section corrects.** The lesson is narrow and sharp: **a default value for
missing data turns "not measured" into "measured clean" — never default a field you are auditing.**

## ⚠⚠ A29-CORRECTED — MY SEED-RUNG CONCLUSION INVERTS. Ops quantified the caveat I had only named.

**I reported: rung 568 is "marginal" at 0.4–8 % headroom, and the binding constraint is whether the ten
report-only legs climb with the core. Both conclusions are WRONG, and the reason is the caveat I listed
myself and then failed to propagate.**

**The mechanism (ops, from record §95.2):** during **SEARCH** a candidate takes **8 cores for ONE
training** (8 threads at the field-measured 1.92× speedup) = **0.24 trainings per core-unit**. At **C4
with pack 8** it is **8 cores for EIGHT trainings**, one core each, OMP=1 = **1.00 trainings per
core-unit**. **Per-core throughput QUADRUPLES the moment a line crosses its gate** — and my 21.1
records/h was measured almost entirely on the *search* side of that transition.

**Cross-checked by an independent route, which is why I accept it:** the registered model gives 34,080
test records over 15.6 d = **91 records/h**, against my measured 21.1/h during search — a ratio of
**4.3×**, reproducing the §95.2 arithmetic derived a completely different way. **Two routes agreeing.**

**Corrected picture:** rung **403** (the registered primary target) lands **08-09, 18 days before the
stop**; rung **568** lands **08-13, 14 days before.** Rungs 30 and 100 are **critical-chain bound** at
4.6 d, so more cores do nothing for them. **The full ladder is not marginal, and the legs climbing
alongside is not the binding constraint — the packed C4 lane absorbs them.**

> **★ THE LESSON, and it is sharper than the error.** I *did* flag this: caveat (2) read *"throughput
> should RISE once search completes … so 21/h may UNDERSTATE the endgame."* **I named the dominant
> uncertainty and then let the point estimate carry the headline anyway.** Naming a caveat is not
> propagating it. This is the same family as **P116** (I used a median as a bound) — right qualitative
> insight, conclusion drawn from the central estimate as though the caveat were decoration.
> **If an uncertainty is large enough to invert the conclusion, it is not a caveat — it is the analysis.**

**★ A separate correction from the same message, and it touches a standing priority:** the compute
**saturation point is 3,235 cores at rung 568 and 2,336 at rung 403 — NOT the 4,584 quoted all
campaign.** That figure came from an *isolated-machine* bench thread-speedup of 2.72×; the field
measurement across **740 timed trainings is 1.92×**. Past 3,235 the critical chain binds and more cores
buy nothing. **Any plan built on reaching 4,000 cores was chasing a number that does not exist.**

**What ops would not claim, and nor will I:** the model assumes ~960 cores hold and that C4 packing
realises its measured rate at full scale, and coord's p90 time-to-first-completion of 25 h is real
variance the model does not carry. **Treat 08-13 as central with a band, not a promise.**

## ★★★★ A30 — THE POPART CONFOUND-MITIGATION CLAIM HAS **NO INSTRUMENT**, and h3ss now inverts it if recomputed

**Two findings, and the second is the one that matters.**

**(1) h3_singleshot contamination reached a science claim.** `h3ss` is the H3 single-shot control — the
campaign's **only single-arm line**, all its records tagged `distributional`. Its ladder is now 450+ and
climbing. Computed campaign-wide, as any archive-wide derivation does:

| arm | h3ss INCLUDED | h3ss EXCLUDED (the H2 family) |
|---|---|---|
| distributional | **27.0 %** [23.9, 30.3] | **60.6 %** [54.8, 66.2] |
| scalar | 63.7 % [58.0, 69.1] | 63.7 % [58.0, 69.1] |
| placebo | 58.6 % | 58.6 % [52.2, 64.6] |
| scalar_cvar5 | 51.8 % | 51.8 % [45.3, 58.3] |
| placebo_shuffled | 60.7 % | 60.7 % [53.3, 67.6] |
| **spread** | **36.8 pp, dist-vs-scalar DISJOINT** | **11.9 pp, all five OVERLAPPING** |

**Included, §44.4's "PopArt is arm-symmetric, therefore cannot confound H2" is flatly refuted. Excluded,
it holds.** The failure direction is the dangerous one — **a false alarm that looks like a fatal
confound** will be believed and acted on, unlike a false all-clear. **And my own M12 figure (63.8 % at
02:00Z) is now 27.0 % by the identical computation** — stale in a way that *inverts the conclusion it
was certifying.*

**(2) ★ THE REAL DEFECT: the claim is produced by NO INSTRUMENT.** I first asked ops to filter h3ss out
of `results_audit` §4. **Wrong fix — I had checked where the number was wrong, not where it comes from.**

- `results_audit` §4 emits only a **campaign-wide** engaged/pinned split — no per-arm breakdown at all,
  so it is contaminated in *level* but does not emit the asymmetry.
- **`scripts/analyze_campaign.py` contains ZERO references to `popart`** (`grep -c` → 0). The per-arm
  claim is **not among the 35 enumerated `out[...]` keys** and is computed **nowhere in the pipeline.**
  I derived it by hand, certified it, and broadcast it — **nothing checked me and nothing would have.**

**And it reaches the paper.** `paper/APPENDIX_B_limitations.md:35-36` names the **SAC reward-scale →
effective-entropy confound** and states the mitigation is *"a uniform PopArt normaliser with
realised-scale logging"*; `paper/01_LITERATURE_DOSSIER.md:251-252` instructs *"…present PopArt as the
principled mitigation, disclose the residual, and **report the σ_max table**."* **That σ_max table — the
per-arm quantity — exists nowhere in the analysis pipeline.**

> **CLAUDE.md's scope clause names this case verbatim:** *"the enumerated scope is machine-defined — the
> 35 `out[...]` keys … **A quantity that reaches the PDF and is not in that enumeration is a defect in
> the enumeration, not an exemption.**"* This is that case, on the **mitigation for a named confound to
> the headline hypothesis.**

**CORRECTED ASK (supersedes the h3ss-filter one): add per-arm PopArt engagement — h3ss-excluded, with
intervals, i.e. the σ_max table the dossier already specifies — to `analyze_campaign`'s output keys**, so
it enters the enumerated scope, the `WHY_REGISTER` gate, and the pre-submission check. That is the
difference between a number recomputed by hand each time and a registered analysis output.

**→ WRITE-UP:** until it exists, the arm-symmetry sentence has **no instrument behind it**. Ship the
values **with** their intervals — *the entire force of the claim is that they overlap* — dated, and
re-measured at write time.

**My lesson:** *where a number is wrong* and *where a number comes from* are different questions, and
only the second tells you what to repair.

## MY OWN ERRORS THIS SESSION — P108, P109, P110 (drawn from the bus arbiter, not guessed)

Logged per the standing rule that every mistake is recorded with root cause, how it was found, the fix,
and the lesson. **None reached a conclusion Tamer or another lane acted on.**

**P108 — I read a MID-WRITE `git diff` as final.** While the ops lane was actively saving
`src/llm/client.py` (D13), I diffed it and concluded their Anthropic-path hunk "repeats the exact bug
they had just fixed on the OpenAI path" — the validation appearing to sit *outside* the retried
callable. **Found by:** reading the live file before posting. It was correct; the check is inside
`_call` on both transports. **Lesson:** when another lane is editing, read the **artifact**, never the
diff — a diff of a file being written is a snapshot of a half-applied edit.

**P109 — I keyed PopArt engagement on a constant flag and got a flat 0.0 % on every arm (0/1594).**
`popart_scale["popart"]` is an on/off marker, not the scale; the engagement predicate is
`sigma_max > 1.0`. **Found by:** the clean-0 tell — a perfect 0 % across five arms and eleven canon
rewards is a claim about my script, not the world. `results_audit`'s own docstring records the sibling
trap (*"`popart_scale` is a DICT, not a float"*). Corrected value 811/1594, matching the instrument.

**P116 — I used a MEDIAN as a BOUND.** In A22 I wrote that leg4's first wave *"could not possibly have
completed yet"*, reasoning from a ~4.2 h training time against a 3 h 35 m window. The coord lane measured
the actual distribution over **n = 1220** records — MIN **2.79 h**, p05 3.05, MEDIAN 4.21, p95 7.61, MAX
14.31 — and **227 of 1220 (18.61 %) finished faster than 3.58 h**, so the naive expectation is **~11 of
60**, not zero. **"Could not possibly" is a claim about the LEFT TAIL, and I had only looked at the
centre.** *(Their queue-wait caveat is the right counterweight and belongs with it: elapsed-from-creation
includes queue wait while `wall_clock` does not, so ~0.8 h of wait drives the expectation back to zero —
the honest interval is 0 to ~11, decided by something neither lane can observe from the laptop.)*
**Lesson:** a central tendency is not a bound; "impossible" needs the extreme, not the average.
**What survives:** *no evidence of failure* still stands — it rests on the `driver_status` control and on
`exhausted=0`/`rounds=1`, which the correction does not touch. **And the correction makes the
recommendation STRONGER**: up to ~11 finished units may sit on the node unpulled, so
`remote_completed_dirs()` is no longer merely "settle failed-vs-lost" but "recover up to 11 units of the
H2 pair that every instrument currently counts as zero."

**P119 — MY OWN FALSIFIER WAS MIS-CALIBRATED AND WOULD HAVE FIRED A FALSE ALARM AT 08:00Z.** My M27 rule
said *"if leg4 h2_pair is still 0/60 at 08:00Z, the sequencing account is REFUTED and the batch is
genuinely stranded."* I derived 08:00Z from an **arrival-rate proxy on the control arms' completions** —
a different quantity entirely — rather than from the distribution that governs. Coord's n=254
**time-to-first-completion** measurement settles it: **p50 5.36 h, p90 25.06, p95 27.95, MAX 30.56 — a
HEALTHY batch sits at `done=0` for up to ~30 h.** leg4's packs were created 07-31 11:12:31Z, so at
08:00Z it would be **~21 h old, inside p90**. **My rule would have declared "genuinely stranded" on
evidence that does not support it** — and the conclusion might even have been right, which is **P41's
shape**: a wrong reason reaching a right action, the hardest kind to catch, and something I had quoted
at two other lanes the same night. **I calibrated against the quantity I could see instead of the one
that governs.**

**The fix changes the PREDICATE, not the clock.** "Still 0/60" is uninformative for ~30 h, so no
threshold on that signal is workable. The discriminating condition is **event-driven** and comes
straight from `campaign.py:1832-1846`: **once `placebo_test` AND `placebo_shuffled_test` are complete,
does the driver ENUMERATE h2_pair?** Yes ⇒ the sequencing account holds. Precondition satisfied and
still unnamed ⇒ refuted **on the correct axis** (unmentioned, not merely uncompleted). Watcher
re-armed on that test; syntax-checked before restart.

**Current reading, claiming nothing:** packs 16.2 h old, `done=0` (**inside p90 → uninformative**), zero
mentions since the 02:42Z relaunch while its sibling batches are named every round — but
**the precondition is NOT yet satisfied** (placebo 24/30, placebo_shuffled 0/30), **so the test has not
run and no conclusion is available.** That is a more useful state than my old rule would have produced
at any hour.

**P110 — I turned a citation of a PRECEDENT into a claim of a live OBSERVATION, and propagated it.**
I credited the coord lane with "also finding leg7 at 8h29m"; that figure is the **historical**
2026-07-29 incident in `arm_coverage.py`'s docstring, which they had quoted as the failure *shape*.
It reached my CHANGELOG block, the cursor and my report to Tamer before coord corrected it.
**Retracted in all three.** **Lesson, and it is the sharpest of the three:** the error rode in on the
credibility of the thing it was attached to — I was *praising convergent verification* while
manufacturing a second observation that did not exist. That is P41's shape (a wrong reason reaching a
right action) in a new dress.

> **★ THE GENERALISATION ACROSS ALL FOUR LANES' ERRORS TONIGHT.** Mine (P108, P109), and coord's two
> near-misses (*"the cores probe has failed"* — the field is only populated under `--ssh`; *"two lines
> stalled 4.5 h"* — record mtime is **pull** time and a training is 4.2 h), and writeup's P107 (a clean
> 100 % from a field that is an empty stub) are **all the same failure**: *reading a value whose MEANING
> was not what its NAME implied* — a conditionally-populated field read as unconditional, a timestamp
> read as a different timestamp, a flag read as a scale, an empty stub read as data. **That is a sharper
> rule than "suspect a clean 0 %/100 %"**, because it names the cause rather than the symptom, and it
> predicts the cases where the number is *not* suspiciously round.

## Standing note — three findings, one shape

A1 (a batch at `0/60` for 10.5 h), A10 (a column NaN on 100 % of records) and A11 (a field empty on 100 %
of records) all passed every gate. **Each is a quantity no instrument looks at, and in two of the three
the tell was a perfect 0 % / 100 %.** The campaign's monitoring is excellent at *values that move* and
blind to *values that never do*. **That is the single most useful generalisation from tonight, and it is
the argument for the per-batch stall detector (A1-c) plus an "always-constant / always-null field" sweep
over the archive schema before the confirmatory analysis runs.**

---

## A33 — "Is the issue the sandbox?" — NO. The M130 cluster is R41's pre-registered `unbounded_magnitude` class, and the one check that could have made it an artifact passes

**Origin.** Tamer asked directly whether we have mis-attributed a harness defect as a science finding.
That is the right question to ask of any result whose mechanism runs through our own code, and it
deserved a measurement rather than a defence of the sandbox.

**The mechanism, from the artifact.** In
`outputs/campaign_cluster_run4/search_leg_haiku_4_5/distributional/distributional-g1-c3/record.json`
(`reward_source`):

```python
# Sortino-like metric: excess return / downside volatility
# Use a small constant to avoid division by zero
sortino_base = mean_ret / (downside_vol + 1e-8)
```

The author guarded **division by zero** and not **magnitude**. As `downside_vol → 0`,
`mean_ret / 1e-8` = `mean_ret × 1e8`, which breaches the `|total| > 1e6` contract bound at
`src/sandbox/executor.py:780-830` and substitutes `SAFE_DEFAULT = 0.0`. A second path reaches the same
place: `np.std(downside_rets, ddof=1)` over a single below-mean return is NaN, and `+ 1e-8` does not
rescue it, so the non-finite branch fires. **`downside_vol` shrinks as the agent succeeds — the reward
degenerates *because* the policy is working.**

**It was predicted.** `PREREGISTRATION.md:889` — amendment **R41, 2026-06-25** — registers a first-class
forensics class `unbounded_magnitude`: *"rewards of the form `return / (variance + ε)`, unbounded above
as realized variance → 0 (the critic-explosion mechanism; Skalse 2022; Pan et al. 2022) — flagged on
CODE SHAPE independent of fitness."* R42 (`:890`) records the prototype instance (`scalar-g5-c3` = 1.15e4
→ SAC Q-target ≈ 1e6 → critic loss 1.1e7). The bound is therefore the **second of two independent
defences against a phenomenon the project named two months before the campaign** — PopArt protects the
critic, the contract bound protects the reward.

**The discriminating check: is the guard arm-differential?** If it bit unequally it could manufacture a
between-arm effect and the finding would be an artifact.

> ⚠ **CORRECTED 11:5xZ — the first measurement used the same under-covering glob as P134.** The
> original pass reported n=1,237 (distributional 15/277, scalar 18/284, placebo 11/241, scalar_cvar5
> 12/222, placebo_shuffled 12/213) and **those numbers were transmitted to ops in M135 and to writeup
> in M136.** They came from a partial archive walk. **The table below is the full-coverage
> re-measurement and supersedes them. The conclusion is unchanged — every interval still overlaps
> every other — but the numbers below are the ones that may be quoted.**

Measured over **n=1,278** LLM-authored search records carrying both counters — fraction of candidates
with ANY substitution, Wilson 95%:

| arm | any substitution | 95% CI | mean fraction of calls |
|---|---|---|---|
| distributional | 15/307 = 4.9% | [3.0, 7.9] | 0.00884 |
| scalar | 18/285 = 6.3% | [4.0, 9.8] | 0.00936 |
| placebo | 11/247 = 4.5% | [2.5, 7.8] | 0.00360 |
| scalar_cvar5 | 12/224 = 5.4% | [3.1, 9.1] | 0.00514 |
| placebo_shuffled | 12/215 = 5.6% | [3.2, 9.5] | 0.00612 |

**Every interval overlaps every other.** The guard cannot produce a between-arm effect; identification
is safe. **This is the check that had to pass for "finding" rather than "artifact", and it passes.**

**Two items are nonetheless genuinely about the sandbox, and neither is a fix.**

> ⚠ **DO NOT CHANGE `src/sandbox/executor.py` OR `src/reward/contract.py`.** Altering `SAFE_DEFAULT` or
> the `1e6` bound mid-run would split RUN 4 into two arithmetic regimes and break CRN pairing. Both
> items below are **disclose-and-document**, never remediate.

- **(a) The `1e6` value is not hash-bound.** R41/R42 register the *phenomenon*; the specific threshold
  was added by the 2026-07-22 audit (row 30e, per the executor comment). Neither `PREREGISTRATION.md`
  nor `config/preregistration.yaml` carries the number — grepped both. **Correct phrasing: "an
  audit-added implementation guard, set pre-data." Never "pre-registered."** Same category as the
  equal-k sensitivity. Ops holds the provenance confirmation (M135).
- **(b) Substituting `0.0` discards direction.** The alternative was to **clip to ±1e6**, preserving
  sign and magnitude ordering. Zero tells the agent *"nothing you did mattered"*; clipping tells it
  *"this was extreme."* A constant zero across a region of state space is itself a signal, and a
  misleading one. No record found that the alternative was considered — on current evidence an
  undocumented default. It interacts with **R115**: the 10% execution floor admits winners with up to
  9.9% of training steps on that null signal, so the choice is not cosmetic.

**What is NOT claimed.** I have not established that the substitution measurably harmed any winner's
policy. That needs a per-candidate steps-on-null vs outcome comparison, which I have not run and which
the 5.4% base rate may leave underpowered. **Stated as an open quantity, not a finding.**

**Handed off:** ops M135 (provenance of row 30e + whether clip-vs-zero was ever evaluated), writeup M136
(the CH6 mechanism paragraph + the two Appendix-B disclosures + the wording trap).

---

## P-LEDGER P131–P134 — four self-inflicted measurement errors, all inside `results_cycle.py`, all caught before reporting

Logged per the standing rule that **every mistake is recorded with root cause · how it was found · the
fix · the lesson**. None of these reached Tamer or another lane as a campaign finding. They are logged
because the pattern is more instructive than any of them individually: **all four were committed within
two hours, in a tool built to detect exactly this class of error, by an operator who had just written
the generalisation that names it.**

| # | The error | Scale of the false signal | Root cause | Fix |
|---|---|---|---|---|
| **P131** | Read `metrics.val_fitness` on every tier | **326 false "non-finite" + 4 false "degenerate unit"** | `val_fitness` is a SEARCH-stage quantity — NaN by design on test records, and where present it is the winner's carried-over search number, identical across all 30 seed replicates *by construction*. The test-tier outcome is `test_sharpe`/`test_cvar05`. | `OUTCOME_BY_TIER` |
| **P132** | Seed-duplication check applied to the search tier | **58 false duplicate-seed units** | Search records are CANDIDATES at a single seed (verified `distributional-g0-c0…g1-c0` all `seed=0`), not seed replicates. | `SEED_REPLICATE_TIERS` |
| **P133** | Array shape-tags (`<list:N>`) compared as values | constant-field report inflated **9 → 31** | Length-constancy was indistinguishable from value-constancy. | segregate `shape_constant` |
| **P134** | Fixed-depth globs | **594 of 2,369 records invisible**, then a clean reported over the visible 75% | Records exist at depths **3, 4 and 5**; every frozen winner is at depth 3, plus the whole `test_h3_singleshot` tier (560) and two depth-5 records. | walk the tree, classify by directory, FATAL on a zero-record walk |

**How each was found.** P131/P132/P133 by refusing to believe the tool's first output and checking a real
record's actual keys and a real search record's actual seeds. **P134 by reconciling against an
independent counter** — ops' cycle reported 2,334 records against my 1,774. Without that second,
independently-derived number the under-coverage would have been invisible, because the tool was internally
consistent and reported no error.

**The two lessons, stated separately because they are different.**

1. **P131 and P134 are the SAME failure as A10/A11, committed by the detector.** A10/A11's
   generalisation was *"reading a value whose MEANING was not what its NAME implied."* P131 read
   `val_fitness` as if the name meant the same thing on every tier. P134 is **P121 verbatim** — the
   depth-3 frozen-winner trap this lane had root-caused hours earlier. **Knowing a failure mode does not
   confer immunity to it**; only a check does. Both fixes therefore remove the assumption rather than
   patch the instance (a tier-keyed field map; a depth-agnostic walk), and both carry a load-bearing
   comment marked *do not tidy away*.
2. **Internal consistency is not correctness.** P134's clean was self-consistent, error-free and wrong.
   The only thing that caught it was a **second number derived by someone else's instrument**. That is
   the argument for keeping ops' counter, coord's batch detector and this lane's cycle as *independent*
   measurements rather than consolidating them — and for treating any disagreement between them as a
   finding, never as noise to be reconciled away.
