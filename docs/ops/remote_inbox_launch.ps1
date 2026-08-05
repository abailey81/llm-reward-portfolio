# Launch the REMOTE-CONTROL inbox loop DETACHED, so it survives the Claude Code session that
# started it.
#
# * WHY THIS FILE EXISTS. The loop was first started as a background job of an interactive session.
# Its parent was that session, so it would have died the moment the session ended -- and the whole
# point of the inbox is that Tamer can reach the campaign when NO session is attached. A control
# channel that only works while someone is already watching is not a control channel.
#
# It mirrors the pattern the campaign's own supervisors use (`scripts/mode_d_launch.ps1:61`,
# `docs/ops/watchdog_fenced.ps1:222`): Start-Process, hidden, no parent handle retained.
#
# SAFE BY CONSTRUCTION: the loop only ever runs `git fetch` / `git show` (read-only), rewrites the
# instruction fence of docs/REMOTE_CONTROL.md, and writes its own state file. It never touches the
# archive, never submits or deletes a job, and never edits a drift-fenced path.
#
#   .\docs\ops\remote_inbox_launch.ps1            # start it (idempotent -- refuses to double-start)
#   .\docs\ops\remote_inbox_launch.ps1 -Status    # is it alive?
#   .\docs\ops\remote_inbox_launch.ps1 -Stop      # stop it, by explicit PID only

param([switch]$Status, [switch]$Stop)

$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$py   = Join-Path $repo '.venv\Scripts\python.exe'
$script = Join-Path $repo 'docs\ops\remote_inbox.py'
$log  = Join-Path $repo 'docs\ops\watch\REMOTE_INBOX.log'

function Get-InboxProcs {
    Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
        Where-Object { $_.CommandLine -like '*remote_inbox.py*' -and $_.CommandLine -like '*--loop*' }
}

if ($Status) {
    $p = @(Get-InboxProcs)
    if ($p.Count -eq 0) { Write-Output 'inbox loop: NOT RUNNING'; exit 1 }
    foreach ($x in $p) { Write-Output ("inbox loop: RUNNING pid={0}" -f $x.ProcessId) }
    exit 0
}

if ($Stop) {
    # Explicit PIDs only. A broad kill on this box would take the campaign's own python processes
    # with it, which is a standing prohibition.
    $p = @(Get-InboxProcs)
    if ($p.Count -eq 0) { Write-Output 'inbox loop: nothing to stop'; exit 0 }
    # Killing the parent cascades to its child, so by the time the loop reaches the second PID that
    # process is already gone and Stop-Process throws. With $ErrorActionPreference='Stop' that
    # aborted the whole script BEFORE the restart -- i.e. -Stop worked and the caller was left with
    # nothing running. An already-dead process is the SUCCESS case for a stop, not a failure.
    foreach ($x in $p) {
        try {
            Stop-Process -Id $x.ProcessId -Force -ErrorAction Stop
            Write-Output ("stopped pid={0}" -f $x.ProcessId)
        } catch {
            Write-Output ("pid={0} was already gone (cascaded from its parent)" -f $x.ProcessId)
        }
    }
    exit 0
}

$existing = @(Get-InboxProcs)
if ($existing.Count -gt 0) {
    Write-Output ("inbox loop already running (pid={0}); refusing to start a second" -f $existing[0].ProcessId)
    exit 0
}

if (-not (Test-Path $py))     { Write-Output "MISSING interpreter: $py";  exit 2 }
if (-not (Test-Path $script)) { Write-Output "MISSING script: $script";   exit 2 }

Start-Process -FilePath $py `
              -ArgumentList @($script, '--loop') `
              -WorkingDirectory $repo `
              -WindowStyle Hidden `
              -RedirectStandardOutput $log `
              -RedirectStandardError ($log + '.err')

Start-Sleep -Seconds 3
$now = @(Get-InboxProcs)
if ($now.Count -gt 0) {
    Write-Output ("inbox loop STARTED detached, pid={0}; log={1}" -f $now[0].ProcessId, $log)
    exit 0
}
Write-Output 'inbox loop FAILED to start -- check the log'
exit 1
