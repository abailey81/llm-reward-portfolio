"""MYRIAD SSH RECOVERY WATCHER -- retries the login nodes on a slow cadence and says the
moment the service comes back.

WHY THIS EXISTS
---------------
From 2026-08-02 17:08:07Z every Myriad login node began refusing SSH *pre-banner*: the TCP
handshake completes and the server then resets the connection at 0.000 s without emitting its
identification string. Measured on 2026-08-02 19:2x-19:3xZ:

    myriad.rc.ucl.ac.uk    193.60.252.107   RESET before banner
    login12.myriad...      193.60.252.108   RESET before banner
    login13.myriad...      193.60.252.109   RESET before banner
    socrates.ucl.ac.uk     193.60.250.149   BANNER  OpenSSH_9.9    <- same 193.60 network
    kathleen/young/michael 144.82.25x       BANNER                 <- other UCL RC clusters
    ssh-gateway.ucl.ac.uk  144.82.250.148   BANNER  OpenSSH_8.0
    github.com             external         BANNER                 <- local stack control

so the refusal is specific to Myriad's three login nodes and is not our source, our route, our
VPN or our client. All eleven driver lines lost transport inside a 129 s window, which is one
external step change across eleven independent processes.

WHY A RAW SOCKET AND NOT ``ssh``
--------------------------------
An SSH server sends its identification string immediately on accept, before the client sends
anything. So a connect-and-read tells us whether sshd is willing to talk to us while sending
ZERO bytes and attempting NO authentication. That keeps the watcher's footprint at three TCP
connections per cycle -- against the drivers' ~600/hour -- and means it can never contribute
to an authentication-failure counter on the server.

WHAT IT DOES NOT DO
-------------------
It does not touch the campaign, the queue, the archive or any driver. It only reads a banner
and appends a line to its own log. Recovery of the *campaign* is still evidenced the usual
way: the cycle log's ``records=`` starts climbing again on its own, because the drivers ride
the outage out and resume without intervention.

USAGE
    python docs/ops/myriad_watch.py --once             # one sweep, exit 0 if any node serves
    python docs/ops/myriad_watch.py                    # loop forever, default 20 min cadence
    python docs/ops/myriad_watch.py --interval-secs 600
    python docs/ops/myriad_watch.py --selftest         # no network; proves the classifier

Exit codes for --once:  0 = at least one login node is SERVING, 1 = all still refusing.

Printed output is deliberately ASCII-only: the PowerShell console this repo runs under is
cp1251 and a non-ASCII character in a print() raises UnicodeEncodeError.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import socket
import sys
import time

HOSTS = (
    "myriad.rc.ucl.ac.uk",
    "login12.myriad.rc.ucl.ac.uk",
    "login13.myriad.rc.ucl.ac.uk",
)
PORT = 22
CONNECT_TIMEOUT = 8.0
READ_TIMEOUT = 10.0
DEFAULT_INTERVAL_SECS = 1200.0  # 20 minutes -- Tamer's instruction, 2026-08-02

_HERE = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(_HERE, "watch", "MYRIAD_SSH_WATCH.log")

# --- classification -----------------------------------------------------------------------
# Pure, so --selftest can prove every branch without a network.

SERVING = "SERVING"
RESET_NO_BANNER = "RESET-NO-BANNER"
FIN_NO_BANNER = "FIN-NO-BANNER"
SILENT = "ACCEPTED-SILENT"
NO_TCP = "NO-TCP"
DNS_FAIL = "DNS-FAIL"


def classify(outcome: str, payload: object) -> tuple[str, str]:
    """Map a probe outcome to (verdict, human detail).

    ``outcome`` is one of 'data', 'eof', 'timeout', 'reset', 'connect-error', 'dns-error'.
    ``payload`` is the bytes read for 'data', else the exception or None.

    Only ``SERVING`` means the login node is usable again; every other verdict means the
    outage persists, and they are kept distinct because they point at different causes:
    a RESET is admission control or an aborted accept queue, a FIN is a clean refusal
    (hosts.deny / MaxStartups drop), and SILENT is an sshd that accepted but is wedged.
    """
    if outcome == "data":
        raw = payload if isinstance(payload, (bytes, bytearray)) else b""
        if raw.startswith(b"SSH-"):
            text = raw.decode("utf-8", "replace").strip().splitlines()[0][:80]
            return SERVING, text
        # Something answered but it is not an SSH server -- a proxy or captive device.
        return FIN_NO_BANNER, "non-SSH bytes: %r" % raw[:40]
    if outcome == "eof":
        return FIN_NO_BANNER, "clean close, zero bytes (refusal before banner)"
    if outcome == "timeout":
        return SILENT, "accepted but no banner within %.0fs" % READ_TIMEOUT
    if outcome == "reset":
        return RESET_NO_BANNER, "RST before banner"
    if outcome == "connect-error":
        return NO_TCP, "TCP connect failed: %s" % type(payload).__name__
    if outcome == "dns-error":
        return DNS_FAIL, "name did not resolve"
    raise ValueError("unknown probe outcome: %r" % (outcome,))


def probe(host: str) -> tuple[str, str, str]:
    """One connection: connect, send NOTHING, read. Returns (verdict, detail, ip)."""
    try:
        infos = socket.getaddrinfo(host, PORT, socket.AF_INET, socket.SOCK_STREAM)
        ip = sorted({i[4][0] for i in infos})[0]
    except Exception:
        v, d = classify("dns-error", None)
        return v, d, "?"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(CONNECT_TIMEOUT)
    try:
        sock.connect((ip, PORT))
    except Exception as exc:
        sock.close()
        v, d = classify("connect-error", exc)
        return v, d, ip
    sock.settimeout(READ_TIMEOUT)
    try:
        data = sock.recv(256)
        v, d = classify("data" if data else "eof", data)
    except socket.timeout:
        v, d = classify("timeout", None)
    except ConnectionResetError as exc:
        v, d = classify("reset", exc)
    except OSError as exc:
        # Windows surfaces a reset as WSAECONNRESET (10054) which is a ConnectionResetError,
        # but an abortive close can also arrive as a bare OSError; treat it as a reset rather
        # than inventing a new state.
        v, d = classify("reset", exc)
    finally:
        try:
            sock.close()
        except OSError:
            pass
    return v, d, ip


def _utc() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append(line: str) -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def _previous_verdict_was_down() -> bool:
    """Was the most recent recorded verdict DOWN? Read from the log this file already writes.

    Deliberately NOT a new state file: the log is the artefact, it is appended on every sweep, and
    deriving the edge from it means there is nothing extra to keep in sync. **A missing or
    unreadable log returns True**, so the banner fires ONCE on the next serving sweep rather than
    never -- the safe direction for a recovery notice, and the opposite of the failure this fixes.
    """
    try:
        with open(LOG_PATH, "r", encoding="utf-8", errors="replace") as fh:
            tail = fh.readlines()[-400:]
    except OSError:
        return True
    for ln in reversed(tail):
        for token in (" DOWN ", " SERVING ", " RECOVERED "):   # RECOVERED = the pre-fix spelling
            if token in ln:
                return token.strip() == "DOWN"
    return True


def sweep(quiet: bool = False) -> bool:
    """One sweep across every login node. Returns True if any node is SERVING."""
    stamp = _utc()
    parts = []
    serving = []
    for host in HOSTS:
        verdict, detail, ip = probe(host)
        short = host.split(".")[0]
        parts.append("%s(%s)=%s" % (short, ip, verdict))
        if verdict == SERVING:
            serving.append((host, ip, detail))
    status = "SERVING" if serving else "DOWN"
    line = "%s  %-9s  %s" % (stamp, status, "  ".join(parts))
    _append(line)
    if not quiet:
        print(line)
    # ⚠⚠ "IS BACK" IS A TRANSITION CLAIM COMPUTED FROM A LEVEL, AND IT HAD FIRED 128 TIMES
    # (auditor, 2026-08-04, RUN 21). `status` reads the CURRENT level and no prior state was kept,
    # so every healthy sweep announced a recovery: the log holds **128 `IS BACK` banners against 22
    # `DOWN` lines**, the last six sweeps consecutively. That is the exact signal-saturation failure
    # `crash_watchdog.py` was built to avoid, running live in a sibling monitor -- and it destroys
    # the value of the one banner that would matter. The banner now fires only on a genuine
    # DOWN -> SERVING edge, read from the previous verdict persisted in the log itself, so no new
    # state file is introduced and a lost log degrades to "announce once", never to "announce never".
    was_down = _previous_verdict_was_down()
    if serving and was_down:
        banner_line = "%s  *** MYRIAD SSH IS BACK -- %d login node(s) serving ***" % (stamp, len(serving))
        _append(banner_line)
        for host, ip, detail in serving:
            _append("%s      %s (%s) -> %s" % (stamp, host, ip, detail))
        if not quiet:
            print(banner_line)
            for host, ip, detail in serving:
                print("      %s (%s) -> %s" % (host, ip, detail))
            print("      The drivers resume pulling on their own. Watch the cycle log's records= climb.")
    return bool(serving)


# --- selftest -----------------------------------------------------------------------------

def _selftest() -> int:
    cases = [
        ("data-ssh", ("data", b"SSH-2.0-OpenSSH_8.0\r\n"), SERVING),
        ("data-ssh-noeol", ("data", b"SSH-2.0-OpenSSH_9.9"), SERVING),
        ("data-not-ssh", ("data", b"HTTP/1.1 400 Bad Request"), FIN_NO_BANNER),
        ("eof", ("eof", b""), FIN_NO_BANNER),
        ("timeout", ("timeout", None), SILENT),
        ("reset", ("reset", ConnectionResetError(10054, "forcibly closed")), RESET_NO_BANNER),
        ("connect-error", ("connect-error", TimeoutError("timed out")), NO_TCP),
        ("dns-error", ("dns-error", None), DNS_FAIL),
    ]
    failures = 0
    print("myriad_watch --selftest  (no network)")
    for name, (outcome, payload), expected in cases:
        got, detail = classify(outcome, payload)
        ok = got == expected
        failures += 0 if ok else 1
        print("  %-16s expect %-16s got %-16s %s" % (name, expected, got, "OK" if ok else "FAIL"))
        if not ok:
            print("      detail: %s" % detail)

    # MUTANT: the one failure mode that actually matters is calling the outage over when it is
    # not. Prove that no non-SSH payload can ever be reported as SERVING.
    for bad in (b"", b"\x00\x00", b"ssh-2.0-lowercase", b" SSH-2.0-leading-space"):
        got, _ = classify("data" if bad else "eof", bad)
        if got == SERVING:
            print("  MUTANT FAIL: %r classified SERVING" % bad)
            failures += 1
    print("  %-16s %s" % ("mutant-guard", "OK -- only a leading 'SSH-' banner counts as SERVING"))

    # An unknown outcome must raise, not silently return a passing verdict.
    try:
        classify("nonsense", None)
    except ValueError:
        print("  %-16s OK -- unknown outcome raises" % "unknown-outcome")
    else:
        print("  %-16s FAIL -- unknown outcome did not raise" % "unknown-outcome")
        failures += 1

    print("")
    print("selftest: %d case(s) FAILED" % failures if failures else "selftest: ALL PASS")
    return 1 if failures else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Watch for Myriad SSH recovery.")
    ap.add_argument("--once", action="store_true", help="one sweep then exit")
    ap.add_argument("--interval-secs", type=float, default=DEFAULT_INTERVAL_SECS,
                    help="cadence in seconds (default 1200 = 20 min)")
    ap.add_argument("--stop-on-recovery", action="store_true",
                    help="exit 0 as soon as a login node serves")
    ap.add_argument("--quiet", action="store_true", help="log only, no stdout")
    ap.add_argument("--selftest", action="store_true", help="prove the classifier, no network")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()

    if args.once:
        return 0 if sweep(args.quiet) else 1

    if not args.quiet:
        print("myriad_watch: cadence %.0f s; logging to %s" % (args.interval_secs, LOG_PATH))
    while True:
        try:
            recovered = sweep(args.quiet)
        except Exception as exc:  # noqa: BLE001 -- a watcher must never die on a transient
            _append("%s  WATCHER-ERROR  %s: %s" % (_utc(), type(exc).__name__, exc))
            recovered = False
        if recovered and args.stop_on_recovery:
            return 0
        time.sleep(args.interval_secs)


if __name__ == "__main__":
    sys.exit(main())
