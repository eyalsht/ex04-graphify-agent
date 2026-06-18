"""Run the keyless EX04 self-grade (R8.9) and exit non-zero if any check fails.

Runnable via ``uv run python scripts/self_grade.py``; NOT collected by pytest
(it lives in ``scripts/``, outside ``testpaths``). Reuses the committed gate scripts
(ruff, mypy, coverage, file-size, no-hardcoded, anti-patterns) via the config-driven
subprocess runner, so no provider API key is ever required.
"""

from __future__ import annotations

import sys

from ex04_graphify_agent.sdk import Ex04Sdk


def main(argv: list[str] | None = None) -> int:
    """Print the self-grade report; return 0 when every check passes, else 1."""
    report = Ex04Sdk().self_grade()
    print(report.render())
    return 0 if report.passed else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
