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
because its 30-proposal chain is the floor-bank's longest SERIAL path; cma_es/tpe are REPORT-ONLY and
parallel-by-design, so they correctly fall to the `else` (`PRIORITY_STAGE1`) — below the confirmatory
core, never gating the rung (consistent with the campaign-speed priority + the baseline-depth logic).

## Open design decisions for Tamer / Okhrati (pre-freeze)
1. **Report-only vs confirmatory (my rec: REPORT-ONLY).** Keep the confirmatory **N4 IUT over
   {random_search, bayes_opt}** exactly as registered (no prereg change). cma_es/tpe are the STRONGER
   black-box controls, reported **descriptively** in H4 (the LLM beats — or honestly does not beat — the
   best DFO across all 3 paradigms). Rationale: adding them to the confirmatory IUT makes the registered
   test *harder to pass with no power gain* and bets the confirmatory claim on out-optimising CMA-ES;
   report-only delivers the non-fragility ("we tried the best optimizers") without that fragility, and
   preserves pre-registration integrity. This is the honest, depth-over-breadth choice.
2. **Run mechanism for report-only comparators (config, currently dirty).** They must RUN to be reported.
   My rec: a `report_only_arms: [cma_es, tpe]` list in `config/campaign.yaml` iterated at `PRIORITY_STAGE1`
   — so they never enter the confirmatory `arms:` roster or N4, but do produce winners for the descriptive
   panel. Alternative: fold into the existing baseline report-only runner. NEEDS the config owner.
3. **Analysis (`scripts/analyze_campaign.py`, dirty).** Extend the H4 panel to report
   `max-over-{random, GP-EI, CMA-ES, TPE}` descriptively alongside the confirmatory N4.
4. **Roster metadata (`config/arms.yaml`, clean).** Add `cma_es`/`tpe` `{search: template, llm: false}`
   rows + viz styles in `src/viz/style.py` (clean) — apply together with E1-E3 so activation is atomic
   (holding them avoids a transient "arm known but unrunnable" inconsistency).

## Paper (my lane, not blocked)
CH4 already frames the H4 control as best-in-class. Once decision 1 is ratified, state explicitly:
confirmatory N4 over the 2 registered controls; CMA-ES + TPE as the descriptive best-in-class robustness
(3 DFO paradigms: GP-EI surrogate / CMA-ES evolution-strategy / TPE density-ratio). Cites already in
`refs.bib` (`hansen2001cmaes`, `bergstra2011tpe`, `akiba2019optuna`).
