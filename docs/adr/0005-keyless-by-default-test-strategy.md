# ADR-0005: Keyless-by-default test strategy, real runs as committed artifacts

## Status
Accepted

## Context
Two requirements appear to be in tension. The CLAUDE.md non-negotiable (brief §6) demands
**keyless-by-default**: the full test suite + `self_grade` must pass with **NO API keys
(the LLM client mocked provider-agnostically — the provider is config-driven, likely
Gemini; D6)**, achieving coverage ≥90%. But R5.6.2 / R5.6.4 / R7.8
require **real token-usage numbers from real LLM calls** — you cannot measure the cost of a
graph-guided vs. naive run by mocking the calls, since the whole point is the actual token
counts (R10.5: every quantitative claim backed by a stored artifact; brief §6: numbers
"from `gatekeeper.py`'s logs, not estimates").

A grader must be able to run `uv run pytest` and `self_grade` to green **without a key**,
*and* be able to verify the R5.6 / R7.8 numbers — also **without a key**. The gatekeeper
(ADR-0002) is the single seam that lets us satisfy both.

## Decision
Resolve the tension through the gatekeeper as the **mock seam**:

- **Test suite (keyless, automated):** `uv run pytest` mocks the LLM client entirely
  at the gatekeeper boundary (provider-agnostically), using deterministic fixtures — **0 real
  API calls**, fully
  reproducible, ≥90% coverage achievable keyless. `self_grade` runs in this mode too. This
  is the default and the gate for CI/grading.
- **Comparison run (real, manual, NOT part of the test suite):** a separate,
  manually-invoked script performs the actual graph-guided vs. naive runs against a real
  provider API key (the env var named by `config/agent.json`'s `api_key_env`, likely
  `GEMINI_API_KEY`). It is **not** collected by pytest and never runs in CI.
- **Artifacts (committed, key-free verification):** the comparison run's **output** — token
  counts, the R7.8 comparison report, and the before/after `graph.json` diff (R5.6.3) — is
  committed as static files under `reports/` and `artifacts/`. A grader with no key verifies
  R5.6 / R7.8 by reading those committed artifacts, not by re-running the LLM.

## Consequences
- **Satisfies both** the keyless-by-default non-negotiable and R5.6 / R7.8 (real numbers) at
  once — the only place that needs a key is the manual comparison script.
- **Depends on ADR-0002:** because all calls funnel through the gatekeeper, the keyless mock
  is installed at exactly one boundary; without the gatekeeper this strategy would require
  patching every node.
- **Constrains** the comparison script to be idempotent-by-artifact: once run, its outputs
  are frozen in the repo; regenerating them requires a key and an explicit manual step (so
  graded baseline artifacts are never silently overwritten — brief §6 EX04 rule).
- **Implies a KNOWN_LIMITATIONS note:** the committed token numbers reflect a specific
  provider/model/run (D6 — config-driven, decided at run time; likely Gemini) and are not
  re-derived in CI; this is disclosed in
  `docs/KNOWN_LIMITATIONS.md` along with the honest self-grade.
- **Implies work:** Phase 3 (gatekeeper mock seam + fixtures), Phase 6 (manual comparison
  run, commit artifacts), Phase 7 (report). See `docs/TODO.md` Phase 3, 6-7.

## Alternatives Considered
- **Record-and-replay (VCR-style) cassettes of real API responses** — *Rejected as the
  primary approach.* Cassettes would let tests replay real responses keylessly, but they add
  a dependency and carry cassette-staleness risk (responses drift from the live model) for a
  course project where the committed artifacts already provide key-free verification. It is
  worth recording in `docs/KNOWN_LIMITATIONS.md` as a possible future improvement, not the
  baseline strategy.
- **Require the grader to have a provider API key** — *Rejected.* This directly violates
  the keyless-by-default non-negotiable (brief §6) and R8.2 (keyless setup), and would make
  grading non-reproducible for anyone without billing access. The committed-artifacts
  approach gives the grader the same evidence with no key.
