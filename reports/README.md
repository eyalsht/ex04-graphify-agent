# Reports (Phase 7)

Evidence and narrative for the EX04 graph-guided fix. Every quantitative claim links back to
a committed artifact or a re-runnable command (R10.5 / CLAUDE.md §4) — nothing here is an
estimate.

| Report | Covers | Requirements |
|---|---|---|
| [`root_cause.md`](root_cause.md) | Single root cause (half-finished `Polygon`); 5 symptoms; how the graph localized it; correctness gate | R4.5, R5.2.2, R5.5.3, R7.7 |
| [`diff_polygons.md`](diff_polygons.md) | Literal before/after unified diff, change-by-change, TODO removal | R5.2.4, R7.6, R7.43 |
| [`oop_improvement.md`](oop_improvement.md) | Why "finish the class" is the right OOP move; each improvement tied to a signal | R3.4, R5.2.3, R7.7, R4.4 |
| [`graph_diff.md`](graph_diff.md) | PRE vs POST graph (machine-rendered): rationale nodes removed, `Polygon` gains a `calls` edge | R5.6.3 |
| [`token_comparison.md`](token_comparison.md) | Keyless input-context delta (76.7% reduction) + pending keyed run | R5.6, R7.8, R4.1, R4.2 |
| [`diagrams.md`](diagrams.md) | C4 context/container, both agent routes, pipeline (Mermaid); topology verified vs `build_graph` | R5.4.2, R7.3 |
| [`pipeline.md`](pipeline.md) | End-to-end pipeline + inspectable artifacts; six-signal convergence; R4.3/R4.6/R4.7 | R4.3, R4.5, R4.6, R4.7, R5.5 |
| [`screenshots.md`](screenshots.md) | Committed graph renders (Fig. 1/2) + **pending** Obsidian capture instructions | R5.4.1, R7.9, R10.3 |

## Reproduce everything from a clean checkout (R1.5 / R10.1)

```bash
uv sync
uv run pytest -m eval            # the keyless thesis evals (token-delta, structural)
uv run python scripts/render_graph.py artifacts/graphify/graph.json reports/img/graph_pre_fix.png  "(PRE-FIX)"
uv run python scripts/render_graph.py artifacts/graphify_post_fix/graph.json reports/img/graph_post_fix.png "(POST-FIX)"
# graph diff (PRE vs POST):
uv run python -c "import sys; sys.path.insert(0,'src'); \
from ex04_graphify_agent.token_comparison.graph_diff import diff_graphs, render_graph_diff; \
print(render_graph_diff(diff_graphs('artifacts/graphify/graph.json','artifacts/graphify_post_fix/graph.json')))"
```

The POST-FIX graph itself was produced keylessly with `graphify update data/broken-python`
(AST extraction, 0 tokens) after applying the fix; the PRE-FIX baseline under
`artifacts/graphify/` is never regenerated in place (CLAUDE.md §4).

## Open items (owner action — see `docs/KNOWN_LIMITATIONS.md`)

1. ✅ **Obsidian screenshots** — captured (Figures 3–6 in [`screenshots.md`](screenshots.md) §2).
2. ✅ **Keyed token + cost run** — done on `gemini-2.5-flash`: graph-guided **passed** at
   **$0.0030** vs naive **fail** at $0.0078 (57.5% fewer input tokens, 61.4% lower cost). The
   R5.6.5 table + cost are in [`token_comparison.md`](token_comparison.md); per-call ledgers
   in [`../artifacts/runs/`](../artifacts/runs/); the model-switching log in
   [`run_journey.md`](run_journey.md). Re-runnable: `uv run python scripts/run_comparison.py`
   (needs `GEMINI_API_KEY`; model/pricing config-driven). *(No open items remain.)*
