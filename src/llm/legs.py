"""v2 replication-leg loader — legs.yaml -> validated transport kwargs (R80/R82).

The executed leg config (``config/legs.yaml``) mirrors the registered ``model_suite`` spec.
This module is the single translation point from a leg entry to the transport-factory kwargs:

* OpenRouter **provider pinning** (``provider_pin`` -> ``extra_body["provider"]`` with
  ``allow_fallbacks: false`` — deterministic routing; the Qwen pair invariant),
* **quantization filters** (``quantizations`` -> ``extra_body["provider"]["quantizations"]``),
* **reasoning pins** (``reasoning`` -> ``extra_body["reasoning"]`` — DeepSeek think-mode,
  Luna effort, Gemini budget; explicit, never provider-default-trusted),
* **per-call cost capture** (``extra_body["usage"] = {"include": true}`` on OpenRouter so the
  realized dollar cost rides each response into the R83 advisory ledger),
* the registered per-leg **max_tokens pins** (R82 silent-truncation guard; kimi = 8192, R97a),
* the **rolling-alias ban** (defense in depth — also enforced at the transport factory).

Anthropic legs carry only id + max_tokens (native transport; no extra_body).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

__all__ = ["load_legs", "leg_by_label", "transport_kwargs"]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_legs(path: str | Path | None = None) -> dict[str, Any]:
    """Parse + validate ``config/legs.yaml``; fail loud on any structural violation."""
    import yaml

    p = Path(path) if path is not None else _repo_root() / "config" / "legs.yaml"
    cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    legs = cfg.get("legs") or []
    if not legs:
        raise ValueError(f"no legs in {p}")
    seen: set[str] = set()
    for leg in legs:
        for req in ("label", "provider", "model", "api_key_env"):
            if not leg.get(req):
                raise ValueError(f"leg {leg.get('label', '?')!r}: missing required field {req!r}")
        if leg["label"] in seen:
            raise ValueError(f"duplicate leg label {leg['label']!r}")
        seen.add(leg["label"])
        model = str(leg["model"])
        if "~" in model or model.endswith("-latest"):
            raise ValueError(
                f"leg {leg['label']!r}: model id {model!r} is a rolling alias — banned (R80)."
            )
        if "max_tokens" not in leg:
            raise ValueError(f"leg {leg['label']!r}: max_tokens pin is REQUIRED (R82).")
    return cfg


def leg_by_label(label: str, path: str | Path | None = None) -> dict[str, Any]:
    """The single leg entry named ``label`` (loud KeyError listing the known labels)."""
    legs = load_legs(path)["legs"]
    for leg in legs:
        if leg["label"] == label:
            return dict(leg)
    known = [str(leg["label"]) for leg in legs]
    raise KeyError(f"unknown leg {label!r}; known legs: {known}")


def transport_kwargs(leg: dict[str, Any]) -> dict[str, Any]:
    """Translate a validated leg entry into :func:`src.llm.client.make_real_transport` kwargs.

    OpenRouter legs get an ``extra_body`` assembling the provider pin, quantization filter,
    reasoning pin, and the usage-cost request; Anthropic legs get none (native transport).
    """
    provider = str(leg["provider"]).lower()
    kwargs: dict[str, Any] = {
        "provider": provider,
        "model": str(leg["model"]),
        "api_key_env": str(leg["api_key_env"]),
        "max_tokens": int(leg["max_tokens"]),
    }
    # R85 uniform-decoding pin: OpenRouter legs carry temperature: 1.0 in legs.yaml; a model that
    # rejects the parameter surfaces at the gate smoke and falls back to provider default,
    # disclosed. Anthropic legs never carry the key (the Opus no-temperature convention).
    if leg.get("temperature") is not None:
        kwargs["temperature"] = float(leg["temperature"])
    if provider == "anthropic":
        return kwargs  # id + max_tokens only; no extra_body on the native transport

    extra: dict[str, Any] = {}
    routing: dict[str, Any] = {}
    pin = leg.get("provider_pin") or {}
    if pin.get("only"):
        routing["only"] = list(pin["only"])
        routing["allow_fallbacks"] = bool(pin.get("allow_fallbacks", False))
    if leg.get("quantizations"):
        routing["quantizations"] = list(leg["quantizations"])
    if routing:
        extra["provider"] = routing
    if leg.get("reasoning"):
        extra["reasoning"] = dict(leg["reasoning"])
    # Per-call realized cost in the response (OpenRouter) -> the R83 advisory spend ledger.
    extra["usage"] = {"include": True}
    kwargs["extra_body"] = extra
    return kwargs
