"""The A5 self-host serving launcher: the `vllm serve` argv ENFORCES the pin (--revision) + dtype +
thinking-off, and the served-manifest records the enforced pin. Pure builders -> no GPU needed."""
import json

from scripts.serve_qwen_selfhost import build_manifest, build_serve_command


def test_serve_command_enforces_commit_dtype_and_thinking_off() -> None:
    cmd = build_serve_command(
        "Qwen/Qwen3.5-9B", "c202236235762e1c871ad0ccb60c8ee5ba337b9a", "bf16",
        "qwen3.5-9b", 8000, enable_thinking=False,
    )
    assert cmd[:2] == ["vllm", "serve"] and "Qwen/Qwen3.5-9B" in cmd
    # the ENFORCED weight pin (the whole point of A5 -- not advisory):
    assert "--revision" in cmd and cmd[cmd.index("--revision") + 1] == "c202236235762e1c871ad0ccb60c8ee5ba337b9a"
    # bf16 -> vLLM's bfloat16 spelling:
    assert cmd[cmd.index("--dtype") + 1] == "bfloat16"
    assert cmd[cmd.index("--served-model-name") + 1] == "qwen3.5-9b"
    # reasoning parser present so the archived reasoning_tokens PROVES thinking-off (R85 round-trip):
    assert cmd[cmd.index("--reasoning-parser") + 1] == "qwen3"
    kw = json.loads(cmd[cmd.index("--default-chat-template-kwargs") + 1])
    assert kw == {"enable_thinking": False}
    assert cmd[cmd.index("--port") + 1] == "8000"
    assert "--api-key" not in cmd  # none passed


def test_serve_command_passes_api_key_and_thinking_on() -> None:
    cmd = build_serve_command("R", "abc", "bfloat16", "m", 9001, enable_thinking=True, api_key="secret")
    assert cmd[cmd.index("--api-key") + 1] == "secret"
    assert cmd[cmd.index("--dtype") + 1] == "bfloat16"  # already-canonical dtype passes through
    assert json.loads(cmd[cmd.index("--default-chat-template-kwargs") + 1]) == {"enable_thinking": True}


def test_manifest_records_the_enforced_pin() -> None:
    m = build_manifest(
        "Qwen/Qwen3.5-9B", "c2022362", "bf16", "qwen3.5-9b", 8000,
        enable_thinking=False, versions={"vllm": "0.9.0", "torch": "2.6.0", "gpu": "A100"},
    )
    assert m["hf_repo"] == "Qwen/Qwen3.5-9B" and m["hf_commit"] == "c2022362"
    assert m["served_dtype"] == "bf16" and m["reasoning_enabled"] is False
    assert m["vllm_version"] == "0.9.0" and m["gpu"] == "A100"


# --- offline-weights preflight (2026-07-26) ---------------------------------------------------
# Myriad compute nodes have NO internet, so `vllm serve --revision` cannot fetch at serve time.
# These lock the guard that turns a wasted GPU allocation into an instant, self-explaining error.

def test_snapshot_path_follows_the_documented_hf_cache_layout():
    from scripts.serve_qwen_selfhost import hf_snapshot_dir

    p = hf_snapshot_dir("/scratch/hf", "Qwen/Qwen3.5-9B", "c202236")
    assert p.as_posix() == "/scratch/hf/hub/models--Qwen--Qwen3.5-9B/snapshots/c202236"


def test_preflight_REFUSES_when_HF_HOME_is_unset_and_says_how_to_stage():
    from scripts.serve_qwen_selfhost import preflight_weights

    ok, why = preflight_weights(None, "Qwen/Qwen3.5-9B", "c202236")
    assert not ok
    assert "no internet" in why and "--prestage" in why


def test_preflight_REFUSES_unstaged_weights_and_names_the_expected_path(tmp_path):
    """The whole point: fail BEFORE consuming the allocation, not inside vLLM afterwards."""
    from scripts.serve_qwen_selfhost import preflight_weights

    ok, why = preflight_weights(tmp_path, "Qwen/Qwen3.5-9B", "c202236")
    assert not ok
    assert "NOT staged" in why and "login node" in why.lower()


def test_an_EMPTY_snapshot_dir_does_NOT_count_as_staged(tmp_path):
    """A half-finished or interrupted download leaves the directory but no weights; treating that
    as staged would re-create exactly the silent failure this guard exists to prevent."""
    from scripts.serve_qwen_selfhost import hf_snapshot_dir, preflight_weights

    hf_snapshot_dir(tmp_path, "Qwen/Qwen3.5-9B", "c202236").mkdir(parents=True)
    ok, _ = preflight_weights(tmp_path, "Qwen/Qwen3.5-9B", "c202236")
    assert not ok


def test_preflight_PASSES_once_the_pinned_revision_is_staged(tmp_path):
    from scripts.serve_qwen_selfhost import hf_snapshot_dir, preflight_weights

    snap = hf_snapshot_dir(tmp_path, "Qwen/Qwen3.5-9B", "c202236")
    snap.mkdir(parents=True)
    (snap / "config.json").write_text("{}", encoding="utf-8")
    ok, why = preflight_weights(tmp_path, "Qwen/Qwen3.5-9B", "c202236")
    assert ok and "present" in why


def test_the_jobscript_exports_the_OFFLINE_env_the_preflight_depends_on():
    """The guard is only useful if the job actually runs offline against a shared HF_HOME."""
    from pathlib import Path

    sh = Path("scripts/serve_qwen_jobscript.sh").read_text(encoding="utf-8")
    assert "HF_HUB_OFFLINE" in sh and "HF_HOME" in sh
    assert "export HF_HOME" in sh
