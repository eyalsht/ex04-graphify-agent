"""TDD for RunMetrics / ComparisonResult dataclasses (PHASE6-001..004).

Ref: docs/PRD_token_comparison.md "Public interface".
"""

from __future__ import annotations

from ex04_graphify_agent.token_comparison import ComparisonResult, RunMetrics


def _metrics(**overrides: object) -> RunMetrics:
    base: dict[str, object] = {
        "run_type": "graph_guided",
        "input_tokens": 100,
        "output_tokens": 10,
        "total_tokens": 110,
        "files_read": 3,
        "iterations": 1,
        "num_llm_calls": 2,
        "duration_s": 1.5,
        "correctness": True,
        "per_node": [{"node": "fix", "input_tokens": 100, "output_tokens": 10}],
        "files_read_list": ["obsidian/index.md", "obsidian/hot.md", "polygons.py"],
    }
    base.update(overrides)
    return RunMetrics(**base)  # type: ignore[arg-type]


def test_run_metrics_fields_round_trip() -> None:
    metrics = _metrics()
    assert metrics.run_type == "graph_guided"
    assert metrics.input_tokens == 100
    assert metrics.output_tokens == 10
    assert metrics.total_tokens == 110
    assert metrics.files_read == 3
    assert metrics.iterations == 1
    assert metrics.num_llm_calls == 2
    assert metrics.duration_s == 1.5
    assert metrics.correctness is True
    assert metrics.per_node == [{"node": "fix", "input_tokens": 100, "output_tokens": 10}]
    assert metrics.files_read_list == ["obsidian/index.md", "obsidian/hot.md", "polygons.py"]


def test_comparison_result_fields_round_trip() -> None:
    graph_guided = _metrics()
    naive = _metrics(run_type="naive", files_read=9, input_tokens=8000)
    result = ComparisonResult(
        graph_guided=graph_guided,
        naive=naive,
        input_token_reduction_pct=85.0,
        correctness_delta="both runs passed correctness; no accuracy cost.",
    )
    assert result.graph_guided is graph_guided
    assert result.naive is naive
    assert result.input_token_reduction_pct == 85.0
    assert "no accuracy cost" in result.correctness_delta
