# ANALYSIS LANE — successor handoff (written 2026-08-01 ~14:00Z by session 4, `e210234f`)

> **How to use:** paste everything between the `===` markers into a new Claude Code session as its
> first message. It is written to be self-sufficient. It assumes nothing, and — unlike the handoff
> *this* session received — it tells you which of its own inherited claims turned out to be **wrong**,
> because that is what actually saves you time.

===============================================================================================

You are taking over the **ANALYSIS lane** of a four-lane parallel Claude Code operation on the
`llm-reward-portfolio` MSc dissertation campaign. **Do not restart cold.** Run §1, say
`Resuming from: … — next: …`, and continue mid-stream.

## 0. THE ONE THING THAT DEFINES THIS LANE

Tamer's standing instruction: *"extremely deeply and constantly analyse and monitor the campaign's
**results** and the **output** … make sure absolutely everything is strictly flawless, logical,
meaningful, correct, and there are no issues with science."*

Session 3 was told it had been monitoring **process health** rather than **results**. Session 4 (me)
ran the results cycle *and* went after the science. **Your job is both: the standing cycle in §5, and
the deep analysis that only happens if you go looking.** Health monitoring is covered by ops and
coord — do not rebuild it.

> **★ AND THE RULE THAT MATTERS MORE THAN ANY FINDING, learned four times over today by four
> different lanes: THE COUNTERMEASURE THAT WORKS IS NOT MORE CARE BY THE AUTHOR. IT IS ANOTHER LANE
> CHECKING.** Every serious error today — mine, ops', coord's, writeup's — was caught by a *different*
> lane. Read other lanes' claims adversarially and verify before re-transmitting. They will do the
> same to you, and that is the machinery working, not friction.

## 1. RESUME SEQUENCE — run these before anything else

```bash
cd /c/Users/User/Desktop/dissertation_papers
"llm-reward-portfolio/.venv/Scripts/python.exe" .claude/lanes/lanebus.py --as analysis join analysis
"llm-reward-portfolio/.venv/Scripts/python.exe" .claude/lanes/lanebus.py --as analysis board
"llm-reward-portfolio/.venv/Scripts/python.exe" .claude/lanes/lanebus.py --as analysis inbox
```

⚠ **Post to the bus by writing the message to a FILE and passing it via a Python `subprocess` argv
list — never through a bash `-c` string.** Backticks and `$` are eaten by the shell as command
substitution, the identifier you were writing *about* is silently deleted, **and the send still
reports success.** Three lanes hit this today (ops M177, writeup M184, me).

## 2. ★ THE READING PLAN — this is the "zero gaps" instruction, made concrete

**Tier 0 — before you touch anything (≈45 min).**
| doc | why |
|---|---|
| `docs/analysis/ANALYSIS_LANE_SESSION4_2026-08-01.md` | **my owner doc, A34–A48.** Read the A-headings, then **A42/A42-bis, A45, A47, A48** in full |
| `docs/ANALYSIS_LANE_2026-08-01.md` | session 3's doc, **A1–A33**. Headings, then A16, A24, A30, A31, A32 |
| `CHANGELOG.md` blocks `[2026-08-01i]` (mine), `[2026-08-01l]`/`[2026-08-01m]` (ops/writeup) | the narrative record |
| `memory/session-current-focus.md` | the cursor — all four lanes' ▶ NOW entries |
| `llm-reward-portfolio/CLAUDE.md` | **the contract.** PRIORITIES · the four authorities · Okhrati's six duties + the SCOPE clause · the verify-your-own-work rule |
| `docs/LANE_PROTOCOL.md` | coord owns it; it is the law for inter-lane conduct |

**Tier 1 — the frozen design (you cannot audit what you have not read).**
`PREREGISTRATION.md` (235 KB — **§1 hypotheses, §10 analysis plan, and the ENTIRE amendment table
from D2 to R115**) · `config/preregistration.yaml` (97 KB — **the `inference.validity_tier` block,
`sesoi_derivation`, `search_adequacy`, `model_suite`**) · `DECISIONS.md` · `DEVIATIONS.md`.

> **★ THE SINGLE MOST EXPENSIVE LESSON OF TODAY: ARGUE FROM THE AMENDMENT ROW, NOT FROM THE
> PARAGRAPHS THAT MENTION THE TOPIC.** Four lanes spent six hours on A16 quoting `PREREGISTRATION.md`
> :43-46, :108 and :300 — and **not one of us read `:1051`, the amendment row (R105) that *creates*
> the validity tier**, which settles it in one sentence. When a dispute is about object X, go read
> where X was registered.

**Tier 2 — the machinery you will audit.** `scripts/analyze_campaign.py` (the 32 `out[…]`
assignments + 7 dict-literal keys) · `src/inference/validity_tier.py` · `src/inference/headroom.py` ·
`src/sandbox/executor.py` (`safe_call`) · `src/env/portfolio_env.py` (the reward call site) ·
`scripts/freeze.py` · `scripts/power_analysis.py`.

**Tier 3 — the operational record, read ANALYTICALLY not chronologically.**
`docs/CAMPAIGN_EXECUTION_RECORD.md` is **941 KB** — do not read it linearly. Grep it for the section
you need (`§100.*` is today). Same for `docs/HANDOFF.md` §1–§3 (§3 is the **authority map** — one
owner per truth) and `docs/COORD_LANE_FINDINGS_2026-08-01.md`.

**Tier 4 — as needed.** `docs/EVIDENCE_AND_FRAGILITY_LEDGER.md` · `docs/GRADE_95_MASTER_PLAN.md` ·
`docs/DEEP_H2.md` / `DEEP_H3.md` · `docs/V2_WRITE_TIME_REGISTRY.md` · `01_literature/` (196 PDFs;
read with PyMuPDF — `pdftoppm` is absent).

## 3. ★★★ INHERITED CLAIMS THAT WERE WRONG — verify before you act

**This section exists because my own handoff contained three of these and each cost me time.**

| claim I inherited or was told | what was actually true |
|---|---|
| *"A16: three artefacts disagree, one must change"* | **They agree.** The hash-bound prose registers the TOST route at `:1051`. It was a code gap, not a design conflict. |
| *"`test_components` is populated on only 22–24 of 992 records"* | It is non-empty on **992/992**. The names are author-chosen per program; the right denominator is the **unit**, not the tier. |
| *"the results-cycle tool is verified against the live archive"* | **Four of its panels were dead**, including the entire determinism envelope (§A39, §A46). |
| coord's *"δ = 0.0502 at T=1571"* | **Wrong** — 694 is the *validation* track length, which is what the SESOI is defined on. δ = **0.075578**. Coord withdrew it. |
| ops' *"the prose is senior, so the code is right"* | The seniority claim is **true** but the **antecedent is false** — there is no disagreement to adjudicate. |
| my own *"D16 has started landing"* (P140) | I counted **directories**, and the 27th was `_env`, the launcher sidecar. |

**⇒ Treat every number in every handoff — including this one — as a claim to re-derive, not a fact.**

## 4. CAMPAIGN STATE AT HANDOVER (2026-08-01 ~13:47Z)

- **RUN 4**, confirmatory, frozen (`3ca6f01ab772…`, nine bound files). **2,455 records · $44.9675 ·
  12/12 lines · ~992 cores on UCL Myriad · drift 0 · sci=OK · arms_full 10/10 · 0 timeouts.**
- **Exogenous stop: 2026-08-27, a calendar date.** Not data-dependent.
- **The critical path is LLM AUTHORING, not seeds.** Core line: **3 of 5 LLM arms frozen**
  (`distributional`, `scalar`, `placebo`); `scalar_cvar5` and `placebo_shuffled` still searching.
- **Common rung = 0.** Twelve units are parked at rung 30, **eight are at zero** (the 5 H2 arms +
  `bayes_opt`/`cma_es`/`tpe`), and **one — `test_h3_singleshot` — ran ahead to 560** against a partner
  at 0. H3 pairs over **shared** seeds, so its excess is currently unusable.
- ⏳ **THE A16 BLIND WINDOW IS STILL OPEN BUT CLOSING.** `test/placebo` is **launched-but-empty**
  (unit dir + `_env` only, created 11:24:48Z); the other four H2 arms have no dir. **0 of 3 H2-RA
  legs computable.** Coord's W7 watch is armed on the correct predicate and has not fired.

## 5. ★★★ YOUR STANDING CYCLE — run it, and interrogate what it tells you

```bash
cd /c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio
.venv/Scripts/python.exe docs/analysis/results_cycle.py --selftest   # 16 falsifying cases; run after ANY edit
.venv/Scripts/python.exe docs/analysis/results_cycle.py --full       # first pass
.venv/Scripts/python.exe docs/analysis/results_cycle.py              # every ~30 min: deltas + anything wrong
.venv/Scripts/python.exe docs/analysis/search_adequacy.py --selftest # 25 falsifying cases
.venv/Scripts/python.exe docs/analysis/search_adequacy.py --line core
```

**`results_cycle.py` now has six panels** (counts · safe-default by arm with Wilson intervals ·
constant/null sweep · determinism envelope · the D17 periodic census on **both** sides of the R115
floor · substitution inside the TEST trainings). **I repaired four dead panels in it — see §A39/§A46.**

**The BLINDING RULE.** The stop is a calendar date and the analysis plan is frozen and mechanical, so
*observing* interim numbers cannot bias the stop. **But no decision may be taken from an interim look,
and the H1/H2/H3/H4 verdicts are NOT your monitoring target.** In scope: record completeness · schema
integrity · provenance and determinism · per-record sanity · execution quantities · report-only
mechanism instruments · spend · anything constant or null across every record. **If you compute a
confirmatory quantity incidentally, LOG THAT YOU LOOKED and draw nothing from it.**

**Each pass, compute:** counts reconciled three ways (recursive walk vs the cycle's depth-4 authority
vs frozen markers + nested duplicates) · per-arm rates **with intervals** · the constant/null sweep ·
the determinism envelope (**one `env_fingerprint.label` and one CPU model per comparison unit**) ·
whether any §6 item has become answerable.

## 6. OPEN ITEMS, BY OWNER

**Ops:**
1. **`campaign_summary.json` does not exist for RUN 4** ⇒ `benchmark_floor` (the DeMiguel table
   **already wired into the PDF**), `attribution`, `h2_rf_robustness`, `regime_stratified` are
   **silently absent** from the final analysis. **Pre-emptable now, unrecoverable after teardown.**
   Ops confirmed the mechanism (the tiered path writes it only when `run_campaign_tiered` RETURNS,
   and returns 3 at a gate stop without writing one) and is building a recovery path. **Chase it.**
   ⚠ It must be produced **by the campaign machinery** — it carries `test_window`, and a wrong window
   silently scores the floor on the wrong slice.
2. **Wire the registered-key completeness GATE** — the analysis currently exits 0 with keys missing.
3. **Wire A47's three search-adequacy instruments** into `analyze_campaign`'s `out[…]` set.
4. **Per-arm PopArt (σ_max)** — A30: the claim reaches the paper and is computed by NO instrument.

**Writeup:** A47/A48 (the K=5 defence, now measured) · A38's precision correction (*"zero R115
breaches on the confirmatory line"* is true; *"no confirmatory training used SAFE_DEFAULT"* is
**false**) · A34/A44's three-mechanism inert-term taxonomy · A36's threshold-on-an-atom disclosure ·
A42-bis's N2 wording (**non-inferiority**, never "superior or equivalent").

**Open questions nobody has answered:**
- **Is the core-line search core-bound or authoring-bound?** One measurement. It decides whether
  `h3_singleshot`'s ~1,900 unusable core-hours were a real cost. **Raised three times, never answered.**
- Was `n* ≈ 173` in the N2 note derived at T=694 or another basis? (coord's M164(3) loose end, mine).

## 7. ★★★ THE ERROR TAXONOMY — eight of mine, and they are all one shape

**P136–P141, P151, P152.** None reached a conclusion anyone acted on. The transferable rules:

1. **Reading a value whose MEANING is not what its NAME implies.** The single most repeated error in
   this codebase, across all four lanes. `val_returns` at the wrong nesting level (P141) · the whole
   `env_fingerprint` instead of `.label` (P137) · a launcher sidecar counted as a record (ops) · a
   flag read as a scale (P109).
2. **A result that is uniform across every arm is a claim about your instrument** (P151: `b > 1`
   everywhere). **A perfect 0 % or 100 % is the same tell.**
3. **Never default a missing field** — it turns *not measured* into *measured clean* (P121).
4. **Slice a prefix only after testing for it** (P136 — `search_h3_singleshot` → "ingleshot").
5. **A replay must reproduce the artefact before any counterfactual is read off it** (P138).
6. **An alarm that compares point estimates is the defect it exists to catch** (P139).
7. **A test built from the constant it tests cannot detect a wrong constant** — my `--selftest`
   passed against the pre-fix code until I rebuilt its fixture from the real schema.
8. **A specification whose prose and code disagree is a defect even when the prose is right**, because
   the implementer types the code (my M156 unit error).
9. **A green check on a PROXY is not a green check.** The PDF had not built since 13 July and every
   lane reported it green, because everyone ran `--md-only`. **Verify the artefact, never its stand-in.**
10. **When a check already exists in the watch, CALL it — do not re-derive it ad hoc**, because the
    ad-hoc version has not been positive-controlled (coord's P142).

## 8. LANE MAP — the boundary you must not cross

| lane | owns |
|---|---|
| **analysis (you)** | `docs/analysis/**` (claimed) and `docs/ANALYSIS_LANE_*.md` — **read-only everywhere else** |
| ops | `src/**`, `scripts/**`, `config/**`, `prompts/**`, `docs/ops/**`, `outputs/**`, `docs/DEFERRED_FIXES_RUN4.md`, `docs/CAMPAIGN_EXECUTION_RECORD.md` |
| coord | `docs/LANE_PROTOCOL.md`, `.claude/lanes/**` |
| writeup | `paper/**`, `docs/GRADE_95_MASTER_PLAN.md`, `docs/V2_WRITE_TIME_REGISTRY.md`, `docs/CITATION_WORK_MAP.md` |

**A finding that implies a code change is a MESSAGE to the owner, never an edit.** This is not
deference — a second writer inside a live campaign is how you split a run into two arithmetic regimes.
**Never lower a Myriad job's priority. Never run `git clean -x`. Never touch a running job.**

## 9. WHAT I WOULD DO FIRST

1. Join the bus, read the board and inbox, run **both selftests**, then `results_cycle.py --full`.
2. **Re-derive the campaign state yourself** — counts three ways, determinism envelope, D16 (should
   read 30/30 on one CPU model).
3. **Check whether the A16 window has closed** (`test/distributional` etc. holding a `-s<N>/record.json`).
   If it has, nothing further may be decided about the confirmatory rule — only disclosed.
4. **Chase `campaign_summary.json` with ops.** It is the highest-value unrecoverable item open.
5. Then go looking. The findings that mattered today came from asking *"what does no instrument
   watch?"* — not from the cycle log.

**Everything in `CLAUDE.md` binds, including: every message to Tamer begins with "Tamer"; ultrathink
by default; verify by RUNNING, never by assertion; document continuously in `CHANGELOG.md` +
`docs/HANDOFF.md` §1 + the cursor. Overstating a risk is as inaccurate as understating one — verify
in both directions before writing it down.**

===============================================================================================
