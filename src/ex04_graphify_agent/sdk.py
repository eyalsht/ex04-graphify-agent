"""sdk — the single façade for all EX04 business logic (SDK-first non-negotiable).

CLI/GUI hold no logic; they call this. Concrete methods are added as each phase lands.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

from .graph_reader import GraphReader
from .obsidian_writer import ObsidianWriter
from .weakness_detector import WeaknessDetector, WeaknessFinding

if TYPE_CHECKING:
    from .agent_workflow.state import AgentState, RunType


class Ex04Sdk:
    """Top-level façade — orchestrates the lower-level modules, holds no algorithms."""

    def detect_weaknesses(self, graph_path: str | Path | None = None) -> list[WeaknessFinding]:
        """Run the six PART-C weakness signals and return ranked findings (Phase 3 façade).

        Thin delegation only — all detection logic lives in ``weakness_detector``.
        """
        return WeaknessDetector(GraphReader(graph_path)).detect()

    def generate_hot(self, vault_dir: str | Path | None = None) -> Path:
        """Render and write ``hot.md`` (R5.1.4 / R5.6.1).

        Keyless — no LLM call. ``vault_dir`` defaults to ``config/paths.json``
        ``obsidian_dir`` when omitted. Only ``hot.md`` is written (CLAUDE.md §4
        baseline immutability).
        """
        reader = GraphReader()
        writer = ObsidianWriter(reader, vault_dir=vault_dir)
        return writer.write_hot_md()

    def run_agent(self, run_type: str, scratch_dir: str | Path | None = None) -> AgentState:
        """Build + invoke the LangGraph agent for ``run_type`` and return the final state.

        Keyless by default (the gatekeeper injects its MockClient when no key is set).
        ``scratch_dir`` is where the fix node writes the corrected file; when ``None`` the
        node computes the diff without touching the vendored baseline (CLAUDE.md §4).
        """
        if run_type not in ("graph_guided", "naive"):
            msg = f"unknown run_type: {run_type!r} (expected 'graph_guided' or 'naive')"
            raise ValueError(msg)
        from .agent_workflow import config, graph_def, nodes
        from .agent_workflow.deps import NodeDeps
        from .gatekeeper import Gatekeeper, TokenLogger

        gatekeeper = Gatekeeper(config.agent_config(), TokenLogger())
        deps = NodeDeps(
            gatekeeper=gatekeeper,
            run_id=run_type,
            scratch_dir=Path(scratch_dir) if scratch_dir is not None else None,
        )
        rt = cast("RunType", run_type)
        graph = graph_def.build_graph(rt, deps)
        return cast("AgentState", graph.invoke(nodes.initial_state(rt)))

    def compare_tokens(self, report_path: str | Path | None = None) -> Path:
        """Run both routes, compare token usage, and write ``reports/token_comparison.md``.

        Thin delegation to ``token_comparison.TokenComparison`` (R5.6 / R7.8). Keyless by
        default — both runs use the gatekeeper's MockClient when no provider key is set.
        """
        from .token_comparison import TokenComparison

        comparison = TokenComparison()
        result = comparison.run_both(self)
        return comparison.write_report(result, path=report_path)
