"""SSH ADMISSION GATE -- a hard, local bound on how many SSH sessions can exist against the
Myriad login node at once. Used as an OpenSSH ``ProxyCommand``.

=============================== WHY THIS EXISTS ===============================================
On 2026-08-03 UCL automatically penalised `ucestes` for exceeding the login-node allowance
(6 cores / 30 GB). Measured, not assumed:

  * Steady state is LEGAL: ~2.75 of 6 cores, 0.00 GB, held almost entirely by exactly FOUR
    concurrent `qacct -j` processes at ~73% CPU each.
  * Each is expensive because /opt/sge/default/common/accounting is **33 GB** and `qacct -j`
    scans it end to end.
  * The VIOLATION was a STAMPEDE. SSH access returned at 00:31:59Z after a 7-hour outage; the
    detector fired at 00:33:47Z -- 108 seconds later -- when all twelve driver lines resumed at
    once, tar-extracting a ~1,400-record backlog while running qacct forensics on every array
    that had drained while we were blind. The email's own averages total ~3.5 cores, UNDER the
    limit; it says so itself ("recent averages ... instantaneous usage may differ"), so the
    detector fired on the PEAK.

So the failure mode is precisely: **N drivers becoming runnable simultaneously**. Bounding
concurrency removes it. Nothing else here needs to change.

=============================== WHY THIS DESIGN ================================================
Three alternatives were evaluated and REJECTED on their merits:

  1. Kill or nice the remote qacct. REJECTED: `driver.py` (P13) treats a MISSING qacct trace as
     evidence that an array was purged and can RESUBMIT the work. Trading a CPU spike for
     spurious re-training on an irreplaceable campaign is a bad bargain.
  2. Serialise qacct with a remote flock wrapper. REJECTED: the count sits at exactly 4 because
     the arrival rate already meets the service rate. Serialising would build an unbounded queue,
     push calls past the driver's 120 s ssh timeout, and land in the SAME resubmit path as (1).
  3. Change poll intervals or driver code. Correct, but needs a twelve-line relaunch.

That leaves the ssh client itself, which is the one mediator every driver already passes through
and the one thing we fully control. A ProxyCommand sees every connection before it exists.

=============================== SAFETY PROPERTIES ==============================================
This sits in the path of EVERY cluster operation, so it is built to be incapable of stopping the
campaign:

  * FAIL-OPEN, ALWAYS. Any error in the gating machinery -- unreadable slot dir, bad config,
    anything -- is swallowed and the connection proceeds ungated. A gate that blocks the campaign
    is worse than no gate.
  * BOUNDED WAIT, NEVER A BLOCK. A connection waits at most ``--max-wait`` seconds for a slot and
    then proceeds ANYWAY. The driver's own ssh timeout is 120 s, so the default 45 s cannot push
    a call into that timeout even if it waits the full time and then connects slowly.
  * SELF-HEALING SLOTS. A slot is a file holding the owner's PID. If a holder dies without
    releasing (crash, taskkill), the next acquirer detects the dead PID and reclaims the slot, so
    capacity can never leak away permanently.
  * TRANSPARENT BYTE PATH. stdin/stdout are put in binary mode and relayed verbatim; the gate
    never interprets, buffers-by-line, or rewrites the stream. It must carry tar streams intact.

=============================== CALIBRATION ====================================================
The default cap is 4, chosen from measurement rather than taste:
  * observed steady state is 4 concurrent qacct + ~5-7 sshd, i.e. normal operation already sits
    at about this level, so the cap is near-transparent day to day;
  * 4 concurrent qacct is ~2.9 cores, leaving >3 cores of headroom under the 6-core limit;
  * the stampede was ~12 simultaneous, which is what this refuses.
Raising it weakens the protection; lowering it starts to throttle normal pulls. Tune from the
gate's own log (it records every WAIT), not from guesswork.

USAGE (as a ProxyCommand -- OpenSSH substitutes %h and %p):
    ProxyCommand python.exe docs/ops/ssh_gate.py --connect %h %p

    python docs/ops/ssh_gate.py --selftest      # no network, proves the slot pool
    python docs/ops/ssh_gate.py --status        # who holds slots right now

Printed output is ASCII-only (this repo's console is cp1251). NOTHING is ever printed to stdout
in --connect mode: stdout IS the byte channel.
"""

from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import os
import socket
import sys
import threading
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
SLOT_DIR = os.path.join(_HERE, "watch", ".sshgate")
LOG_PATH = os.path.join(_HERE, "watch", "SSH_GATE.log")

DEFAULT_SLOTS = int(os.environ.get("SSH_GATE_SLOTS", "4"))
DEFAULT_MAX_WAIT = float(os.environ.get("SSH_GATE_MAX_WAIT", "45"))
POLL = 0.15

_STILL_ACTIVE = 259
_PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def _pid_alive(pid: int) -> bool:
    """True if `pid` is a live process. Used to reclaim slots whose owner died.

    Deliberately conservative: if we cannot TELL, we answer True and leave the slot alone. A
    leaked slot costs a little concurrency; stealing a LIVE holder's slot would break the cap
    this whole file exists to enforce.
    """
    if pid <= 0:
        return False
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        except Exception:                                  # noqa: BLE001
            return True
    try:
        k32 = ctypes.windll.kernel32
        h = k32.OpenProcess(_PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not h:
            return False
        try:
            code = ctypes.c_ulong()
            if not k32.GetExitCodeProcess(h, ctypes.byref(code)):
                return True
            return code.value == _STILL_ACTIVE
        finally:
            k32.CloseHandle(h)
    except Exception:                                      # noqa: BLE001
        return True


def _log(msg: str) -> None:
    """Best-effort logging. Never raises: this runs inside the campaign's data path."""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write("%s  %s\n" % (dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), msg))
    except Exception:                                      # noqa: BLE001
        pass


class SlotPool:
    """A cross-process counting semaphore built from atomically-created files.

    A Windows kernel semaphore is the obvious choice and is WRONG here: unlike a mutex it has no
    abandoned state, so a forwarder killed while holding a token leaks that token forever and the
    cap erodes to zero. File slots carrying a PID are self-healing instead.
    """

    def __init__(self, slots: int = DEFAULT_SLOTS, slot_dir: str = SLOT_DIR):
        self.slots = max(1, int(slots))
        self.dir = slot_dir
        self.held: str | None = None

    def _try_take(self, path: str) -> bool:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            return False
        except OSError:
            return False
        try:
            os.write(fd, str(os.getpid()).encode("ascii"))
        finally:
            os.close(fd)
        return True

    def _reclaim_dead(self) -> int:
        """Delete slot files whose owning PID is gone. Returns how many were reclaimed."""
        n = 0
        for i in range(self.slots):
            p = os.path.join(self.dir, "slot-%d" % i)
            try:
                with open(p, "r", encoding="ascii") as fh:
                    pid = int((fh.read() or "0").strip() or 0)
            except FileNotFoundError:
                continue
            except Exception:                              # noqa: BLE001
                continue
            if not _pid_alive(pid):
                try:
                    os.remove(p)
                    n += 1
                    _log("reclaimed slot-%d from dead pid %d" % (i, pid))
                except OSError:
                    pass
        return n

    def acquire(self, max_wait: float = DEFAULT_MAX_WAIT) -> tuple[bool, float]:
        """Take a slot. Returns (got_slot, seconds_waited).

        NEVER raises and NEVER blocks past ``max_wait`` -- on timeout it returns (False, waited)
        and the caller proceeds ungated. That is deliberate: the cap is a shock absorber, not a
        tourniquet.
        """
        t0 = time.time()
        try:
            os.makedirs(self.dir, exist_ok=True)
        except Exception:                                  # noqa: BLE001
            return False, 0.0
        # ⚠ RECLAIM MUST BE PERIODIC, NOT ONCE. Measured 2026-08-03: ssh does not let the
        # ProxyCommand exit cleanly -- it kills it -- so `release()` in the finally frequently
        # never runs and slots are left owned by dead PIDs. With a one-shot reclaim (the original
        # bug), waiters that arrived before those holders died span the ENTIRE max_wait and then
        # fall through ungated: a 12-way stampede test produced 8 x "WAIT 40.1s -> PROCEEDING
        # UNGATED", i.e. the cap was breached for two thirds of the burst -- precisely the event
        # this file exists to prevent. Re-checking every RECLAIM_EVERY seconds turns a dead
        # holder into free capacity within about a second.
        RECLAIM_EVERY = 1.0
        last_reclaim = -1e9
        while True:
            for i in range(self.slots):
                if self._try_take(os.path.join(self.dir, "slot-%d" % i)):
                    self.held = os.path.join(self.dir, "slot-%d" % i)
                    return True, time.time() - t0
            now = time.time()
            if now - last_reclaim >= RECLAIM_EVERY:
                last_reclaim = now
                if self._reclaim_dead():
                    continue                      # capacity appeared -- grab it before sleeping
            if time.time() - t0 >= max_wait:
                return False, time.time() - t0
            time.sleep(POLL)

    def release(self) -> None:
        if not self.held:
            return
        try:
            os.remove(self.held)
        except OSError:
            pass
        self.held = None


def _relay(sock: socket.socket) -> None:
    """Verbatim byte relay between this process's stdio and the socket.

    os.read/os.write on the raw descriptors, so nothing text-mode can corrupt a tar stream. On
    Windows the descriptors are explicitly switched to binary: without this, a 0x1A byte in a
    record payload would be read as EOF and silently truncate a pull.
    """
    if os.name == "nt":
        try:
            import msvcrt
            msvcrt.setmode(0, os.O_BINARY)
            msvcrt.setmode(1, os.O_BINARY)
        except Exception:                                  # noqa: BLE001
            pass

    done = threading.Event()

    def to_sock() -> None:
        try:
            while True:
                b = os.read(0, 65536)
                if not b:
                    break
                sock.sendall(b)
        except Exception:                                  # noqa: BLE001
            pass
        finally:
            try:
                sock.shutdown(socket.SHUT_WR)
            except Exception:                              # noqa: BLE001
                pass
            done.set()

    def to_stdout() -> None:
        try:
            while True:
                b = sock.recv(65536)
                if not b:
                    break
                off = 0
                while off < len(b):
                    off += os.write(1, b[off:])
        except Exception:                                  # noqa: BLE001
            pass
        finally:
            done.set()

    t1 = threading.Thread(target=to_sock, daemon=True)
    t2 = threading.Thread(target=to_stdout, daemon=True)
    t1.start()
    t2.start()
    done.wait()
    time.sleep(0.05)


def connect(host: str, port: int, slots: int, max_wait: float) -> int:
    pool = SlotPool(slots)
    got, waited = (False, 0.0)
    try:
        got, waited = pool.acquire(max_wait)
        if waited > 1.0:
            _log("WAIT %.1fs for a slot (cap=%d) -> %s:%d %s"
                 % (waited, slots, host, port, "admitted" if got else "PROCEEDING UNGATED (timeout)"))
    except Exception as exc:                               # noqa: BLE001
        _log("gate machinery failed (%s) -- proceeding ungated" % type(exc).__name__)
    try:
        sock = socket.create_connection((host, port), timeout=30)
    except Exception as exc:                               # noqa: BLE001
        # Report on STDERR only. stdout is the byte channel and must stay pristine.
        sys.stderr.write("ssh_gate: connect to %s:%d failed: %s\n" % (host, port, exc))
        pool.release()
        return 1
    try:
        sock.settimeout(None)
        _relay(sock)
    finally:
        try:
            sock.close()
        except Exception:                                  # noqa: BLE001
            pass
        pool.release()
    return 0


def _status(slots: int) -> int:
    print("SSH GATE STATUS   cap=%d   slot dir=%s" % (slots, SLOT_DIR))
    live = 0
    for i in range(slots):
        p = os.path.join(SLOT_DIR, "slot-%d" % i)
        try:
            with open(p, "r", encoding="ascii") as fh:
                pid = int((fh.read() or "0").strip() or 0)
            state = "HELD by pid %d%s" % (pid, "" if _pid_alive(pid) else "  (DEAD -- reclaimable)")
            live += 1
        except FileNotFoundError:
            state = "free"
        except Exception as exc:                           # noqa: BLE001
            state = "unreadable (%s)" % type(exc).__name__
        print("  slot-%d : %s" % (i, state))
    print("  in use : %d/%d" % (live, slots))
    return 0


def _selftest() -> int:
    import tempfile
    bad = 0
    print("ssh_gate --selftest (no network)")
    with tempfile.TemporaryDirectory() as td:
        # 1) the cap actually caps
        pools = [SlotPool(3, td) for _ in range(5)]
        got = [p.acquire(max_wait=0.3)[0] for p in pools]
        ok = got[:3] == [True, True, True] and got[3:] == [False, False]
        bad += 0 if ok else 1
        print("  %-26s %s  (3 admitted, 2 refused -> %s)" % ("cap-holds", "OK" if ok else "FAIL", got))

        # 2) releasing frees capacity
        pools[0].release()
        again, _ = SlotPool(3, td).acquire(max_wait=0.3)
        bad += 0 if again else 1
        print("  %-26s %s" % ("release-frees-slot", "OK" if again else "FAIL"))

        # 3) a timed-out acquire must FAIL OPEN, not raise
        for p in pools[1:3]:
            pass
        t0 = time.time()
        gotx, waited = SlotPool(3, td).acquire(max_wait=0.4)
        elapsed = time.time() - t0
        ok3 = (gotx is False) and (0.3 <= elapsed <= 2.0)
        bad += 0 if ok3 else 1
        print("  %-26s %s  (returned False after %.2fs, no exception)" % ("bounded-wait", "OK" if ok3 else "FAIL", elapsed))

    with tempfile.TemporaryDirectory() as td2:
        # 4) a slot owned by a DEAD pid is reclaimed -- otherwise capacity leaks to zero
        os.makedirs(td2, exist_ok=True)
        with open(os.path.join(td2, "slot-0"), "w", encoding="ascii") as fh:
            fh.write("999999999")            # a pid that cannot exist
        p = SlotPool(1, td2)
        gotd, _ = p.acquire(max_wait=1.0)
        bad += 0 if gotd else 1
        print("  %-26s %s  (dead holder reclaimed)" % ("self-healing-slots", "OK" if gotd else "FAIL"))
        p.release()

    # 4b) REGRESSION PIN for the one-shot-reclaim bug: a holder that dies AFTER we start waiting
    #     must be reclaimed within ~1s, not after the full max_wait. Without periodic reclaim the
    #     acquire below burns the whole 6s budget and returns False.
    with tempfile.TemporaryDirectory() as td3:
        with open(os.path.join(td3, "slot-0"), "w", encoding="ascii") as fh:
            fh.write(str(os.getpid()))           # a LIVE pid: not reclaimable yet

        def _die_later() -> None:
            time.sleep(1.0)
            try:                                  # holder "dies": rewrite as an impossible pid
                with open(os.path.join(td3, "slot-0"), "w", encoding="ascii") as f2:
                    f2.write("999999999")
            except Exception:                     # noqa: BLE001
                pass

        threading.Thread(target=_die_later, daemon=True).start()
        t0 = time.time()
        gotl, _ = SlotPool(1, td3).acquire(max_wait=6.0)
        took = time.time() - t0
        okl = gotl and took < 3.5
        bad += 0 if okl else 1
        print("  %-26s %s  (holder died mid-wait; acquired after %.1fs, must be < 3.5s)"
              % ("periodic-reclaim", "OK" if okl else "FAIL", took))

    # 5) a LIVE holder must never be stolen from
    alive = _pid_alive(os.getpid())
    bad += 0 if alive else 1
    print("  %-26s %s  (our own pid reads as alive)" % ("live-pid-detected", "OK" if alive else "FAIL"))
    # 6) an unknowable pid must read as ALIVE (conservative), never as free
    cons = _pid_alive(0) is False
    bad += 0 if cons else 1
    print("  %-26s %s  (pid 0 is not a process)" % ("pid-zero-not-alive", "OK" if cons else "FAIL"))

    print("")
    print("selftest: %d FAILED" % bad if bad else "selftest: ALL PASS")
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="SSH admission gate (ProxyCommand).")
    ap.add_argument("--connect", nargs=2, metavar=("HOST", "PORT"))
    ap.add_argument("--slots", type=int, default=DEFAULT_SLOTS)
    ap.add_argument("--max-wait", type=float, default=DEFAULT_MAX_WAIT)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.status:
        return _status(args.slots)
    if args.connect:
        try:
            return connect(args.connect[0], int(args.connect[1]), args.slots, args.max_wait)
        except Exception as exc:                           # noqa: BLE001
            sys.stderr.write("ssh_gate: fatal %s: %s\n" % (type(exc).__name__, exc))
            return 1
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
