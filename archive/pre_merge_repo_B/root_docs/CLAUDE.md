# CLAUDE.md — Operating Manual for Claude Code

You are working inside the dissertation repository of **Tamer Atesyakar** (UCL MSc Banking & Digital Finance, supervisor **Dr Ramin Okhrati**, AIRiskLab). Project: *LLM-Driven Agentic Reward Engineering for Risk-Sensitive Deep RL in Portfolio Allocation*. Dissertation due **1 Sep 2026**; candidate ICAIF 2026 paper deadline **2 Aug 2026**. The mark target is the 90–100 band, whose rubric words are "faultless execution, exemplary analysis, entirely appropriate methods, unquestionable originality." Your job is to make *faultless execution* literal.

Read this file fully before your first edit in any session. When in doubt, prefer **doing less, correctly, with a written decision** over doing more.

---

## 0. The one-sentence research question (everything traces to it)

> Do LLM-evolved reward functions, refined under distributional (IQN) tail-risk feedback, produce deep-RL portfolio policies with superior out-of-sample risk-adjusted performance versus hand-designed rewards, on a survivorship-bias-free 30-stock US large-cap universe (2005–2025), across market regimes and under realistic costs?

If a proposed change does not serve this sentence, it is out of scope. Period.

---

## 1. HARD RULES (violations are never acceptable)

**R1 — The pre-registration is law.** Once `PREREGISTRATION.md` carries a freeze commit hash (recorded in `DECISIONS.md`), you may not change hypotheses, the fitness function, candidate/seed budgets, α/cost grids, split boundaries, or inference rules. Amendments require: (a) a new ADR in `DECISIONS.md` with reasoning, (b) an explicit note that the supervisor must be informed, (c) the change marked as a *deviation* to be reported in the dissertation. Silent edits to frozen design are research misconduct, not refactoring.

**R2 — Scope lock.** The following are permanently rejected (confounds or budget-killers — full reasoning in `docs/` strategy notes): news/NLP sentiment features; multi-agent LLM committees; transformer/GNN/Mamba state encoders; additional asset classes (crypto/FX/futures); Decision Transformers; fine-tuning the LLM; intraday/LOB data; market-impact execution models; additional DRL algorithms beyond SAC/PPO/TD3/IQN-SAC; live paper-trading. Do not implement, scaffold, or "just prototype" any of these. If the user asks for one, point to this rule and the rejected-additions table, and ask whether they want to override via ADR.

**R3 — Leakage laws.**
- Features at time *t* may use information available strictly before the decision at *t*. No future bars, no full-sample normalisation, no smoothed-anything in decision paths.
- HMM regimes: fit on the **training window only**; use **filtered** probabilities `P(z_t | data_{1:t})`, never smoothed; **shift(1)** before any use as a feature or stratifier of decisions.
- Fitness **F is computed on the held-out validation window only** and is **never** the training reward. The reward shapes learning; F selects candidates. Keep them separated in code and in prose.
- Splits respect the embargo (`config/inference.yaml`); CPCV uses purging + embargo.
- The reward **search** runs only on the development split defined in `PREREGISTRATION.md`; evaluation windows see only frozen winners.

**R4 — Data immutability.** Files under `data/` are write-once. Every pull appends SHA-256 lines to `data/manifest/checksums.txt`. Code must verify checksums before reading. Never edit a data CSV; if a pull was wrong, pull to a new versioned filename and record an ADR. Never fabricate, interpolate, or "fill in" market data silently — missing-data policy lives in `config/data.yaml` and must be applied explicitly with logging.

**R5 — Statistics laws.**
- DSR inputs are **unannualised** Sharpe ratios; the trial count **N = every candidate evaluated across all arms** (LLM, random, BayesOpt, single-shot), not just the survivors. Maintain the count programmatically (`stats_inference.TrialLedger`).
- Quantiles from the IQN critic are **sorted before** any CVaR/tail statistic (crossing rate is computed on the raw, pre-sort array and reported).
- Every headline cell: ≥5 seeds; ablation cells: ≥3 seeds. No single-seed claims anywhere in reported results.
- Annualisation factor, return convention (log vs simple), and day-count are set once in `config/environment.yaml` and imported — never re-derived ad hoc.

**R6 — Generated-code safety.** LLM-generated reward functions are untrusted input. They run only through `src/sandbox.py` (subprocess, resource limits, no network, stdlib+numpy only, timeout). Never `exec()` candidate code in the main process. Every candidate (valid or not) is archived verbatim under `data/candidates/` with its prompt, model snapshot id, temperature, and outcome.

**R7 — Citation honesty.** Formulas and protocols carry their citation in the docstring (they already do — keep it that way). Never paraphrase a result as established if it lives in `docs/notes/*` with a VERIFY flag. The novelty claim is always hedged "to the best of our knowledge" with the sweep dates.

**R8 — No silent dependency or version changes.** `requirements.txt` bounds are deliberate; adding/upgrading a dependency requires an ADR. d3rlpy is pinned to the 2.x API verified in ADR-003.

---

## 2. Repository map and ownership

```
PREREGISTRATION.md      frozen design (R1)                 DECISIONS.md   ADR log — append-only
RELATED_WORK_WATCH.md   monthly novelty sweeps             README.md      front door
config/                 ALL parameters, citation-annotated YAML — code reads these, never hardcodes
  eureka_loop.yaml      N=5 iters × K=16 samples × R restarts; component-dict requirement
  environment.yaml      state spec (Sood [(n+1)×T], T=60), action softmax, costs, conventions
  data.yaml             universe rule, vendors/fields, FRED ids, screens, delisting corrections
  inference.yaml        DSR/PBO/Ledoit-Wolf/BH-FDR settings, seeds, splits, embargo
  llm.yaml              snapshot pins (closed + open-weights companion), temperature, token logging
prompts/                system / safety / mutation / reflection templates (versioned _vN)
src/                    feedback_schema, stats_inference, fitness, portfolio_env, reward_contract,
                        regimes, sandbox, smoke_iqn_sac, pull_pilot, reconcile, config loader
tests/                  pytest — must pass before any commit ("make test")
docs/                   environment & schema specs, entitlements checklist, paper notes, REFERENCES.md
reports/                supervisor brief, vendor reconciliation
data/                   immutable pulls + manifest (R4); candidates/ archive
```

## 3. Commands

```
make setup        # venv deps + write requirements.lock
make test         # pytest -q  (gate for every commit)
make lint         # ruff check src tests
make smoke        # python -m src.smoke_iqn_sac   (GPU box)
make pull-pilot   # python -m src.pull_pilot      (needs .env / terminal)
make reconcile    # python -m src.reconcile
make freeze-design# prints the git-hash line to paste into DECISIONS.md after committing PREREGISTRATION.md
```

## 4. Conventions

- **Config-driven everything.** A numeric literal in `src/` that exists in `config/` is a bug. Load via `src/config.py`.
- **Typing + docstrings.** Public functions are typed; docstrings state purpose, the citation if the logic implements a published formula, and the leakage posture where relevant ("uses only information ≤ t").
- **Reward contract.** Every reward callable has signature `fn(ctx: RewardContext) -> tuple[float, dict[str, float]]` and must pass `reward_contract.validate()` (finite, bounded, component dict sums consistent). This is what makes Eureka-style reflection and the forensics chapter possible — never accept a bare-scalar reward.
- **Determinism.** Seed numpy/torch/env per run from `config/inference.yaml`; log the seed in every artifact filename.
- **Logging over printing.** Structured logs; every training/eval run writes a JSON sidecar (config hash, data checksums, seed, wall-clock, tokens if LLM involved) — these populate the dissertation's compute-reporting table, which examiners explicitly dinged the coursework for omitting.
- **Commits.** Imperative subject; body references the plan block or ADR (e.g., "T4: freeze pre-registration v1.0 (ADR-005)"). Run `make test` first, always.
- **ADR protocol.** Any decision that future-you could question gets 5 lines in `DECISIONS.md`: date, decision, alternatives, reason, consequences.

## 5. Domain crib sheet (so you don't re-derive or mis-remember)

- **Eureka loop (Ma et al., ICLR 2024):** N=5 iterations × K=16 i.i.d. samples × 5 restarts; backbone pinned (`gpt-4-0314` precedent — we pin our own snapshot in `config/llm.yaml`); reward must expose a **component dictionary**; reflection = per-component scalar time series at training checkpoints + fitness; fitness F is separate from reward by design. Human-init helps; evolution beats same-budget sampling.
- **Differential Sharpe (Moody & Saffell):** `D_t = (B_{t-1}ΔA_t − ½A_{t-1}ΔB_t)/(B_{t-1}−A_{t-1}²)^{3/2}`, `A_t=A_{t-1}+ηΔA_t`, `B_t=B_{t-1}+ηΔB_t`, `ΔA_t=R_t−A_{t-1}`, `ΔB_t=R_t²−B_{t-1}` — the canonical hand-designed baseline (η in `config/environment.yaml`).
- **IQN (Dabney et al., 2018):** cosine embedding (64), quantile-Huber κ=1, τ,τ′~U(0,1); CVaR-greedy = sample τ~U[0,α]. d3rlpy 2.8.1: `IQNQFunctionFactory(n_quantiles=64, n_greedy_quantiles=32, embed_size=64)` inside `SACConfig(q_func_factory=...)` — **verified against source, ADR-003**. IQN crossing risk → sort.
- **DSR (Bailey & López de Prado 2014):** `SR0 = √V[SR_n]·[(1−γ)Φ⁻¹(1−1/N) + γΦ⁻¹(1−1/(Ne))]`, γ≈0.5772156649; `DSR = Φ((SR−SR0)√(T−1)/√(1−γ₃SR+((γ₄−1)/4)SR²))`; **unannualised inputs**; γ₄ = raw kurtosis (normal = 3).
- **PBO/CSCV:** S=16 even row-blocks; all C(S,S/2) IS/OOS splits; ω̄ = OOS relative rank of the IS-best; λ=ln(ω̄/(1−ω̄)); PBO = fraction(λ≤0).
- **Costs:** proportional grid {0,5,10,20,50} bps, 0 on cash (DeMiguel et al. 2009 convention); one-way turnover = ½Σ|Δw|.
- **Data integrity:** point-in-time S&P membership (Refinitiv `TR.IndexConstituentRIC` ≥2016; Datastream `LS&PCOMP MMYY` lists 2005–2016); Datastream `RI` total-return datatype; Shumway delisting corrections −30% NYSE/AMEX / −55% Nasdaq; Ince–Porter screens ($1 min prior price; >300% return reversing within a month → missing). Survivorship bias ≈ 0.9–1.4 %/yr (Elton–Gruber–Blake) — the reason PIT matters.
- **Closest prior art:** FinRL-DeepSeek (Benhenda 2025) = LLM **signals** into a hand-written CVaR-PPO. Our contrast sentence: *LLM-as-signal-generator (existing) vs LLM-as-reward-designer (this work).* Use it verbatim when writing.

## 6. Task playbooks

**Add a hand-designed baseline reward.** Implement in `src/rewards_baselines.py` (create if absent) satisfying the contract; cite the original paper in the docstring; register it in `config/eureka_loop.yaml: baseline_rewards`; add a contract test; ADR only if it changes the baseline set in the pre-registration (it does → R1 applies; ask first).

**Touch the environment.** Read `docs/environment_spec_v1.md` first; any state-feature addition must pass the leakage check (R3) and get a spec edit + ADR. Keep the accounting identity test (`tests/test_portfolio_env.py`) green — wealth must equal compounded net returns to 1e-10.

**Extend the feedback schema.** Edit `src/feedback_schema.py` + `docs/distributional_feedback_schema.md` together; new fields need: computation from *sorted* quantiles, a unit test, and a one-line justification tied to the Kusuoka/spectral framing. The serialized block must stay under the token budget in `config/llm.yaml`.

**Run/extend statistics.** Everything flows through `stats_inference.TrialLedger`; if you add an arm, its candidates increment N. Never compute DSR on a hand-picked subset.

**Writing prose (dissertation/brief).** Voice: balanced, bounded, no overselling (the coursework's 5/5 conclusion voice). Every claim carries its evidence pointer (table/figure) in the same sentence. Intuition before mathematics for every design choice — three sentences: what, why right *for this financial problem*, what breaks otherwise.

## 7. Forbidden actions (quick list)

Never: edit frozen `PREREGISTRATION.md` without ADR+flag · modify or delete anything in `data/` · run candidate code outside the sandbox · use smoothed HMM probabilities or unshifted regimes in decisions · feed annualised SRs to DSR · report unsorted-quantile tail stats · add dependencies or scope items silently · train/evaluate across split boundaries · drop seeds to "save time" on reported cells · fabricate placeholder numbers into reports (templates use `⟨TBD⟩`, keep it that way until real values exist).

## 8. Current state & immediate milestones

Implemented + tested in the initial build: feedback schema, DSR/PSR/MinTRL/PBO, fitness, env core accounting, reward contract. Verified: d3rlpy 2.8.1 IQN+SAC API (ADR-003). Awaiting local execution: smoke test (4090), pilot pulls (entitlements), reconciliation. Next milestones mirror `docs/week_plan_June15.md`: freeze pre-registration (T4) → entitlement outcome recorded → env features → sandbox hardening → first hand-designed-reward training run. When the user asks "what next?", answer from that file and the tier system — not by inventing new scope.
