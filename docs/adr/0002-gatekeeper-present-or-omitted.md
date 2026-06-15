# ADR-0002: API Gatekeeper is present (not omitted)

## Status
Accepted

## Context
The project's CLAUDE.md non-negotiables (§6 of the internal brief) require an **API
Gatekeeper for every external LLM call** (rate-limit, retry, queue, log), but carve out an
exception: *"omit the gatekeeper if the project makes zero external API calls, and document
that omission as an ADR."* This ADR exists to record that the exception does **not** apply.

This project makes **real external LLM-provider API calls** (the provider is config-driven
and decided later — likely Google Gemini; D6) in two places: (1) the
graph-guided LangGraph agent run (ADR-0001, D6), and (2) the **naive baseline run** that
dumps the whole repo into context for the comparison. Both are required to produce the
R5.6.2 / R5.6.4 token-usage numbers and the R7.8 comparison report. Because external calls
exist — and because they exist specifically to be measured — a central choke point is not
optional.

Beyond the standard cross-cutting concerns, the gatekeeper has a **project-specific** job:
it is the single place where per-call token counts are captured and **tagged by
`{run_type: graph_guided|naive, node/step}`**. R10.5 requires every quantitative claim to be
backed by a stored artifact, and the EX04-specific non-negotiable (brief §6) states the
token-comparison numbers *"must come from `gatekeeper.py`'s logs, not estimates."* The
gatekeeper is therefore the data source for R5.6 / R7.8, not merely a hygiene layer.

## Decision
**The gatekeeper is present, and provider-agnostic.** `gatekeeper.py` (§4 of the brief)
wraps every external LLM call behind a single internal interface — the concrete provider
SDK (Gemini, or another, per `config/agent.json`) is an implementation detail hidden behind
the gatekeeper, so switching providers touches only this module. It is responsible for:
- rate-limiting, retry-with-backoff, and request queueing;
- structured logging of each call;
- **capturing per-call input/output token counts tagged with `{run_type, node}`**, which
  `token_comparison.py` aggregates into the R7.8 report;
- being the **single mock seam** for keyless test mode (ADR-0005) — tests swap the real
  provider client at this boundary.

## Consequences
- **Enables R5.6 / R7.8:** one consistent, queryable source of token data across both
  runs, making the comparison genuinely apples-to-apples.
- **Enables ADR-0005:** because all external calls funnel through one wrapper, keyless test
  mode is achieved by mocking exactly one boundary rather than patching every node.
- **Constrains** every module that talks to the LLM provider — no module may call the
  provider SDK directly; all calls go through the gatekeeper (consistent with SDK-first,
  brief §6). This is also what keeps the provider choice swappable (D6).
- **Implies work:** Phase 2-3 build `gatekeeper.py` and its token-logging schema before the
  agent (Phase 5) or comparison (Phase 6) can run. See `docs/TODO.md` Phase 2-3, 6-7.

## Alternatives Considered
- **No gatekeeper; ad-hoc token logging inside each node** — *Rejected.* Token counts would
  be scattered across nodes and the naive baseline, logged in inconsistent formats, making a
  single apples-to-apples R7.8 report hard to assemble and easy to get subtly wrong (the
  exact failure R10.5 / the "from logs, not estimates" rule guard against). It also
  violates the CLAUDE.md gatekeeper non-negotiable, which only permits omission at *zero*
  external calls.
- **Use the provider SDK's built-in `usage`/token objects directly, without a wrapper** —
  *Rejected.* Provider SDKs do report usage per response, but reading it inline gives no
  central place to enforce rate-limit/retry/queue policy and, critically, no single seam to
  install the keyless-test-mode mock that ADR-0005 depends on — nor a single place to swap
  providers (D6). The gatekeeper can still *read* the SDK's usage objects internally — it
  just adds the missing central tagging, logging, provider abstraction, and mock boundary on
  top.
