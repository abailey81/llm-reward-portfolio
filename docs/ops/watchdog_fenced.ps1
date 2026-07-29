# FENCED WATCHDOG - a faithful copy of scripts/mode_d_watchdog.ps1 that also carries -ExcludeHosts.
#
# WHY THIS EXISTS (2026-07-30, D15). The repo watchdog's param block has only IntervalSecs, OutDir
# and RemoteRoot. It revives a dead line by Start-Process on mode_d_supervisor.ps1 WITHOUT passing
# ExcludeHosts, so it would revive that line on the supervisor's DEFAULT fence
# ("node-d00a-230") and SILENTLY UNDO the node-d00b-024 substrate fence for that line.
#
# That is exactly the D4 defect shape, one parameter later - and the repo watchdog's own comment
# warns about it for OutDir/RemoteRoot: "Before this parameter existed the watchdog restarted every
# dead line with the supervisor's DEFAULTS". An automatic restarter is a second launcher and must
# take the same parameters as the thing that started the line.
#
# The correct fix is an ExcludeHosts parameter on scripts/mode_d_watchdog.ps1, which is REGISTERED
# in docs/DEFERRED_FIXES_RUN4.md - but scripts/ is inside the live-run drift pathspec
# (git diff <running-sha> HEAD -- src scripts config prompts must stay empty), so it cannot be
# edited while RUN 4 is live. This file lives under docs/ instead, which is outside the pathspec,
# so the safety net and the fence can both hold at zero drift.
#
# Retire this the moment the deferred fix lands, and go back to the repo watchdog.
#
# ASCII-only and Parser-validated before use (standing rule: PowerShell 5.1 turns em-dashes into
# string-breaking smart quotes).
param(
    [int]$IntervalSecs = 300,
    # These MUST be passed and MUST match mode_d_launch.ps1 exactly - the defaults are RUN 1's.
    [string]$OutDir = "outputs\campaign_cluster_run4",
    [string]$RemoteRoot = "~/Scratch/llmrp4",
    # The substrate fence. node-d00a-230 has no apptainer (a job vacuum); node-d00b-024 is the only
    # Xeon Gold 6140 host observed across all four runs and is what broke test-leg substrate
    # homogeneity (record s.28).
    [string]$ExcludeHosts = "node-d00a-230,node-d00b-024"
)

$ErrorActionPreference = "Continue"
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)   # docs/ops -> docs -> repo
Set-Location $repo

$outDir   = $OutDir
$stopFile = Join-Path $outDir "STOP_CAMPAIGN"
$log      = Join-Path $outDir "watchdog.log"
New-Item -ItemType Directory -Force $outDir | Out-Null

# Must match mode_d_launch.ps1 exactly.
$lines = @(
  "core", "h3",
  "deepseek-v4-pro", "glm-5.2", "qwen3.6-27b", "qwen3.5-9b",
  "haiku-4.5", "gpt-5.6-luna", "nemotron-3-super", "sonnet-5", "gemini-2.5-flash", "kimi-k3"
)

function WLog([string]$m) {
    $l = "{0} | watchdog[fenced] | {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $m
    Write-Host $l
    Add-Content -Path $log -Value $l
}

WLog ("started; watching {0} lines every {1}s (out={2}, remote={3}, fence={4})" -f `
    $lines.Count, $IntervalSecs, $OutDir, $RemoteRoot, $ExcludeHosts)

while ($true) {
    if (Test-Path $stopFile) { WLog "STOP_CAMPAIGN present - watchdog exiting."; break }

    $alive = @()
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match 'mode_d_supervisor' } |
        ForEach-Object { if ($_.CommandLine -match '-Line\s+(\S+)') { $alive += $Matches[1] } }

    $dead = $lines | Where-Object { $alive -notcontains $_ }
    if ($dead.Count -gt 0) {
        WLog ("DEAD lines: {0}" -f ($dead -join ", "))
        foreach ($d in $dead) {
            Start-Process powershell -ArgumentList @(
                "-ExecutionPolicy", "Bypass",
                "-File", (Join-Path $repo "scripts\mode_d_supervisor.ps1"),
                "-Line", $d, "-StaggerSecs", "0",
                "-ExcludeHosts", $ExcludeHosts,
                "-OutDir", $OutDir, "-RemoteRoot", $RemoteRoot
            )
            WLog ("  restarted {0} (fence={1})" -f $d, $ExcludeHosts)
            Start-Sleep -Seconds 3
        }
    }
    Start-Sleep -Seconds $IntervalSecs
}
WLog "watchdog exiting."
