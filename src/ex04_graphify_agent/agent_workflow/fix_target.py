"""Dynamic fix-target resolution — which file the run fixes, and its before/after content.

Graph-guided follows the hypothesis's ``source_file`` (set onto state by ``validate``); the
naive route has no hypothesis, so the LLM declares the file it fixed on a leading
``FILE: <path>`` line, parsed here. No target file is ever hardcoded in node logic
(CLAUDE.md §3) — the agent fixes whatever the graph (or the LLM) points it at.
"""

from __future__ import annotations

from pathlib import Path

from ex04_graphify_agent.agent_workflow import config
from ex04_graphify_agent.agent_workflow.state import AgentState

_FILE_TAG = "FILE:"


def graph_target(state: AgentState) -> str:
    """The graph-guided target: the validated file, else the hypothesis's source_file."""
    if state["target_file"]:
        return state["target_file"]
    hyp = state["current_hypothesis"]
    return hyp.source_file if hyp else ""


def target_file(state: AgentState, llm_text: str) -> str | None:
    """Resolve the file this run fixes — from the hypothesis (graph) or the LLM (naive)."""
    if state["run_type"] == "naive":
        return _named_file(llm_text)
    return graph_target(state) or None


def original_source(state: AgentState, target: str | None) -> str:
    """The pre-fix contents to diff against (the already-validated source, or the file)."""
    if state["run_type"] == "graph_guided" and state["validated_source"] is not None:
        return state["validated_source"]
    if target:
        path = config.repo_path(target)
        if path.is_file():
            return path.read_text(encoding="utf-8")
    return ""


def fixed_content(state: AgentState, llm_text: str) -> str:
    """The post-fix file contents from the LLM (naive strips its leading ``FILE:`` line)."""
    if state["run_type"] == "naive":
        return _strip_file_line(llm_text)
    return llm_text or (state["validated_source"] or "")


def scratch_name(target: str) -> str:
    """The scratch filename derived from the target (e.g. ``a/b/c.py`` -> ``c_fixed.py``)."""
    return f"{Path(target).stem}_fixed.py"


def _named_file(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith(_FILE_TAG):
            return stripped[len(_FILE_TAG) :].strip() or None
    return None


def _strip_file_line(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip().upper().startswith(_FILE_TAG):
        return "\n".join(lines[1:]).lstrip("\n")
    return text
