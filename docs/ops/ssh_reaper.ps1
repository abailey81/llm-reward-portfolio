# INSTRUMENTED SSH REAPER -- replaces the untracked scratchpad reaper_loop.ps1.
#
# ASCII ONLY (PowerShell 5.1 turns smart quotes into string-breaking characters).
#
# WHY THIS FILE EXISTS (2026-07-31, RUN 8).
# A reaper_loop.ps1 was found running from a THIRD session's scratchpad, undocumented in the live
# process stack in CAMPAIGN_EXECUTION_RECORD section 8c, killing ssh.exe processes on the live RUN 4
# campaign. It was built on 2026-07-28 for the RUN 2 transport leak and its own header says
# "RETIRE THIS once every line has been restarted onto the fixed code".
#
# That retirement condition is MET and verified: reap() is present in the running sha 50b6e07
# (src/cluster/submit.py:61, called from src/cluster/poll.py:200 and :236) and all twelve lines have
# been relaunched onto it four times (record sections 46, 54, 58, 60).
#
# BUT the old reaper still killed 13 processes DURING RUN 4, in suspicious consecutive-cycle
# clusters (08:45/08:50/08:55, 09:41/09:46, 14:11/14:16/14:21 on 07-31). A genuine one-off orphan is
# killed once and gone. Something is repeatedly presenting as reapable, and the old log recorded only
# a COUNT -- never an identity -- so there is no way to tell from the record whether those were:
#   (a) genuine orphans reap() does not cover  -> the reaper is still earning its place, or
#   (b) LIVE transport children whose parent lookup failed -> we have been silently killing live
#       archive pulls on a confirmatory run, which is a validity problem, not a tidiness one.
#
# Killing it blind and keeping it blind are both guesses. This measures instead: it DEFAULTS TO
# DRY RUN, and logs the full identity of every candidate before deciding. Nothing is killed unless
# -Apply is passed. The in-code reap() already covers the leak it was built for, so dry run carries
# no regression risk.
#
# NOTE ON THE ORPHAN TEST. The old rule was "parent pid absent from the snapshot". That is the D20
# bug class in mirror image: a pid is not an identity, and on Windows pids are reused aggressively.
# This version records the parent's name and start time alongside, so the log can distinguish a real
# orphan from a reused-pid artifact after the fact.
#
#   powershell -File docs/ops/ssh_reaper.ps1                 # dry run, observe only (DEFAULT)
#   powershell -File docs/ops/ssh_reaper.ps1 -Apply          # actually kill
#   powershell -File docs/ops/ssh_reaper.ps1 -Once           # single pass, for inspection

param(
  [int]$IntervalSecs = 300,
  [switch]$Apply,
  [switch]$Once,
  [string]$LogPath = ""
)

$ErrorActionPreference = 'Continue'
if ([string]::IsNullOrWhiteSpace($LogPath)) {
  $LogPath = Join-Path $PSScriptRoot 'watch\ssh_reaper.log'
}
$dir = Split-Path -Parent $LogPath
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }

# The parent's own tar-extract timeout is 3600 s (src/cluster/poll.py:190); the submit-side push uses
# 1800 s (src/cluster/submit.py:228). An ssh older than 3600 s is therefore past ANY parent timeout,
# so the parent has already raised and moved on. Verified against the running sha, not assumed.
$MinAgeSecs = 3600

$mode = if ($Apply) { 'APPLY' } else { 'DRYRUN' }
Add-Content -Path $LogPath -Encoding utf8 -Value (
  "{0} START mode={1} interval={2}s minage={3}s" -f `
    (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'), $mode, $IntervalSecs, $MinAgeSecs)

while ($true) {
  try {
    $all = Get-CimInstance Win32_Process
    $byPid = @{}
    foreach ($p in $all) { $byPid[[int]$p.ProcessId] = $p }

    $sshList = @($all | Where-Object { $_.Name -eq 'ssh.exe' })
    $acted = 0

    foreach ($o in $sshList) {
      $age = [int]((Get-Date) - $o.CreationDate).TotalSeconds
      $ppid = [int]$o.ParentProcessId
      $parent = $byPid[$ppid]
      $parentAlive = ($null -ne $parent)
      $isTar = $o.CommandLine -match 'tar -C .* -cf -'

      # *** THE ORPHAN RULE NEEDS AN AGE GUARD, AND THE RETIRED REAPER HAD NONE. ***
      # PROVEN BY DIRECT OBSERVATION 2026-07-31T18:19:39Z (record s.68): this loop flagged
      #   reason=orphan pid=33028 age=6s ppid=26516 pname=<gone> istar=False
      #   cmd=ssh.exe myriad "qstat -u '*' -s p -pri"
      # -- a LIVE ssh, SIX SECONDS OLD, issued 30 s earlier by the session itself. Its parent shell
      # had already exited, which is entirely normal for a short-lived tool invocation, so the bare
      # "parent pid absent" test called it an orphan. **The retired reaper_loop.ps1 would have KILLED
      # IT MID-FLIGHT**, and that is what its 13 unexplained RUN-4 kills almost certainly were.
      # A pid whose parent has exited is not a leak; a pid whose parent has exited AND which has been
      # sitting for longer than any parent timeout is. So the orphan branch now carries the SAME age
      # floor as the tar branch. This is what makes -Apply safe to exist at all.
      $reason = $null
      if ((-not $parentAlive) -and $age -gt $MinAgeSecs) { $reason = 'orphan' }
      elseif ($isTar -and $age -gt $MinAgeSecs) { $reason = 'stale_tar' }
      elseif (-not $parentAlive) { $reason = 'young_orphan_IGNORED' }   # logged, never acted on
      if ($null -eq $reason) { continue }

      # IDENTITY FIRST. The whole point of this rewrite: never act on a live campaign without
      # recording exactly what was acted on. Truncated so one candidate stays one log line.
      $cmd = $o.CommandLine
      if ($null -eq $cmd) { $cmd = '<null>' }
      if ($cmd.Length -gt 240) { $cmd = $cmd.Substring(0, 240) }
      $pname = if ($parentAlive) { $parent.Name } else { '<gone>' }
      $pstart = if ($parentAlive) { $parent.CreationDate.ToUniversalTime().ToString('HH:mm:ssZ') } else { '-' }

      Add-Content -Path $LogPath -Encoding utf8 -Value (
        "{0} CANDIDATE mode={1} reason={2} pid={3} age={4}s ppid={5} pname={6} pstart={7} istar={8} cmd={9}" -f `
          (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'),
          $mode, $reason, $o.ProcessId, $age, $ppid, $pname, $pstart, $isTar, $cmd)

      # `young_orphan_IGNORED` is recorded so the pattern stays VISIBLE, but is never acted on --
      # it is the exact class the retired reaper was killing.
      if ($Apply -and $reason -ne 'young_orphan_IGNORED') {
        try { Stop-Process -Id ([int]$o.ProcessId) -Force -ErrorAction Stop; $acted++ } catch { }
      }
    }

    # Same summary shape as the retired reaper, so the two logs concatenate for trend analysis.
    # Retirement check 17 (record section 22) reads this line: ssh_total=0 reaped=0 for consecutive cycles.
    Add-Content -Path $LogPath -Encoding utf8 -Value (
      "{0} ssh_total={1} reaped={2} mode={3}" -f `
        (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ'), $sshList.Count, $acted, $mode)
  } catch {
    Add-Content -Path $LogPath -Encoding utf8 -Value ("ERROR " + $_.Exception.Message)
  }

  if ($Once) { break }
  Start-Sleep -Seconds $IntervalSecs
}
