"""Builder for ``notebooks/results_walkthrough.ipynb`` — the examiner-facing analysis walkthrough.

The notebook is a GENERATED artifact (deterministic, clean, byte-stable — see
``scripts/notebook_builder.py``); this script is its single source of truth. Regenerate with::

    python scripts/build_notebook_results.py

Section map (what the notebook demonstrates, in order):
  0  setup                       repo-root resolution, house style, analysis-only stack
  1  provenance & freeze state   live gold suffix + prereg freeze flags (pre-freeze: frozen=false)
  2  the data (Split C / univ5)  REAL panel header facts + two point-in-time top-30 books + design
  3  EDA (F3)                    stylised facts recomputed LIVE on the real train window
  4  the fed channel             the real four-level CVaR profile + the numeracy bottleneck
  5  analysis bundle             synthetic-NULL demo data (swap for the sealed-leg loader post-run)
  6  headline H2                 TOST/IUT equivalence-first readout + the three headline figures
  7  reward-program taxonomy     REAL prototype-archive kinds table (discriminative validity)
  8  mechanism kernel            SQ1/SQ2/SQ3 instruments on seeded synthetic nulls + figures
  9  robustness                  what the confirmatory run adds
  10 honest limitations
  11 figure manifest             regeneration commands + entry points

Real-data cells only READ frozen artifacts (parquet/JSON); nothing is trained, pulled, or written.
Deterministic: double-build byte-identity is asserted at the end of ``main``.
"""

from __future__ import annotations

from pathlib import Path

from notebook_builder import build_notebook, code, md, sha256_bytes, write_notebook

_REPO = Path(__file__).resolve().parents[1]
_OUT = _REPO / "notebooks" / "results_walkthrough.ipynb"


def cells() -> list[dict]:
    """The notebook, cell by cell (markdown narration first, then the code it explains)."""
    out: list[dict] = []

    # ------------------------------------------------------------------ title + status
    out.append(md(
        "# Results Walkthrough — *Does showing a language model the downside change the reward "
        "code it writes?*\n"
        "\n"
        "**A reproducible, end-to-end analysis of the LLM-reward-design experiment.**\n"
        "\n"
        "An LLM authors the *reward-function code* for a fixed risk-sensitive deep-RL portfolio "
        "agent (SB3 SAC) trading the point-in-time top-30 of a survivorship-free S&P 500 panel. "
        "Across arms we vary **only the feedback channel** — a multi-level **left-tail vector** "
        "(six coordinates) versus a **scalar** performance number — and ask whether the richer "
        "signal produces better risk-adjusted, tail-aware policies. The pre-registered prediction "
        "is a **bounded null**, reported not as a failure but as a **mechanism boundary "
        "condition**: the headline is the *mechanism* — fed signal → authored code → policy → "
        "realised tail — and a null **locates where the chain breaks**.\n"
        "\n"
        "> **Status.** The confirmatory campaign is unrun, so every *inferential* number below is "
        "rendered on a **synthetic NULL-shaped demo** (`make_figures.synthesize_null`) that "
        "exercises the real analysis engine. *No inferential number here is a result.* The data, "
        "EDA, and taxonomy sections **are real** (frozen gold panel + the prototype reward "
        "archive). Post-campaign, replace the one `synthesize_null(...)` call with the sealed-leg "
        "loader and every cell re-runs **identically** — the notebook is the analysis contract."
    ))

    # ------------------------------------------------------------------ reproducibility contract
    out.append(md(
        "## Reproducibility contract\n"
        "\n"
        "- **This notebook is generated.** `scripts/build_notebook_results.py` authors every cell "
        "deterministically (fixed cell ids, no timestamps); the shipped copy stores **no outputs**. "
        "Regenerate with `python scripts/build_notebook_results.py`; validate by executing "
        "top-to-bottom (`jupyter nbconvert --to notebook --execute`).\n"
        "- **Determinism.** Every stochastic cell below draws from an explicitly seeded "
        "`numpy` generator, so re-execution replays byte-identically. LLM calls are "
        "**non-deterministic and are replayed from the archive**, never regenerated (hosted "
        "frontier APIs removed `temperature`/`seed`).\n"
        "- **Provenance.** The design is pinned by `scripts/freeze.py` (SHA-256 over the prereg + "
        "prompts + `arms.yaml` + the inference family + `config/data.yaml`, which binds the PANEL "
        "identity); §1 prints the live freeze state, and the companion "
        "`data_provenance_walkthrough.ipynb` re-verifies the data artifacts hash-by-hash.\n"
        "- **Honest nulls.** Equivalence is read off **TOST vs the ±SESOI band** and **Bayes "
        "factors / a Model Confidence Set** — never off a bare *p* > 0.05."
    ))

    # ------------------------------------------------------------------ 0 setup
    out.append(md("## 0 · Setup"))
    out.append(code(
        "import sys, platform\n"
        "from pathlib import Path\n"
        "import numpy as np\n"
        "import pandas as pd\n"
        "\n"
        "# Resolve the repo root whether the notebook is opened from notebooks/ or the repo root.\n"
        "ROOT = Path.cwd()\n"
        "if not (ROOT / 'src').exists() and (ROOT.parent / 'src').exists():\n"
        "    ROOT = ROOT.parent\n"
        "for p in (str(ROOT), str(ROOT / 'scripts')):\n"
        "    if p not in sys.path:\n"
        "        sys.path.insert(0, p)\n"
        "\n"
        "import matplotlib.pyplot as plt  # noqa: F401  (inline rendering; headless runs use Agg)\n"
        "from src.viz.style import apply_house_style\n"
        "apply_house_style()\n"
        "\n"
        "RNG_SEED = 7\n"
        "# Analysis-only stack ON PURPOSE: no torch / SB3 / CUDA is imported anywhere in this\n"
        "# notebook — it reads frozen artifacts and runs seeded CPU statistics, so it can never\n"
        "# contend with (or depend on) a live training run.\n"
        "print('repo root :', ROOT)\n"
        "print('python    :', platform.python_version())\n"
        "print('numpy     :', np.__version__)\n"
        "print('pandas    :', pd.__version__)"
    ))

    # ------------------------------------------------------------------ 1 provenance
    out.append(md(
        "## 1 · Provenance & freeze state\n"
        "\n"
        "What pins this analysis. Two facts are printed live rather than asserted from memory:\n"
        "\n"
        "1. **The panel identity.** `src.data.loaders.gold_suffix()` resolves the active gold "
        "suffix from `config/data.yaml` (`gold.suffix`), which is **bound into the freeze hash** — "
        "the headline panel cannot be swapped silently. The active panel is `univ5` "
        "(Split C, ADR-044/051).\n"
        "2. **The freeze state.** A frozen design (a non-null `freeze_hash`) is what licenses "
        "confirmatory claims; before the freeze this cell reports `frozen: False` — **by design**, "
        "and every claim in this notebook stays methodological until it flips."
    ))
    out.append(code(
        "import yaml\n"
        "from src.data.loaders import gold_suffix\n"
        "\n"
        "suffix = gold_suffix()\n"
        "assert suffix == 'univ5', f'active gold suffix is {suffix!r}, expected univ5 (Split C)'\n"
        "prereg = yaml.safe_load((ROOT / 'config' / 'preregistration.yaml')"
        ".read_text(encoding='utf-8'))\n"
        "arms = list(prereg['arms'])\n"
        "assert len(arms) == 7, f'expected the 7-arm frozen roster, found {len(arms)}'\n"
        "prov = {\n"
        "    'gold suffix (hash-bound)': suffix,\n"
        "    'frozen': prereg.get('frozen'),\n"
        "    'freeze_hash': prereg.get('freeze_hash'),\n"
        "    'arms (n=7)': ', '.join(arms),\n"
        "}\n"
        "for k, v in prov.items():\n"
        "    print(f'{k:>25} : {v}')"
    ))

    # ------------------------------------------------------------------ 2 the data
    out.append(md(
        "## 2 · The data — Split C on the `univ5` panel\n"
        "\n"
        "**Why this panel.** The gold panel is a licensed Refinitiv/LSEG build: survivorship-free, "
        "point-in-time S&P 500 membership reconstructed by reverse event replay, daily **total** "
        "returns (dividends and terminal delisting returns included), 2005-01-03 → 2026-06-30. "
        "Dead names stay in the panel (Wachovia, Lehman-era casualties, Dell's 2013 take-private "
        "…) — dropping them would manufacture exactly the survivorship bias a *tail-risk* study "
        "cannot afford. The agent trades the **point-in-time top-30 megacap book**: the 30 "
        "largest names by market cap *known at the window start*, never today's list projected "
        "backwards.\n"
        "\n"
        "**Split C** (ADR-044, executed 2026-07-02 with the ADR-051 rebuild):\n"
        "\n"
        "| split | span | role |\n"
        "|---|---|---|\n"
        "| train | 2005-01-01 → 2016-12-31 | agent learns; feedback is *measured* here |\n"
        "| validation | 2017-01-01 → 2019-12-31 | candidate selection (held-out Deflated Sharpe) |\n"
        "| test | 2020-01-01 → 2026-06-30 | **sealed** until final inference |\n"
        "\n"
        "The sealed test span deliberately contains the modern regime set — COVID (2020), the 2022 "
        "inflation-hiking drawdown, the 2023-25 AI rally, and settled H1-2026 — so the tail claim "
        "is evaluated where tails actually happened. Inter-split boundaries carry a "
        "purge of `max(embargo=21, feature lookback=60) = 60` sessions (López de Prado), so no "
        "observation window straddles a boundary."
    ))
    out.append(code(
        "returns = pd.read_parquet(ROOT / 'data' / 'gold' / 'returns_panel_univ5.parquet')\n"
        "top30 = pd.read_parquet(ROOT / 'data' / 'gold' / 'top30_selection_univ5.parquet')\n"
        "assert returns.shape == (5406, 963), f'unexpected panel shape {returns.shape}'\n"
        "assert str(returns.index[0])[:10] == '2005-01-03'\n"
        "assert str(returns.index[-1])[:10] == '2026-06-30'\n"
        "print(f'returns_panel_univ5 : {returns.shape[0]} sessions x {returns.shape[1]} RICs, '\n"
        "      f'{str(returns.index[0])[:10]} -> {str(returns.index[-1])[:10]}')\n"
        "\n"
        "# The point-in-time top-30 book at two window starts, 15 years apart. The lists are\n"
        "# provenance-level metadata (they exist for audit); inside the experiment the panel is\n"
        "# ANONYMISED to integer ids -- no RIC, ticker, or date ever reaches a reward or the LLM.\n"
        "def book(phase, start):\n"
        "    row = top30[(top30['phase'] == phase)\n"
        "                & (pd.to_datetime(top30['window_start']) == pd.Timestamp(start))]\n"
        "    assert len(row) == 1, f'no unique top-30 row for {phase} @ {start}'\n"
        "    sel = list(row.iloc[0]['selection'])\n"
        "    assert len(sel) == 30\n"
        "    return sel\n"
        "\n"
        "b2005 = book('development', '2005-01-03')\n"
        "b2020 = book('walk_forward', '2020-01-02')\n"
        "print('\\ntop-30 @ 2005-01-03 :', ', '.join(b2005[:10]), '...')\n"
        "print('top-30 @ 2020-01-02 :', ', '.join(b2020[:10]), '...')\n"
        "same = sorted(set(b2005) & set(b2020))\n"
        "print(f'overlap after 15y   : {len(same)}/30 names ({\", \".join(same[:8])}...)')\n"
        "print('turnover of the megacap book is itself a survivorship argument: '\n"
        "      f'{30 - len(same)}/30 of the 2005 book is gone by 2020.')"
    ))
    out.append(md(
        "### The design in one box\n"
        "\n"
        "**Seven arms, one varying ingredient.** Every arm shares the identical environment, "
        "agent (SAC), search protocol, and budget; *only the feedback string shown to the "
        "reward-designing LLM differs* (the identification principle: nothing else may vary).\n"
        "\n"
        "| arm | designer | feedback |\n"
        "|---|---|---|\n"
        "| `distributional` | LLM | six-coordinate left-tail vector (CVaR 1/5/10/25% + tail mass + robust skew) |\n"
        "| `scalar` | LLM | one risk-adjusted scalar |\n"
        "| `scalar_cvar5` | LLM | one tail scalar (CVaR-5%) |\n"
        "| `placebo` | LLM | structurally matched, information-free string |\n"
        "| `placebo_shuffled` | LLM | placebo with shuffled numbers (structure-vs-content control) |\n"
        "| `random_search` | none | parameterised template, random constants |\n"
        "| `bayes_opt` | none | parameterised template, BO-tuned constants |\n"
        "\n"
        "**Headline test (H2).** Two **co-primary** one-sided equivalence questions, combined as "
        "intersection–union tests (Berger 1982) at SESOI $\\Delta^\\* = 0.05$:\n"
        "\n"
        "$$H_0^{\\mathrm{RA}}: |\\,\\overline{\\mathrm{DSR}}_{\\mathrm{dist}} - "
        "\\overline{\\mathrm{DSR}}_{\\mathrm{scalar}}\\,| \\ge \\Delta^\\*\n"
        "\\qquad\\text{vs}\\qquad\n"
        "H_1^{\\mathrm{RA}}: |\\Delta| < \\Delta^\\*$$\n"
        "\n"
        "$$H_0^{\\mathrm{Tail}}: |\\,\\mathrm{CVaR}^{5\\%}_{\\mathrm{dist}} - "
        "\\mathrm{CVaR}^{5\\%}_{\\mathrm{scalar}}\\,| \\ge \\Delta^\\*\n"
        "\\qquad\\text{vs}\\qquad\n"
        "H_1^{\\mathrm{Tail}}: |\\Delta| < \\Delta^\\*$$\n"
        "\n"
        "The realized multiple-testing family is **enumerated and frozen at $m=6$**: "
        "3 H2 contrasts (distributional vs {scalar, placebo, scalar_cvar5}) × 2 held-out metrics "
        "(Sharpe, CVaR-5%); Benjamini–Hochberg over the 6 is *reported*, never the gate — the IUT "
        "conjunction **is** the correction. Everything else in this notebook (taxonomy, mechanism "
        "kernel) is **report-only and disjoint** from that family: it can explain the headline, "
        "never gate it."
    ))

    # ------------------------------------------------------------------ 3 EDA / F3
    out.append(md(
        "## 3 · EDA — the stylised facts that motivate the channel (real train window)\n"
        "\n"
        "**Why this section exists.** The contribution is a *feedback channel*, so the design must "
        "be motivated by the **data the channel carries**. Before any model: does the training "
        "panel actually contain lower-tail structure that a single scalar cannot convey? Four "
        "classical stylised facts (Cont 2001), each recomputed **live** here on the **train window "
        "only** (development top-30, 2005-01-03 → 2016-12-30) — the sealed validation/test years "
        "are never read, so this EDA is snoop-clean by construction:\n"
        "\n"
        "1. **(a) Heavy tails** — the crash days a matched Normal cannot see.\n"
        "2. **(b) The tail is a curve, not a number** — empirical vs Normal-implied CVaR$_\\alpha$ "
        "as $\\alpha \\to 0$, with the four *fed* levels marked.\n"
        "3. **(c) Volatility clustering** — a time-averaged scalar hides *when* risk arrives.\n"
        "4. **(d) Co-crashes** — diversification fails exactly in the tail.\n"
        "\n"
        "The loader is called with `verify_checksum=True`: the panel's SHA-256 is re-verified "
        "against the frozen manifest **before** a single statistic is computed (the full "
        "hash-by-hash audit lives in `data_provenance_walkthrough.ipynb`)."
    ))
    out.append(code(
        "from src.data.loaders import load_gold_panel\n"
        "from src.viz.eda import alive_mask_from_returns, fig_stylised_facts, stylised_fact_stats\n"
        "\n"
        "dev = load_gold_panel('development', verify_checksum=True)  # TRAIN window only\n"
        "R, dates = dev.panel.returns, dev.panel.dates\n"
        "alive = alive_mask_from_returns(R)\n"
        "stats = stylised_fact_stats(R, alive_mask=alive)\n"
        "d0, d1 = str(dates[0])[:10], str(dates[-1])[:10]\n"
        "assert (d0, d1) == ('2005-01-03', '2016-12-30'), f'train window drifted: {d0}..{d1}'\n"
        "\n"
        "t3, t5 = stats['tail_3sigma'], stats['tail_5sigma']\n"
        "print(f'train window {d0} -> {d1}: {stats[\"n_days\"]} sessions x '\n"
        "      f'{stats[\"n_assets\"]} names ({stats[\"n_dead_by_end\"]} dead by window end)')\n"
        "print(f'EW daily: mean {stats[\"mean_daily\"]:+.5f}, sd {stats[\"std_daily\"]:.5f}, '\n"
        "      f'skew {stats[\"skewness\"]:.2f}, excess kurtosis {stats[\"excess_kurtosis\"]:.2f}')\n"
        "print(f'< -3 sigma: {t3[\"count\"]} days vs {t3[\"normal_expected_days\"]:.2f} '\n"
        "      f'Normal-expected (x{t3[\"ratio\"]:.1f})')\n"
        "print(f'< -5 sigma: {t5[\"count\"]} days vs {t5[\"normal_expected_days\"]:.4f} '\n"
        "      f'Normal-expected (x{t5[\"ratio\"]:,.0f})')\n"
        "for a, row in sorted(stats['cvar_by_level'].items(), reverse=True):\n"
        "    print(f'CVaR_{a:g}: empirical {row[\"empirical\"]*100:+.2f}%/day vs Normal '\n"
        "          f'{row[\"normal\"]*100:+.2f}%  (x{row[\"ratio\"]:.2f})')\n"
        "print(f'stress: {stats[\"n_stress_episodes\"]} episodes hold all '\n"
        "      f'{stats[\"n_stress_days\"]} top-decile vol days; longest '\n"
        "      f'{stats[\"longest_episode_days\"]} sessions')\n"
        "print(f'co-crash: calm {stats[\"co_crash_calm_mean\"]:.1%} vs stress '\n"
        "      f'{stats[\"co_crash_stress_mean\"]:.1%} '\n"
        "      f'(x{stats[\"co_crash_ratio\"]:.1f}); worst day {stats[\"worst_day_co_crash\"]:.0%}')\n"
        "\n"
        "# Fail-loud pins on the headline EDA numbers quoted in the prose (drift = data change).\n"
        "assert abs(stats['excess_kurtosis'] - 15.25) < 0.05, stats['excess_kurtosis']\n"
        "assert t5['ratio'] > 1e3, 'the -5 sigma days should be >1000x the Normal expectation'\n"
        "ratios = {a: v['ratio'] for a, v in stats['cvar_by_level'].items()}\n"
        "assert ratios[0.25] < 1.0 < ratios[0.01], 'the CVaR curve should CROSS the Normal curve'\n"
        "assert stats['co_crash_stress_mean'] > 3 * stats['co_crash_calm_mean']\n"
        "\n"
        "fig = fig_stylised_facts(\n"
        "    R, dates=dates, alive_mask=alive,\n"
        "    footnote=(f'Descriptive EDA on the TRAIN window only (development top-30, '\n"
        "              f'{d0} -> {d1}; anonymised ids; delisted names liquidate-to-cash) -- '\n"
        "              'the sealed validation/test years are never read.'))\n"
        "fig"
    ))
    out.append(md(
        "### Reading the four panels\n"
        "\n"
        "- **Heavy tails.** Excess kurtosis **15.2** (a Normal scores 0). Nine sessions land "
        "below $-5\\sigma$ — a region where the matched Normal expects **0.0009 days** over the "
        "whole 12-year window, i.e. the observed count is **~10⁴×** the Gaussian expectation. Any "
        "reward that penalises \"volatility\" with a Gaussian mental model never prices these "
        "days.\n"
        "- **The tail is a curve — and it *crosses* the Normal.** At the shallow fed level "
        "($\\alpha=0.25$) the empirical CVaR is *milder* than Normal-implied (ratio **≈0.84×**); "
        "at the deep level ($\\alpha=0.01$) it is *far worse* (**≈1.66×**). Because the two "
        "curves **cross**, no single scalar — no one $\\alpha$, no variance multiple — can "
        "represent the curve: any scalar summary is wrong in one direction at one end. This is "
        "precisely the information the six-coordinate fed vector transmits and a scalar "
        "collapses.\n"
        "- **Clustering.** All 301 top-decile volatility days concentrate into just **19 "
        "episodes** (the longest — the GFC — runs 90 straight sessions); a time-averaged scalar "
        "cannot say *when* risk arrives, which is what a *conditional* tail measure is for.\n"
        "- **Co-crashes.** On calm days **3.3%** of names sit below their own 5% tail "
        "(≈ independence); on stress days **19.8%** fall together — a **5.9×** amplification, "
        "and on the worst day *every* trading name breaches its own tail at once. "
        "Diversification fails exactly when the tail bites, so portfolio-level tail control "
        "cannot be delegated to breadth."
    ))

    # ------------------------------------------------------------------ 4 fed channel
    out.append(md(
        "## 4 · What the channel carries — and why it may still go silent\n"
        "\n"
        "The distributional arm is fed a six-coordinate profile of the *trained policy's own* "
        "realised left tail: the four CVaR levels marked in panel (b), plus a left-tail-mass and "
        "a robust-skew coordinate. The scalar arm is fed essentially one number. Section 3 showed "
        "the extra coordinates are *not redundant* on this panel. Why, then, pre-register a "
        "**null**?\n"
        "\n"
        "**The numeracy bottleneck (the headline mechanism).** Even when the richer vector is "
        "supplied, frontier LLMs compare *close small floats* at only ~50–70% accuracy "
        "(arXiv:2602.07812; NUMCoT, arXiv:2406.02864). Two sibling candidates' CVaR-5% values "
        "typically differ in the **fourth decimal place** — squarely inside that failure regime. "
        "The channel can be *open* (the information is there) yet *silent* (the reader cannot act "
        "on it): a concrete, citable, falsifiable reason the effect should be ≈0 that is about "
        "**legibility, not capacity** — and §8's SQ3b instrument tests exactly that."
    ))
    out.append(code(
        "# The REAL fed-style tail profile of this panel's EW portfolio (train window, daily):\n"
        "profile = {f'cvar_{int(a*100):02d}': v['empirical']\n"
        "           for a, v in sorted(stats['cvar_by_level'].items())}\n"
        "print('four CVaR coordinates of the fed vector (train-window EW, signed daily):')\n"
        "for k, v in profile.items():\n"
        "    print(f'  {k:>10} : {v:+.4f}')\n"
        "print('  (+ left_tail_mass and robust_skew complete the six-coordinate profile;\\n'\n"
        "      '   per-candidate values are measured on each POLICY\\'s own returns)')\n"
        "gap = abs(profile['cvar_05']) * 0.01\n"
        "print(f'\\nnumeracy regime: telling {profile[\"cvar_05\"]:+.4f} from a sibling '\n"
        "      f'{profile[\"cvar_05\"] - gap:+.4f} is a ~{gap:.1e} gap between close small\\n'\n"
        "      'negatives -- the documented ~50-70% LLM comparison-failure regime (SQ3b, sec. 8).')"
    ))

    # ------------------------------------------------------------------ 5 bundle
    out.append(md(
        "## 5 · Load the analysis bundle (synthetic NULL demo)\n"
        "\n"
        "One call produces a NULL-shaped bundle with the exact schema the sealed-leg loader will "
        "emit — arms, per-seed scores by leg, contrasts, Bayes factors, MCS, and the mechanism "
        "arrays. **Post-campaign this is the only line that changes.**"
    ))
    out.append(code(
        "import make_figures as MF\n"
        "from src.viz import figures as F\n"
        "\n"
        "data = MF.synthesize_null(seed=RNG_SEED, n_seeds=30)  # <-- post-campaign: sealed-leg loader\n"
        "print('arms          :', list(data['sharpe']))\n"
        "print('legs          :', list(data['scores_by_leg']))\n"
        "print('candidates    :', len(data['cand_arms']), 'authored reward programs "
        "(for the AST mechanism)')"
    ))

    # ------------------------------------------------------------------ 6 headline H2
    out.append(md(
        "## 6 · Headline H2 — co-primary equivalence (risk-adjusted **and** tail)\n"
        "\n"
        "**Equivalence-first, by construction.** A bare $p>0.05$ says *\"we saw nothing\"*; a "
        "**TOST equivalence** says *\"the effect is provably inside ±SESOI\"* — a positive, "
        "falsifiable claim about a bounded effect. Each co-primary leg (H2-RA on Sharpe, H2-Tail "
        "on CVaR-5%) runs two one-sided tests against the pre-registered SESOI = 0.05; H2 as a "
        "whole is their **intersection–union**: it passes only if *every* leg passes, which is "
        "itself the multiplicity correction (Berger 1982). The forest draws a contrast **filled** "
        "iff its 90% TOST interval lies inside the ±SESOI band.\n"
        "\n"
        "Three complementary readouts, one story:\n"
        "1. the **TOST forest** — is the effect bounded inside the band?\n"
        "2. **rliable IQM intervals** (Agarwal et al. 2021) — seed-level uncertainty, "
        "stratified-bootstrap, no seed-averaging;\n"
        "3. **evidence for the null** — Bayes factors BF₀₁ and the Model Confidence Set: does the "
        "data *support* equivalence rather than merely fail to reject?"
    ))
    out.append(code(
        "SESOI = 0.05\n"
        "for c in data['contrasts']:\n"
        "    equiv = (c['tost_lo'] >= -SESOI) and (c['tost_hi'] <= SESOI)\n"
        "    verdict = 'EQUIVALENT' if equiv else 'inconclusive'\n"
        "    print(f\"{c['leg']:>5} | {c['label']:<16} est={c['estimate']:+.3f} \"\n"
        "          f\"TOST=[{c['tost_lo']:+.3f}, {c['tost_hi']:+.3f}]  ->  {verdict}\")"
    ))
    out.append(code(
        "fig = F.equivalence_forest(data['contrasts'])  # F5/F6 — the bankable-null figure\n"
        "fig"
    ))
    out.append(code(
        "fig = F.rliable_intervals(data['scores_by_leg'])  # IQM + stratified-bootstrap CIs\n"
        "fig"
    ))
    out.append(code(
        "fig = F.evidence_for_null(data['bf01_by_leg'], data['mcs'])  # BF01 + Model Confidence Set\n"
        "fig"
    ))

    # ------------------------------------------------------------------ 7 taxonomy
    out.append(md(
        "## 7 · The reward-program taxonomy — what did the designers actually *write*? (real)\n"
        "\n"
        "**The instrument.** Every authored program is reduced to its canonical **AST shape-set** "
        "(node *types* only — identifiers, constants and comments are invisible, so renaming a "
        "variable or re-tuning a coefficient cannot fake novelty). Pairwise Jaccard similarity "
        "over shape-sets + connected components at ≥ 0.6 = the program **kinds**; each kind gets "
        "a medoid exemplar and a label from construct prevalence (`src.inference."
        "reward_taxonomy`). Report-only, deterministic, disjoint from the m=6 family.\n"
        "\n"
        "**The question it answers.** Do different feedback arms author different *kinds* of "
        "programs — or the same kinds reshaped? This is the discriminative-validity check on the "
        "whole mechanism story: an instrument that cannot even separate a *template sampler* from "
        "an *LLM author* could not possibly detect feedback-driven structure. The numbers below "
        "are **real** — the frozen prototype archive (6 arms × ~40 candidates)."
    ))
    out.append(code(
        "import json\n"
        "tax = json.loads((ROOT / 'outputs' / 'tables' / 'reward_taxonomy_prototype.json')"
        ".read_text(encoding='utf-8'))\n"
        "pooled, per_arm = tax['pooled'], tax['per_arm']\n"
        "assert tax['status'] == 'ok'\n"
        "assert (pooled['n_programs'], pooled['n_kinds'], pooled['n_singletons']) "
        "== (239, 157, 152)\n"
        "print(f\"pooled: {pooled['n_programs']} programs -> {pooled['n_kinds']} kinds \"\n"
        "      f\"({pooled['n_singletons']} singletons) at Jaccard >= \"\n"
        "      f\"{pooled['sim_threshold']:g}, AST depth {pooled['depth']}, \"\n"
        "      f\"{pooled['n_unparseable']} unparseable\")\n"
        "\n"
        "SEARCH_ARMS = {'random_search', 'bayes_opt'}\n"
        "rows = []\n"
        "for arm, e in sorted(per_arm.items()):\n"
        "    rows.append({'arm': arm, 'designer': 'search' if arm in SEARCH_ARMS else 'LLM',\n"
        "                 'programs': e['n_programs'], 'kinds': e['n_kinds_present'],\n"
        "                 'entropy_bits': round(e['entropy_bits'], 3),\n"
        "                 'max_entropy_bits': round(float(np.log2(max(e['n_programs'], 1))), 3)})\n"
        "    if arm in SEARCH_ARMS:  # a template sampler must collapse to ONE structural kind\n"
        "        assert e['n_kinds_present'] == 1 and e['entropy_bits'] == 0.0, arm\n"
        "    else:                   # an LLM arm should be near-fully idiosyncratic\n"
        "        assert e['n_kinds_present'] >= 39, arm\n"
        "composition = pd.DataFrame(rows).set_index('arm')\n"
        "\n"
        "print('\\nkinds shared by MORE than one program (everything else is a singleton):')\n"
        "for k in pooled['kinds']:\n"
        "    if k['size'] > 1:\n"
        "        arms_of = sorted({m.split('/', 1)[0] for m in k['members']})\n"
        "        print(f\"  {k['kind_id']}: size {k['size']:>2}  arms={arms_of}  \"\n"
        "              f\"label='{k['label']}'\")\n"
        "\n"
        "sens = tax['sensitivity']\n"
        "print('\\nthreshold sensitivity (is the taxonomy a threshold artifact?):')\n"
        "print('  n_kinds:', {r['threshold']: r['n_kinds'] for r in sens['by_threshold']})\n"
        "print('  adjacent Rand index:', {r['pair']: round(r['rand_index'], 4)\n"
        "                                 for r in sens['adjacent_stability']})\n"
        "composition"
    ))
    out.append(md(
        "### Reading the taxonomy\n"
        "\n"
        "- **The two search arms collapse to exactly one kind each** (entropy 0.0 bits): all 40 "
        "`random_search` programs are *one re-parameterised template*, and likewise `bayes_opt` — "
        "the AST shape-set sees through the constant-tuning entirely. That the instrument "
        "recovers this known ground truth is its **discriminative validity**.\n"
        "- **The LLM arms are near-fully idiosyncratic**: 152 of the 157 pooled kinds are "
        "singletons, and every LLM arm's kind-entropy sits at ≈ its own maximum "
        "(log₂(40) ≈ 5.32 bits) — the LLM writes a structurally new program almost every call.\n"
        "- **The only shared kinds cut *across* arms, not within them.** The three non-search "
        "multi-member kinds (`kind_003/004/005`) each span **two different feedback arms** "
        "(distributional–scalar_cvar5, distributional–placebo, scalar–scalar_cvar5). Structural "
        "twins appearing across conditions — including the *placebo* — is exactly what the "
        "**null** predicts: the fed signal is not organising program *structure* by arm.\n"
        "- **Not a threshold artifact**: re-clustering at 0.5/0.6/0.7 keeps pair-agreement (Rand "
        "index) at 0.979 and 0.9998 between adjacent cuts.\n"
        "\n"
        "Post-campaign, the identical induction re-runs on the 7-arm campaign archive "
        "(30 candidates/arm) via `scripts/build_taxonomy.py`."
    ))

    # ------------------------------------------------------------------ 8 mechanism kernel
    out.append(md(
        "## 8 · Mechanism — the originality kernel (a 3-link causal chain)\n"
        "\n"
        "The deep contribution is *where* the channel acts — or fails to. The chain\n"
        "\n"
        "$$\\text{fed signal} \\;\\xrightarrow{\\;a\\;}\\; \\text{authored code} \\;"
        "\\xrightarrow{\\;b\\;}\\; \\text{policy} \\;\\longrightarrow\\; \\text{realised tail}$$\n"
        "\n"
        "is decomposed into three sub-questions, each with a dedicated **report-only** instrument "
        "(disjoint from the frozen testing family):\n"
        "\n"
        "| sub-question | what it asks, plainly | instrument | module |\n"
        "|---|---|---|---|\n"
        "| **SQ1 responsiveness** | when the *fed numbers* move, does the *code* move? | rank-correlation of fed-Δ vs reward-code-Δ, bootstrap CI | `src.inference.responsiveness` |\n"
        "| **SQ2 transmission** | when the *code* moves, does the *outcome* move? | single-mediator decomposition, bootstrap CI on the indirect path $a\\times b$ | `src.inference.mediation` |\n"
        "| **SQ3 specificity** | is it *genuine use* of the signal or a surface echo? | AST-structural named-vs-blinded + the numeracy/legibility differential | `src.inference.contamination`, `responsiveness` |\n"
        "\n"
        "**Why a null is informative here.** If SQ1 is null (path $a \\approx 0$), the indirect "
        "effect $a\\times b$ collapses **for any** downstream strength $b$ — the chain is severed "
        "at the *first* hop, and the performance equivalence of §6 is *explained* (the designer "
        "never routed the signal into code), not merely observed. The cells below run each "
        "instrument on **seeded synthetic nulls** so the logic is visible; post-campaign the same "
        "calls run on the archive."
    ))
    out.append(code(
        "from src.inference.responsiveness import (\n"
        "    responsiveness, legible_format_responsiveness_differential)\n"
        "from src.inference.mediation import mediation_analysis\n"
        "from src.inference.contamination import named_vs_blinded_structural\n"
        "rng = np.random.default_rng(0)\n"
        "\n"
        "# SQ1 — illustrative NULL: the authored-code feature does not track the fed tail signal.\n"
        "n = 80\n"
        "fed = rng.normal(size=n)\n"
        "code_feat = rng.normal(size=n)            # independent of `fed` -> responsiveness ~ 0\n"
        "sq1 = responsiveness(fed, code_feat, n_boot=800, rng=np.random.default_rng(1))\n"
        "print('SQ1 responsiveness  : coef=%+.3f  CI=[%+.3f, %+.3f]  responsive=%s'\n"
        "      % (sq1['coef'], sq1['ci_low'], sq1['ci_high'], sq1['responsive']))\n"
        "assert not sq1['responsive']  # the seeded null must read as a null"
    ))
    out.append(code(
        "# SQ2 — mediation fed -> code -> outcome. With SQ1 null (path a ~ 0), the indirect\n"
        "# effect a*b collapses even though the code->outcome link b is REAL by construction.\n"
        "outcome = 0.9 * code_feat + 0.2 * rng.normal(size=n)\n"
        "sq2 = mediation_analysis(fed, code_feat, outcome, n_boot=800,\n"
        "                         rng=np.random.default_rng(2))\n"
        "print('SQ2 mediation       : a=%+.3f  b=%+.3f  indirect(a*b)=%+.3f  '\n"
        "      'CI=[%+.3f, %+.3f]  mediated=%s'\n"
        "      % (sq2['a'], sq2['b'], sq2['indirect'], sq2['ci_low'], sq2['ci_high'],\n"
        "         sq2['mediated']))\n"
        "print('  -> the chain is severed at link 1 (fed -> code): a~0 => indirect~0 for ANY b.')"
    ))
    out.append(code(
        "# SQ3a — AST-structural named-vs-blinded: does revealing dataset identity change the\n"
        "# program STRUCTURE? Blinding renames identifiers and re-tunes constants -- invisible to\n"
        "# the AST shape-set, so structure locked to the DATA (not the name) scores as identical.\n"
        "named = ['def reward(r):\\n    return r.mean() - 0.5 * cvar(r)',\n"
        "         'def reward(r):\\n    return r.mean() / (r.std() + 1e-8)',\n"
        "         'def reward(r):\\n    return r.mean() - drawdown(r)']\n"
        "blinded = ['def reward(x):\\n    return x.mean() - 0.9 * cvar(x)',\n"
        "           'def reward(z):\\n    return z.mean() / (z.std() + 1e-8)',\n"
        "           'def reward(w):\\n    return w.mean() - drawdown(w)']\n"
        "sq3 = named_vs_blinded_structural(named, blinded, rng=np.random.default_rng(3))\n"
        "print('SQ3 AST-structural  : paired=%.3f  within-floor=%.3f  data_locked=%s'\n"
        "      % (sq3['paired_mean'], sq3['within_blinded_mean'], sq3['data_locked']))\n"
        "print('  -> identifier/constant renaming is invisible to the AST shape '\n"
        "      '(structure is data-locked).')"
    ))
    out.append(code(
        "# SQ3b — the numeracy/legibility differential: does rendering the SAME tail content\n"
        "# legibly RAISE responsiveness? A positive, zero-excluding gap => the bottleneck is\n"
        "# LEGIBILITY (fixable by formatting), not model capacity -- the falsifiable scaling\n"
        "# hypothesis behind the sec. 4 numeracy argument.\n"
        "xl = rng.normal(size=120); ml = 0.85 * xl + 0.3 * rng.normal(size=120)  # legible: tracks\n"
        "xr = rng.normal(size=120); mr = 0.05 * xr + rng.normal(size=120)        # raw: washes out\n"
        "diff = legible_format_responsiveness_differential(\n"
        "    xl, ml, xr, mr, n_boot=800, rng=np.random.default_rng(4))\n"
        "print('SQ3 legibility diff : legible=%+.3f  raw=%+.3f  differential=%+.3f  '\n"
        "      'CI=[%+.3f, %+.3f]  helps=%s'\n"
        "      % (diff['coef_legible'], diff['coef_raw'], diff['differential'],\n"
        "         diff['ci_low'], diff['ci_high'], diff['legibility_helps']))"
    ))
    out.append(code(
        "# The mechanism figures: the responsiveness scatter (F8b) and the 3-D reward-code\n"
        "# embedding (clusters cutting ACROSS arms = the taxonomy's cross-arm twins, in 3-D).\n"
        "fig = F.responsiveness_scatter(data['fed_delta'], data['reward_delta'], rho=data['rho'])\n"
        "fig"
    ))
    out.append(code(
        "from src.viz import advanced as ADV\n"
        "fig = ADV.reward_embedding_3d(data['ast_distance'], data['cand_arms'])\n"
        "fig"
    ))

    # ------------------------------------------------------------------ 9 robustness
    out.append(md(
        "## 9 · Robustness (post-campaign)\n"
        "\n"
        "The confirmatory run re-estimates the headline under: the **delisting-treatment band** "
        "`{0, -30, -55, -100}%` (a sensitivity *surface*, never a single hidden choice — note the "
        "provenance walkthrough shows the corrected Shumway band-end `univ5s` is byte-identical "
        "to the headline panel, because every dead name's terminal return was already observed); "
        "**regime-stratified** tail metrics (calm vs crisis); the **PBO/CSCV** overfitting "
        "probability; and **FZ0 ES** backtests. Each is wired through `src/inference/` and "
        "renders in the same house style; the cells activate when the sealed-leg artifacts exist."
    ))

    # ------------------------------------------------------------------ 10 limitations
    out.append(md(
        "## 10 · Honest limitations & interpretation\n"
        "\n"
        "- **The null is a boundary condition, not a non-result.** It says tail *specificity* "
        "adds no marginal value *over general risk-adjustment* **for a bounded, numerically "
        "bottlenecked authoring agent on this panel** — and the mechanism kernel locates *why* "
        "(SQ1/SQ3). It predicts the channel re-opens with a more legible rendering or a stronger "
        "numeric model: a falsifiable scaling hypothesis, not a shrug.\n"
        "- **Endogeneity.** The fed tail is the trained policy's *own* realised returns, so H2 "
        "compares two coupled reward→policy→measurement loops; the estimator is critic-agnostic "
        "but **not** agent-independent. We never claim otherwise.\n"
        "- **Power.** Tight equivalence bounds at 30 seeds are underpowered for some sub-tests "
        "(e.g. the named-vs-blinded TOST); we report effect sizes + CIs + achieved power, never "
        "bare non-rejections.\n"
        "- **Generality.** Search width K, one model family for the confirmatory leg, one asset "
        "class, one panel. The pre-registered multi-model panel (ADR-039: Claude Opus + a strong "
        "open-weights coder) is the generality probe, secondary by design."
    ))

    # ------------------------------------------------------------------ 11 figure manifest
    out.append(md(
        "## 11 · Figure manifest & how to regenerate\n"
        "\n"
        "Everything regenerates deterministically from the repo:\n"
        "\n"
        "```bash\n"
        "python scripts/make_figures.py --out outputs/figures          # headline + 3-D + GIF suite\n"
        "python scripts/make_figures.py --out outputs/figures --no-advanced   # headline only\n"
        "python scripts/build_taxonomy.py --root outputs/prototype     # the section-7 tables\n"
        "python scripts/build_notebook_results.py                      # THIS notebook\n"
        "python scripts/build_notebook_provenance.py                   # the provenance companion\n"
        "```\n"
        "\n"
        "Post-campaign, the same figure script loads the sealed-leg results (`--results-root`) "
        "and re-renders the identical suite from real data."
    ))
    out.append(code(
        "print('figure entry points (scripts/make_figures.py):',\n"
        "      [n for n in dir(MF) if n.startswith('render')])\n"
        "print('headline figures  (src/viz/figures.py)  :', list(F.__all__))\n"
        "print('advanced figures  (src/viz/advanced.py) :',\n"
        "      [f for f in ADV.__all__ if f != 'classical_mds'])"
    ))
    return out


def main() -> None:
    nb = build_notebook(cells(), id_prefix="rw")
    path = write_notebook(nb, _OUT)
    h1 = sha256_bytes(path)
    write_notebook(nb, path)  # double-build: regeneration must be byte-identical
    h2 = sha256_bytes(path)
    if h1 != h2:  # pragma: no cover - determinism guard
        raise RuntimeError(f"non-deterministic notebook build: {h1[:12]} != {h2[:12]}")
    print(f"[build_notebook_results] wrote {path} ({len(nb['cells'])} cells, sha256 {h1[:12]})")


if __name__ == "__main__":
    main()
