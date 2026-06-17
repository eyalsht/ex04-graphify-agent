"""TDD for the provider text-extraction helper (the function_call-robustness fix).

Gemini 3.x can return a ``function_call`` part alongside text; the SDK's ``.text`` accessor
warns and may drop content. ``join_text_parts`` concatenates only the text-bearing parts so
the agent's fix node always receives the full patch text (the function_call part is ignored).
"""

from __future__ import annotations

from ex04_graphify_agent.gatekeeper.provider import join_text_parts


class _Part:
    def __init__(self, text: str | None = None) -> None:
        self.text = text


def test_join_text_parts_concatenates_text_bearing_parts() -> None:
    parts = [_Part("def f():"), _Part("\n    return 1")]
    assert join_text_parts(parts) == "def f():\n    return 1"


def test_join_text_parts_ignores_parts_without_text() -> None:
    # a function_call part exposes no usable ``.text`` -> contributes nothing
    parts = [_Part(None), _Part("real patch text")]
    assert join_text_parts(parts) == "real patch text"


def test_join_text_parts_handles_empty_and_none() -> None:
    assert join_text_parts([]) == ""
    assert join_text_parts(None) == ""
