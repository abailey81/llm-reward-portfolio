<#
.SYNOPSIS
    Register a Task Scheduler ONSTART task that re-enters the campaign after ANY reboot (ops audit C2).

.DESCRIPTION
    A 2-3-week unattended laptop run WILL see a reboot the operator did not schedule (Windows Update,
    power loss, a driver bluescreen). Without re-entry, the run silently stays down until a human
    notices — potentially days of lost wall-clock. This script registers a scheduled task that fires
    AT SYSTEM STARTUP and relaunches `scripts\supervisor.py -- <campaign args> --resume`:

      * the supervisor runs preflight, then keeps the campaign alive (bounded restarts + backoff);
      * `--resume` (also auto-appended by the supervisor itself, M7) makes re-entry idempotent —
        archived candidates/seeds replay from disk, so a reboot never re-bills the paid author;
      * stdout/stderr are appended to outputs\campaign\onstart_task.log for post-hoc forensics.

    OPERATOR-RUN ONLY — nothing in the campaign invokes this. Run it ONCE from an elevated PowerShell
    on run day (see docs/CAMPAIGN_RUNBOOK.md §0), and remove it with scripts\uninstall_onstart_task.ps1
    when the campaign completes (otherwise every future boot relaunches the supervisor; that relaunch
    is harmless — a finished campaign resumes to a no-op and exits 0 — but it is noise you don't want).

    The task runs as the CURRENT user (the .env key + the venv live in this profile) with highest
    privileges, whether or not the user is logged on (S4U logon: no password stored), with a 2-minute
    startup delay so CUDA/network services are up before training starts.

.PARAMETER TaskName
    Scheduled-task name (default: LLMRewardCampaignResume).

.PARAMETER CampaignArgs
    Argument string passed to run_campaign.py AFTER the supervisor's `--` separator. Default is the
    runbook's laptop headline invocation. `--resume` is appended by the supervisor regardless.

.PARAMETER SupervisorGpu
    n_gpu handed to the supervisor's preflight gate (default 2).

.PARAMETER Myriad
    Register the CLUSTER-driver resume task instead of the laptop one: the supervisor child becomes the
    Myriad driver (scripts\run_campaign_cluster.py), the laptop GPU clock lock is SKIPPED (the laptop
    GPU is idle — training is 100% on Myriad), and the supervisor's laptop-GPU preflight is bypassed
    (--no-preflight; the cluster's own G1 cert is the preflight). Use this for the 100%-Myriad campaign.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\install_onstart_task.ps1                 # laptop
    powershell -ExecutionPolicy Bypass -File scripts\install_onstart_task.ps1 -Myriad         # cluster
    powershell -ExecutionPolicy Bypass -File scripts\uninstall_onstart_task.ps1   # after the run
#>
param(
    [string]$TaskName = "LLMRewardCampaignResume",
    # SERIAL reflect-on-best headline (ratified 2026-07-01, corrected 2026-07-02): --search-gpu 0 is the
    # default, so the flag is simply OMITTED. (The previous default here still said "--search-gpu 2" —
    # the SUPERSEDED R24 parallel protocol; a reboot would have resumed the campaign on the WRONG
    # protocol. Found + fixed in the 2026-07-02 engineering review.)
    [string]$CampaignArgs = "--gpu 3 --h3-singleshot --no-shutdown",
    [int]$SupervisorGpu = 3,
    [switch]$Myriad
)

$ErrorActionPreference = "Stop"

# Resolve everything to ABSOLUTE paths (an ONSTART task has no useful working directory).
$repoRoot     = Split-Path -Parent $PSScriptRoot
$pythonExe    = Join-Path $repoRoot ".venv\Scripts\python.exe"
$supervisor   = Join-Path $repoRoot "scripts\supervisor.py"
$clusterEntry = Join-Path $repoRoot "scripts\run_campaign_cluster.py"
$logDir       = Join-Path $repoRoot ($(if ($Myriad) { "outputs\campaign_cluster" } else { "outputs\campaign" }))
$logFile      = Join-Path $logDir "onstart_task.log"

if (-not (Test-Path $pythonExe))  { throw "venv python not found at $pythonExe - create the venv first." }
if (-not (Test-Path $supervisor)) { throw "supervisor not found at $supervisor" }
if ($Myriad -and -not (Test-Path $clusterEntry)) { throw "cluster entry not found at $clusterEntry" }
New-Item -ItemType Directory -Force $logDir | Out-Null

# cmd.exe /c wrapper so stdout+stderr append to the log (Task Scheduler actions cannot redirect).
if ($Myriad) {
    # CLUSTER driver resume: the child is the Myriad driver (over the UCL VPN). No laptop GPU lock (the
    # laptop GPU is idle), and the supervisor's laptop preflight is bypassed. The default cluster args
    # are the tiered C-ladder over the frozen 7-arm roster; override with -CampaignArgs. The supervisor
    # (and, redundantly, the entry) append --resume so re-entry replays the archive — never re-bills.
    if (-not $PSBoundParameters.ContainsKey('CampaignArgs')) {
        # The FROZEN roster: 9 arms (config/arms.yaml, R108's 7 -> 9 with the H4 DFO portfolio) + the
        # 11-member H1 canon (config/preregistration.yaml h1_baselines, expanded 4 -> 11). Counts are
        # stated here for the operator ONLY — resolve them from config, never hand-type a roster: a
        # stale hand-typed list is what caused the 4-vs-11 launch defect. A reboot-recovery MUST resume
        # the complete, correct campaign — a wrong default would resume an incomplete/broken roster.
        # --tiered means the config seed schema (the E1 ladder [0..567]) drives the tiers; --seeds is
        # ignored here. Kept at the full ladder as a belt-and-suspenders default in case --tiered is dropped.
        $CampaignArgs = "--tiered " +
            "--arms distributional scalar placebo scalar_cvar5 placebo_shuffled random_search bayes_opt " +
            # NO --baselines: --tiered resolves the FROZEN config h1_baselines family. The old
            # hand-mirrored H1 four DRIFTED at the 2026-07-26 canon expansion (4 -> 11).
            "--seeds 0-567"
    }
    $inner = "`"$pythonExe`" `"$supervisor`" --no-preflight --campaign `"$clusterEntry`" -- $CampaignArgs --resume"
} else {
    # LAPTOP campaign. The GPU clock lock (nvidia-smi -lgc) RESETS on every reboot — re-apply it BEFORE
    # re-entering so a crash-reboot resumes under the SAME uniform conditions the pilots calibrated
    # (2026-07-02 engineering review; Turbo self-heals via Armoury Crate, the lock does not). The `&`
    # chain means a lock failure logs but never blocks the resume itself.
    $inner = "nvidia-smi -lgc 2200,2560 & `"$pythonExe`" `"$supervisor`" --gpu $SupervisorGpu -- $CampaignArgs --resume"
}
$cmdArg = "/c `"$inner >> `"$logFile`" 2>&1`""

$action    = New-ScheduledTaskAction -Execute "cmd.exe" -Argument $cmdArg -WorkingDirectory $repoRoot
$trigger   = New-ScheduledTaskTrigger -AtStartup
$trigger.Delay = "PT2M"   # let CUDA/network services settle before training re-enters
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest
# Long-running unattended compute: no execution time limit, keep going on battery, never park it.
$settings  = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Principal $principal -Settings $settings -Force | Out-Null

Write-Host "Registered ONSTART task '$TaskName':"
Write-Host "  cmd.exe $cmdArg"
Write-Host "  log -> $logFile"
Write-Host "Verify with:  Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo"
Write-Host "Remove after the campaign with:  scripts\uninstall_onstart_task.ps1"
