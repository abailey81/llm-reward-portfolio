# RUN READINESS — `llm-reward-portfolio` (2026-06-19)

Operational runbook + verified readiness state for executing the experiment. Everything below was
**checked live on this machine** today, not assumed. Read the Status Board, then run the sequence.

---

## 0. Status board

| Area | State | Evidence (verified 2026-06-19) |
|---|---|---|
| **Python env** | ✅ ready | `.venv` Python 3.11.9; full non-slow suite **373 passed / 1 skipped**, order-randomized (pytest-randomly) |
| **LLM wiring** | ✅ ready | Anthropic Sonnet 4.6 wired as Pass-B default; transports prompt-cache + tenacity retry + usage archival + temperature; `tests/test_llm_transport.py` (16) green |
| **Anthropic key** | ✅ set | `ANTHROPIC_API_KEY` present in gitignored `.env` |
| **Refinitiv creds** | ✅ LIVE + entitled | `.env` `REFINITIV_{USERNAME,PASSWORD,APP_KEY}`; headless platform session **OpenState.Opened**; entitlement probe **7 PASS** → *"proceed with the full PIT build"* |
| **FRED key** | ⚠️ empty | `FRED_API_KEY=` — fine for the run (VIX is already in the frozen gold); only needed for a future FRED re-pull (univ4 VIX) |
| **Gold data** | ✅ frozen, real | `data/gold/returns_panel_univ3.parquet` — **licensed Refinitiv, survivorship-free, PIT**: 953 RICs incl. 333 dead, 5,283 trading days 2005-2025 (sha256 `f4edc86…`) |
| **vix units** | ✅ fixed | loader normalizes the gold's fractional VIX → points; regimes 1 → 214 episodes |
| **Configs** | ✅ reconciled | `prototype.yaml` (Pass-A stub default + real model/key/temp), `campaign.yaml` (`llm: pass:B, provider:anthropic, generations:6`), `llm.yaml` |
| **Pre-registration** | ✅ freeze-ready | `freeze.py --check` OK; canonical hash `7e6da01f73811e4e92f8b05643b0222170743badcbf7976b1d6879a3193e41d6`; `freeze_hash: null` (not yet frozen — gated) |
| **End-to-end pipeline** | ✅ runs here | `run_prototype.py --dry-run` → 3 arms × 2 cand × 200 steps, real SAC, winners produced, 18.3s, EXIT 0 |
| **Prototype (full)** | ▶️ ready to run | ~9.1 h on this RTX 4050 (240 cand × 25k steps @ ~183 steps/s, `--parallel`) |
| **Pilot / freeze / univ4 / campaign** | ⏸️ gated on you | GPU rental + your go — see §4–§6 |

---

## 1. The two passes (why the prototype needs no LLM)

- **Pass A (default) — keyless `StubDesignerTransport`.** The 4 LLM arms (distributional, scalar,
  placebo, scalar_cvar5) get reward code from a deterministic seeded stub; the 2 search arms
  (random_search, bayes_opt) never use an LLM. **No key, no cost, instant.** This validates the
  *machinery* (train → rollout → measure tails → select → archive), which is the prototype's only job —
  its numbers are directional and **never enter the dissertation**. The stub does not read the feedback,
  so it cannot test H2/H3 (by design).
- **Pass B — real Claude Sonnet 4.6.** The LLM actually reads each arm's feedback block (tail stats vs.
  scalar) and evolves rewards. **H2 and H3 are only testable here.** Used by the **campaign** (and an
  optional `--pass B` prototype smoke). ~120 calls total, prompt-cached → **~$7 for the whole project**.

---

## 2. RUN — the full prototype on this laptop (Pass A, ~9 h)

```bash
cd llm-reward-portfolio
.venv/Scripts/python.exe scripts/run_prototype.py --parallel
```

- **Work:** 6 arms × 40 candidates × 25,000 SAC steps = 6,000,000 steps.
- **Time:** ~9.1 h at the benchmarked ~183 steps/s aggregate (3 GPU workers; calibrated on this RTX 4050).
  The plain (non-`--parallel`) per-arm path is ~12 h — use `--parallel`.
- **Output:** `outputs/prototype/` — per-arm candidate archives (`write_run` records) + `run_summary.json`.
- **Monitoring:** each arm prints `n_candidates / n_failed / winner_fitness` on completion; tail the
  console or `outputs/prototype/run_summary.json`.
- **Resume:** `resume: true` is on (arm-level) — if it dies or you stop it, re-run the same command and
  it skips arms already marked complete. You won't lose finished arms.
- **Laptop practicalities:** plug in; ensure ventilation (9 h of GPU saturation runs hot); disable
  sleep/hibernate. 3 GPU workers fit the 4050's 6 GB VRAM.
- **Success = ** all 6 arms report `matched=True` (budget enforced: accepted+failed == 40) and a
  `winner_fitness` per arm; `run_summary.json` written.

**Shorter alternatives** (if 9 h is too long for now):
- Smoke (minutes): `.venv/Scripts/python.exe scripts/run_prototype.py --dry-run`  (3 arms × 2 cand × 200, synthetic).
- Quick real run: edit `config/prototype.yaml` `candidates_per_arm`/`train_steps_per_candidate` down
  (e.g. 10 × 10k ≈ 1.5 h), or `--p-arms 3`.

**Optional — smoke-test the REAL LLM wiring** before the campaign (a handful of live Sonnet calls; needs
`ANTHROPIC_API_KEY` + the `anthropic` package installed in the run env):
```bash
.venv/Scripts/python.exe scripts/run_prototype.py --pass B --arms distributional --candidates 2
```

---

## 3. Data — `univ3` is already strong; `univ4` is now unblocked

**`univ3` (the frozen gold) is licensed Refinitiv survivorship-free PIT data** — 953 RICs incl. 333 dead
tickers, PIT membership via reverse event replay, two-vendor reconciliation (corr 0.99994). This is
gold-standard for the study. The single residual quality nuance is the **delisting-return fill**: the env
currently uses a *provisional* `liquidate_to_cash` (0% on delisting) rather than the Shumway −30%/−55%
band — and delisting events sit in the tail H2 cares about.

**`univ4`** = apply the proper Shumway delisting returns (+ tidy the 2005-cohort PIT). The delisting
*metadata* is already in the Refinitiv pull, so this is likely a **re-processing** step, not a fresh
multi-hour re-pull. **Now achievable** — the entitlement probe (2026-06-19) verifies the full Refinitiv
access (delisted coverage P6 ✅, PIT membership P2/P3 ✅). Re-pull path (if needed):
```bash
cd data_pipeline
.../python.exe -m src.data.cli --help     # acquisition stages (build_universe.py + membership.py)
```
(The probe ran in a throwaway venv `D:\tmp\rdp_venv` with `refinitiv-data`; a real build also needs
`DatastreamPy` only if you use the DSWS path — not required, the Refinitiv JL path is used. VIX re-pull
would need a `FRED_API_KEY`.)

**Decision:** run on `univ3` now (defensible, document the delisting caveat), and decide on the `univ4`
delisting upgrade before the campaign — it's the one change that materially firms up the headline tail
result, and you now have the access.

---

## 4. PILOT (gated — your action) — the highest-value next step

A small **real-data** run that (a) proves the pipeline end-to-end on real univ3, (b) measures true
per-candidate GPU cost, and (c) yields the **seed-to-seed σ** that finalizes the power analysis + SESOI.
Run a reduced campaign on real data, then:
```bash
.venv/Scripts/python.exe scripts/power_analysis.py --sigma-dsr <pilot σ>
```
The first real **Pass-B** call also smoke-tests the live Sonnet wiring (transport, prompt-cache,
archiving, parsing) — currently exercised only by fakes.

---

## 5. FREEZE (gated) — the legitimacy gate

After the pilot calibrates σ/λ, run the real freeze (writes the hash, flips `frozen: true`, signs the tag,
OTS-stamps):
```bash
make freeze        # GATED — not run automatically; sets frozen=true + writes freeze_hash 7e6da01f…
```
`freeze.py --check` already passes; the design is byte-consistent and ready.

---

## 6. CAMPAIGN (gated — GPU + key) — the real experiment

```bash
.venv/Scripts/python.exe scripts/run_campaign.py            # Pass B, Sonnet 4.6, per config/campaign.yaml
# smoke first:  scripts/run_campaign.py --dry-run           # 1 LLM arm × 2 cand × 1 seed (stub, no key burn)
```
- **Compute:** rented RTX 4090, ~110 GPU-hr ≈ **$32–44**; LLM ≈ **$7**. `auto_shutdown_on_complete: true`.
- **Protocol:** SEARCH (dev split) → SELECT by validation DSR → FREEZE winner → TEST once on the sealed
  2018-2025 leg, 30 seeds/arm. `resume: true` (idempotent).
- **Then:** `scripts/analyze_campaign.py` → PBO/CSCV + DSR + H2 conjunction (BH q=0.05) → the headline number.

---

## 7. Gated hand-off checklist (your side)

- [ ] Decide `univ3` vs `univ4` delisting fill (raise with supervisor if licensed-data expectation is unclear).
- [ ] Rent the RTX 4090; create `requirements.lock` there (must include the newly-declared `tenacity`).
- [ ] Run the pilot → set `power_analysis --sigma-dsr`; confirm/adjust SESOI=0.05.
- [ ] `make freeze` (after pilot calibration).
- [ ] (Optional) build `univ4` delisting upgrade.
- [ ] Run the campaign → analysis → write up (viva-defense register + H2 theory foundations are the scaffolding).
- [ ] Rotate the Refinitiv password + Anthropic key after the project (both were pasted in chat).

---

## 8. Security note

The Refinitiv password and Anthropic key were pasted into the chat transcript and live in the gitignored
`.env`. They are never logged, committed, or embedded in artifacts (the probe/acquire layer reads them
from `.env` and records only NAMES). **Rotate both after the project.**
