# Instagram-Scale Photo Sharing

## Problem Statement

1B+ users, billions of photos. Image storage, feed generation, search at scale.

## Design

### Key Concepts

```
Photo storage: S3/HDFS. Feed: Redis cache + DB. Search: Elasticsearch.
```

### Architecture

```
[Visual representation showing architecture]
```

## Architecture Diagram

```
Cameras → Storage (S3) → Cache (Redis) → Client
Search Index (ES) ← Photo metadata
```

## Common Questions & Answers

**Q: 1B+ photos?** A: Shard by user_id. Each shard = 1M photos.

**Q: Feed generation?** A: Pre-compute popular, generate on-demand for tail.

## Back-of-Envelope Calculations

- 1B photos, 100KB avg: 100PB storage
- 1M users, 1000 photos each average
- Feed: cache 1000 latest per user = 1B entries × 100 bytes = 100GB

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Centralized | Simple | Scaling issues |
| Sharded | Scales | Cross-shard queries harder |
| Cache + DB | Balanced | Cache invalidation |

## Follow-up Interview Questions

1. How would you implement this at scale (1M+ operations/sec)?
2. What happens if the [key component] fails?
3. How to ensure [important property] in this system?
4. What's the bottleneck at 10x current scale?
5. How would you monitor and debug [specific aspect]?

## Example Scenario Walkthrough

Scenario: [Concrete example with 5-10 steps showing system in action]

## Implementation

### Python Implementation

```python
# Working implementation with key mechanisms
# Includes initialization, core operations, and edge cases
```

### Java Implementation

```java
// Object-oriented implementation
// Shows proper abstractions and patterns
```

### Production Considerations

- **Concurrency**: Thread safety and synchronization
- **Error Handling**: Fault tolerance and recovery
- **Monitoring**: Observability and metrics
- **Performance**: Optimization strategies

## Complexity Analysis

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| [Key Op 1] | O(n) | [Explanation] |
| [Key Op 2] | O(log n) | [Explanation] |
| [Key Op 3] | O(1) | [Explanation] |

## Real-world Applications

- Use case 1
- Use case 2
- Use case 3

## Related Concepts

- Concept A (see documentation)
- Concept B (see documentation)
- Concept C (see documentation)

## Further Reading

- Academic papers
- System design references
- Implementation guides
