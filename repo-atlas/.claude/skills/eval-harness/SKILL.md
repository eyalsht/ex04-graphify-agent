---
name: eval-harness
description: |
  Use this skill when building, running, or reasoning about the project's evals — the layer
  that proves the system produces *correct graph/vault/brief output*, distinct from tests that
  prove the code merely *runs*. Triggers: "eval", "validity", "structural eval",
  "known-answer", "golden graph", "does the brief actually explain the repo", "prove the core",
  "schema check", "pass^k", "token-efficiency eval". Apply whenever a change could affect
  whether the system does the *right thing*, not just whether it executes.
---

# Eval Harness (Eval-Driven Development) — repo-atlas

Tests prove the code runs. **Evals prove the output is right**: that the graph reflects the
repo, that `hot.md` surfaces what actually matters, that the brief describes a real
architecture rather than a plausible-sounding one, and that the token saving is real rather
than bought by saying less.

## The five structural evals

All run **keyless**, under `tests/evals/`, marker `eval`, and each must hold on **every** run
(`pass^k = 100%`).

1. **Golden-graph regression** — `atlas extract` on `tests/fixtures/golden/` reproduces the
   reference graph's AST-origin node ids and its `contains` / `calls` / `inherits` / `method`
   edges exactly. Deltas are limited to the semantic node and edge types documented as out of
   scope in ADR-0001; a delta anywhere else is an extractor bug.
2. **Schema validity** — every emitted `graph.json` satisfies the `docs/PLAN.md` §7.1 contract:
   required node and edge keys present, `confidence` ∈ {EXTRACTED, INFERRED, AMBIGUOUS},
   `source_file` repo-relative, every edge endpoint a real node id.
3. **Vault integrity** — a generated vault has zero dangling wikilinks (every `[[id]]` resolves,
   `community-N.md` included) and every graph node has exactly one note.
4. **Ranking sanity** — on a synthetic graph with a known hub, `hot.md` ranks that hub first;
   with no seed the ranking is centrality-only and never degenerate (not all scores equal, not
   all zero).
5. **Token-efficiency** — the graph-guided context is strictly smaller than the naive dump for
   the same repo, measured through the mock client's real token counts, so the claim holds
   keylessly.

Self-hosting (`atlas map .` describing this repo correctly) is the sixth check, but it needs a
key — it belongs to the behavioural set below, not to CI.

## Behavioural evals — real-LLM runs, opt-in, committed as evidence

The actual graph-guided vs naive numbers (PRD R5.1) need a real provider key and are produced
by a **manual, run-once** comparison — never collected by pytest, never in CI. Reported with
**pass@k** framing. Their outputs (token counts, the comparison report, the brief itself) are
committed as static artifacts so a reader verifies the numbers **without a key**.

Judging a brief is qualitative, so make the criteria explicit before the run: does it name the
real entry points, does the module map match the actual package layout, does it cite hot nodes,
and are INFERRED claims hedged? Record the verdict, not just the tokens.

## How to run

```bash
# Structural evals only (keyless, fast — what CI runs):
uv run pytest -m eval

# Full keyless suite (unit tests + evals, no behavioural):
uv run pytest -m "not behavioural"

# The real-numbers comparison (manual, needs the configured API key — NOT in CI):
uv run atlas compare <repo>
```

Structural evals must pass with **no API key present**. An eval must never trigger a real LLM
call.

## Fixtures

Evals build graphs with `tests/fixtures/graph_factory.py`. The **only** eval permitted to read
`tests/fixtures/golden/` is the golden-graph regression. Pinning the suite to one real artifact
is what made this project's predecessor impossible to retarget — do not reintroduce it.

## The discipline (non-negotiable)

A failing eval is **fixed, or honestly disclosed in `docs/KNOWN_LIMITATIONS.md` — never
rationalised away.** The eval layer exists so a mis-ranked hub, a fabricated token saving, or a
confidently wrong brief is *caught*, not explained after the fact.

- Structural eval red in CI → the core is wrong (graph mis-parsed, ranking degenerate, vault
  inconsistent); fix before merge.
- Behavioural eval red in the manual run → fix the prompt or the context selection, or log a
  limitation with what / why / fix-sketch and a linked issue.
- Never delete an eval to make it green, and never substitute an estimate for a measured token
  number — every figure traces to a gatekeeper log record (PRD R5.2).
