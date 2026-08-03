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
# !! THE FIRST VERSION OF THIS PREDICATE WAS REFUTED BY AN INDEPENDENT AUDITOR, ON THIS
# REPO'S OWN LOGS. It suppressed on ">=2 consecutive completions" alone, reasoning that an
# action repeated with no effect cannot suddenly have one. THAT IS EMPIRICALLY FALSE HERE:
# supervisor_deepseek-v4-pro.log carries TEN consecutive "driver exited 0" entries from
# 2026-07-28 23:14:45 to 2026-07-29 00:01:55, and the ELEVENTH revival launched a driver
# that then ran for a full day. Those are D12's own six legs. The rule would have killed
# deepseek, glm-5.2, kimi-k3, nemotron-3-super, qwen3.5-9b and qwen3.6-27b permanently.
#
# So suppression now needs THREE independent things to agree, not one:
#
#   (1) THE SUPERVISOR ENDED CLEANLY. The log's last non-empty line must be
#       "line supervisor exiting." A supervisor killed mid-attempt (reboot, host kill)
#       writes NO outcome line, so the trailing outcomes would still be the PREVIOUS
#       episode's - and a genuinely dead line would inherit an old completion pair.
#
#   (2) THE COMPLETION TEXT IS THE POST-D12 ONE, ANCHORED. Before D12 the supervisor
#       could not tell completion from a review-gate stop and SAID SO:
#           "driver exited 0 - LINE COMPLETE (or gate stop handled)."   <- ambiguous
#           "driver exited 0 - LINE COMPLETE."                          <- post-D12, decisive
#       Anchoring on the second form is not a string trick, it is causal: only the
#       post-D12 supervisor is entitled to claim completion, because only it returns 3
#       for a gate stop. Measured across all twelve logs, this separates them perfectly -
#       the ambiguous text appears in EXACTLY D12's six legs and nowhere else; the
#       decisive text appears only in h3 and gemini-2.5-flash, the two real completions.
#
#   (3) THE CAMPAIGN ITSELF AGREES, from a source the supervisor does not write. The
#       driver log must carry a campaign-level success ("TIERED OK" / "SINGLE-SHOT OK").
#       Measured: driver_deepseek-v4-pro.log has ZERO of these - the D12 legs reported
#       complete having produced nothing, and it shows. gemini has 2, h3 has 279.
#
# Any one of the three failing means REVIVE. That is the D12 lesson honoured properly:
# a completion claim is not self-certifying, so it must be corroborated rather than
# merely repeated.
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

    # Anchored: an unanchored 'driver exited 3' also matches 3221225786 (STATUS_CONTROL_C_EXIT)
    # and every other code beginning with 3, and the failure direction is "stop reviving".
    if ($outcomes[-1] -match 'driver exited 3 -') { return "GATE" }

    # (1) the supervisor must have terminated CLEANLY rather than been killed mid-attempt
    $lastMeaningful = ($tail | Where-Object { $_.Trim() -ne "" } | Select-Object -Last 1)
    if ($lastMeaningful -notmatch 'line supervisor exiting\.\s*$') { return "REVIVE" }

    # (2) CONSECUTIVE trailing completions, in the decisive post-D12 wording only
    $consec = 0
    for ($i = $outcomes.Count - 1; $i -ge 0; $i--) {
        if ($outcomes[$i] -match 'driver exited 0 - LINE COMPLETE\.\s*$') { $consec++ } else { break }
    }
    if ($consec -lt 2) { return "REVIVE" }

    # (3) independent corroboration from the driver's own log, which the supervisor does
    # not write. Tail only: the campaign emits its verdict at the end of a run.
    $driverLog = Join-Path $outDir ("driver_{0}.log" -f $safe)
    if (-not (Test-Path $driverLog)) { return "REVIVE" }
    $dtail = @(Get-Content -Path $driverLog -Tail 200 -ErrorAction SilentlyContinue)
    if (-not ($dtail | Where-Object { $_ -match 'TIERED OK|SINGLE-SHOT OK' })) { return "REVIVE" }

    return "COMPLETE"
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
            # Get-Date returns LOCAL time and the trailing Z in a format string is a LITERAL, so
            # "-Format ...ssZ" stamps local time and calls it UTC. It logged 04:13:14Z when UTC was
            # 03:13:14Z. A forensic log for an irreplaceable campaign must not lie about its clock.
            "{0} {1}" -f (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"), $msg)
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
            # Name the ACTUAL filename: dots become underscores, so "gemini-2.5-flash" needs
            # REVIVE_gemini-2_5-flash. Following a literal "REVIVE_<line>" would silently do
            # nothing for 9 of the 12 lines.
            Announce $ln $state ("LINE COMPLETE (corroborated: clean exit + 2 post-D12 completions + driver-level OK): {0} - NOT reviving. Revival re-runs a driver that exits immediately, and each attempt re-verifies the remote gold on a shared login node. To override, create the file '{1}' in {2}." -f $ln, ("REVIVE_" + ($ln -replace "[^a-zA-Z0-9_-]", "_")), $outDir)
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
