"""ComparisonRunner — drives both routes through one BriefRunner (PRD R5.1; PLAN §5.7).

Takes already-constructed collaborators only: a ``BriefRunner`` (already wired to its own
``Gatekeeper``), the ``TokenLogger`` that same gatekeeper logs into, a ``GraphReader``, and
plain paths/strings. It builds no ``Gatekeeper`` and reads no config file itself — that
wiring belongs to the SDK layer.
"""

from __future__ import annotations

import time
from pathlib import Path

from repo_atlas.brief.models import BriefResult
from repo_atlas.brief.runner import GRAPH_GUIDED, NAIVE, BriefRunner
from repo_atlas.gatekeeper import TokenLogger
from repo_atlas.graph_reader import GraphReader
from repo_atlas.token_comparison.comparison import compare_metrics
from repo_atlas.token_comparison.coverage import compute_coverage
from repo_atlas.token_comparison.metrics import build_run_metrics
from repo_atlas.token_comparison.models import ComparisonResult, RunMetrics


class ComparisonRunner:
    """Runs the identical brief prompt graph-guided and naive, then compares them."""

    def __init__(self, brief_runner: BriefRunner, logger: TokenLogger) -> None:
        self._brief_runner = brief_runner
        self._logger = logger

    def run_both(
        self,
        reader: GraphReader,
        repo_root: Path,
        vault_text: str,
        repo_name: str,
        budget: int = 8000,
        hot_slices: int = 5,
        seed_id: str | None = None,
    ) -> ComparisonResult:
        """Run graph-guided then naive over the same repo, and compare the two."""
        graph_metrics = self._run_one(
            GRAPH_GUIDED, reader, repo_root, vault_text, repo_name, budget, hot_slices, seed_id
        )
        naive_metrics = self._run_one(
            NAIVE, reader, repo_root, vault_text, repo_name, budget, hot_slices, seed_id
        )
        return compare_metrics(graph_metrics, naive_metrics)

    def _run_one(
        self,
        run_type: str,
        reader: GraphReader,
        repo_root: Path,
        vault_text: str,
        repo_name: str,
        budget: int,
        hot_slices: int,
        seed_id: str | None,
    ) -> RunMetrics:
        start = time.monotonic()
        result = self._brief_runner.run(
            reader,
            repo_root,
            vault_text,
            repo_name,
            run_type=run_type,
            budget=budget,
            hot_slices=hot_slices,
            seed_id=seed_id,
        )
        duration_s = time.monotonic() - start
        return self._metrics(result, run_type, duration_s, reader)

    def _metrics(
        self, result: BriefResult, run_type: str, duration_s: float, reader: GraphReader
    ) -> RunMetrics:
        records = [record for record in self._logger.records if record.run_type == run_type]
        coverage = compute_coverage(result, reader)
        return build_run_metrics(result, records, duration_s, coverage)
