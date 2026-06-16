"""Pinned, archival LLM client for reward discovery.

Purpose
-------
A thin wrapper around the language-model API used to propose reward functions
(FINAL_PLAN F.8). The client exists to make every LLM interaction *reproducible
by replay rather than regeneration* (audit C-2): it pins a model snapshot,
reads its key from an environment variable, and archives the exact rendered
prompt, the raw response, and the exact model id for every call. Downstream
analysis re-reads the archive -- it never re-queries the model.

Design notes
------------
    - Pinned snapshot: ``cfg`` must name a fully qualified, dated model
      snapshot (not a floating alias) so results are stable over time.
    - Dependency injection: the network call is performed by an injectable
      ``transport`` callable ``(system, user) -> str``. Tests and offline runs
      pass a :class:`FakeTransport`; production omits it and a real
      OpenAI-backed transport is created LAZILY (so ``openai`` need not be
      installed to import this module).
    - Key handling: the API key is read from an environment variable named in
      ``cfg`` and never persisted into the archive.
    - Archival (audit C-2): each ``complete`` call appends a provenance record
      containing the rendered system+user prompt, the raw response text, and the
      resolved model id, to an injectable archive sink.

Tests (tests/test_agents.py)
----------------------------
    - LLMClient with an injected FakeTransport returns the canned response and
      records the call (prompt + response + model id) in its archive.
    - constructing the real transport without a key / without openai raises a
      clear error (no network call is made).
"""

from __future__ import annotations


import os
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol

__all__ = [
    "Transport",
    "ProvenanceRecord",
    "LLMClient",
    "FakeTransport",
    "make_openai_transport",
]

#: Type of an injectable LLM transport: ``(system, user) -> response_text``.
Transport = Callable[[str, str], str]


class ArchiveSink(Protocol):
    """Structural type for an archive sink that records provenance.

    Any object with an ``append`` method accepting a :class:`ProvenanceRecord`
    satisfies the sink contract; a plain ``list`` does, which is what tests use.
    """

    def append(self, record: "ProvenanceRecord") -> None:  # pragma: no cover - proto
        ...


@dataclass(frozen=True)
class ProvenanceRecord:
    """One archived LLM interaction (audit C-2: replay, never regenerate).

    Attributes
    ----------
    model : str
        The exact, resolved model id (a pinned, dated snapshot).
    system : str
        The rendered system prompt.
    user : str
        The rendered user prompt.
    response : str
        The raw response text returned by the transport.
    """

    model: str
    system: str
    user: str
    response: str


def _cfg_get(cfg: Any, key: str, default: Any = None) -> Any:
    """Read ``key`` from a dict-like or attribute-like config object."""
    if cfg is None:
        return default
    if isinstance(cfg, dict):
        return cfg.get(key, default)
    return getattr(cfg, key, default)


def make_openai_transport(model: str, api_key_env: str) -> Transport:
    """Create a real OpenAI-backed transport, lazily importing ``openai``.

    Parameters
    ----------
    model : str
        The pinned, fully qualified model snapshot id.
    api_key_env : str
        Name of the environment variable holding the API key. The key is read
        here and closed over; it is never archived.

    Returns
    -------
    Transport
        A callable ``(system, user) -> response_text``.

    Raises
    ------
    RuntimeError
        If ``openai`` is not importable, or the API key environment variable is
        unset/empty. No network call is made in either failure path.
    """
    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise RuntimeError(
            f"OpenAI API key not found: environment variable {api_key_env!r} is "
            f"unset or empty. Set it, or inject a transport (e.g. FakeTransport) "
            f"for offline/testing use."
        )
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "openai is required for the real LLM transport; install the full env "
            "(see pyproject) or inject a transport (e.g. FakeTransport). The "
            "deterministic core does not need it."
        ) from exc

    client = OpenAI(api_key=api_key)

    def _transport(system: str, user: str) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content or ""

    return _transport


@dataclass
class FakeTransport:
    """Deterministic, offline transport for tests and dry runs.

    Returns a canned response and records every call it receives, so tests can
    assert on what the client sent.

    Attributes
    ----------
    response : str
        The canned response text returned by every call.
    calls : list of tuple
        Recorded ``(system, user)`` prompt pairs, in call order.
    """

    response: str = ""
    calls: list[tuple[str, str]] = field(default_factory=list)

    def __call__(self, system: str, user: str) -> str:
        self.calls.append((system, user))
        return self.response


class LLMClient:
    """Pinned, archival client for reward-proposing LLM calls (audit C-2).

    Parameters
    ----------
    cfg : Any
        Configuration. Recognised keys (dict or attributes): ``model`` (the
        pinned, dated snapshot id; required to construct the real transport) and
        ``api_key_env`` (env-var name holding the API key; default
        ``"OPENAI_API_KEY"``).
    transport : Transport, optional
        An injectable callable ``(system, user) -> str``. When omitted, a real
        OpenAI-backed transport is created LAZILY on first use (so importing this
        module never requires ``openai`` or a key). Tests inject a
        :class:`FakeTransport`.
    archive : ArchiveSink, optional
        An object with ``append``; each :meth:`complete` call appends a
        :class:`ProvenanceRecord`. Defaults to an internal list, accessible via
        :attr:`archive`.
    """

    def __init__(
        self,
        cfg: Any,
        transport: Transport | None = None,
        archive: ArchiveSink | None = None,
    ) -> None:
        self.cfg = cfg
        self.model: str = _cfg_get(cfg, "model", "")
        self.api_key_env: str = _cfg_get(cfg, "api_key_env", "OPENAI_API_KEY")
        self._transport = transport
        self.archive: ArchiveSink = archive if archive is not None else []

    def _ensure_transport(self) -> Transport:
        """Return the injected transport, or lazily build the real one."""
        if self._transport is None:
            if not self.model:
                raise RuntimeError(
                    "cfg.model must name a pinned model snapshot to build the real "
                    "OpenAI transport; or inject a transport (e.g. FakeTransport)."
                )
            self._transport = make_openai_transport(self.model, self.api_key_env)
        return self._transport

    def complete(self, system: str, user: str) -> str:
        """Run one chat completion and archive it for replay (audit C-2).

        The rendered prompt, raw response, and exact model id are appended to the
        archive BEFORE the response is returned, so the interaction can later be
        replayed deterministically rather than regenerated.

        Parameters
        ----------
        system : str
            The rendered system prompt.
        user : str
            The rendered user prompt.

        Returns
        -------
        str
            The raw response text from the transport.
        """
        transport = self._ensure_transport()
        response = transport(system, user)
        self.archive.append(
            ProvenanceRecord(
                model=self.model,
                system=system,
                user=user,
                response=response,
            )
        )
        return response
