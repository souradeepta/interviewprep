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

## Edge Cases

1. Capacity = 1
2. Multiple items with same frequency
3. Eviction when all items same frequency (evict LRU)
4. Update existing key
