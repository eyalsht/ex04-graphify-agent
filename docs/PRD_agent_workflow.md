# PRD: agent_workflow/ (LangGraph)

> The LangGraph orchestration for BOTH the graph-guided run and the naive baseline run.
> LangGraph (not CrewAI) is locked by D1/ADR-0001 for typed state + per-node token
> instrumentation. The central concept of this PRD is the **context-minimization
> mechanism** — what exactly enters the LLM context at each node — because that delta is
> precisely what `token_comparison.py` measures (R5.6.2).

---

## Purpose

Define and document the agent's workflow (R5.3.3, R5.5.1): the nodes, the typed state,
the per-node context, and the stop conditions for two runs that fix the same bug
(`data/broken-python/polygons/polygons.py`) two different ways:
- **graph-guided** — reads `index.md` + `hot.md` + the single top finding's `source_file`
  (R5.3.2, R6.2.1: graph is the navigation backbone).
- **naive baseline** — dumps every file under `data/broken-python/` into context.

## One parameterized graph (not two separate graphs)

**Decision:** a single graph parameterized by `run_type: "graph_guided" | "naive"` in
state, with conditional edges selecting the node path. **Justification (per ADR-0001):**
shared `plan`/`fix`/`report` nodes and a single typed `AgentState` mean the token
instrumentation (gatekeeper-wrapped LLM calls) is identical across both runs, so the
comparison measures *context strategy* and nothing else — no divergence from duplicated
node implementations. Two named compiled graphs would risk instrumentation drift.

## Inputs

- `run_type` (chosen by `token_comparison.py` / CLI).
- Graph-guided path: `obsidian/index.md`, `obsidian/hot.md` (from `obsidian_writer`),
  `GraphReader` + `WeaknessDetector`, and on demand
  `data/broken-python/polygons/polygons.py`.
- Naive path: the full `data/broken-python/**` tree.
- `config/agent.json` — `provider` + `model` (config-driven, decided later; no hardcoded
  default, NOT Haiku — likely Gemini, D6), `api_key_env`, `max_findings_tried`,
  `max_validation_attempts`.
- All LLM calls go through `gatekeeper.py` (D2/ADR-0002) — the single choke point that
  logs per-call token usage.

## Outputs

- `fix_diff` — the corrected `polygons.py` content + a unified diff vs the original.
- A populated `AgentState` (esp. `token_usage`) handed to `token_comparison.py`.
- A `report` summary (root cause, finding used, validation result).

## State schema (typed — R6.1.4)

```python
from typing import Literal, TypedDict
# WeaknessFinding imported from weakness_detector

class TokenRecord(TypedDict):
    node: str
    input_tokens: int
    output_tokens: int

class AgentState(TypedDict):
    run_type: Literal["graph_guided", "naive"]
    messages: list[dict]                       # LangGraph message log
    vault_context: str                         # graph-guided: index.md + hot.md text
    dumped_context: str                        # naive: concatenated data/broken-python/**
    current_hypothesis: WeaknessFinding | None # from weakness_detector (carries EXTRACTED/INFERRED/AMBIGUOUS tag)
    validated_source: str | None               # content read during `validate`
    validated: bool
    findings_tried: int                        # graph-guided: hypothesize→validate rounds
    files_read: list[str]                       # every file/textual unit that entered context (R5.6.5 (b))
    fix_diff: str | None
    token_usage: list[TokenRecord]             # one per LLM call, from gatekeeper
```

**Feeds the mandated §5.6 metrics (R5.6.5).** `token_comparison.py` derives `files_read`
from `len(state["files_read"])` (graph-guided: index.md + hot.md + the one validated
source = 3; naive: every dumped file = 9) and `iterations` from `state["findings_tried"]`
for graph-guided (≥1) / the single dump→fix pass (=1) for naive. Both are **explicit,
required report columns**, not implied by token counts. Every node that pulls a file into
context (`read_vault`, `validate`, `dump_repo`) **must append the path(s) to
`files_read`** so the count is auditable evidence (R10.5), not an assertion.

## Nodes

### Graph-guided path
- **`plan`** — Sets `run_type`, initializes state, decides the route. Context: tiny system
  prompt only.
- **`read_vault`** — Reads `obsidian/index.md` + `obsidian/hot.md` into `vault_context`.
  **No source files read here.** This is the compressed, prioritized map (R1.4, R5.3.2).
- **`hypothesize`** — Calls `WeaknessDetector.detect()`, sets `current_hypothesis` to the
  top-ranked (primary) finding — for this repo, Signal 1 / the `Polygon` god node, whose
  `source_file` is `polygons/polygons.py`.
- **`validate`** — Source-reads the `source_file` named in `current_hypothesis`
  (`data/broken-python/polygons/polygons.py`, ~76 lines), stores it in
  `validated_source`, fills `current_hypothesis.source_validation`, sets `validated`.
- **`fix`** — One gatekeeper-wrapped LLM call. Prompt = system + `vault_context` +
  `validated_source` (one file) + the hypothesis. Produces corrected file content →
  `fix_diff`.
- **`report`** — Summarizes root cause, the finding used, validation, and the diff.

### Naive baseline path
- **`plan`** — As above, `run_type="naive"`.
- **`dump_repo`** — Reads **every** file under `data/broken-python/` into
  `dumped_context`: `mathsquiz/mathsquiz.py`, `mathsquiz/mathsquiz-step1.py`,
  `-step2.py`, `-step3.py` (×4 step/main scripts), `polygons/polygons.py`, the two
  `README.md`s (root + `mathsquiz/`), and `LICENSE.txt`. No graph, no hot.md.
- **`fix`** — One gatekeeper-wrapped LLM call. Prompt = system + entire `dumped_context`.
- **`report`** — As above.

## Context-minimization mechanism (central section)

What enters the LLM context at the `fix` node:

| | Graph-guided | Naive |
|---|---|---|
| Map | `index.md` + `hot.md` text (small; ranked list, top item `[[polygons_polygons_polygon\|Polygon]]`) | none |
| Source | exactly **one** file: `polygons/polygons.py` (~76 lines), selected by the top finding's `source_file` | **all** of `data/broken-python/**`: 5 mathsquiz `.py` + `polygons.py` + 2 READMEs + LICENSE |
| Hypothesis | the single primary `WeaknessFinding` (with tag) | none — the LLM must self-locate the bug in the dump |

The graph-guided run passes a small, ordered map plus one relevant file; the naive run
pushes the whole tree (most of it irrelevant — the mathsquiz files have nothing to do with
the polygons bug), inviting the "Lost in the Middle" failure (R1.4). **This delta in
input tokens at the `fix` node is exactly the quantity `token_comparison.py` measures**
(R5.6.2), and the graph-guided run is expected to use materially fewer input tokens while
localizing the same root cause (R4.1, R4.2).

## Stop conditions (R5.3.3)

- Graph-guided stops after `fix` + `report` when `validated == True`.
- If the top finding is **AMBIGUOUS** (e.g. Signal 6 pre-source-read) and `validate` does
  NOT confirm it within `max_validation_attempts` (config, default 1 — a source-read
  either confirms or it doesn't), the workflow **falls through to the next-ranked
  finding**, incrementing `findings_tried`. It never loops forever: it stops after
  `findings_tried >= max_findings_tried` (config, default 3) and reports "no confirmable
  finding".
- Naive stops after `fix` + `report` (single pass; no validation loop — it has no
  finding to validate).

## Edge cases

- **AW-E1 (AMBIGUOUS fall-through).** Top finding tagged AMBIGUOUS, source-read fails to
  confirm → advance to next finding; assert no infinite loop (bounded by
  `max_findings_tried`).
- **AW-E2 (hot.md missing).** Graph-guided `read_vault` before Phase-4 `hot.md` exists →
  fail loud with a clear "run obsidian_writer first" error (don't silently fall back to a
  dump — that would corrupt the comparison).
- **AW-E3 (keyless test mode).** With no provider key present, the gatekeeper returns a
  mocked provider response (ADR-0005); the graph still routes and token *structure*
  assertions still hold.
- **AW-E4 (naive context ordering).** `dump_repo` must concatenate files
  deterministically (sorted paths) so token counts are reproducible across runs.
- **AW-E5 (empty fix).** LLM returns no usable diff → `report` records failure; correctness
  check in `token_comparison.py` will mark it fail rather than crashing.

## Test cases (for TDD — Given/When/Then; keyless, mocked provider client)

- **AW-T1 (context delta — structural, no real LLM).** Given the repo and a mocked
  gatekeeper, When the graph-guided run reaches `fix` and the naive run reaches `fix`,
  Then `count_tokens(state_graph.vault_context + validated_source) <
  count_tokens(state_naive.dumped_context)`. (Pure structural assertion — the core thesis,
  needs no API call.)
- **AW-T2 (graph-guided reads only one source file).** Given a graph-guided run, When it
  completes, Then `validated_source` contains only `polygons/polygons.py` and no mathsquiz
  file content appears in any `fix`-node prompt.
- **AW-T3 (naive reads all files).** Given a naive run, When `dump_repo` completes, Then
  `dumped_context` contains text from all of: `polygons.py`, the 5 mathsquiz scripts, both
  READMEs, and LICENSE.txt.
- **AW-T4 (top finding routes to polygons).** Given graph-guided, When `hypothesize` runs,
  Then `current_hypothesis.source_file == "polygons/polygons.py"` and the finding is
  `priority=="primary"`.
- **AW-T5 (validation fills trail).** Given graph-guided, When `validate` runs, Then
  `validated == True` and `current_hypothesis.source_validation is not None`.
- **AW-T6 (AMBIGUOUS fall-through bounded).** Given a forced AMBIGUOUS top finding that
  never confirms, When the graph runs, Then `findings_tried <= max_findings_tried` and the
  graph terminates.
- **AW-T7 (token_usage populated by gatekeeper).** Given any run with the mocked
  gatekeeper, When it completes, Then `token_usage` has one `TokenRecord` per LLM call,
  each with `node`, `input_tokens`, `output_tokens`.
- **AW-T8 (single parameterized graph).** Given `run_type` toggled, When the graph
  compiles, Then both routes share the same `plan`/`fix`/`report` node objects (no
  duplicated implementations — instrumentation parity).

## Requirement traceability (ASSIGNMENT.md)

- **R5.3.1** — built with LangGraph (ADR-0001).
- **R5.3.2** — graph-guided run consumes `index.md`/`hot.md` as primary context.
- **R5.3.3** — nodes, tools, and stop conditions documented above.
- **R5.5.1** — full pipeline (vault → agent → fix) expressed as the graph.
- **R5.5.2** — every node's input/output is inspectable via typed `AgentState`.
- **R5.5.3** — `validate` node shows how the root cause is confirmed from source.
- **R6.1.4** — explicit typed state (`AgentState` TypedDict), not ad-hoc dicts.
- **R6.2.1** — graph is the navigation backbone (no LLM-only path in graph-guided run).
- **R6.2.2** — every node/tool is documented and explainable.

## Dependencies on other modules

- **Depends on:** `obsidian_writer` (produces `hot.md` read by `read_vault`),
  `graph_reader` + `weakness_detector` (`hypothesize`), `gatekeeper` (every LLM call +
  token logging), `config/agent.json`.
- **Depended on by:** `token_comparison.py` (drives both runs and consumes
  `token_usage` / `fix_diff`); `sdk.py` (façade entry point).
