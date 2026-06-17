"""Dynamic fix-target resolution — which file the run fixes, and its before/after content.

Graph-guided follows the hypothesis's ``source_file`` (set onto state by ``validate``); the
naive route has no hypothesis, so the LLM declares the file it fixed on a leading
``FILE: <path>`` line, parsed here. No target file is ever hardcoded in node logic
(CLAUDE.md §3) — the agent fixes whatever the graph (or the LLM) points it at.
"""

from __future__ import annotations

import re
from pathlib import Path

from ex04_graphify_agent.agent_workflow import config
from ex04_graphify_agent.agent_workflow.state import AgentState

_FILE_TAG = "FILE:"
_LANG_TAG = re.compile(r"^[A-Za-z0-9_+-]{1,15}$")


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
    """The post-fix file contents from the LLM, stripped of any markdown fence/prose.

    A live model often wraps the file in a ```` ```python ... ``` ```` block or adds a
    preamble; we keep only the code so ``check_correctness`` runs the real fix. Naive also
    drops its leading ``FILE:`` line first.
    """
    text = _strip_file_line(llm_text) if state["run_type"] == "naive" else llm_text
    code = _strip_code_fence(text or "")
    return code or (state["validated_source"] or "")


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


def _strip_code_fence(text: str) -> str:
    """Return the first ```-fenced block's code, or the text unchanged if there is no fence."""
    if "```" not in text:
        return text.strip("\n")
    block = text.split("```", 2)[1]
    lines = block.splitlines()
    if lines and _LANG_TAG.match(lines[0].strip()):
        lines = lines[1:]
    return "\n".join(lines).strip("\n")
