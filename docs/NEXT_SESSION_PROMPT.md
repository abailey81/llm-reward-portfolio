# PROMPT FOR THE NEXT CLAUDE CODE SESSION

Copy everything between the rules below into the new session as the first message.

---

Tamer here. You are taking over a LIVE, FROZEN, RUNNING confirmatory campaign for my UCL MSc
dissertation. Read this whole message before acting.

## 0. MY ORIGINAL INSTRUCTION (verbatim — it still stands in full)

> I need you to very deeply and very extensivelly analyse all documents, absolutely all that are
> here, very deeeply the changelog, handoff, and absolutely all other md docs… After you have
> attained a most comprehensive knowledge of this dissertation possible, I want you to ultarthink
> very deeply… start the full campaign run. Work very pricsely, accurately, surgically, and always
> verify very deeply… Make sure you are not lazy… Use the absolute maximum myriad can offer us to
> speed up the training to an absolute maximum. Please study all teh docs we have very carefully.
> Make sure you very closely monitor absolutely everything, the process, teh results, if they make
> sense and meaningful, everythinhing has to be extremely strcitly flawless. Dont forget to document
> everyuthing in parallel. Take as much time as you need for absolutely everything, including teh
> very advacned preparations.

Everything below is the accumulated state and the standing rights I have granted since.

## 1. STANDING RIGHTS I GRANT YOU (all of them, in force)

- **Full permissions for absolutely everything.** Act; do not ask me for routine approval.
- **Full freedom to unfreeze, amend, change, or RELAUNCH the campaign from the start** if quality
  genuinely requires it. I prioritise QUALITY very heavily over elapsed time.
- **Full laptop resource governing** (RAM, apps, power, services) — never kill VS Code, terminals, or
  live training.
- **Ratify on my behalf** where a decision is clearly implied by my priorities (standing delegation,
  2026-07-13), conditioned on ultrathinking and on the strict priorities/feedback in `CLAUDE.md`.
- **Use the absolute maximum Myriad can offer** to land this run as fast as possible.

## 2. MY STANDING DEMANDS (non-negotiable)

- **0% tolerance** for failures, issues, inconsistencies, gaps, or loose ends. Everything must be
  **strictly flawless and logical** — 10/10, 100%.
- **Ultrathink** on every non-trivial step. Work **accurately and surgically**. **Always check and
  verify** — never assert what you have not run and observed.
- **Never be lazy.** Finish the whole task; enumerate the full scope and complete all of it.
- **Monitor absolutely everything very closely** — the process, the results, whether they are
  meaningful and make sense.
- **Document everything in parallel, continuously** — CHANGELOG + HANDOFF + the cursor, even for
  sessions with no commits.
- **Address me as "Tamer" at the start of every message** (absolute rule in `CLAUDE.md`).
- **Never** add Claude/Anthropic attribution to any commit, PR, or tag. Author is
  `Tamer Atesyakar <t.ates232004@gmail.com>`.
- **Never** run `git clean -xfd`/`-x` (it destroys the licensed Refinitiv gold) or `git add -A`.
- **Never** lower SGE job priority (`qalter -p <negative>`).
- PS1 files: ASCII-only and `Parser::ParseFile`-validated. Never put backslash/escape or backtick
  content in bash heredocs or double-quoted strings — use the Write/Edit tools.

## 3. WHAT YOU ARE INHERITING — read these first, in order

1. **`docs/CAMPAIGN_EXECUTION_RECORD.md`** — THE write-up-ready account: what was run, what is
   running, what will run, the evidence, the findings, the disclosures, and the analysis-time
   obligations. **Start here.**
2. **`CHANGELOG.md` → the `[2026-07-28]` block, items ①–㉑** — the full ops chronology of the launch
   and first day.
3. **`docs/HANDOFF.md` §1** (state), **§2** (standing orders), **§3** (the authority map).
4. **`memory/session-current-focus.md`** — the ▶ NOW cursor.
5. **`CLAUDE.md`** — the ★ PRIORITIES and the four-authority rule. These govern everything.

## 4. CAMPAIGN STATE AS OF 2026-07-28 11:45 UTC

- **FROZEN** at `4f90ecc47cc6a779d63b74fdaa9667f967473365863fb615401694131ca136fd`, tag
  `prereg-v2.0`, seal commit `ce27dfc`. Records stamp `deployed-archive:ce27dfc…` and the gold
  sha256 `7cf5d988…`. HEAD `842d3c5`, pushed to `backup-2026-07-28`.
- **12/12 supervised lines alive** since launch (01:08 UTC). **590 records** (330 scored).
  Spend **$7.87** of the $30 ADVISORY (R83 — it warns, it never refuses).
- **★ THE CONFIRMATORY H2 HEADLINE WENT LIVE AT 11:39:43 UTC** — the canary gate cleared
  (`ok: True, completed: 90`), the C0 analysis-smoke gate passed, and `claude-opus-5` began authoring
  the five core LLM arms. Before that moment the confirmatory arms had authored NOTHING.
- Full test suite: **`PYTEST_RC=0`**, zero FAILED/ERROR.

## 5. THE MAKESPAN (settled — do not re-derive from scratch)

True ladder = **40,328 scored units = 326,254 core-hours** at the measured 8.09 h/scored-training
(core 20 units/seed + 10 legs × 5 arms + h3, × 568 seeds). `bayes_opt`'s **25 serial steps ×
3.59 h = 3.7 d is the FLOOR** and is immune to more cores.

| cores held | fill | makespan |
|---|---|---|
| 1,400 (rung-30 transient) | 9.7 d | 9.7 d |
| **4,000** = pack 4 × the 1,000-job cap | 3.4 d | **3.7 d — chain binds** |
| 8,000 | 1.7 d | 3.7 d — **no gain** |

**The configuration is already exactly right; raising pack buys nothing.** Low utilisation now is the
rung-30 transient: at 71 units/seed, rung 30→100 alone releases 1,243 jobs (> the 1,000 cap), so every
rung from 100 upward saturates on its own. **The ONE operational target:** once the ladder passes
rung 30, confirm we reach ~1,000 jobs / ~4,000 cores. A plateau below that WITH work pending is the
only capacity question worth asking.

## 6. FIVE CAPACITY LEVERS — MEASURED AND REFUTED. DO NOT RE-CHASE.

| lever | measurement |
|---|---|
| `tmpfs=15G` | nodes advertise 1.1–1.3 TB; we stage 71 MB. Excludes nobody. |
| `-p -100` | every queued job sits at identical normalised priority ~1.809. Immaterial. |
| `-ac allow=d` | d-class = 81 % of the cluster; we use 14 % of it. |
| job cap | 277 of 1,000. Work-limited, not cap-limited. |
| ssh multiplexing | **re-tested on OpenSSH 10.2p1**: master socket created, session dies (`Connection reset by peer`). Genuinely unavailable. |

## 7. THE ONE ACTIVE CONSTRAINT — transport

Measured from the core driver log:
`tar -xf -` timed out after **3600 s**; `find .../_rejects` after **300 s**; `qstat -r` **8
consecutive** failures over 56 min. It blocked the canary gate for 78 minutes and then **self-healed**.

**Both failing operations scale with archive size** (we are at 590 of 40,328 units), so it WILL recur
and worsen. Remedy = slower polling via a line restart, which is now CHEAP (hundreds of trainings have
completed, so re-authoring replays from the archive instead of re-billing Opus). **Do NOT restart
while the driver's retry discipline is absorbing it** — a restart injects the exact startup-probe
burst that is failing. The bound is 240 consecutive failures / 12 h; currently ~61/240 and
self-healing.

## 8. MONITORS ALREADY RUNNING (do not duplicate; verify they are alive)

- `scripts/mode_d_watchdog.ps1` — restarts any dead line every 300 s.
- `scripts/sentinel.py --watch` — the full health report.
- `scripts/campaign_backup.ps1` — **append-only** archive mirror (never `/MIR`; it would propagate a
  deletion) + harvests node-side reject logs into `docs/evidence/` every 15 min.
- `scripts/allocation_advisor.py --watch 900` — writes the capacity-accumulation telemetry.

## 9. FINDINGS ALREADY ESTABLISHED (use them; do not re-litigate)

1. **Reflection depth drives state-contract violation.** As the Eureka loop reflects, models write
   more stateful rewards and trip the documented `info["reward_state"] … or None at reset` contract.
   NoneType rejects by generation: g1 7/8 · g2 5 · g3 3 · g4 4/5. **Every frozen winner comes from
   g1–g3**; the search converges by g3. **Do NOT "fix" this** — the prompt is freeze-bound and
   softening it would erase the signal.
2. **Ratio-form baselines are numerically fragile.** ALL scored-leg fallback contamination sits in
   exactly `baseline_differential_sharpe` (5/30) and `baseline_differential_downside_ratio` (4/30);
   **0 in the other 9 arms**. Same two arms carry reward `raw_rms` 16,324 and 28,774 vs 0.015–2.33.
   One cause (near-zero denominators), two symptoms. Worst case 2 steps in 400,000.
3. **The g0 collapse was the kill incident, not capability.** 128 g0 rows are jobs that never ran.
   This resolved the apparent "83 %→0 %" for `qwen3.6-27b` (true yield g1 56 %, g2 44 %, g3 80 %).
4. **Results are meaningful** — window 1571 on all, all Sharpe finite, all CVaR ≤ 0, vol ~12–23 %
   annualised, 0 degenerate policies, and **15,312 weight snapshots with min weight 0.000e+00 and
   worst |Σw−1| 0.000e+00**.
5. **12 monitoring defects were fixed**, each one reporting something other than what it claimed to
   measure; the CAMPAIGN was correct in every case. ⚠ **CHANGELOG item ⑳ is RETRACTED** — I misread
   the driver logs as UTC when they are **LOCAL (BST = UTC+1)**; the corrected analysis is item ㉑.

## 10. WHAT TO DO NEXT

1. Verify the monitors are alive and the campaign is progressing; say
   "Resuming from: … — next: …" and CONTINUE. Do not restart cold.
2. **Watch the Opus core spend** — the largest cost event, now live. Measured $0.0822/call;
   projection ≈ $12.33 for the core line, ≈ $19.53 total against the $30 advisory ceiling.
3. **Watch for the rung-30 → rung-100 transition** and confirm saturation to ~1,000 jobs / ~4,000
   cores.
4. **Re-harvest the node reject logs before any Scratch purge** — they are the ONLY source of true
   authoring-reject reasons (the ledger degrades to a generic message because the reject marker is
   mirrored by a later pull). The backup loop does this every 15 min.
5. Keep documenting continuously.

## 10b. THE ANTHROPIC KEY — watch it, do not let it surprise you

FOUR lines bill the Anthropic key and one of them is the CONFIRMATORY arm:
  c1    Opus, CORE confirmatory   18 calls  $1.47  ->  ~$12.3 projected ($0.0814/call x 150)
  h3ss  Opus, H3 single-shot      30 calls  $2.58  ->  ~$2.6 (appears complete)
  leg8  sonnet-5                  90 calls  $1.61  ->  ~$8   (only ~1 of 5 arms done)
  leg5  haiku-4.5                 90 calls  $0.51  ->  ~$2.5 (only ~1 of 5 arms done)
  TOTAL                                     $6.17  ->  ~$25.4 projected

BALANCE: $34.84 (Tamer, 2026-07-28). Headroom ~$9.4 — COMFORTABLE. Tamer monitors and tops up.

Watch it anyway, because if it ever ran dry the line that stops is c1 — the H2 headline — and it
would fail SILENTLY (R83: the ledger warns at 80%/100% but NEVER refuses a call). The leg figures are
extrapolated from ~1 arm each and carry the widest uncertainty in the handoff; re-read them from the
ledger rather than trusting the extrapolation. OpenRouter carries no exposure (~$2.50 for six legs).

## 11. THE ONE DECISION STILL MINE

`train_safe_default_count` is archived but **never gates winner selection** (winner =
`max(val_fitness)`), so a candidate whose reward raised on 50 %+ of steps could be frozen and the
sealed leg would inherit it. Measured: 136 candidates → 127 clean, 2 SEVERE (53.7 %, 50.0 %), both in
weak open-weight legs. **Currently 0 contaminated winners** (all 7 verified at 0/400,000) and
`check_winner_execution_quality` checks every poll. The previous session's recommendation was
**detection over amendment**. Bring it to me with evidence; do not amend the protocol unilaterally.

---

Now ultrathink, verify everything for yourself rather than trusting this summary, and continue.
