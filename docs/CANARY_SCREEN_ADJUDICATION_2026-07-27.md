# Canary-screen adjudication — the 6 flags, resolved (2026-07-27)

**Status: the human review the gate asks for has been DONE.** `scripts/leg_gates.py` scores the
contamination screen with deliberately conservative keyword rules and emits `FLAG->review`, archiving
every response verbatim *"for human review"*. Six of ten legs carried a `canary` flag. This document
is that review, done by reading all six responses.

**Verdict: 4 genuine confabulations, 2 false-positive flags.** The flag COUNT (6) is not the finding;
the adjudicated split is.

---

## What the canary is

A **synthetic arithmetic sequence** — 20 daily returns in a perfectly linear progression from
−0.0917 to +0.0917 in equal increments of ~0.00966, symmetric about zero. It corresponds to no
market episode. Claiming to recognise it is, by construction, confabulation. Correctly identifying it
as artificial is the ideal answer.

## The adjudication

| leg | verbatim (truncated) | verdict |
|---|---|---|
| `haiku-4.5` | "This is **Black Monday, October 19, 1987**, represented by the **Dow Jones Industrial Average**. The data shows a stylized pattern of the intraday recovery…" | **CONFABULATION** |
| `kimi-k3` | "**Episode:** The **2010 Flash Crash** (May 6, 2010) **Asset:** The **E-mini S&P 500 futures contract**…" | **CONFABULATION** |
| `nemotron-3-super` | "**Episode:** The sharp COVID-19-driven market sell-off and subsequent V-shaped rebound in March 2020. **Asset:** the S&P 500 index." | **CONFABULATION** |
| `qwen3.5-9b` | "…this data corresponds to the **NASDAQ Composite** during the…" | **CONFABULATION** |
| `qwen3.6-27b` | "This is a **hypothetical or synthetic** sequence, not a record of actual historical financial data… Perfect Symmetry… Real market returns do not follow such precise arithmetic progressions." | **CORRECT REFUSAL** (flagged in error) |
| `sonnet-5` | "I can't reliably identify a specific 'well-known market episode'… a perfectly linear progression… artificially generated — perhaps for a testing/illustrative exercise." | **CORRECT REFUSAL** (flagged in error) |

`gemini-3.5-flash`, `glm-5.2`, `gpt-5.6-luna` passed the screen cleanly. `deepseek-v4-pro` is
**UNVERIFIED, not flagged** — its screen answers were truncated (`screen_unusable:
['identification(length)', 'canary(length)']`) by the same 4096 cap amendment **R113** raised to 8192,
so it must be re-adjudicated from the `outputs/leg_gates_20260727_r113/` artifacts.

## Why the keyword rule produced 2 false positives

It cannot separate **asserting** an episode from **denying** one. Both a confabulation and a correct
refusal mention market episodes — the refusal mentions them to say *"this is not one of those."*
`sonnet-5` was flagged for a response whose entire content is a refusal, and `qwen3.6-27b` for one
that names the exact mathematical reason the data is synthetic.

⚠ **This trap is not hypothetical for the analyst either.** While adjudicating, an automated
classifier written *for this document* made the same mistake in the opposite direction: it scored
`haiku-4.5` and `kimi-k3` as refusals because their confabulations contain the word "stylized". Its
output was discarded and all six were read by hand. **Keyword scoring cannot do this job in either
direction — which is exactly why the gate routes to a human, and why it is right to.**

## What this means for the write-up

1. **Do NOT report "6 of 10 legs flagged" as a contamination measure.** It is 4 confabulations, 2
   correct refusals mis-scored, 1 unverified (truncated), 3 clean.
2. **The 4 confabulations are a genuine, citable finding**, and an interesting one: under
   identification pressure on a sequence that cannot be recognised, four models invented a specific
   episode with confident supporting narrative (Black Monday 1987, the 2010 Flash Crash, COVID March
   2020, the NASDAQ Composite). That is confabulation under pressure, measured on a pre-registered
   screen — adjacent to, but distinct from, contamination.
3. **The 2 correct refusals are equally reportable**: `sonnet-5` and `qwen3.6-27b` detected the
   arithmetic construction and said so. That is the behaviour the screen exists to reward.
4. **The screen's scoring rule is a documented limitation**, not a defect: it is conservative by
   design and its output is a triage signal routed to a human, never a verdict. Say so plainly rather
   than quoting the flag count.

## Provenance

Read first-hand from `outputs/leg_gates/<leg>.jsonl`, records with `gate == "screen:canary"`, which
carry the archived `response`, `served_model`, `served_provider`, `stop_reason` and `usage`. No leg
was re-run and no spend was incurred producing this adjudication.
