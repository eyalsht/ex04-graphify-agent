"""Budgeted context assembly (PRD R4.1, R4.2) — where the token thesis actually lives.

The graph-guided context is the vault (the map) plus a *window* of source around each of
the highest-ranked nodes. The naive baseline is every eligible file, whole. Both feed the
same prompt, so any difference in cost comes from retrieval rather than from asking a
different question — which is the only way the comparison in PRD R5 means anything.

Token counting is deliberately a whitespace word count, not a provider tokenizer. It is
provider-agnostic, needs no network, and the offline client reports the same measure, so
a keyless run still produces a real reduction figure rather than a fabricated one.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from repo_atlas.graph_reader import GraphReader
from repo_atlas.graph_reader.models import NodeView
from repo_atlas.vault import DEFAULT_WEIGHTS, ranking

_LOCATION_PREFIX = "L"


@dataclass(frozen=True)
class BuiltContext:
    """Assembled prompt context, and an honest record of what was opened to build it."""

    text: str
    files_read: tuple[str, ...]


def count_tokens(text: str) -> int:
    """Provider-agnostic size measure: whitespace-separated words."""
    return len(text.split())


def _line_of(node: NodeView) -> int | None:
    location = node.source_location or ""
    if not location.startswith(_LOCATION_PREFIX):
        return None
    try:
        return int(location[len(_LOCATION_PREFIX) :])
    except ValueError:
        return None


def source_slice(repo_root: Path, node: NodeView, window: int) -> str:
    """The ``window`` lines either side of a node's definition, as a fenced block.

    Returns an empty string when the file or the location is unusable — a brief built on
    a file we could not open should say less, never invent.
    """
    line = _line_of(node)
    if not node.source_file or line is None:
        return ""
    path = repo_root / node.source_file
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    start = max(0, line - 1 - window)
    end = min(len(lines), line + window)
    body = "\n".join(lines[start:end])
    return f"### {node.label} — `{node.source_file}:{node.source_location}`\n```python\n{body}\n```"


def build_graph_context(
    reader: GraphReader,
    repo_root: Path,
    vault_text: str,
    budget: int,
    hot_slices: int,
    window: int = 12,
    seed_id: str | None = None,
) -> BuiltContext:
    """Vault first, then source windows for the top-ranked nodes, capped at ``budget``."""
    parts = [vault_text]
    files: list[str] = []
    used = count_tokens(vault_text)
    ranked = ranking.rank_nodes(reader, hot_slices, DEFAULT_WEIGHTS, seed_id)
    for node in ranked:
        block = source_slice(repo_root, node, window)
        if not block:
            continue
        cost = count_tokens(block)
        if used + cost > budget:
            break
        parts.append(block)
        used += cost
        if node.source_file not in files:
            files.append(node.source_file)
    return BuiltContext(text="\n\n".join(parts), files_read=tuple(files))


def build_naive_context(repo_root: Path, relative_paths: list[str]) -> BuiltContext:
    """Every eligible file, whole — the baseline the graph-guided path is measured against."""
    parts: list[str] = []
    files: list[str] = []
    for relative in sorted(relative_paths):
        try:
            body = (repo_root / relative).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        parts.append(f"# === {relative} ===\n{body}")
        files.append(relative)
    return BuiltContext(text="\n\n".join(parts), files_read=tuple(files))
