# EX04 — Graphify + Obsidian Reverse-Engineering Agent

> University of Haifa · Dr. Yoram Segal's agentic-AI course · Lesson L07
> Authors: Eyal Shtinmtez (314884834) · Imree Cohen (312359284)

A graph-guided [LangGraph](https://langchain-ai.github.io/langgraph/) agent that
reverse-engineers and fixes a bug in
[`martinpeck/broken-python`](https://github.com/martinpeck/broken-python)'s
`polygons/polygons.py`, using a pre-generated **Graphify** knowledge graph and an
**Obsidian** vault (`index.md` / `hot.md`) as its navigation layer — and proves token
savings versus a naive "dump every file" baseline.

> **Status: Phases 0–5 complete** (graph_reader, weakness_detector + gatekeeper, obsidian
> vault + `hot.md`, and the LangGraph `agent_workflow` — graph-guided + naive runs with a
> keyless structural eval showing the graph-guided fix-context uses ~74% fewer tokens);
> Phase 6 (token comparison + evidence) next. This README is still a placeholder; the full
> README (setup, results, root-cause, token numbers, OOP summary, AI-usage disclosure) is
> built in Phase 8 per `docs/ASSIGNMENT.md` §8. See `docs/PRD.md`, `docs/PLAN.md`,
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
`reports/` + `docs/evidence/`, so grading never needs a key (see `docs/adr/0005-*`).

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

## License

MIT — see `LICENSE`.
