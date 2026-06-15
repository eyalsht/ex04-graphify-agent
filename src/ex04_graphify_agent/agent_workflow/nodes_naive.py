"""Naive-baseline-only node: dump_repo.

Reads EVERY file under data/broken-python/ into dumped_context (sorted paths, AW-E4) with no
graph, no hot.md, no hypothesis — the deliberately larger "Lost in the Middle" baseline
(R1.4 / R4.1). Each dumped path is appended to files_read so the naive file count is auditable
(R5.6.5). No LLM call here; the gatekeeper-billed step is the shared fix node.
"""

from __future__ import annotations

from typing import Any

from ex04_graphify_agent.agent_workflow import config, context
from ex04_graphify_agent.agent_workflow.deps import NodeDeps
from ex04_graphify_agent.agent_workflow.nodes_shared import Node
from ex04_graphify_agent.agent_workflow.state import AgentState


def make_dump_repo(deps: NodeDeps) -> Node:
    """Concatenate the whole repo tree into dumped_context (no graph, no vault)."""

    def dump_repo(state: AgentState) -> dict[str, Any]:
        text, files = context.dump_repo_text(config.data_repo_root())
        return {"dumped_context": text, "files_read": [*state["files_read"], *files]}

    return dump_repo
