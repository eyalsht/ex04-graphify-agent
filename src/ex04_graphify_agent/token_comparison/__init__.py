"""token_comparison — graph-guided vs naive metrics + reports/ output.

See ``docs/PRD_token_comparison.md``. Phase 6.
"""

from __future__ import annotations

from .correctness import check_correctness
from .graph_diff import GraphDiff, diff_graphs
from .models import ComparisonResult, RunMetrics
from .runner import TokenComparison

__all__ = [
    "ComparisonResult",
    "GraphDiff",
    "RunMetrics",
    "TokenComparison",
    "check_correctness",
    "diff_graphs",
]
