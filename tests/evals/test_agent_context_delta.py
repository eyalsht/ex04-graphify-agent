"""AW-T1 structural eval (the thesis): graph-guided fix-context << naive (R5.6.2 / R4.1).

Keyless and LLM-free — it measures only the assembled contexts (exactly the delta that
``token_comparison.py`` later bills through the gatekeeper), so the project's core claim is
provable offline, with no API key, as a structural eval (eval-harness skill).
"""

from __future__ import annotations

import pytest

from ex04_graphify_agent.agent_workflow import config, context
from ex04_graphify_agent.graph_reader import GraphReader
from ex04_graphify_agent.weakness_detector import WeaknessDetector

pytestmark = pytest.mark.eval


def test_graph_guided_context_is_far_smaller_than_naive() -> None:
    vault, _ = context.read_vault_text(config.index_md_path(), config.hot_md_path())
    # Follow the graph: the one source file is the top finding's source_file (not hardcoded).
    bug_file = WeaknessDetector(GraphReader()).detect()[0].source_file
    source = config.repo_path(bug_file).read_text(encoding="utf-8")
    graph_guided = context.count_tokens(vault + source)

    dump, _ = context.dump_repo_text(config.data_repo_root())
    naive = context.count_tokens(dump)

    # The thesis: a curated map (index.md + hot.md) + exactly one source file is far
    # cheaper than dumping the whole tree — while localizing the same root cause.
    assert graph_guided < naive
    # Materially so — at least a 50% input-token reduction (R4.1); measured ~74%.
    assert (naive - graph_guided) / naive >= 0.5
