# 01. Caching Systems

Learn fundamental caching strategies and eviction policies essential for all systems.

## Problems

### 1. LRU Cache
**Problem**: Implement a cache with Least Recently Used eviction policy.

**Key Concepts**:
- Doubly linked list for O(1) removal and re-insertion
- HashMap for O(1) lookups
- Move accessed items to front (most recent)
- Evict from tail (least recent)

**Complexity**: O(1) for get/put, O(capacity) space

**Real-world Use**: Redis eviction, browser caches, CPU L1/L2/L3 caches

### 2. LFU Cache
**Problem**: Implement a cache with Least Frequently Used eviction policy.

**Key Concepts**:
- Track frequency count for each key
- When capacity exceeded, evict minimum frequency key
- Tie-breaking: evict oldest among same frequency
- Min-frequency pointer optimization

**Complexity**: O(1) for get/put, O(capacity) space

**Real-world Use**: Adaptive caching, intelligent memory management

## Learning Outcomes

After studying these problems, you should understand:
1. ✅ How caching improves system performance
2. ✅ Different eviction policies and their trade-offs
3. ✅ Data structure selection (linked lists, hash maps)
4. ✅ How to implement efficient cache operations
5. ✅ Scaling considerations for large caches

## Implementation Pattern

Both caches follow this pattern:
```
User Request
    ↓
Cache Check → Hit (return, move to recent)
    ↓
Cache Miss → DB Query (load, add to cache, evict if full)
    ↓
Response
```

## Scalability Considerations

| Aspect | LRU | LFU |
|--------|-----|-----|
| Memory | O(n) | O(n) + freq tracking |
| Hit Rate | Good for temporal locality | Better for temporal + frequency |
| Eviction Cost | O(1) | O(1) |
| Production | Redis (default) | Adaptive scenarios |

## Next Steps

- Study the code implementations in detail
- Implement from scratch without looking at solutions
- Optimize for specific access patterns
- Move to **Core Algorithms** for more complex problems
