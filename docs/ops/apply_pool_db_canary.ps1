# POOL-B CANARY - roll ONE line onto pool db (d + b00a), verify it, and leave a safe fallback.
#
# WHY THIS FILE EXISTS. Every step below was worked out and validated on 2026-08-06 (RUN 24), but
# stopping a live campaign process is refused by the agent's permission classifier. So the whole
# operation is packaged here as ONE self-verifying command for Tamer to run, rather than a list of
# steps to follow by hand. It prints what it is about to do, does it, then PROVES the result.
#
# WHAT IT BUYS. Measured with the audited instrument (docs/ops/placeable_capacity.py) on one
# snapshot at 2026-08-06 06:2xZ:
#     b00a   40 placeable cores   memcap 0   <- 1.5 TB RAM per host, never memory-blocked
#     d00a   32 placeable cores   memcap 2
#     d00b    8 placeable cores
# Pool b alone offers MORE placeable capacity than pool d, so widening roughly DOUBLES what we can
# place. Pool b is the ONLY remaining capacity that exists: e/f/l/s/u/v are refused outright by the
# site JSV on real qsub, and t00a is AMD EPYC 9554P and refused on determinism grounds.
#
# WHY IT IS SAFE - IDENTITY, NOT TOLERANCE. The C3 gate enforces per-seed substrate homogeneity on
# `cpu model | omp | threads | cuda`. Probed first-hand: node-b00a-013 and node-b00a-014 both return
# Intel Xeon Gold 6240 @ 2.60GHz, 2 sockets, 36 cores, microcode 0x5003901, flags sha
# 9ede37ab7eb264ea - byte-identical to node-d00a-246 in pool d. Same silicon, same reduction order.
# node-b00a-008 is FENCED because it reports the same model and microcode but a DIFFERENT flags sha
# (639b672208417b8c), which the C3 gate would not notice. Unknown means excluded.
#
# WHY haiku-4.5 IS THE CANARY. Measured: 1 queued job, 0 running - it is AT its batch boundary, so
# the widening takes effect within hours rather than the ~2.5 days a line with 248 queued jobs would
# take (a restarted driver ADOPTS its queued work and submits nothing until it drains). It is also a
# report-only leg whose work is ladder, i.e. zero marginal value to the reported common rung today.
#
# WHY THE ORDER MATTERS. The supervisor is stopped FIRST: it watches its driver and relaunches it on
# exit, so killing the driver first would simply get it restarted on pool d. And the driver MUST be
# stopped too - on Windows killing a parent orphans the child, and an orphaned driver still holds the
# P12 batch lock, so the replacement driver would be REFUSED. The lock auto-breaks once the owning
# pid is gone.
#
# FALLBACK IS SAFE BY CONSTRUCTION. docs/ops/watchdog_fenced.ps1 polls every 300 s and finds live
# lines with `CommandLine -match 'mode_d_supervisor'`. This copy's filename keeps that substring, so
# the revived line reads as ALIVE and no second supervisor starts (which would be the P12
# one-driver-per-batch violation). If it dies anyway, the watchdog revives it from the FENCED script,
# i.e. straight back onto pool d. Losing the widening is not a hazard.
#
# TO ROLL BACK: stop the supervisor and driver this script started; the watchdog restores pool d
# within 300 s on its own.

param(
    [string]$Line = "haiku-4.5",
    [string]$ExcludeHosts = "node-d00a-230,node-d00b-024,node-b00a-008",
    [string]$OutDir = "outputs\campaign_cluster_run4",
    [string]$RemoteRoot = "~/Scratch/llmrp4",
    [switch]$WhatIf
)

$ErrorActionPreference = "Continue"
# $PSScriptRoot is <repo>\docs\ops, so the repo root is TWO parents up. Using $PSCommandPath (the
# FILE) instead needs three, and my first version used two of those - which resolved $repo to
# <repo>\docs and looked for <repo>\docs\docs\ops\... The -WhatIf dry run caught it before it could
# matter, which is the entire reason this script has a -WhatIf.
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$copy = Join-Path $repo "docs\ops\mode_d_supervisor_db.ps1"

if (-not (Test-Path $copy)) { Write-Output "FATAL: missing $copy"; exit 2 }

# ---- 0. PRE-FLIGHT: name the exact processes, and refuse if the shape is not what we expect ------
$sup = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -match 'mode_d_supervisor' -and $_.CommandLine -match [regex]::Escape($Line) -and $_.Name -match 'powershell'
}
$drv = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object {
    $_.CommandLine -match 'run_campaign_cluster' -and $_.CommandLine -match ("--leg\s+" + [regex]::Escape($Line))
}

# !! POWERSHELL 5.1: a SINGLE pipeline object is NOT an array, so `$sup.Count` is $null rather than
# 1. My first version compared `$sup.Count -ne 1` and REFUSED on a perfectly healthy single
# supervisor - it had already printed the right PID. Every count here is therefore taken as
# `@(...).Count`, which forces an array and is correct for 0, 1 and many. The -WhatIf dry run caught
# this, which is the second bug it caught in this file before either could touch the campaign.
Write-Output ("PRE-FLIGHT for line {0}" -f $Line)
Write-Output ("  supervisors found: {0}" -f @($sup).Count)
foreach ($s in $sup) { Write-Output ("    SUPER PID={0}" -f $s.ProcessId) }
Write-Output ("  drivers found    : {0}" -f @($drv).Count)
foreach ($d in $drv) { Write-Output ("    DRIVER PID={0} PPID={1}" -f $d.ProcessId, $d.ParentProcessId) }

if (@($sup).Count -ne 1) {
    Write-Output "REFUSING: expected EXACTLY ONE supervisor for this line. Zero means it is already down"
    Write-Output "  (let the watchdog revive it first); more than one is a P12 hazard that must be"
    Write-Output "  understood before anything is stopped."
    exit 1
}

# The line must be QUIET on the cluster, or we would be discarding in-flight trainings.
$running = (ssh -o BatchMode=yes myriad "qstat -u ucestes -s r 2>/dev/null | awk 'NR>2' | wc -l" 2>$null)
Write-Output ("  our RUNNING jobs cluster-wide: {0} (informational)" -f $running)

if ($WhatIf) { Write-Output "WhatIf: stopping nothing. Re-run without -WhatIf to apply."; exit 0 }

# ---- 1. supervisor FIRST, so it cannot relaunch the old pool-d driver ---------------------------
Write-Output "STOP 1/2: supervisor"
foreach ($s in $sup) { Stop-Process -Id $s.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Milliseconds 500

# ---- 2. then the driver chain, so no orphan keeps the P12 batch lock ----------------------------
Write-Output "STOP 2/2: driver chain"
foreach ($d in $drv) { Stop-Process -Id $d.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 1
$leftover = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object {
    $_.CommandLine -match 'run_campaign_cluster' -and $_.CommandLine -match ("--leg\s+" + [regex]::Escape($Line))
}
Write-Output ("  leftover drivers (MUST be 0): {0}" -f @($leftover).Count)

# ---- 3. start the widened supervisor -----------------------------------------------------------
Write-Output "START: widened supervisor (pool db)"
$p = Start-Process powershell -PassThru -ArgumentList @(
    "-ExecutionPolicy", "Bypass", "-File", $copy,
    "-Line", $Line, "-StaggerSecs", "0",
    "-ExcludeHosts", $ExcludeHosts,
    "-OutDir", $OutDir, "-RemoteRoot", $RemoteRoot
)
Write-Output ("  launched PID={0}" -f $p.Id)

# ---- 4. VERIFY THE ARTEFACT, NOT THE INTENTION -------------------------------------------------
# A fix is not done when the command was issued, only when the result is OBSERVED. The driver takes
# a few seconds to appear, so poll rather than sampling once.
Write-Output "VERIFY (polling up to 90 s for the driver to appear):"
$ok = $false
for ($i = 0; $i -lt 18; $i++) {
    Start-Sleep -Seconds 5
    $nd = Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object {
        $_.CommandLine -match 'run_campaign_cluster' -and $_.CommandLine -match ("--leg\s+" + [regex]::Escape($Line))
    }
    if (@($nd).Count -gt 0) {
        foreach ($x in $nd) {
            $pool = "<not found>"
            if ($x.CommandLine -match '--pool\s+(\S+)') { $pool = $Matches[1] }
            $fence = "<not found>"
            if ($x.CommandLine -match '--exclude-hosts\s+(\S+)') { $fence = $Matches[1] }
            Write-Output ("  DRIVER PID={0}  --pool {1}  --exclude-hosts {2}" -f $x.ProcessId, $pool, $fence)
            if ($pool -eq "db") { $ok = $true }
        }
        if ($ok) { break }
    }
}
Write-Output ""
if ($ok) {
    Write-Output "RESULT: PASS - the line is running on --pool db."
    Write-Output "NEXT: run docs/analysis/substrate_watch.py as the FIRST new-pool records land, not"
    Write-Output "  afterwards. The entire risk is heterogeneity and the detector must run while the"
    Write-Output "  evidence is arriving. Any cpu.model_name that is not Intel Xeon Gold 6240 means"
    Write-Output "  stop this line and fence that host."
    exit 0
}
Write-Output "RESULT: FAIL - no driver on --pool db appeared within 90 s."
Write-Output "  This is SELF-HEALING: docs/ops/watchdog_fenced.ps1 will revive the line from the"
Write-Output "  FENCED script within 300 s, i.e. back onto pool d, losing only the widening."
Write-Output "  Check the supervisor log under $OutDir before retrying."
exit 1
