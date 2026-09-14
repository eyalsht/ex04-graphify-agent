"""Degraded, line-based recovery for files that fail ``ast.parse`` (SPEC §7).

A file that does not parse is not a file with nothing in it. Legacy Python 2, a
half-finished edit, or a syntax experiment still has classes and functions a reader
needs on the map. This recovers what a regex can see honestly and marks it degraded, so
everything derived from it is tagged INFERRED rather than passed off as fact.

Call sites are deliberately NOT recovered: resolving a call needs scope information a
line scan does not have, and a wrong edge is worse than a missing one.
"""

from __future__ import annotations

import re

from repo_atlas.extractor.models import FileSymbols, MarkerComment, Symbol

_CLASS = re.compile(r"^(?P<indent>[ \t]*)class\s+(?P<name>\w+)\s*(?:\((?P<bases>[^)]*)\))?\s*:")
_DEF = re.compile(r"^(?P<indent>[ \t]*)(?:async\s+)?def\s+(?P<name>\w+)\s*\(")


def _bases(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return ()
    return tuple(base.strip() for base in raw.split(",") if base.strip())


def scan_source(
    source_file: str, source: str, markers: tuple[MarkerComment, ...] = ()
) -> FileSymbols:
    """Recover class/function/method symbols from ``source`` without parsing it."""
    symbols: list[Symbol] = []
    open_class: tuple[str, str] | None = None  # (indent, name) of the class we are inside

    for lineno, line in enumerate(source.splitlines(), start=1):
        class_match = _CLASS.match(line)
        if class_match:
            indent = class_match.group("indent")
            if open_class is not None and len(indent) <= len(open_class[0]):
                open_class = None
            symbols.append(
                Symbol(
                    kind="class",
                    name=class_match.group("name"),
                    lineno=lineno,
                    parent=open_class[1] if open_class else None,
                    bases=_bases(class_match.group("bases")),
                )
            )
            open_class = (indent, class_match.group("name"))
            continue

        def_match = _DEF.match(line)
        if not def_match:
            continue
        indent = def_match.group("indent")
        # A def indented past the open class header belongs to it; one at or before that
        # indentation has closed the class body.
        if open_class is not None and len(indent) <= len(open_class[0]):
            open_class = None
        inside_class = open_class is not None
        symbols.append(
            Symbol(
                kind="method" if inside_class else "function",
                name=def_match.group("name"),
                lineno=lineno,
                parent=open_class[1] if open_class else None,
            )
        )

    return FileSymbols(
        source_file=source_file, degraded=True, symbols=tuple(symbols), calls=(), markers=markers
    )
