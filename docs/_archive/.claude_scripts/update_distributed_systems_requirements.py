#!/usr/bin/env python3
"""
Update distributed systems topics with specific functional/non-functional requirements
and other detailed content sections instead of generic placeholders.
"""

from pathlib import Path
import re

# Topic-specific requirements and content
TOPIC_DETAILS = {
    "11_pub_sub_system": {
        "functional": [
            "Publish messages to topics with multiple subscribers",
            "Guarantee message delivery to all active subscribers",
            "Support topic filtering and pattern-based subscriptions",
            "Handle subscription/unsubscription dynamically",
            "Maintain message ordering within a topic partition"
        ],
        "non_functional": [
            "Throughput: 1M+ messages/sec per broker",
            "Latency: < 10ms p99 message delivery",
            "Durability: At-least-once delivery guarantee",
            "Scalability: Support millions of subscribers globally",
            "Availability: 99.99% uptime with automatic failover"
        ]
    },
    "12_thread_pool": {
        "functional": [
            "Accept tasks and execute asynchronously",
            "Maintain configurable number of worker threads",
            "Queue tasks when all workers are busy",
            "Support task cancellation and timeout",
            "Provide work-stealing for load balancing"
        ],
        "non_functional": [
            "Throughput: Handle 100K+ tasks/sec",
            "Latency: Queue/dequeue in microseconds",
            "Memory: Bounded queue to prevent OOM",
            "Scalability: CPU cores × 2-4 workers",
            "Fairness: No thread starvation or deadlock"
        ]
    },
    "13_load_balancer": {
        "functional": [
            "Distribute incoming requests across multiple backend servers",
            "Support multiple load balancing algorithms (RR, LB, consistent hash)",
            "Health check backends and remove unhealthy ones",
            "Route requests based on path, hostname, or protocol",
            "Maintain persistent connections (sticky sessions when needed)"
        ],
        "non_functional": [
            "Throughput: 1M+ RPS per load balancer",
            "Latency: < 5ms p99 routing decision",
            "Availability: 99.999% uptime across regions",
            "Scalability: Support 10K+ backend servers",
            "Consistency: No request loss during failover"
        ]
    },
    "14_distributed_caching": {
        "functional": [
            "Store key-value pairs in distributed cache across nodes",
            "Retrieve values with TTL/expiration support",
            "Invalidate cache entries on demand or by pattern",
            "Support atomic operations (CAS, increment)",
            "Replicate cache entries for fault tolerance"
        ],
        "non_functional": [
            "Latency: < 1ms p99 for cache hits",
            "Throughput: 10M+ operations/sec",
            "Hit rate: 80%+ on typical workloads",
            "Durability: Configurable persistence to disk",
            "Scalability: Terabytes of data across clusters"
        ]
    },
    "15_service_discovery": {
        "functional": [
            "Register new service instances and their metadata",
            "Deregister instances gracefully or on failure",
            "Query services by name and get healthy instances",
            "Support health checks and automatic removal of unhealthy nodes",
            "Propagate service changes to all clients in real-time"
        ],
        "non_functional": [
            "Availability: 99.99% service registry uptime",
            "Latency: < 100ms for service discovery queries",
            "Consistency: Eventual consistency across replicas",
            "Scalability: Support 10K+ services and 100K+ instances",
            "Durability: Persist service registry data"
        ]
    },
    "16_distributed_locking": {
        "functional": [
            "Acquire exclusive locks on shared resources",
            "Support lock timeout and automatic release",
            "Enable multiple readers with exclusive writer (RWLock)",
            "Prevent deadlocks with timeout and detection",
            "Reentrant locks for same client multiple acquisitions"
        ],
        "non_functional": [
            "Lock acquisition latency: < 10ms p99",
            "Throughput: 100K+ lock operations/sec",
            "Fairness: FIFO ordering prevents starvation",
            "Durability: Survive coordinator restarts",
            "Scalability: Support millions of locks"
        ]
    },
    "17_vector_clocks": {
        "functional": [
            "Track causality relationships between events",
            "Determine partial order of events across processes",
            "Detect concurrent events (no causality relationship)",
            "Merge clocks for information flow analysis",
            "Reconstruct event ordering for debugging"
        ],
        "non_functional": [
            "Storage: O(n) space per event (n = number of processes)",
            "Comparison: O(n) time for causality check",
            "Scalability: Feasible for < 100 processes",
            "Accuracy: Correct causality detection",
            "Overhead: Minimal impact on system performance"
        ]
    },
    "18_quorum_systems": {
        "functional": [
            "Read from quorum of replicas for consistency",
            "Write to quorum of replicas for durability",
            "Support variable quorum sizes (W + R > N)",
            "Handle read repair to update stale replicas",
            "Consistent read-after-write within session"
        ],
        "non_functional": [
            "Consistency: Strong consistency with quorum reads/writes",
            "Availability: Tolerate up to N - ceil(N/2) failures",
            "Latency: p99 latency = max(quorum response times)",
            "Throughput: Quorum parallelism vs serialization",
            "Network: Reduce replica count to save bandwidth"
        ]
    },
    "19_read_repair": {
        "functional": [
            "Detect stale values during read operations",
            "Automatically update stale replicas in background",
            "Merge replica values using vector clocks",
            "Return latest value to client immediately",
            "Repair consistency without user intervention"
        ],
        "non_functional": [
            "Latency: Read operation unaffected by repair",
            "Consistency: Eventual consistency achieved asynchronously",
            "Throughput: Background repairs don't impact reads",
            "Overhead: Extra network requests to lagging replicas",
            "Scalability: Works with many replicas"
        ]
    },
    "20_bloom_filters": {
        "functional": [
            "Check set membership with small false positive rate",
            "Add elements to the filter structure",
            "Support multiple hash functions for distributed data",
            "Count approximate set cardinality (HyperLogLog)",
            "Merge filters from different partitions"
        ],
        "non_functional": [
            "Space: O(n) bits for n elements",
            "Time: O(k) hash computations per lookup",
            "False positives: Configurable p < 1%",
            "Accuracy: Deterministic membership guarantee",
            "Distribution: Partition filters across nodes"
        ]
    },
    "21_skip_lists": {
        "functional": [
            "Store sorted elements with efficient search",
            "Insert/delete/search in O(log n) average time",
            "Range queries on consecutive elements",
            "Iterate elements in sorted order",
            "Support concurrent access with fine-grained locks"
        ],
        "non_functional": [
            "Complexity: O(log n) expected for operations",
            "Space: O(n) with small constant factors",
            "Concurrency: Lock-free or fine-grained locking",
            "Cache locality: Better than balanced trees",
            "Simplicity: Easier to implement than AVL/RB trees"
        ]
    },
    "22_merkle_trees": {
        "functional": [
            "Verify data integrity across partitions",
            "Efficiently reconcile divergent replicas",
            "Identify specific corrupted data blocks",
            "Support incremental synchronization",
            "Detect unauthorized data modification"
        ],
        "non_functional": [
            "Verification: O(log n) hashes to verify n items",
            "Sync: Minimize data transfer during reconciliation",
            "Storage: 2n hashes for n leaf nodes",
            "Computation: O(n log n) to build tree",
            "Throughput: Constant time updates with caching"
        ]
    },
    "23_gossip_protocol": {
        "functional": [
            "Disseminate information probabilistically",
            "Achieve eventual consistency asynchronously",
            "Detect node failures through gossip",
            "Repair corrupted data lazily",
            "Support eventual deletion of data (tombstones)"
        ],
        "non_functional": [
            "Latency: O(log n) rounds to reach all nodes",
            "Availability: Tolerates arbitrary node failures",
            "Consistency: Eventual after O(log n) rounds",
            "Bandwidth: O(log n) messages per node per round",
            "Simplicity: No central coordinator needed"
        ]
    },
    "24_crdt": {
        "functional": [
            "Merge replicas without coordination",
            "Achieve strong eventual consistency",
            "Support offline-first concurrent edits",
            "Commutative operations on any replica order",
            "Preserve user intent in collaborative editing"
        ],
        "non_functional": [
            "Consistency: Strong eventual consistency",
            "Availability: Works offline, syncs later",
            "Latency: Sub-millisecond local operations",
            "Space: Unbounded growth with deletions (tombstones)",
            "Throughput: Merge complexity varies by CRDT type"
        ]
    },
    "25_distributed_config_management": {
        "functional": [
            "Centralized configuration for all services",
            "Push configuration updates in real-time",
            "Support versioning and rollback",
            "Environment-specific configuration overrides",
            "Audit trail of all configuration changes"
        ],
        "non_functional": [
            "Availability: 99.99% config service uptime",
            "Latency: < 10ms to fetch config",
            "Consistency: Read-after-write within service",
            "Scalability: Support 10K+ services",
            "Security: Encrypt sensitive values"
        ]
    },
    "26_leader_election": {
        "functional": [
            "Elect single leader among distributed nodes",
            "Detect leader failure and trigger re-election",
            "Provide leaderless operations during transition",
            "Support safe leader stepdown",
            "Guarantee only one active leader at a time"
        ],
        "non_functional": [
            "Latency: Complete election in < 5 seconds",
            "Safety: No split-brain or multiple leaders",
            "Liveness: Leader elected eventually",
            "Consistency: State consistent across replicas",
            "Scalability: O(log n) election complexity"
        ]
    },
    "27_heartbeat_failure_detection": {
        "functional": [
            "Periodic heartbeats from nodes to detector",
            "Detect failure when heartbeats stop",
            "Reduce false positives with adaptive timeouts",
            "Support different failure models (fail-stop, crash)",
            "Report failure to monitoring and recovery systems"
        ],
        "non_functional": [
            "Detection latency: 3-5 heartbeat intervals",
            "False positive rate: < 0.1% under normal conditions",
            "Overhead: Minimal heartbeat bandwidth",
            "Scalability: O(n) messages for n nodes",
            "Accuracy: Tolerate network jitter and delays"
        ]
    },
    "28_cascading_failures": {
        "functional": [
            "Detect when single failure triggers chain reaction",
            "Isolate failed component using circuit breaker",
            "Shed load to prevent system overload",
            "Graceful degradation with reduced capacity",
            "Automatic recovery when conditions improve"
        ],
        "non_functional": [
            "Detection: < 10 seconds to identify cascade",
            "Recovery: Restart failed service in < 30 seconds",
            "Availability: Partial availability maintained",
            "Impact: Limit blast radius to single component",
            "Automation: Minimal manual intervention needed"
        ]
    },
    "29_distributed_tracing": {
        "functional": [
            "Trace request flow across microservices",
            "Correlate logs using trace IDs",
            "Identify performance bottlenecks",
            "Visualize service dependencies",
            "Support sampling to reduce overhead"
        ],
        "non_functional": [
            "Overhead: < 5% performance impact",
            "Latency: Tracing information available within 5 seconds",
            "Storage: 1KB per trace event",
            "Throughput: Support 1M+ trace events/sec",
            "Queryability: Support complex trace queries"
        ]
    },
    "30_monitoring_alerting": {
        "functional": [
            "Collect metrics from all system components",
            "Define alert rules based on metric thresholds",
            "Send notifications (email, Slack, PagerDuty)",
            "Track alert history and status changes",
            "Support alert silencing and escalation"
        ],
        "non_functional": [
            "Alert latency: < 30 seconds from condition to notification",
            "Metrics collection: 1-minute granularity",
            "Storage: Compress metrics for long-term retention",
            "Availability: Monitoring survives component failures",
            "Scalability: Monitor 10K+ metrics across 1000s of services"
        ]
    },
    "31_load_shedding": {
        "functional": [
            "Reject low-priority requests when overloaded",
            "Queue high-priority requests for later processing",
            "Provide graceful degradation under surge",
            "Support priority-based or cost-aware shedding",
            "Return proper error codes to clients"
        ],
        "non_functional": [
            "Response time: Maintain p99 < 500ms under 2x traffic",
            "Fairness: Prevent starvation of important requests",
            "Recovery: Resume normal operation within 5 minutes",
            "Overhead: < 1% performance impact",
            "Accuracy: Shedding threshold auto-tuning"
        ]
    },
    "32_hinted_handoff": {
        "functional": [
            "Store hints for data destined to failed nodes",
            "Replay hints when failed node recovers",
            "Cleanup hint storage after successful replay",
            "Prevent write loss during node failure",
            "Support cleanup of abandoned hints"
        ],
        "non_functional": [
            "Overhead: < 10% extra storage for hints",
            "Latency: Hint storage adds < 1ms to write",
            "Durability: Hints stored durably",
            "Completeness: All hints eventually delivered",
            "Cleanup: Hints deleted after 3x replication time"
        ]
    },
    "33_gossip_failure_detection": {
        "functional": [
            "Detect failed nodes through peer gossip",
            "Probabilistically disseminate failure info",
            "Adapt gossip frequency based on failures",
            "Support concurrent failure detection",
            "Minimize false positives in dynamic networks"
        ],
        "non_functional": [
            "Detection time: O(log n) rounds",
            "Messages: O(log n) per node per round",
            "Accuracy: > 99% detection rate",
            "Scalability: Works with 1000s of nodes",
            "Overhead: < 5% bandwidth for gossip"
        ]
    }
}

def update_file(filepath: Path, topic_key: str) -> bool:
    """Update a file with specific requirements."""
    try:
        content = filepath.read_text(encoding="utf-8")

        if topic_key not in TOPIC_DETAILS:
            return False

        details = TOPIC_DETAILS[topic_key]

        # Replace generic functional requirements
        functional_text = "\n".join(
            f"- {req}" for req in details["functional"]
        )
        non_functional_text = "\n".join(
            f"- {req}" for req in details["non_functional"]
        )

        # Replace the placeholders
        pattern = r"### Functional Requirements\n- \[Core requirement \d\]\n(- \[Core requirement \d\]\n)*"
        replacement = f"### Functional Requirements\n{functional_text}\n"
        content = re.sub(pattern, replacement, content)

        # Update non-functional requirements section
        content = re.sub(
            r"(### Non-Functional Requirements\n)- \*\*Correctness:.*?\n- \*\*Latency:.*?\n",
            f"\\1{non_functional_text}\n",
            content,
            flags=re.DOTALL
        )

        filepath.write_text(content, encoding="utf-8")
        return True

    except Exception as e:
        print(f"❌ Error updating {filepath.name}: {e}")
        return False

def main():
    """Update all distributed systems topics."""
    print("🔄 Updating distributed systems topics with specific requirements...")
    print("=" * 70)

    system_design = Path("docs/system_design/04-distributed-systems")
    updated = 0

    for md_file in sorted(system_design.glob("*.md")):
        if "README" in md_file.name:
            continue

        topic_key = md_file.stem
        if update_file(md_file, topic_key):
            print(f"✅ Updated: {md_file.name}")
            updated += 1

    print("=" * 70)
    print(f"✨ Updated {updated} topics with specific functional/non-functional requirements!")

if __name__ == "__main__":
    main()
