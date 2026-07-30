# Tables (CH4 Methods): the eleven authoring models with their pins · the eleven-reward canon

Two specification tables, excluded from the word count. Both exist to make a claim checkable rather than
asserted: the first that the *generative* step is reproducible, the second that the human bar is a real
literature bar rather than a convenient one.

---

## Table 4 — The eleven reward-authoring models, with reproducibility pins (`config/legs.yaml`)

**Why the pins matter.** A closed model can be deprecated, which makes the generative step of any
LLM-in-the-loop study historically irreproducible. The industry supervisors' first recommendation was
therefore open weights and permanence. This suite answers it: **one** frontier closed model holds the
confirmatory seat, and **ten** replication legs re-run the identical protocol, seven of them against
Hugging Face repositories pinned to an exact commit.

| # | Model | Provider | Weight pin (HF commit) | Reasoning | Output cap |
|---|---|---|---|---|---|
| — | **`claude-opus-5`** | Anthropic | closed (vendor weight-preservation commitment cited) | off | 16,384 |
| 1 | `deepseek/deepseek-v4-pro` | OpenRouter | `deepseek-ai/DeepSeek-V4-Pro` @ `b5968e91…` | off | 16,384 |
| 2 | `z-ai/glm-5.2` | OpenRouter | `zai-org/GLM-5.2` @ `b4734de4…` | off | 16,384 |
| 3 | `qwen/qwen3.6-27b` | OpenRouter | `Qwen/Qwen3.6-27B` @ `6a9e13bd…` | off | 16,384 |
| 4 | `qwen/qwen3.5-9b` | OpenRouter | `Qwen/Qwen3.5-9B` @ `c2022362…` | off | 16,384 |
| 5 | `claude-haiku-4-5-20251001` | Anthropic | closed, dated snapshot | off | 16,384 |
| 6 | `openai/gpt-5.6-luna` | OpenRouter | closed | off | 16,384 |
| 7 | `nvidia/nemotron-3-super-120b-a12b` | OpenRouter | `nvidia/…-Super-120B-A12B-BF16` @ `d51eab0d…` | off | 16,384 |
| 8 | `claude-sonnet-5` | Anthropic | closed | off | 16,384 |
| 9 | `google/gemini-2.5-flash` | OpenRouter | closed | off | 16,384 |
| 10 | `moonshotai/kimi-k3-20260715` | OpenRouter | closed, dated snapshot | off | 16,384 |

**Three properties this table is designed to prove.**

1. **Reasoning is OFF and output caps are MATCHED at 16,384 across all eleven** (amendment R106). The
   matched cap is what makes the cross-model comparison fair — and it is why the cap must *not* be raised
   mid-run even when a model truncates against it. One truncation occurred (`nemotron-3-super`, 1 of
   1,099 calls); it is excluded from the reliability denominator and reported, not silently absorbed.
2. **A pin nobody can verify is fictional.** Each pin is round-trip evidenced from the served response
   (`served_model`, `served_provider`, and captured `reasoning_tokens`), because an earlier audit found
   that silently-ignored pins had made a previous reproducibility claim untrue.
3. **The suite spans a deliberate capability gradient**, `qwen3.5-9b` being the registered bottom anchor
   at ~83 % expected authoring-reject rate. Its rejects are a **registered finding**, not a fault: they
   are how the gradient is measured.

---

## Table 5 — The eleven-reward canon: the human bar (`src/baselines/rewards.py`)

**Why eleven and why these.** H1 asks whether an LLM-authored reward beats a human-authored one. A
single comparator would be a straw man, so the champion is the **maximum over all eleven with no
selection step** — the hardest bar the literature offers. Each is a published objective, not an invention
of this study.

| Reward | What it optimises | Source |
|---|---|---|
| `raw_return` | the bare portfolio return — myopic, risk-**neutral** floor | — |
| `return_minus_variance` | return penalised by a variance proxy | — |
| `return_minus_cvar` | return penalised by tail risk (CVaR) | coherent-risk literature |
| `differential_sharpe` | differential (online) Sharpe, **stateful** | Moody, Wu, Liao & Saffell (1998); Moody & Saffell (2001) |
| `differential_downside_ratio` | the downside companion of the above | Moody & Saffell (2001) |
| `mean_variance_utility` | Markowitz quadratic utility `r − ½λ·var` | Markowitz (1952) |
| `return_minus_drawdown` | running log-wealth drawdown penalty, **stateful** | Chekhlov, Uryasev & Zabarankin (2005) |
| `return_minus_downside` | Sortino downside semi-deviation | Sortino & van der Meer (1991) |
| **`return_minus_turnover`** | transaction-cost / turnover penalty | Gärleanu & Pedersen (2013) |
| `log_growth` | growth-optimal Kelly log return | Kelly (1956); Thorp (1971) |
| `volatility_scaled_return` | volatility-**targeted** return | Zhang, Zohren & Roberts (2020) |

**The row that carries a result.** `return_minus_turnover` is the only member that is net-positive over
the sealed window (+1.161 against −0.171 … −0.325 for the other ten), and **four of the losers are
explicitly risk-aware** — `differential_sharpe`, `mean_variance_utility`, `return_minus_cvar`,
`return_minus_drawdown` — with gross Sharpes between +0.82 and +1.03. Sophistication about *risk* did not
substitute for pricing *trading*. See CH6 and contribution C3.

⚠ **Two conventions that must be stated wherever these numbers appear.** All reported Sharpe figures are
the **raw** annualised ratio (`sharpe_ratio(returns, periods_per_year=252)` takes no risk-free argument),
and the sealed window is **2020-03-30 → 2026-06-30, n = 1,571 sessions** — the 60-session lookback purge
means it is *not* every session after 2020-01-01, and conflating the two understates every benchmark by
roughly 0.47 Sharpe.
