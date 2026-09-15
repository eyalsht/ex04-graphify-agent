"""Runs the brief: context in, written sections out (PRD R4).

Deliberately a plain pipeline rather than a LangGraph ``StateGraph``. The flow is linear
— assemble context, answer each section, render — with no branching, no retry loop and no
conditional routing, so a state machine would add ceremony without buying anything. The
origin project needed LangGraph because its flow *did* branch (hypothesise → validate →
retry-or-fix). ``docs/KNOWN_LIMITATIONS.md`` records this divergence from CLAUDE.md §2;
the dependency stays so the first branching flow can adopt it without re-plumbing.
"""

from __future__ import annotations

from pathlib import Path

from repo_atlas.brief import context as ctx
from repo_atlas.brief.models import BriefResult, Section
from repo_atlas.brief.prompts import SECTIONS, SYSTEM, section_prompt
from repo_atlas.gatekeeper import Gatekeeper, TokenLogger
from repo_atlas.graph_reader import GraphReader
from repo_atlas.vault import DEFAULT_WEIGHTS, ranking

GRAPH_GUIDED = "graph_guided"
NAIVE = "naive"

#: Synthesised prose is never EXTRACTED: the graph facts underneath it are, the sentences
#: the model writes around them are not (CLAUDE.md §4).
SYNTHESIS_TAG = "INFERRED"
#: Nothing usable reached the model, so the section is a prompt for a human to look.
UNSUPPORTED_TAG = "AMBIGUOUS"


class BriefRunner:
    """Turns a graph and a vault into a written brief, one gatekeeper call per section."""

    def __init__(self, gatekeeper: Gatekeeper, logger: TokenLogger) -> None:
        self._gatekeeper = gatekeeper
        self._logger = logger

    def run(
        self,
        reader: GraphReader,
        repo_root: Path,
        vault_text: str,
        repo_name: str,
        run_type: str = GRAPH_GUIDED,
        budget: int = 8000,
        hot_slices: int = 5,
        seed_id: str | None = None,
    ) -> BriefResult:
        """Assemble context for ``run_type``, then answer every section from it."""
        built = self._context(reader, repo_root, vault_text, run_type, budget, hot_slices, seed_id)
        result = BriefResult(
            repo_name=repo_name,
            run_type=run_type,
            files_read=built.files_read,
            vault_links=self._vault_links(reader, hot_slices, seed_id),
        )
        tag = SYNTHESIS_TAG if built.text.strip() else UNSUPPORTED_TAG
        for index, (title, question) in enumerate(SECTIONS.items()):
            response = self._gatekeeper.call(
                messages=[{"role": "user", "content": section_prompt(title, question, built.text)}],
                run_id=run_type,
                node=f"section_{index}",
                system=SYSTEM,
                run_type=run_type,
            )
            result.sections.append(Section(title=title, body=response.text.strip(), tag=tag))
            result.token_usage.append(
                {
                    "node": f"section_{index}",
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens,
                }
            )
        return result

    @staticmethod
    def _vault_links(
        reader: GraphReader, hot_slices: int, seed_id: str | None
    ) -> tuple[tuple[str, str], ...]:
        """The nodes the brief leans on, so every claim is one click from its evidence."""
        ranked = ranking.rank_nodes(reader, hot_slices, DEFAULT_WEIGHTS, seed_id)
        return tuple((node.id, node.label) for node in ranked)

    def _context(
        self,
        reader: GraphReader,
        repo_root: Path,
        vault_text: str,
        run_type: str,
        budget: int,
        hot_slices: int,
        seed_id: str | None,
    ) -> ctx.BuiltContext:
        """Graph-guided assembles a budgeted selection; naive dumps every indexed file."""
        if run_type == NAIVE:
            files = sorted({node.source_file for node in reader.all_nodes() if node.source_file})
            return ctx.build_naive_context(repo_root, files)
        return ctx.build_graph_context(
            reader, repo_root, vault_text, budget, hot_slices, seed_id=seed_id
        )
