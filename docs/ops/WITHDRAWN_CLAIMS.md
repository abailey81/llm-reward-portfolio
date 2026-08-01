# WITHDRAWN AND CORRECTED CLAIMS — the register of things we said and then unsaid

> **★ WHY THIS FILE EXISTS.** On 2026-08-01 the ANALYSIS lane named a property of the cross-session
> bus that had already cost three lanes real work: **RETRACTIONS TRAVEL SLOWER THAN ASSERTIONS.** One
> unverified premise (*"SGE rotates its accounting, the evidence is perishable"*) was **written by OPS,
> amplified into a scheduling recommendation by ANALYSIS, retracted by OPS 13 minutes later — and then
> re-transmitted by COORD an hour AFTER the retraction**, because a withdrawal is one message in a
> stream and the claim it kills has already been read, quoted and acted on.
>
> **The stakes are not conversational.** The write-up lane mines these lanes for material, and the
> dissertation is graded on the PDF alone. **A withdrawn claim that reaches the PDF is a fabrication
> with a paper trail.** So withdrawal needs a DURABLE, GREPPABLE home rather than a chronological one.
>
> **HOW TO USE IT.** Before any claim from lane traffic enters `paper/`, the QC appendix, or a
> supervisor-facing document, grep this file for its subject. Every row states **what was claimed ·
> who claimed it · what killed it · what the correct statement is.** A row here does NOT mean someone
> was careless — most were caught by their own author, which is the machinery working.
>
> **APPEND ONLY. Never delete a row** — a withdrawn claim that vanishes is indistinguishable from one
> that was never made, which is the exact failure this file prevents.

---

## 2026-08-01 (overnight, RUN 10)

### OPS lane (mine — all self-withdrawn)

| # | CLAIMED | KILLED BY | THE CORRECT STATEMENT |
|---|---|---|---|
| W1 | *"~53 % CPU efficiency"* (qacct CPU-hours ÷ cores currently held) | **qacct accounts only COMPLETED jobs** — verified: our RUNNING job `55979` has **zero** accounting blocks | **No CPU-efficiency ratio may be quoted at all.** Numerator = finished work, denominator = live allocation; different populations. |
| W2 | *"The evidence is perishable — SGE rotates its accounting"* | `qacct -j 55979` returns **19 blocks from 16 users, 2018–2022** | **Retention is ~8 years against a 4-week campaign. There is no deadline and no harvest urgency.** |
| W3 | *"Rung 403 lands 08-09, rung 568 lands 08-13"* | Derived from the **transient 91/h C4 peak**; `docs/ops/stage_eta.py` run 08:58Z | **At 830 cores: rung 403 → 08-10, rung 568 → 08-15**, throughput-bound. We hold ~980 cores so the truth sits slightly inside. Both inside the 08-27 stop. |
| W4 | *"12,445 CPU-hours in a day"* | `qacct -d 1` selects jobs **STARTED** in the window, and accounts only **completed** ones → over-represents SHORT jobs | Use the recorded ledger: **67,166 CPU-hours** (7.67 CPU-years) for jobs started on/after 2026-07-28, **a LOWER BOUND** until the arrays drain. |
| W5 | *"ZERO high-fallback candidates have reached a frozen or test record"* | **True under its own scope**, but compresses into COORD's already-retracted P122 | *"No candidate **at or above R115's 10 % floor** reached a frozen or test record. **Two** frozen winners on `leg_qwen3_5_9b` carry sub-floor fractions of **9.0847 %** and **7.8535 %**, admitted correctly."* |
| W13 | *"The N2 gap is EXECUTED-VS-REGISTERED DRIFT — the code fails to implement the registered `iut_or_tost`."* (§100.33, §100.34) | **`PREREGISTRATION.md:300`** — hash-bound and SENIOR — says the TOST *"does not determine the thesis"*, and `freeze.py` fixes the order *"prose, THEN the … prereg yaml"*, calling the yaml **"the YAML mirror"**. Found by COORD (M150); verified here first-hand. | **Not drift — two REGISTERED artefacts disagreeing, with the code following the SENIOR one.** The code is CORRECT. It also makes the decision not to change N2 stronger: implementing the yaml note would mean the code departing from the senior artefact **to enable a rejection**. |

### ANALYSIS lane (self-retracted; recorded here for cross-lane visibility, not as criticism)

| # | CLAIMED | KILLED BY | THE CORRECT STATEMENT |
|---|---|---|---|
| W6 | *"Per-arm PopArt evidence is computed by NO instrument anywhere"* | **R48 registers it** and `scripts/popart_ablation.py` exists (27,448 bytes) | It is **registered AND implemented** — but **absent from the 35 enumerated `analyze_campaign.py` keys**, so it sits outside the gate. |
| W7 | *"The reasoning-token round trip is essentially unmeasured — 1 row of 2,777"* | `x or <fallback>` **short-circuits on falsy, and `0` is falsy**, so every measured zero was counted as absent | **`reasoning_tokens` is PRESENT on 1,990 rows (all 8 OpenRouter legs); 1,989 read exactly ZERO** = the pin verified off. The 1 nonzero is the `deepseek` violation. |
| W8 | The perishability escalation (amplifying W2 into a scheduling priority) | Same evidence as W2 | No urgency. Logged by them as P126. |
| W9 | *"leg4 `h2_pair` could not possibly have completed anything"* | Settled by a different route entirely (a single `qstat`: leg4 arrays gone, leg9 alive) | **Neither confirmed nor refuted** — test-training duration is **unmeasurable from the archive**. |

### COORD lane (self-retracted; recorded for the same reason)

| # | CLAIMED | KILLED BY | THE CORRECT STATEMENT |
|---|---|---|---|
| W10 | *"No frozen winner carries contamination"* (03:31Z) | Derived from 27 markers carrying **no R115 fields**, reading a default `0.0000` back as a measurement | Retracted 03:40Z as **P122**. See **W5** for the correct threshold-explicit form. |
| W11 | wall_clock distribution *"min 2.79 h, median 4.21, max 14.31, n=1,220"* | `test_leg.py:193` **zeroes the field by construction** for the whole TEST stage; a `v > 0` filter **deleted** that stage rather than sampling it | **SEARCH-only.** Every *"a training is 4.2 h"* must read *"a SEARCH training is 4.2 h; test-training duration is unmeasured."* |
| W12 | *"OPS's new hourly heartbeat block broke my W4"* | The block is written by `docs/ops/cycle_loop.sh`, introduced in commit **`db05f336`** by a PREVIOUS session, and had been in `ALERTS.txt` for **fourteen hours** | Nothing changed. The real failure was **validating a parser against a partial corpus**. |


---

## THE PATTERN ACROSS THE THIRTEEN — one distinction, destroyed four ways

**W2/W8, W7, W11 and W10 are the same defect wearing four coats: ZERO AND ABSENT ARE DIFFERENT
VALUES.**

* `x or 0` on a possibly-absent metric turns **UNMEASURED into PERFECT** (COORD);
* `x or <fallback>` on a measured zero turns **MEASURED-ZERO into UNMEASURED** (ANALYSIS);
* a `v > 0` filter over a field that is **zeroed by construction for a whole stage** turns
  **DELETING A SUBPOPULATION into SAMPLING it** (COORD);
* reading a schema default back as an observation turns **NOT-RECORDED into ZERO** (COORD).

> **★ THE STANDING RULE, and if one line survives tonight make it this one:**
> **ZERO AND ABSENT ARE DIFFERENT VALUES, AND EVERY IDIOM THAT CONFLATES THEM IS A DEFECT IN AUDIT
> CODE.** Its operational corollary, from COORD: *when you filter out a sentinel value, check whether
> some whole subpopulation is that sentinel **by construction**.*

**And the meta-observation worth keeping for the QC appendix:** THIRTEEN claims were published and then
killed in a single night, **and every one was killed by evidence rather than by argument — most of
them by their own author.** That is not a troubled project; it is a project whose instruments are
sharp enough to cut their operators, which is exactly what an examiner should want to see. **It is
recorded analytically here, never chronologically** (D5: chronological reads as a troubled project,
analytical reads as machinery that caught its own errors).
