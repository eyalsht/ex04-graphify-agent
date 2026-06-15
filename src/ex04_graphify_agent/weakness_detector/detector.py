"""WeaknessDetector — orchestrates the six PART-C signals into ranked findings.

Each signal is a pure function in ``signals_graph`` / ``signals_source`` taking the
injected ``GraphReader`` and loaded thresholds; the detector wires them, then ranks
primary (signals 1/5/6 — the real polygons.py bug) above secondary (2/3/4 noise).
``detect()`` never fills ``source_validation`` — that is the validate node's job (WD-T8).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from . import signals_graph, signals_graph_b, signals_source
from .config import default_data_root, load_thresholds
from .hypothesis import WeaknessFinding
from .ranking import rank_findings

if TYPE_CHECKING:
    from ex04_graphify_agent.graph_reader import GraphReader


class WeaknessDetector:
    """Runs the six graph-weakness signals over a single ``GraphReader``."""

    def __init__(
        self,
        reader: GraphReader,
        thresholds_path: str | Path | None = None,
        data_root: str | Path | None = None,
    ) -> None:
        self._reader = reader
        self.thresholds: dict[str, Any] = load_thresholds(thresholds_path)
        self._data_root = Path(data_root) if data_root is not None else default_data_root()

    # -- individual signals ----------------------------------------------
    def signal_1_god_node(self) -> list[WeaknessFinding]:
        return signals_graph.god_node(self._reader, self.thresholds)

    def signal_2_ambiguous_edge(self) -> list[WeaknessFinding]:
        return signals_graph.ambiguous_edge(self._reader, self.thresholds)

    def signal_3_broken_path(self) -> list[WeaknessFinding]:
        return signals_graph_b.broken_path(self._reader, self._data_root)

    def signal_4_critical_path_break(self) -> list[WeaknessFinding]:
        return signals_graph_b.critical_path_break(self._reader)

    def signal_5_isolated_cluster(self) -> list[WeaknessFinding]:
        return signals_graph_b.isolated_cluster(self._reader, self.thresholds)

    def signal_6_semantic_duplicate(self) -> list[WeaknessFinding]:
        return signals_source.semantic_duplicate(self._reader, self._data_root)

    # -- orchestration ----------------------------------------------------
    def detect(self) -> list[WeaknessFinding]:
        """Run all six signals and return findings ranked primary-first (WD-T6)."""
        findings: list[WeaknessFinding] = []
        findings += self.signal_1_god_node()
        findings += self.signal_5_isolated_cluster()
        findings += self.signal_6_semantic_duplicate()
        findings += self.signal_2_ambiguous_edge()
        findings += self.signal_3_broken_path()
        findings += self.signal_4_critical_path_break()
        return rank_findings(findings, self._reader)
