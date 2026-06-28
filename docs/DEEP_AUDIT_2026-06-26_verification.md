# DEEP AUDIT — verification pass on the R43–R53 discharge (2026-06-26)

7-agent first-hand verification of the claim that amendments **R43–R53** discharged the prior
13-agent register (`DEEP_AUDIT_2026-06-25_13agent.md`). Each agent re-broke / re-ran / recomputed,
did not trust "DISCHARGED". Verdict: the prior register **is** genuinely closed — but the same-day
burst left/introduced a new cluster of integrity gaps, two of them serious. NEW = missed by all four
prior sweeps or introduced by R43–R53.

---

## CONFIRMED GENUINELY FIXED (verified first-hand — bank these)

- **R52 sandbox from-import RCE — CLOSED.** All from-imports rejected at `executor.py:469-475`;
  re-attacked with `__import__`, importlib, mro/bases walks, getattr/globals, exec/eval, f-string
  dunder walks, np FS-callables without from-import — **every payload GATE=False**, no new RCE.
  Regression-tested (`test_sandbox.py:47-64`).
- **Suite genuinely green:** 722 collected → **721 passed, 1 skip (POSIX-only), 0 fail/xfail**;
  `ruff check src tests scripts` clean; `mypy` 65 files clean; `freeze.py --check` exit 0. Licensed
  data present so data-gated tests actually ran; the slow PopArt divergence proof ran (15.7s).
- **Freeze hash reproduces** `0efc2411…0816f`; `frozen: false` intact (still user-gated). R52
  `_normalize_bytes` idempotent on doubled `\r\r\n` (verified).
- **R46 EVT ξ≤−0.5 guard** correct + tested; **R50 H3/H4 TOST + named references** correct +
  complete; **R49 H1 descriptive-only** honestly contained (`inference_status`, ⚠ panel banner);
  **R48 PopArt σ-logging + ablation harness** wired.
- **Citations:** DLM (`behari2024dlm`, NeurIPS 2024, 4-delta distinguish) in `refs.bib`;
  Khraishi-Okhrati now `@inproceedings` ICAIF DOI 10.1145/3533271.3561682; GEPA/OPRO/CARD/Singh/IRD/Qu
  promoted with `% VERIFY`. No new fabrications.
- **R45 §1a prediction table** is a genuine, falsifiable Popperian commitment in structure.
- **T0 (placebo reversal) reconfirmed** first-hand: winner CVaR-5% placebo −0.01711 (safest) >
  random −0.01798 > distributional −0.01896 > scalar_cvar5 −0.01981 > scalar −0.02113;
  `analysis.json` ships `distributional_vs_placebo` stat −4.277, p=0.0005; responsiveness −0.053.

---

## NEW BLOCKERS introduced/left by the R43–R53 burst

### V1. [CRIT][NEW] The freeze would lock a **6-arm** design while the campaign runs **7** — and the 7th is the headline control
- `config/preregistration.yaml:11` (frozen mirror): `arms: [distributional, scalar, placebo,
  scalar_cvar5, random_search, bayes_opt]` — **6, no `placebo_shuffled`.**
- `config/campaign.yaml:3` (what runs): **7 arms, includes `placebo_shuffled`.**
- `PREREGISTRATION.md:76` §3 still reads "**The six arms**"; R32 added `placebo_shuffled` only to the
  §10 secondary block.
- `scripts/freeze.py:91-95` `_BOUND_CONFIGS` = inference/environment/data only — **`campaign.yaml`
  and `arms.yaml` are NOT in the hash**, and `assert_prose_matches_yaml` **never checks the arm
  list**. The 6-vs-7 contradiction passes the freeze gate silently.
**Grade impact.** The "bankable null" rests on "the design was cryptographically fixed in advance."
The hash fixes a 6-arm design while a 7-arm campaign runs, and the differing arm is exactly the
R32/R38 structure-vs-content control billed as the most reviewer-convincing experiment. **Fix:** add
`placebo_shuffled` to `preregistration.yaml:11` + retitle §3 "seven arms"; add `campaign.yaml` (≥ its
`arms`/`h1_baselines`) to `_BOUND_CONFIGS`; add an arm-list check to `assert_prose_matches_yaml`.

### V2. [CRIT][NEW] `placebo_shuffled` has **never been run** — the headline construct-validity control is vapourware in the only results that exist
Prototype ran 6 arms (`prototype.yaml:9`); `outputs/prototype/` has no `placebo_shuffled/`;
`campaign_overfitting.json:352`: *"placebo_shuffled has no test record."* The R32/R38 format-vs-content
control exists only as config + synthetic-array unit tests. Combined with V1: the strongest
reviewer-facing control is (a) never executed and (b) outside the freeze. **Fix:** run it in the
campaign and report it, or down-grade it honestly from "the control that closes the threat" to
"specified, pending compute."

### V3. [HIGH][NEW] R44 broke the **delisting_band** — the "headline tail instrument" silently skips under the new univ3 default
`analyze_campaign.py:2889-2909`, called arg-less at `:3511` → resolves `suffix = gold_suffix()` =
**univ3** (post-R44), then loads `shumway_audit_log_univ3.parquet` — which **does not exist** on disk
(only `…_univ4.parquet`). Returns `status="skipped"`. But R44/PREREG:170-172 elevate this band to *the
load-bearing evidence* that abandoning univ4 is harmless ("H2 ordering invariant across the band,
~2% CVaR-5% sweep"). With the default suffix it produces **nothing** — an examiner re-running
`analyze_campaign` gets a silently skipped instrument. **Fix:** pin the band to the univ4 audit/panel
explicitly (`delisting_band(suffix="univ4")`), independent of `gold_suffix()` — it must read the
univ4 audit to locate the 333 cells, then overwrite at d∈grid.

### V4. [HIGH][NEW] The null is **not honestly framed everywhere** — stale "p=0.004 bankable" survives in headline-facing docs
The T0 reversal is disclosed only in the 13-agent audit file + raw `analysis_report.md`. Stale
one-sided overclaim survives in: `DEEP_H2.md:214-215,257,435,461,490` ("distributional won on CVaR
p≈0.004 … makes the prototype's signal *bankable*"); `EXAMINER_grade_audit.md:149-152`. Neither
states the same IUT **fails the placebo leg** (distributional tail significantly *worse* than the
zero-info placebo, p=0.0005). **Fix:** one clause in each — "in the prototype the distributional tail
was worse than placebo (p=0.0005); the reframe builds structure to bank a *campaign* tail win; the
prototype number is directional-null, reversed under control."

### V5. [HIGH][NEW] `PREREGISTRATION.md` §7 self-contradicts on the headline panel, and `RIGOUR_LEDGER` is stale on the day it shipped
- `PREREGISTRATION.md:163-164` lead: "**The headline data panel is `univ4`** (R33)"; `:173-175`:
  "univ3 is now ALSO the FROZEN headline panel (R44)… univ4 is not the headline." Both-headline
  contradiction in one paragraph, on the data-fabrication axis the tail thesis depends on; the config
  mirror (`preregistration.yaml:163 headline: univ3`) already disagrees with the prose.
- `docs/RIGOUR_LEDGER.md` (created by R53, dated 2026-06-26) states its source is "R11–R42", titles §B
  "R11–R42", and its R33 row still calls univ4 the headline — it **omits R43–R53, including R53
  itself**. Stale residue also in `loaders.py:52,69-70` and `analyze_campaign.py:3506` docstrings
  ("exports LLM_RP_GOLD_SUFFIX=univ4 … the headline panel"). **Fix:** rewrite §7 lead to univ3; strike
  "ALSO"; extend the ledger to R53; fix the docstrings.

---

## NEW MAJOR (framing / correctness overclaims)

### V6. [MED-HIGH][NEW] "Off-critic ⇒ agent-independent" is an equivocation — the fed tail distribution is endogenous to the agent it steers
`measurement.py:1-8` / `CLAUDE.md:71-77` claim the estimator "works on any agent / does not depend on
the agent." The code loop (`loop.py:397-432`, `runner.py:199-201`) fits the tail estimator on the
**policy's own realized returns under the candidate reward**. "Off-critic" legitimately means
*critic-architecture-agnostic post-hoc estimator* (reads no Q-net) — true; it does **not** mean
*agent-independent* — false. H2 compares two coupled reward→policy→measurement loops, not a richer-vs-
poorer signal about a fixed object. Okhrati (RL+risk) will see the endogeneity. **Fix:** reword every
"agent-independent / works on any agent" → "critic-agnostic post-hoc estimator"; add a one-paragraph
endogeneity disclosure (train/val split already mitigates selection-overfitting).

### V7. [MED-HIGH][NEW] "Fixed agent across arms" is overstated — PopArt + `ent_coef=auto` make effective exploration arm-dependent
`popart.py:113-118` (`min_scale=1.0`) ⇒ σ is reward-magnitude-dependent ⇒ arm-dependent;
`trainer.py:124` `ent_coef="auto"` tunes entropy temperature against the *normalized* scale. popart.py
itself admits "a LATENT, scale-driven cross-arm difference inside an ostensibly fixed agent."
Prototype scalar rewards hit |r|≈1e4. "Fixed agent" is really "fixed architecture + knobs, arm-varying
*effective* entropy regularisation." The bounding instrumentation (σ_max logging, R48 ablation) exists
but **the answer isn't in** (campaign not run). **Fix (must-have table):** report cross-arm σ_max +
the `popart=False` ablation; soften "fixed agent" wording.

### V8. [MED][NEW] Core-contribution estimator documented as fitting LOG-returns but fed SIMPLE returns
`portfolio_env.py:284-286,308` emits a **simple** `port_ret`; `runner.py:88` → `loop.py:410-412` feed
it to `dist.fit()` with no `log1p`, yet `measurement.py:7-8,196-198` names the input "log-returns."
Second-order at daily scale (won't flip H2 ordering; fed and test CVaR both simple) but a real
correctness/disclosure defect in the module CLAUDE.md calls "the core contribution." **Fix:** apply
`log1p` at the fit boundary, or correct every "log-return" reference to "simple return."

### V9. [MED][NEW] R47's DSR-units TOST — required by the power doc to license the bankable null — is not wired
`CAMPAIGN_power.md:104-133` correctly converts MDE 0.256 Sharpe → 0.177 DSR ≫ 0.05 SESOI and states
the TOST must be evaluated **in DSR units**. But the implemented `h2_tost` (`analyze_campaign.py:2224-
2244`) runs in per-seed Sharpe/CVaR-IQM units (margin 0.05), and `power_analysis.tost_equivalence`
(the DSR-units path) is **never called on campaign records**. So a campaign non-rejection won't
actually compute the equivalence the power doc says is required. **Fix:** wire a DSR-units TOST into
`h2_tost`, or downgrade the power-doc claim to "Sharpe-units TOST reported; DSR-units descriptive."

### V10. [MED][NEW] Single Claude family is the only LLM ever run; the frozen §8 open-weights second model is `PIN_ME`
`llm.yaml:25` `open_weights_check_model: "PIN_ME"`; `contamination.cross_model_disagreement` tested
only on synthetic arrays, degrades to `{"status":"no_data"}`. `PREREGISTRATION.md:183-187` §8 commits
to an open-weights second model — **unexecuted frozen protocol item** (undisclosed deviation), and no
sentence can earn the plural "LLMs" (it is one Claude family, Sonnet→Opus, same vendor/key). **Fix:**
log the deviation; scope every "LLMs" claim to the single model.

### V11. [MED][NEW] The mechanism differential (R51) pools fixed-template search arms into the cross-arm tail differential
`inspect_rewards.py:709` includes `random_search`/`bayes_opt` (each ONE fixed human-authored template,
zero variance, tail_rate=2.000) in the same "LLM tail-construct prevalence" differential as the LLM
arms — a category error in the one mechanism exhibit. **Fix:** drop those two from the differential
loop or flag them "fixed template — not interpretable." (Numbers otherwise reproduce exactly:
distributional 1.69 / scalar 2.02 / placebo 1.90; CVaR-level 35/39 vs 13/40 — a real FORM finding.)

---

## NEW MINOR / disclosure

- **V12 [MED][NEW] Stale run-count / DSR-trial accounting** after R30+R32: locked at "6×30=180,
  ~600 runs" but 7 arms ⇒ 210 winners, H3 single-shot stage adds a block, H1 is really 9 rewards
  (~270 not 120). Per-arm matched-compute holds; total + DSR trial count understated → under-deflates
  Sharpe. Disclose + re-tally.
- **V13 [MED][NEW] Okhrati kill-shot:** the FZ0/(VaR,ES) Diebold-Mariano corroboration backtest
  (`es_backtest.py`) has **no small-sample (Harvey-Leybourne-Newbold) correction** and no
  `null_calibration` certifying its size; DM is oversized at small T and ES backtests are low-power on
  ~8-yr windows (Bauer 2025). No current answer to "what is the actual size/power of your tail
  corroboration?" **Fix:** add HLN correction + a size/power calibration table.
- **V14 [LOW-MED][NEW] Softmax-simplex projection** (`portfolio_env.py:47-75`) cannot reach an exact
  cash corner — structurally damps the "flee to cash" allocations a tail agent most needs; the
  exact-zero L1 alternative exists but wasn't frozen. All-arms ceiling; disclose + justify.
- **V15 [MED][NEW] Sandbox non-RCE determinism holes:** reward code can (a) zero the shared gold panel
  via the `np.asarray` view passed by `portfolio_env.py:263,302` (proven: panel row corrupted across
  candidates), and (b) `np.seterr` leaks global float-error mode across candidates. Not escapes, but
  violate the no-cross-contamination/determinism guarantee. **Fix:** pass `setflags(write=False)` /
  copied arrays + shallow-copied `info`; drop `seterr` from the allowlist.
- **V16 [LOW][NEW]** `_normalize_bytes` doubled-`\r\r\n` idempotency is correct but unguarded by a
  test (the one line-ending test would pass against the pre-R52 code). Add `assert
  _normalize_bytes(b"a\r\r\nb")==b"a\nb"`.
- **V17 [LOW][NEW]** Construct overclaim survives in `CLAUDE.md` header/:73 and `PREREGISTRATION.md:116`
  ("the realized-return distribution is fed to the reward-DESIGNER") — re-contamination risk for
  drafting. Align to the README "multi-level tail-risk feedback" label.
- **V18 [LOW][NEW]** Supervisor sign-off on the pivot disclosure is still **PENDING**
  (`PROPOSAL_PIVOT_DISCLOSURE.md:3` DRAFT) while the body asserts "with my supervisor's agreement" —
  obtain written sign-off before that sentence enters the PDF.
- **V19 [LOW][NEW]** Stale `walk_forward` in `run_campaign.py:32,1382` comments and the unbound
  `data_pipeline/config/inference.yaml:6` snapshot (5 seeds, ledoit_wolf, all-candidates DSR) — not
  read by live code, but greppable contradictions of R43. Banner or delete.

---

## BOTTOM LINE

The R43–R53 discharge was **real** — every prior register item I re-tested is genuinely closed, the
suite is honestly green, and the hardest fixes (sandbox RCE, EVT guard, TOST, citations) are correct
and tested. The repo did **not** regress on the science. But the same-day burst introduced a *new*
integrity layer of problems, because the changes touched the frozen surfaces faster than the freeze
machinery and the docs could be reconciled:

**The single most important NEW issue:** the freeze binds a **6-arm** design while the campaign runs
**7** (V1), and the 7th — `placebo_shuffled`, the headline construct-validity control — is invisible
to the freeze, contradicts the frozen mirror, and **has never been run** (V2). Every prior audit
trusted the freeze as the integrity backstop; the backstop has a hole exactly where the late R32
amendment landed.

Realistic state: still **low-to-mid 80s**, capped now by *process-integrity reconciliation* (V1–V5)
rather than science. All of V1–V5 are a focused day of work. After that — plus the campaign actually
run with `placebo_shuffled` + σ_max + the delisting band reported, and the null framed honestly
everywhere — the 90% ceiling is reachable.
