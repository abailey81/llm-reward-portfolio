# Notes — Eureka (Ma et al., ICLR 2024)  [core paper #1]
Pinned facts (verified via deep-research harvest): Alg.1 loop; N=5 iterations × K=16 i.i.d. samples ×
5 restarts; backbone gpt-4-0314 (snapshot-pinning precedent); reward must expose a COMPONENT DICT;
reflection = per-component scalar time series at checkpoints + fitness F; F separate from reward
("lacks credit assignment" as training signal); 83% of 29 tasks beat human experts, +52% normalised;
evolution > same-budget sampling; human-init uniformly helps.
**VERIFY before first run (plan F5 / notes task):** copy VERBATIM Prompts 1–3 (App. A) and a full reflection
example (App. G.1) from the arXiv PDF + repo `prompts/` dir into this file; confirm sampling temperature.
**Our deltas (the three finance-forced mutations):** out-of-sample fitness (no oracle), regime-contextual
reflection, mandate conditioning. Plus the distributional channel (the contribution).
