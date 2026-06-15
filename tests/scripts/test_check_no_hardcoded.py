"""Tests for scripts/check_no_hardcoded.py."""

from __future__ import annotations

from pathlib import Path

import check_no_hardcoded


def _src(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "src" / "mod.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def test_hardcoded_model_id_flagged(tmp_path: Path) -> None:
    _src(tmp_path, 'MODEL = "gemini-2.0-flash"\n')
    labels = [label for _, _, label in check_no_hardcoded.find_violations(tmp_path)]
    assert "hardcoded-model-id" in labels


def test_api_key_literal_flagged(tmp_path: Path) -> None:
    _src(tmp_path, 'KEY = "AIzaSyA1234567890abcdefghijklmnopqrstuv"\n')
    labels = [label for _, _, label in check_no_hardcoded.find_violations(tmp_path)]
    assert "api-key-literal" in labels


def test_clean_source_passes(tmp_path: Path) -> None:
    _src(tmp_path, 'import os\nKEY = os.environ["GEMINI_API_KEY"]\n')
    assert check_no_hardcoded.find_violations(tmp_path) == []
    assert check_no_hardcoded.main([str(tmp_path)]) == 0
