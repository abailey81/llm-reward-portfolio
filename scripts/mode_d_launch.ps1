# MODE-D LAUNCHER (2026-07-21) - the maximum-parallel campaign: TWELVE supervised driver lines
# at once (the Opus core + the H3 floor unit + all 10 replication legs), each with its own log.
#
# WHAT MODE D IS (runbook s.10): every line submits from L+0; the SGE priority ladder - core
# search/floor/tier-100 highest, legs -200..-280 in the registered queue order, tier-189+ blocks
# from -300 - makes the scheduler enforce the registered unified queue natively, so completion
# and truncation order are EXACTLY the pre-declared ones while the eligible backlog stays deep
# enough to harvest every idle window. Search waves run pack-2 (latency lane); bursts pack-5
# (throughput lane); C4 rungs are pipelined. All ops-only: no registered quantity changes (R88).
#
# USAGE (after the v2 FREEZE + on Tamer's explicit LAUNCH word - never before):
#   powershell -ExecutionPolicy Bypass -File scripts\mode_d_launch.ps1
# Stop everything: create outputs\campaign_cluster\STOP_CAMPAIGN (all lines check it).
# Monitoring: bash scripts/campaign_monitor.sh + the sentinel watch the shared mirror as usual;
# per-line logs at outputs\campaign_cluster\supervisor_<line>.log.

$ErrorActionPreference = "Continue"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo

# Queue order (must match config/preregistration.yaml model_suite.queue_order).
$lines = @(
  "core", "h3",
  "deepseek-v4-pro", "glm-5.2", "qwen3.6-27b", "qwen3.5-9b",
  "haiku-4.5", "gpt-5.6-luna", "nemotron-3-super", "sonnet-5", "gemini-3.5-flash", "kimi-k3"
)

$i = 0
foreach ($line in $lines) {
    $stagger = if ($line -eq "core") { 0 } else { 3600 + $i * 20 }   # CANARY SHIELD: legs start
    # ~1h after the core so most path breakage the C0 canary exists to catch surfaces before
    # any leg authoring is billed (bounded anyway; ~1h is negligible vs the legs' 3-4 days).
    # The +20s spacing spreads the poll phases (login-node kindness).
    Write-Host ("mode-D: starting supervised line '{0}' (stagger {1}s)" -f $line, $stagger)
    Start-Process powershell -ArgumentList @(
        "-ExecutionPolicy", "Bypass",
        "-File", (Join-Path $repo "scripts\mode_d_supervisor.ps1"),
        "-Line", $line, "-StaggerSecs", [string]$stagger
    )
    $i += 1
}
Write-Host ("mode-D: {0} supervised lines started. STOP file: outputs\campaign_cluster\STOP_CAMPAIGN" -f $lines.Count)
