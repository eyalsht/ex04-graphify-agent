# EX04 — Graphify + Obsidian Reverse-Engineering Agent

> University of Haifa · Dr. Yoram Segal's agentic-AI course · Lesson L07
> Authors: Eyal Shtinmtez (314884834) · Imree Cohen (312359284)

A graph-guided [LangGraph](https://langchain-ai.github.io/langgraph/) agent that
reverse-engineers and fixes a bug in
[`martinpeck/broken-python`](https://github.com/martinpeck/broken-python)'s
`polygons/polygons.py`, using a pre-generated **Graphify** knowledge graph and an
**Obsidian** vault (`index.md` / `hot.md`) as its navigation layer — and proves token
savings versus a naive "dump every file" baseline.

> **Status: Phase 1 scaffold.** This README is a placeholder; the full README
> (setup, results, root-cause, token numbers, OOP summary, AI-usage disclosure) is built in
> Phase 8 per `docs/ASSIGNMENT.md` §8. See `docs/PRD.md`, `docs/PLAN.md`, and `docs/TODO.md`.

## Quickstart (keyless)

```bash
uv sync
uv run pytest            # full suite, keyless (provider client mocked)
uv run pytest -m eval    # structural evals (the thesis, no API key)
uv run ruff check . && uv run mypy --strict src/
```

The real token-comparison numbers (one manual run, requires a provider API key — likely
`GEMINI_API_KEY`) are produced separately and committed as static artifacts under
`reports/` + `docs/evidence/`, so grading never needs a key (see `docs/adr/0005-*`).

## License

MIT — see `LICENSE`.
