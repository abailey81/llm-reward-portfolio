# Presentation checklist — the Criterion 4 pass

**Why this file exists.** Criterion 4's top band is *"excellent write up in readability, clarity and
structure, with **faultless presentation of data**."*That phrase is the difference between the 80 band and
the 90 band on **a quarter of the mark**, and it is the one axis entirely within our control. "Faultless"
means *every single one* — so this is a per-item checklist to be walked at the end, not a principle to be
kept in mind.

**How to use it.** Do not run this while writing; run it once when the figures and tables are final, and
walk it item by item with the document open. An unticked box is a defect, not a preference.

---

## 1. Every figure

- [ ] **Axes labelled, with units.** Sharpe is dimensionless — say so or omit the unit deliberately;
      returns are decimal or per cent, never ambiguous; turnover is a fraction of portfolio value per
      session.
- [ ] **Caption stands alone.** A reader who reads only the caption understands what the figure shows and
      what to conclude. No caption may say "see text".
- [ ] **Referenced in the body text**, by number, at the point the reader needs it.
- [ ] Legend present wherever more than one series appears; no reliance on colour alone (greyscale-safe
      and colour-blind-safe).
- [ ] Sample size on the figure or in the caption (`n = 30 seeds`, `n = 1,571 sessions`).
- [ ] Uncertainty shown wherever an estimate is plotted — intervals, not bare points.
- [ ] **The sealed window stated as `2020-03-30 → 2026-06-30, n = 1571`** on any figure over test data.
      Not "2020–2026", which is the panel window and understates every benchmark.

## 2. Every table

- [ ] **Consistent decimal places within a column** — Sharpe to 3 or 4 dp throughout, chosen once;
      percentages to 1 dp; never 4 dp in one row and 2 in the next.
- [ ] Units in the column header, not repeated in every cell.
- [ ] **No table that needs a paragraph to be understood.** If it does, the table is wrong, not the prose.
- [ ] Referenced by number in the text.
- [ ] Net **and** gross reported together wherever a Sharpe appears for an agent, because net alone
      invites the objection that the pair pre-empts.
- [ ] **The Sharpe convention stated once, prominently**: all reported Sharpe figures are the **raw**
      annualised ratio (no risk-free subtraction) — and no table silently mixes raw with excess.

## 3. Consistency across the whole document

- [ ] One symbol per quantity, matching `paper/NOMENCLATURE.md`; the sign convention there governs.
- [ ] Arm names spelled identically everywhere (`placebo_shuffled`, not "shuffled placebo").
- [ ] Every number that appears twice appears identically. **A count that reads 2,875 in one place and
      2,620 in another is a defect**— state which is the collected count and which is the written count.
- [ ] No retracted figure survives anywhere: the passive comparator is **+1.2825** (EW-30) and
      **+1.1656** (market_ew); `+0.817 / +122 %` and `+0.773 / +166 %` must not appear.
- [ ] No claim that any reward "beats the market" — none does, even gross.

## 4. Structure and format (free marks, and conspicuous when absent)

- [ ] The **sixteen prescribed sections, in the prescribed order**.
- [ ] Arial or Helvetica, **≥ 10 pt**; **1.5** line spacing.
- [ ] Pages numbered consecutively **from the title page**.
- [ ] **Harvard** referencing throughout, applied consistently.
- [ ] A dedicated **Limitations** subsection (named exemplary practice in the guidelines) —
      `paper/APPENDIX_B_limitations.md` is the register; the chapter subsection summarises and points to it.
- [ ] **Wall-clock compute reported in prose** — the examiner docks for its absence. 8.09 h per scored
      training; ≈326,254 core-hours for the full ladder.

## 5. The word budget (verify, don't assume)

- [ ] Main-body prose **≤ 10,000 words**. Equations, code, tables, figures, footnotes, appendices, the
      abstract and the glossary are **excluded** — this is a much larger lever than it appears, and
      "anything that can be a table should be a table" is the operative rule.
- [ ] Methodology + Results + Discussion ≈ **60 %** of the body.
- [ ] Count the body **mechanically**, not by estimate, and record the number.

## 6. The abstract — written LAST, rewritten five times

- [ ] ~300 words, **excluded** from the count, and it **stands alone** (the guidelines require this
      explicitly) — it must not merely summarise the conclusions.
- [ ] It states, in this order: **we predicted a tie · we found it · we located where the chain breaks ·
      we identified what would fix it.**If it says that, every later section reads as confirmation; if it
      is vague, the same sections read as excuses.
- [ ] Legible to a non-specialist: no un-introduced `CVaR`, `IUT`, `SESOI`, or `DSR`.

## 7. The single figure that carries the paper

- [ ] **Decide it explicitly.** The strongest candidate is the **psychometric threshold overlay** — each
      model's measured detection threshold against the distribution of differences actually fed it, with
      the fraction below threshold shaded — because it states the whole mechanism result in one image and
      is legible to someone who knows no finance.
- [ ] ⚠ **It is contingent.** That figure requires the psychometric module (R96), which is **specified but
      not built**. **Fallback if it is not activated:** the **baseline Sharpe distribution showing the
      turnover result**— net vs gross per reward, with turnover as the ordering variable. That figure is
      buildable from data already archived and carries contribution C3 on its own.

---

## Open hand-offs — build-level defects found in the compiled PDF, 2026-08-09

Each item below was confirmed by reading `paper/_build/dissertation.pdf` itself, not the markdown. The
four that were fixable from `paper/FRONT_MATTER.md` are already closed and are listed at the end for the
record. The three below are open because the fix has to land in a file the front-matter lane does not own.
Every diagnosis here was established by controlled experiment, and the experiment is named so the next
lane does not have to repeat it.

### H1. Table 5.2 prints only 48 of the 64 characters of the frozen design hash

- **Where.** `paper/CH6_results.md:29`, the first row of Table 5.2.
- **What the reader sees.** `3ca6f01ab7724d47bd5d01bc9e73b4d3150c049e1048dd86` and nothing after it. The
  text run ends at x = 599.1 pt on a 595.28 pt page, so the tail is outside the page and is clipped.
- **Cause.** The 64-character value is one inline code span, so LaTeX sets it as a single unbreakable
  `\texttt` run. It has no break point, the longtable column is about 240 pt wide, and the run is about
  394 pt, so it can neither wrap nor shrink.
- **The fix, verified to render complete.** Split the value into two 32-character code spans separated by
  one space, which gives LaTeX a legal break. Replace that line with exactly this:

```
| Frozen design hash (must match `PREREGISTRATION.md`) | `3ca6f01ab7724d47bd5d01bc9e73b4d3` `150c049e1048dd86a864b400a230432f`, tag `prereg-v2.1`, re-verified by `freeze.py --check` |
```

  Verified by compiling that exact table through the pinned pandoc and Tectonic: both halves render in
  full inside the Value column on consecutive lines, ending at x = 500.6 and x = 503.9 pt, well inside the
  right text edge. A `\newline` between the halves was also tried and is WRONG: pandoc mangles it inside a
  pipe-table cell and the word "ewline" prints into the left margin.
- **Already mitigated, not a substitute.** The full 64-character value is now printed once in the
  Declaration of Originality, where the paragraph is full text width and it fits on one line. That makes
  the study verifiable today. Table 5.2 still shows a truncated value, and a table that prints a wrong
  version of a number is its own defect.

### H2. Two blank pages that carry only a folio, before two of the wide specification tables

- **Where.** In the current build, folios 109 and 121. Folio 109 sits between the introduction of the
  design-decision table and the table itself (`paper/tables/T_design_decisions.md`). Folio 121 sits
  between the introduction of Table 19 and that table (`paper/tables/T_reproducibility_and_mechanism.md`).
- **Cause, established by eight controlled compiles rather than inferred.** It is a `longtable` artefact,
  not a stray `\newpage`. When the space left on the current page cannot hold the repeated header plus the
  first data row, and these tables have data rows that each fill most of a page, longtable ships out an
  empty page and restarts. The signature is visible on the first table page, which prints the column
  header twice.
- **What was tried and does NOT fix it**, each compiled and inspected: removing the thematic break before
  the table, changing how full the preceding page is, adding `\clearpage` immediately before the table,
  zeroing `\LTpre` and `\LTpost`, and setting the table in `\footnotesize`. `\setcounter{LTchunksize}{1}`
  breaks the compile outright.
- **What DOES fix it**, compiled and inspected: giving the table a short first data row. Inserting one
  one-line row at the top removed the blank page entirely in the isolated reproduction. So the practical
  remedies, in order of preference, are to lead each of these two tables with a compact row, or to split
  the mega-rows so no single row approaches a full page, or to break each table into two shorter tables.
  All three land in the two table files above.

### H3. Folio 119 is a page carrying nothing but a horizontal rule

- **Where.** `paper/tables/T_design_decisions.md:32`, the trailing `---` at the end of the file.
- **Cause.** That thematic break renders as `\rule{0.5\linewidth}` and is pushed past the end of the
  table, and the next assembled file begins with a `\newpage`, so the rule gets a page to itself.
- **The fix.** Delete line 32 of that file. Verified in an isolated reproduction: with the trailing `---`
  present the final page carries the rule, and with it removed the page carries no rule at all.

### H4. Two table numbering series collided -- CLOSED 2026-08-10

The legacy bare-numbered series is gone. It was renumbered into the chapter scheme in order of first
appearance, every call site was rewritten in the same pass, and the compiled PDF was re-read to confirm
that no reference dangles and no number is duplicated. The map, recorded here because it is the key to
any older note or commit that still speaks the old language:

| Printed until 2026-08-10 | File | Prints now |
|---|---|---|
| Table 10 Literature positioning matrix | `paper/tables/T_literature_positioning.md` | Table 2.1 |
| Table 18 The four innovation axes | same file | Table 2.2 |
| Table 1 The nine arms | `paper/tables/T_arms_and_hypotheses.md` | Table 4.7 |
| Table 2 Environment specification | same file | Table 4.8 |
| Table 3 Confirmatory decision rules | same file | Table 4.9 |
| Table 3b Inference machinery | same file | Table 4.10 |
| Table 4 Authoring models with pins | `paper/tables/T_models_and_reward_canon.md` | Table 4.11 |
| Table 5 The eleven-reward canon | same file | Table 4.12 |
| Design decisions (no number at all) | `paper/tables/T_design_decisions.md` | Table 4.13 |
| Table 19 Reproducibility statement | `paper/tables/T_reproducibility_and_mechanism.md` | Table 4.14 |
| Table 20 Mechanism apparatus | same file | Table 4.15 |
| Table 21 The chain measured link by link | same file | Table 4.16 |
| Table 22 The gear train | same file | Table 4.17 |
| Table 6 Nine published allocators | `paper/tables/T_benchmark_allocators.md` | Table 5.9 |
| Table 6b The estimation-error test | same file | Table 5.9b |
| Scale and difficulty (no number at all) | `paper/tables/T_scale_and_difficulty.md` | Table E.1 |

Numbers follow the chapter each table PRINTS in, not the chapter that cites it. Tables 4.16 and 4.17
print in Chapter 4 at pages 123 and 126 and are cited from Chapter 5, which is ordinary and is not a
reason to give them 5.x numbers. The earlier hand-off map proposed 5.10 for the allocator table; 5.10
was already taken by the cross-model synthesis, so the allocator floor took 5.11 and its panel 5.11b.

⚠ `paper/FIGURE_TABLE_MANIFEST.md` is a THIRD scheme again, T1 to T17, matching neither the old printed
series nor the new one. It is an internal working file that reaches no PDF; read the captions, not it.

### Closed on 2026-08-09, from `paper/FRONT_MATTER.md`

- Page size was US Letter, 612 x 792 pt. Now A4, 595.28 x 841.89 pt, set by a `papersize: a4` YAML
  metadata block at the head of the front matter.
- All twelve figure captions printed twice-numbered, as "Figure 6: Figure 5.1 — …". The auto label is now
  suppressed by a body-level `\@makecaption` redefinition, and every caption prints its own number once.
  The cleaner fix belongs in the pandoc invocation and is recorded in the front matter beside the block.
- The List of Figures omitted all seven Chapter-5 figures. All seven added, every caption checked against
  `paper/CH6_results.md`.
- The List of Tables omitted ten tables. Eight numbered ones added, 1.5, 3.1, 4.3, 4.4, 4.5, 4.6, 21 and
  22, plus the two that carry no number at all. Five existing rows whose wording had drifted from the real
  caption were corrected.
- The Word-Count Statement named the tool and the exclusion list but printed no count. It now states
  9,984 words with its date and the command that produced it.

---

## Sign-off

Walked and completed by: ____________  Date: ____________

**Every box ticked, or the unticked ones listed here with a reason:**
