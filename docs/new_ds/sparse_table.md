# Sparse Table

A static data structure that answers idempotent range queries — such as range minimum and range maximum — in O(1) time after O(n log n) preprocessing.

---

## Overview

A Sparse Table precomputes answers for all intervals whose length is a power of two. For each starting index i and each exponent j, `table[j][i]` stores the result of applying the query function to the subarray `arr[i .. i + 2^j − 1]`. Building the table takes O(n log n) time and space via the recurrence `table[j][i] = f(table[j-1][i], table[j-1][i + 2^(j-1)])`.

The key insight that enables O(1) queries is **idempotency**: for functions where `f(x, x) = x` (such as min, max, GCD), two overlapping windows can cover a range without double-counting errors. Given a query `[l, r]`, compute `k = floor(log2(r − l + 1))`, then `answer = f(table[k][l], table[k][r − 2^k + 1])`. The two windows of length `2^k` together cover `[l, r]` completely; their overlap is harmless because the function is idempotent.

Sparse Tables are used in competitive programming for Range Minimum Query (RMQ) as a preprocessing step in suffix array LCP queries (with the Farach-Colton & Bender algorithm), in lowest common ancestor (LCA) algorithms via Euler tour reduction to RMQ, and anywhere a static array needs repeated range queries with no updates.

---

## Flowcharts

### Problem Recognition: When to Use Sparse Table

```mermaid
graph TD
    A["Need range queries<br/>on static data?"]:::decision -->|No| B["Use segment tree<br/>or other dynamic DS"]:::output
    A -->|Yes| C["Array will be<br/>updated after build?"]:::decision
    C -->|Yes, updates needed| D["Use Segment Tree<br/>or Fenwick Tree"]:::output
    C -->|No, static| E["What type of<br/>query?"]:::decision
    E -->|Sum, product| F["Use prefix sum<br/>or Fenwick Tree"]:::output
    E -->|Min, max, GCD| G["Idempotent<br/>function?"]:::decision
    G -->|No| H["Custom decomposition<br/>or Segment Tree"]:::output
    G -->|Yes, f(x,x)=x| I["✓ Sparse Table<br/>is ideal"]:::success
    I --> J["O(n log n) preprocessing<br/>O(1) per query"]:::benefit
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef output fill:#50C878,stroke:#333,stroke-width:2px,color:#000
    classDef success fill:#50C878,stroke:#333,stroke-width:2px,color:#000
    classDef benefit fill:#E0F4FF,stroke:#999,stroke-width:1px,color:#000
```

### Sparse Table vs Range Query Alternatives

```mermaid
graph TD
    A["Choose range query<br/>solution"]:::decision
    
    A --> B["Sparse Table"]:::alt
    B --> B1["✓ O(1) queries for<br/>static idempotent ops<br/>O(n log n) build<br/>Simple implementation"]:::altDetail
    B2["⚠️ No updates<br/>O(n log n) space<br/>Idempotent only"]
    B --> B2
    
    A --> C["Segment Tree"]:::alt
    C --> C1["✓ O(log n) query<br/>O(log n) update<br/>Supports any function<br/>Dynamic"]:::altDetail
    C2["⚠️ More complex<br/>O(n) space<br/>Slower per query"]
    C --> C2
    
    A --> D["Fenwick Tree<br/>(Binary Indexed Tree)"]:::alt
    D --> D1["✓ O(log n) update<br/>O(log n) prefix query<br/>Lower constant factors<br/>Range sum only"]:::altDetail
    D2["⚠️ Only for<br/>prefix sums"]
    D --> D2
    
    A --> E["Sqrt Decomposition"]:::alt
    E --> E1["✓ O(√n) per operation<br/>Better constants<br/>Easier implementation"]:::altDetail
    E2["⚠️ Not O(log n)<br/>Cache inefficient<br/>for range queries"]
    E --> E2
    
    A --> F["Prefix Sum Array<br/>(for range sum)"]:::alt
    F --> F1["✓ O(1) range sum<br/>Minimal space<br/>Trivial to build"]:::altDetail
    F2["⚠️ Static array<br/>Sum only<br/>No updates"]
    F --> F2
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef alt fill:#87CEEB,stroke:#333,stroke-width:2px,color:#000
    classDef altDetail fill:#E0F4FF,stroke:#333,stroke-width:1px,color:#000
```

### Idempotency Check & Function Selection

```mermaid
graph TD
    A["Can Sparse Table<br/>work for this query?"]:::decision
    
    A --> B["Check: is f(x,x) = x?"]:::test
    
    B -->|Min| B1["f(x,x) = x<br/>✓ IDEMPOTENT"]:::yes
    B1 --> B1a["Use Sparse Table"]:::action
    
    B -->|Max| B2["f(x,x) = x<br/>✓ IDEMPOTENT"]:::yes
    B2 --> B2a["Use Sparse Table"]:::action
    
    B -->|GCD| B3["gcd(x,x) = x<br/>✓ IDEMPOTENT"]:::yes
    B3 --> B3a["Use Sparse Table"]:::action
    
    B -->|Bitwise AND| B4["x AND x = x<br/>✓ IDEMPOTENT"]:::yes
    B4 --> B4a["Use Sparse Table"]:::action
    
    B -->|Bitwise OR| B5["x OR x = x<br/>✓ IDEMPOTENT"]:::yes
    B5 --> B5a["Use Sparse Table"]:::action
    
    B -->|Sum| B6["Sum: 1+1 ≠ 1<br/>✗ NOT idempotent"]:::no
    B6 --> B6a["Use prefix sum<br/>or Segment Tree"]:::action
    
    B -->|Product| B7["Product: 2·2 ≠ 2<br/>✗ NOT idempotent"]:::no
    B7 --> B7a["Use Segment Tree"]:::action
    
    B -->|Bitwise XOR| B8["XOR: x XOR x = 0<br/>✗ NOT idempotent"]:::no
    B8 --> B8a["Use Segment Tree"]:::action
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef test fill:#FFE0B2,stroke:#333,stroke-width:2px,color:#000
    classDef yes fill:#90EE90,stroke:#333,stroke-width:2px,color:#000
    classDef no fill:#FF6B6B,stroke:#333,stroke-width:2px,color:#fff
    classDef action fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
```

### Sparse Table Build & Query Process

```mermaid
graph TD
    A["Build Sparse Table"]:::action
    
    A --> B["Initialize level 0:<br/>table[0][i] = arr[i]"]:::step
    B --> B1["Each element is<br/>a trivial window"]:::note
    
    B --> C["Loop j = 1 to LOG-1"]:::step
    C --> C1["For each i where<br/>i + 2^j - 1 < n:"]:::bound
    C1 --> C2["table[j][i] = f(<br/>table[j-1][i],<br/>table[j-1][i+2^(j-1)]<br/>)"]:::formula
    C2 --> C3["Two adjacent<br/>j-1 windows merge"]:::explain
    C3 --> C4{"More levels?"}:::decision
    C4 -->|Yes| C1
    C4 -->|No| C5["✓ Build complete"]:::success
    
    D["Query(l, r)"]:::action
    D --> D1["Compute len = r - l + 1"]:::step
    D1 --> D2["k = floor(log2(len))"]:::step
    D2 --> D3["Window length = 2^k"]:::calc
    D3 --> D4["Query window 1:<br/>table[k][l]"]:::step
    D4 --> D4a["Covers [l, l+2^k-1]"]:::explain
    D4 --> D5["Query window 2:<br/>table[k][r-2^k+1]"]:::step
    D5 --> D5a["Covers [r-2^k+1, r]"]:::explain
    D5 --> D6["answer = f(window1,<br/>window2)"]:::action
    D6 --> D7["✓ O(1) query"]:::success
    D7 --> D8["Windows overlap by<br/>2^k - (r-l+1-2^k)<br/>harmless for idempotent"]:::note
    
    classDef action fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef step fill:#B0E0E6,stroke:#333,stroke-width:1px,color:#000
    classDef formula fill:#FFE0B2,stroke:#333,stroke-width:1px,color:#000
    classDef calc fill:#D0D0D0,stroke:#999,stroke-width:1px,color:#000
    classDef explain fill:#F0F0F0,stroke:#999,stroke-width:1px,color:#000
    classDef note fill:#FFFFFF,stroke:#999,stroke-width:1px,color:#000
    classDef bound fill:#FFFACD,stroke:#999,stroke-width:1px,color:#000
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef success fill:#50C878,stroke:#333,stroke-width:2px,color:#000
```

### Optimization Tradeoff Analysis

```mermaid
graph TD
    A["Sparse Table<br/>tradeoff decisions"]:::goal
    
    A --> B["Optimize for"]:::choose
    
    B -->|Query speed| B1["O(1) per query"]:::benefit
    B1 --> B2["Already optimal<br/>can't go faster"]:::note
    B2 --> B3["Tradeoff: must<br/>build in O(n log n)"]:::tradeoff
    
    B -->|Space usage| B4["O(n log n) build"]:::cost
    B4 --> B5{"Can afford this<br/>space?"}:::decision
    B5 -->|Yes| B6["✓ Use Sparse Table"]:::action
    B5 -->|No, limited memory| B7["Use Sqrt Decomposition<br/>O(√n) space, O(√n) query"]:::alt
    B7 --> B8["Or use Segment Tree<br/>O(n) space, O(log n) query"]:::alt
    
    C["Precomputation burden"]:::cost
    C --> C1["Build only once<br/>then reuse"]:::note
    C1 --> C2["If # queries << n,<br/>overhead matters"]:::scenario
    C1 --> C3["If # queries >> n log n,<br/>overhead amortized"]:::scenario
    C3 --> C4["Recommendation:<br/>use Sparse Table<br/>if queries > n log n"]:::recommend
    
    D["Table size<br/>estimation"]:::info
    D --> D1["LOG = ⌈log₂(n)⌉"]:::formula
    D1 --> D2["Exact levels<br/>= n.bit_length()"]:::impl
    D2 --> D3["Space = LOG × n"]:::space
    D3 --> D4["Example: n=10^6<br/>LOG≈20, space≈20M"]:::example
    D4 --> D5{"Affordable?"}:::decision
    D5 -->|Yes| D6["✓ Sparse Table<br/>is choice"]:::action
    D5 -->|No| D7["Use Segment Tree<br/>space=2n"]:::alt
    
    classDef goal fill:#FFD700,stroke:#333,stroke-width:3px,color:#000
    classDef choose fill:#87CEEB,stroke:#333,stroke-width:2px,color:#000
    classDef benefit fill:#90EE90,stroke:#333,stroke-width:1px,color:#000
    classDef cost fill:#FFB6C6,stroke:#333,stroke-width:1px,color:#000
    classDef tradeoff fill:#FFE0B2,stroke:#333,stroke-width:1px,color:#000
    classDef note fill:#FFFFFF,stroke:#999,stroke-width:1px,color:#000
    classDef scenario fill:#F0F0F0,stroke:#999,stroke-width:1px,color:#000
    classDef recommend fill:#FFFACD,stroke:#333,stroke-width:2px,color:#000
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef action fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef alt fill:#FFCCCB,stroke:#333,stroke-width:1px,color:#000
    classDef formula fill:#E0E0E0,stroke:#999,stroke-width:1px,color:#000
    classDef impl fill:#D0D0D0,stroke:#999,stroke-width:1px,color:#000
    classDef space fill:#F5F5F5,stroke:#999,stroke-width:1px,color:#000
    classDef example fill:#FFF8DC,stroke:#999,stroke-width:1px,color:#000
    classDef info fill:#F0F8FF,stroke:#333,stroke-width:2px,color:#000
```

### Implementation Approach & Edge Cases

```mermaid
graph TD
    A["Implement Sparse Table"]:::goal
    
    A --> B["Step 1: Precompute log2[]"]:::step
    B --> B1["log2[0] = log2[1] = 0"]:::init
    B1 --> B2["For i=2 to n:"]:::loop
    B2 --> B3["log2[i] = log2[i//2] + 1"]:::formula
    B3 --> B4["✓ O(n) preprocessing"]:::benefit
    
    A --> C["Step 2: Build min/max<br/>tables"]:::step
    C --> C1["table[j][i] = min of<br/>arr[i..i+2^j-1]"]:::define
    C1 --> C2["Level 0: each<br/>element"]:::base
    C2 --> C3["Level j: merge<br/>two level j-1 windows"]:::recurrence
    C3 --> C4["Check bounds:<br/>i + (1<<j) - 1 < n"]:::critical
    C4 --> C5["✓ O(n log n) build"]:::benefit
    
    A --> D["Step 3: Query<br/>implementation"]:::step
    D --> D1["k = log2[r - l + 1]"]:::lookup
    D1 --> D2["ans = f("]:::formula
    D2 --> D3["  table[k][l],"]:::window1
    D3 --> D4["  table[k][r-(1<<k)+1]"]:::window2
    D4 --> D5[")"]:::close
    D5 --> D6["✓ O(1) per query"]:::benefit
    
    E["Edge cases"]:::warning
    E --> E1["❌ Out-of-bounds<br/>table access"]:::bug
    E1 --> E2["✓ Always check<br/>i + (1<<j) - 1 < n"]:::fix
    E --> E3["❌ Wrong log2 formula"]:::bug
    E3 --> E4["✓ Use bit_length()<br/>or manual recursion"]:::fix
    E --> E5["❌ Forgetting to<br/>build level 0"]:::bug
    E5 --> E6["✓ Initialize trivial<br/>single-element windows"]:::fix
    E --> E7["❌ Not handling<br/>single-element query"]:::bug
    E7 --> E8["✓ Query [i,i]<br/>returns arr[i]"]:::fix
    
    classDef goal fill:#FFD700,stroke:#333,stroke-width:3px,color:#000
    classDef step fill:#87CEEB,stroke:#333,stroke-width:2px,color:#000
    classDef init fill:#B0E0E6,stroke:#999,stroke-width:1px,color:#000
    classDef loop fill:#E0F4FF,stroke:#999,stroke-width:1px,color:#000
    classDef formula fill:#FFE0B2,stroke:#999,stroke-width:1px,color:#000
    classDef define fill:#FFFACD,stroke:#999,stroke-width:1px,color:#000
    classDef base fill:#F0F0F0,stroke:#999,stroke-width:1px,color:#000
    classDef recurrence fill:#F5F5F5,stroke:#999,stroke-width:1px,color:#000
    classDef critical fill:#FF6B6B,stroke:#333,stroke-width:2px,color:#fff
    classDef benefit fill:#90EE90,stroke:#333,stroke-width:1px,color:#000
    classDef lookup fill:#D0D0D0,stroke:#999,stroke-width:1px,color:#000
    classDef window1 fill:#FFE0B2,stroke:#999,stroke-width:1px,color:#000
    classDef window2 fill:#FFE0B2,stroke:#999,stroke-width:1px,color:#000
    classDef close fill:#FFE0B2,stroke:#999,stroke-width:1px,color:#000
    classDef warning fill:#FF6B6B,stroke:#333,stroke-width:2px,color:#fff
    classDef bug fill:#FFB6C6,stroke:#333,stroke-width:1px,color:#000
    classDef fix fill:#90EE90,stroke:#333,stroke-width:2px,color:#000
```

### Common Mistakes & Debugging Guide

```mermaid
graph TD
    A["Common Sparse Table<br/>pitfalls"]:::warning
    
    A --> B["❌ Using range sum<br/>instead of min/max"]:::mistake
    B --> B1["Impact: overlap in<br/>windows counted twice"]:::impact
    B1 --> B2["✓ Fix: only idempotent<br/>functions work"]:::fix
    
    A --> C["❌ Not precomputing<br/>log2[] array"]:::mistake
    C --> C1["Impact: O(log n)<br/>per query overhead"]:::impact
    C1 --> C2["✓ Fix: cache log2[]<br/>O(1) lookup"]:::fix
    
    A --> D["❌ Off-by-one errors<br/>in bounds check"]:::mistake
    D --> D1["Impact: reads beyond<br/>array, crashes"]:::impact
    D1 --> D2["✓ Fix: verify<br/>i + 2^j - 1 < n"]:::fix
    
    A --> E["❌ Building only<br/>min table, forgetting max"]:::mistake
    E --> E1["Impact: can't answer<br/>max queries"]:::impact
    E1 --> E2["✓ Fix: build both<br/>in single pass"]:::fix
    
    A --> F["❌ Incorrect query<br/>window formula"]:::mistake
    F --> F1["Impact: wrong answers"]:::impact
    F1 --> F2["✓ Windows must be:<br/>table[k][l] and table[k][r-2^k+1]"]:::fix
    
    classDef warning fill:#FF6B6B,stroke:#333,stroke-width:2px,color:#fff
    classDef mistake fill:#FFB6C6,stroke:#333,stroke-width:2px,color:#000
    classDef impact fill:#FFCCCB,stroke:#333,stroke-width:1px,color:#000
    classDef fix fill:#90EE90,stroke:#333,stroke-width:2px,color:#000
```

---

## ASCII Visualization

```
Array:  [2, 4, 3, 1, 6, 7, 8, 9, 1, 7]
Index:   0  1  2  3  4  5  6  7  8  9

Min Table (table[j][i] = min of arr[i .. i + 2^j - 1]):

Level j=0  (window len=1, trivially arr[i]):
  i:    0  1  2  3  4  5  6  7  8  9
  val:  2  4  3  1  6  7  8  9  1  7

Level j=1  (window len=2, combine two adjacent j=0 windows):
  i:    0  1  2  3  4  5  6  7  8
  val:  2  3  1  1  6  7  8  1  1
  e.g. table[1][2] = min(table[0][2], table[0][3]) = min(3,1) = 1

Level j=2  (window len=4, combine two adjacent j=1 windows):
  i:    0  1  2  3  4  5  6
  val:  1  1  1  1  6  1  1
  e.g. table[2][0] = min(table[1][0], table[1][2]) = min(2,1) = 1

Level j=3  (window len=8, combine two adjacent j=2 windows):
  i:    0  1  2
  val:  1  1  1

Query: min(arr[2..7]) = ?
  length = 7-2+1 = 6,  k = floor(log2(6)) = 2,  2^k = 4
  Window 1: table[2][2] = min(arr[2..5]) = 1
  Window 2: table[2][4] = min(arr[4..7]) = 6

       arr: 2  4 [3  1  6  7  8  9] 1  7
                  ^----- W1 ----^
                        ^----- W2 ----^
                  overlap: indices 4,5 appear in both (harmless for min)

  answer = min(1, 6) = 1  (correct: min of [3,1,6,7,8,9] = 1)
```

---

## Operations & Complexity

| Operation        | Average     | Worst       | Notes                                           |
|------------------|-------------|-------------|--------------------------------------------------|
| `build(arr)`     | O(n log n)  | O(n log n)  | Fills LOG levels, each with up to n entries     |
| `query_min(l,r)` | O(1)        | O(1)        | Two table lookups + one integer log2 lookup     |
| `query_max(l,r)` | O(1)        | O(1)        | Same two-window trick for maximum               |
| Space            | O(n log n)  | O(n log n)  | LOG ≈ log2(n)+1 levels, each length n           |

- Queries require no branching: one precomputed `log2[]` array lookup, two table reads, one comparison.
- Sparse Table cannot handle updates; for dynamic arrays use a Segment Tree (O(log n) update + O(log n) query).
- Range sum is NOT idempotent; use a prefix sum array for O(1) range sum queries on static arrays instead.

---

## Key Invariants

- `table[j][i]` is only valid for indices `i` such that `i + 2^j − 1 < n` (the window must fit within the array).
- Level 0 is the identity level: `table[0][i] = arr[i]` for all i.
- Each level j is built entirely from level j−1; building must proceed in order j = 1, 2, …, LOG−1.
- The `log2[]` precomputed array satisfies `log2[1] = 0` and `log2[i] = log2[i//2] + 1` for i ≥ 2; it is used to avoid calling `math.floor(math.log2(length))` in the hot query path.
- The array is treated as **immutable** after `build()`; any modification invalidates the precomputed table.
- Two query windows together must always cover the entire `[l, r]` range: window 1 starts at l, window 2 ends at r, both have length `2^k` where `2^k ≤ length < 2^(k+1)`.

---

## Common Interview Questions

- **Why is the query O(1) instead of O(log n)?** Because min/max are idempotent: overlapping the two power-of-two windows is safe, so a single pair of precomputed values suffices without recursion.
- **What types of range queries work with Sparse Table?** Only idempotent functions where `f(x, x) = x`: min, max, GCD, bitwise AND, bitwise OR. Range sum and range product are not idempotent and cannot use this technique.
- **How do you precompute floor(log2(i)) in O(n) for all i up to n?** Use the recurrence `log2[i] = log2[i//2] + 1` with `log2[0] = log2[1] = 0`, iterated from i=2 to n.
- **When would you use Sparse Table over Segment Tree?** When the array is static (no updates) and you need maximum query throughput — Sparse Table has better constant factors and simpler cache behavior. For updates, Segment Tree is necessary.
- **How is Sparse Table used in LCA algorithms?** Reduce LCA on a tree to RMQ by performing an Euler tour of the tree, recording depths, then building a Sparse Table on depths — LCA(u, v) corresponds to a range minimum query.
- **What is the space complexity and can it be reduced?** O(n log n); the Fischer-Heun structure reduces this to O(n) preprocessing and O(1) query using block decomposition, but it is complex to implement.

---

## Implementation Notes

- **LOG levels**: `LOG = n.bit_length()` equals `floor(log2(n)) + 1` for n ≥ 1; this is exactly the number of table levels needed.
- **Table bounds**: when filling level j, only fill indices `i` where `i + (1 << j) - 1 < n`, i.e., `i < n - (1 << j) + 1`. Accessing out-of-bounds indices silently returns `None` in Python but causes index errors in Java/C++.
- **Integer log2 trick**: `k = (r - l + 1).bit_length() - 1` is equivalent to `floor(log2(r - l + 1))` and avoids floating-point; alternatively, maintain a precomputed `log2[]` array to avoid the bit_length call in the query hot path.
- **Separate min and max tables**: since building is O(n log n) either way, the implementation builds both `_min_table` and `_max_table` in a single pass over each level, doubling memory but halving build iterations.
- **Not suitable for online updates**: if even one element changes, the entire table must be rebuilt. For mixed update/query workloads, a Segment Tree with lazy propagation is the correct choice.
- **Practical query speed**: the two-lookup O(1) query is extremely cache-friendly on small-to-medium n; on large n (>10^6), cache misses from the table's non-sequential access pattern can slow queries — a block decomposition or sqrt-decomposition may be preferable.

---

## References

- [Wikipedia — Sparse table (data structure)](https://en.wikipedia.org/wiki/Sparse_table)
- [CP-Algorithms — Sparse Table](https://cp-algorithms.com/data_structures/sparse-table.html)
- [Bender, M. A. & Farach-Colton, M. (2000). The LCA Problem Revisited. LATIN 2000.](https://www.cs.stonybrook.edu/~bender/newpub/BenderFa00-lca.pdf)
