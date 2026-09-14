"""``FileSymbols`` -> ``RawNode`` (``docs/EXTRACTOR_SPEC.md`` §1-§6).

Also the place that resolves each symbol to its owner id, which is what distinguishes a
method (chained off its class) from a module-level function (chained off its module).
The resulting ``symbol_ids`` map is handed to the edge layer so both sides agree on
exactly one id per construct.
"""

from __future__ import annotations

from dataclasses import dataclass

from repo_atlas.extractor import ids, labels
from repo_atlas.extractor.models import ORIGIN_AST, ORIGIN_SCAN, FileSymbols, RawNode, Symbol

CODE = "code"
RATIONALE = "rationale"


@dataclass(frozen=True)
class FileNodes:
    """Nodes from one file, plus the id map the edge layer needs to reference them."""

    module_id: str
    nodes: tuple[RawNode, ...]
    symbol_ids: dict[str, str]  # qualified source name -> node id
    external_ids: dict[str, str]  # base-class text as written -> node id


def _origin(parsed: FileSymbols) -> str:
    return ORIGIN_SCAN if parsed.degraded else ORIGIN_AST


def _owner(module: str, symbol: Symbol, symbol_ids: dict[str, str]) -> str:
    """A method chains off its class; everything else off its module (or nesting parent)."""
    if symbol.parent is None:
        return module
    return symbol_ids.get(symbol.parent, module)


def _external_name(base: str) -> str:
    """``mod.Base`` resolves on its final segment, so one external is one node."""
    return base.rsplit(".", maxsplit=1)[-1]


def build_file_nodes(parsed: FileSymbols, marker_limit: int | None = None) -> FileNodes:
    """Build every node this file contributes, and the id maps that address them."""
    module = ids.module_id(parsed.source_file)
    origin = _origin(parsed)
    nodes: list[RawNode] = [
        RawNode(
            id=module,
            label=labels.module_label(parsed.source_file),
            norm_label=labels.norm_label(labels.module_label(parsed.source_file)),
            file_type=CODE,
            source_file=parsed.source_file,
            source_location=labels.MODULE_LOCATION,
            origin=origin,
        )
    ]
    symbol_ids: dict[str, str] = {}
    defined: set[str] = set()

    for symbol in parsed.symbols:
        owner = _owner(module, symbol, symbol_ids)
        node_id = ids.symbol_id(owner, symbol)
        qualified = ids.qualified_name(symbol)
        if node_id in {node.id for node in nodes}:
            raise ValueError(
                f"node ids collide in {parsed.source_file}: {qualified!r} produces {node_id!r}, "
                "which is already taken — rename one construct or the graph loses it"
            )
        symbol_ids[qualified] = node_id
        defined.add(symbol.name)
        label = labels.symbol_label(symbol)
        nodes.append(
            RawNode(
                id=node_id,
                label=label,
                norm_label=labels.norm_label(label),
                file_type=CODE,
                source_file=parsed.source_file,
                source_location=labels.location(symbol.lineno),
                origin=origin,
            )
        )

    external_ids = _add_externals(parsed, defined, nodes)
    nodes.extend(_rationale_nodes(parsed, module, marker_limit))
    return FileNodes(module, tuple(nodes), symbol_ids, external_ids)


def _add_externals(parsed: FileSymbols, defined: set[str], nodes: list[RawNode]) -> dict[str, str]:
    """A base class not defined in this file still gets a node — the reference does too."""
    external_ids: dict[str, str] = {}
    for symbol in parsed.symbols:
        for base in symbol.bases:
            name = _external_name(base)
            if name in defined or base in external_ids:
                continue
            node_id = ids.external_id(name)
            external_ids[base] = node_id
            nodes.append(
                RawNode(
                    id=node_id,
                    label=base,
                    norm_label=labels.norm_label(base),
                    file_type=CODE,
                    source_file=labels.EXTERNAL_SOURCE_FILE,
                    source_location=labels.EXTERNAL_LOCATION,
                    origin=_origin(parsed),
                )
            )
    return external_ids


def _rationale_nodes(parsed: FileSymbols, module: str, marker_limit: int | None) -> list[RawNode]:
    """Marker comments come off the line stream, so they are never degraded."""
    limited = parsed.markers if marker_limit is None else parsed.markers[:marker_limit]
    return [
        RawNode(
            id=ids.rationale_id(module, marker.lineno),
            label=marker.text,
            norm_label=labels.norm_label(marker.text),
            file_type=RATIONALE,
            source_file=parsed.source_file,
            source_location=labels.location(marker.lineno),
            origin=ORIGIN_AST,
        )
        for marker in limited
    ]


def build_nodes(parsed: FileSymbols, marker_limit: int | None = None) -> list[RawNode]:
    """Convenience for callers that only want the nodes."""
    return list(build_file_nodes(parsed, marker_limit).nodes)
