"""weakness_detector — the six PART-C graph-weakness signals → bug-class hypotheses.

See ``docs/PRD_weakness_detector.md``. The detector reads the graph (via ``GraphReader``)
and emits one ``WeaknessFinding`` per triggered signal, tagged EXTRACTED / INFERRED /
AMBIGUOUS with matching language strength. Only ``agent_workflow``'s validate node fills
in ``source_validation`` after a source read.
"""

from __future__ import annotations

from .detector import WeaknessDetector
from .hypothesis import Priority, SourceValidation, Tag, WeaknessFinding

__all__ = [
    "Priority",
    "SourceValidation",
    "Tag",
    "WeaknessDetector",
    "WeaknessFinding",
]
