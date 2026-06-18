"""self_grade — keyless self-assessment (R8.9): structural checks + gates + rubric grade."""

from __future__ import annotations

from .grader import GateRunner, compute_grade, grade
from .models import CheckResult, GradeReport

__all__ = ["CheckResult", "GateRunner", "GradeReport", "compute_grade", "grade"]
