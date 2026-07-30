# Presentation checklist — the Criterion 4 pass

**Why this file exists.** Criterion 4's top band is *"excellent write up in readability, clarity and
structure, with **faultless presentation of data**."* That phrase is the difference between the 80 band and
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
      2,620 in another is a defect** — state which is the collected count and which is the written count.
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
      we identified what would fix it.** If it says that, every later section reads as confirmation; if it
      is vague, the same sections read as excuses.
- [ ] Legible to a non-specialist: no un-introduced `CVaR`, `IUT`, `SESOI`, or `DSR`.

## 7. The single figure that carries the paper

- [ ] **Decide it explicitly.** The strongest candidate is the **psychometric threshold overlay** — each
      model's measured detection threshold against the distribution of differences actually fed it, with
      the fraction below threshold shaded — because it states the whole mechanism result in one image and
      is legible to someone who knows no finance.
- [ ] ⚠ **It is contingent.** That figure requires the psychometric module (R96), which is **specified but
      not built**. **Fallback if it is not activated:** the **baseline Sharpe distribution showing the
      turnover result** — net vs gross per reward, with turnover as the ordering variable. That figure is
      buildable from data already archived and carries contribution C3 on its own.

---

## Sign-off

Walked and completed by: ____________  Date: ____________

**Every box ticked, or the unticked ones listed here with a reason:**
