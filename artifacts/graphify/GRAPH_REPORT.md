# Graph Report - broken-python  (2026-06-13)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 23 nodes · 20 edges · 6 communities
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 2 edges (avg confidence: 0.85)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 4|Community 4]]

## God Nodes (most connected - your core abstractions)
1. `Polygon` - 4 edges
2. `Maths Quiz Documentation` - 3 edges
3. `calc_polygon_details()` - 2 edges
4. `Broken Python Project` - 2 edges
5. `# TODO: find a better way to work this stuff out` - 1 edges
6. `# TODO: perhaps I should use the class Polygon instead!` - 1 edges
7. `# TODO: make this work for any type of polygon` - 1 edges
8. `MIT License` - 1 edges

## Surprising Connections (you probably didn't know these)
- `Maths Quiz Documentation` --conceptually_related_to--> `Broken Python Project`  [INFERRED]
  mathsquiz/README.md → README.md
- `Broken Python Project` --references--> `MIT License`  [EXTRACTED]
  README.md → LICENSE.txt

## Import Cycles
- None detected.

## Communities (6 total, 0 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.50
Nodes (3): MIT License, Maths Quiz Documentation, Broken Python Project

### Community 1 - "Community 1"
Cohesion: 0.40
Nodes (3): # TODO: find a better way to work this stuff out, # TODO: perhaps I should use the class Polygon instead!, # TODO: make this work for any type of polygon

### Community 4 - "Community 4"
Cohesion: 0.50
Nodes (3): Object, calc_polygon_details(), Polygon

## Knowledge Gaps
- **1 isolated node(s):** `MIT License`
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Polygon` connect `Community 4` to `Community 1`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **What connects `# TODO: find a better way to work this stuff out`, `# TODO: perhaps I should use the class Polygon instead!`, `# TODO: make this work for any type of polygon` to the rest of the system?**
  _4 weakly-connected nodes found - possible documentation gaps or missing edges._