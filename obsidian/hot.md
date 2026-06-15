# Hot — Where to look first

Ranked by centrality * proximity to the bug node `polygons_polygons_polygon` (R5.6.1, PLAN §5): centrality = 0.6·degree + 0.4·betweenness (max-normalized); proximity = 1 / (1 + shortest-path distance to the bug node). File-container roots are excluded.

1. [[polygons_polygons_polygon|Polygon]] — degree=4 · bw=0.0563 · community=4 · polygons/polygons.py:L3
2. [[polygons_polygons_calc_polygon_details|calc_polygon_details()]] — degree=2 · bw=0.0000 · community=4 · polygons/polygons.py:L13
3. [[object|Object]] — degree=1 · bw=0.0000 · community=4 · 
4. [[polygons_polygons_polygon_init|.__init__()]] — degree=1 · bw=0.0000 · community=4 · polygons/polygons.py:L5
5. [[polygons_polygons_draw_polygon|draw_polygon()]] — degree=1 · bw=0.0000 · community=1 · polygons/polygons.py:L41
6. [[polygons_polygons_rationale_18|# TODO: find a better way to work this stuff out]] — degree=1 · bw=0.0000 · community=1 · polygons/polygons.py:L18
7. [[polygons_polygons_rationale_33|# TODO: perhaps I should use the class Polygon instead!]] — degree=1 · bw=0.0000 · community=1 · polygons/polygons.py:L33
8. [[polygons_polygons_rationale_50|# TODO: make this work for any type of polygon]] — degree=1 · bw=0.0000 · community=1 · polygons/polygons.py:L50
