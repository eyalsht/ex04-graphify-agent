"""TDD for TokenComparison.run_both (PHASE6-064..066): drives both runs + the TC-E5 check."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from ex04_graphify_agent.agent_workflow.state import AgentState
from ex04_graphify_agent.gatekeeper import TokenLogger, TokenRecord
from ex04_graphify_agent.token_comparison.runner import TokenComparison
from tests.token_comparison.fixtures.states import graph_guided_state, naive_state


class _FakeSdk:
    """Keyless sdk double: mirrors each state's token_usage into the injected gatekeeper log.

    ``skew`` perturbs the logged tokens so the run_both cross-check (TC-E5) must fail loud.
    """

    def __init__(self, states: list[AgentState], *, skew: bool = False) -> None:
        self._states = list(states)
        self._skew = skew
        self.calls: list[str] = []

    def run_agent(
        self, run_type: str, scratch_dir: Any = None, logger: TokenLogger | None = None
    ) -> AgentState:
        self.calls.append(run_type)
        state = self._states.pop(0)
        if logger is not None:
            for rec in state["token_usage"]:
                logger.record(
                    TokenRecord(
                        run_id=run_type,
                        run_type=run_type,
                        node=rec["node"],
                        input_tokens=rec["input_tokens"] + (1 if self._skew else 0),
                        output_tokens=rec["output_tokens"],
                        model="",
                    )
                )
        return state


def test_run_both_calls_agent_for_both_run_types(tmp_path: Path) -> None:
    sdk = _FakeSdk([graph_guided_state(), naive_state()])
    result = TokenComparison().run_both(sdk, runs_dir=tmp_path)
    assert sdk.calls == ["graph_guided", "naive"]
    assert result.graph_guided.run_type == "graph_guided"
    assert result.naive.run_type == "naive"


def test_run_both_records_wall_clock_durations(tmp_path: Path) -> None:
    sdk = _FakeSdk([graph_guided_state(), naive_state()])
    result = TokenComparison().run_both(sdk, runs_dir=tmp_path)
    assert result.graph_guided.duration_s >= 0.0
    assert result.naive.duration_s >= 0.0


def test_run_both_fails_loud_when_state_disagrees_with_gatekeeper_log(tmp_path: Path) -> None:
    # TC-E5 (mandatory): run_both always verifies token_usage against the gatekeeper ledger.
    sdk = _FakeSdk([graph_guided_state(), naive_state()], skew=True)
    with pytest.raises(ValueError, match="gatekeeper log disagree"):
        TokenComparison().run_both(sdk, runs_dir=tmp_path)


def test_run_both_dumps_gatekeeper_ledger_jsonl(tmp_path: Path) -> None:
    # CLAUDE.md §4: the per-call token ledger is persisted so cost/token numbers trace to it.
    sdk = _FakeSdk([graph_guided_state(), naive_state()])
    TokenComparison().run_both(sdk, runs_dir=tmp_path)
    dumped = sorted(p.name for p in tmp_path.glob("*.jsonl"))
    assert dumped == ["graph_guided.jsonl", "naive.jsonl"]
    records = [
        json.loads(line)
        for line in (tmp_path / "graph_guided.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert records and records[0]["run_type"] == "graph_guided"
