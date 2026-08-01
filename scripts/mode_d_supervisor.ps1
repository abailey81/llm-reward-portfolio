# MODE-D LINE SUPERVISOR - one self-healing driver line (core, h3, or one replication leg).
#
# The mode-D campaign runs TWELVE driver lines concurrently (the Opus core + the H3 floor unit +
# 10 replication legs; docs/CAMPAIGN_DAY_RUNBOOK_2026-07-13.md s.10). Each line gets its own
# supervisor instance (this script): relaunch on any nonzero exit, because the driver is idempotent
# (archive-truth resume, P12 lock auto-break, no authoring re-billed) and running arrays on Myriad
# are never affected by a laptop-side death.
#
# USAGE (normally via mode_d_launch.ps1, which spawns all twelve):
#   powershell -ExecutionPolicy Bypass -File scripts\mode_d_supervisor.ps1 -Line core
#   powershell -ExecutionPolicy Bypass -File scripts\mode_d_supervisor.ps1 -Line deepseek-v4-pro
# Stop everything deliberately: create outputs\campaign_cluster\STOP_CAMPAIGN (shared, checked
# between attempts by every line), or Ctrl+C individual windows.
#
# =====================================================================================
# REWRITTEN 2026-07-27 (the launch gate). The previous version could not have run this
# campaign. Every item below was verified against the code before being changed:
#
#  1. IT WAS GPU-ONLY. Every line passed "--pool EF" and a GPU "--seed-pool-blocks EF:...,L:..."
#     stripe. The confirmatory lane is now CPU (R107/R108), and run_campaign_cluster REFUSES
#     "--device cpu" together with "--seed-pool-blocks" by design - a CPU job pins no pool, so the
#     stripe would assert a device stratification the run does not have. The launcher could not
#     start on the lane it was meant to launch.
#
#  2. THE CORE LINE HAND-TYPED 7 OF THE FROZEN 9 ARMS. cma_es and tpe - two of the four
#     comparators of CONFIRMATORY node N4 - were missing, exactly the drift that hit --baselines
#     when the H1 canon went 4 -> 11. The roster is no longer typed here at all: omitting --arms
#     under --tiered makes the launcher resolve the frozen config roster (resolve_cluster_arms),
#     and passing a partial list is now refused before ssh.
#
#  3. EVERY LEG LINE WOULD HAVE DIED AT ARGV PARSING. They passed "--priority -200".."-290", and
#     finding #96 made a negative priority a hard SystemExit unless --allow-deprioritise is given.
#     All ten lines would have exited non-zero and this supervisor would have relaunched them
#     forever at 600s backoff. The ladder is also RETIRED BY R101 (all 11 full-loop models run at
#     EQUAL standing), and Tamer's standing rule is that our jobs never sit below full fair-share.
#     So no line passes --priority at all now: the default is 0, which is what R101 requires.
#
#  4. R101 LOCKSTEP WAS NEVER IMPLEMENTED. Legs were pinned at "--seeds 0-29", the leg_seed_tier:30
#     floor that R101 explicitly retired. Every line now climbs the SAME registered ladder
#     [30,100,189,279,340,403,568]: the core and the legs via --tiered, H3 across the full seed
#     range in one line instead of the old manual "re-run later at 0-567" step.
#
#  5. THE GOLD PANEL WAS NOT WHERE THE LAUNCHER LOOKS. --gold-dir defaults to
#     ~/Scratch/llmrp/inputs, which exists on Myriad and is EMPTY; the licensed panel is on ACFS.
#     Passed explicitly below and verified sha256-against-the-frozen-manifest at launch.
# =====================================================================================

param(
    [Parameter(Mandatory = $true)][string]$Line,
    [int]$StaggerSecs = 0,
    # The ACFS path holding the licensed gold. Verified at launch by assert_remote_gold(): the
    # panel must be present AND its sha256 must equal the frozen manifest, or the run refuses.
    [string]$GoldDir = "/acfs/users/ucestes/gold",
    # Nodes fenced off. A node that fails a job in SECONDS is always free, so the scheduler keeps
    # feeding it work: a job vacuum. node-d00a-230 has no apptainer and ate 13 ladder cells.
    # EXTEND THIS if the sentinel's host_failure_concentration check fires, then restart the line.
    [string]$ExcludeHosts = "node-d00a-230",
    # RUN GENERATION (added 2026-07-28, after RUN 1 was invalidated by the cross-line reject-marker
    # collision - docs/CAMPAIGN_EXECUTION_RECORD.md s.11.2). A clean re-execution needs a fresh
    # archive on BOTH sides, and BOTH were hardcoded here:
    #   OutDir     - the LOCAL mirror. Also the root every line's driver_status/ and ledger/ live
    #                under, and the root the killswitch reads, so a fresh one also means the
    #                previous run's task deaths are invisible to the new run's admin-kill detector.
    #   RemoteRoot - the SCRATCH working root. This one is not optional: the previous run's jobs
    #                keep archiving into it for hours after a halt, and archive-truth resume would
    #                ADOPT their records - the exact hazard the 2026-07-27 launch gate caught with
    #                8 foreign probe records in the confirmatory search root.
    # The deployed code tree (~/llmrp) and the licensed gold (-GoldDir, on ACFS) do NOT move, so
    # provenance stamps and the gold sha256 are unchanged: same code, same data, same frozen hash.
    [string]$OutDir = "outputs\campaign_cluster",
    [string]$RemoteRoot = "~/Scratch/llmrp"
)

$ErrorActionPreference = "Continue"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

$outDir   = $OutDir
$stopFile = Join-Path $outDir "STOP_CAMPAIGN"
New-Item -ItemType Directory -Force $outDir | Out-Null
$safe     = ($Line -replace "[^a-zA-Z0-9_-]", "_")
$logFile  = Join-Path $outDir ("supervisor_{0}.log" -f $safe)
# The DRIVER's own stdout/stderr, kept separate from the supervisor's few lines so a 23-day
# driver log never buries the relaunch history that says whether the line is healthy.
$driverLog = Join-Path $outDir ("driver_{0}.log" -f $safe)

$py = Join-Path $repo ".venv\Scripts\python.exe"   # ABSOLUTE (2026-07-18 drill)

# Queue order - the ORDER only (R101 retired the priority ladder; these are all equal now).
# Must match config/preregistration.yaml model_suite.queue_order exactly; tests/test_mode_d.py
# locks the labels across files.
$legTag = [ordered]@{
  "deepseek-v4-pro" = "leg1"; "glm-5.2" = "leg2"; "qwen3.6-27b" = "leg3"; "qwen3.5-9b" = "leg4";
  "haiku-4.5" = "leg5"; "gpt-5.6-luna" = "leg6";
  "nemotron-3-super" = "leg7"; "sonnet-5" = "leg8"; "gemini-2.5-flash" = "leg9"; "kimi-k3" = "leg10"
}

# ---------------------------------------------------------------------------------------------
# THE CPU-LANE SUBSTRATE FLAGS, shared by EVERY line so no line can drift from another.
# Each one is backed by a measurement taken 2026-07-27; see docs/CAMPAIGN_LAUNCH_READY_2026-07-27.md
# s.4 and the R107 register.
#
#   --device cpu            the confirmatory lane. GPUs are not reachable at our priority floor
#                           (a GPU probe sat queued 42 min with 24 advertised free).
#   --pool d                294 nodes x 36 = 10,584 Intel Xeon cores. The t pool (AMD EPYC) is
#                           excluded by lanes.EXCLUDED_CPU_POOLS: different oneDNN kernels change
#                           float reduction order and would break CRN bit-exactness.
#   --pack 4                4 INDEPENDENT trainings per job, ONE CORE EACH, so 100% efficient
#                           (packing is not threading). 4-core jobs place in ~6 min; 1,000 jobs x 4
#                           = the 4,000-core ceiling that max_u_jobs allows.
#   --cores-per-training 1  the test flood is throughput work: 8 separate 1-thread trainings give
#                           ~104 steps/s aggregate against ~35 for one 8-thread training.
#   --search-pack 1         the SEARCH lane runs one training per job so that, at 8 threads, the
#   --search-threads 8      job asks for max(1,8) x 1 = 8 cores (places in ~19 min) instead of
#                           8 x 4 = 32 (past the placement cliff). 8 threads is the REGISTERED
#                           chain_thread_count (R107, ratified; NEVER exceed 8, 16 is slower), and
#                           it is worth ~2.7x on the two things that gate everything: the 6-step
#                           reflection chain and bayes_opt's 25-step serial GP chain.
#   --chunk-tasks 1         arrays are SERIALISED by policy (tasks 2..n sit in hqw) and pending
#                           tails have twice been PURGED outright. One job per task, no tail.
#   --poll-secs 180         burst cadence.
#   --search-poll-secs 45   chain cadence: every chain handoff pays up to one poll of notice, and
#                           the BO chain has 25 of them.
#   NO --priority           default 0 = full fair-share standing (R101 + Tamer's absolute rule).
#   NO --seed-pool-blocks   refused on the CPU lane, and correctly so.
#   NO --arms / --baselines resolved from the FROZEN config; a hand-typed list drifts.
# ---------------------------------------------------------------------------------------------
# --pack 8 (2026-07-31, DEFERRED_FIXES 11 / record sections 50 and 58). C4 ONLY - INERT during
# search, which uses --search-pack 1 (run_search_arm takes pack=(run.search_pack or run.pack)), so
# changing it does not touch the running search phase. At C4 run_test_leg takes run.pack, giving 8
# trainings per 8-slot job instead of 4 per 4-slot job: the SAME job width and therefore the same
# placement profile, for twice the trainings per placed job. Memory renders 2G/slot = 16 GB/job
# (verified against the renderer), so 500 concurrent jobs reserve 7.8 TB against ~12 TB free.
# Pack is OUTSIDE the determinism envelope -- pack-mates are separate spawned processes with
# OMP=1 (330 packed CPU baselines in this run prove the path) -- so this buys wall-clock without
# touching arithmetic. Measured justification: at the cores held on 2026-07-31 rung 568 lands
# 08-30, MISSING the 08-27 exogenous stop; pack 8 roughly halves the C4 makespan.
$cpuLane = @(
  "--device", "cpu", "--pool", "d",
  "--pack", "8", "--cores-per-training", "1",
  "--search-pack", "1", "--search-threads", "8",
  "--chunk-tasks", "1",
  "--exclude-hosts", $ExcludeHosts,
  "--gold-dir", $GoldDir,
  "--remote-root", $RemoteRoot,
  "--poll-secs", "180", "--search-poll-secs", "45",
  "--output-dir", $outDir, "--resume"
)

if ($Line -eq "h3") {
    # THE H3 FLOOR UNIT: the pre-registered single-shot control (generations=1, no reflection),
    # same candidate budget and agent config. Its own invocation, archived to disjoint
    # *_h3_singleshot/ roots. --tiered is refused here by design (C5 vs C1-C4), so R101 lockstep is
    # expressed as the FULL seed range in ONE line rather than the old "0-29 now, 0-567 later"
    # two-step, which was a manual dependency on every rung bank.
    $driverArgs = @(
      "scripts/run_campaign_cluster.py", "--h3-singleshot",
      "--seeds", "0-567", "--pass-mode", "B", "--llm-from", "campaign",
      "--batch-tag", "h3ss"
    ) + $cpuLane
} elseif ($Line -eq "core") {
    # THE CORE LINE - the frozen 9-arm roster (RESOLVED, never typed) + the frozen 11-name H1 canon
    # (also resolved), climbing the registered assurance ladder with the rungs pipelined.
    $driverArgs = @(
      "scripts/run_campaign_cluster.py", "--tiered",
      "--pass-mode", "B", "--llm-from", "campaign", "--pipeline-rungs",
      "--batch-tag", "c1"
    ) + $cpuLane
} elseif ($legTag.Contains($Line)) {
    # A REPLICATION LEG - the identical five LLM feedback arms authored by this leg's pinned model,
    # archived under leg_<label>/ (forced by --leg). It carries NO H1 canon (those eleven rewards
    # are hand-designed and model-INDEPENDENT, so they belong to the core line exactly once) and no
    # DFO arm. Under R101 it climbs the SAME ladder as the core, at the SAME priority.
    $driverArgs = @(
      "scripts/run_campaign_cluster.py", "--leg", $Line, "--tiered",
      "--pass-mode", "B",
      "--batch-tag", $legTag[$Line]
    ) + $cpuLane
} else {
    Write-Host ("unknown line '{0}' - use 'core', 'h3', or a leg label from config/legs.yaml" -f $Line)
    exit 2
}

function Log([string]$msg) {
    $l = "{0} | supervisor[{1}] | {2}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Line, $msg
    Write-Host $l
    Add-Content -Path $logFile -Value $l
}

if ($StaggerSecs -gt 0) {
    # Poll staggering: twelve lines polling qstat/rsync in lockstep would burst the login node -
    # offset each line's start so the poll phases spread out.
    Log ("staggering start by {0}s" -f $StaggerSecs)
    Start-Sleep -Seconds $StaggerSecs
}

$attempt = 0
$maxAttempts = 1000
$backoffSecs = 600

Log ("line supervisor started: {0}" -f ($driverArgs -join " "))
while ($attempt -lt $maxAttempts) {
    if (Test-Path $stopFile) { Log "STOP_CAMPAIGN present - deliberate stop."; break }
    $attempt += 1
    Log ("attempt {0}: launching the driver" -f $attempt)
    $rc = -1
    try {
        # CAPTURE THE DRIVER'S OWN OUTPUT (2026-07-28, added during the launch itself).
        # Without this the driver's stdout/stderr goes only to the spawned console window, so its
        # WARNINGs are unreadable to anyone not sitting at the machine. That gap bit immediately:
        # within the first hour the heartbeat reported "N consecutive pull/ops failures" and the
        # driver had logged the exact exception behind it -- to a window nobody can read. For a
        # 23-day unattended run the diagnosis has to survive in a file. Tee, not redirect, so the
        # console still shows it live.
        # Out-File -Encoding utf8, NOT Tee-Object: PowerShell 5.1's Tee writes UTF-16LE, which
        # makes every grep/Select-String over the log return nothing (each character separated by a
        # NUL byte). A log you cannot search is not a log. The console copy is not worth having --
        # nobody reads the spawned window, which is the whole reason this redirect exists.
        & $py @driverArgs 2>&1 | Out-File -FilePath $driverLog -Encoding utf8 -Append
        if ($null -ne $LASTEXITCODE) { $rc = $LASTEXITCODE }
    } catch {
        Log ("driver INVOCATION failed before start: {0}" -f $_.Exception.Message)
        $rc = -1
    }
    if ($rc -eq 0) { Log "driver exited 0 - LINE COMPLETE."; break }
    # D12 (applied 2026-08-01, record s.97). A GATE STOP IS NOT A SUCCESS AND IS NOT A CRASH.
    # Before this branch existed the driver returned 0 on a gate stop, so the line above logged
    # "LINE COMPLETE" and exited - six legs reported complete on 2026-07-29 having produced nothing.
    # The driver now returns 3 (EXIT_AWAITING_REVIEW), and WITHOUT this branch that would fall
    # through to the relaunch line below and spin the line in a backoff loop forever.
    #
    # URGENT BECAUSE OF D16 (same commit): folding the substrate census into the gate's health_ok
    # makes stops MORE likely, so an unhandled stop code would have turned the CONFIRMATORY line
    # into a silent relaunch loop. The two fixes are hard-coupled.
    #
    # Release: review the effect-blind report, then create TIER1_APPROVED_<line_tag> under the read
    # root and re-run with --approve-tier1 --resume. The watchdog decides "dead line" by process
    # ABSENCE, not by exit code (verified in mode_d_watchdog.ps1 / docs/ops/watchdog_fenced.ps1),
    # so breaking here does NOT trigger an automatic revival of this supervisor.
    if ($rc -eq 3) {
        Log "driver exited 3 - STOPPED AT THE REVIEW GATE, awaiting approval. NOT relaunching."
        break
    }
    Log ("driver exited {0} - relaunching in {1}s; Myriad arrays unaffected" -f $rc, $backoffSecs)
    Start-Sleep -Seconds $backoffSecs
}
Log "line supervisor exiting."
