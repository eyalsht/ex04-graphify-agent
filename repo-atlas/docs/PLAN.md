# PLAN — repo-atlas architecture

> Scope from `docs/PRD.md`, decisions from `docs/adr/`, rules from `CLAUDE.md`.
> Phase-1 scaffolding is built from §4, §7 and §8 of this document.

## 1. Context

```
        ┌──────────────┐
        │  developer   │  atlas map <repo>
        └──────┬───────┘
               │
        ┌──────▼───────┐        reads (parse only, never execute)
        │  repo-atlas  │ ─────────────────────────► target repository
        └──────┬───────┘
               │ writes                     ┌──────────────────┐
               ├──► <out>/graph.json        │  LLM provider    │
               ├──► <out>/vault/*.md        │ (via gatekeeper, │
               ├──► <out>/BRIEF.md          │  or offline mock)│
               └──► <out>/runs/*.jsonl ◄────┴──────────────────┘
```

## 2. Containers

| Container | Responsibility | Talks to |
|---|---|---|
| `cli` | Parse arguments into `RunPaths` + `RunConfig` | `sdk` |
| `sdk` | The only public surface; orchestrates phases | every module |
| `extractor` | Target repo → `graph.json` | filesystem |
| `graph_reader` | `graph.json` → queryable views | — |
| `vault` | views → Markdown notes | filesystem |
| `brief` | graph + vault → `BRIEF.md` | `gatekeeper` |
| `gatekeeper` | The only path to a provider | provider SDK / mock |
| `token_comparison` | Two runs → evidence report | `sdk`, `gatekeeper` logs |

## 3. Component — `brief`

```
START ─► load_graph ─► select_context ─► summarize ─► write_brief ─► END
                                            │  ▲
                                            └──┘  once per brief section
```

`select_context` is where the token thesis lives: `index.md` + `hot.md` + source slices for the top
`hot_source_slices` nodes, capped at `context_token_budget`. The naive baseline replaces this node
with a filtered full-repo dump and changes nothing else, so the two runs are comparable by
construction.

## 4. Module structure

```
src/repo_atlas/
├── __init__.py                (~12 lines: version)
├── cli.py                     (~90 lines: Typer commands, zero logic)
├── sdk.py                     (~120 lines: façade — extract/vault/brief/map/compare)
├── paths.py                   (~60 lines: RunPaths, RunConfig, config loading — ADR-0003)
├── extractor/
│   ├── discovery.py           (~110 lines: walk, ignore rules, size cap)
│   ├── py_nodes.py            (~130 lines: module/class/function/method nodes)
│   ├── py_edges.py            (~140 lines: contains/calls/inherits/method/references)
│   ├── confidence.py          (~60 lines: EXTRACTED vs INFERRED resolution)
│   ├── communities.py         (~50 lines: greedy modularity)
│   └── build.py               (~120 lines: assemble, manifest, GRAPH_REPORT.md)
├── graph_reader/
│   ├── models.py              (~55 lines: Confidence, NodeView, EdgeView)
│   ├── loader.py              (~50 lines: load + node_link_graph)
│   ├── metrics.py             (~45 lines: degree, betweenness w/ sampling)
│   ├── filters.py             (~85 lines: confidence/community/centrality filters)
│   └── reader.py              (~140 lines: GraphReader query surface)
├── vault/
│   ├── index.py               (~40 lines)
│   ├── notes.py               (~60 lines: per-node notes)
│   ├── communities.py         (~45 lines: community-N.md — new in this fork)
│   ├── ranking.py             (~70 lines: centrality, optional seed proximity)
│   └── writer.py              (~110 lines: VaultWriter)
├── brief/
│   ├── state.py               (~40 lines)
│   ├── context.py             (~100 lines: budgeted context assembly + naive dump)
│   ├── prompts.py             (~60 lines)
│   ├── nodes.py               (~120 lines)
│   └── graph_def.py           (~70 lines)
├── gatekeeper/
│   ├── client.py              (~130 lines: Gatekeeper, LLMClient, MockClient)
│   ├── provider.py            (~80 lines: real adapters, registered by name)
│   └── token_log.py           (~55 lines: TokenRecord, TokenLogger → JSONL)
└── token_comparison/
    ├── models.py, metrics.py, comparison.py, cost.py, report.py
```

Line budgets are targets, not promises — the 150-line cap in `CLAUDE.md` §3 is the promise.

## 5. Data flow

1. `cli` builds `RunPaths(repo_root, out_dir, config_path)` and `RunConfig` from `config/atlas.json`.
2. `extractor.discovery` yields eligible files; `py_nodes`/`py_edges` parse each with `ast`;
   `communities` labels; `build` writes `graph.json`, `manifest.json`, `GRAPH_REPORT.md`.
3. `graph_reader.GraphReader(graph_path)` loads it, computes centrality, exposes views.
4. `vault.VaultWriter` renders `index.md`, `community-*.md`, node notes, `hot.md`.
5. `brief` assembles budgeted context, calls the gatekeeper per section, writes `BRIEF.md`.
6. `gatekeeper.TokenLogger` writes one JSONL record per call to `<out>/runs/<run_type>.jsonl`.
7. `token_comparison` runs steps 5–6 twice (graph-guided, naive) and reconciles the report against
   those records.

## 6. ADR index

| ADR | Decision |
|---|---|
| 0001 | Own AST extractor instead of the external Graphify CLI |
| 0002 | Comprehension is the product; the bug-fix loop is dropped |
| 0003 | Paths are parameters; no upward config discovery |

## 7. Data contracts

### 7.1 `graph.json`
Node-link JSON (`{"directed": false, "multigraph": false, "graph": {...}, "nodes": [...],
"links": [...]}`), consumed via `networkx.node_link_graph(data, edges="links")`.

Node: `id` (path-with-underscores + symbol), `label`, `norm_label`, `file_type`
(`code` | `document`), `source_file` (repo-relative), `source_location` (`L<line>`), `community`
(int), `_origin` (`ast`).

Edge: `source`, `target`, `relation` (`contains` | `calls` | `inherits` | `method` | `references`),
`confidence` (`EXTRACTED` | `INFERRED` | `AMBIGUOUS`), `confidence_score` (float), `weight` (float),
`source_file`, `source_location`.

`contains` is load-bearing: a node that is the source of a `contains` edge is a file root, which is
how the reader separates files from entities when ranking.

### 7.2 Brief state
`repo_name`, `graph_path`, `context` (str), `files_read` (list[str]), `sections`
(list[{title, body, tag}]), `token_usage` (list[{node, input_tokens, output_tokens}]), `run_type`
(`graph_guided` | `naive`).

### 7.3 Token log (JSONL, one object per LLM call)
`{run_id, run_type, node, input_tokens, output_tokens, model}`.

## 8. Directory layout

```
repo-atlas/
├── CLAUDE.md, README.md, pyproject.toml, uv.lock
├── .github/workflows/ci.yml, .pre-commit-config.yaml
├── config/atlas.json
├── docs/{PRD,PLAN,TODO,KNOWN_LIMITATIONS}.md, docs/adr/
├── scripts/check_{file_sizes,no_hardcoded,anti_patterns,vault_consistency}.py
├── src/repo_atlas/            <- §4
└── tests/
    ├── fixtures/graph_factory.py   <- synthetic graphs; the default for every test
    ├── fixtures/golden/            <- reference graph + its 5-file source (ADR-0001)
    ├── evals/                      <- @pytest.mark.eval structural checks
    └── <mirrors src/>
```

## 9. Config

| File | Purpose | Holds |
|---|---|---|
| `config/atlas.json` | All behaviour | provider, model, `api_key_env`, rate limit, retry, pricing, extractor ignore rules + size cap, vault top-k + weights, brief budget, betweenness sampling |
| `.env` (gitignored) | Local secret | the key named by `api_key_env` |
| CLI arguments | All locations | `repo`, `--out`, `--seed`, `--budget`, `--config` |

No path is ever stored in config; no behaviour is ever hardcoded in a module (ADR-0003,
`CLAUDE.md` §3).
