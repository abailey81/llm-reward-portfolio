# Paper-data implementability map — "for each paper, what data, and can we get/use it?"

Fuses the 196-paper deep-dive (per-paper `datasets` field; see `PAPER_DEEPDIVE_TABLE.md` for the row-per-paper
detail and `PAPER_PACKAGES_GITHUB_INDEX.md` for the deduped datasets/packages/GitHub inventory) with the LSEG
licence assessment (`LSEG_DATA_STRATEGY.md`). Every dataset *category* any corpus paper uses is placed in one of
four availability buckets, with a strict relevance verdict. Bucket counts are category-level, not per-paper
(per-paper data is in the deep-dive table).

## ✅ ALREADY-HAVE (in-repo, licensed, wired) — use as-is
| Data category | Papers that use it | Status here |
|---|---|---|
| US large-cap **daily total returns** (survivorship-free PIT) | DeMiguel, Harvey-Liu-Zhu, Bailey/PBO/DSR, Moody-Saffell lineage, most finance-RL | The headline `returns_panel_univ3` (S&P 500, 2005–2025) — the study's data. |
| **Risk-free rate** (T-bill / FRED) | Sharpe/Sortino-using papers | FRED DGS3MO on disk + wired (`market_reference.py`). |
| **Fama-French / market factors** | factor-attribution, BAB, QMJ papers | Ken French factors on disk; FF3 attribution pre-registered. |
| **VIX / volatility level** | regime/vol-target papers | VIX points loaded via the loader (regime conditioner). |

## 🟢 LSEG-ACCESSIBLE under your full licence (deterministic PIT pulls) — the genuine levers
| Data category | Papers that motivate it | Verdict (see LSEG_DATA_STRATEGY tiers) |
|---|---|---|
| **Longer equity history (~1989–)** | EVT small-sample papers (Belzile-Davison, McNeil-Frey, Pickands/Balkema), backtest-overfitting | **★ Tier 1** — more crises → more tail exceedances → robust EVT. Datastream `LS&PCOMP{MMYY}` to 1989; `TR.TotalReturn`. The single best contribution-strengthener. |
| **Other equity markets** (FTSE/STOXX/TOPIX) | external-validity / generalisation critiques | **Tier 1** — `TR.IndexJLConstituent*` + `0#.<RIC>(YYYYMMDD)`; UK/EU high-confidence, JP probe-first. |
| **Multi-asset** (govvy/credit/commodity/FX total-return indices) | distributional/risk-RL papers wanting fatter, heterogeneous tails | **Tier 2** (heavy) — same total-return machinery; per-asset cost calibration needed → likely v2. |
| **Richer regime/factor data** (credit spreads, macro, StarMine factors) | regime-conditional + attribution papers | **Tier 3** — report-only enrichment. |

## 🔴 UNAVAILABLE-to-us / SCOPE-CREEP — rejected on relevance + design-integrity (NOT "frozen")
| Data category | Papers that use it | Why rejected |
|---|---|---|
| **News / sentiment / NLP text** (FinBERT, FinGPT, FinMem, PIXIU, FinRL-DeepSeek signal layer) | LLM-trading-signal papers | Breaks the deliberate **anonymised-returns** reward design (clean causal attribution) + leakage risk. Separate paper. |
| **Intraday / tick / LOB** | HFT / market-microstructure RL | Granularity mismatch (this study is daily). |
| **Options / implied-vol surface** | hedging-RL papers | Turns the allocator into an options trader — different problem/agent. |
| **Proprietary alt-data** (supply-chain, satellite, ownership, patents) | alt-data alpha papers | No mechanism to the tail-risk reward-design question. |

## 🟡 PUBLIC / FUTURE-WORK (freely available, beyond the current design)
Benchmark RL suites (Atari/MuJoCo/Isaac — robotics reward-design papers), other public finance datasets
(CRSP/WRDS-equivalent — we have the LSEG analogue), crypto (BTCUSD in some evolve-trading papers). All
out-of-scope for the frozen-contribution timeline; FUTURE-WORK only.

## Net read
The deep-dive's honest verdict holds at the data level too: **most papers' data is either something we already
have (US equity returns + rf + factors + VIX) or something we deliberately exclude (text/intraday/options/
alt-data).** The *only* data that both helps and is reachable under your licence is the **LSEG-ACCESSIBLE** bucket
— and within it the ranking is exactly the LSEG strategy's: **extend history (Tier 1) > multi-market (Tier 1) >
multi-asset (Tier 2) > regime/factor enrichment (Tier 3)**. No paper's dataset justifies a scope change beyond
those; the alt-data/text/intraday categories are correctly rejected on design-integrity and granularity, not on
"frozen".
