# selftest_revive_args.ps1 -- FALSIFYING TEST for R26-10.
#
# WHAT IT PROVES: that watchdog_fenced.ps1's revive path PRESERVES a line's duration settings
# (-SpecsPerTask / -HRt), and that it can NEVER apply them to 'core'.
#
# WHY IT IS WRITTEN THIS WAY. The watchdog is a long-lived `while ($true)` process, so it cannot be
# dot-sourced (that would hang) and it cannot be unit-tested by import. Instead this walks the file's
# ABSTRACT SYNTAX TREE, lifts the Get-ReviveArgs function definition out of it, defines that function
# in THIS session, and CALLS it. That is a behavioural test of the real shipped code, not a regex
# over the source.
#
# IT IS DESIGNED TO FAIL AGAINST THE PRE-FIX FILE, which is the only thing that makes it evidence:
# before the fix there is no Get-ReviveArgs at all, and the literal ArgumentList carries no
# -SpecsPerTask. A test that cannot fail verifies nothing.
#
# RUN:  powershell -ExecutionPolicy Bypass -File docs\ops\watch\selftest_revive_args.ps1
# EXIT: 0 = all assertions passed. 1 = a real failure. ASCII-only by contract.

$ErrorActionPreference = "Stop"
$fails = 0
$passes = 0

function Assert-True {
    param([bool]$Cond, [string]$Msg)
    if ($Cond) { $script:passes++; Write-Output ("  PASS  " + $Msg) }
    else       { $script:fails++;  Write-Output ("  FAIL  " + $Msg) }
}

# this file lives at <repo>\docs\ops\watch\, so the repo root is FOUR parents up, not three.
# (Three was the first attempt and it produced '<repo>\docs\docs\ops\...', which made every
# assertion fail for a PATH reason and would have masked the real pre-fix falsification.)
$repo = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)))
$wd   = Join-Path $repo "docs\ops\watchdog_fenced.ps1"
$cfg  = Join-Path $repo "docs\ops\watch\LINE_DURATION.json"

Write-Output ("watchdog : " + $wd)
Write-Output ("config   : " + $cfg)
Write-Output ""

# ---------------------------------------------------------------- 1. the data file
Write-Output "--- 1. LINE_DURATION.json ---"
Assert-True (Test-Path $cfg) "LINE_DURATION.json exists"
$j = $null
if (Test-Path $cfg) { $j = Get-Content -Raw $cfg | ConvertFrom-Json }
Assert-True ($j -ne $null) "LINE_DURATION.json parses as JSON"
if ($j -ne $null) {
    $names = @($j.lines.PSObject.Properties.Name)
    Assert-True ($names.Count -eq 6) ("exactly 6 lines listed (got " + $names.Count + ")")
    Assert-True (-not ($names -contains "core")) "'core' is ABSENT from the data file (it must stay at 8 specs)"
    foreach ($n in $names) {
        $e = $j.lines.$n
        Assert-True ($e.SpecsPerTask -eq 24) ("$n SpecsPerTask = 24")
        Assert-True ($e.HRt -eq "45:0:0")    ("$n HRt = 45:0:0")
    }
}

# ---------------------------------------------------------------- 2. lift the function via AST
Write-Output ""
Write-Output "--- 2. Get-ReviveArgs, lifted from the shipped file by AST ---"
Assert-True (Test-Path $wd) "watchdog_fenced.ps1 exists"

$tokens = $null; $errors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseFile($wd, [ref]$tokens, [ref]$errors)
Assert-True ($errors.Count -eq 0) ("watchdog_fenced.ps1 parses clean (" + $errors.Count + " parse errors)")

$fn = $ast.Find({ param($n)
    $n -is [System.Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq "Get-ReviveArgs"
}, $true)
Assert-True ($fn -ne $null) "Get-ReviveArgs is DEFINED (pre-fix this FAILS, which is the point)"

if ($fn -ne $null) {
    # define it here, then exercise it
    Invoke-Expression $fn.Extent.Text

    $common = @{ Repo = $repo; ExcludeHosts = "node-d00a-230"; OutDir = "outputs\x"; RemoteRoot = "~/Scratch/y"; ConfigPath = $cfg }

    Write-Output ""
    Write-Output "  -- a line that IS in the file keeps its duration --"
    $a = @(Get-ReviveArgs -Line "kimi-k3" @common)
    $s = ($a -join " ")
    Assert-True ($s -match "-SpecsPerTask")      "kimi-k3 revive carries -SpecsPerTask"
    Assert-True ($s -match "24")                 "kimi-k3 revive carries 24"
    Assert-True ($s -match "-HRt")               "kimi-k3 revive carries -HRt"
    Assert-True ($s -match "45:0:0")             "kimi-k3 revive carries 45:0:0"
    Assert-True ($s -match "-Line kimi-k3")      "kimi-k3 revive still names the line"
    Assert-True ($s -match "node-d00a-230")      "kimi-k3 revive still carries the host fence"

    Write-Output ""
    Write-Output "  -- CORE IS PROTECTED, and not merely by being absent from the file --"
    $c = @(Get-ReviveArgs -Line "core" @common)
    $cs = ($c -join " ")
    Assert-True ($cs -notmatch "-SpecsPerTask") "core revive carries NO -SpecsPerTask"
    Assert-True ($cs -notmatch "-HRt")          "core revive carries NO -HRt"
    Assert-True ($cs -match "-Line core")       "core revive still names the line"

    Write-Output ""
    Write-Output "  -- MUTATION: even if the data file listed core, the guard must refuse --"
    $tmp = Join-Path $env:TEMP ("ld_mut_" + $PID + ".json")
    '{ "lines": { "core": { "SpecsPerTask": 24, "HRt": "45:0:0" } } }' | Set-Content -Encoding ascii $tmp
    $m = @(Get-ReviveArgs -Line "core" -Repo $repo -ExcludeHosts "node-d00a-230" -OutDir "outputs\x" -RemoteRoot "~/Scratch/y" -ConfigPath $tmp)
    $ms = ($m -join " ")
    Assert-True ($ms -notmatch "-SpecsPerTask") "core STILL gets no -SpecsPerTask even when the file names it"
    Remove-Item $tmp -ErrorAction SilentlyContinue

    Write-Output ""
    Write-Output "  -- FAIL-SAFE: a missing config yields the PRE-FIX argument vector --"
    $g = @(Get-ReviveArgs -Line "kimi-k3" -Repo $repo -ExcludeHosts "node-d00a-230" -OutDir "outputs\x" -RemoteRoot "~/Scratch/y" -ConfigPath (Join-Path $env:TEMP "definitely_absent_$PID.json"))
    $gs = ($g -join " ")
    Assert-True ($gs -notmatch "-SpecsPerTask") "missing config => no overrides (fails SAFE, not to a guess)"
    Assert-True ($gs -match "-Line kimi-k3")    "missing config => the line is still revived"

    Write-Output ""
    Write-Output "  -- FAIL-SAFE: a MALFORMED config also yields the pre-fix vector --"
    $bad = Join-Path $env:TEMP ("ld_bad_" + $PID + ".json")
    "{ this is not json" | Set-Content -Encoding ascii $bad
    $b = @(Get-ReviveArgs -Line "kimi-k3" -Repo $repo -ExcludeHosts "node-d00a-230" -OutDir "outputs\x" -RemoteRoot "~/Scratch/y" -ConfigPath $bad)
    Assert-True ((($b -join " ") -notmatch "-SpecsPerTask")) "malformed config => no overrides"
    Remove-Item $bad -ErrorAction SilentlyContinue

    Write-Output ""
    Write-Output "  -- a line NOT listed is revived byte-identically to before --"
    $u = @(Get-ReviveArgs -Line "sonnet-5" @common)
    Assert-True ((($u -join " ") -notmatch "-SpecsPerTask")) "unlisted line gets no overrides"
}

# ---------------------------------------------------------------- 3. the caller actually uses it
Write-Output ""
Write-Output "--- 3. the revive path CALLS Get-ReviveArgs (a function nobody calls fixes nothing) ---"
$src = Get-Content -Raw $wd
Assert-True ($src -match "Start-Process\s+powershell\s+-ArgumentList\s+\(Get-ReviveArgs") `
    "the Start-Process revive uses Get-ReviveArgs"

# ---------------------------------------------------------------- 4. ASCII contract
Write-Output ""
Write-Output "--- 4. ASCII-only contract ---"
$bytes = [System.IO.File]::ReadAllBytes($wd)
$nonAscii = @($bytes | Where-Object { $_ -gt 127 }).Count
Assert-True ($nonAscii -eq 0) ("watchdog_fenced.ps1 is ASCII-only (" + $nonAscii + " non-ASCII bytes)")

Write-Output ""
Write-Output ("RESULT: " + $passes + " passed, " + $fails + " failed")
if ($fails -gt 0) { exit 1 } else { exit 0 }
