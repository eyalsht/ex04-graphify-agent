"""TDD for graph-guided node functions: plan / read_vault / hypothesize / validate / fix /
report (PHASE5-010..053, AW-T2/T4/T5/T7). Keyless via the mocked gatekeeper."""

from __future__ import annotations

from ex04_graphify_agent.agent_workflow import nodes
from ex04_graphify_agent.agent_workflow.deps import NodeDeps
from ex04_graphify_agent.agent_workflow.state import AgentState


def _state(run_type: str = "graph_guided") -> AgentState:
    return nodes.initial_state(run_type)  # type: ignore[arg-type]


def test_initial_state_is_fully_populated() -> None:
    st = _state()
    assert st["run_type"] == "graph_guided"
    assert st["files_read"] == [] and st["token_usage"] == []
    assert st["validated"] is False and st["findings_tried"] == 0


def test_plan_sets_run_type_and_records_token(deps: NodeDeps) -> None:
    out = nodes.make_plan(deps)(_state())
    assert out["run_type"] == "graph_guided"
    assert len(out["token_usage"]) == 1
    rec = out["token_usage"][0]
    assert rec["node"] == "plan" and rec["input_tokens"] >= 0


def test_read_vault_loads_index_and_hot(deps: NodeDeps) -> None:
    out = nodes.make_read_vault(deps)(_state())
    assert "polygons_polygons_polygon" in out["vault_context"]
    names = [f.rsplit("\\", 1)[-1].rsplit("/", 1)[-1] for f in out["files_read"]]
    assert names == ["index.md", "hot.md"]


def test_read_vault_reads_no_source_files(deps: NodeDeps) -> None:
    out = nodes.make_read_vault(deps)(_state())
    assert "def calc_polygon_details" not in out["vault_context"]
    assert "import turtle" not in out["vault_context"]


def test_hypothesize_sets_primary_polygon_finding(deps: NodeDeps) -> None:
    out = nodes.make_hypothesize(deps)(_state())
    hyp = out["current_hypothesis"]
    assert hyp is not None
    assert hyp.source_file == "polygons/polygons.py"
    assert hyp.priority == "primary"
    assert hyp.signal == 1


def test_hypothesize_carries_confidence_tag(deps: NodeDeps) -> None:
    out = nodes.make_hypothesize(deps)(_state())
    assert out["current_hypothesis"].tag in {"EXTRACTED", "INFERRED", "AMBIGUOUS"}


def test_validate_reads_only_polygons_and_fills_trail(deps: NodeDeps) -> None:
    st = nodes.make_hypothesize(deps)(_state())
    base = {**_state(), **st}
    out = nodes.make_validate(deps)(base)  # type: ignore[arg-type]
    assert out["validated"] is True
    assert "import turtle" in out["validated_source"]
    assert "mathsquiz" not in out["validated_source"]
    assert out["current_hypothesis"].source_validation is not None
    assert any("polygons.py" in f for f in out["files_read"])


def test_fix_uses_only_one_source_no_mathsquiz(deps: NodeDeps) -> None:
    src = "import turtle"
    hyp = nodes.make_hypothesize(deps)(_state())  # type: ignore[arg-type]
    base = {**_state(), **hyp, "validated_source": src, "validated": True}
    out = nodes.make_fix(deps)(base)  # type: ignore[arg-type]
    assert out["fix_diff"] is not None
    assert "mathsquiz" not in str(out["messages"][-1].get("prompt", ""))


def test_report_summarizes_without_llm(deps: NodeDeps) -> None:
    base = {**_state(), "fix_diff": "--- a\n+++ b\n", "validated": True}
    out = nodes.make_report(deps)(base)  # type: ignore[arg-type]
    assert isinstance(out["messages"][-1]["report"], str)
    assert "token_usage" not in out  # report makes no LLM call (no token record added)
