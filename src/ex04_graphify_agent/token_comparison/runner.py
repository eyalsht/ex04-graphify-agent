"""TokenComparison — the token_comparison façade (PHASE6-005/006, R5.6 / R7.8).

Builds ``RunMetrics`` from completed ``AgentState``s, derives the R4.1/R4.2 narrative
inputs via ``compare``, and renders/writes ``reports/token_comparison.md``. Config-driven
(``config/agent.json``) per CLAUDE.md §3 — no literal paths.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ex04_graphify_agent.agent_workflow.config import target_source_path
from ex04_graphify_agent.agent_workflow.state import AgentState
from ex04_graphify_agent.gatekeeper.config import load_agent_config, repo_root
from ex04_graphify_agent.token_comparison.comparison import compare_metrics
from ex04_graphify_agent.token_comparison.correctness import check_correctness
from ex04_graphify_agent.token_comparison.metrics import build_run_metrics
from ex04_graphify_agent.token_comparison.models import ComparisonResult, RunMetrics
from ex04_graphify_agent.token_comparison.patch import apply_unified_diff

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
            _fixed_source_for_state(graph_guided),
        )
        naive_metrics = self.metrics_from_state(
            naive, wall.get("naive", 0.0), _fixed_source_for_state(naive)
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
        """Drive ``sdk.run_agent`` for both run types, time each, and compare (R5.6.2)."""
        import time

        start = time.monotonic()
        graph_guided = sdk.run_agent("graph_guided", scratch_dir=scratch_dir)
        graph_duration = time.monotonic() - start

        start = time.monotonic()
        naive = sdk.run_agent("naive", scratch_dir=scratch_dir)
        naive_duration = time.monotonic() - start

        durations = {"graph_guided": graph_duration, "naive": naive_duration}
        return self.compare(graph_guided, naive, durations=durations)

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
        post = Path(post_fix_path) if post_fix_path is not None else _default_post_fix_path()
        try:
            return render_graph_diff(diff_graphs(pre, post))
        except FileNotFoundError:
            return render_graph_diff_pending()


def _default_post_fix_path() -> Path:
    """``artifacts/graphify_post_fix/graph.json`` from ``config/paths.json`` (TC-E3)."""
    import json

    paths = json.loads((repo_root() / "config" / "paths.json").read_text(encoding="utf-8"))
    return repo_root() / str(paths["graphify_post_fix_dir"]) / "graph.json"


def _fixed_source_for_state(state: AgentState) -> str:
    """Reconstruct the post-fix ``polygons.py`` text for ``check_correctness`` (R10.5).

    Applies ``state['fix_diff']`` (a unified diff from ``context.make_diff``) to the
    original ``target_source_path`` content. An empty/absent diff means no fix was
    produced, so the original (still-broken) source is checked - correctly yielding
    ``correctness=False``.
    """
    original = target_source_path().read_text(encoding="utf-8")
    diff = state["fix_diff"] or ""
    return apply_unified_diff(original, diff)
