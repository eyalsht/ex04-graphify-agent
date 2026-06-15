"""apply_unified_diff — reconstruct the fixed source from a ``context.make_diff`` output.

``AgentState.fix_diff`` is a ``difflib.unified_diff`` string (original vs fixed
``polygons.py``). To run ``check_correctness`` on a completed run's actual fix, ``compare``
reconstructs the fixed text by applying this diff to the original source — never by
re-deriving or estimating the content (R10.5).
"""

from __future__ import annotations

import re

_HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def apply_unified_diff(original: str, diff_text: str) -> str:
    """Apply a unified diff (as produced by ``context.make_diff``) to ``original``."""
    if not diff_text.strip():
        return original
    src_lines = original.splitlines(keepends=True)
    out: list[str] = []
    src_idx = 0
    for hunk_src_start, hunk_lines in _iter_hunks(diff_text):
        out.extend(src_lines[src_idx : hunk_src_start - 1])
        src_idx = hunk_src_start - 1
        for line in hunk_lines:
            tag, content = line[0], line[1:]
            if tag == " ":
                out.append(content)
                src_idx += 1
            elif tag == "-":
                src_idx += 1
            elif tag == "+":
                out.append(content)
    out.extend(src_lines[src_idx:])
    return "".join(out)


def _iter_hunks(diff_text: str) -> list[tuple[int, list[str]]]:
    """Parse ``@@ -a,b +c,d @@`` hunks into ``(original_start_line, body_lines)``."""
    hunks: list[tuple[int, list[str]]] = []
    current: list[str] | None = None
    start = 0
    for line in diff_text.splitlines(keepends=True):
        match = _HUNK_HEADER.match(line)
        if match:
            if current is not None:
                hunks.append((start, current))
            start = int(match.group(1))
            current = []
            continue
        if current is not None and line and line[0] in (" ", "-", "+"):
            current.append(line)
    if current is not None:
        hunks.append((start, current))
    return hunks
