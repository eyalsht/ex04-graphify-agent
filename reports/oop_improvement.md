# OOP-Improvement Summary (R3.4 / R5.2.3 / R7.7)

> Why the fix is an *object-oriented* improvement, not just a bug patch — and how each
> improvement traces back to a graph signal (R4.4 / R7.17). Code samples are excerpted from
> the POST-FIX [`polygons.py`](../data/broken-python/polygons/polygons.py) and compile/run
> under the correctness gate.

## The core move: `Polygon` becomes the single source of truth

PRE-FIX, the program had **two** representations of a polygon living side by side:

- a `Polygon` class (defined, never used — *dead*), and
- a `dict` `{"sides", "internal_angles_sum", "internal_angles"}` built by hand and threaded
  through every caller.

That duplication is the OOP smell. The fix collapses the two into one — the class — and
deletes the dict. Everything else follows.

| OOP improvement | PRE-FIX | POST-FIX | Graph signal that motivated it |
|---|---|---|---|
| **Single source of truth** | class + parallel dict | `Polygon` only | Signal 6 (semantic duplication: dict keys ≡ constructor params) |
| **Encapsulated construction** | `calc_polygon_details` returns a dict | returns a `Polygon` instance | Signal 1 (god node should *be* the abstraction) + `TODO@L33` (signal 5) |
| **Behavior near data** | hardcoded angle table; `draw` ignores `sides` | formula computes state; `draw` reads `polygon.sides` | Signal 5 (`rationale_18`, `rationale_50`) |
| **Valid type hierarchy** | `Polygon(Object)` (`NameError`) | `Polygon(object)` | Signal 1 (the core class must at least be definable) |

### 1. Encapsulated construction (the dict → object refactor)

PRE-FIX, `calc_polygon_details` computed values, built a `Polygon`, **discarded it**, and
returned a dict. POST-FIX it returns the object it built:

```python
def calc_polygon_details(sides):
    internal_angles_sum = (sides - 2) * 180
    internal_angle = internal_angles_sum / sides
    poly = Polygon(sides, internal_angles_sum, internal_angle)
    return poly
```

`calc_polygon_details` now reads as a **factory** for `Polygon`: callers receive a typed
object with named attributes (`polygon.sides`, `polygon.internal_angle`) instead of
stringly-keyed dict lookups (`details["internal_angles"]`). This is the improvement signal 1
predicted — a god node is the core abstraction, so the highest-value change is to make that
abstraction real and central rather than ornamental.

> **Optional next step (documented, not applied — keeps the diff focused, ADR-0003):** the
> formula could move *into* the class as a `@classmethod` constructor, so the math lives with
> the data it describes:
>
> ```python
> class Polygon:
>     @classmethod
>     def regular(cls, sides):
>         angles_sum = (sides - 2) * 180
>         return cls(sides, angles_sum, angles_sum / sides)
> ```
>
> We left `calc_polygon_details` as the factory to keep the before/after diff minimal and
> reviewable. The refactor path is noted for completeness.

### 2. Behavior near data — `draw_polygon` asks the object

PRE-FIX `draw_polygon` hardcoded a hexagon (`range(0, 6)`, `right(60)`). POST-FIX it derives
the geometry from the object it is handed:

```python
def draw_polygon(polygon):
    ...
    for i in range(0, polygon.sides):
        t.forward(length_of_edge)
        t.right(360 / polygon.sides)
```

The turn angle `360 / sides` is the polygon's **exterior** angle — the correct turtle-turn
for a regular polygon — so a pentagon draws five sides, an octagon eight. The function no
longer needs to know anything except "give me a `Polygon`."

### 3. Valid type hierarchy

`class Polygon(object)` makes the class definable in the first place (PRE-FIX `Object` was a
`NameError`). Minor but foundational: signal 1's "core abstraction" cannot be central if it
cannot be instantiated.

## Invariant enforcement — the Signal-4 guard (R7.16)

- **`sides >= 3` validation** (signal 4): a real `Polygon` is only well-defined for ≥3 sides.
  `calc_polygon_details` now raises `ValueError` for `sides < 3` **before** any arithmetic:

  ```python
  def calc_polygon_details(sides):
      if sides < 3:
          raise ValueError(f"a polygon needs at least 3 sides, got {sides}")
      ...
  ```

  This is not cosmetic: the live script feeds `int(input(...))` straight into this function,
  so without the guard `sides = 0` crashes with `ZeroDivisionError` on `360 / sides` (and
  `sides = 1/2` produces invalid geometry). Guarding the constructor's precondition at the
  factory is the OOP-correct place to defend the abstraction's invariant — an object should
  never exist in an impossible state. Covered by
  `test_calc_polygon_details_rejects_fewer_than_three_sides`. *(Originally deferred as
  "minor"; a ruthless review correctly flagged it as a crashing bug on the critical path, so
  it is now fixed rather than documented as an omission.)*

## Why this is the *right* OOP improvement (R10.2)

The graph said "the most connected thing is a class that nothing uses." The OOP-correct
response to "a class that nothing uses, shadowed by a dict that everything uses" is not to
delete the class — it is to **promote the class to the role it was designed for and retire
the duplicate**. That single decision (return `Polygon`, drop the dict) is what turns five
scattered symptoms into one coherent fix, and it is exactly what signals 1 + 6 + the
`rationale` TODO nodes jointly pointed at. The POST-FIX graph confirms it: `Polygon` now has
an inbound `calls` edge ([`graph_diff.md`](graph_diff.md)).
