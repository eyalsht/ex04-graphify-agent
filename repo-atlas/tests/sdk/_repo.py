"""Shared synthetic-repo builder for ``sdk`` tests.

Split out from the test modules so no single test file grows toward the 150-line cap
(CLAUDE.md §3). Mirrors ``tests/extractor/test_build.py``'s fixture repo so the derived
node ids (``pkg_shapes``, ``pkg_shapes_shape``, ``pkg_shapes_shape_area``,
``pkg_shapes_make``) are already known-good elsewhere in the suite.
"""

from __future__ import annotations

from pathlib import Path

_MODULE = """class Shape:
    def area(self):
        return 0


def make(kind):
    return Shape()
"""


def build_repo(tmp_path: Path, name: str = "proj") -> Path:
    """A minimal but non-trivial Python repo: one module, one class, a method, a function."""
    repo = tmp_path / name
    (repo / "pkg").mkdir(parents=True)
    (repo / "pkg" / "shapes.py").write_text(_MODULE, encoding="utf-8")
    (repo / "README.md").write_text("# Proj\n", encoding="utf-8")
    return repo
