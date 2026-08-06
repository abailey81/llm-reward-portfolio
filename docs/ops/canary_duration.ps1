# canary_duration.ps1 - restart ONE leg onto the DURATION lever, and nothing else.
#
# WHY (measured 2026-08-06, not inferred):
#   cores = dispatch_rate x duration x 8.
#   * 78 pool-d hosts held >=8 free slots while we won ZERO dispatches in two hours, so it is not
#     capacity and not fragmentation.
#   * Dispatch order is decided ENTIRELY by ntckts: weight_urgency=0, so waiting time earns nothing,
#     and prior = 4.0*npprior + 1.5*ntckts (exact to 5 dp on a live job).
#   * Our per-job tickets are 14,757 against ucaqcsu 59,547 and ucaphge 400,379 - but our TOTAL is
#     13.2M, the cluster MEDIAN. We are not penalised. We DILUTE, across 897 jobs.
#   * ucbtjji is the existence proof: h_rt 48h against our 15h, holding 768 cores from 98 jobs.
#
#   16 specs per task at pack 8 runs 2 WAVES in one job. That doubles DURATION and halves our job
#   COUNT, so BOTH terms improve together.
#
# SAFETY, and every clause is load-bearing:
#   * Refuses to touch the 'core' line. c1 carries the entire reported result.
#   * Refuses unless src/cluster/driver.py already carries specs_per_task, so it cannot start a
#     supervisor whose driver will reject the flag and crash-loop the line.
#   * -WhatIf prints the exact stop/start it would perform and changes nothing.
#   * Stops the supervisor FIRST, then its driver, then starts the replacement immediately: the
#     watchdog polls every 300s and would otherwise revive the line WITHOUT the canary flags
#     (docs/ops/watchdog_fenced.ps1:231 - the same omission that file was forked to fix for
#     -ExcludeHosts). Ledger R26-10.
#
# USAGE -- ABSOLUTE PATH, ALWAYS.
#   Tamer's shell sits at C:\Users\User, not the repo, so a relative path fails with
#   "The argument ... to the -File parameter does not exist". That was the THIRD handover in one
#   session to fail because a command assumed the agent's working context instead of his: first
#   bash quoting, then PowerShell 5.1 stripping inner quotes, then this. Ledger R26-8.
#   The rule that covers all three: test the command AS HE WILL RUN IT, FROM HIS DIRECTORY.
#
#   powershell -ExecutionPolicy Bypass -File "C:\Users\User\Desktop\dissertation_papers\llm-reward-portfolio\docs\ops\canary_duration.ps1" -WhatIf
#   powershell -ExecutionPolicy Bypass -File "C:\Users\User\Desktop\dissertation_papers\llm-reward-portfolio\docs\ops\canary_duration.ps1"
#   powershell -ExecutionPolicy Bypass -File "C:\Users\User\Desktop\dissertation_papers\llm-reward-portfolio\docs\ops\canary_duration.ps1" -Revert
param(
    [string]$Line = "kimi-k3",
    [int]$SpecsPerTask = 16,
    [string]$HRt = "30:0:0",
    [string]$ExcludeHosts = "node-d00a-230,node-d00b-024",
    [string]$OutDir = "outputs\campaign_cluster_run4",
    [string]$RemoteRoot = "~/Scratch/llmrp4",
    [switch]$WhatIf,
    [switch]$Revert
)

$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)

if ($Line -eq "core") {
    Write-Host "REFUSING: 'core' is the confirmatory line and carries the entire reported result."
    exit 2
}

$driverPy = Join-Path $repo "src\cluster\driver.py"
if (-not (Select-String -Path $driverPy -Pattern "specs_per_task" -Quiet)) {
    Write-Host "REFUSING: src/cluster/driver.py does not carry specs_per_task yet."
    Write-Host "  Apply the patch first, or this starts a supervisor whose driver rejects the flag"
    Write-Host "  and crash-loops the line. Run apply_duration_patch.py, then the tests, then this."
    exit 2
}

$sup = @(Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" |
         Where-Object { $_.CommandLine -match 'mode_d_supervisor' -and
                        $_.CommandLine -match ("-Line\s+" + [regex]::Escape($Line) + "(\s|$)") })
$drv = @(Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
         Where-Object { $_.CommandLine -match 'run_campaign_cluster' -and
                        $_.CommandLine -match ("--leg\s+" + [regex]::Escape($Line) + "(\s|$)") })

Write-Host ("line            : {0}" -f $Line)
Write-Host ("supervisor pid  : {0}" -f (($sup | ForEach-Object { $_.ProcessId }) -join ", "))
Write-Host ("driver pid(s)   : {0}" -f (($drv | ForEach-Object { $_.ProcessId }) -join ", "))
if ($sup.Count -eq 0) { Write-Host "REFUSING: no supervisor found for that line."; exit 2 }

$extra = if ($Revert) { @() } else { @("-SpecsPerTask", "$SpecsPerTask", "-HRt", $HRt) }
$args2 = @(
    "-ExecutionPolicy", "Bypass",
    "-File", (Join-Path $repo "scripts\mode_d_supervisor.ps1"),
    "-Line", $Line, "-StaggerSecs", "0",
    "-ExcludeHosts", $ExcludeHosts,
    "-OutDir", $OutDir, "-RemoteRoot", $RemoteRoot
) + $extra

Write-Host ("would start     : powershell {0}" -f ($args2 -join " "))
if ($WhatIf) { Write-Host "WHATIF - nothing stopped, nothing started."; exit 0 }

# !! ORDER MATTERS. Supervisor first: it is what relaunches the driver, so killing the driver alone
# just gets it restarted on the OLD argument vector a few seconds later.
foreach ($p in $sup) { Stop-Process -Id $p.ProcessId -Force; Write-Host ("stopped supervisor {0}" -f $p.ProcessId) }
foreach ($p in $drv) { Stop-Process -Id $p.ProcessId -Force; Write-Host ("stopped driver {0}" -f $p.ProcessId) }
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList $args2
Start-Sleep -Seconds 6

$now = @(Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" |
         Where-Object { $_.CommandLine -match 'mode_d_supervisor' -and
                        $_.CommandLine -match ("-Line\s+" + [regex]::Escape($Line) + "(\s|$)") })
if ($now.Count -eq 0) {
    Write-Host "!! the replacement supervisor is NOT running. The watchdog will revive this line"
    Write-Host "!! WITHOUT the canary flags within 300s, which is SAFE but is not a canary."
    exit 1
}
Write-Host ("restarted, pid {0}" -f (($now | ForEach-Object { $_.ProcessId }) -join ", "))
Write-Host ("carries -SpecsPerTask : {0}" -f [bool]($now[0].CommandLine -match 'SpecsPerTask'))
Write-Host ""
Write-Host "NEXT: the flags live only in this process's argument vector. watchdog_fenced.ps1:231"
Write-Host "revives a dead line WITHOUT them (ledger R26-10), so re-check the live CommandLine"
Write-Host "before trusting any before/after measurement from this canary."
