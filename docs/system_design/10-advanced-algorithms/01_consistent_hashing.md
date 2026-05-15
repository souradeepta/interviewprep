# Consistent Hashing

## Problem Statement

Distributes data across nodes minimizing remapping on node addition/removal. Used in caching and NoSQL databases.

## Design

### Key Concepts

```
Hash ring with replica placement. Nodes placed at hash(node_id). Key hashed to nearest node clockwise.
```

### Architecture

```
[Visual representation showing architecture]
```

## Architecture Diagram

```
Ring with N nodes:
  Node 1 (0°) → handles keys 0-90
  Node 2 (90°) → handles keys 90-180
  Node 3 (180°) → handles keys 180-270
  Node 4 (270°) → handles keys 270-360
```

## Common Questions & Answers

**Q: How to handle node addition?** A: Only keys between new and previous node need remapping (~1/n).

**Q: Virtual nodes?** A: Each physical node maps to 150-200 virtual nodes. Better distribution.

**Q: Replication?** A: Place replicas at next k nodes clockwise. Tolerates k-1 failures.

## Back-of-Envelope Calculations

- 1000 nodes, 1B keys: remapping on node add = ~1M keys (0.1%)
- Search: O(log n) binary search on ring + hash = 50 ops
- Virtual nodes: 150 vnodes × 1000 = 150K ring positions

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Consistent hashing | Minimal remapping on node changes | More complex than modulo |
| Modulo hashing | Simple | Requires remapping >50% keys on change |
| Rendezvous hashing | No virtual nodes needed | More CPU expensive |

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
class ConsistentHash:
    def __init__(self, nodes=None, replicas=3):
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []
        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key):
        return hash(key) % (2**32)

    def add_node(self, node):
        for i in range(self.replicas):
            virtual_key = f"{node}:{i}"
            hash_key = self._hash(virtual_key)
            self.ring[hash_key] = node
        self.sorted_keys = sorted(self.ring.keys())

    def remove_node(self, node):
        for i in range(self.replicas):
            virtual_key = f"{node}:{i}"
            hash_key = self._hash(virtual_key)
            del self.ring[hash_key]
        self.sorted_keys = sorted(self.ring.keys())

    def get_node(self, key):
        if not self.ring:
            return None
        hash_key = self._hash(key)
        idx = bisect.bisect_left(self.sorted_keys, hash_key) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]
```

### Java Implementation

```java
class ConsistentHash {
    private final int replicas;
    private final Map<Long, String> ring = new HashMap<>();
    private final SortedMap<Long, String> sortedRing = new TreeMap<>();

    public ConsistentHash(List<String> nodes, int replicas) {
        this.replicas = replicas;
        nodes.forEach(this::addNode);
    }

    private long hash(String key) {
        return Math.abs((long)key.hashCode());
    }

    public void addNode(String node) {
        for (int i = 0; i < replicas; i++) {
            long hash = hash(node + ":" + i);
            ring.put(hash, node);
            sortedRing.put(hash, node);
        }
    }

    public String getNode(String key) {
        if (ring.isEmpty()) return null;
        long hash = hash(key);
        SortedMap<Long, String> tail = sortedRing.tailMap(hash);
        long nodeKey = tail.isEmpty() ? sortedRing.firstKey() : tail.firstKey();
        return sortedRing.get(nodeKey);
    }
}
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
