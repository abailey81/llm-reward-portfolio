## Where this study sits in the literature, cell by cell

<!-- THE "PURPOSE" PARAGRAPH WAS DELETED ON 2026-08-11 UNDER THE META-COMMENTARY RULE. It said the
     table makes the novelty cell legible, that its rows are neighbours and its columns are the
     separating dimensions, and that a matrix can be checked where prose can only be believed. A reader
     looking at the matrix can see all four of those things. The sourcing paragraph below is kept
     because it is not about the table, it is evidence: it states where every cell can be verified and
     in what proportion, which is the claim a sceptical examiner actually tests. -->

**Sourcing discipline, and where to check it.** Every weight-bearing cell is sourced from the work
itself. Of the 54 such cells, being six evaluative columns over nine prior works, 36 carry a short
verbatim quotation with its page, 3 carry a page locator, and 15 are counted full-text searches recording
the strings searched and the hit counts. None is unsourced. Each quotation is located by its enclosing
section as well as its page, because a quotation can be character-exact and still be the wrong evidence:
a sentence in a paper's Related Work reports what others did. That check changed one cell. Three of the
nine carry a dated first-hand read, and where the record holds no date the row says so. The cell-by-cell
record is `docs/POSITIONING_SOURCES.md` in the accompanying repository. Three works often named beside
this lineage carry no row, because they are not nearest neighbours on these columns: DrEureka and
Auto-MC-Reward are robotics and Minecraft systems whose feedback is scalar or trajectory-shaped, and
RD-Agent(Q) authors alpha factors and not a reward for a fixed agent. All three are cited and read
first-hand elsewhere in this document. An invented cell is worse than an absent row.

<!-- ⛔ THE SOURCING PLEDGE POINTED OUT OF THE ARTEFACT UNTIL 2026-08-10, AND THAT WAS THE DEFECT.
     It read: "Every cell is traceable to a first-hand-read entry in 01_LITERATURE_DOSSIER.md under
     paper/, where all 196+ corpus PDFs were read first-hand and each neighbour below carries a
     `VERIFIED first-hand` date or a quoted verbatim claim." Two things were wrong with it and only one
     was a wording problem. (1) The dossier IS NOT IN THE PDF, and the guide says the second marker "may
     come from any discipline and will only assess your submitted report", so the one exhibit that most
     invites cell-by-cell checking sent the checker to a document they cannot open. (2) MEASURED against
     the dossier: a dated first-hand read is recorded for THREE of the nine (ELfolio and GIFT at
     2026-07-02, FINCON at 2026-08-10), Eureka carries a quoted verbatim claim without a date, and the
     remaining five carried neither. The pledge was therefore true of a minority of the rows.
     THE FIX IS EVIDENCE, NOT WORDING: all nine PDFs were re-read from the corpus copies on 2026-08-10
     and every weight-bearing cell now carries its source INSIDE the document, at Appendix H. The three
     counts above (36 verbatim / 3 locator / 15 counted) are machine-counted from the shipped table, not
     tallied by hand: a hand tally read 37/2/15 and was wrong on REvolve's agent cell, which is a page
     locator rather than a quotation. -->

<!-- ⛔ THE THREE-WORKS RATIONALE ABOVE WAS FACTUALLY FALSE UNTIL 2026-08-10 AND IS NOW THE REAL REASON.
     It read: "Papers named in external commentary but for which the dossier holds no detailed entry,
     namely RD-Agent, Auto-MC-Reward and DrEureka, are DELIBERATELY OMITTED rather than filled in from
     memory." All three have full, verified `refs.bib` entries (`ma2024dreureka`, `li2024automc`,
     `li2025rdagentq`), all three are cited in the body (CH2:36, CH1:105, appendices/F:541), and all
     three print in the compiled References. A reader following the cross-reference met the document
     asserting it held no entry for works it cites two chapters earlier. The replacement is not a
     softening: "not a nearest neighbour on these columns" is a design justification, which is a
     stronger thing to be able to say than "we had no source". -->


---

```{=latex}
\Needspace{3\baselineskip}
```

```{=latex}
\begingroup\tabcaptionstyle
```
**Table 2.1 — Literature positioning matrix: the nearest neighbours, column by column.** Every neighbour fails at least one of the seven columns, and the pre-registration column has no other row reading yes, so the claim can be checked cell by cell rather than believed.
```{=latex}
\par\endgroup
```

<!-- COLUMN WIDTHS ARE ARITHMETIC HERE, NOT TASTE. Read this before touching the dash row.
     The text block is 453.54pt (A4 less the 2.5cm margins). Pandoc sets a pipe table as a
     longtable whose column widths are the RELATIVE DASH COUNTS below, over
     (\linewidth - 2(n-1)\tabcolsep), so the dash row is the only width control the source has.
     Set at \footnotesize, which is exactly 10.0pt in a 12pt document and therefore exactly the
     IFTE0008 floor: \scriptsize would be 8pt and is REFUSED for that reason, not for taste.
     MEASURED DEMAND per column, the widest chunk that must be set on one line, taken from the
     glyph advances in the compiled PDF:
       Work 62.0 (bold "Text2Reward") · Domain 54.8 ("autonomous") · Who authors 58.7
       ("state-reward", en dash, no break) · feedback 69.8 ("trend/variability," and
       "success>failure", no break at / or >) · Agent 51.5 ("continuous-") · Risk-sensitive 46.1
       · Pre-registered 49.8 (the abbreviated hash).  Sum 392.7pt.
     At the default \tabcolsep of 6pt only 381.54pt is available and the seven equal columns each
     got 54.5pt, so FOUR of the seven were starved, namely Work, Domain, Who authors and feedback:
     "success>failure" could not fit and broke as "suc-cess", and "Text2Reward" split mid-name at
     its own \allowbreak. \tabcolsep is cut to 3pt,
     which frees 36pt and brings the available width to 417.54pt, and the dash counts
     19/17/18/21/16/14/15 then set
       66.1 · 59.2 · 62.6 · 73.1 · 55.7 · 48.7 · 52.2 pt,
     every one of them 2.3 to 4.4pt above its measured demand, with the surplus given to the
     feedback column because it carries 687 of the matrix's 1,877 set characters.
     ⚠ THE MARGIN IS NOT DECORATION. At an earlier 44.6pt the Domain column could not hold
     "autonomous" (54.8pt) and TeX set an OVERFULL box rather than hyphenating it, so the word ran
     10.1pt past its column and 2.1pt into the next one. Ragged-right columns do not always fall
     back to hyphenation, so a column must be sized for its widest word, not close to it.
     ⚠ The seven columns are NOT separable into panels: the claim this table makes is that every
     neighbour fails at least one column, which a reader can only check with all seven visible on
     one row. Re-measure with docs/analysis/criteria_scorecard.py after any edit that lengthens a
     cell, and re-derive the dash row if a new unbreakable token exceeds its column. -->

\begingroup\footnotesize\setlength{\tabcolsep}{3pt}

| Work | Domain | Who authors the reward | What the loop's feedback contains | Agent held fixed? | Risk-sensitive objective? | Pre-registered? |
|-------------------|-----------------|------------------|---------------------|----------------|--------------|---------------|
| **Eureka** (ICLR 2024) | robotics / control | **LLM writes reward code** | per-component **scalar** training series plus an aggregate fitness | yes | no | **no** |
| **Text2\allowbreak{}Reward** (ICLR 2024 Spotlight) | robotics / control | **LLM writes reward code** | human natural-language **failure summaries** | yes | no | **no** |
| **REvolve** (ICLR 2025) | autonomous driving | **LLM writes reward code** | human **Elo preferences** | yes, discrete-action | no | **no** |
| **CARD** (arXiv 2410.14660) | robotics / control | **LLM writes reward code** | trajectory feedback and a **binary** success-failure ordering | yes | no | **no** |
| **DLM** (NeurIPS 2024) — *structural twin* | public-health RMABs (bandit) | **LLM writes reward code** | simulated-outcome **distribution** over demographic state-features | yes, discrete-action | no | **no** |
| **ELfolio** (2025) — *closest portfolio system* | **portfolio** | LLM writes trading-**strategy** code (not the reward) | **scalar Sharpe** as fitness | no (path templates vary) | no | **no** |
| **FinRL-DeepSeek** (arXiv 2502.07393) | **portfolio** | **fixed, hand-written** CPPO / CVaR-PPO objective | LLM emits sentiment/risk **scores that scale actions** | yes | **yes** (CVaR objective) | **no** |
| **GIFT** (arXiv 2606.08450) — *freshest finance neighbour* | **portfolio** | LLM designs the **state–reward interface**: an intrinsic term + a subset of a **fixed risk-rule library** | generic rollout diagnostics (ICs, reward trend/variability, drawdown) | **no — co-varies the STATE** | partially (fixed rule library) | **no** |
| **FINCON** (NeurIPS 2024) | **portfolio** | no numeric reward trained into a policy | CVaR by **verbal** reinforcement over beliefs | n/a | **yes** (CVaR, verbally) | **no** |
| **THIS WORK** | **portfolio** | **LLM writes reward code** | **multi-quantile lower-tail profile** measured **off-critic** | **YES — only the fed block varies** | **yes** (tail-aware by construction) | **YES — hash-frozen before the sealed leg**|

\endgroup

<!-- ⛔ THE DLM AGENT CELL WAS MIS-CODED UNTIL 2026-08-10, AND THE WAY IT WAS WRONG IS THE LESSON.
     It read "no (bandit, not continuous-action)", and Appendix H supported it with a genuine,
     correctly located, character-exact quotation from DLM p. 2: "The RMAB problem, introduced by
     Whittle, is classically solved through the Whittle index heuristic policy." Every string-level
     check passed. The sentence is nonetheless the WRONG EVIDENCE, because it sits under DLM's own
     heading "2 Related Work / RMABs:" and reports how the problem was CLASSICALLY solved by others.
     What DLM itself does is at p. 5, under "4.3 Multi-Agent Simulation": "We evaluate each
     LLM-proposed reward function R1:K by training a policy network theta under each proposed reward
     Ri", updated with PPO at Alg. 1 line 13. So DLM DOES hold one learner fixed while the reward
     varies, which is this study's own identification structure, and the cell now says so.
     THE CONJUNCTION SURVIVES, ON THREE COLUMNS RATHER THAN FOUR, and the bullets below now name
     them: domain, feedback content and risk-sensitivity (plus pre-registration). What was lost is
     the fourth. That is a real narrowing of the claim and it is stated rather than absorbed.
     THE GENERAL DEFECT, now closed for all nine rows: the appendix proved that each quotation
     EXISTS on the page it names, not that the passage LICENSES the cell. Every quotation in
     Table H.1 has since been re-located against its enclosing section heading, and this was the
     only cell sourced to a passage about other people's work. See Appendix H.2 item 7. -->

---

### What the matrix shows

**1. Not one finance row authors the reward.** The four portfolio systems all put a model inside a trading
loop and all stop short of the objective: FinRL-DeepSeek scales actions against a fixed hand-written CVaR
objective, ELfolio authors a strategy, GIFT designs an interface over a fixed rule library while also
varying the state, and FINCON trains no numeric reward at all. **And not one reward-design row is in
finance.** The five systems that do author reward code work in control, driving and public-health
allocation, and none carries a risk-sensitive objective. The two halves of the table fail on opposite
columns, which is what makes the claim a claim about the field.

**2. The conjunctive cell is empty.** No prior work combines an LLM-authored reward program, multi-level
tail feedback as the manipulated variable, a fixed agent, and a risk-sensitive portfolio setting. Each
neighbour fails at least one column, and the failures are structural:

<!-- ⛔ TWO MECHANICAL DEFECTS FIXED HERE, 2026-08-10, both visible on one compiled page.
     (1) The `+` signs above were written as "variable*+ *a fixed agent*+ *risk" — no space before the
     operator — and the compiled page read "the manipulated variable+ a fixed agent+ risk-sensitive".
     (2) The two items below opened with "*the", with no space after the marker, so markdown read the
     asterisk as an emphasis delimiter rather than a bullet. The compiled page ran both items together
     into ONE paragraph, mid-sentence and mid-lowercase: "... none is in finance or risk-sensitive. the
     finance neighbours either do not ...". They are now "- " bullets with the continuation lines
     indented two columns, which is the same rule the Declaration's third-party list follows. Verify in
     the RENDERED PDF, never in the source: two bullets must appear. -->

- the reward-design lineage (Eureka, Text2Reward, REvolve, CARD, DLM) all hold a learner fixed, and
  four of the five feed scalars, prose, or preferences. DLM is the exception on the feedback column,
  and holding a learner fixed while feeding a distribution is together what earns it the name *structural
  twin*: it trains one PPO
  learner under each proposed reward. It fails the conjunction on the other three columns instead. Its
  distribution is over demographic state-features, not over realised returns, so it is not a tail
  profile. Its domain is public-health allocation rather than a portfolio, and it is neither risk-sensitive nor
  pre-registered. None of the five is in finance or risk-sensitive.

- the finance neighbours either do not let the LLM author the reward at all (FinRL-DeepSeek is a score
  encoder over a *fixed* CVaR objective, and FINCON is verbal with no trained reward [`yu2024fincon`]),
  author a *strategy* rather than a reward (ELfolio, on a scalar Sharpe-ratio fitness, which is
  *precisely this study's control arm*), or co-vary the state alongside the reward (GIFT), which
  forfeits identification.

**3. ELfolio is the sharpest single comparison.** Its fitness is a scalar Sharpe ratio, *this study's
control condition*, so the nearest portfolio system in the literature is, in effect, running our baseline
arm without the treatment.

**4. The pre-registration column has one entry, and it is the most durable of the three claims.** A
referee can always name an adjacent paper, so an empty-cell claim is disputable by construction. "No
pre-registration in the automated-reward-design and portfolio-RL literature" is instead a claim about a
practice: verifiable in an afternoon, and not defeated by pointing at a similar study. It is placed last
because it is the smallest of the three, and kept because it is the one that survives an attack on the
other two. The claim is time-sensitive and is defended by dated sweeps every two to three weeks plus a
mandatory sweep before submission, with any neighbour surfaced by a sweep cite-and-distinguished in §2.4
even when it weakens a claim. Two corpus entries did exactly that and both are handled there.

<!-- ⛔ THE RULE ABOVE WAS FALSIFIED BY ITS OWN DOCUMENT UNTIL 2026-08-10, AND IS NOW STATED AS WHAT THE
     DOCUMENT ACTUALLY DOES. It promised that a sweep-surfaced neighbour "receives a row here", and two
     did not: `qian2026infolimits` and `xue2026riskfeedback`, both verified first-hand, both with
     `refs.bib` entries, both cite-and-distinguished at CH2:172-179, and both absent from the matrix.
     A ROW WAS THE WRONG REMEDY for them, which is why the rule moved rather than the table: this
     matrix's seven columns are about who authors the reward for a fixed agent, and neither work
     authors a reward at all, so a row would have carried five "n/a" cells and said nothing a reader
     could check. The same sentence also pointed at §2.2 while both entries live in §2.4; that
     cross-reference is corrected here too. -->

Table E.8 sets those four axes of innovation against the fifth, which is empty, and names the two
nearest misses rather than asserting a void.
