"""Per-stage ETAs for RUN 4, from the REGISTERED makespan model (src/cluster/lanes.py).

Tamer asked for each stage's current ETA in every update. This computes them from the repo's own
model rather than from arithmetic invented at report time, so the numbers are auditable and move
only when the model's inputs move.

Two core figures are shown side by side ON PURPOSE:
  * MEASURED  - the cores we actually hold right now. Early in a run this is small and the ETA it
                implies is pessimistic, because ~8 h tasks ACCUMULATE (concurrency = dispatch rate
                x duration) rather than appearing at once.
  * MODELLED  - the capacity the plan assumes once accumulation settles.
The gap between them IS the open operational question (record s.21.5 item 3): whether this account
actually saturates. Reporting only one of the two would be picking the answer in advance.

Usage: python stage_eta.py <measured_cores> [modelled_cores]
"""
from __future__ import annotations

import datetime as dt
import sys

sys.path.insert(0, "/c/Users/User/Desktop/dissertation_papers/llm-reward-portfolio")

from src.cluster.lanes import plan_lanes  # noqa: E402

LAUNCH = dt.datetime(2026, 7, 28, 21, 8, 58)   # supervisors up, UTC
STOP = dt.datetime(2026, 8, 27)                # R109 exogenous stop
RUNGS = [30, 100, 189, 279, 340, 403, 568]     # the registered assurance ladder
CHAIN_THREADS = 8                              # --search-threads 8 (R107)

measured = int(sys.argv[1]) if len(sys.argv) > 1 else 20
modelled = int(sys.argv[2]) if len(sys.argv) > 2 else 830   # RUN 3 held 827 slots

now = dt.datetime.utcnow()
elapsed_d = (now - LAUNCH).total_seconds() / 86400.0
days_left = (STOP - now).total_seconds() / 86400.0

print(f"stage ETAs from the registered model  (chain_threads={CHAIN_THREADS}, "
      f"elapsed {elapsed_d:.2f} d, {days_left:.1f} d to the Aug-27 stop)")
print()
print(f"{'rung':>5}  {'@%d cores' % measured:>22}  {'@%d cores' % modelled:>22}   binding")
print(f"{'':>5}  {'makespan / ETA':>22}  {'makespan / ETA':>22}")

for rung in RUNGS:
    row = []
    binding = ""
    for cores in (measured, modelled):
        p = plan_lanes(rung=rung, cpu_cores=cores, chain_threads=CHAIN_THREADS)
        eta = LAUNCH + dt.timedelta(days=p.makespan_days)
        fits = "" if eta <= STOP else "  X"
        row.append(f"{p.makespan_days:6.1f} d  {eta:%m-%d}{fits}")
        binding = p.binding
    print(f"{rung:>5}  {row[0]:>22}  {row[1]:>22}   {binding}")

p = plan_lanes(rung=568, cpu_cores=modelled, chain_threads=CHAIN_THREADS)
print()
print(f"saturation: more than ~{p.saturation_cores:.0f} cores buy NOTHING at rung 568")
print(f"critical chain floor: {p.critical_chain_days:.2f} d  (serial, immune to more cores)")
for n in p.notes:
    print(f"  * {n}")
