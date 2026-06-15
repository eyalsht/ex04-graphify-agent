"""TokenRecord + JSONL token log tagged by {run_type, node}.

The authoritative token source for ``token_comparison`` (R5.6 / R7.8): every gatekeeper
call appends one ``TokenRecord``; ``dump`` writes them as JSONL under the config-driven
``artifacts/runs/<run_id>.jsonl`` so the comparison numbers always trace back to a stored
log entry (never an estimate).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .config import default_runs_dir


@dataclass
class TokenRecord:
    """One LLM call's token accounting, tagged by run and graph node."""

    run_id: str
    run_type: str
    node: str
    input_tokens: int
    output_tokens: int
    model: str


class TokenLogger:
    """Append-only token log; dumps JSONL to ``<runs_dir>/<run_id>.jsonl``."""

    def __init__(self, runs_dir: str | Path | None = None) -> None:
        self._runs_dir = Path(runs_dir) if runs_dir is not None else default_runs_dir()
        self.records: list[TokenRecord] = []

    def record(self, record: TokenRecord) -> None:
        """Append a token record (one per LLM call)."""
        self.records.append(record)

    def dump(self, path: str | Path | None = None) -> Path:
        """Write all records as JSONL; default path derives from the first run_id."""
        out = Path(path) if path is not None else self._default_path()
        out.parent.mkdir(parents=True, exist_ok=True)
        # TokenRecord is flat — ``__dict__`` avoids ``asdict``'s recursive deep-copy.
        lines = [json.dumps(r.__dict__) for r in self.records]
        out.write_text("\n".join(lines), encoding="utf-8")
        return out

    def _default_path(self) -> Path:
        run_id = self.records[0].run_id if self.records else "run"
        return self._runs_dir / f"{run_id}.jsonl"
