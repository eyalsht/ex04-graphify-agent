"""Id derivation (``docs/EXTRACTOR_SPEC.md`` §2). Pure functions, no I/O.

The rules here are counterintuitive enough that a plausible implementation produces a
subtly wrong graph. Three in particular:

* a trailing ``.py`` is stripped **before** slugging — slug first and you get ``..._mod_py``;
* dunder stripping is total on both sides for *symbols* (``__init__`` -> ``init``) but is
  not applied to *paths*, so ``pkg/__init__.py`` keeps its dunder segment;
* methods chain off the **class** id while module-level functions chain off the **module**
  id, which is the only thing distinguishing them.
"""

from __future__ import annotations

from repo_atlas.extractor.models import Symbol

_PY_SUFFIX = ".py"
_SEPARATORS = ("/", "-", ".")


def slug(text: str) -> str:
    """Lowercase, then fold path and name punctuation to underscores."""
    folded = text.lower()
    for separator in _SEPARATORS:
        folded = folded.replace(separator, "_")
    return folded


def module_id(source_file: str) -> str:
    """Id of a file node. Strips one trailing ``.py`` BEFORE slugging (§2 rule 1)."""
    stem = source_file[: -len(_PY_SUFFIX)] if source_file.endswith(_PY_SUFFIX) else source_file
    return slug(stem)


def class_id(module: str, name: str) -> str:
    """Id of a class, chained off its module."""
    return f"{module}_{name.lower()}"


def function_id(module: str, name: str) -> str:
    """Id of a module-level function. Underscores are NOT stripped (§2, methods only)."""
    return f"{module}_{name.lower()}"


def method_id(owner: str, name: str) -> str:
    """Id of a method, chained off its CLASS id, with dunders stripped both sides."""
    return f"{owner}_{name.strip('_').lower()}"


def external_id(name: str) -> str:
    """Id of an unresolved external symbol: bare lowercase, no namespace (§2 rule 4)."""
    return name.lower()


def rationale_id(module: str, lineno: int) -> str:
    """Id of a marker-comment node, keyed by its 1-based line."""
    return f"{module}_rationale_{lineno}"


def symbol_id(owner: str, symbol: Symbol) -> str:
    """Dispatch to the right rule. ``owner`` is the module id, or the class id for a method."""
    if symbol.kind == "class":
        return class_id(owner, symbol.name)
    if symbol.kind == "function":
        return function_id(owner, symbol.name)
    if symbol.kind == "method":
        return method_id(owner, symbol.name)
    raise ValueError(f"unknown symbol kind: {symbol.kind!r}")


def qualified_name(symbol: Symbol) -> str:
    """Dotted source-level name, used to resolve call targets and detect collisions."""
    return f"{symbol.parent}.{symbol.name}" if symbol.parent else symbol.name
