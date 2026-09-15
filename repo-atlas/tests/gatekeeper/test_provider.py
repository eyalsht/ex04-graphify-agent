"""TDD for the Gemini adapter's pure helpers (PHASE4-006).

``GeminiClient`` itself needs a real key and the optional ``google-genai`` SDK, so it stays
``pragma: no cover`` for a manual run (as in the origin project) and this package must import
cleanly without that SDK installed at all (proven by ``test_module_imports_without_sdk``).
The two defects it fixes — messages flattened to one string (dropping roles) and provider
errors never surfacing as ``RateLimitError`` (so retry was dead) — are each isolated into a
pure, fully-tested helper below.
"""

from __future__ import annotations

import sys

import pytest

from repo_atlas.gatekeeper.client import RateLimitError
from repo_atlas.gatekeeper.provider import (
    as_rate_limit_error,
    gemini_role,
    join_text_parts,
)


def test_module_imports_without_sdk_installed() -> None:
    assert "google" not in sys.modules
    assert "google.genai" not in sys.modules


class _Part:
    def __init__(self, text: str | None = None) -> None:
        self.text = text


def test_join_text_parts_concatenates_text_bearing_parts() -> None:
    parts = [_Part("def f():"), _Part("\n    return 1")]
    assert join_text_parts(parts) == "def f():\n    return 1"


def test_join_text_parts_ignores_parts_without_text() -> None:
    parts = [_Part(None), _Part("real patch text")]
    assert join_text_parts(parts) == "real patch text"


def test_join_text_parts_handles_empty_and_none() -> None:
    assert join_text_parts([]) == ""
    assert join_text_parts(None) == ""


@pytest.mark.parametrize(
    ("role", "expected"),
    [("assistant", "model"), ("model", "model"), ("user", "user"), (None, "user"), ("", "user")],
)
def test_gemini_role_maps_assistant_to_model(role: str | None, expected: str) -> None:
    # Defect: flattening messages into one string drops roles, killing multi-turn.
    # Gemini's contents API only accepts "user"/"model" -- this is the round-trip mapping.
    assert gemini_role(role) == expected


class _FakeCodedError(Exception):
    def __init__(self, code: int) -> None:
        super().__init__(f"error {code}")
        self.code = code


def test_as_rate_limit_error_maps_429_status_code() -> None:
    mapped = as_rate_limit_error(_FakeCodedError(429))
    assert isinstance(mapped, RateLimitError)


class _FakeResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


class _FakeHttpError(Exception):
    def __init__(self, status_code: int) -> None:
        super().__init__("http error")
        self.response = _FakeResponse(status_code)


def test_as_rate_limit_error_maps_response_status_code_429() -> None:
    mapped = as_rate_limit_error(_FakeHttpError(429))
    assert isinstance(mapped, RateLimitError)


def test_as_rate_limit_error_maps_resource_exhausted_message() -> None:
    mapped = as_rate_limit_error(RuntimeError("429 RESOURCE_EXHAUSTED: quota"))
    assert isinstance(mapped, RateLimitError)


def test_as_rate_limit_error_returns_none_for_unrelated_error() -> None:
    assert as_rate_limit_error(ValueError("bad request")) is None


def test_as_rate_limit_error_returns_none_for_other_status_code() -> None:
    assert as_rate_limit_error(_FakeCodedError(500)) is None
