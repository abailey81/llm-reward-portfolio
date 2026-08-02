#!/bin/bash
# SSH LAYER STRESS BASELINE -- run LOCALLY (it is the driver host's ssh that matters).
#
# WHY (RUN 13, 2026-08-02). Across the 12 driver logs: 1,385 `pull failed` + 666 `queue op failed`,
# every one of them `ssh ... returned non-zero exit status 255`, i.e. the CONNECTION failed, not the
# remote command. They arrive in BURSTS (132 in one hour, then hours of nothing), and 76 of them
# escalated into `drain with NO qacct trace` -- where the driver concludes the array "was purged
# before dispatch" and RESUBMITS. On the core line's SEQUENTIAL `cma_es` chain that cost 24 h on one
# candidate and 4.5 h on another; healthy candidates show 0.1 h of overhead, so essentially ALL of
# the measured 4.5 h/candidate overhead is ssh-outage damage, and it sits directly on the campaign's
# critical path.
#
# The two candidate mechanisms need different fixes, so measure before changing anything:
#   (i)  HANDSHAKE STORMS -- 12 drivers each opening fresh TCP+auth every poll can trip sshd's
#        MaxStartups (default 10:30:100 => 30% of connections dropped at random beyond 10 in flight).
#        Fix: ControlMaster multiplexing + ConnectionAttempts. Client-side, no repo change.
#   (ii) LINK OUTAGES -- the VPN or the login node drops entirely. Multiplexing does not help;
#        ConnectionAttempts still converts a brief drop into a retry.
# The discriminator is whether CONCURRENCY alone produces failures on a healthy link.
set -u
N=${1:-14}
echo "== serial latency (3 samples) =="
for i in 1 2 3; do
  S=$(date +%s%N)
  ssh -o BatchMode=yes myriad true 2>/dev/null
  RC=$?
  E=$(date +%s%N)
  echo "  attempt $i rc=$RC  $(( (E-S)/1000000 )) ms"
done

echo "== $N CONCURRENT connections (the MaxStartups probe) =="
T0=$(date +%s%N)
rm -f /tmp/ssh_stress_rc.*
for i in $(seq 1 "$N"); do
  ( ssh -o BatchMode=yes myriad true 2>/dev/null; echo $? > "/tmp/ssh_stress_rc.$i" ) &
done
wait
T1=$(date +%s%N)
OK=0; BAD=0
for i in $(seq 1 "$N"); do
  R=$(cat "/tmp/ssh_stress_rc.$i" 2>/dev/null || echo 99)
  if [ "$R" = "0" ]; then OK=$((OK+1)); else BAD=$((BAD+1)); echo "  FAILURE rc=$R"; fi
done
echo "  ok=$OK  failed=$BAD  wall=$(( (T1-T0)/1000000 )) ms"
echo
echo "READ IT: any failure here on a healthy link implicates mechanism (i) and makes ControlMaster"
echo "the correct fix. Zero failures means the bursts are mechanism (ii) and only ConnectionAttempts"
echo "(plus a persistent master, which survives handshake-level flakiness) can help."
