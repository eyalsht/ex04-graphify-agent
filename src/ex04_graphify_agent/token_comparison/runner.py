"""TokenComparison — the token_comparison façade (PHASE6-005/006, R5.6 / R7.8).

Builds ``RunMetrics`` from completed ``AgentState``s, derives the R4.1/R4.2 narrative
inputs via ``compare``, and renders/writes ``reports/token_comparison.md``. Config-driven
(``config/agent.json``) per CLAUDE.md §3 — no literal paths.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ex04_graphify_agent.agent_workflow.state import AgentState
from ex04_graphify_agent.gatekeeper.config import load_agent_config, repo_root
from ex04_graphify_agent.token_comparison import run_helpers
from ex04_graphify_agent.token_comparison.comparison import compare_metrics
from ex04_graphify_agent.token_comparison.correctness import check_correctness
from ex04_graphify_agent.token_comparison.metrics import build_run_metrics
from ex04_graphify_agent.token_comparison.models import ComparisonResult, RunMetrics

_DEFAULT_AGENT_CONFIG = "config/agent.json"


class TokenComparison:
    """Graph-guided vs naive evidence layer (``docs/PRD_token_comparison.md``)."""

    def __init__(self, agent_config: str = _DEFAULT_AGENT_CONFIG) -> None:
        self._agent_config_path = repo_root() / agent_config
        self.agent_config: dict[str, Any] = load_agent_config(self._agent_config_path)

    def metrics_from_state(
        self,
        state: AgentState,
        duration_s: float,
        fixed_source: str,
        gatekeeper_records: list[dict[str, Any]] | None = None,
    ) -> RunMetrics:
        """Aggregate one completed run into ``RunMetrics`` (R5.6.5; TC-E5 if log given)."""
        return build_run_metrics(state, duration_s, fixed_source, gatekeeper_records)

    def check_correctness(self, fixed_source: str) -> bool:
        """The 3-part automated correctness check (TC-T4/T5)."""
        return check_correctness(fixed_source)

    def compare_metrics(self, graph_guided: RunMetrics, naive: RunMetrics) -> ComparisonResult:
        """Derive R4.1 (reduction %) / R4.2 (correctness delta) from two ``RunMetrics``."""
        return compare_metrics(graph_guided, naive)

    def compare(
        self,
        graph_guided: AgentState,
        naive: AgentState,
        durations: dict[str, float] | None = None,
    ) -> ComparisonResult:
        """Build both ``RunMetrics`` (reconstructing each fix from ``fix_diff``) and compare.

        ``durations`` optionally supplies wall-clock seconds per run_type (from ``run_both``);
        defaults to ``0.0`` when timing was not measured.
        """
        wall = durations or {}
        graph_metrics = self.metrics_from_state(
            graph_guided,
            wall.get("graph_guided", 0.0),
            run_helpers.fixed_source_for_state(graph_guided),
        )
        naive_metrics = self.metrics_from_state(
            naive, wall.get("naive", 0.0), run_helpers.fixed_source_for_state(naive)
        )
        return self.compare_metrics(graph_metrics, naive_metrics)

    def render_report(self, result: ComparisonResult) -> str:
        """Render ``reports/token_comparison.md`` as markdown (R5.6.5 table + narrative)."""
        from ex04_graphify_agent.token_comparison.report import render_report

        return render_report(result)

    def write_report(self, result: ComparisonResult, path: str | Path | None = None) -> Path:
        """Render + write the report; default path from ``config/paths.json`` ``reports_dir``."""
        from ex04_graphify_agent.token_comparison.report import write_report

        return write_report(result, path)

    def run_both(self, sdk: Any, scratch_dir: str | Path | None = None) -> ComparisonResult:
        """Drive ``sdk.run_agent`` for both runs and compare, cross-checking each run's
        ``token_usage`` against the gatekeeper's own ledger (TC-E5, mandatory — R10.5)."""
        graph, graph_secs, graph_log = self._timed_run(sdk, "graph_guided", scratch_dir)
        naive, naive_secs, naive_log = self._timed_run(sdk, "naive", scratch_dir)
        graph_metrics = self.metrics_from_state(
            graph, graph_secs, run_helpers.fixed_source_for_state(graph), graph_log
        )
        naive_metrics = self.metrics_from_state(
            naive, naive_secs, run_helpers.fixed_source_for_state(naive), naive_log
        )
        return self.compare_metrics(graph_metrics, naive_metrics)

    @staticmethod
    def _timed_run(
        sdk: Any, run_type: str, scratch_dir: str | Path | None
    ) -> tuple[AgentState, float, list[dict[str, Any]]]:
        """Run one route with an injected gatekeeper logger; return (state, seconds, log)."""
        import time

        from ex04_graphify_agent.gatekeeper import TokenLogger

        logger = TokenLogger()
        start = time.monotonic()
        state: AgentState = sdk.run_agent(run_type, scratch_dir=scratch_dir, logger=logger)
        return state, time.monotonic() - start, run_helpers.ledger(logger)

    def graph_diff_section(
        self,
        pre_fix_path: str | Path | None = None,
        post_fix_path: str | Path | None = None,
    ) -> str:
        """R5.6.3 markdown section: real diff if POST-FIX exists, else "pending re-run" (TC-E3)."""
        from ex04_graphify_agent.graph_reader.loader import default_graph_path
        from ex04_graphify_agent.token_comparison.graph_diff import (
            diff_graphs,
            render_graph_diff,
            render_graph_diff_pending,
        )

        pre = Path(pre_fix_path) if pre_fix_path is not None else default_graph_path()
        post = Path(post_fix_path) if post_fix_path is not None else None
        if post is None:
            post = run_helpers.default_post_fix_path()
        try:
            return render_graph_diff(diff_graphs(pre, post))
        except FileNotFoundError:
            return render_graph_diff_pending()
