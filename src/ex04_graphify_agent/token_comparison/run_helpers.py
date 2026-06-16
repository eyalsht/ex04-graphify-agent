"""Helpers for ``TokenComparison`` — kept out of ``runner.py`` to honor the 150-line budget.

``fixed_source_for_state`` reconstructs the post-fix source from the file the run targeted
(dynamic, never a hardcoded path); ``ledger`` projects a gatekeeper ``TokenLogger`` to the
fields the TC-E5 cross-check compares; ``default_post_fix_path`` resolves the POST-FIX graph.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ex04_graphify_agent.agent_workflow.config import repo_path
from ex04_graphify_agent.agent_workflow.state import AgentState
from ex04_graphify_agent.gatekeeper.config import repo_root
from ex04_graphify_agent.token_comparison.patch import apply_unified_diff


def fixed_source_for_state(state: AgentState) -> str:
    """Apply ``state['fix_diff']`` to the original of the file the run targeted (R10.5).

    The target is ``state['target_file']`` — from the hypothesis (graph) or the naive LLM,
    never a hardcoded path. No target / no diff yields empty/original source, so
    ``check_correctness`` correctly returns ``False``.
    """
    target = state["target_file"]
    if not target:
        return ""
    original = repo_path(target).read_text(encoding="utf-8")
    return apply_unified_diff(original, state["fix_diff"] or "")


def ledger(logger: Any) -> list[dict[str, Any]]:
    """Project a gatekeeper ``TokenLogger``'s records to (node, input, output) — TC-E5."""
    return [
        {"node": r.node, "input_tokens": r.input_tokens, "output_tokens": r.output_tokens}
        for r in logger.records
    ]


def default_post_fix_path() -> Path:
    """``artifacts/graphify_post_fix/graph.json`` from ``config/paths.json`` (TC-E3)."""
    paths = json.loads((repo_root() / "config" / "paths.json").read_text(encoding="utf-8"))
    return repo_root() / str(paths["graphify_post_fix_dir"]) / "graph.json"
