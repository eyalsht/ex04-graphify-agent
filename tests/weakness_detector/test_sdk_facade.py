"""SDK façade: detect_weaknesses delegates to WeaknessDetector (PHASE3-089, SDK-first)."""

from __future__ import annotations

from ex04_graphify_agent.sdk import detect_weaknesses
from ex04_graphify_agent.weakness_detector import WeaknessFinding


def test_detect_weaknesses_returns_ranked_findings() -> None:
    findings = detect_weaknesses()
    assert findings and isinstance(findings[0], WeaknessFinding)
    assert findings[0].priority == "primary"
