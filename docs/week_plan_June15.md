# Week plan — w/c Monday 15 June 2026  (written Fri 12 Jun, plan block F6)
# STATUS UPDATE 2026-06-10 (see CHANGELOG + reports/session_report_2026-06-10.md): the code items
# below were completed EARLY in the 10 Jun session; the week now centres on GPU/training + governance.
Mon: env feature step (vol20, vol20/vol60, VIX into cash row) with leakage tests ✅ DONE 10 Jun (ADR-007);
     λ calibration MACHINERY done (ADR-010) — the calibration RUN still waits on first training runs.
Tue: sandbox hardening + denial corpus + candidate archiver ✅ DONE 10 Jun (ADR-008).
Wed: rewards_baselines completion + tests ✅ DONE 10 Jun (ADR-009);
     first full TRAINING RUN: SAC + differential-Sharpe on dev split, 3 seeds — ⏳ NEEDS THE 4090
     (make setup/test/smoke + make lock there first; ADR-014).
Thu: group meeting prep + attend; IQN-SAC training parity check vs SAC; calibration figure v0
     (IQN quantiles vs empirical returns) — ⏳ 4090.
Fri: TrialLedger dry-run ✅ DONE 10 Jun (DSR 0.577/PBO 0.094 on labelled throwaway candidates);
     PREREGISTRATION FREEZE (T4) — author action, with ADR-010's §3/§4a recommendations;
     week retro + ADRs; ICAIF decision recorded (needed ~19 Jun).
Standing: respect tier system; anything slipping rolls to weekend Tier-3 only.
NEW (unblocked by entitlements, any day): Workspace login + desktop app key → re-run `make data-probe`;
send the Datastream/WRDS escalation email (rendered in docs/evidence/entitlement_report.md).
