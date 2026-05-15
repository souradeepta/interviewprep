# LinkedIn Job/Connection Recommendations

## Problem Statement

650M+ users, ML-based recommendations, job search, feed personalization.

## Design

### Key Concepts

```
User profile → feature vector → nearest neighbors (ANN) → rank → serve.
```

### Architecture

```
[Visual representation showing architecture]
```

## Architecture Diagram

```
User features → embedding → ANN search → Ranker → recommendations
```

## Common Questions & Answers

**Q: Cold start users?** A: Content-based filtering with user attributes.

**Q: Freshness?** A: Update daily or weekly. Real-time for very popular.

## Back-of-Envelope Calculations

- 900M users, 5 recommendation requests/user/month = 3.75B recs/month
- Feature vector: 256 dimensions = 256KB for 900M users = 200GB

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Collaborative filtering | Captures preferences | Cold start problem |
| Content-based | Works for cold start | Less sophisticated |
| Hybrid | Best of both | More complex |

## Follow-up Interview Questions

1. How would you implement this at scale (1M+ operations/sec)?
2. What happens if the [key component] fails?
3. How to ensure [important property] in this system?
4. What's the bottleneck at 10x current scale?
5. How would you monitor and debug [specific aspect]?

## Example Scenario Walkthrough

Scenario: [Concrete example with 5-10 steps showing system in action]

## Flow Diagram

```mermaid
flowchart TD
    A["Training Phase"] --> B["Build User-Item Matrix"]
    B --> C["SVD Factorization"]
    C --> D["Get User/Item Vectors"]
    D --> E["Store in Cache"]

    F["Serving Phase"] --> G["Get User Vector"]
    G --> H["Compute Similarity"]
    H --> I["Score All Items"]
    I --> J["Top-K"]
    J --> K["Filter & Rank"]
```

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
