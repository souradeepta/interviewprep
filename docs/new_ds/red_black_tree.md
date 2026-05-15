# Red-Black Tree

## Overview

A Red-Black Tree (RBT) is a self-balancing BST that uses a one-bit color field (RED/BLACK)
on each node to enforce near-perfect balance. Every path from a node to a NULL leaf passes
through the same number of black nodes — this guarantees O(log n) height, bounding all
operations to O(log n) worst case.

Used in: Linux CFS scheduler (tasks keyed by virtual runtime), Java `TreeMap`/`TreeSet`,
C++ `std::map`/`std::set`, C++ STL associative containers.

---

## Flowcharts

### Problem Recognition: When to Use Red-Black Tree

```mermaid
graph TD
    A["Need ordered map/set<br/>with dynamic ops?"]:::decision -->|No| B["Use other structure"]:::output
    A -->|Yes| C["What's your workload<br/>mix?"]:::decision
    C -->|Read-heavy| D["Use AVL Tree<br/>tighter balance"]:::output
    C -->|Write-heavy| E["Use Red-Black Tree<br/>fewer rotations"]:::output
    C -->|Balanced mix| F["Use Red-Black Tree"]:::output
    F --> G["Do you need concurrent<br/>access?"]:::decision
    G -->|Yes| H["Consider Skip List<br/>easier lock-free"]:::output
    G -->|No| I["✓ Red-Black Tree<br/>is ideal"]:::success
    I --> J["Know insertion will<br/>need fixup logic"]:::note
    J --> K["Be ready for 2-3 cases"]:::note
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef output fill:#50C878,stroke:#333,stroke-width:2px,color:#000
    classDef success fill:#50C878,stroke:#333,stroke-width:2px,color:#000
    classDef note fill:#FFFFFF,stroke:#999,stroke-width:1px,color:#000
```

### RB Tree vs Balanced BST Alternatives

```mermaid
graph TD
    A["Choose balanced BST type"]:::decision
    
    A --> B["Red-Black Tree"]:::alt
    B --> B1["✓ O(log n) operations<br/>≤2 rotations per insert<br/>≤3 rotations per delete<br/>Simpler code<br/>Linux kernel uses this"]:::altDetail
    B2["⚠️ Height up to 2·log(n)"]
    B --> B2
    
    A --> C["AVL Tree"]:::alt
    C --> C1["✓ Faster search<br/>Height ≤ 1.44·log(n)<br/>Good for read-heavy"]:::altDetail
    C2["⚠️ More rotations per update<br/>Complex balancing logic"]
    C --> C2
    
    A --> D["B-Tree"]:::alt
    D --> D1["✓ Cache-friendly<br/>Good for disk I/O<br/>Works as database index"]:::altDetail
    D2["⚠️ More complex<br/>Multiple keys per node"]
    D --> D2
    
    A --> E["Splay Tree"]:::alt
    E --> E1["✓ Good for temporal<br/>locality<br/>Amortized O(log n)"]:::altDetail
    E2["⚠️ Worst case O(n)<br/>No worst-case guarantee"]
    E --> E2
    
    A --> F["Skip List"]:::alt
    F --> F1["✓ Simpler implementation<br/>Better lock-free variants<br/>Redis uses for sorted set"]:::altDetail
    F2["⚠️ Probabilistic O(log n)<br/>Need randomness"]
    F --> F2
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef alt fill:#87CEEB,stroke:#333,stroke-width:2px,color:#000
    classDef altDetail fill:#E0F4FF,stroke:#333,stroke-width:1px,color:#000
```

### Insertion Fixup Case Selection

```mermaid
graph TD
    A["Insert node z<br/>as RED"]:::action
    A --> A1{"z.parent<br/>is RED?"}:::decision
    A1 -->|No| A2["✓ No violation,<br/>done"]:::success
    A1 -->|Yes| A3["Violation detected:<br/>two consecutive REDs"]:::warning
    
    A3 --> B["Get uncle U<br/>= sibling of z.parent"]:::step
    B --> B1{"U is RED?"}:::decision
    
    B1 -->|Yes| C["CASE 1: Recolor"]:::caseBox
    C --> C1["Recolor:<br/>parent(z) ← BLACK<br/>uncle(z) ← BLACK<br/>grandparent(z) ← RED"]:::action
    C1 --> C2["Move z = grandparent<br/>continue fixup upward"]:::action
    C2 --> C3["✓ Redness pushed up"]:::note
    
    B1 -->|No, BLACK| D{"Is z an<br/>inner child?"}:::decision
    
    D -->|Yes| E["CASE 2: Outer rotation<br/>before Case 3"]:::caseBox
    E --> E1["Rotate parent away<br/>to make z outer child"]:::action
    E1 --> E2["Treat new position<br/>as z for Case 3"]:::action
    E2 --> E3["Continue below"]:::note
    
    D -->|No, outer| F["CASE 3: Outer rotation<br/>+ recolor"]:::caseBox
    F --> F1["Rotate grandparent"]:::action
    F1 --> F2["Swap colors:<br/>parent ← BLACK<br/>grandparent ← RED"]:::action
    F2 --> F3["✓ Violation resolved,<br/>done"]:::success
    
    A3 --> A4["Final check"]:::step
    A4 --> A5["Ensure root is BLACK<br/>after all fixups"]:::action
    A5 --> A6["✓ Insert complete"]:::success
    
    classDef action fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef step fill:#B0E0E6,stroke:#333,stroke-width:1px,color:#000
    classDef caseBox fill:#FFE0B2,stroke:#333,stroke-width:2px,color:#000
    classDef warning fill:#FF6B6B,stroke:#333,stroke-width:2px,color:#fff
    classDef note fill:#FFFFFF,stroke:#999,stroke-width:1px,color:#000
    classDef success fill:#50C878,stroke:#333,stroke-width:2px,color:#000
```

### Rotation & Recoloring Decision Tree

```mermaid
graph TD
    A["Detect RB violation<br/>or imbalance"]:::warning
    
    A --> B["Violation type?"]:::decision
    
    B -->|Red-Red edge| C["RBT insertion fixup<br/>see Insertion Case 1-3"]:::action
    
    B -->|After deletion<br/>double-black| D["Deletion fixup<br/>4 cases"]:::action
    D --> D1["Sibling RED?"]:::decision
    D1 -->|Yes| D2["Convert to<br/>BLACK sibling case"]:::action
    D1 -->|No| D3["Sibling BLACK"]:::next
    D3 --> D4{"Sibling's<br/>children colors?"}:::decision
    D4 -->|Both BLACK| D5["Recolor sibling RED<br/>push double-black up"]:::action
    D4 -->|Far child RED| D6["Rotate + recolor<br/>resolve immediately"]:::action
    D4 -->|Near RED,<br/>far BLACK| D7["Rotate sibling<br/>to get far RED"]:::action
    
    E["Rotation types"]:::info
    E --> E1["Left Rotation"]:::rot
    E1 --> E1a["Right child becomes<br/>new root; left subtree<br/>moves right"]:::detail
    E --> E2["Right Rotation"]:::rot
    E2 --> E2a["Left child becomes<br/>new root; right subtree<br/>moves left"]:::detail
    
    classDef warning fill:#FF6B6B,stroke:#333,stroke-width:2px,color:#fff
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef action fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef next fill:#B0E0E6,stroke:#333,stroke-width:1px,color:#000
    classDef info fill:#F0F8FF,stroke:#333,stroke-width:2px,color:#000
    classDef rot fill:#87CEEB,stroke:#333,stroke-width:1px,color:#000
    classDef detail fill:#E0F4FF,stroke:#333,stroke-width:1px,color:#000
```

### Operation Selection & Complexity Guarantees

```mermaid
graph TD
    A["RB Tree operation"]:::decision
    
    A -->|Search| B["Look up key<br/>standard BST traversal"]:::action
    B --> B1["Compare key at node"]:::step
    B1 --> B2{"Equal?"}:::decision
    B2 -->|Yes| B3["✓ Found, O(log n)"]:::success
    B2 -->|No| B3a["Go left or right"]:::step
    B3a --> B2
    
    A -->|Insert| C["Binary search<br/>find insertion point"]:::action
    C --> C1["Insert new RED node"]:::action
    C1 --> C2["Run insertion fixup<br/>up to root"]:::action
    C2 --> C3["At most 2 rotations"]:::note
    C3 --> C4["✓ O(log n) total"]:::success
    
    A -->|Delete| D["Find node to delete"]:::action
    D --> D1{"Node has<br/>children?"}:::decision
    D1 -->|0-1| D2["Direct removal"]:::step
    D1 -->|2| D2a["Replace with successor<br/>or predecessor"]:::step
    D2 --> D3["Run deletion fixup"]:::action
    D2a --> D3
    D3 --> D4["At most 3 rotations"]:::note
    D4 --> D5["✓ O(log n) total"]:::success
    
    E["Height guarantee"]:::prop
    E --> E1["h ≤ 2·log₂(n+1)"]:::formula
    E --> E2["Derived from<br/>black-height property"]:::proof
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef action fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef step fill:#B0E0E6,stroke:#333,stroke-width:1px,color:#000
    classDef note fill:#FFFFFF,stroke:#999,stroke-width:1px,color:#000
    classDef success fill:#50C878,stroke:#333,stroke-width:2px,color:#000
    classDef prop fill:#F0F8FF,stroke:#333,stroke-width:2px,color:#000
    classDef formula fill:#FFFACD,stroke:#999,stroke-width:1px,color:#000
    classDef proof fill:#E0F4FF,stroke:#999,stroke-width:1px,color:#000
```

### Implementation Approach & Edge Cases

```mermaid
graph TD
    A["Build a Red-Black Tree"]:::goal
    
    A --> B["Step 1:<br/>Define Node structure"]:::step
    B --> B1["Fields: key, val,<br/>left, right, parent, color"]:::impl
    B1 --> B2["Use NIL sentinel<br/>for null leaves"]:::best
    B2 --> B3["NIL.color = BLACK<br/>avoid null checks"]:::detail
    
    A --> C["Step 2:<br/>Implement rotations"]:::step
    C --> C1["_rotate_left(node):<br/>right child ← new root"]:::impl
    C1 --> C2["_rotate_right(node):<br/>left child ← new root"]:::impl
    C2 --> C3["Handle parent pointers<br/>carefully"]:::best
    
    A --> D["Step 3:<br/>Implement insert"]:::step
    D --> D1["Standard BST insert"]:::impl
    D1 --> D2["New node ← RED"]:::key
    D2 --> D3["Call _insert_fixup"]:::impl
    D3 --> D4["Loop while parent RED"]:::best
    
    A --> E["Step 4:<br/>Implement delete"]:::step
    E --> E1["Standard BST delete<br/>with successor logic"]:::impl
    E1 --> E2["Harder than insert<br/>introduces double-black"]:::warning
    E2 --> E3["Call _delete_fixup"]:::impl
    
    F["Edge cases<br/>to handle"]:::warning
    F --> F1["❌ Forgetting to<br/>set root.color = BLACK"]:::bug
    F1 --> F1a["✓ Always do after fixup"]:::fix
    F --> F2["❌ NULL checks on NIL"]:::bug
    F2 --> F2a["✓ Use sentinel NIL,<br/>never check is_null"]:::fix
    F --> F3["❌ Rotating root<br/>without updating"]:::bug
    F3 --> F3a["✓ Check parent is None<br/>and update self.root"]:::fix
    
    classDef goal fill:#ffd699,color:#000,stroke:#333,stroke-width:2px,stroke:#333,stroke-width:3px,color:#000
    classDef step fill:#87CEEB,stroke:#333,stroke-width:2px,color:#000
    classDef impl fill:#B0E0E6,stroke:#333,stroke-width:1px,color:#000
    classDef best fill:#90ee90,color:#000,stroke:#333,stroke-width:2px,stroke:#333,stroke-width:1px,color:#000
    classDef detail fill:#E0F4FF,stroke:#333,stroke-width:1px,color:#000
    classDef key fill:#FFE0B2,stroke:#333,stroke-width:1px,color:#000
    classDef warning fill:#FF6B6B,stroke:#333,stroke-width:2px,color:#fff
    classDef bug fill:#FFB6C6,stroke:#333,stroke-width:1px,color:#000
    classDef fix fill:#90ee90,color:#000,stroke:#333,stroke-width:2px,stroke:#333,stroke-width:1px,color:#000
```

### Common Mistakes & Debugging

```mermaid
graph TD
    A["Common RB Tree pitfalls"]:::warning
    
    A --> B["❌ Confusing rotation<br/>direction"]:::mistake
    B --> B1["Impact: tree becomes<br/>unbalanced or unordered"]:::impact
    B1 --> B2["✓ Verify: left-rotate<br/>moves right child up"]:::fix
    
    A --> C["❌ Forgetting to update<br/>parent pointers"]:::mistake
    C --> C1["Impact: tree becomes<br/>disconnected"]:::impact
    C1 --> C2["✓ Always set parent<br/>after rotation"]:::fix
    
    A --> D["❌ Not handling<br/>root changes"]:::mistake
    D --> D1["Impact: rotations at root<br/>don't update self.root"]:::impact
    D1 --> D2["✓ Check if parent is None<br/>and reassign root"]:::fix
    
    A --> E["❌ Wrong case selection<br/>in insertion fixup"]:::mistake
    E --> E1["Impact: red-red violation<br/>not fixed"]:::impact
    E1 --> E2["✓ Check uncle color first<br/>then child position"]:::fix
    
    A --> F["❌ Assuming height<br/>is exactly log(n)"]:::mistake
    F --> F1["Impact: analysis wrong<br/>height is 2·log(n) worst"]:::impact
    F1 --> F2["✓ Remember: RBT allows<br/>longer paths than AVL"]:::fix
    
    classDef warning fill:#FF6B6B,stroke:#333,stroke-width:2px,color:#fff
    classDef mistake fill:#FFB6C6,stroke:#333,stroke-width:2px,color:#000
    classDef impact fill:#FFCCCB,stroke:#333,stroke-width:1px,color:#000
    classDef fix fill:#90ee90,color:#000,stroke:#333,stroke-width:2px,stroke:#333,stroke-width:2px,color:#000
```

---

## ASCII Visualization

### Basic RB Tree Structure

```
            [30,B]
           /       \
       [20,R]     [40,B]
       /    \         \
   [10,B] [25,B]    [50,R]

B = BLACK,  R = RED
NULLs (leaves) are implicitly BLACK
```

### RB Properties

```
1. Every node is RED or BLACK.
2. Root is BLACK.
3. Every NULL leaf is BLACK.
4. If a node is RED, both children are BLACK (no two consecutive reds).
5. For each node, all paths to descendant NULLs contain the same
   number of BLACK nodes (black-height invariant).
```

---

## Insertion Fixup — All 3 Cases

After inserting a RED node z, if z's parent is RED, we have a violation.
Let P = parent, G = grandparent, U = uncle.

### Case 1: Uncle is RED (recolor)

```
       G(B)                  G(R)  <- push redness up
      /    \      -->        /    \
   P(R)   U(R)           P(B)   U(B)
   /                      /
  z(R)                   z(R)
  (continue upward from G)
```

### Case 2: Uncle is BLACK, z is inner child (rotate to make outer)

```
       G(B)                  G(B)
      /    \     LR -->      /    \
   P(R)   U(B)           z(R)   U(B)
      \                   /
      z(R)              P(R)
  (z is right child of P which is left child of G)
  Action: left-rotate P, then treat P as new z for Case 3
```

### Case 3: Uncle is BLACK, z is outer child (rotate + recolor)

```
       G(B)                  P(B)
      /    \     LL -->      /    \
   P(R)   U(B)           z(R)   G(R)
   /                               \
  z(R)                             U(B)
  Action: right-rotate G, swap colors of P and G
```

### Rotation Diagrams

```
Right Rotation on G:              Left Rotation on P:
      G                                  P
     / \           -->                  / \
    P   C                              A   G
   / \                                    / \
  A   B                                  B   C

G's left child B becomes P's right child.
```

---

## Operations & Complexity

| Operation | Best    | Average  | Worst    | Space  |
|-----------|---------|----------|----------|--------|
| Search    | O(1)    | O(log n) | O(log n) | O(1)   |
| Insert    | O(log n)| O(log n) | O(log n) | O(log n) stack |
| Delete    | O(log n)| O(log n) | O(log n) | O(log n) stack |
| Space     | —       | O(n)     | O(n)     | —      |

Height guarantee: h <= 2 * log₂(n+1)

---

## Key Properties / Invariants

1. **Black-height**: bh(T) = number of black nodes on any root-to-null path.
   This is the same for every path (property 5).
2. **Height bound**: A RBT with n internal nodes has height at most 2*log₂(n+1).
3. **Insertion** always adds a RED node (doesn't change black-height, minimizes fixup).
4. **Fixup rotations**: at most 2 rotations on insertion; at most 3 on deletion.
5. **vs AVL**: AVL is more strictly balanced (faster search), RBT has fewer rotations
   (faster insert/delete). Linux kernel uses RBT for this reason.

---

## Common Interview Patterns

| Pattern | Notes |
|---------|-------|
| Order statistics | Augment with `size` subtree field -> rank/select in O(log n) |
| Interval tree | Augment with `max_end` in subtree -> interval overlap queries |
| Balanced BST properties | RBT, AVL, B-tree — know trade-offs |
| Design TreeMap | Describe RBT with in-order traversal for sorted keys |
| Why O(log n) guaranteed? | Black-height argument: no path can be 2x longer than shortest |

---

## Interview Tips

- You almost never have to implement a full RBT in an interview. Know the **properties** and
  the **why** behind them.
- The key insight for property 5 (black-height): the shortest path is all-black with length
  bh; the longest path alternates RED-BLACK with length 2*bh. So max height = 2*bh.
- Deletion is harder than insertion — introduces a "double-black" node concept with 4 cases.
  Know that at most 3 rotations fix a deletion.
- When comparing RBT vs AVL: "RBT is preferred when write-heavy; AVL preferred when
  read-heavy because AVL is more tightly balanced."
- `TreeMap` in Java uses RBT internally — useful to mention in system design.

---

## Example Problems

1. **LeetCode 1382** — Balance a BST (explains BST balancing concepts).
2. **Design a data structure** supporting `insert`, `delete`, `getRandom` in O(log n).
3. **Order statistics**: kth smallest element in a BST — augment RBT with subtree size.
4. **Interval scheduling with overlaps** — interval tree built on RBT.
5. **Linux CFS process scheduler** — describe how RBT stores runnable tasks.

---

## Python Quick Reference

```python
# Python's sortedcontainers.SortedList uses a B-tree variant;
# For interview purposes, use the built-in bisect module or
# roll your own simple RBT skeleton.

RED, BLACK = True, False

class RBNode:
    def __init__(self, key, val=None):
        self.key = key
        self.val = val
        self.color = RED
        self.left = self.right = self.parent = None

class RedBlackTree:
    def __init__(self):
        self.NIL = RBNode(None)        # sentinel leaf
        self.NIL.color = BLACK
        self.root = self.NIL

    def _rotate_left(self, x):
        y = x.right
        x.right = y.left
        if y.left is not self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _rotate_right(self, x):
        y = x.left
        x.left = y.right
        if y.right is not self.NIL:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x is x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    def insert(self, key, val=None):
        z = RBNode(key, val)
        z.left = z.right = z.parent = self.NIL
        y, x = None, self.root
        while x is not self.NIL:
            y = x
            x = x.left if z.key < x.key else x.right
        z.parent = y
        if y is None:
            self.root = z
        elif z.key < y.key:
            y.left = z
        else:
            y.right = z
        self._insert_fixup(z)

    def _insert_fixup(self, z):
        while z.parent and z.parent.color == RED:
            if z.parent is z.parent.parent.left:
                uncle = z.parent.parent.right
                if uncle.color == RED:             # Case 1
                    z.parent.color = BLACK
                    uncle.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                else:
                    if z is z.parent.right:        # Case 2
                        z = z.parent
                        self._rotate_left(z)
                    z.parent.color = BLACK         # Case 3
                    z.parent.parent.color = RED
                    self._rotate_right(z.parent.parent)
            else:
                uncle = z.parent.parent.left
                if uncle.color == RED:
                    z.parent.color = BLACK
                    uncle.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                else:
                    if z is z.parent.left:
                        z = z.parent
                        self._rotate_right(z)
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self._rotate_left(z.parent.parent)
        self.root.color = BLACK

    def search(self, key):
        x = self.root
        while x is not self.NIL and x.key != key:
            x = x.left if key < x.key else x.right
        return x.val if x is not self.NIL else None

# Usage
rbt = RedBlackTree()
for k in [30, 20, 40, 10, 25, 50]:
    rbt.insert(k, k * 10)
print(rbt.search(25))  # 250
```

---

## Java Quick Reference

```java
// Java's TreeMap/TreeSet use Red-Black Tree internally.
// In interviews, use TreeMap directly:

import java.util.TreeMap;
import java.util.TreeSet;

TreeMap<Integer, String> map = new TreeMap<>();
map.put(30, "thirty");
map.put(10, "ten");
map.put(50, "fifty");

// Useful TreeMap methods:
map.floorKey(25);          // largest key <= 25  -> 10
map.ceilingKey(25);        // smallest key >= 25 -> 30
map.firstKey();            // min key            -> 10
map.lastKey();             // max key            -> 50
map.subMap(10, true, 30, true);  // range [10, 30]
map.headMap(30);           // keys < 30
map.tailMap(30);           // keys >= 30

// For order statistics (rank/select), use:
// Apache Commons: TreeList or augment manually
// Or use a policy-based data structure (C++) equivalent

// Key RBT properties to state in interviews:
// - Height <= 2 * log2(n+1)
// - All operations O(log n) worst case
// - At most 2 rotations per insert, 3 per delete
```
