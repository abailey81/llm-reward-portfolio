# H4 DFO toolkit — integration spec (ready-to-apply; blocked only on the hot tree)

**Owner:** FEATURE/BUILD (me). **Status 2026-07-26:** the toolkit + resolver are BUILT, TESTED, COMMITTED
(`a1da13e`, `f427990`). The 4 surgical dispatch edits below are DEFERRED for ONE reason: the working tree
currently holds ~3,041 uncommitted lines across 66 files (the parallel sessions' live 2026-07-26 work —
kill-incident gate, CPU-lane device threading, deep-review loops 2 & 5). `campaign.py` / `parallel.py` /
`analyze_campaign.py` / every config file are mid-flight, so I cannot commit into them without entangling
or clobbering that WIP. **Apply the edits below the moment those files commit** (they are additive and touch
line ranges disjoint from the current dirty hunks, so they will not conflict).

## What is already done (verified, committed)
- `src/search/dfo_toolkit.py` — `cma_es_over_template`, `tpe_over_template` (drop-in siblings of
  `bayes_opt_over_template`: same signature/return, exact matched budget, deterministic-from-rng,
  cache/on_evaluated hooks) + `over_template_optimizer(arm)` resolver (one source of truth for both
  dispatchers; fail-loud on unknown arm).
- `pyproject.toml` — `cma>=4.0,<5.0` (BSD 4.4.4), `optuna>=4.0,<5.0` (MIT 4.9.0).
- `tests/test_dfo_toolkit.py` — 5/5 green.

## The 4 dispatch edits (apply verbatim once the tree is clean)

**E1 — `src/cluster/campaign.py:744`** (routing gate):
```python
_FAMILY_ARMS = ("random_search", "bayes_opt")            # -> ("random_search", "bayes_opt", "cma_es", "tpe")
```

**E2 — `src/cluster/campaign.py` ~814-850** (the `# bayes_opt` branch, after the `random_search` block):
replace `from src.search.bayes_opt import bayes_opt_over_template` with
`from src.search.dfo_toolkit import over_template_optimizer`, and the terminal
`bayes_opt_over_template(template_eval, family_bounds(...), {"matched_budget": n}, rng=...)` call with
`over_template_optimizer(arm)(template_eval, family_bounds(...), {"matched_budget": n}, rng=...)`.
Generalise the two `# bayes_opt —` comments to `# bayes_opt / cma_es / tpe — adaptive over-template optimizer`.
Everything else in the branch (the `template_eval` closure, `_family_specs`, resume replay) is
optimizer-agnostic and is reused UNCHANGED.

**E3 — `src/orchestration/parallel.py` ~1208-1247** (the `# bayes_opt` branch in `_drive_search_arm`):
identical swap — `from src.search.dfo_toolkit import over_template_optimizer`, then
`over_template_optimizer(arm)(template_eval, cast(...family_bounds...), {"matched_budget": n}, rng=...)`.
`params_to_source(...)` in its `template_eval` is optimizer-agnostic — reused as-is. (No change at
`parallel.py:1283`: cma_es/tpe are non-LLM, so `arm in _LLM_ARMS` is already False → they route to
`_drive_search_arm` automatically once they are in the roster.)

**E4 — priority (`src/cluster/campaign.py:1226`)**: NO CHANGE. `bayes_opt` is hoisted to `PRIORITY_CORE`
because its 30-proposal chain is the floor-bank's longest SERIAL path; cma_es/tpe are CONFIRMATORY (N4 portfolio) but
parallel-by-design, so they correctly fall to the `else` (`PRIORITY_STAGE1`) — below the confirmatory
core, never gating the rung (consistent with the campaign-speed priority + the baseline-depth logic).

## CONFIRMATORY RULING + the ATOMIC config activation (Tamer, 2026-07-26 — NO hedge)

**RULING (supersedes the earlier report-only recommendation):** cma_es/tpe are **CONFIRMATORY**. H4/N4 is
the snoop-free intersection–union test over the optimiser portfolio {random_search, GP-EI, cma_es, tpe} =
"the LLM beats the pointwise MAX = the best black-box optimiser of the reward family at matched budget" —
the exact mirror of H1's beat-the-best-human IUT. Deep-researched backbone (now in CH4 §4.5/§4.7 + refs.bib,
committed 1b2366e): the portfolio-envelope is the fair best-numerical-search — no single optimiser dominates
across budgets [`raponi2024lowbudget` IEEE TEVC BBOB+Gym; `shahriari2016bo`], budget-inappropriate methods
pruned with cause; IUT size <= alpha for ANY portfolio size [`berger1982iut`] so N4 stays ONE node with ZERO
added family-wise multiplicity (graph weights unchanged); the free-form-vs-6-term expressivity asymmetry
STRENGTHENS the claim (harder search at the same 30-eval budget; only edge = the semantic prior; attribution
decomposed by the mechanism audit); decisive either way via a non-inferiority readout at the pre-registered
SESOI; and it fills a VERIFIED lineage gap (corpus sweep: no reward-design paper pre-registers this
head-to-head vs best-in-class DFO of a matched family).

**Land these five ATOMICALLY — a prereg node naming arms the cluster cannot run is a freeze landmine (R84):**
1. **prereg `N4_h4` (`config/preregistration.yaml:198`):** `comparators: [random_search, bayes_opt]` ->
   `[random_search, bayes_opt, cma_es, tpe]`. Graph nodes/weights (`:201-208`) UNCHANGED.
2. **prereg `h4_search_controls` (`:163`):** the separate-estimands mirror — `tests: [h4a_vs_random_search,
   h4b_vs_bayes_opt]` + `bonferroni_2` -> add `h4c_vs_cma_es, h4d_vs_tpe` + `bonferroni_4`.
3. **arms roster:** `config/campaign.yaml:3 arms:` += `cma_es, tpe`; `config/arms.yaml` +=
   `cma_es: {search: template, llm: false}` / `tpe: {...}`; `config/eureka_loop.yaml` search list += both;
   `src/viz/style.py` += their plot styles.
4. **dispatch E1–E3** (above): `_FAMILY_ARMS` += cma_es/tpe + the `over_template_optimizer(arm)` swap in
   BOTH dispatchers. `parallel.py` is now CLEAN; **`src/cluster/campaign.py` is the ONE remaining dirty
   file — the whole activation is gated on it clearing.** Land 1–4 + E1–E3 in ONE commit + re-run
   `freeze --check`.
5. **analysis (`scripts/analyze_campaign.py`):** extend the N4 block to the 4-portfolio IUT (max-p over the
   four one-sided paired-seed tests) + the 3-way non-inferiority-at-SESOI readout (mirror the N6/H1 IUT
   block); add a regression test on a synthetic 4-optimiser panel.

## Paper (my lane, not blocked)
CH4 already frames the H4 control as best-in-class. Once decision 1 is ratified, state explicitly:
confirmatory N4 over the 2 registered controls; CMA-ES + TPE as the descriptive best-in-class robustness
(3 DFO paradigms: GP-EI surrogate / CMA-ES evolution-strategy / TPE density-ratio). Cites already in
`refs.bib` (`hansen2001cmaes`, `bergstra2011tpe`, `akiba2019optuna`).
