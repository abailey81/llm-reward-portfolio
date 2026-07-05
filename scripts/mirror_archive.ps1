<#
.SYNOPSIS
    Mirror the irreplaceable run archives to a second physical drive (engineering review 2026-07-02).

.DESCRIPTION
    The campaign archive (LLM-authored reward code, prompts, reflections, per-seed records) is the ONE
    artifact in this project that cannot be regenerated: results REPLAY from the archive (CLAUDE.md
    prime directive 6) because LLM calls are non-deterministic. Everything else — panels, configs,
    code — is reconstructible; the archive is not. Until 2026-07-02 it lived on a single drive with no
    redundancy: a C: failure mid-campaign would have destroyed the experiment.

    This script robocopy-mirrors the archive roots to D:\llm_rp_archive_mirror\ (a different physical
    disk). /MIR keeps an exact replica (adds+updates+deletes); /R:2 /W:5 bounds retries so a locked
    in-flight file never stalls the mirror (it lands on the next pass); /XD excludes nothing today but
    is the hook for future scratch dirs. Run it:
      * manually after any pilot completes;
      * during the campaign: every 6 h via the watcher loop or a scheduled task —
        schtasks /Create /SC HOURLY /MO 6 /TN LLMRewardArchiveMirror
          /TR "powershell -ExecutionPolicy Bypass -File <repo>\scripts\mirror_archive.ps1"
    I/O-light (incremental after the first pass); safe to run beside training (reads only), but the
    2026-07-02 exclusive-phase discipline still prefers the recycle boundaries.

.PARAMETER MirrorRoot
    Destination root on the second drive (default D:\llm_rp_archive_mirror).

.PARAMETER Force
    Override the shrink guard (m8). By default a source whose record.json count is SMALLER than the
    existing mirror's is SKIPPED (a shrunken/emptied source would otherwise propagate the loss into the
    backup via /MIR). Pass -Force to mirror it anyway — e.g. after a deliberate, verified prune.
#>
param(
    [string]$MirrorRoot = "D:\llm_rp_archive_mirror",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

# The irreplaceable set: run archives + the frozen-design record + the manifest ledgers.
$sources = @(
    @{ src = Join-Path $repoRoot "outputs\campaign";     dst = Join-Path $MirrorRoot "campaign" },
    @{ src = Join-Path $repoRoot "outputs\sigma_pilot";  dst = Join-Path $MirrorRoot "sigma_pilot" },
    @{ src = Join-Path $repoRoot "outputs\prototype";    dst = Join-Path $MirrorRoot "prototype" },
    @{ src = Join-Path $repoRoot "outputs\tables";       dst = Join-Path $MirrorRoot "tables" },
    @{ src = Join-Path $repoRoot "data\manifest";        dst = Join-Path $MirrorRoot "manifest" }
)

New-Item -ItemType Directory -Force $MirrorRoot | Out-Null
$stamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$log = Join-Path $MirrorRoot "mirror.log"
Add-Content $log "=== mirror pass $stamp ==="

foreach ($pair in $sources) {
    if (-not (Test-Path $pair.src)) { Add-Content $log "SKIP (absent): $($pair.src)"; continue }
    # Shrink guard (m8): /MIR propagates DELETIONS, so a shrunken or emptied SOURCE (a bad prune, a
    # half-synced drive, a corrupted run dir) would wipe archived history from the BACKUP in a single
    # pass. Test-Path above only catches a FULLY-absent source. Count record.json (the per-run archive
    # marker) recursively in the source vs the existing mirror; if the mirror holds MORE than the source,
    # the source has lost archives -> SKIP loudly rather than mirror the loss, unless -Force is passed.
    # PS 5.1-safe: @(...) forces an array so .Count is valid for 0/1 matches; no ternary / no && used.
    $srcCount = @(Get-ChildItem -LiteralPath $pair.src -Recurse -Filter record.json -File -ErrorAction SilentlyContinue).Count
    $dstCount = 0
    if (Test-Path $pair.dst) {
        $dstCount = @(Get-ChildItem -LiteralPath $pair.dst -Recurse -Filter record.json -File -ErrorAction SilentlyContinue).Count
    }
    if (($dstCount -gt $srcCount) -and (-not $Force)) {
        $skipMsg = "SKIP (shrink guard): $($pair.src) has $srcCount record.json but mirror $($pair.dst) has $dstCount -- refusing to mirror history loss (pass -Force to override)"
        Add-Content $log $skipMsg
        Write-Warning $skipMsg
        continue
    }
    # robocopy exit codes 0-7 = success variants; >=8 = failure. Never let one root abort the rest.
    robocopy $pair.src $pair.dst /MIR /R:2 /W:5 /NP /NDL /NFL /NJH | Out-Null
    $code = $LASTEXITCODE
    $verdict = if ($code -ge 8) { "FAIL($code)" } else { "ok($code)" }
    Add-Content $log "$verdict : $($pair.src) -> $($pair.dst)"
    if ($code -ge 8) { Write-Warning "mirror FAILED for $($pair.src) (robocopy $code)" }
}

$total = (Get-ChildItem $MirrorRoot -Recurse -File | Measure-Object Length -Sum).Sum / 1MB
Add-Content $log ("mirror size: {0:N1} MB" -f $total)
Write-Host ("mirror pass done -> {0}  ({1:N1} MB; log: {2})" -f $MirrorRoot, $total, $log)
