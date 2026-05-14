# Segment Tree

## Overview

A **Segment Tree** is a binary tree where each node stores information about a contiguous range (segment) of an array. It allows both range queries (sum, min, max, GCD, etc.) and point/range updates in O(log n) time. The tree is built over an array and uses 4n space.

**When to use:**
- Range sum / min / max queries with updates
- Range updates (lazy propagation)
- Count inversions, range GCD/LCM
- Interval stabbing queries
- When Fenwick Tree is insufficient (range updates + range queries simultaneously)

---

## Visualization

### Array to Segment Tree (Range Sum)

```
Array:  [2, 1, 5, 3, 4]
Index:   0  1  2  3  4

Segment Tree (node = sum of range):

                     [0,4] = 15
                    /            \
          [0,2] = 8              [3,4] = 7
          /       \              /       \
      [0,1]=3   [2,2]=5     [3,3]=3   [4,4]=4
      /    \
  [0,0]=2  [1,1]=1

Node indices (1-indexed array implementation):
        1 (root = entire array)
       / \
      2   3
     / \ / \
    4  5 6  7

tree[1] = 15 (sum of [0..4])
tree[2] = 8  (sum of [0..2])
tree[3] = 7  (sum of [3..4])
tree[4] = 3  (sum of [0..1])
tree[5] = 5  (sum of [2..2])
tree[6] = 3  (sum of [3..3])
tree[7] = 4  (sum of [4..4])

For node at index i:
  Left child  = 2*i
  Right child = 2*i + 1
  Parent      = i // 2
```

### Build Process

```
Build segment tree for [2, 1, 5, 3, 4]:

build(node=1, start=0, end=4):
  mid = 2
  build(2, 0, 2)  → builds left half
  build(3, 3, 4)  → builds right half
  tree[1] = tree[2] + tree[3]

build(node=2, start=0, end=2):
  mid = 1
  build(4, 0, 1)
  build(5, 2, 2) → leaf: tree[5] = arr[2] = 5
  tree[2] = tree[4] + tree[5]

build(node=4, start=0, end=1):
  mid = 0
  build(8, 0, 0) → leaf: tree[8] = arr[0] = 2
  build(9, 1, 1) → leaf: tree[9] = arr[1] = 1
  tree[4] = 3

Final tree array:
  [_, 15, 8, 7, 3, 5, 3, 4, 2, 1]
   ^   ^  ^  ^  ^  ^  ^  ^  ^  ^
   0   1  2  3  4  5  6  7  8  9
  (idx 0 unused for 1-indexed)
```

### Range Query: sum(1, 3) = arr[1]+arr[2]+arr[3] = 1+5+3 = 9

```
query(node=1, start=0, end=4, l=1, r=3):
  Node [0..4] partially overlaps [1..3] → recurse both children

  query(node=2, start=0, end=2, l=1, r=3):
    Node [0..2] partially overlaps [1..3] → recurse

    query(node=4, start=0, end=1, l=1, r=3):
      Node [0..1] partially overlaps [1..3] → recurse

      query(node=8, start=0, end=0, l=1, r=3):
        [0..0] outside [1..3] → return 0

      query(node=9, start=1, end=1, l=1, r=3):
        [1..1] fully inside [1..3] → return tree[9] = 1

      return 0 + 1 = 1

    query(node=5, start=2, end=2, l=1, r=3):
      [2..2] fully inside [1..3] → return tree[5] = 5

    return 1 + 5 = 6

  query(node=3, start=3, end=4, l=1, r=3):
    [3..4] partially overlaps [1..3] → recurse

    query(node=6, start=3, end=3, l=1, r=3):
      [3..3] fully inside [1..3] → return tree[6] = 3

    query(node=7, start=4, end=4, l=1, r=3):
      [4..4] outside [1..3] → return 0

    return 3 + 0 = 3

Total: 6 + 3 = 9  ✓
```

### Point Update: update(2, 10) — set arr[2] = 10

```
update(node=1, start=0, end=4, idx=2, val=10):
  mid = 2
  idx <= mid → go left: update(2, 0, 2, 2, 10)

    update(node=2, start=0, end=2, idx=2, val=10):
      mid = 1
      idx > mid → go right: update(5, 2, 2, 2, 10)

        update(node=5, start=2, end=2, idx=2, val=10):
          Leaf! tree[5] = 10

      tree[2] = tree[4] + tree[5] = 3 + 10 = 13

  tree[1] = tree[2] + tree[3] = 13 + 7 = 20

Updated tree:
        20 (was 15)
       /    \
     13       7
    /   \    / \
   3    10  3   4
  / \
 2   1
```

### Lazy Propagation (Range Update + Range Query)

```
Array: [1, 2, 3, 4, 5]   → add 3 to range [1..3]

Without lazy: update all leaves in range → O(n) per range update
With lazy:    mark the covering node, propagate only when needed

Lazy tree concept:
  lazy[node] = pending update not yet pushed to children

  range_update(node, start, end, l, r, val):
    if no overlap: return
    if full overlap:
      tree[node] += val * (end - start + 1)   # update node sum
      lazy[node] += val                         # mark pending
      return
    push_down(node)   # propagate lazy to children first
    recurse on children
    tree[node] = tree[2*node] + tree[2*node+1]

  push_down(node):
    if lazy[node] != 0:
      for child in [2*node, 2*node+1]:
        tree[child] += lazy[node] * child_range_size
        lazy[child] += lazy[node]
      lazy[node] = 0
```

---

## Operations & Complexity

| Operation               | Time       | Space  | Notes                           |
|-------------------------|:----------:|:------:|----------------------------------|
| Build                   | O(n)       | O(n)   | 4n array space                   |
| Point Query             | O(log n)   | O(log n) | Same as point update path       |
| Range Query             | O(log n)   | O(log n) | At most 4 nodes per level       |
| Point Update            | O(log n)   | O(log n) |                                 |
| Range Update (lazy)     | O(log n)   | O(log n) | Needs lazy propagation           |
| Space                   | —          | O(n)   | Use 4*n sized array              |

---

## Key Properties / Invariants

1. **Each node covers a contiguous range**: node at position i covers [start_i, end_i].
2. **Root covers the entire array**: tree[1] represents [0, n-1].
3. **Leaves correspond to individual elements**: tree[leaf] = arr[element_index].
4. **Internal nodes derived from children**: e.g., tree[i] = tree[2i] + tree[2i+1] for sum.
5. **Height = O(log n)**: A segment tree over n elements has height ⌈log₂ n⌉.
6. **Lazy invariant**: Before accessing children, always push pending lazy updates down.

---

## Common Interview Patterns

### Pattern 1: Range Sum with Point Updates
The classic application — build, query, update.

### Pattern 2: Range Min/Max Query
Change the merge function from `+` to `min()` or `max()`. No other changes needed.

### Pattern 3: Range Update + Range Query (Lazy Propagation)
Add a lazy array. Push lazy down before recursing into children.

### Pattern 4: Count of Elements in Range / Frequency Queries
Build a segment tree over value space [0, MAX_VAL]. Insert elements by updating index = value.

### Pattern 5: Persistent Segment Tree
Create a new version of the tree for each update, sharing unchanged subtrees. Enables time-travel queries.

---

## Interview Tips

- **4*n space**: Always allocate `tree = [0] * 4 * n` to be safe.
- **1-indexed**: Most implementations use 1-indexed trees (root at index 1) — left child is 2*i, right is 2*i+1.
- **Three cases in query**: completely outside, completely inside, partially overlapping.
- **Lazy vs no lazy**: Point updates don't need lazy. Range updates do. Mixing them wrongly is a common bug.
- **Offline vs online**: Segment trees are online (handle queries one at a time). For offline, consider merge sort tree or persistent ST.
- **BIT (Fenwick) vs Segment Tree**: BIT is simpler for prefix sum queries with point updates; use segment tree when you need range updates or non-summable operations (min/max).

---

## Example Problems

| Problem                                               | Pattern                        |
|-------------------------------------------------------|--------------------------------|
| Range Sum Query - Mutable (LC 307)                    | Classic segment tree           |
| Count of Smaller Numbers After Self (LC 315)          | Coordinate-compressed seg tree |
| Range Min Query (classic)                             | Min segment tree               |
| My Calendar I / II (LC 729, 731)                      | Interval insertion + query     |
| Falling Squares (LC 699)                              | Range max with lazy            |

---

## Python Quick Reference

```python
# ── Segment Tree: Range Sum + Point Update ────────────────────────────────────
class SegmentTree:
    def __init__(self, arr):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        if arr:
            self._build(arr, 1, 0, self.n - 1)

    def _build(self, arr, node, start, end):
        if start == end:
            self.tree[node] = arr[start]
        else:
            mid = (start + end) // 2
            self._build(arr, 2 * node,     start, mid)
            self._build(arr, 2 * node + 1, mid + 1, end)
            self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def update(self, idx, val, node=1, start=0, end=None):
        if end is None: end = self.n - 1
        if start == end:
            self.tree[node] = val
        else:
            mid = (start + end) // 2
            if idx <= mid:
                self.update(idx, val, 2 * node,     start, mid)
            else:
                self.update(idx, val, 2 * node + 1, mid + 1, end)
            self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def query(self, l, r, node=1, start=0, end=None):
        if end is None: end = self.n - 1
        if r < start or end < l:      # no overlap
            return 0
        if l <= start and end <= r:   # full overlap
            return self.tree[node]
        mid = (start + end) // 2      # partial overlap
        left  = self.query(l, r, 2 * node,     start, mid)
        right = self.query(l, r, 2 * node + 1, mid + 1, end)
        return left + right

# Usage:
arr = [2, 1, 5, 3, 4]
st = SegmentTree(arr)
print(st.query(1, 3))       # → 9  (sum of indices 1..3)
st.update(2, 10)            # set arr[2] = 10
print(st.query(1, 3))       # → 14

# ── Segment Tree with Lazy Propagation (Range Update + Range Query) ────────────
class LazySegTree:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (4 * n)
        self.lazy = [0] * (4 * n)

    def _push_down(self, node, start, end):
        if self.lazy[node]:
            mid = (start + end) // 2
            # Update left child
            self.tree[2*node]   += self.lazy[node] * (mid - start + 1)
            self.lazy[2*node]   += self.lazy[node]
            # Update right child
            self.tree[2*node+1] += self.lazy[node] * (end - mid)
            self.lazy[2*node+1] += self.lazy[node]
            self.lazy[node] = 0

    def range_update(self, l, r, val, node=1, start=0, end=None):
        if end is None: end = self.n - 1
        if r < start or end < l:
            return
        if l <= start and end <= r:
            self.tree[node] += val * (end - start + 1)
            self.lazy[node] += val
            return
        self._push_down(node, start, end)
        mid = (start + end) // 2
        self.range_update(l, r, val, 2*node,   start, mid)
        self.range_update(l, r, val, 2*node+1, mid+1, end)
        self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

    def range_query(self, l, r, node=1, start=0, end=None):
        if end is None: end = self.n - 1
        if r < start or end < l: return 0
        if l <= start and end <= r: return self.tree[node]
        self._push_down(node, start, end)
        mid = (start + end) // 2
        return (self.range_query(l, r, 2*node,   start, mid) +
                self.range_query(l, r, 2*node+1, mid+1, end))
```

---

## Java Quick Reference

```java
class SegmentTree {
    private int[] tree;
    private int n;

    SegmentTree(int[] arr) {
        n = arr.length;
        tree = new int[4 * n];
        build(arr, 1, 0, n - 1);
    }

    private void build(int[] arr, int node, int start, int end) {
        if (start == end) {
            tree[node] = arr[start];
        } else {
            int mid = (start + end) / 2;
            build(arr, 2 * node,     start, mid);
            build(arr, 2 * node + 1, mid + 1, end);
            tree[node] = tree[2 * node] + tree[2 * node + 1];
        }
    }

    public void update(int idx, int val) {
        update(1, 0, n - 1, idx, val);
    }

    private void update(int node, int start, int end, int idx, int val) {
        if (start == end) {
            tree[node] = val;
        } else {
            int mid = (start + end) / 2;
            if (idx <= mid) update(2 * node,     start, mid,     idx, val);
            else            update(2 * node + 1, mid + 1, end,   idx, val);
            tree[node] = tree[2 * node] + tree[2 * node + 1];
        }
    }

    public int query(int l, int r) {
        return query(1, 0, n - 1, l, r);
    }

    private int query(int node, int start, int end, int l, int r) {
        if (r < start || end < l) return 0;
        if (l <= start && end <= r) return tree[node];
        int mid = (start + end) / 2;
        return query(2 * node,     start, mid,     l, r)
             + query(2 * node + 1, mid + 1, end,   l, r);
    }
}
```
