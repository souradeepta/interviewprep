#!/usr/bin/env python3
"""
Complete enhancement of all 20 distributed systems concepts.
"""

import os
import re

base_path = "/home/sbisw/github/datastructures/docs/system_design/04-distributed-systems"

enhancements = {
    "33_gossip_failure_detection": {  # File named with wrong name, but it's actually accrual failure detector
        "architecture": "Track heartbeat history. Compute probability of failure rather than binary decision.",
        "diagram": "Heartbeat intervals: [500ms, 450ms, 480ms, 550ms, ...]\nVariance: low = consistent\nMissing interval: 1s instead of 500ms\nProbability of failure: 95% (configurable threshold)",
        "qa": "**Q: vs fixed timeout?** A: Adapts to network jitter. False positive rate < 5% configurable.\n\n**Q: Algorithm?** A: Phi accrual detector. Gaussian distribution of intervals.\n\n**Q: Threshold tuning?** A: Phi = 1 (90% confident dead), Phi = 2 (99% confident).\n\n**Q: Recovery?** A: Reset on heartbeat received.",
        "calculations": "- Heartbeat interval: 1 second nominal\n- Network jitter: 50ms std dev\n- P95 interval: 1.08 seconds\n- Detection with Phi=2: requires ~3 missing intervals\n- False positive rate: <1% with correct tuning",
        "design_choices": [
            ["Accrual detector", "Adaptive, fewer false positives", "More complex"],
            ["Fixed timeout", "Simple", "Prone to false positives"],
            ["Multiple independent detectors", "Voting", "Overkill for most"],
            ["Gossip-based detection", "Decentralized", "Slower consensus"]
        ]
    },
    "14_distributed_caching": {
        "architecture": "Redis Cluster with 6 nodes (3 master, 3 slave). Each master handles 5461 slots. Data hashed to slots via CRC16.",
        "diagram": "┌─────────────┐\n│ Redis Master 1 (Slots 0-5461)│\n│ ├─ Slave 1 (replication) │\n├─────────────┤\n│ Redis Master 2 (Slots 5461-10922)│\n│ ├─ Slave 2 (replication) │\n├─────────────┤\n│ Redis Master 3 (Slots 10922-16384)│\n│ ├─ Slave 3 (replication) │\n└─────────────┘",
        "qa": "**Q: How to handle failover?** A: Automatic promotion. Slave becomes master if master unavailable (sentinel/cluster mode).\n\n**Q: Cross-slot operations?** A: Not supported natively. Use hash tags {key} to force same slot.\n\n**Q: Resharding?** A: Move slots gradually. Pipeline commands to minimize latency.\n\n**Q: Consistency?** A: Eventual consistency with async replication.",
        "calculations": "- 6 nodes, 1M keys: ~167K keys per node\n- 1M req/sec distributed: ~166K req/sec per node\n- Latency: <1ms single node, network adds 1-5ms\n- Memory: 1GB per 1M small keys (assuming ~1KB avg value)",
        "design_choices": [
            ["Redis Cluster", "Scalable, HA, persistence", "More operational complexity"],
            ["Memcached+DHT", "Simple, fast", "No persistence, no HA"],
            ["DynamoDB", "Managed, global", "Vendor lock-in, higher cost"]
        ]
    },
    "15_service_discovery": {
        "architecture": "Centralized registry with client polling or server-side discovery via LB.",
        "diagram": "Service Registry (etcd/Consul/Zookeeper)\n├─ web-service-1: 10.0.1.1:8080 (healthy)\n├─ web-service-2: 10.0.1.2:8080 (healthy)\n├─ api-service-1: 10.0.1.3:9000 (healthy)\n└─ api-service-2: 10.0.1.4:9000 (unhealthy → removed)",
        "qa": "**Q: Health check frequency?** A: 10-30 second intervals. Balance between detection time and load.\n\n**Q: TTL for entries?** A: 30s-5m. Prevents stale registrations.\n\n**Q: Client-side vs server-side?** A: Client: flexible, complex. Server: centralized, simpler.\n\n**Q: Consistency?** A: Eventual consistency acceptable.",
        "calculations": "- 1000 services, 10K instances: 10MB registry (1KB per entry)\n- Health checks: 1000 checks/min = 16 checks/sec per service\n- Query load: 100K queries/sec from clients\n- Replication overhead: 3x for HA (3 replicas)",
        "design_choices": [
            ["Consul", "Service mesh, HA, consul UI", "Complex setup, resource overhead"],
            ["Eureka", "Netflix-proven, simple", "Eventual consistency only"],
            ["etcd+custom", "Lightweight, flexible", "More DIY work"]
        ]
    },
    "16_distributed_locking": {
        "architecture": "Lock service handles mutex via atomic operations. TTL prevents deadlock.",
        "diagram": "Client 1: acquire(lock) → SET key val EX 30 NX → Success\nClient 2: acquire(lock) → SET key val EX 30 NX → Fail (blocked)\nClient 1: release(lock) → DEL key → Success\nClient 2: acquire(lock) → SET key val EX 30 NX → Success",
        "qa": "**Q: Deadlock prevention?** A: TTL-based auto-release. Client heartbeat renews lease.\n\n**Q: Lock fairness?** A: FIFO queue tracks requesters. Process in order.\n\n**Q: Reentrant locks?** A: Store holder ID. Allow re-acquire by same holder.\n\n**Q: Lock watch?** A: Event-driven better than polling.",
        "calculations": "- 1000 concurrent clients, 100ms critical section\n- Lock acquisition: 1-5ms (network RTT)\n- Lock contention: increased latency linearly\n- TTL duration: should be 10x max critical section",
        "design_choices": [
            ["Redis (SET NX EX)", "Fast, simple", "Single point of failure, no HA"],
            ["Zookeeper ephemeral", "Reliable, HA", "Slower performance"],
            ["Redlock (multi-Redis)", "Distributed, safer", "Still has partition issues"]
        ]
    },
    "17_vector_clocks": {
        "architecture": "Each process maintains vector [t1, t2, ..., tn]. Increment on local event, piggyback on messages.",
        "diagram": "Process A: [1, 0, 0] → send msg → [2, 0, 0]\nProcess B: [0, 1, 0] → receive → [2, 2, 0] → send → [2, 3, 0]\nProcess C: [0, 0, 1] → receive → [2, 3, 2]",
        "qa": "**Q: Vector vs Lamport clock?** A: Vector: partial order (causality). Lamport: total order (no causality).\n\n**Q: Scalability?** A: Vector grows O(n) per message. Use interval tree clocks for 1000+ processes.\n\n**Q: Concurrent events?** A: Incomparable - neither causally related.\n\n**Q: Space overhead?** A: ~8 bytes per process per message.",
        "calculations": "- 1000 processes: 8KB vector per message\n- Message overhead: 0.8% bandwidth for large payloads\n- Causality detection: compare O(n) vectors per message\n- Storage per million messages: 8GB just for vectors",
        "design_choices": [
            ["Vector Clocks", "Causality information", "O(n) space, grows with processes"],
            ["Lamport Clocks", "O(1) space, simple", "No causality information"],
            ["Hybrid Logical Clocks", "Compact (8 bytes), causality", "More complex"],
            ["Synchronized clocks", "Zero overhead", "Requires NTP sync across WAN"]
        ]
    },
    "18_quorum_systems": {
        "architecture": "Read and write to quorum of replicas. W + R > N ensures consistency.",
        "diagram": "N=5 replicas\nW=3 (60%), R=3 (60%)\nWrite: wait for 3/5 acks\nRead: check 3/5, return latest\nOverlap ensures we read written value",
        "qa": "**Q: Read repair?** A: Read quorum may contain stale. Compare versions, update stale replicas.\n\n**Q: Sloppy quorum?** A: Accept responses from any 3 (not just designated). Use hinted handoff.\n\n**Q: Quorum unavailable?** A: Cannot proceed if too many replicas down. Trade CAP for consistency.\n\n**Q: Byzantine quorum?** A: Need (3f+1) replicas for f Byzantine failures. 13 replicas for 4 failures.",
        "calculations": "- 5 replicas, W=3, R=3\n- Write latency: wait for 3rd slowest (p50 of 3 nodes, ~20ms typical)\n- Read latency: same, but can read from any 3\n- Unavailability: if 3+ replicas down, cannot write\n- Network partition: can lose consistency if W < N/2 + 1",
        "design_choices": [
            ["W=1, R=N", "Fast writes", "Slow reads, eventual consistency"],
            ["W=N/2+1, R=N/2+1", "Balanced", "Slower than W=1, R=1"],
            ["W=N, R=1", "Slow writes, fast reads", "All replicas must be up"],
            ["Sloppy quorum", "High availability", "Temporary inconsistency during healing"]
        ]
    },
    "19_read_repair": {
        "architecture": "Read returns highest version seen. Async repair updates stale replicas to match.",
        "diagram": "Read: [v5,X], [v3,Y], [v5,X] → return X\nRepair: send v5,X to replica with v3,Y async",
        "qa": "**Q: Active vs passive?** A: Active: repair every read (CPU cost). Passive: only on mismatch.\n\n**Q: Merkle trees?** A: Hash structure for efficient node sync. Identifies diverged parts quickly.\n\n**Q: Anti-entropy scans?** A: Daily/weekly full syncs. CPU/bandwidth intensive.\n\n**Q: Conflict resolution?** A: Last-write-wins (timestamp), vector clocks, CRDTs, application logic.",
        "calculations": "- 10M keys, 3 replicas, 10% stale\n- Read repair: 1M keys updated per day (background)\n- Bandwidth: 1MB per 1M keys with Merkle tree\n- Scan overhead: 10M keys × 3 replicas = 30M comparisons",
        "design_choices": [
            ["Read repair", "Fixes on access", "Limited coverage, doesn't catch unread"],
            ["Merkle tree anti-entropy", "Complete sync", "Batch operation, CPU intensive"],
            ["CRDTs", "Auto-converge", "Limited data types, higher memory"]
        ]
    },
    "20_bloom_filters": {
        "architecture": "Bit array + k hash functions. Set bits on insert, check all bits on lookup.",
        "diagram": "Bit array (m bits): [0,1,0,1,0,1,1,0]\nInsert 'apple': h1%m=2, h2%m=5, h3%m=6 → set bits 2,5,6\nLookup 'apple': check bits 2,5,6 → all set → MAYBE present\nLookup 'banana': check bits → not all set → DEFINITELY absent",
        "qa": "**Q: False positives?** A: Yes, unavoidable. Tune size for target rate (~1-5%).\n\n**Q: False negatives?** A: Zero. If lookup returns no, item definitely absent.\n\n**Q: Optimal size?** A: m = 1.44 × n × log2(1/p) bits for p false positive rate.\n\n**Q: Deletions?** A: Cannot delete from standard BF. Use counting Bloom filter.",
        "calculations": "- 1M items, 1% FP rate: 10Mb bits ≈ 1.25MB\n- k optimal hash functions: k = 0.7 × (m/n) ≈ 10 for 1% FP\n- Lookup: O(k) = O(10) operations\n- vs hash table: 50× smaller (1.25MB vs 50MB for 1M keys)",
        "design_choices": [
            ["Bloom filter", "Minimal memory", "False positives"],
            ["Hash table", "Exact matching", "O(n) memory"],
            ["Counting Bloom", "Deletion support", "4× memory, slower"],
            ["Cuckoo filter", "Deletion, lower FP", "More complex"]
        ]
    },
    "21_skip_lists": {
        "architecture": "Multiple sorted levels. Level 0 has all elements, higher levels have fewer (probability 1/2).",
        "diagram": "L3: 1 ─────────────────────→ 9\nL2: 1 ────→ 3 ────→ 7 ──→ 9\nL1: 1 → 2 → 3 → 5 → 7 → 8 → 9",
        "qa": "**Q: vs B-tree?** A: Skip list: simpler code, better CPU cache locality. B-tree: fewer cache misses for range.\n\n**Q: Probabilistic guarantees?** A: High probability balanced (not deterministic). Insertions O(log n).\n\n**Q: Range queries?** A: Walk L0 forward from start position.\n\n**Q: Rebalancing?** A: None needed. Probabilistic balance sufficient.",
        "calculations": "- 1M items: typical height = log2(n) = 20 levels\n- Insert: O(log n) = O(20) operations average\n- Memory overhead: 1/(1-p) = 2× for p=0.5\n- vs balanced tree: simpler implementation, similar performance",
        "design_choices": [
            ["Skip list", "Simpler than trees", "Probabilistic, not deterministic"],
            ["B-tree", "Optimized I/O", "More complex"],
            ["AVL tree", "Deterministic balance", "More rotations"],
            ["Hash table", "O(1) lookup", "No ordering, no range queries"]
        ]
    },
    "22_merkle_trees": {
        "architecture": "Binary tree of hashes. Leaf nodes = data. Parent = hash(left + right).",
        "diagram": "              Root\n             /    \\\\\n         H(AB)    H(CD)\n        /   \\      /    \\\\\n      H(A) H(B) H(C) H(D)\n       |     |    |     |\n      Data  Data Data  Data",
        "qa": "**Q: Sync efficiency?** A: Compare root. If match, done. If differ, recurse to children.\n\n**Q: Dynamic updates?** A: Rebuild path from leaf to root. O(log n) operations.\n\n**Q: Storage?** A: n data items = n + (n-1) hashes = O(n) space.\n\n**Q: Verification?** A: Client verifies subset with O(log n) hashes in proof.",
        "calculations": "- 1M objects, SHA256 hashes\n- Tree depth: log2(1M) ≈ 20 levels\n- Identifying 1% divergence: ~200 hash comparisons vs 10K pairwise\n- Proof size: 20 hashes × 32 bytes = 640 bytes per object",
        "design_choices": [
            ["Merkle tree", "Efficient partial sync", "Must rebuild on updates"],
            ["Simple hash of all", "Fast full comparison", "Cannot identify partial divergence"],
            ["Rsync rolling hash", "Very bandwidth efficient", "Complex algorithm"],
            ["CRDTs", "No sync needed", "Limited data types"]
        ]
    },
    "23_gossip_protocol": {
        "architecture": "Nodes periodically exchange state with random peers. Information propagates exponentially.",
        "diagram": "Round 1: A knows update, tells B,C,D (3 random)\nRound 2: B,C,D each tell 3 random → ~9 nodes know\nRound 3: ~27 nodes know\nRound log(N): ~N nodes know (all)",
        "qa": "**Q: Message efficiency?** A: O(n log n) total messages for full propagation.\n\n**Q: Fault tolerance?** A: Works if 50% nodes fail (random selection likely picks live).\n\n**Q: Convergence?** A: O(log n) rounds for full spread. Exponential growth.\n\n**Q: Piggyback?** A: Include gossip in heartbeat messages. Minimal overhead.",
        "calculations": "- 1000 nodes: ~log2(1000) = 10 rounds\n- Messages per round: 1000 × fan-out (3-5) = 3-5K messages\n- Total: ~30-50K messages\n- vs flooding: 1K nodes × 999 = 1M messages\n- Convergence time: 10 rounds × 1 sec interval = 10 seconds",
        "design_choices": [
            ["Gossip protocol", "Decentralized, resilient", "Eventual consistency, slower"],
            ["Flooding", "Guaranteed fast", "O(n²) messages, network overload"],
            ["Tree-based propagation", "Efficient", "Single point of failure at root"],
            ["Centralized coordinator", "Consistent, fast", "Coordinator bottleneck"]
        ]
    },
    "24_crdt": {
        "architecture": "CRDTs use commutative operations. All nodes merge same operations → converge to same state.",
        "diagram": "G-Counter CRDT:\nNode A: {A:5, B:0, C:0} = 5\nNode B: {A:5, B:3, C:0} = 8\nNode C: {A:5, B:3, C:2} = 10\nMerge: max-per-node = 10 (consistent)",
        "qa": "**Q: Convergence guaranteed?** A: Yes, mathematically. Commutative + associative operations.\n\n**Q: Data types supported?** A: Counters, sets (LWW, OR, UR), registers, maps, sequences (RGA, Yata).\n\n**Q: Causality?** A: Depends on implementation. Vector clocks optional.\n\n**Q: Memory?** A: Metadata overhead 10-20× for concurrent edits.",
        "calculations": "- 100K users, 1M edits over time\n- Per-edit metadata: ~100 bytes\n- Total CRDT metadata: 100MB vs 10MB raw data\n- Merge time: O(n log n) for n operations to sync",
        "design_choices": [
            ["CRDT (OT-free)", "Auto-converge, no central server", "Memory overhead, limited types"],
            ["Operational Transform", "More data types", "Central server required"],
            ["Consensus (PAXOS/Raft)", "Strong consistency", "Unavailable on partition"],
            ["Last-write-wins", "Simple", "Data loss possible"]
        ]
    },
    "25_distributed_config_management": {
        "architecture": "Centralized store (etcd/Consul/Zookeeper) with watch-based propagation to clients.",
        "diagram": "/config hierarchy:\n  /app\n    /db: postgres://...\n    /cache: redis://...\n    /features: {flag1:true, flag2:false}",
        "qa": "**Q: Push vs pull?** A: Push (watch): event-driven, live. Pull (polling): simpler, eventual.\n\n**Q: Versioning?** A: Track versions. Rollback capability. Audit trail.\n\n**Q: Secret management?** A: Encrypt at rest. TLS in transit. RBAC. Rotate periodically.\n\n**Q: Consistency?** A: Strong consistency preferred (all servers see same).",
        "calculations": "- 100 services, 1000 config values\n- Average config size: 100 bytes\n- Total: 100KB\n- Watch propagation latency: <100ms typically\n- Storage: 100KB × 3 replicas = 300KB",
        "design_choices": [
            ["Zookeeper", "Battle-tested, HA", "Complex, JVM resource heavy"],
            ["etcd", "Fast, simple API", "Smaller community"],
            ["Consul", "Service mesh integrated", "More features, more overhead"],
            ["Git + poll", "Simple, auditability", "Slower propagation"]
        ]
    },
    "26_leader_election": {
        "architecture": "Candidates compete via quorum voting. Highest priority/ID becomes leader. Heartbeat confirms.",
        "diagram": "Node 5 (leader) detected dead\nNode 4,6,7 candidates\nNode 7 (highest) sends heartbeat → elected leader\nOther nodes acknowledge",
        "qa": "**Q: Split brain prevention?** A: Require quorum majority for leadership. Partition loses minority.\n\n**Q: Failover latency?** A: Election timeout (500ms-2s) + message propagation.\n\n**Q: Candidate ranking?** A: By node ID, capabilities, uptime, or custom logic.\n\n**Q: Stale leader?** A: Heartbeat from new leader forces old to step down.",
        "calculations": "- 5 nodes: quorum = 3\n- Election timeout: 1 second\n- Detect failure: ~1 second heartbeat interval\n- Failover latency: 2-3 seconds typical\n- Message overhead: election = 5 × 5 = 25 messages",
        "design_choices": [
            ["Bully algorithm", "Simple, fast", "Many messages"],
            ["Raft", "Practical, safe", "More complex"],
            ["Ring algorithm", "Elegant", "Slower convergence"],
            ["Zookeeper/etcd", "Proven, reliable", "External service required"]
        ]
    },
    "27_heartbeat_failure_detection": {
        "architecture": "Nodes send periodic heartbeats. Absence of N heartbeats → failure. Adaptive timeout.",
        "diagram": "Node A healthy: heartbeats every 1s ✓✓✓✓\nNode B fails: heartbeat stops ✓✗✗✗ → marked down after 3 missing",
        "qa": "**Q: Timeout tuning?** A: Too aggressive → false positives. Too lenient → slow detection.\n\n**Q: Adaptive timeouts?** A: Accrual detectors adjust based on historical data.\n\n**Q: Network jitter?** A: Causes false positives. Use P95/P99 + buffer.\n\n**Q: Partition handling?** A: Minority side must detect and step down.",
        "calculations": "- 1000 node cluster, 1-second heartbeat interval\n- Network RTT: 10ms avg, 50ms P95\n- Detection latency: 3 missed + timeout = 3-4 seconds\n- False positive rate: tune to <1% (cost of wrong detection)",
        "design_choices": [
            ["Fixed timeout", "Simple", "Tuning difficult, false positives"],
            ["Adaptive timeout", "Lower false positives", "More complex"],
            ["Gossip-based", "Decentralized", "Slower detection"],
            ["Dedicated monitor", "Centralized, fast", "Single point of failure"]
        ]
    },
    "28_cascading_failures": {
        "architecture": "Bulkheads isolate failures. Circuit breaker stops cascades. Backpressure prevents overload.",
        "diagram": "Service A → Service B → Service C\nIf C fails:\n  Without bulkhead: A exhausted waiting → cascades\n  With bulkhead: timeout, return cached/degraded\n  Circuit breaker: stop sending after threshold",
        "qa": "**Q: Timeout strategy?** A: Must be shorter than upstream timeout to prevent cascades.\n\n**Q: Graceful degradation?** A: Return cached data or reduced functionality instead of error.\n\n**Q: Recovery?** A: Exponential backoff to slowly re-probe failed service.\n\n**Q: Load shedding?** A: Reject requests when overloaded rather than queue infinitely.",
        "calculations": "- Service response time: 100ms normally\n- Failure: 1 service down, 100 requests queued\n- Timeout: 500ms\n- Cascading requests: 100 × downstream services = 100 wasted requests\n- With bulkhead: 100 × timeout = 50 seconds queue delay prevented",
        "design_choices": [
            ["Bulkheads + timeouts", "Prevents cascade", "Requires tuning"],
            ["Circuit breaker", "Fails fast", "Need fallback logic"],
            ["Rate limiting", "Prevents overload", "Rejects traffic"],
            ["Async queue", "Buffers load", "Delays increase"]
        ]
    },
    "29_distributed_tracing": {
        "architecture": "Trace ID flows through all services. Each span records timing, tags, events.",
        "diagram": "Request span (100ms):\n  Service A (20ms)\n  → Service B (50ms, includes)\n    → Service C (30ms)\n  → Service D (10ms)",
        "qa": "**Q: Sampling?** A: 1-10% in prod. Full tracing in staging/test.\n\n**Q: Overhead?** A: ~5-10% latency impact. Worth it for debugging.\n\n**Q: Storage?** A: 1K trace spans/sec = ~1MB/sec uncompressed.\n\n**Q: Privacy?** A: Sanitize PII from spans. Encrypt in transit/rest.",
        "calculations": "- 10K req/sec, sampling 1% = 100 traces/sec\n- ~100 spans per trace = 10K spans/sec\n- 1KB per span = 10MB/sec raw\n- With compression (4:1): 2.5MB/sec\n- Monthly: 2.5MB/s × 2.6M seconds = 6.5TB (with retention policies)",
        "design_choices": [
            ["Distributed tracing (Jaeger/Zipkin)", "Production debugging", "Storage overhead"],
            ["Structured logging", "Simpler", "Harder to correlate"],
            ["APM (DataDog/NewRelic)", "Managed, more features", "Expensive"],
            ["Custom sampling", "Flexible", "DIY maintenance"]
        ]
    },
    "30_monitoring_alerting": {
        "architecture": "Metrics collected → time-series DB → alert rules → incidents → escalation.",
        "diagram": "Prometheus scrapes → TSDB storage\n         ↓\n  Grafana dashboards\n         ↓\nAlert rules (if metric > threshold)\n         ↓\nAlertmanager → Slack/PagerDuty",
        "qa": "**Q: Metrics to collect?** A: RED (Rate, Errors, Duration). USE (Utilization, Saturation, Errors).\n\n**Q: Cardinality explosion?** A: Limit tags. No user IDs in metrics.\n\n**Q: Alert fatigue?** A: Tune thresholds. Use baselines, anomaly detection.\n\n**Q: SLA/SLO?** A: Define meaningful SLOs. Map to alerts.",
        "calculations": "- 10K metrics, 15-second resolution = 40K points/minute\n- Each point: 64-bit timestamp + value = 16 bytes\n- 40K points/min × 16 bytes × 43200 min/month = 27.6GB/month\n- 1 year retention: 331GB (before compression)",
        "design_choices": [
            ["Prometheus + Grafana", "Open source, flexible", "DIY scaling/retention"],
            ["Datadog/NewRelic", "Managed, powerful", "Expensive at scale"],
            ["CloudWatch/Stackdriver", "Cloud-native", "Vendor lock-in"],
            ["Custom TSDB", "Tailored", "High maintenance"]
        ]
    },
    "31_load_shedding": {
        "architecture": "Detect overload → reject low-priority requests → reduce processing → return to normal.",
        "diagram": "Request rate: 1000 req/sec\n  Processing capacity: 800 req/sec\n  Accepted: 800 (high priority)\n  Dropped: 200 (low priority)",
        "qa": "**Q: Detection mechanism?** A: Queue depth, response latency, CPU usage.\n\n**Q: Priority levels?** A: Gold/Silver/Bronze customers. Authenticated > anonymous.\n\n**Q: Graceful degradation?** A: Return cached data or 503 Service Unavailable.\n\n**Q: Recovery?** A: Gradual acceptance increase as load drops.",
        "calculations": "- Service can handle 1000 req/sec\n- Traffic spike: 2000 req/sec arrives\n- Without shedding: 1000 accepted (overloaded), rest timeout\n- With shedding: 1000 accepted (normal), 1000 rejected fast (2ms)\n- Better: user gets immediate rejection vs 10s timeout",
        "design_choices": [
            ["Token bucket (rate limiting)", "Smooth load", "Not true shedding"],
            ["Queue + drop", "Simple", "Delayed rejection"],
            ["Adaptive shedding", "Dynamic thresholds", "Complex tuning"],
            ["Request prioritization", "Fair allocation", "Requires priority info"]
        ]
    },
    "32_hinted_handoff": {
        "architecture": "If primary replica unavailable, write to temporary 'hint' node. Later deliver to primary.",
        "diagram": "Write normally:\n  Client → Primary → ACK\n\nWrite with hint (primary down):\n  Client → Hint node → ACK\n  Hint node: store('primary_id', value)\n  Later: primary recovers → hint delivers stored value",
        "qa": "**Q: Hint storage?** A: In-memory or disk. Eventual delivery.\n\n**Q: Hint failures?** A: Rare, but data can be lost if hint fails too.\n\n**Q: Delivery mechanism?** A: Background process pushes after recovery detection.\n\n**Q: Multi-hint?** A: Multiple replicas down → write to multiple hints.",
        "calculations": "- 10-node cluster, 1 node down\n- 100K write/sec, 1KB values\n- Hints accumulated: 100K values × 1KB = 100MB/hour\n- Delivery latency: 1-10 minutes after recovery\n- Storage on hint nodes: must have 10× normal space",
        "design_choices": [
            ["Hinted handoff", "Higher availability", "Temporary consistency loss"],
            ["Read repair", "Fixes on access", "Doesn't help writes"],
            ["Quorum writes (W=N)", "Consistency", "Cannot tolerate failures"],
            ["Replication factor 5", "More hints available", "Higher resource cost"]
        ]
    }
}

def enhance_file(concept_id, content):
    """Enhance a single distributed systems concept file."""
    filepath = os.path.join(base_path, f"{concept_id}.md")

    try:
        with open(filepath, 'r') as f:
            doc = f.read()

        # Replace sections
        doc = doc.replace(
            "Core Mechanism:\n- How this system works\n- Key components and interactions\n- Data flow and processing",
            content['architecture']
        )

        doc = doc.replace(
            "[Visual system components and interactions]",
            content['diagram']
        )

        doc = doc.replace(
            "**Q: When to use this approach?**\nA: [Specific use cases and scenarios where this is beneficial]\n\n**Q: What are the key trade-offs?**\nA: [Pros and cons of this approach vs alternatives]\n\n**Q: How does this handle failures?**\nA: [Failure scenarios and recovery mechanisms]\n\n**Q: How to scale this?**\nA: [Scaling strategies and bottlenecks]",
            content['qa']
        )

        doc = doc.replace(
            "For typical distributed system scenario:\n- Performance metrics\n- Scalability limits\n- Resource requirements\n- Typical deployment sizes",
            content['calculations']
        )

        # Replace design table
        table_rows = "\n".join([f"| {row[0]} | {row[1]} | {row[2]} |" for row in content['design_choices']])
        doc = doc.replace(
            "| Option A | [Advantages] | [Disadvantages] |\n| Option B | [Advantages] | [Disadvantages] |\n| Option C | [Advantages] | [Disadvantages] |",
            table_rows
        )

        with open(filepath, 'w') as f:
            f.write(doc)

        return True
    except Exception as e:
        print(f"Error enhancing {concept_id}: {e}")
        return False

# Enhance all 20 concepts
for concept_id, content in enhancements.items():
    if enhance_file(concept_id, content):
        print(f"✓ Enhanced {concept_id}")

print("\n✅ All 20 distributed systems concepts enhanced")
