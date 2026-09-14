# repo-atlas

**Understand an unfamiliar Python repository without pouring it into a context window.**

`repo-atlas` builds a knowledge graph of a repo from its AST, turns that graph into a navigable
Obsidian vault, and writes an architecture brief from the graph's most central code — reading a
handful of targeted files instead of dumping the tree.

```
repo -> extractor (AST) -> graph.json -> graph_reader -> vault (index / notes / hot.md) -> BRIEF.md
```

## Status

**Phase 0 — scaffold.** Project rules, configuration, CI and the quality gates are in place;
`atlas version` is the only wired command. The extractor, reader, vault, brief and comparison
layers land in phases 1–6 (`docs/TODO.md`).

## Planned CLI

| command | does |
|---|---|
| `atlas extract <repo> [--out DIR]` | AST → `graph.json`, `manifest.json`, `GRAPH_REPORT.md` |
| `atlas vault <repo> [--seed ID]` | `index.md`, `community-*.md`, per-node notes, `hot.md` |
| `atlas brief <repo> [--budget N]` | `BRIEF.md` — the architecture/onboarding write-up |
| `atlas map <repo>` | all three in one pass |
| `atlas compare <repo>` | graph-guided vs naive-dump token comparison, from gatekeeper logs |

## Design commitments

- **No external graph tool.** The extractor is in this repo and runs on the standard-library `ast`
  module — keyless, offline, no network.
- **Runs with no API key.** The gatekeeper falls back to an offline mock client, so the full test
  suite and a complete `atlas map` work without credentials.
- **Nothing is pinned to one repository.** A graph node id or a target source path appearing as a
  string literal in `src/` fails the build (`scripts/check_no_hardcoded.py`).
- **Claims are tagged.** Every graph-derived statement is EXTRACTED, INFERRED, or AMBIGUOUS, with
  language strength matching the evidence (`CLAUDE.md` §4).
- **Numbers come from logs.** Token and cost figures trace to gatekeeper records, never estimates.

## Development

```bash
uv sync
uv run pytest --cov=src --cov-fail-under=90
uv run ruff check . && uv run mypy --strict src/
uv run python scripts/check_file_sizes.py
uv run python scripts/check_no_hardcoded.py
uv run python scripts/check_anti_patterns.py
```

`uv` only — `pip`, `venv` and `python -m` are forbidden in this repo.

## Origin

Forked from `ex04-graphify-agent` (University of Haifa, EX04 — Dr. Yoram Segal), which proved the
token-efficiency claim against a single vendored target using an external `graphify` CLI. This fork
keeps the graph reader, vault writer, gatekeeper and evidence discipline, replaces the external
extractor with its own, and drops the bug-fix scope. See `docs/adr/`.
