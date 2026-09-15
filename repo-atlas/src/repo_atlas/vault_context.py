"""Selecting which parts of a generated vault belong in an LLM's context.

Its own module because the choice is load-bearing, not plumbing: get it wrong and the
graph-guided route stops being cheaper than a full-source dump.
"""

from __future__ import annotations

from pathlib import Path


def vault_text(vault_dir: Path) -> str:
    """The map the brief reasons over: ``hot.md``, plus only the shape of ``index.md``.

    Emphatically NOT the whole vault. ``index.md`` lists every node, so its size scales
    with the repository exactly as a full-source dump does — feeding it wholesale made the
    graph-guided route *more* expensive than the naive one on every repo size measured.
    What earns its place is the ranked entry points and the community structure; the
    per-node index is navigation for a human, not context for a model.
    """
    parts: list[str] = []
    hot = vault_dir / "hot.md"
    if hot.is_file():
        parts.append(hot.read_text(encoding="utf-8"))
    index = vault_dir / "index.md"
    if index.is_file():
        parts.append(communities_only(index.read_text(encoding="utf-8")))
    return "\n\n".join(part for part in parts if part)


def communities_only(index_text: str) -> str:
    """Keep the Communities section of index.md and drop the exhaustive node listing."""
    lines = index_text.splitlines()
    kept: list[str] = []
    inside = False
    for line in lines:
        if line.startswith("## "):
            inside = line.strip().lower() == "## communities"
            if inside:
                kept.append(line)
            continue
        if inside:
            kept.append(line)
    return "\n".join(kept).strip()
