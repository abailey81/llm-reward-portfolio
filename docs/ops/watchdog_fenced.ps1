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
# !! THE PARAGRAPH ABOVE IS HISTORY, NOT CURRENT STATE (corrected 2026-08-03).
# That ExcludeHosts deferred fix DID land: RUN 10 applied it on 2026-08-01 and
# scripts/mode_d_watchdog.ps1:52 now carries the parameter. So the original reason
# for this file no longer holds -- but do NOT retire it yet, because it has since
# acquired a SECOND reason: the P202 completion-awareness fix below, which the repo
# watchdog still lacks (scripts/mode_d_watchdog.ps1:88 is still absence-only and is
# drift-fenced, so it cannot be edited while RUN 4 is live). Registered as D31.
#
# !! AND KNOW WHICH ONE A REBOOT STARTS. The boot task `LLMRewardCampaignResume` launches
# scripts\mode_d_watchdog.ps1, NOT this file, so after a reboot the h3-style churn returns
# until D31 lands. Relaunch this file by hand after any reboot, and do not run both at
# once -- two watchdogs would race to revive the same line and start duplicate supervisors.
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

# ---------------------------------------------------------------------------
# COMPLETION AWARENESS (added 2026-08-03, defect P202).
#
# WHY. This watchdog decided "dead line" by process ABSENCE alone. A supervisor
# that finishes breaks out of its retry loop and exits (mode_d_supervisor.ps1:292,
# "driver exited 0 - LINE COMPLETE"), so a COMPLETED line looks exactly like a
# CRASHED one. Measured: the h3 line completed its full 568-seed ladder at
# 2026-08-01 20:27:46 and was then revived 278 times in ~31 hours, each revival
# re-running a driver that re-verified the remote gold (sha256 over ~36.8 MB of
# parquet) on a SHARED UCL LOGIN NODE before exiting 0 again. That is sustained
# login-node CPU of exactly the kind that auto-penalised this account on
# 2026-08-03 00:33:47Z, and it was invisible because nothing counted the lines.
#
# It is also a TIME BOMB rather than an h3 quirk: every one of the 12 lines ends
# this way, so as the campaign finishes we would have had 12 lines churning.
#
# THE PREDICATE IS ABOUT DEMONSTRATED FUTILITY, NOT ABOUT TRUSTING EXIT 0. That
# distinction is what keeps D12 intact. D12 (supervisor:293-301) exists because
# six legs once reported "LINE COMPLETE" HAVING PRODUCED NOTHING, so a completion
# claim is not by itself trustworthy. Therefore a first completion still earns
# exactly ONE confirmation revival. If that revival ALSO returns an immediate
# completion, then repeating it cannot change anything - whether or not the
# completion is truthful - so we stop and RAISE AN ALARM instead of churning
# silently. A false complete is thereby escalated to a human, which is strictly
# better than today's behaviour of hiding it inside a 5-minute loop.
#
# rc=3 (review gate) is NEVER revived. supervisor:303-306 already claims that
# breaking there "does NOT trigger an automatic revival ... verified in
# mode_d_watchdog.ps1 / docs/ops/watchdog_fenced.ps1". That claim was FALSE in
# both watchdogs for the same absence-based reason; this makes it true here.
#
# ESCAPE HATCH: drop a file named REVIVE_<safe-line> in $OutDir to force revival
# of a suppressed line, so the suppression is reversible without editing code.
# ---------------------------------------------------------------------------
function Get-LineTerminalState([string]$lineName) {
    # EXACTLY mode_d_supervisor.ps1:81 - deriving it any other way risks drifting
    # from the real log name, which would silently disable this whole check.
    $safe = ($lineName -replace "[^a-zA-Z0-9_-]", "_")

    if (Test-Path (Join-Path $outDir ("REVIVE_{0}" -f $safe))) { return "REVIVE" }

    $logPath = Join-Path $outDir ("supervisor_{0}.log" -f $safe)
    # FAIL-SAFE: no log, unreadable log, or no recognised outcome all fall through
    # to REVIVE, which is exactly the behaviour this file had before P202.
    if (-not (Test-Path $logPath)) { return "REVIVE" }
    $tail = @(Get-Content -Path $logPath -Tail 400 -ErrorAction SilentlyContinue)
    $outcomes = @($tail | Where-Object { $_ -match 'driver exited' })
    if ($outcomes.Count -eq 0) { return "REVIVE" }

    if ($outcomes[-1] -match 'driver exited 3') { return "GATE" }

    # Count CONSECUTIVE trailing completions, not completions anywhere in the tail:
    # a line that completed during some earlier episode and was later restarted by
    # hand must still get its confirmation revival.
    $consec = 0
    for ($i = $outcomes.Count - 1; $i -ge 0; $i--) {
        if ($outcomes[$i] -match 'driver exited 0 - LINE COMPLETE') { $consec++ } else { break }
    }
    if ($consec -ge 2) { return "COMPLETE" }
    return "REVIVE"
}

# Alert on the DELTA. An alarm that is always on is not an alarm - that is the
# operational lesson this defect was hidden by (guards=2 had been permanently red).
$announced = @{}
function Announce([string]$lineName, [string]$state, [string]$msg) {
    $key = "{0}={1}" -f $lineName, $state
    if ($announced.ContainsKey($key)) { return }
    $announced[$key] = $true
    WLog $msg
    $watchDir = Join-Path $repo "docs\ops\watch"
    if (Test-Path $watchDir) {
        Add-Content -Path (Join-Path $watchDir "WATCHDOG_LINES.log") -Value (
            "{0} {1}" -f (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"), $msg)
    }
}

WLog ("started; watching {0} lines every {1}s (out={2}, remote={3}, fence={4})" -f `
    $lines.Count, $IntervalSecs, $OutDir, $RemoteRoot, $ExcludeHosts)

while ($true) {
    if (Test-Path $stopFile) { WLog "STOP_CAMPAIGN present - watchdog exiting."; break }

    $alive = @()
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match 'mode_d_supervisor' } |
        ForEach-Object { if ($_.CommandLine -match '-Line\s+(\S+)') { $alive += $Matches[1] } }

    # P202: an absent supervisor is not automatically a dead one. Triage before acting.
    $dead = @()
    foreach ($ln in $lines) {
        if ($alive -contains $ln) { continue }
        $state = Get-LineTerminalState $ln
        if ($state -eq "COMPLETE") {
            Announce $ln $state ("LINE COMPLETE (confirmed twice): {0} - NOT reviving. Revival re-runs a driver that exits immediately, and each attempt re-verifies the remote gold on a shared login node. Drop REVIVE_<line> in the out dir to override." -f $ln)
        } elseif ($state -eq "GATE") {
            Announce $ln $state ("REVIEW GATE STOP: {0} - NOT reviving. THIS NEEDS A HUMAN: review the effect-blind report, then create TIER1_APPROVED_<line_tag> and re-run with --approve-tier1 --resume." -f $ln)
        } else {
            $dead += $ln
        }
    }
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
