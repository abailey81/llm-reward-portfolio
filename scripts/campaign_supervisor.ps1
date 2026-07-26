# CAMPAIGN SUPERVISOR (2026-07-18) — makes any driver death SELF-HEALING.
#
# WHY: the 2026-07-17 VPN outage killed both laptop drivers after their bounded ride-out
# (loud + resumable BY DESIGN — but a human had to notice). During the real campaign a
# night-time outage would stall authoring/requeues until morning. This wrapper relaunches
# the driver on ANY nonzero exit: the driver is idempotent (archive-truth resume; the P12
# lock auto-breaks for a dead owner; ledger-resubmit never re-bills authored candidates),
# so relaunching is always safe. Running arrays on Myriad are NEVER affected by a driver
# death — only the laptop-side loop stalls, and this closes that gap.
#
# USAGE (from the repo root, after the freeze — the P19 gate applies on every relaunch):
#   powershell -ExecutionPolicy Bypass -File scripts\campaign_supervisor.ps1
# Stop deliberately: create the file outputs\campaign_cluster\STOP_CAMPAIGN (checked
# between attempts), or Ctrl+C the supervisor itself.

$ErrorActionPreference = "Continue"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

$outDir   = "outputs\campaign_cluster"
$stopFile = Join-Path $outDir "STOP_CAMPAIGN"
$logFile  = Join-Path $outDir "supervisor.log"
New-Item -ItemType Directory -Force $outDir | Out-Null

# THE LAUNCH LINE — must stay in lockstep with docs/CAMPAIGN_DAY_RUNBOOK_2026-07-13.md §2.
$py = Join-Path $repo ".venv\Scripts\python.exe"   # ABSOLUTE (2026-07-18 drill: a relative path can fail to resolve and PS tries module-autoload)
$args = @(
  "scripts/run_campaign_cluster.py", "--tiered",
  "--arms", "distributional", "scalar", "scalar_cvar5", "placebo", "placebo_shuffled",
            "random_search", "bayes_opt",
  # NO --baselines: under --tiered the launcher resolves the FROZEN config h1_baselines family
  # (resolve_cluster_baselines). This line used to hand-mirror the H1 four and DRIFTED when the
  # canon expanded 4 -> 11 on 2026-07-26 - it would have run a subset, breaking the N6 IUT and
  # mis-sizing the C0 canary. Never hand-type a frozen list here again.
  "--pass-mode", "B", "--llm-from", "campaign",
  "--pack", "5", "--cores-per-training", "1", "--pool", "EF",
  "--seed-pool-blocks", "EF:0-14,L:15-29,EF:30-64,L:65-99,EF:100-143,L:144-188,EF:189-233,L:234-278,EF:279-308,L:309-339,EF:340-370,L:371-402,EF:403-484,L:485-567",
  "--batch-tag", "c1", "--poll-secs", "180", "--chunk-tasks", "1",
  "--output-dir", $outDir, "--resume"
)

$attempt = 0
$maxAttempts = 1000
$backoffSecs = 600

function Log([string]$msg) {
    $line = "{0} | supervisor | {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $msg
    Write-Host $line
    Add-Content -Path $logFile -Value $line
}

Log "supervisor started (MSYS_NO_PATHCONV irrelevant here: native PowerShell, no path mangling)"
while ($attempt -lt $maxAttempts) {
    if (Test-Path $stopFile) { Log "STOP_CAMPAIGN present - deliberate stop."; break }
    $attempt += 1
    Log ("attempt {0}: launching the campaign driver" -f $attempt)
    # 2026-07-18 drill catch: if the invocation FAILS TO START, $LASTEXITCODE is never set and a
    # STALE zero from a prior iteration would read as "CAMPAIGN COMPLETE". Default rc to -1 and
    # only trust $LASTEXITCODE when the call actually ran.
    $rc = -1
    try {
        & $py @args
        if ($null -ne $LASTEXITCODE) { $rc = $LASTEXITCODE }
    } catch {
        Log ("driver INVOCATION failed before start: {0}" -f $_.Exception.Message)
        $rc = -1
    }
    if ($rc -eq 0) { Log "driver exited 0 - CAMPAIGN COMPLETE (or gate stop handled). Supervisor done."; break }
    Log ("driver exited {0} (outage/crash class) - relaunching in {1}s; running arrays on Myriad are unaffected" -f $rc, $backoffSecs)
    Start-Sleep -Seconds $backoffSecs
}
Log "supervisor exiting."
