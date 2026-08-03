# COORD LANE — SESSION HANDOVER, 2026-08-01 ~12:10 UTC

**Paste `docs/COORD_SESSION_PROMPT_2026-08-01.md` as the first message of the new session.**
Written by the outgoing coord session (`68e4aa59`), which ran 2026-08-01 01:20 → 12:10 UTC.

---

## 0. YOUR FIRST TWO ACTIONS, IN THIS ORDER

**① Join the bus** — from `llm-reward-portfolio/`:

```
.venv/Scripts/python.exe ../.claude/lanes/lanebus.py join coord
.venv/Scripts/python.exe ../.claude/lanes/lanebus.py inbox
```

**② ★★★ RE-ARM THE WATCH. IT DIED WHEN THE LAST SESSION ENDED.**

The watch is a `Monitor` task, which is **session-scoped**. When this session closed, the campaign
lost its only watchdog for the things `cycle.py` structurally cannot see. Re-arm with the **Monitor**
tool, `persistent: true`:

```
cd "c:/Users/User/Desktop/dissertation_papers/llm-reward-portfolio" && .venv/Scripts/python.exe -u ../.claude/lanes/watch.py 300
```

It prints **only on change**; silence means nothing changed. Checks:
`W1` cycle-stall (self-calibrating) · `W2` batch left the driven set · `W2b` driver down ·
`W3` ledger regression · `W4` alert-set change · `W5` lane silence · `W6` core seed-set/substrate
divergence · **`W7` the A16 pre-data window closing**.

> **Do not skip ②.** `W7` is the only thing watching for the moment the A16 decision becomes
> impossible (§4). Everything else has a second pair of eyes; that does not.

---

## 1. VERIFIED STATE AT HANDOVER (measured, not remembered)

| | |
|---|---|
| campaign | **2,358 records · $44.29 · drift 0 · sci=OK · arms_full 10/10 · 12/12 lines** |
| fence | **ARMED**, owner `ops`; `git status --porcelain -- src scripts config prompts` **EMPTY** |
| lanes on the bus | ops · writeup · analysis ×2 · coord (+ several unregistered) |
| withdrawn-claims register | **8 entries** (`lanebus.py board` surfaces them) |
| **PDF** | **BUILDS — `RC=0`, 230 pages, valid `%PDF-1.5`** (first success since 13 July) |
| citations | **clean across 18 chapters** under the widened recursive scan |
| reproducibility | **8 PASS / 0 WARN / 0 FAIL** — Priority 5 satisfied |
| word budget | **22,900 / 10,000 — FAIL, known and deliberate** (argument work before the deletion pass) |

---

## 2. WHAT THIS LANE IS

**Coordination + independent verification.** It exists because CLAUDE.md requires that the author not
grade their own work. **Standing commitments — keep them:**

1. **Never edit** `src/ scripts/ config/ prompts/ outputs/ docs/ops/`. Route to ops.
2. **Never** launch anything that spends money or touches Myriad. No ssh.
3. **Verify before relaying.** Every claim carried to another lane gets checked first-hand.
4. `paper/**` is the write-up lane's. **One crossing was made** (§6) and announced first.

---

## 3. THE MACHINERY THIS LANE OWNS (`.claude/lanes/`, outside the git repo by design)

| file | what it does |
|---|---|
| `lanebus.py` | the bus: append-only JSONL, `join · board · inbox · msg · alert · claim · ack/done · withdraw · next <series>` |
| `.claude/hooks/lane_guard.py` | `PreToolUse` heartbeat + guard; `SessionStart` board; `UserPromptSubmit` mail |
| `batch_progress.py` | stranded-batch detector (`--test-only`, `--rung`) |
| `watch.py` | the W1–W7 watch |

Both selftests must stay green: `lanebus.py selftest` · `lane_guard.py --selftest`.
Kill switch for the hook: `touch .claude/lanes/DISABLED`.

**`next P` is the P-series arbiter** — it has prevented three collisions. Always draw from it.
**`withdraw <id> <reason>`** attaches a retraction to the message it kills, because *retractions
travel slower than assertions* (measured: one claim survived its own withdrawal by 74 minutes).

---

## 4. ★★★ THE ONE DECISION WITH A DEADLINE — A16

**`config/preregistration.yaml` registers N2 as `test: h2_ra_iut_or_tost` with
`equivalence: tost_0.05_dsr`. `validity_tier.py` implements the superiority IUT only — `grep tost`
returns nothing. The paper's hypothesis table states the registered rule to the examiner.**

Run on the registered graph with synthetic p-values (effect-blind), initial weights are
`N1 0.5 · N2 0.5 · H3/H4/N5/H1 0.0`, so under the design's own **predicted** branch propagation halts
at step one and **H1/H3/H4/N5 are tested at local alpha exactly 0.0**.

**Three things established since, all of which the next session must carry:**

1. **The registration KNEW.** Its dated 2026-07-26 note says activation "rests entirely on N2
   rejecting via TOST … power-limited: n\* ~ 173 … the tier is **BORDERLINE to activate on the
   design's own prediction**." My earlier "this cannot have been the intent" is **withdrawn**.
2. **But the registration priced a POWER risk; the code delivers a STRUCTURAL IMPOSSIBILITY** — no
   TOST route exists at any n. That gap is disclosed nowhere.
3. **Precedent exists in the frozen text:** the `N6_h1` **endpoint** was corrected on 2026-07-26
   because under DSR "the IUT could essentially never reject" — a registered rule that structurally
   could not fire, corrected **pre-data**, disclosed as a dated correction, and it **also enabled
   rejection**.
4. **★★★ ADDED BY THE SUCCESSOR SESSION (M172/M174) — AND IT SUPERSEDES THE WHOLE "TWO ARTEFACTS
   DISAGREE" FRAME.** Every lane argued this over `PREREGISTRATION.md` **:108**, **:300** and
   **:43-46**, and ops declined M156 on the ground that the prose is *senior* and excludes the TOST
   route. **Nobody read the prose where it actually REGISTERS the tier.** `PREREGISTRATION.md:1051`,
   amendment row **R105** (ratified by **R108** at `:1053`), verbatim: *"**TOST is itself an IUT**
   (Berger-Hsu 1996), so our *predicted* CVaR-tail-win + Sharpe-**equivalence** legitimately activates
   the tier (**α flows on a TOST *rejection*** = 'equivalence proven')."* And **`:398`** calls *"the
   Sharpe-leg TOST … **decisive**"*. No later row (R106/R109/R111–R115) touches it. **⟹ the two frozen
   artefacts AGREE; there is no disagreement for a seniority rule to adjudicate; the code simply never
   implemented a ratified spec.** Independently, `freeze.py` states **no** precedence rule at all —
   `:5-10` requires the two to **AGREE**, the order quoted against this is `:30` and is explicitly the
   **byte-concatenation order of the canonical hash**, and the prose↔yaml gate at `:43-51` enumerates
   six checked fields that **do not include N2's `test`**. ⚠ **`docs/ops/WITHDRAWN_CLAIMS.md` W13
   therefore marks a TRUE claim as retracted** in the register the write-up lane greps before anything
   enters `paper/`. Ops' file; routed to them, not touched.

**The algebra, agreed independently by three lanes:** superiority `θ>0` ∪ equivalence `|θ|<δ` =
`θ > −δ`, so `iut_or_tost` is **one non-inferiority test at margin δ** — no `min()`, no alpha
inflation. **⚠ δ was argued over for hours and is now SETTLED: `δ = 0.0756` annualised Sharpe**
(`= 0.05 / k` at the **registered** `VALIDATION_TRACK_LENGTH = 694`, `k = 0.6616`), which reproduces
the hash-bound `sesoi_ann_sharpe_equiv` to four decimals. **`0.0502` came from substituting the TEST
track length 1571 into a conversion whose registered basis is the VALIDATION window — it is wrong.**
See the corrected block below and analysis M170.

### ⚡ A16 WAS DECIDED AT ~12:05Z — after most of the above was written. Carry the OUTCOME, not the debate.

The **analysis lane (session 4)** decided it on Tamer's explicit ratification (*"I won't send anything
to Okhrati, I give you full permissions, and ratify your actions"*), effect-blind, reversible on his
word. **Their re-framing supersedes mine:** the three artefacts do **not** disagree — `yaml:287`
registers the disjunction, `:293` says *"alpha recycled on ANY rejection (superiority OR
equivalence)"*, and `PREREGISTRATION.md:43-46` **defers the tier to the yaml**. **So it is a BUG (the
code never implemented the registered disjunction), not a design conflict** — nothing frozen changes,
no unfreeze, no relaunch.

**DECISION: N2 = per-leg NON-INFERIORITY IUT at the registered margin.** Blindness timestamped
**11:38:39Z**, 0 of 3 H2-RA legs computable. Routed to ops as **M156** with the patch and falsifying
tests. ⚠ **The margin figure originally written here was wrong — see the corrected block below.**

> ## ⚠⚠ THE RETRACTION THAT STOOD HERE IS ITSELF RETRACTED (successor coord session, M174).
>
> **This block previously said: "I was wrong about the margin — δ = 0.05, because the executed
> `test_returns` length is 1571 where `sharpe_mde_to_dsr(1.0, 1571) = 0.9958."** That retraction was
> the error. **The ORIGINAL F-14 position — the registered margin is `0.0756` — is correct.** It is
> left visible above rather than deleted, because a retraction that vanishes is indistinguishable
> from one never made.
>
> **Why, measured rather than argued.** The SESOI is registered in **validation**-DSR units
> (`PREREGISTRATION.md` R12; `freeze.py`'s prose↔yaml gate checks `inference.sesoi` against the prose
> string *"SESOI = 0.05 validation-DSR units"*), and node N2 names `equivalence: tost_0.05_dsr`,
> i.e. the function `h2_tost_dsr`. That function
> (`scripts/analyze_campaign.py:2582-2592`) takes its track length from
> `power_analysis.VALIDATION_TRACK_LENGTH`, **which is 694** — *"the executed Split-C validation
> window [3081,3775)"*. **1571 is the TEST window and is not the registered basis.**
>
> | route | `k = sharpe_mde_to_dsr(1.0, T)` | margin `0.05/k` (ann. Sharpe) |
> |---|---|---|
> | **T = 694 — the REGISTERED validation track** | **0.661571** | **0.075578** |
> | T = 1571 — the test track (NOT registered) | 0.995771 | 0.050212 |
>
> `0.075578` reproduces the **hash-bound** `inference.sesoi_derivation.sesoi_ann_sharpe_equiv = 0.0756`
> to four decimals, and `0.661571` reproduces `dsr_per_ann_sharpe = 0.6616`. `k` was **cross-checked by
> hand** against `φ(0)·√(T−1)/√252` — exact agreement, `|diff| = 0.0e+00`, at T = 694, 756 and 1571.
> **The analysis lane reached the same number independently and by a stronger route (M170): every
> `metrics['val_returns']` is `list[694]` on 1,373/1,373 search records — config, code and data agree.**
>
> **It is outcome-relevant, not academic.** Three synthetic legs at true effects (−0.055, −0.062,
> −0.048), n = 30, n_boot = 2000, the real `paired_seed_difference_test`, IUT p = max over legs, N2's
> local alpha = 0.025: **δ = 0.0756 → p(N2) = 0.0065 (REJECTS)** versus **δ = 0.0502 → p = 0.5445 (does
> not)**.
>
> **⚠ AND M156's PATCH LINE CARRIES A UNIT ERROR — true under EITHER A16 outcome, so it must not die
> with the disagreement.** `ni = paired_seed_difference_test(a + delta, b, …)` with
> `delta = _frozen_equiv_margin()` adds **0.05 in validation-DSR units** (that function's own docstring
> at `analyze_campaign.py:207` names the units) to **per-seed annualised Sharpe** data (`a`, `b` at
> `:1513` are `_sharpe_seed`). **Requested guard, whatever is decided about N2:** a test asserting the
> executed margin equals `sesoi_derivation.sesoi_ann_sharpe_equiv` to 4 dp. It fails against the patch
> line as written, and fires loudly if anyone ever "corrects" the track length to 1571 — the failure
> mode F-14 predicted verbatim. This matters even if N2 is never touched: `h2_tost`/`h2_tost_dsr` are
> report-only but they **ship**, and the bankable-null statement rests on them.
>
> **State the direction plainly in the amendment, because it cuts against us:** `0.0756` is the
> **wider** margin, and a wider non-inferiority margin is **easier** to reject. We adopt it because it
> is the value the frozen config **records and prices** — R104 hash-binds the band
> `0.0055 < 0.0756 < 0.10` with verdict `sesoi_inside_band`, **in annualised Sharpe**. A margin chosen
> for its conservatism rather than its registration is a researcher degree of freedom in the other
> direction. Name both numbers, say which is registered, say which is conservative, say they differ by
> 50 %, and pre-specify the T = 1571 re-derivation as a reported sensitivity while still blind.
>
> **Open question, taken by the analysis lane (M170):** whether `n* ≈ 173` (the N2 note's power
> figure) was itself derived at T = 694. If so it is internally consistent with the 0.0756 margin; if
> not, the note's own power claim needs restating.

**THE DEADLINE STILL BINDS:** the decision is legitimate **only while no H2 outcome exists**. Core
`test/` currently holds only baselines + `random_search`. **`W7` fires on the first core H2 record.**
After that, only disclosure remains — so **confirm ops has landed M156 before the core C4 ladder
starts.**

---

## 5. OPEN ITEMS BY OWNER

**WRITEUP** — ① **73 characters silently missing from the PDF** (literal α/σ/χ in *prose*; math-mode
renders fine — fix is `$\alpha$` etc.). Includes the VaR/CVaR glossary definitions, the whole A16
passage, `σ_seed = 0.244`, and **"7.8 × 10␣␣"** (a lost exponent). ② the hypothesis-table promise
(§4). ③ the word budget, 22,900 → target.
**OPS** — ① move `CH5_prototype.md` from `ASSEMBLY` to `APPENDICES` (one tuple move; fixes the
missing Chapter 5, the mid-body appendix, and the lettering). ② `analyze_campaign.py:3165` docstring
still says *"H1 — descriptive panel (no inferential p)"* although the code beneath it now reads the
IUT p-value. ③ leg4 `h2_pair` re-submission.
**ANY LANE** — put a **full PDF build** in the gate, not `--md-only`; fail on any control byte in
`paper/**` and any `U+FFFF` in the built PDF text.

---

## 6. THE ONE BOUNDARY CROSSING — declare it if asked

Four bytes in `paper/**`, announced on the bus before the edit, to fix a **fatal** build error:
`NOMENCLATURE.md:16`, `CH6_results.md:162`, `APPENDIX_B_limitations.md:394` (BEL → `\a`) and
`CH6_results.md:212` (`$B^\*$` → `$B^{*}$`). **Uncommitted, mixed with the write-up lane's own
uncommitted work.** Nothing else in `paper/` was touched.

---

## 7. ERRORS THIS LANE MADE — do not repeat them

Logged P111, P112, P117, P118, P120, P122, P129 and in `docs/COORD_LANE_FINDINGS_2026-08-01.md`.
**The five that generalise:**

1. **`x or 0` on a possibly-absent metric turns UNMEASURED into PERFECT.** I read R115 fields off 27
   frozen markers that carry none and reported 27 fabricated `0.0000`s as evidence of cleanliness.
2. **When you filter out a sentinel, check whether a whole subpopulation IS that sentinel by
   construction.** My `wall_clock > 0` filter deleted the entire test stage (`test_leg.py:193`
   hardcodes `0.0`) and I used the result to correct another lane.
3. **Enumerate the record types before you parse.** My W4 was validated against a corpus missing a
   block type that had been in the file for 14 hours.
4. **A documented safety property no test exercises against live state is a claim, not a guarantee.**
   My "unregistered sessions are never blocked" was false for claims the moment a real lane took a
   real hold — the selftest passed all night, then failed the instant the world changed.
5. **Heredocs eat backslashes.** Three times tonight, including in the *tool written to repair it*.
   Use Write/Edit for anything containing `\`.

**And the tell that caught most of them:** *a detector that fires on nearly everything — or on
nothing — is making a claim about its own specification first.*

---

## 8. READ ORDER

`docs/COORD_LANE_FINDINGS_2026-08-01.md` (F-1…F-15, this lane's record) →
`docs/LANE_PROTOCOL.md` (§4d ask-before-analysing, §4e enumerate-record-types) →
`memory/session-current-focus.md` → `CHANGELOG.md [2026-08-01e]` →
`docs/ops/WITHDRAWN_CLAIMS.md` **before any claim from lane traffic enters `paper/`.**
