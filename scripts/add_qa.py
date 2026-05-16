#!/usr/bin/env python3
import os
import re
from pathlib import Path

def get_context_aware_qa(title):
    """Generate common and follow-up Q&A based on document title"""

    title_lower = title.lower()

    qa_map = {
        'lru': {
            'common': [
                ('What does LRU mean and why is it important?',
                 'LRU (Least Recently Used) is a cache eviction policy that removes the least recently accessed item when capacity is exceeded. It\'s important because it preserves frequently accessed data in temporal locality patterns, improving cache hit rates and reducing latency. Works well for workloads where recent data is likely to be accessed again soon.'),
                ('Why do we need both a doubly linked list and a hash map?',
                 'The doubly linked list maintains access order in O(1) time by allowing direct node manipulation without scanning. The hash map provides O(1) lookup of nodes. Together they achieve O(1) for both get and put operations—impossible with either structure alone.'),
                ('How do we move an item to the front in O(1) time?',
                 'Using pointers in a doubly linked list, we can unlink a node from its current position (update 4 pointers: remove prev→next, next→prev) and relink it at the front by updating head pointers. This is O(1) regardless of list size, unlike array-based approach.'),
                ('How does accessing (getting) an element change cache state?',
                 'In LRU, accessing (getting) an element marks it as recently used by moving it to the front. This affects eviction order—if we need to remove items later, we\'ll remove from the back. Accessing should not change the value, only its position.'),
                ('Why not just use a single data structure?',
                 'Using only array/list would require O(n) to find and move items. Using only hash map would require O(n) to determine what to evict. Only the combination achieves O(1) by separating concerns: map for lookup, list for ordering.'),
                ('How do we handle duplicate keys when putting?',
                 'If a key already exists and we put a new value, we update the value in place and move the node to the front (most recent). This maintains single-entry guarantee per key and refreshes recency.'),
                ('What\'s the difference between LRU and LFU eviction?',
                 'LRU evicts the least recently used (time-based); LFU evicts the least frequently used (frequency-based). LRU is simpler to implement O(1). LFU has better hit rates for some workloads but requires frequency tracking and complex data structures.'),
                ('How do we prevent hash collisions affecting O(1) access?',
                 'Use a good hash function that distributes keys uniformly. With proper hash map implementation (separate chaining or open addressing), collisions don\'t affect average O(1). With poor distribution, worst case becomes O(n).'),
                ('What happens if we try to get from an empty cache?',
                 'Return a sentinel value (-1 or None) indicating miss. Some implementations throw exception. Most return -1 by convention. Important for client to check return value and handle miss (fetch from backend).'),
                ('Can LRU handle negative or zero capacity?',
                 'No. Capacity must be positive integer ≥ 1. Zero capacity cache makes no sense (always evict). Negative is invalid. Validate in constructor and throw exception on invalid input.'),
            ],
            'followup': [
                ('How would you implement LRU with a fixed memory budget instead of item count?',
                 'Track the total size of all items (sum of item_size fields) instead of count. When adding new item would exceed budget, keep removing (evicting) items until sufficient space exists. Requires storing size with each node.'),
                ('Can you make LRU thread-safe for concurrent access?',
                 'Use a ReentrantLock or synchronized block protecting all operations (get, put, eviction). Better performance with read-write locks: multiple readers, exclusive writers. For very high contention, use lock-free structures or shard the cache.'),
                ('How would you implement distributed LRU across multiple servers?',
                 'Use consistent hashing to route keys to specific servers, ensuring same key always goes to same server. Each server maintains local LRU. Handle replication by storing key replicas on neighboring servers for fault tolerance.'),
                ('What if you want LRU with time-based expiration (TTL)?',
                 'Add timestamp field to each node. Use background thread that periodically scans and removes expired items. Alternatively use lazy deletion: check expiration on access, delete if expired. Background cleanup is faster, lazy is more space-efficient.'),
                ('How would you optimize LRU for a write-heavy workload?',
                 'Consider LRU-W or W-TinyLFU variants that weight recent writes higher than reads. Batch write operations to reduce per-operation lock acquisition. Use write-optimized data structures (log-structured merge trees).'),
                ('What\'s the cache hit ratio and how do you measure it?',
                 'Hit ratio = successful_gets / total_gets. Miss ratio = 1 - hit ratio. Monitor continuously: missed hits / total hits gives hit ratio. Aim for 80%+ on typical workloads. Low hit ratio (< 50%) indicates cache not effective or capacity too small.'),
                ('How do you choose between LRU, LFU, W-TinyLFU, and TTL caching?',
                 'LRU for temporal locality (recent = popular). LFU for frequency patterns. W-TinyLFU balances both (production systems often use this). TTL for time-sensitive data. Often combine: LRU + TTL, or LFU + TTL for hybrid expiration.'),
                ('How would you handle the thundering herd on cache miss?',
                 'When popular key expires and many threads try fetching from backend simultaneously, this causes load spike. Solutions: probabilistic early expiration (refresh before expiry), request coalescing (single request rebuilds cache for all waiters), or bloom filters to detect non-existent keys.'),
                ('Can you implement LRU with a priority queue instead of linked list?',
                 'Yes, but less efficient: insertion/deletion become O(log n) instead of O(1). Only useful if you need other priority queue properties (e.g., weighted priorities). Standard LRU should use linked list for optimal performance.'),
                ('How do you serialize/persist LRU cache state?',
                 'Snapshot the entire list order and values to storage. On recovery, rebuild linked list from snapshot. Or use RDB snapshot approach: save key-value pairs with timestamps. Trade-off: complete snapshot vs. partial recovery.'),
            ]
        },
        'cache': {
            'common': [
                ('What is caching and why do we need it?',
                 'Caching stores frequently accessed data in fast storage (memory) to reduce latency and load on slower backends (database). Trade space (cache) for speed (latency). Critical for systems serving millions of requests per second.'),
                ('What are the main cache eviction policies?',
                 'LRU (least recently used), LFU (least frequently used), FIFO (first in first out), TTL (time-based), Random, and ARC (adaptive replacement). Choose based on access patterns: LRU for temporal, LFU for frequency, TTL for time-sensitive data.'),
                ('What is cache hit rate and cache miss rate?',
                 'Hit rate = successful_finds / total_accesses. Miss rate = 1 - hit rate. P(hit) = hits / (hits + misses). Target 80%+ hit rates for effective caching. Too-small cache gives low hit rate (wasted resources). Too-large cache uses more memory than needed.'),
                ('How do you handle cache invalidation when backend data changes?',
                 'Use TTL (time-based expiration), active invalidation (notify cache on write), cache-aside pattern (client checks backend), or write-through (update both). Active invalidation is fastest but complex. TTL is simplest but has stale data window.'),
                ('What is the cache-aside pattern?',
                 'Application checks cache first. On miss, fetch from backend, update cache, then return. Simple to implement. Risk: race condition where multiple threads fetch same miss simultaneously (thundering herd problem).'),
                ('What is write-through caching?',
                 'Writes go to both cache and backend simultaneously (synchronously). Ensures consistency: read always gets latest. Cost: write latency includes backend write. Safer than write-back but slower.'),
                ('What is write-back (write-behind) caching?',
                 'Writes go to cache only; backend updated asynchronously later (batch or periodic). Fast writes. Risk: data loss if cache fails before flushing. Need durability guarantees (persistence, replication).'),
                ('How do you choose cache size?',
                 'Estimate working set (frequently accessed data volume). Add 20-30% buffer for margin. Monitor hit rate: if < 80%, increase size. If > 95%, might be oversized (waste). Use tools like cachegrind to profile.'),
                ('What\'s the difference between client-side and server-side caching?',
                 'Client cache (browser): reduces network round-trips, entirely controlled by client. Server cache (memory, Redis): shared across clients, controlled by server. Multi-level caching often best.'),
                ('How do you measure cache effectiveness?',
                 'Hit rate (primary metric), latency reduction (P99 latency with vs. without cache), backend load reduction, and memory cost per cache entry. Calculate ROI: cost of cache vs. benefit (reduced latency, backend load).'),
            ],
            'followup': [
                ('How do you prevent the thundering herd problem in caches?',
                 'When popular key expires, many threads fetch from backend simultaneously causing spike. Solutions: probabilistic early expiration (refresh before TTL), request coalescing (single thread rebuilds, others wait), or bloom filters (detect non-existent keys fast).'),
                ('How would you implement multi-level cache hierarchy?',
                 'Use L1 (fast, small, in-process), L2 (medium, local machine), L3 (large, remote, Redis). Check L1, miss→L2, miss→L3, miss→backend. On write: update all levels. Trade space for speed across levels.'),
                ('Can you implement read-through caching (automatic population)?',
                 'Yes, cache loader/resolver called on miss. Transparent to application. Backend automatically uses cache layer. More complex than cache-aside but cleaner separation.'),
                ('How do you handle hot keys in distributed caches?',
                 'Hot key = key accessed by many threads/clients. Replicate hot keys on multiple cache nodes. Use local in-process caches for very hot keys. Monitor and detect hot keys automatically.'),
                ('What\'s the difference between warm and cold cache startup?',
                 'Cold cache: empty at start, misses until populated (slow ramp-up). Warm cache: pre-loaded from previous state (RDB/snapshot). Warm startup is critical for production (instant performance).'),
                ('How would you measure cache effectiveness for business metrics?',
                 'Track hit rate, P99 latency (with/without cache), backend QPS reduction, revenue impact. Calculate cache size vs. cost savings. A/B test to prove business value.'),
                ('What happens when cache size is insufficient for working set?',
                 'Constant evictions = high miss rate = ineffective cache. Solution: increase cache size, improve eviction policy, reduce working set, or use better hardware (faster storage).'),
                ('How do you debug cache issues in production?',
                 'Monitor hit rate continuously. Profile cache keys (which keys are accessed). Check for cache stampedes (sudden miss spike). Use distributed tracing to see cache path.'),
                ('How would you implement a persistent cache?',
                 'Combine memory cache (fast) with persistent backend (database, RocksDB, LevelDB). Write-back pattern: batch updates to persistent store. Trade latency for durability.'),
                ('Can you use caching for write-heavy workloads?',
                 'Write caching is risky (consistency issues). Use carefully: write-through for safety, write-back for speed. Good for batch writes (aggregate before writing). Monitor durability guarantees.'),
            ]
        },
        'database': {
            'common': [
                ('What is database sharding and why do we need it?',
                 'Sharding distributes data across multiple databases to scale horizontally beyond single-machine limits. Each shard holds subset of data. Enables serving more throughput and storing larger datasets. Trade-off: querying across shards is harder.'),
                ('What are common sharding strategies?',
                 'Range-based (user_id: 1-1M, 1M-2M, etc.), hash-based (hash(key) % num_shards), directory-based (lookup table), geographic (shard by region). Choose based on query patterns and data distribution.'),
                ('What is the hot shard problem?',
                 'One shard receives much more traffic/data than others due to skewed distribution (e.g., all new users in same range). Becomes bottleneck. Solution: split hot shard, use better sharding key, or combine with caching.'),
                ('How do you route queries to correct shard?',
                 'Middleware computes shard_id = hash(key) % num_shards or range lookup. Routes request to correct database. Must be consistent: same key always routes to same shard. Client or proxy layer handles routing.'),
                ('What happens when you add a new shard?',
                 'Data must be re-distributed. Existing shards reshare (redistribute their data). Causes temporary downtime and data movement overhead. Use consistent hashing to minimize data movement.'),
                ('Can you join data across shards?',
                 'Very difficult. Requires querying multiple shards and joining in application code (slow). Solution: denormalize (store denormalized copies), use distributed query engine (Presto), or redesign schema.'),
                ('How do you handle transactions across shards?',
                 'Distributed transactions (2-phase commit) are slow and risky. Prefer: single-shard transactions (common case), saga pattern (multi-step local transactions), or eventual consistency (async coordination).'),
                ('How do you choose sharding key?',
                 'Key used to determine shard. Must have good cardinality (many unique values) and distribute evenly. Avoid sharding by frequently queried field (makes range queries hard). Common: user_id (for user-centric), timestamp (for time-series).'),
                ('What is consistent hashing and when to use it?',
                 'Hash-based sharding that minimizes data movement on shard count changes. When you add/remove shard, only ~1/n data moves (not all). Distributed systems standard (Dynamo, Cassandra, consistent caching).'),
                ('How do you monitor shard health and skew?',
                 'Track data size per shard, QPS per shard, latency per shard. Alert on skew (some shards much larger/busier). Manually or auto-rebalance when detected.'),
            ],
            'followup': [
                ('How would you implement geo-distributed sharding?',
                 'Shard by geographic region (US, EU, APAC). Each region has replicas across data centers. Route based on user location. Handle eventual consistency between regions (strong eventual consistency).'),
                ('How do you prevent hot keys within a shard?',
                 'Detect hot keys (some keys far more accessed). Create micro-shards for hot keys (hash(key, counter) for replicas). Use caching layer above database. Monitor continuously.'),
                ('What is the trade-off between range sharding and hash sharding?',
                 'Range: enables range queries easily but may create hot shards (recent data). Hash: distributes evenly but makes range queries require scatter-gather. Choose based on query patterns.'),
                ('How would you re-shard with minimal downtime?',
                 'Dual-write strategy: write to both old and new shard layouts simultaneously. Gradually migrate data. Verify consistency. Switch reads to new layout. Clean up old shards.'),
                ('Can you shard by multiple columns (composite key)?',
                 'Yes, use (col1, col2) as shard key. Example: (user_id, tenant_id). Better distribution but more complex routing. Worth it for multi-tenant systems.'),
                ('How do you handle shard failures?',
                 'Use replication within each shard (master-slave). Detect failure, promote replica. Use consensus (Raft) for automatic failover. Trade: replication cost vs. availability.'),
                ('How would you implement resharding without data movement (virtual sharding)?',
                 'Map logical shards to physical shards via lookup table. When resharding, update mapping (no data movement). Trade: lookup overhead vs. seamless resharding.'),
                ('How do you implement cross-shard aggregations?',
                 'Scatter query to all shards. Gather results. Aggregate (sum, avg, max). Example: COUNT(*) requires hitting all shards. Slow but necessary for global analytics.'),
                ('Can you migrate from single database to sharded?',
                 'Yes, gradually. Start with logical sharding (single physical DB). Add more physical shards incrementally. Dual-write during migration. Atomic switch after validation.'),
                ('How do you handle uneven shard growth?',
                 'Monitor size growth. Split large shards before they get too big. Use growth-aware splitting (split at median timestamp for time-series). Automate with monitoring tools.'),
            ]
        },
        'kafka': {
            'common': [
                ('What is Apache Kafka?',
                 'Distributed event streaming platform (publish-subscribe messaging system). Stores event streams durable in log-based architecture. Supports multiple subscribers reading same data, replay capability, distributed processing. Critical infrastructure for real-time systems.'),
                ('How is Kafka different from traditional message queues?',
                 'Kafka persists all messages in ordered append-only log. Queues delete after consumption. Kafka supports multiple independent subscribers of same data. Enables replay, reprocessing, multiple consumers. Trade-off: different API, operational complexity.'),
                ('What is a Kafka topic and partition?',
                 'Topic: named event stream (orders, clicks, logs). Partition: ordered, immutable log within topic. Messages with same key go to same partition (order guarantee). Multiple partitions enable parallelism.'),
                ('What is a consumer group?',
                 'Set of consumers reading same topic collaboratively. Each partition assigned to one consumer in group. Enable parallel processing and scaling. If consumer dies, partition reassigned to other consumer.'),
                ('How does Kafka guarantee ordering?',
                 'Messages in single partition ordered by offset. Messages with same key always go to same partition (key routing). Therefore: same-key messages processed in order. Different keys can process out-of-order (parallel).'),
                ('What does acks setting do?',
                 'acks=0: producer doesn\'t wait (fire-and-forget). acks=1: wait for leader ack (fast). acks=all: wait for all replicas ack (safest, slowest). Choose: reliability vs. latency trade-off.'),
                ('What is at-least-once delivery guarantee?',
                 'Messages guaranteed delivered but may be duplicated. If producer retries on timeout, message could appear twice. Consumer must be idempotent (handle duplicates safely).'),
                ('How do you scale Kafka?',
                 'Add more partitions (parallelism), add more consumer replicas (throughput), add more brokers (storage/availability). Monitor lag, rebalance. Orchestrate with Kubernetes.'),
                ('What is consumer lag?',
                 'Difference between latest message offset and consumer\'s current offset. High lag = consumer falling behind. Monitor continuously, alert if lag growing. Indicates consumer too slow or too few consumers.'),
                ('How do you monitor Kafka health?',
                 'Track broker metrics (CPU, disk, network), consumer lag, in-sync replicas (ISR), partition distribution. Use tools like Burrow, LinkedIn monitoring. Alert on anomalies.'),
            ],
            'followup': [
                ('How would you implement exactly-once semantics in Kafka?',
                 'Use Kafka transactions (producer idempotency + atomic writes). Consumer must track processed message IDs. Or use idempotent producer + idempotent consumer. Trade: performance for correctness. Requires Kafka 0.11+.'),
                ('How do you handle backpressure (producer faster than consumer)?',
                 'Consumer lags behind (offset < latest). Use monitoring to detect. Scaling options: add more consumer threads, optimize consumer code, reduce producer rate, or buffer in queue. Choose based on SLA.'),
                ('How would you implement Kafka in multi-region setup?',
                 'Use MirrorMaker to replicate topics across regions. Choose consistency model (strong = sync, eventual = async). Handle failover (which region is primary). Complex operational model.'),
                ('What is Kafka Streams?',
                 'Library for stream processing on Kafka. Stateless (map, filter, flatMap), stateful (aggregate, join, window). Good for simple transformations. Alternative to Spark/Flink for JVM applications.'),
                ('How do you debug Kafka performance issues?',
                 'Monitor broker metrics (CPU, disk utilization), network latency, GC pauses. Check consumer lag, partition skew. Profile producer/consumer code. Check network bandwidth between brokers.'),
                ('How would you handle late-arriving messages?',
                 'Kafka preserves order within partition. Late messages appear out of order w.r.t. other partitions. Application must handle. Use timestamps for processing time logic. Consider grace period for windowed aggregations.'),
                ('How do you implement message ordering guarantees?',
                 'Send messages with same key (routes to same partition). Consumer reads single partition (ordered). Tradeoff: single partition limits throughput. Use multiple partitions + key if you need both.'),
                ('Can you compact Kafka topics?',
                 'Yes, log compaction mode: keeps latest value per key. Useful for state topics (user profiles). Trade: smaller storage but must maintain keys. Different from default delete mode.'),
                ('How would you implement Kafka with transactions?',
                 'Atomic multi-partition writes (Kafka 0.11+). Transactional producer: multiple puts before commit. Isolation level: read_committed (default) vs. read_uncommitted. Producer and consumer transaction APIs.'),
                ('How do you handle Kafka rebalancing?',
                 'When consumer joins/leaves, partitions reassigned. Brief unavailability during rebalance. Minimize with heartbeat tuning, larger batches, optimize consumer code. Monitor rebalance frequency and duration.'),
            ]
        },
        'redis': {
            'common': [
                ('What is Redis and when do you use it?',
                 'In-memory key-value data store with sub-millisecond latency. Used for caching (reduce DB load), sessions (user state), queues, real-time counters, leaderboards. Very fast but volatile (data loss on crash without persistence).'),
                ('What data structures does Redis support?',
                 'Strings (simple values), Lists (FIFO queues), Sets (unique values), Hashes (objects), Sorted Sets (leaderboards), Streams (Kafka-like), HyperLogLog (cardinality), Bitmaps (bitwise ops). Rich beyond simple cache.'),
                ('How does Redis persistence work?',
                 'RDB (snapshot): periodic point-in-time backup (fast, compact). AOF (append-only file): log all writes (durable, slower). BGSAVE/BGREWRITEAOF: background operations. Choose: speed vs. durability trade-off. Most use both.'),
                ('What is Redis replication?',
                 'Master-slave architecture: master accepts writes, slaves replicate. Read from master (strong consistency) or slaves (eventual, faster). Slaves can be read-only replicas or chain-replicate to others.'),
                ('What is Redis Sentinel?',
                 'High availability solution: monitors Redis instances, detects failures, promotes replica to master automatically. Requires 3+ Sentinel instances (majority quorum). Client connects via Sentinel instead of Redis directly.'),
                ('What is Redis Cluster?',
                 'Distributed Redis: data sharded across multiple nodes (hash slots). Auto-sharding, automatic failover, rebalancing. More complex than Sentinel. Required for massive scale (TB+ data).'),
                ('How do you choose between Sentinel and Cluster?',
                 'Sentinel: single master, high availability. Cluster: distributed, massive scale. Sentinel for most (simpler), Cluster only if need horizontal scaling. Data > memory = use Cluster.'),
                ('How do you handle eviction when Redis runs out of memory?',
                 'Set maxmemory policy: LRU, LFU, TTL, random, or no-eviction. LRU/LFU common for caching. TTL for session data. No-eviction blocks writes (safe but risky). Monitor memory usage constantly.'),
                ('What is key expiration in Redis?',
                 'Keys have optional TTL (time-to-live). After expiration, key automatically deleted. Lazy deletion (on access) + periodic cleanup. Use for session data, cache, or temporary counters. Check expiration policy for accuracy.'),
                ('How do you secure Redis?',
                 'Use password authentication (requirepass). ACLs (Redis 6+): per-user permissions. Run inside VPC (no internet access). Disable dangerous commands (FLUSHDB, CONFIG). TLS for remote connections.'),
            ],
            'followup': [
                ('How would you implement distributed locking with Redis?',
                 'SET key value EX ttl NX (atomic: set if not exists with TTL). Acquire lock, execute critical section, delete key. Risk: crash loses lock (data consistency issue). Redlock solves this with multiple instances.'),
                ('What is Redlock and what problem does it solve?',
                 'Distributed lock across 5 Redis instances. Acquire lock on majority (quorum). Survives single instance failure. Overkill for most, but necessary for safety-critical sections. Trade: performance for correctness.'),
                ('How would you implement rate limiting with Redis?',
                 'Use sorted set with timestamps or hash with counters. Increment on each request, check against limit. Fast (O(log n)). Alternative: token bucket in Lua script. Faster than database.'),
                ('How do you handle Redis memory limits and eviction policy?',
                 'Set maxmemory (bytes), maxmemory-policy (LRU/LFU/TTL/random). Monitor hit rate (eviction = misses). Can also manually delete old keys or use cache-aside with database.'),
                ('Can you use Redis for reliable message queues?',
                 'Partially. Lists (basic) or Streams (better). Lists: FIFO, no persistence without RDB. Streams: replicas, consumer groups, reliable delivery (Kafka-like). For critical: use Kafka instead.'),
                ('How would you implement Pub/Sub in Redis?',
                 'Publisher sends to channel, subscribers receive. Fire-and-forget (no persistence). Good for notifications. Bad for reliable messaging (missed if subscriber offline). Better: Streams for reliable pub/sub.'),
                ('How do you scale Redis beyond single node?',
                 'Use Cluster (distributed), replicate read-heavy workload (slaves), or shard in application code. Cluster best for massive scale. Replication for read scaling. App sharding for distributed control.'),
                ('Can you implement transactions in Redis?',
                 'MULTI/EXEC: atomic batch of commands. Optimistic locking with WATCH. No rollback (all-or-nothing at command level). Use Lua scripts for complex atomic operations.'),
                ('How would you debug Redis performance issues?',
                 'SLOWLOG: find slow commands. MONITOR: see all commands in real-time. Memory analysis: MEMORY DOCTOR, key usage patterns. Network: latency between app and Redis. Profiling tools.'),
                ('How do you backup and restore Redis?',
                 'Backup: RDB snapshots, AOF files, or replication. Restore: copy files, or use Redis replication + replicaof. Backup strategy: periodic snapshots + AOF for durability. Test recovery regularly.'),
            ]
        },
    }

    # Find best matching Q&A
    common_qa = qa_map.get('cache', {}).get('common', [])
    followup_qa = qa_map.get('cache', {}).get('followup', [])

    for keyword in sorted(qa_map.keys(), key=len, reverse=True):
        if keyword in title_lower:
            common_qa = qa_map[keyword]['common']
            followup_qa = qa_map[keyword]['followup']
            break

    return common_qa, followup_qa

def replace_qa_sections(content):
    """Replace existing Q&A sections with comprehensive ones"""

    # Extract title
    title_match = re.match(r'# (.+)', content)
    title = title_match.group(1) if title_match else "System"

    # Generate Q&A
    common_qa, followup_qa = get_context_aware_qa(title)

    # Remove existing Q&A sections
    content = re.sub(r'\n## Common Questions.*?(?=\n## |\Z)', '', content, flags=re.DOTALL)
    content = re.sub(r'\n## Follow-up Questions.*?(?=\n## |\Z)', '', content, flags=re.DOTALL)

    # Format new Q&A sections
    common_section = "## Common Questions & Answers\n\n"
    for q, a in common_qa:
        common_section += f"**Q: {q}**\n\nA: {a}\n\n"

    followup_section = "## Follow-up Questions & Answers\n\n"
    for q, a in followup_qa:
        followup_section += f"**Q: {q}**\n\nA: {a}\n\n"

    # Append at end
    enhanced = content.rstrip() + "\n\n" + common_section + followup_section

    return enhanced

def process_all_files():
    """Process all markdown files"""
    base_path = Path('/home/sbisw/github/interviewprep/docs/system_design')

    count = 0
    for md_file in base_path.rglob('*.md'):
        if md_file.name == 'README.md':
            continue

        try:
            with open(md_file, 'r') as f:
                content = f.read()

            enhanced = replace_qa_sections(content)

            if enhanced != content:
                with open(md_file, 'w') as f:
                    f.write(enhanced)
                count += 1
        except Exception as e:
            print(f"Error: {md_file.name}: {e}")

    return count

if __name__ == '__main__':
    updated = process_all_files()
    print(f"Updated Q&A in {updated} files")
