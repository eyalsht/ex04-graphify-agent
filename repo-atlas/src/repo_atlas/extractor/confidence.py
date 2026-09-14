"""Confidence policy (``docs/EXTRACTOR_SPEC.md`` §6).

A fact read off a parsed AST is EXTRACTED at full confidence. A fact recovered by line
scanning a file that would not parse is INFERRED and worth less, because a regex cannot
see scope. Keeping the policy in one module means the tags stay load-bearing instead of
drifting into decoration.

Every edge today is intra-file, so an edge takes its confidence from the one file it came
from. A "weaker of two endpoints" rule belongs here the moment cross-file edges exist; it
is deliberately absent until then rather than shipped untested.
"""

from __future__ import annotations

from repo_atlas.extractor.models import EXTRACTED, INFERRED, ORIGIN_SCAN

#: How far to trust a symbol recovered without a parser.
SCAN_SCORE = 0.7
EXTRACTED_SCORE = 1.0


def for_origin(origin: str) -> tuple[str, float]:
    """The confidence label and score implied by how a fact was obtained."""
    if origin == ORIGIN_SCAN:
        return INFERRED, SCAN_SCORE
    return EXTRACTED, EXTRACTED_SCORE
