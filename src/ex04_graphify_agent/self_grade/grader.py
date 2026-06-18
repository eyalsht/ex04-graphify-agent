"""Assemble the self-grade: structural checks + reused gate scripts + rubric number."""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from . import checks
from .config import load_config, repo_root
from .models import CheckResult, GradeReport

GateRunner = Callable[[Sequence[str]], tuple[bool, str]]


def compute_grade(rubric: list[dict[str, Any]]) -> float:
    """Scale the per-area rubric (summing to 72/80) to a /100 grade => 90.0."""
    earned = sum(float(row["score"]) for row in rubric)
    possible = sum(float(row["max"]) for row in rubric)
    return round(100.0 * earned / possible, 1) if possible else 0.0


def subprocess_runner(root: Path) -> GateRunner:
    """Default gate runner — invokes a command at ``root`` and reports pass/last-line."""

    def run(cmd: Sequence[str]) -> tuple[bool, str]:
        proc = subprocess.run(list(cmd), cwd=root, capture_output=True, text=True, check=False)
        tail = (proc.stdout + proc.stderr).strip().splitlines()
        return proc.returncode == 0, tail[-1] if tail else ""

    return run


def grade(root: Path | None = None, gate_runner: GateRunner | None = None) -> GradeReport:
    """Run structural checks + config-driven gates and emit the rubric grade (R8.9)."""
    base = root if root is not None else repo_root()
    cfg = load_config(base)
    number = compute_grade(cfg["rubric"])
    results: list[CheckResult] = [
        checks.requirement_coverage(base, cfg),
        checks.hot_md_consistent(base, cfg),
        checks.baselines_unmodified(base, cfg),
        checks.token_trace(base, cfg),
        checks.grade_documented(base, number),
    ]
    runner = gate_runner if gate_runner is not None else subprocess_runner(base)
    for name, cmd in cfg["gates"].items():
        ok, detail = runner(cmd)
        results.append(CheckResult(f"gate:{name}", ok, detail))
    return GradeReport(tuple(results), number)
