"""Fail if a shipped anti-pattern appears in ``src/`` (CLAUDE.md §3).

Flags: ``NotImplementedError`` shipped to main, bare ``print(`` debug calls (the CLI uses
``typer.echo``), and ``--no-verify`` traces. Scans ``src/`` only. Exit 1 on violation,
else 0. Mirrors agent-debate's committed CI gate.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("NotImplementedError", re.compile(r"\bNotImplementedError\b")),
    ("debug-print", re.compile(r"(?<![\w.])print\s*\(")),
    ("no-verify", re.compile(r"--no-verify")),
)


def find_violations(root: Path) -> list[tuple[Path, int, str]]:
    """Return ``(path, line_no, label)`` for each anti-pattern found under ``src/``."""
    offenders: list[tuple[Path, int, str]] = []
    base = root / "src"
    if not base.is_dir():
        return offenders
    for path in sorted(base.rglob("*.py")):
        lines = path.read_text(encoding="utf-8").splitlines()
        for line_no, line in enumerate(lines, start=1):
            for label, pattern in _PATTERNS:
                if pattern.search(line):
                    offenders.append((path, line_no, label))
    return offenders


def main(argv: list[str] | None = None) -> int:
    root = Path(argv[0]) if argv else Path.cwd()
    offenders = find_violations(root)
    if offenders:
        print(f"Anti-pattern check FAILED — {len(offenders)} finding(s):")
        for path, line_no, label in offenders:
            print(f"  {path.relative_to(root)}:{line_no} [{label}]")
        return 1
    print("Anti-pattern check passed — no shipped anti-patterns in src/.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
