# CAMPAIGN — FREEZE DECISION BRIEF (3 decisions to record at freeze)

**For:** Tamer Atesyakar · **Compiled:** 2026-06-24 · **Status:** decision brief — NOT dissertation prose.
**Repo:** `c:\Users\User\Desktop\dissertation_papers\llm-reward-portfolio`

> **⚠ SUPERSEDED 2026-07-01 (ADR-040):** "DECISION 3 — rent the RTX 4090" below is **reversed**. The campaign runs
> **laptop-only on the owned RTX 4050** (~2–3 weeks; no cloud — LSEG licence; WSL2/GPU probed + rejected). Decisions
> 1–2 in this brief stand; Decision 3's recommendation does not. Current plan: ADR-040 + `CAMPAIGN_DESIGN_AND_EXECUTION_PLAN.md`.

> **Where we are.** The pre-registration is freeze-ready: `python scripts/freeze.py --check` is GREEN
> (prose↔YAML consistency on seeds, the m=6 family, SESOI/TOST, cost grid, **and** the three 2026-06-24
> amendments R21/R22/R23). The `--check` gate already *asserts the conservative value of all three decisions
> below* — `fitness.lambda_cvar == 0.0` (R22), `agent_numerics.tf32 is true` (R23), and a non-empty
> `search.reflect_protocol_default` (R21) — see `scripts/freeze.py:347-373`. So freezing **today** bakes in
> the conservative branch of each. These three decisions are therefore not "blockers"; they are **affirmative
> ratifications** the user must consciously make and date, because each touches a frozen quantity and one of
> them (λ) is still flagged **PROPOSED**. This brief lays out each trade-off, states what a null vs a positive
> H2 result *means* under each branch, and recommends.

> **One framing that governs all three.** The dissertation is **graded on the PDF alone, no viva**
> (memory: NO-VIVA grade strategy). A **pre-registered null is bankable** (PREREGISTRATION §10 R12 SESOI/TOST).
> The dominant grade lever is therefore *credibility + self-disclosed rigour*, not a positive H2. Every
> recommendation below is biased toward **the cleanest, most defensible, most reproducible branch**, because
> that is what the marking rewards — even where it lowers the probability of a "significant" H2.

---

## DECISION 1 — λ (the selection penalty): **λ = 0** vs **λ > 0 calibrated**

### What is actually being decided
The winner of each arm is selected on **validation Deflated Sharpe** (`held_out_fitness`, `src/selection/fitness.py`).
The pre-registration permits an optional `−λ·|validation-CVaR(5%)|` term (PREREGISTRATION §5). The question is
the value of `λ`:

- **λ = 0 (PROPOSED, R22):** selection is **pure validation-DSR**, tail-blind. Verified first-hand: `held_out_fitness`
  takes `lam: float = 0.0` as its **default** and short-circuits `if lam == 0.0: return float(dsr)`
  (`fitness.py:33, 91-92`) — the CVaR-penalty branch is **never entered** on the live path. The
  `lambda_grid: [0,1,2,5,10]` / `lambda_frozen: null` / `calibration_fold` scaffolding in
  `config/inference.yaml:16-20` is **read by no live code** (confirmed) and `lambda_frozen` was **never calibrated**.
- **λ > 0 calibrated:** would require (i) a real pre-2015 calibration on the reserved
  `calibration_fold: train 2005-2012 / val 2013-2014` to pick one λ from the grid, (ii) wiring that λ into the
  selection hot path, and (iii) an ADR justifying the chosen value. None of this exists today.

### The trade-off (sharpened by the research the user authorised)

The decisive issue is **circular analysis / "double dipping"** — a result statistic is optimistically biased
unless it is **independent of the selection criterion under the null** (Kriegeskorte et al. 2009; Cawley &
Talbot, JMLR 2010, on selection-induced "optimism").

- **H2's tail legs test a CVaR difference** (family members #2/#4/#6, `cvar @ 0.05`; PREREGISTRATION §10 R13).
- **λ = 0** keeps the selection criterion (DSR) and the tested statistic (test-leg CVaR) **structurally
  decoupled**: the winner is picked for risk-adjusted *mean* performance and the tail emerges *downstream* on
  the **sealed** test leg, measured by an independent off-critic estimator. The CVaR legs are clean.
- **λ > 0** folds **validation-CVaR into the selection objective**. The tail metric you then *test* is now
  *correlated with the thing you selected on*. Even with the train/val/test split firewall, you have
  **engineered the selection objective to prefer the property H2 claims to find** — exactly the configuration
  the double-dipping literature flags as optimistically biased. A positive CVaR leg under λ>0 is **confounded**:
  "did the distributional *feedback* shape the tail, or did the tail-penalised *selection rule* hand the
  distributional arm its win by construction?" That is unrecoverable from the data alone.

  Note the asymmetry, already documented in **L13(a)**: the bias-against-H2 of λ=0 is **specific to the
  CVaR/tail legs**; for the **Sharpe-gated headline conjunction** (the three Sharpe legs are the gate, R13),
  λ=0 is **neutral** — DSR *is* the right selection objective for a Sharpe-based gate. So λ=0 costs H2 nothing
  on its primary gate and only makes the *secondary* CVaR legs harder — the right direction for credibility.

- **The cost of λ = 0 (state it honestly):** the selection objective does **not** reward the tail, so a
  candidate that sacrifices DSR to improve its tail can be **passed over** — this **biases the CVaR legs
  AGAINST H2** (a true tail-improving feedback effect is *harder* to detect). The directional prototype already
  shows the symptom: scalar leads on DSR-winner-fitness (0.110 vs 0.060) while distributional wins on CVaR
  (p≈0.004) (memory; L13). This is a **conservative** bias, not a confound — it makes a *positive* tail result
  *more* credible and a *null* a clean ceiling statement, which is precisely what a no-viva, pre-registered
  design wants.

- **The (weak) case for λ > 0:** it is the only branch under which the selection rule actively *rewards*
  tail-shape, so it would **raise the probability of a positive CVaR leg**. But (a) that gain is precisely the
  optimistic bias above — it inflates H2 rather than testing it; (b) it requires a calibration that does not
  exist and that the CVaR-penalty literature shows is itself a non-trivial, contestable choice (λ trades
  return for tail with no canonical value — the surveyed mean-CVaR work tunes λ per problem with no agreed
  default); (c) it makes the headline **less clean** ("you tuned selection toward your hypothesis") for a
  co-author supervisor who knows the backtest-overfitting literature; (d) it is **less Eureka-faithful** —
  Eureka selects on a single holistic fitness, not a metric-aligned multi-objective.

### What each implies for the H2 *result*
| | **λ = 0 (recommend)** | **λ > 0 calibrated** |
|---|---|---|
| Positive CVaR leg means | "the **feedback channel** shaped the tail through DSR-optimal rewards" — clean causal attribution to H2's actual treatment | "the tail improved" — **confounded** with the tail-penalised selection rule; weak attribution |
| Null CVaR leg means | a clean, bankable ceiling on the feedback channel (the conservative bias is disclosed → a null is *informative*, null condition (3) in the theory spine) | ambiguous: weak feedback **or** mis-calibrated λ |
| Sharpe gate (headline) | **unaffected** (DSR is the correct objective for a Sharpe gate) | unaffected, but the whole selection now carries a tuning story |
| Reproducibility / cleanliness | maximal; one fewer free parameter; deletes dead config | adds a calibrated free parameter + an ADR + a calibration run |
| Examiner read | "principled, conservative, biased-against-its-own-hypothesis" = rigour | "selection engineered toward the hypothesis" = a probe target |

### RECOMMENDATION — **ratify λ = 0.**
It is the Eureka-faithful, reward-independent, un-reward-hackable choice; it keeps the H2 CVaR legs free of
circular bias; it biases *against* H2 on exactly the legs where that buys credibility; it is neutral on the
Sharpe gate; and it removes a free parameter and dead config. The one real cost — the selection rule does not
reward the tail — is a *feature* for a pre-registered, null-bankable, no-viva design, and is already written up
as **L13(c)** ready for the Discussion. The λ>0 branch buys a higher *probability* of a positive tail leg only
by *inflating* it, which is worth nothing (arguably negative) under PDF-only marking.

### EXACTLY what to set + the dated ratification
1. **Config (already correct — confirm, don't change):** `config/preregistration.yaml: fitness.lambda_cvar: 0.0`.
2. **Delete the inert scaffolding** (R22 says "deleted at freeze IF ratified"): remove
   `lambda_grid`, `lambda_frozen`, `calibration_fold` from `config/inference.yaml:18-20` (keep `fitness.alpha: 0.05`,
   which the `lam≠0` guard path and the CVaR-difference test still read). Leave `held_out_fitness` as-is.
3. **Flip the prose flag PROPOSED → ratified** in PREREGISTRATION §5 (the 2026-06-24 amendment block) and in
   the amendment-record row R22, with the dated line:
   > *λ = 0 RATIFIED 2026-06-24 (T. Atesyakar). Selection is pure validation-Deflated-Sharpe; no CVaR penalty.
   > The never-calibrated lambda_grid/lambda_frozen/calibration_fold are deleted from config/inference.yaml.
   > Rationale: keeps the H2 tail legs independent of the selection criterion (no circular/double-dipping bias);
   > biases conservatively against the tail legs; Eureka-faithful. The rejected alternative (a pre-2015-calibrated
   > λ>0) is recorded.*
4. Re-run `python scripts/freeze.py --check` → must stay GREEN (the gate already asserts `lambda_cvar==0.0`).

---

## DECISION 2 — Headline reflection protocol: **serial reflect-on-last** vs **parallel reflect-on-best**

### What is actually being decided (R21)
Which SEARCH protocol produces the **headline** frozen winners. The choice changes the *reflection prompt
sequence* — a frozen-decision item — so it is recorded at freeze and **not** silently switched
(`config/preregistration.yaml: search.headline_reflect_protocol: record_at_freeze`).

- **Serial reflect-on-last** (`src/llm/loop.py`; `run_campaign.py --search-gpu 0`, the **default**): seeds the
  next generation's reflection from the generation's **LAST** candidate. **This is the path the completed
  Sonnet prototype de-risked end-to-end** (6 arms, ran to completion; memory: prototype COMPLETE).
- **Parallel reflect-on-best** (`run_campaign.py --search-gpu N>0`; built + unit-tested 2026-06-24,
  `tests/test_run_campaign.py`): trains candidates within a generation (and across arms) concurrently and seeds
  reflection from the generation's **BEST** candidate (Eureka Alg.1 line-9-faithful). It is **~Nx faster on the
  search half** and folds in a **secondary fix**: it couples `buffer_size == train_steps = 50k`, matching the
  TEST leg, whereas the serial path inherits the prototype's pinned **25k** buffer (this is the **L14**
  select-vs-evaluate asymmetry).

### The trade-off
| | **Serial reflect-on-last** | **Parallel reflect-on-best** |
|---|---|---|
| De-risked? | **Yes — the prototype ran this exact path to completion.** Lowest execution risk before the deadline. | Built + unit-tested, but **never run at campaign scale**. Some residual execution risk. |
| Eureka faithfulness | Reflects on *last* (a deviation from Eureka, which reflects on best-so-far). | **Faithful** to Eureka Alg.1 (reflect on best). |
| Speed (search half) | 1× | ~Nx (the search half is ~half the campaign; see Decision 3 timing). |
| Replay buffer at search | **25k** (≠ test's 50k) → the **L14 asymmetry**: winners *selected* under 25k, *evaluated* under 50k. | **50k** (== test) → **resolves L14**. |
| `feedback_block` archival | Populated (`loop.py` writes both fields). | Leaves `feedback_block` empty, fed feedback in `prompt` (the **L12** housekeeping note; the responsiveness gate reads *both*, so no result risk). |
| H2 confound? | No — symmetric across all arms. | No — symmetric across all arms (Door A; the protocol is identical for every arm). |
| SELECT/FREEZE/TEST schema | Unchanged. | Unchanged (writes the same `val_fitness`/`val_returns` the selector reads). |

Two things are **not** in tension: whichever is headline, the *other* is the natural **robustness/sensitivity
companion** (a "headline protocol vs alternative protocol" exhibit on the two headline arms strengthens the PDF
either way). And the L14/L12 items are *disclosed* in the LIMITATIONS_REGISTER regardless of choice — the only
question is which one the *headline* inherits.

### The genuine tension
This is a **reproducibility-and-de-risking vs faithfulness-and-cleanliness** call:

- **Serial** is the *safest* path to a completed campaign before the deadline (it is the only path proven to run
  to completion), but it ships the **L14 25k/50k buffer asymmetry** into the headline (a real, if minor,
  select-vs-evaluate inconsistency an RL-attentive examiner will note).
- **Parallel** is *Eureka-faithful* and *resolves L14 at the headline* and is *much faster* — but its only
  proof is unit tests, so choosing it for the headline bets the campaign on an unexercised scale path.

### RECOMMENDATION — **declare PARALLEL reflect-on-best the headline, with a guard.**
Rationale, in order of weight for a PDF-graded thesis:
1. **It removes a documented headline limitation (L14) instead of shipping it.** "Winners selected under a
   different replay budget than they're evaluated under" is the kind of crisp, citable inconsistency that costs
   credibility; the parallel path *matches buffer to budget* and makes L14 a *resolved-in-the-headline* note
   rather than a live caveat. This is the single strongest reason.
2. **It is Eureka-faithful.** The dissertation's framing leans on the Eureka lineage; reflecting on *best*
   (not *last*) is what Eureka does, so the headline matching Eureka is a cleaner methods story.
3. **Speed compounds with Decision 3** (it is the lever that makes the rented-4090 ~5h plausible on the search
   half), and it is **symmetric across arms**, so it is *not* an H2 confound.

**The guard that neutralises the execution risk** (this is what makes the recommendation safe, not reckless):
- The serial path is **already de-risked and remains the default** (`--search-gpu 0`). Treat it as the
  **fallback**: if the parallel campaign hits any scale problem, fall back to serial **and** the L14 asymmetry
  is then a disclosed limitation (already drafted as L14(c)) — no re-pre-registration needed, because *both*
  protocols are pre-registered and the choice is *recorded*, not hidden.
- Run a **short parallel smoke first** (a few candidates, `--search-gpu N`, GPU-smoke is already shown feasible
  at `n_gpu=4`; memory: parallel engine PROVEN, equivalence == serial byte-identical on the test leg). Only
  commit the headline to parallel **after** that smoke is GREEN on the rented box.
- One-line clean-up worth doing regardless (L12): populate `feedback_block` on the parallel path so the
  released archive is tidy.

> **If the user is deadline-risk-averse:** declaring **serial** the headline is fully defensible and maximally
> de-risked — it is the proven path — at the cost of shipping L14 in the headline. Both are pre-registered;
> this is a genuine judgement call. The brief's recommendation (parallel + guard) optimises the *PDF* (resolves
> L14, Eureka-faithful) while the fallback keeps the *deadline* safe. Either way: **record the choice explicitly
> at freeze** in `search.headline_reflect_protocol`.

### Reproducibility implication (state in the PDF either way)
Reproducibility is **replay-from-archive** (CLAUDE.md directive 6; L9), not regeneration — *independent* of which
protocol is headline (both write the same archive schema the analysis replays). The serial path's *additional*
asset is that it is the **prototype-exercised** path; the parallel path's asset is **buffer/Eureka fidelity**.
Whichever is headline, name the other as the pre-registered alternative and (ideally) show the robustness exhibit.

### EXACTLY what to set + the dated ratification
1. **`config/preregistration.yaml: search.headline_reflect_protocol`** — change `record_at_freeze` to the chosen
   value: `best_of_generation` (recommended) **or** `serial_reflect_on_last` (fallback choice).
2. Add the dated decision to PREREGISTRATION §6 (the R21 amendment block) + amendment-record row R21, e.g.:
   > *Headline reflection protocol RECORDED 2026-06-24 (T. Atesyakar): parallel reflect-on-best
   > (`--search-gpu N`, buffer==train_steps==50k, Eureka-Alg.1-faithful), CONDITIONAL on a GREEN parallel
   > GPU-smoke on the rented 4090; serial reflect-on-last (`--search-gpu 0`, prototype-de-risked) is the
   > pre-registered fallback and is invoked — with L14 disclosed — if the parallel campaign fails at scale.*
3. Re-run `freeze.py --check` (the gate only requires `reflect_protocol_default` to be **set**, which it is;
   confirm GREEN).

---

## DECISION 3 — Platform: **maxed laptop (~27h, free)** vs **rented RTX 4090 (~5h, ~$15)**

### The trade-off (numbers from `docs/COMPUTE_AND_TRAINING_TIME.md`, with the caveat below)
| | **Maxed laptop (RTX 4050, owned)** | **Rented RTX 4090 (RunPod/Vast)** |
|---|---|---|
| Cost | **$0** | **~$15** *(see caveat)* |
| Wall-clock | the prompt's **~27h** figure | the prompt's **~5h** figure |
| `m` (min / 50k run) | ~12–25 (central ~18) | ~10–12 |
| Sandbox containment | **POSIX RLIMITs are a no-op on Windows** — only the wall-clock timeout backstops; `signal.SIGALRM` was a Windows no-op too (L4; closed by the killable-child design, ADR-028). | **RLIMIT_AS/CPU/NOFILE/FSIZE actually enforced** (Linux); the killable child contains an allocation bomb at validation (L4(c)). |
| Parallel recycling | serial; ties up the laptop (heat/throttle) | **recycling/parallel TEST-leg works natively** (memory: parallel engine PROVEN; `n_gpu=4` feasible). |
| Reproducibility | identical (replay-from-archive); but `m` is laptop-throttle-dependent | identical; clean, frozen-config-driven, **the pre-registered campaign venue** |

> **Numbers caveat (be precise — do not overstate the laptop).** The repo's *authoritative* compute doc gives
> the **lean campaign** (≈600 winner-equivalent runs after amendment D2 raised winners to 30 seeds) as
> **~110 GPU-hr ≈ ~$32-44 / ~4.6 days on ONE rented 4090**, or **~7.5 days on the laptop**
> (`COMPUTE_AND_TRAINING_TIME.md §3-5`). The prompt's **~5h / ~27h / ~$15** figures correspond to a **smaller
> slice** (closer to the *pre-D2* ~205-run lean path, ~38 GPU-hr ≈ $13-16, or a search-only / reduced-seed
> cut) — **or** to a *parallel* rented run (~half a day across several GPUs at the same total $). **The
> platform recommendation does not depend on which figure is right** (4090 wins on every axis), but **record
> the campaign's actual run-count and the resulting hours/cost at freeze from `COMPUTE_AND_TRAINING_TIME.md`,
> not the round numbers in the brief** — Phase-0's measured `m` collapses the bands to exact figures, and the
> DSR trial count the freeze locks is the *search* run-count, so the number must be the real one.

### The decisive non-cost factors
1. **Containment is a real difference, not cosmetic.** On Windows the resource caps silently no-op (L4(a)),
   so the laptop runs LLM-authored code with **only a wall-clock backstop**. On the Linux 4090 the killable
   child enforces `RLIMIT_AS/CPU/NOFILE/FSIZE` and an allocation-proportional bomb **surfaces at validation,
   not during a training run** (L4(c)). The rewards are LLM-authored arithmetic on anonymised arrays, not an
   adversary — so this is an **engineering-harness** point, not a validity threat — but the *campaign* should
   still run where the layered defence is **actually enforced**, and the LIMITATIONS register's own mitigation
   sentence *promises* the campaign runs on the Linux box (L4(c)). Choosing the laptop would **contradict a
   written mitigation** the dissertation relies on.
2. **The 4090 is the pre-registered venue** (PREREGISTRATION §12 / ADR-023). Running the campaign on the laptop
   would be a deviation requiring its own ADR; running on the 4090 is simply executing the frozen plan.
3. **Parallel recycling works natively on the rented box** (memory: parallel campaign engine PROVEN,
   equivalence-proven byte-identical to serial) — this is what makes Decision 2's parallel-search and the short
   wall-clock achievable together.
4. **Cost is trivial** relative to the dissertation's stakes — single-digit-to-low-tens of dollars against an
   MSc grade. The laptop's only genuine advantage is "$0", and it is dominated.

### RECOMMENDATION — **rent the RTX 4090.**
It is the pre-registered venue, it is where the sandbox RLIMITs are *actually* enforced (honouring the L4
mitigation the thesis cites), it is where parallel recycling works natively (enabling Decision 2 + the short
wall-clock), and the cost is negligible. Keep the **laptop as the Phase-0 / dev / fallback** machine (it already
ran the prototype; `smoke_test.py` measures `m` there first). Use **spot/interruptible + auto-shutdown +
`run_campaign.py --resume`** so an interruption is harmless and you never pay idle (`COMPUTE_AND_TRAINING_TIME.md §5`).

### EXACTLY what to set + the dated ratification
- **No frozen-config change** — §12/ADR-023 already specifies the rented 4090; this is *confirming* the plan,
  not amending it. Record in the freeze note: *"Campaign venue confirmed: rented RTX 4090 (RunPod/Vast), spot +
  auto-shutdown + --resume; laptop RTX 4050 = Phase-0/dev/fallback (ADR-023). Actual run-count, GPU-hours and
  cost recorded from COMPUTE_AND_TRAINING_TIME.md after Phase-0 fixes m."*
- If, and only if, the ~$15-44 is genuinely unavailable: the **stacked-free** fallback
  (Kaggle 30h/wk + Lightning ~80h/mo + Colab + laptop overnight → the lean run in ~3-4 weeks, $0, with
  checkpointing) is the documented free path (`COMPUTE_AND_TRAINING_TIME.md §4`) — but it costs **weeks** of
  calendar and does **not** give native parallel recycling, so it is a true last resort.

---

## TO FREEZE — do X, Y, Z (one-page action list)

> Do these in order from the repo root. Steps 1-3 are the three decisions; 4-8 are the mechanical freeze
> (`docs/FREEZE_RUNBOOK.md`). **The agent must not run the write path — `make freeze` / `freeze.py` (no
> `--check`) is the USER's act.**

1. **λ = 0 — RATIFY (Decision 1).**
   - Confirm `config/preregistration.yaml: fitness.lambda_cvar: 0.0` (already set).
   - **Delete** `lambda_grid`, `lambda_frozen`, `calibration_fold` from `config/inference.yaml:18-20`
     (keep `fitness.alpha: 0.05`).
   - In `PREREGISTRATION.md` §5 + amendment row R22: change **PROPOSED → RATIFIED 2026-06-24** with the
     rationale line in Decision 1.

2. **Headline reflection protocol — RECORD (Decision 2).**
   - Set `config/preregistration.yaml: search.headline_reflect_protocol` to `best_of_generation`
     (recommended, **conditional on a GREEN parallel GPU-smoke**) or `serial_reflect_on_last` (de-risked fallback).
   - Record the dated choice + the serial fallback in `PREREGISTRATION.md` §6 / amendment row R21.
   - (Recommended) one-line clean-up: populate `feedback_block` on the parallel path (L12).

3. **Platform — CONFIRM (Decision 3).**
   - No config change (already in §12/ADR-023). Record the rented-4090 confirmation + laptop-as-fallback +
     spot/auto-shutdown/`--resume` in the freeze note, and commit to recording the **real** run-count/GPU-hours/cost
     from `COMPUTE_AND_TRAINING_TIME.md` once Phase-0 fixes `m`.

4. **Re-verify the gate:** `python scripts/freeze.py --check` → **must be GREEN** (it asserts λ=0, tf32=true,
   reflect-default set; deleting the inert λ keys does not touch the hashed `preregistration.yaml`, but note the
   `config/inference.yaml` edit **does** change the freeze hash, since inference.yaml is a `_BOUND_CONFIG` —
   that is correct and intended).

5. **Review the diff:** `git diff PREREGISTRATION.md config/`.

6. **Gate tests:** `make test` (green before the freeze commit).

7. **Freeze (USER runs this):** `git add PREREGISTRATION.md config/ && git commit -m "Freeze pre-registration v1.0"`
   then `make freeze` (prints the SHA-256 + date).

8. **Record + notify:** paste the hash into the `DECISIONS.md` freeze ADR (heading → `FROZEN <date>`), commit,
   and send the supervisor the freeze notification (`FREEZE_RUNBOOK.md` step 8).

---

### Sources (external research used only to sharpen the λ trade-off)
- Kriegeskorte et al. 2009 — circular analysis / "double dipping": a result is biased unless independent of the
  selection criterion under the null: <https://pmc.ncbi.nlm.nih.gov/articles/PMC2841687/>
- Cawley & Talbot 2010 (JMLR) — over-fitting in model selection / optimistic "optimism" bias:
  <https://www.jmlr.org/papers/volume11/cawley10a/cawley10a.pdf>
- Raschka 2016 — selection-on-test-metric optimistic bias (tutorial corroboration):
  <https://sebastianraschka.com/blog/2016/model-evaluation-selection-part1.html>
- Eureka (OpenReview / project page) — single holistic fitness, not a metric-aligned multi-objective (supports
  the λ=0 = "Eureka-faithful" framing): <https://openreview.net/forum?id=IEduRUO55F> ·
  <https://eureka-research.github.io/>
- CVaR-penalty calibration (no canonical λ; tuned per problem) — confirms λ>0 needs a real, contestable
  calibration: <https://arxiv.org/pdf/2402.11999>

*(All repo claims — `held_out_fitness` λ=0 default, the inert inference.yaml scaffolding, the `freeze.py --check`
assertions, the compute bands — were verified first-hand in the files cited inline.)*
