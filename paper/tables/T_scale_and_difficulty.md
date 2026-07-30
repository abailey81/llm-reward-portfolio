# Table (Appendix): Scale and difficulty of the executed system

**Purpose.** Criterion 3 is normalised *"given difficulty of the problem"* — the most favourable wording
in the rubric for this project — but **a marker cannot weight difficulty they cannot see**, and students
systematically under-communicate what they built. This table makes it visible in one page. Appendices are
excluded from the 10,000-word limit, so it costs nothing in prose.

**Tone discipline: factual, not boastful.** Every row is a count or a measurement with its source
command or its registered origin. No adjectives, no "extensive", no "comprehensive". A reader should be
able to reproduce every figure.

---

## A. What was built

| Component | Count | Source |
|---|---|---|
| Python modules in the experimental engine (`src/`) | **111** | `find src -name '*.py' -not -path '*__pycache__*'` |
| Lines of engine code (`src/`) | **33,556** | as above, `wc -l` |
| Data-acquisition modules (`data_pipeline/`) | **28** | `find data_pipeline -name '*.py'` |
| Command-line entrypoints (`scripts/`) | **65** | `find scripts -name '*.py'` |
| Configuration files (single source of truth for all parameters) | **14** | `find config -name '*.yaml'` |
| Automated test files | **161** | `find tests -name 'test_*.py'` |
| **Automated tests passing at the launch gate** | **2,875 passed / 3 skipped / 0 failed** | certified pre-launch, `PYTEST_RC=0` read from the log, source-tree hash identical both ends |
| Test functions as written (before parametrisation expands them) | **2,620** | `grep -rh '^def test_' tests/` — the 2,875 figure above is the *collected* count |
| Version-controlled commits | **989** | `git rev-list --count HEAD` |
| Written design/analysis documents | **181** | `find docs paper -name '*.md'` |

## B. The registered experimental design

| Dimension | Value | Source |
|---|---|---|
| Experimental arms | **9** | `config/arms.yaml` — 5 LLM-fed arms + 4 derivative-free optimisers |
| Hand-written comparator rewards (the H1 canon) | **11** | `config/campaign.yaml: h1_baselines` |
| Reward-authoring models in the replication suite | **11** | 1 confirmatory (`claude-opus-5`) + **10** open/closed replication legs, `config/legs.yaml` |
| Candidates per arm | **30** | `config/campaign.yaml: candidates_per_arm` (6 reflection generations × 5) |
| Training steps per candidate | **400,000** | `config/campaign.yaml` — B\*, set by the measured convergence knee (R77) |
| Seed ladder (assurance tiers) | **30 · 100 · 189 · 279 · 340 · 403 · 568** | `config/campaign.yaml: seeds.tiers` |
| Concurrent supervised execution lines | **12** | core + H3 single-shot + 10 replication legs |
| Registered pre-analysis amendments | **115** (highest `R115`) | `PREREGISTRATION.md` amendment table |
| Frozen design hash | `3ca6f01ab7724d47…`, tag `prereg-v2.1` | `python scripts/freeze.py --check` |

## C. The compute actually required

| Quantity | Value | Source |
|---|---|---|
| Trainings in the full registered ladder | **42,128** | registered work model (R108): 1,800 search + 71·n test at n=568 |
| Measured wall-clock per scored training | **8.09 h** | measured, not estimated |
| Measured wall-clock per reflection chain step | **3.59 h** | measured |
| **Core-hours for the full ladder** | **≈326,254** | derived from the two measurements above |
| Peak concurrent cores held on UCL Myriad | **1,584** | measured during execution |
| Substrate | CPU lane, pools `d` only; `t` excluded | the `t` pool is AMD and would break bit-exact CRN reduction order |

## D. Off-the-shelf versus written for this study

| Off-the-shelf (used as published) | Written for this study |
|---|---|
| Stable-Baselines3 SAC; sb3-contrib TQC (secondary critic experiment) | The long-only 31-weight portfolio environment with half-L1-drifted turnover accounting |
| PyTorch, NumPy, pandas, SciPy | The reward **contract + AST-gated sandbox** for executing untrusted LLM-authored code |
| Provider SDKs (Anthropic, OpenAI-compatible) + `tenacity` retry | The tail-measurement / feedback stack (empirical + EVT), critic-agnostic and off-critic |
| Refinitiv/LSEG market data (licensed) | The reflection loop, the 9 arms, and the two placebo controls |
| — | The inference stack: deflated Sharpe, PBO, TOST equivalence, `rliable` per-seed aggregation, BH-FDR |
| — | The cluster orchestration layer (`src/cluster/`, 8 modules) with archive-truth resume, per-batch driver locks, and a 17-check live sentinel |
| — | The survivorship-free point-in-time data pipeline (28 modules) and the figure engine |

## E. What the difficulty actually consisted of

Three things, stated plainly because they are what a marker cannot infer from a count:

1. **Executing untrusted generated code safely, 42,128 times.** Every reward is LLM-authored Python
   compiled and run inside the training loop. It is AST-gated once, then executed in-process on
   anonymised arrays. A single unguarded construct is a remote-code-execution path.
2. **Holding an identification claim across twelve concurrent execution lines.** Only the fed feedback
   block may vary. Three separate defects in this campaign were the *same shape* — a resource shared
   across concurrent lines but keyed by an identifier unique only *within* one line — and none was
   detectable by any unit test, because all 2,875 exercise a single line. They required live invariants.
3. **Bit-exact determinism as a design constraint, not an aspiration.** Common random numbers underpin
   every paired contrast, so the CPU model, thread count, BLAS parallelism, `tf32`, and every provider
   pin are part of the frozen design. One host with a different Xeon generation was enough to raise a
   validity alarm and required fencing.

> **Cross-reference.** The honest execution narrative — four launches, 115 amendments, and every defect
> with its root cause and fix — is the *Quality-control record* appendix, framed analytically rather than
> chronologically. It is the strongest available evidence that the rigour is real rather than described.
