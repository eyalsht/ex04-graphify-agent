"""TDD for TokenComparison.run_both (PHASE6-064..066): drives graph_guided + naive."""

from __future__ import annotations

from unittest.mock import MagicMock

from ex04_graphify_agent.token_comparison.runner import TokenComparison
from tests.token_comparison.fixtures.states import graph_guided_state, naive_state


def test_run_both_calls_agent_for_both_run_types() -> None:
    sdk = MagicMock()
    sdk.run_agent.side_effect = [graph_guided_state(), naive_state()]

    tc = TokenComparison()
    result = tc.run_both(sdk)

    calls = [call.args[0] for call in sdk.run_agent.call_args_list]
    assert calls == ["graph_guided", "naive"]
    assert result.graph_guided.run_type == "graph_guided"
    assert result.naive.run_type == "naive"


def test_run_both_records_wall_clock_durations() -> None:
    sdk = MagicMock()
    sdk.run_agent.side_effect = [graph_guided_state(), naive_state()]

    tc = TokenComparison()
    result = tc.run_both(sdk)

    assert result.graph_guided.duration_s >= 0.0
    assert result.naive.duration_s >= 0.0
