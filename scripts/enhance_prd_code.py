#!/usr/bin/env python3
import re
from pathlib import Path

def get_detailed_code_explanation(title):
    """Generate detailed code explanation based on title"""
    title_lower = title.lower()

    if 'lru' in title_lower:
        return """## Code Explanation (Detailed)

### Python OrderedDict Implementation
The OrderedDict approach is clearest and production-ready:
- Maintains insertion order automatically
- move_to_end(key) marks as recently used in O(1)
- popitem(last=False) evicts LRU in O(1)

### Key Operations
**GET: Check cache, move to front (mark recent)**
1. Check if key in cache (HashMap O(1))
2. If yes: move_to_end (relink pointers O(1))
3. Return value or -1

**PUT: Insert or update, evict if needed**
1. If key exists: move_to_end (mark recent)
2. Insert/update value (HashMap O(1))
3. If size > capacity: popitem(last=False) removes LRU

### Edge Cases
- Capacity=1: every put evicts previous
- Duplicate put: update value, move to end
- Get on empty: return -1 (miss)

### Performance
- All operations: O(1) time
- Space: O(capacity) + overhead (~48B per entry)
- No scanning, no O(n) operations"""

    elif 'kafka' in title_lower:
        return """## Code Explanation (Detailed)

### Producer Patterns
**Fire-and-forget**: Send and ignore response (risky)
**Async**: Send with callback (recommended)
**Sync**: Wait for ack (safest, slowest)

Acks setting:
- acks=0: No confirmation (data loss risk)
- acks=1: Leader ack (good balance)
- acks=all: All replicas (safest, high latency)

### Consumer Patterns
**Simple**: Single consumer, reads all messages
**Consumer Group**: Multiple consumers, auto-assign partitions
**Manual Offset**: Control where to read from

Key pattern: Same key → same partition → ordered"""

    elif 'redis' in title_lower:
        return """## Code Explanation (Detailed)

### Data Structures
- String: Atomic increment, append (cache values, counters)
- List: FIFO queue (rpush/lpop)
- Hash: Object-like (hset/hget)
- Set: Unique values, fast membership (sadd/smembers)
- Sorted Set: Ranked data (zadd/zrevrange for leaderboards)

### Caching Pattern (Cache-Aside)
1. Check cache (fast path, O(1))
2. If miss: fetch from DB (slow)
3. Update cache with TTL (setex)
4. Risk: thundering herd on popular key

### Atomic Operations
- Lua scripts: Complex operations, server-side atomicity
- WATCH/MULTI/EXEC: Optimistic locking
- INCR/ZADD: Inherently atomic"""

    elif 'database' in title_lower or 'shard' in title_lower:
        return """## Code Explanation (Detailed)

### Sharding Key Selection
Hash-based: shard_id = hash(key) % num_shards
- Even distribution (no hot shards from skew)
- Consistent hashing minimizes resharding

### Query Routing
1. Compute shard_id from key
2. Route to master (write) or replica (read)
3. Async replication to other replicas

### Handling Hot Shards
1. Detect via monitoring (QPS per shard)
2. Solutions:
   - Add more replicas (read scaling)
   - Cache hot keys locally (in-process)
   - Split shard (expensive but permanent)

### Resharding Data
1. Dual-write: write to old and new
2. Migrate: copy data to new shards
3. Verify: checksums match
4. Switch: route to new
5. Cleanup: remove old shards"""

    else:
        return """## Code Explanation (Detailed)

### Implementation Approach
The code demonstrates core patterns and trade-offs.

### Key Operations
Each operation shows algorithm and performance characteristics.

### Concurrency and Atomicity
Locking strategies, race condition prevention.

### Edge Cases
Boundary conditions and error handling.

### Performance Optimization
Techniques for reducing latency and throughput."""

def get_detailed_prd(title):
    """Generate detailed PRD based on title"""
    title_lower = title.lower()

    if 'lru' in title_lower:
        return """## PRD (Detailed)

### Functional Requirements
- Get(key) in O(1): retrieve value, mark recently used
- Put(key, value) in O(1): insert/update, evict LRU if over capacity
- Eviction when full: remove least recently used item
- Consistency: each key maps to one value, size ≤ capacity

### Non-Functional Requirements
- Performance: O(1) get/put, no O(n) operations
- Space: O(capacity) + overhead
- Thread safety: handle concurrent access safely
- Eviction latency: microseconds, not milliseconds

### Success Metrics
- Hit rate 80%+ on typical workloads
- Consistent O(1) latency (< 1μs)
- No memory leaks
- Correct edge cases"""

    elif 'kafka' in title_lower:
        return """## PRD (Detailed)

### Functional Requirements
- Publish messages with optional key
- Consume in order within partition
- Support consumer groups (parallel processing)
- Replicate to ISR (in-sync replicas)
- Configurable retention (time/size based)

### Non-Functional Requirements
- Throughput: millions msgs/sec
- Latency: < 10ms publish, < 100ms delivery
- Availability: 99.99% uptime
- Durability: survive broker failures
- Optional: exactly-once semantics

### Success Metrics
- Replication latency < 100ms
- Consumer lag < 1000
- Zero message loss
- Broker recovery < 30s"""

    elif 'redis' in title_lower:
        return """## PRD (Detailed)

### Functional Requirements
- Store key-value with optional TTL
- Support strings, lists, sets, hashes, sorted sets
- Atomic INCR, APPEND, ZADD operations
- Optional persistence (RDB, AOF)
- Master-slave replication

### Non-Functional Requirements
- Latency: < 1ms for get/set
- Throughput: 100K-1M ops/sec
- Memory: all in-memory (set maxmemory policy)
- Availability: sentinel or cluster HA
- Durability: optional (can lose data without persistence)

### Success Metrics
- Hit rate > 95% for caching
- Latency p99 < 10ms
- Memory utilization < 80%
- Replication lag < 1s"""

    elif 'database' in title_lower or 'shard' in title_lower:
        return """## PRD (Detailed)

### Functional Requirements
- Partition data across multiple shards
- Route queries to correct shard
- Replicate within each shard
- Support resharding (add/remove shards)
- Cross-shard scatter-gather queries

### Non-Functional Requirements
- Scalability: 100+ shards, petabyte scale
- Availability: 99.99%, auto-failover
- Latency: < 100ms single-shard, < 500ms cross-shard
- Consistency: strong within shard, eventual across shards
- Operational simplicity: auto-rebalance, monitoring

### Success Metrics
- Even data distribution (< 10% skew)
- Even traffic distribution (< 10% skew)
- Resharding in < 1 hour
- Query routing overhead < 1ms"""

    else:
        return """## PRD (Detailed)

### Functional Requirements
- Core operations work correctly
- Explicit error handling
- Consistency guarantees defined
- Monitoring and observability

### Non-Functional Requirements
- Performance targets met
- Availability SLA achieved
- Scalability headroom
- Cost efficient

### Success Metrics
- Benchmarks met
- Uptime targets met
- Resource budgets
- No data loss"""

def replace_prd_and_code(content):
    """Replace generic PRD and Code Explanation sections"""

    # Extract title
    title_match = re.match(r'# (.+)', content)
    title = title_match.group(1) if title_match else "System"

    # Get detailed versions
    detailed_prd = get_detailed_prd(title)
    detailed_code = get_detailed_code_explanation(title)

    # Remove old generic PRD (keep section marker but replace content)
    content = re.sub(
        r'## PRD\n\n\*\*Functional Requirements:\*\*.*?(?=\n## )',
        '## PRD\n\n',
        content,
        count=1,
        flags=re.DOTALL
    )

    # Insert detailed PRD after the marker
    prd_marker_pos = content.find('## PRD\n\n')
    if prd_marker_pos >= 0:
        insert_pos = prd_marker_pos + len('## PRD\n\n')
        prd_content = detailed_prd.replace('## PRD (Detailed)\n\n', '')
        content = content[:insert_pos] + prd_content + '\n\n' + content[insert_pos:]

    # Remove old Code Explanation if exists
    content = re.sub(
        r'\n## Code Explanation\n\nThe provided.*?(?=\n## |\Z)',
        '',
        content,
        flags=re.DOTALL
    )

    # Insert detailed code before Architecture/Design
    flow_match = re.search(r'\n## (Architecture|Design|Implementation)', content)
    if flow_match:
        insert_pos = flow_match.start()
        content = content[:insert_pos] + '\n\n' + detailed_code + '\n' + content[insert_pos:]

    return content

def process_all_files():
    """Process all markdown files"""
    base_path = Path('/home/sbisw/github/datastructures/docs/system_design')

    count = 0
    for md_file in sorted(base_path.rglob('*.md')):
        if md_file.name == 'README.md':
            continue

        try:
            with open(md_file, 'r') as f:
                content = f.read()

            enhanced = replace_prd_and_code(content)

            if enhanced != content:
                with open(md_file, 'w') as f:
                    f.write(enhanced)
                count += 1
        except Exception as e:
            print(f"Error in {md_file.name}: {e}")

    return count

if __name__ == '__main__':
    updated = process_all_files()
    print(f"Enhanced {updated} files with detailed PRD and Code Explanation")
