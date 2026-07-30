# Citation-verification TODO (pre-submission reference round)

Generated from the 2026-06-28 deep-research + refs.bib audit. The `% VERIFY` discipline in `paper/refs.bib`
is deliberate and exemplary; this list **prioritises** what must be confirmed first-hand before the PDF, and
**fences off** references that must NOT be cited as confirmed.

## 🔴 RED — confirm first-hand BEFORE the campaign / submission (load-bearing or trust-critical)
| bibkey / ref | Why it is RED | What to confirm |
|---|---|---|
| `patton2019dynamic` | The FZ0 strictly-consistent (VaR, ES) scoring function is used in **production** code (`src/inference/es_backtest.py`) — a wrong formula would invalidate the H2-Tail corroboration backtest. | Obtain the published PDF; confirm Patton, Ziegel & Chen (2019), *J. Econometrics* 211(2):388–413, and the exact FZ0 score form used. |
| `khraishi2022offline` | **Supervisor (Okhrati) co-authored paper** — citation-integrity is trust-critical (no viva; a bad supervisor cite is caught). | Confirm ICAIF 2022 venue + DOI 10.1145/3533271.3561682, author order, first-hand from the ACM record. |
| `agrawal2026gepa` | Future-dated (2026); ICLR-2026-Oral acceptance is aspirational. | Before final submission, set year to the actual arXiv year (2025) unless ICLR 2026 acceptance is confirmed; mark provisional. |
| `kusuoka2001lawinvariant` | Dual published venue (RIMS Kokyuroku 1215 vs Advances in Mathematical Economics 3) — currently ambiguous. | Cite the version actually read; pick one. |

## 🟡 YELLOW — verify coordinates before the PDF (arXiv-to-published lag; not load-bearing)
`rockafellar2000cvar` (J. Risk 2(3):21–41), `coache2024dynamicrisk` (Math. Finance 34(2)), `nolde2017elicitability`
(AoAS 11(4):1833–1874), `bailey2014deflated` (JPM 40(5)), `bailey2017pbo` (J. Comp. Finance 20(4)),
`acerbi2002coherence`, `artzner1999coherent`, `demiguel2009naive`, `buehler2019deephedging`, `haarnoja2018sac`,
`kumar2020cql`, `troop2021biascorrected`, and the ~30 other `% VERIFY`-flagged entries — the standard
pre-submission reference round (do NOT bulk-clear now; confirm each against its primary source).

## 🟢 VERIFIED this session (deep-research, 3-vote) — safe to keep as cited (still `% VERIFY` until on-disk PDF check)
- `fissler2016higherorder` — Annals of Statistics 44(4):1680–1707 (2016); arXiv:1503.08123. **Distinct** from the
  short *Risk* note Fissler-Ziegel-Gneiting (arXiv:1507.00244, Risk Jan 2016 pp.58–61). (`% VERIFY` already cleared.)
- `mcneilfrey2000` — *J. Empirical Finance* 7(3-4):271–300. `belziledavison2022` — *Ann. Appl. Stat.* 16(3).
  `bayerdimitriadis2022` — *J. Fin. Econometrics* 20(3):437–471, doi:10.1093/jjfinec/nbaa013.
- Reframe backbone (verified existence; confirm exact title/vol at PDF time): `rubin2025preregistration`
  (Synthese 2025, arXiv:2408.12347), `gelman2014forking`, `lakens2018tost`
  (AMPPS 1(2):259–269, doi:10.1177/2515245918770963), `campbell2018cet` (PLOS ONE), `mayo2018severetesting`
  (CUP 2018). WS5 method cites: `troop2021biascorrected` (arXiv:2103.05059), Politis-White 2004 (block bootstrap).

## ⛔ DO-NOT-CITE — UNVERIFIED / likely-nonexistent (NONE are in `refs.bib`; keep it that way)
2026-dated arXiv ids surfaced by sweep/agents, beyond the plausibility/verification horizon and **NOT** resolved
by the citation-verify pass (which punted): **2602.09305, 2604.23505, 2602.18053, 2605.08061, 2512.23139,
2605.23007**; SSRN **5950754** ("Lopez de Prado, New Standard" — slides only); Wang & Liu JRFM 2025; Grant et al.
multi-horizon Diebold-Mariano (J. Forecasting 2026). Treat ALL as nonexistent until independently confirmed on
arXiv/SSRN; none may enter `paper/refs.bib`.

## 📄 ON-DISK FILE INTEGRITY — from first-hand P31 PDF extraction (2026-06-28)
First-hand reading of the `01_literature/` PDFs (PyMuPDF + page-image render) surfaced file-vs-content and
preprint-coordinate issues. **Do not cite a published coordinate that is not actually printed in the on-disk PDF.**
| File | Issue | Action before citing |
|---|---|---|
| `H_manual_journal/Maillard-RiskParity__2010.pdf` | ⚠ **MISLABELED** — the file is actually **Cagna & Casuccio, CeRP WP 142/14 (2014)** (an ES-based ERC extension), NOT Maillard-Roncalli-Teiletche. The genuine MRT closed forms (`σ_i = x_i(Σx)_i/√(x'Σx)`, `w_i ∝ 1/σ_i`) are **absent on disk** under this name. | Re-acquire the REAL Maillard, Roncalli & Teiletche paper (JPM 36(4), 2010; working draft 2009) before citing `risk_parity` to it. Until then `risk_parity`'s primary cite is **unsourced first-hand**. |
| `DeMiguel-1overN` (on disk) | 2006 working draft — no journal vol/pages/DOI printed. | Use published RFS 22(5):1915–1953 (2009) coords, sourced separately. |
| `LopezDePrado-HRP` (on disk) | SSRN preprint — no JPM vol/pages. | Use JPM 42(4):59–69 (2016) coords, sourced separately. |
| `RockafellarUryasev-CVaR` (on disk) | 1999 working paper. | Use published J. Risk 2(3):21–41 (2000) coords (already YELLOW above). |
| `FisslerZiegel` (on disk) | arXiv version. | AoS 44(4):1680–1707 (already VERIFIED above). |

**NEW 2026-07-30 — one dangling source found while auditing the H1 canon's provenance (Tamer asked
"where did the 11 human rewards come from, is that verified and legit").** `src/baselines/rewards.py`
attributes `log_growth` to *"Kelly 1956; **Thorp 1971**"*, and **Thorp is in NEITHER `paper/refs.bib`
NOR any chapter** (0 hits in both). Kelly IS present. Impact is bounded — it is a **code docstring**,
not prose, so it cannot produce a dangling key in the submitted PDF — but the attribution is currently
unsourced. **Fix either way before submission:** add Thorp (1971), *"Portfolio Choice and the Kelly
Criterion"*, in Ziemba & Vickson (eds), verified first-hand; or drop the name from the docstring and
let Kelly 1956 carry it alone. Every OTHER member of the canon resolves to a graded, dated-verified
entry (e.g. `chekhlov2005drawdown` — *"Grade A. Source for return_minus_drawdown. VERIFIED
2026-07-26."*).

**VERIFIED first-hand (formula + coordinates, render-confirmed) — safe to cite once published coords above are reconciled:**
Moody & Saffell DSR (Dₜ update Eqs 14–16, IEEE TNN 12(4), 2001) · Markowitz E-V (J. Finance 7(1):77–91, 1952) ·
Rockafellar-Uryasev CVaR auxiliary `F_β` · Jiang EIIE `r=ln(μ_t y_t·w_{t−1})` (arXiv:1706.10059) · DeMiguel
Sharpe/CEQ/turnover protocol · HRP 3-stage algorithm · **Black-Litterman master posterior IS printed in the 1992
FAJ original (App. item 8, p.42)** · rliable IQM/POI/score-distribution · Fissler-Ziegel joint (VaR,ES) score ·
Eureka human-normalized score (83%/52%, K=16×N=5). Full detail: `docs/PAPER_BENCHMARK_EXTRACTIONS.md`.
