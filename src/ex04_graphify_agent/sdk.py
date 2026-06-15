"""sdk — the single façade for all EX04 business logic (SDK-first non-negotiable).

CLI/GUI hold no logic; they call this. Concrete methods are added as each phase lands.
"""

from __future__ import annotations

from pathlib import Path

from .graph_reader import GraphReader
from .weakness_detector import WeaknessDetector, WeaknessFinding


def detect_weaknesses(graph_path: str | Path | None = None) -> list[WeaknessFinding]:
    """Run the six PART-C weakness signals and return ranked findings (Phase 3 façade).

    Thin delegation only — all detection logic lives in ``weakness_detector``.
    """
    return WeaknessDetector(GraphReader(graph_path)).detect()
