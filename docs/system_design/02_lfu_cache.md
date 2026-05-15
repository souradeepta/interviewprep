# LFU Cache

## Problem Statement

Implement an LFU (Least Frequently Used) Cache with fixed capacity. When capacity is exceeded, evict the least frequently used item. Break ties using LRU (least recently used among items with same frequency).

**Operations:**
- `get(key)` — return value, increment frequency
- `put(key, value)` — insert/update, evict LFU+LRU if over capacity

**Constraints:**
- Both operations must be O(1)
- Frequency tracked per key
- Ties broken by recency

## Architecture Diagram

```
┌──────────────────────────────────────┐
│     LFU Cache (capacity=3)           │
├──────────────────────────────────────┤
│  freq_map: {key -> frequency}        │
│  {1: 3, 2: 1, 3: 2}                  │
├──────────────────────────────────────┤
│  freq_list: {freq -> keys (ordered)} │
│  {1: [2], 2: [3], 3: [1]}            │
├──────────────────────────────────────┤
│  min_freq: 1 (track minimum)         │
└──────────────────────────────────────┘
```

## Design

### Data Structures

```
freq_map: {key -> freq}        (track frequency per key)
freq_list: {freq -> OrderedDict of keys}  (keys with each frequency, ordered by recency)
min_freq: int                   (current minimum frequency)
```

**Why:**
- `freq_map` gives O(1) frequency lookup
- `freq_list` allows O(1) LFU+LRU eviction
- OrderedDict preserves insertion order (most recent at end)

### Key Operations

```
GET(key):
  - Increment freq[key]
  - Move key from freq_list[old_freq] to freq_list[new_freq]
  - If freq_list[old_freq] empty and old_freq == min_freq: min_freq++
  - Return value

PUT(key, value):
  - If over capacity: evict from freq_list[min_freq][0] (oldest)
  - Insert/update with freq=1, set min_freq=1
```

### Complexity

| Operation | Time | Space |
|-----------|------|-------|
| get | O(1) | — |
| put | O(1) | — |
| Space | — | O(capacity) |

## Common Questions & Answers

**Q: Why track both freq and freq_list?**
A: freq_map gives O(1) lookup. freq_list gives O(1) min eviction. Combined = O(1) all ops.

**Q: What if multiple keys have same frequency?**
A: Store in OrderedDict. Evict from front (oldest = least recently used).

**Q: How does min_freq optimization help?**
A: Don't scan all frequencies. min_freq always points to eviction target.

**Q: LFU vs LRU - when to use?**
A: LFU better for predictable workloads. LRU better for unknown patterns.

## Back-of-Envelope Calculations

Cache 10K items, frequency distribution (80% access 1 time, 20% access 5+ times):
- Storage: 10K × (8 + 8 + overhead) = 160KB + overhead
- Access distribution: 8K items freq=1, 2K items freq=5+
- On eviction: Remove from 8K pool (LFU)
- Hit rate with distribution: ~70% (2K items get 80% traffic)

## Design Choices

| Approach | Pros | Cons |
|----------|------|------|
| HashMap + FreqList | O(1) all ops | Complex state |
| Heap + HashMap | Simple | O(log n) update |
| Array of queues | Memory efficient | Hash collisions |

## Follow-up Questions

1. Tie-breaking: how to break LFU ties? (LRU, FIFO, random)
2. Frequency overflow: what if frequency exceeds int? (modulo, reset periodically)
3. Access pattern: what if 90% requests to single item? (still works, freq increases)
4. Eviction cost: O(1) - but what about freq_list cleanup?
5. Why not just use frequency count? (need to know which key is LFU = need ordering)

## Example Walkthrough

Sequence: put(1,1), put(2,2), get(1), put(3,3), put(4,4), get(1), evict?

```
put(1,1): Cache={1:1}, freq={1:1}, freq_list={1:[1]}, min_freq=1
put(2,2): Cache={1:1,2:2}, freq={1:1,2:1}, freq_list={1:[1,2]}, min_freq=1
get(1): freq={1:0,2:1}, freq_list={1:[2],2:[1]}, min_freq=1
put(3,3): Cache full, evict key with freq=1 (tie=2), freq={1:1,2:1,3:1}
put(4,4): Cache full, evict 1 from freq=1, freq={2:1,3:1,4:1}
get(1): Miss! Evicted. freq_list={1:[3,4,2]}
```

## Trade-offs

| Trade-off | Option A | Option B |
|-----------|----------|----------|
| Accuracy vs Speed | Perfect LFU (O(log n)) | Approximate LFU (O(1)) |
| Memory | Freq histogram | Full freq_list |
| Tie-breaking | LRU (complex) | FIFO (simple) |

## Real-World Use Cases

- Database indices (hot data)
- CDN edge caches (popular content)
- CPU cache (predicted reuse)
- Memory allocation (frequently used pages)
- Recommendation systems (popular items)
