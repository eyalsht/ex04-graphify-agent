# Before/After Diff — `polygons/polygons.py` (R5.2.4 / R7.6)

> The unified diff below is the **literal** `git diff` of the fix applied to
> [`data/broken-python/polygons/polygons.py`](../data/broken-python/polygons/polygons.py).
> The pristine PRE-FIX original is preserved in git history and in the sibling
> `broken-python/` clone. The POST-FIX source passes the automated 3-part correctness gate
> (`token_comparison.correctness.check_correctness` → `True`; see
> [`root_cause.md`](root_cause.md)).
>
> Reproduce: `git diff <pre-fix-commit> -- data/broken-python/polygons/polygons.py`.

## Unified diff

```diff
--- a/data/broken-python/polygons/polygons.py
+++ b/data/broken-python/polygons/polygons.py
@@ -1,44 +1,31 @@
 import turtle
 
-class Polygon(Object):
+
+class Polygon(object):
 
     def __init__(self, sides, internal_angles_sum, internal_angle):
         self.sides = sides
         self.internal_angles_sum = internal_angles_sum
         self.internal_angle = internal_angle
-        
+
 
 # calculate the total internal angles, and the angles within
 # a regular version of the polygon
 def calc_polygon_details(sides):
 
-    internal_angles_sum = 0
-    internal_angles = 0
-
-    # TODO: find a better way to work this stuff out
-    if sides == 3:
-        internal_angles_sum = 180
-        internal_angles = 60
-    elif sides == 4:
-        internal_angles_sum = 360
-        internal_angles = 90
-    else:
-        internal_angles_sum = 1000
-        internal_angles = 200
+    if sides < 3:
+        raise ValueError(f"a polygon needs at least 3 sides, got {sides}")
 
-    poly = new Polygon(sides, internal_angles_sum, internal_angles)
-    print(poly)
+    internal_angles_sum = (sides - 2) * 180
+    internal_angle = internal_angles_sum / sides
 
-    # return a dictionary containing info about the polygon
-    # TODO: perhaps I should use the class Polygon instead!
-    return {"sides": sides,
-            "internal_angles_sum": internal_angles_sum,
-            "internal_angles": internal_angles}
+    poly = Polygon(sides, internal_angles_sum, internal_angle)
 
+    return poly
 
 
 # draws a polygon using the turtle
-def draw_polygon(polygon_details):
+def draw_polygon(polygon):
 
     # set up the screen and turtle
     scr = turtle.Screen()
@@ -46,30 +33,21 @@ def draw_polygon(polygon_details):
     t.pen(pencolor="red", pensize=2, fillcolor="green")
 
     length_of_edge = 50
-    
-    # TODO: make this work for any type of polygon
-    for i in range(0, 6):
-        t.forward(length_of_edge)
-        t.right(60)
-
 
+    for i in range(0, polygon.sides):
+        t.forward(length_of_edge)
+        t.right(360 / polygon.sides)
 
 
 sides = int(input("How many sides does your polygon have?: "))
 
-polygon_details = calc_polygon_details(sides)
+polygon = calc_polygon_details(sides)
 
-print("    Sides:", polygon_details["sides"])
-print("    Internal angles sum:", polygon_details["internal_angles_sum"])
-print("    Internal angles:", polygon_details["internal_angles"])
+print("    Sides:", polygon.sides)
+print("    Internal angles sum:", polygon.internal_angles_sum)
+print("    Internal angle:", polygon.internal_angle)
 
 draw = input("Would you like me to draw it? (Y/n): ")
 
 if draw == "" or draw.lower() == "y":
-    draw_polygon(polygon_details)
-        
-
-
-
-
-    
+    draw_polygon(polygon)
```

## Change-by-change (each tied to a documented weakness)

| # | Change | PRE-FIX line(s) | Bug class | Signal that flagged it |
|---|---|---|---|---|
| 1 | `Object` → `object` | L3 | `NameError` — undefined base class | Signal 1 (god node `Polygon` is the core abstraction, so its definition matters most) |
| 2 | `new Polygon(...)` → `Polygon(...)`; dropped `print(poly)` | L29–30 | `SyntaxError` — Java/JS `new` keyword in Python | — (blocking syntax; surfaced once the god node is opened) |
| 3 | Hardcoded `if/elif/else` (3→180/60, 4→360/90, else→**1000/200**) → `(sides-2)*180`, `sum/sides` | L15–27 | Wrong-answer logic — the `else` branch returns nonsense for any polygon with ≥5 sides | Signal 5 (`TODO@L18` "find a better way" → `rationale_18` node) |
| 4 | Returns a `dict` → returns a `Polygon` instance | L34–36 | Duplicated state — the `dict` shadows the class, so `Polygon` is **dead code** | Signal 6 (semantic duplication) + `TODO@L33` "perhaps I should use the class Polygon instead!" → `rationale_33` node |
| 5 | `range(0, 6)` / `right(60)` → `range(0, polygon.sides)` / `right(360 / polygon.sides)` | L51–53 | Hardcoded hexagon — `draw_polygon` ignores `sides` | Signal 5 (`TODO@L50` "make this work for any type of polygon" → `rationale_50` node) |
| 6 | `draw_polygon(polygon_details)` dict arg → `draw_polygon(polygon)` object arg | L41, L69 | API mismatch — consumes the now-unified `Polygon` object | Follows from #4 |
| 7 | **Added `if sides < 3: raise ValueError(...)`** | (new) | Critical-path crash — `sides=0` → `ZeroDivisionError` on `360 / sides`; `sides=1/2` → invalid geometry | **Signal 4 (critical-path break)** — the missing geometric guard on the live `input()` path |

### TODO comments removed (R7.43)

All three `TODO:` comments are deleted by the fix because each is **resolved**, not
suppressed:

- `# TODO: find a better way to work this stuff out` (L18) → general formula (#3)
- `# TODO: perhaps I should use the class Polygon instead!` (L33) → returns a `Polygon` (#4)
- `# TODO: make this work for any type of polygon` (L50) → loop honors `polygon.sides` (#5)

Their disappearance is independently visible in the graph: the three
`polygons_polygons_rationale_{18,33,50}` nodes are **removed** in the POST-FIX graph (see
[`graph_diff.md`](graph_diff.md)).

## Scope discipline (ADR-0003)

The diff stays inside the single half-finished `Polygon` abstraction — `calc_polygon_details`
/ `Polygon` / `draw_polygon`. No changes to `mathsquiz/` (out of scope, ADR-0003), no
speculative refactors. This is one root cause with several symptoms plus the Signal-4 guard
that closes the only crashing input path (R5.2.2 / R7.44). See
[`root_cause.md`](root_cause.md) for the narrative and [`oop_improvement.md`](oop_improvement.md)
for the OOP rationale.
