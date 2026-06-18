"""Grade assembly (PHASE8-027/030/031..040): rubric number + gates via injected runner."""

from __future__ import annotations

import sys
from collections.abc import Sequence

from ex04_graphify_agent.self_grade import GradeReport, compute_grade, grade
from ex04_graphify_agent.self_grade.config import load_config, repo_root
from ex04_graphify_agent.self_grade.grader import subprocess_runner


def _all_pass(_cmd: Sequence[str]) -> tuple[bool, str]:
    return True, "ok"


def test_compute_grade_is_ninety() -> None:
    rubric = load_config(repo_root())["rubric"]
    assert compute_grade(rubric) == 90.0


def test_compute_grade_zero_when_no_rubric() -> None:
    assert compute_grade([]) == 0.0


def test_grade_all_pass_yields_passing_report() -> None:
    report = grade(gate_runner=_all_pass)
    assert isinstance(report, GradeReport)
    assert report.grade == 90.0
    assert report.passed is True
    gate_checks = [c for c in report.checks if c.name.startswith("gate:")]
    assert len(gate_checks) == 6


def test_grade_fails_when_a_gate_fails() -> None:
    def one_gate_fails(cmd: Sequence[str]) -> tuple[bool, str]:
        return ("mypy" not in cmd), "boom"

    report = grade(gate_runner=one_gate_fails)
    assert report.passed is False
    assert report.grade == 90.0


def test_subprocess_runner_reports_exit_code() -> None:
    run = subprocess_runner(repo_root())
    ok, _ = run([sys.executable, "-c", "raise SystemExit(0)"])
    bad, _ = run([sys.executable, "-c", "raise SystemExit(1)"])
    assert ok is True
    assert bad is False


def test_report_render_shows_grade_and_status() -> None:
    report = grade(gate_runner=_all_pass)
    rendered = report.render()
    assert "90 / 100" in rendered
    assert "PASS" in rendered
