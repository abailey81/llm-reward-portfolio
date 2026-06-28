# Reward forensics — opening the black box (FINAL_PLAN Phase 4.C; §6.1 GREEN gate)

Qualitative evidence that the LLM reward-designer USED the distributional feedback (H2), not just that a metric gap exists. DIRECTIONAL on a 1-seed development archive — a go/no-go narrative, not a number for the dissertation.

Arms inspected: bayes_opt, distributional, placebo, random_search, scalar, scalar_cvar5.

## 1. Per-generation summary (fitness + reward-code complexity + tail-usage trend)
| arm | gen | n | best fit | mean fit | mean LOC | mean ops | frac uses-tail | mean tail-terms |
|---|---|---|---|---|---|---|---|---|
| bayes_opt | 0 | 40 | +0.0198 | +0.0040 | 39.0 | 32.0 | 1.00 | 5.00 |
| distributional | 0 | 5 | +0.0046 | +0.0020 | 83.6 | 54.6 | 1.00 | 6.60 |
| distributional | 1 | 4 | +0.0127 | +0.0050 | 79.8 | 89.8 | 1.00 | 6.00 |
| distributional | 2 | 5 | +0.0022 | +0.0013 | 78.6 | 90.4 | 1.00 | 6.00 |
| distributional | 3 | 5 | +0.0601 | +0.0200 | 75.0 | 81.2 | 1.00 | 6.00 |
| distributional | 4 | 5 | +0.0047 | +0.0020 | 83.6 | 111.8 | 1.00 | 7.20 |
| distributional | 5 | 5 | +0.0557 | +0.0190 | 81.2 | 99.0 | 1.00 | 6.60 |
| distributional | 6 | 5 | +0.0056 | +0.0015 | 86.0 | 84.2 | 1.00 | 7.20 |
| distributional | 7 | 5 | +0.0161 | +0.0092 | 75.6 | 84.2 | 1.00 | 6.60 |
| placebo | 0 | 5 | +0.0142 | +0.0078 | 97.6 | 258.2 | 1.00 | 6.40 |
| placebo | 1 | 5 | +0.0167 | +0.0047 | 73.2 | 67.2 | 1.00 | 5.20 |
| placebo | 2 | 5 | +0.0074 | +0.0024 | 67.4 | 58.0 | 1.00 | 6.60 |
| placebo | 3 | 5 | +0.0027 | +0.0016 | 65.2 | 72.0 | 1.00 | 5.60 |
| placebo | 4 | 5 | +0.0260 | +0.0072 | 70.6 | 67.6 | 1.00 | 4.40 |
| placebo | 5 | 5 | +0.0020 | +0.0014 | 77.4 | 66.6 | 1.00 | 6.60 |
| placebo | 6 | 5 | +0.0168 | +0.0048 | 70.8 | 67.4 | 1.00 | 4.80 |
| placebo | 7 | 5 | +0.0012 | +0.0004 | 68.4 | 68.8 | 1.00 | 6.20 |
| random_search | 0 | 40 | +0.0518 | +0.0053 | 19.0 | 18.0 | 1.00 | 4.00 |
| scalar | 0 | 5 | +0.0251 | +0.0087 | 88.4 | 51.8 | 1.00 | 6.60 |
| scalar | 1 | 5 | +0.0085 | +0.0045 | 67.6 | 92.0 | 1.00 | 5.40 |
| scalar | 2 | 5 | +0.0137 | +0.0032 | 59.4 | 63.6 | 1.00 | 5.00 |
| scalar | 3 | 5 | +0.0189 | +0.0066 | 70.0 | 74.0 | 1.00 | 5.20 |
| scalar | 4 | 5 | +0.0114 | +0.0059 | 77.6 | 71.6 | 1.00 | 5.80 |
| scalar | 5 | 5 | +0.0072 | +0.0036 | 75.0 | 81.0 | 1.00 | 6.20 |
| scalar | 6 | 5 | +0.0037 | +0.0011 | 67.0 | 83.2 | 1.00 | 6.00 |
| scalar | 7 | 5 | +0.1100 | +0.0227 | 70.0 | 85.0 | 1.00 | 5.20 |
| scalar_cvar5 | 0 | 5 | +0.0947 | +0.0256 | 89.4 | 60.0 | 1.00 | 6.00 |
| scalar_cvar5 | 1 | 5 | +0.0234 | +0.0065 | 80.4 | 99.6 | 1.00 | 6.80 |
| scalar_cvar5 | 2 | 5 | +0.0314 | +0.0081 | 73.2 | 78.4 | 1.00 | 6.60 |
| scalar_cvar5 | 3 | 5 | +0.0017 | +0.0012 | 81.4 | 99.4 | 1.00 | 6.60 |
| scalar_cvar5 | 4 | 5 | +0.0233 | +0.0065 | 77.6 | 84.6 | 1.00 | 7.00 |
| scalar_cvar5 | 5 | 5 | +0.0120 | +0.0047 | 76.0 | 99.2 | 1.00 | 6.80 |
| scalar_cvar5 | 6 | 5 | +0.0056 | +0.0024 | 82.4 | 111.4 | 1.00 | 6.60 |
| scalar_cvar5 | 7 | 5 | +0.0087 | +0.0026 | 77.0 | 66.2 | 1.00 | 6.60 |

## 2. Feedback responsiveness (did the revision track the fed-back distribution? — DIRECTIONAL probe)
DIRECTIONAL only — no number in this table enters the dissertation; the CAUSAL 'did it use the distribution' test is the matched-budget ablation contrast across arms (cf. Eureka §4.3). Per-arm SPEARMAN (rank) correlation between the reward-source EDIT magnitude (gen N→N+1) and the L1 tail-stat DELTA the LLM was shown that step. Higher ⇒ the designer changed its code more when the distribution moved more. `n/a` = arm carries no tail feedback (scalar/placebo/search).

| arm | responsiveness | n steps | note |
|---|---|---|---|
| bayes_opt | n/a | 0 | arm not fed a tail distribution (scalar/placebo/search) — nothing to track |
| distributional | -0.0529 | 38 | ok |
| placebo | n/a | 0 | arm not fed a tail distribution (scalar/placebo/search) — nothing to track |
| random_search | n/a | 0 | arm not fed a tail distribution (scalar/placebo/search) — nothing to track |
| scalar | n/a | 0 | arm not fed a tail distribution (scalar/placebo/search) — nothing to track |
| scalar_cvar5 | -0.0678 | 39 | ok |

## 3. Reward-hacking taxonomy (Skalse 2022; Hadfield-Menell 2017)
Flagged 2 / 239 candidates. specification_gaming=0, proxy_no_tail=0, tautology=2.

| arm | candidate | gen | val fitness | uses tail | flags |
|---|---|---|---|---|---|
| bayes_opt | bayes_opt-c0 | 0 | +0.0087 | True | — |
| bayes_opt | bayes_opt-c1 | 0 | +0.0001 | True | — |
| bayes_opt | bayes_opt-c10 | 0 | +0.0056 | True | — |
| bayes_opt | bayes_opt-c11 | 0 | +0.0049 | True | — |
| bayes_opt | bayes_opt-c12 | 0 | +0.0159 | True | — |
| bayes_opt | bayes_opt-c13 | 0 | +0.0031 | True | — |
| bayes_opt | bayes_opt-c14 | 0 | +0.0039 | True | — |
| bayes_opt | bayes_opt-c15 | 0 | +0.0006 | True | — |
| bayes_opt | bayes_opt-c16 | 0 | +0.0034 | True | — |
| bayes_opt | bayes_opt-c17 | 0 | +0.0059 | True | — |
| bayes_opt | bayes_opt-c18 | 0 | +0.0002 | True | — |
| bayes_opt | bayes_opt-c19 | 0 | +0.0002 | True | — |
| bayes_opt | bayes_opt-c2 | 0 | +0.0198 | True | — |
| bayes_opt | bayes_opt-c20 | 0 | +0.0001 | True | — |
| bayes_opt | bayes_opt-c21 | 0 | +0.0029 | True | — |
| bayes_opt | bayes_opt-c22 | 0 | +0.0030 | True | — |
| bayes_opt | bayes_opt-c23 | 0 | +0.0012 | True | — |
| bayes_opt | bayes_opt-c24 | 0 | +0.0006 | True | — |
| bayes_opt | bayes_opt-c25 | 0 | +0.0112 | True | — |
| bayes_opt | bayes_opt-c26 | 0 | +0.0021 | True | — |
| bayes_opt | bayes_opt-c27 | 0 | +0.0008 | True | — |
| bayes_opt | bayes_opt-c28 | 0 | +0.0000 | True | — |
| bayes_opt | bayes_opt-c29 | 0 | +0.0142 | True | — |
| bayes_opt | bayes_opt-c3 | 0 | +0.0013 | True | — |
| bayes_opt | bayes_opt-c30 | 0 | +0.0001 | True | — |
| bayes_opt | bayes_opt-c31 | 0 | +0.0036 | True | — |
| bayes_opt | bayes_opt-c32 | 0 | +0.0003 | True | — |
| bayes_opt | bayes_opt-c33 | 0 | +0.0065 | True | — |
| bayes_opt | bayes_opt-c34 | 0 | +0.0139 | True | — |
| bayes_opt | bayes_opt-c35 | 0 | +0.0132 | True | — |
| bayes_opt | bayes_opt-c36 | 0 | +0.0001 | True | — |
| bayes_opt | bayes_opt-c37 | 0 | +0.0004 | True | — |
| bayes_opt | bayes_opt-c38 | 0 | +0.0022 | True | — |
| bayes_opt | bayes_opt-c39 | 0 | +0.0038 | True | — |
| bayes_opt | bayes_opt-c4 | 0 | +0.0000 | True | — |
| bayes_opt | bayes_opt-c5 | 0 | +0.0001 | True | — |
| bayes_opt | bayes_opt-c6 | 0 | +0.0001 | True | — |
| bayes_opt | bayes_opt-c7 | 0 | +0.0009 | True | — |
| bayes_opt | bayes_opt-c8 | 0 | +0.0004 | True | — |
| bayes_opt | bayes_opt-c9 | 0 | +0.0038 | True | — |
| distributional | distributional-g0-c0 | 0 | +0.0012 | True | — |
| distributional | distributional-g0-c1 | 0 | +0.0003 | True | — |
| distributional | distributional-g0-c2 | 0 | +0.0009 | True | — |
| distributional | distributional-g0-c3 | 0 | +0.0030 | True | — |
| distributional | distributional-g0-c4 | 0 | +0.0046 | True | — |
| distributional | distributional-g1-c1 | 1 | +0.0127 | True | — |
| distributional | distributional-g1-c2 | 1 | +0.0016 | True | — |
| distributional | distributional-g1-c3 | 1 | +0.0001 | True | — |
| distributional | distributional-g1-c4 | 1 | +0.0057 | True | — |
| distributional | distributional-g2-c0 | 2 | +0.0002 | True | — |
| distributional | distributional-g2-c1 | 2 | +0.0022 | True | — |
| distributional | distributional-g2-c2 | 2 | +0.0001 | True | — |
| distributional | distributional-g2-c3 | 2 | +0.0020 | True | — |
| distributional | distributional-g2-c4 | 2 | +0.0019 | True | — |
| distributional | distributional-g3-c0 | 3 | +0.0601 | True | — |
| distributional | distributional-g3-c1 | 3 | +0.0013 | True | — |
| distributional | distributional-g3-c2 | 3 | +0.0316 | True | — |
| distributional | distributional-g3-c3 | 3 | +0.0066 | True | — |
| distributional | distributional-g3-c4 | 3 | +0.0003 | True | — |
| distributional | distributional-g4-c0 | 4 | +0.0019 | True | tautology |
| distributional | distributional-g4-c1 | 4 | +0.0003 | True | — |
| distributional | distributional-g4-c2 | 4 | +0.0021 | True | — |
| distributional | distributional-g4-c3 | 4 | +0.0008 | True | — |
| distributional | distributional-g4-c4 | 4 | +0.0047 | True | — |
| distributional | distributional-g5-c0 | 5 | +0.0557 | True | — |
| distributional | distributional-g5-c1 | 5 | +0.0254 | True | — |
| distributional | distributional-g5-c2 | 5 | +0.0016 | True | — |
| distributional | distributional-g5-c3 | 5 | +0.0007 | True | — |
| distributional | distributional-g5-c4 | 5 | +0.0115 | True | — |
| distributional | distributional-g6-c0 | 6 | +0.0000 | True | — |
| distributional | distributional-g6-c1 | 6 | +0.0008 | True | — |
| distributional | distributional-g6-c2 | 6 | +0.0056 | True | — |
| distributional | distributional-g6-c3 | 6 | +0.0000 | True | — |
| distributional | distributional-g6-c4 | 6 | +0.0008 | True | — |
| distributional | distributional-g7-c0 | 7 | +0.0074 | True | — |
| distributional | distributional-g7-c1 | 7 | +0.0094 | True | — |
| distributional | distributional-g7-c2 | 7 | +0.0007 | True | — |
| distributional | distributional-g7-c3 | 7 | +0.0161 | True | — |
| distributional | distributional-g7-c4 | 7 | +0.0127 | True | — |
| placebo | placebo-g0-c0 | 0 | +0.0142 | True | — |
| placebo | placebo-g0-c1 | 0 | +0.0087 | True | — |
| placebo | placebo-g0-c2 | 0 | +0.0103 | True | — |
| placebo | placebo-g0-c3 | 0 | +0.0000 | True | — |
| placebo | placebo-g0-c4 | 0 | +0.0060 | True | — |
| placebo | placebo-g1-c0 | 1 | +0.0167 | True | — |
| placebo | placebo-g1-c1 | 1 | +0.0012 | True | — |
| placebo | placebo-g1-c2 | 1 | +0.0003 | True | — |
| placebo | placebo-g1-c3 | 1 | +0.0033 | True | — |
| placebo | placebo-g1-c4 | 1 | +0.0019 | True | — |
| placebo | placebo-g2-c0 | 2 | +0.0002 | True | — |
| placebo | placebo-g2-c1 | 2 | +0.0074 | True | — |
| placebo | placebo-g2-c2 | 2 | +0.0022 | True | — |
| placebo | placebo-g2-c3 | 2 | +0.0006 | True | — |
| placebo | placebo-g2-c4 | 2 | +0.0015 | True | — |
| placebo | placebo-g3-c0 | 3 | +0.0004 | True | — |
| placebo | placebo-g3-c1 | 3 | +0.0027 | True | — |
| placebo | placebo-g3-c2 | 3 | +0.0016 | True | — |
| placebo | placebo-g3-c3 | 3 | +0.0022 | True | — |
| placebo | placebo-g3-c4 | 3 | +0.0010 | True | — |
| placebo | placebo-g4-c0 | 4 | +0.0011 | True | — |
| placebo | placebo-g4-c1 | 4 | +0.0260 | True | — |
| placebo | placebo-g4-c2 | 4 | +0.0034 | True | — |
| placebo | placebo-g4-c3 | 4 | +0.0028 | True | — |
| placebo | placebo-g4-c4 | 4 | +0.0028 | True | — |
| placebo | placebo-g5-c0 | 5 | +0.0011 | True | — |
| placebo | placebo-g5-c1 | 5 | +0.0014 | True | — |
| placebo | placebo-g5-c2 | 5 | +0.0009 | True | — |
| placebo | placebo-g5-c3 | 5 | +0.0014 | True | — |
| placebo | placebo-g5-c4 | 5 | +0.0020 | True | — |
| placebo | placebo-g6-c0 | 6 | +0.0036 | True | — |
| placebo | placebo-g6-c1 | 6 | +0.0168 | True | — |
| placebo | placebo-g6-c2 | 6 | +0.0004 | True | — |
| placebo | placebo-g6-c3 | 6 | +0.0027 | True | — |
| placebo | placebo-g6-c4 | 6 | +0.0004 | True | — |
| placebo | placebo-g7-c0 | 7 | +0.0006 | True | — |
| placebo | placebo-g7-c1 | 7 | +0.0001 | True | — |
| placebo | placebo-g7-c2 | 7 | +0.0012 | True | — |
| placebo | placebo-g7-c3 | 7 | +0.0000 | True | — |
| placebo | placebo-g7-c4 | 7 | +0.0001 | True | — |
| random_search | random_search-c0 | 0 | +0.0002 | True | — |
| random_search | random_search-c1 | 0 | +0.0023 | True | — |
| random_search | random_search-c10 | 0 | +0.0070 | True | — |
| random_search | random_search-c11 | 0 | +0.0018 | True | — |
| random_search | random_search-c12 | 0 | +0.0002 | True | — |
| random_search | random_search-c13 | 0 | +0.0027 | True | — |
| random_search | random_search-c14 | 0 | +0.0000 | True | — |
| random_search | random_search-c15 | 0 | +0.0159 | True | — |
| random_search | random_search-c16 | 0 | +0.0001 | True | — |
| random_search | random_search-c17 | 0 | +0.0000 | True | — |
| random_search | random_search-c18 | 0 | +0.0001 | True | — |
| random_search | random_search-c19 | 0 | +0.0002 | True | — |
| random_search | random_search-c2 | 0 | +0.0000 | True | — |
| random_search | random_search-c20 | 0 | +0.0145 | True | — |
| random_search | random_search-c21 | 0 | +0.0000 | True | — |
| random_search | random_search-c22 | 0 | +0.0091 | True | — |
| random_search | random_search-c23 | 0 | +0.0069 | True | — |
| random_search | random_search-c24 | 0 | +0.0002 | True | — |
| random_search | random_search-c25 | 0 | +0.0007 | True | — |
| random_search | random_search-c26 | 0 | +0.0017 | True | — |
| random_search | random_search-c27 | 0 | +0.0069 | True | — |
| random_search | random_search-c28 | 0 | +0.0027 | True | — |
| random_search | random_search-c29 | 0 | +0.0071 | True | — |
| random_search | random_search-c3 | 0 | +0.0518 | True | — |
| random_search | random_search-c30 | 0 | +0.0007 | True | — |
| random_search | random_search-c31 | 0 | +0.0001 | True | — |
| random_search | random_search-c32 | 0 | +0.0001 | True | — |
| random_search | random_search-c33 | 0 | +0.0047 | True | — |
| random_search | random_search-c34 | 0 | +0.0042 | True | — |
| random_search | random_search-c35 | 0 | +0.0070 | True | — |
| random_search | random_search-c36 | 0 | +0.0083 | True | — |
| random_search | random_search-c37 | 0 | +0.0005 | True | — |
| random_search | random_search-c38 | 0 | +0.0145 | True | — |
| random_search | random_search-c39 | 0 | +0.0175 | True | — |
| random_search | random_search-c4 | 0 | +0.0091 | True | — |
| random_search | random_search-c5 | 0 | +0.0009 | True | — |
| random_search | random_search-c6 | 0 | +0.0011 | True | — |
| random_search | random_search-c7 | 0 | +0.0068 | True | — |
| random_search | random_search-c8 | 0 | +0.0014 | True | — |
| random_search | random_search-c9 | 0 | +0.0013 | True | — |
| scalar | scalar-g0-c0 | 0 | +0.0110 | True | — |
| scalar | scalar-g0-c1 | 0 | +0.0251 | True | — |
| scalar | scalar-g0-c2 | 0 | +0.0010 | True | — |
| scalar | scalar-g0-c3 | 0 | +0.0005 | True | — |
| scalar | scalar-g0-c4 | 0 | +0.0057 | True | — |
| scalar | scalar-g1-c0 | 1 | +0.0045 | True | — |
| scalar | scalar-g1-c1 | 1 | +0.0019 | True | — |
| scalar | scalar-g1-c2 | 1 | +0.0059 | True | — |
| scalar | scalar-g1-c3 | 1 | +0.0085 | True | — |
| scalar | scalar-g1-c4 | 1 | +0.0017 | True | — |
| scalar | scalar-g2-c0 | 2 | +0.0137 | True | — |
| scalar | scalar-g2-c1 | 2 | +0.0001 | True | — |
| scalar | scalar-g2-c2 | 2 | +0.0022 | True | — |
| scalar | scalar-g2-c3 | 2 | +0.0000 | True | — |
| scalar | scalar-g2-c4 | 2 | +0.0001 | True | — |
| scalar | scalar-g3-c0 | 3 | +0.0010 | True | — |
| scalar | scalar-g3-c1 | 3 | +0.0189 | True | — |
| scalar | scalar-g3-c2 | 3 | +0.0079 | True | — |
| scalar | scalar-g3-c3 | 3 | +0.0052 | True | — |
| scalar | scalar-g3-c4 | 3 | +0.0001 | True | — |
| scalar | scalar-g4-c0 | 4 | +0.0114 | True | — |
| scalar | scalar-g4-c1 | 4 | +0.0099 | True | — |
| scalar | scalar-g4-c2 | 4 | +0.0059 | True | — |
| scalar | scalar-g4-c3 | 4 | +0.0017 | True | — |
| scalar | scalar-g4-c4 | 4 | +0.0007 | True | — |
| scalar | scalar-g5-c0 | 5 | +0.0015 | True | — |
| scalar | scalar-g5-c1 | 5 | +0.0063 | True | — |
| scalar | scalar-g5-c2 | 5 | +0.0072 | True | — |
| scalar | scalar-g5-c3 | 5 | +0.0019 | True | — |
| scalar | scalar-g5-c4 | 5 | +0.0009 | True | — |
| scalar | scalar-g6-c0 | 6 | +0.0037 | True | — |
| scalar | scalar-g6-c1 | 6 | +0.0000 | True | — |
| scalar | scalar-g6-c2 | 6 | +0.0011 | True | — |
| scalar | scalar-g6-c3 | 6 | +0.0003 | True | — |
| scalar | scalar-g6-c4 | 6 | +0.0002 | True | — |
| scalar | scalar-g7-c0 | 7 | +0.0004 | True | — |
| scalar | scalar-g7-c1 | 7 | +0.0010 | True | — |
| scalar | scalar-g7-c2 | 7 | +0.0006 | True | — |
| scalar | scalar-g7-c3 | 7 | +0.1100 | True | — |
| scalar | scalar-g7-c4 | 7 | +0.0018 | True | — |
| scalar_cvar5 | scalar_cvar5-g0-c0 | 0 | +0.0034 | True | — |
| scalar_cvar5 | scalar_cvar5-g0-c1 | 0 | +0.0262 | True | — |
| scalar_cvar5 | scalar_cvar5-g0-c2 | 0 | +0.0026 | True | — |
| scalar_cvar5 | scalar_cvar5-g0-c3 | 0 | +0.0009 | True | — |
| scalar_cvar5 | scalar_cvar5-g0-c4 | 0 | +0.0947 | True | — |
| scalar_cvar5 | scalar_cvar5-g1-c0 | 1 | +0.0082 | True | — |
| scalar_cvar5 | scalar_cvar5-g1-c1 | 1 | +0.0006 | True | — |
| scalar_cvar5 | scalar_cvar5-g1-c2 | 1 | +0.0003 | True | — |
| scalar_cvar5 | scalar_cvar5-g1-c3 | 1 | +0.0000 | True | — |
| scalar_cvar5 | scalar_cvar5-g1-c4 | 1 | +0.0234 | True | — |
| scalar_cvar5 | scalar_cvar5-g2-c0 | 2 | +0.0314 | True | — |
| scalar_cvar5 | scalar_cvar5-g2-c1 | 2 | +0.0020 | True | — |
| scalar_cvar5 | scalar_cvar5-g2-c2 | 2 | +0.0004 | True | — |
| scalar_cvar5 | scalar_cvar5-g2-c3 | 2 | +0.0061 | True | — |
| scalar_cvar5 | scalar_cvar5-g2-c4 | 2 | +0.0007 | True | — |
| scalar_cvar5 | scalar_cvar5-g3-c0 | 3 | +0.0012 | True | — |
| scalar_cvar5 | scalar_cvar5-g3-c1 | 3 | +0.0010 | True | — |
| scalar_cvar5 | scalar_cvar5-g3-c2 | 3 | +0.0009 | True | tautology |
| scalar_cvar5 | scalar_cvar5-g3-c3 | 3 | +0.0011 | True | — |
| scalar_cvar5 | scalar_cvar5-g3-c4 | 3 | +0.0017 | True | — |
| scalar_cvar5 | scalar_cvar5-g4-c0 | 4 | +0.0020 | True | — |
| scalar_cvar5 | scalar_cvar5-g4-c1 | 4 | +0.0233 | True | — |
| scalar_cvar5 | scalar_cvar5-g4-c2 | 4 | +0.0069 | True | — |
| scalar_cvar5 | scalar_cvar5-g4-c3 | 4 | +0.0001 | True | — |
| scalar_cvar5 | scalar_cvar5-g4-c4 | 4 | +0.0002 | True | — |
| scalar_cvar5 | scalar_cvar5-g5-c0 | 5 | +0.0120 | True | — |
| scalar_cvar5 | scalar_cvar5-g5-c1 | 5 | +0.0003 | True | — |
| scalar_cvar5 | scalar_cvar5-g5-c2 | 5 | +0.0010 | True | — |
| scalar_cvar5 | scalar_cvar5-g5-c3 | 5 | +0.0065 | True | — |
| scalar_cvar5 | scalar_cvar5-g5-c4 | 5 | +0.0036 | True | — |
| scalar_cvar5 | scalar_cvar5-g6-c0 | 6 | +0.0032 | True | — |
| scalar_cvar5 | scalar_cvar5-g6-c1 | 6 | +0.0011 | True | — |
| scalar_cvar5 | scalar_cvar5-g6-c2 | 6 | +0.0001 | True | — |
| scalar_cvar5 | scalar_cvar5-g6-c3 | 6 | +0.0056 | True | — |
| scalar_cvar5 | scalar_cvar5-g6-c4 | 6 | +0.0021 | True | — |
| scalar_cvar5 | scalar_cvar5-g7-c0 | 7 | +0.0003 | True | — |
| scalar_cvar5 | scalar_cvar5-g7-c1 | 7 | +0.0040 | True | — |
| scalar_cvar5 | scalar_cvar5-g7-c2 | 7 | +0.0000 | True | — |
| scalar_cvar5 | scalar_cvar5-g7-c3 | 7 | +0.0087 | True | — |
| scalar_cvar5 | scalar_cvar5-g7-c4 | 7 | +0.0000 | True | — |

## Notes
- Reads results ONLY through `src.io.results.load_all` (audit C-1) and never writes a run record (the archive is read-only).
- The interpretability lens (`_TAIL_TERMS`) and the archive walk (`load_arms`) are REUSED from `scripts/analyze_results.py`.
- specification_gaming = a reward that references a logged tail component while held-out fitness collapsed (≤ 0): the proxy was driven up while the true objective fell.
