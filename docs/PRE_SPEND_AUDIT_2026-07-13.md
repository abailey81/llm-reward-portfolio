# Pre-spend deep audit — consolidated findings inventory (2026-07-13)

> Tamer commissioned the deepest audit before real money is spent. Method: 4 money-critical checks
> first-hand + **5 parallel read-only auditors** (authoring/spend · driver/resume · tiered
> orchestration · on-node worker · bank-gate readiness), every finding **verified first-hand before
> fixing**. Two waves committed: `b7173db` (money criticals) + `23f4811` (14 fixes). This file is
> the living ledger of ALL findings — nothing is closed by silence. GO/NO-GO at the bottom.

## FIXED (verified + committed)

| # | Finding (severity) | Fix |
|---|---|---|
| M1 | **Wrong author model** — cluster campaign inherited prototype.yaml's llm block, never campaign.yaml's Opus (CRITICAL) | `--llm-from campaign` default + provider↔model fail-loud guard (fires verified) |
| M2 | Spend guard no-op by default (CRITICAL) | auto-cap = 2×(LLM-arms×candidates)+60, logged |
| M3 | pack>1 h_rt default 1:30 = walltime-kill at B\* (HIGH) | auto h_rt from the measured F-curve at ×0.5 contention (+ help-text corrected: NEVER per-training) |
| M4 | `wall_clock` hardcoded 0.0 in `_archive` since inception (MED, grade-relevant) | worker elapsed threads through |
| A1-F1 | **pass-B + provider=stub default = silent stub campaign** (CRITICAL) | provider derived from llm block or fail loud |
| A1-F2 | restart without `--resume` re-authors everything, discards paid calls (CRITICAL) | dirty-archive guard fails loud |
| A1-F7 | `--max-author-calls 0` meant UNCAPPED | `is not None` (0 = forbid) |
| A1-F9 | frozen-winner `search_seed` provenance always 0 | threaded from opts |
| A1-F4 | prototype.yaml TEMP-Qwen block | REVERTED to Sonnet 4.6 |
| A3/4-F1 | **gate crash: nested env_fingerprint dict → TypeError at C3 AFTER the floor trained** (HIGH, found by 2 agents independently) | unwrap at source (run_one) + defensive census coercion |
| A4-F3 | **on-node gold loads NOT checksum-verified** (jobscript comment claimed they were; silent window mis-slice risk) (HIGH) | `verify_checksum=True` at both on-node call sites |
| A4-F4 | archival exception aborts surviving pack-mates (MED-HIGH) | per-row try; `archive_error` stamped |
| A4-F7 | `-r y` rerun retrains completed pack-mates + record divergence (MED) | `_already_archived` skip (inline + pack paths) |
| A4-F8 | laptop thermal governor (88 °C) shipped onto V100 nodes (MED) | `thermal_guardian=None` in cluster agent_cfg |
| A2-#1 | **driver acts on a STALE mirror after failed pull → double-trains completed work** (HIGH) | failed-pull cycles beat-and-wait; hazard-encoding test updated |
| A2-#2 | `shared_pull` cached failures as successes → 12 h outage bound could never trip (HIGH) | window opens on SUCCESS only; failures propagate in-window |
| A5-1..4,7 | **bank gate: 4 of 6 steps used nonexistent flags; would crash at step 1** (CRITICAL) | all six invocations rewritten to the true argparse contracts; write→verify integrity; realized-rung `--seeds` required |
| A5-5 | rehearsal mode tolerated wiring errors (false-green) (HIGH) | exit-2/argparse never tolerated; **rehearsed live — wiring certified** |
| A5-6 | SNR exhibit silently empty on the cluster layout (HIGH) | `<root>/search` + dual-layout loader |
| A5-10 | fed-delta chain order lexicographic (c10<c2) (MED) | numeric (gen, cand) sort |
| A5-12 | bundle never asserted canonical==recorded hash (MED) | fail-loud drift assert |
| A4-F12 | pack>1 needs DEFAULT GPU compute mode (suspected) | **CLOSED BY EVIDENCE**: p1pack2/3/5/8 ran 2–8 concurrent contexts on real nodes |

## PENDING — tracked, ranked (the next fix wave; NONE may be silently dropped)

| # | Finding | Severity | Plan |
|---|---|---|---|
| P1 | A2-#3 **no Eqw detection; no max_wall bound** → an Eqw array waits forever with green heartbeats | HIGH | qstat state parse + bounded Eqw dwell → qdel + drain; before GO |
| P2 | A1-F3 authoring rides out only ~31 s of API trouble (vs 12 h transport) → arm dies on a 529 window | HIGH | time-bounded outage loop around the authoring call; before GO |
| P3 | A1-F5 infra-killed candidates permanently ledgered; resume never retrains from stored source | HIGH | resume resubmits ledgered cids from stored `reward_source` (no re-author); before GO |
| P4 | A3-F2 **H3 single-shot has NO cluster path**; improvised reuse of the same roots would fabricate a null via run-id adoption | HIGH (design) | build the C5 mode with `search_h3_singleshot/` sub-roots OR hard-guard distinct roots; **Tamer decision: cluster-H3 vs laptop-H3** |
| P5 | A3-F3 mid-unit winner swap undetectable on resume | HIGH | per-unit `reward_source_hash` census in the gate + freeze-overwrite refusal |
| P6 | A3-F6 stale `TIER1_APPROVED` bypasses a RED gate | MED | mtime-postdates-report + consume-on-release |
| P7 | A5-8 no `campaign_summary.json` on the cluster mirror → DeMiguel floor silently absent; blanket except in analyze | MED | write summary at campaign end + log the exception |
| P8 | A1-F8 truncated/refused completions shipped to nodes; ledger misattributes | MED | driver-side `ast_gate` pre-check (no spawn) + `stop_reason` into failure rows |
| P9 | A4-F6 sandbox rejects invisible to the driver → 2 pointless requeue rounds each | MED | node-side durable failure marker the poll layer subtracts |
| P10 | A4-F9 `buffer_size` not stamped into specs (remote-checkout cap divergence = OOM cascade) | MED | stamp explicitly into cluster specs |
| P11 | A1-F6 resume replay reads a stale mirror (no pull before authoring loop) | MED | expose shared_pull on ClusterRun; call at resume entry |
| P12 | A2-#5 no single-driver lock (double-submit across processes) | MED | lockfile keyed on base_name |
| P13 | A2-#4 drain requeue bumps never-attempted tasks (2 purge events = permanent abandonment) | MED | bump only with qacct evidence; unbumped requeue otherwise |
| P14 | A2-#6/#7 heartbeat starvation in long pulls; local errors classed as transport | MED | beat per chunk; exception whitelist |
| P15 | A3-F4 k-seed selector mismatch (IQM-reflect vs max-single-seed freeze) | dormant (k=1) | document; wire aggregate-selector IF k=3 is ever enabled |
| P16 | A3-F7 seed-pool blocks submit serially (idles the 2nd pool) | MED (throughput) | thread the block submissions |
| P17 | A3-F8 gate budget check `>=` not exact; A3-F9 D1 cpg remainder; A3-F10 sweep continues past failed block; A3-F12 hold+no-review-gate conflict; A2-#8/#10/#11/#12; A4-F10/F11; A1-F10 | LOW batch | one cleanup pass |
| P18 | A4-F5 pack=1 inline path skips `_worker_init` (pyarrow-order SIGSEGV + thread pinning) | LOW (downgraded: p4det ran inline on real gold successfully) | call `_worker_init()` in run_one.main |

## GO/NO-GO for the real spend

**NO-GO until P1–P5 close** (each is hours, not days): Eqw watch, authoring outage tolerance,
ledger-resubmit, the H3 decision (Tamer's), and the winner-hash census. Everything else is either
fixed, evidence-closed, or bounded-cost. After P1–P5: freeze → C0 canary (which now also
analysis-smokes) → GO.
