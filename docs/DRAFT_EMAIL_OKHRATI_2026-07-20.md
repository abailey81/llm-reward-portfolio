# DRAFT — email to Dr Okhrati (for Tamer to edit + send, target 2026-07-21)

Subject: Pre-data design revision (v2) — sign-off requested by Fri 26 July

Dear Dr Okhrati,

Ahead of the confirmatory campaign (no data has been collected; the sealed test window is
untouched), I received detailed feedback from my industry supervisors at NatWest's AI R&D group
(reproducibility permanence, open-weight models, multi-model evidence). Acting on it, I have made
a documented pre-data revision to the pre-registration — v1.0 was formally superseded and the
change is recorded as dated amendments (R79–R82) with the full decision trail in the repository.

What is UNCHANGED — everything you approved: the confirmatory author (Claude Opus 4.8), the seven
arms, the m=6 testing family, the two co-primary intersection–union tests, the ±0.05 SESOI, and
the E1 winner-seed ladder with its exogenous stopping rule. On current throughput the ladder's
likely landing remains the 403-seed / 95%-assurance rung you approved.

What is ADDED — all report-only, none of it gating the confirmatory hypotheses:

1. Nine replication "legs": the same five feedback arms authored by nine further models (six
   open-weight — DeepSeek V4-Pro, GLM-5.2, a Qwen 27B/9B within-family pair, Nemotron 3 — plus
   Haiku/Sonnet forming a within-family capability ladder with Opus, GPT-5.6's budget tier, and
   Gemini Flash as a stretch seat), each at the 30-seed floor tier, queue-ordered with a
   pre-declared calendar gate. This converts the single-family limitation (B.3.1) into a measured
   cross-model result and, per a first-hand survey of the literature I can share, would be the
   first systematic open-weight replication suite in this line of work.
2. A pre-registered, dependence-aware cross-model synthesis (the legs share the panel and the
   CRN seeds, so the replication count is reported descriptively and inference uses a per-seed
   joint-flip permutation test), plus a registered capability-gradient prediction.
3. A 30-USD planning ceiling on total LLM spend, tracked per-call in a cross-provider ledger
   and reported in full (the design's exogenous stops are the seed-rung rule and the leg
   calendar gate).
4. An interim floor-tier report to you (~6–8 August, clearly labelled provisional) — with the
   protocol registered that post-launch feedback informs presentation only, never data-collection
   decisions, so the single-confirmatory-look discipline is preserved.

The revised registration re-freezes (new hash, publicly deposited with a DOI) before any launch.
I would be grateful for your sign-off, or any objections, by Friday 26 July so the campaign can
launch on the 28th; given the compressed window, if I do not hear from you I will proceed under
the permissions you kindly granted and treat any later concerns as dated amendments.

The one-page revision record and the model-selection evidence are attached / available on request.

Best regards,
Tamer
