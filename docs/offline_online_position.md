# Online vs offline RL — position memo (supervisor task)
Anchors: Khraishi & Okhrati (2022, ICAIF) — offline CQL for credit pricing because live exploration harms
real customers; Levine et al. (2020) survey; Khraishi & Okhrati (2023) noise augmentation.

**Harm criterion applied.** Their decision rule: offline is mandated when the experiment can cause real
damage. Here, training and exploration occur ONLY in historical-replay simulation — no live market, no
customers — so the predicate is absent and simulated-online training is permissible *by the supervisor's own
published criterion*. The simulator's epistemics are declared (exogenous prices: defensible for a 30-name
large-cap long-only book at modest notional; stated with its validity domain, not hidden).

**The relabelling bridge (small original observation).** Every LLM-generated reward is executable code over
(s, a, s′). A fixed logged-transition dataset can therefore be RELABELLED under any candidate at near-zero
cost — Eureka-style reward search is *natively compatible with fully offline RL*: relabel → CQL/IQL (d3rlpy)
→ rank on held-out fitness. That is the deployment path an institution (e.g., a bank) would need, where live
exploration is impossible — and it connects this dissertation directly to the AIRiskLab line. Optional
contained experiment: CQL under the single best evolved reward, end-July, if the schedule allows; the
written argument carries the marks regardless.
