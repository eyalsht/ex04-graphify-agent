"""Fail if any first-party Python file exceeds the 150-line limit (CLAUDE.md §3).

Scans ``src/``, ``tests/``, ``scripts/``. Exit 1 (and print offenders) on violation,
else exit 0. Mirrors agent-debate's committed CI gate.
"""

from __future__ import annotations

import sys
from pathlib import Path

MAX_LINES = 150
SCAN_DIRS = ("src", "tests", "scripts")


def _line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for _ in handle)


def find_violations(root: Path, max_lines: int = MAX_LINES) -> list[tuple[Path, int]]:
    """Return ``(path, line_count)`` for every ``.py`` file over ``max_lines``."""
    offenders: list[tuple[Path, int]] = []
    for scan_dir in SCAN_DIRS:
        base = root / scan_dir
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.py")):
            count = _line_count(path)
            if count > max_lines:
                offenders.append((path, count))
    return offenders


def main(argv: list[str] | None = None) -> int:
    root = Path(argv[0]) if argv else Path.cwd()
    offenders = find_violations(root)
    if offenders:
        print(f"File-size check FAILED — {len(offenders)} file(s) over {MAX_LINES} lines:")
        for path, count in offenders:
            print(f"  {path.relative_to(root)}: {count} lines")
        return 1
    print(f"File-size check passed — all files within {MAX_LINES} lines.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
