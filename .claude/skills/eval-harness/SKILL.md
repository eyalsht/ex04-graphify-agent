---
name: eval-harness
description: |
  Use this skill when building, running, or reasoning about the project's evals — the layer
  that proves the system produces *correct graph/agent output*, distinct from tests that
  prove the code merely *runs*. Triggers: "eval", "validity", "structural eval",
  "known-answer", "does the agent actually find the bug", "prove the core", "schema check",
  "pass^k", "token-efficiency eval". Apply whenever a change could affect whether the system
  does the *right thing*, not just whether it executes.
---

# Eval Harness (Eval-Driven Development) — EX04

Tests prove the code *runs*; **evals** prove the system *behaves correctly* — here, that the
graph is parsed faithfully, the weakness detector finds the *known* signals, the vault ranks
the *known* god node, and the graph-guided agent really uses fewer tokens than the naive
baseline. A green unit-test suite over a system that mis-ranks the god node or fabricates a
token saving is exactly the failure mode evals exist to catch.

> **Methodology attribution.** This skill's structure — known-answer scenarios, the
> structural/behavioural split, and pass^k/pass@k framing — is adapted from this project's own
> **HW3/crew-scribe `eval-harness` skill**, which in turn credits the public
> [`affaan-m/ecc`](https://github.com/affaan-m/ecc) skill set (acknowledge in an ADR). The
> Python harness and the graph/agent invariants below are this project's own.

## The two layers

### Structural evals — deterministic invariants, keyless, in CI
Run against the **real, committed** `artifacts/graphify/graph.json` (PRE-FIX baseline) and
against mock-gatekeeper fixtures (ADR-0005). **Each invariant must hold on every run — the bar
is `pass^k = 100%`, not a statistical rate.** These are **known-answer evals**: the answers are
known in advance from `docs/_internal_context_brief.md` §2 (the six-signal table) and the PRDs.

1. **graph.json schema valid** — parses against PLAN.md §7.1's node-link data contract
   (`nodes`/`links`, node fields `id`/`label`/`file_type`/`source_file`/`community`, edge
   fields `relation`/`confidence`/`confidence_score`/`weight`). 23 nodes · 20 edges · 6
   communities, confidence mix 90% EXTRACTED / 10% INFERRED / 0% AMBIGUOUS.
2. **hot.md ranks the god node** — after Phase 4, `obsidian/hot.md` exists and ranks
   `polygons_polygons_polygon` (the Polygon god node, degree 4) at or near the top, per
   `PRD_graph_reader.md`'s centrality×proximity metric (R5.1.4 / R5.6.1). Not hand-curated.
3. **weakness_detector finds the known signals** — run against the real `graph.json`, the
   detector must emit **signal #1 (god node = `Polygon`/`polygons_polygons_polygon`, degree 4)**
   and **signal #5 (isolated cluster = the three `rationale_*` nodes,
   `polygons_polygons_rationale_{18,33,50}`, each with exactly one `rationale_for` edge)**. The
   expected answer comes from brief §2; this is a pure known-answer eval.
4. **graph-guided context < naive context** — structural/keyless: for this repo the
   graph-guided `Retrieve` context (index.md + hot.md + `polygons.py`, ~76 lines) is strictly
   smaller than the naive `Dump` context (all 9 files under `data/broken-python/**`), per
   `PRD_agent_workflow.md`. Asserted by token-counting the assembled context, not by a real
   LLM call.
5. **fixed `polygons.py` passes the correctness check** — per `PRD_token_comparison.md`:
   `calc_polygon_details(5)` → sum 540 / each 108 (pentagon), `calc_polygon_details(6)` → sum
   720 / each 120 (hexagon); and with a **mocked turtle**, `draw_polygon` for a pentagon issues
   5 `forward`/`right` iterations (call count == `sides`, turn == `360/sides`) — not the
   hardcoded 6. The original broken source must **fail** this check.
6. **token_comparison report is well-formed** — given **mocked gatekeeper-log fixtures**,
   `render_report` emits a table with rows `graph_guided` / `naive` and correct
   input/output/total sums, plus the R4.1 reduction-% and R4.2 correctness narrative
   (`PRD_token_comparison.md` TC-T1..TC-T8).

All structural evals run **keyless** — none may trigger a real LLM-provider call. They run
against committed baselines and deterministic fixtures.

### Behavioural evals — real-LLM runs, opt-in, committed as evidence
The **actual** graph-guided vs. naive token numbers (R5.6.2 / R5.6.4 / R7.8) require a real
provider API key (config-driven, likely `GEMINI_API_KEY`; D6) and are produced by ADR-0005's
**manual, run-once** comparison script — not
collected by pytest, never in CI. Reported with **pass@k** framing. The run's outputs (token
counts, `reports/token_comparison.md`, the PRE-FIX vs POST-FIX `graph.json` diff) are committed
as static artifacts so a grader verifies the numbers **without a key**.

## How to run

```bash
# Structural + known-answer evals only (keyless, fast — what CI runs); these live in tests/evals/:
uv run pytest -m eval

# Full keyless suite (unit tests + evals, no behavioural):
uv run pytest -m "not behavioural"

# The real-numbers comparison (manual, needs the provider key e.g. GEMINI_API_KEY — NOT in CI, ADR-0005):
uv run python scripts/run_comparison.py   # (once src/ + the script exist)
```

The structural evals live under `tests/evals/` (marker `eval`) and each must hold on
**every** run (`pass^k = 100%`). The single real keyed run's transcripts are committed under
`docs/evidence/` so the live behaviour is inspectable without a key (the agent-debate
committed-evidence signature).

Structural evals must pass with **no API key present**. An eval must never trigger a real LLM
call.

## The discipline (non-negotiable)

A failing eval is **fixed, or honestly disclosed in `docs/KNOWN_LIMITATIONS.md` — never
rationalised away.** The eval layer exists so a mis-ranked god node, a fabricated token saving,
or a wrong fix is *caught*, not explained after the fact.
- Structural / known-answer eval red in CI → the core is wrong (graph mis-parsed, signal
  missed, fix incorrect); fix before merge.
- Behavioural eval red in the manual run → fix the prompt/mechanism, or log a limitation with
  what/why/fix-sketch + a linked issue. Never delete the eval to make it green, and never
  substitute an estimate for a real token number (R10.5 — numbers trace to gatekeeper logs).
