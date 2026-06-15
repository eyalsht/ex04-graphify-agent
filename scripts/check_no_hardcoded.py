"""Fail if a hardcoded secret, provider model id, or absolute path appears in ``src/``.

Config belongs in ``config/*.json`` and secrets in ``os.environ`` only (CLAUDE.md §3, D6).
Scans ``src/`` only (so the detection patterns below do not flag this script). Exit 1 on
violation, else 0. Mirrors agent-debate's committed CI gate.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Detection patterns (kept narrow to avoid false positives on stubs):
_KEY = r"(sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{12,}|AIza[0-9A-Za-z_\-]{20,})"
_MODEL = r"[\"'](?:gemini|claude|gpt|llama|mistral)-[A-Za-z0-9.\-]+[\"']"
_ABSPATH = r"[\"'](?:[A-Za-z]:\\\\|/home/|/Users/|/mnt/)"
_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("api-key-literal", re.compile(_KEY)),
    ("hardcoded-model-id", re.compile(_MODEL)),
    ("absolute-path", re.compile(_ABSPATH)),
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
    print("No-hardcoded check passed — no secrets/model-ids/absolute paths in src/.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
