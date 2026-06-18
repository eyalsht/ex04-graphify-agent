"""SDK façade delegates to self_grade (PHASE8-042; SDK-first non-negotiable)."""

from __future__ import annotations

from collections.abc import Sequence

from ex04_graphify_agent.sdk import Ex04Sdk
from ex04_graphify_agent.self_grade import GradeReport


def _all_pass(_cmd: Sequence[str]) -> tuple[bool, str]:
    return True, "ok"


def test_sdk_self_grade_returns_passing_report() -> None:
    report = Ex04Sdk().self_grade(gate_runner=_all_pass)
    assert isinstance(report, GradeReport)
    assert report.passed is True
    assert report.grade == 90.0
