"""The extractor's data contract (``docs/EXTRACTOR_SPEC.md`` §1).

Two layers live here. ``Symbol``/``CallSite``/``MarkerComment``/``FileSymbols`` are the
*intermediate* representation: what parsing one source file yields, independent of graph
shape. ``RawNode``/``RawEdge`` are the *graph* representation that serializes into
``graph.json``. Keeping them apart is what lets node extraction and edge extraction be
written against each other without either owning the other's vocabulary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

EXTRACTED = "EXTRACTED"
INFERRED = "INFERRED"
AMBIGUOUS = "AMBIGUOUS"

ORIGIN_AST = "ast"
ORIGIN_SCAN = "scan"


@dataclass(frozen=True)
class Symbol:
    """A class, module-level function, or method found in one file."""

    kind: str  # "class" | "function" | "method"
    name: str
    lineno: int
    parent: str | None = None  # enclosing class name, for methods
    bases: tuple[str, ...] = ()  # base-class names as written, for classes


@dataclass(frozen=True)
class CallSite:
    """One call expression, with enough context to apply the §5 selection rule."""

    callee: str  # the bare Name, or the attribute's final segment
    lineno: int
    enclosing: str | None = None  # symbol name the call sits inside; None at module level
    is_attribute: bool = False  # True for obj.method() — never yields an edge


@dataclass(frozen=True)
class MarkerComment:
    """A whole-line TODO/FIXME/XXX/HACK comment (§8)."""

    text: str  # the stripped comment line, "#" retained
    lineno: int


@dataclass(frozen=True)
class FileSymbols:
    """Everything one source file yields. ``degraded`` means ast.parse failed (§7)."""

    source_file: str  # repo-relative POSIX path
    degraded: bool = False
    symbols: tuple[Symbol, ...] = ()
    calls: tuple[CallSite, ...] = ()
    markers: tuple[MarkerComment, ...] = ()


@dataclass(frozen=True)
class RawNode:
    """A graph node, ready to serialize (§1)."""

    id: str
    label: str
    norm_label: str
    file_type: str  # "code" | "rationale"
    source_file: str  # "" for external symbols
    source_location: str | None  # "L<n>"; "" for external symbols
    origin: str  # ORIGIN_AST | ORIGIN_SCAN

    def to_dict(self) -> dict[str, Any]:
        """Serialize with the reference graph's key name for origin (``_origin``)."""
        return {
            "label": self.label,
            "file_type": self.file_type,
            "source_file": self.source_file,
            "source_location": self.source_location,
            "_origin": self.origin,
            "norm_label": self.norm_label,
            "id": self.id,
        }


@dataclass(frozen=True)
class RawEdge:
    """A graph edge, ready to serialize (§1). ``context`` is omitted when absent."""

    source: str
    target: str
    relation: str
    confidence: str
    confidence_score: float
    source_file: str
    source_location: str | None
    weight: float = 1.0
    context: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"relation": self.relation}
        if self.context is not None:
            payload["context"] = self.context
        payload.update(
            {
                "confidence": self.confidence,
                "source_file": self.source_file,
                "source_location": self.source_location,
                "weight": self.weight,
                "confidence_score": self.confidence_score,
                "source": self.source,
                "target": self.target,
            }
        )
        return payload
