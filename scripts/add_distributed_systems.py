#!/usr/bin/env python3
"""
Add 20 distributed systems concepts to system design documentation.
"""

import os

base_path = "/home/sbisw/github/interviewprep/docs/system_design/04-distributed-systems"

# 20 New distributed systems concepts
distributed_systems = {
    "14_distributed_caching": {
        "title": "Distributed Caching",
        "description": "Redis Cluster: sharded caching across multiple nodes with replication and failover."
    },
    "15_service_discovery": {
        "title": "Service Discovery",
        "description": "Dynamic service registration and discovery (Consul, Eureka) for microservices."
    },
    "16_distributed_locking": {
        "title": "Distributed Locking",
        "description": "Mutex, semaphores, and lock management across multiple servers."
    },
    "17_vector_clocks": {
        "title": "Vector Clocks",
        "description": "Logical clocks for ordering events in distributed systems without synchronized clocks."
    },
    "18_quorum_systems": {
        "title": "Quorum-based Systems",
        "description": "Voting-based consensus for reads and writes in distributed databases."
    },
    "19_read_repair": {
        "title": "Read Repair & Anti-entropy",
        "description": "Techniques for detecting and fixing data inconsistencies in distributed systems."
    },
    "20_bloom_filters": {
        "title": "Bloom Filters",
        "description": "Probabilistic data structure for membership testing with minimal memory."
    },
    "21_skip_lists": {
        "title": "Skip Lists",
        "description": "Probabilistic alternative to balanced trees for sorted data."
    },
    "22_merkle_trees": {
        "title": "Merkle Trees",
        "description": "Hash tree structure for efficient data synchronization and verification."
    },
    "23_gossip_protocol": {
        "title": "Gossip Protocol",
        "description": "Peer-to-peer information propagation for eventual consistency."
    },
    "24_crdt": {
        "title": "CRDT (Conflict-free Replicated Data Type)",
        "description": "Data structures that converge without coordination in distributed systems."
    },
    "25_distributed_config_management": {
        "title": "Distributed Configuration Management",
        "description": "Centralized config distribution and versioning (Zookeeper, etcd, Consul)."
    },
    "26_leader_election": {
        "title": "Leader Election",
        "description": "Algorithms for selecting a coordinator in distributed systems."
    },
    "27_heartbeat_failure_detection": {
        "title": "Heartbeat & Failure Detection",
        "description": "Detecting node failures through periodic health checks."
    },
    "28_cascading_failures": {
        "title": "Cascading Failures & Bulkheads",
        "description": "Preventing failure propagation through isolation and resource limits."
    },
    "29_distributed_tracing": {
        "title": "Distributed Tracing",
        "description": "Request tracing across services (OpenTelemetry, Jaeger, Zipkin)."
    },
    "30_monitoring_alerting": {
        "title": "Monitoring & Alerting Systems",
        "description": "Observability stack for distributed systems (Prometheus, Grafana)."
    },
    "31_load_shedding": {
        "title": "Load Shedding & Backpressure",
        "description": "Graceful degradation and flow control under overload."
    },
    "32_hinted_handoff": {
        "title": "Hinted Handoff",
        "description": "Temporary data storage during node unavailability in Dynamo-style systems."
    },
    "33_gossip_failure_detection": {
        "title": "Accrual Failure Detector",
        "description": "Adaptive failure detection using historical health data (Cassandra)."
    }
}

def create_ds_concept(num, concept_id, title, description):
    """Create a distributed systems concept document."""

    content = f"""# {title}

## Problem Statement

{description}

## Design

### Key Concepts

```
Core Mechanism:
- How this system works
- Key components and interactions
- Data flow and processing
```

### Architecture

```
[Visual representation showing architecture]
```

## Architecture Diagram

```
[Visual system components and interactions]
```

## Common Questions & Answers

**Q: When to use this approach?**
A: [Specific use cases and scenarios where this is beneficial]

**Q: What are the key trade-offs?**
A: [Pros and cons of this approach vs alternatives]

**Q: How does this handle failures?**
A: [Failure scenarios and recovery mechanisms]

**Q: How to scale this?**
A: [Scaling strategies and bottlenecks]

## Back-of-Envelope Calculations

For typical distributed system scenario:
- Performance metrics
- Scalability limits
- Resource requirements
- Typical deployment sizes

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Option A | [Advantages] | [Disadvantages] |
| Option B | [Advantages] | [Disadvantages] |
| Option C | [Advantages] | [Disadvantages] |

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
"""

    return content

# Create all documents
for i, (concept_id, details) in enumerate(distributed_systems.items(), start=14):
    filepath = os.path.join(base_path, f"{concept_id}.md")
    content = create_ds_concept(i, concept_id, details["title"], details["description"])

    with open(filepath, 'w') as f:
        f.write(content)

    print(f"✓ Created {concept_id}.md")

print(f"\n✅ Created 20 new distributed systems concept documents")
