# PLAN B — the fallback host (2026-07-06; Tamer's 16" Intel i9 MacBook Pro 2019)

**Purpose.** If the campaign host (the RTX-4050 laptop) suffers an unrecoverable failure mid-run,
the study must survive with its integrity intact — and until then, the second machine should earn
its keep. Three roles, in order of value:

## Role 1 — the OFF-SITE third archive copy (activate NOW; the highest-value, zero-risk role)
The archive is the ONE irreplaceable artifact, and today BOTH copies (C: + the D: mirror) live in
the SAME laptop — one theft/fire/motherboard failure destroys the study. The Mac becomes the third,
physically-separate copy:
- Simplest robust setup: **Syncthing** (free, LAN+relay, versioned) syncing
  `outputs/` + `data/gold/` + `data/manifest/` one-way (send-only from the PC, receive-only on the
  Mac). Alternatives: an `rsync`/`robocopy`-over-SMB scheduled job, or Tailscale + rsync.
- Verify the copy exactly like the D: mirror: on the Mac,
  `python scripts/archive_integrity.py verify-mirror <synced outputs/prototype>` (inside the
  Docker image below, or any python 3.11 with no extra deps — the script is stdlib+hashlib only).
- Licence note: the gold panel is licensed Refinitiv data; Tamer's OWN second machine is fine —
  never a cloud copy.

## Role 2 — the external watcher + write-up station (during the campaign)
- **Deadman receiver:** point `monitor.py --heartbeat <url>` at a healthchecks.io check whose
  alert goes to Tamer's phone/email; the Mac (always-on browser/mail) is where the alarm lands.
  This is the ONLY detector for host death (power loss, kernel panic) — runbook §5 B6.
- **Read-only dashboards on the synced copy:** `sentinel.py <synced-root> --once` gives a lagged
  health verdict without touching the run host.
- **Write-up/compile station:** the PDF pipeline (pandoc + Tectonic) installs natively on macOS;
  the paper chapters are plain markdown — Tamer can write and compile the whole campaign window
  on the Mac while the PC trains untouched.

## Role 3 — the TRAINING LIFEBOAT (the actual Plan B; prepare now, use only on the trigger)

### The hard facts (why the design is what it is)
- The Radeon 5300M/5500M has **no CUDA** and no usable torch backend on Intel macOS → CPU-only.
- PyTorch **dropped macOS x86_64 wheels after 2.2** → the pinned stack (torch 2.6.0, SB3 2.8.0)
  CANNOT run natively. **Docker (linux/amd64) can run the EXACT pinned versions in their CPU
  build** — `docker/Dockerfile.planb` + `requirements-planb-cpu.lock` (identical pins, torch from
  the CPU index). Software drift: zero. Device numerics: CPU ≠ CUDA — inherent to ANY fallback and
  handled by the protocol below, never hidden.
- Honest throughput: the i9-9880H/9980HK (8C/16T, thermally constrained chassis) at this
  overhead-bound workload ≈ **2–4× slower** than the RTX-4050 box (~2–3 h/training single worker;
  2 concurrent workers RAM/thermals permitting). A campaign TAIL survives on it; a FULL campaign
  would take ~2 months — it is a lifeboat, not a plan.

### The trigger (pre-declared, so using it is never a judgment call under stress)
Unrecoverable failure of the campaign host: hardware death, or repair time that would push the
run past the write-up deadline (> ~4 days of confirmed downtime). NOT for: reboots, thermal
pauses, resumable crashes — the supervisor + `--resume` own those.

### The migration protocol (integrity-preserving, in order)
1. **Recover the archive** from the D: mirror (or the Mac's synced copy):
   `archive_integrity.py verify-mirror` FIRST — never trust an unverified copy.
2. **Migrate at a SEED boundary, never mid-pair (THE critical rule).** The CRN design pairs
   arm A seed k with arm B seed k; a pair split across devices breaks the common-random-numbers
   variance reduction. The fallback therefore takes over WHOLE seeds across ALL arms (e.g. the PC
   completed seeds 0–189 everywhere -> the Mac runs seeds 190+ for every arm). Within any seed,
   every arm's training shares one device -> every PAIR stays device-homogeneous.
3. **Search-stage failure instead?** Whole ARMS migrate (an arm's search completes on one device);
   arms already completed on the PC stand.
4. **Run CPU-only inside the container** (`--gpu 0 --cpu 2`; the S6 real-run `--cpu` refusal is
   PC-specific guidance — on the fallback the DECLARED device IS the cpu, and
   `metrics.device` records it per record, which is exactly why S6 added the field).
5. **Disclose**: the device split is already recorded per record; CH4/limitations gains one
   sentence naming the failure date, the seed boundary, and the per-device split; the analysis can
   condition on device as a robustness split (per-seed records carry everything needed).
6. Resume-safety is device-agnostic: run-id keyed records + ledgered failures + the hash-verified
   caches work identically in the container (certify once with `crash_rehearsal.py` on the Mac).

### The pre-registration contingency clause (batch into the seed-ratification amendment)
> *Hardware-failure contingency: in the event of unrecoverable campaign-host failure, remaining
> units continue on a pre-specified fallback host (CPU; identical pinned software via container).
> Migration occurs only at seed boundaries across all arms, preserving device-homogeneous
> common-random-number pairs; the training device is recorded per record and reported; no
> completed unit is re-run.*

### Prep checklist (Tamer, ~1 hour on the Mac — do BEFORE the campaign)
- [ ] Install Docker Desktop (Intel build) + git; clone the repo.
- [ ] Copy `data/gold/` + `data/manifest/` (USB/LAN — licensed data stays on your machines).
- [ ] `docker build -f docker/Dockerfile.planb -t llm-rp-planb .`
- [ ] Verify the stack: the image's default CMD prints torch 2.6.0 / SB3 2.8.0 / cuda False.
- [ ] Certify the machinery: the keyless dry-run + `crash_rehearsal.py` inside the container
      (commands in the Dockerfile header) — both must PASS.
- [ ] Set up Role 1 (Syncthing share) + Role 2 (healthchecks.io check on the Mac's account).
- [ ] Note the Mac's RAM size in this doc (decides 1 vs 2 fallback workers: ~2.1 GiB/worker + OS).
