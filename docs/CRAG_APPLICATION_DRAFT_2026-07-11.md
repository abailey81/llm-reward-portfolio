# CRAG application draft — GPU allocation for the IFTE0008 confirmatory campaign

> **For Tamer to review, edit, and send (with Dr Okhrati's co-sign) before/at the CRAG meeting
> Tue 14 July 2026.** Everything quantitative below is measured, not estimated — sources in
> brackets. Trim to taste; the committee-facing text is the block quote.

---

## The ask (committee-facing text)

> **Request:** a short-term reserved/priority GPU allocation on Myriad for a pre-registered MSc
> dissertation experiment (IFTE0008, UCL Institute of Finance & Technology; supervisor
> Dr Ramin Okhrati), submission deadline 1 September 2026.
>
> - **Compute:** ≈ 2,760 GPU-hours on the V100 pool (≈ 3,830 GPU-h at the pre-registered
>   maximum), as ~5,600 independent array tasks of ~33 minutes each (measured: 102.2 steps/s
>   per training on a V100-PCIE-32GB, job 764154).
> - **Shape of the request:** e.g. **12 dedicated V100s for 10 days** (≈ 2,880 GPU-h) within
>   28 July – 15 August 2026, or an equivalent priority arrangement at the committee's
>   discretion. Any concurrency level works — the workload is embarrassingly parallel,
>   checkpointed, and resumable; a reservation only converts a fair-share-variable completion
>   time into a predictable one ahead of the hard submission deadline.
> - **Good citizenship (already engineered):** tasks request 1–2 CPU cores each (measured:
>   a training uses < 1 core, so we do not compete for CPU capacity); tight, measured walltime
>   requests (backfill-friendly); GPU packing of multiple trainings per card where efficient
>   (cgroup-safe, verified on-node); node-local tmpfs data staging (no shared-FS hammering);
>   `-r y` resumable arrays; all software containerised (Apptainer). The mandatory Myriad
>   acknowledgment will appear in the dissertation and any resulting publication.
> - **Why it matters scientifically:** a frozen, pre-registered, seven-arm controlled study
>   (equivalence-testing design with a pre-registered seed ladder up to n = 568) of whether
>   LLM reward-designers can use distributional risk information — the confirmatory run is a
>   single-look design, so the compute must complete as one coherent campaign before the
>   write-up deadline.

## Supporting numbers (for questions)

| Quantity | Value | Source |
|---|---|---|
| Per-training wall (B\* = 200k steps) | 32.6 min = 0.543 GPU-h | measured, job 764154 (G1 anchor) |
| Stage-1 total to the 95% assurance target | ≈ 5,580 trainings ≈ 3,254 GPU-h (core ≈ 2,760) | E1 ladder arithmetic |
| Distinction floor (n = 30, complete study) | ≈ 1,104 trainings ≈ 644 GPU-h | grade-security tiering |
| Task footprint | 1 GPU + 1–2 cores + ≤ 8 GB RAM + tmpfs 15 GB | jobscript; rehearsal finding |
| Packing (if used) | 2–5 trainings/GPU, cgroup-isolated | G0 probe 762862; P1 ladder in flight |
| At 12 reserved V100s (packed ×2) | Stage-1 core completes in ≈ 2–3 days; full 95% target ≈ 5–7 days | arithmetic |

## Notes for Tamer (not for the committee)

- File through the ARR/CRAG channel rc-support advertises; CRAG meets the **second Tuesday**
  of the month — **Tue 14 July** is the window; the next is mid-August, which is too late to
  de-risk the calendar. Ask Dr Okhrati to co-sign (supervisor backing is the usual requirement).
- If the committee prefers a smaller grant: **any** dedicated number helps; 6 V100s × 14 days
  ≈ 2,016 GPU-h still covers the core + most of the sweep, and fair-share tops up the rest.
- If asked "why not fair-share alone": measured queue behaviour (11 July) — 369 pending
  GPU-requesting jobs against ~74 GPUs, ~2 free V100s at peak; placement latency for even a
  15-minute job exceeded an hour at fresh fair-share, and the campaign's single-look design
  cannot be split opportunistically across weeks without eating the writing calendar.
