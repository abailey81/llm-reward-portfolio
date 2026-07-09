"""Cluster adapter unit tests (§12.4 B-A1): spec batches, the §14.6 jobscript, run_one routing.

No network, no GPU, no Myriad: run_one's heavy calls are monkeypatched (the real end-to-end is
the G1 on-cluster dry-run acceptance); everything else is exercised for real.
"""
from __future__ import annotations

import json

import pytest

from src.cluster.jobscript import render_jobscript
from src.cluster.spec_io import payload_sha, read_spec, write_specs

SPEC = {"arm": "distributional", "reward_kind": "source", "reward": "def reward(...): ...",
        "candidate_id": "distributional-g0-c0", "archive_root": "/scratch/out", "seed": 0}


def test_spec_roundtrip_and_index(tmp_path):
    n = write_specs([SPEC, [SPEC, {**SPEC, "seed": 1}]], tmp_path)  # single + a pack
    assert n == 2
    loaded = read_spec(tmp_path / "task_1.json")
    assert loaded == SPEC
    pack = read_spec(tmp_path / "task_2.json")
    assert isinstance(pack, list) and pack[1]["seed"] == 1
    index = json.loads((tmp_path / "index.json").read_text())
    assert index["1"] == payload_sha(SPEC)


def test_write_specs_rejects_non_json_serializable_specs(tmp_path):
    """A non-JSON-native field (would be silently str-coerced by default=str AND pass the sha check,
    since payload_sha coerces too) must FAIL LOUD at write time instead of mis-training on the node."""
    import numpy as np

    bad = {"candidate_id": "c0", "arm": "x", "weird": np.int64(5)}  # numpy scalar smuggled in
    with pytest.raises(TypeError, match="not cleanly JSON-serializable"):
        write_specs([bad], tmp_path / "bad")
    # a clean spec (all native types) still writes + round-trips
    ok = {"candidate_id": "c0", "arm": "x", "seed": 5, "window": [0, 100]}
    write_specs([ok], tmp_path / "ok")
    assert read_spec(tmp_path / "ok" / "task_1.json") == ok


def test_spec_sha_mismatch_fails_loud(tmp_path):
    write_specs([SPEC], tmp_path)
    p = tmp_path / "task_1.json"
    tampered = dict(SPEC, seed=999)
    p.write_text(json.dumps(tampered, indent=1, sort_keys=True), encoding="utf-8")
    with pytest.raises(ValueError, match="sha MISMATCH"):
        read_spec(p)


def test_jobscript_encodes_every_researched_rule():
    js = render_jobscript("s1_search", 630, "/home/u/Scratch/llmrp",
                          "/acfs/users/u/llmrp-inputs", pool="EF", tc=38,
                          priority=-100, hold_jid="marker_1", pack=3)
    for needle in ("#!/bin/bash -l", "-l gpu=1", "-pe smp 12", "-l mem=4G", "-l tmpfs=15G",
                   "-l h_rt=1:30:0", "-ac allow=EF", "#$ -r y", "#$ -p -100",
                   "-t 1-630 -tc 38", "#$ -hold_jid marker_1", "umask 077",
                   'if cp "/acfs/users/u/llmrp-inputs"/*.parquet "$TMPDIR/gold/"',
                   'export LLM_RP_GOLD_STAGED_DIR="$TMPDIR/gold"',
                   'export LLM_RP_GOLD_STAGED_DIR="/acfs/users/u/llmrp-inputs"',
                   'export PYTHONPATH="~/llmrp:',  # BUG-4: `src` importable (repo != -wd)
                   "--pack 3", "epilogue.jsonl"):
        assert needle in js, f"missing: {needle}"


def test_jobscript_pack1_defaults_and_priority_guard():
    js = render_jobscript("t", 10, "/r", "/inputs")
    assert "-pe smp 4" in js and "-l h_rt=3:0:0" in js and "#$ -p 0" in js
    with pytest.raises(ValueError, match="<= 0"):
        render_jobscript("t", 1, "/r", "/p", priority=5)


def test_write_jobscript_forces_lf_endings(tmp_path):
    """V11 regression: the driver runs on Windows — a platform-translated CRLF shebang
    (``#!/bin/bash -l\\r``) makes qsub/exec fail on the cluster. Bytes must be LF-pure."""
    from src.cluster.jobscript import write_jobscript

    js = render_jobscript("t", 2, "/r", "/inputs")
    p = write_jobscript(js, tmp_path / "sub" / "t.sh")
    raw = p.read_bytes()
    assert b"\r" not in raw and raw.startswith(b"#!/bin/bash -l\n")


def test_epilogue_line_produces_valid_json_under_real_bash(tmp_path):
    """Execute the template's trickiest escaping — the epilogue echo — under a REAL bash and
    parse the result as JSON (what the torn-line-tolerant ledger reader will ingest)."""
    import shutil
    import subprocess

    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("no bash on this host")
    js = render_jobscript("t", 2, "/r", "/inputs")
    echo_line = next(ln for ln in js.splitlines() if ln.startswith("echo "))
    ledger = tmp_path / "t.epilogue.jsonl"
    script = (
        "SGE_TASK_ID=7\nRC=0\nGPUINFO='Tesla V100-SXM2-16GB, 525.105'\n"
        + echo_line.replace('"/r/ledger/t.epilogue.jsonl"', f'"{ledger.as_posix()}"')
    )
    try:
        r = subprocess.run([bash, "-c", script], capture_output=True, text=True, timeout=30)
    except OSError:
        pytest.skip("bash present but not runnable")
    assert r.returncode == 0, r.stderr
    row = json.loads(ledger.read_text().strip())
    assert row["task"] == 7 and row["rc"] == 0 and "V100" in row["gpu"]


def test_run_one_routing_and_exit_semantics(monkeypatch, tmp_path):
    import src.cluster.run_one as ro

    calls: list[str] = []
    archived: list[str] = []

    def fake_train(spec):
        calls.append(spec["candidate_id"])
        return {"ok": spec["seed"] != 13, "candidate_id": spec["candidate_id"]}

    import src.orchestration.parallel as par
    monkeypatch.setattr(par, "train_candidate", fake_train)
    monkeypatch.setattr(par, "_archive", lambda r, arm, opts, root, gen=0: archived.append(r["candidate_id"]))

    # single spec, ok -> archived, exit 0
    write_specs([SPEC], tmp_path)
    assert ro.main(["--spec", str(tmp_path / "task_1.json")]) == 0
    assert archived == [SPEC["candidate_id"]]

    # single spec, failing seed -> NOT archived, exit 1
    write_specs([{**SPEC, "seed": 13, "candidate_id": "bad-c0"}], tmp_path / "b2")
    assert ro.main(["--spec", str(tmp_path / "b2" / "task_1.json")]) == 1
    assert "bad-c0" not in archived


def test_run_one_routes_the_test_leg_to_the_sealed_worker_with_node_env_fp(monkeypatch, tmp_path):
    """A leg=='test' spec routes to _test_seed_worker (NOT train_candidate), archives via write_run,
    and OVERRIDES the record's env_fingerprint with a NODE-captured one (S6 homogeneity parity)."""
    import src.cluster.run_one as ro
    import src.orchestration.parallel as par
    import src.orchestration.test_leg as tl

    written: list[dict] = []
    monkeypatch.setattr(tl, "_test_seed_worker",
                        lambda spec: {"ok": True, "run_id": spec["run_id"], "arm": spec["arm"],
                                      "record": {"run_id": spec["run_id"], "arm": spec["arm"],
                                                 "seed": spec["seed"], "env_fingerprint": "DRIVER-fp"}})
    monkeypatch.setattr(par, "_run_env_fp", lambda root, rid, opts: "NODE-fp")
    monkeypatch.setattr("src.io.results.write_run", lambda rec, root: written.append(rec))
    # train_candidate must NOT be called for a test leg
    monkeypatch.setattr(par, "train_candidate",
                        lambda spec: (_ for _ in ()).throw(AssertionError("search worker on a test leg")))

    test_spec = {"leg": "test", "run_id": "distributional-s0", "arm": "distributional", "seed": 0,
                 "archive_root": str(tmp_path / "out")}
    write_specs([test_spec], tmp_path / "t")
    assert ro.main(["--spec", str(tmp_path / "t" / "task_1.json")]) == 0
    assert len(written) == 1 and written[0]["run_id"] == "distributional-s0"
    assert written[0]["env_fingerprint"] == "NODE-fp"  # driver label overridden by the node capture
