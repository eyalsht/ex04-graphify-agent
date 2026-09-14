"""Fail if a hardcoded secret, model id, absolute path, or TARGET-REPO literal is in ``src/``.

Config belongs in ``config/*.json`` or CLI arguments, secrets in ``os.environ`` only
(CLAUDE.md §3). Scans ``src/`` only, so the detection patterns below do not flag this file.
Exit 1 on violation, else 0.

The last two rules are what this fork adds over its origin project. EX04 became impossible to
retarget because library code carried literals like ``"polygons/polygons.py"`` and
``_INIT_ID = "polygons_polygons_polygon_init"`` — both of which sail past a secrets-and-paths
gate. A node id or a target source path in ``src/`` means the library has been welded to one
repository, so it is a build failure here.

Escape hatch for a deliberate, reviewed exception: end the line with ``# atlas: allow-literal``.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_ALLOW = "# atlas: allow-literal"

# Detection patterns (kept narrow to avoid false positives):
_KEY = r"(sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{12,}|AIza[0-9A-Za-z_\-]{20,})"
_MODEL = r"[\"'](?:gemini|claude|gpt|llama|mistral)-[A-Za-z0-9.\-]+[\"']"
_ABSPATH = r"[\"'](?:[A-Za-z]:\\\\|/home/|/Users/|/mnt/)"
# A repo-relative path literal: has a separator and a concrete file extension. Config keys and
# node-id fragments have no "/", so this fires only on real paths into a target tree.
_TARGET_PATH = r"[\"'][\w.\-]+(?:/[\w.\-]+)+\.(?:py|md|json|txt|toml|cfg|ini|ya?ml)[\"']"
# A module-level constant that looks like it pins one graph node / one target file, e.g.
# ``_BUG_NODE = "..."``, ``TARGET_SOURCE = "..."``, ``_CALC_ID = "..."``.
_PINNED_CONST = r"^\s*_?[A-Z][A-Z0-9_]*(?:_ID|_IDS|_NODE|_NODES|_TARGET|_SOURCE)\s*=\s*[\"']"

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("api-key-literal", re.compile(_KEY)),
    ("hardcoded-model-id", re.compile(_MODEL)),
    ("absolute-path", re.compile(_ABSPATH)),
    ("target-path-literal", re.compile(_TARGET_PATH)),
    ("pinned-target-constant", re.compile(_PINNED_CONST)),
)


def find_violations(root: Path) -> list[tuple[Path, int, str]]:
    """Return ``(path, line_no, label)`` for each hardcoded value found under ``src/``."""
    offenders: list[tuple[Path, int, str]] = []
    base = root / "src"
    if not base.is_dir():
        return offenders
    for path in sorted(base.rglob("*.py")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_no, line in enumerate(lines, start=1):
            if line.rstrip().endswith(_ALLOW):
                continue
            for label, pattern in _PATTERNS:
                if pattern.search(line):
                    offenders.append((path, line_no, label))
    return offenders


def main(argv: list[str] | None = None) -> int:
    root = Path(argv[0]) if argv else Path.cwd()
    offenders = find_violations(root)
    if offenders:
        print(f"No-hardcoded check FAILED — {len(offenders)} finding(s):")
        for path, line_no, label in offenders:
            print(f"  {path.relative_to(root)}:{line_no} [{label}]")
        return 1
    print("No-hardcoded check passed — no secrets, model ids, or target literals in src/.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
