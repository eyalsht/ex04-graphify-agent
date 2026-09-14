"""Wikilink and community-note naming — one place, so links can never dangle.

Every note that names another note goes through here. The origin project spelled
``community-N`` inline in two renderers and never wrote the matching file, which the
consistency gate could not see because it only scanned the two entry points.
"""

from __future__ import annotations

from repo_atlas.graph_reader.models import NodeView

COMMUNITY_PREFIX = "community-"


def community_note_id(community: int) -> str:
    """Note stem for a community, e.g. ``community-3``."""
    return f"{COMMUNITY_PREFIX}{community}"


def community_title(community: int) -> str:
    """Human-facing name for a community."""
    return f"Community {community}"


def wikilink(target_id: str, label: str) -> str:
    """An aliased wikilink: ``[[id|Label]]``."""
    return f"[[{target_id}|{label}]]"


def node_link(node: NodeView) -> str:
    """Wikilink to a node's own note."""
    return wikilink(node.id, node.label)


def community_link(community: int) -> str:
    """Wikilink to a community note."""
    return wikilink(community_note_id(community), community_title(community))
