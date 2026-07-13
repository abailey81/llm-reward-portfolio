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
| P1 | ~~A2-#3 no Eqw detection~~ | HIGH | **FIXED wave 3 (`bd05c8b`)**: state capture + 15-min dwell → harvest+qdel+drain; parser test |
| P2 | ~~A1-F3 authoring 31 s outage budget~~ | HIGH | **FIXED wave 3**: transient failures ridden out ≤2 h; non-transient immediate |
| P3 | ~~A1-F5 infra-failure permanence~~ | HIGH | **FIXED wave 3**: resume resubmits from the ledger's stored source (no re-author); test locks resubmit + recovery |
| P4 | A3-F2 **H3 single-shot has NO cluster path**; improvised reuse of the same roots would fabricate a null via run-id adoption | HIGH (design) | build the C5 mode with `search_h3_singleshot/` sub-roots OR hard-guard distinct roots; **Tamer decision: cluster-H3 vs laptop-H3** |
| P5 | ~~A3-F3 mid-unit winner swap~~ | HIGH | **FIXED wave 3**: per-unit hash census gates health + freeze-overwrite refusal |
| P6 | ~~A3-F6 stale `TIER1_APPROVED` bypasses a RED gate~~ | MED | **FIXED wave 4 (`f2bfd92`+`83125a4`)**: approval must postdate the PRIOR report (the one the reviewer saw) + consumed on release; gate test locks it |
| P7 | ~~A5-8 no `campaign_summary.json` on the cluster mirror; blanket except in analyze~~ | MED | **FIXED wave 4 (`21d89e3`)**: cluster writes an analyze-compatible summary at both terminal paths (never at the C3 stop); analyze floor-skip now LOUD |
| P8 | ~~A1-F8 truncated/refused completions shipped to nodes~~ | MED | **FIXED wave 4 (`926b814`)**: spawn-free AST pre-check at authoring; permanent F5 row; P3 never resubmits it |
| P9 | ~~A4-F6 sandbox rejects invisible to the driver~~ | MED | **FIXED wave 4 (`e9208d7`)**: durable `_rejects/<rid>.json` markers (atomic, ride the pull); PERMANENT class abandoned with zero requeue rounds; F5 row marked permanent |
| P10 | ~~A4-F9 `buffer_size` not stamped into specs~~ | MED | **FIXED wave 4 (`877f1f9`)**: cap stamped into every spec (self-contained task JSON) |
| P11 | ~~A1-F6 resume replay reads a stale mirror~~ | MED | **FIXED wave 4 (`1e4a84b`)**: resume refreshes the mirror first (3×30 s, then loud) |
| P12 | ~~A2-#5 no single-driver lock~~ | MED | **FIXED wave 4 (`d5ce18b`)**: O_EXCL lockfile + owner pid; live foreign owner refused, dead owner auto-broken (psutil — never `os.kill(pid,0)` on Windows: it TERMINATES) |
| P13 | ~~A2-#4 drain requeue bumps never-attempted tasks~~ | MED | **FIXED wave 4 (`866f1ae`)**: bumps require qacct ATTEMPT evidence; trace-less drains requeue unbumped (bounded 3); per-taskid attribution |
| P14 | ~~A2-#6/#7 heartbeat starvation in long pulls; local errors classed as transport~~ | MED | **FIXED wave 4 (`6f3bf23`)**: per-chunk pull beats; transport whitelist — local bugs crash loud on cycle 1 |
| P15 | ~~A3-F4 k-seed selector mismatch~~ | dormant (k=1) | **GUARDED wave 4 (`1654ddb`)**: `_guard_k_seed_selector` fails loud at both select sites if k>1 without an injected aggregate-aware selector |
| P16 | ~~A3-F7 seed-pool blocks submit serially~~ | MED (throughput) | **FIXED wave 4 (`1654ddb`)**: blocks drive concurrently (one thread per pool); barrier test proves overlap |
| P17 | ~~low batch: A3-F8/F9/F10/F12; A2-#8/#10/#11; A4-F10/F11; A1-F10~~ | LOW batch | **FIXED wave 4 (`7daab27`)**: exact candidate-level matched-budget (`==`, overshoot fails); cpg-remainder + gate-flag conflicts fail loud at the CLI; C4 stops at a failed block; anchored adoption regex; exhausted∩batch; qacct jobname filter (job-number reuse); epilogue via EXIT trap + `-notify`; env-fp fallback marked `capture-failed:`; resume/resubmit carry the REAL prompt. ⚠ **A2-#12: detail LOST to context compaction** (the driver was independently re-hardened by P9/P12/P13/P14 + three P17 driver fixes this wave, so the residual risk is low — disclosed, not silently dropped) |
| P18 | ~~A4-F5 pack=1 inline path skips `_worker_init`~~ | LOW | **FIXED wave 4 (`1654ddb`)**: inline path runs the same init as the pack path (preload order + thread pinning). NOTE: cluster checkout NOT re-synced — the queued p4det leg-2 runs the old code, keeping the determinism pair internally consistent; the campaign syncs fresh (both legs same code) |

## GO/NO-GO for the real spend

**UPDATED (wave 4 COMPLETE, `21d89e3`…`7daab27`): every tracked finding except P4 is FIXED and
test-locked — 40 findings closed across the four waves, all suites green (full-suite capstone run
at wave-4 close). The single remaining pre-GO item is P4 — Tamer's H3 decision** (cluster C5 mode
~half a day of build, or H3 as a laptop leg; either is valid, improvised reuse of the same roots is
the only forbidden path). Two wave-4 additions beyond the tracked list: **P19** — the cluster entry
point had NO freeze gate at all (the laptop's verify-or-refuse now mirrored exactly; `--allow-unfrozen`
for rehearsals only; NOTE: any pm2 prototype RESUME now needs `--allow-unfrozen`) — and the
campaign launch line is unchanged (post-freeze, no flag). After the H3 decision:
freeze (Tamer) → C0 canary (which also analysis-smokes the reader path) → GO.
