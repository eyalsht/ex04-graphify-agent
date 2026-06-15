---
name: tdd-cycle
description: |
  Use this skill when implementing any new feature, function, class, or module. Triggers include:
  "implement", "let's build", "add a feature", "write a function", "create a class",
  "add a method", "let's code", "now build", "let's write".
  Always apply for any new code that has logic — skip only for pure config/data files.
---

# TDD Cycle (Red → Green → Refactor)

Enforces strict test-first discipline per CLAUDE.md §3 / §7 (RED → GREEN → REFACTOR; tests
committed before or with the code, never after).

## The cycle (one feature at a time)

### Phase 1: RED — write the failing test FIRST

1. Open or create the matching test file in `tests/unit/test_<module>/`, where `<module>` ∈
   `{graph_reader, weakness_detector, obsidian_writer, agent_workflow, gatekeeper,
   token_comparison, sdk, cli}`.
2. Write a test that **describes the desired behavior**, not the implementation.
3. Use descriptive test names: `test_degree_of_polygon_god_node_is_four`, not `test_degree`.
4. Cover the **specific edge case** you're targeting in this cycle.
5. Run the test — it MUST fail:
   ```bash
   uv run pytest tests/unit/test_graph_reader/test_metrics.py::test_degree_of_polygon_god_node_is_four -xvs
   ```
6. Verify the failure message is meaningful (e.g., `AttributeError: module 'ex04_graphify_agent.graph_reader.metrics' has no attribute 'degree'`), not a syntax error or import error in unrelated code.

**Commit RED:**
```bash
git add tests/
git commit -m "test(graph_reader): failing test for degree() on Polygon god node"
```

### Phase 2: GREEN — write the MINIMAL code to pass

1. Write only enough implementation to make the failing test pass — nothing more.
2. Resist the temptation to add features that aren't tested yet.
3. Run the same test — it MUST now pass:
   ```bash
   uv run pytest tests/unit/test_graph_reader/test_metrics.py::test_degree_of_polygon_god_node_is_four -xvs
   ```
4. Run the full test suite to confirm nothing else broke (keyless by default — D5/ADR-0005):
   ```bash
   uv run pytest -x
   ```

**Commit GREEN:**
```bash
git add src/
git commit -m "feat(graph_reader): implement degree() to pass Polygon god-node test"
```

### Phase 3: REFACTOR — improve without changing behavior

1. Now that the test is green, you can safely improve the code:
   - Extract repeated logic
   - Improve names
   - Add docstrings
   - Reduce file size if approaching the 150-line limit (split, never compress — CLAUDE.md §3)
2. Run the tests again — they MUST still pass:
   ```bash
   uv run pytest -x
   ```
3. Refactor commits are optional — if you wrote clean code first time, skip this.

**Commit REFACTOR (if needed):**
```bash
git add src/
git commit -m "refactor(graph_reader): extract _build_adjacency helper from degree"
```

## Rules of the cycle

1. **One concern per cycle.** Don't write a test for `degree()` then implement both `degree()` and `betweenness()`. Each function gets its own RED → GREEN cycle.
2. **No skipping RED.** If you implement code without a test first, the cycle is broken. Delete the code, write the test, then re-implement.
3. **Verify each phase with output.** Don't just "trust" the test passed — read the pytest output. Look for `1 passed` after GREEN, `1 failed` after RED.
4. **No `pytest.skip` to defer work.** Either write the test now or remove it. Skipped tests rot.
5. **Coverage is a side effect, not the goal.** ≥ 90% coverage (CLAUDE.md §2, tightened from the course's 85%) emerges naturally from disciplined TDD. Don't write tests just to inflate coverage on a function that has no logic.

## What "minimal" means in GREEN

Pseudo-example drawn from `docs/PRD_graph_reader.md` (the real `Polygon` god node —
`polygons_polygons_polygon`, degree 4, the highest in `artifacts/graphify/graph.json`). Test:
```python
def test_degree_of_polygon_god_node_is_four():
    g = load_graph(Path("artifacts/graphify/graph.json"))
    assert degree(g)["polygons_polygons_polygon"] == 4
```

Minimal GREEN that passes:
```python
def degree(g: "KnowledgeGraph") -> dict[str, int]:
    counts: dict[str, int] = {node.id: 0 for node in g.nodes}
    for edge in g.edges:
        counts[edge.source] += 1
        counts[edge.target] += 1
    return counts
```

That's it. No betweenness (no test demands it). No confidence filtering (no test demands it). Add those in their own RED → GREEN cycles.

## When the test should be an integration test

Unit tests cover one module in isolation. Integration tests cover module composition.

Use `tests/integration/` for tests that:
- Touch multiple `src/ex04_graphify_agent/` modules
- Verify the `sdk.py` façade surface end-to-end
- Confirm the full pipeline (graph_reader → weakness_detector → agent_workflow → token_comparison) works

Use `tests/unit/` for everything else. All tests run **keyless** — the gatekeeper's
provider client is mocked at its boundary (ADR-0005), so no provider API key (e.g.
`GEMINI_API_KEY`) is needed.

## Verification before signaling success

After completing a cycle, run:
```bash
uv run pytest --cov=src --cov-report=term-missing   # full suite, keyless
uv run ruff check .                                  # 0 violations
uv run mypy --strict src/                            # 0 errors
```

All must be green. If any fails, the cycle isn't complete.
