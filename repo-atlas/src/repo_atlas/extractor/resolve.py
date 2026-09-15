"""Cross-file edges: what turns a pile of per-file islands into a map.

Intra-file extraction alone leaves every module disconnected, which makes betweenness
zero everywhere, communities identical to file boundaries, and any centrality ranking
collapse to raw degree — so the "most important" node becomes whichever helper one file
happens to call most. Resolving imports fixes the graph's shape, not just its size.

Only imports that land inside the repository produce edges. ``import os`` is true, but it
is not a fact about *this* repository's structure.
"""

from __future__ import annotations

from collections.abc import Mapping

from repo_atlas.extractor import bindings, labels
from repo_atlas.extractor.confidence import for_origin
from repo_atlas.extractor.models import ORIGIN_AST, FileSymbols, RawEdge
from repo_atlas.extractor.py_edges import CALL_CONTEXT, CALLS
from repo_atlas.extractor.py_nodes import FileNodes

REFERENCES = "references"


def cross_file_edges(
    parsed: Mapping[str, FileSymbols], built: Mapping[str, FileNodes]
) -> list[RawEdge]:
    """Resolve imports into ``references`` edges and cross-file ``calls`` edges."""
    # Register every name a file can be imported as, so both flat and src layouts resolve.
    all_files = set(parsed)
    by_module: dict[str, str] = {}
    for path in sorted(parsed):
        for name in bindings.module_names(path, all_files):
            by_module.setdefault(name, path)
    confidence, score = for_origin(ORIGIN_AST)
    edges: list[RawEdge] = []
    seen_references: set[tuple[str, str]] = set()

    for path, file_symbols in sorted(parsed.items()):
        importer_id = built[path].module_id
        name_bindings: dict[str, str] = {}  # local name -> node id in another module
        modules: dict[str, str] = {}  # local name -> path of an imported repo module
        for record in file_symbols.imports:
            target_path = by_module.get(bindings.target_module(record, path))
            if target_path is None or target_path == path:
                continue
            target = built[target_path]
            key = (importer_id, target.module_id)
            if key not in seen_references:
                seen_references.add(key)
                edges.append(
                    RawEdge(
                        source=importer_id,
                        target=target.module_id,
                        relation=REFERENCES,
                        confidence=confidence,
                        confidence_score=score,
                        source_file=path,
                        source_location=labels.location(record.lineno),
                    )
                )
            name_bindings.update(bindings.bind_names(record, target))
        modules.update(bindings.bind_modules(file_symbols.imports, by_module, path))
        # `from pkg import helpers` names a submodule rather than the package, so the
        # link belongs to the submodule that was actually imported.
        for module_path in sorted(set(modules.values())):
            target_id = built[module_path].module_id
            key = (importer_id, target_id)
            if key in seen_references:
                continue
            seen_references.add(key)
            edges.append(
                RawEdge(
                    source=importer_id,
                    target=target_id,
                    relation=REFERENCES,
                    confidence=confidence,
                    confidence_score=score,
                    source_file=path,
                    source_location=labels.location(bindings.import_line(file_symbols.imports)),
                )
            )
        edges.extend(
            _call_edges(file_symbols, built[path], name_bindings, modules, built, confidence, score)
        )
    return edges


def _call_edges(
    file_symbols: FileSymbols,
    built: FileNodes,
    name_bindings: Mapping[str, str],
    modules: Mapping[str, str],
    all_built: Mapping[str, FileNodes],
    confidence: str,
    score: float,
) -> list[RawEdge]:
    """Calls to an imported name, subject to the same rule as intra-file calls (§5)."""
    edges: list[RawEdge] = []
    for call in file_symbols.calls:
        if call.enclosing is None:
            continue
        target_id = bindings.resolve_call(call, name_bindings, modules, all_built)
        caller_id = built.symbol_ids.get(call.enclosing)
        if target_id is None or caller_id is None:
            continue
        edges.append(
            RawEdge(
                source=caller_id,
                target=target_id,
                relation=CALLS,
                confidence=confidence,
                confidence_score=score,
                source_file=file_symbols.source_file,
                source_location=labels.location(call.lineno),
                context=CALL_CONTEXT,
            )
        )
    return edges


__all__ = ["REFERENCES", "cross_file_edges"]
