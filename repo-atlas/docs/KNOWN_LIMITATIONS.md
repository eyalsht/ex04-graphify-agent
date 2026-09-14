# Known limitations — repo-atlas

Honest, current, and updated as phases land. Nothing here is a promise that it will be fixed.

## Scope limits (by decision, not by omission)

- **Python only for symbols.** Other languages are indexed as file nodes with no internal
  structure. A polyglot repo gets a partial map, and the brief will say so. (`docs/PRD.md` §5)
- **No bug finding, no repair.** Dropped deliberately; see `docs/adr/0002-*`.
- **Syntactic, not semantic.** Our extractor reads the AST. It does not know that two differently
  named functions do the same thing, or that a module is "the auth layer" — the origin tool got
  some of that from LLM-derived nodes we do not reproduce (`docs/adr/0001-*`). The brief recovers
  part of it at query time, which is slower per question but cheaper per repo.
- **The target repo is never executed.** Dynamic dispatch, plugin registries, entry points resolved
  at runtime, and metaprogramming are invisible to a parser. Anything inferred from them is tagged
  `INFERRED` at best.

## Technical limits

- **Call resolution is heuristic.** `foo()` where `foo` is imported resolves; `obj.method()`,
  `getattr`, and star-imports resolve by name match at best and are tagged `INFERRED` with a
  confidence below 1.0. Expect both false edges and missing edges in dynamic code.
- **Betweenness is sampled on large graphs.** Above the configured node count the centrality
  ranking is approximate, so `hot.md` ordering can shift slightly between runs on big repos.
- **Community labels are not stable across runs.** Greedy modularity is deterministic for a fixed
  graph, but a small source change can renumber communities, which renames `community-N.md` notes.
- **`hot.md` is a centrality ranking, not a relevance ranking.** Central ≠ important-to-your-task.
  With `--seed` it becomes proximity-weighted, which is better but still structural.
- **Briefs are LLM output.** Tagged and grounded in the graph, but not verified line by line. An
  `EXTRACTED` tag guarantees the *graph fact* is real, not that the sentence around it is.
- **Offline mode produces no insight.** With no API key the gatekeeper returns mock text: the graph,
  vault, token accounting and the whole test suite are real, but `BRIEF.md` is a placeholder.

## Verified gaps in the extractor

These are measured against the golden reference graph, not guessed at. The eval in
`tests/evals/test_golden_regression.py` holds us to them: 19 of 19 in-scope nodes match the
reference attribute-for-attribute, and 14 of its 15 in-scope edges are reproduced.

- **One unreachable edge.** The reference contains a `calls` edge anchored at
  `polygons.py:29` — a call site inside the exact region of the file that fails to parse.
  Our degraded line scan deliberately does not guess at call edges, because resolving a call
  needs scope a regex cannot see and a wrong edge is worse than a missing one. So this edge
  is permanently out of reach for us, and the eval asserts it is *the only* miss rather than
  quietly tolerating any shortfall.
- **Degraded files produce weaker claims.** Two of the five golden files do not parse
  (a Python-2 `print` statement; a JavaScript `new`). We recover their classes, functions and
  methods by line scan and tag every resulting node and edge `INFERRED` at 0.7, where the
  reference tagged them `EXTRACTED`. That divergence is deliberate: a fact a regex found is
  genuinely less certain than one the parser confirmed, and saying otherwise would make the
  confidence tags decoration.
- **Community integers are not comparable to the reference.** Its partition was computed over
  a larger edge set that included five document-pipeline edges we do not produce, so the eval
  asserts node and edge structure and never `community`.
- **No semantic edges.** `rationale_for` aside, the reference's `references`,
  `semantically_similar_to` and `conceptually_related_to` edges came from an LLM pass over
  prose. We emit none of them (ADR-0001), and the eval asserts their four source nodes are
  absent rather than fabricated.

## Open items

- [ ] `uv.lock` not yet committed — `PHASE0-013`.
- [ ] No performance figures yet; the largest repo mapped so far is none. `PHASE2-015` records the
      first real numbers.
- [ ] `pyproject.toml` authors are carried over from the origin project (joint coursework). Confirm
      who should be listed here before any public release, and confirm the Latin spelling of Eyal's
      surname ("Shtinmtez" vs the "shtinmetz" in his email).
- [ ] The golden fixture is a 5-file repository. It validates correctness of the extractor's
      structural output, not its behaviour at scale.
