# Meeting script — 2 minutes, spoken (first group meeting; pairs with research_brief_v1.md)

> **SUPERSEDED — describes the abandoned IQN-SAC line (IQN-SAC agents, IQN-critic quantile statistics), see
> ADR-022.** The live design measures the return distribution **off-critic** (empirical + EVT,
> `src/feedback/measurement.py`) and trains SB3 SAC (+ TQC secondary), not IQN-SAC. Retained as a dated
> record of the first-meeting framing.

My project asks one question: can a large language model *design* the reward function for a
risk-sensitive portfolio RL agent — not feed it signals, which is what the closest prior work does, but
write the reward as code, evolve it over generations, and crucially, be told about the *tail* of the
return distribution while it designs.

Method in one breath: the Eureka loop from robotics — the LLM reads the environment source, writes
sixteen candidate rewards per generation, each trains SAC and IQN-SAC agents, candidates are ranked on a
held-out CVaR-penalised Sharpe, and a reflection goes back for the next generation. My contribution is
the reflection's content: quantile statistics from the IQN critic — a CVaR profile, tail skewness,
left-tail slope — against a scalar-only control at matched compute. Novelty checked by three literature
sweeps, hedged as "to the best of our knowledge".

Where I am: the engine and the data platform are built and tested — 114 tests green. I've run real data
through it end-to-end: a 5,282-day panel, every artifact checksummed, embargoed splits matching the
pre-registration exactly. The profiling justifies the design — excess kurtosis up to fifty on Citigroup
through the GFC, Hill tail indices near three across all names: variance genuinely understates the risk,
which is why selection is CVaR-penalised. Caveat: that's the shadow universe — point-in-time membership
waits on one LSEG entitlement flag; the escalation is drafted and the pipeline back-fills automatically.

The design freezes Friday: pre-registered hypotheses, budgets, splits, and a Deflated-Sharpe trial count
over *every* candidate evaluated — so even a null result is a publishable, diagnosed result. That was
your guidance and it's structural now.

**The one decision I need from you: ICAIF 2026 — the deadline is 2 August, a month before the
dissertation. Do we aim the main track, a workshop, or dissertation-first and submit later? My fork
decision is due around 19 June, so your steer this week or next sets July's intensity.**
