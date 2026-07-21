# MODE-D LINE SUPERVISOR (2026-07-21) - one self-healing driver line (core OR one leg).
#
# The mode-D campaign runs TEN driver lines concurrently (the Opus core + 9 replication legs;
# see docs/CAMPAIGN_DAY_RUNBOOK_2026-07-13.md s.10). Each line gets its own supervisor instance
# (this script) with the same self-healing contract as campaign_supervisor.ps1: relaunch on any
# nonzero exit (the driver is idempotent - archive-truth resume, P12 lock auto-break, no
# authoring re-billed); running arrays on Myriad are never affected by a laptop-side death.
#
# USAGE (normally via mode_d_launch.ps1, which spawns all ten):
#   powershell -ExecutionPolicy Bypass -File scripts\mode_d_supervisor.ps1 -Line core
#   powershell -ExecutionPolicy Bypass -File scripts\mode_d_supervisor.ps1 -Line deepseek-v4-pro
# Stop everything deliberately: create outputs\campaign_cluster\STOP_CAMPAIGN (shared, checked
# between attempts by every line), or Ctrl+C individual windows.

param(
    [Parameter(Mandatory = $true)][string]$Line,
    [int]$StaggerSecs = 0
)

$ErrorActionPreference = "Continue"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

$outDir   = "outputs\campaign_cluster"
$stopFile = Join-Path $outDir "STOP_CAMPAIGN"
New-Item -ItemType Directory -Force $outDir | Out-Null
$safe     = ($Line -replace "[^a-zA-Z0-9_-]", "_")
$logFile  = Join-Path $outDir ("supervisor_{0}.log" -f $safe)

$py = Join-Path $repo ".venv\Scripts\python.exe"   # ABSOLUTE (2026-07-18 drill)

# The five LLM arms every replication leg runs (model_suite: "the identical five LLM arms").
$legArms = @("distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled")
# Queue order + the -p ladder (-200..-280): must match model_suite.queue_order exactly.
$legPriority = @{
  "deepseek-v4-pro" = -200; "glm-5.2" = -210; "qwen3.6-27b" = -220; "qwen3.5-9b" = -230;
  "haiku-4.5" = -240; "sonnet-4.6" = -250; "gpt-5.6-luna" = -260; "nemotron-3-super" = -270;
  "gemini-3.5-flash" = -280
}
$legTag = @{
  "deepseek-v4-pro" = "leg1"; "glm-5.2" = "leg2"; "qwen3.6-27b" = "leg3"; "qwen3.5-9b" = "leg4";
  "haiku-4.5" = "leg5"; "sonnet-4.6" = "leg6"; "gpt-5.6-luna" = "leg7";
  "nemotron-3-super" = "leg8"; "gemini-3.5-flash" = "leg9"
}

if ($Line -eq "core") {
    # THE CORE LINE - the s.2 canonical line + the mode-D levers (search lane pack-2, pipelined rungs).
    $driverArgs = @(
      "scripts/run_campaign_cluster.py", "--tiered",
      "--arms", "distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled",
                "random_search", "bayes_opt",
      "--baselines", "raw_return", "return_minus_variance", "return_minus_cvar", "differential_sharpe",
      "--pass-mode", "B", "--llm-from", "campaign",
      "--pack", "5", "--search-pack", "2", "--search-poll-secs", "45", "--pipeline-rungs",
      "--cores-per-training", "1", "--pool", "EF",
      "--seed-pool-blocks", "EF:0-14,L:15-29,EF:30-64,L:65-99,EF:100-143,L:144-188,EF:189-233,L:234-278,EF:279-308,L:309-339,EF:340-370,L:371-402,EF:403-484,L:485-567",
      "--batch-tag", "c1", "--poll-secs", "180", "--chunk-tasks", "1",
      "--output-dir", $outDir, "--resume"
    )
} elseif ($legPriority.ContainsKey($Line)) {
    $driverArgs = @(
      "scripts/run_campaign_cluster.py", "--leg", $Line,
      "--arms") + $legArms + @(
      "--seeds", "0-29", "--pass-mode", "B",
      "--priority", [string]$legPriority[$Line],
      "--pack", "5", "--search-pack", "2", "--search-poll-secs", "45",
      "--cores-per-training", "1", "--pool", "EF",
      "--seed-pool-blocks", "EF:0-14,L:15-29",
      "--batch-tag", $legTag[$Line], "--poll-secs", "180", "--chunk-tasks", "1",
      "--output-dir", $outDir, "--resume"
    )
} else {
    Write-Host ("unknown line '{0}' - use 'core' or a leg label from config/legs.yaml" -f $Line)
    exit 2
}

function Log([string]$msg) {
    $l = "{0} | supervisor[{1}] | {2}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Line, $msg
    Write-Host $l
    Add-Content -Path $logFile -Value $l
}

if ($StaggerSecs -gt 0) {
    # Poll staggering: ten lines polling qstat/rsync in lockstep would burst the login node -
    # offset each line's start so the 180s poll phases spread out.
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
        & $py @driverArgs
        if ($null -ne $LASTEXITCODE) { $rc = $LASTEXITCODE }
    } catch {
        Log ("driver INVOCATION failed before start: {0}" -f $_.Exception.Message)
        $rc = -1
    }
    if ($rc -eq 0) { Log "driver exited 0 - LINE COMPLETE (or gate stop handled)."; break }
    Log ("driver exited {0} - relaunching in {1}s; Myriad arrays unaffected" -f $rc, $backoffSecs)
    Start-Sleep -Seconds $backoffSecs
}
Log "line supervisor exiting."
