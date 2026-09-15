"""Shared synthetic repo/graph/gatekeeper fixtures for token_comparison tests (CLAUDE.md §7).

Not a test module itself — nothing here is collected by pytest. Keeps ``test_runner.py`` and
the keyless eval (PHASE5-012) from duplicating the same synthetic setup.
"""

from __future__ import annotations

from pathlib import Path

from repo_atlas.brief.runner import BriefRunner
from repo_atlas.gatekeeper import Gatekeeper, TokenLogger
from repo_atlas.graph_reader import GraphReader
from tests.fixtures import graph_factory

#: An env var that is never set in this test run, so the gatekeeper always falls back to
#: its offline client (ADR-0005: keyless by default) without needing to touch os.environ.
_UNSET_KEY_ENV = "ATLAS_TOKEN_COMPARISON_TEST_UNSET_KEY"

_LINES_PER_FILE = 300


def build_repo(tmp_path: Path) -> Path:
    """A tiny two-module repo, large enough that graph-guided/naive token counts differ."""
    repo = tmp_path / "proj"
    (repo / "pkg").mkdir(parents=True)
    body = "\n".join(f"# line {index}" for index in range(1, _LINES_PER_FILE + 1)) + "\n"
    (repo / "pkg" / "core.py").write_text(body, encoding="utf-8")
    (repo / "pkg" / "util.py").write_text(body, encoding="utf-8")
    return repo


def build_reader(tmp_path: Path) -> GraphReader:
    """A graph over ``build_repo``'s two modules, each with one contained entity."""
    nodes = [
        graph_factory.make_node("pkg_core", source_file="pkg/core.py", source_location="L1"),
        graph_factory.make_node("pkg_core_run", source_file="pkg/core.py", source_location="L10"),
        graph_factory.make_node("pkg_util", source_file="pkg/util.py", source_location="L1"),
        graph_factory.make_node(
            "pkg_util_helper", source_file="pkg/util.py", source_location="L10"
        ),
    ]
    edges = [
        graph_factory.make_edge("pkg_core", "pkg_core_run", relation="contains"),
        graph_factory.make_edge("pkg_util", "pkg_util_helper", relation="contains"),
        graph_factory.make_edge("pkg_core_run", "pkg_util_helper", relation="calls"),
    ]
    path = graph_factory.write_graph(tmp_path, graph_factory.graph_dict(nodes, edges))
    return GraphReader(path)


def build_brief_runner(logger: TokenLogger) -> BriefRunner:
    """A keyless ``BriefRunner`` wired to the offline gatekeeper client."""
    config = {"provider": "offline", "model": "mock-offline", "api_key_env": _UNSET_KEY_ENV}
    return BriefRunner(Gatekeeper(config, logger), logger)
