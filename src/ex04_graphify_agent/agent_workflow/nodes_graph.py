"""Graph-guided-only nodes: read_vault / hypothesize / validate.

read_vault loads the compressed map (index.md + hot.md) and reads NO source (R5.3.2/R1.3);
hypothesize ranks the six weakness signals to the primary finding (AW-T4); validate opens
exactly one source file (polygons/polygons.py) to confirm it, promoting an INFERRED/AMBIGUOUS
proposal toward an EXTRACTED conclusion (R5.5.3, inference discipline). No LLM calls here —
these are deterministic graph/source reads; the gatekeeper-billed step is fix.
"""

from __future__ import annotations

from typing import Any

from ex04_graphify_agent.agent_workflow import config, context
from ex04_graphify_agent.agent_workflow.deps import NodeDeps
from ex04_graphify_agent.agent_workflow.nodes_shared import Node
from ex04_graphify_agent.agent_workflow.state import AgentState
from ex04_graphify_agent.graph_reader import GraphReader
from ex04_graphify_agent.weakness_detector import (
    SourceValidation,
    WeaknessDetector,
    WeaknessFinding,
)


def make_read_vault(deps: NodeDeps) -> Node:
    """Read index.md + hot.md into vault_context (fail loud if hot.md absent — AW-E2)."""

    def read_vault(state: AgentState) -> dict[str, Any]:
        text, files = context.read_vault_text(config.index_md_path(), config.hot_md_path())
        return {"vault_context": text, "files_read": [*state["files_read"], *files]}

    return read_vault


def make_hypothesize(deps: NodeDeps) -> Node:
    """Set current_hypothesis to the top-ranked (primary) finding (AW-T4)."""

    def hypothesize(state: AgentState) -> dict[str, Any]:
        findings = WeaknessDetector(GraphReader()).detect()
        index = min(state["findings_tried"], len(findings) - 1) if findings else 0
        finding = findings[index] if findings else None
        return {"current_hypothesis": finding}

    return hypothesize


def make_validate(deps: NodeDeps) -> Node:
    """Open the hypothesis source_file (one file) and fill the validation trail (AW-T5)."""

    def validate(state: AgentState) -> dict[str, Any]:
        hyp = state["current_hypothesis"]
        if hyp is None:
            return {"validated": False}
        source = config.target_source_path().read_text(encoding="utf-8")
        confirmed = _confirms(hyp, source)
        hyp.source_validation = SourceValidation(
            confirmed=confirmed,
            note=_validation_note(hyp, confirmed),
        )
        return {
            "validated_source": source,
            "validated": confirmed,
            "current_hypothesis": hyp,
            "findings_tried": state["findings_tried"] + 1,
            "files_read": [*state["files_read"], str(config.target_source_path())],
        }

    return validate


def _confirms(hyp: WeaknessFinding, source: str) -> bool:
    """Source-validation step: AMBIGUOUS must be confirmed by a real source token."""
    if hyp.tag == "AMBIGUOUS":
        return any(node_label_in_source(node, source) for node in hyp.nodes)
    return True


def node_label_in_source(node_id: str, source: str) -> bool:
    """Heuristic confirm: the node's trailing label token appears in the source text."""
    token = node_id.rsplit("_", 1)[-1]
    return token in source


def _validation_note(hyp: WeaknessFinding, confirmed: bool) -> str:
    verb = "confirmed" if confirmed else "not confirmed"
    return f"signal {hyp.signal} ({hyp.tag}) {verb} against {hyp.source_file}"
