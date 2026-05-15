# LRU Cache

## Problem Statement

Implement an LRU (Least Recently Used) Cache with fixed capacity. When capacity is exceeded, evict the least recently used item.

**Operations:**
- `get(key)` — return value, mark as recently used
- `put(key, value)` — insert/update, evict LRU if over capacity

**Constraints:**
- Both operations must be O(1)
- Capacity is fixed
- Track access order, not insertion order

## Design

### Data Structures

```
Doubly Linked List (tracks order)
    head <-> Node1 <-> Node2 <-> Node3 <-> tail
    |most recent            least recent|

HashMap (for O(1) lookup)
    {key -> Node*}
```

**Why this works:**
- Doubly linked list maintains insertion/access order
- Removing node from middle and adding to front = O(1) with pointers
- HashMap gives O(1) access to node

### Key Operations

```
GET(3):
Before: 1 <-> 2 <-> 3 <-> 4
After:  1 <-> 2 <-> 4 <-> 3  (3 moves to front = most recent)

PUT(5) with capacity=4:
Before: 1 <-> 2 <-> 4 <-> 3
After:  2 <-> 4 <-> 3 <-> 5  (evict 1, add 5 at front)
```

### Complexity

| Operation | Time | Space |
|-----------|------|-------|
| get | O(1) | — |
| put | O(1) | — |
| Space | — | O(capacity) |

## Trade-offs

| Approach | Pros | Cons |
|----------|------|------|
| Doubly LL + HashMap | O(1) all ops, simple | More memory overhead per node |
| OrderedDict (Python) | Built-in, clean | Language-specific |
| Single LL + HashMap | Less memory | O(n) to find/remove node |

## Edge Cases

1. Capacity = 1: only one item at a time
2. Duplicate keys: update value, move to front
3. Access pattern: get should update recency
4. Empty cache: get returns None/null
