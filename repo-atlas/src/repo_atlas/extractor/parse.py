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
from repo_atlas.extractor.comments import find_markers
from repo_atlas.extractor.models import CallSite, FileSymbols, Symbol

_FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)


class _Collector(ast.NodeVisitor):
    """Walks a module, tracking the lexical stack so parents and callers are known."""

    def __init__(self) -> None:
        self.symbols: list[Symbol] = []
        self.calls: list[CallSite] = []
        self._stack: list[tuple[str, str]] = []  # (kind, name) of enclosing definitions

    @property
    def _parent(self) -> str | None:
        return self._stack[-1][1] if self._stack else None

    @property
    def _enclosing(self) -> str | None:
        """Name of the nearest enclosing definition — what a call site is 'inside'."""
        return self._stack[-1][1] if self._stack else None

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.symbols.append(
            Symbol(
                kind="class",
                name=node.name,
                lineno=node.lineno,
                parent=self._parent,
                bases=tuple(ast.unparse(base) for base in node.bases),
            )
        )
        self._descend("class", node.name, node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._function(node)

    def visit_Call(self, node: ast.Call) -> None:
        callee, is_attribute = _callee(node.func)
        if callee:
            self.calls.append(
                CallSite(
                    callee=callee,
                    lineno=node.lineno,
                    enclosing=self._enclosing,
                    is_attribute=is_attribute,
                )
            )
        self.generic_visit(node)

    def _function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        # A def directly inside a class is a method; anywhere else it is a function,
        # nested ones chaining off their parent exactly as methods chain off a class.
        inside_class = bool(self._stack) and self._stack[-1][0] == "class"
        self.symbols.append(
            Symbol(
                kind="method" if inside_class else "function",
                name=node.name,
                lineno=node.lineno,
                parent=self._parent,
            )
        )
        self._descend("function", node.name, node)

    def _descend(self, kind: str, name: str, node: ast.AST) -> None:
        self._stack.append((kind, name))
        self.generic_visit(node)
        self._stack.pop()


def _callee(func: ast.expr) -> tuple[str, bool]:
    """The called name, and whether it came through an attribute access."""
    if isinstance(func, ast.Name):
        return func.id, False
    if isinstance(func, ast.Attribute):
        return func.attr, True
    return "", False


def parse_source(source_file: str, source: str, marker_limit: int | None = None) -> FileSymbols:
    """Parse one file's text into symbols, call sites and marker comments."""
    markers = find_markers(source, limit=marker_limit)
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return scan.scan_source(source_file, source, markers)
    collector = _Collector()
    collector.visit(tree)
    return FileSymbols(
        source_file=source_file,
        degraded=False,
        symbols=tuple(collector.symbols),
        calls=tuple(collector.calls),
        markers=markers,
    )
