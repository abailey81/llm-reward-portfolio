#!/usr/bin/env python
"""Serve the self-hosted, HF-commit-PINNED, bf16 Qwen leg on a GPU node (the A5 reproducibility-
permanence anchor: the lineage's first fully-pinned open-weight author). vLLM exposes the
OpenAI-compatible /v1/chat/completions surface that ``src/llm/client.py``'s ``vllm_selfhost`` provider
consumes, so NO new transport is needed.

WHY this closes the gap closed / aggregator-served models cannot (Stefan #1/#3; R85):
  * ``--revision <commit>`` makes vLLM download and serve EXACTLY the pinned HF commit -- the pin is
    ENFORCED at serve time, not merely reported by an aggregator whose serving stack / quantization can
    drift silently. This is the first leg in the lineage whose weight pin is enforceable, not advisory.
  * ``--dtype bfloat16`` pins the served numeric variant (recorded, never inferred).
  * ``--reasoning-parser qwen3 --default-chat-template-kwargs {"enable_thinking": false}`` pins thinking
    OFF (the R103 fix: Qwen3 defaults to thinking-ON, which spends the whole output budget on hidden
    reasoning -> EMPTY authored code) AND separates reasoning so the archived response PROVES it
    (``reasoning_tokens == 0``), closing the R85 round-trip. The client sends the request-level override
    too (belt-and-suspenders; request-level wins over the server default).
  * a ``served-manifest.json`` records the enforced commit + dtype + vLLM/torch/GPU versions -- the
    serving-NODE provenance the driver-side ``capture_env`` cannot see.

Usage (on the GPU node):
    python -m scripts.serve_qwen_selfhost --leg qwen3.5-9b-selfhost --port 8000
then, for the campaign driver:  export VLLM_BASE_URL=http://<node>:8000/v1  VLLM_API_KEY=<key>
``--dry-run`` prints the exact command + writes the manifest WITHOUT launching (CI / off-GPU safe).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, Sequence

#: vLLM's ``--dtype`` spellings (the leg records the short form in ``quantizations``).
_DTYPE_ALIASES = {"bf16": "bfloat16", "fp16": "float16", "fp32": "float32"}


def build_serve_command(
    repo: str, commit: str, dtype: str, served_name: str, port: int,
    *, enable_thinking: bool, api_key: Optional[str] = None,
) -> list[str]:
    """The exact ``vllm serve`` argv that ENFORCES the pin (``--revision``) + dtype + thinking state.

    Pure + deterministic so it is unit-tested without a GPU; the enforcement (not merely the recording)
    of the commit is what makes this leg's reproducibility real rather than advisory (R85).
    """
    dtype_arg = _DTYPE_ALIASES.get(str(dtype).lower(), str(dtype))
    cmd = [
        "vllm", "serve", str(repo),
        "--revision", str(commit),          # ENFORCE the pinned weights -- the first enforceable pin (R85)
        "--dtype", dtype_arg,
        "--served-model-name", str(served_name),
        "--reasoning-parser", "qwen3",      # separate reasoning so reasoning_tokens PROVES thinking-off
        "--default-chat-template-kwargs", json.dumps({"enable_thinking": bool(enable_thinking)}),
        "--port", str(int(port)),
    ]
    if api_key:
        cmd += ["--api-key", str(api_key)]
    return cmd


def build_manifest(
    repo: str, commit: str, dtype: str, served_name: str, port: int,
    *, enable_thinking: bool, versions: dict[str, Any],
) -> dict[str, Any]:
    """The served-manifest: serving-NODE provenance the driver-side ``capture_env`` cannot capture."""
    return {
        "leg": str(served_name),
        "served_model_name": str(served_name),
        "hf_repo": str(repo),
        "hf_commit": str(commit),           # the ENFORCED pin (--revision)
        "served_dtype": str(dtype),
        "reasoning_enabled": bool(enable_thinking),
        "port": int(port),
        "vllm_version": versions.get("vllm"),
        "torch_version": versions.get("torch"),
        "gpu": versions.get("gpu"),
    }


def _versions() -> dict[str, Any]:
    """Best-effort serving-stack versions (absence recorded as null, never fabricated)."""
    v: dict[str, Any] = {"vllm": None, "torch": None, "gpu": None}
    try:
        import vllm  # type: ignore
        v["vllm"] = getattr(vllm, "__version__", None)
    except Exception:  # noqa: BLE001 -- provenance is best-effort; a missing serving dep is recorded null
        pass
    try:
        import torch  # type: ignore
        v["torch"] = torch.__version__
        if torch.cuda.is_available():
            v["gpu"] = torch.cuda.get_device_name(0)
    except Exception:  # noqa: BLE001
        pass
    return v


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Serve the pinned bf16 Qwen self-host leg (A5).")
    p.add_argument("--leg", default="qwen3.5-9b-selfhost", help="leg label in config/legs.yaml")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--manifest", default=None, help="where to write served-manifest.json")
    p.add_argument("--dry-run", action="store_true",
                   help="print the command + write the manifest; do NOT launch (CI / off-GPU safe)")
    args = p.parse_args(argv)

    from src.llm.legs import leg_by_label
    leg = leg_by_label(args.leg)
    if str(leg.get("provider")) != "vllm_selfhost":
        raise SystemExit(f"leg {args.leg!r} is provider {leg.get('provider')!r}, not vllm_selfhost")
    hf = leg.get("hf_pin") or {}
    repo, commit = hf.get("repo"), hf.get("commit")
    if not repo or not commit:
        raise SystemExit(f"leg {args.leg!r} needs hf_pin.repo + hf_pin.commit (R85: the enforceable pin)")
    dtype = (leg.get("quantizations") or ["bfloat16"])[0]
    enable_thinking = bool((leg.get("reasoning") or {}).get("enabled", False))

    import os
    api_key = os.environ.get(str(leg.get("api_key_env", "VLLM_API_KEY")))
    served_name = str(leg["model"])

    cmd = build_serve_command(repo, commit, dtype, served_name, args.port,
                              enable_thinking=enable_thinking, api_key=api_key)
    manifest = build_manifest(repo, commit, dtype, served_name, args.port,
                              enable_thinking=enable_thinking, versions=_versions())
    manifest_path = Path(args.manifest) if args.manifest else Path(f"served-manifest-{args.leg}.json")
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[serve_qwen_selfhost] manifest -> {manifest_path}", file=sys.stderr)
    print(f"[serve_qwen_selfhost] command : {' '.join(cmd)}", file=sys.stderr)
    if args.dry_run:
        return 0
    return subprocess.call(cmd)  # pragma: no cover (GPU-node launch)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
