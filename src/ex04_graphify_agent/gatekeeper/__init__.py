"""gatekeeper — provider-agnostic choke point for every LLM call.

Rate-limit, retry, queue, logging, and per-call token counters tagged by {run_type, node}.
The single mock seam for keyless tests (ADR-0002, ADR-0005). Phase 3 builds it.
"""
