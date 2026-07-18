# Campaign-author model sweep — 2026-07-18 (fresh, unbiased; pre-freeze decision input)

> Commissioned by Tamer ("very deep research… don't be biased towards any of them"). Method: one
> web-research agent over vendor pages, API docs, and July-2026 leaderboards; primary sources
> preferred; unverified items quarantined. Full detail in the session record; this file is the
> decision-grade condensation.

## VERDICT: the campaign author stays **Claude Opus 4.8** (`claude-opus-4-8`) — now on fresh
## evidence, not default inertia. (ADR-056.)

**Why it wins on the fixed criteria (code > numeracy > reproducibility > cost):**
- Strongest INDEPENDENTLY-verified coding record of any available model for this role as of
  today: SWE-bench Verified 88.6%, SWE-bench Pro 69.2%, **LMArena coding leader (~1582 Elo,
  July 2026)** — a full month of third-party validation.
- No operational confounds: **no refusal classifiers** (a mid-campaign refusal would break arm
  symmetry — an experimental-validity threat, not an inconvenience), no data-retention
  precondition, no preview-endpoint churn, one stable canonical id.
- ~$10.50 total authoring spend for ~300 calls ($5/$25 per MTok).
- API behavior already handled by our client: `temperature`/`top_p` rejected on Opus 4.7+ →
  diversity is prompt-side (our per-provider diversity design, ADR-038); prompt-cache minimum
  4096 tokens ⇒ caching physically inert at our prompt sizes (disclosed, R-existing).

**The honest runners-up and why not:**
- **Claude Fable 5** — the outright frontier (SWE-Pro 80.3, GDPval-AA 1932) but: safety
  classifiers can return `stop_reason:"refusal"` (arm-asymmetric interference risk in a
  pre-registered design), 30-day retention requirement, always-on thinking (minutes-long turns
  × the reflection chain; thinking billed as output → real cost 2–4×). **Disposition: joins the
  M2 survey roster** — there a refusal is *data* (a recorded outcome), not a confound. The
  methods section gets one sentence answering "why not Fable?" on exactly these grounds.
- **GPT-5.6 Sol** (GA Jul 9) — nine days old, **no independent classic benchmarks published**,
  hidden reasoning-token billing, snapshot strings unverified. Banking a pre-registered
  campaign on launch-week vendor claims is a weaker evidentiary position. M2 roster instead.
  **All GPT-5.5 references in plans/prose must update to GPT-5.6 or be explicitly dated —
  GPT-5.5 is superseded (Jul 9) and would read stale to a late-2026 examiner.**
- **DeepSeek V4-Pro** — LiveCodeBench #1 (93.5), MIT weights (the strongest possible pin),
  ~$0.52 total. But the design REJECTED DeepSeek on contamination grounds (dated decision) and
  re-opening that audit for the primary author is not worth it days before freeze; China-hosted
  API adds a governance surface. M2 roster candidate.
- **Gemini 3.1 Pro** — frontier tier still Preview-only; Google killed two 3.x previews in
  June. A pre-registered study cannot cite a non-guaranteed endpoint. No.
- **Grok 4.5 / Kimi K3** — 10 and 2 days old respectively; K3 weights not yet released; UK
  availability of Grok unconfirmed. Watch for the M2 roster.

## Unverified (never cite as fact)
Fable-5 SWE-V 95.0 (single-sourced) · GPT-5.6 dated-snapshot strings · GPT-5.6/Grok-4.5
AIME/SWE-V scores (unpublished) · Opus-4.8-specific AIME (only Opus 4.6's 98 is sourced) ·
Grok 4.5 UK access · Kimi K3 weights (promised Jul 27) · an explicit Anthropic immutability
guarantee for canonical undated ids (docs treat ids as fixed; one methods-sentence discloses
this).

## Write-up actions (into the wording batch)
1. Methods: one sentence on the model choice date + the "why not Fable 5" grounds.
2. Replace/date any GPT-5.5 "frontier" references (→ GPT-5.6).
3. Disclose the canonical-id pinning convention (no date-suffixed snapshots on current
   Anthropic models) + the retention/classifier facts for the M2 roster models when M2 runs.
