"""TDD for TokenRecord + TokenLogger JSONL dump (PHASE4-002).

``runs_dir`` is a required constructor argument here (ADR-0003: every path is a parameter,
never discovered by walking up the filesystem), unlike the origin project's cached
``default_runs_dir()``.
"""

from __future__ import annotations

import json
from pathlib import Path

from repo_atlas.gatekeeper import TokenLogger, TokenRecord


def _record(node: str = "plan") -> TokenRecord:
    return TokenRecord(
        run_id="run-1",
        run_type="graph_guided",
        node=node,
        input_tokens=10,
        output_tokens=4,
        model="test-model",
    )


def test_token_record_fields() -> None:
    r = _record()
    assert r.run_id == "run-1"
    assert r.run_type == "graph_guided"
    assert r.node == "plan"
    assert r.input_tokens == 10
    assert r.output_tokens == 4
    assert r.model == "test-model"


def test_logger_records_appended(tmp_path: Path) -> None:
    logger = TokenLogger(runs_dir=tmp_path)
    logger.record(_record("plan"))
    logger.record(_record("fix"))
    assert [r.node for r in logger.records] == ["plan", "fix"]


def test_logger_dump_writes_jsonl(tmp_path: Path) -> None:
    logger = TokenLogger(runs_dir=tmp_path)
    logger.record(_record("plan"))
    logger.record(_record("fix"))
    out = tmp_path / "run-1.jsonl"
    logger.dump(out)
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    first = json.loads(lines[0])
    assert first["node"] == "plan"
    assert first["input_tokens"] == 10
    assert first["model"] == "test-model"
    assert set(first) == {"run_id", "run_type", "node", "input_tokens", "output_tokens", "model"}


def test_logger_dump_default_path_uses_run_id(tmp_path: Path) -> None:
    logger = TokenLogger(runs_dir=tmp_path)
    logger.record(_record("plan"))
    path = logger.dump()
    assert path == tmp_path / "run-1.jsonl"
    assert path.exists()


def test_logger_dump_creates_missing_runs_dir(tmp_path: Path) -> None:
    nested = tmp_path / "nested" / "runs"
    logger = TokenLogger(runs_dir=nested)
    logger.record(_record())
    path = logger.dump()
    assert path.exists()
