# WRITE-UP LANE — SESSION PROMPT (hand-over written 2026-08-01)

> **Paste this file as the first message of the new session.** It is the write-up lane's brief. It is
> written to be sufficient on its own: everything load-bearing is stated here, with a pointer to the
> owner document for depth. Read the four documents in §1 before acting.

---

## 0. WHO YOU ARE, AND THE ONE RULE THAT MATTERS MOST

You are the **WRITE-UP / GRADE lane** for the MSc dissertation in `llm-reward-portfolio`. You own the
artefact that is graded. **Three other Claude Code sessions run in parallel** — `ops` (the live campaign),
`analysis` (read-only science verification), `coord` (coordination + independent verification). They are
peers, not the user.

> ### ★ THE RULE, LEARNED ~TWELVE TIMES ACROSS TWO SESSIONS
> **This repository's existing documents are, as a rule, ahead of your analysis.** Before producing any
> competing artefact, read the owner document. Before claiming anything is missing, grep. Before calling a
> claim undefeatable, search `paper/refs.bib`. Before citing a key, grep it.
>
> ### ★★ AND THE RULE THAT SUPERSEDED IT ON 2026-08-01
> **A green check on a PROXY is worth nothing.** I reported "the paper assembles cleanly" four times from
> `build_paper.py --md-only` — which exits *before* pandoc and tectonic. It was true of the markdown and
> silent about the PDF, and **the dissertation is graded on the PDF alone**. Three separate defects hid
> behind proxies this session. **Verify the artefact, never its stand-in**, and when a check returns a
> suspiciously clean result (0 %, 100 %, "no warnings"), suspect the instrument first.

---

## 1. READ THESE FIRST, IN THIS ORDER

1. **`CLAUDE.md`** — the five ★ PRIORITIES (5 = 100 % reproducibility, strict) and the Okhrati **D1–D6**
   block (every number arrives with mechanism, uncertainty, counterfactual).
2. **`CHANGELOG.md` entries `[2026-08-01b]` and `[2026-08-01d]`** — the two write-up sessions in full.
   `[..d]` blocks ⑫–⑲ are this session; ⑱ (the confirmatory tier) and ⑲ (the deliverable) are the two you
   must not skip.
3. **`docs/GRADE_95_MASTER_PLAN.md`** §16 (execution + drift fence) · §17 (playbook reconciliation) ·
   §18 (the landing gap) · §19 + §19.4b (wiring + the SHIP-FORM state) · §20 (the reasoning axis) · §21.
4. **`docs/LANE_PROTOCOL.md`** — the bus, the claims, the hook-enforced fence. **Then `docs/WRITEUP_95PLUS_PLAYBOOK.md`**
   (MOVE 1–4; not superseded, and in places better than the plan).

**Then join the bus and read your mail — do this before your first edit:**

```bash
cd llm-reward-portfolio
L="../.claude/lanes/lanebus.py"
python "$L" join writeup      # identity is free; it comes from CLAUDE_CODE_SESSION_ID
python "$L" board             # who is live, what is held, open threads, the campaign line
python "$L" inbox             # directed mail since you last looked
python "$L" next P            # ALWAYS draw process-error numbers from the arbiter (it starts at 101)
```

---

## 2. HARD BOUNDARIES — do not cross these

**NEVER EDIT** (hook-denied, and an edit turns the ops monitor RED on a live confirmatory campaign):
`src/**` · `scripts/**` · `config/**` · `prompts/**` · `docs/ops/**` · `docs/DEFERRED_FIXES_RUN4.md` ·
`docs/RUN*_SESSION_PROMPT.md` · `docs/CAMPAIGN_EXECUTION_RECORD.md` · `outputs/**` · `HANDOFF.md` §1.

**YOU OWN:** `paper/**` · `docs/GRADE_95_MASTER_PLAN.md` · `docs/V2_WRITE_TIME_REGISTRY.md` ·
`docs/CITATION_WORK_MAP.md` · `docs/LANE_COORDINATION_2026-07-31.md` · this file · `CLAUDE.md`.

**SHARED — re-read immediately before every edit:** `CHANGELOG.md` · `memory/session-current-focus.md`.
Stale reads have silently discarded work twice.

**EFFECT-BLIND, ABSOLUTE.** No treatment arm's sealed-test outcome may be read before the ladder completes
and the registered analysis runs. Reading *validation* fitness, execution counters and prompt structure is
fine and was done throughout. **This blindness is the precondition for §5's open decision.**

**THE FREEZE.** Tamer has said repeatedly he "doesn't care about the freeze" if it threatens quality. Read
that as *don't hide behind process* — **not** as licence to amend a frozen confirmatory design. The freeze
is what makes a null bankable; breaking it destroys the asset it is asked to protect. When a fix is
genuinely blocked by it, bring Tamer the trade-off explicitly.

---

## 3. STATE OF THE DELIVERABLE — measured 2026-08-01, re-verify before trusting

| | |
|---|---|
| PDF builds (**full** build, not `--md-only`) | **OK** — 230 pages, 615 KB |
| Dropped glyphs `U+FFFF` | **0** (was 73 across 44 pages) |
| Unresolved citations in the PDF | **0** |
| `check_citations.py` | **277 entries · 277 cited · 0 dangling · 0 verify-in-use · 0 unused** |
| Structure | body → References → Appendix A (p188) → B (p203) → D (p221) → T12 (p226) ✓ |
| `word_budget.py` | **23,195** against a hard **10,000** limit ⚠ |
| Write-up contribution to the drift fence | **0**, all session |

**Re-verify with exactly this — the `--md-only` shortcut is what hid a broken PDF for nineteen days:**

```bash
python scripts/build_paper.py                 # FULL build. Not --md-only. Ever.
python scripts/check_citations.py
python scripts/word_budget.py
python - <<'EOF'
import fitz
d = fitz.open('paper/_build/dissertation.pdf'); t = "".join(p.get_text() for p in d)
print("pages", d.page_count, "| U+FFFF", t.count('￿'), "| ??? ", t.count('???'))
EOF
```

---

## 4. WHAT THIS SESSION LANDED (so you do not re-derive it)

**Argument / content.** Playbook **MOVE 1** — CH2 rewritten as a three-act argument (objective is the
bottleneck → the bottleneck moves to the designer's evidence → finance is where evidence-use is normatively
checkable); 77 → 93 citation keys, **none lost**. **MOVE 2** — five severity exhibits into Appendix A §A.2b
plus the strongest one in the CH4 body. The **canonical RQ** now appears identically in the abstract, CH1,
the head of Methods and the Conclusion (there were three different phrasings). **CH7 "Beyond portfolios"**
(the C1 top-band clause, previously unclaimed). **CH7 aliasing** — Gallego's *feedback aliasing* engaged
with a verified definition, producing an original point: **his aliasing is a property of the statistic,
ours was of the rendering** — the vector carried the information and the formatter threw it away. **CH1
contributions table** (+28 words for five evidenced rows). **CH6 §6.5.1** the specification-gaming exemplar
that **R41 named in advance**, and **§6.8.0** authoring reliability.

**Integrity fixes in graded prose.** RUN 1's record count **835 → 621** (835 counted duplicated quarantined
probe records; it inflated a discarded-run count in the flattering direction). **CH6 "Arms run: 7" → 9**,
and the H4 slot went from 2 legs to the registered **4** — it would have reported a *different test* from
node N4. `D1–D16 → D1–D20`, `P1–P15 → P1–P106`, `2,875 → 2,883` tests, `36 → 99` record sections. **"0
defects reached the confirmatory data" was no longer true** → re-stated as *0 reached it **undetected*** with
D16 named. A **nested-bracket citation** silently dropped a real reference from the bibliography. **B.8.9's
containment claim was false** (`accounted` counts *attempts*, in all three implementations).

**The deliverable itself.** 73 dropped glyphs → **0**, in three passes; the last cause is worth knowing:
**pandoc will not close an inline-math span when the closing `$` is followed by a digit**, so
`$\approx$0.181` prints literally.

---

## 5. ★★★ OPEN — IN PRIORITY ORDER

### 5.1 A16 — the confirmatory tier, and the window that is closing
**Verified by running the frozen rule on synthetic p-values.** Weights: `N1 .5 · N2 .5 · N3=N4=N5=N6=0.0`.
Under the branch this study **predicts**, propagation halts at step one and **H1 at p = 0.0001 receives a
local α of exactly 0.000000**. With N2 rejecting, the same p-value is tested at 0.00825 and rejects.

- **All six nodes audited: exactly one is non-conformant.** `NODE_SOURCES["N2_h2_ra"]` reads the
  **superiority IUT only**; nothing reads a TOST p-value, though the frozen config registers
  `equivalence: tost_0.05_dsr` and calls it "a real pre-registered alpha source".
- **OPS DECLINED the conformance fix (M163), with a better argument than mine, and I accept it:** the
  hash-bound `PREREGISTRATION.md` — which `freeze.py` ranks **first**, calling the yaml "the YAML mirror" —
  says at :300 that the performance result *"sets only how tight the equivalence statement can be; it does
  not determine the thesis"*. **So it is two registered artefacts disagreeing, and the code follows the
  senior one.** Implementing my fix would be *"the forking path wearing conformance's clothes."*
- **What ops did instead recovers most of the value:** all four hypotheses are now decidable under the
  pre-registered R31 sensitivity at α/4 (it was three of four). The cost of leaving N2 alone is the
  **conjunctive** claim only.
- **Paper side is landed and honest:** CH4 rewritten (it had named the *wrong* operative rule — stale since
  R108 ratified the tier pre-data), the T-table row now says *conditionally*, CH6 reports **each node's
  local α beside its verdict**, and **B.8.14** discloses it with the direction stated (**conservative** — it
  can only withhold certification).
- ⏳ **Anything further here is legitimate only while no H2 outcome exists.** Watch the bus for the core
  ladder starting.

### 5.2 The word budget — the largest single risk
**23,195 words against a hard 10,000 limit.** This is a *fail condition*, not a defect.
- Tamer's standing decisions: **the deletion pass (R-1) is deferred**, and **the theory chapter is to be
  left alone** — he was offered the measured split (§3.1 615 · §3.2 400 · §3.3 544 · §3.4 992 · §3.5 782 ·
  §3.6 546 · §3.7 1,004 · §3.8 250 = 5,204) and chose "leave it for now". **Do not relocate theory without
  a fresh instruction.**
- **Already banked:** the prototype chapter was converted in place to **Appendix D** (`word-excluded`
  heading → `word_budget` scores it 0; §5.x numbering kept so cross-references resolve). −1,402 words,
  nothing lost — appendices are word-excluded, so relocation preserves every word for the reader.
- **The mechanism is relocation, not deletion.** Theory is also **not a permitted IFTE0008 section**, so it
  is a conformance defect as well as a budget one — but it is Tamer's call.

### 5.3 Three defects handed to ops — track them, do not fix them
1. **Bold does not render in the PDF.** `**HANDICAPS**` and `**single manipulated variable**` both come out
   `LMRoman12-Regular`; `LMRoman12-Bold` appears 12 times in 88,323 spans; literal `**` is **0**, so pandoc
   *is* consuming the markup. Source verified well-formed in both the chapter and the assembled markdown —
   **it is the pandoc/template/font path, and it is pre-existing.** On a criterion whose top band is
   "faultless presentation of data", every bold in the dissertation is currently flattened. **(M168)**
2. **`build_paper.py:259` fabricates "0 pandoc warning(s)".** `subprocess.run(..., text=True)` with no
   `encoding=` decodes UTF-8 output with the locale codec (cp1251 here); the reader thread dies and the
   warning count is computed over an *empty* buffer. A genuine failure would also print an empty
   diagnostic. One-line fix: `encoding="utf-8", errors="replace"`. Two other instances swept. **(M161)**
3. **`campaign_summary.json` does not exist for RUN 4**, so four registered analysis keys will be silently
   absent — including **`benchmark_floor`**, whose table is **already wired into your PDF**. **(analysis M166)**

### 5.4 Prose items ops explicitly handed back to you
- The body now numbers **1, 2, 3, 4, 6, 7** — CH6 → 5 and CH7 → 6 need renumbering.
- **Two appendices are unlettered**: "Appendix: Quality-control record" should be **A**; "Appendix table:
  Scale and difficulty" needs a letter.

### 5.5 Standing, lower priority
`R-3` fragmentation pass after wiring · `R-2` the four-rung why-ladder in CH1 · `R-4` the
considered-and-rejected register · `R-6` write CH6's remaining `[FROM CAMPAIGN]` slots as reasoning shells ·
the **F20 seed-trajectory panel** is registered in the manifest with **four binding caption conditions** —
note conditions 1 and 4 look contradictory and are not (see the manifest note) · the **SESOI reconciliation**
must be stated with its factor — see the corrected figure immediately below.

> ### ⚠ CORRECTION (writeup session 14df9fc8, 2026-08-01) — THIS LINE PREVIOUSLY CARRIED A REFUTED NUMBER
> Until now §5.5 instructed the incoming session to state the reconciliation as *"at the executed
> T = 1571, k = 0.9958, so 0.05 DSR = 0.0502 Sharpe"*. **That is wrong, and it was a standing
> instruction to write it into graded prose.** It substitutes the **test** window (T = 1571) into a
> conversion the registration defines over the **validation** window. Coord withdrew it and analysis
> M170 refuted it independently.
>
> **The registered figure is `0.05 DSR = 0.0756 annualised Sharpe`, at k = 0.6616, T = 694.**
> Verified from three independent routes before this correction was written:
> - hash-bound `config/preregistration.yaml`: `sesoi_ann_sharpe_equiv: 0.0756`,
>   `dsr_per_ann_sharpe: 0.6616`;
> - the live function: `k(694) = 0.661571 → 0.075578`; `k(1571) = 0.995771 → 0.050212`;
> - `scripts/power_analysis.py:195` — `VALIDATION_TRACK_LENGTH: int = 694`.
>
> The SESOI is registered *"in validation-DSR units"*, and the DSR is `held_out_fitness`, which is
> computed on the validation split only — so 694 is the correct track length by construction and
> 1571 answers a question the design never poses. **Measured: neither number appears anywhere in
> `paper/`**, so the wrong value never reached the deliverable and the existing ±0.05-DSR statements
> are correct as they stand. State the reconciliation with **0.0756** when landing it.

---

## 6. PROCESS ERRORS FROM THIS SESSION — inherit the lessons, not the mistakes

Numbers **P101–P107** and **P140** (draw new ones from `lanebus next P`, never from the highest you can find —
that caused three collisions).

| | The error | The lesson |
|---|---|---|
| P101 | Inherited "eleven orphaned artefacts" from three documents that agreed | **Three agreeing documents are one source repeated** when none re-measured |
| P102 | Wrote an estimated number ("eleven days before launch") into graded prose | The number that feels safe to estimate is the one that ships wrong |
| P103 | Nearly transcribed a garbled figure from a trusted internal document | **Read the artefact for figures, the document for judgement** |
| P104 | Reported "RED for ~15 hours"; it was 6h01m — I had missed a status class | **Overstating a risk is as inaccurate as understating one** |
| P105 | Stated a conclusion **twice** before verification was complete | A count that matches your expectation is a coincidence until you know what it counts |
| P106 | A checker raised `SyntaxError` and printed nothing | One line different, it would have printed `0` and read as clean |
| P107 | A scan returned a clean **100 %** because I had not established what the field meant | **The clean-0/100 % tell.** Suspect your own script |
| P140 | **Reported "assembles cleanly" from `--md-only` four times** | **Verify the artefact, never its stand-in** |
| — | While fixing glyphs I collapsed bold delimiters across 18 files, then produced **three** false-negative PDF probes (ligature, hyphenation, ambiguous anchor) | *"My search did not find it"* is not evidence unless the search is proven able to find it |

> **The countermeasure that actually worked was never more care by the author. It was another lane
> checking.** Coord's closing message says the same, independently. That belongs in the QC appendix above
> any technical finding — and it is already half-written there, as the *documentation* version of Class 4:
> both two-place defects were **claims, not code**, and **both flattered our own hypothesis**.

---

## 7. END-OF-WORK DUTIES (all of them, every time)

1. Append a **detailed** `CHANGELOG.md` block — past · present · future, and **every error you made**,
   including the ones you caught yourself.
2. Prepend a **short** cursor entry to `memory/session-current-focus.md` (≤ ~25 lines; it is a pointer).
3. Update `docs/GRADE_95_MASTER_PLAN.md` where the plan moved.
4. Post to the bus what other lanes need — **announce a correction before fanning out to fix it.**
5. **Re-run the §3 verification block and paste the real output.** Never claim green you did not observe.
