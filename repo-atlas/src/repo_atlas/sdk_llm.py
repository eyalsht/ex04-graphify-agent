"""SDK operations that need a provider: the brief, and the two-route comparison.

The gatekeeper is constructed here rather than inside the brief or comparison layers:
choosing a provider is a run-level decision, and keeping it at the façade leaves those
layers pure consumers a test can hand any client.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from repo_atlas import vault_context
from repo_atlas.brief import GRAPH_GUIDED, BriefResult, BriefRunner
from repo_atlas.extractor.build import GRAPH_FILENAME
from repo_atlas.gatekeeper import Gatekeeper, TokenLogger
from repo_atlas.graph_reader import GraphReader
from repo_atlas.paths import RunConfig, RunPaths
from repo_atlas.sdk_graph import vault
from repo_atlas.token_comparison.models import ComparisonResult
from repo_atlas.token_comparison.report import write_report
from repo_atlas.token_comparison.runner import ComparisonRunner

RUNS_DIRNAME = "runs"
BRIEF_FILENAME = "BRIEF.md"
COMPARISON_FILENAME = "token_comparison.md"


@dataclass(frozen=True)
class ComparisonOutcome:
    """Where the evidence report landed, plus the metrics behind it."""

    report_path: Path
    result: ComparisonResult


@dataclass(frozen=True)
class BriefOutcome:
    """Where the brief landed, plus the run it came from (tokens, sources, sections)."""

    brief_path: Path
    result: BriefResult


def brief(
    paths: RunPaths,
    seed_id: str | None = None,
    run_type: str = GRAPH_GUIDED,
) -> BriefOutcome:
    """Write ``BRIEF.md`` for a repository, extracting and building the vault if needed.

    The gatekeeper is constructed here rather than inside the brief layer: choosing a
    provider is a run-level decision, and keeping it at the façade means the brief layer
    stays a pure consumer that tests can hand any client.
    """
    vault_result = vault(paths, seed_id=seed_id)
    config = RunConfig.load(paths.config_path)
    reader = GraphReader(
        paths.out_dir / GRAPH_FILENAME,
        exact_max_nodes=config.graph_reader.betweenness_exact_max_nodes,
        sample_k=config.graph_reader.betweenness_sample_k,
    )
    logger = TokenLogger(paths.out_dir / RUNS_DIRNAME)
    runner = BriefRunner(Gatekeeper(config.gatekeeper_config(), logger), logger)
    result = runner.run(
        reader=reader,
        repo_root=paths.repo_root,
        vault_text=vault_context.vault_text(vault_result.vault_dir),
        repo_name=paths.repo_root.name,
        run_type=run_type,
        budget=config.brief.context_token_budget,
        hot_slices=config.brief.hot_source_slices,
        seed_id=seed_id,
    )
    if logger.records:
        logger.dump()
    return BriefOutcome(brief_path=result.write(paths.out_dir / BRIEF_FILENAME), result=result)


def compare(paths: RunPaths, seed_id: str | None = None) -> ComparisonOutcome:
    """Run both routes over one repository and write the evidence report (PRD R5).

    Both routes share one gatekeeper and one token logger, so the numbers in the report
    and the numbers in the JSONL log are the same numbers, not two measurements that
    happen to agree.
    """
    vault_result = vault(paths, seed_id=seed_id)
    config = RunConfig.load(paths.config_path)
    reader = GraphReader(
        paths.out_dir / GRAPH_FILENAME,
        exact_max_nodes=config.graph_reader.betweenness_exact_max_nodes,
        sample_k=config.graph_reader.betweenness_sample_k,
    )
    logger = TokenLogger(paths.out_dir / RUNS_DIRNAME)
    runner = ComparisonRunner(
        BriefRunner(Gatekeeper(config.gatekeeper_config(), logger), logger), logger
    )
    result = runner.run_both(
        reader=reader,
        repo_root=paths.repo_root,
        vault_text=vault_context.vault_text(vault_result.vault_dir),
        repo_name=paths.repo_root.name,
        budget=config.brief.context_token_budget,
        hot_slices=config.brief.hot_source_slices,
        seed_id=seed_id,
    )
    if logger.records:
        logger.dump()
    report_path = write_report(
        result,
        {
            "input_per_million_usd": config.pricing.input_per_million_usd,
            "output_per_million_usd": config.pricing.output_per_million_usd,
        },
        paths.repo_root.name,
        config.model,
        paths.out_dir / COMPARISON_FILENAME,
    )
    return ComparisonOutcome(report_path=report_path, result=result)
