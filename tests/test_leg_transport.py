"""v2 leg-transport tests (R80/R82): legs.yaml integrity, the loader's translation contract,
the rolling-alias ban, extra_body passthrough, and per-call cost capture."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.llm import client as C  # noqa: E402
from src.llm.legs import leg_by_label, load_legs, transport_kwargs  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
QUEUE = ["deepseek-v4-pro", "glm-5.2", "qwen3.6-27b", "qwen3.5-9b", "haiku-4.5",
         "gpt-5.6-luna", "nemotron-3-super", "sonnet-5",  # R90/R92: sonnet-4.6 removed, sonnet-5 stays
         "gemini-3.5-flash"]


# --------------------------------------------------------------------------- #
# legs.yaml integrity vs the registered model_suite                            #
# --------------------------------------------------------------------------- #
def test_legs_match_registered_queue_order():
    legs = load_legs()["legs"]
    ms = yaml.safe_load((REPO / "config" / "preregistration.yaml").read_text(encoding="utf-8"))
    assert [leg["label"] for leg in legs] == ms["model_suite"]["queue_order"] == QUEUE


def test_qwen_pair_invariant_same_provider_and_quant():
    """The confound-free family pair: identical provider pin AND quantization (R80)."""
    q27, q9 = leg_by_label("qwen3.6-27b"), leg_by_label("qwen3.5-9b")
    assert q27["provider_pin"] == q9["provider_pin"]
    assert q27["quantizations"] == q9["quantizations"] == ["fp8"]
    assert q27["provider_pin"]["allow_fallbacks"] is False


def test_every_leg_has_max_tokens_and_no_alias():
    for leg in load_legs()["legs"]:
        assert isinstance(leg["max_tokens"], int)
        assert "~" not in leg["model"] and not leg["model"].endswith("-latest")


def test_planning_prices_cover_all_legs():
    cfg = load_legs()
    priced = set(cfg["planning_prices"])
    assert {leg["model"] for leg in cfg["legs"]} <= priced


# --------------------------------------------------------------------------- #
# The loader's translation contract                                            #
# --------------------------------------------------------------------------- #
def test_transport_kwargs_openrouter_assembles_extra_body():
    kw = transport_kwargs(leg_by_label("qwen3.6-27b"))
    assert kw["provider"] == "openrouter" and kw["max_tokens"] == 4096
    eb = kw["extra_body"]
    assert eb["provider"] == {"only": ["siliconflow"], "allow_fallbacks": False,
                              "quantizations": ["fp8"]}
    assert eb["usage"] == {"include": True}  # per-call cost for the advisory ledger


def test_transport_kwargs_reasoning_pins():
    assert transport_kwargs(leg_by_label("deepseek-v4-pro"))["extra_body"]["reasoning"] == {
        "mode": "think-high"}
    luna = transport_kwargs(leg_by_label("gpt-5.6-luna"))
    assert luna["extra_body"]["reasoning"] == {"effort": "low"} and luna["max_tokens"] == 2048


def test_transport_kwargs_anthropic_is_bare():
    kw = transport_kwargs(leg_by_label("sonnet-5"))
    assert kw["provider"] == "anthropic" and "extra_body" not in kw


def test_loader_rejects_alias_and_missing_fields(tmp_path: Path):
    bad = tmp_path / "legs.yaml"
    bad.write_text("legs:\n  - {label: x, provider: openrouter, model: openai/gpt-latest, "
                   "api_key_env: K, max_tokens: 100}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="rolling alias"):
        load_legs(bad)
    bad.write_text("legs:\n  - {label: x, provider: openrouter, model: a/b, api_key_env: K}\n",
                   encoding="utf-8")
    with pytest.raises(ValueError, match="max_tokens"):
        load_legs(bad)


# --------------------------------------------------------------------------- #
# The transport factory: alias ban + extra_body plumbing + cost capture        #
# --------------------------------------------------------------------------- #
def test_factory_bans_rolling_aliases(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    with pytest.raises(ValueError, match="rolling 'latest' alias"):
        C.build_transport("openrouter", "~openai/gpt-latest")
    with pytest.raises(ValueError, match="rolling 'latest' alias"):
        C.build_transport("openrouter", "moonshotai/kimi-latest")


def test_factory_rejects_extra_body_on_anthropic(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with pytest.raises(ValueError, match="anthropic"):
        C.build_transport("anthropic", "claude-sonnet-4-6",
                          extra_body={"provider": {"only": ["x"]}})


class _FakeCompletions:
    def __init__(self, response):  # captures kwargs; returns the canned response
        self._response = response
        self.last_kwargs = None

    def create(self, **kwargs):
        self.last_kwargs = kwargs
        return self._response


def _fake_openai_client(response):
    return SimpleNamespace(chat=SimpleNamespace(completions=_FakeCompletions(response)))


def _fake_response(cost=None):
    usage = SimpleNamespace(prompt_tokens=10, completion_tokens=20, total_tokens=30, cost=cost)
    choice = SimpleNamespace(finish_reason="stop",
                             message=SimpleNamespace(content="def reward(): ..."))
    return SimpleNamespace(usage=usage, choices=[choice], id="req-1", model="served/slug")


def test_extra_body_reaches_the_wire_and_cost_is_captured():
    resp = _fake_response(cost=0.00123)
    fake = _fake_openai_client(resp)
    t = C._OpenAITransport(fake, "z-ai/glm-5.2", temperature=None, retrying=None,
                           max_tokens=4096,
                           extra_body={"provider": {"only": ["p"]}, "usage": {"include": True}})
    out = t("sys", "user")
    sent = fake.chat.completions.last_kwargs
    assert sent["extra_body"]["provider"] == {"only": ["p"]}
    assert sent["max_tokens"] == 4096
    assert out == "def reward(): ..."
    assert t.last_cost_usd == pytest.approx(0.00123)
    assert t.last_served_model == "served/slug"


def test_cost_none_when_provider_returns_no_cost():
    t = C._OpenAITransport(_fake_openai_client(_fake_response(cost=None)), "m",
                           temperature=None, retrying=None, max_tokens=100)
    t("s", "u")
    assert t.last_cost_usd is None
