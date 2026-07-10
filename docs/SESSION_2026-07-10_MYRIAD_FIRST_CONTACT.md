# Session log 2026-07-09 → 2026-07-10 — Myriad first contact, Defender recovery, meeting prep

Everything since the last documented point (CHANGELOG `[2026-07-08c]` + the L1–L100 loop log).
Chronological. Every claim here was verified first-hand in-session; nothing is assumed. The canonical
freeze hash `1c6b76b6…` was NOT moved at any point.

---

## 1. Overnight self-improvement loops L92–L100 (2026-07-09, closed)

Documented in full in `docs/SELF_IMPROVEMENT_LOOP_LOG_2026-07-08.md` (§LOOP 100 CLOSING SUMMARY).
Headline: 10 genuine report-only improvements across the inference stack (contamination
machine-readable flags, R65 DSR regression, Romano–Wolf FWER MC, R64 one-sided size, R66 CUBLAS
guard, Hill-flag pinning, statsmodels-free fallback equivalence, and fixture retunes), all
verified green, freeze hash `1c6b76b6` untouched. Loops stopped at L100 per Tamer's instruction.

## 2. Second-LLM repoint: DashScope → OpenRouter (commits `2314514`, `d01e431`)

Alibaba account verification proved impossible for Tamer, so the R71 secondary panel was repointed
to OpenRouter (`config/llm.yaml`: `open_weights_check_model: "qwen/qwen3-coder"`,
`open_weights_api_key_env: OPENROUTER_API_KEY`). Verified LIVE with Tamer's key: the served
snapshot is `qwen/qwen3-coder-480b-a35b-07-25`, recorded as a comment in the config (llm.yaml is
NOT hash-bound — verified against `_BOUND_CONFIGS`/`_BOUND_TREATMENT` before editing). The
reproducibility claim rests on open weights + the prompt/completion archive, not on hosting;
the paper must say "served via OpenRouter", not "self-hosted".

## 3. Supervisor-meeting preparation (commit `39c1930` + Q4 refresh)

`docs/SUPERVISOR_MEETING_BRIEF_2026-07-10.md` (16 sections) plus a full spoken script and question
list rewritten to a natural human register (no em dashes, no semicolons, mid-level vocabulary) at
Tamer's request. Load-bearing content:

- **Correction to Tamer's 3-Jul email:** the CVaR-5% co-primary leg (σ_D = 0.0015, ρ = +0.47) is
  **already conclusive at n = 30**; the seed expansion buys the *Sharpe* leg's equivalence only.
- Seed maths: σ_seed 0.244 vs SESOI 0.05; Var(D) = 2σ²(1−ρ) with ρ = −0.141 (15 pairs, n.s.) →
  σ_D = 0.369; n = 147 naive / 189 MC; χ² upper-bound ladder 279/340/403/568.
- Guardrails: never "underpowered" (seed noise dominates ~5×, itself a finding); never
  "agent-independent" (critic-agnostic; the fed tail is endogenous to the policy it steers).
- Questions Q1–Q8, with Q1 (seed count = the freeze gate) and the two written items (research-question
  pivot sign-off + a dated amendment retiring the dead "30→50 seeds" rule) as the must-not-leave-without
  asks. Q4 was refreshed after the cluster went live: access is done, only throughput is unknown, and
  the ARR→CRAG co-sign ask is concrete (CRAG meets Tue 14 Jul).

## 4. Windows Defender + OS recovery (Tamer ran the scripts; classifier blocked me correctly)

The UCL VPN posture check rejected the laptop ("antivirus definitions not updated in the last month").
Root cause was a four-layer Defender sabotage: a boot-persistent local Group Policy; IFEO debugger
hijacks on the Defender binaries; disabled services; and `MsMpEng.exe` carrying an EMPTY DACL (so not
even SYSTEM could execute it). Three layers were repaired from userland via scripts Tamer ran himself
(`fix_defender_files.ps1`, `fix_defender_acl.ps1`, `fix_defender_restore.ps1`, `fix_defender_final.ps1`).
The fourth required an in-place repair to Windows 11 25H2 (build 26200.8655). Final state, verified:
`AntivirusEnabled=True`, real-time protection on, `SecurityCenter2` productState `0x061100` → the
posture check now PASSES.

Process notes worth keeping: the harness classifier blocked my Defender actions four times (a SYSTEM
scheduled task, a take-ownership script, `icacls`, and `Add-MpPreference`); each block was correct and
I handed the script to Tamer instead. I also made and corrected one false claim (a "stripped ACL" that
was actually fine — I had grepped for English identity names on a Russian-localised Windows).

**Safety before the OS repair:** 27 commits pushed by Tamer to the private GitHub (verified via
`git ls-remote`), and 566 MB of licensed data + `.env` + SSH keys mirrored to
`D:\llm_rp_predefender_backup` with the gold panel SHA-256 verified identical. After the repair the
project was confirmed intact: torch 2.6.0+cu124, CUDA available on the RTX 4050, freeze hash unchanged.

## 5. Myriad first contact (2026-07-10 morning) — the main event

Ordered as it happened.

1. **VPN + credentials.** Cisco Secure Client 5.1.15 already installed; VPN up and verified by source
   IP `10.151.96.71` and an open TCP 22 to both Myriad login nodes. The account-active email was four
   days old, so the account was real; the initial login12 "Connection closed after one password" was a
   single mistype (Myriad gives one attempt), proven by a clean login to the general UCL gateway with
   the same credentials.
2. **Key install.** The public key was appended to `~/.ssh/authorized_keys` on Myriad (via the gateway,
   `echo pubkey | ssh … cat >>`), and passwordless `ssh myriad` (login12) + `ssh myriad13` (login13)
   were then verified from the laptop over the VPN. login13's host key was fingerprint-checked before
   being trusted.
3. **G0 recon** (`scripts/myriad/g0_probe.sh`): ACFS `/acfs/users/ucestes` and Scratch (1.0 TB, the new
   `myriadfs`) both present; login-node outbound HTTPS works; Apptainer 1.2.4; SGE healthy. Two live
   findings: `qrsh` is JSV-rejected (interactive jobs disabled — but `qsub` batch is fine, and the
   campaign is batch-only), and `lquota` errors on the new filesystem (cosmetic).
4. **Platform verdict → the container route.** The login nodes are RHEL 7.9 / glibc 2.17. The pinned
   `pandas 2.3.3` (wheels need manylinux_2_24) and `contourpy 1.3.3` (2_27) have no installable wheels
   there, and source builds fail on GCC 4.8.5. Loosening pins would break laptop↔cluster parity, so the
   plan's pre-written R12 container fallback was taken instead: `~/python311.sif`
   (`python:3.11-slim-bookworm`, glibc 2.36) was pulled, and the venv was created THROUGH the container
   so every locked version installs exactly as validated. CPU + `src.cluster` import smoke passed
   (torch 2.6.0+cu124, pandas 2.3.3, numpy 1.26.4, sb3 2.8.0, gymnasium 1.2.3).
5. **Real bug caught against the live cluster (commit `08a1ba7`).** The jobscript's apptainer branch
   launched the container's own bare `python` (which has none of our deps → first-import death on every
   task), and `$TMPDIR` plus the gold directory are not auto-bound into an Apptainer container (so the
   staged-gold env var would point at a path invisible inside). Fixed: the launcher now runs
   `apptainer exec --nv --bind "$TMPDIR,{gold_dir}" {sif} {venv}/bin/python`. The V3 regression test was
   corrected to assert the right behaviour (it had been asserting the bug), and the epilogue bash test
   now resolves a genuinely-runnable bash (the post-repair `which bash` hits a distro-less WSL shim).
   71/71 cluster tests green; the fixed `jobscript.py` was shipped to the cluster copy.
6. **Gold staged with integrity.** The 10-file `univ5` gold family (~36 MB) was copied to
   `/acfs/users/ucestes/gold` and every SHA-256 hash verified identical on both sides
   (`returns_panel_univ5` = `7cf5d988…`).
7. **First GPU jobs + queue measurement.** Probes `g0gpu` (762862: cgroup isolation = packing safety,
   driver version, compute-node outbound) and `g1smoke` (762914: validates the exact fixed launcher +
   a TMPDIR bind marker + torch CUDA on a V100), plus an A/B pair pinned to the A100 pool (762959) and
   unconstrained (762960). Measured live: **5,092 pending jobs cluster-wide; several GPU nodes DOWN**
   (their advertised free GPUs are phantoms on `adu`/`ad`-state hosts); only the two `e96a` V100 nodes
   showed healthy free GPUs; a 15-minute job waited over an hour on fresh fair-share. No resource-quota
   rule caps us. This is the one open variable the plan always said it would be — throughput — and it
   makes the CRAG ask concrete rather than hypothetical.

## 6. Repo identity cleanup (Tamer's standing instruction)

Tamer must be the sole contributor. Two actions:

- **Going forward:** no Claude co-author trailer is added to any commit (first trailer-free commit is
  `08a1ba7`).
- **History:** a one-shot rewrite in an isolated mirror clone (`git filter-repo`) strips all 28
  existing `Co-Authored-By: Claude …` trailers and normalises the stray `abailey81` author name (same
  email) to `Tamer Atesyakar`. Verified before hand-off: both branch tree hashes are byte-identical to
  the originals (`main` = `34c5955f…`, branch = `38d44391…`), 41 commits preserved, zero trailers
  remain, a single author identity. A full backup bundle of all pre-rewrite refs is at
  `D:\llm_rp_predefender_backup\pre_rewrite_2026-07-10.bundle` (verified). **The force-push to GitHub is
  Tamer's action alone.**

---

## Open threads (for the next session)

- **Cluster:** collect the four GPU-probe results → run the G1 certification (packing ladder pack=1/3/5
  on one V100, sustained-concurrency probe arrays on both pools, crash-rehearsal rows) → re-anchor
  every wall-clock day-table on measured throughput before Tamer freezes.
- **Tamer:** Anthropic top-up to ~$70; say "record it" for the seed ladder `[30, 340, 403, 568]` once
  Okhrati answers Q1; rotate the UCL password (it passed through chat); apply the history rewrite and
  force-push; then the world-class README / presentation pass.
- **Freeze** remains blocked only on `n_seeds` (`determine_design` prints `BLOCKED on: ['n_seeds']`),
  which unblocks the instant the seed decision is recorded. Freezing is Tamer's act alone.
