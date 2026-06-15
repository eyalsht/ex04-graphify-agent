"""Signal 6 — semantic duplicate (AMBIGUOUS, primary), the one signal that needs a
source-read even to *hypothesize* (WD-E1).

There is no ``similar_to`` edge in graph.json for the polygons duplication, so this signal
derives structurally (both nodes in Community 4, same source_file) AND by a *disclosed*
source-peek: it opens ``polygons/polygons.py`` and compares the ``Polygon.__init__`` field
names against the dict literal keys returned by ``calc_polygon_details()`` (the drifted
``internal_angle`` vs ``internal_angles`` duplicate). Pre-read the finding is AMBIGUOUS —
"manual source check required" — promoted only after the agent's validate node confirms.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from .hypothesis import WeaknessFinding

if TYPE_CHECKING:
    from ex04_graphify_agent.graph_reader import GraphReader

TARGET_SOURCE = "polygons/polygons.py"
_INIT_ID = "polygons_polygons_polygon_init"
_CALC_ID = "polygons_polygons_calc_polygon_details"


def _init_fields(source: str) -> list[str]:
    """Field names assigned in ``Polygon.__init__`` (``self.<name> = ...``)."""
    return sorted(set(re.findall(r"self\.(\w+)\s*=", source)))


def _dict_keys(source: str) -> list[str]:
    """String keys of the dict literal returned by ``calc_polygon_details``."""
    return sorted(set(re.findall(r'"(\w+)"\s*:', source)))


def semantic_duplicate(reader: GraphReader, data_root: Path) -> list[WeaknessFinding]:
    """Detect the dict/class field duplication via structure + a disclosed source-peek."""
    if not (reader.node_exists(_INIT_ID) and reader.node_exists(_CALC_ID)):
        return []
    init_node = reader.node(_INIT_ID)
    calc_node = reader.node(_CALC_ID)
    if init_node.community != calc_node.community:
        return []

    source_path = data_root / (init_node.source_file or TARGET_SOURCE)
    peeked = source_path.exists()
    fields = _init_fields(source_path.read_text(encoding="utf-8")) if peeked else []
    keys = _dict_keys(source_path.read_text(encoding="utf-8")) if peeked else []
    overlap = sorted(set(fields) & set(keys))

    hypo = (
        f"`{calc_node.label}`'s returned dict may duplicate the unused `Polygon` class's "
        "fields — unclear from the graph alone; manual source check of "
        f"`{init_node.source_file or TARGET_SOURCE}` required. Source-peek opened the file "
        f"and compared __init__ fields {fields} vs dict keys {keys} (overlap: {overlap})."
    )
    return [
        WeaknessFinding(
            signal=6,
            tag="AMBIGUOUS",
            hypothesis=hypo,
            priority="primary",
            source_file=init_node.source_file or TARGET_SOURCE,
            nodes=[_INIT_ID, _CALC_ID],
            edges=[],
        )
    ]
