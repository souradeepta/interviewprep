# Eventual Consistency Patterns

Design systems where data eventually synchronizes across replicas while maintaining availability and handling concurrent writes.

---

## ⚖️ Consistency Model Trade-offs

### Consistency Guarantees Comparison

| Model | Read Latency | Write Latency | Cost | Complexity |
|-------|---|---|---|---|
| **Strong** | Slow | Slow | High | Low |
| **Eventual** | Fast | Fast | Low | Medium |
| **Causal** | Medium | Medium | Medium | High |
| **Monotonic** | Medium | Fast | Medium | Medium |

### CAP Theorem Review

```
Choose 2 of 3:
- Consistency: All nodes see same data
- Availability: System always responsive
- Partition tolerance: Survives network split

Consistency + Availability = Single datacenter (unrealistic)
Consistency + Partition = CP (DynamoDB strong, MongoDB)
Availability + Partition = AP (DynamoDB eventual, Cassandra)
```

---

## 🏗️ Eventual Consistency Patterns

### Pattern 1: Read-Your-Write Consistency

```
Problem: Write to primary, read from replica (stale data)
  Time 0: Write "name=Bob" to primary
  Time 10ms: Replica still sees "name=Alice" (lag)
  
Solution: Route reads to primary for 1 second after write
  1. Write to primary
  2. Cache: "I just wrote name=Bob"
  3. For 1 second, read from primary (not replica)
  4. After 1 second, replica caught up, read from replica
```

### Pattern 2: Monotonic Reads

```
Problem: Read from replica A (v1), then replica B (v0, slower sync)
  User sees: v1 → v0 (time goes backwards!)
  
Solution: Sticky reads
  1. First read from replica A (v1)
  2. Subsequent reads must go to A or later (B if B >= A)
  3. Never read from earlier version
```

### Pattern 3: Causal Consistency

```
Problem: Write order matters
  User A: "post a comment"
  User B: "replies to comment"
  
  If B's reply propagates before A's comment, reply is orphaned
  
Solution: Causal ordering
  1. Each write has version vector
  2. Reply write carries: depends_on: [comment_write_version]
  3. Consumer doesn't apply reply until comment is applied
```

### Pattern 4: Conflict Resolution (Last-Write-Wins)

```
Concurrent writes on two regions:
  Region A (time 10:00:00): price = $100
  Region B (time 10:00:05): price = $95
  
Last-write-wins:
  10:00:05 > 10:00:00 → Use $95
  Risk: Earlier write is lost (silent data loss)
```

---

## 📊 Handling Inconsistency

### Conflict Detection

```python
import time

class ConflictDetector:
    def __init__(self):
        self.versions = {}  # key → version vector
    
    def write(self, key, value, version_vector):
        """Write with version vector"""
        if key not in self.versions:
            self.versions[key] = version_vector
        else:
            old_version = self.versions[key]
            # Check if concurrent
            if self._concurrent(old_version, version_vector):
                # Conflict detected!
                return self._resolve_conflict(key, value, old_version, version_vector)
        
        self.versions[key] = version_vector
        return True
    
    def _concurrent(self, v1, v2):
        """Check if versions are concurrent (neither dominates)"""
        # Simplified: if both have happened, it's concurrent
        return v1 != v2
    
    def _resolve_conflict(self, key, value, old_v, new_v):
        """Resolve conflict"""
        if new_v > old_v:
            # New write is later
            return True
        elif new_v < old_v:
            # Old write is later
            return False
        else:
            # Same timestamp, use some tiebreaker
            return value > self.versions[key]
```

### Anti-entropy (Repair)

```
Background process to fix inconsistencies:

Every 6 hours:
  1. Replica A checksums data
  2. Replica B checksums data
  3. Compare checksums
  4. For mismatched data:
     - Copy from A to B (or vice versa)
     - Ensure consistency

Cost: 10% overhead but catches corruption
```

---

## ❓ Interview Q&A

**Q1: Users see different data depending on which server they hit - solution?**

A:
- Problem: Eventual consistency → stale reads
- Solutions:
  1. Read-your-write:
     - Route user's reads to primary after write
     - Cache user → primary mapping for 1 second
     - Trade: Slightly higher latency
  
  2. Sticky reads:
     - Remember which replica user read from
     - Always route to same replica (or newer)
     - Trade: Less load balancing
  
  3. Strong consistency:
     - Replicate synchronously
     - All reads from primary
     - Trade: Slower writes

**Q2: Concurrent writes to same record - how to handle?**

A:
- Problem: User updates profile simultaneously from two devices
  - Phone: name = "Alice Smith"
  - Laptop: name = "Alice Wonderland"
  - Both write at same time
  
- Solutions:
  1. Last-write-wins (simplest):
     - Use timestamp
     - Later write wins
     - Risk: Earlier write silently lost
  
  2. Merge (conflict resolution):
     - Store both versions
     - Ask user to choose
     - Merge automatically if possible
  
  3. Avoid concurrent writes:
     - Optimistic locking: Write includes version
     - Write fails if version doesn't match
     - User retries with new version

**Q3: Replica lag is 5 seconds - users complain about stale data, solution?**

A:
- Cause: Replication bottleneck
  - High write load
  - Slow network to replica
  - Replica underprovisioned
  
- Solutions:
  1. Reduce replica lag:
     - Add more replicas (distribute reads)
     - Upgrade replica hardware
     - Optimize network (local datacenter)
  
  2. Work with eventual consistency:
     - Show "data refreshed 5 seconds ago" to user
     - Provide "refresh now" button (route to primary)
     - Use cache with TTL < 5 seconds
  
  3. Use strong consistency selectively:
     - Reads from primary for critical data
     - Reads from replica for non-critical
     - Balance speed and consistency

**Q4: How to verify data consistency between replicas?**

A:
- Methods:
  1. Checksums:
     - Primary: SHA256(all_data) = ABC123
     - Replica: SHA256(all_data) = ABC123
     - If match, consistent
  
  2. Row counts:
     - SELECT COUNT(*) on both
     - If match, probably consistent
     - Caveat: Doesn't detect incorrect rows
  
  3. Sampling:
     - Compare 1000 random rows
     - If 100% match, assume consistent
     - Faster than full comparison
  
  4. Write verification:
     - Write test record to primary
     - Wait for replication
     - Verify on replica

---

## 🧪 Practical Exercises

### Exercise 1: Read-Your-Write Implementation (Easy)

**Problem:** Ensure users always read their own writes, even with replicas.

**Solution:**

```python
import time

class ReadYourWriteCache:
    def __init__(self):
        self.write_times = {}  # user_id → last_write_time
        self.router = ReadWriteRouter()
    
    def write(self, user_id, key, value):
        """User writes data"""
        self.write_times[user_id] = time.time()
        self.router.write_to_primary(key, value)
    
    def read(self, user_id, key):
        """User reads data"""
        # Check if user wrote recently
        last_write = self.write_times.get(user_id, 0)
        time_since_write = time.time() - last_write
        
        if time_since_write < 1.0:
            # Route to primary (less than 1 second since write)
            return self.router.read_from_primary(key)
        else:
            # Route to replica (enough time for replication)
            return self.router.read_from_replica(key)

class ReadWriteRouter:
    def __init__(self):
        self.primary = {'data': {}}
        self.replica = {'data': {}}
        self.replication_delay = 0.5  # 500ms
    
    def write_to_primary(self, key, value):
        """Write to primary"""
        self.primary['data'][key] = value
        # Schedule replication
        self._schedule_replication(key)
    
    def _schedule_replication(self, key):
        """Simulate async replication"""
        import threading
        def replicate():
            time.sleep(self.replication_delay)
            if key in self.primary['data']:
                self.replica['data'][key] = self.primary['data'][key]
        
        thread = threading.Thread(target=replicate)
        thread.daemon = True
        thread.start()
    
    def read_from_primary(self, key):
        """Read from primary"""
        return self.primary['data'].get(key)
    
    def read_from_replica(self, key):
        """Read from replica"""
        return self.replica['data'].get(key)

# Test
ryw = ReadYourWriteCache()

print("Test 1: Read immediately after write (should get from primary)")
ryw.write('user1', 'name', 'Alice')
time.sleep(0.1)
result = ryw.read('user1', 'name')
print(f"  Result: {result} (from primary)")

print("\nTest 2: Read after 2 seconds (should get from replica)")
time.sleep(2)
result = ryw.read('user1', 'name')
print(f"  Result: {result} (from replica after replication)")
```

---

### Exercise 2: Monotonic Reads (Medium)

**Problem:** Ensure reads never go backwards in time.

**Solution:**

```python
class MonotonicReadRouter:
    def __init__(self):
        self.user_replicas = {}  # user_id → preferred_replica
        self.replicas = {
            'replica_1': {'version': 0},
            'replica_2': {'version': 0},
            'replica_3': {'version': 0}
        }
    
    def read(self, user_id, key, user_context=None):
        """Read with monotonic guarantee"""
        # Check if user has previous replica
        if user_id not in self.user_replicas:
            # First read, choose any replica
            self.user_replicas[user_id] = 'replica_1'
        
        preferred_replica = self.user_replicas[user_id]
        preferred_version = self.replicas[preferred_replica]['version']
        
        # Find replica with >= version
        best_replica = None
        for replica_name, replica_data in self.replicas.items():
            if replica_data['version'] >= preferred_version:
                best_replica = replica_name
                break
        
        if best_replica is None:
            # Preferred replica is ahead, stick with it
            best_replica = preferred_replica
        
        # Update preference for next read
        self.user_replicas[user_id] = best_replica
        
        return f"Read from {best_replica}"
    
    def advance_version(self, replica_name, new_version):
        """Update replica version"""
        self.replicas[replica_name]['version'] = new_version

# Test
router = MonotonicReadRouter()

print("Simulating monotonic reads:")
print(f"Read 1: {router.read('user1', 'key1')}  (version 0)")

# Update replicas
router.advance_version('replica_1', 1)
router.advance_version('replica_2', 0)
router.advance_version('replica_3', 1)

print(f"Read 2: {router.read('user1', 'key1')}  (version >= 0)")

# Version goes backwards on replica_2
router.advance_version('replica_2', 0)
print(f"Read 3: {router.read('user1', 'key1')}  (avoids replica_2)")
```

---

### Exercise 3: Conflict Resolution (Hard)

**Problem:** Two regions write concurrently. Resolve conflicts without losing data.

**Solution:**

```python
from datetime import datetime

class ConflictResolution:
    def __init__(self):
        self.records = {}
        self.conflicts = []
    
    def write(self, record_id, data, timestamp, region):
        """Write with conflict detection"""
        if record_id not in self.records:
            self.records[record_id] = {
                'data': data,
                'timestamp': timestamp,
                'region': region,
                'versions': [{'data': data, 'ts': timestamp, 'region': region}]
            }
        else:
            existing = self.records[record_id]
            if timestamp > existing['timestamp']:
                # New write is later, update
                self.records[record_id] = {
                    'data': data,
                    'timestamp': timestamp,
                    'region': region,
                    'versions': existing['versions'] + [{'data': data, 'ts': timestamp, 'region': region}]
                }
            elif timestamp < existing['timestamp']:
                # Old write wins, ignore
                pass
            else:
                # Same timestamp - CONFLICT
                self.conflicts.append({
                    'record_id': record_id,
                    'data1': existing['data'],
                    'data2': data,
                    'timestamp': timestamp
                })
                # Last-write-wins with region tiebreaker
                if region > existing['region']:
                    self.records[record_id]['data'] = data
    
    def get_record(self, record_id):
        """Get record (resolved value)"""
        return self.records.get(record_id)
    
    def get_conflicts(self):
        """Get detected conflicts"""
        return self.conflicts

# Test
cr = ConflictResolution()

print("Simulating concurrent writes:")

# Write from region A
cr.write('user:1', {'name': 'Alice', 'email': 'alice@a.com'}, 100, 'us-east')
print(f"Write from US-East: name='Alice'")

# Write from region B at same time
cr.write('user:1', {'name': 'Alicia', 'email': 'alice@b.com'}, 100, 'eu')
print(f"Write from EU: name='Alicia'")

conflicts = cr.get_conflicts()
print(f"\nConflicts detected: {len(conflicts)}")
if conflicts:
    for c in conflicts:
        print(f"  Record {c['record_id']}: '{c['data1']['name']}' vs. '{c['data2']['name']}'")

# Resolution
record = cr.get_record('user:1')
print(f"\nResolved value: name='{record['data']['name']}' (from {record['region']})")
```

---

**Last updated:** 2026-05-22
