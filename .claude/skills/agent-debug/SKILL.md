---
name: agent-debug
description: |
  DORMANT until the LangGraph agent_workflow exists (Phase 5+). Use this skill to debug the
  LangGraph `agent_workflow` and the validate→fix loop — a node that produces wrong output, a
  hypothesis that source-validation didn't confirm, state lost between nodes, a mocked
  gatekeeper that won't engage, or a validate→fix loop that won't converge. Triggers (Phase 5+
  only): "agent produced garbage", "hypothesis not validated", "state lost between nodes",
  "gatekeeper mock not engaging", "validation loop won't converge". Do NOT invoke before the
  agent is wired — there is nothing to debug yet.
---

# Agent Debug (LangGraph agent_workflow + validate→fix diagnostics) — DORMANT

> **Status: documented, not yet active.** This skill targets the LangGraph `agent_workflow`
> (nodes Plan → Retrieve/Dump → Hypothesize → Validate → Fix → Report, PLAN.md §3) and the
> validate→fix loop. That layer does **not exist yet** — the build is plan-first (docs →
> scaffold → graph_reader/weakness_detector → gatekeeper/mock seam → agent). Until the agent is
> wired (Phase 5), there is nothing to debug; this skill is a no-op. It is committed now so the
> methodology is on record, and **activates when Phase 5 lands**.

## What it will cover (Phase 5+)

- **Bad node output** — a node (`plan` / `retrieve` / `hypothesize` / `validate` / `fix` /
  `report`) emits wrong or empty output. Inspect the **LangGraph `AgentState`** (PLAN.md §7.2)
  at that node: confirm its inputs (`retrieved_context`, `current_hypothesis`), check whether
  the node delegated to the right module (`graph_reader` / `weakness_detector`) and that its
  prompt (`agent_workflow/prompts.py`) was applied.
- **Lost state between nodes** — a downstream node didn't receive an upstream value. Trace the
  `AgentState` TypedDict field-by-field: a field that a node forgot to set/return won't
  propagate (e.g. `current_hypothesis` written by `hypothesize` but not carried into
  `validate`, or `validated` never flipped to `True`). Confirm each node returns the full
  updated state.
- **Gatekeeper mock not engaging** — in keyless tests the gatekeeper's provider client is
  mocked at its boundary (ADR-0005). If a node hits the real API in a test, the **mock seam
  isn't installed** — check the gatekeeper handle is the injected mock, not a fresh
  `Gatekeeper` constructing a real client, and that the provider API key (e.g.
  `GEMINI_API_KEY`) isn't leaking in.
- **Validate→fix loop won't converge** — the loop (Validate re-hypothesizes when source
  contradicts the hypothesis) hits `max_validation_attempts` (from `config/agent.json` per
  PLAN.md §9) without confirming a hypothesis. Confirm the loop is **bounded** and **falls
  through to the next-ranked `weakness_detector` finding** rather than spinning — for this repo
  the top hypothesis (the `Polygon` god node) should validate against
  `data/broken-python/polygons/polygons.py`; if it didn't, check the inference discipline
  (INFERRED/AMBIGUOUS proposal never reached `validated=True` via the source-validation step).

## How it will be driven

- Through the **SDK façade** (`sdk.py`) — re-run or replay a node/run without re-spending the
  whole agent budget where possible (`Ex04Sdk.run_agent(run_type=...)`).
- Against the **gatekeeper run logs** (`artifacts/runs/<run_id>.jsonl`) and the per-node
  `token_usage` in `AgentState` — the primary evidence trail.
- Reusing the **eval-harness's known-answer fixtures** (`eval-harness` skill) to reproduce a
  failure **deterministically against the mocked gatekeeper before spending real tokens** — the
  god-node and isolated-cluster known answers (brief §2) make a regression reproducible keyless.

When the agent lands, replace this notice with the active runbook and remove "DORMANT" from the
front-matter description.
