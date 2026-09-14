# TODO — repo-atlas

> Scope: `docs/PRD.md` (R#.#) · Architecture: `docs/PLAN.md` · Decisions: `docs/adr/*`
> Rules: `CLAUDE.md` (overrides everything here).

## Legend

**Phases** — 0 Scaffold · 1 Extractor · 2 Graph reader · 3 Vault · 4 Brief · 5 Token comparison ·
6 CLI/SDK + docs

**Priority** — `P0` blocking/critical path · `P1` required, not blocking · `P2` nice-to-have

**Status** — `[ ]` not started · `[x]` done

**Task ID** — `PHASEN-NNN`, sequential within phase.

TDD phases are written as strict RED/GREEN pairs (odd = RED test-first, even = GREEN implement),
each phase closing with a REFACTOR item enforcing the ≤150-line budget.

## Task count per phase

| Phase | Tasks |
|---|---|
| 0 — Scaffold | 12 |
| 1 — Extractor | 26 |
| 2 — Graph reader | 16 |
| 3 — Vault | 16 |
| 4 — Brief | 18 |
| 5 — Token comparison | 14 |
| 6 — CLI/SDK + docs | 12 |
| **Total** | **114** |

---

## Phase 0 — Scaffold

> Project rules, config, gates and CI. No business logic.

- [x] **P0** `PHASE0-001` repo: fork scaffold from `ex04-graphify-agent`, drop target-specific trees
- [x] **P0** `PHASE0-002` pyproject: rename package, `networkx>=3.4`, `google-genai` → optional extra
- [x] **P0** `PHASE0-003` docs: write `CLAUDE.md` (project constitution)
- [x] **P0** `PHASE0-004` docs: write `docs/PRD.md` (R1-R6, non-goals, success criteria)
- [x] **P0** `PHASE0-005` docs: write `docs/PLAN.md` (C4, module table, data contracts)
- [x] **P0** `PHASE0-006` docs: ADR-0001 own extractor, ADR-0002 comprehension-only, ADR-0003 paths
- [x] **P0** `PHASE0-007` config: `config/atlas.json` (behaviour only, no paths) + `.env.example`
- [x] **P0** `PHASE0-008` gates: port `check_file_sizes` / `check_anti_patterns`
- [x] **P0** `PHASE0-009` gates: `check_no_hardcoded` + target-path and pinned-constant rules — ref R6.4
- [x] **P0** `PHASE0-010` gates: `check_vault_consistency` scans every note, not just index/hot
- [x] **P0** `PHASE0-011` ci: workflow + pre-commit wiring all gates, keyless
- [x] **P0** `PHASE0-012` src: `__init__` + thin `cli.py` with `version`; tests for CLI and all gates
- [ ] **P1** `PHASE0-013` repo: `uv sync`, commit lockfile, confirm the full gate set green in CI

---

## Phase 1 — Extractor (TDD)

> ADR-0001. The fixture factory lands first: nothing may pin the suite to a real artifact.

- [x] **P0** `PHASE1-001` tests: `tests/fixtures/graph_factory.py` — synthetic node-link builder
- [x] **P0** `PHASE1-002` tests: vendor the reference graph + its 5-file source to `fixtures/golden/`
- [x] **P0** `PHASE1-003` paths: RED — `RunPaths`/`RunConfig` construction and config load — ref ADR-0003
- [x] **P0** `PHASE1-004` paths: GREEN — implement `paths.py`
- [ ] **P0** `PHASE1-005` discovery: RED — ignore rules, `.gitignore`, size cap, binary skip — ref R1.3
- [ ] **P0** `PHASE1-006` discovery: GREEN — implement `discovery.py`
- [x] **P0** `PHASE1-007` py_nodes: RED — module/class/function/method nodes, id convention — ref R1.1
- [x] **P0** `PHASE1-008` py_nodes: GREEN — implement `py_nodes.py`
- [x] **P0** `PHASE1-009` py_nodes: RED — syntax error in a target file is recorded, not fatal — ref R1.5
- [x] **P0** `PHASE1-010` py_nodes: GREEN — tolerate `SyntaxError` per file
- [x] **P0** `PHASE1-011` py_edges: RED — `contains` edges make file roots resolvable — ref R2.1
- [x] **P0** `PHASE1-012` py_edges: GREEN — implement `contains`
- [x] **P0** `PHASE1-013` py_edges: RED — `calls` / `inherits` / `method` from the AST
- [x] **P0** `PHASE1-014` py_edges: GREEN — implement them
- [x] **P0** `PHASE1-015` py_edges: RED — `references` from imports, incl. relative imports
- [x] **P0** `PHASE1-016` py_edges: GREEN — implement `references`
- [x] **P0** `PHASE1-017` confidence: RED — direct call = EXTRACTED@1.0, attribute/star = INFERRED — ref R1.6
- [x] **P0** `PHASE1-018` confidence: GREEN — implement `confidence.py`
- [x] **P1** `PHASE1-019` communities: RED — greedy modularity labels every node
- [x] **P1** `PHASE1-020` communities: GREEN — implement `communities.py`
- [x] **P0** `PHASE1-021` build: RED — `graph.json` shape matches the §7.1 contract
- [x] **P0** `PHASE1-022` build: GREEN — implement `serialize.py` (envelope assembly,
      validation, writer — split out of the planned `build.py` to stay under the
      150-line cap; see `docs/PLAN.md` note)
- [x] **P1** `PHASE1-023` build: RED — `manifest.json` lets an unchanged file be skipped — ref R1.7
- [x] **P1** `PHASE1-024` build: GREEN — implement `manifest.py` (content-hash + diff)
- [x] **P0** `PHASE1-025` evals: golden regression — AST nodes + structural edges match the reference
- [ ] **P0** `PHASE1-026` extractor: REFACTOR — split any file over 150 lines; gates green

---

## Phase 2 — Graph reader (port + decouple)

- [ ] **P0** `PHASE2-001` models: port `Confidence`/`NodeView`/`EdgeView` verbatim
- [ ] **P0** `PHASE2-002` loader: RED — load from an explicit path, no upward walk — ref ADR-0003
- [ ] **P0** `PHASE2-003` loader: GREEN — implement
- [ ] **P0** `PHASE2-004` reader: RED — unknown confidence value degrades to AMBIGUOUS + warns — ref R2.3
- [ ] **P0** `PHASE2-005` reader: GREEN — tolerant parsing
- [ ] **P0** `PHASE2-006` reader: port the query surface (nodes, edges, communities, centrality)
- [ ] **P1** `PHASE2-007` metrics: RED — betweenness switches to sampling above the node threshold — ref R2.4
- [ ] **P1** `PHASE2-008` metrics: GREEN — implement `k`-sampling
- [ ] **P1** `PHASE2-009` reader: RED — `edges_of` is O(1) amortised, not a per-call scan
- [ ] **P1** `PHASE2-010` reader: GREEN — build an adjacency index once
- [ ] **P0** `PHASE2-011` filters: port, strip origin-project docstrings
- [ ] **P0** `PHASE2-012` tests: every reader test uses the factory, not the golden artifact
- [ ] **P1** `PHASE2-013` reader: RED — a graph with zero edges does not divide by zero
- [ ] **P1** `PHASE2-014` reader: GREEN — guard normalisation
- [ ] **P1** `PHASE2-015` perf: record reader construction time on the largest smoke repo
- [ ] **P0** `PHASE2-016` graph_reader: REFACTOR — file sizes, gates green

---

## Phase 3 — Vault

- [ ] **P0** `PHASE3-001` index: port `render_index`
- [ ] **P0** `PHASE3-002` notes: port `render_node_note`
- [ ] **P0** `PHASE3-003` communities: RED — a `community-N.md` exists for every referenced community — ref R3.1
- [ ] **P0** `PHASE3-004` communities: GREEN — implement `vault/communities.py`
- [ ] **P0** `PHASE3-005` ranking: RED — no seed ⇒ pure weighted centrality, never all-zero — ref R3.3
- [ ] **P0** `PHASE3-006` ranking: GREEN — make `seed_id` optional
- [ ] **P0** `PHASE3-007` ranking: RED — an explicit seed absent from the graph raises, loudly
- [ ] **P0** `PHASE3-008` ranking: GREEN — validate the seed
- [ ] **P1** `PHASE3-009` ranking: RED — weights and top-k are arguments, not config lookups
- [ ] **P1** `PHASE3-010` ranking: GREEN — parameterise
- [ ] **P0** `PHASE3-011` writer: RED — a generated vault has zero dangling wikilinks — ref R3.1
- [ ] **P0** `PHASE3-012` writer: GREEN — implement `VaultWriter.write_all`
- [ ] **P1** `PHASE3-013` writer: RED — `hot.md` states its metric honestly (seeded vs unseeded)
- [ ] **P1** `PHASE3-014` writer: GREEN — render the metric line from actual parameters
- [ ] **P1** `PHASE3-015` evals: run `check_vault_consistency` over a generated vault in CI
- [ ] **P0** `PHASE3-016` vault: REFACTOR — file sizes, gates green

---

## Phase 4 — Brief (TDD)

- [ ] **P0** `PHASE4-001` state: RED/GREEN — brief state schema — ref PLAN §7.2
- [ ] **P0** `PHASE4-002` gatekeeper: port client/provider/token_log
- [ ] **P0** `PHASE4-003` gatekeeper: RED — provider dispatch honours `config["provider"]`
- [ ] **P0** `PHASE4-004` gatekeeper: GREEN — registry dispatch + `offline` provider — ref R6.1
- [ ] **P1** `PHASE4-005` gatekeeper: RED — a provider 429 surfaces as `RateLimitError` and retries
- [ ] **P1** `PHASE4-006` gatekeeper: GREEN — map provider errors onto the retry path
- [ ] **P0** `PHASE4-007` context: RED — graph context stays under the configured budget — ref R4.1
- [ ] **P0** `PHASE4-008` context: GREEN — implement budgeted assembly
- [ ] **P0** `PHASE4-009` context: RED — source slices come from `source_location`, not whole files — ref R4.2
- [ ] **P0** `PHASE4-010` context: GREEN — implement slicing
- [ ] **P0** `PHASE4-011` context: RED — naive dump obeys the same ignore rules
- [ ] **P0** `PHASE4-012` context: GREEN — reuse `discovery` for the dump
- [ ] **P0** `PHASE4-013` nodes: RED — one gatekeeper call per section, each token-logged
- [ ] **P0** `PHASE4-014` nodes: GREEN — implement `summarize`
- [ ] **P0** `PHASE4-015` nodes: RED — every section carries a tag; INFERRED prose hedges — ref R4.3
- [ ] **P0** `PHASE4-016` nodes: GREEN — enforce tagging in the renderer
- [ ] **P1** `PHASE4-017` write_brief: RED/GREEN — `BRIEF.md` links resolve into the vault — ref R4.4
- [ ] **P0** `PHASE4-018` brief: REFACTOR — file sizes, gates green

---

## Phase 5 — Token comparison

- [ ] **P0** `PHASE5-001` models/metrics/comparison/cost: port
- [ ] **P0** `PHASE5-002` metrics: keep `_assert_logs_agree` — reported numbers must equal logs — ref R5.2
- [ ] **P0** `PHASE5-003` runner: RED — both routes run the same prompt, differing only in context
- [ ] **P0** `PHASE5-004` runner: GREEN — implement `run_both`
- [ ] **P0** `PHASE5-005` coverage: RED — fraction of hot nodes + modules cited by the brief — ref R5.3
- [ ] **P0** `PHASE5-006` coverage: GREEN — implement the metric
- [ ] **P0** `PHASE5-007` report: RED — table renders from metrics, no hardcoded prose or numbers
- [ ] **P0** `PHASE5-008` report: GREEN — implement `render_report`
- [ ] **P1** `PHASE5-009` cost: RED/GREEN — cost from config pricing; zero for the offline provider
- [ ] **P1** `PHASE5-010` report: RED — a mismatch between log and report fails the run
- [ ] **P1** `PHASE5-011` report: GREEN — reconcile before rendering
- [ ] **P1** `PHASE5-012` evals: keyless comparison shows a real reduction via the mock's token counts
- [ ] **P2** `PHASE5-013` run: one real-key run; commit the report as static evidence
- [ ] **P0** `PHASE5-014` token_comparison: REFACTOR — file sizes, gates green

---

## Phase 6 — CLI / SDK / docs

- [ ] **P0** `PHASE6-001` sdk: RED — every method takes `RunPaths`; no global state — ref ADR-0003
- [ ] **P0** `PHASE6-002` sdk: GREEN — implement the façade
- [ ] **P0** `PHASE6-003` cli: RED/GREEN — `atlas extract` with `--out`
- [ ] **P0** `PHASE6-004` cli: RED/GREEN — `atlas vault` with `--seed`
- [ ] **P0** `PHASE6-005` cli: RED/GREEN — `atlas brief` with `--budget`
- [ ] **P0** `PHASE6-006` cli: RED/GREEN — `atlas map` (extract + vault + brief)
- [ ] **P1** `PHASE6-007` cli: RED/GREEN — `atlas compare`
- [ ] **P0** `PHASE6-008` evals: self-hosting — `atlas map .` describes this repo correctly — ref PRD §6.1
- [ ] **P1** `PHASE6-009` evals: third-party smoke on 3 repos of different shapes — ref PRD §6.3
- [ ] **P1** `PHASE6-010` docs: README walkthrough with real output excerpts
- [ ] **P1** `PHASE6-011` docs: `KNOWN_LIMITATIONS.md` updated from what the smoke runs revealed
- [ ] **P0** `PHASE6-012` release: tag 0.1.0 with all gates green
