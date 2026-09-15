"""The AST visitor: one module in, symbols and call sites out.

Split from ``parse.py`` so that file stays a thin entry point choosing between the AST
path and the degraded line scan.
"""

from __future__ import annotations

import ast

from repo_atlas.extractor.models import CallSite, ImportedName, ImportRecord, Symbol

_FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)


class Collector(ast.NodeVisitor):
    """Walks a module, tracking the lexical stack so parents and callers are known."""

    def __init__(self) -> None:
        self.symbols: list[Symbol] = []
        self.calls: list[CallSite] = []
        self.imports: list[ImportRecord] = []
        self._stack: list[tuple[str, str]] = []  # (kind, name) of enclosing definitions

    @property
    def _parent(self) -> str | None:
        """Dotted path of the enclosing definitions, e.g. ``Outer.Inner``.

        Fully qualified rather than just the immediate name so that the id map keys and
        the call sites' ``enclosing`` agree: a call inside ``Polygon.__init__`` has to
        name the same construct the node layer registered, not the bare ``__init__``.
        """
        return ".".join(name for _, name in self._stack) or None

    @property
    def _enclosing(self) -> str | None:
        """The definition a call site sits inside — the same dotted path."""
        return self._parent

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

    def visit_Import(self, node: ast.Import) -> None:
        """``import a.b`` / ``import a.b as c`` — one record per dotted name."""
        for alias in node.names:
            bound = (ImportedName(original=alias.name, bound=alias.asname),) if alias.asname else ()
            self.imports.append(ImportRecord(module=alias.name, names=bound, lineno=node.lineno))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """``from x import a, b`` — the bound names are what call sites will reference."""
        self.imports.append(
            ImportRecord(
                module=node.module or "",
                names=tuple(
                    ImportedName(original=alias.name, bound=alias.asname or alias.name)
                    for alias in node.names
                ),
                lineno=node.lineno,
                level=node.level,
            )
        )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        callee, is_attribute, receiver = callee_of(node.func)
        if callee:
            self.calls.append(
                CallSite(
                    callee=callee,
                    lineno=node.lineno,
                    enclosing=self._enclosing,
                    is_attribute=is_attribute,
                    receiver=receiver,
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


def callee_of(func: ast.expr) -> tuple[str, bool, str | None]:
    """The called name, whether it came through an attribute, and the receiver if plain.

    The receiver matters: ``mod.func()`` is the commonest way one Python module uses
    another, and without knowing that ``mod`` is an imported module the call cannot be
    resolved to a real node.
    """
    if isinstance(func, ast.Name):
        return func.id, False, None
    if isinstance(func, ast.Attribute):
        receiver = func.value.id if isinstance(func.value, ast.Name) else None
        return func.attr, True, receiver
    return "", False, None
