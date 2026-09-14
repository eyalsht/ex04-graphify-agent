# PRD — repo-atlas

> Source of truth for scope. Architecture lives in `docs/PLAN.md`, decisions in `docs/adr/`,
> execution in `docs/TODO.md`. Project rules in `CLAUDE.md` override everything here.

## 1. Problem

Reading an unfamiliar repository costs either a lot of human time or a lot of context window.
Dumping a source tree into an LLM is the naive answer: it scales with repo size, most of what it
sends is irrelevant to any given question, and it produces no artifact a human can navigate
afterwards.

A structural map of the repo — what exists, what calls what, what is central — is small, cheap to
build from the AST, and is exactly the index needed to decide *which* few files actually deserve to
be read.

## 2. Users and use cases

| User | Situation | Wants |
|---|---|---|
| New contributor | Cloned a repo, first day | "What does this do, where do I start reading?" |
| Reviewer | PR touching unfamiliar modules | "What depends on this, what is central here?" |
| Maintainer | Inherited a codebase | A navigable vault that stays useful after the session |

## 3. Product

`atlas map <repo>` produces three artifacts in `<repo>/.atlas/` (or `--out`):

1. **`graph.json`** — nodes for modules, classes, functions and methods; edges for `contains`,
   `calls`, `inherits`, `method`, `references`. Plus `manifest.json` (for incremental re-runs) and
   a `GRAPH_REPORT.md` summary.
2. **A vault** — `index.md`, one note per community, one note per node, and `hot.md`: the ranked
   "read these first" list. Obsidian-compatible wikilinks; usable in any Markdown editor.
3. **`BRIEF.md`** — an LLM-written architecture and onboarding brief: what the repo does, entry
   points, module map, hot spots, data flow, where to start. Every claim tagged EXTRACTED /
   INFERRED / AMBIGUOUS.

## 4. Requirements

### R1 — Extraction
- **R1.1** Build a graph from any Python repository using only the standard library's `ast`.
- **R1.2** Never execute target code. Parse only.
- **R1.3** Skip `.git`, caches, virtualenvs, build output, binaries and oversized files; honour
  `.gitignore` and a configurable exclude list.
- **R1.4** Index non-Python files as file nodes; no symbol extraction.
- **R1.5** Survive syntax errors in target files — record the file, skip its symbols, continue.
- **R1.6** Tag every edge with a confidence: `EXTRACTED` for direct AST facts, `INFERRED` for
  heuristically resolved targets (attribute calls, star-imports).
- **R1.7** Write `manifest.json` so an unchanged file can be skipped on re-run.

### R2 — Graph reading
- **R2.1** Degree and betweenness per node; communities from the graph itself.
- **R2.2** Filter and query by confidence, community, and centrality.
- **R2.3** Tolerate unknown confidence values (downgrade to AMBIGUOUS, warn) rather than crashing.
- **R2.4** Stay usable on large graphs — sampled betweenness above a configured node count.

### R3 — Vault
- **R3.1** `index.md`, `community-N.md`, and one note per node, with no dangling wikilinks.
- **R3.2** `hot.md` ranked by a documented metric: weighted degree/betweenness, optionally
  multiplied by proximity to a `--seed` node.
- **R3.3** With no seed, rank on centrality alone. Never silently produce a degenerate ranking.

### R4 — Brief
- **R4.1** Assemble context from the graph and vault under a configurable token budget — never the
  whole source tree.
- **R4.2** Open only the source slices of the top-ranked nodes.
- **R4.3** Tag every claim; hedge INFERRED and AMBIGUOUS claims in the prose itself.
- **R4.4** Link back into the vault so a reader can follow any claim to its node.

### R5 — Evidence
- **R5.1** Run the same brief prompt graph-guided and naive-dump; report input tokens, output
  tokens, files read, LLM calls, duration, cost.
- **R5.2** Every reported number must equal a stored gatekeeper log record — assert, do not trust.
- **R5.3** Report a coverage measure alongside the token reduction, so brevity cannot be bought by
  saying less.

### R6 — Operability
- **R6.1** Work with no API key (offline mock provider); the full test suite runs keyless.
- **R6.2** Provider and model config-driven; swapping providers touches no module but the adapter.
- **R6.3** Secrets from `os.environ` only.
- **R6.4** No target-repo literal anywhere in `src/` — enforced by a CI gate.

## 5. Non-goals

- Finding or fixing bugs (see `docs/adr/0002-*`).
- Languages other than Python for symbol extraction.
- Executing, building, or testing the target repository.
- Hosting, a web UI, or an editor plugin.
- Reproducing Graphify's LLM-derived semantic nodes and edges (see `docs/adr/0001-*`).

## 6. Success criteria

1. `atlas map` on this repository produces a brief that correctly describes the
   extractor → reader → vault → brief pipeline, and a `hot.md` surfacing its core modules.
2. `atlas extract` on the golden fixture reproduces the reference graph's AST-origin nodes and
   structural edges exactly.
3. Three third-party Python repositories of different shapes map without a crash, within budget.
4. Graph-guided input tokens are materially below the naive dump at equal or better coverage.
