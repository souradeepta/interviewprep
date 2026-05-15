# LFU Cache

A cache eviction policy that always discards the item accessed the fewest number of times, using LRU order to break ties among equally-frequent items.

---

## Overview

An LFU (Least Frequently Used) Cache tracks an access count for every cached item. When capacity is reached and a new item must be inserted, the item with the lowest access frequency is evicted. If multiple items share the minimum frequency, the least recently used among them is removed (LRU tiebreaking), making the policy fully deterministic.

The key engineering challenge is achieving O(1) get and put. A naive approach scans all items to find the minimum frequency in O(n). The optimal solution uses three coordinated data structures: a key→node map for O(1) lookup, a frequency→doubly-linked-list map where each list holds all nodes at that frequency in LRU order, and a single `min_freq` integer maintained in O(1). When a node's frequency increases it is moved from bucket f to bucket f+1; when bucket f becomes empty and f == min_freq, min_freq is incremented. A new insert always resets min_freq to 1.

LFU suits workloads with stable popularity distributions — CDN caches, DNS caches, database buffer pools for hot pages — where repeatedly-accessed items should survive eviction much longer than one-hit wonders. LRU is generally preferred when recency is a better predictor of future access than historical frequency.

---

## Flowcharts

### Problem Recognition: When to Use LFU Cache

```mermaid
graph TD
    A["Need a cache with<br/>eviction policy?"]:::decision -->|No| B["Use in-memory store"]:::output
    A -->|Yes| C["What drives future<br/>access patterns?"]:::decision
    C -->|Recent items matter| D["Use LRU Cache"]:::output
    C -->|Frequency matters| E["Are all items equally<br/>sized in cost?"]:::decision
    E -->|No| F["Use Weighted LFU<br/>or cost-aware variant"]:::output
    E -->|Yes| G["Will access patterns<br/>shift over time?"]:::decision
    G -->|Yes, items age| H["Use LFUDA or LRU<br/>with frequency decay"]:::output
    G -->|Relatively stable| I["✓ LFU Cache is ideal"]:::success
    I --> J["Choose tiebreaker:<br/>LRU for equal frequency"]:::action
    J --> K["Build three structures:<br/>key→val, freq→list, min_freq"]:::action
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef action fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef output fill:#50C878,stroke:#333,stroke-width:2px,color:#000
    classDef success fill:#50C878,stroke:#333,stroke-width:2px,color:#000
```

### LFU vs LRU vs LRU-2 Decision Tree

```mermaid
graph TD
    A["Cache eviction<br/>strategy"]:::decision
    
    A --> B["LRU<br/>Least Recently Used"]:::alt
    B --> B1["✓ Evict by access time<br/>O(1) with doubly linked list<br/>Simple implementation<br/>Good for time-based access"]:::altDetail
    B2["⚠️ One-time full scan<br/>pollutes cache"]
    B --> B2
    
    A --> C["LFU<br/>Least Frequently Used"]:::alt
    C --> C1["✓ Evict by usage count<br/>O(1) with freq buckets<br/>Resists scans<br/>Complex implementation"]:::altDetail
    C2["⚠️ Frequency stale over time"]
    C --> C2
    
    A --> D["LRU-2<br/>Two-touch eviction"]:::alt
    D --> D1["✓ Track two most recent<br/>Good balance of simplicity<br/>Handles scans better"]:::altDetail
    D2["⚠️ Not true LFU behavior"]
    D --> D2
    
    A --> E["Clock Replacement"]:::alt
    E --> E1["✓ Approximate LRU<br/>Very low memory<br/>O(1) amortized"]:::altDetail
    
    A --> F["Adaptive: LFU + Recency"]:::alt
    F --> F1["✓ Hybrid frequency + time<br/>Best for shifting patterns<br/>Most complex"]:::altDetail
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef alt fill:#87CEEB,stroke:#333,stroke-width:2px,color:#000
    classDef altDetail fill:#E0F4FF,stroke:#333,stroke-width:1px,color:#000
```

### LFU Cache: Insert vs Update vs Eviction Decision

```mermaid
graph TD
    A["LFU Operation"]:::decision
    
    A -->|put(key, val)| B{Key exists?}:::decision
    B -->|No| C["Check capacity"]:::step
    C -->|Available slot| C1["freq=1, reset min_freq=1"]:::action
    C1 --> C2["Insert at freq=1 bucket<br/>MRU end"]:::action
    C2 --> C3["✓ new item added"]:::success
    C -->|Full| C4["Evict from min_freq<br/>LRU position"]:::action
    C4 --> C5["Remove LRU node from<br/>freq_map[min_freq]"]:::action
    C5 --> C6{"freq bucket<br/>empty now?"}:::decision
    C6 -->|Yes, was min_freq| C7["increment min_freq"]:::action
    C6 -->|No| C8["No change"]:::note
    C7 --> C9["Insert new item<br/>at freq=1"]:::action
    C9 --> C3
    
    B -->|Yes| D["Update value"]:::action
    D --> D1["Increment frequency<br/>from f to f+1"]:::action
    D1 --> D2["Move node from<br/>freq_map[f] to freq_map[f+1]"]:::action
    D2 --> D3["Append to MRU end<br/>of new bucket"]:::action
    D3 --> D4{"Was bucket f<br/>now empty?"}:::decision
    D4 -->|Yes, was min_freq| D5["increment min_freq"]:::action
    D4 -->|No| D6["No change"]:::note
    D5 --> D7["✓ node updated & promoted"]:::success
    D6 --> D7
    
    A -->|get(key)| E["Lookup in key_map"]:::action
    E --> E1{"Key found?"}:::decision
    E1 -->|No| E2["Return nil"]:::output
    E1 -->|Yes| E3["Same as put-update:<br/>promote to f+1"]:::action
    E3 --> E4["✓ value returned,<br/>frequency incremented"]:::success
    
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef action fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef step fill:#B0E0E6,stroke:#333,stroke-width:1px,color:#000
    classDef note fill:#FFFFFF,stroke:#999,stroke-width:1px,color:#000
    classDef output fill:#D3D3D3,stroke:#333,stroke-width:1px,color:#000
    classDef success fill:#50C878,stroke:#333,stroke-width:2px,color:#000
```

### Frequency Bucket Management: min_freq Transitions

```mermaid
graph TD
    A["LFU state:<br/>freq buckets + min_freq"]:::info
    
    A --> B["Scenario 1:<br/>new item inserted"]:::scenario
    B --> B1["min_freq is set to 1"]:::action
    B1 --> B2["New node added to<br/>freq_map[1]"]:::action
    B2 --> B3["old min_freq is ignored"]:::note
    B3 --> B4["✓ After eviction cycle<br/>min_freq resets to 1"]:::success
    
    A --> C["Scenario 2:<br/>node promoted f → f+1"]:::scenario
    C --> C1["Remove from freq_map[f]"]:::action
    C1 --> C2["Add to freq_map[f+1]"]:::action
    C2 --> C3{"Is freq_map[f]<br/>now empty<br/>AND f == min_freq?"}:::decision
    C3 -->|Yes| C4["Increment min_freq<br/>to f+1"]:::action
    C3 -->|No| C5["No change to min_freq"]:::note
    C4 --> C6["✓ promotion complete"]:::success
    C5 --> C6
    
    A --> D["Scenario 3:<br/>frequency gap created"]:::scenario
    D --> D1["Example: min_freq=3,<br/>only freq-3 node exists"]:::example
    D1 --> D2["Promote that node to<br/>freq=4"]:::action
    D2 --> D3["freq-3 bucket now empty"]:::result
    D3 --> D4["Update min_freq=4<br/>jump over gap"]:::action
    D4 --> D5["✓ Efficient: no scan needed"]:::note
    
    classDef info fill:#E0E0E0,stroke:#333,stroke-width:2px,color:#000
    classDef scenario fill:#FFE0B2,stroke:#333,stroke-width:2px,color:#000
    classDef action fill:#4A90E2,stroke:#333,stroke-width:2px,color:#fff
    classDef decision fill:#FFA500,stroke:#333,stroke-width:2px,color:#000
    classDef note fill:#FFFFFF,stroke:#999,stroke-width:1px,color:#000
    classDef example fill:#F0F0F0,stroke:#999,stroke-width:1px,color:#000
    classDef result fill:#FFFACD,stroke:#999,stroke-width:1px,color:#000
    classDef success fill:#50C878,stroke:#333,stroke-width:2px,color:#000
```

### Complexity Analysis: O(1) Implementation Requirements

```mermaid
graph TD
    A["Achieve O(1) get and put<br/>for LFU cache"]:::goal
    
    A --> B["Data Structure 1:<br/>key → (value, frequency)"]:::struct
    B --> B1["HashMap (dict in Python)"]:::impl
    B1 --> B2["✓ O(1) lookup/update"]:::benefit
    
    A --> C["Data Structure 2:<br/>frequency → bucket"]:::struct
    C --> C1["HashMap of doubly linked lists"]:::impl
    C1 --> C2["Bucket = DLinkedList<br/>of (key,val) nodes<br/>in LRU order"]:::detail
    C2 --> C3["✓ O(1) node insertion/removal"]:::benefit
    C2 --> C4["✓ O(1) min-frequency find"]:::benefit
    
    A --> D["Data Structure 3:<br/>min_freq counter"]:::struct
    D --> D1["Single integer"]:::impl
    D1 --> D2["✓ O(1) read/update"]:::benefit
    
    E["Key insight:<br/>no linear scan ever needed"]:::insight
    E --> E1["Do NOT search for<br/>minimum frequency"]:::antipattern
    E1 --> E2["min_freq automatically<br/>maintained by bucket<br/>topology"]:::mechanism
    
    F["Cost breakdown"]:::cost
    F --> F1["put new: 1 insert"]:::op
    F --> F2["put update: 1 remove<br/>+ 1 insert"]:::op
    F --> F3["get: 1 lookup<br/>+ 1 remove + 1 insert"]:::op
    F --> F4["eviction: O(1) by<br/>accessing freq_map[min_freq]<br/>tail pointer"]:::op
    
    classDef goal fill:#ffd699,color:#000,stroke:#333,stroke-width:2px,stroke:#333,stroke-width:3px,color:#000
    classDef struct fill:#87CEEB,stroke:#333,stroke-width:2px,color:#000
    classDef impl fill:#B0E0E6,stroke:#333,stroke-width:1px,color:#000
    classDef detail fill:#E0F4FF,stroke:#333,stroke-width:1px,color:#000
    classDef benefit fill:#90ee90,color:#000,stroke:#333,stroke-width:2px,stroke:#333,stroke-width:1px,color:#000
    classDef insight fill:#FFE0B2,stroke:#333,stroke-width:2px,color:#000
    classDef antipattern fill:#FF6B6B,stroke:#333,stroke-width:2px,color:#fff
    classDef mechanism fill:#FFFACD,stroke:#333,stroke-width:1px,color:#000
    classDef cost fill:#F0F8FF,stroke:#333,stroke-width:2px,color:#000
    classDef op fill:#E0F4FF,stroke:#333,stroke-width:1px,color:#000
```

### Common Mistakes & Implementation Pitfalls

```mermaid
graph TD
    A["Common LFU implementation bugs"]:::warning
    
    A --> B["❌ Forgetting to reset<br/>min_freq = 1 on eviction"]:::mistake
    B --> B1["Impact: next insert fails<br/>can't find capacity"]:::impact
    B1 --> B2["✓ Fix: always set min_freq=1<br/>after inserting new key"]:::fix
    
    A --> C["❌ Not cleaning up empty<br/>frequency buckets"]:::mistake
    C --> C1["Impact: memory bloat;<br/>buckets stay allocated"]:::impact
    C1 --> C2["✓ Fix: explicitly check<br/>and remove/skip empty"]:::fix
    
    A --> D["❌ Using incorrect<br/>LRU tiebreaker order"]:::mistake
    D --> D1["Impact: wrong node evicted;<br/>test case failure"]:::impact
    D1 --> D2["✓ Fix: always evict<br/>LRU (oldest) of min_freq"]:::fix
    
    A --> E["❌ Scanning all keys<br/>to find min frequency"]:::mistake
    E --> E1["Impact: O(n) put,<br/>defeats LFU purpose"]:::impact
    E1 --> E2["✓ Fix: use min_freq<br/>counter + bucket structure"]:::fix
    
    A --> F["❌ Not handling<br/>capacity=0 or capacity=1"]:::mistake
    F --> F1["Impact: edge case failures"]:::impact
    F1 --> F2["✓ Fix: guard with<br/>capacity validation"]:::fix
    
    A --> G["❌ Updating frequency<br/>without moving node"]:::mistake
    G --> G1["Impact: LRU order broken;<br/>wrong node evicted"]:::impact
    G1 --> G2["✓ Fix: always move node<br/>from old bucket to new"]:::fix
    
    classDef warning fill:#FF6B6B,stroke:#333,stroke-width:2px,color:#fff
    classDef mistake fill:#FFB6C6,stroke:#333,stroke-width:2px,color:#000
    classDef impact fill:#FFCCCB,stroke:#333,stroke-width:1px,color:#000
    classDef fix fill:#90ee90,color:#000,stroke:#333,stroke-width:2px,stroke:#333,stroke-width:2px,color:#000
```

---

## ASCII Visualization

```
LFU Cache, capacity=3.  State after: put(A), put(B), put(C), get(A), get(A), get(B)

freq_map:
  freq=1 -> [C]                     (C is LRU victim if eviction needed)
  freq=2 -> [B]
  freq=3 -> [A]

  min_freq = 1   (always tracks the smallest occupied frequency bucket)

key_map:   A->(val_a, freq=3)   B->(val_b, freq=2)   C->(val_c, freq=1)

Each freq bucket is a doubly linked list (head <-> nodes <-> tail):

freq=1 bucket:    [HEAD] <-> [C, freq=1] <-> [TAIL]
                              ^ LRU end (evict from here)

freq=2 bucket:    [HEAD] <-> [B, freq=2] <-> [TAIL]

Now put(D) triggers eviction (capacity=3, all slots taken):
  1. Evict from freq_map[min_freq=1] -> remove C (LRU of freq-1 bucket)
  2. Insert D with freq=1, reset min_freq=1

freq_map after:
  freq=1 -> [D]
  freq=2 -> [B]
  freq=3 -> [A]

Tiebreaking example (two items at min_freq):
  freq=1 -> [HEAD] <-> [X] <-> [Y] <-> [TAIL]
             LRU end ^                   ^ MRU end
  Eviction removes X (arrived/accessed earlier)
```

---

## Operations & Complexity

| Operation | Average | Worst | Notes                                               |
|-----------|---------|-------|-----------------------------------------------------|
| `get(key)`| O(1)    | O(1)  | Lookup in key_map + move node to freq+1 bucket      |
| `put(key, val)` | O(1) | O(1) | Insert at freq=1 or update + promote existing key |
| Space     | O(n)    | O(n)  | n = capacity; freq buckets together hold n nodes    |

- O(1) requires the doubly linked list + min_freq trick (LFUCacheOptimal).
- A simpler implementation using Counter + OrderedDict achieves O(1) get but O(n) put due to minimum-frequency scan.

---

## Key Invariants

- Every key in `key_map` is in **exactly one** frequency bucket in `freq_map`.
- `min_freq` always equals the smallest frequency with a non-empty bucket.
- When a new item is inserted, `min_freq` is reset to **1** — the new item always has the lowest possible frequency.
- When `freq_map[f]` becomes empty and `f == min_freq`, `min_freq` is incremented to `f+1`.
- Within each frequency bucket, nodes are maintained in **LRU order**: the head side is the oldest (eviction candidate), the tail side is the most recently accessed.
- Accessing a node (get or put-update) moves it from bucket `f` to bucket `f+1` and appends it at the MRU end of the new bucket.

---

## Common Interview Questions

- **What is the difference between LRU and LFU eviction?** LRU evicts the item not accessed for the longest time (recency); LFU evicts the item accessed the fewest total times (frequency). LFU is more resistant to one-time scans polluting the cache.
- **How do you achieve O(1) get and put for LFU?** Three structures: key→node hashmap, freq→DLinkedList hashmap, and a `min_freq` counter. Moving a node between frequency buckets and updating `min_freq` are both O(1).
- **When does LFU degrade in practice?** When access patterns shift over time: an item popular long ago accumulates high frequency and is unfairly protected even after its usefulness expires (frequency aging problem). Solutions include frequency decay or LFUDA (LFU with Dynamic Aging).
- **What is the LRU tiebreaking rule and why does it matter?** Among all items at `min_freq`, the least recently used is evicted. Without this rule, eviction would be non-deterministic and could fail LeetCode 460 test cases.
- **Implement LFU cache** (LeetCode 460) — the canonical interview problem. Must handle capacity=1 edge case and the min_freq reset on every new insertion.
- **Compare LFU to LRU implementation complexity.** LRU needs one doubly linked list + one hashmap; LFU needs two hashmaps + per-frequency doubly linked lists + min_freq tracking — significantly more complex.

---

## Implementation Notes

- **min_freq reset on insert**: every new key starts at frequency 1, so `min_freq = 1` after any eviction+insert cycle. Forgetting this reset is the most common bug.
- **Empty bucket cleanup**: after removing a node from `freq_map[f]`, check if the bucket is empty. If so and `f == min_freq`, increment `min_freq`. Do not delete empty buckets eagerly when using `defaultdict` — they will be recreated on the next access to that frequency.
- **OrderedDict as ordered set**: `freq_map[f][key] = None` uses the OrderedDict purely for its insertion-order `popitem(last=False)` behavior, not for stored values. This is the pattern used by LFUCacheSimple.
- **Sentinel nodes in doubly linked list**: the `_FreqBucket` uses head/tail sentinel nodes so that `append` and `remove` never need null checks — every real node has valid `prev` and `next` pointers.
- **Capacity=0 edge case**: the constructor rejects non-positive capacity with a `ValueError`; LeetCode's variant uses capacity=0 to mean all puts are no-ops.
- **Duplicate puts**: calling `put(key, val)` for an existing key must update the value and increment its frequency — treat it as a "get + update", not as a new insert.

---

## References

- [LeetCode 460 — LFU Cache (problem statement and constraints)](https://leetcode.com/problems/lfu-cache/)
- [Wikipedia — Cache replacement policies — LFU](https://en.wikipedia.org/wiki/Cache_replacement_policies#Least-frequently_used_(LFU))
- [Einziger, G. & Friedman, R. (2014). TinyLFU: A Highly Efficient Cache Admission Policy. IEEE Transactions on Storage.](https://arxiv.org/abs/1512.00727)
