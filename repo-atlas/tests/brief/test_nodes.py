"""The brief pipeline: graph + vault in, BRIEF.md out (PRD R4.3, R4.4)."""

from __future__ import annotations

from pathlib import Path

from repo_atlas.brief import SECTIONS, BriefRunner
from repo_atlas.gatekeeper import Gatekeeper, OfflineClient, TokenLogger
from repo_atlas.graph_reader import GraphReader
from tests.fixtures import graph_factory

_CONFIG = {
    "provider": "offline",
    "model": "mock-offline",
    "api_key_env": "ATLAS_TEST_KEY_ABSENT",
    "rate_limit_per_minute": 6000,
    "retry": {"max_attempts": 2, "backoff_seconds": 0.0},
}


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "proj"
    (repo / "pkg").mkdir(parents=True, exist_ok=True)
    # Substantial enough that a budgeted slice is genuinely smaller than the whole file;
    # on a two-line module, windowing costs more than dumping and the comparison is moot.
    body = "def run():\n" + "".join(f"    value_{i} = {i}\n" for i in range(200)) + "    return 1\n"
    (repo / "pkg" / "core.py").write_text(body, encoding="utf-8")
    return repo


def _reader(tmp_path: Path) -> GraphReader:
    nodes = [
        graph_factory.make_node("pkg_core", source_file="pkg/core.py", source_location="L1"),
        graph_factory.make_node("pkg_core_run", source_file="pkg/core.py", source_location="L1"),
    ]
    edges = [graph_factory.make_edge("pkg_core", "pkg_core_run", relation="contains")]
    path = graph_factory.write_graph(tmp_path, graph_factory.graph_dict(nodes, edges))
    return GraphReader(path)


def _runner(tmp_path: Path) -> BriefRunner:
    logger = TokenLogger(tmp_path / "runs")
    gatekeeper = Gatekeeper(_CONFIG, logger, client=OfflineClient())
    return BriefRunner(gatekeeper, logger)


def _run(tmp_path: Path, run_type: str = "graph_guided"):  # type: ignore[no-untyped-def]
    return _runner(tmp_path).run(
        reader=_reader(tmp_path),
        repo_root=_repo(tmp_path),
        vault_text="# Graph Index\n\n- [[pkg_core_run|run()]]\n",
        repo_name="proj",
        run_type=run_type,
        budget=5000,
        hot_slices=2,
    )


def test_produces_one_section_per_topic(tmp_path: Path) -> None:
    assert [section.title for section in _run(tmp_path).sections] == list(SECTIONS)


def test_makes_one_llm_call_per_section(tmp_path: Path) -> None:
    assert len(_run(tmp_path).token_usage) == len(SECTIONS)


def test_records_input_and_output_tokens_per_call(tmp_path: Path) -> None:
    usage = _run(tmp_path).token_usage[0]
    assert usage["input_tokens"] > 0
    assert usage["output_tokens"] > 0


def test_every_section_carries_a_confidence_tag(tmp_path: Path) -> None:
    """CLAUDE.md §4: no graph-derived claim ships untagged."""
    assert all(
        section.tag in {"EXTRACTED", "INFERRED", "AMBIGUOUS"} for section in _run(tmp_path).sections
    )


def test_synthesised_prose_is_never_tagged_extracted(tmp_path: Path) -> None:
    """The graph facts are extracted; the sentences an LLM writes around them are not."""
    assert all(section.tag != "EXTRACTED" for section in _run(tmp_path).sections)


def test_an_empty_context_is_flagged_ambiguous(tmp_path: Path) -> None:
    result = _runner(tmp_path).run(
        reader=_reader(tmp_path),
        repo_root=tmp_path / "absent",
        vault_text="",
        repo_name="proj",
        run_type="graph_guided",
        budget=5000,
        hot_slices=2,
    )
    assert all(section.tag == "AMBIGUOUS" for section in result.sections)


def test_records_which_files_it_opened(tmp_path: Path) -> None:
    assert "pkg/core.py" in _run(tmp_path).files_read


def test_the_naive_route_reads_more_than_the_graph_route(tmp_path: Path) -> None:
    """The comparison that justifies the whole design."""
    graph_tokens = sum(u["input_tokens"] for u in _run(tmp_path).token_usage)
    naive_tokens = sum(u["input_tokens"] for u in _run(tmp_path, "naive").token_usage)
    assert naive_tokens > graph_tokens


def test_rendered_brief_links_back_into_the_vault(tmp_path: Path) -> None:
    body = _run(tmp_path).render()
    assert "[[pkg_core_run" in body or "[[pkg_core" in body


def test_rendered_brief_states_every_section_and_its_tag(tmp_path: Path) -> None:
    body = _run(tmp_path).render()
    for title in SECTIONS:
        assert title in body
    assert "INFERRED" in body or "AMBIGUOUS" in body


def test_writes_the_brief_to_disk(tmp_path: Path) -> None:
    out = tmp_path / "out" / "BRIEF.md"
    _run(tmp_path).write(out)
    assert out.is_file() and out.read_text(encoding="utf-8").startswith("#")
