"""render_report / write_report — reports/token_comparison.md (PHASE6-039..047, R5.6.5).

The markdown table is the mandated §5.6 evidence: tokens (a), ``Files read`` (b),
``Iterations`` (c), plus correctness + duration as "quality & speed to root cause" (d).
The narrative sections answer R4.1 (token reduction) and R4.2 (accuracy cost/gain).
"""

from __future__ import annotations

import json
from pathlib import Path

from ex04_graphify_agent.gatekeeper.config import repo_root
from ex04_graphify_agent.token_comparison.models import ComparisonResult, RunMetrics

_PATHS_CONFIG = "config/paths.json"
_REPORTS_DIR_KEY = "reports_dir"
_REPORT_FILENAME = "token_comparison.md"

_HEADER = (
    "| Run | Input tok | Output tok | Total | Files read | Iterations "
    "| # LLM calls | Duration (s) | Correctness | Notes |"
)
_SEPARATOR = "|---|---|---|---|---|---|---|---|---|---|"


def default_report_path() -> Path:
    """Resolve ``reports/token_comparison.md`` from ``config/paths.json`` (config-driven)."""
    root = repo_root()
    paths = json.loads((root / _PATHS_CONFIG).read_text(encoding="utf-8"))
    return root / str(paths[_REPORTS_DIR_KEY]) / _REPORT_FILENAME


def render_report(result: ComparisonResult) -> str:
    """Render the full markdown report: table + R4.1/R4.2 narrative sections."""
    lines = [
        "# Token Comparison - Graph-Guided vs Naive Baseline",
        "",
        _HEADER,
        _SEPARATOR,
        _row(result.graph_guided, "hot.md + polygons.py only"),
        _row(result.naive, "full data/broken-python/** dump"),
        "",
        "> **Columns `Files read` and `Iterations` are mandated by R5.6.5 (PDF §5.6)** - "
        "not optional. `Files read` = distinct files/textual units that entered the LLM "
        "context; `Iterations` = hypothesize->validate rounds. Together with `Duration` "
        'and `Correctness` they answer R5.6.5 (d) ("quality and speed of reaching root '
        'cause").',
        "",
        *_narrative(result),
    ]
    return "\n".join(lines) + "\n"


def write_report(result: ComparisonResult, path: str | Path | None = None) -> Path:
    """Render and write the report; default path is ``reports/token_comparison.md``."""
    out = Path(path) if path is not None else default_report_path()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_report(result), encoding="utf-8")
    return out


def _row(metrics: RunMetrics, notes: str) -> str:
    correctness = "pass" if metrics.correctness else "fail"
    return (
        f"| {metrics.run_type} | {metrics.input_tokens} | {metrics.output_tokens} "
        f"| {metrics.total_tokens} | {metrics.files_read} | {metrics.iterations} "
        f"| {metrics.num_llm_calls} | {metrics.duration_s:.2f} | {correctness} | {notes} |"
    )


def _narrative(result: ComparisonResult) -> list[str]:
    pct = result.input_token_reduction_pct
    pct_str = f"{pct:g}"
    graph_in = result.graph_guided.input_tokens
    naive_in = result.naive.input_tokens
    return [
        "## R4.1 - Token reduction",
        (
            f"Graph-guided used {pct_str}% fewer input tokens than naive "
            f"({graph_in} vs {naive_in}), because the `fix` node received only "
            "index.md + hot.md + polygons.py instead of the full data/broken-python/** dump."
        ),
        "",
        "## R4.2 - Accuracy cost",
        result.correctness_delta,
    ]
