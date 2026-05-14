# Bloom Filter

A space-efficient probabilistic data structure that tests set membership with guaranteed no false negatives but a tunable false-positive probability.

---

## Overview

A Bloom Filter uses a bit array of m bits and k independent hash functions to represent a set. Adding an item sets k bit positions; querying checks whether all k positions are 1. If any bit is 0 the item was definitely never inserted. If all k bits are 1 the item was probably inserted — but a false positive is possible because those bits may have been set by other items.

The false-positive probability is governed by `p ≈ (1 − e^{−kn/m})^k`, where n is the number of inserted items. Given a target error rate p and expected capacity n, the optimal bit array size is `m = ⌈−n·ln(p) / (ln 2)²⌉` and the optimal number of hash functions is `k = (m/n)·ln 2`. For p ≈ 1%, this works out to roughly 9.6 bits per item — orders of magnitude less than storing the items themselves.

Real-world uses include: Google Bigtable and Apache Cassandra (avoid disk lookups for missing keys), web browsers (Chrome Safe Browsing — check URLs against a blocklist locally), spell checkers, CDN cache admission, and duplicate-URL filtering in crawlers.

---

## Flowcharts

### Problem Recognition: When to Use a Bloom Filter

```mermaid
graph TD
    A["Need fast membership test?"]:::decision -->|No| B["Use different structure"]:::output
    A -->|Yes| C["Can tolerate false positives?"]:::decision
    C -->|No| D["Use exact data structure:<br/>hash set, B-tree, etc."]:::output
    C -->|Yes| E["Is memory a<br/>critical constraint?"]:::decision
    E -->|No| F["Use hash set or<br/>hash table"]:::output
    E -->|Yes| G["Will data be static or<br/>rarely updated?"]:::decision
    G -->|No| H["Use Counting Bloom Filter<br/>or other variant"]:::output
    G -->|Yes| I["Choose hash functions:<br/>independent, fast, uniform"]:::action
    I --> J["Calculate m and k<br/>from n and target p"]:::action
    J --> K["✓ Build Bloom Filter"]:::success
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef action fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef output fill:#50C878,stroke:#333,stroke-width:2px,color:#000
    classDef success fill:#50C878,stroke:#333,stroke-width:2px,color:#000
```

### Bloom Filter vs Alternatives Decision Tree

```mermaid
graph TD
    A["Select data structure<br/>for membership testing"]:::decision
    
    A --> B["Hash Set"]:::alt
    B --> B1["✓ O(1) avg search<br/>No false positives<br/>O(n) space<br/>Supports deletion"]:::altDetail
    
    A --> C["Bloom Filter"]:::alt
    C --> C1["✓ O(1) search<br/>Allows false positives<br/>O(m) space, m << n<br/>No deletion"]:::altDetail
    
    A --> D["Bit Array<br/>for small range"]:::alt
    D --> D1["✓ O(1) search<br/>No false positives<br/>Small space (range-limited)<br/>Fixed range only"]:::altDetail
    
    A --> E["Counting Bloom Filter"]:::alt
    E --> E1["✓ O(1) add/remove<br/>Allows false positives<br/>O(m·log(n)) space<br/>Counter overflow risk"]:::altDetail
    
    A --> F["Cuckoo Filter"]:::alt
    F --> F1["✓ O(1) avg<br/>Supports deletion<br/>Lower space than CBF<br/>Slightly complex"]:::altDetail
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef alt fill:#87CEEB,stroke:#333,stroke-width:2px,color:#000
    classDef altDetail fill:#E0F4FF,stroke:#333,stroke-width:1px,color:#000
```

### Hash Function Selection & False Positive Rate Analysis

```mermaid
graph TD
    A["Select hash functions<br/>for Bloom Filter"]:::decision
    
    A -->|Few hash calls needed| B["Use Double Hashing:<br/>h_i(x) = h1(x) + i·h2(x) mod m"]:::action
    B --> B1["✓ O(2) hash calls<br/>k independent hashes simulated<br/>Simple implementation"]:::success
    
    A -->|Maximum security| C["Use Independent Hash:<br/>MurmurHash3, xxHash, SipHash"]:::action
    C --> C1["✓ Truly independent<br/>Cryptographic strength<br/>Higher CPU cost"]:::success
    
    D["Calculate parameters<br/>from error budget"]:::action
    D --> E["Given: capacity n,<br/>target error p"]:::info
    E --> F["m = ⌈−n·ln(p)/ln²(2)⌉<br/>bits needed"]:::calc
    F --> G["k = ⌊m/n · ln(2)⌋<br/>hash functions"]:::calc
    G --> H["Verify: expected p<br/>= (1 − e^(-kn/m))^k"]:::verify
    H --> I["Capacity exceeded?"]:::decision
    I -->|Yes, adjust| J["Reduce p or increase m"]:::action
    I -->|No| K["✓ Proceed with insert"]:::success
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef action fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef info fill:#E0E0E0,stroke:#333,stroke-width:1px,color:#000
    classDef calc fill:#D0D0D0,stroke:#333,stroke-width:1px,color:#000
    classDef verify fill:#FFE0B2,stroke:#333,stroke-width:1px,color:#000
    classDef success fill:#50C878,stroke:#333,stroke-width:2px,color:#000
```

### Bloom Filter Operations: Insert vs Query vs Monitoring

```mermaid
graph TD
    A["Choose operation"]:::decision
    
    A -->|Add new item| B["insert(item)"]:::action
    B --> B1["Compute k hashes:<br/>h1(item), h2(item), ..., hk(item)"]:::step
    B1 --> B2["Set bits:<br/>bits[h_i] = 1 for all i"]:::step
    B2 --> B3["✓ Item added<br/>Bits are permanent"]:::success
    B3 --> B4["Warn: exceeding capacity<br/>increases false positive rate"]:::warning
    
    A -->|Check membership| C["contains(item)?"]:::action
    C --> C1["Compute k hashes"]:::step
    C1 --> C2{"All k bits<br/>are set?"}:::decision
    C2 -->|No| C3["✓ Definitely NOT in set<br/>False negative impossible"]:::success
    C2 -->|Yes| C4["✓ PROBABLY in set<br/>False positive possible"]:::warning
    C4 --> C5["Probability of false positive<br/>≈ (1 − e^(-kn/m))^k"]:::info
    
    A -->|Monitor quality| D["Analyze false positive rate"]:::action
    D --> D1["Count actual errors<br/>in production"]:::step
    D1 --> D2["Compare to formula<br/>estimate"]:::step
    D2 --> D3{"Formula p << actual?"}:::decision
    D3 -->|Yes| D4["⚠️ Hash function bias<br/>Consider rehashing"]:::warning
    D3 -->|No| D5["✓ Hashing is uniform"]:::success
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef action fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef step fill:#B0E0E6,stroke:#333,stroke-width:1px,color:#000
    classDef success fill:#50C878,stroke:#333,stroke-width:2px,color:#000
    classDef warning fill:#FF6B6B,stroke:#333,stroke-width:2px,color:#fff
    classDef info fill:#E0E0E0,stroke:#333,stroke-width:1px,color:#000
```

### Complexity & Optimization Tradeoff Analysis

```mermaid
graph TD
    A["Optimize for:<br/>space vs speed"]:::decision
    
    A -->|Minimize space| B["Goal: reduce m"]:::action
    B --> B1["Increase target error p"]:::step
    B1 --> B2["Formula: m ∝ −n·ln(p)"]:::calc
    B2 --> B3["Accept higher false<br/>positive rate"]:::tradeoff
    B3 --> B4["Use case: CDN cache,<br/>duplicate URL filter"]:::use
    
    A -->|Maximize accuracy| C["Goal: reduce p"]:::action
    C --> C1["Increase bits m"]:::step
    C1 --> C2["Formula: p ∝ e^(-kn/m)"]:::calc
    C2 --> C3["Higher memory cost"]:::tradeoff
    C3 --> C4["Use case: spam detection,<br/>authentication filter"]:::use
    
    A -->|Balance both| D["Choose m for target p<br/>given expected n"]:::action
    D --> D1["Typical: ~10 bits/item<br/>for 1% error"]:::guideline
    D1 --> D2["Space-time curve is smooth"]:::note
    D2 --> D3["Small parameter tweaks<br/>have gradual effects"]:::note
    
    E["Edge case: capacity<br/>exceeded (n > design n)"]:::warning
    E --> E1["False positive rate grows"]:::impact
    E1 --> E2["No data corruption<br/>but accuracy degrades"]:::note
    E2 --> E3["Monitor n; rebuild if<br/>n > 0.5·m/ln(2)"]:::recommend
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef action fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef step fill:#B0E0E6,stroke:#333,stroke-width:1px,color:#000
    classDef tradeoff fill:#FFE0B2,stroke:#333,stroke-width:1px,color:#000
    classDef use fill:#E0F4FF,stroke:#333,stroke-width:1px,color:#000
    classDef calc fill:#D0D0D0,stroke:#333,stroke-width:1px,color:#000
    classDef guideline fill:#F0F0F0,stroke:#333,stroke-width:1px,color:#000
    classDef note fill:#FFFFFF,stroke:#999,stroke-width:1px,color:#000
    classDef warning fill:#FF6B6B,stroke:#333,stroke-width:2px,color:#fff
    classDef impact fill:#FFCCCB,stroke:#333,stroke-width:1px,color:#000
    classDef recommend fill:#FFE0B2,stroke:#333,stroke-width:1px,color:#000
```

### Common Mistakes & Avoidance Strategies

```mermaid
graph TD
    A["Common Bloom Filter pitfalls"]:::warning
    
    A --> B["❌ Forgetting m and k<br/>must be computed at construction"]:::mistake
    B --> B1["Impact: wrong parameters<br/>lead to excessive false positives"]:::impact
    B1 --> B2["✓ Fix: compute m, k<br/>from n, p before building"]:::fix
    
    A --> C["❌ Using non-independent<br/>hash functions"]:::mistake
    C --> C1["Impact: k bits not<br/>uniformly distributed"]:::impact
    C1 --> C2["✓ Fix: use double hashing<br/>or cryptographic hash"]:::fix
    
    A --> D["❌ Trying to delete items<br/>by clearing bits"]:::mistake
    D --> D1["Impact: clears shared bits,<br/>corrupts other items"]:::impact
    D1 --> D2["✓ Fix: use Counting<br/>Bloom Filter variant"]:::fix
    
    A --> E["❌ Not resetting hash seed<br/>across process boundaries"]:::mistake
    E --> E1["Impact: PYTHONHASHSEED<br/>changes hash() output"]:::impact
    E1 --> E2["✓ Fix: use deterministic<br/>hash (MurmurHash3, xxHash)"]:::fix
    
    A --> F["❌ Exceeding designed<br/>capacity without monitoring"]:::mistake
    F --> F1["Impact: false positive rate<br/>increases exponentially"]:::impact
    F1 --> F2["✓ Fix: track n; warn/rebuild<br/>when n > threshold"]:::fix
    
    A --> G["❌ Assuming 'false' means<br/>definitely not present in queries"]:::mistake
    G --> G1["Impact: correct! But assuming<br/>'true' means definitely present is wrong"]:::note
    G1 --> G2["✓ Remember: contains()=true<br/>is probabilistic"]:::fix
    
    classDef warning fill:#FF6B6B,stroke:#333,stroke-width:2px,color:#fff
    classDef mistake fill:#FFB6C6,stroke:#333,stroke-width:2px,color:#000
    classDef impact fill:#FFCCCB,stroke:#333,stroke-width:1px,color:#000
    classDef fix fill:#90EE90,stroke:#333,stroke-width:2px,color:#000
    classDef note fill:#FFFFCC,stroke:#333,stroke-width:1px,color:#000
```

---

## ASCII Visualization

```
Bloom Filter: m=18 bits, k=3 hash functions

Bit array (index 0..17):
  index:  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17
  bits:   0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0

add("cat"):  h1("cat")=1, h2("cat")=5, h3("cat")=13
  bits:   0  1  0  0  0  1  0  0  0  0  0  0  0  1  0  0  0  0
                                                    ^
add("dog"):  h1("dog")=3, h2("dog")=5, h3("dog")=11
  bits:   0  1  0  1  0  1  0  0  0  0  0  1  0  1  0  0  0  0
                     ^  shared with "cat"

contains("cat")?  check bits 1,5,13 -> 1,1,1  -> PROBABLY YES  (correct)
contains("dog")?  check bits 3,5,11 -> 1,1,1  -> PROBABLY YES  (correct)
contains("fox")?  h1=1, h2=3, h3=11 -> 1,1,1  -> PROBABLY YES  (FALSE POSITIVE!)
contains("elk")?  h1=0, h2=7, h3=16 -> 0,0,0  -> DEFINITELY NO (correct)

No deletions are possible — clearing a shared bit would corrupt other items.
```

---

## Operations & Complexity

| Operation            | Average | Worst | Notes                                      |
|----------------------|---------|-------|--------------------------------------------|
| `add(item)`          | O(k)    | O(k)  | k hash computations + k bit sets           |
| `contains(item)`     | O(k)    | O(k)  | k hash computations + k bit reads          |
| `false_positive_rate`| O(1)    | O(1)  | Computed analytically from n, m, k         |
| Space                | O(m)    | O(m)  | m bits regardless of item size             |

- k is a small constant (typically 7–10 for p = 1%).
- All operations are effectively O(1) in practice.
- Deletion is not supported; use a Counting Bloom Filter variant for that.

---

## Key Invariants

- A bit, once set to 1, is **never cleared** — the filter is append-only.
- `contains` returning `False` is **definitive**: the item was never added.
- `contains` returning `True` is **probabilistic**: false positives occur with probability p.
- The false-positive rate only increases as more items are added beyond the design capacity.
- k hash functions must be **independent** (or nearly so via double hashing) to achieve the theoretical p.
- Double hashing `h_i(x) = (h1(x) + i·h2(x)) mod m` simulates k independent hash functions with only two underlying hash calls.

---

## Common Interview Questions

- **Why can't a Bloom Filter produce false negatives?** Once bits are set they stay set; if all k bits for an item are 1, either the item was added or other items happened to set those exact bits — but an item that was added always has its bits set.
- **How do you choose m and k given n and a target false-positive rate p?** Use `m = ⌈−n·ln(p)/(ln 2)²⌉` and `k = (m/n)·ln 2`. Be ready to derive or recall these formulas.
- **What happens when you exceed the design capacity?** The actual false-positive rate rises above the target; the filter degrades gracefully but never breaks.
- **How would you support deletions?** Use a Counting Bloom Filter: replace each bit with a small counter; decrement on delete. Risk: counter overflow can create false negatives.
- **Compare Bloom Filter vs hash set.** Bloom Filter uses O(m) bits vs O(n·item_size) for a hash set; Bloom Filter allows false positives and no deletions, but is far more memory-efficient for large n.
- **Where is a Bloom Filter used in a database engine?** As a pre-filter before a disk read: check the filter first; only perform the expensive I/O if the filter says "maybe present."

---

## Implementation Notes

- **Optimal m and k must be computed at construction time** from capacity and error_rate; changing them later requires rebuilding the filter from scratch.
- **Double hashing** `(h1 + i*h2) % m` requires h2 ≠ 0 and, when m is a power of 2, h2 must be odd to visit all positions (the implementation enforces `h2 = 1` if h2 would be 0).
- **Python's `hash()` is not deterministic across processes** (PYTHONHASHSEED); production implementations use deterministic hash families like MurmurHash3 or xxHash.
- The **bit array is backed by a `bytearray`** for memory efficiency; index arithmetic is `byte_idx, bit_idx = divmod(index, 8)`.
- **`count_set()` using `bin(byte).count('1')`** is a clean Pythonic popcount; for performance-critical code use `bin(byte).count('1')` on each byte or use a lookup table.
- The empirical `false_positive_rate()` formula `(1 − e^{−kn/m})^k` gives a slightly optimistic estimate because it assumes perfectly uniform hashing; actual rates may be slightly higher.

---

## References

- [Bloom, B. H. (1970). Space/time trade-offs in hash coding with allowable errors. CACM 13(7).](https://dl.acm.org/doi/10.1145/362686.362692)
- [Wikipedia — Bloom filter](https://en.wikipedia.org/wiki/Bloom_filter)
- [Broder, A. & Mitzenmacher, M. (2004). Network applications of Bloom filters: A survey. Internet Mathematics 1(4).](https://www.eecs.harvard.edu/~michaelm/postscripts/im2005b.pdf)
