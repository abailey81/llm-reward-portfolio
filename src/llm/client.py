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
      pass a :class:`FakeTransport`; production omits it and a real provider
      transport is created LAZILY per ``cfg.provider`` (default ``anthropic``; the
      campaign reward-author is Claude Opus 4.8 — ADR-035, which REJECTS temperature
      so its diversity is prompt-variation — and the prototype author is Claude
      Sonnet 4.6 — ADR-038, which honors temperature; so ``anthropic``/``openai``
      need not be installed to import this module).
    - Key handling: the API key is read from an environment variable named in
      ``cfg`` and never persisted into the archive.
    - Archival (audit C-2): each ``complete`` call appends a provenance record
      containing the rendered system+user prompt, the raw response text, the
      resolved model id, and (when the transport exposes it) the token ``usage``,
      to an injectable archive sink.

Tests (tests/test_agents.py)
----------------------------
    - LLMClient with an injected FakeTransport returns the canned response and
      records the call (prompt + response + model id) in its archive.
    - constructing the real transport without a key / without openai raises a
      clear error (no network call is made).
"""

from __future__ import annotations


import json
import logging
import os
from dataclasses import asdict, dataclass, field, is_dataclass
from pathlib import Path
from typing import Any, Callable, Protocol

from src.utils.config import cfg_get

#: Module logger (stdlib only — keeps this module importable without rich/anthropic). Under a campaign
#: run ``attach_run_logging`` routes its WARNINGs to events.jsonl + run.log so a truncated/refused
#: completion is loudly visible in monitoring, not silently swallowed.
_LOG = logging.getLogger("llm.client")

#: Provider stop/finish reasons that mean "the returned text is NOT a complete, willing answer" — a
#: ``max_tokens`` truncation (reward code cut off mid-function) or a safety ``refusal`` (empty/partial).
#: Surfaced per-call (``last_stop_reason`` -> ``ProvenanceRecord.stop_reason``) and WARN-logged so a
#: capped/refused completion is correctly ATTRIBUTED in the replay archive rather than mislabeled as a
#: sandbox-rejected "bad candidate" (which would silently bias the per-arm candidate-yield accounting).
#: Anthropic uses ``max_tokens``/``refusal``; the OpenAI-compatible surface uses ``length`` for truncation.
_INCOMPLETE_STOP_REASONS: frozenset[str] = frozenset({"max_tokens", "refusal", "length", "content_filter"})

# NOTE on prompt caching (measured 2026-06-29): the shared prefix here (prompts/system.txt + the rendered
# ENV_INTERFACE) is ~898 tokens — BELOW Opus 4.8's 4096-token minimum cacheable prefix (and below Sonnet
# 4.6's 2048-token floor). So the ``cache_control`` marker on the system block below is a SILENT NO-OP on
# both campaign + prototype models: caching cannot engage regardless of placement. It is left in place
# (harmless; would engage on a future model with a lower floor or a larger contract) and disclosed in the
# write-up — the ADR-016 "shared-context cache lever" is inert on Opus 4.8. The wasted spend is trivial
# (~188k prefix tokens over ~210 calls ~= $0.94), so no request restructuring is warranted.

__all__ = [
    "Transport",
    "ProvenanceRecord",
    "LLMClient",
    "FakeTransport",
    "JsonlArchiveSink",
    "make_openai_transport",
    "make_anthropic_transport",
    "build_transport",
    "default_key_env",
    "PROVIDERS",
]

#: Type of an injectable LLM transport: ``(system, user) -> response_text``.
Transport = Callable[[str, str], str]

#: Claude models that REJECT the ``temperature`` parameter (HTTP 400). Diversity for these comes from
#: per-candidate PROMPT VARIATION (src/llm/loop.py), not sampling. ``make_anthropic_transport`` drops a
#: stray ``temperature`` for these so a config mismatch can't silently 400 a run (audit 2026-06-20). The
#: campaign author Opus 4.8 is here; the prototype author Sonnet 4.6 is NOT (it honors temperature).
_TEMPERATURE_REJECTING_MODELS: tuple[str, ...] = ("opus-4-7", "opus-4-8")


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
    usage : dict or None
        Provider token-usage for the call (input/output + prompt-cache write/read counts) when
        the transport exposes it (Anthropic), else ``None``. Archived for cost accounting + to
        make the shared-context cache lever (ADR-016) measurable from the replay archive.
    stop_reason : str or None
        The provider stop/finish reason for the call (``end_turn``/``tool_use``/``max_tokens``/
        ``refusal`` on Anthropic; ``stop``/``length``/... on OpenAI-compatible) when the transport
        exposes it. A value in :data:`_INCOMPLETE_STOP_REASONS` means the archived ``response`` is a
        TRUNCATION or REFUSAL, not a complete candidate — so a later gate-rejection is correctly
        attributable rather than mislabeled as a "bad reward" (integrity of the per-arm yield count).
    request_id : str or None
        The provider request id (Anthropic ``response._request_id``; OpenAI ``response.id``) when
        exposed — provenance for replay + for reporting a failed call to the provider.
    served_model : str or None
        The model id string the PROVIDER's response reports it actually served (``response.model``)
        when the transport exposes it. For an aggregator like OpenRouter (the R71 secondary
        open-weights designer) this is the exact snapshot/version behind the requested slug — the
        REPRODUCIBILITY ANCHOR that must be recorded at the first live call (config/llm.yaml).
    """

    model: str
    system: str
    user: str
    response: str
    usage: dict[str, Any] | None = None
    stop_reason: str | None = None
    request_id: str | None = None
    served_model: str | None = None


def _warn_if_incomplete(stop_reason: str | None, model: str) -> None:
    """WARN-log when a completion is a truncation/refusal so it is not silently mislabeled downstream.

    The returned text for these stop reasons is partial (``max_tokens``/``length`` -> reward code cut off
    mid-function) or empty/partial (``refusal``/``content_filter``), so it will fail the AST gate. Logging
    it loudly (and recording ``stop_reason`` in the archive) keeps a capped/refused completion correctly
    ATTRIBUTED rather than counted as a genuine "bad candidate" — protecting the per-arm yield accounting.
    """
    if stop_reason in _INCOMPLETE_STOP_REASONS:
        _LOG.warning(
            "llm_incomplete_completion stop_reason=%s model=%s — response is truncated/refused, "
            "not a complete candidate; it will fail the AST gate and is archived as such.",
            stop_reason, model,
        )


def _openai_usage_dict(response: Any) -> dict[str, Any] | None:
    """Extract token usage from an OpenAI-compatible response as a plain dict (or None).

    Archived per call (audit C-2 + cost accounting) so any provider's token spend is measurable
    from the replay archive, exactly like the Anthropic path.
    """
    u = getattr(response, "usage", None)
    if u is None:
        return None
    return {
        "input_tokens": getattr(u, "prompt_tokens", None),
        "output_tokens": getattr(u, "completion_tokens", None),
        "total_tokens": getattr(u, "total_tokens", None),
    }


class _OpenAITransport:
    """Callable OpenAI-compatible transport (OpenAI / Gemini / DeepSeek) exposing ``last_usage``.

    Mirrors :class:`_AnthropicTransport`: applies the injected ``retrying`` backoff, passes
    ``temperature`` only when explicitly set (so temperature-rejecting endpoints aren't sent it),
    and records per-call token usage for the replay archive (read by :meth:`LLMClient.complete`).
    """

    def __init__(
        self,
        client: Any,
        model: str,
        *,
        temperature: float | None,
        retrying: Any,
        max_tokens: int = 4096,
        extra_body: dict[str, Any] | None = None,
    ) -> None:
        self._client = client
        self._model = model
        self._temperature = temperature
        self._retrying = retrying
        self._max_tokens = int(max_tokens)
        # v2 legs (R80/R82): OpenRouter routing prefs — provider pinning ({"provider": {"only":
        # [...], "allow_fallbacks": false}}), quantization filters, reasoning pins ({"reasoning":
        # {"effort"/"mode": ...}}), and {"usage": {"include": true}} (per-call cost for the R83
        # advisory ledger) — all ride the OpenAI SDK's ``extra_body`` passthrough.
        self._extra_body = dict(extra_body) if extra_body else None
        self.last_usage: dict[str, Any] | None = None
        self.last_stop_reason: str | None = None
        self.last_request_id: str | None = None
        self.last_served_model: str | None = None
        self.last_cost_usd: float | None = None

    def __call__(self, system: str, user: str) -> str:
        kwargs: dict[str, Any] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            # Cap the completion length (final-audit #35: this was never sent, so Gemini/DeepSeek/
            # OpenAI used each provider's default and could silently TRUNCATE a long reward -> gate
            # failure misattributed to a 'bad candidate'). Mirrors the Anthropic transport.
            "max_tokens": self._max_tokens,
        }
        if self._temperature is not None:
            kwargs["temperature"] = self._temperature
        if self._extra_body:
            kwargs["extra_body"] = self._extra_body

        def _call() -> Any:
            return self._client.chat.completions.create(**kwargs)

        response = self._retrying(_call) if self._retrying is not None else _call()
        self.last_usage = _openai_usage_dict(response)
        # OpenRouter returns the realized dollar cost in usage when {"usage": {"include": true}}
        # was requested (extra_body above); absent elsewhere -> None (the ledger then estimates
        # from tokens x planning prices). Advisory only (R83) — never gates.
        _usage_obj = getattr(response, "usage", None)
        _cost = getattr(_usage_obj, "cost", None) if _usage_obj is not None else None
        self.last_cost_usd = float(_cost) if _cost is not None else None
        choice = response.choices[0]
        self.last_stop_reason = getattr(choice, "finish_reason", None)
        self.last_request_id = getattr(response, "id", None)
        # The model the provider REPORTS it served (``response.model``). For OpenRouter (R71) this is
        # the exact snapshot behind the requested slug — archived as the reproducibility anchor.
        self.last_served_model = getattr(response, "model", None)
        _warn_if_incomplete(self.last_stop_reason, self._model)
        return choice.message.content or ""


def make_openai_transport(
    model: str,
    api_key_env: str,
    *,
    temperature: float | None = None,
    base_url: str | None = None,
    max_retries: int = 6,
    max_tokens: int = 4096,
    extra_body: dict[str, Any] | None = None,
) -> Transport:
    """Create a real OpenAI-SDK transport, lazily importing ``openai``.

    Serves every OpenAI-COMPATIBLE provider from one code path — OpenAI itself
    (``base_url=None``), Google **Gemini** (its ``/v1beta/openai/`` surface), **DeepSeek** and
    **OpenRouter** (the R71 secondary open-weights designer's aggregator) — because all four
    expose the same ``chat.completions`` API. The provider is therefore just a
    ``(base_url, key-env)`` choice and needs no extra SDK beyond ``openai`` (see
    :func:`build_transport`).

    Parameters
    ----------
    model, api_key_env : str
        Pinned model id and the env-var holding the API key (read here, never archived).
    temperature : float or None
        Sampling temperature; ``None`` leaves the provider default. The Eureka K-sampling loop
        needs > 0 for diversity on models that honor it (Gemini / DeepSeek-chat do; models that
        reject it use prompt-variation diversity instead — see ``src/llm/loop.py``).
    base_url : str or None
        OpenAI-compatible API base URL; ``None`` = the default OpenAI endpoint.
    max_retries : int
        tenacity attempts on transient errors; the SDK's own retries are set to 0 (ADR-034).

    Raises
    ------
    RuntimeError
        If ``openai`` is not importable, or the key env var is unset/empty (no network call).
    """
    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise RuntimeError(
            f"OpenAI-compatible API key not found: environment variable {api_key_env!r} is "
            f"unset or empty. Set it, or inject a transport (e.g. FakeTransport) for offline use."
        )
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "openai is required for the OpenAI/Gemini/DeepSeek transport; `pip install openai` "
            "or inject a transport (e.g. FakeTransport). The deterministic core does not need it."
        ) from exc

    # SDK retries OFF (ADR-034): tenacity is the single, observable backoff policy.
    client = OpenAI(api_key=api_key, base_url=base_url, max_retries=0)
    return _OpenAITransport(
        client, model, temperature=temperature, retrying=_make_retrying(max_retries),
        max_tokens=max_tokens, extra_body=extra_body,
    )


def _is_transient_api_error(exc: BaseException) -> bool:
    """True for retryable LLM-API failures (connection/timeout/rate-limit/5xx/overloaded).

    Matched by class NAME + HTTP status so we need not import provider-specific exception
    classes (keeps the retry policy portable across the anthropic/openai SDKs). 4xx client
    errors (bad request, auth, permission) are NOT transient and are re-raised immediately.
    """
    name = type(exc).__name__
    if name in (
        "APIConnectionError",
        "APITimeoutError",
        "RateLimitError",
        "InternalServerError",
        "APIError",
    ):
        return True
    status = getattr(exc, "status_code", None)
    return isinstance(status, int) and status >= 500


def _make_retrying(max_retries: int) -> Any:
    """Build a tenacity ``Retrying`` (exponential backoff) or ``None`` if retries are off.

    ``tenacity`` is imported LAZILY so the deterministic core need not depend on it; if it is
    absent the transport still works (single attempt, no backoff). ADR-034 wiring: the SDK's
    own ``max_retries`` is set to 0 so this is the single, observable backoff policy.
    """
    if max_retries <= 0:
        return None
    try:
        from tenacity import Retrying, retry_if_exception, stop_after_attempt, wait_exponential
    except ImportError:  # pragma: no cover - tenacity is a declared dep; degrade gracefully
        return None
    return Retrying(
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential(multiplier=1.0, min=1.0, max=30.0),
        retry=retry_if_exception(_is_transient_api_error),
        reraise=True,
    )


def _usage_dict(message: Any) -> dict[str, Any] | None:
    """Extract the token-usage object from an Anthropic message as a plain dict (or None).

    Archived per call (audit C-2 + cost accounting against the GPU/API budget): records input,
    output, and the prompt-cache write/read token counts so the K-shared-context cache lever
    (ADR-016) is measurable from the replay archive.
    """
    u = getattr(message, "usage", None)
    if u is None:
        return None
    return {
        "input_tokens": getattr(u, "input_tokens", None),
        "output_tokens": getattr(u, "output_tokens", None),
        "cache_creation_input_tokens": getattr(u, "cache_creation_input_tokens", None),
        "cache_read_input_tokens": getattr(u, "cache_read_input_tokens", None),
    }


def _is_key_dead_error(exc: BaseException) -> bool:
    """True iff ``exc`` means THIS KEY cannot pay/authenticate — the only failover triggers.

    Duck-typed on ``status_code`` (SDK-independent, hence unit-testable without ``anthropic``):
    * **400 + "credit balance"** — Anthropic's insufficient-funds error ("Your credit balance is
      too low to access the Anthropic API") — the account is dry; a different funded key fixes it.
    * **401** — authentication_error: the key is invalid/disabled/revoked.

    DELIBERATELY excluded: 429/5xx/overloaded (transient — tenacity retries them on the SAME key;
    rotating would burn the fallback on a shared outage) and every other 400 (a malformed request
    fails identically on any key — rotating cannot help and would only mask a real bug).
    """
    status = getattr(exc, "status_code", None)
    if status == 401:
        return True
    return status == 400 and "credit balance" in str(exc).lower()


class _AnthropicTransport:
    """Callable Anthropic transport that also exposes ``last_usage`` for archival.

    A plain closure cannot surface per-call token usage to :class:`LLMClient`; this small
    callable class does (the client reads ``getattr(transport, "last_usage", None)`` after
    each completion). Prompt-caches the static system block, applies the injected ``retrying``
    backoff, and passes ``temperature`` only when explicitly set (else the provider default —
    which for the Eureka K-sampling loop MUST stay > 0, ADR-016).

    **Automatic key failover (2026-07-19, Tamer's request).** If ``fallback_key_env`` names a
    set, non-empty env var (convention: ``<primary>_FALLBACK``, e.g.
    ``ANTHROPIC_API_KEY_FALLBACK``), then a call that fails with a KEY-DEAD error
    (:func:`_is_key_dead_error`: credit exhausted, or 401) switches to a fresh client built on
    the fallback key and retries the SAME request once. The switch is **sticky** (every later
    call uses the fallback — no flapping) and **loud** (an ERROR log; the archived call itself
    is unaffected — a failed request never billed and never generated). With no fallback set,
    behaviour is byte-identical to before: the error propagates and the loop's skip-and-resume
    path handles it. Safe by construction: authored candidates replay from the archive, so the
    retried request can never double-bill or duplicate a candidate.
    """

    def __init__(
        self,
        client: Any,
        model: str,
        *,
        temperature: float | None,
        max_tokens: int,
        cache_system: bool,
        retrying: Any,
        fallback_key_env: str | None = None,
        client_factory: Any = None,  # Callable[[str], client]; injectable for tests
    ) -> None:
        self._client = client
        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._cache_system = cache_system
        self._retrying = retrying
        self._fallback_key_env = fallback_key_env
        self._client_factory = client_factory
        self._failed_over = False
        self.last_usage: dict[str, Any] | None = None
        self.last_stop_reason: str | None = None
        self.last_request_id: str | None = None
        self.last_served_model: str | None = None

    def _try_failover(self, exc: BaseException) -> bool:
        """Switch to the fallback key if ``exc`` is key-dead and a fallback is available."""
        if self._failed_over or not self._fallback_key_env or not _is_key_dead_error(exc):
            return False
        fallback_key = os.environ.get(self._fallback_key_env, "").strip()
        if not fallback_key:
            return False
        if self._client_factory is not None:
            new_client = self._client_factory(fallback_key)
        else:  # pragma: no cover - exercised only with the real SDK installed
            from anthropic import Anthropic

            new_client = Anthropic(api_key=fallback_key, max_retries=0)
        _LOG.error(
            "API KEY FAILOVER: the primary key is dead (%s: %s) — switching PERMANENTLY to the "
            "fallback key from %s and retrying this request. Top up / replace the primary before "
            "the next run.",
            type(exc).__name__, str(exc)[:160], self._fallback_key_env,
        )
        self._client = new_client
        self._failed_over = True
        return True

    def __call__(self, system: str, user: str) -> str:
        # Prompt-cache the static system block (ADR-016: the K=16 shared-context lever — a 5-min
        # ephemeral cache makes the repeated env-source/system prefix ~0.1x to read).
        system_arg: Any = (
            [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
            if self._cache_system
            else system
        )
        kwargs: dict[str, Any] = {
            "model": self._model,
            "max_tokens": self._max_tokens,
            "system": system_arg,
            "messages": [{"role": "user", "content": user}],
        }
        if self._temperature is not None:
            kwargs["temperature"] = self._temperature

        def _call() -> Any:
            return self._client.messages.create(**kwargs)

        try:
            message = self._retrying(_call) if self._retrying is not None else _call()
        except Exception as exc:  # noqa: BLE001 — classify, fail over on key-dead only, else re-raise
            if not self._try_failover(exc):
                raise
            # One sticky retry of the SAME request on the fallback client (idempotent: the failed
            # request neither billed nor generated; the archive/ledger never double-bills).
            message = self._retrying(_call) if self._retrying is not None else _call()
        self.last_usage = _usage_dict(message)
        self.last_stop_reason = getattr(message, "stop_reason", None)
        self.last_request_id = getattr(message, "_request_id", None)
        self.last_served_model = getattr(message, "model", None)
        _warn_if_incomplete(self.last_stop_reason, self._model)
        parts = [blk.text for blk in message.content if getattr(blk, "type", None) == "text"]
        return "".join(parts)


def make_anthropic_transport(
    model: str,
    api_key_env: str,
    *,
    temperature: float | None = None,
    max_tokens: int = 4096,
    cache_system: bool = True,
    max_retries: int = 6,
) -> Transport:
    """Create a real Anthropic-backed transport, lazily importing ``anthropic`` (ADR-033 primary).

    The PRIMARY reward-author transport: serves BOTH the campaign author Claude Opus 4.8 (ADR-035)
    and the prototype author Claude Sonnet 4.6 (ADR-038). Reads the key from ``api_key_env``
    (never archived), pins ``model``, maps the system prompt to Anthropic's top-level ``system``
    field, and wires the ADR-034 "queued" hardening: prompt-cache the static system block, archive
    the ``usage`` object (via ``last_usage``), and own retry/backoff (the SDK's ``max_retries`` is
    set to 0 so ``tenacity`` is the single backoff policy).

    Parameters
    ----------
    model, api_key_env : str
        Pinned model snapshot id and the env-var name holding the API key.
    temperature : float or None
        Sampling temperature. ``None`` (default) leaves the provider default. NOTE: the Eureka loop
        samples ``candidates_per_gen`` candidates from the SAME prompt, so on a temperature-HONORING
        model (Sonnet 4.6) within-generation diversity comes from sampling — keep it > 0 (ADR-016/038
        use 1.0). Opus 4.7/4.8 instead REJECT temperature (HTTP 400): a stray value is DROPPED here
        (see ``_TEMPERATURE_REJECTING_MODELS``) and their diversity comes from prompt-variation
        (``src/llm/loop.py``), not sampling.
    max_tokens : int
        Output cap per completion (default 4096, matching ``config/llm.yaml``).
    cache_system : bool
        Mark the system block with an ephemeral ``cache_control`` (the shared-context cache lever).
    max_retries : int
        tenacity attempts on transient errors (connection/timeout/rate-limit/5xx). 0 disables.

    Raises
    ------
    RuntimeError
        If ``anthropic`` is not importable or the key env var is unset/empty (no network
        call is made in either failure path).
    """
    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise RuntimeError(
            f"Anthropic API key not found: environment variable {api_key_env!r} is unset "
            f"or empty. Set it, or inject a transport (FakeTransport / StubDesignerTransport)."
        )
    try:
        from anthropic import Anthropic
    except ImportError as exc:
        raise RuntimeError(
            "anthropic is required for the Anthropic transport; `pip install anthropic` or "
            "inject a transport. The deterministic core does not need it."
        ) from exc

    # Opus 4.7/4.8 REJECT temperature (HTTP 400); drop a stray value so a config mismatch can't silently
    # 400 the campaign run (their diversity is prompt-variation, not sampling). Sonnet 4.6 honors it.
    if temperature is not None and any(p in model for p in _TEMPERATURE_REJECTING_MODELS):
        temperature = None
    # SDK retries OFF (ADR-034): tenacity is the single, observable backoff policy.
    client = Anthropic(api_key=api_key, max_retries=0)
    return _AnthropicTransport(
        client,
        model,
        temperature=temperature,
        max_tokens=max_tokens,
        cache_system=cache_system,
        retrying=_make_retrying(max_retries),
        # Automatic key failover (2026-07-19): <primary>_FALLBACK, e.g. ANTHROPIC_API_KEY_FALLBACK.
        # Read lazily at failover time, so adding it to .env mid-run needs no rebuild.
        fallback_key_env=f"{api_key_env}_FALLBACK",
    )


# --------------------------------------------------------------------------- #
# Provider registry + single transport factory (provider dispatch lives HERE). #
# --------------------------------------------------------------------------- #
#: OpenAI-compatible providers -> API base URL (None = the default OpenAI endpoint). Google
#: Gemini, DeepSeek and OpenRouter all expose an OpenAI ``chat.completions`` surface, so one
#: transport serves them all; adding a provider is one registry entry, not a new SDK.
_OPENAI_COMPAT_BASE_URL: dict[str, str | None] = {
    "openai": None,
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "deepseek": "https://api.deepseek.com",
    # R71 (pinned 2026-07-02): OpenRouter can serve the SECONDARY open-weights designer
    # (Qwen3-Coder — config/llm.yaml ``open_weights_*``; report-only, NEVER confirmatory).
    "openrouter": "https://openrouter.ai/api/v1",
    # 2026-07-06 (supersedes the OpenRouter ROUTING for R71; the Qwen3-Coder model decision is
    # unchanged): first-party Alibaba Cloud Model Studio — the Qwen vendor's own OpenAI-compatible
    # host (a stronger reproducibility anchor than a router). This default is the PUBLIC
    # international endpoint; a personal WORKSPACE endpoint overrides at build time via
    # ``DASHSCOPE_BASE_URL`` in the gitignored .env, so no personal workspace URL is committed.
    "dashscope": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
}

#: Default env-var holding each provider's API key (overridable via ``cfg.api_key_env``).
_DEFAULT_KEY_ENV: dict[str, str] = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "dashscope": "DASHSCOPE_API_KEY",
}

#: Providers the registry can build a real transport for (Pass A uses the keyless stub instead).
PROVIDERS: tuple[str, ...] = ("anthropic", "openai", "gemini", "deepseek", "openrouter", "dashscope")


def default_key_env(provider: str) -> str:
    """The conventional env-var name holding ``provider``'s API key (falls back to OPENAI)."""
    return _DEFAULT_KEY_ENV.get(provider.lower(), "OPENAI_API_KEY")


def build_transport(
    provider: str,
    model: str,
    api_key_env: str | None = None,
    *,
    temperature: float | None = None,
    max_tokens: int = 4096,
    max_retries: int = 6,
    extra_body: dict[str, Any] | None = None,
) -> Transport:
    """Single, centralized real-transport factory — provider dispatch lives in ONE place.

    Used by :class:`LLMClient` AND every orchestrator (``run_prototype``/``parallel``/
    ``run_campaign``), so a new provider is one registry entry rather than a four-file edit
    (provider-neutral architecture, 2026-06-19). Routes ``anthropic`` to the native Anthropic
    transport (prompt-cache + usage + retry) and ``openai``/``gemini``/``deepseek``/``openrouter``
    to the OpenAI-SDK transport pointed at the provider's OpenAI-compatible base URL.

    Raises
    ------
    RuntimeError
        For an unknown provider, or (lazily, at build time) a missing key / SDK.
    """
    provider = provider.lower()
    # ROLLING-ALIAS BAN (R80, 2026-07-20): OpenRouter's "~vendor/*-latest" aliases redirect to
    # the newest family member — reproducibility poison for a pinned study. Reject at the single
    # factory chokepoint so no code path can construct one.
    if "~" in model or model.endswith("-latest"):
        raise ValueError(
            f"model id {model!r} is a rolling 'latest' alias — banned for reproducibility (R80). "
            "Pin the concrete slug/snapshot instead."
        )
    key_env = api_key_env or default_key_env(provider)
    if provider == "anthropic":
        if extra_body:
            raise ValueError(
                "extra_body (OpenRouter routing/reasoning prefs) is not supported on the "
                "anthropic transport — leg pins for Anthropic models are id+max_tokens only."
            )
        return make_anthropic_transport(
            model, key_env, temperature=temperature, max_tokens=max_tokens, max_retries=max_retries
        )
    if provider in _OPENAI_COMPAT_BASE_URL:
        base_url = _OPENAI_COMPAT_BASE_URL[provider]
        if provider == "dashscope":
            # Resolved at BUILD time (not module import): entry points call load_env() AFTER this
            # module imports, so a .env-supplied workspace endpoint must be read here.
            import os as _os

            base_url = _os.environ.get("DASHSCOPE_BASE_URL", base_url)
        return make_openai_transport(
            model,
            key_env,
            temperature=temperature,
            base_url=base_url,
            max_retries=max_retries,
            max_tokens=max_tokens,  # final-audit #35: was dropped, capping Gemini/DeepSeek silently
            extra_body=extra_body,  # v2 legs: provider pins / quantizations / reasoning / usage-cost
        )
    raise RuntimeError(
        f"unknown LLM provider {provider!r}; known providers: {', '.join(PROVIDERS)} "
        f"(or use the keyless stub designer for Pass A)."
    )


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


class JsonlArchiveSink(list):
    """A list-compatible archive sink that ALSO appends each record to a jsonl ledger AT CALL TIME.

    F11 (ultrareview 2026-07-02): :class:`LLMClient` archives one :class:`ProvenanceRecord` per call
    into its sink, and the orchestrators used to dump that in-memory list to ``llm_calls.jsonl`` at END
    OF ARM in ``"w"`` mode — so a mid-arm crash lost the arm's ENTIRE call provenance, including the R71
    ``served_model`` reproducibility anchor that config/llm.yaml requires recorded at the FIRST live
    call. This sink keeps the in-memory list contract (``src/llm/loop.py`` reads ``archive[-1].usage``
    after each call) and ADDITIONALLY appends the row to disk with a flush the moment it is archived,
    so a crash loses at most the in-flight call. The disk write is best-effort (a provenance-ledger
    hiccup must never crash a paid call): on failure the in-memory record is kept and the next append
    retries the file.
    """

    def __init__(self, path: str | Path) -> None:
        super().__init__()
        self._path = Path(path)
        self._n_write_failures = 0

    def append(self, record: Any) -> None:  # type: ignore[override]
        super().append(record)
        try:
            row = (
                asdict(record)
                if is_dataclass(record) and not isinstance(record, type)
                else dict(record)
            )
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with self._path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row, default=str) + "\n")
                fh.flush()
        except Exception as exc:  # noqa: BLE001 — best-effort ledger; the in-memory copy is updated
            # 2026-07-06: the no-raise contract stands (a provenance hiccup must never crash a paid
            # call), but a PERSISTENT failure (AV lock, permissions) silently losing the ONLY
            # on-disk copy of raw responses/usage/served_model deserved at least a visible warning.
            # Rate-limited: the first failure + every 50th.
            self._n_write_failures += 1
            import logging as _lg

            _log = _lg.getLogger(__name__)
            if self._n_write_failures >= 3:
                # row 30g (audit 2026-07-22): >=3 consecutive-run failures = a PERSISTENT condition
                # (AV lock / permissions / disk-full) silently starving the replay archive. Escalate
                # to ERROR on EVERY failure (the sentinel greps ERROR) + drop a best-effort marker
                # the monitor can see. The no-raise contract stands — never crash a paid call.
                _log.error(
                    "llm_calls.jsonl append FAILED (%d so far, PERSISTENT) at %s: %s — the "
                    "replay archive is losing rows; fix the disk/permissions NOW",
                    self._n_write_failures, self._path, exc,
                )
                try:
                    (self._path.parent / "ARCHIVE_WRITE_FAILURES").write_text(
                        f"{self._n_write_failures} failures; last: {exc}\n", encoding="utf-8")
                except Exception:  # noqa: BLE001 — the marker itself is best-effort
                    pass
            elif self._n_write_failures == 1:
                _log.warning(
                    "llm_calls.jsonl append FAILED (first) at %s: %s — raw call provenance is "
                    "not reaching disk", self._path, exc,
                )


class LLMClient:
    """Pinned, archival client for reward-proposing LLM calls (audit C-2).

    Parameters
    ----------
    cfg : Any
        Configuration. Recognised keys (dict or attributes): ``model`` (the pinned, dated
        snapshot id; required to construct the real transport); ``provider`` (``"anthropic"``
        — the ADR-033 PRIMARY default — ``"openai"``/``"deepseek"`` for the OpenAI-compatible
        check model); ``api_key_env`` (env-var name holding the API key; defaults to
        ``"ANTHROPIC_API_KEY"`` for the anthropic provider, else ``"OPENAI_API_KEY"``); and an
        optional ``temperature`` (left at the provider default when absent — see the transport
        note: the Eureka loop needs temperature > 0).
    transport : Transport, optional
        An injectable callable ``(system, user) -> str``. When omitted, a real provider-backed
        transport is created LAZILY on first use per ``provider`` (so importing this module never
        requires ``anthropic``/``openai`` or a key). Tests inject a :class:`FakeTransport`.
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
        self.model: str = cfg_get(cfg, "model", "")
        self.provider: str = str(cfg_get(cfg, "provider", "anthropic")).lower()
        self.api_key_env: str = cfg_get(cfg, "api_key_env", default_key_env(self.provider))
        self.temperature: float | None = cfg_get(cfg, "temperature", None)
        # F17 (ultrareview 2026-07-02): honor cfg ``max_tokens``/``max_retries`` when lazily building
        # the real transport (defaults = the historical hardcodes 4096/6) — raising the value in the
        # author config (e.g. config/llm.yaml: max_tokens) must not silently no-op into truncation.
        self.max_tokens: int = int(cfg_get(cfg, "max_tokens", 4096))
        self.max_retries: int = int(cfg_get(cfg, "max_retries", 6))
        self._transport = transport
        self.archive: ArchiveSink = archive if archive is not None else []
        # R83 advisory spend ledger (v2): when cfg names a ledger path, every completed call's
        # realized cost (transport ``last_cost_usd``; OpenRouter usage.cost) — or, failing that,
        # the tokens×planning-prices estimate — is appended per-call. None/absent -> no recording
        # (bare clients, tests, and fakes stay ledger-silent; the campaign author paths thread the
        # path in via opts). Advisory: recording failures warn (rate-limited), never raise.
        self.spend_ledger: str | None = cfg_get(cfg, "spend_ledger", None) or None
        self._n_ledger_failures = 0

    def _ensure_transport(self) -> Transport:
        """Return the injected transport, or lazily build the real one for ``provider``."""
        if self._transport is None:
            if not self.model:
                raise RuntimeError(
                    "cfg.model must name a pinned model snapshot to build the real "
                    f"{self.provider} transport; or inject a transport (e.g. FakeTransport)."
                )
            self._transport = build_transport(
                self.provider, self.model, self.api_key_env, temperature=self.temperature,
                max_tokens=self.max_tokens, max_retries=self.max_retries,  # F17: cfg-driven caps
            )
        return self._transport

    def advance_author_stream(self, k: int = 1) -> None:
        """Consume ``k`` author-stream positions WITHOUT a call — resume replay of AUTHORED slots.

        A resume replays archived candidates (and ledgered sandbox failures) instead of re-calling
        the author; each such slot consumed one authoring call in the original run. POSITIONAL
        transports (the keyless Pass-A stub, whose call ``n`` is a pure function of ``(seed, n)``)
        expose ``advance`` so the post-resume fresh candidates keep the indices — hence the exact
        outputs — they would have had uninterrupted (2026-07-06, crash-rehearsal catch). Real LLM
        transports have no ``advance`` (a paid, non-deterministic call cannot be replayed by
        position) -> silently a no-op, leaving Pass-B replay semantics exactly as before. Reads the
        injected transport directly: never lazily builds a real one just to no-op it."""
        adv = getattr(self._transport, "advance", None)
        if adv is not None:
            adv(int(k))

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
        # Transports that surface per-call metadata (the real provider transports) expose it via
        # ``last_usage`` / ``last_stop_reason`` / ``last_request_id`` / ``last_served_model``;
        # closures/FakeTransport that do not -> None (audit C-2 / cost accounting +
        # truncation-attribution + provenance + the R71 served-snapshot reproducibility anchor).
        usage = getattr(transport, "last_usage", None)
        stop_reason = getattr(transport, "last_stop_reason", None)
        request_id = getattr(transport, "last_request_id", None)
        served_model = getattr(transport, "last_served_model", None)
        self.archive.append(
            ProvenanceRecord(
                model=self.model,
                system=system,
                user=user,
                response=response,
                usage=usage,
                stop_reason=stop_reason,
                request_id=request_id,
                served_model=served_model,
            )
        )
        self._record_spend(transport, usage)
        return response

    def _record_spend(self, transport: Any, usage: dict[str, Any] | None) -> None:
        """Best-effort R83 per-call ledger append (advisory — must NEVER crash a paid call).

        Records ONLY when a ledger path is configured AND the transport surfaced real per-call
        metadata (cost or usage) — fakes/stubs expose neither and stay silent. Realized cost
        (``last_cost_usd``) is the authority; else the tokens×planning-prices estimate; an
        unpriced model records $0 with an explicit note rather than a fabricated number.
        """
        if not self.spend_ledger:
            return
        cost = getattr(transport, "last_cost_usd", None)
        if cost is None and usage is None:
            return  # no real metadata (fake/stub transport) — nothing truthful to record
        try:
            from src.llm.spend_ledger import estimate_cost_usd, record_spend

            t_in = (usage or {}).get("input_tokens")
            t_out = (usage or {}).get("output_tokens")
            note = "realized"
            if cost is None:
                cost = estimate_cost_usd(self.model, t_in, t_out)
                note = "estimated-from-planning-prices"
            if cost is None:
                cost, note = 0.0, "cost-unknown(model-unpriced)"
            record_spend(
                self.spend_ledger, provider=self.provider, model=self.model,
                cost_usd=float(cost), tokens_in=t_in, tokens_out=t_out, note=note,
            )
        except Exception as exc:  # noqa: BLE001 — advisory ledger: warn (rate-limited), never raise
            self._n_ledger_failures += 1
            if self._n_ledger_failures == 1 or self._n_ledger_failures % 50 == 0:
                logging.getLogger(__name__).warning(
                    "spend-ledger append FAILED (%d so far) at %s: %s — advisory only, call "
                    "unaffected", self._n_ledger_failures, self.spend_ledger, exc,
                )
        return
