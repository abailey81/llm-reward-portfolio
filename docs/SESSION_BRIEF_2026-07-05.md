# Session brief for Tamer — decisions owed + gated work (2026-07-05)

The 2026-07-05 deep review is complete. Everything **safe + non-hash-bound** is fixed and verified (see
`docs/DEEP_REVIEW_2026-07-05.md`; gate 17/17 @ `1c6b76b6`, frozen:false, PDF 0-warn, citations clean). What
remains needs **your** decision or is gated. Ordered by leverage.

## A. THE freeze blocker (unchanged — this is the gate)
1. **Ratify the seed count (~350 arm-adaptive).** σ_D=0.369 fires the pre-registered ">0.10 → raise seeds"
   trigger, so **30 is provably wrong** and `determine_design` now correctly reports **BLOCKED on n_seeds**
   (fixed this session — it used to lie FREEZE-READY at 30). Decision = arm-adaptive ~350 on the 2 H2 arms,
   controls at 30 → ~23 days, deadline-safe. On your go it amends `campaign.yaml` + `preregistration.yaml` +
   PREREG §6 prose, then freeze. This is the one thing standing between here and freeze.
2. **Okhrati's reply** (email sent; pivot sign-off on `docs/PROPOSAL_PIVOT_DISCLOSURE.md` still owed).

## B. Pre-freeze design decisions surfaced this session (all improve the grade; all your call)
3. **§9 nine-vs-four baseline panel** — frozen §9 promises NINE hand rewards "reported as a secondary panel";
   the pipeline runs only the 4-name H1 family. **Council (both seats): amend §9 to a two-tier design** — 4-name
   confirmatory @ full seeds (unchanged) + the 5 extras (drawdown, downside/Sortino, log-growth/Kelly distinct;
   MV-utility/turnover near-dup) as a **descriptive panel @ ~10 seeds, excluded from best-of selection**, ~1
   trailing GPU-day. Answers the examiner's "sophisticated rewards or strawmen?" — this is also the "advanced
   hand-written reward functions" you asked for. **Decision: run the 5 extras (Y/N) + at how many seeds.**
4. **Add a min-CVaR (Rockafellar-Uryasev) allocator** — the one genuinely missing benchmark, the natural
   tail-aware comparator in a CVaR study, analysis-time / ~free compute. Needs a one-line §9 amendment.
   **Recommend: yes.**
5. **Freeze-gate hardening (council: adopt, as ONE batched hash move with the seed amendment)** —
   `assert_generations_match` (6 & H3=1 are design-defining but un-guarded), author-model prereg mirror,
   tail-neutrality prompt check, search-splits cross-assert, bound-file existence assert. All close evidenced
   gaps; batching them into the seed-amendment commit avoids dribbling hash moves. **Decision: adopt all / a
   subset / defer.**
6. **R76 hash-bound wording batch** (authorized-pattern, no decision changes): PREREG §4 "log-returns" →
   "simple (arithmetic) returns" (the code uses simple; R55 fixed the code, missed this sentence);
   `inference.yaml:1` header points to a nonexistent `src/stats_inference.py` + wrong section. Fold into the
   seed-amendment commit. **Decision: batch it in (Y/N).**
7. **H2-Tail TOST margin** (M11) — the frozen tail-equivalence margin is ±0.05 in raw CVaR units (near-vacuous
   at daily scale); the code default uses a 25%-of-|scalar-CVaR| fractional margin that is **unregistered**.
   Since the tail leg is the ONE place equivalence could actually land (cvar σ_D is tight), register the
   fractional margin ex-ante or the "post-hoc margin" attack is open. **Decision: register the fractional
   margin pre-freeze / keep raw + disclose / drop tail-TOST to descriptive.**

## C. Data wins already on your disk (report-only, no amendment for report-only rows; do at analysis time)
8. **`.SPXTR` true market benchmark** — on disk, zero consumers; closes the self-reported "no cap-weighted
   benchmark" limitation. **Best single data win.**
9. **Bid/ask spread EDA** — on disk, zero consumers; grounds the frozen cost grid in your own data (Okhrati's
   motivate-with-data). Grid stays frozen.
10. **Pull BAB/QMJ + FF5 daily** (free, ~1h) — fulfils the *already-frozen* attribution `controls_for`; without
    them the ff5/ff6/BAB/QMJ attribution rungs report "skipped" and BAB is the pre-registered headline rival.

## D. Code work that needs care (not rushed; mostly post-campaign timing)
11. **Mechanism-kernel rewire (M13/M14)** — the SQ1 responsiveness + mediation instruments currently use each
    candidate's OWN post-training measured tail as "the fed signal", not the tail the designer was actually FED
    (previous generation's best block, which IS in the archived prompt). Also levels-not-deltas + gen-0
    inclusion. This is the **originality headline instrument**, report-only + disjoint from m=6, and it runs
    **post-campaign** — so there is time to do it right: fix to the registered estimand (Δ fed-tail vs Δ
    authored-feature), add regression tests, validate on the prototype archive. **I recommend doing this as a
    dedicated pre-analysis task, not under token pressure.**
12. **Verify H3-pooling (M15)** — under `--h3-singleshot` + analyze-on-parent-root, H3 single-shot candidates
    may pool into the distributional arm's records (colliding run_ids, global de-dup by run_id). Needs a
    first-hand trace of whether the collision actually fires; if so, exclude the `*_h3_singleshot/` subtree from
    `load_campaign_records` or namespace the run_ids.
13. **H1/H3 parallel-husk status (M19)** — the parallel H1/H3 test path banks status='tested' (exit 0) even on a
    total failure wave (0 records). Serial is fail-loud. Worth a status fix before the real run.

## E. Ops you already knew about
14. OpenRouter key → `smoke_qwen`; Anthropic credit glance (~$30-80 authoring); OSF account + deposit at freeze;
    run-day §0b checklist (Turbo, WU pause, disk ≥20 GB); **`git push`** the snapshot when you're ready (remote
    is yours: `abailey81/llm-reward-portfolio`).

---
**Nothing in A–E was executed autonomously** — all are your decisions or are gated. The mechanism-kernel item
(11) is the most consequential for the grade after the seed ratification; the SPXTR + bid-ask data wins (8/9)
are the cheapest depth-per-token. The full evidenced findings list (0 crit / 19 major / 63 minor) is in the
13-auditor map; the ~60 minor doc/comment staleness items are catalogued and low-priority.
