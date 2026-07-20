# Response brief — Raad (Head of AI R&D) & Stefan — how your feedback changed the study
_Tamer Atesyakar · 2026-07-20 · MSc dissertation, UCL (supervisor Dr R. Okhrati)_

Thank you both — your call on the 19th triggered a formal pre-data design revision (the
pre-registration was unfrozen with a dated decision record and re-freezes before launch).
Point-by-point:

| Your point | What happened |
|---|---|
| "Test different models / families of LLMs" | **Adopted structurally.** 10 models now run the full experiment: one frontier confirmatory + 9 replication legs incl. two within-family capability pairs (Qwen 9B↔27B open; Haiku↔Opus closed); a further ~25 models run the cheap reading-link survey. |
| "Use open weights; current studies use open/cheap models" | **Adopted — and tested.** Six legs are open-weight (MIT/Apache), hash-pinned, provider-pinned. We also surveyed the literature first-hand: in our specific lineage, 15/15 published papers used closed primary authors (table available) — the open-weight norm dominates the adjacent fine-tuning literature. Our design therefore does both: the lineage-standard closed confirmatory PLUS what the lineage has never had — a systematic open replication suite. |
| "Opus is expensive/slow" | The measured authoring bill for the whole campaign is ~$6–16 (~180 short calls); GPU training, not the LLM, is >99% of cost. We nevertheless adopted the discipline: **total LLM spend is tracked per-call in a cross-provider ledger against a $30 planning ceiling and reported in full** — the whole ~35-model study runs for roughly thirty dollars. |
| "Ensure amazing reproducibility" | Three layers, stated exactly: analysis = bit-exact replay from archives; protocol = fully re-runnable (open code, frozen prompts, synthetic-data path); experiment = the open legs + hash/provider/quantization pins + vendors' deprecation policies cited + the pre-registration deposited publicly (DOI) at freeze. |
| "Analyse what models papers use" | Done first-hand: the 15/15 table with per-paper version-pinning and cost-reporting norms. |
| "Outline success metrics / what to measure so the method is useful" | Registered study-level success metrics (decision-grade verdict rate; instrument precision; replication coverage; budget/schedule adherence reported as results) + a measurement-to-decision map: the responsiveness audit ("is your model using what you feed it — test before you build"), the bounded-value verdict ("is this feature worth building"), the legibility/guided-comparison probes ("is the fix a renderer or a sentence"), and the per-model authoring-reliability table ("which models write executable objective code at all"). |
| "Good vs bad approaches" | A named "Practitioner's checklist for LLM-in-the-loop feedback" section, built from the above. |
| "Multiple papers" | Four, by design: the main study (TMLR track); "Do LLMs read the numbers you feed them?" (evaluation venue); "The $30 open replication suite" (ICAIF/workshop — we would value your input on this one); the evaluation protocol itself. |

One respectful push-back, with the evidence — on the point that cheap/open models make the study
*more credible*: that is true for one kind of credibility and false for another, and the design
separates them. **Credibility of the finding:** our predicted result is a null, and a null on a
cheap model is uninformative — reviewers read it as "the author couldn't use any feedback well"
(the capacity artifact; REvolve, ICLR 2025, states exactly this: the closed frontier model "was
a necessary choice" given the reward-design capability gap — and 15/15 published papers in this
lineage made the same choice). The frontier seat is what makes the null *mean something*.
**Credibility of reproduction:** here you are right, and the design delivers it in full — the
cheap/open models run the complete experiment (five open-weight legs, weights-hash + provider +
quantization pinned, ~$1–4 each: permanently re-runnable by anyone), every frontier-model call is
archived verbatim so the closed leg's entire analysis chain replays bit-exactly even after model
retirement, and the vendor's dated retirement floor + weight-preservation commitment are cited.
Because both kinds of model run the same frozen experiment, your suggestion becomes a *measured
result* rather than a design opinion: if the cheap models replicate the bounded null, the finding
is general and the reproducible legs carry it — your standard satisfied in full; if they do not,
that is the capability-gating discovery only the frontier seat could reveal. Either way the
study answers the question you raised, with evidence.

You will receive the interim floor-tier results pack ~6–8 August. Thank you again — the study is
materially stronger for the call.
