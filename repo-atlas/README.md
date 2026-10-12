# repo-atlas

**Understand an unfamiliar Python repository without pouring it into a context window.**

`repo-atlas` builds a knowledge graph of a repo from its AST, turns that graph into a navigable
Obsidian vault, and writes an architecture brief from the graph's most central code — reading a
handful of targeted files instead of dumping the tree.

```
repo -> extractor (AST) -> graph.json -> graph_reader -> vault (index / notes / hot.md) -> BRIEF.md
```

## Status

**Phases 0–5 complete; phase 6 (CLI/SDK) wired.** All six commands below run today, keylessly.
The suite is **498 tests at 99% coverage**, ruff 0 / mypy --strict 0, every gate green.
`docs/TODO.md` tracks what is left: perf figures, third-party smoke runs, the 0.1.0 tag.

## CLI

| command | does |
|---|---|
| `atlas extract <repo> [--out DIR]` | AST → `graph.json`, `manifest.json`, `GRAPH_REPORT.md` |
| `atlas vault <repo> [--seed ID]` | `index.md`, `community-*.md`, per-node notes, `hot.md` |
| `atlas brief <repo> [--budget N]` | `BRIEF.md` — the architecture/onboarding write-up |
| `atlas map <repo>` | extract + vault in one pass |
| `atlas compare <repo>` | graph-guided vs naive-dump token comparison, from gatekeeper logs |
| `atlas version` | installed version |

## Walkthrough — repo-atlas mapping itself

`atlas map` needs no API key. Pointed at this repository:

```console
$ uv run atlas map . --out /tmp/atlas
Extracted 1076 nodes / 2355 edges.
  graph: /tmp/atlas/graph.json
Vault written to /tmp/atlas/vault (1076 notes, 68 communities).
```

The generated `vault/hot.md` — the "where do I look first" note, and (with `index.md`'s
community structure) the only part of the vault the brief ever feeds to a model:

```markdown
# Hot — where to look first

Ranked by centrality (0.6*degree + 0.4*betweenness, each normalised against this graph's maximum).

1. [[src_repo_atlas_graph_reader___init__|__init__.py]] (degree 23, betweenness 0.164) — `src/repo_atlas/graph_reader/__init__.py:L1`
2. [[src_repo_atlas_extractor___init__|__init__.py]] (degree 26, betweenness 0.112) — `src/repo_atlas/extractor/__init__.py:L1`
3. [[src_repo_atlas_extractor_parse_parse_source|parse_source()]] (degree 34, betweenness 0.036) — `src/repo_atlas/extractor/parse.py:L23`
4. [[src_repo_atlas_gatekeeper___init__|__init__.py]] (degree 14, betweenness 0.155) — `src/repo_atlas/gatekeeper/__init__.py:L1`
5. [[src_repo_atlas_extractor_build_extract|extract()]] (degree 24, betweenness 0.027) — `src/repo_atlas/extractor/build.py:L80`
```

That ranking is the pipeline grading its own homework: the parser, the graph builder and
file discovery *are* where a newcomer should start. `tests/evals/test_self_hosting.py`
asserts exactly that — the map must name the core modules and leave zero dangling wikilinks.

Edge confidence from the same run (`GRAPH_REPORT.md`): **EXTRACTED 2347 (99.7%)**,
INFERRED 8 (0.3%), AMBIGUOUS 0.

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
- **The saving is reported honestly, including when it is negative.** Assembling a vault plus
  source windows costs a fixed overhead, so below a crossover repository size the graph-guided
  route uses *more* input than dumping every file — `atlas compare` will show a negative
  reduction on a toy repo, which is the correct answer rather than a defect
  (`docs/KNOWN_LIMITATIONS.md`).

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
