# Research Questions (R4.1–R4.7) — answered with evidence

Each course research question, answered concisely with a link to the committed evidence
(PHASE8-015 / R4.x). Deeper narrative lives in [`pipeline.md`](pipeline.md) and
[`root_cause.md`](root_cause.md).

### R4.1 — Does graph-guided navigation reduce tokens vs. a naive dump, and by how much?
**Yes — 76.7% fewer input-context tokens** (graph-guided 406 vs naive 1743), keyless and
reproducible via `uv run pytest -m eval`; the keyed live run shows a 57.5% input cut at
real-provider scale. Evidence: [`token_comparison.md`](token_comparison.md),
[`tests/evals/test_agent_context_delta.py`](../tests/evals/), [README §6](../README.md#-6-token-efficiency--cost-results-r86).

### R4.2 — Does that reduction cost (or improve) bug-localization accuracy?
**It improves it.** On the keyed live run the graph-guided route **passed** the executable
correctness gate while the naive dump **failed** ("Lost in the Middle") — same model, same
prompts, only the context strategy differed. Evidence: [`token_comparison.md`](token_comparison.md),
`token_comparison/correctness.py`.

### R4.3 — What do God Nodes reveal about core abstractions / coupling risk?
The degree-4 `Polygon` god node is the program's intended central abstraction left
half-finished — every downstream computation re-implements the state it should own. The
graph surfaces this coupling risk without reading source. Evidence:
[`root_cause.md`](root_cause.md), `weakness_detector/signals_graph.py` (signal 1).

### R4.4 — What OOP improvements does the graph suggest, and were they applied?
Promote `Polygon` to the single source of truth and retire the shadowing dict; five symptoms
collapse into one fix. Applied and gated. Evidence: [`oop_improvement.md`](oop_improvement.md).

### R4.5 — How did the graph identify the root cause (not a symptom)?
Signals 1 (god node), 5 (isolated `rationale` TODO nodes), 6 (dict duplicates the class
fields) all converge on `Polygon` — the root cause — before any source is read. Evidence:
[`root_cause.md`](root_cause.md), [`pipeline.md`](pipeline.md).

### R4.6 — How did Obsidian concretely help (with evidence)?
`hot.md` ranks `Polygon` #1 as the entry point; the vault graph view makes the coupling
visible. Evidence: [`screenshots.md`](screenshots.md) (Figs 3–6), [`obsidian/hot.md`](../obsidian/hot.md).

### R4.7 — How was AI used, and where did the agent diverge from a human?
Full append-only disclosure in [`docs/PROMPTS.md`](../docs/PROMPTS.md): AI drafted all code,
tests, docs under TDD; the human owner made repo/bug/metric decisions and ran the reviews.
The agent navigated the *graph map* rather than reading files top-to-bottom as a human might.
Evidence: [README §8](../README.md#-8-ai-usage-disclosure-r88), [`run_journey.md`](run_journey.md).
