# Graph Visuals & Obsidian Screenshots (R5.4.1 / R7.9 / R10.3)

This page has two kinds of visual evidence:

1. **Committed, reproducible renders** of the Graphify graph (generated keylessly by
   `scripts/render_graph.py` — no Obsidian, no API key). These are in the repo now.
2. **Obsidian app screenshots** (R5.4.1 / R7.9) — these *must* be captured by a human from
   the Obsidian desktop app and dropped into `reports/img/`. Placeholders + exact
   instructions are below. **Status: PENDING owner action.**

---

## 1. Committed graph renders (available now)

### PRE-FIX knowledge graph

![PRE-FIX Graphify knowledge graph of broken-python: 23 nodes, 20 edges, 6 communities. The
Polygon class node is ringed in red as the highest-degree god node; three TODO-derived
rationale nodes hang off the polygons subgraph.](img/graph_pre_fix.png)

*Figure 1 — PRE-FIX graph (`artifacts/graphify/graph.json`). Node size = degree, colour =
community, red ring = the `Polygon` god node (degree 4) at the bug location. The three
`# TODO ...` rationale nodes around `polygons.py` are signal 5.*

### POST-FIX knowledge graph

![POST-FIX Graphify knowledge graph: 23 nodes, 17 edges. The three TODO rationale nodes are
gone and the Polygon node now has an inbound calls edge from
calc_polygon_details.](img/graph_post_fix.png)

*Figure 2 — POST-FIX graph (`artifacts/graphify_post_fix/graph.json`). The three `rationale`
nodes have disappeared (the TODOs were resolved) and `calc_polygon_details -calls-> Polygon`
now exists. See [`graph_diff.md`](graph_diff.md).*

> **Interactive version:** Graphify also emitted
> [`artifacts/graphify_post_fix/graph.html`](../artifacts/graphify_post_fix/graph.html) — open
> it in a browser for a zoomable, draggable force graph of the POST-FIX state.
>
> Regenerate the PNGs any time (deterministic, seeded layout):
> ```bash
> uv run python scripts/render_graph.py artifacts/graphify/graph.json reports/img/graph_pre_fix.png "...(PRE-FIX)"
> uv run python scripts/render_graph.py artifacts/graphify_post_fix/graph.json reports/img/graph_post_fix.png "...(POST-FIX)"
> ```

---

## 2. Obsidian screenshots — PENDING owner action

These are required deliverables (R5.4.1 graph view, R7.9 committed images, R10.3 `hot.md`).
The renders above are a substitute for reviewers without Obsidian; the assignment still asks
for the real Obsidian UI. Please capture the four PNGs below.

### How to capture (≈5 minutes)

1. Open Obsidian → **Open folder as vault** → select the repo's `obsidian/` directory.
2. For each shot, use your OS screenshot tool and save into `reports/img/` with the exact
   filename listed, then commit. (Windows: `Win+Shift+S`; macOS: `Cmd+Shift+4`.)

| # | Filename to save | What to show | Requirement |
|---|---|---|---|
| 1 | `reports/img/obsidian_graph_view.png` | The **Graph View** (ribbon → "Open graph view"). Let it settle so clusters are visible. | R5.4.1 / R7.9 |
| 2 | `reports/img/obsidian_polygon_node.png` | Graph View **zoomed/focused on the `polygons_polygons_polygon` (Polygon) node** so its 4 links are visible — the god node. | R4.6 |
| 3 | `reports/img/obsidian_hot.png` | `hot.md` open in **reading view** (the ranked "where to look first" list). | R10.3 |
| 4 | `reports/img/obsidian_index.png` | `index.md` open, showing the 6-community navigation. | R5.1.3 |

### After capturing

Once the four files exist, add them under section 1's style with captions, and tick
PHASE7-018..021 + PHASE8-053 in `docs/TODO.md`. Until then these requirements are tracked as
**open** in `docs/KNOWN_LIMITATIONS.md`.

> Tip: Obsidian's Graph View colour-groups can be set to match communities via
> Settings → Graph → Groups (optional polish for shot #1).

---

## How Obsidian helped (R4.6)

Even before the screenshots, the *navigation* value is concrete: opening `obsidian/hot.md`
puts `[[polygons_polygons_polygon|Polygon]]` at the top of the reading order, and clicking
its wikilinks walks straight to `calc_polygon_details` and `draw_polygon` — the two functions
that needed editing — without ever scrolling raw source. That "follow the links from the
hottest node" path is exactly what the graph-guided agent automates in its `read_vault →
hypothesize` step (see [`pipeline.md`](pipeline.md)).
