"""Tests for docs/ops/compute_ledger.py — the campaign wall-clock compute harvester.

The load-bearing property here is NOT "it parses". It is **it refuses to invent a number**. A
compute figure that silently reads zero because a format drifted would be reported in the
dissertation as a measurement, which is worse than reporting nothing. So the fail-loud contract gets
as much coverage as the happy path.

The happy-path fixture is REAL OUTPUT captured from Myriad on 2026-08-01, banner and all — including
ssh's post-quantum warning, which arrives interleaved on stdout in this environment and is exactly
the sort of thing that breaks a naive line-index parser.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

_MODULE_PATH = Path(__file__).resolve().parents[1] / "docs" / "ops" / "compute_ledger.py"
_spec = importlib.util.spec_from_file_location("compute_ledger", _MODULE_PATH)
cl = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(cl)


#: REAL qacct output, captured live 2026-08-01 (jobs started on/after 202607280000).
REAL_OUTPUT = """** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
OWNER       WALLCLOCK         UTIME         STIME           CPU             MEMORY                 IO                IOW
========================================================================================================================
ucestes      37012662 238003110.894    840381.266 241084998.677      341191339.051            699.392              0.000
"""


class TestParsing:
    def test_parses_the_real_captured_output(self):
        """POSITIVE CONTROL: the exact bytes the cluster returned must yield the exact numbers."""
        got = cl.parse_qacct_summary(REAL_OUTPUT)
        assert got["owner"] == "ucestes"
        assert got["wallclock"] == pytest.approx(37012662.0)
        assert got["cpu"] == pytest.approx(241084998.677)
        assert got["utime"] == pytest.approx(238003110.894)
        assert got["stime"] == pytest.approx(840381.266)

    def test_cpu_is_utime_plus_stime_within_rounding(self):
        """CROSS-CHECK by an independent route: the columns must be internally consistent.

        If a future format change shifted the columns, every individual value would still parse as a
        float and the error would be silent. This is the check that would catch it.
        """
        got = cl.parse_qacct_summary(REAL_OUTPUT)
        assert got["cpu"] == pytest.approx(got["utime"] + got["stime"], rel=0.02)

    def test_the_headline_figure_is_the_one_we_reported(self):
        """66,968 CPU-hours is destined for the PDF; pin it so a refactor cannot move it silently."""
        got = cl.parse_qacct_summary(REAL_OUTPUT)
        assert got["cpu"] / 3600.0 == pytest.approx(66968.0, abs=1.0)

    def test_ssh_banner_alone_does_not_parse_as_data(self):
        banner_only = "\n".join(REAL_OUTPUT.splitlines()[:3])
        with pytest.raises(cl.QacctParseError):
            cl.parse_qacct_summary(banner_only)

    def test_header_and_rule_lines_are_not_data(self):
        header_only = "\n".join(REAL_OUTPUT.splitlines()[3:5])
        with pytest.raises(cl.QacctParseError):
            cl.parse_qacct_summary(header_only)


class TestFailLoud:
    """The contract that matters: never default to zero."""

    @pytest.mark.parametrize("text", [
        "",
        "no jobs found",
        "error: invalid option -- 'b'",
        "OWNER WALLCLOCK\n=====\n",
    ])
    def test_raises_rather_than_returning_zero(self, text):
        with pytest.raises(cl.QacctParseError):
            cl.parse_qacct_summary(text)

    def test_error_message_names_what_it_saw(self):
        """A fail-loud error that does not say what arrived is not actionable."""
        with pytest.raises(cl.QacctParseError) as exc:
            cl.parse_qacct_summary("totally unexpected payload")
        assert "totally unexpected payload" in str(exc.value)

    def test_wrong_column_count_is_rejected_not_coerced(self):
        """A row with too few columns must NOT be padded into a plausible answer."""
        short_row = "OWNER WALLCLOCK CPU\n=====\nucestes 100 200\n"
        with pytest.raises(cl.QacctParseError):
            cl.parse_qacct_summary(short_row)


class TestSnapshotArithmetic:
    def test_mean_slots_per_task_matches_the_packing_we_requested(self):
        """6.51 cores/task on the campaign-window reading — a sanity check on the measurement.

        If this read ~1.0 the figure would be measuring single-slot tasks, i.e. not our campaign.
        (The 5.84 that appears in the 5-day sliding window is a DIFFERENT population — jobs started
        in the last 5 days rather than since launch — and the two must not be conflated.)
        """
        s = cl.ComputeSnapshot({"cpu_s": 241084998.677, "wallclock_s": 37012662.0})
        assert s.mean_slots_per_task == pytest.approx(6.51, abs=0.05)
        assert s.cpu_hours == pytest.approx(66968.0, abs=1.0)

    def test_mean_slots_is_division_safe(self):
        s = cl.ComputeSnapshot({"cpu_s": 5.0, "wallclock_s": 0.0})
        assert s.mean_slots_per_task == 0.0


class TestCommandConstruction:
    def test_uses_begin_not_days(self):
        """-d is a SLIDING window that would silently drop early campaign work as time passes."""
        cmd = cl.qacct_command()
        assert " -b " in cmd
        assert " -d " not in cmd

    def test_does_not_hardcode_an_identity(self):
        """$USER must expand ON THE CLUSTER, so no username is baked into the repo."""
        cmd = cl.qacct_command()
        assert "$USER" in cmd
        assert "ucestes" not in cmd

    def test_campaign_start_is_the_launch_day(self):
        assert cl.CAMPAIGN_START == "202607280000"


class TestLedgerIO:
    def test_read_ledger_missing_file_is_empty_not_an_error(self, tmp_path):
        assert cl.read_ledger(tmp_path / "nope.jsonl") == []

    def test_read_ledger_skips_malformed_lines_without_losing_good_ones(self, tmp_path):
        p = tmp_path / "l.jsonl"
        p.write_text('{"ts": "a", "cpu_s": 1}\nNOT JSON\n\n{"ts": "b", "cpu_s": 2}\n',
                     encoding="utf-8")
        rows = cl.read_ledger(p)
        assert [r["ts"] for r in rows] == ["a", "b"]

    def test_cadence_guard_declines_a_recent_snapshot(self, tmp_path, monkeypatch):
        from datetime import datetime, timezone
        p = tmp_path / "l.jsonl"
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        p.write_text(json.dumps({"ts": now, "cpu_s": 1.0}) + "\n", encoding="utf-8")

        def _boom(*a, **k):
            raise AssertionError("cadence guard failed to prevent a 72-second login-node query")
        monkeypatch.setattr(cl, "_run_remote", _boom)

        assert cl.snapshot(path=p) is None

    def test_force_overrides_the_cadence_guard_and_appends(self, tmp_path, monkeypatch):
        from datetime import datetime, timezone
        p = tmp_path / "l.jsonl"
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        p.write_text(json.dumps({"ts": now, "cpu_s": 1.0}) + "\n", encoding="utf-8")
        monkeypatch.setattr(cl, "_run_remote", lambda *a, **k: REAL_OUTPUT)

        snap = cl.snapshot(path=p, force=True)
        assert snap is not None
        rows = cl.read_ledger(p)
        assert len(rows) == 2
        assert rows[-1]["cpu_s"] == pytest.approx(241084998.677)

    def test_snapshot_records_its_own_scope_caveat(self, tmp_path, monkeypatch):
        """The superset caveat must travel WITH the number, not live only in a docstring."""
        monkeypatch.setattr(cl, "_run_remote", lambda *a, **k: REAL_OUTPUT)
        snap = cl.snapshot(path=tmp_path / "l.jsonl", force=True)
        assert "SUPERSET" in snap["scope_note"]

    def test_snapshot_records_the_command_for_provenance(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cl, "_run_remote", lambda *a, **k: REAL_OUTPUT)
        snap = cl.snapshot(path=tmp_path / "l.jsonl", force=True)
        assert snap["command"] == cl.qacct_command()

    def test_a_failed_query_appends_nothing(self, tmp_path, monkeypatch):
        """A partial or failed reading must not leave a phantom row behind."""
        p = tmp_path / "l.jsonl"
        monkeypatch.setattr(cl, "_run_remote", lambda *a, **k: "garbage")
        with pytest.raises(cl.QacctParseError):
            cl.snapshot(path=p, force=True)
        assert cl.read_ledger(p) == []
