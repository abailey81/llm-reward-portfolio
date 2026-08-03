# Selftest for the P202 completion-awareness predicate in docs/ops/watchdog_fenced.ps1.
#
# It extracts Get-LineTerminalState FROM THE REAL SOURCE FILE rather than copying it,
# because a selftest that exercises a copy can pass while the integrated path differs
# (the standing lesson from P193/P196).
#
# Cases L1-L6 are the AUDITOR'S REFUTATION, pinned as permanent regressions: the first
# version of this predicate would have permanently killed D12's six legs.

$ErrorActionPreference = "Stop"
# derive the repo from this file's own location: docs/ops -> docs -> repo
$repoReal = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$src      = Join-Path $repoReal "docs\ops\watchdog_fenced.ps1"

# ---- extract the function verbatim from source -----------------------------
$all   = Get-Content -Path $src
$start = ($all | Select-String -Pattern '^function Get-LineTerminalState' | Select-Object -First 1).LineNumber
if (-not $start) { Write-Host "FATAL: could not find the function in source"; exit 1 }
$end = $null
for ($i = $start; $i -lt $all.Count; $i++) { if ($all[$i] -eq '}') { $end = $i + 1; break } }
if (-not $end) { Write-Host "FATAL: could not find the function end"; exit 1 }
Invoke-Expression (($all[($start-1)..($end-1)]) -join "`n")
Write-Host ("extracted {0} lines of REAL source" -f ($end - $start + 1))

$fixture = Join-Path $env:TEMP ("p202_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force $fixture | Out-Null

$START    = "2026-08-03 01:00:00 | supervisor[x] | line supervisor started: scripts/run_campaign_cluster.py --resume"
$ATTEMPT  = "2026-08-03 01:00:01 | supervisor[x] | attempt 1: launching the driver"
$EXITING  = "2026-08-03 01:00:02 | supervisor[x] | line supervisor exiting."
$RELAUNCH = "2026-08-03 01:00:00 | supervisor[x] | driver exited -1 - relaunching in 600s; Myriad arrays unaffected"
$COMPLETE = "2026-08-03 01:00:00 | supervisor[x] | driver exited 0 - LINE COMPLETE."
$AMBIG    = "2026-07-28 23:14:45 | supervisor[x] | driver exited 0 - LINE COMPLETE (or gate stop handled)."
$GATE     = "2026-08-03 01:00:00 | supervisor[x] | driver exited 3 - STOPPED AT THE REVIEW GATE, awaiting approval."
$WEIRD    = "2026-08-03 01:00:00 | supervisor[x] | driver exited 3221225786 - relaunching in 600s"

function MakeLog([string]$name, [string[]]$body, [switch]$WithDriverOK) {
    Set-Content -Path (Join-Path $fixture ("supervisor_{0}.log" -f $name)) -Value $body -Encoding ascii
    $d = if ($WithDriverOK) { @("noise", "[campaign] TIERED OK - 7 tiers, sizes [30, 70]") } else { @("noise", "no verdict here") }
    Set-Content -Path (Join-Path $fixture ("driver_{0}.log" -f $name)) -Value $d -Encoding ascii
}

$pass = 0; $fail = 0
function Check([string]$label, [string]$got, [string]$want) {
    if ($got -eq $want) { $script:pass++; Write-Host ("  PASS  {0,-62} -> {1}" -f $label, $got) }
    else { $script:fail++; Write-Host ("  FAIL  {0,-62} -> got {1}, want {2}" -f $label, $got, $want) }
}

$outDir = $fixture

MakeLog "b_relaunch" @($START, $RELAUNCH, $EXITING) -WithDriverOK
Check "B last outcome is a relaunch" (Get-LineTerminalState "b_relaunch") "REVIVE"

MakeLog "c_one" @($START, $RELAUNCH, $START, $COMPLETE, $EXITING) -WithDriverOK
Check "C exactly ONE trailing completion (confirmation retry)" (Get-LineTerminalState "c_one") "REVIVE"

MakeLog "d_two" @($START, $COMPLETE, $EXITING, $START, $COMPLETE, $EXITING) -WithDriverOK
Check "D two consecutive completions + clean exit + driver OK" (Get-LineTerminalState "d_two") "COMPLETE"

MakeLog "e_split" @($COMPLETE, $COMPLETE, $RELAUNCH, $EXITING) -WithDriverOK
Check "E two completions but last outcome is a relaunch" (Get-LineTerminalState "e_split") "REVIVE"

MakeLog "f_episode" @($COMPLETE, $COMPLETE, $RELAUNCH, $START, $COMPLETE, $EXITING) -WithDriverOK
Check "F old completion episode, restart, then ONE completion" (Get-LineTerminalState "f_episode") "REVIVE"

Check "G missing log (fail-safe)" (Get-LineTerminalState "g_absent") "REVIVE"

MakeLog "h_nooutcome" @($START, $ATTEMPT) -WithDriverOK
Check "H log with no outcome lines (fail-safe)" (Get-LineTerminalState "h_nooutcome") "REVIVE"

MakeLog "i_gate" @($START, $COMPLETE, $COMPLETE, $GATE, $EXITING) -WithDriverOK
Check "I review-gate stop wins over prior completions" (Get-LineTerminalState "i_gate") "GATE"

MakeLog "j_override" @($START, $COMPLETE, $EXITING, $START, $COMPLETE, $EXITING) -WithDriverOK
New-Item -ItemType File -Force (Join-Path $fixture "REVIVE_j_override") | Out-Null
Check "J REVIVE_<safe-line> override releases a suppressed line" (Get-LineTerminalState "j_override") "REVIVE"

# ---- THE AUDITOR'S REFUTATION, PINNED ---------------------------------------
Write-Host ""
Write-Host "AUDITOR REGRESSION CASES (the first predicate FAILED all of these):"

MakeLog "L1_d12" (@($START) + (1..10 | ForEach-Object { $AMBIG }) + @($EXITING))
Check "L1 D12's ten AMBIGUOUS completions must NOT suppress" (Get-LineTerminalState "L1_d12") "REVIVE"

MakeLog "L2_d12_ok" (@($START) + (1..10 | ForEach-Object { $AMBIG }) + @($EXITING)) -WithDriverOK
Check "L2 ...not even when the driver log DOES carry an OK" (Get-LineTerminalState "L2_d12_ok") "REVIVE"

MakeLog "L3_killed" @($START, $COMPLETE, $EXITING, $START, $COMPLETE, $EXITING, $START, $ATTEMPT) -WithDriverOK
Check "L3 supervisor KILLED mid-attempt after old completions" (Get-LineTerminalState "L3_killed") "REVIVE"

MakeLog "L4_nodriverok" @($START, $COMPLETE, $EXITING, $START, $COMPLETE, $EXITING)
Check "L4 two completions but NO campaign-level OK in driver log" (Get-LineTerminalState "L4_nodriverok") "REVIVE"

MakeLog "L5_weird3" @($START, $COMPLETE, $COMPLETE, $WEIRD, $EXITING) -WithDriverOK
Check "L5 exit 3221225786 must NOT read as a review-gate stop" (Get-LineTerminalState "L5_weird3") "REVIVE"

MakeLog "L6_mixed" @($START, $AMBIG, $EXITING, $START, $COMPLETE, $EXITING) -WithDriverOK
Check "L6 one ambiguous + one decisive is only ONE decisive" (Get-LineTerminalState "L6_mixed") "REVIVE"

# ============================ REAL-DATA CASES ==============================
Write-Host ""
Write-Host "REAL logs from the live campaign:"
$outDir = Join-Path $repoReal "outputs\campaign_cluster_run4"

Check "A  h3 (568/568, churned 278x)" (Get-LineTerminalState "h3") "COMPLETE"
Check "A2 gemini-2.5-flash (568 x 5 arms = 2840)" (Get-LineTerminalState "gemini-2.5-flash") "COMPLETE"

# K: NO CURRENTLY-WORKING LINE MAY BE SUPPRESSED. This is the safety property, and it is
# what caught gemini's completion live.
$live = @("core","deepseek-v4-pro","glm-5.2","qwen3.6-27b","qwen3.5-9b","haiku-4.5",
          "gpt-5.6-luna","nemotron-3-super","sonnet-5","kimi-k3")
foreach ($l in $live) {
    Check ("K live line must stay revivable: " + $l) (Get-LineTerminalState $l) "REVIVE"
}

Remove-Item -Recurse -Force $fixture -ErrorAction SilentlyContinue
Write-Host ""
Write-Host ("SELFTEST: {0} passed, {1} failed" -f $pass, $fail)
if ($fail -gt 0) { exit 1 }
exit 0
