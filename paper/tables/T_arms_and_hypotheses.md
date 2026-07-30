# Tables (CH4 Methods): the nine arms · the environment · the confirmatory decision rules

Three specification tables, all excluded from the word count. Each is extracted from the frozen
configuration, so a reader can diff the table against `config/` and find no daylight.

---

## Table 1 — The nine arms (`config/arms.yaml`)

**Read this table as the whole experiment.** Rows 1–5 differ in **one thing only** — the feedback block
the reward-designing model is shown. Rows 6–9 replace the model entirely with a derivative-free
optimiser, which is what makes "did the LLM help?" answerable.

| Arm | Feedback the designer receives | Role |
|---|---|---|
| `distributional` | `full_tail_set` — CVaR 5 %, 10 %, 25 %, 1 %, left-tail mass, robust skew (**6 numbers**) | **treatment** |
| `scalar` | `scalar_only` — the validation fitness alone (**0 tail numbers**) | **primary control**: the field's universal practice |
| `scalar_cvar5` | `scalar_plus_cvar5` — the scalar plus CVaR 5 % (**1 number**) | **dose**: is one tail number enough? |
| `placebo` | `scalar_plus_inert_block` — six inert `+0.0000` constants under *neutral* labels | **format control**: matches block shape and token count with no diagnostic content |
| `placebo_shuffled` | `scalar_plus_shuffled_tail` — the six real values on **deranged** labels | **structure control**: is the label→value *correspondence* what is used? |
| `random_search` | none (`llm: false`, searches **code**) | DFO comparator |
| `bayes_opt` | none (`llm: false`, searches a **template**) | DFO comparator |
| `cma_es` | none (`llm: false`, template) | DFO comparator |
| `tpe` | none (`llm: false`, template) | DFO comparator |

**Why two placebos and not one.** They isolate different things. `placebo` separates *"six numbers are
present"* from *"six **tail** numbers are present"*. `placebo_shuffled` keeps the real labels and values
and destroys only their **pairing**, separating *"the tail structure is usable"* from *"tail-ish numbers
are present"*. Verified in the archive: the CVaR ladder is monotone in **102/102** `distributional`
blocks and **0/24** `placebo_shuffled` blocks — a mathematical consequence of nested tail sets, so the
derangement is demonstrably active.

---

## Table 2 — Environment specification (`config/environment.yaml`)

| Field | Value | Note |
|---|---|---|
| Risky assets | **30** + cash | `include_cash: true`; 31 weights summing to 1 |
| Universe selection | `top_market_cap_point_in_time` | PIT at the window start — **no look-ahead** |
| Observation lookback | **60** sessions | this is also the purge that delays test execution to 2020-03-30 |
| Realized-vol windows | 20, 60 | |
| VIX in state | yes (pre-lagged) | |
| **Previous weights in state** | **yes** | the agent can observe its own position, so turnover is controllable — which is what makes the turnover result a *choice* of objective rather than a mechanical artefact |
| Action space | `simplex`, softmax projection, bound 10.0 | **long-only** by construction |
| Transaction cost | **10 bps** one-way headline; grid 0/5/10/25/50 registered report-only | `proportional_turnover` on half-L1-**drifted** turnover `0.5·‖w − w_held‖₁` |
| Timing | `return_realized_after_action` | the trade settles before the return is earned |
| Cash rate | 0.0 | disclosed; the risk-free series enters the reported Sharpe, not the environment |

---

## Table 3 — The confirmatory decision rules, fixed in advance (`config/preregistration.yaml`)

**For a non-specialist reader.** Each row states a test *and the direction that would count as support*,
written before any sealed data was seen. An **intersection–union test** (IUT) requires the claim to hold
against *every* comparator simultaneously — which is why it needs no multiplicity correction: the
composite null is only rejected if each component is. A **TOST equivalence** test can *reject the
presence* of an effect larger than a pre-specified bound, which is how a null becomes a finding rather
than an absence of evidence.

| Node | Hypothesis | Test | Endpoint / metric | Direction | Equivalence backstop |
|---|---|---|---|---|---|
| **N1** | H2-Tail | `h2_tail_iut` | CVaR at 5 % | one-sided, `distributional` better | — |
| **N2** | H2-RA | `h2_ra_iut_or_tost` | Sharpe | one-sided, `distributional` better | **`tost_0.05_dsr`** — the pre-registered SESOI |
| **N3** | H3 | `h3_iterative_gt_singleshot` | per-seed IQM | one-sided | — |
| **N4** | H4 | `h4_llm_gt_search_iut` | vs `random_search`, `bayes_opt`, `cma_es`, `tpe` | one-sided (IUT over **all four**) | — |
| **N5** | structure | `distributional_gt_placebo_shuffled` | CVaR at 5 % | one-sided, **content over format** | — |
| **N6** | H1 | `llm_beats_best_human_reward` | annualized Sharpe | one-sided, LLM better | IUT over the **full 11-name** canon; champion = `max` over canon, **no selection** |

**Two properties worth naming, because a marker will not infer them.** N6's champion is the *maximum*
over eleven hand-written rewards with **no selection step** — the hardest available human bar, not a
convenient one. And N2 carries an equivalence backstop, so the result is **decisive either way**: either
`distributional` is better, or an effect larger than the SESOI is rejected. There is no outcome in which
the study merely fails to find something.
