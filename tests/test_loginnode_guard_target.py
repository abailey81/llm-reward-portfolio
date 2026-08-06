"""The login-node guard must watch the node the CAMPAIGN is actually loading.

WHY THIS TEST EXISTS -- a measured, live failure, 2026-08-06 (RUN 28).

At 16:27:55Z RUN 27 fixed a campaign outage by moving `Host myriad` in `~/.ssh/config` from
login13 to login12. Every driver followed, because `src/cluster/{campaign,driver,poll,submit,
telemetry}.py` all pass the literal alias ``"myriad"``.

`docs/ops/loginnode_guard.py` did NOT follow, because it hardcoded a DIFFERENT alias
(``"myriad13"``) for a good reason -- `Host myriad` carries a `ProxyCommand` through the ssh
admission gate, and probing through it would put the observer inside the mechanism it observes.

The result: the guard's last real reading was ``2026-08-06T16:25:04Z OK node=login13...`` and it
then logged **133 consecutive `PROBE-UNPARSED`** over 3 h 40 m, because login13 was down. It was
measuring a dead node while twelve driver lines loaded login12 -- the exact node that earned UCL's
`penalty1` on 2026-08-03, and the only instrument `docs/ops/MAINTENANCE_2026-08-12.md` §5 says to
check on an at-risk day.

Two invariants, and the first is the one that failed:

  1. the guard's probe target is the SAME ssh alias the drivers use, so it can never again watch a
     node the campaign has left;
  2. the probe is nonetheless UNGATED (``ProxyCommand=none`` on the command line, which overrides
     the config), so the observer stays outside the admission gate and does not consume one of its
     four slots.

Both are statically checkable, which is the point: they hold without a live cluster.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
#: Overridable ONLY so these assertions can be mutation-tested against a COPY. A 2-minute loop
#: reads the real file, so mutating it in place to prove the tests can fail is not acceptable.
GUARD = Path(os.environ.get("LNG_GUARD_PATH") or (REPO / "docs" / "ops" / "loginnode_guard.py"))
#: every module that opens an ssh session to run the campaign
DRIVER_SOURCES = [
    REPO / "src" / "cluster" / "campaign.py",
    REPO / "src" / "cluster" / "driver.py",
    REPO / "src" / "cluster" / "poll.py",
    REPO / "src" / "cluster" / "submit.py",
    REPO / "src" / "cluster" / "telemetry.py",
]

#: an ssh alias literal, e.g. "myriad" / "myriad13" / "myriadjump"
_ALIAS = re.compile(r'"(myriad[a-z0-9]*)"')


def _driver_alias() -> str:
    """The single ssh alias the drivers use. Fails loudly if they ever disagree."""
    found: set[str] = set()
    for src in DRIVER_SOURCES:
        if not src.exists():                     # a rename must fail the test, not skip it
            pytest.fail("driver source missing: %s" % src)
        found |= set(_ALIAS.findall(src.read_text(encoding="utf-8", errors="replace")))
    assert found, "no ssh alias literal found in the driver sources -- the regex has gone stale"
    assert len(found) == 1, (
        "the drivers disagree about which ssh alias to use: %s. The guard cannot follow two "
        "targets, so this must be resolved in src/cluster/ first." % sorted(found)
    )
    return found.pop()


def _guard_host() -> str:
    m = re.search(r'^HOST\s*=\s*"([^"]+)"', GUARD.read_text(encoding="utf-8"), re.M)
    assert m, "loginnode_guard.py no longer defines HOST = \"...\" at module level"
    return m.group(1)


def test_guard_probes_the_same_node_the_drivers_load() -> None:
    """INVARIANT 1. A guard pointed at a node the campaign left is worse than no guard: it reports
    a healthy stranger while the loaded node approaches the penalty ceiling."""
    assert _guard_host() == _driver_alias(), (
        "loginnode_guard.py probes %r but the drivers load %r. This exact divergence left the "
        "campaign with no penalty guard for 3 h 40 m on 2026-08-06." % (_guard_host(), _driver_alias())
    )


def _captured_ssh_argv(monkeypatch) -> list[str]:
    """Run sample() with the network stubbed and return the argv it ACTUALLY built.

    Asserting on source text would pass for a `ProxyCommand=none` sitting in a comment and fail for
    a correct one built from a named constant. Only the argv is the behaviour.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("_lng", GUARD)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    seen: list[list[str]] = []

    class _Res:
        stdout = ""                       # forces the PROBE-UNPARSED branch; we only want the argv

    def _fake_run(argv, **kw):
        seen.append(list(argv))
        return _Res()

    monkeypatch.setattr(mod.subprocess, "run", _fake_run)
    monkeypatch.setattr(mod, "_append", lambda line: None)     # do not write the real log
    mod.sample(quiet=True)
    assert seen, "sample() never invoked subprocess.run"
    return seen[0]


def test_guard_probe_is_ungated(monkeypatch, capsys) -> None:
    """INVARIANT 2. `Host myriad` carries a ProxyCommand through docs/ops/ssh_gate.py (cap 4). The
    guard must override it, or the observer sits inside the mechanism it observes AND steals a slot
    the drivers need."""
    argv = _captured_ssh_argv(monkeypatch)
    capsys.readouterr()
    joined = " ".join(argv)
    assert "ProxyCommand=none" in joined, (
        "the guard's ssh argv is %r -- it reaches its target THROUGH the ssh admission gate. It "
        "must pass -o ProxyCommand=none so the probe stays outside the gate." % (argv,)
    )
    assert argv[-2] == _driver_alias(), (
        "the guard's ssh argv targets %r, not the drivers' alias %r" % (argv[-2], _driver_alias())
    )


def test_guard_probe_argv_is_ascii(monkeypatch, capsys) -> None:
    """The repo's PowerShell console is cp1251, so a non-ASCII glyph anywhere in printed output
    raises UnicodeEncodeError. RUN 27 shipped one into a published string and caught it only by
    walking the bytes -- so walk the bytes of what this tool actually emits."""
    _captured_ssh_argv(monkeypatch)
    printed = capsys.readouterr().out
    bad = [(i, ch) for i, ch in enumerate(printed) if ord(ch) > 127]
    assert not bad, "non-ASCII in printed guard output at %r" % (bad[:5],)


def test_failure_message_names_the_probe_target() -> None:
    """A probe that fails must say WHAT it was probing. The 2026-08-06 message listed three generic
    causes and never named the host, which is why the real cause took 40 minutes to find."""
    text = GUARD.read_text(encoding="utf-8")
    m = re.search(r"def _unknown\(.*?\n(?=\n\ndef |\n\nclass )", text, re.S)
    assert m, "could not isolate _unknown() in loginnode_guard.py"
    body = m.group(0)
    assert "HOST" in body, (
        "_unknown() does not name the probe target. A failure report that omits which host was "
        "probed cannot distinguish 'the node is down' from 'we are watching the wrong node'."
    )
