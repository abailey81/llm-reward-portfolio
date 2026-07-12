# Reflection-funnel coding rubric — v1, FROZEN PRE-DATA (2026-07-12)

> Instrument for PREREGISTRATION §2a(g). **This rubric (including the verbatim coder prompt below) is
> frozen BEFORE any campaign reflection exists** — no campaign text has been seen by the author of this
> rubric, so the instrument cannot have been tuned to the data. Any post-freeze change requires a dated
> amendment note here. Declared EXPLORATORY, outside every confirmatory family.
> (The Sonnet prototype's reflections exist but are directional-only and were NOT consulted in writing
> this rubric.)

## 1. Unit and scope

One coded unit = one designer reflection text (the LLM's verbalized reasoning turn) from a TAIL-FED arm
(`distributional`, `scalar_cvar5`, `placebo_shuffled`), per generation. All units are coded (bounded:
generations × candidates per arm).

## 2. The four stages (code each 0/1, cumulative in intent but coded independently)

| Stage | Code = 1 iff … | Operational notes |
|---|---|---|
| **QUOTE** | the text references ≥1 of the six fed tail values (number OR its label) from ITS OWN feedback block | verbatim number match at ≥3 significant figures, OR an unambiguous label reference ("the CVaR-5% shown", "left-tail mass"). Generic risk talk ("reduce tail risk") without reference to the fed values = 0 |
| **COMPARE** | the text compares fed values ACROSS candidates or ACROSS levels (the numeracy-critical step) | e.g. "-0.0582 is worse than -0.0577", "CVaR-1% deteriorated while CVaR-25% improved", "candidate 2's tail is heavier". A restatement of one value with no relation = 0 |
| **CONCLUDE** | the text draws an explicit DESIGN implication from a comparison | "so I will increase the drawdown penalty", "therefore weight the CVaR term higher". The implication must be attributed to the comparison, not free-floating |
| **IMPLEMENT** | the authored code change in the SAME turn realises that implication | cross-checked mechanically against the SQ1 code-feature deltas (`inspect_rewards` features): the concluded change direction appears in the diff. Coder marks the claimed implication; the mechanical check settles it |

Ambiguity rule: if a stage is arguable, code 0 and set `uncertain: true` (conservative; uncertainty rate
is reported).

## 3. The frozen LLM-coder prompt (verbatim; temperature 0; one unit per call)

```
You are coding one reflection text written by an AI reward-designer. The designer was shown a
feedback block containing these six tail-risk values for its previous candidates:
{fed_values_json}

Reflection text:
"""{reflection_text}"""

Code the four stages, each strictly 0 or 1, using ONLY the text above:
- quote: 1 iff the text references at least one of the six fed values above, by number (>=3
  significant figures) or by an unambiguous label. Generic risk vocabulary does not count.
- compare: 1 iff the text explicitly compares fed values across candidates or across tail levels
  (a relational statement between two or more fed quantities).
- conclude: 1 iff the text states a design change that it explicitly justifies by such a comparison.
- implement_claim: 1 iff the text claims the authored code realises that design change.
Also set uncertain: true if any judgment was arguable.
Return ONLY JSON: {"quote":0|1,"compare":0|1,"conclude":0|1,"implement_claim":0|1,
"uncertain":true|false,"evidence":"<the shortest quotation supporting your highest coded stage>"}
```

`IMPLEMENT` final coding = `implement_claim` AND the mechanical SQ1 code-feature cross-check (§2).

## 4. Reliability protocol

- **Two coders:** the frozen-prompt LLM coder + a human (Tamer) coding an independent random sample of
  **≥ 20%** of units (seeded sample, seed = 20260712).
- **Agreement:** Cohen's κ per stage on the overlap sample; report all four κ values. κ < 0.6 on any
  stage ⇒ that stage's funnel result is reported with an explicit reliability caveat (never silently).
- The LLM coder's model id + parameters are archived with every call (the standard transport archival).

## 5. Registered interpretation (from §2a(g), restated)

Per-stage pass rates with the drop-off location; the accounts predict different drop-offs:
A2 readout → falls at COMPARE; A3 execution → falls at COMPARE/CONCLUDE despite quoting;
A4 prior-dominance → falls at QUOTE or CONCLUDEs generically; A5 rational-insensitivity → QUOTE/COMPARE
pass but CONCLUDE selectively tracks only high-SNR deltas (cross-read with instrument (h));
A1 genuine-use → survives to IMPLEMENT.
