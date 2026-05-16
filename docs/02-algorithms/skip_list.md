# Skip List

## Overview

A Skip List is a probabilistic data structure built on top of a sorted linked list.
It adds express lanes — extra levels of forward pointers — so that searches can skip
over large sections of the list, achieving O(log n) average-case performance without
the rotational complexity of balanced BSTs.

Invented by William Pugh (1990), skip lists are used in Redis sorted sets, LevelDB
memtables, and Java's `ConcurrentSkipListMap`.

---

## Flowcharts

### Problem Recognition: When to Use Skip List

```mermaid
graph TD
    A["Need ordered map/set<br/>with O(log n) ops?"]:::decision -->|No| B["Use different DS"]:::output
    A -->|Yes| C["Is concurrent access<br/>needed?"]:::decision
    C -->|Yes| D["Use Skip List<br/>easier lock-free"]:::output
    C -->|No, single-thread| E["Use RB-Tree or AVL<br/>deterministic"]:::output
    E --> E1["Still considering<br/>Skip List?"]:::decision
    E1 -->|Simpler code preferred| F["✓ Skip List is fine"]:::success
    E1 -->|Deterministic required| G["Stick with RB-Tree"]:::output
    F --> H["Level assignment:<br/>coin flip randomness"]:::note
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef output fill:#50C878,stroke:#333,stroke-width:2px,color:#000
    classDef success fill:#50C878,stroke:#333,stroke-width:2px,color:#000
    classDef note fill:#FFFFFF,stroke:#999,stroke-width:1px,color:#000
```

### Skip List vs Balanced Tree Alternatives

```mermaid
graph TD
    A["Choose ordered map<br/>implementation"]:::decision
    
    A --> B["Skip List"]:::alt
    B --> B1["✓ Simpler concurrent<br/>implementation<br/>Lock-free variants<br/>Good constant factors<br/>Redis, LevelDB use it"]:::altDetail
    B2["⚠️ Randomized O(log n)<br/>Probabilistic guarantee<br/>Extra space for levels"]
    B --> B2
    
    A --> C["Red-Black Tree"]:::alt
    C --> C1["✓ Deterministic O(log n)<br/>Well-studied<br/>Used in Linux, Java"]:::altDetail
    C2["⚠️ Complex rotations<br/>Harder to parallelize"]
    C --> C2
    
    A --> D["AVL Tree"]:::alt
    D --> D1["✓ More balanced<br/>than RB-Tree<br/>Faster search"]:::altDetail
    D2["⚠️ More rebalancing<br/>Overhead on updates"]
    D --> D2
    
    A --> E["B-Tree"]:::alt
    E --> E1["✓ Cache-friendly<br/>Good for disk I/O"]:::altDetail
    E2["⚠️ Complex multi-key<br/>management"]
    E --> E2
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef alt fill:#87CEEB,stroke:#333,stroke-width:2px,color:#000
    classDef altDetail fill:#E0F4FF,stroke:#333,stroke-width:1px,color:#000
```

### Level Assignment & Promotion Strategy

```mermaid
graph TD
    A["Insert new node with key"]:::action
    A --> B["Assign random level"]:::step
    B --> B1["Flip coin (p=0.5):<br/>H → promote<br/>T → stop"]:::randomness
    B1 --> B2{"Continue<br/>flipping?"}:::decision
    B2 -->|Heads: yes| B3["Level += 1"]:::step
    B3 --> B4{"Exceed<br/>max_level?"}:::decision
    B4 -->|Yes| B5["Stop at max_level"]:::limit
    B4 -->|No| B2
    B2 -->|Tails: no| B6["Assigned level = current"]:::result
    
    C["Node appears in<br/>levels 0..L"]:::info
    C --> C1["Level 0: base sorted<br/>linked list"]:::level
    C1 --> C1a["Every element here"]:::guarantee
    C --> C2["Level 1+: progressively<br/>thinner layers"]:::level
    C2 --> C2a["Probability halves<br/>per level"]:::guarantee
    
    D["Expected properties<br/>with p=0.5"]:::prop
    D --> D1["Expected # levels<br/>= log₂(n) + O(1)"]:::stat
    D --> D2["Expected space<br/>= 2n (each node in ~2 levels)"]:::stat
    D --> D3["Expected search path<br/>= 2·log₂(n) comparisons"]:::stat
    
    classDef action fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef step fill:#B0E0E6,stroke:#333,stroke-width:1px,color:#000
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef randomness fill:#FFE0B2,stroke:#333,stroke-width:2px,color:#000
    classDef limit fill:#FFFACD,stroke:#999,stroke-width:1px,color:#000
    classDef result fill:#90ee90,color:#000,stroke:#333,stroke-width:2px,stroke:#333,stroke-width:1px,color:#000
    classDef info fill:#F0F8FF,stroke:#333,stroke-width:2px,color:#000
    classDef level fill:#E0F4FF,stroke:#333,stroke-width:1px,color:#000
    classDef guarantee fill:#FFFFFF,stroke:#999,stroke-width:1px,color:#000
    classDef prop fill:#FFF8DC,stroke:#333,stroke-width:2px,color:#000
    classDef stat fill:#F5DEB3,stroke:#999,stroke-width:1px,color:#000
```

### Search & Update Operations

```mermaid
graph TD
    A["Skip List operation"]:::decision
    
    A -->|Search for key| B["Start at HEAD,<br/>topmost level"]:::action
    B --> B1["Walk forward while<br/>next.key < target"]:::step
    B1 --> B2{"Overshot or<br/>at end?"}:::decision
    B2 -->|Yes| B3["Drop down<br/>one level"]:::step
    B3 --> B4{"At level 0?"}:::decision
    B4 -->|No| B1
    B4 -->|Yes| B5["Found or not found"]:::result
    
    A -->|Insert key, val| C["Search to find<br/>position (get update[])"]:::action
    C --> C1["update[i] = node before<br/>insertion point at level i"]:::step
    C1 --> C2["Check: is key<br/>already present?"]:::decision
    C2 -->|Yes| C3["Update value,<br/>return"]:::action
    C2 -->|No| C4["Generate random level"]:::action
    C4 --> C5["If level > current_level,<br/>update missing levels"]:::step
    C5 --> C6["Create new node"]:::step
    C6 --> C7["Insert at all<br/>appropriate levels"]:::step
    C7 --> C8["✓ Insertion complete"]:::success
    
    A -->|Delete key| D["Search to find<br/>node (get update[])"]:::action
    D --> D1{"Key found?"}:::decision
    D1 -->|No| D2["Return false"]:::output
    D1 -->|Yes| D3["Remove from all<br/>levels"]:::step
    D3 --> D4["Trim excess levels<br/>at head if empty"]:::step
    D4 --> D5["✓ Deletion complete"]:::success
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef action fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef step fill:#B0E0E6,stroke:#333,stroke-width:1px,color:#000
    classDef result fill:#FFFACD,stroke:#999,stroke-width:1px,color:#000
    classDef output fill:#D3D3D3,stroke:#333,stroke-width:1px,color:#000
    classDef success fill:#50C878,stroke:#333,stroke-width:2px,color:#000
```

### Complexity Analysis: Search Path Cost

```mermaid
graph TD
    A["Analyze Skip List<br/>search complexity"]:::analysis
    
    A --> B["Top-down search path"]:::method
    B --> B1["Start at HEAD,<br/>level L-1 (top)"]:::step
    B1 --> B2["Expected # levels<br/>= O(log n)"]:::bound
    
    C["At each level i"]:::detail
    C --> C1["Walk forward until<br/>next.key ≥ target"]:::action
    C1 --> C2["Expected hops per level<br/>= 2 (since p=0.5)"]:::bound
    C2 --> C3["If p=0.5:<br/>at level i, ~n/2^i nodes"]:::analysis
    C3 --> C4["Must skip over<br/>~2 nodes on average"]:::reasoning
    
    D["Total cost"]:::summary
    D --> D1["Search = O(log n) levels<br/>× O(2) hops/level"]:::formula
    D1 --> D2["Expected comparisons<br/>= 2·log₂(n)"]:::result
    D2 --> D3["Worst case:<br/>all nodes at all levels"]:::worstcase
    D3 --> D4["Worst case = O(n)<br/>astronomically unlikely"]:::note
    
    E["Space analysis"]:::summary
    E --> E1["Each node appears<br/>in ~2 levels on average"]:::expected
    E1 --> E2["Space = O(n)"]:::bound
    E2 --> E3["vs RB-Tree: same O(n)"]:::compare
    E3 --> E4["Extra pointers, but<br/>simpler structure"]:::tradeoff
    
    classDef analysis fill:#F0F8FF,stroke:#333,stroke-width:2px,color:#000
    classDef method fill:#87CEEB,stroke:#333,stroke-width:1px,color:#000
    classDef step fill:#B0E0E6,stroke:#333,stroke-width:1px,color:#000
    classDef detail fill:#E0F4FF,stroke:#333,stroke-width:1px,color:#000
    classDef action fill:#4A90E2,stroke:#333,stroke-width:1px,color:#fff
    classDef bound fill:#FFFACD,stroke:#999,stroke-width:1px,color:#000
    classDef reasoning fill:#F5F5F5,stroke:#999,stroke-width:1px,color:#000
    classDef summary fill:#FFF8DC,stroke:#333,stroke-width:2px,color:#000
    classDef formula fill:#FFE0B2,stroke:#999,stroke-width:1px,color:#000
    classDef result fill:#90ee90,color:#000,stroke:#333,stroke-width:2px,stroke:#333,stroke-width:1px,color:#000
    classDef worstcase fill:#FF6B6B,stroke:#333,stroke-width:1px,color:#fff
    classDef note fill:#FFFFFF,stroke:#999,stroke-width:1px,color:#000
    classDef compare fill:#E0F4FF,stroke:#999,stroke-width:1px,color:#000
    classDef tradeoff fill:#F0F0F0,stroke:#999,stroke-width:1px,color:#000
```

### Common Mistakes & Implementation Pitfalls

```mermaid
graph TD
    A["Common Skip List pitfalls"]:::warning
    
    A --> B["❌ Not maintaining<br/>update[] array properly"]:::mistake
    B --> B1["Impact: wrong pointers<br/>after insertion/deletion"]:::impact
    B1 --> B2["✓ Fix: carefully track<br/>predecessor at each level"]:::fix
    
    A --> C["❌ Forgetting to trim<br/>excess levels at head"]:::mistake
    C --> C1["Impact: memory waste<br/>after deletions"]:::impact
    C1 --> C2["✓ Fix: after delete,<br/>remove empty top levels"]:::fix
    
    A --> D["❌ Hash function bias<br/>in random level selection"]:::mistake
    D --> D1["Impact: some levels<br/>underutilized"]:::impact
    D1 --> D2["✓ Fix: use uniform random<br/>in [0, 1)"]:::fix
    
    A --> E["❌ Not checking<br/>key equality on level 0"]:::mistake
    E --> E1["Impact: can miss exact<br/>key match"]:::impact
    E1 --> E2["✓ Fix: always proceed<br/>to level 0 for final check"]:::fix
    
    A --> F["❌ Updating current_level<br/>incorrectly"]:::mistake
    F --> F1["Impact: levels lost<br/>or corrupted"]:::impact
    F1 --> F2["✓ Fix: only update<br/>when inserting node"]:::fix
    
    A --> G["❌ Comparing keys<br/>without null checks"]:::mistake
    G --> G1["Impact: crash on NIL<br/>sentinel"]:::impact
    G1 --> G2["✓ Fix: check if<br/>forward[i] != null"]:::fix
    
    classDef warning fill:#FF6B6B,stroke:#333,stroke-width:2px,color:#fff
    classDef mistake fill:#FFB6C6,stroke:#333,stroke-width:2px,color:#000
    classDef impact fill:#FFCCCB,stroke:#333,stroke-width:1px,color:#000
    classDef fix fill:#90ee90,color:#000,stroke:#333,stroke-width:2px,stroke:#333,stroke-width:2px,color:#000
```

---

## ASCII Visualization

```
Inserting: 10, 20, 30, 50, 70, 90  (some nodes randomly promoted)

Level 3: HEAD ─────────────────────────────────> 50 ────────────────> NIL
Level 2: HEAD ────────────> 20 ──────────────> 50 ──────> 70 ───────> NIL
Level 1: HEAD ──> 10 ──> 20 ──────────> 50 ──────────> 70 ──> 90 ───> NIL
Level 0: HEAD ──> 10 ──> 20 ──> 30 ──> 50 ──> 70 ──> 90 ─────────── > NIL
          (base layer: sorted linked list with ALL elements)
```

### Search for 70 — walk top-down

```
Start at HEAD, Level 3
  HEAD -> 50 (50 < 70, advance)  50 -> NIL  (stop, drop to Level 2)
Level 2 from 50:
  50 -> 70 (70 == 70, FOUND)
```

### Node Promotion (coin flip)

```
New node with key=40:
  Flip coin: H (promote to L1)
  Flip coin: H (promote to L2)
  Flip coin: T (stop)   -> node lives in levels 0, 1, 2
```

---

## Operations & Complexity

| Operation | Average   | Worst  | Notes                          |
|-----------|-----------|--------|--------------------------------|
| Search    | O(log n)  | O(n)   | Probabilistic guarantee        |
| Insert    | O(log n)  | O(n)   | Random level assignment        |
| Delete    | O(log n)  | O(n)   | Must update all level pointers |
| Space     | O(n) avg  |O(n log n)| Each node in ~2 levels avg  |

- Average assumes promotion probability p = 0.5 and max level = log₂(n).
- Worst case occurs when every node promotes to all levels (degenerate).

---

## Key Properties / Invariants

1. **Level 0** is the complete sorted linked list — every element is here.
2. Each level i is a **subset** of level i-1.
3. A node at level k also appears at all levels 0..k.
4. HEAD sentinel has `-inf` key and spans all levels; NIL sentinel terminates each level.
5. **Promotion probability**: node promoted to level k with probability p^k.
   With p = 0.5 and n elements, expected levels = log₂(n).
6. No false ordering: keys are always in ascending order on every level.

---

## Common Interview Patterns

| Pattern | Description |
|---------|-------------|
| Design ordered map | Use skip list instead of BST when concurrent access is needed |
| Range queries | Walk level 0 from found node; all elements in range are adjacent |
| Rank / order statistics | Augment each forward pointer with a `span` count |
| Floor/ceiling queries | Stop one step before overshooting; that node is floor |

---

## Interview Tips

- When asked "why skip list over balanced BST?" — answer: simpler concurrent implementation
  (CAS on forward pointers vs tree rotations), lock-free variants exist.
- The expected number of comparisons is **2 log₂ n** — close to a balanced BST.
- If asked to implement: start with the `update[]` array pattern; it holds the predecessor
  at each level, enabling pointer surgery in O(log n).
- Know that Redis uses a **augmented** skip list (with `span` field) to support rank queries.
- Worst case is O(n) but astronomically unlikely with random coin flips.

---

## Example Problems

1. **Design Skiplist** (LeetCode 1206) — implement `search`, `add`, `erase`.
2. **Design a Data Structure that Supports Range Sum Queries** — augmented skip list.
3. **Redis Sorted Set design** — use skip list + hash map for O(log n) rank and score ops.
4. **Concurrent ordered map** — explain why skip list beats AVL/Red-Black for lock-free design.

---

## Python Quick Reference

```python
# Source: python/new_ds/skip_list.py
import random

MAX_LEVEL = 16
P = 0.5

class SkipListNode:
    def __init__(self, key, val, level):
        self.key = key
        self.val = val
        self.forward = [None] * (level + 1)

class SkipList:
    def __init__(self, max_level=MAX_LEVEL, p=P):
        self.max_level = max_level
        self.p = p
        self.current_level = 0
        self.size = 0
        self._head = SkipListNode(float('-inf'), None, max_level)

    def _random_level(self):
        level = 0
        while random.random() < self.p and level < self.max_level:
            level += 1
        return level

    def _find_update(self, key):
        update = [None] * (self.max_level + 1)
        cur = self._head
        for i in range(self.current_level, -1, -1):
            while cur.forward[i] and cur.forward[i].key < key:
                cur = cur.forward[i]
            update[i] = cur
        return update

    def insert(self, key, val):
        update = self._find_update(key)
        candidate = update[0].forward[0]
        if candidate and candidate.key == key:
            candidate.val = val
            return
        lvl = self._random_level()
        if lvl > self.current_level:
            for i in range(self.current_level + 1, lvl + 1):
                update[i] = self._head
            self.current_level = lvl
        node = SkipListNode(key, val, lvl)
        for i in range(lvl + 1):
            node.forward[i] = update[i].forward[i]
            update[i].forward[i] = node
        self.size += 1

    def search(self, key):
        cur = self._head
        for i in range(self.current_level, -1, -1):
            while cur.forward[i] and cur.forward[i].key < key:
                cur = cur.forward[i]
        cur = cur.forward[0]
        return cur.val if cur and cur.key == key else None

    def delete(self, key):
        update = self._find_update(key)
        target = update[0].forward[0]
        if not target or target.key != key:
            return False
        for i in range(self.current_level + 1):
            if update[i].forward[i] is not target:
                break
            update[i].forward[i] = target.forward[i]
        while self.current_level > 0 and not self._head.forward[self.current_level]:
            self.current_level -= 1
        self.size -= 1
        return True

# Usage
sl = SkipList()
sl.insert(3, "three")
sl.insert(1, "one")
print(sl.search(3))   # "three"
sl.delete(1)
print(1 in sl)        # False (uses __contains__ -> search)
```

---

## Java Quick Reference

```java
// Source: java/new_ds/SkipList.java
import java.util.Random;

public class SkipList<K extends Comparable<K>, V> {
    private static final int MAX_LEVEL = 16;
    private static final double P = 0.5;

    private static class Node<K, V> {
        K key; V val;
        Node<K, V>[] forward;
        @SuppressWarnings("unchecked")
        Node(K key, V val, int level) {
            this.key = key; this.val = val;
            forward = new Node[level + 1];
        }
    }

    private final Node<K, V> head;
    private int currentLevel = 0;
    private final Random rng = new Random();

    @SuppressWarnings("unchecked")
    public SkipList() {
        head = new Node<>(null, null, MAX_LEVEL);
    }

    private int randomLevel() {
        int level = 0;
        while (rng.nextDouble() < P && level < MAX_LEVEL) level++;
        return level;
    }

    public V search(K key) {
        Node<K, V> cur = head;
        for (int i = currentLevel; i >= 0; i--)
            while (cur.forward[i] != null && cur.forward[i].key.compareTo(key) < 0)
                cur = cur.forward[i];
        cur = cur.forward[0];
        return (cur != null && cur.key.compareTo(key) == 0) ? cur.val : null;
    }

    @SuppressWarnings("unchecked")
    public void insert(K key, V val) {
        Node<K, V>[] update = new Node[MAX_LEVEL + 1];
        Node<K, V> cur = head;
        for (int i = currentLevel; i >= 0; i--) {
            while (cur.forward[i] != null && cur.forward[i].key.compareTo(key) < 0)
                cur = cur.forward[i];
            update[i] = cur;
        }
        Node<K, V> candidate = cur.forward[0];
        if (candidate != null && candidate.key.compareTo(key) == 0) {
            candidate.val = val; return;
        }
        int lvl = randomLevel();
        if (lvl > currentLevel) {
            for (int i = currentLevel + 1; i <= lvl; i++) update[i] = head;
            currentLevel = lvl;
        }
        Node<K, V> node = new Node<>(key, val, lvl);
        for (int i = 0; i <= lvl; i++) {
            node.forward[i] = update[i].forward[i];
            update[i].forward[i] = node;
        }
    }
}
```
