# Send a local shell script to Myriad and run it under bash, BYTE-EXACTLY.
#
# The naive `Get-Content -Raw | ssh ... bash -s` path corrupts the payload: the script arrived
# with a UTF-8 BOM and CRLF endings, which bash reported as
#   bash: line 1: #!/bin/bash: No such file or directory
#   bash: line 9: $'\r': command not found
# Normalising the text in PowerShell did not fix it, because the pipe to a native command
# re-encodes. So the script is base64-encoded here and decoded on the far side: base64 is
# ASCII-safe, survives every layer of quoting, and is byte-exact by construction.
#
# ASCII-only, per the standing PS1 rule.
param(
    [Parameter(Mandatory = $true)][string]$ScriptPath,
    [string]$RemoteHost = 'myriad'
)

$text = [System.IO.File]::ReadAllText($ScriptPath) -replace "`r`n", "`n"
if ($text.Length -gt 0 -and [int]$text[0] -eq 0xFEFF) { $text = $text.Substring(1) }

$bytes = (New-Object System.Text.UTF8Encoding($false)).GetBytes($text)
$b64 = [System.Convert]::ToBase64String($bytes)

ssh -o BatchMode=yes -o ConnectTimeout=25 $RemoteHost "echo $b64 | base64 -d | bash"
