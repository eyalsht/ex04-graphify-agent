"""TDD for ComparisonRunner.run_both (PRD R5.1; PHASE5-003/004) — keyless, offline provider."""

from __future__ import annotations

from pathlib import Path

from repo_atlas.brief.prompts import SECTIONS
from repo_atlas.gatekeeper import TokenLogger
from repo_atlas.token_comparison.runner import ComparisonRunner
from tests.token_comparison import _fixtures as fx


def _runner(tmp_path: Path) -> tuple[ComparisonRunner, TokenLogger]:
    logger = TokenLogger(runs_dir=tmp_path)
    return ComparisonRunner(fx.build_brief_runner(logger), logger), logger


def test_run_both_runs_the_identical_prompt_for_both_routes(tmp_path: Path) -> None:
    runner, _logger = _runner(tmp_path)
    reader = fx.build_reader(tmp_path)
    repo = fx.build_repo(tmp_path)
    result = runner.run_both(reader, repo, vault_text="INDEX\nHOT\n", repo_name="proj")
    assert result.graph_guided.run_type == "graph_guided"
    assert result.naive.run_type == "naive"
    assert result.graph_guided.num_llm_calls == len(SECTIONS)
    assert result.naive.num_llm_calls == len(SECTIONS)


def test_run_both_naive_uses_more_input_tokens_than_graph_guided(tmp_path: Path) -> None:
    # The whole R5.1 thesis: naive dumps whole files, graph-guided budgets a slice + vault.
    runner, _logger = _runner(tmp_path)
    reader = fx.build_reader(tmp_path)
    repo = fx.build_repo(tmp_path)
    result = runner.run_both(reader, repo, vault_text="INDEX\nHOT\n", repo_name="proj", budget=200)
    assert result.naive.input_tokens > result.graph_guided.input_tokens
    assert result.input_token_reduction_pct > 0.0


def test_run_both_logs_every_call_tagged_by_run_type(tmp_path: Path) -> None:
    runner, logger = _runner(tmp_path)
    reader = fx.build_reader(tmp_path)
    repo = fx.build_repo(tmp_path)
    runner.run_both(reader, repo, vault_text="INDEX\nHOT\n", repo_name="proj")
    run_types = {record.run_type for record in logger.records}
    assert run_types == {"graph_guided", "naive"}
    assert len(logger.records) == 2 * len(SECTIONS)


def test_run_both_computes_coverage_for_each_route(tmp_path: Path) -> None:
    runner, _logger = _runner(tmp_path)
    reader = fx.build_reader(tmp_path)
    repo = fx.build_repo(tmp_path)
    result = runner.run_both(reader, repo, vault_text="INDEX\nHOT\n", repo_name="proj")
    assert result.graph_guided.coverage.hot_nodes_total >= 0
    assert result.naive.coverage.modules_total == 2
