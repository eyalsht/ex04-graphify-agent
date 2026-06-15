"""TDD for the naive dump_repo node + naive fix context (AW-T3, PHASE5-054..061)."""

from __future__ import annotations

from ex04_graphify_agent.agent_workflow import nodes
from ex04_graphify_agent.agent_workflow.deps import NodeDeps


def _naive() -> dict:
    return nodes.initial_state("naive")  # type: ignore[arg-type, return-value]


def test_dump_repo_fills_dumped_context_with_all_files(deps: NodeDeps) -> None:
    out = nodes.make_dump_repo(deps)(_naive())  # type: ignore[arg-type]
    text = out["dumped_context"]
    assert "polygons.py" in text
    assert "mathsquiz" in text
    assert "LICENSE" in text.upper()
    assert len(out["files_read"]) == 8


def test_dump_is_deterministic_sorted(deps: NodeDeps) -> None:
    out1 = nodes.make_dump_repo(deps)(_naive())  # type: ignore[arg-type]
    out2 = nodes.make_dump_repo(deps)(_naive())  # type: ignore[arg-type]
    assert out1["files_read"] == out2["files_read"] == sorted(out1["files_read"])


def test_naive_fix_prompt_uses_dump_no_hypothesis(deps: NodeDeps) -> None:
    st = nodes.make_dump_repo(deps)(_naive())  # type: ignore[arg-type]
    base = {**_naive(), **st}
    out = nodes.make_fix(deps)(base)  # type: ignore[arg-type]
    prompt = str(out["messages"][-1]["prompt"])
    assert "mathsquiz" in prompt  # naive sees the whole tree
    assert "Hypothesis:" not in prompt  # no curated hypothesis in naive fix
