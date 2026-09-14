# ADR-0001 — Build our own AST extractor instead of depending on Graphify

- **Status:** Accepted
- **Date:** 2026-09-14
- **Supersedes:** the origin project's black-box treatment of Graphify

## Context

The origin project (`ex04-graphify-agent`) consumed `graph.json` as a committed artifact produced by
an external CLI. Its own docs state the position plainly: "Graphify is consumed as a **black-box
tool**; this project does not regenerate its internals" (`docs/PRD.md` §3). The only invocation
recorded anywhere in that repo is `graphify update data/broken-python` (v0.8.39, AST mode, keyless),
noted in `docs/KNOWN_LIMITATIONS.md`. Nothing in its `src/` writes a graph, there is no install
path, no version pin, no submodule, and no package on any index.

For a tool whose entire purpose is "point me at a repo I do not know", an undocumented external
binary in the critical path is fatal: a user who does not already have `graphify` on `$PATH` cannot
produce an input at all.

## Decision

Build the graph extractor in this repository, on the Python standard library's `ast` module, and
emit the same node-link schema the existing reader consumes:

- nodes: `id, label, norm_label, file_type, source_file, source_location, community, _origin`
- edges: `source, target, relation, confidence, confidence_score, weight, source_file,
  source_location`
- relations: `contains`, `calls`, `inherits`, `method`, `references`

Communities are computed locally with `networkx` greedy modularity, filling the field Graphify used
to supply. Non-Python files become file nodes with no symbol extraction.

## Consequences

**Good.** Zero external dependencies for graph construction; runs offline and keyless; the schema
stays identical so `graph_reader`, `vault` and `brief` port unchanged; extraction becomes testable
and versioned with the rest of the code.

**Cost.** We do not reproduce Graphify's LLM-derived nodes and edges — its `document` /`rationale`
nodes and its `rationale_for`, `semantically_similar_to`, `conceptually_related_to` relations are
semantic, not syntactic. Our graphs will be structurally complete and semantically thinner. The
brief layer recovers some of that at query time rather than at extraction time.

**Verification.** The origin project's committed `artifacts/graphify/graph.json` (23 nodes, 20
links, over a known 5-file repo) is kept at `tests/fixtures/golden/` as a regression oracle: our
extractor must reproduce its AST-origin node set and its `contains`/`calls`/`inherits`/`method`
edges exactly, with the semantic deltas above documented as intentional.
