"""Human-facing label and location rules (``docs/EXTRACTOR_SPEC.md`` §3, §4).

The label shapes are asymmetric on purpose, matching the reference graph: a class is
bare (``Polygon``), a module-level function carries empty parens (``draw()``), and a
method leads with a dot and drops its class (``.__init__()``). ``norm_label`` is exactly
``label.lower()`` — no trimming, no punctuation handling, nothing else.
"""

from __future__ import annotations

from pathlib import PurePosixPath

from repo_atlas.extractor.models import Symbol

#: Modules always anchor to line 1, whatever the file actually starts with.
MODULE_LOCATION = "L1"
#: Unresolved external symbols use empty-string sentinels, never None (§2 rule 4).
EXTERNAL_LOCATION = ""
EXTERNAL_SOURCE_FILE = ""


def module_label(source_file: str) -> str:
    """A file node's label: the basename, extension kept, case and hyphens preserved."""
    return PurePosixPath(source_file).name


def symbol_label(symbol: Symbol) -> str:
    """Label for a class, module-level function, or method."""
    if symbol.kind == "class":
        return symbol.name
    if symbol.kind == "function":
        return f"{symbol.name}()"
    if symbol.kind == "method":
        return f".{symbol.name}()"
    raise ValueError(f"unknown symbol kind: {symbol.kind!r}")


def norm_label(label: str) -> str:
    """The searchable form of a label. Lowercase, and nothing else."""
    return label.lower()


def location(lineno: int) -> str:
    """Format a 1-based line as the graph's ``L<n>`` location string."""
    return f"L{lineno}"
