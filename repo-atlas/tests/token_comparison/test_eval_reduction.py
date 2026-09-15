"""Keyless eval (PHASE5-012): the offline provider still proves a real token reduction.

Not a unit test of one function — it drives the real ``ComparisonRunner`` + ``BriefRunner``
+ offline ``Gatekeeper`` end to end and checks the headline claim PRD R5 exists to support:
graph-guided retrieval costs materially fewer input tokens than a naive full-repo dump, on
the same prompt, with no provider key. Run via ``uv run pytest -m eval``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from repo_atlas.gatekeeper import TokenLogger
from repo_atlas.token_comparison.report import render_report
from repo_atlas.token_comparison.runner import ComparisonRunner
from tests.token_comparison import _fixtures as fx

_ZERO_PRICING = {"input_per_million_usd": 0.0, "output_per_million_usd": 0.0}
#: Not a claimed real-world figure — just "graph-guided must win by a wide, non-fluke margin"
#: on this synthetic fixture, so the eval fails loud if the thesis ever regresses to noise.
_MIN_REDUCTION_PCT = 50.0


@pytest.mark.eval
def test_offline_run_shows_a_material_input_token_reduction(tmp_path: Path) -> None:
    logger = TokenLogger(runs_dir=tmp_path)
    runner = ComparisonRunner(fx.build_brief_runner(logger), logger)
    reader = fx.build_reader(tmp_path)
    repo = fx.build_repo(tmp_path)

    result = runner.run_both(reader, repo, vault_text="INDEX\nHOT\n", repo_name="proj", budget=200)

    assert result.input_token_reduction_pct >= _MIN_REDUCTION_PCT
    assert result.graph_guided.input_tokens < result.naive.input_tokens

    # The report itself must trace to the very log this run produced (R5.2) and render.
    graph_log = [r for r in logger.records if r.run_type == "graph_guided"]
    naive_log = [r for r in logger.records if r.run_type == "naive"]
    report = render_report(
        result, _ZERO_PRICING, "proj", "mock-offline", graph_log=graph_log, naive_log=naive_log
    )
    assert "proj" in report
    assert str(result.graph_guided.input_tokens) in report
