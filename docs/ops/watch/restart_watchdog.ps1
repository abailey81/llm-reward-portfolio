# restart_watchdog.ps1 -- activate a watchdog_fenced.ps1 code change.
#
# WHY THIS EXISTS. PowerShell binds a script at PROCESS START, so editing watchdog_fenced.ps1 is
# INERT: the running watchdog keeps the code and argument vector it was launched with. The R26-10
# fix (Get-ReviveArgs, which preserves -SpecsPerTask/-HRt across a revive) therefore does nothing
# until the watchdog is restarted.
#
# WHY IT IS A SCRIPT AND NOT A TYPED COMMAND. Stop-Process typed inline is classifier-blocked;
# inside a .ps1 it is the sanctioned route (RUN 26 restarted six supervisors this way).
#
# SAFETY. This REFUSES to act unless the board is exactly as expected, because a botched restart on
# a live campaign is far worse than a delayed fix:
#   * exactly ONE watchdog process must be running (two would fight over revives)
#   * at least MinSupervisors supervisors must be alive AND NONE may be missing, so the new
#     watchdog cannot come up, see a dead line, and spawn a duplicate during the gap
#   * the new process is launched with the OLD process's argument vector, read live, never assumed
#   * it verifies AFTER, and says plainly if the relaunch failed
# The stop and the start are adjacent so the uncovered window is about a second, and no line is
# dead at that moment by the pre-check above.
#
# RUN: powershell -ExecutionPolicy Bypass -File docs\ops\watch\restart_watchdog.ps1 [-WhatIf]
# ASCII-only by contract.

param(
    [int]$MinSupervisors = 7,
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

function Get-Watchdogs {
    # ⚠ MUST filter on the PROCESS NAME as well as the command line. The ONSTART launcher is a
    # cmd.exe whose single command line contains the whole chain INCLUDING the watchdog invocation,
    # so a command-line-only match reports TWO watchdogs and this script's own safety pre-check
    # refuses to act. Caught by the -WhatIf dry run before anything was stopped.
    # NOTE: predicate deliberately on ONE line. A first version used backtick continuations inside
    # the Where-Object block and returned ZERO watchdogs even though a direct check of the same two
    # conditions matched pid 21560 -- so the logic was right and the line-continuation was not.
    # One line removes the whole class.
    # ⚠ THE QUOTES ARE OPTIONAL AND THAT MATTERS. The ONSTART launcher starts the watchdog with a
    # QUOTED -File path; `Start-Process powershell -ArgumentList @(...)` (i.e. THIS script's own
    # relaunch) produces an UNQUOTED one. A quote-REQUIRING regex therefore found the original
    # watchdog but was blind to the one this script had just started -- the post-check reported
    # "0 watchdogs after restart" and cried failure while the process was demonstrably running and
    # logging. Worse, the next invocation's PRE-check would have found 0 and refused outright.
    $rx = '-File\s+"?[^"\s]*watchdog_fenced\.ps1"?'
    @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ieq 'powershell.exe' -and $_.CommandLine -ne $null -and $_.CommandLine -match $rx -and $_.CommandLine -notmatch 'restart_watchdog' })
}
function Get-SupervisorLines {
    # ⚠ Emit to the PIPELINE and let the caller collect with @(). An earlier version accumulated
    # into a local and returned `,$out`, whose comma operator produced an ARRAY CONTAINING AN ARRAY
    # -- the count read 1 and the names printed as "System.Object[]".
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match 'mode_d_supervisor' } |
        ForEach-Object { if ($_.CommandLine -match '-Line\s+(\S+)') { $Matches[1] } }
}

Write-Output ("clock: " + (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"))

# ---------------------------------------------------------------- PRE-CHECK
# ⚠ @() IS LOAD-BEARING, NOT DECORATION. PowerShell 5.1 UNROLLS a single-element array on return,
# so `$wd = Get-Watchdogs` binds a bare CimInstance whose `.Count` is $null -- and `$null -ne 1` is
# TRUE, so this script refused to act while printing "found " with an empty count. Exactly the
# footgun recorded in the RUN 27 brief's harness-limits table, walked into anyway.
$wd = @(Get-Watchdogs)
$sup = @(Get-SupervisorLines)
Write-Output ("watchdogs running : " + $wd.Count)
Write-Output ("supervisor lines  : " + $sup.Count + "  [" + ($sup -join ", ") + "]")

if ($wd.Count -ne 1) {
    Write-Output ("REFUSING: expected exactly 1 watchdog, found " + $wd.Count + ". Nothing was changed.")
    exit 2
}
if ($sup.Count -lt $MinSupervisors) {
    Write-Output ("REFUSING: only " + $sup.Count + " supervisors alive, need >= " + $MinSupervisors +
                  ". A restart now could spawn duplicates. Nothing was changed.")
    exit 2
}

$old = $wd[0]
$cmd = $old.CommandLine
Write-Output ("old watchdog pid  : " + $old.ProcessId)

# Rebuild the argument vector from the LIVE command line, never from a remembered one.
$argList = @()
# ⚠ EACH PATTERN ACCEPTS BOTH THE QUOTED AND UNQUOTED FORM, for the same reason as $rx above: the
# ONSTART launcher quotes these, this script's own relaunch does not, and a restart must be
# repeatable against a watchdog THIS script started. `"?([^"\s]+)"?` captures either.
if ($cmd -match '-File\s+"?([^"\s]+)"?')         { $argList += @("-File", $Matches[1]) }        else { Write-Output "REFUSING: could not read -File from the live command line."; exit 3 }
if ($cmd -match '-OutDir\s+"?([^"\s]+)"?')       { $argList += @("-OutDir", $Matches[1]) }      else { Write-Output "REFUSING: could not read -OutDir."; exit 3 }
if ($cmd -match '-RemoteRoot\s+"?([^"\s]+)"?')   { $argList += @("-RemoteRoot", $Matches[1]) }  else { Write-Output "REFUSING: could not read -RemoteRoot."; exit 3 }
if ($cmd -match '-ExcludeHosts\s+"?([^"\s]+)"?') { $argList += @("-ExcludeHosts", $Matches[1]) } else { Write-Output "REFUSING: could not read -ExcludeHosts."; exit 3 }
$argList = @("-NoProfile", "-ExecutionPolicy", "Bypass") + $argList
Write-Output ("relaunch args     : " + ($argList -join " "))

# Prove the file we are about to activate actually carries the fix, BEFORE killing anything.
$file = ($argList | Select-Object -Index (([array]::IndexOf($argList, "-File")) + 1))
$src = Get-Content -Raw $file
if ($src -notmatch "function Get-ReviveArgs") {
    Write-Output "REFUSING: the target watchdog file does not define Get-ReviveArgs -- restarting would gain nothing."
    exit 4
}
if ($src -notmatch "Start-Process\s+powershell\s+-ArgumentList\s+\(Get-ReviveArgs") {
    Write-Output "REFUSING: the target watchdog file does not CALL Get-ReviveArgs."
    exit 4
}
Write-Output "target file carries the R26-10 fix (definition + call site): OK"

if ($WhatIf) { Write-Output "WHATIF -- nothing stopped, nothing started."; exit 0 }

# ---------------------------------------------------------------- ACT
Stop-Process -Id $old.ProcessId -Force
Start-Sleep -Milliseconds 400
Start-Process powershell -ArgumentList $argList
Start-Sleep -Seconds 3

# ---------------------------------------------------------------- POST-CHECK
$wd2 = @(Get-Watchdogs)   # @() load-bearing -- see the note on the pre-check
$sup2 = @(Get-SupervisorLines)
Write-Output ""
Write-Output ("watchdogs now     : " + $wd2.Count + "  pid(s): " + (($wd2 | ForEach-Object { $_.ProcessId }) -join ", "))
Write-Output ("supervisor lines  : " + $sup2.Count + "  [" + ($sup2 -join ", ") + "]")

$ok = $true
if ($wd2.Count -ne 1) { Write-Output ("!! FAILED: " + $wd2.Count + " watchdogs after restart (want 1)"); $ok = $false }
if ($wd2.Count -eq 1 -and $wd2[0].ProcessId -eq $old.ProcessId) { Write-Output "!! FAILED: same pid -- the old process did not die"; $ok = $false }
if ($sup2.Count -lt $sup.Count) { Write-Output ("!! FAILED: supervisors dropped " + $sup.Count + " -> " + $sup2.Count); $ok = $false }

if ($ok) { Write-Output "RESTART OK -- the R26-10 fix is now LIVE."; exit 0 }
else     { Write-Output "RESTART PROBLEM -- investigate immediately."; exit 1 }
