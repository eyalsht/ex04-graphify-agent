"""Source file -> ``FileSymbols`` (``docs/EXTRACTOR_SPEC.md`` §7).

Tries ``ast.parse`` first. On ``SyntaxError`` it does NOT give up on the file: it hands
off to :mod:`repo_atlas.extractor.scan`, whose line-based recovery yields the same
symbol shapes tagged as degraded. In the reference corpus that fallback is the
difference between extracting most of a file's structure and losing it entirely.

Call sites are recorded, never filtered. Deciding which of them become ``calls`` edges
is the edge layer's rule (§5), and keeping that decision in one place is what stops the
two layers disagreeing about what a call is.
"""

from __future__ import annotations

import ast

from repo_atlas.extractor import scan
from repo_atlas.extractor.collector import Collector
from repo_atlas.extractor.comments import find_markers
from repo_atlas.extractor.models import FileSymbols


def parse_source(source_file: str, source: str, marker_limit: int | None = None) -> FileSymbols:
    """Parse one file's text into symbols, call sites and marker comments."""
    markers = find_markers(source, limit=marker_limit)
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return scan.scan_source(source_file, source, markers)
    collector = Collector()
    collector.visit(tree)
    return FileSymbols(
        source_file=source_file,
        degraded=False,
        symbols=tuple(collector.symbols),
        calls=tuple(collector.calls),
        markers=markers,
        imports=tuple(collector.imports),
    )
