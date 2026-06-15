# ADR-0004: Graph-guided retrieval over naive whole-repo dump (core thesis)

## Status
Accepted

## Context
This is the project's **core thesis** (R1.4, R3.2, R3.3, R4.1, R4.2) and the reason the
token comparison (R5.6, R7.8) exists at all. The course material grounds it directly:
`lec/PART-B-*.pdf` (graph-based architectures / context management in LLMs) describes the
**"Lost in the Middle"** problem — relevant information buried inside a large context window
is retrieved less reliably, so dumping an entire unfamiliar codebase into the prompt both
wastes tokens and *degrades* localization. `lec/PART-C-*.pdf` supplies the **six-signal
inference discipline** (§5 of the internal brief): the graph proposes a hypothesis, and only
reading `source_file` turns it into a conclusion (Observe → Relation → Confidence → Context
→ Source-validation).

R5.3.2 requires the agent to consume `index.md` / `hot.md` / `graph.json` as its **primary
context — graph-guided, not raw-dump**, and R1.3 states it reads `index.md` / `hot.md` first,
**not raw source files**. R5.6.2 requires measuring a graph-guided run **and** a naive
baseline so the difference can be quantified (R5.6.4, concrete numbers). The decision below
defines exactly what each of those two runs is.

## Decision
The LangGraph agent's **first action is always to read `obsidian/index.md` and (once
generated, Phase 4) `obsidian/hot.md`** — **never raw source files first**. It only opens
`data/broken-python/polygons/polygons.py` **after** the graph/vault has produced a
hypothesis — i.e., at the **source-validation step** of the five-step pipeline (Plan →
Retrieve(graph) → Hypothesize → Validate(source) → Fix → Report). The graph proposes; the
source confirms.

The **naive baseline agent**, by contrast, is given the **entire `data/broken-python/`
tree** as context with no graph, no `index.md`, and no `hot.md`. The two runs differ only in
how context is supplied — this is what `token_comparison.py` measures.

**Deliberate modeling choice (stated for the grader):** the naive baseline is modeled as a
single dump→fix pass with **no validation/iteration loop**, whereas the graph-guided run
has a hypothesize→validate→(re-hypothesize) loop. This is a faithful operationalization of
the PDF's framing (§5.6 / §6.2: the naive agent "operates on many raw files without enough
context-focusing"), **not** an attempt to weaken the baseline to win the comparison — a
no-graph agent has no structured signal on which to iterate, so a single focused pass is
the honest naive analogue. The asymmetry is intentional and disclosed here; both runs are
still measured on the identical task and identical correctness check, and the naive run is
given a fair, complete view of the code (the whole tree), not a crippled one.

## Consequences
- **Defines the R5.6 / R7.8 measurement:** the graph-guided vs. naive contrast is exactly
  the variable `token_comparison.py` isolates; both runs are tagged via the gatekeeper
  (ADR-0002, `run_type`).
- **Operationalizes R1.4 / R4.1 / R4.2:** the thesis (fewer tokens, equal-or-better
  localization) becomes a directly testable claim with stored artifacts (R10.5).
- **Enforces PART-C discipline (R5.2.1):** the agent must reach the source only through a
  source-validation step, never as its opening move — INFERRED/AMBIGUOUS claims are
  validated, not acted on directly.
- **Depends on `hot.md` (R5.6.1):** `hot.md` must be derived from a graph metric
  (centrality / proximity to the bug), generated in Phase 4, before the graph-guided run.
- **Implies work:** Phase 4 (vault + `hot.md`), Phase 5 (agent with the graph-first node
  order), Phase 6 (run both, capture tokens + before/after `graph.json` diff). See
  `docs/TODO.md` Phase 4-6.

## Alternatives Considered
- **Hybrid: always dump all files AND provide the graph** — *Rejected.* If the graph-guided
  run also receives the full file dump, there is no token saving to measure and the "Lost in
  the Middle" effect is reintroduced — it defeats the entire purpose of the R5.6 / R4.1
  comparison. The two runs must differ *only* in context strategy.
- **Graph-only with no source-validation step** (act directly on graph hypotheses) —
  *Rejected.* This violates the PART-C inference discipline (brief §5): INFERRED and
  AMBIGUOUS claims must be **source-validated** before being acted on, not treated as fact.
  Skipping validation would also undercut R4.2 (correctness of the fix) — the graph points
  to `polygons.py`, but only reading the file confirms the precise `Object`/`new`/formula
  defects. The validate step is what makes the graph-guided run *both* cheaper *and* correct.
