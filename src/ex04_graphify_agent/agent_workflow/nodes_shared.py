"""Shared nodes + helpers used by BOTH run types (plan / fix / report) — AW-T8 parity.

These node objects are reused verbatim across the graph-guided and naive routes so the
gatekeeper token instrumentation is identical (the comparison measures *context strategy*
and nothing else). ``call_llm`` is the single helper that funnels a node's LLM call through
the gatekeeper and appends one ``TokenRecord`` to state (AW-T7 / ADR-0002).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ex04_graphify_agent.agent_workflow import context, fix_target, prompts
from ex04_graphify_agent.agent_workflow.deps import NodeDeps
from ex04_graphify_agent.agent_workflow.state import AgentState, RunType, TokenRecord
from ex04_graphify_agent.gatekeeper import LLMResponse

Node = Callable[[AgentState], dict[str, Any]]


def initial_state(run_type: RunType) -> AgentState:
    """A fully-populated empty state (no untyped holes — R6.1.4)."""
    return AgentState(
        run_type=run_type,
        messages=[],
        vault_context="",
        dumped_context="",
        current_hypothesis=None,
        validated_source=None,
        validated=False,
        findings_tried=0,
        files_read=[],
        target_file=None,
        fix_diff=None,
        token_usage=[],
    )


def call_llm(deps: NodeDeps, state: AgentState, node: str, system: str, prompt: str) -> LLMResponse:
    """The single seam: every node LLM call goes through the gatekeeper (ADR-0002)."""
    response = deps.gatekeeper.call(
        messages=[{"role": "user", "content": prompt}],
        run_id=deps.run_id,
        node=node,
        system=system,
        run_type=state["run_type"],
    )
    return response


def token_record(node: str, response: LLMResponse) -> TokenRecord:
    """Mirror a gatekeeper response into a state ``TokenRecord`` (AW-T7)."""
    return TokenRecord(
        node=node,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
    )


def make_plan(deps: NodeDeps) -> Node:
    """Plan node — tiny system prompt only; records the route + one TokenRecord."""

    def plan(state: AgentState) -> dict[str, Any]:
        response = call_llm(deps, state, "plan", prompts.PLAN_SYSTEM, state["run_type"])
        message = {"role": "assistant", "node": "plan", "content": response.text}
        return {
            "run_type": state["run_type"],
            "messages": [*state["messages"], message],
            "token_usage": [*state["token_usage"], token_record("plan", response)],
        }

    return plan


def make_fix(deps: NodeDeps) -> Node:
    """Fix node (shared) — one gatekeeper call; context differs by run_type only."""

    def fix(state: AgentState) -> dict[str, Any]:
        prompt = _fix_prompt(state)
        response = call_llm(deps, state, "fix", prompts.FIX_SYSTEM, prompt)
        target = fix_target.target_file(state, response.text)
        original = fix_target.original_source(state, target)
        fixed = fix_target.fixed_content(state, response.text)
        diff = context.make_diff(original, fixed, target) if target else ""
        _write_scratch(deps, target, fixed)
        message = {"role": "assistant", "node": "fix", "prompt": prompt, "content": response.text}
        return {
            "messages": [*state["messages"], message],
            "target_file": target,
            "fix_diff": diff or None,
            "token_usage": [*state["token_usage"], token_record("fix", response)],
        }

    return fix


def make_report(deps: NodeDeps) -> Node:
    """Report node — deterministic summary, no LLM call (PHASE5-052)."""

    def report(state: AgentState) -> dict[str, Any]:
        summary = _render_report(state)
        message = {"role": "assistant", "node": "report", "report": summary}
        return {"messages": [*state["messages"], message]}

    return report


def _fix_prompt(state: AgentState) -> str:
    if state["run_type"] == "naive":
        return prompts.NAIVE_FIX_USER_TEMPLATE.format(dump=state["dumped_context"])
    hyp = state["current_hypothesis"]
    return prompts.FIX_USER_TEMPLATE.format(
        filename=fix_target.graph_target(state),
        context=state["vault_context"],
        source=state["validated_source"] or "",
        hypothesis=hyp.hypothesis if hyp else "",
    )


def _write_scratch(deps: NodeDeps, target: str | None, fixed: str) -> None:
    if deps.scratch_dir is not None and target:
        (deps.scratch_dir / fix_target.scratch_name(target)).write_text(fixed, encoding="utf-8")


def _render_report(state: AgentState) -> str:
    hyp = state["current_hypothesis"]
    root = hyp.hypothesis if hyp else "no confirmable finding"
    tag = hyp.tag if hyp else "n/a"
    status = "validated" if state["validated"] else "unvalidated"
    has_fix = "yes" if state["fix_diff"] else "no"
    return (
        f"run_type={state['run_type']} | root_cause={root} | tag={tag} | "
        f"validation={status} | findings_tried={state['findings_tried']} | fix={has_fix}"
    )
