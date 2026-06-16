# Graph Visuals & Obsidian Screenshots (R5.4.1 / R7.9 / R10.3)

This page has two kinds of visual evidence:

1. **Committed, reproducible renders** of the Graphify graph (generated keylessly by
   `scripts/render_graph.py` — no Obsidian, no API key).
2. **Obsidian app screenshots** (R5.4.1 / R7.9 / R10.3) — captured from the vault open in the
   Obsidian desktop app. **Status: done** (Figures 3–6 below).

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

## 2. Obsidian app screenshots (captured)

The required Obsidian-UI deliverables (R5.4.1 graph view, R7.9 committed images, R10.3
`hot.md`), captured from the vault open in the Obsidian desktop app.

### Graph View (R5.4.1 / R7.9)

![Obsidian Graph View of the EX04 vault: 23 note-nodes plus the 6 community hubs and the
index/hot map-notes, force-laid-out into the polygons and mathsquiz clusters around the
central index hub.](img/obsidian_graph_view.png)

*Figure 3 — Obsidian Graph View. `index` is the central map-note linking every node; the
polygons subgraph (top-left) and the mathsquiz subgraph (bottom) separate naturally.*

### The Polygon god node (R4.6)

![Obsidian Graph View focused on polygons_polygons_polygon: the node is highlighted and its
incident links to index, hot, polygons_polygons, calc_polygon_details, object and
polygon_init are drawn in colour while the rest of the graph fades.](img/obsidian_polygon_node.png)

*Figure 4 — `polygons_polygons_polygon` (the Polygon god node) selected. Its highlighted
links fan out to the module, `hot`, and the functions that use it — the coupling surface the
fix targeted. This is the "follow the links from the hottest node" path made visual.*

### hot.md — "where to look first" (R10.3)

![Obsidian reading view of hot.md: the ranked list with Polygon at #1 (degree 4, bw 0.0563),
calc_polygon_details #2, then the rationale TODO nodes, each annotated with its metric and
source location.](img/obsidian_hot.png)

*Figure 5 — `hot.md` in reading view. Ranked by centrality × proximity-to-bug; `Polygon` is
#1 and every entry is a clickable wikilink to its node note.*

### index.md — community navigation (R5.1.3)

![Obsidian reading view of index.md: a Graph Index listing the 6 communities as links
followed by an All Nodes list of every node as a wikilink.](img/obsidian_index.png)

*Figure 6 — `index.md` in reading view: the 6 communities and the full node list, all
wikilinked.*

> Capture note: taken from a local scratch vault (`obsidian/HW4/`, gitignored) populated with
> copies of the 31 notes from the deliverable `obsidian/` vault, so these screenshots reflect
> the committed vault exactly.

---

## How Obsidian helped (R4.6)

Even before the screenshots, the *navigation* value is concrete: opening `obsidian/hot.md`
puts `[[polygons_polygons_polygon|Polygon]]` at the top of the reading order, and clicking
its wikilinks walks straight to `calc_polygon_details` and `draw_polygon` — the two functions
that needed editing — without ever scrolling raw source. That "follow the links from the
hottest node" path is exactly what the graph-guided agent automates in its `read_vault →
hypothesize` step (see [`pipeline.md`](pipeline.md)).
