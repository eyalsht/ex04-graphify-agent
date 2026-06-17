# EX04 — Graphify + Obsidian Reverse-Engineering Agent

> University of Haifa · Dr. Yoram Segal's agentic-AI course · Lesson L07
> Authors: Eyal Shtinmtez (314884834) · Imree Cohen (312359284)

A graph-guided [LangGraph](https://langchain-ai.github.io/langgraph/) agent that
reverse-engineers and fixes a bug in
[`martinpeck/broken-python`](https://github.com/martinpeck/broken-python)'s
`polygons/polygons.py`, using a pre-generated **Graphify** knowledge graph and an
**Obsidian** vault (`index.md` / `hot.md`) as its navigation layer — and proves token
savings versus a naive "dump every file" baseline.

> **Status: Phases 0–7 complete** (graph_reader, weakness_detector + gatekeeper, obsidian
> vault + `hot.md`, the LangGraph `agent_workflow`, `token_comparison`, and the **Phase-7
> reports**). The bug is fixed (`data/broken-python/polygons/polygons.py` passes the 3-part
> correctness gate), the POST-FIX graph is regenerated under `artifacts/graphify_post_fix/`,
> and a keyless structural eval shows the graph-guided fix-context uses **76.7% fewer input
> tokens** than the naive dump.
>
> The full R5.6/R7.8 keyed numbers (output tokens, LLM calls, duration) come from a manual
> key-gated run (`scripts/run_comparison.py`) and the Obsidian app screenshots are an owner
> capture — both tracked as open items in [`reports/README.md`](reports/README.md) and
> `docs/KNOWN_LIMITATIONS.md`. The full README (setup, results, AI-usage disclosure) is
> assembled in Phase 8 per `docs/ASSIGNMENT.md` §8. See `docs/PRD.md`, `docs/PLAN.md`,
> `docs/TODO.md`.

## Quickstart (keyless)

```bash
uv sync
uv run pytest            # full suite, keyless (provider client mocked)
uv run pytest -m eval    # structural evals (the thesis, no API key)
uv run ruff check . && uv run mypy --strict src/
uv run ex04 hot          # (re)generate obsidian/hot.md from the PRE-FIX graph (keyless)
```

The real token-comparison numbers (one manual run, requires a provider API key — likely
`GEMINI_API_KEY`) are produced separately and committed as static artifacts under
`reports/` + `docs/evidence/`, so grading never needs a key (see `docs/adr/0005-*`). For
that manual run, copy `.env.example` → `.env` and set your key (the `.env` is gitignored and
auto-loaded only by `scripts/run_comparison.py`); pick the model in `config/agent.json`:

```bash
cp .env.example .env          # then edit: GEMINI_API_KEY=...
uv run python scripts/run_comparison.py
```

## Navigating the graph (Obsidian vault)

Open `obsidian/` as an Obsidian vault. Start at
[`obsidian/index.md`](obsidian/index.md) (all 23 nodes + 6 communities) or
[`obsidian/hot.md`](obsidian/hot.md) — "where to look first", ranked by **centrality ×
proximity-to-bug** (R5.1.4/R5.6.1): a `0.6·degree + 0.4·betweenness` blend (max-normalized)
times `1 / (1 + graph distance)` to the bug node. The top entry,
`[[polygons_polygons_polygon|Polygon]]` (degree 4), is the god node at the bug location, and
every top-8 entry lives in `polygons/polygons.py` — the disconnected mathsquiz/README nodes
score 0 proximity and drop out. The metric is config-driven (`config/weakness_thresholds.json`)
and disclosed in the note itself.

## Reports & evidence (Phase 7)

The [`reports/`](reports/README.md) directory holds the graph-guided fix evidence — start at
[`reports/README.md`](reports/README.md):

- [Root-cause narrative](reports/root_cause.md) — one root cause (half-finished `Polygon`),
  five symptoms, localized via the graph (R4.5/R5.5.3).
- [Before/after diff](reports/diff_polygons.md) — the literal `polygons.py` fix (R5.2.4/R7.6).
- [OOP-improvement summary](reports/oop_improvement.md) — `Polygon` as single source of truth
  (R3.4/R7.7).
- [Graph diff](reports/graph_diff.md) — PRE vs POST structure (R5.6.3).
- [Token comparison](reports/token_comparison.md) — 76.7% input-context reduction, keyless (R4.1/R7.8).
- [Diagrams](reports/diagrams.md) — C4 + both agent routes (Mermaid, topology-verified, R5.4.2).
- [Pipeline & research questions](reports/pipeline.md) — R4.3/R4.6/R4.7, six-signal convergence.
- [Graph renders + Obsidian screenshot guide](reports/screenshots.md) — R5.4.1/R7.9/R10.3.

## License

MIT — see `LICENSE`.
