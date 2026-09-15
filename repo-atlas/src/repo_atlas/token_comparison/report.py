"""render_report / write_report — token_comparison.md, entirely derived from RunMetrics.

Every figure in the table and the narrative is read from the ``ComparisonResult`` (and the
``pricing``/``repo_name``/``model`` the caller supplies) — never a literal number or repo
name baked into this module's text. This module reads no config file and discovers no path
of its own (``write_report`` requires an explicit path); that is the SDK layer's job.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from repo_atlas.gatekeeper import TokenRecord
from repo_atlas.token_comparison import cost
from repo_atlas.token_comparison.metrics import assert_totals_match_log
from repo_atlas.token_comparison.models import ComparisonResult, RunMetrics

_HEADER = (
    "| Run | Input tok | Output tok | Total | Files read | # LLM calls | Duration (s) "
    "| Hot-node coverage | Module coverage |"
)
_SEPARATOR = "|---|---|---|---|---|---|---|---|---|"


def render_report(
    result: ComparisonResult,
    pricing: Mapping[str, float],
    repo_name: str,
    model: str,
    graph_log: Sequence[TokenRecord] | None = None,
    naive_log: Sequence[TokenRecord] | None = None,
) -> str:
    """Render the full markdown report: table + reduction + coverage + cost.

    When ``graph_log``/``naive_log`` are given, each ``RunMetrics`` is first reconciled
    against that raw gatekeeper log (``assert_totals_match_log``) and the render is refused
    on any disagreement — a second, independent check on top of the one ``build_run_metrics``
    already performed, so a report can never be produced from stale or tampered numbers.
    """
    if graph_log is not None:
        assert_totals_match_log(result.graph_guided, list(graph_log))
    if naive_log is not None:
        assert_totals_match_log(result.naive, list(naive_log))
    lines = [
        f"# Token comparison — {repo_name}",
        "",
        "> Graph-guided vs naive-dump, the same brief prompt, one gatekeeper ledger (PRD R5). "
        "Every number below is read from the run's `RunMetrics` — none are hand-typed.",
        "",
        _HEADER,
        _SEPARATOR,
        _row(result.graph_guided),
        _row(result.naive),
        "",
        *_reduction_section(result),
        "",
        *_coverage_section(result),
        "",
        *_cost_section(result, pricing, model),
    ]
    return "\n".join(lines) + "\n"


def write_report(
    result: ComparisonResult,
    pricing: Mapping[str, float],
    repo_name: str,
    model: str,
    path: str | Path,
    graph_log: Sequence[TokenRecord] | None = None,
    naive_log: Sequence[TokenRecord] | None = None,
) -> Path:
    """Render and write the report to an explicit ``path`` (ADR-0003: paths are parameters)."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        render_report(result, pricing, repo_name, model, graph_log, naive_log), encoding="utf-8"
    )
    return out


def _row(metrics: RunMetrics) -> str:
    coverage = metrics.coverage
    return (
        f"| {metrics.run_type} | {metrics.input_tokens} | {metrics.output_tokens} "
        f"| {metrics.total_tokens} | {metrics.files_read} | {metrics.num_llm_calls} "
        f"| {metrics.duration_s:.3f} | {coverage.hot_node_coverage:.0%} "
        f"| {coverage.module_coverage:.0%} |"
    )


def _reduction_section(result: ComparisonResult) -> list[str]:
    pct = result.input_token_reduction_pct
    graph_in = result.graph_guided.input_tokens
    naive_in = result.naive.input_tokens
    return [
        "## Input-token reduction",
        f"Graph-guided used {pct:g}% fewer input tokens than naive ({graph_in} vs {naive_in}).",
    ]


def _coverage_section(result: ComparisonResult) -> list[str]:
    graph_cov = result.graph_guided.coverage
    naive_cov = result.naive.coverage
    return [
        "## Coverage",
        (
            f"Graph-guided cited {graph_cov.hot_nodes_cited}/{graph_cov.hot_nodes_total} hot "
            f"nodes and {graph_cov.modules_cited}/{graph_cov.modules_total} modules. Naive "
            f"cited {naive_cov.hot_nodes_cited}/{naive_cov.hot_nodes_total} hot nodes and "
            f"{naive_cov.modules_cited}/{naive_cov.modules_total} modules."
        ),
    ]


def _cost_section(result: ComparisonResult, pricing: Mapping[str, float], model: str) -> list[str]:
    graph_cost = cost.cost_usd(
        result.graph_guided.input_tokens, result.graph_guided.output_tokens, pricing
    )
    naive_cost = cost.cost_usd(result.naive.input_tokens, result.naive.output_tokens, pricing)
    pct = round(100.0 * (naive_cost - graph_cost) / naive_cost, 1) if naive_cost else 0.0
    return [
        "## Cost (USD)",
        f"Model: `{model}`. Rates from the atlas config's `pricing` block.",
        "",
        "| Run | Cost (USD) |",
        "|---|---|",
        f"| {result.graph_guided.run_type} | ${graph_cost:.4f} |",
        f"| {result.naive.run_type} | ${naive_cost:.4f} |",
        "",
        f"Graph-guided cost ${graph_cost:.4f} vs naive ${naive_cost:.4f} ({pct:g}% lower).",
    ]
