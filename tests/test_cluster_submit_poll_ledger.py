"""submit/poll/ledger layer tests — fake runners and synthetic archives; zero network."""
from __future__ import annotations

import json

import pytest

from src.cluster.ledger import failures, parse_qacct, read_epilogue, requeue_specs
from src.cluster.poll import completed_run_ids, pending_specs, spec_run_id
from src.cluster.submit import parse_job_id, qsub, submit_marker


def test_parse_job_id_array_and_plain_and_garbage():
    assert parse_job_id("Your job-array 4211375.1-630:1 (\"s1\") has been submitted") == "4211375"
    assert parse_job_id("Your job 99 (\"m\") has been submitted") == "99"
    with pytest.raises(RuntimeError, match="could not parse"):
        parse_job_id("qsub: error")


def test_qsub_and_marker_use_the_runner_and_hold_chain():
    sent: list[list[str]] = []

    def fake_runner(cmd):
        sent.append(cmd)
        return "Your job-array 777.1-10:1 submitted" if "qsub" in cmd else "Your job 778 ok"

    assert qsub("/remote/s1.sh", fake_runner) == "777"
    mid = submit_marker("m_s1", "777", "/remote", fake_runner)
    assert mid == "777" or mid == "778"  # id parsed from whatever the runner returned
    joined = " ".join(sent[-1])
    assert "-hold_jid 777" in joined and "h_rt=0:5:0" in joined


def test_poll_completed_and_compacted_resume(tmp_path):
    # synthetic archive: two committed records
    for rid in ("distributional-g0-c0", "scalar-s5"):
        d = tmp_path / "search" / rid
        d.mkdir(parents=True)
        (d / "record.json").write_text("{}")
    specs = [
        {"candidate_id": "distributional-g0-c0"},   # done
        {"run_id": "scalar-s5"},                    # done
        {"candidate_id": "distributional-g0-c1"},   # missing
    ]
    assert completed_run_ids(tmp_path) == {"distributional-g0-c0", "scalar-s5"}
    pend = pending_specs(specs, tmp_path)
    assert [spec_run_id(s) for s in pend] == ["distributional-g0-c1"]
    with pytest.raises(KeyError):
        spec_run_id({"arm": "x"})


QACCT = """==============================================================
jobnumber    777
taskid       3
exit_status  1
failed       0
maxvmem      3.1G
==============================================================
jobnumber    777
taskid       4
exit_status  0
failed       0
"""


def test_qacct_parse_failures_and_bounded_requeue(tmp_path):
    rows = parse_qacct(QACCT)
    assert len(rows) == 2
    bad = failures(rows)
    assert len(bad) == 1 and bad[0]["taskid"] == "3"

    specs = {3: {"candidate_id": "c3"}}
    ledger = tmp_path / "perm.jsonl"
    r1 = requeue_specs([3], specs, ledger)          # retry 1
    r2 = requeue_specs([3], {3: r1[0]}, ledger)     # retry 2
    r3 = requeue_specs([3], {3: r2[0]}, ledger)     # exhausted -> permanent ledger
    assert r1 and r2 and r3 == []
    perm = [json.loads(x) for x in ledger.read_text().splitlines()]
    assert perm[0]["reason"] == "retries_exhausted"


def test_marker_script_is_real_multiline_printf_not_echo():
    """V2 regression: echo '\\n' does NOT expand in POSIX sh — the marker must be printf-built
    so every #$ directive lands on its own line (else hold/h_rt are dead comments)."""
    sent: list[list[str]] = []

    def fake_runner(cmd):
        sent.append(cmd)
        return "Your job 5 ok"

    from src.cluster.submit import submit_marker
    submit_marker("m_ok", "42", "/r", fake_runner)
    script = " ".join(sent[-1])
    assert "printf '%s\\n'" in script and "'#$ -hold_jid 42'" in script and "echo" not in script
    with pytest.raises(ValueError, match="numeric"):
        submit_marker("m_ok", "42; rm -rf /", "/r", fake_runner)
    with pytest.raises(ValueError, match="invalid SGE job name"):
        submit_marker("bad name!", "42", "/r", fake_runner)


def test_prepare_remote_creates_log_dirs_before_qsub():
    """V4 regression: Grid Engine must be able to open the -o path at job START. V9: outputs/
    is pre-created too, so the first pull's remote find cleanly reads '0 completed'."""
    sent: list[list[str]] = []
    from src.cluster.submit import prepare_remote
    prepare_remote("/home/u/Scratch/llmrp", ["s1_search"], lambda c: sent.append(c) or "")
    assert sent[0][0] == "mkdir" and any("logs/s1_search" in a for a in sent[0])
    assert any(a.endswith("/outputs") for a in sent[0])


def test_spec_missing_index_fails_closed(tmp_path):
    """V6 regression: an index-less batch (partial rsync) must refuse to run, not run unverified."""
    import json as _json
    from src.cluster.spec_io import read_spec
    p = tmp_path / "task_1.json"
    p.write_text(_json.dumps({"candidate_id": "c0"}), encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="index missing"):
        read_spec(p)


def test_write_specs_requires_resume_identity(tmp_path):
    """V6 regression: identity-at-write — a spec without run_id/candidate_id cannot be resumed."""
    from src.cluster.spec_io import write_specs
    with pytest.raises(ValueError, match="resume identity"):
        write_specs([{"arm": "scalar"}], tmp_path)
    with pytest.raises(ValueError, match="resume identity"):
        write_specs([[{"candidate_id": "ok"}, {"arm": "no-id"}]], tmp_path / "b2")


def test_jobscript_apptainer_launcher_is_on_the_run_line():
    """V3 regression: containerized jobs must actually LAUNCH through apptainer.
    G1 regression (2026-07-10, caught against the live cluster): the container image is BARE
    python — the run line must call the VENV interpreter through the container, and $TMPDIR
    (NOT auto-bound by apptainer) plus the gold dir must be explicitly --bind mounted, or the
    staged-gold env var points at a path that does not exist inside the container."""
    from src.cluster.jobscript import render_jobscript
    js = render_jobscript("t2", 5, "/r", "/inputs", apptainer_sif="~/llmrp.sif")
    assert (
        'apptainer exec --nv --bind "$TMPDIR,/inputs" ~/llmrp.sif '
        "~/venvs/llmrp/bin/python -m src.cluster.run_one" in js
    )
    # the bare container python must never be the interpreter
    assert "llmrp.sif python -m" not in js
    assert "source ~/venvs" not in js


def test_epilogue_reader_tolerates_torn_lines(tmp_path):
    p = tmp_path / "a.epilogue.jsonl"
    p.write_text('{"task":1,"rc":0}\n{"task":2,"rc"\n{"task":3,"rc":1}\n')
    rows = read_epilogue(p)
    assert [r["task"] for r in rows] == [1, 3]


# ---------------------------------------------------------------------------
# V9/V10 deep-dive regressions: no rsync on the driver host + remote requoting
# ---------------------------------------------------------------------------


def test_ssh_runner_requotes_for_the_remote_shell(monkeypatch):
    """V10 regression: ssh space-joins its argv and the REMOTE shell re-splits it — the runner
    must POSIX-quote every word so the remote side reconstructs EXACTLY our argv (round-trip)."""
    import shlex as _sh

    captured: dict[str, list[str]] = {}

    def fake_run(argv, **kw):
        captured["argv"] = argv

        class R:
            stdout = "ok"

        return R()

    monkeypatch.setattr("src.cluster.submit.subprocess.run", fake_run)
    from src.cluster.submit import ssh_runner

    cmd = ["bash", "-c", "printf '%s\\n' 'a b' > /r/m.sh && qsub /r/m.sh"]
    assert ssh_runner("h")(cmd) == "ok"
    argv = captured["argv"]
    # hardened prefix (BatchMode/accept-new) then the host then the single remote payload word
    assert argv[0] == "ssh" and argv[-2] == "h"
    assert "BatchMode=yes" in argv and "StrictHostKeyChecking=accept-new" in argv
    assert _sh.split(argv[-1]) == cmd  # the property that matters: exact argv reconstruction


def test_push_batch_is_tar_over_ssh_not_rsync(tmp_path, monkeypatch):
    """V9 regression: the Windows driver host has NO rsync (only scp/ssh) — push must stream a
    tar pipe with a POSIX-quoted remote side, and validate the batch dir + name first."""
    import io
    import shlex as _sh

    calls: dict[str, object] = {}

    class _FakeTar:
        def __init__(self):
            self.stdout = io.BytesIO(b"TARBYTES")
            self.returncode = 0

        def wait(self, timeout=None):
            return 0

    def fake_popen(argv, stdout=None, cwd=None):
        calls["tar"] = (argv, cwd)
        return _FakeTar()

    def fake_run(argv, stdin=None, check=None, timeout=None):
        calls["ssh"] = argv

    monkeypatch.setattr("src.cluster.submit.subprocess.Popen", fake_popen)
    monkeypatch.setattr("src.cluster.submit.subprocess.run", fake_run)
    from src.cluster.submit import push_batch

    batch = tmp_path / "s1_search"
    batch.mkdir()
    (batch / "task_1.json").write_text("{}")
    root = "/home/u/Scratch/llm rp/specs"  # a space — exercises the quoting
    push_batch(batch, root + "/")

    tar_argv, tar_cwd = calls["tar"]
    assert tar_argv == ["tar", "-cf", "-", "s1_search"] and tar_cwd == str(tmp_path)
    ssh_argv = calls["ssh"]
    assert ssh_argv[0] == "ssh" and "myriad" in ssh_argv and "rsync" not in " ".join(ssh_argv)
    assert "BatchMode=yes" in ssh_argv  # driver hang-guard present
    q = _sh.quote(root)
    assert f"mkdir -p {q}" in ssh_argv[-1] and f"tar -xf - -C {q}" in ssh_argv[-1]

    with pytest.raises(FileNotFoundError):
        push_batch(tmp_path / "nope", root)
    bad = tmp_path / "bad name!"
    bad.mkdir()
    with pytest.raises(ValueError, match="invalid SGE job name"):
        push_batch(bad, root)


def _fake_find_runner(root: str, rels: list[str]):
    """A runner whose only supported call is the pull's find — returns one line per record."""

    def _run(cmd):
        assert cmd[0] == "find" and cmd[1] == root
        return "\n".join(f"{root}/{r}/record.json" for r in rels) + "\n"

    return _run


def _writing_fetch(payload_note: str = "x", *, omit_record: set[str] = frozenset()):
    """A fetch that materializes the requested dirs in staging (record.json + one sibling)."""
    fetched_batches: list[list[str]] = []

    def _fetch(relpaths, staging):
        fetched_batches.append(list(relpaths))
        for rel in relpaths:
            d = staging / rel
            d.mkdir(parents=True, exist_ok=True)
            (d / "returns.parquet").write_text(payload_note)
            if rel not in omit_record:
                (d / "record.json").write_text("{}")

    _fetch.batches = fetched_batches  # type: ignore[attr-defined]
    return _fetch


def test_pull_archive_exact_incremental_staged_and_chunked(tmp_path):
    """V9: pull = remote-vs-local run-dir DIFF (immutable records ⇒ exact), staged whole-dirs-
    only arrival, chunked argv, staging swept afterwards."""
    from src.cluster.poll import pull_archive

    rels = ["search/c0", "search/c1", "test/s1"]
    runner = _fake_find_runner("/r/out", rels)
    # the mirror already holds search/c0 — it must NOT be re-fetched
    pre = tmp_path / "search" / "c0"
    pre.mkdir(parents=True)
    (pre / "record.json").write_text("{}")

    fetch = _writing_fetch()
    n = pull_archive("/r/out", tmp_path, runner=runner, fetch=fetch, chunk=1)
    assert n == 2
    assert fetch.batches == [["search/c1"], ["test/s1"]]  # chunk=1 → one dir per pipe
    assert (tmp_path / "search" / "c1" / "record.json").is_file()
    assert (tmp_path / "test" / "s1" / "returns.parquet").is_file()
    assert not (tmp_path / ".pull_tmp").exists()
    # idempotent second pull: nothing missing, no fetch
    n2 = pull_archive("/r/out", tmp_path, runner=runner, fetch=_writing_fetch())
    assert n2 == 0


def test_pull_archive_torn_dir_fails_loud_and_stale_staging_never_counts(tmp_path):
    """V9: (a) a dir arriving without record.json (torn tar) raises and never enters the
    mirror; (b) a PREVIOUS pull's staging leftovers are swept — neither trusted as complete
    nor counted by completed_run_ids."""
    from src.cluster.poll import completed_run_ids, pull_archive

    # stale staging from a killed pull: contains a record.json — must be ignored + swept
    stale = tmp_path / ".pull_tmp" / "search" / "c9"
    stale.mkdir(parents=True)
    (stale / "record.json").write_text("{}")
    assert completed_run_ids(tmp_path) == set()  # staging is not the mirror

    runner = _fake_find_runner("/r/out", ["search/c9"])
    fetch = _writing_fetch()
    assert pull_archive("/r/out", tmp_path, runner=runner, fetch=fetch) == 1
    assert (tmp_path / "search" / "c9" / "record.json").is_file()  # re-fetched fresh

    # torn transfer: record.json missing in staging → loud failure, mirror untouched
    runner2 = _fake_find_runner("/r/out", ["search/c9", "test/s2"])
    torn = _writing_fetch(omit_record={"test/s2"})
    with pytest.raises(RuntimeError, match="without record.json"):
        pull_archive("/r/out", tmp_path, runner=runner2, fetch=torn)
    assert not (tmp_path / "test" / "s2").exists()


def test_remote_completed_dirs_parses_skips_and_fails_loud():
    from src.cluster.poll import remote_completed_dirs

    out = (
        "/r/out/search/c0/record.json\n"
        "/r/out/record.json\n"            # stray root-level file → skipped
        "/r/out/test/s1/other.txt\n"      # not a record → skipped
        "\n"
    )
    got = remote_completed_dirs("/r/out/", lambda cmd: out)
    assert got == {"search/c0"}

    def failing(cmd):
        import subprocess as sp

        raise sp.CalledProcessError(1, cmd)

    with pytest.raises(RuntimeError, match="wrong outputs root"):
        remote_completed_dirs("/r/out", failing)
