# Accrual Failure Detector

## Problem Statement

Adaptive failure detection using historical health data (Cassandra).

## Design

### Key Concepts

```
Track heartbeat history. Compute probability of failure rather than binary decision.
```

### Architecture

```
[Visual representation showing architecture]
```

## Architecture Diagram

```
Heartbeat intervals: [500ms, 450ms, 480ms, 550ms, ...]
Variance: low = consistent
Missing interval: 1s instead of 500ms
Probability of failure: 95% (configurable threshold)
```

## Common Questions & Answers

**Q: vs fixed timeout?** A: Adapts to network jitter. False positive rate < 5% configurable.

**Q: Algorithm?** A: Phi accrual detector. Gaussian distribution of intervals.

**Q: Threshold tuning?** A: Phi = 1 (90% confident dead), Phi = 2 (99% confident).

**Q: Recovery?** A: Reset on heartbeat received.

## Back-of-Envelope Calculations

- Heartbeat interval: 1 second nominal
- Network jitter: 50ms std dev
- P95 interval: 1.08 seconds
- Detection with Phi=2: requires ~3 missing intervals
- False positive rate: <1% with correct tuning

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Accrual detector | Adaptive, fewer false positives | More complex |
| Fixed timeout | Simple | Prone to false positives |
| Multiple independent detectors | Voting | Overkill for most |
| Gossip-based detection | Decentralized | Slower consensus |

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
