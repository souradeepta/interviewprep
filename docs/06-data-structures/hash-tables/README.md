# Hash Tables — O(1) Average Lookup via Key Hashing

**Level:** L3-L4
**Time to read:** ~20 min

The single most versatile data structure in interviews. When you need to trade space for time, a hash table is usually the answer.

---

## Quick Summary

A hash table maps keys to values using a hash function to compute a bucket index. Average O(1) insert, delete, and search — worst case O(n) when all keys collide. Use when you need fast key-based lookup and don't require ordering. Key trade-off: O(n) extra space buys O(1) operations; hash map loses ordering, BST keeps it.

---

## Operations & Complexity Table

| Operation    | Time (avg) | Time (worst) | Space  | Notes                                      |
|--------------|-----------|-------------|--------|--------------------------------------------|
| Insert       | O(1)      | O(n)        | O(1)   | Worst case: all keys hash to same bucket   |
| Delete       | O(1)      | O(n)        | O(1)   | Same as insert — depends on collisions     |
| Search       | O(1)      | O(n)        | O(1)   | O(n) if many keys in one chain             |
| Iteration    | O(n+m)    | O(n+m)      | O(1)   | m = capacity; iterate all buckets          |
| Resize       | O(n)      | O(n)        | O(n)   | Triggered at load_factor threshold         |

---

## Memory Layout / Internal Structure

```
Hash Table with Chaining (load factor = 0.75):

Hash function: h(key) = hash(key) % capacity

Bucket array (capacity=8):
Index │ Chain
──────┼──────────────────────────────
  0   │ → None
  1   │ → ("apple", 5) → None
  2   │ → ("banana", 3) → ("grape", 7) → None   ← collision!
  3   │ → None
  4   │ → ("cherry", 1) → None
  5   │ → None
  6   │ → ("date", 9) → None
  7   │ → None

Load factor = 4 entries / 8 buckets = 0.5
Rehash triggered at load_factor > 0.75 (Java default)

Open Addressing (linear probing):
   Key: "apple" → h=1 → bucket 1 free → store here
   Key: "grape" → h=1 → bucket 1 occupied → probe bucket 2 → store
   Key: "mango" → h=1 → probe 1→2→3 → store at 3

Bucket: [_] [apple] [grape] [mango] [_] [_] [_] [_]
Index:   0     1      2       3      4   5   6   7

Delete in open addressing uses "tombstone" markers
to avoid breaking probe chains.
```

---

## Trade-offs vs Alternatives

| Feature               | Hash Table   | BST (balanced) | Sorted Array   | Trie           |
|-----------------------|--------------|----------------|----------------|----------------|
| Lookup                | O(1) avg     | O(log n)       | O(log n)       | O(m) key length|
| Insert                | O(1) avg     | O(log n)       | O(n) shift     | O(m)           |
| Delete                | O(1) avg     | O(log n)       | O(n) shift     | O(m)           |
| Ordered iteration     | No           | O(n) in-order  | O(n)           | Alphabetical   |
| Range queries         | No           | O(log n + k)   | O(log n + k)   | Prefix only    |
| Prefix search         | No           | No             | O(log n)       | O(m)           |
| Memory                | O(n) + slack | O(n) pointers  | O(n) compact   | O(ALPHABET×m×n)|
| Collision handling    | Required     | N/A            | N/A            | N/A            |
| Worst-case guarantee  | O(n)         | O(log n)       | O(log n)       | O(m)           |

```
When to choose:
┌─────────────────────────────────────────────────────────────────┐
│ Need O(1) lookup, no ordering required?    → Hash Table         │
│ Need sorted iteration + dynamic inserts?   → BST (TreeMap)      │
│ Need prefix search or autocomplete?        → Trie               │
│ Small, fixed dataset?                      → Sorted Array       │
│ Need deterministic worst-case?             → BST (guaranteed)   │
└─────────────────────────────────────────────────────────────────┘
```

---

## When NOT to Use

- **Ordered operations required** — hash tables have no ordering; use BST (`TreeMap` / `SortedList`).
- **Small number of distinct keys** — the overhead of hashing may exceed a simple array scan.
- **Keys must be sorted in output** — hash maps don't preserve insertion order for sorting (Python 3.7+ preserves insertion order, not sort order).
- **Adversarial inputs (hash DoS)** — if keys are attacker-controlled, worst-case O(n) is a security concern; randomized hashing or tree maps mitigate this.
- **Memory-constrained systems** — hash tables use ~1.3-2x the space of stored data due to load factor slack.

---

## Core Operations (Code)

```python
from collections import defaultdict, Counter

# ── Python dict basics ───────────────────────────────────────────────────────

d = {}
d['key'] = 'value'          # insert / update O(1)
val = d.get('key', None)    # lookup with default O(1)
del d['key']                # delete O(1)
'key' in d                  # membership test O(1)

# ── Common patterns ──────────────────────────────────────────────────────────

# Frequency count
def count_freq(nums: list) -> dict:
    freq = {}
    for x in nums:
        freq[x] = freq.get(x, 0) + 1
    return freq

# Using Counter (faster, same big-O)
from collections import Counter
freq = Counter(nums)
freq.most_common(3)          # top 3 by frequency O(n log k)

# Grouping
def group_by(items, key_fn):
    groups = defaultdict(list)
    for item in items:
        groups[key_fn(item)].append(item)
    return dict(groups)

# ── Custom hash table (chaining) — for interviews ─────────────────────────────

class HashMap:
    """Fixed-size hash map with chaining. Demonstrates internals."""

    def __init__(self, capacity: int = 1024):
        self.capacity = capacity
        self.buckets  = [[] for _ in range(capacity)]    # list of (key, val)

    def _bucket(self, key) -> int:
        return hash(key) % self.capacity

    def put(self, key, val) -> None:
        b = self._bucket(key)
        for i, (k, v) in enumerate(self.buckets[b]):
            if k == key:
                self.buckets[b][i] = (key, val)   # update
                return
        self.buckets[b].append((key, val))         # insert

    def get(self, key, default=None):
        b = self._bucket(key)
        for k, v in self.buckets[b]:
            if k == key:
                return v
        return default

    def remove(self, key) -> None:
        b = self._bucket(key)
        self.buckets[b] = [(k, v) for k, v in self.buckets[b] if k != key]

# ── Load factor and rehashing ─────────────────────────────────────────────────

class DynamicHashMap:
    LOAD_FACTOR = 0.75

    def __init__(self):
        self.capacity = 8
        self.size     = 0
        self.buckets  = [[] for _ in range(self.capacity)]

    def _rehash(self):
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets   = [[] for _ in range(self.capacity)]
        self.size      = 0
        for bucket in old_buckets:
            for k, v in bucket:
                self.put(k, v)    # re-insert into larger table

    def put(self, key, val):
        b = hash(key) % self.capacity
        for i, (k, v) in enumerate(self.buckets[b]):
            if k == key:
                self.buckets[b][i] = (key, val)
                return
        self.buckets[b].append((key, val))
        self.size += 1
        if self.size / self.capacity > self.LOAD_FACTOR:
            self._rehash()
```

---

## 3 Worked Problems

---

### Problem 1 — Two Sum (LeetCode #1)

**Clarifying Questions**
- Can I use the same element twice? (No — two different indices)
- Is there exactly one solution? (Yes, guaranteed)
- Are values distinct? (Not stated — can have duplicates)
- Is the array sorted? (No — assume unsorted)

**Brute Force**

Check every pair.

```python
def two_sum_brute(nums: list[int], target: int) -> list[int]:
    # O(n²) time, O(1) space
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
```

**Optimization**

For each element x, we need `target - x`. Store seen values in a hash map for O(1) lookup.

```python
def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}                           # value → first index
    for i, x in enumerate(nums):
        complement = target - x
        if complement in seen:
            return [seen[complement], i]
        seen[x] = i                     # add after check (avoid using same index)
    return []
```

**Edge Cases**
- `[3, 3]`, target=6 → return `[0, 1]`; works because we check before adding.
- Negative numbers: `[-1, -3]`, target=-4 → complement math still correct.
- Large array: O(n) hash map handles n=10⁵ easily.

**Complexity**
- Time: O(n) — single pass
- Space: O(n) — hash map up to n entries

**Follow-ups**
- "Sorted input?" → Two pointers, O(n) time O(1) space.
- "All pairs?" → Collect pairs instead of early return; careful with duplicates.
- "3Sum?" → Fix one element, two-pointer on rest; O(n²).

---

### Problem 2 — Group Anagrams (LeetCode #49)

**Clarifying Questions**
- Lowercase only? (Yes)
- Empty strings allowed? (Yes — they group together)
- Order of output groups matter? (No)
- Duplicates? (Can appear, group together)

**Brute Force**

For each pair, check if they're anagrams.

```python
# O(n² × m log m) time — impractical
```

**Optimization**

Key insight: anagrams share the same sorted character sequence. Use sorted string (or character count tuple) as hash map key.

```python
from collections import defaultdict

def group_anagrams(strs: list[str]) -> list[list[str]]:
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))          # "eat" → ('a','e','t')
        groups[key].append(s)
    return list(groups.values())

# Alternative key: character count array (faster for long strings)
def group_anagrams_v2(strs: list[str]) -> list[list[str]]:
    groups = defaultdict(list)
    for s in strs:
        count = [0] * 26
        for ch in s:
            count[ord(ch) - ord('a')] += 1
        groups[tuple(count)].append(s)
    return list(groups.values())
```

**Edge Cases**
- `[""]` → one group with one empty string
- `["", ""]` → one group with two empty strings (both map to same zero-count key)
- Single character strings → each unique char is its own group

**Complexity**
- `sorted` version: O(n × m log m) where n = number of strings, m = max length
- `count` version: O(n × m) — linear in total characters

**Follow-ups**
- "Only return groups with ≥ 2 anagrams?" → Filter output.
- "Stream of strings, add one at a time?" → Same hash map, update incrementally.

---

### Problem 3 — LRU Cache (LeetCode #146)

**Clarifying Questions**
- What are get/put operations? (`get(key)` returns value or -1; `put(key, val)` inserts, evicts LRU if at capacity)
- Capacity guaranteed ≥ 1? (Yes)
- Should both operations be O(1)? (Yes — that's the constraint)

**Brute Force**

Store list of (key, val, timestamp). On access, scan for key, update timestamp. On evict, find min timestamp. O(n) per operation.

**Optimization**

Combine hash map (O(1) lookup) with doubly linked list (O(1) move-to-front and evict-from-tail).

```python
from collections import OrderedDict

# Interview shortcut using OrderedDict:
class LRUCache:
    def __init__(self, capacity: int):
        self.cap   = capacity
        self.cache = OrderedDict()      # preserves insertion/access order

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)     # mark as recently used
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.cap:
            self.cache.popitem(last=False)  # evict LRU (front)

# Full implementation (HashMap + doubly linked list) for interviews that ask:
class DLinkedNode:
    def __init__(self, key=0, val=0):
        self.key  = key
        self.val  = val
        self.prev = None
        self.next = None

class LRUCacheManual:
    def __init__(self, capacity: int):
        self.cap  = capacity
        self.map  = {}                          # key → DLinkedNode
        self.head = DLinkedNode()               # dummy head (most recent)
        self.tail = DLinkedNode()               # dummy tail (LRU)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: DLinkedNode):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: DLinkedNode):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next      = node

    def get(self, key: int) -> int:
        if key not in self.map:
            return -1
        node = self.map[key]
        self._remove(node)
        self._add_to_front(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.map:
            self._remove(self.map[key])
        node = DLinkedNode(key, value)
        self._add_to_front(node)
        self.map[key] = node
        if len(self.map) > self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.map[lru.key]
```

**Edge Cases**
- `put` with existing key → update value, move to front (not a new entry)
- `capacity = 1` → every put evicts the previous entry
- `get` on missing key → return -1 (don't change cache)

**Complexity**
- get: O(1) — hash map lookup + O(1) doubly linked list move
- put: O(1) — hash map + O(1) linked list operations
- Space: O(capacity)

**Follow-ups**
- "LFU Cache?" → LeetCode #460; track frequency, evict least frequently used.
- "Thread-safe LRU?" → Lock on get/put; or segment the cache.
- "Distributed LRU?" → Redis with TTL; no explicit eviction needed.

---

## Interview Q&A

**Q1: How does a hash function work and what makes a good one?**

A: A hash function maps a key to an integer index in [0, capacity). A good hash function has three properties: (1) Deterministic — same key always produces same hash. (2) Uniform distribution — hashes spread evenly across buckets to minimize collisions. (3) Fast to compute — O(1) for fixed-size keys. Python's built-in `hash()` uses SipHash-1-3 (randomized per process start) to prevent hash collision DoS attacks.

---

**Q2: Explain chaining vs open addressing for collision resolution.**

A:
```
Chaining:
  - Each bucket holds a linked list (or dynamic array) of entries
  - Load factor can exceed 1.0 (unlimited chain length)
  - Simple to implement; delete is straightforward
  - Bad cache performance (pointer chasing through chain)
  - Java HashMap uses chaining (converts to Red-Black tree at chain length 8)

Open addressing (linear probing):
  - On collision, probe next bucket: (h + 1) % cap, (h + 2) % cap...
  - Load factor must stay below 1.0 (no empty bucket = infinite loop)
  - Better cache performance (data stays in contiguous array)
  - Deletion requires tombstone markers
  - Python dict uses open addressing

Performance crossover: chaining is better at high load factors;
open addressing is better at low load factors (< 0.5) due to cache.
```

---

**Q3: What is a load factor and why does it trigger rehashing?**

A: Load factor = (number of entries) / (number of buckets). As load factor increases, expected chain length increases (for chaining) or probe sequences lengthen (for open addressing), degrading O(1) to O(n). Java's HashMap triggers rehashing at load factor > 0.75 (default), doubling capacity and re-inserting all entries. Rehashing is O(n) but amortized O(1) per insert over n inserts (same argument as dynamic array doubling).

---

**Q4: Why is hash map worst case O(n) and when does it matter?**

A: If all keys hash to the same bucket, every operation must traverse the full chain — O(n). This can happen with: (1) poor hash function that clusters keys, (2) adversarial inputs designed to cause collisions (hash DoS attack). Mitigations: randomized hash seeds (Python, Java 8+), universal hashing, or switching to tree-based maps for security-sensitive code.

---

**Q5: When would you use a HashSet vs HashMap?**

A:
```
HashMap  (key → value):
  - Frequency counting: {"apple": 3, "banana": 1}
  - Caching/memoization: dp[state] = result
  - Grouping: {sorted_key: [anagrams]}
  - Graph adjacency: {node: [neighbors]}

HashSet  (key only, no value):
  - Membership test: "have I seen this element?"
  - Deduplication: remove duplicates from list
  - "Two Sum" seen set (when only existence matters)
  - Cycle detection in linked lists

Rule: if you only need "does this key exist?", use HashSet (simpler, same O(1))
```

---

**Q6: How does Python's dict maintain insertion order?**

A: Since Python 3.7+, `dict` guarantees insertion order. The CPython implementation maintains a compact array of (key, value) pairs in insertion order, plus a hash table of indices into that array. Order is preserved across inserts (new keys appended) but deleted entries leave gaps (compacted on resize). This differs from a sorted map — insertion order ≠ sorted order.

---

**Q7: What is the time complexity of iterating over a hash map?**

A: O(n + capacity) where n is the number of entries and capacity is the bucket array size. Even empty buckets must be scanned. This means iterating over a mostly-empty hash map (e.g., capacity=1024, entries=10) takes O(1024), not O(10). Python's compact dict representation mitigates this; Java's HashMap can be slow to iterate when load factor is low.

---

**Q8: Describe the internal structure of Java's HashMap.**

A:
```
Java HashMap internals (Java 8+):
  - Array of Entry objects (default capacity 16)
  - Each bucket: linked list if chain length ≤ 8
  - Each bucket: Red-Black tree if chain length > 8
                (treeification threshold = 8)
  - Load factor: 0.75 (rehash triggers at 12 entries for cap=16)
  - Resize: double capacity, re-insert all entries

Hash function: key.hashCode() ^ (key.hashCode() >>> 16)
  "Spreads high bits into low bits" — reduces collisions for
  hash functions with poor low-bit distribution.

Why tree at chain 8? Analysis shows Poisson distribution gives
probability < 10^-6 of reaching length 8 with uniform distribution.
Tree only matters under adversarial or degenerate hash functions.
```

---

## Interview Tips

- **Hash map = the default answer.** "How do you do this in O(1)?" is almost always answered with a hash map. Practice the reflex: "I'll use a hash map keyed by X to store Y."
- **Two pointers vs hash map trade-off.** Sorted input → two pointers (O(n) time, O(1) space). Unsorted → hash map (O(n) time, O(n) space). Know when space matters.
- **LRU Cache = hash map + doubly linked list.** This is a top-10 interview question. Know both the `OrderedDict` shortcut and the manual implementation.
- **Anagram/group problems = sort the key.** Sorted string or character count tuple as hash map key solves a whole family of problems.
- **Always mention collision and load factor when explaining hash maps.** It shows depth: "average O(1), worst-case O(n) due to collisions, kept rare by rehashing at load factor 0.75."
