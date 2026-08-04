# FLAWLESS LEDGER — the standing open-items register for the 30-minute deep check

**Tamer, 2026-08-04:** *"make sure the checks that are every 30 minutes do not stop until they ensure
absolutely everything is 10000% absolutely strictly flawless. I give them full permissions, do
whatever it takes to ensure absolute flawlessness."*

---

## THE CONTRACT — READ THIS BEFORE TOUCHING A ROW

**No finding may be left in an unresolved state.** Every row reaches exactly ONE of three terminal
states, and there is no fourth. "I looked at it and it seemed fine" is not a state.

| state | what it requires |
|---|---|
| **FIXED** | the defect is gone AND the fix was FALSIFIED — the new assertion must fail against the pre-fix behaviour. A passing test proves nothing on its own (RUN 18 reported a file "verified byte-identical" that had never been modified). |
| **PROVEN-BENIGN** | a MEASUREMENT is recorded here showing the condition cannot harm the campaign. Not an argument, not a docstring, a measurement with its command and output. |
| **ESCALATED** | named precisely, with the reason it cannot be actioned from this session, and surfaced to Tamer. Fair-share, frozen thresholds and UCL policy live here. |

### ⛔ THE ONE RULE THAT OUTRANKS "MAKE IT GREEN"

**NEVER make a check pass by weakening the check.** No raised threshold, no widened tolerance, no
skipped assertion, no suppressed alarm, no `continue` past an error, no frozen value edited. On this
campaign the fastest route to a green board is to break the instrument, and that is the one outcome
worse than a red board. If a check is genuinely wrong, fix the CHECK and prove the fix falsifies —
then say so in the row. Fix causes, never symptoms.

### WHAT IS NOT A DEFECT, AND MUST NOT BE "FIXED"

A check that never stops needs to know where the floor is, or it will chase honest states forever.

* **The common rung being 0.** That is the campaign's true current state under R101, not a fault.
* **Holes below an arm's frontier while jobs are running or queued.** Normal during pipelined C4.
  Actionable ONLY on hole + ZERO running AND ZERO queued.
* **`RED` on the cycle line, `guards=2`, `seed_alignment:CRITICAL`, `silent_hang:UNKNOWN`, the
  truncation and transport entries.** Acknowledged in `docs/ops/acknowledged_alarms.txt`; each
  carries its own re-triage trigger. Re-read the trigger, do not re-litigate the alarm.
* **`M2_r115_threshold` exiting 1.** By design. The registered insensitivity claim IS falsified and
  that is the disclosed state; it cannot return to 0 without editing a frozen value, which is
  forbidden.
* **`M3_seed_completeness` exiting 1** while lines are climbing. Same reason.
* **Core count / fair share.** Closed by fourteen independent measurements. The only remaining lever
  is a human request to UCL RC, which is Tamer's decision. Do not re-open it.
* **Lines idle on the test tier with work queued.** Fair-share, not a fault. `line_balance` is the
  arbiter.
* **The 2026-08-12 Myriad maintenance.** A planned at-risk day with a playbook.

---

## THE HARD PROHIBITIONS (a check with full permissions still may not do these)

* **NEVER read a treatment arm's SEALED-TEST outcome.** Single confirmatory look; reading it is a
  forking path on a frozen pre-registration.
* **NEVER edit `src/`, `scripts/`, `config/`, `prompts/` while the campaign is live** — drift-fenced,
  `drift` must stay 0. `docs/**` is safe. `paper/**` belongs to the write-up session.
* **NEVER change a frozen threshold or `PREREGISTRATION.md`.**
* **NEVER lower SGE priority** (prohibited, one-way); never `qdel -u`; explicit job ids only.
* **NEVER junction the archive** (`poll.py:305` renames; cross-volume it rmtrees the record).
* **NEVER `git clean -x`, `git add -A`/`-u`, or `git stash`.** Stage BY NAME.
* **NEVER put backticks, `$(...)` or heredocs in a `bash -c` string or a `-m` commit message.**
  Write to a FILE and use `-F`. Broken seven times; it is the single most repeated error here.
* **Printed output is ASCII-ONLY** (the console is cp1251 and the status page publisher REFUSES
  non-ASCII, so one bad character silently freezes Tamer's page).
* **NEVER add Claude/Anthropic attribution anywhere.** Tamer is sole author.
* **Editing a running loop is INERT** — `cycle_loop.sh` / `publish_loop.sh` need a RESTART;
  `cycle.py` / `publish_status.sh` are re-invoked each iteration and do not.

---

## OPEN — every row must move to a terminal state

Rows carry: `id · found · what · evidence needed · owner-action`. Work the **BLOCKING** rows first;
they are the ones that can cost the campaign or the grade. Add every new finding here the moment it
is found, including findings about this ledger.

### BLOCKING — can cost records, the result, or the grade

*(none open as of 2026-08-04 00:20 UTC — the two P244/P245 defects were FIXED and falsified this
session; see CHANGELOG `[2026-08-04b]` and execution record §132)*

### MAJOR — an instrument can mislead a future session

| id | found | what | to resolve |
|---|---|---|---|
| F1 | 08-04 RUN19 audit | `stage_eta` monotonicity assertions filter `GATED` rows out before comparing (`if e not in ("REACHED","GATED")`), so the check is blind BY CONSTRUCTION to a table that gates a low rung while dating a higher one — a logical contradiction. **Not live today** (every row is dated, verified). | make GATED absorbing upward and assert it; the existing `tmp2` fixture already produces the violating shape |
| F2 | 08-04 RUN19 audit | `stage_eta` go-forward exclusion `(568 - len(mts)) > PACK` is untested, and worse than disclosed: **INVERTING it to `<= PACK` still scores 42/42** (every `latest` cell reads GATED, so J2 passes vacuously). | two-cell fixture (one at 560, one at 300) asserting `fleet_rate > goforward_rate` and `latest > earliest` |
| F3 | 08-04 RUN19 audit | `stage_eta`: the `-1h` VALUE is untested (both fixtures have an empty 1 h window by construction, so `d1` is identically 0 in every assertion). Deleting the COLUMN *is* caught. | fixture with records inside `lo1` and a cell CROSSING the rung, asserting the exact decrement |
| F4 | 08-04 RUN19 audit | `stage_eta`: `concentration()`, `_parse_cores()`, the `yes`/`risk` verdicts, `REACHED` and the GATED branch are all unasserted. `_parse_cores` carries the production `?`/`0` contract from `publish_status.sh:231`. | direct unit assertions for each |
| F5 | 08-04 RUN19 audit | `stage_eta`: `568` is a magic literal repeated 6-7 times (`:224 :264 :337 :413 :425 :427-428`) with `RUNGS[-1]` unlinked. A ladder change desynchronises them silently and no test would notice. | `CEILING = RUNGS[-1]` |
| F6 | 08-04 RUN19 audit | `stage_eta`: `rem` includes `missing * rung`, but missing units are not in `cells` and can therefore NEVER contribute to `owing_rate`. A rung can be dated off one producing cell while most of its priced backlog belongs to units that have produced nothing by definition. Partially disclosed at `:429-433`, not reflected in the gate. | reflect it in the gate, or state the bound honestly |

### MINOR — correctness or hygiene, no campaign exposure

| id | found | what | to resolve |
|---|---|---|---|
| F7 | 08-04 RUN19 audit | `stage_eta` selftest E1 is host-dependent: on a host whose local time IS UTC, `skew == 0.0` and E1 FAILS — the suite reports a defect exactly where the defect is impossible. | make E1 conditional/informational; E2-E5 are the portable control |
| F8 | 08-04 RUN19 audit | `stage_eta`: `concentration(cells, now_epoch, 12)` hardcodes 12 h while the ETA window `eh2` may be 24 h, so the composition warning is silently ABSENT in the one state where it matters most. | use `eh2` |
| F9 | 08-04 RUN19 audit | `stage_eta`: `now_epoch` is sampled BEFORE the archive walk, so records landing during the walk are excluded from every window but still counted in `len(mts)`. | sample after the walk |
| F10 | 08-04 RUN19 audit | `stage_eta`: selftest section J has a `try:` with only a `finally:`, so an exception there aborts the run before the pass/fail summary prints. | wrap like F/G/H |
| F11 | 08-04 RUN19 audit | `stage_eta`: any stray subdirectory under a `test*` root is silently promoted to a registered unit. Not live (all 62 pairs verified genuine, reconciling to 71 with 9 missing). | allowlist the arm names |
| F12 | 08-04 RUN19 | `session_preflight --full` docstring advertises "~60 s"; measured ~200 s. | correct the docstring |
| F13 | 08-04 RUN19 | `run_record_layers.sh` header says "ALL SEVEN RECORD LAYERS" while an internal comment says "these EIGHT layers"; it runs 7 gated layers + 3 ungated measurements. | reconcile the wording |
| F14 | inherited RUN18 | 18 style-only lint items (E702 x14, E741 x4), 12 in `record_validator.py`. Deliberately left: renaming variables inside live instruments is risk for no gain. | confirm still deliberate, or clear post-campaign |

### DISCLOSURES — true, permanent, and must reach the write-up rather than be "fixed"

| id | what |
|---|---|
| D-a | `metrics.train_curve.return` is 100% NaN on every test record (SB3 logs `ep_rew_mean`; no episode closes in the logging window). A disclosure, NEVER an exhibit. |
| D-b | A62: `per_period_pnl` is byte-identical to `test_returns` on 9,065/9,065 records. No consumer reads it; no result affected. |
| D-c | **S4 determinism is VACUOUS in this archive** — 0 replicate `(arm, seed, reward_hash)` keys exist, so "0 disagree" tests NOTHING. Determinism must be evidenced from the 30/30 bit-identical farm, never from here. |
| D-d | S5: the sealed test's worst safe-default fallback is 9.0847%, INSIDE the registered R115 10% floor with 0.9153% margin. The phenomenon the campaign measures, not a defect. |
| D-e | **R115 is a stated Limitation, threshold UNCHANGED, and is PROVISIONAL for 3 of 10 core groups — RE-RUN BEFORE SUBMISSION.** |
| D-f | D34: the authoring-reliability marker set structurally cannot hold an author-side reject. D35: `n_attempted` publishes `placebo = 33` against a registered budget of 30. |
| D-g | `campaign_summary.json` at teardown remains the only UNRECOVERABLE item. |

### WATCH — not yet a finding, but trending

| id | what | trigger |
|---|---|---|
| W1 | `gate_failure_drift` CUSUM rising (0.99 → 2.56) | investigate to a cause if it keeps climbing |
| W2 | anthropic spend 31% over the credit ESTIMATE, but `still to author $0.0000` | cannot halt anything; note only |
| W3 | disk forecast to the 20 GB floor | preflight `disk` row; full ladder fits with ~6 GB |
| W4 | repair jobs 83464 / 85065, ranked 309/314 and 314/314 of 314 pending | measured drain 9-18 h; escalate only if still queued after ~24 h |
| W5 | core line C1 chain: `tpe` owes 5 of 30, `bayes_opt` 4 of 30 | this gates the common rung leaving 0 |

---

## RESOLVED — append-only, never deleted

| id | resolved | state | evidence |
|---|---|---|---|
| P244 | 2026-08-04 RUN19 | **FIXED** | S15 took each line's rung as a minimum over STARTED arms, so core/glm/kimi/nemotron printed 30 while banking 0. New check C6 reads the roster from `frozen*/`. Selftest 9→16; the four new cases were run against a verbatim reconstruction of the pre-fix `scan()` and each reads TRUE after / **FALSE before**. Case M is a regression guard reading 30 on both sides. |
| P245 | 2026-08-04 RUN19 | **FIXED** | `stage_eta` priced the serial chain as elapsed wall-clock and printed "0.00 d still to run" while `bayes_opt` held 26/30 and `tpe` 25/30. Now measured from candidate RECORDS against `lanes.SERIAL_CHAIN_BUDGET`; unreadable tree returns UNKNOWN, never 0. Selftest 38→42, ruff clean, page rc=0 with 0 non-ASCII, live on the page. |
| A-1 | 2026-08-04 RUN19 | **PROVEN-BENIGN** | Apparent duplicate monitor/driver processes. Resolved by ANCESTRY: each `.venv` launcher is the PARENT of its base-interpreter child (`ParentProcessId` chains verified). A pattern census counts CHAINS, not instances. |
| A-2 | 2026-08-04 RUN19 | **PROVEN-BENIGN** | Repair jobs 83464/85065 feared stuck. `qalter -w p` → *"found possible assignment with 8 slots"*; real PE `smp-[D]*`, `reserve: y`. Ranked last because SGE priority is monotone in submit time (verified across the whole pending set). Measured drain 9-18 h. |
| A-3 | 2026-08-04 RUN19 | **PROVEN-BENIGN** | RUN 18 §10 alleged the `-1h` predicate `max(0, min(k, rung-(len-k)))` was untested and possibly wrong. It is CORRECT in all three regimes (`L<=R`, crossing, `L-k>=R`), and deleting the column IS caught by the J3 parser. A disclosed defect that was not one. |
| A-4 | 2026-08-04 RUN19 | **PROVEN-BENIGN** | Auditor reported as MAJOR that the ETA table is printing GATED for low rungs while dating higher ones. Refuted by running it: every row is dated, none GATED. The structural half survives as F1. |
| P246 | 2026-08-04 RUN19 | **FIXED** | Mine: a heredoc inside a `bash -c` string, seventh occurrence. Blast radius NIL. Both documents were then written with the Write tool and appended by a script doing no shell quoting. |
