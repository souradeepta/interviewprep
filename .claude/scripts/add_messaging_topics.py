#!/usr/bin/env python3
"""
Script to add 30 more comprehensive messaging and streaming topics to 18-messaging-streaming.
Topics include brokers, protocols, patterns, and real-world implementations.
"""

from pathlib import Path

# New messaging and streaming topics (11-40)
new_topics = {
    11: {
        "name": "RabbitMQ Advanced Patterns",
        "description": "Advanced RabbitMQ patterns: message routing, dead-letter exchanges, priority queues, TTL, lazy queues.",
        "sections": [
            "Routing Topologies",
            "Exchange Types (Direct, Fanout, Topic, Headers)",
            "Dead-Letter Exchanges and Queues",
            "Priority Queues",
            "Message TTL and Queue TTL",
            "Lazy Queues for Large Messages",
            "Clustering and High Availability",
            "Consumer Prefetch and Flow Control"
        ]
    },
    12: {
        "name": "Redis Streams",
        "description": "Using Redis Streams for event streaming: data structure, consumer groups, trimming strategies.",
        "sections": [
            "Stream Data Structure",
            "Consumer Groups",
            "Stream Trimming Strategies",
            "Message Acknowledgment",
            "Claimed Messages",
            "Persistence with RDB/AOF",
            "Performance Optimization",
            "Use Cases: Activity Feeds, Real-time Logs"
        ]
    },
    13: {
        "name": "Google Cloud Pub/Sub",
        "description": "GCP Pub/Sub: push vs pull delivery, subscriptions, ordering, exactly-once processing.",
        "sections": [
            "Publisher-Subscriber Model",
            "Push vs Pull Delivery",
            "Subscription Types",
            "Message Ordering",
            "Exactly-Once Delivery Semantics",
            "Retention Policies",
            "Dead-Letter Topics",
            "Integration with BigQuery and Dataflow"
        ]
    },
    14: {
        "name": "AWS Kinesis Streams",
        "description": "AWS Kinesis: shards, partition keys, DynamoDB for state, enhanced fan-out.",
        "sections": [
            "Kinesis Data Streams Architecture",
            "Sharding and Partition Keys",
            "GetRecords vs EnhancedFanOut",
            "State Management with DynamoDB",
            "Batch Processing vs Real-time",
            "Resharding Strategies",
            "Monitoring with CloudWatch",
            "Kinesis vs Kafka Trade-offs"
        ]
    },
    15: {
        "name": "MQTT Protocol and IoT",
        "description": "MQTT protocol for IoT: publish-subscribe, QoS levels, retained messages, last will.",
        "sections": [
            "MQTT Protocol Basics",
            "QoS Levels (0, 1, 2)",
            "Retained Messages",
            "Last Will Testament",
            "Topic Wildcards and Filters",
            "Keep-Alive and Heartbeat",
            "Message Broker (Mosquitto, HiveMQ)",
            "IoT Use Cases"
        ]
    },
    16: {
        "name": "AMQP Advanced Messaging",
        "description": "AMQP protocol: message queuing standard, vs MQTT, broker implementations.",
        "sections": [
            "AMQP Protocol Specification",
            "Message Format and Headers",
            "Queue Declaration and Binding",
            "Transactions vs Confirmations",
            "Resource Management",
            "Flow Control",
            "Security (SSL/TLS, SASL)",
            "Comparing MQTT, AMQP, STOMP"
        ]
    },
    17: {
        "name": "gRPC Streaming",
        "description": "gRPC bidirectional streaming: server push, client streaming, flow control, deadlines.",
        "sections": [
            "gRPC Streaming Types",
            "Server Push Streams",
            "Client Streaming",
            "Bidirectional Streaming",
            "Back-Pressure Handling",
            "Deadlines and Timeouts",
            "Stream Cancellation",
            "Use Cases: Real-time Updates, Multiplexing"
        ]
    },
    18: {
        "name": "Idempotency in Messaging",
        "description": "Ensuring idempotency: deduplication, idempotency keys, request IDs, idempotency maps.",
        "sections": [
            "Idempotency Definitions",
            "Idempotency Keys",
            "Request ID Tracking",
            "Deduplication Windows",
            "State Store Patterns",
            "Hash-based Deduplication",
            "Time-limited Deduplication",
            "Exactly-Once Semantics Implementation"
        ]
    },
    19: {
        "name": "Message Batching and Aggregation",
        "description": "Batching strategies for throughput: linger time, batch size, compression, aggregation windows.",
        "sections": [
            "Batching Benefits and Trade-offs",
            "Linger Time Configuration",
            "Batch Size Optimization",
            "Compression Algorithms",
            "Aggregation Windows",
            "Windowing Functions",
            "Micro-batching vs True Batching",
            "Performance Impact"
        ]
    },
    20: {
        "name": "Backpressure and Flow Control",
        "description": "Handling backpressure: slow consumers, circuit breakers, buffer management.",
        "sections": [
            "Backpressure Definition",
            "Detection Mechanisms",
            "Slow Consumer Handling",
            "Circuit Breaker Pattern",
            "Buffer Overflow Strategies",
            "Graceful Degradation",
            "Rate Limiting",
            "Resource Exhaustion Prevention"
        ]
    },
    21: {
        "name": "Message Ordering Guarantees",
        "description": "Ordering semantics: per-partition, per-key, global ordering, consistency.",
        "sections": [
            "Ordering Levels",
            "Per-Partition Ordering",
            "Per-Key Ordering",
            "Global Ordering Costs",
            "Deterministic Reordering",
            "Out-of-Order Detection",
            "Session Windows",
            "Trade-offs with Throughput"
        ]
    },
    22: {
        "name": "Message Transformations",
        "description": "Stream processing: filtering, mapping, enrichment, stateless transformations.",
        "sections": [
            "Stateless Transformations",
            "Filtering and Projection",
            "Enrichment Patterns",
            "Serialization Formats (JSON, Avro, Protobuf)",
            "Schema Evolution",
            "Field Masking and Encryption",
            "Compression and Decompression",
            "Complex Object Transformations"
        ]
    },
    23: {
        "name": "Stateful Stream Processing",
        "description": "Stream state management: aggregations, joins, windowing, state backends.",
        "sections": [
            "State Stores",
            "Aggregations and Reductions",
            "Stream-Stream Joins",
            "Stream-Table Joins",
            "Windowing (Tumbling, Sliding, Session)",
            "State Checkpointing",
            "State TTL and Cleanup",
            "Consistency in Distributed State"
        ]
    },
    24: {
        "name": "Changelog Streams and Compaction",
        "description": "Kafka log compaction: changelog topics, event sourcing, state reconstruction.",
        "sections": [
            "Log Compaction Architecture",
            "Cleaner Policy Configuration",
            "Changelog Topics",
            "Head/Tail Versioning",
            "Retention Policies",
            "Compaction Triggers",
            "State Reconstruction",
            "Event Sourcing Patterns"
        ]
    },
    25: {
        "name": "Messaging System Monitoring",
        "description": "Monitoring messaging systems: lag, throughput, latency, system health.",
        "sections": [
            "Consumer Lag Metrics",
            "Lag Alerting",
            "Throughput Monitoring",
            "Latency Percentiles",
            "Error Rate Tracking",
            "Message Skew Detection",
            "Consumer Rebalancing Metrics",
            "Dashboard Design"
        ]
    },
    26: {
        "name": "Multi-Tenancy in Messaging",
        "description": "Isolating tenants: topic naming, RBAC, quota management, resource isolation.",
        "sections": [
            "Tenant Isolation Strategies",
            "Topic Naming Conventions",
            "Role-Based Access Control",
            "Quota Management",
            "Resource Limits per Tenant",
            "Cost Allocation",
            "Cross-Tenant Monitoring",
            "Blast Radius Containment"
        ]
    },
    27: {
        "name": "Disaster Recovery for Messaging",
        "description": "Disaster recovery: backup strategies, failover, multi-region replication.",
        "sections": [
            "Backup Strategies",
            "Point-in-Time Recovery",
            "Multi-Region Replication",
            "Active-Active Setup",
            "Failover Procedures",
            "RTO and RPO Targets",
            "Data Validation After Recovery",
            "Testing Recovery Plans"
        ]
    },
    28: {
        "name": "Schema Registry and Schema Evolution",
        "description": "Schema management: registry, versioning, compatibility, schema validation.",
        "sections": [
            "Schema Registry Architecture",
            "Schema Versioning",
            "Compatibility Modes (Backward, Forward, Full)",
            "Avro and Protobuf Schema",
            "Schema Validation",
            "Breaking Changes Detection",
            "Migration Strategies",
            "Schema Documentation"
        ]
    },
    29: {
        "name": "Exactly-Once Semantics (EOS)",
        "description": "Guaranteeing exactly-once: transactions, deduplication, idempotency.",
        "sections": [
            "Delivery Semantics (At-Most, At-Least, Exactly-Once)",
            "Kafka Transactions",
            "Transactional ID",
            "Isolation Levels",
            "Deduplication Semantics",
            "Exactly-Once in Distributed Systems",
            "Performance Overhead",
            "Use Case Analysis"
        ]
    },
    30: {
        "name": "Message Deduplication Strategies",
        "description": "Deduplication: in-memory maps, external stores, bloom filters, windowing.",
        "sections": [
            "Deduplication Approaches",
            "Memory-Based Deduplication",
            "External Store (Redis, Cache)",
            "Bloom Filters for Deduplication",
            "Sliding Window Deduplication",
            "Time-Based Windows",
            "Scalability Considerations",
            "False Positive Management"
        ]
    },
    31: {
        "name": "Kafka Connect and Integration",
        "description": "Kafka Connect: source/sink connectors, distributed workers, offset management.",
        "sections": [
            "Kafka Connect Architecture",
            "Source Connectors",
            "Sink Connectors",
            "Connector Configuration",
            "Standalone vs Distributed Mode",
            "Worker Management",
            "Offset and State Management",
            "Connector Ecosystem (Debezium, JDBC, S3, etc.)"
        ]
    },
    32: {
        "name": "Change Data Capture (CDC)",
        "description": "CDC patterns: log-based, query-based, event-based, database replication.",
        "sections": [
            "CDC Definition and Approaches",
            "Log-Based CDC (PostgreSQL WAL, MySQL binlog)",
            "Query-Based CDC",
            "Event-Based CDC",
            "Debezium for CDC",
            "CDC Latency and Consistency",
            "Handling Deletes and Schema Changes",
            "Data Warehouse Sync"
        ]
    },
    33: {
        "name": "Real-time Analytics with Streaming",
        "description": "Streaming analytics: aggregations, windowed metrics, real-time dashboards.",
        "sections": [
            "Real-time Metrics Collection",
            "Time-Windowed Aggregations",
            "Percentile Calculations",
            "Cardinality Estimation",
            "Approximate Algorithms",
            "Real-time Dashboard Updates",
            "Latency vs Accuracy Trade-offs",
            "Tools: Flink, Spark, Kafka Streams"
        ]
    },
    34: {
        "name": "Distributed Tracing in Messaging",
        "description": "Distributed tracing: trace context propagation, end-to-end latency, debugging.",
        "sections": [
            "Trace Context Propagation",
            "W3C Trace Context",
            "Message Header Injection",
            "Span Creation",
            "Correlation IDs",
            "End-to-End Latency Tracking",
            "Debugging Failed Messages",
            "Tools: Jaeger, Zipkin, X-Ray"
        ]
    },
    35: {
        "name": "Circuit Breakers for Messaging",
        "description": "Circuit breaker pattern: detecting failures, fallbacks, recovery strategies.",
        "sections": [
            "Circuit Breaker States",
            "Failure Detection",
            "Threshold Configuration",
            "Half-Open State Testing",
            "Fallback Mechanisms",
            "Cascading Failures Prevention",
            "Exponential Backoff",
            "Integration with Messaging Systems"
        ]
    },
    36: {
        "name": "Geo-Distributed Messaging",
        "description": "Multi-region messaging: replication, latency, consistency, failover.",
        "sections": [
            "Multi-Region Architectures",
            "Cross-Region Replication",
            "Latency Optimization",
            "Consistency Models (Strong, Eventual)",
            "Conflict Resolution",
            "Region Failover",
            "Data Residency Compliance",
            "Cost Optimization"
        ]
    },
    37: {
        "name": "Message Expiration and TTL",
        "description": "Message lifecycle: TTL, expiration, cleanup, time-based retention.",
        "sections": [
            "TTL Definition",
            "Per-Message TTL",
            "Queue-Level TTL",
            "Expired Message Handling",
            "Dead-Letter Queue Integration",
            "Cleanup Strategies",
            "Storage Optimization",
            "Configuring Retention Policies"
        ]
    },
    38: {
        "name": "Performance Tuning for Brokers",
        "description": "Optimizing broker performance: compression, batching, hardware, JVM tuning.",
        "sections": [
            "Broker Resource Allocation",
            "CPU and Memory Optimization",
            "Disk I/O Tuning",
            "Network Bandwidth",
            "Compression Algorithm Selection",
            "Batch Size Configuration",
            "JVM Tuning (Kafka, RabbitMQ)",
            "Benchmarking and Profiling"
        ]
    },
    39: {
        "name": "Consumer Lag and Catchup",
        "description": "Managing consumer lag: lag calculation, acceleration, replay, skip.",
        "sections": [
            "Lag Calculation Methods",
            "Lag Monitoring",
            "Slow Consumer Detection",
            "Lag Alerting Thresholds",
            "Message Replay",
            "Partition Reassignment",
            "Parallel Consumption",
            "Message Skipping Strategies"
        ]
    },
    40: {
        "name": "Transactional Outbox Pattern",
        "description": "Outbox pattern: dual writes, consistency, exactly-once delivery guarantee.",
        "sections": [
            "Outbox Pattern Definition",
            "Database Outbox Table",
            "Polling Strategies",
            "CDC-Based Polling",
            "Exactly-Once Delivery",
            "Deduplication in Outbox",
            "Failure Scenarios",
            "Applications: Order Processing, Event Publishing"
        ]
    }
}

def generate_topic_file(topic_num, topic_info):
    """Generate markdown content for a messaging topic."""

    name = topic_info["name"]
    description = topic_info["description"]
    sections = topic_info["sections"]

    sections_md = "\n".join([f"### {section}\n\n[Content to be developed]\n" for section in sections])

    content = f"""# {name}

## Overview

{description}

## Key Concepts

- **Purpose:** [Define the purpose and use case]
- **When to Use:** [When this pattern/technology is applicable]
- **Tradeoffs:** [Performance vs consistency, complexity, etc.]
- **Complexity:** Intermediate to Advanced

## Architecture

```
[ASCII diagram or architecture description]
```

## Core Concepts

{sections_md}

## Best Practices

1. **Design Consideration 1:** [Details]
2. **Design Consideration 2:** [Details]
3. **Design Consideration 3:** [Details]
4. **Design Consideration 4:** [Details]
5. **Design Consideration 5:** [Details]

## Common Patterns

### Pattern 1

[Description and code example]

### Pattern 2

[Description and code example]

### Pattern 3

[Description and code example]

## Comparison with Alternatives

| Aspect | {name} | Alternative 1 | Alternative 2 |
|--------|-----------|---------------|---------------|
| Latency | - | - | - |
| Throughput | - | - | - |
| Complexity | - | - | - |
| Consistency | - | - | - |
| Cost | - | - | - |

## Implementation Example

### Scenario: [Real-world Use Case]

**Requirements:**
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

**Solution:**
```
[Code or architecture solution]
```

**Metrics:**
- Latency: [Target]
- Throughput: [Target]
- Availability: [Target]

## Performance Considerations

### Throughput Optimization

[Optimization strategies]

### Latency Reduction

[Optimization strategies]

### Resource Management

[Resource allocation guidance]

## Monitoring and Observability

### Key Metrics

- **Metric 1:** [Definition and threshold]
- **Metric 2:** [Definition and threshold]
- **Metric 3:** [Definition and threshold]

### Alerting

- Alert on [condition]
- Alert on [condition]
- Alert on [condition]

## Troubleshooting

### Issue 1: [Common Problem]

**Symptoms:** [What to look for]

**Root Causes:**
- [Cause 1]
- [Cause 2]

**Solutions:**
- [Solution 1]
- [Solution 2]

### Issue 2: [Common Problem]

[Same structure]

## Real-World Examples

### Example 1: [Company/Use Case]

[Description of how this system/pattern is used]

### Example 2: [Company/Use Case]

[Description of how this system/pattern is used]

### Example 3: [Company/Use Case]

[Description of how this system/pattern is used]

## Interview Questions

1. **Design Question:** [Question about designing a system using this pattern]
2. **Tradeoff Question:** [Question about tradeoffs]
3. **Implementation Question:** [Question about implementation details]
4. **Scaling Question:** [Question about scaling considerations]
5. **Failure Handling:** [Question about handling failures]

## Further Reading

- **Official Documentation:** [Link]
- **Research Papers:** [Link]
- **Blog Posts:** [Link]
- **Video Tutorials:** [Link]

---

**Difficulty:** Intermediate
**Time to Master:** 3-4 weeks
**Prerequisite Knowledge:** Messaging basics, distributed systems fundamentals
**Common in Interviews:** Yes - Medium to Hard problems
"""

    return content

def main():
    """Generate and save new messaging topics."""
    base_path = Path("docs/system_design/18-messaging-streaming")

    if not base_path.exists():
        print(f"❌ Directory not found: {base_path}")
        return

    print(f"📨 Adding 30 new messaging topics (11-40)...")
    print("=" * 60)

    success_count = 0
    for num, info in new_topics.items():
        filename = f"{num:02d}_{info['name'].lower().replace(' ', '_')}.md"
        filepath = base_path / filename

        # Skip if already exists
        if filepath.exists():
            print(f"⏭️  Already exists: {info['name']}")
            continue

        try:
            content = generate_topic_file(num, info)
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"✅ Created: {info['name']}")
            success_count += 1
        except Exception as e:
            print(f"❌ Error creating {info['name']}: {e}")

    print("=" * 60)
    print(f"✨ Added {success_count} new messaging topics!")
    print(f"\nTotal topics: 40 (original 10 + 30 new)")
    print(f"\nCoverage:")
    print(f"  - Message Brokers: RabbitMQ, Redis, Kafka, AWS, GCP")
    print(f"  - Protocols: MQTT, AMQP, gRPC streaming")
    print(f"  - Patterns: Idempotency, Deduplication, CDC, Outbox")
    print(f"  - Stream Processing: Stateful ops, Windowing, Joins")
    print(f"  - Operations: Monitoring, Disaster Recovery, Multi-region")
    print(f"  - Advanced: EOS, Schema Registry, Circuit Breakers")

if __name__ == '__main__':
    main()
