"""build_run_metrics — one route's BriefResult + gatekeeper log -> RunMetrics (PRD R5.1/R5.2).

Keeps the origin project's ``_assert_logs_agree``: the numbers this layer reports must equal
the gatekeeper's own log, element for element. A mismatch raises rather than quietly
reporting an estimate — that guarantee is the whole point of this layer.
"""

from __future__ import annotations

from typing import Any

from repo_atlas.brief.models import BriefResult
from repo_atlas.gatekeeper import TokenRecord
from repo_atlas.token_comparison.coverage import CoverageMetrics
from repo_atlas.token_comparison.models import RunMetrics


def build_run_metrics(
    result: BriefResult,
    log_records: list[TokenRecord],
    duration_s: float,
    coverage: CoverageMetrics,
) -> RunMetrics:
    """Aggregate one completed ``BriefResult`` into a ``RunMetrics``.

    ``log_records`` must be exactly this run's slice of the gatekeeper's ``TokenLogger``
    (same ``run_type``, call order preserved) — see ``_assert_logs_agree``.
    """
    _assert_logs_agree(result.token_usage, log_records)
    input_tokens = sum(record.input_tokens for record in log_records)
    output_tokens = sum(record.output_tokens for record in log_records)
    return RunMetrics(
        run_type=result.run_type,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        files_read=len(result.files_read),
        num_llm_calls=len(log_records),
        duration_s=duration_s,
        coverage=coverage,
        files_read_list=result.files_read,
    )


def _token_view(node: str, input_tokens: int, output_tokens: int) -> dict[str, Any]:
    return {"node": node, "input_tokens": input_tokens, "output_tokens": output_tokens}


def _assert_logs_agree(token_usage: list[dict[str, Any]], log_records: list[TokenRecord]) -> None:
    """The brief's own token_usage must equal the gatekeeper's log, entry for entry (R5.2)."""
    brief_view = [
        _token_view(rec["node"], rec["input_tokens"], rec["output_tokens"]) for rec in token_usage
    ]
    log_view = [_token_view(rec.node, rec.input_tokens, rec.output_tokens) for rec in log_records]
    if brief_view != log_view:
        msg = (
            "brief token_usage and the gatekeeper log disagree "
            f"(brief={brief_view!r} vs log={log_view!r}) - refusing to report an estimate"
        )
        raise ValueError(msg)


def assert_totals_match_log(metrics: RunMetrics, log_records: list[TokenRecord]) -> None:
    """Defense in depth for the report step: recompute totals from the log and compare.

    ``build_run_metrics`` already verifies this at construction time; this second check lets
    ``render_report`` refuse to render a ``RunMetrics`` that reached it by any other path
    (e.g. reloaded from storage) but no longer agrees with the stored ledger.
    """
    input_tokens = sum(record.input_tokens for record in log_records)
    output_tokens = sum(record.output_tokens for record in log_records)
    num_calls = len(log_records)
    logged = (input_tokens, output_tokens, num_calls)
    reported = (metrics.input_tokens, metrics.output_tokens, metrics.num_llm_calls)
    if logged != reported:
        msg = (
            f"RunMetrics for {metrics.run_type!r} disagrees with the gatekeeper log: "
            f"reported (input, output, calls)={reported} vs logged={logged}"
        )
        raise ValueError(msg)
