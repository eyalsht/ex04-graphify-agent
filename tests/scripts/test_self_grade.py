"""scripts/self_grade.py thin-runner exit codes (PHASE8-027/028; keyless, mocked)."""

from __future__ import annotations

import self_grade as script
from ex04_graphify_agent.self_grade import CheckResult, GradeReport


def _report(passed: bool) -> GradeReport:
    return GradeReport((CheckResult("x", passed),), 90.0)


def test_main_exits_zero_when_report_passes(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(script.Ex04Sdk, "self_grade", lambda self: _report(True))
    assert script.main([]) == 0


def test_main_exits_one_when_report_fails(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(script.Ex04Sdk, "self_grade", lambda self: _report(False))
    assert script.main([]) == 1
