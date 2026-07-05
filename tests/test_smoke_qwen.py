"""Tests for scripts/smoke_qwen.py — the R71 secondary-designer (Qwen3-Coder via OpenRouter) smoke.

All offline: ``load_env`` is stubbed so a real gitignored ``.env`` (once the user adds
OPENROUTER_API_KEY) cannot leak into the key-missing test, and the transport factory is faked so the
key-present path exercises the script's real flow (config pin -> build_transport -> one call -> report)
with no network. Covered:

  - key MISSING -> exit code 2 with an actionable "add OPENROUTER_API_KEY=... to .env" message
    (NOT an exception), and the message names the pinned model + provider;
  - key PRESENT -> exit code 0, routes the PINNED config (qwen/qwen3-coder via openrouter,
    OPENROUTER_API_KEY) through ``build_transport``, prints the served-model reproducibility anchor
    + response text + usage, and NEVER prints the key.
"""
from __future__ import annotations

from typing import Any

from scripts import smoke_qwen


def _stub_load_env(monkeypatch) -> None:
    """Keep the real gitignored .env out of the test (the script calls src.utils.env.load_env)."""
    import src.utils.env as env_mod

    monkeypatch.setattr(env_mod, "load_env", lambda: None)


def test_missing_key_exits_2_with_actionable_message(monkeypatch, capsys) -> None:
    _stub_load_env(monkeypatch)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    rc = smoke_qwen.main()
    out = capsys.readouterr().out
    assert rc == 2
    assert "OPENROUTER_API_KEY" in out and ".env" in out  # actionable: what to set, where
    assert "qwen/qwen3-coder" in out  # names the pinned model so the operator knows what will run


def test_key_present_makes_one_call_and_reports_anchor(monkeypatch, capsys) -> None:
    _stub_load_env(monkeypatch)
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-SECRET-not-to-print")

    calls: list[tuple[str, str]] = []
    built: dict[str, Any] = {}

    class _FakeTransport:
        last_served_model = "qwen/qwen3-coder-served-snapshot"
        last_usage = {"input_tokens": 21, "output_tokens": 1, "total_tokens": 22}
        last_request_id = "gen-123"

        def __call__(self, system: str, user: str) -> str:
            calls.append((system, user))
            return "OK"

    def _fake_build(provider, model, key_env, **kw):  # type: ignore[no-untyped-def]
        built.update(provider=provider, model=model, key_env=key_env)
        return _FakeTransport()

    import src.llm.client as client_mod

    monkeypatch.setattr(client_mod, "build_transport", _fake_build)
    rc = smoke_qwen.main()
    out = capsys.readouterr().out

    assert rc == 0
    # Routed the PINNED R71 config through the single dispatch point.
    assert built == {
        "provider": "openrouter", "model": "qwen/qwen3-coder", "key_env": "OPENROUTER_API_KEY",
    }
    # Exactly ONE tiny call carrying the OK instruction.
    assert len(calls) == 1
    assert "Reply with the single word OK" in calls[0][1]
    # Reports the reproducibility anchor + text + usage; the key is NEVER printed.
    assert "qwen/qwen3-coder-served-snapshot" in out
    assert "'OK'" in out
    assert "output_tokens" in out
    assert "sk-or-SECRET-not-to-print" not in out
