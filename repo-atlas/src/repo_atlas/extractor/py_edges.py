"""``FileSymbols`` + ``FileNodes`` -> ``RawEdge`` (``docs/EXTRACTOR_SPEC.md`` §5, §6).

The selection rules here are narrow on purpose. ``contains`` reaches top-level symbols
only, ``rationale_for`` always points at the module even when the comment sits inside a
function, and a call becomes an edge only when it is lexically inside a definition AND
its callee is a bare name defined in the same file. That last rule is why a file with
dozens of call sites contributes almost no call edges: builtins and attribute calls are
not facts about *this* repo's internal structure.
"""

from __future__ import annotations

from repo_atlas.extractor import confidence, ids, labels
from repo_atlas.extractor.models import ORIGIN_AST, ORIGIN_SCAN, FileSymbols, RawEdge, Symbol
from repo_atlas.extractor.py_nodes import FileNodes

CONTAINS = "contains"
METHOD = "method"
INHERITS = "inherits"
CALLS = "calls"
RATIONALE_FOR = "rationale_for"
CALL_CONTEXT = "call"


def _edge(
    relation: str,
    source: str,
    target: str,
    parsed: FileSymbols,
    lineno: int,
    context: str | None = None,
) -> RawEdge:
    label, score = confidence.for_origin(ORIGIN_SCAN if parsed.degraded else ORIGIN_AST)
    return RawEdge(
        source=source,
        target=target,
        relation=relation,
        confidence=label,
        confidence_score=score,
        source_file=parsed.source_file,
        source_location=labels.location(lineno),
        context=context,
    )


def _structural_edges(parsed: FileSymbols, built: FileNodes) -> list[RawEdge]:
    edges: list[RawEdge] = []
    for symbol in parsed.symbols:
        node_id = built.symbol_ids[ids.qualified_name(symbol)]
        edges.extend(_symbol_edges(symbol, node_id, parsed, built))
    return edges


def _symbol_edges(
    symbol: Symbol, node_id: str, parsed: FileSymbols, built: FileNodes
) -> list[RawEdge]:
    edges: list[RawEdge] = []
    if symbol.kind == "method" and symbol.parent is not None:
        owner = built.symbol_ids.get(symbol.parent)
        if owner is not None:
            edges.append(_edge(METHOD, owner, node_id, parsed, symbol.lineno))
    elif symbol.parent is None:
        edges.append(_edge(CONTAINS, built.module_id, node_id, parsed, symbol.lineno))
    for base in symbol.bases:
        target = built.symbol_ids.get(base) or built.external_ids.get(base)
        if target is not None:
            edges.append(_edge(INHERITS, node_id, target, parsed, symbol.lineno))
    return edges


def _call_edges(parsed: FileSymbols, built: FileNodes) -> list[RawEdge]:
    """A call is an edge only when it is inside a definition and resolves in this file."""
    edges: list[RawEdge] = []
    for call in parsed.calls:
        if call.enclosing is None or call.is_attribute:
            continue
        caller = built.symbol_ids.get(call.enclosing)
        callee = built.symbol_ids.get(call.callee)
        if caller is None or callee is None:
            continue
        edges.append(_edge(CALLS, caller, callee, parsed, call.lineno, context=CALL_CONTEXT))
    return edges


def _rationale_edges(parsed: FileSymbols, built: FileNodes) -> list[RawEdge]:
    """Inverted direction, and always to the module — never the enclosing function."""
    return [
        _edge(
            RATIONALE_FOR,
            ids.rationale_id(built.module_id, marker.lineno),
            built.module_id,
            parsed,
            marker.lineno,
        )
        for marker in parsed.markers
    ]


def build_edges(parsed: FileSymbols, built: FileNodes) -> list[RawEdge]:
    """Every edge this file contributes, in a deterministic order."""
    return [
        *_structural_edges(parsed, built),
        *_call_edges(parsed, built),
        *_rationale_edges(parsed, built),
    ]
