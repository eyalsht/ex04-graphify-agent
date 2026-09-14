"""Gate tests for ``scripts/check_no_hardcoded.py``.

The last two cases are the point of this fork: a target-repo path literal and a pinned node-id
constant must FAIL the build, because those are exactly what welded the origin project to one
repository while passing its secrets-and-paths gate.
"""

from __future__ import annotations

from pathlib import Path

import check_no_hardcoded as gate


def _src(tmp_path: Path, body: str) -> Path:
    module = tmp_path / "src" / "pkg" / "mod.py"
    module.parent.mkdir(parents=True)
    module.write_text(body, encoding="utf-8")
    return module


def _labels(tmp_path: Path) -> list[str]:
    return [label for _, _, label in gate.find_violations(tmp_path)]


def test_clean_source_passes(tmp_path: Path) -> None:
    _src(tmp_path, 'import os\n\nKEY = os.environ["ATLAS_API_KEY"]\n')
    assert gate.find_violations(tmp_path) == []


def test_missing_src_dir_is_not_a_violation(tmp_path: Path) -> None:
    assert gate.find_violations(tmp_path) == []


def test_api_key_literal_flagged(tmp_path: Path) -> None:
    _src(tmp_path, 'KEY = "AIzaSyA1234567890abcdefghijklmnopqrst"\n')
    assert "api-key-literal" in _labels(tmp_path)


def test_model_id_literal_flagged(tmp_path: Path) -> None:
    _src(tmp_path, 'MODEL = "gemini-2.5-flash"\n')
    assert "hardcoded-model-id" in _labels(tmp_path)


def test_absolute_path_flagged(tmp_path: Path) -> None:
    _src(tmp_path, 'ROOT = "/home/user/project"\n')
    assert "absolute-path" in _labels(tmp_path)


def test_target_path_literal_flagged(tmp_path: Path) -> None:
    _src(tmp_path, 'source = open("polygons/polygons.py").read()\n')
    assert "target-path-literal" in _labels(tmp_path)


def test_pinned_node_id_constant_flagged(tmp_path: Path) -> None:
    _src(tmp_path, '_INIT_ID = "polygons_polygons_polygon_init"\n')
    assert "pinned-target-constant" in _labels(tmp_path)


def test_config_key_literal_is_not_flagged(tmp_path: Path) -> None:
    """Underscored config keys are legitimate; only pinned *_ID/_TARGET constants are not."""
    _src(tmp_path, 'top_k = config["vault"]["hot_md_top_k_value"]\n')
    assert gate.find_violations(tmp_path) == []


def test_allow_literal_comment_suppresses(tmp_path: Path) -> None:
    _src(tmp_path, 'DEFAULT = "config/atlas.json"  # atlas: allow-literal\n')
    assert gate.find_violations(tmp_path) == []


def test_main_reports_exit_codes(tmp_path: Path) -> None:
    assert gate.main([str(tmp_path)]) == 0
    _src(tmp_path, 'MODEL = "claude-opus-5"\n')
    assert gate.main([str(tmp_path)]) == 1
