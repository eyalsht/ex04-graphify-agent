"""Marker-comment extraction (``docs/EXTRACTOR_SPEC.md`` §8).

A repository's TODO/FIXME/XXX/HACK comments are a real comprehension signal: they mark
where the authors themselves thought the soft spots were. They become ``rationale`` nodes.

This deliberately scans the raw line stream rather than the AST. Two reasons: ``ast``
discards comments entirely, and this path must keep working on files that raise
``SyntaxError`` — which is exactly where a reader most needs the hint.
"""

from __future__ import annotations

import re

from repo_atlas.extractor.models import MarkerComment

MARKERS = ("TODO", "FIXME", "XXX", "HACK")

# Whole-line comments only: optional indentation, then "#". A trailing `x = 1  # TODO`
# is excluded on purpose (§8) so the graph does not fill with inline noise. The marker
# is matched on a word boundary so TODOS and mastodon do not qualify.
_COMMENT_LINE = re.compile(r"^\s*#")
_MARKER = re.compile(rf"\b(?:{'|'.join(MARKERS)})\b")


def find_markers(source: str, limit: int | None = None) -> tuple[MarkerComment, ...]:
    """Return the marker comments in ``source``, in line order, capped at ``limit``.

    ``limit=None`` means uncapped; ``limit=0`` disables marker nodes entirely.
    """
    if limit is not None and limit <= 0:
        return ()
    found: list[MarkerComment] = []
    for lineno, line in enumerate(source.splitlines(), start=1):
        if not _COMMENT_LINE.match(line) or not _MARKER.search(line):
            continue
        found.append(MarkerComment(text=line.strip(), lineno=lineno))
        if limit is not None and len(found) >= limit:
            break
    return tuple(found)
