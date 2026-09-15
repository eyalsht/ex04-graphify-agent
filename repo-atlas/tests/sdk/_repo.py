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


def build_large_repo(tmp_path: Path, name: str = "bigproj", modules: int = 6) -> Path:
    """A repo big enough for the token comparison to mean anything.

    Graph-guided retrieval only pays off once a repo is larger than the context it would
    assemble: on a seven-line module, the vault plus a source window costs *more* than
    dumping the file. That crossover is a real property of the design (recorded in
    ``docs/KNOWN_LIMITATIONS.md``), not a bug — so a comparison test needs a repo on the
    far side of it, or it asserts an artifact of its own fixture.
    """
    repo = tmp_path / name
    (repo / "pkg").mkdir(parents=True)
    for index in range(modules):
        body = [f'"""Module {index}."""', "", "", f"class Widget{index}:"]
        body += [f"    def method_{step}(self):\n        return {step}\n" for step in range(8)]
        body += ["", f"def build_{index}():", f"    return Widget{index}()", ""]
        (repo / "pkg" / f"mod_{index}.py").write_text("\n".join(body), encoding="utf-8")
    (repo / "README.md").write_text("# Big Proj\n", encoding="utf-8")
    return repo
