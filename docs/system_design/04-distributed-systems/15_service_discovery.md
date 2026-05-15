# Service Discovery

## Problem Statement

Dynamic service registration and discovery (Consul, Eureka) for microservices.

## Design

### Key Concepts

```
Centralized registry with client polling or server-side discovery via LB.
```

### Architecture

```
[Visual representation showing architecture]
```

## Architecture Diagram

```
[['Consul', 'Full service mesh', 'Complex'], ['Eureka', 'Simple, Netflix proven', 'Less features'], ['etcd + custom', 'Lightweight, flexible', 'DIY responsibility']]
```

## Common Questions & Answers

**Q: Health check frequency?** A: 10-30 second intervals. Balance between detection time and load.

**Q: TTL for entries?** A: 30s-5m. Prevents stale registrations.

**Q: Client-side vs server-side?** A: Client: flexible, complex. Server: centralized, simpler.

**Q: Consistency?** A: Eventual consistency acceptable.

## Back-of-Envelope Calculations

1000 services, 10K service instances. Registry: ~10MB (1K per entry). Queries: 100K/sec.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Consul | Service mesh, HA, consul UI | Complex setup, resource overhead |
| Eureka | Netflix-proven, simple | Eventual consistency only |
| etcd+custom | Lightweight, flexible | More DIY work |

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
