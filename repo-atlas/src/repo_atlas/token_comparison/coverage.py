"""compute_coverage — what fraction of the graph a brief actually talks about (PRD R5.3).

The origin project measured "correctness" against a hardcoded, one-repo oracle (ADR-0002).
That has no repo-agnostic replacement, but the failure mode it guarded against does: a route
could "win" the token comparison by simply saying less. Coverage is this fork's guard against
that.

**Definition.** Two target sets, both drawn from the graph a brief was built from:

- *Hot nodes*: the ranked entities the brief leaned on, i.e. ``BriefResult.vault_links`` —
  the same nodes the rendered brief links back into the vault (PRD R4.4), so "cited" here
  means "the prose backs up the very claims it points a reader at".
- *Modules*: every file-root node in the graph (``NodeView.is_file_root``), regardless of
  whether the brief was built graph-guided or naive — the naive route reads every module's
  source, so its coverage is measured against the same yardstick.

A target is **cited** when its label, or its source file (full repo-relative path or just
the basename), appears case-insensitively anywhere in the concatenation of the brief's
section bodies. This is deliberately a substring search, not an exact-name match: prose that
says "the `Board` class in `board.py`" should count, and a false-positive substring hit
(e.g. a short label matching inside an unrelated word) is a fair price for not demanding the
model quote identifiers verbatim.

Coverage is ``cited / total`` for each set, and is **0.0**, never a division error, when the
target set is empty — including the degenerate case of a brief with no sections at all,
which correctly scores zero on any non-empty target set.
"""

from __future__ import annotations

from dataclasses import dataclass

from repo_atlas.brief.models import BriefResult
from repo_atlas.graph_reader import GraphReader


@dataclass(frozen=True)
class CoverageMetrics:
    """Citation counts for one brief, against the two target sets described above."""

    hot_nodes_cited: int
    hot_nodes_total: int
    modules_cited: int
    modules_total: int

    @property
    def hot_node_coverage(self) -> float:
        """Fraction of hot nodes cited; ``0.0`` when there were none to cite."""
        return _fraction(self.hot_nodes_cited, self.hot_nodes_total)

    @property
    def module_coverage(self) -> float:
        """Fraction of modules cited; ``0.0`` when the graph has no modules."""
        return _fraction(self.modules_cited, self.modules_total)


def _fraction(cited: int, total: int) -> float:
    return cited / total if total else 0.0


def _mentions(haystack: str, label: str, source_file: str) -> bool:
    """Whether ``label`` or ``source_file`` (full path or basename) appears in ``haystack``.

    ``haystack`` is already lower-cased by the caller.
    """
    if label and label.lower() in haystack:
        return True
    if not source_file:
        return False
    lowered = source_file.lower()
    if lowered in haystack:
        return True
    basename = lowered.rsplit("/", 1)[-1]
    return bool(basename) and basename in haystack


def _brief_text(result: BriefResult) -> str:
    return "\n".join(section.body for section in result.sections).lower()


def _hot_node_source_file(reader: GraphReader, node_id: str) -> str:
    """The node's source file, or ``""`` for a link that names an id outside this graph.

    A ``BriefResult`` built directly in a test carries its own ``(id, label)`` pairs and need
    not resolve against a live reader (PRD R5.3 tests build these directly) — such a link is
    still scored on its label, just not on a source file it has no way to name.
    """
    if not reader.node_exists(node_id):
        return ""
    return reader.node(node_id).source_file


def compute_coverage(result: BriefResult, reader: GraphReader) -> CoverageMetrics:
    """Score one brief against its own hot nodes and the repo's modules."""
    text = _brief_text(result)
    hot_cited = sum(
        1
        for node_id, label in result.vault_links
        if _mentions(text, label, _hot_node_source_file(reader, node_id))
    )
    modules = [node for node in reader.all_nodes() if node.is_file_root]
    modules_cited = sum(1 for node in modules if _mentions(text, node.label, node.source_file))
    return CoverageMetrics(
        hot_nodes_cited=hot_cited,
        hot_nodes_total=len(result.vault_links),
        modules_cited=modules_cited,
        modules_total=len(modules),
    )
