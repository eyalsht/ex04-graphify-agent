"""End-to-end keyless runs of both routes (AW-T2/T3/T4/T7, files_read counts).

The mocked gatekeeper drives the graph (ADR-0005); the deterministic graph/source reads do
the real localization, so these assertions on state structure hold with no API key.
"""

from __future__ import annotations

from typing import Any

from ex04_graphify_agent.agent_workflow import graph_def, nodes
from ex04_graphify_agent.agent_workflow.deps import NodeDeps


def _run(run_type: str, deps: NodeDeps) -> dict[str, Any]:
    graph = graph_def.build_graph(run_type, deps)  # type: ignore[arg-type]
    return graph.invoke(nodes.initial_state(run_type))  # type: ignore[arg-type]


def test_graph_guided_run_localizes_and_fixes(deps: NodeDeps) -> None:
    final = _run("graph_guided", deps)
    assert final["validated"] is True
    assert final["current_hypothesis"].source_file == "polygons/polygons.py"  # AW-T4
    assert final["current_hypothesis"].priority == "primary"
    assert final["fix_diff"] is not None


def test_graph_guided_reads_only_one_source(deps: NodeDeps) -> None:
    final = _run("graph_guided", deps)
    # AW-T2: exactly one source file (polygons.py) is read — no mathsquiz *source* content.
    # (The vault map legitimately lists mathsquiz node *names*; what must not leak is their
    # file contents, which only enter via validated_source.)
    assert "calc_polygon_details" in final["validated_source"]
    assert "mathsquiz" not in final["validated_source"]
    # files_read = index.md + hot.md + the one validated source == 3 (R5.6.5).
    assert len(final["files_read"]) == 3


def test_naive_run_dumps_every_file(deps: NodeDeps) -> None:
    final = _run("naive", deps)
    dump = final["dumped_context"]
    # AW-T3: the whole tree — polygons + mathsquiz scripts + READMEs + LICENSE.
    assert "polygons.py" in dump
    assert "mathsquiz" in dump
    assert "LICENSE" in dump or "License" in dump
    assert final["fix_diff"] is not None
    assert len(final["files_read"]) >= 8  # materially more files than graph-guided's 3


def test_token_usage_one_record_per_llm_call(deps: NodeDeps) -> None:
    # AW-T7: gatekeeper-billed nodes (plan, fix) each append one well-formed TokenRecord.
    final = _run("graph_guided", deps)
    billed = [record["node"] for record in final["token_usage"]]
    assert "plan" in billed and "fix" in billed
    for record in final["token_usage"]:
        assert record["input_tokens"] >= 0
        assert record["output_tokens"] >= 0
