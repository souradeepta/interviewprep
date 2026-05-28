---
Level: L5+
Time: ~20 min
---

# Geometry Algorithms

## Quick Summary

Geometry questions are rare in SDE interviews but appear at FAANG/quant levels. The key principles: prefer integer arithmetic over floating point, use cross products for orientation, and compare squared distances to avoid `sqrt`. Know convex hull (Graham scan) and the shoelace formula.

---

## Core Concepts Quick Reference

| Concept | Formula | Notes |
|---------|---------|-------|
| Euclidean distance | `sqrt((x2-x1)^2 + (y2-y1)^2)` | Avoid sqrt — compare squared dist when possible |
| Manhattan distance | `abs(x2-x1) + abs(y2-y1)` | Used in grid problems, no sqrt needed |
| Cross product (2D) | `(b-a) × (c-a) = (bx-ax)(cy-ay) - (by-ay)(cx-ax)` | > 0: left turn; < 0: right turn; = 0: collinear |
| Dot product | `a·b = ax*bx + ay*by` | Positive: acute angle; negative: obtuse |
| Area of triangle | `0.5 * abs(cross product)` | Uses the cross product formula above |
| Area of polygon | Shoelace formula | Sum of signed trapezoid areas |
| Slope | `dy/dx = (y2-y1)/(x2-x1)` | Use fractions (GCD) to avoid float precision |
| Point in polygon | Ray casting | Count crossings of horizontal ray |
| Convex hull | Graham scan O(n log n) | Sort by polar angle, maintain left-turn stack |

---

## Algorithms

### 1. Cross Product and Orientation

**The cross product of vectors `AB` and `AC`** determines the turn direction at `B` when going from `A` to `C`.

```python
def cross_product(o: tuple, a: tuple, b: tuple) -> int:
    """
    Returns cross product of vectors OA and OB.
    > 0: counter-clockwise (left turn)
    < 0: clockwise (right turn)
    = 0: collinear
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def orientation(p: tuple, q: tuple, r: tuple) -> int:
    """
    Returns:
      1 if p->q->r is counter-clockwise
     -1 if p->q->r is clockwise
      0 if collinear
    """
    val = cross_product(p, q, r)
    if val > 0: return 1
    if val < 0: return -1
    return 0
```

---

### 2. Convex Hull — Graham Scan

**Approach:**
1. Find the lowest (then leftmost) point as anchor.
2. Sort remaining points by polar angle relative to anchor.
3. Process points: maintain a stack where each turn is counter-clockwise. Pop when a right turn is detected.

**Time:** O(n log n) | **Space:** O(n)

```python
def convex_hull(points: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Returns points on the convex hull in counter-clockwise order."""
    points = sorted(set(points))   # remove duplicates, sort lexicographically
    n = len(points)
    if n <= 1:
        return points

    # Build lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross_product(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross_product(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Combine (remove duplicate endpoints)
    return lower[:-1] + upper[:-1]


# Example
points = [(0,0), (1,1), (2,2), (0,2), (2,0), (1,0), (0,1)]
hull = convex_hull(points)
print(hull)  # [(0,0), (2,0), (2,2), (0,2)]
```

Note: `cross_product <= 0` excludes collinear points from the hull. Use `< 0` to include collinear boundary points.

---

### 3. Shoelace Formula (Area of Polygon)

**Formula:** For polygon with vertices `(x0,y0), (x1,y1), ..., (xn-1,yn-1)`:
```
Area = 0.5 * |Σ (xi * y(i+1) - x(i+1) * yi)|
```
Indices are modulo n (wrap around).

```python
def polygon_area(vertices: list[tuple[int, int]]) -> float:
    """Returns area of polygon given its vertices in order."""
    n = len(vertices)
    area = 0
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2


# Example
# Rectangle with vertices (0,0),(4,0),(4,3),(0,3) → area = 12
print(polygon_area([(0,0), (4,0), (4,3), (0,3)]))  # 12.0

# Triangle (0,0),(4,0),(2,3) → area = 6
print(polygon_area([(0,0), (4,0), (2,3)]))  # 6.0
```

---

### 4. Exact Slope Comparison Using GCD

To avoid floating point errors when comparing slopes, represent slope as a reduced fraction `(dy/gcd, dx/gcd)` with a canonical sign convention.

```python
from math import gcd

def normalize_slope(dy: int, dx: int) -> tuple[int, int]:
    """
    Returns slope as reduced fraction (dy, dx) with canonical sign.
    Vertical line → (1, 0). Horizontal line → (0, 1).
    """
    if dx == 0:
        return (1, 0)        # vertical
    if dy == 0:
        return (0, 1)        # horizontal
    g = gcd(abs(dy), abs(dx))
    dy //= g
    dx //= g
    if dx < 0:               # make dx always positive
        dy, dx = -dy, -dx
    return (dy, dx)


# Example
print(normalize_slope(4, 6))    # (2, 3)
print(normalize_slope(-4, -6))  # (2, 3) — same slope
print(normalize_slope(-4, 6))   # (-2, 3)
```

---

## Worked Problems

### Problem 1: Max Points on a Line — LC #149

**Section 1 — Understand the problem.**
Given `n` points on a 2D plane, return the maximum number of points that lie on the same straight line.

**Section 2 — Examples.**
```
[[1,1],[2,2],[3,3]]      → 3
[[1,1],[3,2],[5,3],[4,1],[2,3],[1,4]] → 4
```

**Section 3 — Constraints & edge cases.**
- 1 ≤ n ≤ 300
- n = 1 → 1 (single point)
- Duplicate points: two identical points define infinitely many lines — count them as collinear with everything
- Vertical lines: infinite slope — handle separately

**Section 4 — Approach.**
For each anchor point, use a hash map from normalized slope to count. The max count + duplicates + 1 (the anchor itself) gives the line size through the anchor.

**Section 5 — Code.**
```python
from collections import defaultdict
from math import gcd

def maxPoints(points: list[list[int]]) -> int:
    n = len(points)
    if n <= 2:
        return n

    ans = 2
    for i in range(n):
        slope_count = defaultdict(int)
        duplicates = 0
        local_max = 0

        for j in range(i + 1, n):
            dx = points[j][0] - points[i][0]
            dy = points[j][1] - points[i][1]

            if dx == 0 and dy == 0:
                duplicates += 1
                continue

            g = gcd(abs(dx), abs(dy))
            dx //= g
            dy //= g
            if dx < 0:        # canonical sign: dx always non-negative
                dx, dy = -dx, -dy
            elif dx == 0:
                dy = abs(dy)  # vertical line: dy positive

            slope_count[(dx, dy)] += 1
            local_max = max(local_max, slope_count[(dx, dy)])

        ans = max(ans, local_max + duplicates + 1)

    return ans
```

**Section 6 — Complexity.**
Time O(n^2), Space O(n) for slope map. With n ≤ 300, this is fine (90,000 operations).

---

### Problem 2: K Closest Points to Origin — LC #973

**Section 1 — Understand the problem.**
Given an array of points, return the `k` closest to the origin `(0, 0)`. Distance is Euclidean. Answer can be in any order.

**Section 2 — Examples.**
```
points = [[1,3],[-2,2]], k=1  → [[-2,2]]   (dist^2: 10 vs 8)
points = [[3,3],[5,-1],[-2,4]], k=2  → [[3,3],[-2,4]]
```

**Section 3 — Constraints & edge cases.**
- 1 ≤ k ≤ len(points) ≤ 10^4
- No need for sqrt — compare squared distances
- Guaranteed k ≤ n and answer is unique (distances all distinct in test cases)

**Section 4 — Approach.**
Option A: Sort by `x^2 + y^2`, return first k. O(n log n).
Option B: Max-heap of size k. O(n log k) — better when k << n.
Option C: Quickselect. O(n) average — best for large inputs.

For interviews, sort is cleanest; heap is better if asked about large n/small k.

**Section 5 — Code.**
```python
import heapq

def kClosest_sort(points: list[list[int]], k: int) -> list[list[int]]:
    return sorted(points, key=lambda p: p[0]**2 + p[1]**2)[:k]


def kClosest_heap(points: list[list[int]], k: int) -> list[list[int]]:
    # Max-heap of size k: negate distance to simulate max-heap with Python's min-heap
    heap = []
    for x, y in points:
        dist_sq = -(x*x + y*y)     # negate for max-heap
        heapq.heappush(heap, (dist_sq, x, y))
        if len(heap) > k:
            heapq.heappop(heap)    # remove farthest
    return [[x, y] for _, x, y in heap]
```

**Section 6 — Complexity.**
Sort: O(n log n) time, O(k) space for output.
Heap: O(n log k) time, O(k) space.

---

### Problem 3: Minimum Area Rectangle — LC #939

**Section 1 — Understand the problem.**
Given a set of points in the XY plane (axis-aligned only), return the minimum area of a rectangle formed by any 4 points. Return 0 if no rectangle exists.

**Section 2 — Examples.**
```
[[1,1],[1,3],[3,1],[3,3],[2,2]] → 4
[[1,1],[1,3],[3,1],[3,3],[4,1],[4,3]] → 2
```

**Section 3 — Constraints & edge cases.**
- 1 ≤ n ≤ 500
- All points unique, integer coordinates
- No axis-aligned rectangle possible → 0

**Section 4 — Approach.**
Store all points in a set. For each pair of points `(x1,y1)` and `(x2,y2)` that form a diagonal, check if `(x1,y2)` and `(x2,y1)` exist. Track minimum area.

**Section 5 — Code.**
```python
def minAreaRect(points: list[list[int]]) -> int:
    point_set = {(x, y) for x, y in points}
    min_area = float('inf')

    for i in range(len(points)):
        x1, y1 = points[i]
        for j in range(i + 1, len(points)):
            x2, y2 = points[j]
            # Only consider pairs that could be diagonals (different x and y)
            if x1 != x2 and y1 != y2:
                if (x1, y2) in point_set and (x2, y1) in point_set:
                    area = abs(x2 - x1) * abs(y2 - y1)
                    min_area = min(min_area, area)

    return 0 if min_area == float('inf') else min_area
```

**Section 6 — Complexity.**
Time O(n^2) for pair iteration + O(1) hash lookups. Space O(n) for the set.

---

## Common Mistakes

1. **Floating point precision:** `0.1 + 0.2 != 0.3` in IEEE 754. For slope comparison, never use `float` division — use integer fractions `(dy, dx)` reduced by GCD. For distance comparison, compare `dx^2 + dy^2` (squared distance) instead of `sqrt(dx^2 + dy^2)`.

2. **Assuming sqrt is needed:** For "closest point", "within distance r", or "farthest point" queries, you almost never need `sqrt`. Compare squared distances. Only compute `sqrt` when the actual distance value must be returned.

3. **Collinear points in convex hull:** The cross product test `<= 0` vs `< 0` determines whether collinear points are included on hull edges. Off-by-one here changes the hull point count — clarify with interviewer if needed.

4. **Slope of vertical lines:** `dx = 0` causes division by zero. Handle vertical lines as a special case (e.g., represent as `(1, 0)` or count separately).

5. **Sign normalization for slopes:** `(2, 3)` and `(-2, -3)` represent the same slope but hash differently. Always normalize: make `dx > 0`, or if `dx = 0`, make `dy > 0`.

6. **Forgetting duplicate points:** In Max Points on a Line, two identical points have `dx = dy = 0` and are collinear with every line. Track duplicates separately and add them to every line count through that anchor.

---

## Interview Q&A

**Q1: What is the cross product and how is it used in geometry problems?**
The 2D cross product of vectors `AB` and `AC` is `(B-A) × (C-A) = (Bx-Ax)(Cy-Ay) - (By-Ay)(Cx-Ax)`. Its sign determines orientation: positive → counter-clockwise turn, negative → clockwise, zero → collinear. Used in convex hull, line intersection, polygon area, and point-in-polygon tests.

**Q2: How does Graham scan build the convex hull?**
Sort points lexicographically (or by polar angle from the lowest point). Build a lower hull left-to-right: for each new point, pop the stack while the last three points make a clockwise turn (cross product ≤ 0). Then build upper hull right-to-left the same way. The result is the convex hull in O(n log n) time.

**Q3: What is the shoelace formula and why does it work?**
The shoelace formula computes `0.5 * |Σ(xi * y(i+1) - x(i+1) * yi)|`. It works by summing signed trapezoid areas between each edge and the x-axis. Positive terms add area, negative terms subtract it. The absolute value gives the total polygon area regardless of vertex order (CW or CCW).

**Q4: When would you use Manhattan distance instead of Euclidean?**
Manhattan distance (`|dx| + |dy|`) is used when movement is restricted to a grid (e.g., city blocks, robot navigation on a matrix). It's also cheaper to compute (no multiplication) and appears naturally in problems involving axis-aligned movements. Some problems give both and ask you to choose — Manhattan is exact for grid traversal; Euclidean is exact for straight-line distance.

**Q5: How do you handle floating point precision in geometry?**
Three strategies: (1) Use integer arithmetic throughout — represent slopes as reduced fractions, compare squared distances. (2) Use an epsilon for comparisons: `abs(a - b) < 1e-9`. (3) Use Python's `fractions.Fraction` for exact rational arithmetic when needed. In interviews, always ask "can coordinates be floating point?" — if they're integers, integer arithmetic is always preferable.

**Q6: What is the time complexity of the closest pair of points problem?**
O(n log n) using divide-and-conquer (Shamos-Hoey algorithm). The naive approach is O(n^2). The divide-and-conquer splits the point set, finds the closest pair in each half, and then checks the "strip" around the median — which is O(n log n) with careful analysis. This is a classic algorithm but rarely asked in coding interviews (more common in algorithm theory courses).
