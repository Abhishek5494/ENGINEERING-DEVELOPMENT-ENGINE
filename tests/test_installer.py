"""Tests for src.pem.installer (T-0107).

All tests use injected runners/probes and injected system data: no test
touches the network, installs anything, or reads real disk state.
"""

from __future__ import annotations

import sys

from src.pem.installer import (
    EXIT_FAILURE,
    EXIT_OK,
    EXIT_REFUSED,
    apply_installs,
    expand_command,
    low_disk_volumes,
    plan_installs,
)
from src.pem.report import LOW_DISK_THRESHOLD_BYTES

COMMAND = "{python} -m pip install example"


def _entry(tool_id, *, command=COMMAND, required="optional", min_version=None):
    return {
        "id": tool_id,
        "tool": tool_id,
        "required": required,
        "purpose": f"{tool_id} purpose",
        "installation_method": f"{tool_id} method",
        "install_command": command,
        "min_version": min_version,
    }


def _record(tool_id, state, version="UNKNOWN", reason="probe reason"):
    return {
        "id": tool_id,
        "state": state,
        "version": version,
        "evidence": "OBSERVED",
        "reason": reason,
        "min_version": None,
    }


class _Runner:
    def __init__(self, returncode=0, output="ok"):
        self.calls = []
        self.returncode = returncode
        self.output = output

    def __call__(self, argv):
        self.calls.append(argv)
        return self.returncode, self.output


class _Probe:
    def __init__(self, records):
        self.records = records
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return self.records


def _disk_system(free_bytes):
    return {
        "storage": {
            "value": [{"mount": "D:\\", "free_bytes": free_bytes}],
            "evidence": "OBSERVED",
        }
    }


def test_expand_command_substitutes_python_as_single_token():
    argv = expand_command("{python} -m pip install jupyter")
    assert argv[0] == sys.executable
    assert argv[1:] == ["-m", "pip", "install", "jupyter"]


def test_expand_command_preserves_plain_command():
    assert expand_command("custom-setup --yes") == ["custom-setup", "--yes"]


def test_plan_classifies_every_state():
    entries = [
        _entry("missing"),
        _entry("known"),
        _entry("old", min_version="2.0"),
        _entry("current", min_version="2.0"),
        _entry("unknown"),
    ]
    records = [
        _record("missing", "NOT_FOUND"),
        _record("known", "DETECTED", "1.0"),
        _record("old", "DETECTED", "1.5"),
        _record("current", "DETECTED", "2.3"),
        _record("unknown", "UNKNOWN"),
    ]
    actions = {row["id"]: row["action"] for row in plan_installs(entries, records)}
    assert actions == {
        "missing": "install",
        "known": "skip",
        "old": "upgrade",
        "current": "skip",
        "unknown": "investigate",
    }


def test_plan_marks_missing_command_as_manual():
    rows = plan_installs(
        [_entry("tool", command=None)], [_record("tool", "NOT_FOUND")]
    )
    assert rows[0]["action"] == "manual"


def test_plan_investigates_absent_record():
    rows = plan_installs([_entry("tool")], [])
    assert rows[0]["action"] == "investigate"
    assert rows[0]["state"] == "NO_RECORD"


def test_healthy_tool_performs_zero_actions():
    entry = _entry("known")
    record = _record("known", "DETECTED", "1.0")
    runner = _Runner()
    outcome = apply_installs(
        [entry],
        [record],
        runner=runner,
        system=_disk_system(LOW_DISK_THRESHOLD_BYTES * 2),
        probe=_Probe([record]),
    )
    assert outcome.exit_code == EXIT_OK
    assert runner.calls == []
    assert outcome.skipped == ["known"]
    assert outcome.executed == []


def test_not_found_tool_is_installed_once_and_reprobed():
    entry = _entry("missing")
    fresh = _record("missing", "DETECTED", "3.1")
    runner = _Runner(returncode=0)
    outcome = apply_installs(
        [entry],
        [_record("missing", "NOT_FOUND")],
        runner=runner,
        system=_disk_system(LOW_DISK_THRESHOLD_BYTES * 2),
        probe=_Probe([fresh]),
    )
    assert runner.calls == [expand_command(COMMAND)]
    assert outcome.exit_code == EXIT_OK
    assert len(outcome.executed) == 1
    assert outcome.executed[0]["result_state"] == "DETECTED"
    assert outcome.executed[0]["result_version"] == "3.1"


def test_second_run_against_healthy_records_does_nothing():
    entry = _entry("missing")
    runner = _Runner()
    outcome = apply_installs(
        [entry],
        [_record("missing", "DETECTED", "3.1")],
        runner=runner,
        system=_disk_system(LOW_DISK_THRESHOLD_BYTES * 2),
        probe=_Probe([]),
    )
    assert runner.calls == []
    assert outcome.exit_code == EXIT_OK


def test_unknown_tool_is_never_acted_on():
    entry = _entry("unknown")
    runner = _Runner()
    outcome = apply_installs(
        [entry],
        [_record("unknown", "UNKNOWN", reason="probe timed out")],
        runner=runner,
        system=_disk_system(LOW_DISK_THRESHOLD_BYTES * 2),
        probe=_Probe([]),
    )
    assert runner.calls == []
    assert outcome.investigated == ["unknown"]
    assert outcome.exit_code == EXIT_OK
    assert any("NOT ACTED" in line and "inconclusive" in line for line in outcome.lines)


def test_absent_record_is_never_acted_on():
    runner = _Runner()
    outcome = apply_installs(
        [_entry("tool")],
        [],
        runner=runner,
        system=_disk_system(LOW_DISK_THRESHOLD_BYTES * 2),
        probe=_Probe([]),
    )
    assert runner.calls == []
    assert outcome.investigated == ["tool"]


def test_below_minimum_tool_is_upgraded():
    entry = _entry("old", min_version="2.0")
    fresh = _record("old", "DETECTED", "2.1")
    runner = _Runner(returncode=0)
    outcome = apply_installs(
        [entry],
        [_record("old", "DETECTED", "1.5")],
        runner=runner,
        system=_disk_system(LOW_DISK_THRESHOLD_BYTES * 2),
        probe=_Probe([fresh]),
    )
    assert runner.calls == [expand_command(COMMAND)]
    assert outcome.executed[0]["action"] == "upgrade"
    assert outcome.exit_code == EXIT_OK


def test_no_command_means_manual_and_zero_calls():
    entry = _entry("manual", command=None)
    runner = _Runner()
    outcome = apply_installs(
        [entry],
        [_record("manual", "NOT_FOUND")],
        runner=runner,
        system=_disk_system(LOW_DISK_THRESHOLD_BYTES * 2),
        probe=_Probe([]),
    )
    assert runner.calls == []
    assert outcome.manual == ["manual"]
    assert outcome.exit_code == EXIT_OK


def test_low_disk_refuses_without_running_anything():
    entry = _entry("missing")
    runner = _Runner()
    outcome = apply_installs(
        [entry],
        [_record("missing", "NOT_FOUND")],
        runner=runner,
        system=_disk_system(LOW_DISK_THRESHOLD_BYTES - 1),
        probe=_Probe([]),
    )
    assert outcome.exit_code == EXIT_REFUSED
    assert outcome.refused is True
    assert runner.calls == []
    assert outcome.executed == []
    assert any("REFUSED" in line and "No action performed" in line for line in outcome.lines)


def test_unobserved_storage_does_not_block():
    entry = _entry("missing")
    runner = _Runner()
    outcome = apply_installs(
        [entry],
        [_record("missing", "NOT_FOUND")],
        runner=runner,
        system={"storage": {"value": [], "evidence": "UNKNOWN"}},
        probe=_Probe([_record("missing", "DETECTED", "1.0")]),
    )
    assert outcome.exit_code == EXIT_OK
    assert runner.calls != []


def test_failed_command_is_not_reported_as_installed():
    entry = _entry("missing")
    runner = _Runner(returncode=1, output="pip: error")
    outcome = apply_installs(
        [entry],
        [_record("missing", "NOT_FOUND")],
        runner=runner,
        system=_disk_system(LOW_DISK_THRESHOLD_BYTES * 2),
        probe=_Probe([_record("missing", "NOT_FOUND")]),
    )
    assert outcome.exit_code == EXIT_FAILURE
    assert any("FAILED" in line and "Not treated as installed" in line for line in outcome.lines)


def test_success_exit_but_probe_still_missing_is_failure():
    entry = _entry("missing")
    runner = _Runner(returncode=0)
    outcome = apply_installs(
        [entry],
        [_record("missing", "NOT_FOUND")],
        runner=runner,
        system=_disk_system(LOW_DISK_THRESHOLD_BYTES * 2),
        probe=_Probe([_record("missing", "NOT_FOUND")]),
    )
    assert outcome.exit_code == EXIT_FAILURE


def test_low_disk_volumes_only_reports_observed():
    assert low_disk_volumes({"storage": {"value": [], "evidence": "UNKNOWN"}}) == []
    observed = low_disk_volumes(_disk_system(LOW_DISK_THRESHOLD_BYTES - 1))
    assert observed == [("D:\\", LOW_DISK_THRESHOLD_BYTES - 1)]