# Changelog

All notable changes to this repository. Format follows Keep a Changelog; this project is pre-versioned
research code, so entries are grouped by session date. Every entry cites its ADR where one exists.

## [2026-07-22] — ★★★ THE FREEZE CYCLE (R93→R94) · K3 SEATED (R95) · the roster of record · post-churn consistency pass

- **The handoff system made SELF-VERIFYING (the smart-continuity upgrade):** `docs/HANDOFF.md` §1
  now carries a machine-readable `handoff_state` block (regenerated_utc / head / frozen / legs_n /
  amendments_through / suite_status / gate_checks / backup_branch); NEW `scripts/update_handoff.py`
  regenerates it from LIVE facts in one command (git HEAD, the `frozen:` flag, the legs.yaml count,
  the highest amendment row — `--suite-status` stays a required human input, verify-then-claim);
  the SessionStart hook (`scripts/resume_brief.py`) now DIFFS the block against the same live facts
  at every boot (stdlib-only, fail-safe, HEAD-tolerance = last 3 commits so the snapshot commit
  itself never false-alarms) and prints a LOUD per-field staleness warning or a one-line CURRENT
  verdict; both paths verified live (injected head+legs_n mismatches detected, restore clean);
  the hook's closing pointer now names the full read order + all four END-duties; CLAUDE.md
  protocol duty ① names the script. **11th full-suite certification exit 0** (background run,
  post-audit-battery).

- **R93 freeze-day preparation, all evidence-backed (`30ae72b`):** the five HF weights pins FILLED
  from the official HF API (licenses independently re-verified MIT/MIT/Apache/Apache/OML;
  hash-bound record `model_suite.hf_pins_recorded`); the R84 anchor table applied DISCRETION-FREE
  (at-freeze {qwen27: 77.2, haiku: 73.3}; every other leg MISSING by rule — the DeepSeek Max-mode
  80.6 conflation refused); the K3/Opus-5 conditional windows re-anchored to the LAUNCH-GO day;
  the Aug-14 leg gate confirmed; R80 gate timing → PRE-LAUNCH (credit-gated; branches
  pre-declared); the Okhrati sign-off invariant → before-LAUNCH with default-proceed; the
  freeze-due novelty probe CLEAN. **THE FREEZE EXECUTED** on Tamer's twice-given explicit
  permission (ccf2e76f, verified [MATCHES]) — then **LIFTED the same day (R94, `79f4347`)** on his
  clarified instruction: the freeze now executes TOGETHER WITH the full-campaign-run approval
  (GO-sequence step 1), never before. Pre-data, integrity-clean; the ccf2e76f records preserved;
  the state scalars are hash-excluded, so the GO-day freeze RE-STAMPS the same hash if no design
  change lands. Launch was never touched.
- **R95 (`7439ece`): KIMI K3 SEATED as leg 10** — re-researched on Tamer's challenge: live on
  OpenRouter ($3/$15, 1M ctx; two-keys rule holds) with a CANONICAL DATED slug
  `moonshotai/kimi-k3-20260715` (stronger pinning than the undated closed legs); the Luna
  stability precedent; the Jul-27 weights upgrade it to open-class by the pre-declared
  `kimi_k3_upgrade_rule`. **10 legs + Opus = 11 full-loop models**; K3 last (truncates first).
  Earlier the same day: **R92 (`c56c402`)** removed sonnet-4.6 on Tamer's instruction (the
  pilot-bridge prediction WITHDRAWN pre-data; the R90 generation pair re-scoped to the
  conditional Opus pair; sonnet-4.6 retained in M2; Qwen-9B retention re-affirmed; the
  freed-seat alternatives sweep registered).
- **The roster of record (`721ed2d`):** `docs/MODEL_ROSTER_2026-07-22.md` — the 11-model
  full-loop matrix (status/pin-grade/architecture/prices/costs/functions/truncation order), the
  three instruments, the rule-driven seats, the ~34-row M2 survey by family ladders, the
  excluded-by-design table, the money page (~$28 expected all-in). Feeds CH4 registry row 2.
- **Post-churn consistency pass (this entry):** the roster churned three times in 24 h; the
  sweep found + fixed six stale surfaces — CH6 §6.7 "Nine further"→Ten + §6.1 "k of 9"→10; the
  DEAD R90 generation-pair slot in §6.8 → re-scoped to the conditional Opus contrast; gemini's
  "first-to-truncate" role notes (both yamls) → K3 truncates first now; the launcher header
  ("ten lines") → TWELVE (core + h3 + 10 legs) + the runbook count parenthetical; the handoff
  roster table/queue/M2 counts (+ the K3 row); the cross_model docstring cite. §14 prose
  updated to ten legs incl. K3.

- **R96 (`b6d0fb7`): the OPTIONAL M2 psychometric module** fully pre-specified (Axis A: 2AFC
  delta-ladder JND per full-loop model + THE OVERLAY — the share of realized fed deltas below
  each model's resolution limit, the mechanism's quantitative closure; Axis B: the census-frame
  ecosystem map, ~100–130 bases, psychometrically linked short form; activation = Tamer's dated
  write-time decision with the ALL-OR-NOTHING reporting clause; registry row 25).
- **THE HANDOFF SYSTEM (this entry):** `docs/HANDOFF.md` = the new canonical entrypoint
  (regenerated §1 state snapshot · §2 standing orders · §3 the authority map — one owner per
  truth · §4 the R78–R96 one-line ledger · §5 first actions); V2_HANDOFF bannered historical;
  CLAUDE.md gains the ★ SESSION HANDOFF PROTOCOL (start/end duties incl. regenerate-§1,
  ≤15-line cursor entries, CHANGELOG blocks, the backup push; + the hard-won lessons: PS1
  ASCII+parse-check, no `git add -A`, no backslash heredocs, R-row ordering, name-needs-value).
  **Final audit battery:** gate 21 OK · citations clean · rung-freshness green · backup==HEAD ·
  three stale spots fixed (runbook §10 expectations/line-count; §14 n=9→10) · the freeze-written
  `prereg-v1.0.sha256` restored to its v1 content (the GO-day freeze writes its own) · the 10th
  full-suite certification green.

## [2026-07-21d] — ★★★ MODE-D FINAL PASSES + THE RAISED BAR + R89–R91 (freshness) + the completeness sweep

- **Mode-D 2nd/3rd/4th passes (`26caaf6`, `1922e27`, `0643df2`):** the training-latency anatomy —
  the floor's TRUE critical path identified as the 30-step BO chain (honest correction: floor ≈
  L+1.5–1.8, not L+1.3) → bayes_opt hoisted to −p 0 (`_core_priority`, unit-tested) + chain-lane
  polling (`--search-poll-secs 45`); the H3 single-shot FLOOR unit added as launcher line 12
  (the last manual dependency on every rung bank — day-0, seeds 0–29 only so H3 rung seeds never
  jump the legs; ladder completion = documented follow-up); **canary-concurrency** — the C0
  canary gates only what it protects (Opus authoring): family arms + baselines start at L+0
  (the suite then CAUGHT a real race this introduced — canary-covered baselines double-submitted
  → now excluded, dedup asserted); launcher CANARY SHIELD (legs +1h). Evaluated-and-REJECTED
  recorded: torch.compile (env-loop-bound per the pack curve), pre-gate baseline flood
  (early window saturated), pack-1 search, per-unit rung release (the gate's protection kept).
- **THE RAISED BAR (`9974d62`, `5b7cc5b`; memory: project-grade-inflation-adjustment-2026):**
  supervisor-confirmed grade-inflation adjustment (last year's distinction ≈ this year's merit)
  → guidelines re-read first-hand; registry rows 19–24 (SESOI justification; H4 prominence +
  Coache–Jaimungal; 60%-core re-check; independence narrative; demonstrable publishability; the
  any-discipline reader gate); **D6–D10 drafted at submission quality** (the five keystones now
  exist as prose); D3's stale 200k→400k fixed.
- **R89–R91 freshness (`47585b3`, `27d5c30`, `c7987ca`; web-verified as-of-today):** every leg
  pin re-verified CURRENT; M2 extras +2 (sonnet-5, qwen4-coder); **R90: claude-sonnet-5 promoted
  to LEG seat 9/10 → the GENERATION PAIR (sonnet-4.6 ↔ sonnet-5; 11 full-loop models; ladder
  −200…−290; 13 launcher lines)**; the Fable-5 confirmatory swap analysed and DECLINED
  (classifier fallback = a treatment-correlated interference channel; the June suspension = the
  permanence contradiction); **R91: the Opus-5 leak (Honeycomb EAP) converted to a pre-declared
  conditional seat** (GA + API id + gates + verifiable single-author attribution — the leaked
  4.8-fallback routing would FAIL it on the Fugu principle → the second generation pair if it
  fires; the confirmatory stays Opus 4.8 regardless).
- **The completeness sweep (this entry):** ★ **the unpushed-history existential risk CLOSED** —
  the local sole-author-rewritten history (all of today's work) shared no commits with origin;
  a NON-destructive `backup-2026-07-21` branch pushed (Tamer's force-push decision untouched);
  disk/commit-headroom re-verified green (C: 25.8 GB > the 20 GB floor; commit 14 GB > 6);
  the concurrent-session Ramin brief given minimal currency fixes (9→10-leg family ×2 + an
  R88–R91 currency note; left uncommitted as found); CH6 §6.8 gains the generation-pair slot
  (+ the conditional Opus-pair line); runbook §10 gains the MODE-D SYNTHETIC MINI-REHEARSAL as
  a named pre-launch step (the 13-line concurrency is the one unrehearsed surface).
  Six full-suite certifications today; gate 21 OK throughout.

## [2026-07-21c] — ★★★★ PRE-FREEZE DEEP SWEEP (R84–R88) + MODE-D MAX-PARALLEL + the consistency audit

**Tamer's directives:** deep-analyse the design/structure/feedback for every closable gap ("nothing
is frozen, anything could be changed"), then "global minimum for the training time" on Myriad
(everything-on-Myriad; no RC share request), then a full consistency/bug audit. Three commits +
this audit's fixes; full suite GREEN after each wave.

- **NatWest brief reframe (`4d233db`):** the push-back rewritten to the TWO-CREDIBILITIES argument
  their actual claim ("cheap models = more credible") deserves — finding-credibility (a null on a
  cheap author is a capacity artifact; REvolve verbatim + the 15/15 survey) vs
  reproduction-credibility (conceded and DELIVERED: pinned open legs run the complete experiment
  ~$1–4 each; verbatim call archives make even the closed leg's analysis chain replay bit-exactly
  post-retirement); the synthesis turns their suggestion into a measured result on either branch.
- **DEEP-SWEEP AMENDMENTS R84–R87 (`e16fad2`; every finding evidence-cited):** R84 pins the two
  registered-name-without-registered-value forking paths (capability anchor → the SWE-bench-Verified
  discretion-free retrieval rule, missing=excluded-never-imputed, M2-circularity named; T0
  leg-inclusion floor → equal_weight mean per-seed Sharpe on seeds 0–29 + the arm-symmetry
  size-preservation argument registered ex-ante). R85 lands the adopted-but-absent permanence
  mechanics: HF weights pins REQUIRED per open leg (`freeze.py::pending_hf_pins` REFUSES the real
  freeze while TO-VERIFY placeholders remain; `--check` surfaces "PENDING ×5"), the fp8
  served-variant disclosure, temperature=1.0 pinned on OpenRouter legs (decoding uniformity — the
  prior "provider default, recorded" was partially unfulfillable), Gemini's undocumented
  `budget: default` reasoning key REMOVED (silent-ignore = fictional pin) → provider-default
  DISCLOSED, and the reasoning-pin ROUND-TRIP evidence (leg_gates archives usage incl. reasoning
  tokens; `pin_roundtrip` verdict, UNVERIFIED→review). R86 registers the synthesis's missing
  equivalence tier: `cross_model.pooled_bound` = the 90% seed-block-bootstrap CI on the pooled
  CVaR diff (dependence-honest — property-tested: k identical legs yield ONE leg's CI), absolute +
  relative-to-scalar-CVaR; the leg TOST family pinned to the CVaR contrast; the capability
  regression labeled DESCRIPTIVE with the pair DiDs as the identified estimates. R87 makes the
  gradient prediction FALSIFIABLE (three ex-ante signatures: capacity=rising /
  representational=flat-at-zero=THE registered prediction / echo=decreasing — the prior "monotone
  non-decreasing" was near-unfalsifiable AND named the rival account's signature) + the ex-ante
  sonnet-bridge direction (≤0, the pilot's). Plus: the ADR-060 OpenRouter entitlement addendum
  (six derived aggregates only; the account do-not-log toggle), registry rows 14–18 (word-budget
  APPENDIX-FIRST re-plan vs the 10k cap; REvolve/GEPA/METR verified ABSENT from refs.bib →
  evidence-grade row; novelty-fence scope + due-at-freeze; 6 limitations rows; the plain-language
  paragraph), runbook §9(f) Anthropic top-up resized ≥$35 (the $25 was Opus-only; the Haiku+Sonnet
  legs push the worst case ≈$28–30) + §9(g) freeze-day decisions, Okhrati email dates made relative.
- **MODE D (`131a8e2`, R88 — ops-only):** maximum-parallel execution built on first-hand-verified
  structure (C1–C3 already concurrent; random_search floods; BO inherently sequential and already
  pack-1). (1) Phase-adaptive packing: `--search-pack 2` runs the 6-deep reflection chains in a
  latency lane (auto-sized tight h_rt 5:0:0 = prime backfill; ≈halves chain latency at ~2–4%
  GPU-time) while bursts keep pack-5; legacy None byte-identical (strict-fake test). (2) Pipelined
  C4 (`--pipeline-rungs`): all assurance blocks eligible at once under the descending ladder —
  tier-100 at −100 ABOVE the legs, tier-189+ from `PRIORITY_RUNG_BASE` −300 BELOW them (fixing the
  wiring where rungs-at-0 would starve the legs against the registered queue); barrier-proven
  concurrency test; banking semantics untouched. (3) `mode_d_launch.ps1` = ONE command spawning 10
  self-healing supervised lines (ladder −200…−280, tags leg1–9, 20s poll stagger, shared STOP).
  (4) R88 registered (`model_suite.queue_semantics` + row): queue order = a PRIORITY LADDER;
  completion/truncation order = the pre-declared queue. Expected: all 9 legs ~L+3–4 (was L+8.8),
  tier-403 ~L+12–14 (was L+16.5). Both mode-D lines dry-ran GREEN on real gold; the lane check
  hoisted into the keyless pre-flight.
- **CONSISTENCY AUDIT (this commit):** (a) CONFIRMED BUG FIXED — any `--root-suffix` invocation
  (every leg line; the C6 dose class) sharing `--output-dir` CLOBBERED the headline
  `campaign_summary.json` the watcher/analyze read (the exact hazard the H3 path guards against
  for itself) → summaries now namespaced `campaign_summary_<suffix>.json`; (b) mode-D PS1s
  PARSE-VALIDATED — the supervisor had 5 real parse errors (em-dash bytes read as cp1252 smart
  QUOTES under BOM-less UTF-8 in PowerShell 5.1, closing a string early) + a `$args`-shadow splat
  bug introduced by the rename (the driver would have launched with NO arguments); both now
  ASCII-clean, `@driverArgs`, 0 parse errors (the legacy supervisor re-verified 0 too);
  (c) shared-state hazards for 10 concurrent drivers verified SAFE by inspection (per-batch driver
  locks, per-batch heartbeat files) with the summary the one real collision (fixed); (d) M2 loader
  key (`extras_budget_permitting`) verified; the leg (non-tiered) path verified fully concurrent
  per-arm; (e) citations gate clean; V2_HANDOFF de-staled (+4 rows, Gemini pin row, heading);
  §14 gains the R85 pin clause.

## [2026-07-21b] — ★★★ V2 BUILD COMPLETE (steps 7–8 on Tamer's "Build") + the four-authority rule + full-suite certification

**Session shape:** deep resume (both handoffs + all v2 authorities re-read first-hand) → two
fix-on-sight defects closed → Tamer's "Build" → steps 7–8 (the last two) built sequential-solo,
each verified then committed → full suite GREEN (exit 0, 3 POSIX-only skips). All 8/8 v2 build
steps are now done; the only remaining items are Tamer's (Okhrati email, OpenRouter top-up,
freeze GO, launch GO).

- **R83 consistency fix (`5c7f50c`, fix-on-sight):** PREREGISTRATION.md §14 prose still said the
  spend ceiling was "hard-capped, enforced in code, trimmed" — the R83 softening had updated the
  yaml comment + both external drafts but missed this sentence. Reconciled to the advisory
  wording (tracked per-call, warned 80/100%, never refused, reported in full). No decision
  changed; gate re-verified 21 OK; repo-wide grep confirmed no other stale site.
- **★★★ THE FOUR-AUTHORITY STANDING COMPLIANCE RULE (Tamer's instruction; CLAUDE.md, which is
  gitignored by design — the rule lives on disk and auto-loads every session):** every
  substantive decision is checked explicitly against (1) the ★ PRIORITIES (they arbitrate
  conflicts), (2) Dr Okhrati's revealed grading function (chapters drafted AGAINST it), (3) the
  Raad+Stefan six points (structural adoption; registry-tracked, none silently droppable), and
  (4) the IFTE0008 guidelines read first-hand (weakest-dimension-caps, 10k body, 16-section
  order, any-discipline second marker). Enforcement: per-chapter four-authority check at write
  time + zero-open-registry-rows at pre-submission; the guardrail preserved (industry feedback
  never weakens confirmatory logic / identification / mechanism depth).
- **STEP 7 (`e968cdd`) — results machinery v2:** CH6 gains §6.7 (replication suite: leg
  completion/truncation, per-leg contrasts → Table 6.6, T0-floor inclusion semantics, the
  authoring-reliability Table 6.7, the ten-winners exhibit) + §6.8 (synthesis: descriptive sign
  count, pooled-mean joint-flip permutation, family-pair DiD, capability regression,
  generation-indexed SQ1, leg-family BH, the g(capability) bridge — closing with the explicit
  cannot-alter-§6.6 sentence) + achieved-rung/realised-power + leg-execution/spend slots in §6.1.
  **The rung-freshness convention, previously named but never DEFINED, is now concrete
  (reporting rule 5: `<!--RUNG:n-->` core / `<!--LEG-TIER:30-->` legs) and MECHANICAL:**
  `scripts/check_rung_freshness.py` (per-rung mode fails stale tags; `--final` also fails
  unfilled `[FROM CAMPAIGN…]` slots; the achieved rung comes from a flag or
  `outputs/tables/achieved_rung.json`, never assumed; validated against the frozen E1 ladder;
  DRAFTS_ excluded; 7 behaviour tests + a live green run on the real paper dir).
  FIGURE_TABLE_MANIFEST v2: F12 cross-leg forest / F13 capability-gradient scatter / F14
  reliability heatmap / F15 ten-winners exhibit + T6/T7 + honest-null renderer notes. The four
  renderers land in `src/viz/figures.py` matching the `cross_model`/`leg_aggregate` contracts
  (excluded legs greyed-never-hidden; the permutation *p* is a forest's ONE inferential number;
  NaN renders "—" never fake-zero; winner highlights = the fixed registered
  `TAIL_CONSTRUCT_PATTERNS` regex set, never curated; byte-determinism tested). One layout fix
  mirrors the `reward_code_similarity` precedent (no `tight_layout` on colorbar figures under
  the house constrained-layout engine — caught by cross-module test ordering). 15 new tests.
- **STEP 8 (`7bf1fa7`) — leg LAUNCH wiring + runbook v2 + dry-runs. ★ WIRING GAP FOUND + CLOSED
  during verification:** the legs were UNLAUNCHABLE — `load_legs`/`transport_kwargs` were
  consumed only by `leg_gates.py`, and BOTH author-construction sites
  (`parallel._drive_llm_arm` + `cluster._build_cluster_author`) dropped `extra_body`, so an
  OpenRouter leg would have authored with its registered provider/quantization/reasoning pins
  SILENTLY STRIPPED (pin loss = registered-design violation). Closed end-to-end:
  `run_campaign_cluster.py --leg <label>` (the SAME `transport_kwargs` translation the gates use
  — one translation point, no drift; FORCES the sanitized `leg_<label>` root-suffix = the
  `leg_aggregate` disjoint-roots contract; conflicting explicit suffix refused; `--llm-from
  prototype`/`--h3-singleshot` combos refused; provider-derivation log names the leg source);
  `extra_body` + `spend_ledger` threaded through `build_parallel_opts` into both author sites.
  **The R83 per-call author ledger** (the REGISTERED "tracked per-call" behaviour, previously
  gates-only) now lives at the `LLMClient.complete` chokepoint: realized cost (OpenRouter
  `usage.cost`) else the tokens×planning-prices estimate (`spend_ledger.estimate_cost_usd`;
  `claude-opus-4-8: [5.00, 25.00]` added to legs.yaml planning_prices) — best-effort,
  rate-limited-warn, NEVER crashes a paid call; fakes/stubs surface no metadata and stay
  ledger-silent (suite-clean by construction). **Runbook §9** (day-runbook): the leg queue —
  the gates command, the EXACT per-leg launch line (5 LLM arms, `--seeds 0-29` = the common-30
  CRN subset the pair-DiD needs, `-p -200`, no `--tiered`/`--baselines`), per-leg monitoring
  rows, the spend-summary one-liner, the per-leg bank-gate + aggregation path. **DRY-RUNS GREEN
  ON REAL GOLD:** the exact §2 core line (7 arms, 568 seeds, tiers [30,70,89,90,61,63,165],
  windows == frozen `expected_windows`) + two leg lines (deepseek → suffix `leg_deepseek_v4_pro`;
  qwen3.6 → `leg_qwen3_6_27b`; providers derived correctly). 10 new tests
  (`tests/test_leg_launch.py`) + a regression sweep over
  leg-gates/transports/cluster/campaign/prototype/parallel-resume/freeze: exit 0.
- **Certification:** freeze gate **21 OK** (incl. the leg-roster guard, post-legs.yaml-edit),
  ruff clean on every touched file, **FULL SUITE GREEN (exit 0, [100%], 3 POSIX-only skips)** —
  run twice this session (baseline at resume + certification after steps 7–8).
- **⚠ Open (external):** cluster sync VPN-BLOCKED (ssh timeout; recorded — GO-sequence step 3
  re-syncs at launch; the cluster marker is stale until then). Tamer's items: send the Okhrati
  email; OpenRouter ~$5 (gates) / ~$25 (everything); then the freeze GO + launch GO.

## [2026-07-20/21] — ★★★★★ THE UNFREEZE → THE V2 REDESIGN (NatWest feedback) → implementation steps 1–5

**Trigger (2026-07-19 call):** industry supervisors Raad (Head of AI R&D, NatWest) + Stefan —
open-weight/multi-model evidence, reproducibility permanence, cost discipline, success metrics,
multiple papers. Their feedback is now BINDING alongside Okhrati's compass (CLAUDE.md block).

- **THE UNFREEZE (`3db904a`, ADR-059 + amendment R78):** v1.0 (`ce5db62c`) superseded PRE-DATA on
  Tamer's instruction — zero campaign data existed, sealed leg untouched → a documented pre-data
  revision, not a forking path. v1 records preserved (tags/bundle/log). `enforce_freeze` refuses
  real launches until a v2 freeze — which happens ONLY on Tamer's explicit word (no scheduled
  date; his 2026-07-21 instruction removed all date pressure). Freeze-state tests made
  STATE-ADAPTIVE (assert consistency with the live yaml, not a pinned state).
- **THE 8-AGENT MODEL SWEEP (`f88a3d2` + close-out `b9e5c74`, `docs/MODEL_SWEEP_2026-07-20_v2.md`):**
  frontier-closed delta (GPT-5.6 benchmarks/pins; Anthropic deprecation floors + weight-preservation
  commitment = best closed-vendor repro posture; METR: GPT-5.6 Sol = highest reward-hacking rate of
  any public model, 55.4%), open-weight majors (DeepSeek V4-Pro MIT LCB-93.5 #1; GLM-5.2 MIT;
  Qwen3.6 line supersedes the stale 480B pin; 4-rung all-Apache Qwen family gradient), the
  15/15-closed-authors LINEAGE SURVEY (REvolve "necessary choice" verbatim; GEPA ICLR'26-Oral
  closed+open precedent; NeurIPS checklist accepts hosted models; GIFT never names its model),
  exhaustive Chinese labs (~17), rest-of-world (~45 labs), the OpenRouter 339-model census
  (catalog JSON archived; provider-pin mechanics verified; `~latest` aliases = banned), and the
  primary-source LICENSE GATE: **MiniMax-M3 FAILED the open bar** ($20M revenue trigger +
  attribution badge) → its seat fell to the pre-declared fallback; Nemotron = NVIDIA OML (not
  Apache; "major portions" of data released — exact phrasing bound); K3 weightless (watch Jul 27).
- **THE V2 DESIGN (ADR-060; `docs/V2_MASTER_PLAN_2026-07-20.md` + §1b/§2b):** ONE frontier
  confirmatory (Opus 4.8, unchanged core: 7 arms, m=6, IUTs, SESOI, E1 ladder — rung 403 remains
  the likely landing at C=12) + **9 replication legs at tier-30** (DeepSeek V4-Pro [contamination
  gate; GLM absorbs] · GLM-5.2 · Qwen3.6-27B + Qwen3.5-9B [open family pair, SiliconFlow-fp8-
  paired] · Haiku 4.5 + Sonnet 4.6 [closed family ladder; Sonnet = the PILOT BRIDGE] · GPT-5.6
  Luna [effort-low, 2k cap] · Nemotron 3 Super · Gemini 3.5 Flash [seat-10 stretch,
  first-to-truncate]) + M2 reading-link survey at 25 models (+7 extras; inclusion rule) + the
  unified TIER × STAGE × LEG queue (tier-100 hoisted early so the exogenous stop consumes the
  UPDATED σ; leg gate 2026-08-14T23:59Z; Aug-11 Myriad maintenance budgeted +1d). Compute matrix
  banked: leg = 300 tr = 0.63d @C12; 10 models × full 403 ladder ≈ Aug 13–14 @C12.
- **PREREG-V2 RECORDS (`a858b04`):** R79 (model-agnostic prompt-format pass; tail-neutrality gate
  re-verified) · R80 (the model_suite: legs+pins+queue+gates+synthesis+success metrics+feedback
  protocol+interim report) · R81 (spend + presentation-only feedback protocol) · R82 (the
  completeness supplement: uniform max-token pins; exact gate timestamp; synthesis exactness —
  CVaR-contrast sign statistic, T0-floor leg-inclusion, common-30 pair-DiD estimator, leg-family
  BH; M2 guided-comparison + responsiveness-POSITIVE-CONTROL probes; generation-indexed
  responsiveness; Stage-2 qwen9 search replicate; PUBLIC OSF/Zenodo deposit on the freeze-day
  checklist; per-leg bank gates; the g(capability) envelope-gap theory bridge) · §14 v2 prose ·
  `config/m2_models.yaml` v2 (schema-aware loader + `--include-extras`, 25/32 verified) ·
  `docs/V2_WRITE_TIME_REGISTRY.md` (13 binding items) · the Okhrati email draft + the NatWest
  response brief (`docs/DRAFT_EMAIL_OKHRATI_2026-07-20.md`, `docs/NATWEST_RESPONSE_BRIEF_2026-07-20.md`).
- **R83 (`41e9a1e`, Tamer):** the spend system is ADVISORY — `src/llm/spend_ledger.py` records
  per-call cross-provider costs, warns at 80%/100% of the $30 planning ceiling, and NEVER refuses;
  drafts + yaml softened to "tracked and reported".
- **IMPLEMENTATION (sequential-solo per Tamer; agents stopped unused):**
  step 1 `ceadd54` `config/legs.yaml` (9 legs, pins validated vs the registered queue; Qwen pair
  invariant; alias ban; planning prices) · step 3 `99d2901` leg transport (client `extra_body`
  passthrough: provider pins/quantizations/reasoning/usage-cost; `~latest` HARD-REJECT at
  `build_transport`; `last_cost_usd` capture; `src/llm/legs.py` loader; 13 tests) · step 4
  `aa910eb` freeze-gate `assert_leg_roster_match` (**the live gate now runs 21 checks**; order+
  ids+pin-membership+quantization+caps+reasoning-presence+duplicate+alias guards; 9 adversarial
  drift tests) · step 5 `0464b4f` `src/inference/cross_model.py` (T0-filtered sign count; the
  joint per-seed-flip permutation test; pair DiD on the common-30 subset with seed-paired
  bootstrap; leg-family BH; generation-indexed SQ1; capability regression; 15 property tests).
- **★ PRE-FREEZE STATISTICAL CATCH (the property tests earning their keep):** the registered
  permutation statistic was the SIGN COUNT — near-POWERLESS under joint per-seed flips with
  correlated legs (all legs flip together ⇒ unanimity routine under the null ⇒ p≈0.5 even for a
  strong true effect). REFINED PRE-DATA to the **POOLED MEAN difference** (the multivariate
  paired sign-flip test — full power, identical dependence-honest null); the sign count stays
  DESCRIPTIVE; registered text updated in yaml + §14. Second registered-spec defect caught by
  verification before any data (the first: the sign-test independence flaw caught at design).
- **Remaining build (sequential):** step 6 compliance-smoke script + multi-root leg aggregation +
  per-leg bank gates · step 7 CH6 skeleton v2 + figures v2 (forest/gradient/reliability/winners)
  · step 8 runbook v2 + dry-runs + cluster sync. **Tamer's pending items:** send the Okhrati
  email; OpenRouter ~$25 top-up (gates the ×9 contamination screens + author smokes + compliance
  baselines). **Freeze + launch strictly on Tamer's explicit word.**

## [2026-07-18d] — ★★★ THE FREEZE (Tamer's instruction) + notebooks-to-world-class

- **THE PRE-REGISTRATION IS FROZEN** (`068f0e1`, tag `prereg-freeze-ce5db62c` + `prereg-v1.0`):
  `frozen: true`, hash **ce5db62c97b6f79236e5f827ae7ad2df81d8c9df450757df5f066ba4480c58ba**
  stamped 2026-07-18T13:41:24Z at git `c523d77`; gate `--check` verifies recorded == canonical
  [MATCHES]. Bundle `outputs/prereg_bundle_ce5db62c.zip` (73 KB, sha256 `6f9fbfa725ce916e…`).
  Cluster synced: `frozen: true` verified node-side, marker = `068f0e1`. From here every design
  change is a dated, approved amendment; the freeze-aware guard now protects the 8 bound files.
  LAUNCH still awaits Tamer's explicit GO (his two items: Windows-Update pause + top-up).
- **Opus top-up computed from MEASURED archive usage** (160 real authored calls: mean 534 in /
  1,215 out tokens) × the documented $5/$25 per MTok: expected campaign authoring (150 headline
  + 30 H3 = 180 calls) ≈ **$5.95**; absolute worst case at the spend caps (480 calls, driver
  hard-stops) ≈ **$15.86** → recommended top-up **$25** (covers worst case + canary/smoke +
  M2/Qwen headroom).
- **Notebooks to world-class** (`c523d77`): results_walkthrough 44 cells — at-a-glance + TOC,
  REAL §5 budget-curve section (30-point grid re-derived, R77 rule verdict re-asserted, F11
  rendered live), REAL §9 mechanism-kernel exhibit (239 records → per-arm SQ1 fingerprint rows,
  honest at-depth verdicts), §13 machine-checked real-vs-synthetic ledger; provenance notebook
  21 cells / 39 checks + vault-at-a-glance. Both execute-validated on final bytes (0 errors);
  palette re-validated (dataviz six-checks; the one sub-threshold CVD adjacency is the
  hatch+marker-encoded control pair, by design).

## [2026-07-18c] — DEFAULTS-CLASS SWEEP (2 launch-critical catches) · COMMIT-STARVATION FORENSICS → validation handshake (ADR-057)

**The hardcoded-defaults bug class (the B\* instance generalized, all pre-launch):**
- **Catch #1 (launch-critical):** `run_campaign_cluster.py --train-steps None` fell back to
  prototype.yaml's **25,000** instead of campaign.yaml's 400,000 — the whole campaign would have trained
  at 1/16th the registered B\*. Runtime assembly now resolves None from `campaign.yaml
  train_steps_per_candidate` AND hard-asserts it equals the pre-registered B\* (mirror-drift refusal).
- **Catch #2 (launch-critical, NEW):** the auto-`h_rt` sizer read `campaign.agent.train_steps_per_candidate`
  — a key that DOES NOT EXIST — then a stale hardcoded 200000: at 400k every pack-5 array task (~6:09
  needed) would have been sized ~4h and **walltime-killed after burning ~4 GPU-h each**. Now reads the same
  top-level key the assembly resolves; fails loud if missing; `autosize_h_rt()` unit-locked (7:0:0 at 400k).
- The rest of the class closed the same way: `--candidates/--generations/--n-trials/--embargo` argparse
  defaults (30/6/30/21 hardcoded mirrors) → None + resolution from campaign.yaml/inference.yaml with a
  candidates-vs-`matched_budget` prereg assert; a real-spend guard refuses ANY explicit design override
  without `--allow-unfrozen`; laptop-parity documented against run_campaign.py:2134-2151. 7 regression
  tests; exact launch line + H3 dry-runs re-verified green (resolved: 30/6/30/21 + B\* in-assembly).

**Commit-starvation forensics (15 probes; began as "5 cross-file test failures", ended launch-relevant):**
- Symptom: `test_cluster_campaign.py` + `test_run_campaign.py` together → 5 failures ("reward exceeded the
  2.0s validation timeout"); each file alone green. PRE-EXISTED this session's diff (stash-verified).
- Root cause chain, each link verified empirically: validation children were **stalled loading the
  numpy/MKL DLLs** (py-spy stack) because **system commit charge was exhausted** (2.15→0.37 GB across the
  first half of the cluster file; py-spy itself died with "memory allocation failed") — the box's ceiling
  was already low because **ArmouryCrate.UserSessionHelper.exe had leaked 7.61 GB of commit over 8 days**
  (+ a wedged 3.3 GB stale background pytest), and the pagefile cannot grow far on the constrained C:.
  A starved child completed numpy import in ~103 s — the 2.0 s `validate_once` timeout (which clocked
  spawn+import+user-code TOGETHER) then false-failed perfectly good rewards. NOT mp-specific (plain
  subprocess hung too), NOT env/CWD/priority/CPU (all counterfactualed; HIGH-priority child still hung).
- **Why it mattered for the campaign:** the same conflation would (a) reject PAID candidates at authoring
  on a commit-pressured laptop, (b) fail sealed-leg seeds on contended Myriad nodes (the p6ext800 ×0.5
  class), where child startup alone can exceed 2 s.
- **Fix (ADR-057): the three-phase validation handshake.** `src/sandbox/_child_boot.py` (stdlib-only;
  AST-locked by test) boots the child: `ready` (pre-import) → `armed` (numpy+fixture done; fixture ships
  as pickle BYTES so unpickling can't front-load numpy into bootstrap) → verdict. `timeout_s` (2.0 s)
  now clocks ONLY the candidate's code; startup/import get environment graces (45 s/120 s) whose
  exhaustion raises a DISTINCT "spawn environment starved" error — never a candidate rejection. Graceful
  join-before-terminate on the success path. Security unchanged (AST gate, killable child, user-code cap).
  4 regression tests; the formerly-failing pair now 96/96 green.
- **Ops closures:** ArmouryCrate leaker + stale pytest killed (commit 0.37→9.82 GB; standing
  resource-management grant); `preflight.py` gained `check_commit_headroom` (FAIL < 6 GB, live-verified);
  the 4.5 GB StateRepository svchost is flagged for Tamer (admin-only). Campaign authoring pattern itself
  verified clean (validate_once ×100 sequential: no degradation).
- **Post-batch certification:** full suite **2,139 passed + 3 skipped (POSIX-only) = 2,142 = the collected
  count, 0 failed, exit 0** (three-way verified: progress-char census == collection sum, [100%] reached,
  exit code; the final pytest count line does not appear in captured output on this box — counted from the
  progress lines; the 07-13 "2,196" figure is a different counting basis, and no test was deleted since:
  `--diff-filter=D` empty, 0 `-def test_`, +18 `+def test_`). Monitoring arm-up (`96239ad`): ntfy push in
  campaign_monitor.sh + the sentinel — built+certified 07-06 but NEVER armed in the runbook — added as
  §5(e), verified clean against the cluster mirror. Audit trail consolidated: PRE_SPEND_AUDIT addendum
  P20/P21/P22. Cluster re-synced twice; GIT_COMMIT marker `96239ad`.

## [2026-07-13b] — B\* reopened + curve recovery · launch config finalized · dim-4 integration · ALL non-write-up gaps closed · max-throughput levers · walltime-floor revision

**The B\* thread (Tamer's correction: "nothing is closed"):**
- The 1.6M ext rung landed val-DSR **0.187 vs 0.041 @100k, same CRN seed** (verified: same reward
  hash, same 694-day val window, real return-path gain). Evidence-ledger claim 8 DOWNGRADED A−→B;
  claim 15 added; the **extended B\* decision rule PRE-COMMITTED before the remaining curve points**.
- Verdict-INDEPENDENT honesty rewording applied to graded prose (`91a1097`): "convergence pilot"→
  "learning-curve pilot"; "below the (mild-)overfit onset" REMOVED (no onset was ever observed);
  the 25k–350k range stated AS the pilot's measured ceiling. Hash-bound wording held for ONE
  post-verdict batch. Plus 2 claims false on the CURRENT record fixed (`6b05d94`: README
  "measured convergence knee"; determine_design provenance label).
- **Curve-tail PURGE caught live** (p6ext1600b tasks 2–6: no qacct trace; 771972 comparators
  crawling) → recovered via the `--singles` ladder mode (`5bdf247`): 22 one-task arrays, no tail
  to purge. Then **774923 (800k) h_rt-killed at its full 6 h ⇒ that node ran <37 st/s** →
  planning floor revised 51→25 st/s (ADR-055, `bb35478`); 16 at-risk pending singles replaced
  (400k@7h / 800k@12h incl. the dead s0 / 1.6M@24h); the 200k six kept their accrued priority.

**Launch readiness (`7a1e44a`, `ccbe860`, `dc86322`):**
- **C5 H3-single-shot cluster mode BUILT** (P4 closed by the Myriad directive): disjoint
  `*_h3_singleshot/` roots by construction, `h3ss_` batch namespace, −100 priority,
  reflection-never-fires verified, adoption-decoy test.
- **`--root-suffix` C6-class guard**: any report-only re-search invocation gets namespaced
  search/test/frozen roots + prefixed batch names (the P4 hazard class closed generically);
  `--priority` threaded through the non-tiered pipeline.
- **STRIPED seed-pool blocks ratified** (delegated): both pools engaged ~50/50 at EVERY ladder
  rung (the contiguous split idled the A100s until seed 284); the parser merges repeated pool
  names (two same-name arrays would collide on P12 locks).
- **CHUNKED SUBMISSION (`--chunk-tasks`, ADR-054)**: the snx=1 serialization policy is ACTIVE —
  big arrays crawl at ~1 task/2 h regardless of free GPUs; every round now submits as many small
  arrays; drain/P13 evidence follows the parts; launch lines carry `--chunk-tasks 1`.
- **`scripts/author_smoke.py`** — one-call Opus pre-flight via the campaign's own transport;
  LIVE-VERIFIED (claude-opus-4-8, key valid, account funded, 3.1 s).
- **A100 pack probes submitted** (785630 pack-5 / 785631 pack-8, pool L — the F-curve was
  V100-only; ledger claim 16). Dry-run now validates the tiered seeds schema + block spec; the
  EXACT launch and H3 lines dry-ran GREEN on real gold.
- **`docs/CAMPAIGN_DAY_RUNBOOK_2026-07-13.md`** = the single operative launch document
  (preconditions, pre-flight, verbatim commands, monitoring + C measurement, resume/abort,
  bank gate). Bank-gate flags in it corrected to the TRUE argparse contract.

**Dimension-4 + gap closures (Tamer: "close absolutely all gaps except the write up"):**
- **D1–D4 integrated** (`9d7a334`): plain-terms paragraph → CH1; outward positioning (honesty-
  softened "to our knowledge") → FRAMING; **the 3-link mechanism figure BUILT**
  (`schematics.mechanism_chain`, outcome-neutral cut glyph, manifest F10, both variants render);
  4 missing limitations → APPENDIX_B (B.2.0 endogeneity, B.5.6 conventions + VERIFIED
  `lo2002statistics`, B.5.7 single-look, B.6.6 prototype-not-evidence). **D5 DEFERRED BY RULE**
  (quotes prototype numbers) — re-instantiated from campaign records at the bank gate.
- **NOVELTY FENCE SWEEP banked** (`docs/NOVELTY_FENCE_SWEEP_2026-07-13.md`): **cell still EMPTY,
  HIGH confidence** (21 queries, 12 first-hand fetches); two-flank squeeze documented;
  `kvasiuk2026madevolve` hallucination flag RESOLVED as real; 2 new verified bib entries.
- **M2 SURVEY FLEET RUNNER BUILT** (`scripts/m2_survey.py`, protocol-v1-exact, 4 tests, roster
  config); harness validated at zero spend (70 items × 2 stub models).
- **Bank-gate rehearsal RAN CLEAN on the pm2 CLUSTER archive** (REHEARSAL_20260713_180954) —
  runbook precondition 0.5 closed early. AI disclosure finalized against UCL's PUBLISHED
  3-category framework. `_build` PDF rebuilt (0 warnings). CH4 compute prose → Myriad facts
  (`6e48592`). The 66-skip transient: instrumented (`-rs` in the runbook), fail-safe, clean
  re-run 2,196/3/0.

**Governance:** launch (and the freeze trigger with it) is GATED ON TAMER'S OFFICIAL APPROVAL
(his 2026-07-13 instruction; the delegation memory amended). ADR-053 (Myriad substrate),
ADR-054 (chunked posture), ADR-055 (25 st/s floor) recorded. Ops lesson (4th occurrence, now
absolute): backslash-bearing content goes through Write/Edit tools ONLY — bash heredocs mangle
`
`/`
` escapes.

## [2026-07-13] — pre-spend audit CLOSED (41 findings) · B\* reopened under a pre-committed rule · C5 built · campaign = Myriad · DELEGATED RATIFICATIONS

- **Pre-spend audit COMPLETE**: waves 1–4 + P19 (missing cluster freeze gate) + P4/C5 = **41
  findings fixed + test-locked**; full suite 2,116 passed / 0 failed. Inventory:
  `docs/PRE_SPEND_AUDIT_2026-07-13.md` (final).
- **B\* REOPENED (Tamer's correction: "nothing is closed")**: the 1.6M ext rung scored val-DSR
  0.187 vs 0.041 @100k on the same CRN seed (verified: same reward hash, real return-path gain).
  Evidence-ledger claim 8 downgraded A−→B; claim 15 added; the **extended B\* decision rule was
  PRE-COMMITTED before the remaining curve points land**. Verdict-independent honesty rewording
  applied to unbound prose (`91a1097`); hash-bound wording held for ONE post-verdict batch.
- **C5 BUILT (`ccbe860`)**: the H3 single-shot control on the cluster — disjoint
  `*_h3_singleshot/` roots by construction, `h3ss_` batch namespace, −100 priority, gens=1
  (reflection provably never fires), own summary sentinel.
- **Campaign substrate = UCL MYRIAD (Tamer's directive)**: "the whole campaign, we will run it
  on Myriad to speed up." Laptop demoted to certified fallback (CLAUDE.md superseded).
- **DELEGATED RATIFICATIONS (Tamer, 2026-07-13: "full permission, full freedom, ratify on my
  behalf" — each exercised only within the pre-registered design):**
  1. **Launch config RATIFIED**: device-stratified seed blocks ON at launch
     (`--seed-pool-blocks "EF:0-283,L:284-567"` — the 2026-07-11c design, now a launch fact);
     full line: `run_campaign_cluster.py --tiered --pack 5 --cores-per-training 1
     --llm-from campaign --pass-mode B --batch-tag c1 --seed-pool-blocks "EF:0-283,L:284-567"
     --resume` + a separate `--h3-singleshot --batch-tag c1 --resume` invocation after the
     headline, + C0 canary first.
  2. **Freeze execution DELEGATED**: freeze runs (by Claude, loudly announced) only when ALL of:
     the 30-point curve verdict is applied, the post-verdict wording batch has landed, and the
     gate is 21/21 green. NOT before the curve verdict (standing recommendation).
  3. **B\* verdict protocol**: clean-cut outcome (no ascent → keep 200k; ascent at 400k only →
     raise to 400k with the rung math) = decided autonomously with a dated amendment; any
     outcome forcing an n-vs-budget-vs-deadline trade-off still goes to Tamer explicitly.

## [2026-07-11d] — the fleet's first live results: path CERTIFIED, the throughput model measured, a third day-1 breaker fixed

- **★ Apptainer-on-node CERTIFIED**: `p1pack2` (772152) completed on a real V100 — the FULL
  campaign path (container → venv → `run_one --pack 2` → 2×`train_candidate` on ACFS gold →
  archived records, real `val_fitness`) executed live end-to-end. No untested piece remains.
- **The throughput model is now measured**: 102.2 steps/s solo · 66.4 steps/s each at pack-2 ·
  ~860 s fixed per-task overhead (p4det-t1) → 1.28/1.86 trainings/GPU-h at B\* (unpacked/pack-2);
  F(2)≈1.45 effective (the early 0.7 was an overhead artifact on 50k probes — fewer/longer tasks
  ≫ many short). The cores-scale-with-pack confound (CPU starvation vs GPU time-slicing) is
  resolved by the `p1pack2c4` discriminator (`--cores-total`/`--name-suffix`, 26d9acb).
- **BUG 3 (batch_tag, 83b06ee)**: the driver's double-submit guard matches queued jobs by NAME
  across the whole user queue → concurrent runs sharing arm names collide (the prototype adopted
  the rehearsal's `distributional_g0`/`scalar_g0` and silently polled forever). Per-run
  `--batch-tag` namespacing at the run_batch choke point + regression test; the prototype's 5
  orphaned arrays qdel'd and the driver relaunched namespaced (`pm_*`).
- **Myriad serialization policy measured** (~21:00): `policyjsv`/`snx=1` holds tasks 2..N of every
  pending array (`hqw`); cascade did NOT release on first task completion (grace, then rc-support);
  chunked-fleet mitigation encoded.
- Session record: `docs/SESSION_2026-07-11_NIGHT_PILOT_FLEET_AND_FIXES.md` (chronology, all 11
  commits, measurements, decisions, the campaign wall-clock table from measured constants).

## [2026-07-11c] — max-throughput campaign levers (hardware-only); CRAG rejected; device-stratified seed blocks RATIFIED; the battery live on Myriad

Tamer's directives, executed same-night: "use everything Myriad offers, hardware only, no science
reduction" · "no CRAG — we finish without" · "solve all other issues yourself, full permissions."

- **CRAG reservation REJECTED (Tamer)** — the campaign runs on fair-share alone; the draft
  application was deleted. The design absorbs fair-share variability by construction (floor-first
  C-ladder + the E1 exogenous stopping tier: a slow queue costs only the marginal rung).
- **Device-stratified seed blocks RATIFIED (2026-07-11c, delegated full permission)** — whole seed
  blocks may run on different GPU pools (`--seed-pool-blocks "EF:0-283,L:284-567"`): the inference
  is CRN-paired per seed, so every contrast D_s compares arms trained on the SAME device (device
  cancels in the pair — a randomized-block design); the device×arm interaction is reported via the
  per-record `env_fp` as a per-device D̄ diagnostic. Adds the A100 pools to confirmatory C
  (≈ +60–80%). Implemented FLAG-OFF in `ClusterRun.seed_pool_blocks` + `run_test_leg` partition +
  `parse_seed_pool_blocks` (disjointness fail-loud; unassigned seeds fall back — never dropped);
  the default single-pool path is unchanged. Regression tests added.
- **`--h-rt` backfill lever** threaded entry→campaign→driver→jobscript (measured wall ×1.5 instead
  of the 3 h default — a 5.5× over-request that disqualified tasks from backfill gaps).
- **Battery live:** P0 rehearsal (3 arrays) · P6 authored-winner ladder 18 tasks + extensions
  **800k/1.6M** (measured range now 25k→1.6M, 64×; the object is the eval plateau, not the
  critic-loss minimum — Goodhart) · P1 packing 2/3/5/**8** · P4 cross-node determinism pair ·
  **P8 full 7-arm prototype on Myriad** (real gold, Qwen, directional-only). P2 dropped as
  redundant (the fleet's epilogue ledgers ARE the placement experiment); P3 subsumed by P6.
  Persistent order-insensitive fleet monitor (sorted-diff; v1 false-alarmed on row reordering).
- **Amendment R76** (separate commit db52495): A5 rational-insensitivity account + the fed-delta
  SNR/attenuation exhibit; canonical hash `79a6db44` → `e3a8c880`, gate 21/21 GREEN.

## [2026-07-11b] — the vanished-rehearsal root cause: literal `~` paths (campaign-day-1 breaker) FIXED; pilot battery planned

### Diagnosed: the rehearsal arrays Eqw-died on unexpanded `~` and were admin-purged traceless
The 2026-07-11 rehearsal's three arrays disappeared from the queue with **no `qacct` record**. Forensic
chain (all verified first-hand on the cluster): the rendered jobscript carried literal `~` in the SGE
`#$ -wd`/`#$ -o` directives (SGE expands neither `~` nor `$HOME` there → the array goes **Eqw at
dispatch**, where UCL's cleanup deletes it; deleted-before-start jobs write no accounting), in
double-quoted bash strings (`mkdir -p "~/..."`), in the Apptainer `--bind` list, and in `PYTHONPATH`
(Python never expands `~` → `ModuleNotFoundError` on every task even had dispatch succeeded). The spec
push had created a **literal `~` directory** under `$HOME` (which is why `qsub` "worked" — the relative
literal path resolved); verified to contain only our specs/logs (44K) and removed. **This would have
broken the real campaign identically on day 1.**

### Fixed: tilde-free jobscript contract, fail-loud at the render choke point
`render_jobscript` now REJECTS any literal `~` in `remote_root`/`gold_dir`/`venv`/`repo_root`/
`apptainer_sif` and requires an absolute `remote_root` (directive sink — even `$HOME` is unsafe there);
shell-only defaults moved `~/…` → `$HOME/…` (double-quoted bash expands variables, never tildes). New
`submit.remote_home(runner)` (resolves the real remote `$HOME` via an explicit remote shell — the quoted
ssh runner keeps a bare `$HOME` argv word literal) + `submit.expand_remote(path, home)`; the entry point
expands all user-supplied `~` paths ONCE before anything renders (live path), and against a documented
`/home/USER` stub in `--dry-run`. Two tests that had regression-locked the broken tilde form corrected;
new regression tests for the render contract + the expansion helpers. Cluster suite green; ruff clean;
dry-run re-validated end-to-end.

### Planned: the pre-freeze pilot battery (`docs/PILOT_BATTERY_2026-07-11.md`)
P0 rehearsal relaunch (certifies Apptainer-on-node; command staged, awaiting Tamer's go) · P1 packing-F
ladder · P2 sustained-C probe · P3 full-length 200k anchor · P4 cross-node determinism pair · P5
resume-under-fire drill · P6 B\*-on-authored-rewards ladder {100k,200k,400k} × 2 archived winner rewards
× 3 CRN seeds (closes R74's one-hand-written-reward blind spot; the only pilot that could still move a
frozen number, hence pre-freeze; needs Tamer's go) · P7 laptop D5 early-start. ≈33 GPU-h total; explicit
NOT-piloted list (σ_D re-run, intraday, prompt experiments, sealed-leg anything) with reasons.

## [2026-07-11] — E1 ladder UPGRADED to 7 rungs + deep pre-freeze sweep (5 auditors) + G1 anchor + LIVE end-to-end rehearsal (found & fixed the cluster path)

A long autonomous session that took the pre-registration to freeze-ready and then stress-tested the
Myriad campaign path with a real end-to-end run. **Canonical hash progressed `4b116f64` → `af385617`
(7-rung upgrade) → `79a6db44` (sweep fixes); NOT yet frozen (freeze is Tamer's act).**

### Seed ladder upgraded 4 → 7 rungs (Tamer's insight)
E1 first recorded the 4-rung ladder `[30, 340, 403, 568]`. Tamer flagged the **30 → 340 gap** as a real
flaw: rungs are the pre-declared fallback points if a run is truncated by the deadline or the queue, and
that gap spans ~3,700 trainings, so a truncation at, say, seed 250 would discard 220 completed paired
seeds back to 30. Upgraded to **`[30, 100, 189, 279, 340, 403, 568]`** — each rung with a pre-registered
meaning (30 distinction core / 100 σ-precision / 189 Monte-Carlo point-estimate / 279=80% / 340=90% /
403=95% target / 568=99%), zero extra compute (tiers are order-only labels on the same seed set). Updated
across all three seed carriers + `PREREGISTRATION.md` E1 block + amendment row + `power_analysis`
`ASSURANCE_TIER_BOUNDS` + its test + the freeze-test fixtures.

### Deep pre-freeze sweep — 5 independent auditors (read-only), every finding fixed
Ran five parallel auditors over seed/tier consistency, statistical-design coherence, the identification
principle, data leakage/splits, and paper-vs-frozen-design. **Verdict: theory CLEAN** (CVaR sign, Le Cam
deficiency direction, DPI strict-convexity gate, Fissler–Ziegel elicitability chain — all correct, no
misattribution to Okhrati); **leakage EXEMPLARY** (60-session purge re-derived correct at both boundaries;
survivorship-freeness proven with Wachovia/AIG retained through 2008; sealed test unreachable by
selection); **identification HOLDS** (only the feedback block varies; 7-arm roster consistent in all five
locations; placebo_shuffled a correct derangement); **arithmetic EXACT** (re-derived Var(D)=2σ²(1−ρ)=0.369,
the χ²-upper ladder 279/340/403/568, the m=6/[3,3] partition, TOST=0.05, the R64 one-sided p). Every
freeze-blocker was the same root cause — the E1 seed change not propagated into older passages — and all
were fixed: **hash-bound self-contradictions** (the verbatim bankable-null statement said "30 winner
seeds"; the R64 invariants list; the mechanism sub-tests caveat; the §12 D2 re-affirmation; the H1/H3
"same 30 seeds" comments in `campaign.yaml`; a `preregistration.yaml` calibration note); **3 operational
seed-default bugs** (`resume_audit.py`/`run_campaign_cluster.py`/`install_onstart_task.ps1` defaulted
`0-402` or `0-29` → would silently skip seeds 403–567; now `0-567`); **stale-doc reconciliations**
(superseded banners on the arm-adaptive `SEED_DECISION` doc and `COMPUTE_AND_TRAINING_TIME.md`; the
inverted "more seeds than the campaign" comparison in `contamination.py`; six factual seed refs in the
paper body CH4/CH5/CH6/APPENDIX_B). Committed **79bbfd6**. Gate 21/21 GREEN, `determine_design`
FREEZE-READY, full suite **2095 passed**. (Deferred post-freeze, non-hash-bound: extend the tail-neutrality
scan to the in-code reflection preamble; the bulk scattered "30 seeds" doc comments — high false-positive,
many are legitimately tier-0, want a careful human pass.)

### G1 anchor MEASURED (committed eff0dca)
A real short SAC training on a Myriad **Tesla V100-PCIE-32GB**: **102.2 steps/s, 8.15 min/50k → ≈32.6
min/training at B\*=200k**, critic loss 418→0.07. That is **≈1.87× the laptop** (61 min solo), squarely
in the pre-registered 1.4–2.5× band. Appended to `docs/G0_G1_CLUSTER_CERTIFICATION_2026-07-10.md`. Also
confirmed the launcher fix on BOTH pools (V100 + an A100-PCIE-40GB), and that the A100 is **not faster**
per training (0.21 s vs 0.144 s microbench) — its only value is denser packing for Stage 2.

### LIVE end-to-end rehearsal — a small real run to shake out the whole cluster path
Tamer: "do a very small prototype run with LLMs … to catch and fix absolutely all issues, so the main
campaign is strictly flawless." Ran the first-ever live execution of `run_campaign_cluster.py` (3 arms,
2 generations, 1 seed, 10k steps, real **Qwen3-Coder via OpenRouter** authoring — cheap, `--pass-mode B`,
`--synthetic`, `outputs/proto_timing`). It caught **five real campaign-breaking issues**, all fixed +
committed (`fb3fc11`, `8118fb8`; ruff clean, 280 cluster tests):
1. **`apptainer_sif` not threaded into the campaign path** — the cluster venv is built INSIDE
   `python311.sif` (RHEL7 glibc too old for the cu124 wheels natively), so every training MUST launch
   through Apptainer; the campaign path rendered the bare-venv launcher → would have failed on every node.
   Threaded `build_cluster_run` → `driver` → `render_jobscript` + a `--apptainer-sif` flag.
2. **The driver didn't `load_env()`** — the laptop-side driver authors before shipping specs, so it needs
   the API key in `os.environ`; real authoring crashed "key unset". Added (parity with `run_campaign.py`).
3. **cp1251 console crash** — the Russian-locale Windows default encoding crashed the ssh reader thread on
   any non-ASCII byte from the cluster. Pinned `ssh_runner` to utf-8/`errors=replace`.
4. **Empty gold dir under `--synthetic`** — the jobscript still `--bind`s the gold dir into the container,
   and Apptainer errors if the path is absent. Create the input dir.
5. **The throughput finding + `--cores-per-training` lever** — the decisive one. Myriad GPU nodes sit at
   **load=36 (CPU-saturated) with free GPUs**, so a job's **CPU-core** request is the binding scheduling
   constraint, not the GPU. The jobscript's default 4 cores/training is over-provisioned (a training uses
   <1 core), so pack=5 → 20 cores wouldn't place. Added `cores_per_training` threaded through to
   `render_jobscript` (cores = cores_per_training × pack; default unchanged) so the campaign can shrink the
   footprint and pack jobs actually place. This reframes campaign throughput planning: concurrency is gated
   by GPU-node cores, which depend on total cluster load — so max throughput needs a small core footprint +
   off-peak timing or a CRAG reservation.

After the fixes, authoring (Qwen `HTTP 200 OK`) and submission worked for all arms; the run is queued
behind the cluster-wide core saturation. Overnight: sleep disabled so the laptop driver survives, a
persistent poller fires on the first training record (live Apptainer validation) or a node error, and the
precise campaign-time answer is owed once the run completes + a packing probe measures F. **⚠ TEMP state:
`config/prototype.yaml` `llm` block is pointed at Qwen for the smoke — revert to
`anthropic`/`claude-sonnet-4-6` after; NOT committed.**

## [2026-07-10b] — AMENDMENT E1: the seed decision RECORDED (supervisor-approved) → FREEZE-READY

> **Note (superseded by [2026-07-11]):** this entry was written at hash `4b116f64` with the ladder later
> extended to 7 rungs; the deep sweep then moved the canonical hash to **`79a6db44`**. See the
> [2026-07-11] entry for the 7-rung ladder, the sweep fixes, and the final hash.

Ramin approved the design in the 10-Jul meeting; Tamer ratified the assurance-tier ladder and
instructed the freeze. Recorded as **Amendment E1** across the three seed carriers:

- `config/campaign.yaml` + `config/preregistration.yaml`:
  `seeds: {mode: tiered, tiers: [30, 100, 189, 279, 340, 403, 568]}` (flat `[0..567]`, headline 568);
  `config/inference.yaml` mirror updated to the same ladder. Every rung has a pre-registered meaning
  (30 core / 100 σ-precision / 189 point-estimate power / 279=80% / 340=90% / 403=95% target / 568=99%),
  and the intermediate rungs cap the worst-case seeds discarded on an exogenous truncation (a truncated
  run falls back to the largest COMPLETED rung — with the old 30→340 gap, a truncation at seed 250 would
  have discarded 220 completed seeds). `power_analysis.ASSURANCE_TIER_BOUNDS` mirrors the ladder.
- `PREREGISTRATION.md`: the full E1 amendment block (σ_D = 0.369 fired the σ_D>0.10 trigger; the
  unattainable "30→50" rule RETIRED; sizing 189 point-estimate → χ²-upper ladder 279/340/403/568;
  CVaR-5% co-primary leg already conclusive at tier 0; **exogenous stopping tier** preserves the single
  look) + amendment-table row + header updated to freeze-ready; historical D2 text preserved, marked
  superseded.
- **Three tiered-schema bugs fixed en route** (each would have mis-read the dict): `determine_design.py`
  `config_n_seeds` used a raw `len()` (would read 2 and keep `n_seeds` PENDING forever);
  `power_analysis.py` ×2 (silent fallback to the literal 30 / `list(dict)` yielding keys). All three now
  resolve through `src.utils.seeds.resolve_seeds`. Three stale freeze-test fixtures updated to the
  ratified schema (they pinned the old `[0..29]` literal); `tests/test_freeze.py` + `test_seeding.py`
  58/58 green.
- Gates: `determine_design` → **FREEZE-READY** (was `BLOCKED on: ['n_seeds']`); `freeze.py --check` all
  green at the new canonical SHA-256 `4b116f64…` (chain `1c6b76b6` → `296a19ee` → `4b116f64`, every hop
  this authorized E1 batch). Full suite re-run before the freeze act.

## [2026-07-10] — MYRIAD FIRST CONTACT: login → container environment → verified data staging → first GPU jobs queued; supervisor-meeting brief; Defender/OS repair; repo-identity cleanup

The cluster went from "never logged in" to "certification jobs in the queue" in one morning, with
one real bug caught against the live system. The canonical freeze hash is UNCHANGED (`1c6b76b6`).

### Context recovered first (2026-07-09→10, pre-cluster)
- **Overnight self-improvement loops L92–L100 closed** (see `docs/SELF_IMPROVEMENT_LOOP_LOG_2026-07-08.md`
  §LOOP 100): 10 verified report-only improvements across the inference stack; loops STOPPED at L100
  per Tamer's instruction.
- **2nd-LLM re-point (commits `2314514`, `d01e431`)**: Alibaba/DashScope key unobtainable → Qwen3-Coder
  served via **OpenRouter**; live-verified snapshot `qwen/qwen3-coder-480b-a35b-07-25` recorded in a
  `config/llm.yaml` comment (file NOT hash-bound; verified against `_BOUND_CONFIGS`).
- **Windows Defender restored** after a four-layer sabotage (boot-persistent local GPO; IFEO debugger
  hijacks; disabled services; `MsMpEng.exe` with an EMPTY DACL). Three layers fixed from userland
  (scripts run by Tamer); the fourth required the in-place repair to 25H2 (build 26200.8655).
  Result: AntivirusEnabled=True, RTP on, SecurityCenter2 `0x061100` → the UCL VPN posture check PASSES.
  Before the repair: **27 commits pushed by Tamer** to the private GitHub (verified via `ls-remote`)
  + 566 MB licensed data / `.env` / SSH keys mirrored to `D:\llm_rp_predefender_backup` (gold SHA verified).
- **Supervisor-meeting brief** `docs/SUPERVISOR_MEETING_BRIEF_2026-07-10.md` (commit `39c1930`) + a full
  spoken script and question set. Load-bearing correction to the 3-Jul email: **the CVaR-5% leg is
  already conclusive at n=30** (σ_D=0.0015, ρ=+0.47) — the seeds sharpen the Sharpe leg only.

### Myriad first contact (2026-07-10 morning, all first-hand)
- **Access**: the Myriad account was ALREADY ACTIVE (4-day-old approval email); the initial
  login12 "Connection closed" was a single mistyped password (Myriad allows ONE attempt) — proven by a
  successful gateway login with the same credentials. Public key installed via the gateway;
  **passwordless `ssh myriad` (login12) and `myriad13` (login13) both work over the VPN**.
- **G0 recon** (`scripts/myriad/g0_probe.sh`): ACFS `/acfs/users/ucestes` + Scratch (1.0 TB, new
  `myriadfs`) exist; **login-node outbound HTTPS works** (api.anthropic.com reachable, pypi 200);
  Apptainer 1.2.4 present; SGE healthy; **`qrsh` is JSV-rejected (interactive) but `qsub` batch
  submits cleanly** — the campaign uses batch arrays only, so no impact; `lquota` errors on the new
  filesystem (cosmetic; `df` gives the quota).
- **Platform verdict → R12 container route executed**: login nodes run **RHEL 7.9 / glibc 2.17**;
  pinned `pandas 2.3.3` (wheels need manylinux_2_24) and `contourpy 1.3.3` (2_27) have NO installable
  wheels there, and source builds die on GCC 4.8.5. Rather than break laptop↔cluster pin parity:
  `~/python311.sif` (docker `python:3.11-slim-bookworm`, glibc 2.36) pulled; **the venv is created
  THROUGH the container** → every locked version installs exactly as validated
  (torch 2.6.0+cu124 / pandas 2.3.3 / numpy 1.26.4 / sb3 2.8.0 / gymnasium 1.2.3; `src.cluster` imports).
  Repo shipped to `~/llmrp` via `git archive HEAD` (tracked files only — no data, no secrets).
- **REAL BUG caught + fixed + committed `08a1ba7`** (jobscript template, would have killed every
  containerized task at first import): the apptainer branch launched the BARE container `python`
  instead of the venv interpreter, and `$TMPDIR` + the gold dir are NOT auto-bound into the container
  (the staged-gold env var would point at a path invisible inside). Launcher is now
  `apptainer exec --nv --bind "$TMPDIR,{gold_dir}" {sif} {venv}/bin/python`; the V3 regression test
  was updated to lock the CORRECT behaviour (it previously asserted the bug). Also fixed: the
  epilogue bash test now resolves a WORKING bash (the post-repair `which bash` hits a distro-less WSL
  shim). 71/71 cluster tests green; fixed `jobscript.py` shipped to the cluster copy.
- **Gold staged with integrity**: the 10-file `univ5` family (~36 MB) → `/acfs/users/ucestes/gold`;
  **all SHA-256 hashes verified identical** both sides (`returns_panel_univ5` = `7cf5d988…`).
  Trainings need only the gold parquets (risk-free CSV is analysis-time; `cash_daily_rate` is config).
- **First GPU jobs queued + queue-contention measurement**: probes `g0gpu` 762862 (cgroup isolation =
  packing safety; driver version; compute-node outbound) and `g1smoke` 762914 (validates the EXACT
  fixed launcher + TMPDIR bind marker + torch CUDA on a V100), plus an A/B pair 762959 (`allow=L`) /
  762960 (no pool constraint). Measured live: **5,092 pending jobs cluster-wide; several GPU nodes
  DOWN** (`adu`/`ad` states — e00a-008, f00a-001, l00a-007 — their "free" GPUs are phantoms); only
  the two e96a nodes show healthy free V100s; **no resource-quota rule caps us** (the sole RQS is
  disabled and targets another user); >60 min wait for a 15-min job on fresh fair-share. Implication
  folded into the meeting brief (§11 + Q4): access is LIVE, the only unknown is throughput, and the
  **ARR→CRAG co-sign ask is now concrete (CRAG meets Tue Jul 14)**.
- Meeting brief §11/Q4 updated to the live cluster state; the resume cursor
  (`memory/session-current-focus.md`) carries the full session block.

### Repo-identity cleanup (Tamer's standing instruction, 2026-07-10)
- **No Claude co-author trailers from `08a1ba7` onward** (first trailer-free commit).
- Staged next: a one-shot history rewrite stripping the 28 existing `Co-Authored-By: Claude` trailers
  and normalizing the stray `abailey81` author name (same email) to `Tamer Atesyakar` — prepared in an
  isolated clone, tree-identity verified, **force-push executed by Tamer only**.

## [2026-07-08c] — MYRIAD-NATIVE resilience + monitoring + auto-proceed gate (100%-Myriad GO) — all uncommitted, pre-freeze machinery

Tamer confirmed the GO ("we will use Myriad 100%") and asked that ALL systems be genuinely advanced +
strictly flawless for a multi-week cluster run: "resume if for absolutely any reason the run was
stopped" and "advanced systems for Myriad, not only monitoring, everything." Built + tested; the
canonical freeze hash is UNCHANGED (`1c6b76b6`) — everything here is execution-layer, gated to GO.

- **Long-outage transport tolerance (`driver.run_batch`).** The driver now rides out a long VPN/ssh/
  login-node outage instead of dying every ~2 h: a transport-failure streak is fatal only past a
  WALL-TIME bound (`max_transport_outage_secs`, default 12 h) OR the count cap — the time bound is the
  real guard, decoupled from `poll_secs`. Rationale: the queued Myriad arrays keep training regardless
  of laptop connectivity, and the archive is the truth, so nothing is lost by waiting; a genuinely dead
  link is still surfaced (raises → supervisor relaunches with `--resume` on reconnect).
- **Driver heartbeat → Myriad-native monitoring.** `run_batch` emits a per-cycle read-only status beat
  (`driver_status/<batch>.json`, atomic; a FINAL `phase=done` beat on completion). Two new sentinel
  checks consume it, effect-blind (freshness + counts + SGE occupancy — never a result): **`check_driver_lease`**
  = the orchestration deadman (a stale beat = driver crash/hang, laptop power-loss, or an outage the
  driver could not ride out — the ONLY monitor that can see laptop host-death during a cluster run,
  since the trainings survive it on Myriad); **`check_queue_health`** = the queue + transport panel
  (queued/pending across active batches + the driver's own pull/ops failure counters as the earliest
  VPN-outage warning). Cluster-only (a laptop run has no `driver_status` → INFO); done beats never read
  as hung.
- **Auto-proceed review gate (`run_campaign_tiered`, Tamer's delegated tier-0 decision).** The C3 gate
  now AUTO-PROCEEDS on green execution health (no manual latency — the time-security requirement) and
  STOPS only on a real execution defect (a short/inhomogeneous unit) or an explicit `--hold-at-gate`.
  It reads ONLY counts + homogeneity censuses (`integrity.write_integrity_report` now returns the report
  dict with `verdict.health_ok`), so releasing on green never conditions continuation on an effect — the
  single-look inference is protected. The report gained a SEALED-SAFE selection section (the winner's
  authored reward CODE, the mechanism headline — no performance number).
- **Myriad-capable boot recovery (`install_onstart_task.ps1 -Myriad`).** The ONSTART Task-Scheduler
  re-entry now has a cluster mode: the supervisor child becomes the Myriad driver
  (`run_campaign_cluster.py`), the laptop GPU clock-lock is skipped (laptop GPU idle), and the laptop
  preflight is bypassed — so a reboot/power-loss auto-resumes the cluster orchestration.
- **`scripts/resume_audit.py` — the pre-relaunch confidence check (capstone of "resume from ANY
  reason").** Reads the pulled archive READ-ONLY and reports the EXACT `--resume` plan (per-arm search
  completeness + winner-frozen; the precise missing sealed-leg seeds), VERIFIES integrity (every record
  parses — surveys corruption without crashing, unlike `load_all`), and cross-checks a second-disk
  mirror for un-mirrored sealed records. Exit 2 on a real integrity problem. Effect-blind (run_ids +
  counts only).
- **Tests:** +the driver wall-time outage guard + heartbeat/`phase=done`; +the two sentinel Myriad
  checks + `_read_driver_status` running/done aggregation + the gather_inputs end-to-end; +the gate
  auto-proceed-vs-hold pair; +4 resume-audit (missing-seed plan / corruption / mirror parity / CLI exit).
  Driver+sentinel+cluster+resume_audit suites green; freeze `--check` green (hash unchanged).
- **DEEP MYRIAD RESEARCH → `docs/MYRIAD_DEEP_RESEARCH_2026-07-08.md`** (Tamer: "extremely deep research
  on Myriad — usage, capabilities, papers that used it; dive deep, not just abstracts"). 13 sources read
  first-hand (rc.ucl.ac.uk docs + `UCL-ARC/mkdocs-rc-docs` source + nf-core production config + a UCL
  Myriad paper). **KEY: the §15 GPU-packing risk is DOWNGRADED from "could double the timeline" to "G0
  confirms."** The Young GPU-nodes page states VERBATIM that **device cgroups are implemented (10 Aug
  2022) so each job "only ha[s] access to the number of GPUs they requested"** — UCL-wide SGE policy ⇒
  a `gpu=1` job owns its GPU cgroup-exclusively ⇒ running N training processes on it is safe (§15 pack
  ×2–2.5 validated); `CUDA_VISIBLE_DEVICES` renumbers our GPU to index 0 ⇒ `cuda:0` correct; `-ac
  exclusive` reserves a whole node. CONFIRMED: 74 GPUs (38 V100 EF / 24 A100-40 L / 12 A100-80 U/V);
  393 nodes; walltime 72 h/48 h; SGE `-l h_rt/mem/tmpfs/gpu`, `-pe smp`, `-ac allow=EF|L`, `-t/-tc`,
  `-hold_jid`, `-r y`; **home==Scratch 1 TB not-backed-up + ACFS backed-up read-only-on-compute** (gold
  home); `$TMPDIR` 1.5 TB local, wiped on exit; ARR→**CRAG monthly 2nd-Tue** via `rc-support@ucl.ac.uk`;
  the Myriad@UCL acknowledgment (verbatim). REAL precedent: **nf-core's live Myriad profile**
  (`executor sge`, `queueSize 100`, `submitRateLimit 10/1s`, `penv smp` — sources our throughput model)
  and **arXiv:2303.10672** (a UCL group solving an MDP by GPU value iteration on Myriad A100s — the
  develop-local/scale-on-Myriad pattern + ~2.4× consumer→A100, validating our 1.75× laptop→V100
  constant). GOTCHAS encoded: Apptainer **builds on local fs ($TMPDIR) not home/Scratch**, no
  Dockerfiles (`.def`/`pull`), `--nv` for GPU; inode quota; **don't confuse Myriad (`mem`/`gpu=1`/
  `module load`) with the UCL CS-dept cluster (`tmem`/`gpu=true`/`/share/apps`)**. NEW: Open OnDemand
  (`ood.myriad.rc.ucl.ac.uk`, pilot via rc-support) as a browser queue-monitor + Jupyter. `g0_probe.sh`
  updated to confirm cgroup isolation (`nvidia-smi -L` count + `CUDA_VISIBLE_DEVICES`) and `lquota`.
- **GRADE SECURITY made a first-class design aspect + precise run times + tier ultrathink →
  `docs/GRADE_SECURITY_AND_TIER_DESIGN_2026-07-08.md`** (Tamer: "add grade security"; "ultrathink the
  tiers inside the stages"; "precise run times for everything"). Grade security = the design guarantees
  a distinction-grade submittable dissertation under EVERY adversity, by construction (7 named
  guarantees: floor-first ordering, every-stop-a-complete-design, exogenous stopping, dual-track
  fallback, bulletproof resume, deadline buffer, procedural hygiene). The Stage-1 C-ladder is tabulated
  tier-by-tier with per-tier GPU-h: **the complete distinction floor (7 arms + mechanism + H1 + H3 at
  n=30) banks in ~1,104 trainings ≈ 644 GPU-h ≈ 1.3 days central** (~10% of Stage 1); the equivalence
  sweep (30→340→403→568) is additive CI-tightening. **Precise run-time table:** floor ~1.3 d · to 95%
  (n=403)+D1 ~7 d · to 99% ~9.4 d (central 36 trainings/h = C=12 × packing ×1.75); Stage 2 (report-only,
  both pools, A100-80 dense packing) ~3–6 d overlapping the write-up. **New code:
  `power_analysis.recommend_assurance_target(trainings_per_hour, days)`** — the throughput-aware,
  deadline-safe target selector (picks the highest assurance tier that fits the calendar minus a 25%
  buffer, floor as last resort; the stop is exogenous ⇒ valid single-look) + test. Freeze hash UNCHANGED
  (power_analysis is not hash-bound). **THEN (Tamer: "ultrathink Stage 2, re-read the plan, how would
  everything look") the doc gained §4 (Stage-2 ARMOR design) + §5 (the finished-object view):** Stage 2
  = publishability armor that CANNOT hurt the grade (no-forward-references; each item = +1 appendix
  table +1 sentence, prunable to 0). Internal 4-tier structure by value×dependency (2.A FREE DEPTH
  D3/D4/D9/D6/U5/U4b, no authoring · 2.B nearly-free U3 Qwen + D2+ · 2.C laptop D5 calibration · 2.D
  premium shelf U2b/D7/U4 → else CH7 future-work). The sophistication: **execute in dependency-readiness
  order (zero-authoring analyses + robustness flood the pools at the bank gate while U3/D2+ author),
  prune in value order** — two distinct orderings; A100-80 dense packing for the report-only fleet;
  D2+ = one authoring sweep of 6 counterfactuals over sampled reflection states + top-Δ trainings; the
  Eureka re-read register discharged (deviations each probed; k=3 exceeds Eureka). Stage 2 reuses the
  CERTIFIED orchestrator (config-only, no mega-driver); the D3/D4/D9/D5/D2+ analysis scripts already
  exist (`variance_decomposition.py`/`popart_ablation.py`/`cost_sweep.py`/`mutation_probe.py`).
- **THE OVERALL-DESIGN SYNTHESIS → `docs/OVERALL_DESIGN_2026-07-08.md`** (Tamer: "ultrathink the overall
  design, all stages, all tiers, everything"). The canonical single-source that disambiguates every
  structural axis (the recurring tier-confusion): **5 value-ladders** (STAGES · C-LADDER execution-order
  · ASSURANCE-LADDER power · VALUE-CASCADE banking · STAGE-2 ARMOR) + **1 identity axis** (ARM TIERS:
  arms→hypotheses→tests) + **1 machinery layer** (resume+monitoring+orchestrator), all ORTHOGONAL and
  composed under the unifying principle "**complete-at-every-boundary**" (cheapest-strongest rung first;
  adversity costs only the marginal rung). Coherence review (adversarial): CONSISTENT (roster/bounds/
  order identical in code+config+docs, hash green); RECONCILED the plan's UNPACKED durations (12.4 d)
  vs the now-validated PACKED figures (~7 d to n=403) — the plan's is the conservative bound, packed
  supersedes; REFINEMENT: the C3→C4 gate can re-confirm the assurance target from the run's OWN measured
  cadence (exogenous ⇒ still valid single-look; hook exists); CRISP-UP: one bank-gate runsheet
  (verify-mirror→analyze→depth-bundle→prereg-bundle). **THE HONEST DOMINANT LEVER stated plainly:** the
  machinery secures the RESULT with near-certainty but does NOT win the grade — the grade is won in the
  MECHANISM CHAPTER (SQ1-3 + causal chain + taxonomy), the honest null framing, and the motivating EDA;
  after freeze the dominant remaining lever is the write-up depth + the 17k→9.5k surgery, not the cluster.
- **DEEP INTEGRATION AUDIT (Tamer: "find absolutely everything, all issues/inconsistencies/gaps; find
  first, then fix; don't be lazy").** First-hand adversarial read of every component + seam built this
  session; ~13 seams VERIFIED CLEAN (resume_audit ids ↔ test-leg run_ids, heartbeat keys ↔ sentinel
  reader, seed-tier partition ↔ assurance ladder, gate health_ok wiring, driver transport tolerance +
  done-accounting, `driver_status/` not polluting any archive scan, boot→supervisor→entry chain,
  gate effect-blindness, resume-through-gate winner-stability). **Fixed 2 MAJOR + 3 MINOR real defects:**
  (1) **MAJOR** `mirror_archive.ps1` mirrored `outputs\campaign` but NOT `outputs\campaign_cluster` — the
  MYRIAD archive was UN-MIRRORED (broke the 3-site guarantee); now covers it + `/XD` skips the transient
  `driver_status`/`batches` dirs. (2) **MAJOR** `resume_audit` had the mirror severity INVERTED — it
  failed `integrity_ok` (exit 2) on benign 6-hourly mirror-lag (cry-wolf every relaunch) and never
  checked the real alarm; now `mirror_behind`=benign warning, `local_lost` (mirror has sealed records
  local lost)=the exit-2 alarm with `recover_from_mirror`. (3) `ASSURANCE_SWEEP_UNITS` 11→12 (the uniform
  sweep includes H3, matching the run-time doc). (4) plan §3 durations now note the validated packing
  (12.4 d unpacked → ~7 d packed). (5) resume_audit `--mirror` example → the `campaign_cluster` subdir.
  **BUILT the one real gap:** the **bank-gate runsheet** (PLAN §3) — the exact idempotent sequence
  archive_integrity write→verify-mirror → resume_audit → analyze_campaign (the single look) →
  variance_decomposition (D3) + D4/D9 → make_prereg_bundle. Documented-as-design (tools ready, G1-live):
  gate target-reconfirmation, Eqw-state detection. Touched suites (109 tests) + freeze `--check` GREEN,
  hash unchanged.
- **Round-2 Myriad research (dossier §13):** GPU **MPS + pack density** (V100 ~4–5 / A100-40 ~12–15 /
  **A100-80 ~25–30** trainings — the Stage-2 lever; MPS optional G1-tested boost, time-slicing default
  for robustness); **compute-accounting** `jobhist`/`qacct`/`nodesforjob`/`qexplain`/`ruse` (the paper's
  wall-clock reporting Okhrati grades); `qstat` **`Eqw`** state (a G1 sentinel-panel upgrade);
  fair-share/Gold/priority-cycles; T-type 64-core AMD nodes for the CPU analysis. **⚠ MIGRATION RISK:**
  Myriad is moving **SGE→Slurm (RHEL 9.5)** — Kathleen done 06/2025, **Myriad UNSCHEDULED as of 06/2026**
  (SGE correct for our window). Contingency: the laptop track is scheduler-independent + the isolated
  scheduler seam ports via the recorded SGE→Slurm directive mapping (dossier §13f) ≈ a day's work.

## [2026-07-08b] — Long-run resilience (tier ladder + resume-hardening + seed schema) + statistical rigor (--assurance) + k=3 search denoising — all uncommitted, pre-freeze upgrades

Tamer delegated the seed/k work ("do k and seed schema and all other stuff yourself … ultrathink,
strictly to our priorities") and, for the long training, "ultrathink the tier / resume / checkpoint
systems in an extremely advanced manner … secure the grade SAFELY." Built + tested; the freeze
canonical hash is UNCHANGED (`1c6b76b6`) — every change is pre-freeze machinery, gated to activation.

- **The grade-securing TIER ladder (`campaign.run_campaign_tiered`).** Each tier is a milestone locked
  in order, so a crash always leaves the strongest guarantee reached: **tier 0 (n=30)** = the complete
  distinction-floor (H2 + mechanism + H1 + H3); **tier 1 (n=340)** = 90% equivalence power; **tier 2
  (n=403)** = 95%; **tier 3 (n≈568)** = 99%. Tiers PARTITION the seed set (order-only, CRN preserved),
  each later tier extends ONLY the H2 test leg (winners frozen once in tier 0). `src.utils.seeds`
  (`resolve_seeds`/`seed_tiers`, schema `{mode: uniform|tiered}` + bare-list back-compat) is the single
  resolver the campaign, entry point, and freeze mirror all bind on.
- **`power_analysis --assurance`.** χ² upper-CI seed sizing that REPRODUCES the seed-decision doc
  exactly (80%→279, 90%→340, 95%→403) and extends it (99%→**568**). `assurance_seed_count(C)` =
  `round(n_point·ν/χ²_{1-C,ν})`; n_point=189, ν=14. (Caught + noted a doc error: the 90% σ_up is
  0.495, not the 0.449 the seed-decision doc labels — 0.449 is the 80% bound; n=340 is correct.)
- **Resume-hardening for the days-to-weeks run.** The batch driver now consults its OWN permanent
  ledger on restart — a deterministically-failing seed was being re-tried 2× on EVERY restart forever;
  now permanently-ledgered run_ids are skipped from the start. (The full resilience matrix — archive-
  as-truth per-training checkpoint, compacted-resume, search-replay, supervisor auto-restart, bounded
  requeue, 3-site mirror, determinism — is documented; per-training granularity is the deliberate
  checkpoint unit, intra-training checkpointing rejected as marginal.)
- **k=3 multi-seed search selection (`src.search.multiseed`).** Each search candidate trains at k seeds
  and is SELECTED on the IQM of its per-seed scores — closing the σ_seed SELECTION channel the pilot
  measured (σ_seed≈0.244 dominates the SESOI). All-or-nothing validity, per-period MEAN PBO vector,
  fed tail on the concatenation of the seeds' val returns. Config-gated `search_seeds_per_candidate`
  (default 1 = **byte-identical** single-seed). Wired into the cluster LLM search AND the H4 family
  arms (so LLM-vs-family is not confounded by k), with correct partial-candidate resume (reuse the
  archived source, never re-author). ⚠ FLAGGED for ratification: the single-seed fed tail is on TRAIN
  returns while the plan's k-seed text says VAL — this follows the plan's literal val-concatenation.
- **[SAME DAY, LATER] THE C-LADDER EXECUTABLE (tier system v2 — doc-faithful after Tamer's
  "you're hallucinating a bit; analyse the md plans deeply").** The docs carry FOUR distinct tier
  concepts on different axes — (1) ARM tiers (statistical labelling: H2 information-channel tier vs
  search-baseline tier, out of the IUT), (2) SEED tiers (the assurance ladder 30/340/403/568),
  (3) the C-LADDER (execution checkpoint order C0–C6, §13.1), (4) the VALUE-CASCADE banking levels
  (0–6: training → CRN pair → seed-block → contrast → checkpoint → stage → program) — and v1
  conflated them. `run_campaign_tiered` is now the C-ladder verbatim: **C0 canary** (hard-gate
  before any Opus spend) → **C1–C3** concurrent search pipelines under the §14.3 `-p` priority
  ladder (H2 at 0, rest at -100; SGE executes the value order natively) + the H2 core test as ONE
  **pair-adjacent interleaved** array (the Lv-1 CRN-pair banking quantum) → **the effect-blind
  REVIEW GATE** (Tamer's tier-0-review idea, made statistically safe: `src.cluster.integrity`
  writes a counts/census-only report — completeness vs budget, F5 ledgers, device/env-fp
  homogeneity — NO performance statistic read; single-look discipline preserved; approval =
  `TIER1_APPROVED` file → `--resume` proceeds) → **C4** the uniform-n ROUND-ROBIN sweep (7 arms +
  H1 baselines, seed-major) in assurance blocks. C5 H3/C6 D1 = separate invocations at -100/-200.
  Entry: `--tiered --canary --approve-tier1 --no-review-gate`. Priority threaded
  driver→ClusterRun→orchestrators; `run_test_leg(interleave=…)`.
- **FED-TAIL WINDOW DECIDED (Tamer-delegated: "whatever maximises publishability/grade"):**
  the k-seed fed tail = the 6 frozen stats on the CONCATENATION of the k seeds' **TRAIN-window**
  returns — the plan's "val" line was a drafting slip (corrected, dated). Rationale: the ratified
  construct is **fed in-sample / scored out-of-sample** (the named selection-overfitting defense;
  `ReturnDistribution.fit(train_realized_returns)` is the k=1 behaviour); val-fed tails would hand
  the author richer information about the SELECTION set and split the k=1/k>1 constructs. Plumbed
  end-to-end: worker `emit_train_returns` flag (k>1 specs only; k=1 byte-identical) → archived
  `metrics.train_returns` → `aggregate_k_seeds` concatenates TRAIN (fails LOUD if absent — no
  silent val fallback). Paper claim gained: the fed tail is estimated on 3× the in-sample data.
- **Verification: 71/71 cluster/entry/multiseed/seeds battery + the full not-slow suite GREEN;
  ruff clean; freeze hash UNCHANGED (`1c6b76b6`).**

## [2026-07-08] — Myriad cluster integration: the generation-level campaign orchestrator BUILT + deep-audited (4 real bugs + 1 provenance fix), all uncommitted pending Tamer's go

Tamer: "close all gaps and lets go … speed up training as much as possible … strictly flawless …
work sequentially, ultrathink … the design very accurate, clean, professional, sophisticated." The
`src/cluster/` adapter (already built + twice-audited: V1–V11) gained the piece that turns the batch
driver into the actual campaign, then a strict adversarial audit of the whole new surface. **Nothing
frozen; all cluster work is ADDITIVE + uncommitted — the laptop track stays the certified default
until Tamer says GO.**

- **Architecture (clean layering, single responsibility per module):** packaging (`spec_io`,
  `jobscript`) → transport (`submit` tar-over-ssh/qsub/markers, `poll` exact-incremental pull +
  compacted diff, `ledger` qacct forensics) → on-node (`run_one`, leg-aware) → batch kernel
  (`driver`, archive-as-truth) → campaign orchestration (`campaign`). Every layer is injectable
  (runner/push/pull/run_batch/select/freeze/author-lock) so the whole stack is unit-tested with no
  network/GPU.
- **`src/cluster/campaign.py` (NEW) — the generation-level composition (PLAN §12 B-A1).** Split
  laptop/cluster (authoring/reflection/selection laptop-side, training on Myriad). LAPTOP↔CLUSTER
  PARITY is the invariant: every science primitive is the SAME object the certified local paths use
  (`build_prompt_set`/`LLMClient`/`extract_reward_source`/`_diversity_directive`/`_spec`/
  `schema.build_block`/`_test_seed_worker`), so the two substrates cannot run different science.
  `run_search_arm` mirrors `parallel._drive_llm_arm` step-for-step (reflect-on-generation-BEST, M5)
  but batches each generation as ONE array (candidates in a gen are independent → batching ==
  pool-training); F5 failures ledger + search-replay resume preserved. `run_test_leg` = the sealed
  leg as ONE `-tc`=pool array (93% of GPU-h at max concurrency). `run_arm_pipeline` =
  SEARCH→SELECT→FREEZE→TEST so an arm's test floods the instant its search ends.
  `run_campaign_on_cluster` = all arms' pipelines CONCURRENT (thread/arm; a shared authoring lock
  keeps the API arm-serial while training arrays interleave). `build_cluster_run` wires the production
  `ClusterRun` over `driver.run_batch` with a shared throttled puller + the hard `spend_guard`.
- **`run_one` leg-aware routing** — `leg=="test"` → `_test_seed_worker` (+ NODE-side env fingerprint,
  parity with the search leg's `_run_env_fp`); else the search `train_candidate`. Prompt threaded onto
  the search record for provenance. **`test_leg.build_test_specs`** extracted as the single source of
  the sealed-leg spec schema (reused by the local pool AND the cluster). ssh calls hardened
  (`BatchMode=yes -o StrictHostKeyChecking=accept-new`) so an unattended driver never wedges on a
  prompt (Tamer's interactive login untouched). `scripts/myriad/build_env.sh` (module-purge → venv →
  torch 2.6.0+cu124 → lockfile → `pip install -e` → `--smoke` GPU check; Apptainer fallback).
- **DEEP ADVERSARIAL AUDIT — 4 real bugs + 1 provenance fix, each regression-locked:**
  - **BUG-1 (resume contamination):** a test record carries the winner's `val_fitness`
    (`build_test_record`), and on the cluster both legs archived to the same arm dir → on RESUME
    `select_winner` (max val_fitness) could pick a test record. Fixed by DISJOINT search/test
    sub-roots (parity with the laptop's search_root/test_root split); the driver is subdir-agnostic.
  - **BUG-2 (concurrent-pull race):** the shared throttled puller only rate-limited — a pull outlasting
    `min_pull_interval` let a second arm thread start a concurrent `pull_archive`, both racing on the
    shared `.pull_tmp` staging dir. Fixed with a `busy` in-progress flag.
  - **BUG-3 (silent JSON coercion):** `write_specs` wrote task files with `default=str`, silently
    coercing a non-serializable field to a string — and because `payload_sha` ALSO used `default=str`,
    the sha check computed over the coerced form on BOTH sides and PASSED, so the node mis-trained
    silently. Fixed: strict JSON write that FAILS LOUD on the driver.
  - **BUG-4 (day-1 breaker):** the jobscript ran `python -m src.cluster.run_one` with `-wd`=Scratch
    while the repo lives at `~/llmrp` (not pip-installed) → `ModuleNotFoundError` on EVERY task. Fixed
    with a `PYTHONPATH={repo_root}` export ($HOME auto-binds into Apptainer) + `pip install -e` in the
    build script.
  - **REFINE-1 (provenance):** the cluster test record's `env_fingerprint` was the DRIVER's, not the
    V100 that trained the seed (misleading for the S6 sealed-leg homogeneity audit); `run_one` now
    captures the NODE env fingerprint, matching the search leg.
- **FULL confirmatory roster (completeness-critic pass).** Beyond the 5 LLM arms, the cluster now runs
  the whole frozen roster: **the 2 H4 family-search arms** (`run_family_search_arm` — `random_search`
  samples K family sources up front → ONE array; `bayes_opt` runs the GP on the driver, training each
  proposed coefficient vector as an array-of-1; both mirror `parallel._drive_search_arm` + reuse
  `sample_reward_source`/`bayes_opt_over_template`), dispatched in `run_arm_pipeline` (LLM vs family,
  parity with `run_parallel`); and **the H1 baselines** (`run_baselines_on_cluster` — fixed rewards,
  no search, flooding the pool from minute 0 as ONE concurrent test array, reusing the single-source
  `_baseline_winner_record`). H3 single-shot = a separate entry invocation (`--generations 1`).
- **`scripts/run_campaign_cluster.py` (NEW) — the production entry point.** Reuses `run_campaign`'s
  config assembly (panel/windows/agent-config/`build_parallel_opts`) so the cluster runs byte-identical
  science, wires `build_cluster_run` + `run_campaign_on_cluster` (arms + `--baselines`), and ships a
  `--dry-run` that validates the whole wiring WITHOUT a cluster (assembles config, builds one gen's
  specs through the strict-JSON guard, renders a jobscript) — verified end-to-end on the synthetic
  panel. The existing `supervisor.py` wraps it unchanged (`--campaign scripts/run_campaign_cluster.py`,
  idempotent `--resume`, auto-restart).
- **Verification:** 57 cluster/campaign/loaders/entry tests (incl. a full-roster CAPSTONE: assemble the
  real config → run an LLM arm + a family arm + an H1 baseline CONCURRENTLY through a fake cluster →
  assert the complete archive in the analyze_campaign parity layout) + the full not-slow suite GREEN;
  ruff clean.
  Documented-not-fixed (with rationale): deterministic sandbox rejects incur ≤2 fast-failing requeues
  before ledgering (impact = queue latency, not GPU-h — validation fails in seconds); the `git archive
  HEAD` push requires the cluster code committed first (Tamer-gated); the daily determinism-heartbeat +
  qstat queue-panel are cluster-side G1 features (need the live cluster to build/test).

## [2026-07-06b] — The 11-angle flawlessness review CLOSED, sequentially and first-hand: 22 serious findings verified + fixed, 29 minors, 4 delta-audits, the max-throughput plan

Tamer: "verify absolutely everything yourself, sequentially" (after the review workflow hit his token
limit mid-verify: 7/11 audits + 1 verifier completed; 22 serious findings + 29 minors recovered from
the journal). Every serious finding re-verified by ME against the current files before fixing; every
fix regression-tested. Commits `7cafd07` (code I), `4a3df91` (provenance/guards II), `f8d6a13`
(paper III). Freeze **20/20 @ `1c6b76b6` UNCHANGED** throughout.

- **The three biggest catches:** (S15) `run_recycling`'s whole-batch token-BLOCKING submission had
  quietly resurrected the crash-loss window the as-completed rewrite existed to close (+ would have
  false-CRITICAL'd the stall check every batch — S16); fixed with the bounded sliding window + a
  spawn-overhead-cancelling latency test. (S17) six documented sentinel checks + BOTH CUSUM drift
  monitors were PERMANENTLY INERT live — the gatherer never produced their inputs; producers built
  (cached archive scan, dual-layout ledger census, winner-divergence identity join, mirror age,
  config expectations). (S21/S5) the parallel search arms ignored `--resume` (~42 GPU-h re-trained +
  records overwritten per crash); hash-verified replay added, full-resume = zero re-training.
- **Sentinel truth restored:** transitions now PERSIST (sentinel-owned `sentinel_events.jsonl`
  sidecar — **corrects the [2026-07-05b] claim** that they reached `events.jsonl`: they never did
  from the standalone process); the journal probe unions `search/events.jsonl` (S20 — the documented
  invocation had every journal-backed check inert); coverage reconciles ledgered failures (S19 —
  summary rows now carry per-arm `n_failed`; an ACCOUNTED shortfall is WARN, not a false husk-CRITICAL);
  the fps baseline freezes at the first 10 samples ever seen.
- **Sealed-leg integrity:** `--cpu>0` on a REAL run is CLI-refused (S6: CPU≠CUDA bit-for-bit +
  token-race assignment = irreproducible device-heterogeneous seeds + degraded CRN pairing — costs
  no speed, the GPU is the binding resource); every test record carries `metrics.device`; test
  records now carry CONTENT-HASHED env fingerprints (per-arm `_env` snapshot, F12 reuse-on-resume;
  `load_run` verifies via the new shared-`_env` fallback that also un-no-ops the serial search
  snapshots).
- **Mechanism/inference wiring:** the pooled SQ1/SQ2 primary excludes `placebo_shuffled` (deranged
  values attenuated rho toward the predicted verdict — anti-conservative; it is the floor row now,
  S7); the SQ3b differential bootstraps SEED cells (K-clustered rows understated the registered
  decision CI ~√K, S8); the hash-frozen §2a(f)/(b)/(c) instruments are now CODE (per-arm fingerprint
  rows incl. the scalar arm's own-scalar A4 discriminator + the floor row; the declared-exploratory
  distance moderator; the Mayo–Spanos severity CURVE on every TOST companion — empirical, from the
  same paired draws) (S9); the B.5.2 FZ0 loss-differential Hill tail-index is IMPLEMENTED (per-leg,
  with the DM-companion heavy-tail flag); the regime block stratifies the median-tail-seed path;
  the SQ1 cells no longer condition on outcome availability; `h2_conjunction`'s docstring
  min→max corrected; the evt guard reuses the corrected `_was_fed_tail`.
- **Paper factual repairs (all my-verified):** the CONFIRMED CH3↔CH4 convergence contradiction
  (the bounded-agent premise now rests on true grounds); Table 3.1 reproduces the FROZEN §1a table
  faithfully (S22); the PopArt ablation is nowhere claimed in completed tense (S2 — the only
  artifact says the OPPOSITE); CH7's scorecard no longer invents pre-registered predictions for
  H3/H4 (+ H4b over-TEMPLATE); six theory-precision fixes (BSS finite-Θ, DPI finiteness, convex-order
  gloss, FZ Thm 5.2/Cor 5.4 pinpoint, elicitability scope, finite-valued-φ ball) + Berger's
  intersection–union naming + the NOMENCLATURE VaR gloss; the ratified v2 mechanism-led abstract is
  EMBEDDED (the deliverable shipped v1) + the Eureka-pillar-anchored title analysis (final pick =
  Tamer); CH6 gains the promised regime/synthetic-null/MCS-Bayes/mediation/fingerprint slots and
  B.7 no longer lists BUILT instruments as future work (S4); the compiled PDF structure is
  UCL-correct (ToC after the front matter, no double numbering, no "Chapter 9" appendix — S10,
  verified in the rebuilt PDF); `build_paper.py --final` = the submission placeholder lint (S13,
  finds today's 59 legitimate fill slots); the Moodle cover placeholder (S14); the word-surgery
  arithmetic corrected (S11); the seed-ratification checklist gains the paper 30-seed prose sweep.
- **Guard completeness:** freeze prompt-neutrality vocabulary + skew/kurtosis/\bVaR\b (11 tokens,
  prompts verified clean, hash unchanged); deterministic omitted-rng defaults in the search APIs;
  llm_calls.jsonl failures now WARN (rate-limited); `advance_author_stream` unit-pinned + the
  driver-level byte-identity regression (gen-0 replay ⇒ fresh gens author at uninterrupted
  positions); the rehearsal PASS banner names its certified path.
- **4 delta-audits (the angles whose auditors died):** session-crosscut (no submission-order
  collectors or min-gate twins remain; env/agents untouched this week), rl-env-sandbox +
  data-leakage (only the already-audited executor/loaders touches), tests-quality (new tests
  average 3+ behavior asserts). `docs/MAX_THROUGHPUT_RUN_PLAN.md`: the search-stage mode is the one
  big scheduling lever (serial ≈ +5 days vs the 3-worker mode the ~23-day plan assumes —
  amendment-gated, recommended YES at seed ratification); H3-parallel as the fallback lever; the
  TEST leg is already at the hardware ceiling; zero science cut.

## [2026-07-06] — Resume + monitoring pushed to the maximum: as-completed archival, the journal, 5 new sentinel checks, verified mirror, and an automated crash-resume certifier that immediately CAUGHT a real bug

Tamer: "very extensively work on the resume mechanisms — lose no progress — and detect ANYTHING;
push it to the absolute maximum." Blueprint `docs/RESUME_AND_MONITORING_HARDENING_PLAN.md` (now marked
EXECUTED). Commits `bb01e2e`, `df5a61f`, `43cfb21`. Freeze gate **20/20 @ `1c6b76b6` UNCHANGED**.
First, the 2026-07-06 adversarial audit of the session-2 diff returned **0 CRITICAL / 0 MAJOR / 4 MINOR**
— all four fixed + regression-tested (resume-correct monitor indices + dead `val_vectors` removed;
strictly-consecutive-generation dx/dm deltas per the registered §2a form; word-boundary `tail` matching
in the freeze prompt-neutrality guard so "detailed/retail" cannot false-block a freeze).

- **A1 — as-completed streaming archival.** `run_recycling` now collects futures the moment they
  COMPLETE (order-preserving return for the σ_D farm's positional contract): a driver crash mid-batch
  loses only in-flight work (was: up to `recycle_every−1` ≈ 12 completed trainings ≈ 17 h), and one
  wedged CUDA training no longer blocks the batch's archival. NEW `stall_after_s`/`on_stall` wedge
  DETECTION (pending identities surfaced when nothing completes in the window — the hang liveness
  checks cannot see). The parallel search drivers stop archiving at arm END (whole-arm loss): random
  archives per completion through a draw-order-preserving sliding window; BO per evaluation.
- **A2 — the journal.** Write side = the existing root-attached `events.jsonl` (ONE ledger, no drift)
  extended with `seed_done`/`seed_failed`/`test_leg_stall` events from the TEST leg
  (`config/campaign.yaml monitoring.test_stall_after_s: 5400`, wired at all 3 run_campaign call
  sites); read side = NEW `src/utils/journal.py` (torn-line-tolerant reader, completion stream,
  median/MAD cadence, error taxonomy).
- **B1–B7 — the detect-everything sentinel layer.** `completion_stall` (PRODUCTIVITY from the run's
  own cadence — WARN 3×/CRIT 8× median silence; catches the wedged-training-alive-driver hang);
  `coverage_search`/`coverage_test` (expected-vs-done UNIT ledger from config + ETA;
  claims-complete-with-missing-units → CRITICAL — the anti-husk guarantee at unit granularity);
  `error_taxonomy` (failures clustered by kind + affected arms); `disk_forecast` (predictive: "floor
  in ~N h" at the measured fill rate); fps direction-down CUSUM (thermal creep in hours;
  cross-candidate critic-CUSUM deliberately rejected — per-candidate scale would false-alarm);
  `monitor.py` B7 unified sentinel line in the dashboard + B6 `--heartbeat` DEADMAN (unconditional
  periodic ping; the external service alarms on ABSENCE — the only host-death detector). Live smoke
  immediately flagged a REAL risk: **C: free disk 18 GB < the 20 GB floor**.
- **A3 — stage-resume audit.** Verified skip-done on every stage + FIXED a real gap: the `p_arms>1`
  prototype path dropped `resume` (a partial arm restarted from scratch and re-billed the author).
  `--dry-run` honors `--p-arms`; new `--out`/`--resume` hooks.
- **A4 — actionable corruption handling.** A corrupt archive record fails LOUD naming the exact path +
  recovery routes (mirror restore preferred; delete-to-rerun ONLY for deterministic units — an LLM-arm
  record is irreplaceable, so auto-quarantine is deliberately rejected). `campaign_summary.json` now
  writes atomically (tmp + `os.replace`).
- **A5 — VERIFIED mirror.** `mirror_archive.ps1` re-hashes every mirrored tree against its sealed
  manifest via the new `verify-mirror` mode (sealed records intact; post-seal ADDS tolerated — a
  mid-campaign mirror lawfully carries newer work; exit 9 on backup rot).
- **A6 — the automated crash-resume certifier** (`scripts/crash_rehearsal.py`: reference →
  determinism control → hard TREE-kill at 1 record → resume → canonical byte-compare). **On its first
  execution it CAUGHT a genuine resume infidelity**: the Pass-A stub author was stream-positional, so
  a resume that replayed archived candidates without consuming their draws shifted every later
  candidate. Fixed with the search-arms' own discipline: the stub is now a pure function of
  `(seed, call_index)` and BOTH replay paths consume one author-stream position per replayed authored
  slot via duck-typed `LLMClient.advance_author_stream()` (real-LLM transports no-op — paid
  non-deterministic calls cannot be replayed by position; Pass-B semantics unchanged). Re-certified:
  killed at 1/6 records + resume == uninterrupted run, byte-identical.
- Runbook §3e-bis (one-command rehearsal), §5 (the deep-monitoring layer), §5b(iv) (verified mirror).
  Tests: +~30 across parallel-recycling/test-leg/journal/sentinel/dashboard/archive-integrity/
  results-io/crash-rehearsal/stub/llm-deep; ruff clean.

## [2026-07-05c] — Advanced methodologies: CUSUM change-point drift detection + a content-addressed archive-integrity seal; citations closed

Tamer: "close absolutely everything strictly flawless + implement very advanced methodologies." A fresh
adversarial auditor was put on the session-2 diff (author≠reviewer); two advanced, in-scope (report-only,
no frozen-design change, no forking paths) methodologies were added, and the last citation gaps closed.

- **ADVANCED METHODOLOGY #1 — statistical process control in the SENTINEL.** Added a one-sided Page (1954)
  **CUSUM change-point detector** (`scripts/sentinel.py::cusum` + `check_metric_drift`): the `--watch` loop
  accumulates the streaming gate-failure and NaN rates and alarms on a sustained upward DRIFT *before* any
  single value crosses a hard threshold — the right tool for "catch anything early". WARN-level (an early
  investigate signal; the threshold checks escalate on an actual breach). +5 tests (stable→no alarm,
  upward-drift→alarms mid-stream at the change-point, total on bad input, min-points gate).
- **ADVANCED METHODOLOGY #2 — content-addressed result-archive integrity seal** (`scripts/archive_integrity.py`).
  The archive is the one irreplaceable artifact (results replay from it), and nothing sealed it (the freeze
  hash seals the design; data checksums seal the inputs). Now a flat-Merkle manifest — every `record.json`'s
  SHA-256 under one verifiable **root** (line-ending invariant, matching the freeze convention). The driver
  auto-seals at campaign end (root stamped into `campaign_summary.json`); **`analyze()` re-verifies the live
  archive against the seal BEFORE trusting any number** and reports the verdict under
  `out["archive_integrity"]` — a modified/dropped/added record between run and analysis is caught loudly,
  never silently averaged in. Tamper-evident reproducibility. +6 tests (seal→verify OK, detects
  modify/add/remove, order-independent + deterministic root, line-ending invariance, unreadable-record
  perturbs the root). Runbook §5 documents both.
- **Citations closed:** `troop2021biascorrected` (bias-corrected POT-CVaR) is now CITED in CH4 §4.4 as the
  documented future-work extreme-value estimator (the bib entry existed but was uncited); `duan2021dsac`
  **web-verified** — published IEEE T-NNLS 33(11):6584-6598 (2021), DOI 10.1109/TNNLS.2021.3082568 — its
  `% VERIFY` flag discharged and coordinates completed. check_citations: 0 dangling / 0 verify-in-use.

## [2026-07-05b] — World-class run hardening: search-arm resume, the SENTINEL invariant monitor + precise logging, mechanism-kernel rewire, freeze gate 17→20; ~40 fixes

Second 2026-07-05 session. Tamer asked for (a) precise seed sizing, (b) world-class resume/checkpoint +
monitoring + LOGGING that "catches absolutely anything early", then (c) to close ALL flagged issues.
Master reconciliation: `docs/SESSION_MASTER_STATUS_2026-07-05.md`; seed decision:
`docs/SEED_DECISION_2026-07-05.md`. Freeze gate **20/20 @ hash `1c6b76b6` UNCHANGED** (the 3 new guards
are code, not hashed content); ruff clean; touched-file suites green.

- **Crash-resume — the real gap closed.** The two SEARCH arms (`random_search`, `bayes_opt`) had NO
  resume — a mid-arm crash re-trained from candidate 0 (up to ~40 h re-paid; a deterministic fault =
  an infinite crash-loop). Added per-candidate checkpointing + a hash-verified resume cache: the seeded
  draw sequence is regenerated identically, archived candidates skip training, and a source-hash
  mismatch fails LOUD. **Byte-identity certified** (`tests/test_search.py` ×2: the resumed archive ==
  the uninterrupted archive, only the un-finished tail re-trained). random_search re-draws + skips;
  bayes_opt re-fits its GP from the archived (x, y) so every subsequent proposal reproduces.
- **The SENTINEL (`scripts/sentinel.py`) — "catch absolutely anything early".** A continuous, READ-ONLY
  invariant health-monitor: 12 severity-graded checks (disk/RAM/GPU-temp, silent-hang, gate-failure
  rate, **NaN rate in the archive**, **critic-explosion clustering** + a CRITICAL if a FROZEN WINNER
  diverged, **cross-arm reward-scale drift** = the P5 confound made live, API error rate, exit-code,
  coverage/husk, mirror freshness). `--watch` loops; exits non-zero on CRITICAL; every check TRANSITION
  is written **severity-tagged to `events.jsonl`** (the precise, replayable health log). 16 tests; caught
  the real disk-low condition live. Runbook §5 documents it.
- **Watcher + ops:** ntfy rules `disk_low` + `anomaly_surge`; the watcher now SURVIVES exit-3 resumable
  passes (exits only on a terminal `exit_code==0`), so one launch covers the multi-pass run; mirror
  script exits 0 on success; runbook §5b pre-commits the Day-2 GO/RECHECK gate (treatment-blind), the
  integrity-only first-arm rehearsal, the anomaly-triage protocol, and the 6-hourly mirror task.
- **Analysis integrity:** **M19 husk statuses** (a no-shutdown total H1/H3 failure wave now banks
  `test_failure_wave`→exit 3, not a husk `tested`); **M15** the H3 single-shot subtrees are excluded
  from the default record walk (they collide run_ids with the headline distributional arm); **the
  mechanism-kernel rewired to the REGISTERED §2a estimand** — SQ1/SQ2 now use the tail the designer was
  FED (parsed from the archived prompt = prev-gen best), not each candidate's own post-training tail,
  with gen-0 excluded and per-generation deltas as the primary form (validated on the real prototype
  archive); `information_gap` fixed to read the fed prompt not the own-block; the **legible
  sub-experiment redesigned** to actually inject a real per-seed reference tail block (raw vs legible),
  with resume + the `left_tail_mass` percent-unit fix + purge/diversity threading.
- **Freeze gate 17→20** (non-hash-bound guards): R38 prompt tail-neutrality, search-split cross-assert,
  bound-file existence on the real root; + `preflight.check_generations_mirror` (the design-defining
  reflection depth was un-guarded). Hash `1c6b76b6` unchanged.
- **~40 verified small fixes:** attribution x26-refresh routing, loaders manifest-backslash + yaml-error
  intent, features `nanmean` market proxy, viz `iqm` NaN-strip, `dsr_effective_n` sorted NaN-safe winner
  scan, ood 2D-shape disambiguation, measurement bootstrap warning-storm, algos.yaml recorded SB3
  defaults, power-generator conditional-σ prose + window label + k80 sync + `CAMPAIGN_power.md` regen,
  requirements-test pins + pytest-timeout note, TEST_RIGOR counts/floor, equivalence-claim wording,
  .gitignore provenance-sidecar rescue, run_campaign stale spans/50k comments, §18-19 phantom cites,
  reflect-on-last comments, CLAUDE.md panel line, 4 planning-doc staleness banners, LIT-map examiner +
  RWW #8 attributions.
- **Deferred by decision (not drift):** write-up prose incl. the 2 corpus cites (troop2021, duan2021dsac);
  hash-bound edits batched for the seed-ratification amendment; P5/P6 + §9 extra-reward run (compute-gated).

## [2026-07-05] — Deep review + Claude Council + data/benchmark/lit sweeps; 10 verified fixes; hash-chain changelog gap closed

Full ledger: `docs/DEEP_REVIEW_2026-07-05.md`; the Tamer-decision brief: `docs/SESSION_BRIEF_2026-07-05.md`.
Installed the Claude Council (`.claude/commands/council.md` + 4 personas incl. examiner-okhrati/statistics-referee).
A 13-auditor read-only map surfaced **0 critical / 19 major / 63 minor** evidenced findings; a 4-seat council
deliberated the contested design calls; deep DATA, advanced BENCHMARK, and fresh LITERATURE sweeps ran. Protective
snapshot commit `cbe269c` (6 days of pre-freeze WIP; no secrets/licensed data staged); first archive-mirror pass.

- **Retroactive record (closes the CHANGELOG gap M07):** the four authorized pre-freeze hash-bound WORDING
  batches of 2026-07-04 (chain `3c2082…` → `5117d739` → `cedc576b` → `1c6b76b6`; R75 amendment; **NO decision
  changed** — P9 COVID-in-purge, P20 ξ small-sample bias, P17 leg-p pointer) and the **freeze gate growing
  15 → 17 checks** were applied in the overnight loop (`docs/OVERNIGHT_DEEP_LOOP_2026-07-04.md` rows 28–31) but
  never got a CHANGELOG entry until now. Current invariant: **17/17 @ `1c6b76b6`, frozen:false**.
- **10 verified fixes (all NON-hash-bound → hash UNCHANGED at `1c6b76b6`; ruff clean; 46 touched tests green):**
  - **Security (M03):** `sandbox/executor.ast_gate` now rejects non-`Load` attribute context — `np.mean = …`,
    `del np.mean`, `np.pi += 1` on allowlisted names used to pass and execute in-process, poisoning the
    process-global numpy across reused workers. +3 mutation-vector regression tests.
  - **Destructive-tool guard (M18):** `data_pipeline/scripts/purge_suffix.py` matched victims/ledger lines by
    substring while guarding by equality, so `--suffix _univ --yes` matched EVERY universe artifact incl. the
    frozen headline panel; now requires a digit-bearing suffix + a token-boundary regex.
  - **Freeze-readiness gate (M06):** `determine_design` reported FREEZE-READY at the pre-pilot 30-seed
    placeholder despite σ_D=0.369 firing the pre-registered ">0.10 → raise seeds" trigger; now BLOCKS n_seeds
    until amended. `DESIGN_DETERMINATION.md` regenerated (→ BLOCKED on n_seeds). +1 test.
  - **`mirror_archive.ps1`** leaked robocopy's success code (1) as a failing exit → maps 0–7 to exit 0.
  - **`.claude/hooks/freeze_guard.py`** now protects `config/algos.yaml` (B\*-assert-bound since batch-6 M1).
  - **UCL presentation compliance:** `build_paper.py` +`linestretch=1.5` +`helvet` sans default (portable);
    PDF rebuilds 315 KB / 0 warnings.
  - **Run-day safety (M05):** `CAMPAIGN_RUNBOOK` GO/NO-GO said verify `steps=50000` (frozen B\*=200,000) — would
    make an operator kill a correct launch; fixed + wall-clock marked superseded (→ ~23 days at ~350 seeds);
    reconciled the PopArt-absent / univ4r internal contradictions.
  - **CH4 factual (M09):** delisting-band "moves CVaR-5% by ~two percentage points" was a ×20 unit error (the
    move is ~2% RELATIVE, ≈0.1 pp) that also baked into the CH6 fill contract.
  - **Money guard (M16):** the legible sub-experiment is INERT at `generations=1` (the legible rendering never
    reaches a prompt) yet would burn ~1,500 paid Opus calls; `run_subexperiment` now refuses it fail-loud.
- **Sweep verdicts (details in the review doc):** DATA — `.SPXTR` / bid-ask / (pull) BAB-QMJ are the licensed
  under-exploited report-only wins; BENCHMARK — all 8 allocators + 9 rewards ARE implemented, the one genuine
  gap is a **min-CVaR (Rockafellar-Uryasev) allocator**, and §9 needs a two-tier amendment (council: run the 5
  extra rewards @ ~10 seeds); LIT — **0 scoops**, ~9 new fence neighbours (unverified leads; verify pre-submission).
- **Routed to the brief (Tamer-gated / careful):** seed ratification, §9 panel, freeze-gate additions, R76
  wording, TOST margin, the mechanism-kernel rewire (M13/M14, post-campaign, do carefully), H3-pooling verify
  (M15), parallel-husk status (M19), the write-up prose items, and the corpus citation gaps.

## [2026-07-04b] — 100-loop DEEP adversarial sweep (10 parallel auditors; confirmatory core verified solid, real prose/consistency findings surfaced)

Went deeper than the 20-loop pass: 100 distinct probes across 10 domains, one read-only adversarial auditor
each, told to FIND the weakest point. Parent verified every load-bearing finding first-hand; applied only
isolated safe fixes; recorded the rest. Full ledger: `docs/DEEP_SWEEP_100_2026-07-04.md`. Guardrails held (no
frozen-experiment change, no forking-paths, no scope creep, no fabrication; freeze gate stays 15/15, hash 3c2082).

- **Confirmatory CORE verified ROCK-SOLID first-hand:** statistics literature-exact (BH+drift-guard, three-way
  TOST that structurally cannot false-positive, Berger IUT, paired-seed rliable, DSR/PBO on full C(16,8),
  DM/FZ0/HLN, Bayes/MCS/TSED report-only); data reproduced against the on-disk univ5 parquet (333/333 terminals
  recovered, 0 changed cells vs univ3, purge 60/60, COVID in the purge, no ticker/date to a reward, 5/5
  checksums) — NO leakage; theory proof-core (M1/M2/M3/C2/C3/M4/M7) intact; ethics/AI-disclosure/H1/hedging
  clean; citations zero-dangling, high-stakes years/authors exact; tail-neutral base prompts confirmed.
- **Real findings (all safe to fix, none touching the core):**
  - **Prose ahead of code on REPORT-ONLY diagnostics** — 3 "claims an analysis that doesn't exist": mediation
    sensitivity analysis (CH7:60-62), FZ0 tail-index check (CH7:215), novelty draft-artifact ELfolio drift.
  - **B\* stale in the paper:** chapters say 50,000 training steps but frozen B\*=200,000 (configs correct); the
    B.2.1 "undertraining" limitation is inverted (design chose a CONVERGED budget). Biggest consistency defect.
  - **Precision over-claims:** "tail-blind" for a DSR selector that penalizes skew/kurtosis (6 sites); Table 3.1
    Null-row logic ("or"→"and"); "factorial dissection" for a report-only ablation.
  - **Deepest new objection (Loop 99):** the confirmatory H2 replicates training seeds (n=30) but NOT authoring
    (n=1 program/arm) → pseudoreplication; the CI generalizes to the programs, not the channel. Reinforces the
    mechanism-as-headline reframe (the across-candidate mechanism kernel samples authoring). To be disclosed.
  - **Two clean code-hardening gaps:** freeze.py has no assert_seeds_match/assert_matched_budget_match (silent
    post-freeze seed drift passes GREEN — timely for the 30→350 change); PopArt `raw*raw` has no overflow guard
    (finite |raw|≥~1.34e154 → σ=inf → zeroed critic, silently). Both additive fixes + tests.
  - **Manuscript mechanics (Okhrati-docked):** body 16,001 vs 10,000 words; 6/15 exhibits orphaned; motivating
    tail EDA absent from the body; no wall-clock/compute in prose.
- **FIXED this session (verified, isolated):** CH1:137 grade-modality leak excised (substance kept); theory
  Table 3.1 Null-row "or"→"and" (matches its prose + the responsiveness≤0 cell).
- **Routed to the overnight sequential loop** (each verified + logged, none touching hash-bound files): the
  paper-prose corrections (B\*, tail-blind, mediation/tail-index softenings, wording pins, pseudoreplication
  limitation), the two code guards + tests, the docs reconciles, and the depth additions (EDA passage, compute
  reporting, RQ scorecard, cross-refs, density). Seed-sizing code-vs-plan gap recorded for the ratification step.

## [2026-07-04] — 20-loop self-improvement sweep (structured self-audit; NO defect found, prior hardening held)

User directive: "add 20 self-improving loops … very strict … always verify … remember our priorities …
don't ruin anything … strictly flawless … record everything." Executed a 20-lens self-audit-and-harden
sweep under hard guardrails (no loop touches the frozen experiment or reacts to the σ_D result =
forking-paths; only isolated fully-verified safe fixes inline; everything else RECORDED, never silently
changed; no fabricated findings). Full ledger: `docs/SELF_IMPROVEMENT_SWEEP_2026-07-04.md`.

- **Outcome: NO critical or high defect found; zero safe-fixes were required** (nothing stale/broken/
  over-claimed existed to fix). The value is (a) CONFIRMATION that the 6-batch code review + 4-front paper
  audit + pre-freeze audit + EDA refresh + citation vetting had already closed this surface, and (b)
  confirming the post-verdict write-time items (ADD-0..6) are genuine forward work, not defects.
- **Load-bearing result (Loop 5):** the σ_D verdict introduced NO inconsistency into the drafted chapters,
  because the null framing was pre-committed to BOTH the equivalence and the bounded-effect/inconclusive
  branches (CH1:113, CH7:210-211, FRAMING:53). The verdict merely selects the branch — the pre-registration
  working as designed.
- **Tool-verified clean this session (grep):** no stale EDA numbers (14.52/20.4 only in the explicit
  supersession note; univ5 15.25/19.7% propagated) · citation-integrity flags all clear (Acerbi/Acerbi-Tasche
  distinct, Shumway 1997/1999 distinct, BAB-2014/QMJ-2019 years, FZ correction note, no Okhrati↔elicitability) ·
  CH7 limitations cover all named threats + construct-validity controls · FRONT_MATTER ethics/AI-disclosure/
  data-governance present · mechanism spine (responsiveness/mediation/ACME) present across CH4/CH6/CH7/theory ·
  novelty-fence neighbours present (first-hand-verified in prior sessions).
- **Recorded forward (not defects — expected work):** results/discussion write-up guided by the banked
  ADD-0..6; a final pre-submission deep-read pass (one theorem-level theory re-read; heavy-tailed DM-test
  tail-index check; figure/table cross-reference audit in the compiled PDF; the P7 word trim); the 4
  external-verify items from the literature re-read. seeds 30→~350 remains a pending pre-committed
  amendment (Tamer's ratification), not an inconsistency.
- No code, config, prose, or freeze-bound file was modified by the sweep (gate stays 15/15, hash 3c2082…).

## [2026-07-03c] — σ_D FARM COMPLETE + verdict banked · byte-compare CLEAN · power-analysis fix PROVEN · seed-count decision analysed · cloud ruled out at $50 · Okhrati email drafted

The pre-campaign chain resolved to two remaining USER gates (Okhrati's reply + Tamer's seed ratification).

- **σ_D farm COMPLETE — 30/30 cells, 0 failures** (15 differential_sharpe + 15 return_minus_cvar; median
  ~85 min/cell = 5090s; windows [60,3021]/[3081,3775]/[3835,5406] confirmed). Clean exit, no orphans.
- **THE σ_D VERDICT (pivotal unknown RESOLVED):** σ_seed=**0.244** (ann-Sharpe), σ_D=**0.369**, ρ=**−0.141
  (NEGATIVE** — Common Random Numbers gave no variance reduction, a finding to disclose). cvar_05 leg tight
  (σ_D=0.0015, ρ=+0.47). Practical equivalence at SESOI 0.05 DSR is NOT reachable at a small seed count, so the
  study banks the **pre-committed BOUNDED-EFFECT / INCONCLUSIVE null** and the mechanism headline (σ_D-robust)
  carries it. σ_seed dominating (~3× SESOI) is itself a publishable RL-fragility finding. `sigma_seed_pilot.py`
  ran under the m1/m2 fixes (UTF-8, outputs/sigma_pilot default). determine_design flips to **FREEZE-READY**.
- **M7-b5 BYTE-COMPARE DONE + CLEAN** (discharges the deferred reproducibility guard): re-trained
  differential_sharpe-s0 + return_minus_cvar-s0 with the CURRENT post-6-batch-edit code into `outputs/_bytecheck`
  and byte-compared `metrics.test_returns` to the archived cells → **bit-identical, max_abs_diff 0.000e+00**
  (test_sharpe −0.1564147893 in both). The archive mixes pre-edit (differential_sharpe s0-s8, written 07-02) and
  post-edit code (s9-s14 + all return_minus_cvar), and this proves the review edits are numerically INERT on the
  pilot path → σ_D is trustworthy with no re-run of the pre-crash cells.
- **power_analysis M2/M3 fixes PROVEN on real data:** ran the authoritative tool at the measured σ_D/ρ in
  **6 minutes 45 seconds** (the old "10–30 h hang" was a slow, block-buffered Monte-Carlo, never a deadlock).
  It drew ρ=−0.14 exactly (M3 signed-ρ, not clamped) with visible per-sweep progress (line-buffer). MDE@30 =
  0.181 Sharpe = 0.120 DSR vs SESOI 0.05. `docs/CAMPAIGN_power.md` regenerated with the real inputs.
- **SEED-COUNT decision analysed (freeze-gating; awaiting Tamer's ratification).** Built a throwaway exact
  seed→MDE sweep (`scripts/_seed_mde_sweep.py`, delete post-decision) reusing the authoritative power functions:
  SESOI crossing (MDE ≤ 0.05 DSR) at **n≈189** (point estimate). Strong-evidence sizing (power to the UPPER
  confidence bound of the n=15 pilot σ_D via chi-square): 80%→279, 90%→340, 95%→403 seeds. Recommendation =
  **arm-adaptive ~350 on the 2 H2 arms, controls at 30 → ~23 days, deadline-safe** (uniform-all-arms ~2× would
  miss 1 Sep). The pre-registered "30→50 if σ_D>0.10" is re-framed as a pre-pilot placeholder; the principled
  anchor is powering to the SESOI. Full rationale: memory `project-sigma-d-verdict-and-seeds-2026-07-03`.
- **Cloud compute ruled OUT at the $50 budget:** the campaign is ~500–4,400 GPU-hours and $50 buys ~250 spot
  GPU-hours (3–18× short of even the minimal design), so laptop-only stands and the $50 is reserved for the
  Anthropic reward-authoring API (~$30–50 for the Opus authoring; a hard spend-cap wiring is offered).
- **Okhrati supervisor email drafted** (many iterations → comprehensive, full timings, human voice): full
  status, the design/data/methods specifics, the prototype, the second model (Qwen, reproducibility anchor),
  the recently-found neighbours (GIFT 2606.08450 / ELfolio 10.34133/icomputing.0176 / Gallego 2603.19453) with
  honest distinctions, the recent rigor work, and 5 examiner-grounded questions (seed power · null-as-mechanism
  vs his ACL personality-risk work · offline-RL positioning vs his CQL · elicitability FZ0 foregrounding · which
  deep analysis to expand). Still owed by him: the written pivot sign-off (`docs/PROPOSAL_PIVOT_DISCLOSURE.md`).
  Awaiting his reply. (The four background readers that sourced the email confirmed the prototype/2nd-LLM/data-
  bias/paper/examiner facts against the docs — no new science, a consolidation.)
- **Post-farm queue (now unblocked, NOT yet run):** ONE full pytest suite validating every review fix, the
  farm-driver exit-code (M4-b5), the results.py sidecar tmp+replace (m3-b5), the RAM recalibration (m7-b5), the
  first archive-mirror pass, P3 sub-experiments, and scratch cleanup.

## [2026-07-03b] — SEQUENTIAL ULTRAREVIEW batches 4–6 CLOSED: sandbox/data (NO MAJOR), pipeline/persistence/ops (7 MAJOR), meta/freeze-chain (1 MAJOR). Full 6-batch review campaign COMPLETE; every finding closed to a flawless bar (user directive)

The review campaign is now COMPLETE across all six batches. Batches 4–5 are logged above ([2026-07-03]
continues below); this entry records **batch 6 (meta layer) + the user's "close absolutely everything,
majors and minors" directive** — every batch-6 finding closed, the safe-during-farm items now, the
farm-gated items queued with explicit triggers.

- **Batch 6 — test quality + config consistency + THE FREEZE CHAIN: 1 MAJOR + 7 minor, ALL closed.**
  The last audit before freeze found the freeze chain sound, no vacuous tests of load-bearing invariants,
  and config consistent across all nine YAMLs. Closed (freeze `--check` re-run GREEN 15/15, hash
  3c2082…, all Python ruff-clean):
  * **M1 (MAJOR) — B\* had no executed↔frozen freeze guard.** `train_steps_per_candidate` (B*=200k, R74)
    is the single most important executed number, yet it was the ONLY headline frozen quantity with no
    cross-file check: the hashed prereg copy was immutable but campaign.yaml/algos.yaml (what the run
    reads) are un-hashed compute knobs, and `preflight.check_budget_mirror` compares only campaign↔algos.
    A coordinated post-freeze edit of BOTH mirrors (e.g. to 250k) would pass budget_mirror, leave the
    hashed prereg at 200k, and run UNDETECTED. Fixed: `freeze.assert_train_steps_match` (the exact
    not-in-the-hash-so-assert idiom of `assert_executed_arms_match`/`assert_h1_baselines_match`), wired
    into `verify()`; freeze gate now **15 checks** (test updated + a `test_train_steps_drift_raises`).
  * **M5 — the frozen tail-diagnostic set had no prose↔yaml freeze check** (unlike sesoi/m/grid). Added a
    §4 guard binding each frozen CVaR level (round()-safe 0.10→cvar_10) + extra to a prose mention, so a
    pre-freeze yaml↔prose contradiction can't freeze silently.
  * **M2 — freeze check #13 (data_panel) read `config/data.yaml` via CWD, not `root`.** Correct for the
    real freeze (repo-root CWD) but CWD-fragile and untestable from a mini-repo. Threaded `root` through
    `assert_prose_matches_yaml`; made the mini-repo fixture faithful (copies data.yaml); added
    `test_data_panel_drift_raises` (the guard now RAISES on a drifted suffix, hermetically).
  * **M4 — the reward-author model was not consistency-checked.** It is common-mode across arms (doesn't
    break identification) and the served snapshot is archived as the repro anchor, so it is deliberately
    NOT hash-bound — but it's authored twice (campaign.yaml llm block + llm.yaml) with no drift guard.
    Added `preflight.check_model_consistency` (the budget-mirror idiom, at the INFRA layer not the freeze)
    + `test_model_mirror_logic`. A partial model swap now FAILs the gauntlet.
  * **M3 — config/subexperiment.yaml drift:** val_end was a stale pre-Split-C `2017-12-31` (a ~1yr val
    window vs the campaign's 3yr) → `2019-12-31` (matches inference/data.yaml); stale "50k-step main
    training" comments → B*=200k. Report-only + not hash-bound, but reconciled.
  * **M6 — FREEZE_RUNBOOK.md drift:** Step 0.2 told the operator to check budgets against the
    documentary-only `config/eureka_loop.yaml` (legacy 240 budget ≠ live 30) → repointed to campaign.yaml
    + the new freeze guards; the "rented RTX 4090" venue → laptop-only (2026-06-30); clarified DECISIONS.md
    (human ADR) vs docs/DECISION_LOG.md (freeze.py auto-append) are two intended files.
  * **M7 — stale test gold-gate:** `test_data_deep.py` gated on `returns_panel_univ3.parquet` while the
    active panel is univ5 → tracks `gold_suffix()` like its siblings; `test_run_campaign.py` fixture +
    assertion `== 50000` (stale, confusing "== 50k" comment) → 200000 with the buffer-cap decoupling note.
  * **M8 (informational) — two fail-loud stubs** (scripts/build_gold.py, verify_inventory.verify_splits)
    verified DEAD (no live caller; grep-confirmed) and correctly point to their real replacements
    (data_pipeline/ and freeze.py --check). A fail-loud stub naming its replacement is correct defensive
    behavior, not a defect — left as-is (deleting risks orphaning DECISIONS.md doc refs for zero gain).
  * **m4 (batch-5 carry) — corrupt-dir restart-loop:** added a CAMPAIGN_RUNBOOK §6 contingency row (quarantine
    the named dir → `--resume` regenerates the slot; never hand-edit a record to make it parse).
- **Farm-gated deferrals (documented with triggers — deliberate risk-management, NOT omission):** four
  items require touching the live σ_D farm's process tree or its realized data, so they are queued for the
  instant the farm exits, NOT done mid-run (the crash incident taught this discipline): **M4-b5** (farm-driver
  exit-code — editing run_sigma_pilot_train.py's process tree), **m3-b5** (results.py sidecar tmp+replace —
  farm workers call write_run; the narrow re-write trigger doesn't occur in this write-once farm anyway),
  **M7-b5** (byte-compare one pre-crash cell vs its archive before banking σ_D — needs a torch re-run),
  **m7-b5** (recalibrate the 3 per-worker RAM constants from realized r2 RSS). All in the post-farm queue.

## [2026-07-03] — SEQUENTIAL ULTRAREVIEW batches 1–3 CLOSED (stats core · campaign execution · training path): 1 gate-inverting MAJOR + 8 campaign-survival MAJORs + ~32 minors, all fixed + first-hand verified

User directive: "ultrareview my entire code … deeply review EVERYTHING … fix if something is off …
sequentially, don't blow up tokens." Protocol (post-incident, exclusive-phase-safe): ONE read-only
auditor per batch (Read/Grep/Glob only — zero process execution beside the running σ_D farm), findings
verified first-hand by the orchestrator at source before any edit, ONE fixer per batch, every fixer
hunk re-read and verified after landing, ruff over all touched files; **tests deliberately DEFERRED to
a single post-farm suite run** (runbook §0b). Batches 4–6 (sandbox+data · pipeline/persistence/ops ·
meta) follow the same protocol.

- **Batch 1 — statistical core (analyze_campaign + inference): CLEAN of critical/high; 11 fixes.**
  Conventions verified literature-exact (DSR/PBO/FZ0/rliable). Fixed: deterministic median-tail-seed
  selection path (`_arm_median_tail_seed_test_returns`, explicit sort key — no ndarray-comparison
  ambiguity); Bayes tail-equivalence ROPE made RELATIVE (tail_margin_fraction=0.25 of the IQM baseline);
  family-assert strict-superset guard (realized levels ⊃ frozen levels → refuse, not silently subset);
  NaN-safe winner scan (a NaN fitness can no longer win `max()`); JZS |t|>10 → bf10=inf guard (BF
  integrator overflow); contamination bootstrap 90% CI flag (opt-in return_draws). Plus finding-6
  (anomaly-clustering topology) carried to batch 5 scope.
- **Batch 2 — campaign execution path: 8 MAJOR + 12 minor, all fixed.** The MAJORs, each verified at
  source before fixing: **F1** parallel legs archived only at END (a crash at hour 20 lost every
  completed candidate → streaming `on_result` archival hook); **F2** `write_run` wrote record.json
  BEFORE its sidecars (power loss ⇒ a record that loads but replays hollow → sidecars-first with
  open+flush+fsync, `os.replace` of record.json is now the atomic COMMIT POINT); **F3** unbounded
  supervisor restart loop (→ `--max-total-restarts 60` + exit-2 non-restartable class); **F4**
  `--no-resume` foot-gun on a frozen run (re-bills Opus + violates the sealed once-only leg → hard
  refusal); **F5** parallel failures-ledger lost on mid-arm crash (→ append-per-rejection, mirroring
  the serial loop); **F6** 2-asset `_reinstantiate` fixture husked rehydrated winners (→ shared
  production-shape `_FIXTURE`); **F7** one shared reward_fn object coupled 30 test seeds' reward_state
  (→ per-seed reward rebuild in `evaluate_winner_on_test`); **F8** run-id scheme mismatch double-pooled
  search candidates (→ `_assert_search_mode_unchanged` prefix guard). Minors include drain-honest
  SHUTDOWN at seed boundaries (`frozen_test_deferred`), budget_spent = actual draws, max_tokens/
  max_retries threading, dry-run forces resume=False.
- **Batch 3 — training path (env/trainer/loop/search): 1 MAJOR + 9 minors; two structural verdicts.**
  **THE MAJOR (fixed by the orchestrator itself at 3 sites): the sandbox validation fixture fed
  equal-length 31/31/31 arrays while production calls `reward(weights(31), returns(30), prev(31))`**
  (portfolio_env.py:347-348; the FROZEN prompt promises exactly those shapes). The gate was therefore
  INVERTED for shape-aware rewards: a spec-faithful `weights[:-1] @ returns` was falsely REJECTED at
  validate_once (burning budget slots) while a sloppy `weights @ returns` was falsely ACCEPTED and then
  zero-trained via SAFE_DEFAULT substitution on every real step — uniform across arms (no H2 bias) but
  a direct campaign-quality threat. Fixed at `parallel._FIXTURE` / `loop.run_loop` fixture /
  `random_search._default_fixture` with shape-parity why-comments; `tests/test_loop.py` +
  `tests/test_llm_deep.py` reconciled to the spec-faithful form (validated post-farm). **Verdicts:**
  the t/t+1 alignment chain is CLEAN (obs strictly past; scored return enters only the next obs; VIX
  pre-lagged at load; sealed windows physically absent from search bundles) and the **σ_D pilot↔campaign
  parity PASSES** (same windows/trainer/agent-config/seeding/test-record builder; the two deltas —
  campaign-only thermal governor, device literal — are result-neutral), so tonight's σ_D transfers to
  the freeze decision. Minors fixed (one fixer, all hunks re-verified): training-time SAFE_DEFAULT
  substitutions now WARNed + archived as `train_safe_default_count/_call_count` candidate metrics
  (trainer resets counters before `model.learn`, reads after, attaches to the policy on BOTH branches;
  loop + parallel worker archive them — the old "flag the candidate" promise was dead code, docstring
  corrected); `docs/environment_spec_v1.md` → v1.1 (drift convention documented as the implemented
  r_t form incl. the cash sleeve g_cash = 1+cash_daily_rate, with the ≈hundredths-of-a-bp/step
  magnitude + identical-across-arms note; state section corrected to the real `_obs` incl. SIMPLE
  returns + dim 1,893; the nonexistent `RewardContext` API replaced by the real 5-arg contract);
  R18 purge-guard ARMED on both SEARCH gold paths (`make_env_builder(..., embargo, lookback)` at
  parallel.py + run_prototype.py; synthetic stays legacy-inert 0/0 by design — its windows abut);
  `_panel_and_windows` cache key completed (+on_missing +embargo_days +lookback); arm-start
  `reset_fed_estimator_log()` at both drivers (T2.8b scoping); PopArt docstrings softened to the honest
  approximate-invariance claim (exact only at constant σ / unit scale; residual auditable via R48 +
  the popart=False ablation); preflight `ALLOWED_AGENT_KEYS` typo guard (25 consumer-enumerated keys
  over campaign+prototype agent blocks — cfg_get's silent-default trap closed; `net_arch` deliberately
  NOT block-level); `info["weights"]` zero-copy `setflags(write=False)` freeze (project_simplex verified
  fresh-array on both branches). Flagged not fixed (diagnostic paths, same purge-guard pattern):
  run_subexperiment.py:185, learning_curve.py:301.
- **Verification discipline note:** every fixer claim above was re-read at the diff site; the batch-3
  fixer's 12 substantive hunks were 12/12 true to report. Post-farm queue: the ONE full test suite
  validating all review fixes (incl. the reconciled test files), power_analysis hang diagnosis,
  CAMPAIGN_power.md regen, first mirror_archive.ps1 pass.
- **Follow-through closed same session:** (a) the batch-3 fixer's flagged optional gap — TEST-leg records
  now archive the R66 counts too: `build_test_record(train_safe_default_count=, train_safe_call_count=)`
  (None-default = byte-identical for the running σ_D pilot's call site, which was deliberately NOT
  touched mid-farm) + attr-read/pass at BOTH seed paths (test_leg._test_seed_worker, run_campaign serial
  evaluate; ruff clean); (b) batch-2 **F16** recovered verbatim from the transcript and BANKED with two
  sibling disclosures as `docs/LITERATURE_SWEEP_2026-07-02.md` "REVIEW-CAMPAIGN WRITE-UP NOTES" —
  resume-lineage caveat (disclose iff `meta.llm_error_skips`>0 on a resumed arm), the training-substitution
  audit statistic as a CH4 audit-kit row, drain-honest `frozen_test_deferred` semantics (ops appendix).
- **Batch 5 — pipeline + persistence + ops: 7 MAJOR + 10 minor — the review's richest haul, clustered
  on the POST-FARM freeze chain and the campaign ops layer.** The freeze-chain-critical fixes landed
  by the orchestrator the same hour (all verified at source first; ruff clean):
  * **M1 (freeze-gate integrity):** determine_design flipped n_seeds DETERMINED off the σ_D JSON's mere
    EXISTENCE — but sigma_seed_pilot.py writes that JSON unconditionally (even `status="skipped"` on an
    empty archive), and its in-JSON success flag was read by NO ONE. A failed/husked farm could have
    reported FREEZE-READY. Now: the evidence parse requires the sharpe-leg `sigma_seed_pilot: true`
    flag AND an n_shared floor (≥ 12 of the 15 planned CRN seeds); `recommended_n`/`n_shared` surfaced
    into the evidence notes; an unreadable artifact is NO evidence.
  * **M2 (the power_analysis "hang" DIAGNOSED + FIXED):** not a deadlock — a ~10-30 h single-threaded
    Monte-Carlo (11 MDE sweeps × 41 grid points × 2000 sims, each a 2000-replicate PURE-PYTHON
    bootstrap ≈ 1.8×10⁹ replicates) with block-buffered stdout (zero bytes for hours → mis-read as
    hung; 3 orphans killed). Fixed threefold, semantics-preserving: (a) `paired_seed_difference_test`
    gained a VECTORIZED IQM fast path (`_iqm_rows`) that is **bit-identical** to the loop — one
    C-order (n_boot,n) index draw consumes the same RNG words as the old per-iteration draws; non-iqm
    statistics/non-finite inputs keep the reference loop over the same index rows; equality pinned by
    2 new regression tests (bitwise `==`, incl. n<4 and the NaN gate) in test_audit_regressions.py;
    (b) `minimum_detectable_effect` early-exits the grid at the target-power crossing (each point
    re-seeds `default_rng(cfg.seed)`, so every kept value is byte-identical; grid/power truncate
    together); (c) line-buffered streams + per-sweep/per-ρ progress prints. Expected wall-clock:
    minutes, not days. Wiring verified while there: T=694 both sides, k=0.66157, SESOI from frozen
    config, measured σ enters as --sigma-seed.
  * **M3 (negative-ρ clamp):** `_draw_paired_scores` silently clamped ρ<0 to 0 — understating
    σ_D=σ√(2(1−ρ)) exactly in the branch where the pilot's own report says "trust the Monte-Carlo".
    Now a Cholesky pair draws the measured NEGATIVE ρ exactly (all three normals drawn on both
    branches → the ρ≥0 stream stays byte-identical to pre-fix); the pilot's markdown advice corrected.
  * **m1:** sigma_seed_pilot's σ/ρ console glyphs crash a legacy-codepage console AFTER artifacts are
    written (the farm twin already carried the fix) → UTF-8 reconfigure copied in, BEFORE parse_args
    (the parser description itself contains σ_D). **m2:** the analyzer's default `--root` pointed at
    outputs/campaign (zero pilot cells → a skipped JSON written exactly where resume_brief looked) →
    default now outputs/sigma_pilot; resume_brief's phase probe repointed.
  * Remaining batch-5 items LANDED by the fix agent + verified first-hand by the orchestrator (ruff
    clean; mirror_archive.ps1 static-parsed 0 errors): **M5** (the ratified SERIAL headline campaign
    ran with NO RunMonitor — watcher/stall/anomaly ALL inert on the frozen protocol → one RunMonitor
    built lazily on the first serial search under `<output>/search`, arm_start/arm_done bracketing +
    crash-path close(status=error) + normal close, mirroring run_prototype; gated `not synthetic` so
    the ~15 synthetic wiring tests stay byte-identical and the observability targets exactly the gold
    run; H3 single-shot is a separate report-only root, left unmonitored by design — verified
    search_root defined at :1347 before use, crash close cannot double-fire vs the :1660 normal close),
    **M6** (finding-6 resolved: `anomaly()` stamps in-flight arm/cand onto id-less rows; dedup key
    →(kind,step,cand) so cross-candidate rows survive; ParallelMonitor threads arm/cand into
    _check_training_anomalies + failure_wave; loop.py llm_error/training_error gain arm/cand), **m9**
    (STATE-like kinds {entropy_collapse, entropy_explosion, fps_collapse} fire ≤once per (kind,arm,cand)
    — correct on BOTH serial and parallel paths, worst-case ~450 bounded entries), **m10** (parallel
    fitness_nan parity), **m6** (supervisor --no-resume guard hardened: `_abbreviates_no_resume` refuses
    --no-r…--no-resume[=…] the 6-char minimal disambiguating prefix, still allows --no-shutdown), **m8**
    (mirror shrink guard: skip a /MIR pass when the destination record.json count EXCEEDS the source's,
    -Force override; PS-5.1-safe). Plus the m5 doc note in parallel.py (the two failures-ledger layouts
    never cross-replay — guarded by _assert_search_mode_unchanged). Deferred to post-farm ON PURPOSE:
    **M4** (farm driver exits 0 despite failed cells — the driver is RUNNING; compensated by M1's floor
    + manual chain control), **M7** (mixed-archive code-version check: byte-compare one pre-crash cell
    re-run vs its archive before banking σ_D), **m7** (RAM-calibration recalibration from realized r2
    RSS), **m3** (sidecar tmp+replace on overwrite), **m4** (corrupt-dir quarantine = runbook note).
- **Batch 4 — sandbox + data layer: NO MAJOR; 8 minors, the actionable 5 closed.** The layer's two
  make-or-break properties verified end-to-end by the auditor AND re-verified at source by the
  orchestrator: (i) NO look-ahead anywhere — obs strictly `returns[t-lookback:t]`; `market_reference`
  is forward-fill-only (RF `(1+DGS3MO/100)^{1/252}-1` correct against the raw CSV; FF factors decimal,
  no rescale); the val purge (=lookback=60) lands the earliest val feature exactly at the train
  boundary, non-inclusive; allocators/momentum consume only the strictly-past window. (ii) Sandbox
  containment holds — the 06-26 from-import RCE fix intact (ALL `ast.ImportFrom` rejected), attribute
  allowlist + banlist + dunder walls + forbidden-call check on Name AND Attribute forms + format-field
  regex; `np.random` unreachable (protects determinism); `safe_call` catches `Exception` only
  (KeyboardInterrupt/SystemExit propagate); the reward receives detached read-only copies. Fixes
  landed (all by the orchestrator, ruff clean): headline gold load now ALSO runs the semantic
  contract — `load_gold_panel(..., validate=True)` (strictly-increasing-dates leakage invariant on
  the hot path, #7); `validate_panel` market-caps conditions split so non-finite caps are flagged
  instead of silently skipping the negativity check (#8); counter SEQUENTIAL-USE INVARIANT documented
  at the definitions (#4); the `safe_call` containment-boundary note rewritten to the WINDOWS TRUTH
  (parent-enforced wall-clock timeout is real everywhere; the POSIX rlimits are a silent no-op on the
  laptop the campaign actually runs on — the stale "Linux campaign box" framing superseded) + the two
  accepted residuals recorded (value-dependent cost; unbounded `reward_state` accumulation) with the
  operational recovery path (#1+#3); NEW runbook §6 contingency row "Hung candidate (in-process
  reward)" — stall alert → kill → `--resume`, un-archived slot regenerates, budget matched; NEW
  cross-resolver pin test `test_both_window_resolvers_agree_with_the_univ5_registry` (both
  independent purge-arithmetic implementations pinned to `expected_windows.univ5`, #6; runs in the
  post-farm suite). Deliberately NOT changed: `components`-value screening (#2 — grep-verified that
  `info["components"]` never reaches any serializer, so it is cosmetic; hot-loop purity wins) and the
  inline-fallback timeout (#5 — reachable only if worker daemonization changes, documented).

## [2026-07-02m] — INCIDENT + RECOVERY: concurrent-load crash killed the σ_D farm's 2nd arm; resume clean; EXCLUSIVE-PHASE rule codified

- **The incident (operator error — the agent's own scheduling):** two ultrareview WORKFLOWS (~20
  concurrent agents, many running pytest with torch imports) were launched WHILE the 3-worker σ_D farm
  was running. Combined RAM+VRAM exhaustion: `differential_sharpe` banked 6/15 cells, then ALL 15
  `return_minus_cvar` cells failed (MemoryError 361 MiB obs-array / CUDA OOM / WinError 1450) and the
  IDE session itself died. THE CRASH-SAFE DESIGN HELD: the farm logged every failure, kept its 6
  atomic records, exited cleanly with the honest 6/30 summary.
- **Recovery:** 8 orphaned processes killed (incl. THREE power_analysis.py runs HUNG for hours — the
  real cause of the "silent" power-doc regen failures; investigate its runtime after σ_D) + 1 orphan
  pytest holding the CUDA context. σ_D **resumed**: the done-scan skipped exactly the 6 archived cells
  and re-farmed 24 (PID 14832, AboveNormal, watcher re-armed) — the resume machinery's first REAL-fire
  worked byte-exactly as its tests promised. Clock lock intact (no OS reboot — only the session died).
- **Codified:** runbook §0b **EXCLUSIVE-PHASE RULE** — during ANY farmed leg (σ_D or the campaign TEST
  leg): no agent fleets, no test suites, no review workflows, no torch-importing side processes; the
  wave margin belongs to the recycle waves. The two review workflows are RESUMABLE with cached agents
  (run IDs wf_f0d8597f-6f5 fresh-code / wf_f786dab7-d31 full-surface) — they re-launch AFTER σ_D exits.
  The instruments build (information_gap.py 24 KB + headroom.py 12 KB on disk, stopped mid-build) gets
  verified/finished after σ_D too. Deferred with them: the power-doc regen.

## [2026-07-02l] — Write-time literature wave EXECUTED EARLY (8 items, 18 verified bib entries) + 2 MORE registered instruments (fingerprint + reflection funnel)

- **Prereg §2a gained (f) + (g)** (gate-verified, hash 3c2082): the **MECHANISM FINGERPRINT** — 4 rival
  accounts (genuine-use / readout / execution / prior-dominance) × 6 instruments with ex-ante predicted
  signatures, incl. the A4 discriminator = the SCALAR arm's own responsiveness, and the A4↔Hartley-Okhrati
  risk-preference-prior anchor — and the **REFLECTION-FUNNEL content analysis** (QUOTE→COMPARE→CONCLUDE→
  IMPLEMENT staged coding of the designer's own reasoning text, dual-coder + κ, exploratory; the accounts
  predict DIFFERENT drop-off stages = the qualitative cross-examiner of the fingerprint). To our knowledge
  no LLM-agent study has either. Sweep-doc NOVELTY-GENERATION ADDENDUM records d/e/f/g + 3 write-time
  garnishes (detector-blind-spot methods note; NAME the audit kit; release it as an artifact).
- **The "write-time" literature items executed NOW** (agent; independently verified: 193 bib entries
  0/0/0 · gate 13/13 · PDF 321 KB 0 warnings): examiner's papers FINALLY in prose (Hartley→CH1/CH7;
  Khraishi→CH4 inside a new simulated-online-NOT-offline-RL paragraph w/ levine2020offline+kumar2020cql);
  the numeracy evidentiary base (cookbook/ICLR-2025 + sandoval format-flip + singh tokenization + zhang
  comprehension-without-competence — CH1 bracket + CH7 B.3.2); mediation canon (imai/mackinnon/orourke +
  sequential-ignorability honesty clause); theory §3.7 attainability now FORCED (bauerle2011markov +
  lim2022cvar: state augmentation + non-Markovian ⇒ the reward channel is the forced injection point);
  fence one-liners (LLM-judge-SAC, nie+fcp directional-feedback, LEARN-Opt null-corroborator licensing
  the 30/30 design); the named "profit mirage" contamination defence (CH4 ¶ + Table 4.1 row + CH7);
  null-lineage bracket (webson+schaeffer); **the two crown sentences**: "the first pre-registered,
  controlled, inferentially DECIDED instance of feedback engineering for reward design" (CH2) + "the
  first factorial dissection of the feedback channel — content × encoding" (CH1). +682 body words
  (body now 16.0k → the P7 trim grows accordingly; every insertion rides the trim as a swap).
- 18 new bib entries, EVERY one verified first-hand on its primary page (2 plan corrections caught:
  sandoval's pair is 9.11-vs-9.8; CWC single-author). Fix-on-sight: word_budget.py now correctly
  EXCLUDES word-excluded appendices (was over-counting CH7 by ~1,174 words).

## [2026-07-02k] — NOVELTY RED TEAM (3 falsifiers) + consolidation: NINE battle-tested firsts; 2 NEW registered instruments; fence current through July 2026

User directive: "must be genuinely novel and FIRST." Response: three adversarial red-team agents whose
SUCCESS CONDITION was falsifying the first-ness claims (~20 search fan-outs incl. GitHub code-search,
SSRN, thesis repositories, OpenReview API; 12+ full primary-source verifications incl. first-hand reads
of RDA's experiments section and GIFT/ELfolio full texts).

### Verdicts
- **Broad wordings FALSIFIED (as designed):** "first prereg LLM×finance" (Powdthavee 2604.20652 exists,
  fraud-advisory), "first feedback-content variation" (Eureka's snapshot ablation + CARD's leave-one-out
  are literal engineering-grade counterexamples), "first format ablation in an agent loop" (Goodyear
  routing-games; Agent Trading Arena text-vs-chart). **The narrowed claims SURVIVED every attack** — and
  the neighbours found actively CORROBORATE the numeracy mechanism (Agent Trading Arena: LLMs mishandle
  plain-text numbers in trading loops).
- **Core claims STAND, sharpened:** GIFT's own text FORBIDS open-ended authorship ("select, transform,
  and compose" from a registered library, "parameters are clipped before execution"); RD-Agent(Q)
  publishes its exact 8-metric feedback vector — max-drawdown yes, CVaR/ES/quantiles ABSENT — the
  perfect one-line contrast. WORDING HAZARD codified: drawdown IS fed to LLMs elsewhere → all tail
  claims pin to CVaR/ES/tail-quantiles/distribution-summaries, never "risk metrics".
- **NINE battle-tested firsts** recorded in RELATED_WORK_WATCH.md (content-as-IV prereg+placebo
  experiment · tail-vs-scalar manipulation · CVaR-vectors-to-designer · prereg-in-LLM-reward-design ·
  equivalence-capable inference on the contrast · three-way decoupling · open-ended reward-code
  authorship for trading RL · first prereg LLM-agent study in trading AT ALL [77-study survey: zero] ·
  numeric-encoding ablation in a reward-design loop).

### Consolidation (agent; independently re-verified: citations 175 entries 0/0/0, gate 13/13)
7 new first-hand-verified citations (gallego2026beyondscalar [coins "feedback engineering" — the
founding-rigorous-study slot is OURS to take], sharma2026algoevolve, li2025rdagentq, han2026quantaalpha,
tang2025alphaagent, darmanin2025lmguided, lee2026rda) + the attack-proof feedback-content paragraph
(CH2 §2.1) + GIFT fence upgraded with the constraint quotes + the R⁸-vector contrast + 2 falsifiable
wordings fixed (CH2:117, CH1:69 → "to our knowledge") + 00_FRAMING cite-and-distinguish list extended +
FunSearch duplicate bib entry merged (fix-on-sight). Corpus integration (separate agent): GIFT +
LLM-judge-SAC PDFs binned with full-text 0-CVaR confirmation, integration-map §6 + dossier §B.2 entries,
ELfolio venue-refreshed.

### TWO NEW REGISTERED INSTRUMENTS (prereg §2a micro-anchors d+e, pre-freeze — novelty CREATED, not just defended)
- **(d) Information-utilization gap**: measured redundancy of the fed tail vector given the scalar on the
  ACTUAL archived feedback sequences (placebo_shuffled = built-in calibration floor) vs SQ1's usage →
  "given vs used", quantified. Kills the "the tail carried nothing extra" objection with data.
- **(e) Validation-headroom (oracle-selection) bound**: best-achievable validation CVaR/DSR over ALL
  authored candidates vs achieved selection, per arm — establishes headroom EXISTED (sealed leg
  untouched). Kills "there was nothing better to find". Together with SQ1-SQ3: the first fully
  QUANTIFIED localisation of where information dies in an LLM-designer loop. Gate re-verified
  (hash c6a2f54a, intentional).

## [2026-07-02j] — ULTRA literature/publishability sweep (125-agent, 6 lenses, adversarial triage): 59→51 adopted; novelty fence refreshed; prereg micro-anchors landed

- **The sweep** (user-directed "anything missed / more publishable"): six parallel research lenses
  (fresh-scoop watch · corpus mining · methods standards · examiner alignment · numeracy frontier · venue
  fit), every finding judged by a science-fit judge (identification/no-scope/rejected-list/freeze-clock) AND
  a value judge (grade+TMLR per effort). **Verdict: nothing material missing experimentally — all 51
  survivors are citations/fences/reporting/prose; zero new runs/arms/inputs needed.** Durable roadmap:
  `docs/LITERATURE_SWEEP_2026-07-02.md` (TOP-10 + full queue + scoop register; ~45-50h total, ~6h pre-freeze).
- **Scoop closure (pre-freeze, executing)**: GIFT (arXiv 2606.08450, June 2026 — nearest published neighbor;
  varies state+reward jointly, no CVaR, framework not experiment → the conjunctive novelty cell SURVIVES but
  broad "no prior work" claims must tighten) + ELfolio (now VENUE-PINNED: Intelligent Computing, DOI
  10.34133/icomputing.0176 — its evolutionary fitness is a SCALAR Sharpe, i.e. the closest competitor
  instantiates OUR scalar control arm) — fence agent adding verified bib entries + fence sentences +
  broad-claim tightening + the dated RELATED_WORK_WATCH entry.
- **Prereg §2a micro-anchors (DONE, dated 2026-07-02)**: (a) SQ3b now adjudicates two NAMED rival accounts
  ex-ante — READOUT (encoded-but-not-verbalized; legible rendering recovers responsiveness) vs EXECUTION
  (format won't help) with predicted directions each way; (b) declared-exploratory numeric-distance
  moderator of responsiveness (report-only, CVaR-fed arms); (c) the post-data severity-curve presentation of
  the TOST result registered ex-ante. Freeze gate re-verified ALL-OK after (hash e3395985, intentional).
- Notable write-time levers banked (see the sweep doc): examiner's own papers currently cited in ZERO
  chapters; SQ3's numeracy claim rests on one 2019 cite while a 2024-26 canon exists; mediation terminology
  uncited; Bäuerle-Ott/Lim-Malik make §3.7 probabilist-grade; CH1↔CH6↔CH7 promise mismatch (run MCS on the
  archived matrix; BF01 needs its CH6 slot); NeurIPS-checklist compute table closes a named examiner dock.

## [2026-07-02i] — Dormant-items wave: Qwen3-Coder PINNED + WIRED (R71 executed) · P3 verified ready · FTSE rescheduled · two more live-constant catches

- **Qwen3-Coder second designer (R71) — wiring COMPLETE, key-gated** (agent build, independently
  verified: 33+105 tests, ruff, smoke exit-2 behavior observed, freeze hash UNCHANGED by the code
  work = headline path byte-untouched). `src/llm/client.py`: `openrouter` base-url + key-env registry
  entries (the transport was already provider-neutral, ADR-035) + a **served-model reproducibility
  anchor** (`ProvenanceRecord.served_model` — OpenRouter's exact snapshot string archived per call).
  `config/llm.yaml`: `open_weights_check_model: "qwen/qwen3-coder"` + provider/key-env keys (PIN_ME
  resolved). NEW `scripts/smoke_qwen.py` (key absent → actionable exit 2; key present → one-call smoke
  printing the served-model anchor). Prose reconciled as dated notes (prereg §8 V10 + R71 register row
  + MODEL_CARD): pinned 2026-07-02, NOT yet executed — the plural-"LLMs" guardrail stands until the
  secondary panel runs. **USER item: OPENROUTER_API_KEY in .env (~$1-3), then `scripts/smoke_qwen.py`.**
  Campaign-window follow-ups listed: cost-table entries for Qwen pricing; a secondary-panel run-config
  llm block (Qwen honors temperature=1.0 — no prompt-variation workaround needed).
- **P3 sub-experiments verified launch-ready** (`run_subexperiment.py --mode named|legible
  --output-dir ...`; keyless `--synthetic` rehearsal available) — slot: the σ_D→freeze gap.
- **FTSE-100 lite RESCHEDULED to the campaign window** (report-only external validity, not
  freeze-bound; the ~11 GPU-busy/API-quiet days are the natural slot; zero science cost).
- **Two more flawlessness catches**: `sigma_seed_pilot.py` carried a LIVE stale
  `DEFAULT_TRACK_LENGTH = 756` (would have mis-scaled TONIGHT'S σ_D Sharpe→DSR verdict; → 694,
  matching power_analysis) + a latent sibling-import test-isolation flaw (self-providing path; 13/13
  solo) + freeze.py phantom-"§18" message refs (→ §1 + register).
- σ_D farm healthy: first wave archived (3/30 cells), GPU 58%, 53 °C, ~9 h pace.

## [2026-07-02h] — PRE-FREEZE DEEP AUDIT executed + fixed (1 CRITICAL, 4 HIGH, 9 MEDIUM, 5 LOW) · B* = 200k SET (R74) · rehearsal gauntlet GREEN · σ_D pilot LAUNCHED farmed

User directive: "before freezing, everything justified scientifically by evidence; before the campaign,
absolutely everything ready and flawless." Two audit agents (citation-verifier + post-Split-C
staleness/justification auditor) + the ladder verdict + the full gauntlet, all in one wave.

### The CRITICAL find (C1) — the frozen protocol description contradicted the executed code
The 2026-07-01 amendment + yaml mirror said the headline search reflects on each generation's LAST
candidate; the CODE (verified `src/llm/loop.py:604-615`) reflects on the generation's **BEST** (the
earlier M5/R32 upgrade — Eureka-faithful; CH4 already described best). Freezing that text would have
hashed a protocol the campaign does not execute. **Corrected as a dated amendment note** (the ratified
DECISION — serial execution for reliability — unchanged; only the label): prereg §6 + yaml
(`serial_reflect_on_best`) + runbook §0/§4/launch-commands (which still taught R24's superseded parallel
headline, incl. a `--search-gpu 8` "fallback" the CLI would REFUSE) + `run_campaign.py` help. Bonus: the
old "reflect-on-last deviates from Eureka" disclosure DISSOLVES — the headline is Eureka-faithful.

### The HIGH finds (all fixed) + a 13th freeze-gate check
- H1: prereg §7 residual sentence + yaml `data_panel.headline` still declared **univ3** the frozen
  headline (never mirrored by R73) → univ5 everywhere, univ5s/zero-surcharge finding integrated;
  `correct_panel_on_repull: univ4r` → `corrected_panel_executed: univ5s`. **freeze.py gained check #13**:
  `data_panel.headline == config/data.yaml gold.suffix == prose` — this drift class can never freeze
  silently again (test updated to 13 checks; gate verified live ALL-OK).
- H2: the pre-registered VERBATIM bankable-null statement named the wrong sealed span (2018–2025) →
  corrected to 2020–2026H1 with a dated note.
- H3: prereg §1 asserted unconditional validation-selection of the H1 baseline; the pipeline falls back
  to disclosed sealed-leg selection (R49) → §1 now states the executed truth.
- H4: runbook launch commands modernised (see C1).

### The MEDIUM/LOW batch (fixer agent; independently gate-verified)
M1 power arithmetic re-anchored to the EXECUTED val window T=694 (was 756): k 0.6905→0.6616, SESOI
0.05 DSR ≈ 0.0756 ann-Sharpe (was 0.0724), MDE 0.256 Sharpe ≈ 0.169 DSR (was 0.177) — fixed at the
single source constant (`power_analysis.VALIDATION_TRACK_LENGTH`) that `analyze_campaign.h2_tost_dsr`
also reads; CAMPAIGN_power.md regenerated; CH4/CH7 numbers updated. M2 SESOI economic rationale
reconciled. M3 EVT-regime notes re-scoped to the executed ≈2,961-session fed window. M4 delisting band:
docstrings corrected to ADR-051 (truth AT the zero end), the band now CLAMPS its window to the
univ4-era span and RECORDS the clamp (2026H1 outside the band audit — disclosed). M5 CH7 B.5.5
direct-tail p = primary (R64). M6 CH7 limitations updated (univ5 headline; univ5s finding = the answer,
MEASURED; §10 numeraire). M7 §10 R17 cohort spec re-scoped to Split C. M8 PROPOSED/RATIFIED
contradictions + dead pointers fixed. M9 buffer passes 20→~17. L1-L5 (phantom §18 refs, hash-bound
data.yaml comment, F3 manifest row, PopArt triage guidance, §12 compute prose). Verified: freeze gate
13/13 · citations 0/0/0 · ruff · delisting-band tests 9/9.

### The ladder verdict + B* = 200,000 (R74 — amends R70's unsatisfiable criterion)
Run 3 (uniform Turbo+lock conditions): eval-IQM **flat within seed noise across 25k→350k** (14×) —
REPRODUCING the pre-Split-C ladder; the knee detector's tolerance scales with the curve's own range ⇒
on a flat-noise curve it can NEVER return CONVERGED (verified branch analysis; extension cannot
terminate — R70's "extend until converged" is structurally unsatisfiable here). Evidence dossier:
critic terminal loss completes its steep descent by 100k (0.59→0.10; →0.01 at 350k = internal polish);
350k nominally WORSE than 200k on eval (the old-window pilot's mild-overfit direction); ≈17 buffer
passes at 200k. **B\* = 200,000** (≥2× the critic knee, below the overfit onset), identical across arms.
Mirrored: campaign.yaml + algos.yaml + preregistration.yaml + the R74 register row; `determine_design`
reports DECIDED (same honest semantics as candidates_per_arm) → **BLOCKED on ['n_seeds'] ONLY**.
**Paired Turbo speed table** (12 identical cells): 54.8→57.9 steps/s median (+5.6%) — far below the
audit's +20-28% estimate (owned honestly: the GPU slice of each step is tiny; Turbo's real value =
3-worker power headroom + thermal margin). Baseline preserved:
`learning_curve_baseline_preTurbo_2026-07-01.json`.

### Rehearsal gauntlet + σ_D launch
- **Keyless campaign dry-run: GO** (exit 0, end-to-end SEARCH→SELECT→FREEZE→TEST into campaign_dryrun,
  summary status `tested`) — first full-pipeline rehearsal post-univ5/Split-C. It exposed
  `auto_shutdown_on_complete: true` (4090-era; "host would power off now") → **DISARMED** (false).
- **preflight --probe: LIVE 1-token Opus 4.8 call SUCCEEDED** (key/credits/model verified today);
  disk/VRAM/tenacity/budget-mirror/data-checksum green; the 2 FAILs are the expected pre-freeze ones
  (frozen=false; RAM marginal at probe time — free-at-launch closes it).
- **σ_D pilot LAUNCHED farmed**: `run_sigma_pilot_train.py --budget 200000 --n-seeds 15 --gpu 3`
  (PID recorded; 30 cells; GPU util jumped 13→58%; watcher armed; ~9h ETA). Full test suite running in
  the same window. On σ_D: power_analysis with measured σ_D → seeds 30-vs-50 → determine_design
  FREEZE-READY → bundle regen → the freeze button (USER).
- Date-error sweep: my "+1 day" 2026-07-03 stamps corrected to 2026-07-02 across 14 files (today IS
  July 2; the CHANGELOG headers for the earlier waves renamed [2026-07-02f]/[2026-07-02g] to avoid
  duplicate keys).

User directive: "make sure everything is very precise" + full resource permission. Executed as a precision
audit of every load-bearing piece the automated ladder→σ_D→freeze chain depends on, using the serial
ladder's idle CPU (box measured 97% CPU-idle / 85% GPU-idle under the 1-worker ladder).

### The freeze chain, verified against the code (not memory)
- σ_D farm launch flags verified verbatim (`--budget <B*> --n-seeds 15 --gpu 3`; `--end 2026-06-30`
  Split-C default; `--out-dir outputs/sigma_pilot`). Amendment targets pinned: `campaign.yaml:12`
  `train_steps_per_candidate` + the algos.yaml mirror (budget-mirror preflight guard); seeds list
  `campaign.yaml:8` (30 → 50 if σ_D > 0.10). Buffer stays 50k at ANY B* (deliberate decouple, verified).
- Ladder health: launcher+worker alive, locked clocks; the `.venv\Scripts\python.exe` → base-interpreter
  child pattern EXPLAINED (Windows venv launcher stub — benign, standard; the child IS the venv run).

### `scripts/determine_design.py` — FOUR latent defects fixed (+DECIDED status; 11/11 tests, ruff clean)
1. **Unconverged-B* laundering**: `_gather_evidence` read `recommended_budget` without checking
   `converged` — a NOT-converged ladder (which reports its CEILING as the extend-sentinel) stamped
   `train_steps` DETERMINED. Now only a `converged=True` knee is evidence → the regenerated report
   honestly shows PENDING until tonight's ladder verdicts.
2. **`n_seeds` unsatisfiable via CLI**: the documented `sigma_seed_pilot` evidence key was never
   gathered. Now read from `outputs/sigma_pilot/sigma_seed_pilot.json` (the analyzer's artifact).
3. **`candidates_per_arm` unsatisfiable pre-campaign**: DETERMINED required `saturated=True`, evidence
   never computed, and the honest verdict is False (below) → freeze-readiness could NEVER be reached.
   The parameter's actual criterion is the RATIFIED 2026-07-01 cap (30; multiplicity control; "more
   candidates" explicitly rejected) with the CH7 search-width disclosure — new `Status.DECIDED` reports
   exactly that; saturation stays a disclosed diagnostic (a missing ratified anchor still BLOCKS).
4. **`cash_daily_rate` FIX_NEEDED was pre-ratification semantics**: cash=0 is the §10-RATIFIED numeraire
   (2026-07-01) — now DECIDED when the env value MATCHES `preregistration.numeraire.idle_cash_daily_rate`
   (a mismatch still fails loud). Registry text updated from the stale "risk-free series (R20)".
- `docs/DESIGN_DETERMINATION.md` regenerated end-to-end: **BLOCKED on exactly
  ['train_steps_per_candidate', 'n_seeds']** — the two pilots in flight — with an Evidence-notes section.

### The saturation engine's FIRST run on real data (prototype archive, 239 records, 8 generations)
`recommend_candidates` verdict: **NOT saturated at strict tolerance** — distributional saturated gen 3
(20 cands), placebo gen 4 (25), scalar_cvar5 gen 0; but **`scalar` jumped 0.025 → 0.11 at generation 7**
(candidates 36-40). DIRECTIONAL evidence (Sonnet author, pre-Split-C window, single-seed fitness = the
max-order-statistic drifts under luck): does NOT reopen the ratified 30-cap (multiplicity decision
stands); it gives the CH7 search-width limitation MEASURED texture ("a late candidate can move an arm's
best — our K is a disclosed budget, not a proven optimum") — write-time material, banked here.

### Vault-writer POSIX relpath fix (subagent; independently verified by me)
`data_pipeline/src/data/vault.py:129` `relative_to(ROOT).as_posix()` — the SINGLE origin of relpaths in
all three ledgers (manifest/checksums/lineage verified). Historical backslash lines untouched (SHA-256 of
all three ledgers identical before/after); name-fallback resolution preserved + regression-tested.
`data_pipeline/tests/test_vault_relpath.py` NEW (2 tests); pipeline suite 21→23, my own re-run: 23/23.

### Also this pass
- French June probe: upstream daily FF3 still ends 2026-05-29 → the P4 re-refresh stays pending (verified,
  not assumed). C: gate re-verified 20.9 GB ≥ 20. `.vscode/settings.json` minimal-footprint config
  (watcher/search excludes incl. the data junction, Pylance indexing off, tab limit) — VS Code stays open
  during the campaign per user decision, TRIMMED + agent-monitored (runbook §0b row updated; Defender row
  updated: service confirmed DISABLED at OS level → exclusion moot, command recorded for if re-enabled).

## [2026-07-02f] — Two reboots, Turbo UNLOCKED (user installed Armoury Crate), B* ladder relaunched clean

- **Reboot #1 (user, accidental) + Armoury Crate installed + Turbo set.** Enforced GPU limit
  74.87→**140.00 W**; burn-probe signature flipped from power-limited (draw pinned 94.7 W, clocks
  bouncing) to **clock-limited** (clocks pinned flat 2550 MHz, draw floating ~100 W, ≤58 °C) — the box
  now delivers everything the silicon gives at locked clocks. The app installs its own "Turbo" power
  scheme (replaced High Performance) — AC-sleep=Never re-set + verified on it.
- **Interpreter catch at relaunch:** the dead ladder's nominal interpreter (system Python311) has NO
  torch — it had been riding an inherited env; relaunched under `.venv` (torch 2.6.0+cu124, CUDA
  verified TRUE). Ladder writes only at completion → interrupted runs lost nothing but wall-clock;
  the clean rerun is BETTER (uniform Turbo+lock conditions vs the mixed Balanced/HP/locked original).
- **Reboot #2 (user, accidental) + MUX → Ultimate** ("GPU maximum"): dGPU now drives the display —
  ~neutral for headless training (costs ~300-500 MB VRAM + a sliver of compositing; our 3-worker
  footprint ~1 GB of 6 GB → harmless); not worth a third reboot to revert. **Turbo AUTO-persisted at
  boot** (the app re-applies it) → runbook m15 row downgraded to verify-only. No pending-update reboot
  flags (CBS/WU clean) — the restarts were one-offs, not an update loop.
- Clock lock re-applied after each reboot (it always resets); apps re-closed per the standing grant
  (re-affirmed twice tonight, now including delete authority); RAM 10.4 GB free. ⚠ C: down to
  **19.2 GB** (Armoury ~1.3 GB) — below the 20 GB campaign preflight gate → pre-campaign cleanup item.
- **B* ladder RUN 3 launched** (PID 12252, AboveNormal, `-u` → `outputs/logs/learning_curve_2026-07-02_r3.log`)
  under the final uniform conditions: Turbo 140 W + lgc 2200-2560 + MUX-Ultimate + sleep-Never;
  exit-watcher armed. On exit: fresh-timestamp check → recommend_budget → farmed σ_D `--gpu 3`.
- **Pre-Turbo baseline PRESERVED**: `outputs/tables/learning_curve_baseline_preTurbo_2026-07-01.json`
  (run 3 overwrites the live json) — median **54.8 steps/s** over 12 cells / 10.7 h; the paired per-cell
  before/after table generates from it when run 3 lands (compute-reporting evidence for the paper).
- **FINAL exhaustive speed sweep (user-requested "everything the laptop can offer") — verdict: at the
  ceiling.** Verified already-optimal: HAGS ON (HwSchMode=2), thermals 58 °C max (no cooling headroom to
  buy), thread pinning in the farm, VRAM 1.3/6 GB. Examined + REJECTED with reasons: patching SB3's 4
  forced `.item()` syncs (reproducibility hazard on the core loop; farming already overlaps the dead
  time across workers), driver update 556.12→current (~0 CUDA gain, churn risk — driver FROZEN through
  the campaign), CPU-mitigations/VBS-off (security posture), undervolt (locked SKU + thermals not
  binding), manual P-core affinity (Thread Director + AboveNormal already optimal), pagefile-fitting a
  4th worker (a swapping farm is slower than serial). PENDING on user: Defender exclusion for the repo
  (verified NOT set — needs admin `Add-MpPreference`). NEW run-day row: campaign runs HEADLESS (close
  VS Code → +2-2.5 GB wave headroom).

## [2026-07-02e] — σ_D farming + the two notebooks LANDED (verified first-hand); split-boundary precision fixes; F3/F4 re-rendered on Split C

- **σ_D pilot farm mode** (`scripts/run_sigma_pilot_train.py --gpu N`, default 1 = serial verbatim):
  per-(reward,seed) cells through the proven `run_recycling`/`DevicePool`; worker delegates to the SAME
  `train_one` (seed-first by construction), writes the SAME records in-worker (incremental, resume-safe);
  RAM preflight gate (2.5 GB/worker budget; ~2.11 GB measured); single-device pools only; submission-order
  re-attribution with a hard one-result-per-spec check. **Verified by me:** 12/12 tests (incl. serial-vs-farmed
  byte-identity under REVERSED execution order + shuffle-invariant summary + resume zero-spec) + test_leg 6/6 +
  ruff clean + the load-bearing hunks read. ~53 h serial → **~12–13 h at `--gpu 3`** (needs ≥7.5 GB RAM free).
  Bonus fix: `--help` crashed on cp1251 consoles (UTF-8 reconfigure now precedes `parse_args`).
- **Notebooks (examiner-facing):** deterministic builders (`scripts/notebook_builder.py` + 2 build scripts;
  fixed cell ids, no timestamps, clean-by-construction) → `notebooks/results_walkthrough.ipynb` (35 cells;
  Split-C/univ5 asserts, live F3 EDA recompute, taxonomy from the real prototype JSON, equivalence-first H2,
  mechanism SQ1-SQ3) + **NEW `notebooks/data_provenance_walkthrough.ipynb`** (20 cells: live sha256 vs manifest,
  `verify_gold` 0-changed-cells re-run, EVHC splice exhibit, 333 `vendor_terminal_kept` + univ5s≡univ5
  byte-identity, `expected_windows` live assert). **Verified by me:** builders re-run → byte-identical sha256s
  (`d63fa280a12a`/`1fcfd88f04f3`); provenance notebook re-executed via nbconvert on THIS machine →
  **"ALL INTEGRITY CHECKS PASSED (n=39)"**; ruff clean. Agent-flagged inconsistencies triaged: manifest
  Windows-relpath drift (loader basename fallback covers; vault-writer cleanup queued), CI `ruff format`
  drift (CI deferred anyway), prototype arm has 39-not-40 candidates on disk (n=239 used).
- **Split-boundary precision (fix-on-sight, examiner-grade):** the paper claimed the sealed test includes
  "the COVID drawdown" — FALSE under the 60-session purge: the crash (2020-02-19→03-23) falls INSIDE the
  boundary gap; the executed window opens 2020-03-30 (near the trough). CH4 §4.2 now states this plainly
  and defends it (leakage guarantee; no single-3-week-episode-dominated CVaR estimand; boundary shared by
  all arms ⇒ cannot confound the contrast); theory §3.6 rephrased. F4 timeline gained the two regime
  markers the manifest promised (COVID marker AT the executed start, labelled "crash in purge"; 2022 bear)
  + a pre-existing val/test caption collision fixed; rendered+inspected, shipped `F4_splits_timeline.png`.
- **F3 re-rendered from univ5 Split-C train window** (the on-disk PNG was the OLD 2005–2014 window): now
  kurtosis **15.25** (was 14.52), −5σ ×10,393, CVaR crossover ×0.84→×1.66, co-crash 3.3%→**19.7%**,
  worst day 2008-09-29 (100%). `src/viz/eda.py` docstring window + FRONT_MATTER F3 row (dropped stale
  "Hill") + 00_FRAMING regeneration note all reconciled to the delivered figure.

## [2026-07-02d] — Strict laptop-capabilities audit (user-directed) + the science-neutral speed levers APPLIED

Question audited: "is training using the full capabilities of the laptop?" Verdict (read-only auditor with
live GPU/CPU sampling against the RUNNING B* ladder, my verification):

- **Serial pilots ≈ 25% of box capacity** — one worker holds ~55 steps/s while the proven 3-per-GPU
  machinery sustains ~186 aggregate; the binding constraint at n_gpu=3 is **RAM** (~2.11 GB/worker against
  a 15.6 GB box), not VRAM (~313 MiB/context) and not the GPU itself.
- **Per-step time budget is overhead-bound, not compute-bound**: ~58% of each SAC step is dead time —
  WDDM submit/sync round-trips (4 forced `.item()` syncs inside SB3 `sac.py` per gradient step) plus
  clock P-state hunting between kernel bursts. Big-batch GPU math is NOT the bottleneck; latency is.
- **The campaign config is already ~75–85% of the realistic maximum** (n_gpu=3 + Turbo 140W + capped
  buffer); the residual gap is a DELIBERATE RAM-safety trade (recycle_every, n_gpu=3-not-4), kept.
- **Levers APPLIED mid-ladder (wall-clock-only, zero science keys touched):**
  1. Windows power plan Balanced → **High Performance** (`powercfg /setactive 8c5e7fda…`) — the ladder had
    been training at 10.9 W / 675 MHz / 32% util on the balanced plan.
  2. **GPU core clocks LOCKED** `nvidia-smi -lgc 2200,2560` — kills P-state hunting between kernel bursts;
    confirmed holding at **2205 MHz** on the live ladder (was 570–1080 MHz). Revert: `nvidia-smi -rgc`
    (+ powercfg back to Balanced) after the runs.
  3. **σ_D pilot farming being wired** (`scripts/run_sigma_pilot_train.py --gpu N`): per-(reward,seed)
    cells through the PROVEN `run_recycling`/`DevicePool` machinery (`src/orchestration/parallel.py`) —
    each cell `set_global_seed`-ed in its own process, identical records, order-independent aggregation ⇒
    **science-neutral by construction**; ~53 h serial → **~12–13 h at 3 workers**. Precondition: ≥7.5 GB
    RAM free (close apps).
- **FORBIDDEN levers reaffirmed** (FIX-class, never speed-tuned): batch_size 256, net arch, buffer cap
  50k, learning_starts, train_freq/gradient_steps, n_envs=1. **DEAD levers verified with reasons**:
  `torch.compile` (no native Triton on Windows), SBX/JAX (ADR-040), AMP, CUDA graphs, cudnn.benchmark.
- **⚠ Auditor error caught + NOT adopted:** its §5 claimed campaign SEARCH-leg parallelism is "no longer
  amendment-locked", citing R24. Wrong — the **2026-07-01 ratified amendment SUPERSEDES R24** with
  `headline_reflect_protocol: serial_reflect_on_last`; the campaign search leg stays **SERIAL** (the
  reflection chain is sequential by design). Its TEST-leg and pilot numbers stand.
- **Resource management executed under the user's standing grant** (2026-07-02, full permission to
  free/manage laptop resources for training; recorded in agent memory):
  - **Sleep time-bomb defused:** the High-Performance plan switch had brought **AC sleep = 600 s** with it
    — the overnight ladder would have frozen 10 min after the user stepped away. `powercfg /change
    standby-timeout-ac 0` applied + verified (`0x00000000`); battery sleep kept (4 min) as a
    power-loss safety net. Hibernate-after already 0.
  - **RAM freed 2.3 → 3.4 GB** (Steam + 7 webhelpers ~0.84 GB, background Edge, Phone Link, OneDrive —
    graceful `/shutdown`, after verifying the Desktop shell-folder is plain `C:\Users\User\Desktop`, i.e.
    OneDrive does NOT sync the repo → no file-lock hazard, closure is comfort not necessity). At σ_D
    launch the ladder's ~4.7 GB releases ⇒ ~8.1 GB free ≥ the 7.5 GB 3-worker bar; re-swept at launch
    (free-at-launch pattern). VS Code / claude processes / Armoury Crate (owns the Turbo profile) never touched.
  - Ladder worker (PID 20984) → **AboveNormal** priority (insulates the CPU-bound submit path).
  - **Enforced GPU power limit measured 74.87 W** (default 80, max 140): the box is NOT in Turbo mode.
    Not binding for the 1-worker ladder (21 W draw) but WILL matter for 3-worker phases → Turbo via
    Armoury Crate (Fn+F5) is a USER keypress; already a §0b run-day row.
  - **[2026-07-02 follow-up] Turbo is UNREACHABLE on this install** — empirically established: two
    10-s CUDA-burn probes show a flat ~94.7 W power-limit plateau (clocks bouncing under it = the
    Performance-mode cap) unchanged across Fn+F5 presses; the ASUS WMI interface answers INIT/fan/
    battery/MUX but returns not-supported for EVERY mode-control device ID (0x00120075, 0x00110018, …)
    — mode switching needs the Armoury Crate app (or G-Helper), which is NOT installed. §0b row updated
    with the install-before-run-day prerequisite. Performance mode (~95 W GPU cap) costs the overhead-
    bound pilots ≈ nothing (probe: matmul saturates at max clocks within the cap; SAC draws ~21 W);
    Turbo's real campaign value = higher sustained CPU PL + fan curve.
  - determine_design freshness check closed: the running ladder writes `outputs/tables/learning_curve.json`
    (absolute `--out-dir`) = exactly the path `determine_design._gather_evidence` reads; current evidence
    (`recommended_budget: 350000`) is YESTERDAY'S noisy pre-Split-C run — superseded on ladder exit.

## [2026-07-02c] — P1 EXECUTED: the univ5 rebuild + SPLIT C (ADR-051 + addendum; prereg R73). Gate ② given by the user ("execute everything up to the campaign")

State: pre-freeze; freeze gate ALL-OK on the new configuration (hash `d9204087…`, moved intentionally: 3 bound
configs + prereg changed). **The referee: `verify_gold` univ5-vs-univ3 = 0 changed cells (max |Δ| 0.000e+00)
over the full 5,283×953 overlap; +123 sessions (2026-H1), +10 new-member columns.**

### The extension pull (PowerShell + `.venv-lseg`; dedicated `x26` journal — chunk-ids are param-hashed, so a
### config-span re-run would have re-pulled 21 years; ADR-051 chose the dedicated-driver route)
- `data_pipeline/scripts/extend_universe_2026.py`: A1' chain+events → fresh reverse replay → **overlap gate**
  → SPLICE (frozen pit authoritative through 2025-12; fresh contributes ONLY 2026) → A2' returns / A3' caps /
  A4' meta / A5' px-bid-ask-vol / SPXTR. **138/138 chunks frozen, 0 failed** (ReadTimeouts absorbed by backoff).
- **The overlap gate FIRED on first live contact** (working as designed): Refinitiv backfilled EVHC.N^L16's
  Dec-2016 leaver event in the 3 weeks since the frozen pull; the missing join made replay claim membership
  since 2004 — provably impossible (IPO 2013; SEC 25-NSE delisting 2016-12-13) and provably immaterial (~$7B,
  never top-30). Allowlisted + disclosed (ADR-051 addendum); union 953→963 (incl. the real FDX-Freight/
  Honeywell-Aerospace 2026 spinoffs).
- `refresh_fred_2026.py`: VIX/rf/term series re-pulled keyless to the cutoff (last VIX print 2026-06-30) as
  `fred_macro_x26`; `build_universe` now consumes the LATEST `fred_macro*`.
- Vault-root junction `data_pipeline/data → data` (the ADR-022 merge split ROOT from the real vault).

### The builds + the delisting finding
- First build was POISONED by a config split (`data_pipeline/config/data.yaml: window` — not the engine
  config — clips the calendar): 5,283 sessions, no 2026. **Surgically purged** with the new guarded
  `purge_suffix.py` (36 files + 53 ledger lines, all never-consumed; refuses protected/active suffixes);
  window bumped; rebuilt correct: **univ5 = 5,406 × 963, 2005-01-03 → 2026-06-30**.
- **`univ5s` (Shumway + OBSERVED-terminal recovery): `vendor_terminal_kept: 333`, ZERO surcharges** — every
  dead name's realised terminal was already in the vendor series, so univ4's flat −30/−55% surcharge was
  DOUBLE-COUNTING on top of its M&A contamination. The corrected band-end equals the zero-fill headline;
  recovery implemented as the pure, hermetic `_recover_terminal_from_returns` (+5 tests).

### SPLIT C executed everywhere (ADR-044 → R73 in the prereg register)
- Configs: engine data.yaml (splits + `gold.suffix: univ5` + period 2026-06-30), inference.yaml (splits +
  `expected_windows.univ5 = [60,3021]/[3081,3775]/[3835,5406]`), preregistration.yaml (`data_splits` +
  banner), pipeline data.yaml (window). PREREGISTRATION.md §7 rewritten + the formal **R73** amendment row.
- Code+tests sweep (agent, my verification): 23 files — loaders (`_DEV_END` 2016-12-31, `_DEFAULT_SUFFIX`
  univ5, module facts), run_campaign/run_prototype/parallel defaults+docs, test_leg/runner/results/strategies
  spans, learning-curve/σ-pilot/popart/variance-decomp dates, F4 schematic renders Split C, prototype.yaml
  (TRACED campaign-live) + provenance note. Univ3/univ4 band semantics and historical framings preserved.
- **CRITICAL catch by the sweep**: 2016-12-31 is a SATURDAY — the old `searchsorted(left)+1` convention
  (correct on session-valued boundaries like 2014-12-31) leaked 2017-01-03 into the SEARCH train window and
  shifted the executed val start off the ratified date. Fixed with `side="right"` at 3 sites (loaders
  `embargoed_val_start`, run_prototype, parallel) — byte-identical on the univ3 era, byte-matching
  `expected_windows.univ5` now; regression tests pin `abut` + the ratified 2017-03-30.
- **Latent test bug exposed+fixed**: `_config_gold_suffix`'s def-time default ignored the
  `loaders._DATA_YAML` monkeypatch — the config-primacy test passed only by coincidence; now resolved at
  call time. Suffix-flip fallout in 5 test files fixed (suffix-aware fixtures / univ5 expectations).
- Paper prose: FRONT_MATTER/00_FRAMING abstracts, CH4 §4.2 (panel facts + splits + regime set), CH5
  (date-free process claim), theory §regime, CH7 B.4.1, F3/F4 manifest rows (F3 row now describes the
  DELIVERED figure — closes the "Hill" reconciliation flag).

### Verification (observed)
- verify_gold: **PASS (0 changed cells)** · spot-checks: span 2026-06-30 ✓, top-30 books sane ✓,
  shumway audit 333/333 kept ✓ · loader opens univ5 under checksum verification ✓ · freeze gate ALL-OK ✓ ·
  Split-C sweep suite 203/203 + flag-closures 113/113 + pipeline 21/21 ✓ · PDF 292 KB 0-warnings ✓ ·
  word budget 15,716 tracked (P7) · **FULL engine suite: GREEN (exit 0)** after the last 5 suffix-fallout
  test fixes (market_reference ×2 [suffix-aware `_MKT` + tmp fixtures], capture_env, membership_shumway,
  plus the earlier data_deep/loaders_checksum/platform_coverage batch).
- Known-cosmetic: `splits_univ5.parquet` carries the stale pre-Split-C dev-boundary cell — provably inert
  (pinned by a dedicated test), documented in loaders + config comments; refresh at a future rematerialization.

### Post-P1 closure batch (same session)
- **Docs Split-C sweep landed (12 live docs)**: DATASHEET gained the dated "2026-07-02 extension + rebuild"
  section (byte-diff · EVHC/SPLICE · zero-surcharge finding · the 10 new members incl. VEEV.N/VRT.N);
  MODEL_CARD/REPRO_CHECKLIST/RIGOUR_LEDGER (new A-ter threat→guard rows) / CAMPAIGN_* updated;
  DESIGN_DETERMINATION regenerated (blockers now exactly ['n_seeds','candidates_per_arm'] — note:
  train_steps shows DETERMINED off the PRE-Split-C learning-curve json; the running ladder supersedes it).
- **Runbook reconciled** (10 sites): headline univ5/R73, the univ4 double-counting note, univ5s-supersedes-
  univ4r, ~150 authorings (was 180), R21–R73, smoke label; `smoke_test.py` + `determine_design.py` labels
  made suffix-aware/963.
- **Reference-series coverage (docs-sweep catch)**: French factor CSVs ended 2026-04-30 vs the 2026-06-30
  test end → `refresh_french_2026.py` (direct zip parse — pandas_datareader's famafrench parser breaks on
  modern pandas) froze `french_ff3_daily_x26` + `french_mom_daily_x26` to **2026-05-29** (upstream's own
  lag; the June tail publishes later — re-run pre-analyze). `market_reference` readers now PREFER the
  versioned refreshes (`_raw_path` + `_REFRESHED_RAW`, +2 tests) — also fixes the risk-free series
  (fred_macro ended 2025-12; the x26 refresh reaches the cutoff). market_reference 11/11; all 5 rebuild
  scripts ruff-clean.
- **P2 STARTED**: the B* convergence ladder is RUNNING detached (budgets 25k–350k × seeds 0-2, CUDA,
  Split-C univ5 train window; exit-watcher armed). σ_D pilot queues after it.

## [2026-07-02b] — Deliverable pipeline + run-day ops hardening + two new instruments (ADR-050)

State: pre-freeze (`frozen: false`, hash `843b84c3…` stable). **Consolidated verification (all observed):**
271/271 tests in one combined run across every touched suite (+398 executions inside the ops wave, +245
taxonomy-affected, +37 viz) · ruff clean repo-wide (`src tests scripts`) · `freeze.py --check` 12/12 OK ·
`build_paper.py` → dissertation.pdf **292 KB, 0 pandoc warnings** · `word_budget.py` = 15,698 (tracked; P7 owns).

### The deliverable pipeline (NEW-LENS A: the md→PDF toolchain did not exist)
- `tools/` pinned portable **pandoc 3.10 + Tectonic 0.16.9** (no system install; MSI needs elevation and is
  unpinned — portable is deliberate); TeX cache on D: (`TECTONIC_CACHE_DIR` — C: hit 0 bytes on first compile).
- `scripts/build_paper.py` (+9 tests): UCL-order assembly, fence-aware `[`key`]`→`[@key]` transform (year-key
  discriminator; catches multi-line + locator/prefix forms — the first compile missed 18), Harvard
  cite-them-right CSL, References section, fail-loud diagnostics. **118 citation groups resolve, 0 warnings.**
- `scripts/word_budget.py` (+8 tests): main-body count per the UCL exclusion rules — **15,532 words at first
  measure vs the 10,000 hard limit** (was hand-estimated ~11.5k); the P7 depth-pass has per-chapter targets.
- `scripts/make_prereg_bundle.py` (+test): the OSF-deposit zip of the exact hash-bound file set (dry-run
  emitted `prereg_bundle_843b84c3.zip` with the PRE-FREEZE banner).
- Front matter: **Glossary of Terms** (23 entries, non-specialist second marker); Makefile targets
  `paper`/`wordcount`/`prereg-bundle`; `.gitignore` +tools/ +paper/_build/.

### Run-day ops hardening (NEW-LENS B: 3 run-killers found, all closed)
- **C1**: `tenacity` was NOT installed → every API call single-attempt (SDK retries deliberately 0) →
  **installed 9.1.4 + `_make_retrying(3)` verified + preflight `check_retry_layer` hard-FAIL probe**.
- **C2**: Windows Update unpaused + no reboot re-entry → preflight `check_windows_update` (RebootRequired/
  RebootPending registry FAIL; unpaused WARN) + `install_onstart_task.ps1`/`uninstall_onstart_task.ps1`
  (Task-Scheduler ONSTART supervisor re-entry).
- **C3**: exit-0 husk runs → `campaign_exit_status`/`incomplete_arms` (EXIT_INCOMPLETE=3; fail-loud on unknown
  statuses; operator-interrupt keeps exit 0) + the **winner-selection floor** `select_floor_ok`
  (resolved-slots = accepted+ledgered-failures == budget; a partial pool can never freeze a winner) +
  `llm_error_skips` counted + anomaly-emitted. **BONUS: the new gate immediately exposed a pre-existing
  exit-0 husk** — the keyless dry-run's TEST leg had been silently failing (600-day synthetic panel can't
  span the frozen splits) → root-caused, synthetic driver panel → 7800 sessions; dry-run genuinely green.
- **M4** serial fallback + H3 search now thread `--resume` (no re-billing/archive overwrite) · **M5** watcher
  `--follow-campaign` (no exit on per-arm done), dedupe reset on healthy, alert-add only after successful
  POST, `deadman_ping.ps1` (the only alert surviving host death), runbook progress-path corrected ·
  **M6** thermal governor LIVE on every path (`campaign.yaml agent.thermal_guardian {hi:88, lo:80}` +
  threaded through the parallel spec) · **M7** supervisor attempt-reset after >30-min healthy runtime +
  `--resume` on EVERY launch · **M9** preflight `load_env()` + REAL 1-token `--probe`
  (ok/auth/client-4xx/transient classified; never fires in tests) · minors m10 (config `resume: true` wired
  as CLI default) m11 (mtime-tolerant staleness) m12 (Manager shutdown) + **runbook §0b RUN-DAY checklist**
  (pause updates 5wks · Turbo ~140 W after every reboot · lid Do-Nothing · Defender · ≥20 GB C: ·
  `--min-disk-gb 20` · ONSTART + deadman). ~35 new/updated tests.

### Two new instruments (report-only, DISJOINT from m=6)
- **Reward-program taxonomy** (`src/inference/reward_taxonomy.py`, 14 tests; wired `out["reward_taxonomy"]`
  + renderer + `scripts/build_taxonomy.py`): AST shape-set Jaccard → connected components → labelled KINDS +
  per-arm composition/entropy/overlap + threshold sensitivity; construct vocabulary consolidated from
  `inspect_rewards` (single source). **Validated on the real 239-program prototype archive**: search arms
  collapse to ONE re-parameterised template-kind each (within-sim 1.000 — instrument discriminative
  validity), LLM arms near-fully idiosyncratic (152/157 singletons, entropy ≈ max), the few multi-member
  kinds SPAN arms — null-consistent. CH7's "left to future work" updated to delivered-and-validated.
- **F3 stylised-facts EDA figure** (`src/viz/eda.py`, 12 tests; wired into `make_figures`; PNG+PDF rendered
  from the REAL train window): excess kurtosis **14.52**; −3σ ×7.1 / −5σ **×~10⁴** vs Normal; the **CVaR
  crossover** (×0.8 at α=.25 → ×1.7 at α=.01 — a shallow tail summary looks benign while the deep tail is
  catastrophic); 9 stress episodes; co-crash 3.3%→**20.4%** (2008-09-29 = 100%). Empirical CVaR REUSED from
  `bootstrap.cvar` (figure↔inference cannot drift). ⚠ Write-time flags: skew is **positive** (+0.22 — never
  claim negative); manifest's "Hill" wording to reconcile; reconcile the old "kurtosis 49.9" note
  (different aggregate).

### Paper + citations + plan
- **CH1 chapter lede** (the question in one breath — mechanism-led, could-vs-does, either-answer-is-evidence).
- `bauer2025equal` verified first-hand (arXiv 2505.23333 abs fetched) + promoted + cited at both CH4
  power-caveat sites; `sun2024card` upgraded to the first-hand-confirmed published venue (Knowledge-Based
  Systems 326:114065, 2025) and the stale "Sun, Hao discrepancy" note replaced with the resolution.
- **docs/ULTRAPLAN_2026-07-02.md**: P0–P8 with gates/owners/exit criteria, timeline vs 1 Sep (+1.5-2 wk
  slack), risk register, the standing documentation protocol, Tamer's gate list (gate ① disk CLOSED —
  20.5 GB verified; next gate ② rebuild GO + settled-2026 cutoff). P7 reframed: the word surgery IS the
  depth pass; EDA/Data argument + CH1 elevated; figure-standards + integration rehearsal added to P6.
- Disk: C: 0.00 GB → 6 GB (cache purges) → **20.5 GB (user cleanup, verified)**.

## [2026-07-02] — Deep 8-front audit + fix-everything hardening (ADR-049); repro-integrity C1–H4; inference P1–P7; CH4/CH7 prose

State: pre-freeze (`frozen: false`). **Verified:** ruff clean on all touched files; targeted suites green
(inference fixers 280+; repro-integrity full suite exit 0; this session's 10-file batch **223/223**);
`freeze.py --check` **12/12 OK** — canonical SHA-256 now `843b84c3…` (changed intentionally twice: the C1/M1
panel-identity + expected-windows binding, then the §18 h1_baselines mirror). Full findings register: ADR-049.

### Deep audit (8 read-only auditors, literature-validated; + 4 fixer subagents independently verified)
- **Verdict: NO CRITICAL/HIGH code defect.** FZ0 / DSR / PSR / expected-max-Sharpe / HLN / stationary bootstrap /
  PBO / MCS / IUT-BH multiplicity / differential-Sharpe / allocator QPs / the six-scalar tail estimator (GPD-POT
  closed forms) all match the primary literature; sandbox allowlist repels the escape battery; pipeline leakage-free.
- The one CRITICAL was in the **bibliography**: `harvey1997testing` named a nonexistent "Harvey & Liu 1997" →
  replaced with the real **Harvey–Leybourne–Newbold 1997** (IJF 13(2):281–291). `witzany2021bayesian` metadata
  corrected (Risks 9(1):18). gridach/orra venue labels corrected to arXiv preprints (no ICLR acceptance found).

### Statistical-code fixes (each with tests)
- `mediation.py` P1 stability guard (prop_mediated NaN + flag when c_total ≈ 0; determinism preserved) ·
  `power_analysis`/`analyze_campaign` P2 paired TOST reconcile · P3 wired `comparative_es_backtest` /
  `bayesian_null_report` / `model_confidence_set` as report-only DISJOINT blocks · P6 CVaR fractional margin ·
  `mechanism_multiplicity()` (BH + Bonferroni across mechanism legs) · P7 bootstrap pairing/reliability fixes.
- `bootstrap.null_calibration` now also certifies the **one-sided** size (the rule H2-Tail actually gates on, R64).
- `es_backtest`: two-sided **equal-accuracy** DM framing reconciled code↔CH4 (not Nolde–Ziegel's one-sided form);
  `var_es_estimates` unified so ES ≤ VaR by construction.
- `contamination.named_vs_blinded_structural`: unparseable (empty-AST) pairs no longer score jaccard=1.0 —
  excluded + `n_unparseable_pairs` (P7c mirror) + regression tests.
- `parallel.train_candidate`: `n_trials` fail-loud (the silent prototype-40 fallback removed).

### Design-coherence + guards
- **λ reclassified CALIBRATE→FIX** (`determine_design.py` + tests): λ=0 is the tail-blind-selector identification
  choice, not a pending calibration — no longer a freeze blocker; legacy `lambda_grid`/`lambda_frozen`/
  `calibration_fold` **deleted** from the hash-bound `inference.yaml` (executes the prereg §5 instruction).
- **New guard:** `freeze.py::assert_h1_baselines_match` — §18 family mirrored into `config/preregistration.yaml`
  (hash-bound) and asserted equal to `campaign.yaml` (roster-guard pattern); freeze gate now 12 checks.
- **New guard:** `preflight.py::check_budget_mirror` — campaign vs algos `train_steps_per_candidate` must agree
  (a B* amendment cannot half-land).
- Repro-integrity C1–C5/H1–H4/M1 (subagent, verified): `gold.suffix` config-primary + stamped into env/campaign
  provenance; checksum fail-loud + wired at all 3 production loads; preflight real hash compare; `env_fp` real
  label; conftest `preload()` (SIGSEGV order fix); `preload(strict=True)` in entry points; `--gpu >= 4` refusal +
  RUNBOOK reconcile; `campaign: laptop_rtx_4050`; `verify_gold.py` byte-diff validator implemented (univ4 vs univ3
  → the 333 delisting-surcharge cells detected).

### Paper / docs
- **CH4 §4.3**: replay-buffer-cap justification added (`zhang2017deeper` + `fedus2020revisiting` — first-hand
  verified, added to refs.bib; fixed-calendar ~20-pass coverage argument; replay-ratio-1; common-mode across arms).
- **CH7 §7.1**: explicit RQ scorecard (responsiveness / transmission / specificity verdict slots, wired to §6).
- CH4 §4.7 (prose fixer): ES backtest disclosed as two-sided DM equal-accuracy; CVaR-Tail margin justified on the
  CVaR scale + lowest-power flag; report-only/disjoint framing; CH7 mechanism-multiplicity disclosure;
  "taxonomy" → "reward-construct prevalence differential" (a true taxonomy explicitly future work).
- `docs/CAMPAIGN_preflight.md`: 6→7 arms, 180→210 winner re-runs, `--gpu 4`→`--gpu 3`, laptop-only compute.
- Stale buffer comments in `run_campaign.py` reconciled to the single invariant (final clamp verified at
  `trainer.py` L120: `buffer = min(requested, campaign_replay_cap())` on every leg).

### False positives cleared (recorded so they are never "re-fixed")
DSR raw-kurtosis (correct) · differential-Sharpe minus sign (canonical) · gneiting DOI (already correct) ·
`return_minus_cvar` estimator (≡ ceil(αn); documented) · placebo "inert" intro (truthful zero-information is the
right design; `placebo_shuffled` is the tell-free headline control) · reward-penalty ddof=0 (scale, not estimator;
documented) · CH4 softmax-corner + PopArt disclosures (already present) · `kvasiuk2026madevolve` +
`heavytailsDM2026` (both confirmed REAL). **Okhrati = "Dr"** (verified): front matter was right; CLAUDE.md corrected.

## [2026-07-01b] — Gap-closing build, Phase-A pre-freeze completion + ratification, mechanism reframe, Phase-B start

State: `memory/session-current-focus.md`. No frozen change (`frozen: false`); nothing committed. **Verified:** full
test suite **exit 0**, a fresh **adversarial 5-area audit CLEAN** (ITEM 3 / GAP A / GAP B / ratification / reframe),
**ruff clean** across `src`+`scripts`+`tests`.

### Mechanism kernel — report-only, DISJOINT from the frozen m=6 (the originality core; SQ1→SQ2→SQ3)
- `src/inference/responsiveness.py` (NEW) — SQ1 responsiveness (Spearman/slope + bootstrap CI) **and** the
  numeracy-bottleneck **legible-format differential** (ADR-039 headline reframe, made testable).
- `src/inference/mediation.py` (NEW) — SQ2 fed→code→outcome single-mediator decomposition (indirect a·b + bootstrap
  CI); the predicted null severs the chain at link 1.
- `src/inference/contamination.py::named_vs_blinded_structural` (NEW) — SQ3 AST-structural named-vs-blinded
  (identifier-invariant: a placebo can echo tail *tokens* yet write a different *program*); wired into `contamination_report`.
- `src/inference/regime_analysis.py` (NEW) — regime-stratified tail metrics (T3′) + honest independent-episode power bound.

### Figure/viz suite — grown 5 → 9 headline + 3 schematics + 3 static-3D + 2 GIF animations
- `src/viz/figures.py`: + controls-overlay (F7), responsiveness-scatter (F8b), learning-curves (F9), delisting-band.
- `src/viz/advanced.py` (NEW): classical-MDS reward-code 3-D embedding + CVaR×gen×Sharpe landscape + search-evolution
  and rotating-embedding **GIFs** (principled 3-D, not chartjunk; GIF dpi capped for the repo).
- `src/viz/schematics.py` (NEW): F1 system diagram, F2 prediction-branch, F4 splits-timeline.

### Notebook + reproducibility tooling
- `notebooks/results_walkthrough.ipynb` (NEW) — world-class walkthrough; runs on the synthetic-null demo, swaps to
  the sealed-leg loader post-campaign; **validated by real nbconvert kernel execution**; shipped clean (no outputs).
- `scripts/audit_reproducibility.py` (NEW) — one-command PASS/WARN/FAIL repro audit (live 7P/1W/0F). `.python-version` (3.11.9).

### Phase-A pre-freeze fixes (all independently re-verified)
- **ITEM 3 — parallel resume-cache:** the parallel search path lacked the serial resume cache → on the certain
  auto-restart it re-billed the LLM and could flip the winner. Mirrored into `parallel.py::_drive_llm_arm`
  (`load_run(cid, arm_root)`; reflection block rebuilt live; failures-ledger replay) + threaded `resume` end-to-end
  (`run_prototype.build_parallel_opts` → `run_campaign._search_parallel_arm` → `run_headline_campaign`). +10 tests.
- **GAP A — mechanism analyses wired into the report:** they were BUILT but ORPHANED (called only in tests). Wired
  into `analyze_campaign.analyze()` as DISJOINT `out[...]` blocks + renderers + `write_report`; responsiveness/
  mediation/regime fire from the archive; named-vs-blinded + legible-format honestly DEGRADE to `executed:False`. +7 tests (137 in the analyze family).
- **GAP B — the two missing sub-experiment runners:** `scripts/run_subexperiment.py` (NEW; NAMED reveal-identity
  pass + LEGIBLE basis-points/decile pass) + 3 **default-off** seams (`schema.py` `legible` kwarg; `loop.py`
  `extra_record_fields` + `legible_render`) + `config/subexperiment.yaml`. Both `analyze()` legs flip
  `no_data`→`ok` (end-to-end acceptance); default-off byte-identity verified (the treatment surface is git-SHA-
  pinned at freeze, not canonical-hash-bound). +8 tests.

### Pre-registration — 4 amendments RATIFIED (user-delegated) + `freeze.py --check` GREEN (canonical hash `0f5e99e5`)
- **§2a mechanism-headline reframe** — RQ + SQ1–3 + the 3-link causal chain (fed signal → authored code → policy →
  realized tail) + the numeracy-bottleneck hypothesis; **σ_D-robust** (the mechanism headline holds whether H2 lands
  equivalence or non-rejection); report-only, disjoint from m=6. Mirrored `preregistration.yaml: mechanism`.
- **§5 λ=0** (tail-blind selector) ratified. **§10 rf/cash numeraire** — rf=0 headline + DGS3MO rf-excess robustness
  + cash=0 (common-mode: rf cancels to first order in the arm contrast); mirrored `numeraire`. **§6 serial-headline**
  — REVERTED R24 to **serial reflect-on-last** (ADR-040 makes speed moot; buffer moot; reproducibility now EQUAL
  after the ITEM-3 parallel-cache fix; unattended-run reliability); parallel retained as a now-resume-safe robustness
  variant. Mirrored `search.headline_reflect_protocol: serial_reflect_on_last`.

### Paper — mechanism reframe propagated to the highest-leverage prose
- `00_FRAMING` abstract → **v2 mechanism-led** (opens with the mechanistic question + 3-link chain + SQ1–3; a null is
  a *located* finding) + **C4** (mechanism = the headline contribution; C1–C3 its machinery).
- `CH1` §1.2 → the mechanistic question + 3-link chain + sub-questions; §1.3 → **C4** (four contributions).
- `CH4` → **Table 4.1** (the consolidated threats→defenses table).

### Decisions
- **Serial-headline** (above; supersedes R24). **Alpha — NO scope expansion** (no alpha-generation / market-beating;
  the thesis stays the risk-sensitive comparative-null + mechanism); the "no hidden factor bet" characterization is
  already delivered by the pre-registered 6-factor attribution (CH4 §4.7 / R26).
- **Compute reconciliation:** LSEG licensed data is NOT a blocker (user) → laptop-only is a **cost** choice, not a
  licence one (corrected 4 docs + ADR-040). **WSL2 probed and REJECTED** (CUDA torch wheel failed to install 3×) →
  native Windows confirmed (torch 2.6.0+cu124).

### Phase B (pilots) — started
- Pilot infrastructure verified ready (`learning_curve.py` → B*, `sigma_seed_pilot.py` → σ_D, `pilot.py` decision
  logic). GPU confirmed (RTX 4050, CUDA). Convergence-harness **smoke GREEN**; the real ladders follow.

### Phase B/C execution (pilots → freeze)
> Chronological execution log: `docs/SESSION_LOG_2026-07-01_phaseBC.md` (appended at each milestone).
- **Verification gate GREEN:** full suite **exit 0**; fresh **adversarial 5-area audit CLEAN** (ITEM 3 / GAP A /
  GAP B / ratification / reframe); **ruff clean** (`src`+`scripts`+`tests`); **coverage 91.96%** (≥ 90% target,
  above the 88% floor).
- **Coverage raise (tests-only, no src touched):** responsiveness 86→95%, mediation 86→97%, es_backtest 83→99%,
  multiple_testing 88→100%, contamination 86→99%, ood_stress 77→85% (capped by a `statsmodels` "SVD did not
  converge" on this Windows/BLAS build in the Markov success-body — its graceful-degrade path IS tested +
  documented, not a defect). ~70 targeted error/edge/degrade-path tests added.
- **σ_D pilot harness BUILT** (no ready path existed): **NEW `scripts/run_sigma_pilot_train.py`** trains the two
  CRN baselines (`differential_sharpe`+`return_minus_cvar` × shared seeds) → per-seed **sealed-TEST** records via
  `test_leg.build_test_record`+`write_run` (the exact schema `sigma_seed_pilot.py` reads). Smoke generate→analyze
  GREEN; real command `run_sigma_pilot_train.py --budget <B*> --n-seeds 15 --device cuda`.
  **NEW `tests/test_run_sigma_pilot_train.py` green; ruff clean.**
- **Convergence-ladder fix:** `learning_curve.py` smoke green; unbuffered foreground real-gold+CUDA probe green.
  The first background (Tee-piped) launch **HUNG** on a block-buffering/pipe deadlock (python not training, GPU
  idle) — **diagnosed via `nvidia-smi`+process-CPU (not assumed)**, killed, **relaunched UNBUFFERED with a direct
  file redirect (no Tee)**. Ladder: `--budgets 50000,100000,200000,350000 --seeds 0,1,2 --device cuda`.
- **Resource cleanup (user-authorized):** killed all stale python (orphaned multiprocessing workers + leftover
  `D:/tmp` smoke scripts) → GPU →0 MiB, RAM →8 GB free, so the pilots own the machine.
- **Device settled:** head-to-head 10k-step timing **CUDA 173 s vs CPU 378 s** → CUDA (~2.2×; ~55 steps/s). The
  low "9% CPU" is normal GPU-sync-bound behaviour, not a stall.
- **Convergence-pilot OOM → 50k buffer cap wired (ADR-042):** the first capped-device ladder finished with
  **n_ok 3/3/1/0** across 50k/100k/200k/350k — root cause a **`MemoryError`** at SB3 replay allocation
  (`buffer_size == budget` → 2.8 GB at 200k / 5 GB at 350k on the 15.6 GB laptop; critic losses all FINITE, so RAM
  not instability). This is the **"buffer-cap wiring" pre-freeze fix** flagged open in CLAUDE.md. FIXED: a **50k
  HARD cap** (config-driven `campaign_replay_cap()`, `min(train_steps, 50k)`) at every construction site —
  `config/campaign.yaml` `agent.buffer_size`, `trainer.resolve_agent_kwargs`, `factory._policy_kwargs`,
  `run_prototype._agent_cfg` (also closing the **serial-SEARCH-25k vs TEST-50k buffer skew**), and both pilots.
  VERIFIED: all sites → 50000 at 200k / 25000 at 25k (prototype unchanged); **93 buffer tests green**, ruff clean,
  no test changed. The uncapped run's "recommend 200k / still rising" verdict is **SUPERSEDED**.
- **Ladder re-launched under the cap** (`bfb5oi4wo`, same budgets×seeds, unbuffered) — all budgets now survive;
  ~10 h → B\*.
- **Next:** B\* → σ_D at B\* → n_seeds → `pilot.py` verdict → set B\*/seeds → `freeze.py`.

## [2026-07-01c] — Convergence-pilot verdict, DATA PLAN (Split-C + forward-2026), report-only rigor upgrades, 2nd-LLM pick, multi-market plan, Refinitiv access solved

Decisions/findings recorded this session. `frozen: false`; nothing committed. **Every item tagged with EXECUTION STATUS**
so nothing un-executed reads as done. ADRs appended: **ADR-043 … ADR-048** (buffer-cap ADR-042 already recorded — referenced,
not duplicated).

### Convergence pilot → B* = 200,000 (ADR-043) — DECIDED, RE-RUN PENDING on Split-C
- Pilot findings (ran on the **OLD 2005–2014 train window**): held-out eval is **flat-noise ≈ 0** across 50k→350k (no gain
  from more training); critic loss **bottoms ~100k then rises mildly** to 350k (mild overfit). The harness verdict
  "**recommend 350k / NOT CONVERGED**" is a **plateau-detector ARTIFACT** (a flat-noise curve is not the monotone-approach
  shape its plateau rule expects). **B\* = 200,000** set by the loss-knee + the ADR-042 memory envelope.
- **MUST be RE-RUN on the new Split-C window** (below) before B\* is finally banked. **STATUS: DECIDED-pending-execution.**

### DATA PLAN (ADR-044) — DECIDED, pending rebuild
- **Split-C re-partition:** train **2005–2016** / val **2017–2019** / test **2020–2025** (2020–2026 if forward-extended) —
  more training (**12y vs 10y**) + a tail event in **both halves** (2008 GFC train, 2020 COVID + 2022 test).
- **Forward-extend to a SETTLED 2026 cutoff** — feasible + **FAST** (Refinitiv pull ~30 min–2 h, not the earlier "2 weeks"
  guess); H1-2026 was a bull market (no tail event → marginal science) but cheap.
- **REJECTED (research-grounded):** 2000 backward extension (dot-com is where survivorship-free reconstruction is hardest AND
  validation breaks — Ince–Porter 2006 "worst-earliest"; yfinance can't validate dead names; CRSP is the academic gold, not our
  Refinitiv entitlement); options data (scope creep + OptionMetrics/IvyDB quality); other-markets-as-features / synthetic /
  more-assets (creep + model risk); more-candidates (raises the Deflated-Sharpe multiplicity penalty, does not fix data size).
- **STATUS: DECIDED-pending-execution** (gold re-partition + forward pull not yet run).

### Report-only rigor upgrades (ADR-045) — DECIDED, pending implementation; all DISJOINT from the frozen m=6
- **Bid–ask SQUARE-ROOT market-impact cost model** — replaces the arbitrary flat 10 bps; spreads **already frozen (A5)** → NO
  new pull; sweep **γ ∈ {0.5, 0.75, 1.0}**.
- **BAB / QMJ factor-attribution completion** — free AQR / Ken-French factors (extends the 6-factor attribution).
- **Delisting correction via OBSERVED TERMINAL RETURNS** — the delisting-reason mnemonic is absent under this entitlement →
  terminal-return approach is cleaner; corrects the **univ4 M&A mis-booking** (why univ3 is the headline panel).
- **STATUS: DECIDED-pending-implementation.**

### Second LLM reward-author (ADR-046) — DECIDED (cost incurred only at campaign-time)
- **Qwen3-Coder** (strong open coding model, **~$1–3** via a cheap hosted API) → cross-vendor diversity (Anthropic vs Alibaba)
  + reproducibility via archive-replay (open weights).
- **REJECTED: GPT-5.5** on cost ($5/$30 per MTok → ~$20–40); **weak/mini models** on principle (uninformative null → the
  documented **"no weak models"** rule, ADR-039). Panel = **Opus 4.8 primary + Qwen3-Coder**.

### Multi-market external validity (ADR-047) — DECIDED, pending implementation
- **Lite FTSE-100 replication** of the FROZEN protocol on a 2nd survivorship-free panel (single-market = #1 reviewer weakness);
  **reuses the fixed agent** → respects identification (replicates, does not modify).
- **STANDING IDENTIFICATION RULE codified:** only the **reward-feedback block** varies across arms → any addition feeding the
  agent a **new STATE or REWARD input** is identification-breaking creep (REJECT); legitimate rigor = cost realism / delisting
  accuracy / benchmark-factor construction / replicating the frozen protocol on another market. (The throughline behind
  ADR-044/045/046.)
- **STATUS: DECIDED-pending-implementation.**

### Refinitiv access SOLVED (ADR-048) — DONE, verified
- LSEG session **opens (`OpenState.Opened`)** via **PowerShell + an isolated `.venv-lseg`** (`refinitiv-data==1.6.2`). **Root
  cause** of the prior failures: the **Bash/Git-Bash tool's sandboxed network couldn't resolve `api.refinitiv.com`**; native
  PowerShell resolves it. **RULE: run ALL Refinitiv ops via PowerShell + `.venv-lseg`, never the Bash tool.** Verified: pull is
  FAST; 2026 daily data clean; dead-name (survivorship-free) terminal returns recoverable (Lehman verified) → this de-risks the
  ADR-044 forward-extend and the ADR-045 terminal-return delisting fix.

### RL positioning clarified (ADR-048) — methodological
- The setup is **simulated-ONLINE off-policy** (SAC interacts with + explores a historical-replay simulator; price-taker,
  exogenous prices) — **NOT classic offline RL**. Positioned vs Okhrati's offline-RL by his own harm-criterion + the
  relabelling→CQL bridge (`docs/offline_online_position.md`). Prose must say "simulated-online off-policy," not "offline RL."

## [2026-06-30 → 07-01] — Paper flawlessness pass, citation overhaul, campaign-hardening suite, model decision

Full narrative: `docs/SESSION_LOG_2026-06-30_to_07-01.md`. No frozen change (`frozen: false`); nothing committed.

### Paper (publication-grade pass)
- **Theory — both Le Cam deficiency errors fixed** (catastrophic: the formula was vacuously zero; Cor 3.3 named
  the wrong-direction deficiency) + all theory-care (M1 sign box, M2 `P`-a.s., C2/C3/M4/M7/m13, Gneiting cite,
  Table 3.1, intuition gloss).
- Honesty edits across `00_FRAMING`/`CH1`/`CH2`/`CH4`/`CH7` (content-not-channel + endogeneity, INCONCLUSIVE
  branch, bounded caveat, phantom "off-critic non-closedness" pillar struck, K=5 limitation); CH2 "Related Work"
  → "Literature Review". `FRONT_MATTER`: single title, AI disclosure, Ethics section, inlined abstract, ToC/LoF/LoT.
- **Citations:** the entire `refs.bib` web-verified (incl. the examiner's own papers); 34 dangling entries added;
  dedups + `sun2024card`/`rubin2025` content errors fixed; `% VERIFY` note-scaffolding stripped; 4 unverifiable
  keys → researched verified replacements (`gridach2025agentic`, `orra2025volatility`, `wallace2019numbers`,
  `prashanth2018risk`); **integrity gate: 0 cited-but-undefined keys**. 6 new source PDFs added to `01_literature/`.

### Campaign hardening (de-risking suite — `docs/CAMPAIGN_HARDENING_PLAN.md`; 32+ tests green, ruff clean)
- **#1** search-replay cache (`src/llm/loop.py`, wired into serial `run_arm`; replays candidates **and** failures,
  no Opus re-bill, byte-faithful → same winner; closed a real reproducibility bug via a failures-ledger);
  **#2** graceful API-degradation; **#3** pre-flight gauntlet (`scripts/preflight.py`); **#4** auto-guardian
  thermal+RAM governor (`src/utils/guardian.py`, **wired into the SB3 callback** via `trainer._make_governor` +
  `monitoring.make_training_callback(governor=…)`, config-gated `thermal_guardian`); **#5** auto-restart
  supervisor (`scripts/supervisor.py`); **#6** buffer-cap 2nd site (`parallel.py`).
- 5-subsystem scout + 15-item risk register; parallelization verdict (n_gpu=4 = hard 6 GB wall; torch.compile +
  SBX the only result-neutral speed levers; disk a non-issue at ~50–200 MB).

### Decisions
- **PRIORITIES** strengthened into CLAUDE.md as the absolute overriding north star (95%+→100%; world-class,
  cutting-edge, publishable; very deep).
- **Model decision (ADR-039):** primary = **Opus 4.8**; a **REQUIRED strong-diverse panel** (Opus 4.8 + GPT-5.5 +
  Qwen3-Coder; **NO weak models** — Haiku dropped) with a **reasoning-effort** mechanism axis + a legible-format
  ablation; headline reframe = the **numeracy bottleneck**. **SBX/JAX** to be built (gated) as the laptop-only
  panel enabler. Determinism finding (hosted APIs non-deterministic) validates archive-replay.

## [2026-06-29b] — Parameter determination, literature grounding, and the full campaign-design record

Deep determination session (no frozen change; report-only + tooling). Resolved every campaign parameter by
the correct criterion for its class and grounded each in the literature (196-paper corpus, read first-hand).

### The authoritative determination record — `docs/CAMPAIGN_DESIGN_AND_EXECUTION_PLAN.md`
Captures everything: the **committed spec** (200k training steps / 30 seeds / 30 candidates / 7 arms); the
**four-class framework** (MEASURE / CALIBRATE / FIX / REALISTIC — and why most parameters must NOT be
performance-optimised); per-parameter literature justification (training steps = data-limited regime, more
overfits — FinRL-DeepSeek early-stop, ARM-FM plateau, Sharpe-Regret-Reward; seeds = rliable N≈10 +
Henderson power-analysis + paired-CRN; candidates = Eureka/ICPL/CARD saturation; arms = DrEureka control
battery + the **novel `placebo_shuffled`** content-derangement control); the **power analysis** (paired
one-sided IUT MDE table, σ_seed scenarios, n\* = 25/71/11); **construct-validity verification** (frozen base
prompts are tail-neutral); the **tiered 14-day 24/7 compute plan** (primary at its scientific optimum +
secondary panels — padding the primary would overfit); the **framing strategy** (dose-response ladder,
bank-equivalence, mechanism-central, ceiling-effect, H1-anchor, two-tier arms); the execution priority; and
the freeze-blocker list. Indexed in `docs/INDEX.md`.

### Tooling
- `scripts/determine_design.py` — Design Determination Pipeline: per-parameter status + FREEZE-READY verdict;
  the search-saturation engine `recommend_candidates`. +8 tests.
- `scripts/learning_curve.py` — `project_campaign`: turnkey campaign wall-clock + GO/ADAPT/RECONSIDER from the
  measured ladder timings. +5 tests.
- Reproducibility surface: `requirements.lock` (torch==2.6.0+cu124), `REPRODUCIBILITY.md`, `.gitattributes`.
  Private repo `github.com/abailey81/llm-reward-portfolio` (clean, user-authored, no Claude attribution).

## [2026-06-29] — Figure engine + LLM-integration hardening + CI dependency completion (report-only; no frozen change)

Deep-sweep build: all report-only / engineering, **nothing frozen touched** (`freeze.py --check` SHA `7fc686b6`
unchanged), full fast suite **1517 green**, slow 13, data_pipeline 16, ruff-lint + mypy (73 src) clean.

### Publication-grade figure engine — `src/viz/` + `scripts/make_figures.py` (the "faultless presentation" lever)
Results figures were entirely missing. Built a deterministic Okabe-Ito (colourblind-safe + greyscale-robust)
engine: `style.py` (per-arm colour/marker/hatch, IQM + bootstrap-CI, SESOI band, 600-dpi PNG + vector PDF) and
five headline figure functions designed for an HONEST null — `equivalence_forest` (90% TOST vs the ±0.05-DSR
SESOI band; never reads a null off a p), `rliable_intervals` (per-arm IQM + stratified-bootstrap CI), the novel
`risk_return_clouds` (the 7 arms' per-seed clouds collapse onto one neighbourhood) and `evidence_for_null` (JZS
Bayes-factor gauge + Model-Confidence-Set strip = positive evidence FOR H0), and the mechanism figure
`reward_code_similarity` (AST-distance clustered heatmap; clusters cut across arms ⇒ the placebo writes the same
code). `make_figures.py --demo` renders the suite on synthetic NULL-shaped data so the engine is validatable
pre-campaign; post-campaign the same functions take the real per-seed + inference outputs. +11 tests
(`tests/test_viz.py`, headless). Manifest updated (`paper/FIGURE_TABLE_MANIFEST.md`).

### LLM-integration hardening (transport-only; uniform across arms; no prompt-byte change)
- **`stop_reason` correctness fix** (`src/llm/client.py`): `_AnthropicTransport`/`_OpenAITransport` never
  inspected `stop_reason`/`finish_reason`, so a `max_tokens` truncation (reward cut off mid-function) or a
  `refusal` returned partial/empty text → failed the AST gate → was silently mislabeled as a "bad candidate",
  biasing per-arm candidate-yield accounting. Now captures + WARN-logs (`_warn_if_incomplete`) + archives
  `stop_reason` + `request_id` on `ProvenanceRecord` so a capped/refused call is correctly attributed in the
  replay archive.
- **`src/llm/cost.py`** — report-only cache-aware USD + completion-integrity reducer over the replay archive.
- **Disclosure (measured):** the shared prefix (system.txt + ENV_INTERFACE) is ~898 tokens, BELOW Opus 4.8's
  4096-token minimum cacheable prefix (and Sonnet 4.6's 2048), so the ADR-016 prompt-cache lever is **inert on
  Opus 4.8** — documented in `client.py`; no request restructuring (would be a no-op; ~$0.94 of unavoidable
  uncached prefix over ~210 calls). +7 tests (`tests/test_llm_stop_reason_and_cost.py`).

### CI dependency completion — `requirements-test.txt` (fixes a pre-existing latent CI gap)
A clean light-CI env reproduction (only `requirements-test.txt`) revealed the non-slow suite needed four
deterministic deps absent from the light job, so `pytest -m "not slow"` would have errored on collection/run in
CI even though the full venv passed: **`psutil`** (`test_max_power`), **`arch`** (`test_model_confidence_set`
R69, `test_inference_crosscheck`), **`matplotlib`** (the figure engine / `test_viz`), **`pyarrow`** (the
parquet gold-panel loader tests). All CPU-only (no torch). Verified: the full non-slow suite (1517) now runs
GREEN in a from-scratch `requirements-test.txt`-only venv.

### Read-only monitoring extensions — `scripts/monitor.py` (2026-06-28)
Silent-hang/STALE detection (progress.json staleness), an anomaly-by-kind error tracker + live LLM token/USD
panel, an opt-in fail-safe `--notify` (ntfy/healthchecks; stdlib-only side-channel), rotating-circle spinner,
`rich.traceback`. +8 tests; runbook updated. (The known repo-wide `ruff format --check` mismatch — a denser
hand-style flagged by ruff 0.5.7 *and* 0.15.x — remains a tolerated non-defect; `ruff check` lint is the gate
and is clean. Pinning CI ruff to 0.5.7 is rejected: 0.5.7 lint flags a pre-existing `E402` in `test_properties.py`.)

## [2026-06-25] — Deep hypotheses + benchmarks scrutiny (8 agents) + headline reframe + integrity hardening (amendments R25–R31)

An eight-agent exhaustive, literature-grounded, adversarial scrutiny of the WHOLE scientific core (one agent per
hypothesis H1–H4; two on the benchmark ladder; one on the statistical backbone; one hostile-examiner red-team).
Verdict: world-class on conception + inference; the exposure was system-level *completeness*, every fatal route
self-inflicted over-claiming and pre-emptable by disclosure before freeze; a Distinction in every genuine
outcome. The findings (`docs/DEEP_*.md`) were then integrated — all governance/report-only/disclosure, **no
campaign re-run** — and verified GREEN (full suite exit 0, `freeze.py --check` 9/9, ruff clean, mypy +0 new).

### Headline reframed — H2 = two co-primary intersection–union tests (R25; the keystone)
The old gate was `(3-leg Sharpe conjunction) ∘ (BH-over-m=6)` — statistically **double-corrected** (a conjunction
is itself an IUT and is the correction; Berger 1982), and it gated on the *Sharpe* leg while the distributional
contribution acts on the *tail* (the pilot's only signal was CVaR p≈0.004). Restructured `h2_conjunction` into
**H2-RA** (3 Sharpe legs, IUT, one-sided α=0.05, no leg correction) + **H2-Tail** (3 CVaR-5% legs, IUT,
corroborated by FZ0/ES) — each a clean IUT, the m=6 union retained as the realized-family assert + a *reported*
BH-over-6 sensitivity. Fixed a latent cvar_01-gating bug (the tail gates at the headline CVaR-5%). Makes the
distributional contribution **bankable on its strongest dimension**; the null stays bankable too (verbatim
pre-registered statement, §10). A design CORRECTION justified a priori by the theory spine, not a post-hoc switch.

### The asymmetric-rigor fix — H3 + H4 now have campaign-grade sealed-leg tests (R30)
The red-team's CRITICAL finding: H3/H4 were pre-registered but only H1/H2 had a sealed-leg test. Wired:
- **H3 single-shot stage** (`run_campaign.run_h3_singleshot`): the iterative distributional winner (gen 6,
  reflect-on-best) vs a matched single-shot condition (`generations:1`, best-of-N, no reflection; identical
  budget/seeds/50k-buffer/val-DSR selector; disjoint `*_h3_singleshot/` roots; `--h3-singleshot`).
- **H3/H4 difference tests** in `analyze_campaign` (`out["h3"]` + TOST ±0.05; `out["h4"]` H4a/H4b 2-test family +
  Bonferroni-over-2) — per-seed IQM paired, report-only, OUTSIDE the frozen m=6.

### Cross-hypothesis multiplicity declared (R31; the stats linchpin)
H1–H4 are separate pre-registered estimands (each with its own multiplicity control); **no global FWER correction**
by design, with a **Bonferroni-across-4 sensitivity** reported (`out["cross_hypothesis_multiplicity"]`) — making
the garden-of-forking-paths stance explicit.

### Integrity defects fixed (all caught first-hand)
- **R29** — the H4b arm was mislabelled `bayesopt_tpe` / "Optuna TPE, 240 trials" but is scikit-learn **GP-EI**
  (Optuna is not a dependency); relabelled, cite **Snoek et al. 2012** (added to refs.bib with Bergstra-Bengio 2012).
- **R28** — H4a random-search grammar widened from 3 terms to the **shared six-term family** (realizing the frozen
  ADR-010 intent), so H4a is a genuine procedure-only control at matched compute.
- **R27 / §4** — the Troop (2021) bias-corrected POT was promised but only a docstring; **measured** that in-regime
  (n≈750) the plain-MLE CVaR error is ~98% variance and Troop's correction is ill-conditioned (GPD ξ≤0 in ~94% of
  samples) → disclosed plain-MLE, Troop = future work (implementing it would be theatre).
- **H1 hardened** (in R30) — best-of-4 baseline selected on **validation** not test (data-snoop fix), the dangling
  `§18-19→§1/§9` citation fixed, the metric relabelled **Eureka-STYLE** (Eureka's HNS is not computable single-task).

### Killer critiques pre-empted by disclosure
- **R26** — factor attribution (`src/inference/attribution.py`, difference-in-alpha after FF5+Mom(+BAB) HAC) now
  **pre-registered as a declared secondary** — the answer to "the edge is just BAB/low-vol" (red-team G2).
- **L15–L19** added to the limitations register (BAB/low-vol; untuned baselines; measurement-noise; n-of-1
  external-validity; off-policy-SAC-on-noisy-rewards) + `docs/DEEP_FRAMING_discipline.md` (the **no-SOTA-claim**
  discipline — the FinRL band is partly reproducibility smear (0.16→2.39 on seed-fixed code), restrict "does it
  work" to the internal matched ladder; the "distribution → multi-level tail-risk feedback" construct retitle; the
  T0 cost/deflation fairness table).

### Report-only sensitivities + a fixed flaky test
Added DSR effective-N (`out["dsr_effective_n"]`; ρ̄≈0.80→N_eff=1, benign direction), EVT-estimator-consistency guard,
and the T0 per-benchmark turnover/cost + undeflated-N=1 DSR. **Work B (per-candidate resume) DEFERRED** as a
documented operational follow-up (hard-crash risk already mitigated by sleep-disable + n_gpu=2 + the SIGINT
graceful-shutdown + arm-level resume; it is the one change touching the science-sensitive reflection loop).

## [2026-06-25] — Ten-agent campaign-readiness sweep + integration (analysis modules wired, run hardened, citation/compute corrected)

A ten-agent parallel sweep (web-enabled, critical, NO dissertation prose) built the post-run analysis
machinery + operational hardening + the freeze-decision/runbook docs, then the deliverables were integrated
into the live code and verified GREEN (full fast suite exit 0, `freeze.py --check` 9/9, ruff clean, mypy +0
new). All new docs live under `docs/CAMPAIGN_*.md`.

### Analysis-completeness modules (built, tested, standalone-green)
- `src/inference/attribution.py` (+`tests/test_attribution.py`, 18) — factor-model **difference-in-alpha**
  (the "edge is just BAB/low-vol beta" rebuttal); paired across-seed bootstrap (carries training-RNG
  variance like frozen H2), Door-C disjoint family. CAPM/FF3/Carhart-4 run on on-disk data today; FF5/6 +
  BAB/QMJ need a small factor pull (a `factor_provider` hook injects them).
- `scripts/variance_decomposition.py` (+tests, 20) — σ²_seed/σ²_search/σ²_market one-way random-effects ANOVA
  (the "one-lucky-reward" defence); verdict "gap exceeds √σ²_search"; needs K≥2 search re-runs (else skipped).
- `src/inference/contamination.py` + `src/inference/ood_stress.py` (+tests, 31) — named-vs-blinded N3 A/B
  (paired TOST; needs a sealed ~150–200-seed side-experiment) + GARCH-EVT/block-bootstrap/Markov OOD stress.
  Fixed a real GARCH bug (`conditional_variance`→`conditional_volatility`; FHS now reproduces vol-clustering).
- `scripts/power_analysis.py` — re-derived the MDE against the REAL paired test (n_seeds=30, NOT seeds×folds×N);
  honest directional σ=0.360 → **MDE@80% = 0.362 Sharpe**; pre-committed null framing. Generates
  `docs/CAMPAIGN_power.md`.

### Wired into the live analysis (additive, disjoint keys — frozen m=6 untouched)
- `scripts/analyze_campaign.py::analyze()` now computes `out["attribution"]` (panel-dependent, reuses the R20
  rf) and `out["variance"]` (opt-in `--variance-runs`, ≥2 roots); both render in `write_report` and degrade
  gracefully. Default report is byte-identical (variance omitted without the flag).

### Operational hardening (science-neutral, applied + tested, 47 targeted tests)
- `src/io/results.py` — **atomic** record write (temp+fsync+`os.replace`): a kill mid-`json.dump` can no
  longer leave a truncated `record.json` that crashes `--resume`.
- `scripts/run_campaign.py` — SIGINT/SIGTERM **graceful-shutdown** (cooperative `threading.Event`, arm/stage
  boundaries, double-Ctrl-C hard-exit, non-destructive) + a fail-loud failure-wave guard + a CLI-boundary
  `--search-gpu ≥ 4` refusal (6 GB VRAM hard-caps search; n_gpu=4 is the measured search OOM).
- `src/utils/monitoring.py` — GPU-temp (87/91 °C) + RAM (85/92 %) anomaly thresholds (one edit covers serial +
  parallel monitors). `scripts/watch_thermal.py` — NEW zero-touch NVML/`progress.json` thermal sidecar.
- DEFERRED (science-sensitive, pending a dated pre-freeze amendment): per-candidate SEARCH resume in `loop.py`
  (would stop a mid-arm crash re-burning up to 30 paid Opus calls; reconstructs the reflection chain).

### Corrections
- **Citation:** the HAC truncation-lag rule `floor(4(T/100)^(2/9))` is **Newey-West (1994)**, NOT Schwert
  1989 (Schwert's `12(T/100)^(1/4)` is a different ADF unit-root rule). Renamed `schwert_hac_lag →
  newey_west_hac_lag` and corrected the prose in `attribution.py` + test + `docs/CAMPAIGN_attribution.md`
  (which had stated the rule "is Schwert 1989, *not* Newey-West" — exactly backwards). Also re-confirmed
  QMJ = Review of Accounting Studies 2019 (not Review of Finance).
- **Compute:** runbook figures corrected to the authoritative `COMPUTE_AND_TRAINING_TIME.md` (post-amendment
  D2): 6-arm core = 360 runs (~27 h laptop @ n_gpu=4); full lean (core + 120 H1 baselines + ~120 PPO/TD3) =
  ~600 runs ≈ **110 GPU-hr ≈ $32–44 / ~4.6 days serial** on a 4090, ~7.5 days laptop. The run-count locked at
  freeze IS the DSR trial count.
- **Two latent bugs fixed:** `tests/test_contamination_ood.py` `_garch_like_panel` read uninitialised
  `np.empty` memory (`eps[0]` before the loop) → seed-dependent non-finite panels (verified across 8 seeds);
  `tests/test_utils.py::test_logging_configures_idempotently` was order-fragile (root-handler pollution via
  `attach_run_logging` + the module-level `_configured` flag) → now snapshots/restores its own logging state.

### Open (gate the freeze — user decisions, NOT auto-applied)
- **H1 REWARD_CANON** "beat-the-human" test is **un-wired** (the `reward_kind="baseline"` worker branch is
  unreachable; no Eureka fraction/normalised-improvement metric; stale `eureka_loop.yaml` names). REWARD_CANON
  has **9** rewards → wiring it is ~270 runs (9×30), not the compute doc's budgeted 120 (which assumed 4).
- The four freeze-decision-brief calls (λ=0; parallel reflect-on-best headline; rent the 4090; N3 ~150–200
  seeds) + ratifying the per-candidate-resume amendment. See `docs/CAMPAIGN_freeze_decisions.md`.

## [2026-06-24] — Four-agent possibility-space sweep + analysis-machinery correctness (PBO enumeration, responsiveness confound, prototype validation)

A four-agent read-only sweep (engineering / science / write-up-grade / adversarial-risk) mapped the remaining
work. The dominant grade reframe it surfaced: **the MSc is assessed on the submitted PDF alone — there is no
viva** (`02_guidelines_and_examples/.../MSc_Project_Marking_Criteria`), and a pre-registered null is bankable,
so citation integrity + self-disclosed limitations + faultless write-up are the controlling levers (recorded
for the write-up phase, not code). The cross-validated, code-confirmed *correctness* items were then fixed:

### Reflect-on-BEST parallel SEARCH wired into the campaign (behind `--search-gpu`, default off) + buffer-skew fix
- New shared `scripts/run_prototype.py::build_parallel_opts` (the prototype `--parallel` path refactored onto it,
  byte-for-byte) so the prototype and campaign cannot drift in how they assemble the `run_parallel` `opts`.
- `scripts/run_campaign.py`: `_search_parallel_arm` + `--search-gpu/--search-cpu` (default serial). When set, each
  arm's development-split search runs the within-generation/cross-arm scheduler (`parallel.run_parallel`) with the
  campaign's RESOLVED 50k budget and its OWN Opus author (mapped into the flat `model`/`api_key_env`/`temperature`
  keys the driver reads); SELECT/FREEZE/TEST downstream are unchanged (same `val_fitness`/`val_returns` schema).
  The ONLY behavioural delta from serial is the reflection seed (generation BEST vs serial LAST) — amendment-gated
  (PREREGISTRATION §6). Bonus fix: the parallel worker couples `buffer_size == train_steps` (50k), so SEARCH now
  trains at the SAME replay budget as TEST — resolving the documented serial-search 25k-buffer skew.
- Verify: `tests/test_run_campaign.py` (+2: opts built at the 50k campaign budget with the Opus author; `--search-gpu`
  defaults to serial) GREEN; run_prototype + run_campaign tests GREEN; ruff clean; `run_campaign.py` mypy 0 (fixed the
  2 new injectable-callable narrows + 2 pre-existing: the `trainer` factory type and the `write` injectable).

### Pre-freeze amendments drafted (PREREGISTRATION.md, 2026-06-24) — ready for the user's freeze-time ratification
- §6: optional reflect-on-best parallel search + matched 50k buffer (above); serial-vs-parallel choice recorded at freeze.
- §5: λ formalization (PROPOSED) — `lambda_cvar = 0.0` (pure validation-DSR selection; retire the un-calibrated
  `lambda_grid`/`calibration_fold`); the tail is the FEEDBACK channel's job, measured on the test leg, not a selection term.
- §11: config-driven TF32 (`agent.tf32`, default on) uniform across serial/SEARCH/TEST — resolves the select-vs-evaluate
  numerics asymmetry.

### Write-up artifacts produced (no-viva grade levers; non-code)
- `paper/refs.bib` — 36 corpus-verified Harvard BibTeX entries (every 2025-26 / unprinted-field flagged `% VERIFY`); the
  sweep REJECTED four fabricated/future-dated arXiv ids, corrected Troop→arXiv:2103.05059 and Kusuoka→RIMS, flagged the
  memory note's "Di Castro first" as likely wrong, and surfaced that Khraishi-Okhrati 2022 prints NO ICAIF venue (any
  "ICAIF 2022" cite is unsupported — supervisor-stakes).
- `00_planning/LIMITATIONS_REGISTER.md` — 12 threats-to-validity entries (statement + why-probed + prose-ready paragraph),
  repo-grounded; verified the empty `feedback_block` is prototype-only (the live `loop.py` persists it → no campaign risk).

### Environment: SB3/sb3-contrib restored to the pinned `<2.9` (reproducibility-of-record)
- Verified first-hand: the venv had DRIFTED to `stable-baselines3`/`sb3-contrib` **2.9.0**, but SB3 2.9.0 DECLARES
  `torch<3.0,>=2.8` while the validated GPU build is **torch 2.6.0+cu124** (ADR-030/032) — so the installed stack
  violated SB3 2.9.0's own torch floor AND the deliberate `pyproject` cap (`<2.9`); a clean `pip install` could not
  reproduce it. **Downgraded to 2.8.0** (+ gymnasium 1.3.0→1.2.3 to satisfy it), matching the pin + torch 2.6.0.
  **Verify:** the real-SAC equivalence test (`test_test_leg_equivalence`, slow) and the **full fast suite** are GREEN
  on the restored stack. (NB: the prior adversarial-sweep suggestion to "bump the cap to <2.10" was WRONG — it would
  have ratified the non-reproducible stack; the pin was correct, the venv was not.)

### Three-agent adversarial review (science/literature + code + docs) — every CONFIRMED issue CLOSED
A deep, strict, literature-grounded review audited THIS session's work from all angles. Net: science + code
are SOUND — NO confirmed code bugs (466 fast tests pass), and 5/6 scrutinized science decisions sound. Two
verify-first REFUTATIONS of earlier suggestions: (a) the DSR raw-trial-count "anti-conservative" worry is
BACKWARDS (E[max SR]↑ in N → raw N > N_eff → LOWER DSR → MORE conservative; Bailey-LdP 2014 App. A.3), so an
ONC N_eff module was NOT built (it would move the number the permissive way); (b) λ=0, PBO full-enumeration,
reflect-on-best (Eureka Alg.1 line 9), and the FZ0/ES non-wiring are all confirmed sound/Eureka-faithful.
Confirmed issues — all CLOSED + re-verified (full fast suite GREEN, ruff clean, mypy +0, YAML parses):
- **#3** responsiveness metric was over-billed "core H2 evidence" vs its own directional disclaimer → DEMOTED to
  a directional probe (the ablation lattice is the causal test, cf. Eureka §4.3); Pearson→**Spearman**; 0.0→**None**.
- **C1** §11 "explicit in config" overclaim → softened (TF32 is one `train_agent` setting, default-on/overridable, uniform).
- **C2** the 3 amendments had no YAML mirror → added `search.*` + `agent_numerics.tf32` to `config/preregistration.yaml`.
- **C3** §5 "λ-grid retired" vs still-present config → softened to "left INERT (deleted at freeze if λ=0 ratified)".
- **C4** added rows R21/R22/R23 to the PREREGISTRATION amendment-record table.
- **C5** added the missing frozen-prereg reference Troop 2021 (arXiv:2103.05059, bias-corrected POT) to `paper/refs.bib`.
- **C6** dropped the unsupported "ICAIF" venue on Khraishi-Okhrati 2022 in `docs/REFERENCES.md` (matches refs.bib; supervisor-stakes).
- **3a** (latent) threaded `learning_rate`/`gamma`/`ent_coef` through `build_parallel_opts`→`_spec`→`train_candidate`
  so the parallel SEARCH worker honors the full agent config (parity with serial + TEST; behaviour-preserving).
- **U1/U2/U4** added LIMITATIONS L13 (λ=0 tail-blind selection trade-off) + L14 (default-path 25k-buffer skew); fixed L12's
  nuance (the parallel `--search-gpu` path also leaves `feedback_block` empty — the gate reads `prompt` either way).
- **Noted for the run** (3e, not a code fix): the `--search-gpu` path reuses `run_parallel`'s single non-recycling
  DevicePool — monitor RSS on the first real arm or wire `run_recycling` for TEST-leg parity.

### Split verification (3 more independent agents, re-running suites + freeze.py) → final residuals closed
Net: code FLAWLESS (no bugs; 466 fast + real-SAC equivalence green), `freeze.py --check` PASSES, the H2 chain intact.
The residuals it surfaced — all closed + re-verified:
- **TF32 made genuinely config-driven** (V2's recommended resolution): added `agent.tf32` to `config/prototype.yaml`
  and threaded it `_agent_cfg`→`build_parallel_opts`→`_spec`→`train_candidate`, so the serial/SEARCH/TEST legs read the
  precision from CONFIG (was a `train_agent` default). §11/R23/mirror flipped to the now-true "config-driven" (behaviour-
  preserving — tf32=True everywhere as before; verified flowing True through all three legs).
- **§5 + L13 λ prose** corrected to cite the `held_out_fitness` default (`lam=0.0`), not `config/inference.yaml` (which
  carries no `lambda_cvar` key); selection is λ=0 by function default, config-independent. L13 also notes λ=0 is *neutral*
  for the Sharpe-gated headline (adversarial only on the tail legs).
- **CHANGELOG** `+0.0504` annotated as the pre-Spearman Pearson value (true Spearman = −0.0529; directional, no number enters).
- **refs.bib** Politis-Romano 1994 added (verified first-hand: JASA 89(428):1303-1313, JSTOR 2290993) + the Tier-1 scope disclosed.
- **freeze.py gate hardened** — `assert_prose_matches_yaml` now also checks `fitness.lambda_cvar` (R22), `agent_numerics.tf32`
  (R23), `search.reflect_protocol_default` (R21); 2 freeze tests updated (6→9 checks).
- **Verify:** full fast suite GREEN (1 skip); real-SAC equivalence GREEN; `freeze.py --check` PASSES (9 checks); ruff clean;
  mypy +0 new; `preregistration.yaml` parses; `refs.bib` 38 entries, no dup keys.

### PBO/CSCV primary overfitting guard — FULL deterministic enumeration (was a random subsample)
- `src/inference/overfitting.py::pbo` caps evaluated CSCV splits at `_MAX_COMBINATIONS = 4000`, but the frozen
  `n_blocks=16` gives `C(16,8) = 12,870 > 4000`, so the **PRIMARY** (trial-count-free) overfitting guard ran on
  a random 4,000-split subsample → the headline PBO was **seed-dependent**. `scripts/analyze_campaign.py::campaign_pbo`
  now passes `max_combinations = math.comb(n_blocks, n_blocks // 2)` → the full 12,870-split enumeration (ms-cheap),
  making PBO deterministic. **Verify:** new `test_campaign_pbo_fully_enumerates_at_frozen_s16` (two unrelated rng
  seeds → identical PBO ⇔ enumerated, not sampled); `test_analyze_campaign.py` 14/14 GREEN, ruff+mypy clean.

### `inspect_rewards.feedback_responsiveness` — measured-vs-fed tail CONFOUND fixed (the H2 mechanism metric)
- The "did the LLM USE the distribution" metric (the single most distinctive non-benchmark artifact) correlated
  each reward edit with the tail delta the designer was *fed*. But `_tail_vector` preferred `metrics['tail_stats']`
  — the tail **measured off-critic for EVERY arm** — so `scalar` (fed only a Sharpe scalar) and `placebo` (fed
  inert constants) were scored against a distribution **they were never shown**, yielding spurious correlations
  (real prototype: scalar **+0.42** > distributional +0.05). The synthetic unit-test fixtures coupled
  `tail_stats` to the rendered tail text, so this **passed in tests but was wrong on real data**.
- **Fix:** a new `_was_fed_tail(record)` gate decides responsiveness from what the designer **SAW** — the rendered
  `feedback_block`, or the full `prompt` when the loop leaves `feedback_block` empty (as the prototype does) —
  applied per-arm in `feedback_responsiveness`. Arms not fed a tail (`scalar`/`placebo`/the search arms) now
  correctly report `score=None`; **distributional is preserved by the gate (38 steps; +0.0504 was the Pearson value at
  this step, later switched to Spearman −0.0529 by the review's #3 fix below — DIRECTIONAL, no number enters the dissertation)**; `scalar_cvar5`
  retains a score (it *was* fed `cvar_05`). **Verify:** new `test_feedback_responsiveness_ignores_measured_tail_when_not_fed`
  replicates the real confound (measured tail present, none fed → `None`); `test_inspect_rewards.py` 13/13 GREEN;
  ruff clean; `inspect_rewards.py` mypy **0** (also inlined a pre-existing `vec` `[no-redef]`).
- NB (for the campaign): records persist the fed feedback in `prompt` and leave `feedback_block` empty — the gate
  reads both, so it is robust either way; populating `feedback_block` in the loop would be a tidy follow-up.

### TEST-leg TF32 comment corrected (stale after the config-driven TF32 change)
- `src/orchestration/test_leg.py` said the worker "DELIBERATELY do NOT enable TF32"; since TF32 became config-driven
  in `train_agent` (default on), all three legs (serial / SEARCH / parallel TEST) share it. Comment rewritten to
  match (the adversarial-risk agent's only CONFIRMED code issue — it had verified 12 invariants sound); worker
  traceback widened 3→12 frames for real-run debuggability.

### Prototype analysis pipeline VALIDATED end-to-end on the real archive (directional — no number enters the dissertation)
- Ran `analyze_results.py` + `inspect_rewards.py` on `outputs/prototype` (6 arms × ~40 candidates): verdict **AMBER**;
  the analysis pipeline (`load_arms`/`load_all`, IQM, stratified bootstrap CI, difference tests, forensics) works on
  real records — **de-risks the campaign H2 analysis** (an initially-suspected loader bug was a wrong `--root`; the
  loader is sound). Directional mechanism signal (NOT a result): the distributional winner's CODE genuinely uses tail
  terms (`cvar, drawdown, sort, std, var`); distributional-vs-scalar is **indistinguishable on Sharpe (p=0.41) but
  significant on CVaR (p=0.004)** (1-seed, directional) — the tail-shaping the H2 thesis predicts; reward-hacking minimal (2/239, both benign
  tautology). Containment rule respected: directional go/no-go only.

## [2026-06-24] — Max-throughput laptop campaign: deadlock-free pool-recycling primitive (parallel test leg + security hardening in progress)

### Worker-recycling deadlock MEASURED across all installed Pythons (3.11–3.14)
- The campaign throttled candidate concurrency to `n_gpu=2` because `ProcessPoolExecutor(max_tasks_per_child=…)`
  — the clean per-worker RAM-reclaim — was *believed* to deadlock on Windows spawn (only 3.11.9 was noted).
  **Measured first-hand 2026-06-24:** recycling HANGS (>75 s, no progress, terminated) on Python **3.11.9,
  3.12.10, 3.13.13 AND 3.14.4**; the no-recycle control completes in 0.1 s on all four. So a Python upgrade
  buys **no** recycling benefit, and 3.14 is beta (no torch-2.6 wheels). **Decision: stay on the validated
  3.11.9 venv** (torch 2.6.0+cu124, SB3/sb3-contrib 2.9.0, pyarrow 24, numpy 1.26.4).
- Hardware measured (this laptop): 16 logical / 10 physical cores, 15.6 GB RAM, RTX 4050 **6 GB VRAM**.
  `auto_n_gpu()` = **4** at 25k and 50k steps (VRAM caps GPU workers at 4 ≈ 1.4 GB CUDA ctx each; RAM caps
  ~5 total). Beyond ~4–5 = swap = slower. Free alternative flagged: Kaggle T4/P100 (16 GB, 30 h/wk free).

### `src.orchestration.parallel.run_recycling` — deadlock-free RAM reclaim (NEW)
- Replaces broken in-pool recycling with **manual pool-level recycling**: runs specs through a sequence of
  fresh `DevicePool`s of `recycle_every` tasks each; the `with` exit terminates the worker processes → the
  OS reclaims each worker's entire (fragmented SAC-replay-buffer) heap → per-worker RSS cannot creep across
  a long run. Pool re-spawn (~15 s) is amortized over `recycle_every` trainings.
- Additive, back-compatible API: `DevicePool(initializer=…)` (a `_DEFAULT_INIT` sentinel keeps the production
  `_worker_init`; tests pass `None` for bare no-torch workers); `DevicePool.submit_with(fn, spec)` (run an
  arbitrary picklable worker on the shared device-token pool, e.g. the TEST-leg worker);
  `run_recycling(specs, worker=, n_gpu=, n_cpu=, recycle_every=, initializer=)`.
- **Verify:** new `tests/test_parallel_recycling.py` (2 tests) **GREEN** — 10 tasks processed in order, cpu
  device tokens assigned, **5 distinct worker pids across 3 fresh pools** (reclaim confirmed) + single-batch
  edge case; `parallel.py` imports clean (no syntax regressions from the 6 edits).

### Parallel campaign TEST leg — single-source-of-truth + science-neutral (NEW)
- **`src.orchestration.test_leg`** (new module): `build_test_record` is the SOLE per-seed record schema,
  called by BOTH the serial `evaluate_winner_on_test` (refactored onto it — verified byte-identical by the
  existing `test_run_campaign` invariant tests) AND the new parallel worker, so the two paths cannot drift.
  `_test_seed_worker` reconstructs panel/reward/env/trainer from a picklable spec (mirrors `train_candidate`)
  and replicates the serial per-seed body EXACTLY (B1-B6: matched budget, per-seed `set_global_seed`, frozen
  re-instantiation, ONCE-only test touch, env-fingerprint, R18 lookback purge). `evaluate_winners_on_test_parallel`
  is the driver: frozen/test desync guard once per winner, `--resume` skip, per-arm writes, failure-counting;
  its `runner`/`worker`/`write` are injectable so the orchestration is fast-tested with no spawn / no torch.
- **TF32 made a single config-driven setting (`agent.tf32`, default on) applied in `train_agent`**, so the
  serial trainer, the SEARCH worker, and the parallel TEST worker select AND evaluate the fixed agent under
  IDENTICAL float32 numerics. Removes a latent SEARCH-vs-TEST numerics asymmetry (TF32 was previously enabled
  only inside `parallel.train_candidate`; the serial trainer ran TF32-off) — the cousin of the batch_size
  256/512 drift. **Pre-freeze amendment to ratify** (alongside reflect-on-best); applied identically across
  all arms, so it does not affect H2 identification.
- **`run_recycling`** (manual pool-level recycling) is the deadlock-free RAM reclaim for the laptop n_gpu=4
  campaign (in-pool `max_tasks_per_child` deadlocks on Windows spawn across CPython 3.11-3.14 — measured).
  `DevicePool.submit_with(fn, spec)` runs the TEST worker on the same device-token pool; crash-safe (a worker
  that RAISES is captured, never aborts the run). **`parallel.py` mypy 8 → 2** (the 6 cleared were pre-existing).
- **Verify:** `tests/test_parallel_recycling.py` (4) + `tests/test_test_leg.py` (6) GREEN; full non-slow suite
  GREEN (pre-TF32 + re-run); ruff clean on all changes; mypy +0 new everywhere.
- **Security:** a fresh adversarial audit of the untrusted-code sandbox, secrets (`.env`/`capture_env`),
  prompt-injection (schema-derived feedback only), and supply-chain (`pyarrow` 24 / `torch` 2.6 CVEs
  patched-or-unused-paths) found **ZERO critical issues** — a strong, citable posture for a codebase that
  executes LLM-generated code.

### `run_campaign --gpu` TEST-leg wiring + science-neutrality PROVEN (NEW)
- `run_campaign.py` gains `--gpu/--cpu`; `run_headline_campaign(n_gpu>0)` runs each arm's 30 TEST seeds
  through `evaluate_winners_on_test_parallel` (device pool + manual recycling). Default `n_gpu=0` keeps the
  serial `evaluate_winner_on_test`, so every serial unit test is untouched (`test_run_campaign` green;
  mypy +0 new — the 4 run_campaign.py errors are pre-existing). A parallel-TEST failure wave is surfaced
  (no silent "tested (0)").
- **Science-neutrality PROVEN** — `tests/test_test_leg_equivalence.py` (slow) trains the fixed SAC for real
  and asserts the PARALLEL `test_returns` **== the SERIAL** path's (CPU, single-threaded, fixed seed →
  byte-identical within 1e-6; same `run_id`/`frozen`/schema). Parallelizing the TEST leg changes nothing
  observable. A `--dry-run --gpu 1` confirmed the integration runs end-to-end (its degenerate 1-day test
  window writes 0 records in BOTH serial + parallel — a synthetic-panel/`resolve_windows` artefact, not a
  parallel bug).

### Remaining (gated on the user)
- **Reflect-on-best SEARCH parallelization** (`run_parallel` into the campaign search, for the laptop ~27 h):
  gated on the dated PREREGISTRATION amendment (reflect-on-best + the config-driven TF32) being ratified
  and mirrored in `config/preregistration.yaml`.
- **FREEZE the pre-registration** — `config/preregistration.yaml: frozen: false` today; freezing must
  PRECEDE the confirmatory run (the single highest-grade-weight integrity action; user-gated).

## [2026-06-20] — Prototype reward-author → Claude Sonnet 4.6 (ADR-038) + per-file strict audit: all 42 confirmed defects fixed

### Provider switch Gemini → Anthropic Claude Sonnet 4.6 (prototype only; campaign stays Opus 4.8)
- `config/prototype.yaml: llm` → `provider: anthropic`, `model_snapshot: claude-sonnet-4-6`,
  `api_key_env: ANTHROPIC_API_KEY`, `temperature: 1.0` (Sonnet HONORS temperature → sampling diversity;
  no prompt-variation, unlike campaign Opus 4.8 which rejects it). Recorded as **ADR-038**.
- **`.env` was never loaded** — nothing in `src/`/`scripts/` called `load_dotenv`, so a Pass-B run would
  die "ANTHROPIC_API_KEY not found" despite `.env` holding it. Added `src/utils/env.py::load_env()` called
  at the real entry points (`run_prototype`/`run_campaign` `main` + the parallel worker). Kept OUT of
  `client.build_transport` so that factory stays PURE (its no-key error path remains unit-testable;
  Windows-`spawn` workers inherit `os.environ`).
- **Opus temperature guard:** `_TEMPERATURE_REJECTING_MODELS = (opus-4-7, opus-4-8)`;
  `make_anthropic_transport` drops a stray `temperature` for those so a config mismatch can't 400 the
  campaign. `anthropic` SDK 0.111.0 installed. **Validated end-to-end** with a live Sonnet call (valid
  reward code returned, `temperature=1.0` accepted, token usage archived).

### Per-file strict audit (127-agent, 42 confirmed) — ALL fixed + reconciled
A file-by-file marking pass found 42 confirmed defects (1 crit, 3 high, 18 med, 20 low) beyond the earlier
~80. Fixed via a 27-file fix-workflow (adversarially verified) + manual completion of every flagged item:
- **The 1 CRITICAL + 3 HIGH are all in utility/analysis scripts** (`verify_inventory` broken imports +
  no `__main__`; `power_analysis` unbounded auto-regime count N=145; the `analyze_campaign` "single-root"
  report) — **none blocks the prototype/campaign run.** `verify_inventory` now reads the real repo-root
  manifest + emits its JSON; `power_analysis` got a `too_many` upper-bound trip (config-read
  `MAX_PLAUSIBLE_REGIMES`); the `analyze_campaign` single-root + `winner_dsr`-ddof findings were verified
  **already fixed in source** (the loader walks `_MAX_ARCHIVE_DEPTH=3` over `<leg>/<arm>/<cand>` and
  separates search-leg `val_returns` from test-leg `test_returns`; `winner_dsr` already uses the ddof=1
  `_sample_moments`) — the stale **test** was corrected to match.
- **Run-affecting MEDs fixed:** `portfolio_env.step()` now reports the window-exhaustion boundary as
  `truncated` (not `terminated`) so SB3 SAC bootstraps the boundary value instead of zeroing it (3 tests
  reconciled to the new Gymnasium contract); `reward_family` clips `log1p(port_ret)` so a < -100% return
  can't poison the stateful cum/drawdown; `extract_reward_source` no longer commits to a syntactically
  broken first `def reward` block; the TQC factory routes `n_quantiles`/`n_critics` via `policy_kwargs`
  (top-level would `TypeError`) and `top_quantiles_to_drop_per_net` top-level.
- **Inference/data MEDs fixed:** `reporting.iqm` + `es_backtest.var_es` now strip non-finite inputs
  (agreeing with their `bootstrap` twins); the data pipeline purges adjacent splits by
  `max(embargo=21, lookback=60)=60` (R18) with a `dict[str, Any]` manifest (no `type: ignore` smuggle);
  `loaders` VIX leading-NaN seeds from the genuine prior session (bfill only for the irreducible
  global-first cell); the `measurement` EVT-boundary docstring direction corrected.
- **20 LOW** (dead code, stale docstrings, wrong exception types, edit-trail prose) cleaned.
- **Verify:** full non-slow suite **GREEN**, 8 slow SAC/TQC tests pass (terminated/truncated + TQC
  construction safe), `ruff check` clean, `mypy` at the 13-error baseline (+0 new), `freeze --check` OK.
  (Pre-existing/out-of-scope: `ruff format --check` flags 83/117 hand-formatted files — never enforced,
  no live CI; not introduced here.)

## [2026-06-20] — No-hardcoding audit (54-agent): 10 config-source violations fixed (config is the single source of truth)

A strict audit (CLAUDE.md: "config/*.yaml is the single source of truth; code reads config, never hardcodes")
found **10 real config-source/drift violations** — confirmed by the cross-cutting fact that `cfg_get` returns
a present-but-`null` value AS `None` (so an `algos.yaml: sac.batch_size: null` is NOT an effective source —
the in-code literal defaults were the de-facto source of truth). All HIGH/MED fixed; verified 451 passed /
1 skip, ruff clean, mypy +0 new errors, freeze OK.

- **[HIGH] SAC `batch_size` drift (256 vs 512)** — the same hyperparameter had TWO divergent literal defaults
  across the sequential (256) vs `--parallel` (512) training paths (5 resolution sites). On the documented
  max-throughput `--parallel` path this could SELECT the frozen winner under batch 512 but EVALUATE it on the
  sealed test under 256 — the fixed-agent train/test mismatch audit A-1 forbids. Unified to ONE canonical
  default (256, the SB3 default + what prototype.yaml and the sequential path already use); deleted the 512
  literals in `run_prototype.py` + `orchestration/parallel.py`.
- **[HIGH] `buffer_size` 1M literal in `agents/factory.py`** contradicted ADR-025 (buffer = train-step budget,
  full-history replay, no eviction) AND diverged from `trainer.resolve_agent_kwargs`. Now mirrors the trainer
  exactly: defaults to `train_steps_per_candidate` (the 1M literal OOM'd the 4090).
- **[HIGH] Headline H2 BH/FDR `q` (0.05) was never passed on the wired path** — `analyze()` called
  `h2_conjunction` with no `q`, so the frozen FDR level lived only as a function-default literal. Now READ
  from `config/inference.yaml: multiplicity.q` and passed explicitly. Same for the **headline CVaR tail level**
  — now read from the FROZEN `config/preregistration.yaml: inference.testing_family.cvar_levels` (it is NOT in
  inference.yaml, so the prior read was a silent `(0.05,)` fallback, not the frozen value).
- **[HIGH] pre-registered family size `m=6` hardcoded in `power_analysis.py`** (PowerConfig + CLI default) →
  READ from `config/preregistration.yaml: inference.testing_family.m` via a new `_frozen_family_m()` helper
  (the SAME m the campaign enumerates + asserts), so the selection-power Šidák adjustment can't silently drift.
- **[MED] eval-span end date `"2025-12-31"` hardcoded** in `analyze_campaign.main()` (the floor-panel load) →
  READ from `config/inference.yaml: splits.evaluation.span[1]`.
- **[MED] prototype/parallel embargo `21` literal fallback** (read from a config block lacking the key) → now
  falls back to the canonical `config/data.yaml: embargo_days`, not a bare literal.
- **[MED] `n_assets=30` hardcoded on the `--parallel` LLM-prompt path** (sequential uses `panel.N`) → READ
  from `config/environment.yaml: universe.n_assets`.
- **[LOW] fitness CVaR penalty α=0.05 hardcoded** in `held_out_fitness` → a `cvar_alpha` param defaulting to
  `config/inference.yaml: fitness.alpha`, read only when the penalty is active (λ≠0), so the λ=0 hot path stays
  config-free. (The duplicated action-`bound` 10.0 fallback was assessed and ACCEPTED: both call sites fall
  back to the same value, `action.bound` is always present + freeze-bound, so there is no real drift.)

## [2026-06-20] — Critical-review pass: Omega-threshold fix, additive R20 risk-free robustness, independent verification of the highest-stakes changes

A second, EXTREMELY critical multi-angle pass (user: "ultrathink, be very critical, watch from as many
angles as possible"). An 8-dimension adversarial review workflow was launched; in parallel:

### A real bug I had introduced — Omega's MAR silently shifted with rf (fixed)
- The array-rf generalisation made `metrics.compute_metrics`' **Omega** use the rf as its threshold. Omega
  is a distribution-SHAPE ratio about a fixed minimum-acceptable-return (Keating-Shadwick 2002; standard
  τ=0); using rf made it rf-dependent (a real per-period rf shifted it by ~0.02). Fixed to a **fixed 0 MAR**
  (rf-invariant), with a test asserting Omega is rf-invariant while Sharpe/Sortino correctly are not.

### R20 — additive risk-free robustness of the H2 Sharpe conjunction (frozen headline UNTOUCHED)
- **Critical insight (analytic + empirically confirmed):** my earlier "rf ≈ cancels for same-agent arm
  contrasts" was too glib. The per-seed Sharpe rf penalty is `mean(rf)·√252/σ` — LARGER for LOWER-vol arms.
  If the distributional (tail-aware) arm wins partly via lower realised volatility, threading rf
  SYSTEMATICALLY SHRINKS the measured H2 edge. A synthetic low-vol distributional arm showed positive
  shrinkage on all three legs (`distributional>scalar` −0.042 Sharpe). So rf genuinely moves the headline.
- `collect_family_pvalues` gained a `risk_free=None` param: **`None` is byte-identical to the frozen rf=0
  headline** (verified; `h2_conjunction` unchanged), and a per-period rf makes the SHARPE leg use excess
  returns (CVaR stays raw). New `h2_sharpe_rf_robustness` runs the family BOTH ways and reports per-leg
  effect/p-value/direction/BH-rejection + the shrinkage, certifying whether H2 survives the rf convention.
  Purely additive sensitivity — the decision to make excess the PRIMARY headline stays parked for the user.
- **Independent verification of the highest-stakes changes** (real data): the R18 embargo purge provably
  clears the prior split (first test obs lookback `[1259:1319]` starts exactly at `val_end`=1259, at BOTH
  boundaries); the `benchmark_floor` market-reference alignment is correct end-to-end (winner size = window,
  beta 0.83 for EW-top-30 vs the EW market — sensible). Full suite 442 passed / 0 failed.

### The 8-angle review landed (95 agents, 32 confirmed findings) — triaged + fixed
- **The benchmark suite was the real liability (all FIXED).** My R19 allocators were broken on the real
  test leg: `minimum_variance`/`maximum_diversification`/`mean_variance` Euclidean-projected an
  UNCONSTRAINED Σ⁻¹ vector onto the simplex and **collapsed to a single asset** (min-var had HIGHER
  variance than 1/N; max-div ratio = 1.0, the worst); `inverse_volatility`/min-var/max-div put ~100% on
  **delisted zero-variance names**; and `hrp` **crashed** on those names (linkage finite-value error).
  Rewrote them to solve the **long-only constrained QP** (`_long_only_min_variance`/`_long_only_max_sharpe`
  via SLSQP, mirroring risk_parity), exclude dead names (`_live_mask`), and made hrp robust + the
  `WeightPolicy` shim exception-safe (1/N fallback). 6 new correctness tests (GMV beats 1/N variance,
  max-div beats 1/N ratio, dead names get 0, no collapse, hrp robust) — verified over 20 seeds.
- **Leakage hardening (R18).** `make_env_builder`'s guard is now **lookback-aware** (`max(embargo,lookback)`,
  threaded from the campaign) so the R18 invariant no longer rests on one unguarded line; the resolve_windows
  test now asserts `gap ≥ lookback` (a future revert to embargo-only now FAILS the suite). Reconciled the
  R18 freeze/doc desync: the "byte-match 2015-02-03" claim was false (executed val starts ~2015-03-31 under
  the 60-session purge) — fixed across `loaders` (×2), `run_prototype`, `parallel`, `data.yaml`.
- **Correctness + honesty.** `compute_metrics` benchmark-relative now uses ONE shared finite mask over the
  aligned (returns, benchmark) pair (an interior NaN previously desynced beta/alpha/IR). `Omega` decoupled
  from rf (fixed 0 MAR, rf-invariant). `assert_fixed_agent_across_arms` honestly relabelled as a TEST-ONLY
  determinism/budget check (it is tautological — cannot catch a per-arm override the architecture cannot
  express). Stale-docs swept: prereg `benchmarks` mirror → 8 R19 names, "five benchmarks" → eight, removed
  Cornish-Fisher citation, `market_reference` suffix → `gold_suffix()`, DGS3MO/FF-Momentum docstrings.
  Edge-cases hardened: `return_minus_drawdown` log1p clip, drawdown-series divide warning.
- **Benchmark floor WIRED into production (#2/#6/#12, +MED#5).** `analyze()` now produces the DeMiguel
  floor + `market_reference` when given the panel/cfg/test_window (records-only default preserved for unit
  tests); `analyze_campaign.main()` loads the panel + reads the resolved `test_window` from the campaign
  summary; new `benchmark_floor_markdown` renderer wired into `write_report`. Carried **#14** (market-line
  Sharpe now routed through the same rf convention as winner-vs-market) and **#17** (the searched winner's
  DSR is deflated by `winner_n_trials`=candidate budget, while the un-searched benchmarks stay N=1). The
  floor gate uses the headline arm's seed-mean test path as the representative winner. Test added.
- **Net:** every must-fix from the 32-finding review resolved; suite **448 passed / 0 failed**, ruff +
  mypy (baseline) + freeze clean. Remaining items are documented-as-limitation / latent-unreachable
  (walk-forward CPCV materializer purge, rf leading-gap, synthetic dry-run mask) per the review synthesis.

### R20 finalised + env cash-rate support (user: "proceed"); confirmation review launched
- **R20 wired into the report.** `analyze()` now also produces `h2_sharpe_rf_robustness` (the excess-return
  H2 Sharpe sensitivity) when a panel is supplied, with a `h2_rf_robustness_markdown` renderer in
  `write_report`. The **frozen rf=0 headline is RETAINED as the pre-registered primary** (additive only);
  PREREGISTRATION **R20** records the convention + the vol-dependent shrinkage caveat. Test added.
- **Env cash sleeve now priceable** (`portfolio_env.cash_daily_rate`, config key added). Default **0.0** —
  byte-for-byte unchanged, so no test/training impact. Held at 0.0 deliberately: a CONSTANT cash rate
  biases the risk study (the 3-mo T-bill ranged 0–5.6%/yr 2005–2025 and would overpay cash in the
  2008/2020 ZIRP stress the tail-aware arm exploits), so a per-session DGS3MO SERIES is the documented
  correct refinement before enabling. The env *prices* cash when set; the value choice is flagged, not rushed.
- A second adversarial **confirmation review** (6 dimensions: are the fixes correct? new regressions?) was
  launched on the fixed code to close the verification loop.

### Confirmation review landed (7 findings) — all addressed; + manual deep verification
- **[HIGH] `risk_parity` lacked the dead-name mask** — the ONLY cov/vol allocator I missed: its ERC
  log-barrier put ~0 risk on (hence dumped ~49% weight onto) zero-variance delisted names, corrupting the
  frozen DeMiguel floor. Fixed to run on the live sub-panel like its siblings; added to the dead-name test.
- **[MED] floor gate re-introduced seed-averaging inflation** — the gate computed the winner DSR on the
  30-seed MEAN test path, shrinking variance ~√S and inflating DSR vs the single-path benchmarks (the exact
  anti-conservatism the H2 #9/#14 fix removed). Now gates the **median of per-seed DSRs** (like-for-like
  single-realisation), verified below the seed-mean value. Report-only gate (does not touch H2/PBO/selection).
- **[MED] floor `winner_n_trials`** now derived from the records' authoritative per-arm count (consistent
  with `winner_dsr`); the `main()` fallback reads the campaign budget (30), not the prototype's 40.
- **[LOW] residuals fixed**: `test_embargo_splits` module docstring (the byte-match-2015-02-03 claim the
  reconciliation sweep missed), `ARCHITECTURE_BLOCKS.md` Cornish-Fisher reference, `log_growth` log1p clip
  (consistency with its sibling; unreachable but defensive). One out-of-scope item (pre-existing synthetic
  dry-run window clamp) left as the already-documented smoke-path limitation.
- **Manual deep verification** (concrete, beyond the workflow): all `src` modules import clean; the
  `NotImplementedError`s are legitimate loud guards; cross-config values (embargo/lookback/seeds=30/m=6/
  budgets) consistent; **warnings-as-errors** suite passes (no hidden numerical warnings from our code); all
  test skips are legit data/platform guards; the **freeze hash is stable + deterministic**; the **8 slow
  agent-training (SAC) tests PASS** (verified for the first time — they are deselected in every normal run);
  removed the dead `_project_simplex` (the Euclidean-projection footgun that caused the allocator collapse).
  Suite **448 passed / 0 failed**, ruff + mypy (baseline) + freeze clean.

### Whole-project verification (96-agent, 41 findings) + fixes; science confirmed sound
- The exhaustive verification verdict: **none of the 41 findings corrupt the headline H2 result, the sealed
  test leg, the inference, or any reported number** — the defects cluster in freeze-integrity + CI/coverage.
  The 6 must-fix-now are all fixed:
  - **[HIGH] `freeze.py --check` was self-defeating** — the canonical hash included the two MUTABLE
    freeze-state bytes (`frozen`, `freeze_hash`) that `make freeze` flips, so `--check` reported DRIFT
    forever post-freeze (would fire at submission). The hash now blanks those fields (invariant to the
    freeze act; new test). It ALSO now **binds the executed config** (inference/environment/data.yaml), so
    a change to the load-bearing knobs (splits/embargo/lookback/family) is caught — it previously hashed
    only the prereg, so "nothing frozen can drift" was false at the config layer.
  - **[MED, sandbox hardening] `str.format` dunder-walk escape** — `'{0.__class__.__mro__[1].__subclasses__}'
    .format(x)` passed the AST gate (which inspects attribute *nodes*, not string-literal contents) and
    walked to `object.__subclasses__` (RCE/info-disclosure). Fixed: `format` removed from the allowlist +
    a defence-in-depth scan of string literals for replacement-field attribute access; new test.
  - **[HIGH] CI never gated the SAC agent / leakage guard** — the slow agent-training + NormalizedPolicy
    eval-stat-freeze tests (the no-leakage invariant underpinning H2) ran in NO CI path. Added a torch CI
    job running the slow set + the data_pipeline leakage tests. (Verified locally: all 8 slow tests pass.)
  - **[MED] config contradictions** — `power_analysis` SESOI/equiv-margin were a hardcoded 0.20 (4× the
    frozen 0.05) rendered under a "FROZEN-design value" label → now READ from `config/preregistration.yaml`
    (config-driven, not hardcoded); `config/llm.yaml` advertised the superseded Sonnet 4.6 → Opus 4.8 per
    ADR-035. The 30 LOW findings (cash_features-NaN-but-unused, dormant checksum, doc-labels, agent-config
    defaults) are documented-as-limitation / overlap the running no-hardcoding audit.

### Deep research (42 vetted resources) + oracle validation
- A 120-agent strict research sweep (2-vote relevance vetting) → `docs/RESEARCH_RESOURCES.md`: the
  publishable gap CONFIRMED (no prior work feeds a return distribution as LLM reward feedback, nor applies
  reward-code search to portfolio RL), plus the citation lineage (Eureka/Text2Reward/REvolve/DSAC/Beyond-CVaR),
  baseline ladder (FinRL value-change + Moody-Saffell DSR), N3 backbone (Profit Mirage/FinLake), and
  cross-check oracles.
- **Oracle-validated the headline inference**: `inference.{bootstrap,reporting}.iqm` and
  `reporting.probability_of_improvement` now MATCH the canonical `rliable` (Agarwal et al. 2021)
  implementation to 1e-9 (new `test_inference_crosscheck` oracle tests; rliable is an installed dep).

## [2026-06-20] — World-class elevation pass: block decomposition, B11 backtest analytics, B8 baseline expansion, supervisor leakage/rigor audit (15 findings) + fixes (R18 embargo, R19 benchmarks)

User mandate: decompose the prototype into blocks, elevate each to a "world-class, publishable, flawless
grade-maximiser" standard, run deep research + a 50-year-supervisor leakage/rigor audit, fix every gap,
and record everything. Pre-registration is still `frozen: false`, so design changes are dated pre-freeze
amendments. ADRs: **ADR-037**; PREREGISTRATION amendments **R18/R19**.

### Block decomposition (B1–B14) — `docs/ARCHITECTURE_BLOCKS.md` (new)
- Precise decomposition of the prototype/project into 14 blocks (data, env/regimes, reward sandbox, LLM
  loop, measurement/H2, agent/training, search baselines, reward/strategy baselines, selection, inference,
  backtesting analytics, orchestration/compute, analysis/reporting, provenance/freeze), each with files,
  current state, a 1–5 gap rating, and a supervisor gap analysis. Guiding principle: **elevate
  engineering/analytics/benchmarking/rigor without corrupting the frozen H2 scientific contribution**
  (reporting more metrics/benchmarks is additive; changing arms/env/hypotheses is not).

### B11 — world-class backtest analytics suite — `src/backtest/` (new; 15 tests)
- `metrics.compute_metrics` reports ~30 **only-highly-relevant** metrics across return / risk-adjusted
  (Sharpe, Sortino, Calmar/MAR, Omega, Martin) / drawdown (max-DD + duration, Ulcer, pain, time-under-water)
  / tail (CVaR/ES, historical + Cornish-Fisher VaR, tail ratio, downside dev) / distribution (skew, excess
  kurtosis) / trading (turnover, cost drag) / benchmark-relative (IR, tracking error, beta, annualised
  alpha) / overfitting (PSR, deflated Sharpe) families. **Reuses the audited inference primitives**
  (`bootstrap.{sharpe_ratio,cvar}`, `deflated_sharpe.{probabilistic_sharpe_ratio,deflated_sharpe_ratio}`)
  — DRY, no re-derivation. `drawdown_series`, `regime_conditional_metrics`, `tearsheet_markdown`.
- Degenerate inputs are provably safe (empty / single / zero-variance / total-ruin); a **PSR signature
  bug** (silent broad-except swallow) was caught and fixed during testing (per-period Sharpe, raw kurtosis,
  n; no broad except). `regime_conditional_metrics` now **fails loud** on a returns/regimes length
  mismatch and masks non-finite returns + regime labels TOGETHER (was a silent truncation + misalignment).

### B8 — baseline canon expanded + a real correctness fix — `src/baselines/`
- **+5 published reward baselines** (`REWARD_CANON`, 9 total): mean–variance utility (Markowitz 1952),
  return−drawdown (Chekhlov-Uryasev-Zabarankin 2005), return−downside (Sortino 1991), return−turnover
  (Gârleanu-Pedersen 2013), log-growth (Kelly 1956 / Thorp 1971) — the "did the LLM beat hand-written
  reward CODE?" panel.
- **+4 published allocators** (`STRATEGY_CANON`, 9 total): minimum-variance (Clarke-de Silva-Thorley 2011),
  inverse-volatility, maximum-diversification (Choueifaty-Coignard 2008), cross-sectional momentum
  (Jegadeesh-Titman 1993).
- **`risk_parity` correctness fix.** The iterative `w·(target/rc)` update **divided by zero (→ NaN)** on a
  generic window AND converged to a CONCENTRATED non-risk-parity solution (max risk-contribution deviation
  0.91). Replaced with the **convex Spinu (2013) / Maillard-Roncalli-Teiletche (2010) log-barrier**
  formulation solved by L-BFGS-B (worst deviation now 1.5e-04). The benchmark floor's `WeightPolicy` no
  longer needs its 1/N fallback for risk_parity.

### Supervisor leakage/rigor audit (44 agents, 2-vote verification) → 15 confirmed findings
- **[HIGH, R18] Embargo (21) < feature lookback (60) → insufficient purge.** Each observation reads
  `returns[t-lookback:t]`, so a 21-session split gap left the downstream window's first 39 observations
  reading prior-split returns (López de Prado purge-insufficiency — exactly the "data-leakage" failure mode
  a strict examiner flags). **Fix:** the effective inter-split purge is now `max(embargo, lookback) = 60`
  at BOTH boundaries, in `resolve_windows` (campaign val+test) and `embargoed_val_start` (search val, new
  `lookback=` arg threaded from both callers). `test_embargo_splits` now asserts `gap ≥ lookback`
  (+ a new focused test). Recorded in §7 + both config comments.
- **[HIGH, R19] "SPY buy-and-hold" was an exact 1/N duplicate** mislabelled as the S&P 500 (no index/caps
  in the anonymized panel). **Fix:** honest relabelling, removed from the frozen gate (de-dupes the
  DeMiguel floor + fixes a best-benchmark double-count), suite EXPANDED to 8 distinct published allocators.
  A true SPX-TR/cap-weighted market benchmark is a documented **gated data addition**.
- `mean_variance` confirmed to correctly apply Ledoit-Wolf shrinkage (finding #9 is a prose name-drift only).
- Fixed two more findings: **DSR trial-count** config label reconciled to the per-arm count the code uses
  (`per_arm_candidates`; cross-arm multiplicity is handled separately by the m=6 family, so all-arms would
  double-correct); **VIX unit-detection** now reads only the first ~2 years (always TRAIN), never the
  sealed test span.
- **VIX-shift pipeline test added** (`data_pipeline/tests/test_features.py`, 5 tests). The
  `build_cash_features` docstring claimed two leakage invariances were unit-tested, but the cited test
  file did not exist — the leakage-critical gold VIX `shift(1)` + `rolling_vol_shifted` lag were
  UNVERIFIED. Now checked: VIX feature at row t reads the t-1 close (never t), rolling vol is strictly
  past, + truncation and future-perturbation invariances. Runs isolated (`make test-pipeline`; the
  data_pipeline `src` package shadows the engine's).
- **Runtime algo-equivalence check implemented** (`arms.factory.assert_fixed_agent_across_arms`, +3 tests).
  `trainer.py` referenced a "runtime equivalence test" that licenses the matched-compute H2/H4 comparison
  but it was never written. It now asserts (a) every arm shares one `candidate_budget`, (b) the resolved
  SB3-SAC kwargs depend on the SEED ALONE (same arch/lr/buffer/batch/gamma/device + train-step budget at
  two seeds, policy = `MlpPolicy`) — catching a future per-arm hyperparameter override, and (c) the LLM
  arms each carry a distinct `feedback_kind`.
- **Two doc-note findings closed**: `config/algos.yaml` now flags itself as DIRECTIONAL (the live agent
  hyperparameters are resolved by `resolve_agent_kwargs` from `prototype.yaml`/campaign cfg, not this
  file) and ties its `equivalence_test: true` to the implemented `assert_fixed_agent_across_arms`;
  `sharpe_ratio` documents the Lo-2002 autocorrelation caveat of `sqrt(252)` annualisation (a descriptive
  point-estimate convention — the headline H2 test uses the per-seed paired bootstrap over the per-period
  series, so it is unaffected). The only remaining audit item is the analyze() val+test subtree merge
  (MED#5), which needs the real campaign archive layout traced (deferred to a focused pass, not guessed).

### Deep targeted research (7 agents) + reference-data integration — the "gated" findings were NOT gated
- A deep-research sweep (metrics / benchmarks / leakage / hardware / literature / data-enrichment) **validated**
  the B11 metric set and the B8 baseline canon as exactly the referee-expected panels, and surfaced that the
  data I had called "gated" is **already pulled and frozen on disk**. New tested loader `src/data/
  market_reference.py` (+9 tests) exposes three portfolio-level REFERENCE series that live ENTIRELY in the
  reporting layer (zero env/anonymisation change, so H2 is untouched):
  - **risk-free rate** — FRED `DGS3MO` (3-month T-bill) from `data/raw/fred_macro.csv`, converted to a
    per-session decimal (the research's sanctioned path; preferred over the within-month-constant FF RF).
  - **real market line** — `market_ew` (full-universe EW return) from `data/gold/market_proxy_*.parquet`,
    a genuine market benchmark (≠ the 30-asset 1/N), now reported in `benchmark_floor` as an additive
    `market_reference` block (market Sharpe/CVaR/DSR + the winner's beta / annualised alpha / IR), NOT in
    the same-universe DeMiguel gate. (A true cap-weighted SPX-TR stays a documented minor limitation.)
  - **Fama-French factors** (Mkt-RF/SMB/HML + Momentum) for OOS factor attribution.
- `compute_metrics` generalised to accept a per-period rf **series** (a real bug caught while wiring: it did
  `float(risk_free)`); a series is reduced to its mean — exact for the Sharpe/Sortino numerator, negligible
  in the vol denominator for a daily T-bill. **Cornish-Fisher VaR removed** (research: non-monotonic /
  unreliable for fat tails; historical VaR + coherent CVaR/ES dominate) — keeping ONLY highly-relevant tail
  metrics. Throughput research flagged **SBX (SB3+JAX)** as the big SAC speed lever (gated on numerical-parity
  validation + an ADR) and concurrent multi-run packing on the 4090 as the safe win; the literature sweep
  confirmed the **publishable gap** (distributional reflection × reward-code search × portfolio RL is unoccupied).

## [2026-06-20] — Headline H2 inference corrected to per-seed rliable (#9/#14, R16), H2 conjunction wired (#18), test-universe limitation documented (#13, R17)

User mandate on the three flagged pre-registered-analysis items: "ultrathink, do whatever you think would
maximise my grade … work extensively and hard." The pre-registration is still `frozen: false`, so these are
pre-freeze design **corrections/clarifications** (legitimate, dated as amendments). ADRs: **ADR-036**;
PREREGISTRATION amendments **R16/R17**.

### #9/#14 — the headline H2 inference was anti-conservative; corrected to per-seed rliable (R16)
- **The bug.** `analyze_campaign._arm_test_returns` AVERAGED the 30 per-seed frozen-winner TEST return
  series per arm (a per-period mean over seeds) and fed that single denoised series to a single-strategy
  stationary block-bootstrap difference test. Averaging N i.i.d.-seed paths shrinks the tested object's
  variance ~N×, so the bootstrap SE was ~√N too small and the test **over-rejected a true null** — measured
  empirically at **≈21% at the 5% level on 30 seeds** (a real false-positive inflation the supervisor would
  catch as p-hacking-shaped).
- **The fix (rliable; Agarwal et al. 2021, the recognised RL-evaluation standard).** New
  `src/inference/bootstrap.py`: `iqm` (interquartile mean) + `paired_seed_difference_test` — each arm's
  PER-SEED Sharpe/CVaR scores → IQM point estimate → a **paired stratified bootstrap over the shared
  training SEEDS** (i.i.d. seed resample applied to both arms), carrying the across-seed (training-RNG)
  variance. It uses the SAME re-centred basic empirical-bootstrap p-convention (`|boot−obs|≥|obs|`) as the
  existing `sharpe_difference_test`, so `null_calibration` certifies it identically. **Null-calibrated:
  ≈5% true-null rejection (correctly sized) vs the old ≈21%; power 1.00 on a real edge.**
- `collect_family_pvalues`, `romano_wolf_joint` (now over per-seed score arrays with one shared SEED
  resample per replication), and `h2_conjunction` were rewired to the per-seed unit; the family (R13, m=6),
  BH/Romano-Wolf correction, directional conjunction gate, and SESOI/TOST (R12) are **unchanged** — only
  the resampling unit moved from time-blocks-on-a-seed-averaged-series to seeds-on-per-seed-scores. The
  valid series-level tests are retained for single-realization use. This realizes the already-frozen
  `config/preregistration.yaml: inference.seed_reporting = rliable_iqm_poi_stratified_ci` at the test.

### #18 — the H2 conjunction is now wired into the analysis entry point
- `collect_family_pvalues` / `h2_conjunction` / `assert_realized_family_matches_frozen` were implemented and
  unit-tested but had **no caller** in `analyze_campaign.analyze()` — so the documented headline H2 test
  never actually ran. `analyze()` now computes `h2_conjunction(records)` (firing the R13 family-equals-frozen
  assertion), `write_report` emits the H2 verdict + the per-seed family BH table (`h2_markdown`), and `main`
  prints the verdict.

### #13 — sealed test-leg universe limitation documented + PIT robustness building block (R17)
- The fixed 30-asset action space means SEARCH/SELECT and the sealed TEST share ONE universe — the
  development-phase point-in-time top-30 (selected 2005-01-03). The 2018-2025 test leg therefore trades the
  **2005 cohort** (a composition bias: **11/30 names differ** from the 2018 point-in-time top-30), accepted
  for train/test consistency and now **reported as a headline limitation** (loud caveat in `run_campaign`),
  not silently inherited. `load_gold_panel` gained a `window_start` argument so a PIT walk-forward universe
  (e.g. the verified 2018-01-02 top-30) can be loaded for a robustness re-evaluation of the frozen winners.
  Whether to elevate PIT to the headline or keep the consistent fixed cohort + this robustness check is a
  methodological design choice flagged for the supervisor (not a code defect).

### Verification
- Tests: `paired_seed_difference_test`/`iqm`; `test_campaign_inference.py` lifted to **multi-seed** (faithful
  to the 30-seed campaign); a null-calibration **proof** test (new ≈5% vs old over-rejection) and a
  PIT-universe loader test in `test_audit_regressions.py` / `test_loaders.py`. Full non-slow suite **410
  passed / 1 skipped**; `ruff` clean (src/scripts/tests); `mypy` 0-new; **`freeze.py --check` passes all
  prose↔yaml consistency** (canonical hash `7e6da01f → a1f458d5 → 5aaf1fc4` — the intended pre-freeze R16/R17
  refinements; `freeze_hash` still null, so no committed hash is violated). An independent re-audit of the
  inference rewrite + wiring was run.

## [2026-06-19] — Provider-neutral LLM architecture (Gemini prototype + Opus 4.8 campaign) + deep adversarial audit (38 findings fixed)

User mandate: "engineer everything … we will use gemini 3.5 flash for the prototype, and opus 4.8 for the
main … create a necessary architecture for that … very deeply search and find all bugs, all vulnerabilities,
all issues, all inconsistencies … fix everything … verify strictly and deeply." Scope boundary held per
CLAUDE.md §2: "advanced/sophisticated" = engineering quality (provider-neutrality, robustness, observability,
type-safety, test depth), NOT new scientific scope — the frozen pre-registration's 6 fields are untouched
(`freeze.py --check` canonical hash `7e6da01f…` unchanged throughout). ADR: **ADR-035**.

### Provider-neutral transport architecture (ADR-035)
- **`src/llm/client.py`** — new `build_transport(provider, model, api_key_env=None, *, temperature, max_tokens,
  max_retries)` single dispatch point over a provider registry: `anthropic` → the native Anthropic SDK
  transport; `openai` / `gemini` / `deepseek` → the OpenAI SDK pointed at each provider's `base_url`
  (`_OPENAI_COMPAT_BASE_URL`; Gemini = `https://generativelanguage.googleapis.com/v1beta/openai/`) — so a
  new provider is ONE registry entry, not a four-file edit, and **no new dependency** (Gemini rides the
  existing `openai` SDK). Added `default_key_env(provider)` (`_DEFAULT_KEY_ENV`) and `PROVIDERS`. New
  `_OpenAITransport` (callable, mirrors `_AnthropicTransport`): injected tenacity `retrying`, `temperature`
  sent only when set, `max_tokens` sent (final-audit #35), `last_usage` token capture for cost accounting.
- **Orchestrators** now call `build_transport` (DRY): `scripts/run_prototype.py::run_arm`,
  `src/orchestration/parallel.py::_drive_llm_arm`, and via the threaded `llm_cfg`, `scripts/run_campaign.py`.
- **Separate reward-authors per stage (the shared-config bug fixed).** `run_arm` gained an `llm_cfg` param;
  the campaign threads its OWN `llm` block (Claude **Opus 4.8**) down `run_campaign.main → run_headline_campaign
  → run_winner_search → run_arm`, so it no longer inherits the prototype's author. `config/prototype.yaml`
  → **Gemini 3.5 Flash** (`provider: gemini`, `GEMINI_API_KEY`, `pass: B`, `temperature: 1.0`);
  `config/campaign.yaml` → **Opus 4.8** (`temperature: null`, `diversity_prompt_variation: true`).
- **Temperature-free within-generation diversity.** `src/llm/loop.py::_diversity_directive(cidx, n)` appends a
  per-candidate exploration directive (uniform across arms → NOT an H2 confound) when
  `diversity_prompt_variation` is set — required because Opus 4.8 rejects the `temperature` parameter, while
  Gemini honors `temperature: 1.0`. Applied identically in the serial (`loop.py`) and parallel
  (`parallel.py`) paths; the exact prompt sent is archived (C-2).

### Deep adversarial audit — 8 dimensions × 3-vote verify (134 agents) → 38 confirmed findings, ALL fixed
A multi-agent workflow fanned adversarial auditors across correctness, sandbox security, inference math, the
data pipeline, orchestration/determinism, config consistency, the campaign protocol, and coverage gaps; each
finding was verified by 3 independent skeptics (≥2/3 to confirm). 42 raised → **38 confirmed** (3 critical,
9 high, 11 medium, 15 low), 0 under-verified. Every confirmed engineering finding is fixed and regression-tested.

**Critical**
- **#1 (reward extraction).** Raw LLM completions went straight to `ast.parse`; a markdown fence or prose
  preamble from Opus 4.8 (thinking off) / Gemini → `SyntaxError` → candidate rejected for FORMATTING, which
  at campaign scale could starve every arm (the stub returns bare code, so the fast suite never saw it).
  Added `src/sandbox/executor.py::extract_reward_source` (strip fences / prose preamble-epilogue; clean code
  is a byte-identical no-op), applied at the LLM boundary in `loop.py` + `parallel.py` (clean archive) and as
  a safety net atop `validate_once` (single choke point).
- **#2 (search RNG).** The sequential search arms (`run_arm`) called `random_search_over_code` /
  `bayes_opt_over_template` WITHOUT `rng=`, so `np.random.default_rng()` drew OS entropy (not the run seed) →
  non-reproducible winner selection. Now seeded `rng=np.random.default_rng(seed)`, mirroring the parallel path.
- **#3 (sandbox RCE).** The AST gate was a denylist; numpy's object graph reaches `os`/`builtins`/`pickle` via
  gate-legal submodule chains (e.g. `np._pytesttester.os.system(...)` — verified end-to-end RCE + env-var
  exfiltration). Replaced with an **allowlist** (`_ALLOWED_ATTRS`): every attribute must name a known-safe
  numeric/array/container op — sound because the dangerous leaves (`system`, `popen`, `environ`, …) are not
  numeric, so no chain can reach them. Also banned `ndarray.ctypes`/`.data` (FFI/pointer). Verified all
  known-good rewards (reward_family + 12 stub archetypes) still pass and the RCE vectors are blocked.

**High** — #4/5/8 matched compute (SEARCH selected at 25k but TEST evaluated at 50k): the campaign now builds
ONE agent_cfg and threads the SAME train_steps into both stages. #6 `run_prototype.py --dry-run` forces
keyless stub (it would otherwise hit real Gemini after the config flip). #7 gold VIX double-lag (pipeline
pre-shift + env lag → t-2): added `Panel.vix_prelagged`; the env lags only the contemporaneous (synthetic)
convention. #10/17 resume re-searched & re-froze a possibly-different winner while skipping its test seeds
(frozen/test desync): SEARCH+FREEZE are now resume-aware (load the existing frozen winner) + a frozen-source
hash guard. #11 the TEST stage never re-seeded per seed: added `set_global_seed` per seed. #12 the validation
fixture was 2-element: enlarged to realistic per-step shapes + documented that the in-process training path
is not a containment boundary.

**Medium** — #16/#36 the LLM provenance archive (raw response + token usage) was built then discarded: now
persisted to `llm_calls.jsonl` per arm (serial + parallel). #19 VIX-units (clarified: points is the canonical
LIVE unit; the conversion is deliberate, not a silent revert). #20 `ffill_then_zero` fabricated post-delisting
returns: now ffills interior gaps then zeros the dead tail. #21 the matched-budget guard passed at 100%
candidate failure: now requires ≥1 accepted candidate + persists `failures.jsonl`. #22/#33 candidate_id /
diversity-directive index diverged between paths: parallel uses the per-gen index `k`. #24 added the frozen-H2-
family fail-loud guard to `run_campaign` (PREREGISTRATION §10 prose now true). #34 unified the reflection
preamble across the serial/parallel paths.

**Low** — #15 stale docstring; #25 provider-aware key default on the parallel path; #26 honor `agent.device`;
#27 annotated dead config keys; #28 env guards `max(vol_windows) ≤ lookback`; #29 corrected dead stub-script
imports; #30 `winner_returns` ndarray-truthiness guard; #31 `deflated_sharpe` alias rejects `sr_benchmark`
loudly; #32 `winner_dsr` uses the full per-arm trial count; #35 OpenAI transport sends `max_tokens`; #37
`load_run` verifies env.json provenance; #38 removed the unfulfilled `prompt_hash` field.

**Flagged, NOT silently changed (pre-registered analysis plan — CLAUDE.md §3 requires user/supervisor sign-off):**
#9/#14 the headline H2 inference averages the per-seed return series before the bootstrap (anti-conservative,
~√N variance collapse); #18 the H2 conjunction / family-p-value functions are implemented + tested but not
wired into the analysis entry point; #13 the sealed-test leg reuses the fixed 2005-cohort universe across
2018-2025 (composition bias the prototype prose calls disqualifying). These are statistical-design decisions,
raised for the user rather than unilaterally rewritten.

### Verification
- **Tests:** +18 regression guards (`tests/test_audit_regressions.py`: extraction, RCE-blocked, vix-lag,
  vol-window guard, max_tokens, dsr alias, ndarray winner_returns) + the earlier +13 transport/diversity tests.
  Full non-slow suite **404 passed / 1 skipped, ×3 order-randomized (pytest-randomly)**.
- **Static:** `ruff check src/ scripts/ tests/` clean; `mypy src` at the 13-error pre-existing baseline (0 new);
  `freeze.py --check` canonical hash unchanged. (Pre-existing lint debt in `archive/` + generated `outputs/`
  artifacts is out of scope.) A pre-existing truncated `scripts/verify_inventory.py` (unrelated to the audit)
  was made syntactically valid with an honest deferred-stub.
- **Re-audit (two independent passes).** Pass 1 (verify-fix + regression-hunt, 33 agents) re-checked every
  critical/high fix and the changed files: 3 fixes clean, 8 "correct-but-incomplete" with mostly-cosmetic
  residuals, and — decisively — **2 HIGH regressions from the #7 vix fix itself**: `Panel.slice()` dropped
  `vix_prelagged` (a sliced gold panel reverted to the double-lag), and the terminal `step()` indexed
  `vix[panel.T]` out of bounds on a prelagged panel (**would have crashed the gold campaign's once-per-arm
  sealed evaluation on its final step** — invisible to the fake-based fast suite). Both fixed (slice
  propagates the flag; the vix index is clamped to the last row) + regression-tested. The real missed
  call-sites the residuals named were also closed: the parallel BO arm is now seeded (#2 parity) and the
  parallel `_summary`/`_drive_llm_arm` got the accepted>0 guard + `failures.jsonl` (#21 parity). Pass 2
  (16 agents, over the residual-fix files) verified **all five residual fixes correct AND complete** with no
  new regressions. It additionally flagged **2 PRE-EXISTING, headline-safe items** in `resolve_windows`
  (untouched by this work): on the 600-day SYNTHETIC dry-run panel — which cannot span the frozen 2018-2025
  test calendar — the clamped windows are rejected by the builder, so the dry-run smoke exercises
  search→select→freeze but not TEST, and a broad `except ValueError` mislabels that as `winner_not_testable`.
  The real 5,283-session gold path is verified unaffected (the headline windows resolve correctly). These are
  left as documented smoke-path limitations (modifying the windowing risks the frozen gold splits) — see the
  flagged items.
- **Final state:** full non-slow suite **407 passed / 1 skipped, 6 consecutive order-randomized runs**; +21
  regression guards total; `ruff` clean (src/scripts/tests); `mypy` 0-new; `freeze` hash unchanged.

## [2026-06-19] — Refinitiv access VERIFIED live + probe-tooling fixes + full run-readiness preparation

End-to-end run preparation at the user's request ("absolutely fully prepare everything for a run"), plus a
**material data-provenance correction** and two `data_pipeline` probe-tooling bug fixes. ADR: **IMPL-RUNPREP-1**.

### Data-provenance CORRECTION (the gold is Refinitiv, not yfinance)
- An earlier turn this session wrongly stated the gold panel was built from yfinance (over-reading the
  datasheet's vendor tags). **Corrected:** `data/gold/returns_panel_univ3.parquet` is the **licensed
  Refinitiv, survivorship-free, PIT** panel (`data_pipeline/README.md`): union **953 RICs incl. 333 dead**,
  PIT membership via reverse event replay through `TR.IndexJLConstituent*` (ADR-020), daily total returns
  via datagrid `Frq=D`, two-vendor reconciliation (corr 0.99994). The 333 dead tickers are dispositive —
  only a licensed survivorship-free vendor supplies delisted names' full history. yfinance is only the
  second reconciliation vendor; FRED supplies VIX, Ken French the factors. CLAUDE.md's "Refinitiv/LSEG"
  was correct; ADR-015's "empty scopes → yfinance fallback" was an interim 06-10 state, superseded when
  entitlements were fixed by 06-12 and the full Refinitiv PIT build ran. **Thesis/viva: claim
  Refinitiv/LSEG survivorship-free PIT** (yfinance as cross-check).

### Refinitiv entitlement VERIFIED LIVE (2026-06-19) — `univ4` unblocked
- The user's `.env` platform creds (`REFINITIV_{USERNAME,PASSWORD,APP_KEY}`) were tested two ways:
  (a) **direct** via `acquire.open_refinitiv_session()` (platform `GrantPassword`, headless — no Workspace):
  `OpenState.Opened`; live pricing (AAPL.O) PASS; **dead-ticker `LEH.N^I08` 2008 history PASS** (177 rows
  OHLC+volume through Lehman's collapse). (b) the **official probe** (`python -m src.data.cli probe`):
  **7 PASS** (P0 session, P1 chain, P2/P3 PIT membership content-validated incl. Lehman 2008 leaver, P5
  total-return continuity, P6 delisted coverage, P8 RDP scope census), P4 BLOCKED (DatastreamPy absent —
  DSWS path not used), P7 MANUAL. Verdict: ***"Pre-2016 membership path verified — proceed with the full
  PIT build."*** So `univ4` (apply the proper Shumway −30/−55% delisting returns vs the provisional
  `liquidate_to_cash` fill; likely a re-PROCESS of already-pulled delisting metadata, not a fresh re-pull)
  is now achievable. `docs/evidence/entitlement_report.md` + `entitlement_probes.json` regenerated.

### `data_pipeline` probe-tooling fixes (post-unification bugs)
- **`acquire.py::load_env`**: searched only `ROOT/.env` where `ROOT = data_pipeline/`; after the 06-17
  unification (ADR-022) the `.env` moved to the **parent** (unified repo root), so creds never loaded and
  `open_refinitiv_session` silently fell back to the **desktop proxy** (`localhost:9000`, which needs
  Workspace running). Fixed: search `ROOT/.env` then `ROOT.parent/.env`. `probes.py` `env_file` flag
  updated to match.
- **`probes.py::write_report`**: crashed with `UnicodeEncodeError` writing the `🚫` status icon under the
  user's `cp1251` (Russian) Windows locale. Fixed: `write_text(..., encoding="utf-8")` on both the report
  and the JSON sidecar.

### `.env` updated (user-directed)
- Wrote the pasted Refinitiv creds into the gitignored `.env` (merge: the three `REFINITIV_*` keys updated;
  `ANTHROPIC_API_KEY` preserved; `FRED_API_KEY` left as-is — the paste's was empty, FRED only needed for a
  VIX re-pull). Values never echoed; only NAMES + set/empty status printed. **Both pasted secrets (Refinitiv
  password, Anthropic key) are in the chat transcript → rotate after the project.**

### Run-readiness PROVEN on this laptop
- **Full non-slow suite: 373 passed / 1 skipped**, order-randomized (the `data_pipeline` edits don't touch
  the engine `src/`). **`freeze.py --check`: OK** (6/6 prose↔YAML fields consistent; canonical hash
  `7e6da01f…` unchanged; `freeze_hash: null` pre-freeze). **`run_prototype.py --dry-run`: EXIT 0** — 3 arms
  × 2 cand × 200 steps, real SAC train → measure → select → archive, winners produced, budget matched,
  18.3s. The end-to-end pipeline runs here; the full ~9.1 h prototype (`--parallel`, 240×25k @ ~183 steps/s
  on this RTX 4050) will work.
- **New: `docs/RUN_READINESS_2026-06-19.md`** — the operational runbook: status board, the two-pass model,
  exact run commands + timings + monitoring + resume + success criteria for prototype → (Pass-B smoke) →
  pilot → freeze → univ4 → campaign → analysis, plus the gated hand-off checklist and security note.

## [2026-06-19] — Run-readiness wiring: real Anthropic Pass-B + the vix-units fix (closes ADR-034 "Wiring queued")

Completes the ADR-034 §"Wiring (queued)" items so the headline campaign can actually run the real
reward-author (Claude Sonnet 4.6) instead of the keyless stub, and fixes a silent regime-collapse bug.
ADR: **IMPL-WIRING-1** (docs/DECISION_LOG.md). **Full non-slow suite: 373 passed / 1 skipped**, order-
randomized (pytest-randomly); +21 over the prior 352 (20 provider/transport tests + 1 gold-vix regression).
**The freeze hash is UNCHANGED** — none of `PREREGISTRATION.md` / `config/preregistration.yaml` is touched.

### THE CRITICAL FIX — the headline campaign could not call the real LLM at all
- **`scripts/run_campaign.py::main` was HARDCODED to the keyless stub.** It never read `provider`/`pass`,
  so the call to `run_headline_campaign(...)` fell through to the signature defaults `pass_mode="A",
  provider="stub"`, and `generations` was pinned to `1`. The script whose numbers enter the dissertation
  would have silently run the StubDesignerTransport (not Sonnet 4.6) on every invocation. Fixed: `main`
  now reads `config/campaign.yaml: llm` → `pass` / `provider` / `generations` and threads them through.
  `--dry-run` still forces the stub (`A`/`stub`/`1`) so the smoke path never burns the API key. The run
  banner now prints `gens=… pass=… provider=…` so the active mode is visible in every log.

### THE MAJOR CATCH — temperature stays 1.0 (Eureka), NOT 0
- My continuation summary asserted "set temperature=0". **That is wrong and would have gutted the
  experiment.** `src/llm/loop.py` samples all `candidates_per_gen` candidates per generation from the
  *identical* `system`+`user` prompt (loop.py:292-296) — within-generation diversity comes ENTIRELY from
  sampling stochasticity, so temperature MUST be > 0 (ADR-016 sets 1.0 per Eureka). ADR-033's "Sonnet 4.6
  honors `temperature=0`" is a provider-*selection* criterion and explicitly notes "reproducibility comes
  from the archive (replay), not live determinism" — it is NOT an instruction to run at 0. Verdict
  (reconcile-don't-assume, CLAUDE.md directive 1): **temperature = 1.0 everywhere**; transports leave it
  unset → provider default unless config says otherwise; the configs record 1.0 with the rationale inline.

### Provider transports + client — `src/llm/client.py` (ADR-033/034 hardening)
- **`make_anthropic_transport` now wires the full ADR-034 queue**: (a) **prompt-caches** the static system
  block (`system=[{type:text, text, cache_control:{type:ephemeral}}]`) — the K-shared-context cache lever
  (ADR-016); (b) **owns retry/backoff** via lazy `tenacity` (exponential 1→30 s, ≤6 attempts) on a
  PORTABLE transient predicate `_is_transient_api_error` (connection/timeout/rate-limit/5xx by class-name +
  HTTP status; 4xx is terminal) while the SDK's own `max_retries` is set to **0** so tenacity is the single
  observable policy; (c) **archives token `usage`** (input/output + cache write/read) via a small callable
  `_AnthropicTransport` exposing `last_usage`; (d) accepts `temperature` (passed only when set). tenacity
  is imported lazily and **degrades to no-retry if absent**, so the deterministic core still imports without
  it (same discipline as the lazy `anthropic` import).
- **`make_openai_transport`** gains a symmetric `temperature` kwarg (used only for the N3/DeepSeek-V4 check
  model, ADR-033).
- **`ProvenanceRecord`** gains an optional `usage: dict | None` field (default `None`); `LLMClient.complete`
  reads `getattr(transport, "last_usage", None)` and archives it (audit C-2 + cost accounting). Transports
  without usage (FakeTransport) archive `None` — no error.
- **`LLMClient` is now provider-aware** (closes the latent OpenAI-default footgun the audit flagged): reads
  `cfg.provider` (default **`anthropic`**), defaults `api_key_env` to `ANTHROPIC_API_KEY` for anthropic else
  `OPENAI_API_KEY`, threads `cfg.temperature`, and dispatches `_ensure_transport` to the matching
  `make_*_transport` (`anthropic` | `openai`/`deepseek`; unknown → clear RuntimeError). Both orchestrators
  always INJECT a transport, so this only governs non-injecting callers — but it makes the standalone client
  honest and matches the project decision. Module + class docstrings updated (no longer claim OpenAI-default).

### Orchestrator threading — model/key/temperature now flow to the transport
- **`scripts/run_prototype.py::run_arm`** (the shared search worker reused by BOTH prototype and campaign):
  reads `temperature` from the `llm` block and passes it to `make(model, key, temperature=…)`; the
  `api_key_env` default flips `LLM_API_KEY` → `ANTHROPIC_API_KEY`. The parallel-path opts dict in
  `run_prototype.main` now carries `temperature` (same default flip).
- **`src/orchestration/parallel.py::_drive_llm_arm`**: reads `opts["temperature"]` and passes it through.

### Configs reconciled to ADR-016/033 (were stale placeholders)
- **`config/prototype.yaml: llm`** (the SHARED reward-author config `run_arm` reads for prototype AND
  campaign): `model_snapshot "<pinned-when-Pass-B>"` → **`claude-sonnet-4-6`**; `api_key_env LLM_API_KEY` →
  **`ANTHROPIC_API_KEY`**; **added `temperature: 1.0`** with the Eureka-diversity rationale + a DO-NOT-set-0
  warning. `pass:A`/`provider:stub` kept (the prototype is directional/keyless by default).
- **`config/campaign.yaml`** — **added the missing `llm` block** (the campaign had none): `pass: B`,
  `provider: anthropic`, `generations: 6` (= 6×5 = the 30-candidate budget; the H3 single-shot control runs
  the same budget at `generations:1`). Documents that model/key/temperature are the shared prototype values.
- **`config/llm.yaml`** — reconciled the stale reference: `provider: anthropic` (new), `model_snapshot
  claude-sonnet-4-6`, key-name `api_key_env_var → api_key_env: ANTHROPIC_API_KEY`, `temperature: 1.0` (kept;
  comment corrected — it is Eureka diversity, not "freeze in Phase 1"), and the `open_weights_check_model`
  placeholder replaced with an HONEST `PIN_ME` + ADR-033 note (Llama-4 N3 control; exact HF commit pinned at
  use — no fabricated revision, CLAUDE.md directive 4). The temperature 1.0 there was NOT a bug (it matches
  Eureka); only the model/key/`<placeholder>` strings were stale.
- **`pyproject.toml`**: `tenacity>=8.2` added (LLM-transport backoff; SDK `max_retries=0`).

### Tests
- **`tests/test_llm_transport.py` (NEW, 16):** drive `_AnthropicTransport` with a FAKE SDK client (no
  `anthropic`/`tenacity` install needed) — prompt-cache content-block shape, `cache_system=False` → plain
  string, text-block concatenation, temperature passed-when-set / omitted-when-None, `last_usage` capture,
  `_usage_dict` None-handling, the transient/terminal classification (5 transient classes + 5xx-vs-4xx +
  ValueError), an injected-retrying wrapper actually retrying, `_make_retrying(0)→None`, and the no-key raise.
- **`tests/test_agents.py`:** replaced the OpenAI-default assumption with provider-aware tests — default
  provider is anthropic + `ANTHROPIC_API_KEY`; explicit `openai` provider routes to the OpenAI transport;
  unknown provider raises; `complete` archives transport `usage` (and `None` for a plain transport).

### vix-units bug — gold regime stratification was silently collapsed (audit B-6)
- **Root cause (verified against the frozen gold, not assumed):** `data/gold/cash_features_*.parquet` store
  vix as a FRACTION (FRED VIXCLS / 100 — min 0.0914, median 0.1672, max 0.8269 over 2005-2025), but
  `config/regimes.yaml` thresholds are conventional POINTS (calm<15 / stress>25). Every one of 5,282 gold
  dates is < 15 → ALL labelled calm → `independent_regime_count` = **1**, silently zeroing the regime-
  stratified evaluation that bounds H2 power. The env obs is scale-agnostic (uses `panel.vix[t-1]` raw under
  VecNormalize, `portfolio_env.py:326`), so the bug touched ONLY regime labelling.
- **Fix — `src/data/loaders.py::load_gold_panel`:** normalize vix to points at the load boundary, magnitude-
  GUARDED (`if median(vix) < 2.0: vix *= 100`) so the current fractional gold is rescaled (~9.9..80.9) while a
  future points-storing rebuild is never double-scaled. Chosen over flipping the thresholds to decimal because
  it keeps the WHOLE system in one conventional, viva-defensible unit (the thresholds, the synthetic panel
  ~10-50, the trainer's documented ~10-80 obs range, and the env doc "FRED VIXCLS" were all already points —
  only the frozen gold was fractional). The frozen parquet is untouched (transform on read).
- **Result:** gold vix → points (median 17.0, max 80.9); regimes now 955 calm / 1071 normal / 491 stress with
  **214 independent episodes** (was 1). `config/regimes.yaml` annotated with the convention + loader
  dependency. **`tests/test_loaders.py`:** new regression loads the real gold, asserts vix is in points
  (min>1, median>5, max>25) and that all three regimes + >1 episode realise — the collapse cannot recur.

### Status — what this does and does NOT unblock
- **Unblocked (ungated, done here):** the campaign/prototype can now invoke the real Sonnet 4.6 Pass-B path
  (set the staged `ANTHROPIC_API_KEY` in the gitignored `.env`); regime-stratified analysis is meaningful.
- **Still gated on the user / GPU box (unchanged):** `make freeze`; the univ4 Refinitiv rebuild; the
  `requirements.lock` on the 4090 (must `pip install` the now-declared `tenacity`); the pilot → `power_analysis
  --sigma-dsr`; the campaign run itself. The live key pasted in chat remains the user's to manage per ADR-033.

## [2026-06-19] — Keystone Rank 7: reward forensics (§6.1 "open the black box", H2 interpretability)
- **`scripts/inspect_rewards.py` — implemented (was a STUB) + `tests/test_inspect_rewards.py` (NEW).** Replaced the
  `raise SystemExit('STUB')` and deleted the two dead imports (`from src.io.results import ResultStore`, `from
  src.feedback import distributional` — results.py has no `ResultStore`; the feedback code is `measurement.py`/
  `schema.py`). The tool produces the §6.1 GREEN-gate QUALITATIVE evidence that the LLM reward-designer *used* the
  distributional feedback (H2), not merely that a metric gap exists.
- Three analyses, **read-only** on the archive (audit C-1, via `load_all`), **reusing** `analyze_results.{load_arms,
  interpretability, _TAIL_TERMS}` (no duplication): `per_generation_summary` (per-arm-per-gen best/mean fitness +
  reward-code size/complexity + tail-term-usage trend); `feedback_responsiveness` (per-arm Pearson correlation of
  successive reward-source EDIT magnitude vs the L1 tail-stat DELTA the LLM was fed — the "did it use the information"
  core; finite, `None` for scalar/placebo which carry no tail); `hacking_taxonomy` (specification_gaming / proxy_no_tail
  / tautology via the `_TAIL_TERMS` lens + collapsed OOS fitness; Skalse 2022, Hadfield-Menell 2017). Emits
  `reward_forensics.md` + `.json` into `--out-dir` only.
- Tests: 12 fast/no-torch — keying by (arm, generation); a FINITE responsiveness score DISTINGUISHING a constructed
  responsive (+0.92) vs unresponsive (−0.98) fixture; a flagged gaming example; markdown emitted to a tmp dir; an
  end-to-end `inspect()` over written archives that asserts the archive is untouched. **Suite: 261 passed / 1 skipped**
  (+12). Ruff clean. ADR: IMPL-INSPECT-1.

## [2026-06-19] — Final acceptance audit (6-auditor workflow) + 3 P1 fixes
- **Ran a final adversarial acceptance-audit workflow** (6 read-only auditors over the completed codebase —
  integration, inference-math, frozen-prereg/freeze, sandbox+data, docs-vs-code, completeness; findings adversarially
  verified). Verdict: **3 confirmed P1 defects** in implemented code (the gated items correctly NOT flagged). All fixed +
  regression-tested:
- **P1-1 — `winner_dsr` 252× units bug (`scripts/analyze_campaign.py`):** the canonical headline DSR deflated the
  winner's PER-PERIOD Sharpe by a `var_sr` computed from ANNUALIZED candidate Sharpes (`sharpe_ratio` default
  `periods_per_year=252`), so `sr_star = sqrt(var_sr)·term` was ~15.87× too large → `dsr_canonical` collapsed spuriously
  to ~0. Fixed: compute the cross-candidate `var_sr` with `periods_per_year=1` (per-period, matching
  `deflated_sharpe_ratio`'s annualization-invariant convention); `winner_sharpe` stays annualized-for-display (labelled).
  R16's test hand-computed `var_sr` and bypassed `winner_dsr`'s internal call — so a new regression test invokes
  `winner_dsr` DIRECTLY and asserts `var_sr` is per-period (not ~252×) + the DSR is non-collapsed.
- **P1-2 — sandbox file-READ escape (`src/sandbox/executor.py`):** `np.recfromtxt`/`np.recfromcsv` (genfromtxt aliases)
  + `np.fromregex` (file-first read) slipped the AST gate → added to `_BANNED_ATTRS` + 3 denial tests.
- **P1-3 — sandbox file-WRITE escape:** `ndarray.dump(path)`/`.dumps()` pickle to an arbitrary path (the tofile hole,
  reopened) → added `dump`/`dumps` to `_BANNED_ATTRS` + 2 denial tests.
- **Full suite: 352 passed / 1 skipped** (+6). The freeze hash is **UNCHANGED** (code/test fixes; `PREREGISTRATION.md` +
  `config/preregistration.yaml` — the hashed artifacts — untouched). ADR: IMPL-AUDITFIX-1. **Residual P3 (noted):**
  `scripts/build_gold.py`/`verify_gold.py` are deferred-by-design stubs not yet labelled "deferred" — doc polish, not a
  defect. **Auditors' hardening rec (future ADR):** replace the numpy denylist with a positive allowlist of pure-array
  ops (the "forgot to ban X" class recurs); `RLIMIT_FSIZE`/namespace is the backstop.

## [2026-06-19] — Rank 9: pre-registration freeze gate (`scripts/freeze.py`)
- **Implemented `scripts/freeze.py`** (was a `SystemExit` stub): **canonical hash** = SHA-256 over the LF-normalized
  UTF-8 bytes of `PREREGISTRATION.md` ++ `config/preregistration.yaml` (fixed order: prose then yaml, `\n`-joined;
  BOM/CRLF-invariant). The **prose↔YAML consistency GATE** checks all 6 freeze-relevant fields (seeds=30,
  `inference.testing_family.m`=6 == len(members), `difference_tests`, `sesoi`=0.05, `equivalence_margin`=0.05,
  `cost_sweep.grid_bps`) — comparing the NUMBER parsed from the prose to the YAML value, so a silent drift fires.
- **Phase-0 precondition:** refuses unless `phase0_smoke_passed_log_id` is set. **`--check` mode** re-runs the hash +
  all assertions WITHOUT writing (exit non-zero on drift), wired as `make freeze-check` for CI.
- **Write path (implemented, USER-GATED — NOT executed):** `do_freeze` flips `frozen:`/`freeze_hash:` via a line-level
  edit (preserves every comment + amendment), appends a dated `FREEZE-DONE` entry (hash + UTC + git SHA) to the ADR-005
  slot in `docs/DECISION_LOG.md`, creates a signed tag `prereg-v1.0` (best-effort → annotated fallback), and `ots
  stamp`s the hash (best-effort → skip if absent); the recorded hash is the PRE-flip content (= what `--check`
  re-derives). Refuses if already frozen.
- **`--check` PASSES on the current consistent prereg** (exit 0; Phase-0 met; all 6 fields OK). Deterministic canonical
  hash (3 runs): **`7e6da01f…e41d6`** (informational — the recorded value once `make freeze` runs, absent further
  amendments). **Tests:** `tests/test_freeze.py` (19) — gate raises on each deliberate mismatch; hash deterministic +
  order/content-sensitive + LF-invariant; `--check` mutates nothing. **Full suite: 346 passed / 1 skipped** (mypy + ruff
  clean). ADR: IMPL-FREEZE-1. **The real `make freeze` is the user's gated action — NOT run.**

## [2026-06-19] — Wave-3 freeze-prep: pre-registration amendments D2/R11/R12/R13/R15 (ADR-034)
- **PREREGISTRATION.md (dated amendments only; FROZEN doc):** §6+§12 **Amendment D2** (user-approved) — winner seed count
  **5→30** (search budget untouched; seeds-on-winners); §10 **R13** the multiple-testing family ENUMERATED + FROZEN at
  **m = 6** (`{arm-contrast × {Sharpe, CVaR-0.05}}`, incl. the 3 H2-conjunction legs; BH q=0.05 primary, joint
  Romano-Wolf the FWER alternative; Harvey-Liu t>3 scoped to absolute-alpha only); §10 **R11** Sharpe-test relabel
  (studentized-LW → re-centred basic stationary block-bootstrap, numerics unchanged); §10 **R15** pre-registered
  cost-robustness sweep; §10 **R12** SESOI=0.05 + TOST ±0.05 DSR. New **Amendment record** table + Freeze-record row.
- **config/preregistration.yaml (machine-readable mirror):** `seeds:[0..29]`; `difference_tests:
  [sharpe_recentred_bootstrap, cvar_difference]`; new `inference.testing_family` (m:6 + 6 members) +
  `multiple_testing_primary/q` + `alpha_hurdle_scope`; `inference.{sesoi,equivalence_margin}=0.05`; top-level
  `cost_sweep`. **Prose↔YAML verified consistent on all 6 freeze-relevant fields.**
- **config/campaign.yaml + config/inference.yaml:** headline seeds → `[0..29]` (ablation `[0,1,2]` untouched).
  **docs/COMPUTE_AND_TRAINING_TIME.md:** run-count/GPU-hour bands recomputed as winners×30 (lean ≈600 runs ≈110 GPU-hr
  ≈ $32-44 / ~4.6 days on a rented 4090; full 30×5 grid retained as the costed alternative).
- **scripts/analyze_campaign.py:** added `assert_realized_family_matches_frozen` (# fail-loud) wired into
  `collect_family_pvalues` — asserts the realized {contrast×metric×level} family == the frozen `inference.testing_family`
  (no-op on a missing-arm subset or the opt-in cvar_01 superset).
- **docs/POWER_ANALYSIS.md** SESOI reconciled 0.200→0.05. **Suite: 327 passed / 1 skipped; ruff clean.** **ADR-034**
  (supersedes the PENDING frozen-doc amendment notes in IMPL-BOOT-1 / IMPL-COSTSWEEP-1 / IMPL-POWER-1 — now applied).
  The amended design is internally consistent and ready for `freeze.py` (Rank 9) to hash.

## [2026-06-19] — Rank 5: univ4 Shumway-STYLE delisting build (CODE; parquet GATED on Refinitiv)
- **`membership.apply_shumway_corrections` — KeyError landmine FIXED + direct tests (had none).** The surcharge booked
  onto the all-NaN nominal-delist row via `out.loc[date,name]=value` — KeyErroring off-grid (the `^MYY` delist date
  often is) or planting a phantom row `liquidate_to_cash` then zero-filled (so the crash return never reached the tail).
  Now books on the **LAST VALID session** (`_last_valid_label`), compounded **MULTIPLICATIVELY** `(1+r)(1+dl)−1` (never
  additive; OpenSourceAP #49); all-NaN names → `shumway_skipped_no_obs`; vendor-terminal preferred (kept). Audit log
  gains `booked_on`/`delisting_return`/`prior_return`.
- **`build_universe(apply_delisting=False)` wires STAGE 7** between the clean freeze and `build_gold`: derives the delist
  map (`_derive_delisting_map`, reusing `parse_delisting_metadata` over `rf_meta_*` + `^MYY`/exchange-code fallback),
  feeds the CORRECTED frame to gold, freezes `clean_returns_shumway`/`shumway_audit_log`. **Default off → `_univ`
  byte-identical.** GATED: the real `_univ4` parquet needs the data_pipeline re-run + Refinitiv creds.
- **`loaders.gold_suffix()`** — `LLM_RP_GOLD_SUFFIX` switches the gold suffix (default `univ3`, **NOT** flipped to univ4).
- **`tests/test_membership_shumway.py` (NEW, 13)** incl. **TAIL-PRESERVATION:** corrected synthetic CVaR_05 strictly
  more negative than `liquidate_to_cash` (gap > 1e-4 — the surcharges, not float noise). **Suite: 327 passed / 1
  skipped.** Ruff clean. ADR: IMPL-UNIV4-1. ⚠ **Headline tail numbers remain invalid until the gated `univ4` rebuild +
  env reload** (`LLM_RP_GOLD_SUFFIX=univ4`); report the {0%, −30%, −55%, −100%} sensitivity band then.

## [2026-06-19] — Rank 14: reproducibility/provenance trio (replayable archive + CI-grade env)
- **`scripts/capture_env.py` (NEW):** EXTENDS `provenance.env_fingerprint()` with `pip_freeze` (importlib.metadata),
  `nvidia-smi` driver (best-effort), `torch.version.cuda` + cuDNN + `are_deterministic_algorithms_enabled()`, the run
  seed, an `os.environ` snapshot (CUBLAS_WORKSPACE_CONFIG/PYTHONHASHSEED/CUDA_VISIBLE_DEVICES); writes
  `outputs/<run>/env.json` (`capture_env`/`env_json_sha256`/`write_env_json` API + CLI). Wired into the orchestration
  archive (`parallel.py`) + the sequential path (`run_prototype.py`) so every run dir gets one; the bare-string
  `env_fingerprint` (e.g. `'synthetic:steps200'`) is now `{label, env_json_sha256}` pointing at the content-hashed
  snapshot (audit C-2/C-6).
- **Persisted the rendered prompt (CLAUDE.md §6 "archive every prompt"):** added `'prompt'` to the LLM-loop + parallel
  candidate records; `results.write_run` dumps a `prompt.txt` sidecar next to `reward.py` and `load_run` reattaches it;
  `'prompt'`/`'prompt_hash'` added to `OPTIONAL_FIELDS` (REQUIRED_FIELDS unchanged → round-trip tests green). Closes the
  replay-archive gap — results now REPLAY with the exact prompt.
- **Makefile + pin:** added a gated `.PHONY lock` target (`uv pip compile --all-extras --generate-hashes`, pip-freeze
  fallback) — the lockfile itself MUST be generated on the Linux RTX-4090 box (cu124 wheels) → FLAGGED gated; pinned
  `pytest-randomly>=3.15,<5` (was declared but missing from the venv → the determinism guard can't silently disappear).
  Tests green. ADR: IMPL-REPRO-1.

## [2026-06-19] — Rank 12: power-analysis machinery (`scripts/power_analysis.py`)
- **Implemented `scripts/power_analysis.py`** (was a stub with a broken `from src.regimes import detect`): fixed the
  import to `src.regimes.definition.independent_regime_count`; added a **vectorized Monte-Carlo power routine** over the
  arm-level re-centred bootstrap difference test (faithfully reusing `bootstrap.sharpe_difference_test`'s SE-cancels
  rule), a **selection-aware (Šidák) α penalty**, **MDE** location at 80% power, and a **symmetric-margin TOST**
  equivalence test. σ (seed-to-seed validation-DSR sigma), SESOI, and the TOST margin are CLI parameters with flagged
  placeholder defaults; the inner bootstrap loops are vectorized (~5 s full run).
- **Filled `docs/POWER_ANALYSIS.md`** (every `___`): N=6, n_eff=30, `alpha_eff=0.0085` (m=6 Šidák), **MDE = 0.269 DSR
  (0.90σ)** at the placeholder σ, **trial count = 180** (6 arms × 30), SESOI + TOST recorded. **σ and the MDE are
  flagged pilot-TBD** — re-run `--sigma-dsr <pilot>` to finalise before the freeze.
- **Tests:** `tests/test_power_analysis.py` (14 fast) — import resolves; N sane; power ∈ [0,1] with correct monotonicity
  in effect/σ/N/seeds; null rejection ≈ α_eff; TOST flags equivalence/non-equivalence correctly. **327 passed / 1
  skipped.** ADR: IMPL-POWER-1.
- ⚠ **DATA-INTEGRITY FLAG (recorded; fix before the campaign — NOT a frozen-prereg item):** the gold panel's `vix` is
  stored as a **decimal** (~0.10-0.81) but `config/regimes.yaml` thresholds are **VIX points** (calm=15/stress=25), so
  regime auto-detection collapses every date to ONE regime. The agent added a `--n-regimes` override (default 6,
  literature-grounded) + surfaced the mismatch; the real fix is to rescale the gold `vix` to points OR set
  `regimes.yaml` to decimal thresholds (calm=0.15/stress=0.25).
- **PENDING (frozen-doc amendment, the Wave-3 pass):** the adopted **SESOI = 0.05 DSR + TOST margin ±0.05** for the H2
  contrast → PREREGISTRATION.md §10 + `config/preregistration.yaml inference:{sesoi, equivalence_margin}` (exact text in
  IMPL-POWER-1).

## [2026-06-19] — Rank 2c: bayes_opt archives a materialized executable reward_source (H4 held-out fix) — COMPLETE
- `src/baselines/reward_family.py`: added `params_to_source(coeffs, cvar_alpha, window) -> str` (additive; in `__all__`),
  a sibling of `params_to_reward` emitting the six-term H4 family at `coeffs` as runnable `def reward(...)` source
  (coefficients/alpha/window baked in via `repr`; body a verbatim transcription of the closure). Passes the AST gate +
  `validate_once`; reproduces `params_to_reward` **bit-for-bit** (max abs diff 0.0 over a 60-step stateful replay).
- **Wired into both archivers (orchestrator did the 2-site swap):** `scripts/run_prototype.py` (the sequential BO
  branch) and `src/orchestration/parallel.py` (the `kind=="coeffs"` worker) now archive `params_to_source(coeffs,
  cvar_alpha=alpha, window=window)` as `reward_source` instead of the non-executable `# coeffs=[...]` comment stub.
- **Why:** the BO arm (H4b) only held an in-memory closure; the stub left its frozen winner non-rehydratable for the
  sealed TEST leg (`_reinstantiate_frozen_winner → validate_once → winner_not_testable`), BREAKING the H4 LLM-vs-search
  held-out comparison. The BO winner now round-trips through the IDENTICAL test path as the LLM / random-search arms.
- **Tests:** `tests/test_reward_family_source.py` (11) — executable/gate/validate_once + ~1e-12 reproduction (incl. a
  real `bayes_opt_over_template` winner) + `_reinstantiate_frozen_winner` rehydrates a materialized BO winner (no
  `winner_not_testable`); the legacy stub still raises. Targeted search/family/campaign suite green. ADR: IMPL-BAYESSRC-1.

## [2026-06-19] — Rank 18: embargo at executed split boundaries + low-risk cleanups
- **Embargo (PREREGISTRATION §7):** `run_prototype._load_panel_and_windows` + `parallel._panel_and_windows` no longer
  abut train/val. New `loaders.embargoed_val_start` reads the **materialized** `development.validation_post_embargo`
  boundary from `data/gold/splits_univ3.parquet` (val → **2015-02-03**, byte-matching the freeze; 21-trading-day purge),
  with a 21-session fallback. Verified on real gold (val_start `2015-01-02 → 2015-02-03`, 21 purged sessions).
  (+`tests/test_embargo_splits.py`, 7 tests incl. real-gold e2e.) **Also closes the Rank-2 window-byte-match flag.**
- `fitness.held_out_fitness`: CVaR penalty guarded (`lam*abs(c) if isfinite else 0.0`) — no NaN propagation on empty /
  all-non-finite series; the `var_sr` kwarg (R16) preserved. `sandbox/executor.py`: removed the shadowed duplicate
  `candidate_failed`/`reset_failure_flag` (kept the live P0-2 pair). `run_prototype`: `set_global_seed(
  deterministic_torch=True)` parity. `loaders` checksum: `parents[1]→parents[2]` so the exact-relpath manifest branch
  fires (was basename-only). Added **`CITATION.cff`** (cff 1.2.0, Atesyakar/UCL, MIT) + **`DEVIATIONS.md`** (append-only
  post-freeze deviation log). **Tests: 302 passed / 1 skipped.** ADR: IMPL-CLEANUP-1.

## [2026-06-19] — Rank 17: IQN-era doc/code reconciliation + stale pre-merge quarantine
- **Quarantined the freeze hazard:** `git mv docs/staging/{PREREGISTRATION_v1.0_FINAL,FREEZE_RUNBOOK}.md →
  archive/pre_merge_repo_B/staging/` (+ README). The old runbook's `cp …_v1.0_FINAL.md PREREGISTRATION.md` would have
  CLOBBERED the canonical root pre-registration with the abandoned IQN draft at freeze. Left a corrected
  `docs/FREEZE_RUNBOOK.md` that freezes the canonical root `PREREGISTRATION.md` **in place** (no `cp`) and calls the real
  Makefile target **`make freeze`** (the old runbook called the nonexistent `freeze-design`).
- **Reconciled the distributional-feedback docs to the off-critic empirical+EVT reality:** rewrote
  `docs/distributional_feedback_schema.md` (impl path → `src/feedback/measurement.py`+`schema.py`, was the wrong
  `src/feedback_schema.py`; dropped the IQN-critic `Z(s₀,a₀)` sourcing + the frozen-DROPPED
  `crossing_rate`/`left_tail_slope`/`bowley_skew`/`moment_skew`/`n_quantiles`/`source`; field list = the frozen six;
  removed the false "Verified as-built 2026-06-10" line; kept the Kusuoka/Acerbi theory).
- **Archived the 5 inert IQN-era B-set prompts** (`*_v0.md` + `safety_instruction`) → `archive/pre_merge_repo_B/prompts/`
  — confirmed INERT (`src/llm/prompts.py::build_prompt_set` loads ONLY the live A-set `system.txt`/
  `initial_generation.txt`/`reflection.txt`; no code path loads any `*_v0.md`). They asserted the IQN sourcing + a wrong
  `compute_reward(ctx)` contract. Updated `prompts/README.md`, `config/eureka_loop.yaml` comments, root README.
- **Compute provenance:** `config/campaign.yaml` compute → `primary: rtx_4050` / `campaign: rented_rtx_4090` (was
  `rtx_4090`/`ucl_myriad_array_job` — NO Myriad access, ADR-023); README Phase-0 smoke → owned RTX **4050**; SUPERSEDED
  headers on the three IQN-SAC reports. **Seed counts untouched (R10's domain).** Engine tests: **291 passed / 1
  skipped**. ADR: IMPL-DOCSYNC-1. Companion fix: `docs/DECISION_LOG.md` DATA-REAL-1 corrected CRSP-via-WRDS →
  Refinitiv/LSEG (the live source).

## [2026-06-19] — Correctness + robustness wave (punch-list Ranks 11, 15, 16)

### Rank 11 — bootstrap difference tests documented accurately (+ `arch` cross-check oracle)
- **Dropped the "studentized (Ledoit-Wolf 2008)" framing** from `src/inference/bootstrap.py`
  (`sharpe_difference_test`, `cvar_difference_test`, module docstring) + `src/inference/es_backtest.py`. **VERIFIED
  against the code** that the bootstrap SE *cancels* in the two-sided p-value: `stat = obs/se`, `centred = (boot−obs)/se`,
  and `|centred| ≥ |stat| ⇔ |boot−obs| ≥ |obs|` — se-free. So the tests are a **re-centred basic (empirical) stationary
  block bootstrap** whose size is certified by `null_calibration` (audit C-7), NOT studentized. Labels/docs only — no
  test numerics changed (the `stat` field is still `obs/se`, a studentized point summary, but it does not drive the
  decision).
- **Reconciled `config/inference.yaml`** `sharpe_test`: it described `circular_block / block_size 5 / n_boot 4999` but
  the code is stationary `p=0.1 / n_boot 2000`. Fixed the YAML to faithfully describe the code (the lower-risk option —
  no `src/` caller reads `sharpe_test` from config, so threading config in would be a behaviour change), with a
  provenance comment naming `bootstrap.py` as the source of truth; removed the stale `crossing_rate` mention (ADR-022).
- **Wired the `arch` cross-check oracle** in `tests/test_inference_crosscheck.py` (`arch.bootstrap.StationaryBootstrap`
  + `optimal_block_length`, mirroring the statsmodels BH oracle): the bespoke stationary-bootstrap SE/CI agree with
  `arch` within loose tol on a fixed-seed AR(1); `optimal_block_length` recovers a longer block for AR(1) than iid.
  Fixed the `pyproject.toml` comment that wrongly said `arch` is "wired in bootstrap.py" (it is a tests-only oracle).
  **270 passed / 1 skipped** (+9). ADR: IMPL-BOOT-1.
- **PENDING (frozen-doc amendment, to apply in the Wave-3 freeze-prep pass):** PREREGISTRATION.md §10 +
  `config/preregistration.yaml:36` relabel "Sharpe studentized (Ledoit-Wolf 2008)" → "re-centred stationary
  block-bootstrap" (exact amendment text recorded in IMPL-BOOT-1).

### Rank 16 — Deflated Sharpe cross-trial variance in the wired selection path
- `deflated_sharpe_ratio(var_sr=None)` used the single-series SAMPLING-variance proxy, not the cross-trial Sharpe
  DISPERSION the canonical Bailey-Lopez de Prado DSR requires; on a heterogeneous candidate population this silently
  mis-stated the (secondary) DSR. `src/selection/fitness.py::held_out_fitness` now accepts/forwards `var_sr` (default
  `None` → the per-candidate path is byte-unchanged, since the population variance is unknowable mid-loop).
- **The empirical cross-candidate `var_sr` is computed at ANALYSIS time** (the clean place — the population variance
  over ALL of an arm's candidates is not knowable inside the per-candidate loop; threading a partial-population variance
  there would bias early candidates). New `scripts/analyze_campaign.py::winner_dsr(records)`: per arm, reconstructs the
  candidate population's per-period validation Sharpes (`sharpe_ratio(metrics['val_returns'])` — the same columns
  `build_perf_matrix` stacks for PBO), forms `var_sr = np.var(sharpes, ddof=1)`, finds the winner (max
  `metrics['val_fitness']`), and recomputes the winner's DSR deflated by that population variance — reporting the
  canonical-vs-proxy DSR + `var_sr` in a new markdown/JSON table; arms with <2 candidates are `skipped` (no ddof=1
  dispersion), never fabricated.
- `src/inference/deflated_sharpe.py` docstring now states plainly that `var_sr=None` is a within-series
  sampling-variance proxy — a DIFFERENT quantity from the cross-trial dispersion — coinciding ONLY under the homogeneous
  zero-skill null.
- **Tests:** two hand-computed golden DSR fixtures in `tests/test_inference.py` (canonical `var_sr` DIFFERS from the
  proxy on a dispersed-skill population, both matching golden values to 1e-10; the two COINCIDE under a homogeneous null
  to 1e-12). **279 passed / 1 skipped.** ADR: IMPL-DSR-1.

### Rank 15 — transaction-cost robustness sweep (cost-defence arm; `costs.grid_bps` was dead config)
- **`config/environment.yaml: costs.grid_bps=[0,5,10,25,50]` was DEAD** — no `cost_bps` override, no harness. Added an
  additive `cost_bps: float|None=None` to `PortfolioEnv.__init__` (`None`→headline `costs.headline_bps`, unchanged;
  else `self.cost=cost_bps*1e-4`) and threaded it through `EnvBundle`/`make_env_builder` (trailing keyword default →
  every existing caller byte-for-byte unchanged).
- **Per-step gross/turnover were NOT persisted** (campaign stored only NET `test_returns`). Added `rollout_port_series`
  + `EnvBundle.test_series` (same seal as `test_returns`); `run_campaign.evaluate_winner_on_test` now persists
  `metrics['test_gross']`+`metrics['test_turnover']` (verified `net==gross−c·turnover` to 1e-12), documented in
  `results.OPTIONAL_FIELDS`. Back-compatible: a NET-only record/fake just triggers the re-roll fallback.
- **`scripts/cost_sweep.py` (NEW):** RE-PRICES frozen winners across the grid WITHOUT retraining — ANALYTIC
  `net_c=gross−c·turnover` (preferred, from the persisted decomposition; valid because cost is charged AFTER the action,
  so gross/turnover are cost-independent, audit C-5) with a `cost_bps`-overridden-env RE-ROLL fallback/cross-check.
  Emits the **winner-identity-vs-cost table** (winner by Sharpe + every arm's Sharpe/CVaR-5% at each level) — the key
  check a tail-aware reward doesn't win merely by trading less. Reads only via `src.io.results`.
- **Tests:** `tests/test_cost_sweep.py` (9 fast, no-torch) — override sets/scales `self.cost`; analytic re-price ==
  re-roll across the full grid to **1e-12**; headline re-price reproduces the default-env net; one table row per cost
  level. **Suite: 279 passed / 1 skipped** (+9). Ruff clean. ADR: IMPL-COSTSWEEP-1. **PENDING (frozen-doc amendment,
  Wave-3 pass):** add the pre-registered cost-sweep to PREREGISTRATION.md §10 + `config/preregistration.yaml` (it is not
  yet listed; exact text in IMPL-COSTSWEEP-1).

## [2026-06-19] — Keystone Rank 8: campaign inference (H2 conjunction + multiplicity family + 1/N floor)
- **`scripts/analyze_campaign.py` (EXTENDED, additive):** wired the FROZEN pre-registration's selection-aware tests onto
  the per-(arm,seed) TEST-leg records (`metrics['test_returns']`).
  - `collect_family_pvalues()` — the arm-contrast × {Sharpe, CVaR@pre-reg levels} family via the stationary-bootstrap
    difference tests, then Benjamini-Hochberg at `multiplicity.q=0.05`; records the signed effect + `direction_ok` so the
    directional decision needs no bootstrap re-run.
  - `h2_conjunction()` — **the HEADLINE test:** `H2_supported` iff distributional beats **scalar AND placebo AND
    scalar_cvar5** in the predicted direction *post-correction* (confirmed against FINAL_PLAN B.6 L83 + PREREGISTRATION
    §1/§10 — the placebo rules out token-count, scalar_cvar5 rules out any-downside-number).
- **Romano-Wolf — methodological gap found + fixed:** the existing `multiple_testing.romano_wolf` is a *pure stepdown*
  that takes a precomputed `boot_stats (n_boot × n_hyp)` and draws nothing; its joint-max (line 104) is only valid if each
  row is ONE joint resample — which nothing in the repo built for the arm-contrast family. Added `romano_wolf_joint()`:
  draws ONE shared `stationary_bootstrap_indices` path per replication, evaluates every contrast on that single path
  (recentred at the observed difference), then feeds the existing stepdown — preserving cross-hypothesis dependence.
  `romano_wolf` + its test untouched; BH stays the default (per config).
- **`benchmark_floor()` + a `WeightPolicy` shim:** rolls all five frozen benchmarks (1/N equal-weight, spy/buy-and-hold,
  mean_variance, risk_parity, hrp) through the **IDENTICAL costed `PortfolioEnv`** via `rollout_port_returns`, by
  reconstructing the lookback window from the obs and returning an action the env's frozen projection *inverts* back to
  the target weights (`log(w)` for softmax; `w` for l1-clip) — so no edit to `strategies.py` or the env. Reports each
  benchmark's test Sharpe/CVaR/MaxDD/DSR; the gate = frozen winner test-DSR **strictly >** max(benchmark test-DSR) (the
  DeMiguel 1/N floor — POST-FREEZE, report-only, never re-selects).
- **Tests:** new `tests/test_campaign_inference.py` (15 fast, no-torch) — H2 supported only when all 3 legs reject (not
  on a tied / wrong-direction / missing leg); BH set == `benjamini_hochberg(pvals)`; `romano_wolf_joint` rejects strong /
  spares null; **the 1/N WeightPolicy's per-step gross == hand-computed `mean(panel.returns[:N])` through the REAL env**
  (`info['gross']==hand`, `port_ret==gross−cost`); the floor reports all five costed benchmarks; the gate flags
  pass/fail. **Full suite: 261 passed / 1 skipped** (additive; +15). ADR: IMPL-H2-1. *With Ranks 1-3, the entire
  executable inference path — select→freeze→test-once → PBO → H2 conjunction + FDR + 1/N floor — now exists.*

## [2026-06-19] — Keystone Rank 3: PBO/CSCV primary overfitting metric (logit + per-arm perf-matrix)

### `logit < 0` fix — the primary metric was mis-counting exact-median ties
- `src/inference/overfitting.py`: PBO counted splits with `logit <= 0`, but **FINAL_PLAN B.9 (line 100)** and Bailey et
  al. 2017 specify the **strict** `logit < 0` (the in-sample-best lands *strictly* below the OOS median; an exact
  OOS-median tie, `λ == 0`, does NOT count as overfit). Fixed the condition + the docstring + renamed the counter
  (`logits_nonpositive`→`logits_negative`). 3 PBO tests stay green — a **spec-confirmed** correction of the headline
  overfitting metric (verified against the project's own B.9, not merely the sweep's assertion).

### Per-arm PBO matrix wired — over CANDIDATES' validation returns
- **Methodology (confirmed against 3 sources — B.9 + the `pbo` docstring + PREREGISTRATION §10):** PBO is computed
  **PER ARM over that arm's search candidates' per-period VALIDATION returns** — the CSCV "trials" are the candidates
  (the within-arm best-candidate-by-validation selection is what actually risks overfitting; "trial count ill-defined
  under guided search"). This is *distinct from* the CPCV-on-winners evaluation folds (a separate scheme for the
  difference-test inference). No discrepancy found; no frozen item touched; all changes additive.
- **Per-candidate validation-vector persistence (additive, all six arms):** the LLM loop (`loop.py:373`) and the
  parallel path already wrote `metrics['val_returns']`; the gap was the *sequential* search arms. `src/agents/evaluator.py`
  gains `evaluate_reward_with_returns(...) -> (fitness, val_returns)` (surfacing the per-period vector already computed
  for `held_out_fitness`; `evaluate_reward` delegates, scalar contract unchanged); `scripts/run_prototype.py` captures
  each search candidate's vector in evaluation order and archives it via an extended `_archive_record(val_returns=...)`.
  `src/io/results.py` `OPTIONAL_FIELDS` doc updated (schema tuples unchanged; the field stays optional/skippable).
- **`scripts/analyze_campaign.py` (NEW — the campaign analysis, separate from the 1-seed-directional
  `analyze_results.py`, which stays untouched):** `build_perf_matrix(records, arm) -> (T_val, N_candidates)` +
  `campaign_pbo(records, *, n_blocks) -> {arm: pbo}` (calls `overfitting.pbo`, `n_blocks=16` from
  `config/inference.yaml`); reads results ONLY via `src.io.results.load_all`; arms with <2 candidates or
  `T_val < n_blocks` degrade to `status="skipped"` (never fabricated/raised); emits a per-arm PBO markdown + JSON.
- **Tests:** new `tests/test_analyze_campaign.py` (12 fast, no-torch) — matrix shape; PBO ∈ [0,1]; a clean monotone
  ladder → **PBO ≈ 0**; pure noise → **PBO ≈ 0.5**; too-few-candidates / short-window / absent-arm all skip gracefully.
  **Full suite: 234 passed / 1 skipped** (was 222/1; +12). ADR: IMPL-PBO-1.
- **Noted (pre-existing, NOT introduced):** the `slow` `test_run_prototype.py` search-arm tests crash with a Windows
  native access violation during torch/SB3 import (a known real-SAC-on-Windows C-extension instability the `slow`
  marker excludes; the campaign runs on Linux/4090). Tracked for the Linux verification pass.

## [2026-06-19] — Keystone implementation pass (punch-list, parallel agents)

### Rank 2 — headline campaign driver (`scripts/run_campaign.py`)
- Implemented the Eureka post-loop **SEARCH → SELECT → FREEZE → TEST** on the frozen development/evaluation split
  (train 2005-2014 / val 2015-2017 → held-out test 2018-2025, embargo 21), replacing `raise SystemExit('STUB')` and
  deleting the dead `from src.io.results import ResultStore` import (results.py never had `ResultStore`).
  **SEARCH** reuses `run_prototype.run_arm`; **SELECT** picks each arm's winner by validation Deflated Sharpe
  (`metrics["val_fitness"]`) via the explicit `from src.io.results import load_all` (name-collision-safe vs
  `src.utils.config.load_all`); **FREEZE** persists `reward_source` + `reward_source_hash` with a `frozen: True` marker;
  **TEST** re-instantiates the frozen winner via `validate_once` (same AST-gate/contract), builds a **3-window**
  `EnvBundle` (`make_env_builder(..., test_window=<2018-2025 idx>, embargo=21)`), re-trains per campaign seed, and calls
  `bundle.test_returns(policy)` **exactly once** — one record per `(arm, seed)` (`run_id=f"{arm}-s{seed}"`) carrying
  `val_fitness`, the realized per-step `test_returns` vector, `per_period_pnl`, `test_sharpe`, `test_cvar05`.
  `resolve_windows` derives all three windows by `np.searchsorted` on the panel date axis; `--resume` skips archived
  records. Fully dependency-injected (trainer/env_builder/arm_runner) so the wiring is unit-testable without real SAC
  training. **Walk-forward folds DEFERRED** (`# TODO(Rank 2b)`; per-fold val-split not invented — directives #3/#7).
- **`src/io/results.py`:** added an additive `OPTIONAL_FIELDS = ("frozen","test_returns","per_period_pnl",
  "reward_source")` registry; **`REQUIRED_FIELDS` UNCHANGED** — a new required field would break every existing writer
  (loop/search/prototype) and the loader round-trip tests, so the additive registry is the correct call (overriding the
  punch-list's literal "extend REQUIRED_FIELDS"). The per-step vector also rides in `metrics["test_returns"]` where
  `analyze_results` already reads `metrics`, so Rank 3's PBO consumes it back-compatibly.
- **Embargo on contiguous splits:** the frozen calendar splits abut (val begins the day after train ends), so raw
  `searchsorted` gives `val_start == train_end`, violating the `make_env_builder` embargo guard. Resolved per LdP
  purge+embargo by carving the 21-day embargo from each *later* window's start. ⚠ **To reconcile (Rank 18):** prefer
  reading the materialized `data/gold/splits_univ3.parquet` so the executed windows **byte-match** the frozen split.
- **Tests:** new FAST `tests/test_run_campaign.py` (9 tests, no torch) — window resolution; winner selection; **the
  selection 2-window bundle refuses the test leg (the seal holds)**; freeze marker; one record per `(arm, seed)` with
  the test metrics + per-step vector; **test leg touched exactly once / val never re-rolled**; `--resume` skips done;
  OPTIONAL_FIELDS additivity. **222 passed / 1 skipped** (+9 over the prior 214). ADR: IMPL-CAMPAIGN-1.
- **FLAGGED (follow-ups; neither blocks the headline H2):** (1) `bayes_opt` archives a *non-executable* comment stub
  (`# bayes_opt coeffs=[...]`), so its frozen winner can't be rehydrated for the sealed test leg — the driver records
  `status="winner_not_testable"` rather than invent a round-trip; the fix (search arms archive the *materialized
  executable* reward_source, required for the **H4** BO-vs-LLM held-out comparison) is tracked as **Rank 2c**. (2) An
  order-dependent test flagged under `pytest-randomly` → to fix + jointly re-verify with Rank 4.

### Rank 4 — transaction cost reconciled to ½-L1-DRIFTED spec (viva priority #2)
- **`src/env/portfolio_env.py` `step()`:** replaced the full-undrifted-L1 cost (`c·‖w − w_prev‖₁`, ~**2×** the spec — it
  missed BOTH the ½ one-way factor AND the realized-return weight drift) with the spec's **½-L1-DRIFTED** turnover:
  `growth = [1+r_t (risky), 1.0 (cash)]`; `port_growth = w_prev·growth` (guarded `> 0`, else `FloatingPointError`); the
  drift-adjusted previous weights `w̃ = w_prev·growth / port_growth`; `turnover = ½‖w − w̃‖₁`; `gross = w[:N]·r_t`;
  `cost = c·turnover`; `port_ret = gross − cost`; + a NEW `info["turnover"]` key. The action projection, simplex bounds,
  log-wealth accumulation, and the `safe_call` sandbox path are untouched; all prior info keys preserved.
- **Docs reconciled to one source of truth (`docs/environment_spec_v1.md`):** removed the stale "Verified as-built
  2026-06-10" header (it pointed at the dead pre-merge `src/portfolio_env.py` + the nonexistent
  `tests/test_portfolio_env.py` → fixed to `src/env/portfolio_env.py` / `tests/test_env.py`); updated the
  `config/environment.yaml` cost comment, the LLM-facing `src/llm/prompts.py:78` text, and FINAL_PLAN L50/260/276 —
  which had previously *agreed with the buggy full-L1 code* (the bug's source); reconciled to the spec (spec wins).
- **Two deliberate, spec-following divergences:** (1) cash grows at **1.0** — no `cash_daily_rate` key in the live
  `config/environment.yaml` (only the pre-merge B-line had one), so `cash_daily_rate = 0` per the documented fallback;
  (2) the drift uses *this step's* realized `r_t` (the code's audit-C-5 timing), matching the spec's intent.
- **Tests:** fixed `tests/test_runner.py::test_uniform_policy_returns_match_panel_mean` — the old "zero turnover after
  t0" assumption was genuinely WRONG under drift (a held uniform weight DRIFTS → ongoing nonzero turnover); it now
  asserts the **full** closed-form net series to **1e-12** (not a loosened tail) with a `turnover.max() > 0` guard.
  Added two `tests/test_env.py` tests: `test_cost_is_half_l1_drifted_turnover` (2-risky-asset + cash, hand-computed
  `w̃`/turnover/cost/gross/port_ret to 1e-12, + drifted-turnover < naive-full-L1, proving BOTH the ½ and the drift) and
  `test_turnover_is_zero_when_target_equals_drifted_weights` (drift-term isolation). ADR: IMPL-COST-1. Unblocks Rank 15
  (cost-sweep). The headline + sweep are now priced at the correct effective bps (viva Q7).

### Rank 6 — sandbox AST gate denylist + candidate memory cap (ADR-008 now matches the code)
- **`ast_gate` (`src/sandbox/executor.py`):** added a numpy IO/FFI attribute denylist `_BANNED_ATTRS`
  (load/loads/save/savez/savez_compressed/savetxt/loadtxt/genfromtxt/fromfile/tofile/memmap/frombuffer/DataSource/
  lib/ctypeslib/f2py/testing/mro/open). The gate was previously **dunder-only**, so `np.load(..., allow_pickle=True)`
  (a pickle-RCE vector), `np.save`, `np.fromfile`, `np.genfromtxt`, `np.memmap`, `np.DataSource`, and the `.mro`/`.open`
  object-model escapes **all passed the live gate**. They are now rejected statically (`return False`) before any
  execution. ADR-008 + the CHANGELOG already *claimed* this control — the gate now enforces it (closes the
  viva-falsifiable gap; sweep Rank 6 / viva Q22).
- **`_candidate_child`:** best-effort POSIX resource caps applied before `exec` — `RLIMIT_AS` ~2 GiB, `RLIMIT_CPU` 15 s,
  `RLIMIT_NOFILE` 64, `RLIMIT_FSIZE` ~1 MiB — each clamped to the existing hard limit, never raised, all best-effort.
  Ported in shape from `archive/pre_merge_repo_B/src_flat/sandbox.py::_limit`. An LLM-written reward can no longer OOM
  the rented 4090. The in-process `_validate_inline` fallback is deliberately **not** capped (capping the orchestrator
  process would be wrong).
- **Windows:** `resource` is POSIX-only, so the caps are a documented no-op there (psutil is **not** a dependency → no
  RSS watchdog added, only the documented gap); the wall-clock timeout (the killable spawn child, ADR-028) is the
  backstop. The Linux/4090 campaign box enforces every cap.
- **Tests (`tests/test_sandbox.py`):** 10 gate-denial cases over the numpy IO/FFI + `.mro` surface; a POSITIVE control
  proving legitimate reward math (sum/mean/std/var/dot/clip/abs/where + indexing/arithmetic) still passes (the denylist
  didn't over-block); a POSIX-gated (`skipif` on absent `resource`) address-space memory-bomb rejection. **220 passed /
  1 skipped / 8 deselected** (fixed order). ADR: IMPL-SANDBOX-1. The duplicate `candidate_failed`/`reset_failure_flag`
  defs were left untouched (Rank 18).

### Verification + tooling — joint suite green + determinism guard now active
- All three parallel ranks (2/4/6) integrate cleanly: the full non-slow suite is **222 passed / 1 skipped / 8
  deselected**, **order-independent across 3 shuffled runs**.
- Installed the declared-but-missing **`pytest-randomly`** into the venv (pyproject declared `>=3.15`, but the venv was
  out of sync, so the test-order shuffle — the inter-test state-leakage guard — had never actually run). The
  `test_run_campaign::test_resolve_windows_…` "flake" the Rank-6 agent reported was a transient artifact of reading the
  file *mid-write* during concurrent agent execution; it passes in isolation and under every shuffle. **Follow-up
  (Rank 14):** the lockfile / `make sync` must pin this so the guard can't silently disappear again.

## [2026-06-19] — Verified 13-sweep punch-list (workflow wr6yuz0yd) + Keystone Pass 1: held-out TEST leg

### Adversarial verification sweep — 60 agents, 84 → 43 findings
- Ran a 13-sweep deterministic workflow (3 GitHub-repo wiring/collision + 10 internal adversarial-verification sweeps)
  over the whole repo + planning corpus; every P0/P1 finding was re-checked by an independent skeptic (default-refute).
  **84 raw findings → 46 deduped P0/P1 → 43 survived.** Synthesised into a strict, ranked, implementation-ready
  punch-list: `00_planning/IMPLEMENTATION_PUNCHLIST_2026-06-19.md` (the execution bible).
- **Headline — the keystone inference path is the dominant grade risk:** `run_campaign.py`/`inspect_rewards.py` are
  stubs importing a non-existent `ResultStore`; `EnvBundle` had no test leg; `pbo()`/`romano_wolf`/`benjamini_hochberg`/
  `baselines.strategies` are implemented-but-never-called outside tests; `univ4` does not exist (live panel is `univ3`
  with `liquidate_to_cash` zero-filling the exact left tail the H2 measures read); `freeze.py`/`power_analysis.py` are
  stubs; the transaction-cost model is full-undrifted-L1 (~2× the half-L1-drifted spec); the sandbox AST gate misses the
  numpy file/FFI surface (`np.load` pickle-RCE) with no candidate memory cap; + a cluster of IQN-era doc-vs-code
  contradictions and the seeds-5-vs-30 frozen-record conflict to reconcile before the Phase-1 freeze.
- **Verified SOLID (do not refactor):** the sandbox two-stage design (ast_gate → killable-child validate → in-process
  safe_call; ADR-028); the `EnvBundle` two-window contract + policy-agnostic `rollout_port_returns`;
  `src/agents/evaluator.py` (matched-compute reward evaluator); `src/io/results.py`; the PIT+21d-embargo split
  materialisation (byte-matches prereg); `analyze_results.py` correctly scoped 1-seed directional;
  `src/feedback/measurement.py`+`schema.py` (the canonical frozen-six estimator — docs reconcile *to* it); the novelty
  conjunction (survives the mid-2026 sweep). Repo sweeps surfaced Eureka/rl-baselines3-zoo/qlib wiring templates +
  `arch.StationaryBootstrap`/`StepM` as cross-check oracles + QuantEvolve (arXiv:2510.18569 %VERIFY) as the closest
  finance collision (strategy-code QD, scalar score, NO RL, NO tail-to-LLM → cite-and-distinguish).

### Keystone Rank 1 — held-out TEST leg (`src/env/runner.py`) — DONE, verified
- **The unblocker.** `EnvBundle` + `make_env_builder` gained an optional `test_window`; new `EnvBundle.test_returns(
  policy)` rolls the frozen policy through the test env but **raises `RuntimeError("test split sealed until final
  inference")`** whenever the bundle has no test window. Because the discovery loop and every search arm build only
  2-window bundles, the 2018-2025 test split is now **structurally unreachable during selection** (PREREGISTRATION §10:
  select-on-validation → freeze → test-once; AUDIT-B2/B3).
- `make_env_builder` gained `embargo: int = 0` and now validates **both** boundaries: `val_start ≥ train_end + embargo`
  (generalising the old disjoint check, message keeps "disjoint") and, when a test window is given, `test_start ≥
  val_end + embargo` (Lopez de Prado 2018 purge+embargo). Default `embargo=0` keeps the legacy 2-window callers
  (`run_prototype`, `parallel`) byte-identical; the campaign passes 21.
- **Deferred (IMPL-TESTLEG-1):** `make_walk_forward_windows` (rolling 5y/1y/1y evaluation folds) → Rank 2, where the
  `Panel` date API + the per-fold val-split question are confirmed against the frozen prereg rather than invented.
- **Tests:** 3 added to `tests/test_runner.py` (the seal raises without a window + returns the right shape with one; the
  val→test and train→val embargo guards both fire). **Full non-slow suite: 199 passed / 0 failed** (was 196; +3). No
  regressions. ADR: IMPL-TESTLEG-1 (`docs/DECISION_LOG.md`).

## [2026-06-19] — 20-track deep audit + P0 remediation + provider decision (ADR-032, ADR-033)

### Audit (engineering + scientific) + GitHub-repo research
- 20-track strict deep audit + 4 GitHub-repo research agents. Verdict: the codebase is **excellent in design**; the
  singular gap is the **executable inference path stops at validation**. Registers:
  `00_planning/SYSTEM_AUDIT_AND_REMEDIATION_2026-06-19.md` + `00_planning/GITHUB_REPO_FINDINGS_2026-06-19.md`.

### P0 correctness fixes — DONE, full non-slow suite green
- **Numerical (P0-1):** an exact `sd==0` guard that a near-constant series **evades** (`std ~ 2e-19`, not 0) made
  `deflated_sharpe` return **1.0 for a flat reward — which would WIN candidate selection**. Fixed: relative near-zero
  guard (+`np.ptp`) + non-finite stripping + f64 in `deflated_sharpe._sample_moments` and `bootstrap.sharpe_ratio`/`cvar`.
  28 invariant tests added (`tests/test_numerical_guards.py`).
- **Sandbox (P0-2):** `safe_call` (stage-2) was **never wired** into training — a reward valid on the fixture but failing
  on a real N-asset obs **crashed the rollout**. Now routed through `safe_call`; added `reset_failure_flag`/
  `candidate_failed`; runner resets + logs.
- **Seeding (P0-3):** the GPU parallel worker now calls `set_global_seed(seed, deterministic_torch=True)` at entry —
  all RNG stacks + `use_deterministic_algorithms(warn_only)` + `CUBLAS_WORKSPACE_CONFIG`.

### Dependencies (P0-5) + provider
- torch↔SB3 conflict resolved: capped `stable-baselines3`/`sb3-contrib` `<2.9` (keeps validated torch 2.6+cu124).
  Dropped `rliable` (upstream archived). Wired `arch`. Security re-pins (`python-dotenv≥1.2.2`, `pytest≥9.0.3`,
  `ruff>=0.15,<0.16`). Added `anthropic` + `seaborn` + `pytest-randomly`/`pytest-timeout`. `requires-python<3.13`.
- **Provider decided (ADR-033): Sonnet 4.6 primary + Llama-4 N3 + DeepSeek-V4 check** (~$7 whole project). ⚠ The
  Anthropic key pasted in chat is exposed in the transcript → **must be rotated** (never stored/committed).

### Queued (per the register; the real run stays gated)
- Campaign inference-path builds (held-out **test leg** + `run_campaign` + PBO/benchmark-floor/`inspect_rewards` wiring
  + cost-sweep + **≥20 seeds** + **univ4** delisting imputation); repro hardening (freeze.py+OpenTimestamps, capture_env,
  lockfile, CITATION.cff, make-figures); provider wiring (anthropic transport default + prompt-cache + tenacity);
  adopted tooling (import-linter, gitleaks, …); cross-check tests (arch/statsmodels/pyextremes oracles); doc
  reconciliation (4× prompt/schema-vs-code drift).

## [2026-06-18] — Max-compute calibration: GPU enabled, GPU-ONLY optimal; LLM provider decided (ADR-030, ADR-031)

### Compute — "use full power": GPU is ~3× CPU, but GPU-ONLY beats every GPU+CPU mix
- Installed CUDA torch (2.6.0+cu124); added explicit `device` to the agent factory/trainer (ADR-030). Single SAC:
  **GPU 96–110 steps/s vs CPU 34** — the 1,893-dim obs is GPU-favorable, overturning the earlier "CPU-bound" read.
- Built `src/orchestration/parallel.py` — a device-load-balanced candidate pool (`DevicePool`: n_gpu cuda + n_cpu
  cpu tokens over a non-daemon `ProcessPoolExecutor`, fed by per-arm driver threads) + a `--parallel` path in
  `run_prototype.py`.
- **Calibrated (`scripts/bench_compute.py`): the GPU saturates at ~185 steps/s; CPU training workers are useless
  (threads=1 → ~5 steps/s each) AND starve the GPU (3 GPU=186 → 3 GPU + 8 CPU=143). GPU-ONLY is optimal**
  (ADR-031). Set `n_gpu=3 / n_cpu=0`, `agent.device: cuda`. **Full 240×25k prototype ≈ 9 h on the laptop**
  (ADR-030's ~3–6 h was wrong; the GPU is the hard ceiling; SBX/JAX ~10× is the only sub-3h lever, gated).
- **Verified:** GPU dry-run (2 workers) ran all three arm types — incl. the nested sandbox validate-once child
  spawning *inside* a GPU pool worker — `matched_budget_ok=true`, reloadable archive, clean exit 0.

### LLM provider — deep research + accurate costing
- Two deep-research passes (provider comparison + decision validation). **Decision: Sonnet 4.6
  (`claude-sonnet-4-6`) primary reward-author** (clean, honors `temperature=0`, novel, reliable) **+ Llama 4 open
  N3 contamination control** (only model with an official cutoff) **+ DeepSeek-V4 optional "contaminated"
  cross-check** (FinRL-DeepSeek / AlphaForgeBench expose DeepSeek on the same universe → wrong for the *clean*
  headline; GPT-5.4-mini is the max-determinism alternative).
- Costed from the *real* prompts + stateless loop (~85k in + 72k out per prototype model): **whole project ≈ $7**
  (range $0.5 all-open → $13 GPT-5.5) — cost is immaterial; provider chosen on fit. Provider ADR pending user lock-in.

## [2026-06-18] — Build P3–P6: world-class prototype machinery, verified (ADR-029)

### The headline
- Built and end-to-end-verified the full advanced-prototype machinery (MASTER_EXECUTION_PLAN P3–P6) to a
  world-class standard, **without executing the directional run** (user directive: build to the max, coordinate
  every step with the literature, verify everything, don't run yet). **Full non-slow suite: 175 green; ruff clean.**

### P3 — the two missing keystones + the C1 adapter
- `src/env/runner.py` (the `env_builder` keystone the loop injects: train/val/measurement windows on one PIT
  panel, deterministic no-look-ahead rollout); `src/agents/trainer.py` (fixed SAC; memory-safe buffer ADR-025;
  train-only obs-normalization via a stats-carrying `NormalizedPolicy` — deep-research §2);
  `src/agents/evaluator.py` (the **C1** adapter so the search arms consume matched compute).

### P4 — LLM glue
- `src/llm/prompts.py` renders `{ENV_INTERFACE}`; `loop.py` rewired to send it (**C3**, non-breaking);
  `src/llm/stub_designer.py` emits keyless, deterministic, varied valid reward code (6 archetypes spanning the
  reward family + tail-aware/stateful designs) so the LLM-arm pipeline runs with NO API key;
  `make_anthropic_transport` (provider parity).

### P5 — orchestration
- `src/baselines/reward_family.py` (the live-contract H4 `params_to_reward`, authored — it existed only as an
  injected name + an incompatible archived version); `config/prototype.yaml`; `scripts/run_prototype.py`
  (6 arms; arm-level parallelism across non-daemon workers; search arms via the C1 evaluator + family; uniform
  archiving; matched-compute assertion; resumable; dry-runnable). **Dry-run ran all 3 arm types in parallel,
  matched=True, 19.2s.**

### P6 — analysis
- `scripts/analyze_results.py` (H2/H4 directional reads; Sharpe/CVaR difference tests on archived validation
  returns; rliable IQM; the interpretability mechanism-gate; GREEN/AMBER/RED verdict; compute-accounting).
  `loop.py` now archives `val_returns` so the difference tests can run on the winners.

### Verified / recorded
- +22 tests (runner, trainer+integration, prompts, stub-designer, reward-family, analysis, orchestration);
  ADR-029. **Open (user's, plan §10):** the LLM provider + key for Pass B, and the gated prototype RUN.

## [2026-06-17] — Build P1–P2: runtime + Phase-0 GATE GREEN (ADR-026/027/028)

### Runtime (P1)
- Built the pinned **Python 3.11** venv; installed torch (CPU) + SB3 2.9 + sb3-contrib + numpy<2 / pandas<3 /
  scipy / sklearn / statsmodels / gymnasium / arch / rliable / pyarrow. Pinned **pandas<3.0** (pandas 3.0 broke
  `arch` under the numpy<2.0 pin) and moved **d3rlpy to an optional extra** (ADR-026). **Full non-slow suite
  re-earned GREEN on this laptop: 153 passed** — 3 env-dependent agent tests were updated to *simulate* backend
  absence via monkeypatch (they previously passed only because SB3 was not installed).

### Phase-0 GATE (P2) — GREEN
- Implemented `scripts/smoke_test.py`; **GATE GREEN** on the RTX-4050 **CPU**: SAC **m ≈ 18.9 min/50k**, TQC
  **m ≈ 25.9**, critic loss falls (SAC 413→1.0, TQC 9.8→0.25), obs_dim = 1893. The one unmeasured quantity `m`
  is now measured (matches the compute doc). Recorded in `docs/DECISION_LOG.md` (PHASE-0).

### Fixes the gate surfaced (each recorded)
- **ADR-027** — bounded the env action space `Box(-inf,inf)` → `Box(-10,10)` (SAC/TQC assert finite bounds).
- **ADR-028** — cross-platform sandbox validation timeout: Windows `signal.SIGALRM` was a silent no-op, so a
  `while True` reward hung the run AND the test suite; now a killable child process (C2).
- Fixed the smoke stub's wrong import `src.env.portfolio` → `src.env.portfolio_env`.

## [2026-06-17] — Advanced execution plan + build reconnaissance (ADR-025)

### The headline
- Authored **`00_planning/MASTER_EXECUTION_PLAN.md`** — the authoritative execution plan for (Part I) a
  user-requested **advanced 40-candidate prototype** (6 arms × 40 candidates × 1 seed; 8×5 reflection) and
  (Part II) the full **6 × 30 × 5** campaign. Every build step is anchored to a corpus paper, carries an
  acceptance test, and names a recording target. **Supersedes `ADVANCED_PROTOTYPE_BLUEPRINT.md`** (its data
  task T0 is closed — the `_univ3` panel exists).

### Reconnaissance (verified on this laptop, not inherited)
- **Runtime absent:** no `.venv`, no torch/SB3/numpy installed (system Py 3.12 only) → the 153-test green must
  be **re-earned here** (P1). Hardware: i7-13620H 16T / 15.6 GB RAM / RTX 4050 6 GB.
- **⚠ Memory bug found:** default `buffer_size=1e6` × 1,893-dim obs ≈ 15 GB replay RAM → would OOM the laptop;
  fix recorded (size to `train_steps` / `optimize_memory_usage`).
- **Missing keystones:** the concrete SAC trainer (`train_and_evaluate`) and the env-runner (`env_builder`) —
  only faked in tests. All 8 execution scripts confirmed STUBs; real `_univ3` gold panel confirmed loadable.

### Keyless machinery-validation path
- A deterministic **`StubDesignerTransport`** lets the entire pipeline run end-to-end on real GPU+data
  **without an API key** (Pass A); the real-LLM headline (Pass B) is one transport swap, gated on provider/key.

### Recorded / open
- ADR-025 (this session). Frozen-design open items (budget 30/40/240, embargo 10/21, provider, delisting,
  action-projection, λ) routed to the Phase-1 freeze (plan §7.1). Plan under independent adversarial review
  before the build begins.

## [2026-06-17] — Repository unification: one folder (engine ⊕ data) — Stage 1 (ADR-022)

### The headline
- **Two divergent repos are being merged into one project folder** under an absolute **no-loss/no-delete**
  rule: the audited *experimental engine* (was `dissertation_papers/llm-reward-portfolio`) is the structural
  base; the *data + hardened core* line (was `~/Downloads/llm-reward-portfolio`, this repo's prior identity)
  is being folded in. Staged + test-verified, never a big-bang (rationale + full plan in **ADR-022**).
- **Safety net first:** full backups of both repos at `~/Downloads/_merge_backup_2026-06-17/`
  (B 416M, A 513M, incl. `.git` + data). The source repo B is **retained untouched** until Stage 4.

### Stage 1 — folded in, non-breaking (DONE)
- **Real data + provenance copied and CHECKSUM-VERIFIED** — canonical panel `returns_panel_univ3.parquet`
  sha256 `f4edc86…` identical at source and destination; `data/{gold(54 parquets),clean,raw,staged,
  manifest}` now live in the unified repo; `data/manifest` carries checksums.txt + manifest.jsonl (874) +
  lineage.jsonl + invalidated.jsonl + journal.
- **Provenance & docs folded in:** `CHANGELOG.md`, `DECISIONS.md`, `RELATED_WORK_WATCH.md`, `reports/`,
  `runs/`, all of B's `docs/*` (DATASHEET, DATA_ENTITLEMENTS, REFERENCES, distributional_feedback_schema,
  environment_spec, …), `scripts/verify_inventory.py`.
- **Configs/prompts:** B-unique `eureka_loop.yaml` + `inference.yaml` added; the 3 clashing configs
  preserved as `config/{data,environment,llm}.B.yaml` (A's never clobbered); all B prompts added alongside
  A's (no filename clash) for Stage-2 reconciliation.
- **Engine integrity confirmed:** **148 tests pass, 0 failed** across 20 test files after the fold-in —
  A's audited science modules were not touched in Stage 1.

### Convergence decision (evidence-based) + interim state
- **B's flat science modules are the PRE-AUDIT line** (verified: B still ships `smoke_iqn_sac.py` — the
  IQN-SAC the audit rejected for SAC+TQC — and a `crossing_rate` neural-IQN diagnostic the preregistration
  dropped). So **A's audited science stays canonical as the live `src/`**; B's pre-audit science is **NOT
  merged** and is **preserved wholesale, not deleted** (Stage 4 folds all of B into `archive/
  pre_merge_repo_B/`). Audit-neutral B engineering gains (resource-limited sandbox isolation) are logged as
  candidate future ports under their own ADR — never blind-merged.
- **B's data-acquisition layer is self-contained** (imports only within `src/data/`), so Stage 3 integrates
  it cleanly into the package and wires a real-gold loader for the audited env.
- Interim only: `config/*.B.yaml` and the dual prompt set are reconciled in Stage 4. PREREGISTRATION stays
  A-canonical and **untouched** — the frozen design is unchanged by the merge.

### Stage 3 — acquisition pipeline relocated + B preserved (DONE; env↔data loader flagged)
- **`data_pipeline/`** created: B's Refinitiv→gold acquisition stack relocated **verbatim** (its dependency
  closure `{config.py, features.py, data/}` + B's `config/*.yaml` + a README). Imports are intact (B's
  `config.py` resolves `CONFIG_DIR` relative to itself) — **smoke-imported clean** in A's venv (which already
  has `lseg-data`, `pandas-market-calendars`). It is decoupled from the live engine: the gold panel is frozen,
  so the pipeline is provenance/reproducibility only (re-running needs live Refinitiv creds).
- **`archive/pre_merge_repo_B/`** created (nothing lost): B's pre-audit flat science modules (`src_flat/`,
  with a successor-map README) + B's root docs (`root_docs/`: CLAUDE/README/PREREGISTRATION/Makefile/
  pyproject/requirements). Full `.tgz` of B (incl. `.git`+data) remains at `~/Downloads/_merge_backup_2026-06-17/`.
- **Flagged for careful follow-up (NOT improvised):** the live env↔real-data **loader** (`returns_panel_univ3`
  → audited `Panel`) must decide **intra-window delisting handling** — e.g. Wachovia `WB.N^A09` is in the
  dev-2005 top-30 and dies in 2009 (NaNs after delisting), while the env's `Panel` requires finite returns.
  That is a preregistration/`environment_spec_v1` design decision, deferred to align with the frozen design.

### Stage 4 — single folder, dedicated git repo (DONE)
- `.gitignore` extended to protect the merged licensed data (`data/clean|staged`, `manifest/journal`,
  `runs/`); `.env` brought into the repo and confirmed **untrackable**; redundant `config/*.B.yaml` removed
  (preserved in `data_pipeline/config/` + backup).
- **Standalone B removed** after its backup was verified to contain the canonical panel + 526 git objects —
  truly one folder now; nothing lost (integrated + `archive/` + 416M `.tgz`).
- **Dedicated git repo** initialised at the repo root (was loose inside the home `parametric-catbond-erc20`
  repo); initial commit on `main`, 1061 files, **0 secrets/parquets/`.venv` staged** (guard-verified).
- README updated for the unified layout.

### Gap-closure wave (DONE) — ADR-023, ADR-024
Audited the unified repo and closed every inconsistency (or flagged it explicitly):
- **Real-gold loader** `src/data/loaders.py` + 5 tests — the audited env can now train on
  `returns_panel_univ3` (anonymised ids; delisting policy `liquidate_to_cash`, ⚠ provisional, ADR-024).
  **Suite: 153 green.**
- `pyproject` gained `[optional-dependencies] data` (lseg-data, pandas-market-calendars, python-dotenv,
  pyarrow); the `openai` line annotated (provider OPEN vs ADR-016 Claude — reconcile before freeze).
- `config/data.yaml` source corrected **CRSP→Refinitiv** (+ `vix: FRED_VIXCLS`); `environment.yaml` VIX
  source noted; `src/data/pipeline.py` docstring now points to `loaders.py`/`data_pipeline/` (synthetic vs
  real disambiguated).
- README counts fixed (10 YAMLs; scripts marked **STUB**; 153 tests); **CLAUDE.md** gained a post-merge
  section; the **two decision logs cross-linked** (`DECISIONS.md` authoritative; `docs/DECISION_LOG.md` =
  A-line audit); `prompts/README.md` documents the hardcoded-vs-template state; `PREREGISTRATION §12`
  carries the compute amendment footnote.
- **Build-gated remainder (NOT inconsistencies — tracked):** the GPU/credential entry-point STUBS
  (smoke_test, build_gold, run_campaign, freeze, analyze_results, inspect_rewards, power_analysis =
  blueprint T1–T6), the concrete SAC trainer, and the LLM key/provider choice.

## [2026-06-12] — Entitlement landed: PIT membership built; universe pulls running

### The headline
- **A1 PIT membership EXISTS and validates** (`data/staged/pit_membership.parquet`): 252 months ×
  499–506 names, union **953 RICs** (2005–2025) incl. **333 dead ^RICs**; Lehman in 2005-01/out 2008-10
  (leaver event 2008-09-17, `LEH.N^I08`), FactSet/Airbnb absent 2005, Tesla out 2019/in 2021.
  Lineage to the three raw event pulls; validation gates recorded in provenance.

### Two silent vendor traps caught by CONTENT validation (shape checks false-passed both)
1. **Membership snapshots return the CURRENT chain** on this route — `TR.IndexConstituentRIC`+SDate,
   the dated chain `0#.SPX(date)`, and field-embedded SDate all silently survivorship-biased (FDS/ODFL/
   ABNB "in 2005"). 98 `rf_members_*` artifacts INVALIDATED (`data/manifest/invalidated.jsonl`, now
   git-tracked); method switched to **reverse event replay** through `TR.IndexJLConstituent*` streams
   (3 requests for 21 years), gated by count-band [495,510] + known-truth checks (**ADR-020**).
2. **`TR.TotalReturn` via get_history returns empty/NaN frames** — 39 `rf_tr_*` artifacts INVALIDATED;
   corrected to **datagrid long form** `Frq=D` (content-verified: Lehman daily series through
   2008-09-12, worst day −44.9%, percent units) and `Frq=M` for market cap; price/bid/ask/volume via
   no-fields `get_history` (TRDPRC_1/BID/ASK/ACVOL_UNS), split per-field for lossless CSV.
- Probes P2/P3 rewritten to content-validated JL queries (assert known dead-RIC leavers), and the
  mnemonic checks of 06-12 morning now read values, not shapes — the trap class is test-closed.

### Added
- `src/data/build_universe.py` + `build-universe` CLI/make target: long→wide assembler
  (percent→decimal, dedup-keep-last, XNYS align, fail-loud on missing pulls) feeding the existing
  `panel.build_gold` with membership+mcap → D2 mcap panel, D3 top-30 per window, PIT D1/D4/D6 (`_univ`).
- Live mnemonic confirmations into config (`TR.CompanyMarketCap`, `TR.BidPrice/AskPrice`, `TR.Volume`,
  TRBC-on-dead-RICs, `.SPXTR`); `.VIX` NOT licensed (CBOE) → FRED VIXCLS stays primary;
  `TR.InstrumentDelistedDate` often null → delist dates derive from ^MYY suffix + last trade.
- Probe evidence serializer fix (Timestamp keys from live frames).

### Pulls (journaled `universe_refinitiv`, resumable)
- Frozen: `rf_chain_current`, `rf_jl_joiners` (523 events), `rf_jl_leavers` (520 events);
  daily-TR chunks streaming (429 total: 39 name-chunks × 11 two-year spans), then 39 monthly-mcap
  chunks, 39 OHLC/bid/ask/volume chunks, delisting/sector metadata, `.SPXTR` benchmark.

### Integrity
- PREREGISTRATION.md + prompts/ untouched; `lambda_frozen` null; invalidations are append-only
  declarations (write-once artifacts remain on disk, nothing consumes them); suite 121 passed + 1 skip.

## [2026-06-10 — data requirements & inventory session]

### Added
- `reports/data_requirements_and_inventory.md` — canonical data bill-of-materials (A1–D6 matrix),
  fully verified physical inventory (39/39 checksums re-hashed PASS, 0 orphans, 0 mutations), D5
  byte-match vs PREREG §6, gap summary with per-item unlock conditions + closing commands, quarantine
  status, and the completeness line ("5 of 14 satisfied; remaining unlock on Refinitiv/LSEG entitlement").
- `config/data.yaml: universe_pull` — A1–A5 acquisition bill-of-materials, citation-annotated, VERIFY
  flags on unconfirmed mnemonics (ADR-019).
- `src/data/pull_universe.py` — header-tolerant parsers (membership / delisting / panel) + journaled-engine
  orchestrator; `pull-universe` CLI subcommand (dry-run default, `--live` when entitled); `make pull-universe`.
- `tests/test_pull_universe.py` — 5 parser/orchestrator tests on synthetic fixtures (no network).
- `DECISIONS.md` ADR-019 (A1–A5 wiring; identification untouched) + ADR-017/018 reserved markers.

### Verified (no change to data)
- Re-probed entitlements: platform session did not open this run (P0 BLOCKED `OpenState.Closed`, vs PASS
  on 10 Jun — short-lived RDP token); data-access conclusion unchanged (no non-empty scope set ever);
  DSWS still `ZLDU178` ClientApi-not-entitled. Report regenerated.
- Write-once integrity: every layer re-hashed, all PASS, no orphan/mutation.

### Unchanged (integrity)
- PREREGISTRATION.md + prompts/ byte-untouched; lambda_frozen null; no data re-pulled; no new dependency;
  no live Refinitiv pull beyond the probe. Test suite 118 passed + 1 platform-skip; ruff clean.

## [2026-06-10 — close-out session] — Pre-Friday plan completion (sections A–E only)

### Added
- `docs/outbox/availability_reply_ramin.md` — copy-paste-ready Thu/Fri availability reply (two bracketed
  slot placeholders, group-format preference, one-pager closing line). DEADLINE: TODAY. Not sent.
- `docs/outbox/escalation_lseg.md` — finalized LSEG escalation (DSWS ClientApi enablement for account
  ZLDU178; RDP data scopes; WRDS/CRSP question; recipient guidance). Verbatim from the entitlement
  report. Not sent.
- `docs/staging/PREREGISTRATION_v1.0_FINAL.md` — freeze candidate: current draft + exactly three folded
  changes (§3 λ tie-break sentence; §4a naming the H4 reward family per config; §10 hash cell re-pointed
  to ADR-005). Diff-verified: 19 lines, all accounted for. Live PREREGISTRATION.md byte-untouched.
- `docs/staging/FREEZE_RUNBOOK.md` — ordered T4 commands + Step-0 decision list: (1) single-shot arm
  count 80 (PREREG §4) vs 240 (config) — recommend "240 = 80 × R=3"; (2) "fixed hyperparameters from
  config/" but no algo-hyperparameter file exists yet — add config/algos.yaml or re-word before freezing.
- `reports/meeting_script.md` — 2-minute spoken version ending on the ICAIF 2-Aug question.
- `reports/session_report_2026-06-10_close.md` — this session's stage-by-stage report incl. 4090 runbook.

### Changed
- `reports/research_brief_v1.md` — live-status block added (5,282×35 panel marked PROVISIONAL pending
  PIT; kurtosis 49.9 / Hill 2.1–3.6 headline; entitlement one-liner; freeze-staged-Friday line).
  427 words — one page.
- `docs/evidence/entitlement_report.md` + probes.json regenerated by a fresh live probe run
  (REFINITIV_APP_KEY present in .env → probe executed per plan): outcomes UNCHANGED — token still
  carries zero scopes (new EDP-API key not yet minted); DSWS still "ClientApi not entitled" for ZLDU178.
  Checklist statuses remain accurate as-is.

### Explicitly NOT done (per session constraints)
- Nothing sent, frozen, or signed; PREREGISTRATION.md, prompts/, scope-lock list untouched
  (byte-verified); lambda_frozen still null; no new dependencies; no week-15 work, no training,
  no new pipeline stages. `make smoke`/`make lock` remain 4090 actions (runbook in the session report).

## [2026-06-10] — Session: W15 build-out + research-grade data platform

### Added — research engine (week-plan W15 items)
- `src/features.py` — leakage-safe cash-row features [vol20, vol20/vol60, vix]: rolling sample std of
  the equal-weight market proxy, shift(1)-lagged, VIX/100 scaling, NaN warm-up; truncation- and
  future-perturbation-invariance tested (ADR-007).
- `src/portfolio_env.py` — optional `cash_features` observation block with fail-loud non-finite guard;
  observation dim +3 when supplied; accounting unchanged (ADR-007).
- `src/rewards_baselines.py` — completed the six-reward canon: `SharpeEpisodic` (expanding-Welford SR
  increment, telescopes to episode Sharpe), `CVaRPenalisedMean` (Rockafellar–Uryasev shortfall),
  `DrawdownPenalised` (running-peak level penalty), `TurnoverPenalised` (extra anti-churn shaping);
  `BASELINE_FACTORIES` registry test-enforced against `config/eureka_loop.yaml` (ADR-009).
- `src/reward_family.py` — six-term parameterised reward family for the H4 random/BayesOpt arms; vertices
  recover the hand-designed canon; seeded uniform sampler over config-frozen ranges; shared
  `params_to_reward` constructor; content-addressed `params_id` (ADR-010).
- `src/calibrate_lambda.py` — PREREG §3 λ-selection machinery: per-λ separation accuracy of known-good vs
  known-degenerate rewards; tie-breaks = across-seed stability, then smallest λ; full table returned for
  the freezing ADR; never writes config (ADR-010).
- `src/candidate_archive.py` — verbatim append-only candidate archive (source + prompt + model snapshot +
  temperature + outcome; content-addressed; collision raises) per R6 (ADR-008).
- `src/dry_run_random_search.py` — TrialLedger end-to-end dry run on labelled THROWAWAY candidates
  (synthetic returns, untrained fixed-logit policies, explicit throwaway λ): 10 candidates → ledger N=10 →
  DSR 0.577 / SR0 +0.069 → PBO 0.094 over 12,870 CSCV splits; sidecar to `runs/dry_run/` (ADR-010).
- `src/reward_contract.py` — `probe_contexts()` extracted as the single source of the synthetic probe
  battery (in-process validator and sandbox share it).

### Added — data platform (`src/data/`, 13 stages; ADR-012)
- `vault.py` — write-once layered storage (raw/staged/clean/gold), SHA-256 manifest (`manifest.jsonl` +
  legacy `checksums.txt`), provenance sidecars, checksum-verified reads (unmanifested reads refused),
  lineage graph (`record_lineage`/`lineage_chain`).
- `acquire.py` — rate governor, exponential backoff with full jitter, per-chunk resumable `PullJournal`,
  ticker/date chunkers, minimal `.env` loader (no new dependency; never logs values), provenance capture
  with library versions, vendor fetchers (Refinitiv platform/desktop, DSWS `DataClient`, yfinance
  OHLCV+actions non-adjusted, FRED, Ken French), `EntitlementError` degradation type,
  `capture_field_definitions` (RI day-count = explicit MANUAL-CONFIRMATION record).
- `probes.py` — automated DATA_ENTITLEMENTS checklist (chain, PIT 2018/2010, DSWS list, GE exit window,
  dead-RIC `LEH.N^I08`, field definitions) → `docs/evidence/entitlement_report.md` + `probes.json`;
  escalation email auto-rendered when the pre-2016 path fails both vendors.
- `security_master.py` — RIC↔ticker symbology with dead-RIC `^`-suffix parsing (month letters A–L),
  yfinance symbol mapping (share-class dashes), curated overrides (GOOG/GOOGL 2014, META/FB 2022),
  `resolve()` that raises on unknown/ambiguous symbols.
- `validate.py` — minimal schema core (dtype/nullability/bounds/monotone-unique tz-naive index), explicit
  coercion (never invents values), XNYS sessions via exchange-calendars with explicit `calendar_start`
  (default ~20y lookback would clip 2005), calendar alignment with off-session reporting, exact-vs-conflict
  duplicate detection, missing-data engine (holiday/pre-IPO/post-delisting/interior taxonomy, full
  conservation counting, ZERO interpolation).
- `integrity.py` — RI internal-consistency flags, unadjusted-split signatures (−50%/−66.7% without vendor
  record), stale-price runs, zero-volume flags, Ince–Porter screens (daily adaptation, documented),
  cross-sectional extreme-day classification with SELF-EXCLUDED peer context (a lone collapse cannot
  certify itself via the EW average), reason-coded quarantine assembly — REAL_TAIL rows are never
  quarantined; no function mutates values.
- `membership.py` — PIT membership normalize/stitch with 2016 overlap cross-validation (Jaccard table),
  joiners/leavers audit, Shumway corrections with per-application audit log and citation (input never
  mutated), `members_asof`/`top30_at` strictly-prior selection (PIT leakage assertions in tests).
- `reconcile_full.py` — two-vendor reconciliation with discrepancy clustering (ex-div / split day /
  index-exit window / unexplained→quarantine), per-field vendor-authority merge (column-wise only;
  cell-wise blending would fabricate an unpublished series).
- `panel.py` — as-of join framework (`AsOfFeature` declares availability lag; the only sanctioned join),
  gold construction (returns panel, cash features via `src/features.py`, EW market proxy, top-30 per
  window when membership+mcap exist), `materialize_splits` = PREREG §6 exact (dev train/val, 8
  walk-forward folds 2018–2025, 21-trading-day embargo at every boundary, CPCV 16 purged blocks) as
  explicit session lists; parquet artifacts with lineage.
- `eda.py` — ADF/KPSS, moments, Hill left-tail estimator, |r|-ACF + ARCH-LM, rolling mean pairwise
  correlation, cross-sectional dispersion, drawdown anatomy, naive reconstitution turnover; every figure
  captioned with the design choice it motivates; headless matplotlib.
- `quality.py` — weighted per-series quality score, coverage matrix, scoreboard, lineage map renderer,
  Gebru et al. datasheet generator (auto-filled from manifests, ⟨TBD⟩ when empty), data-chapter seed
  paragraphs (one per stage, real numbers injected when available).
- `cli.py` — `python -m src.data.cli {probe,pull,build,validate,reconcile,eda,status}`; per-stage run
  sidecars (config hashes, wall-clock, counts); graceful vendor degradation recorded as explicit SKIP.
- Makefile targets: `data-probe data-pull data-build data-validate data-reconcile data-eda data-status`.

### Added — tests (68 → 113; all offline, synthetic fixtures in tmp dirs only)
- `tests/conftest.py` — `data_root` fixture redirects every platform module's ROOT to tmp.
- `tests/test_features.py` — truncation/future-perturbation invariance, lagged VIX, zero-variance ratio,
  env integration (dims, accounting equality, NaN rejection).
- `tests/test_sandbox.py` — 15-case static denial corpus (multi-import bypass, np.load/.lib/DataSource,
  dunders, eval/getattr/open, class/decorator/yield/global, oversized, missing compute_reward, syntax),
  numpy-idiom acceptance incl. real `import numpy as np` execution, malformed-runtime corpus (wrong arity,
  NaN, component-name instability), infinite-loop kill, Linux-gated memory bomb, result-validation bounds.
- `tests/test_rewards_baselines.py`, `test_reward_family.py`, `test_calibrate_lambda.py`,
  `test_regimes.py` (truncation invariance proves filtering-not-smoothing), `test_candidate_archive.py`,
  `test_dry_run.py`.
- `tests/test_data_vault.py` (write-once, tamper detection, lineage chains), `test_data_acquire.py`
  (governor spacing, backoff, journal resume idempotence, env loader), `test_data_validate.py` (schema,
  XNYS MLK-day alignment, conflicts, missing conservation), `test_data_integrity.py` (split recorded-vs-
  suspect, IP screens, REAL_TAIL preservation vs lone-crash quarantine), `test_data_membership.py`
  (splice/overlap, Shumway log + non-mutation, strictly-PIT top-30), `test_data_panel.py` (as-of lag,
  PREREG-§6 embargo-exact splits, gold leakage assertion, golden determinism), `test_data_security_master.py`,
  `test_data_property.py` (hypothesis: softmax/drift distributions, missing-cell conservation, chunk
  partitions, quality bounds), `test_data_cli_and_quality.py` (offline probe report, status, reconciliation
  clustering, authority merge, datasheet honesty).

### Added — configuration
- `config/environment.yaml`: `state.vol_short_window/vol_long_window/vix_scale`; `reward_defaults` for
  cvar_penalised_mean / drawdown_penalised / turnover_penalised (scale-parity comments).
- `config/eureka_loop.yaml`: `reward_family` search space (weight ranges, α choices, window choices).
- `config/data.yaml`: `platform` block (layers, manifests, lineage, journal, quarantine, evidence, runs,
  XNYS calendar + explicit `calendar_start`, chunking, rate limits, outlier taxonomy thresholds,
  vendor-authority rules, quality weights).
- `config/llm.yaml`: PIN_ME resolved — primary `claude-sonnet-4-6` @ $3/$15 per MTok (verified on the
  official models overview 2026-06-10; dateless 4.6-generation ids are documented pinned snapshots);
  open-weights companion `deepseek-ai/DeepSeek-V3-0324` (dated HF checkpoint) (ADR-016).

### Added — governance & docs
- Git repository initialized (the project was previously inside the home-directory repo); two commits:
  `75a697c` scaffold + W15 build-out, `0af2ee9` data platform.
- `DECISIONS.md`: ADR-007 … ADR-016 appended (features, sandbox+archiver, baselines, family+λ-rule,
  filtered HMM, platform architecture, dependencies, build-box environment, entitlement outcome,
  LLM pin).
- `docs/evidence/entitlement_report.md` + `entitlement_probes.json` (live probe evidence).
- `docs/DATASHEET_v1.md`, `reports/eda_v1.md` + `reports/figures/*`, `reports/data_quality_scoreboard.md`,
  `reports/data_chapter_seeds.md`, `docs/evidence/lineage_map.md` — all generated from REAL pulled data.
- `CHANGELOG.md` (this file) and `reports/session_report_2026-06-10.md`.

### Changed
- `src/sandbox.py` — full hardening rewrite (ADR-008): AST static gate replaces the bypassable string
  check; per-resource best-effort rlimits clamped to current hard limits (fixes pre-existing macOS
  `RLIMIT_AS` crash that failed `test_benign_candidate_executes`); minimal subprocess env (no inherited
  secrets, BLAS threads pinned); runtime `__import__` restricted to numpy (previously `None`, which broke
  the mandated `import numpy as np`); parent-side contract validation incl. component-name stability.
- `src/regimes.py` — explicit scaled forward recursion over public fitted parameters replaces private
  hmmlearn APIs; filtering proven causal by truncation invariance (ADR-011).
- `src/feedback_schema.py` — `empirical_cvar` now self-enforces ascending input (R5 made structural);
  `build_feedback` alpha grid defaults from config instead of a duplicated literal.
- `src/data/cli.py` — Ince–Porter price screens fed RAW close instead of adjusted close (the $1 threshold
  is about actual traded microstructure; split-adjustment retroactively drags early AAPL below $1). The
  v1 pilot quarantine (13 rows) was produced under adjusted prices — values were never mutated and
  clean/gold are unaffected; the corrected screens apply from the next build.
- `src/data/acquire.py` — FRED keyless path: date-chunked public fredgraph CSV (full-range requests 504 at
  FRED's gateway; pandas-datareader's combined request times out identically).
- `src/pull_pilot.py`, legacy tests — semicolon statements split; `make lint` now actually passes
  (pre-existing ruff failures fixed forward, no test weakened).
- `Makefile` — data-platform targets appended.
- `requirements.txt` — platform dependencies appended with ADR-013 reference (refinitiv-data, DatastreamPy,
  pyarrow, exchange-calendars, statsmodels, hypothesis, tabulate).
- `README.md`, `docs/environment_spec_v1.md`, `docs/DATA_ENTITLEMENTS.md`, `docs/week_plan_June15.md` —
  status updates to match code as built.
- `.venv` rebuilt on Python 3.12 (3.13 has no torch wheels; d3rlpy 2.8 needs torch≥2.5 which has no
  Intel-mac wheels at all → RL stack remains a 4090 install per ADR-002/ADR-014).

### Live runs (real data only — R4; nothing synthetic enters `data/`)
- Entitlement probes: Refinitiv platform session AUTHENTICATES (credentials recovered, at user direction,
  from `~/Downloads/ifte0005_phase1/.env` into gitignored `.env`; values never displayed) but carries an
  EMPTY RDP scope set — no datagrid, no historical-pricing; Workspace desktop path needs interactive
  login; DSWS connection refused (separate entitlement). Escalation email rendered (ADR-015).
- Pulls frozen to the raw vault: yfinance OHLCV+dividends+splits 2005–2025 (5 field artifacts, 5,282
  sessions × 5 pilot names), FRED {VIXCLS, DGS3MO, DGS10, T10Y2Y} (5,478 rows), Ken French daily factors
  + momentum (5,365 rows each). 8 raw artifacts, 42,618 rows, all SHA-256-manifested with provenance.
- Pipeline: staged (XNYS-aligned, validated, missing-classified) → integrity (13-row quarantine queue:
  6 sub-dollar flags + 7 Citi-2009 extreme-day reviews; tails preserved) → clean 5,282×5 (authority:
  yfinance fallback, decision recorded) → gold (returns panel, cash features, market proxy, PREREG-§6
  splits — dev val 734 post-embargo sessions starting 2015-02-03, 8 walk-forward folds) → EDA (excess kurtosis 5.75–49.9,
  Hill α 2.18–3.48 — the fat-tail evidence behind the CVaR fitness) → quality scoreboard + datasheet +
  lineage map. Every stage left a run sidecar under `runs/data/`.

### Live runs — second wave (universe-scale shadow + screen correction)
- Shadow30 pull: 30 additional real large-caps via yfinance (journaled, 2 chunks of 25; union with the
  pilot = 35 names) — explicitly a PIPELINE-SCALE proof, **not** the research universe (PIT top-30
  selection awaits entitled membership data). 18 raw artifacts total, all checksum-verified (0 failures).
- **Vendor subtlety discovered and fixed at scale**: yfinance `Close` is split-adjusted even with
  `auto_adjust=False` (NVDA's 2005 close reads $0.196 vs ~$23.5 actually traded). Added
  `integrity.reconstruct_unadjusted_close` (close × ∏ future split ratios; unit test pins the exact
  inversion) and routed the Ince–Porter $1 screen through reconstructed traded prices. Effect at scale:
  4,274 phantom sub-dollar flags → **0**; quarantine_v2 holds exactly the 49 genuine extreme-day reviews;
  34 REAL_TAIL classifications preserved.
- v2 build: clean 5,282 × 35; missing engine: 184,870 cells, 177,269 observed, 7,601 pre-IPO masked
  (TSLA/META/ABBV/AVGO… — taxonomy conservation hypothesis-tested), 0 interior gaps; EDA refreshed across
  35 names (Hill α 2.14–3.59 — uniformly fat tails). v1 `_pilot`/`_shadow30` artifacts remain manifested
  (write-once); v2 supersedes for analysis.

### Live runs — third wave (app-free Refinitiv access characterized)
- Added probe **P8 "RDP scope census"** (search/news/pricing families): token carries ZERO scopes for
  EVERY product family → cause narrowed to app-key permissions vs seat licence; BLOCKED status carries the
  app-free fix (web App Key Generator, "EDP API" box, new key in `.env`). Fixed a status-flip bug my P8
  insertion introduced (P7 MANUAL flag had moved onto P8).
- **DSWS upgraded from "unreachable" to "authenticates, service flag missing"**: probe P4 now returns
  `User not entitled to ClientApi service` — credentials are valid Datastream credentials; escalation email
  sharpened to a one-line enablement request (+ RDP scope ask). Checklist row 4 upgraded ❌→🟡.
- No machine-account credentials exist on the laptop (targeted LSEG_*/MACHINE_ID name-scan: zero hits).

### Deliberately NOT done (scope/governance)
- PREREGISTRATION.md, prompts/, and the R2 scope-lock list: UNTOUCHED.
- `lambda_frozen` remains null; the freeze (T4) and supervisor sign-off remain the author's actions.
- No Eureka-loop orchestrator / LLM client yet (post-freeze work; provider now pinned).
- No optuna (BayesOpt arm later, own ADR). No paper-trading, no scope-locked items.

## [2026-06-10] — Initial scaffold (pre-session baseline, commit 75a697c)
- Feedback schema, stats inference (PSR/DSR/MinTRL/PBO/TrialLedger), fitness, env core accounting,
  reward contract, prompts v0, configs, docs, 19-test suite (ADR-001…006).

## [2026-06-12 — completion wave] — Universe data layer COMPLETE (ADR-021)
- A2–A5 pulls finished: journal 653+ chunks frozen / 0 failed; raw vault 788+ artifacts, 5.86M+ rows.
- Third silent-form catch: `TR.TotalReturn` via get_history is empty on this route → datagrid long
  Frq=D (39 junk artifacts invalidated); mnemonic checks now read VALUES.
- Acquisition PARALLELISED on user request: thread-safe launch governor (global requests_per_minute
  respected exactly), 6 workers overlapping response latency; vault/journal lock-serialised; exact
  resume under concurrency (tested).
- `selection_buffer_months`: membership+caps acquired before window.start → dev-2005 top-30 selects on
  strictly-prior Dec-2004 data. Span-stamped artifact versioning fixed a write-once collision.
- **Research panel built (suffix _univ3, canonical):** clean 5,283×953; missing engine 5.03M cells /
  373k pre-IPO / 957k post-delisting / 3,155 interior (0.06%); top-30 at all 9 window starts
  historically exact (dev-2005: GE/XOM/MSFT/C/WMT/PFE/BAC/JNJ; 2019: MSFT>AAPL); two-vendor
  reconciliation median corr 0.99994 (35 names; 390 breaches clustered to ex-div/split);
  dev-30 EDA: excess kurtosis WB 89.4 / AIG 76.8 / C 49.8 — GFC tails inside the search window.
- D1–D6 all satisfied on entitled PIT data. _univ/_univ2 superseded (manifested, write-once).
