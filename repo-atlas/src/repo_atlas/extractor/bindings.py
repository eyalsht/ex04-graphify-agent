"""Resolving import statements to nodes in other modules.

Separated from edge emission because this is the part that reasons about Python's import
semantics — dotted paths, relative levels, aliases, submodules — while ``resolve.py`` only
turns the answers into edges.
"""

from __future__ import annotations

from collections.abc import Mapping

from repo_atlas.extractor.models import CallSite, ImportRecord
from repo_atlas.extractor.py_nodes import FileNodes

_INIT = "__init__"


def dotted(source_file: str) -> str:
    """``pkg/mod.py`` -> ``pkg.mod``; ``pkg/__init__.py`` -> ``pkg``."""
    stem = source_file[:-3] if source_file.endswith(".py") else source_file
    parts = stem.split("/")
    if parts and parts[-1] == _INIT:
        parts = parts[:-1]
    return ".".join(parts)


def target_module(record: ImportRecord, importer: str) -> str:
    """Absolute module name an import refers to, resolving relative levels."""
    if record.level == 0:
        return record.module
    package = dotted(importer).split(".")[:-1]
    base = package[: len(package) - (record.level - 1)] if record.level > 1 else package
    return ".".join([*base, record.module]) if record.module else ".".join(base)


def bind_names(record: ImportRecord, target: FileNodes) -> dict[str, str]:
    """Map each imported name to the node it names in the target module, when it has one."""
    bound: dict[str, str] = {}
    for name in record.names:
        node_id = target.symbol_ids.get(name.original)
        if node_id is not None:
            bound[name.bound] = node_id
    return bound


def import_line(imports: tuple[ImportRecord, ...]) -> int:
    """Line to anchor a submodule reference to — the first import in the file."""
    return imports[0].lineno if imports else 1


def bind_modules(
    imports: tuple[ImportRecord, ...], by_module: Mapping[str, str], importer: str
) -> dict[str, str]:
    """Map a local name to an imported repo *module*, so ``mod.func()`` can resolve."""
    bound: dict[str, str] = {}
    for record in imports:
        target = target_module(record, importer)
        # `import pkg.mod as m` — the alias names the module itself.
        for name in record.names:
            aliased = by_module.get(name.original)
            if aliased is not None and aliased != importer:
                bound[name.bound] = aliased
                continue
            # `from pkg import mod` — the bound name is a submodule of the target.
            submodule = by_module.get(f"{target}.{name.original}" if target else name.original)
            if submodule is not None and submodule != importer:
                bound[name.bound] = submodule
    return bound


def resolve_call(
    call: CallSite,
    bindings: Mapping[str, str],
    modules: Mapping[str, str],
    built: Mapping[str, FileNodes],
) -> str | None:
    """The node a cross-file call targets, or None when it cannot be resolved honestly."""
    if not call.is_attribute:
        return bindings.get(call.callee)
    # obj.method() only resolves when obj is a module we imported; anything else would
    # need type inference, and a guessed edge is worse than a missing one.
    module_path = modules.get(call.receiver or "")
    if module_path is None:
        return None
    return built[module_path].symbol_ids.get(call.callee)
