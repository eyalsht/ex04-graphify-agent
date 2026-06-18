"""Self-grade value objects: one check outcome and the assembled report."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CheckResult:
    """A single keyless gate/structural check and whether it held."""

    name: str
    passed: bool
    detail: str = ""


@dataclass(frozen=True)
class GradeReport:
    """The full self-assessment: per-check results plus the rubric number (R8.9)."""

    checks: tuple[CheckResult, ...]
    grade: float
    max_grade: float = 100.0

    @property
    def passed(self) -> bool:
        """True only if every check passed — the script's exit-0 condition."""
        return all(check.passed for check in self.checks)

    def render(self) -> str:
        """Human-readable report (printed by ``scripts/self_grade.py``)."""
        status = "PASS" if self.passed else "FAIL"
        lines = [f"EX04 self-grade: {self.grade:g} / {self.max_grade:g}  [{status}]", ""]
        for check in self.checks:
            mark = "PASS" if check.passed else "FAIL"
            suffix = f" — {check.detail}" if check.detail else ""
            lines.append(f"  [{mark}] {check.name}{suffix}")
        return "\n".join(lines)
