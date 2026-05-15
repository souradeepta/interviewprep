# Template Method Pattern

## Problem Statement

Defines algorithm skeleton in base class, letting subclasses override specific steps.

## Design

### Key Concepts

```
Base class defines algorithm steps. Subclasses override specific steps.
```

### Architecture

```
[Visual representation showing architecture]
```

## Architecture Diagram

```
BaseClass.templateMethod():
  step1() [concrete]
  step2() [abstract]
  step3() [concrete]
Subclass overrides step2()
```

## Common Questions & Answers

**Q: vs Strategy?** A: Template: inheritance, compile-time. Strategy: composition, runtime.

**Q: Inversion of control?** A: Framework calls subclass methods.

## Back-of-Envelope Calculations

- Reduces code duplication: 30-50% less code
- Performance: 0% overhead

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Template Method | Code reuse, inversion of control | Tight coupling |
| Strategy pattern | Runtime flexibility | More classes |
| Inheritance | Simple | Tight coupling, fragile base |

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
