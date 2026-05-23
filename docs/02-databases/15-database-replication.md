# Database Replication & Failover

Keep data synchronized across multiple database instances and automatically promote replicas when primary fails.

---

## ⚖️ Replication Trade-offs

### Replication Strategy Comparison

| Strategy | Latency | Consistency | Availability | Use Case |
|----------|---------|-------------|---|----------|
| **Synchronous** | High (waits for replicas) | Strong | 99.5% | Financial systems |
| **Asynchronous** | Low (replica lags) | Eventual | 99.9% | Social media, analytics |
| **Semi-sync** | Medium | Eventual+ | 99.8% | E-commerce |
| **Logical** | Medium | Eventual | High | Cross-DB replication |
| **Physical (WAL)** | Medium | Strong | High | PostgreSQL, MySQL |

### RTO vs. RPO Trade-off

```
RTO (Recovery Time Objective): How fast to restore service
RPO (Recovery Point Objective): How much data can be lost

Financial system:
  RTO: 1 minute
  RPO: 0 (no data loss - synchronous replication)
  Cost: High (replication waits for all replicas)

Social media:
  RTO: 5 minutes
  RPO: 5 minutes of data
  Cost: Low (async replication)

  Diagram:
  
  Sync Rep: RTO=1min, RPO=0
  ├─ All writes wait for replicas
  └─ Slower writes (strong consistency)
  
  Async Rep: RTO=5min, RPO=5min
  ├─ Writes don't wait
  └─ Fast writes (eventual consistency)
```

### Number of Replicas Impact

| Replicas | Availability | Consistency | Cost | Recovery Time |
|----------|---|---|---|---|
| **1 (Primary only)** | 99.0% | N/A | $100/mo | Manual |
| **3 (1 primary + 2)** | 99.9% | Eventual | $300/mo | 2 minutes |
| **5 (Multi-region)** | 99.99% | Eventual | $500/mo | 30 seconds |
| **7+ (Consensus)** | 99.999% | Strong | $700+/mo | <10 seconds |

---

## 🏗️ Replication Patterns

### Pattern 1: Master-Replica (Simple)

```
Write Flow:
  Client → Primary DB (stores data)
                ↓
           Log entry created
                ↓
           Replica 1, Replica 2 (async)

Read Flow:
  Client → Load Balancer
              ↓
          Route to Replicas
          (any replica is OK)
              ↓
          Eventual consistency
          (replica lag: 0-100ms)

Pros: Simple, scales reads
Cons: Replica lag causes stale reads
```

### Pattern 2: Multi-Master (Active-Active)

```
Client A → Primary 1 (US-East)
              ↓
          Write to both
          Primary 1 AND Primary 2
              ↓
          Primary 2 (EU)
              ↓
          Client B reads latest

Benefits:
  - No single point of failure
  - Low latency writes (local write)
  - Disaster recovery ready
  
Challenges:
  - Conflict resolution (A and B write same key)
  - Network partition (split brain)
  - Consistency complex
```

### Pattern 3: Cascading Replication

```
Primary (US)
  ↓ (logs)
Replica 1 (US-West) - gets logs from primary
  ↓ (logs)
Replica 2 (EU) - gets logs from Replica 1
  ↓ (logs)
Replica 3 (APAC) - gets logs from Replica 2

Latency: Primary → Replica 1: 100ms
         Replica 1 → Replica 2: 200ms (total)
         Replica 2 → Replica 3: 300ms (total)

Saves bandwidth on primary but increases lag
```

### Pattern 4: Consensus-Based (Raft)

```
5 Replicas (Raft cluster):
  ┌─ Replica 1 (Leader)
  ├─ Replica 2
  ├─ Replica 3
  ├─ Replica 4
  └─ Replica 5

Write flow:
  1. Client writes to Leader
  2. Leader sends append request to all
  3. Majority (3/5) ack
  4. Leader commits
  5. All followers catch up

Strong consistency: Majority agreement required
```

---

## 🔍 Replication Mechanisms

### Write-Ahead Logging (WAL)

```python
# Physical replication using WAL

class WALReplication:
    def __init__(self):
        self.wal_log = []  # Write-ahead log
        self.replicas = []
    
    def write(self, data):
        # Step 1: Write to WAL first
        wal_entry = {'type': 'write', 'data': data, 'lsn': len(self.wal_log)}
        self.wal_log.append(wal_entry)
        
        # Step 2: Apply to primary
        self.apply(wal_entry)
        
        # Step 3: Async replicate to followers
        for replica in self.replicas:
            replica.receive_wal(wal_entry)
    
    def apply(self, entry):
        # Apply write to data structures
        print(f"Applied: {entry}")
    
    def add_replica(self, replica):
        self.replicas.append(replica)
        # Catch up replica with current log
        for entry in self.wal_log:
            replica.receive_wal(entry)

class Replica:
    def __init__(self, name):
        self.name = name
        self.applied_lsn = 0
        self.wal = []
    
    def receive_wal(self, entry):
        self.wal.append(entry)
        self.apply(entry)
    
    def apply(self, entry):
        print(f"{self.name}: Applied LSN {entry['lsn']}")
```

### Binary Log Replication

```python
# Logical replication using binary log (MySQL style)

class BinaryLogReplication:
    def __init__(self):
        self.binlog = []
        self.position = 0
    
    def execute_write(self, sql):
        """Execute write and add to binlog"""
        # Execute on primary
        print(f"Primary: Executing {sql}")
        
        # Add to binary log
        event = {
            'position': self.position,
            'sql': sql,
            'timestamp': time.time()
        }
        self.binlog.append(event)
        self.position += 1
        
        return event
    
    def get_binlog_since(self, position):
        """Get events since position for replica"""
        return self.binlog[position:]

# Replica pulls from primary
binlog = BinaryLogReplication()

# Primary executes writes
binlog.execute_write("INSERT INTO users VALUES (1, 'Alice')")
binlog.execute_write("UPDATE users SET email = 'alice@example.com' WHERE id = 1")

# Replica connects and fetches
events = binlog.get_binlog_since(0)
for event in events:
    print(f"Replica applying: {event['sql']}")
```

---

## 🔄 Failover Mechanisms

### Automatic Failover with Raft

```python
from enum import Enum
import time
import random

class NodeState(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

class RaftNode:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.state = NodeState.FOLLOWER
        self.term = 0
        self.voted_for = None
        self.log = []
        self.election_timeout = random.uniform(0.15, 0.3)
        self.last_heartbeat = time.time()
    
    def heartbeat_received(self):
        """Reset election timeout when heartbeat from leader"""
        self.last_heartbeat = time.time()
    
    def check_election_timeout(self):
        """Start election if no heartbeat"""
        if time.time() - self.last_heartbeat > self.election_timeout:
            return True
        return False
    
    def start_election(self):
        """Become candidate and request votes"""
        self.state = NodeState.CANDIDATE
        self.term += 1
        self.voted_for = self.node_id
        
        votes = 1  # Vote for self
        for peer in self.peers:
            if peer.grant_vote(self.node_id, self.term):
                votes += 1
        
        # Win if majority votes
        if votes > len(self.peers) / 2:
            self.become_leader()
            return True
        return False
    
    def become_leader(self):
        """Become leader and start heartbeats"""
        self.state = NodeState.LEADER
        print(f"Node {self.node_id} became leader at term {self.term}")
        self.send_heartbeats()
    
    def send_heartbeats(self):
        """Send heartbeats to all followers"""
        for peer in self.peers:
            peer.heartbeat_received()
    
    def grant_vote(self, candidate_id, term):
        """Grant vote if valid election"""
        if term > self.term:
            self.term = term
            self.voted_for = candidate_id
            return True
        return False
    
    def append_entry(self, data):
        """Append write to log (only leader)"""
        if self.state != NodeState.LEADER:
            return False
        
        entry = {'term': self.term, 'data': data}
        self.log.append(entry)
        return True

# Test failover
nodes = [RaftNode(i, []) for i in range(5)]
for node in nodes:
    node.peers = [n for n in nodes if n.node_id != node.node_id]

# Elect initial leader
print("Initial election:")
nodes[0].start_election()

# Simulate leader failure and new election
print("\nSimulating leader failure:")
nodes[0].state = NodeState.FOLLOWER
nodes[0].last_heartbeat = 0

# Trigger new election on another node
print("New election after leader failure:")
nodes[1].last_heartbeat = 0
nodes[1].start_election()
```

### Manual Failover with Promotion Script

```python
class ManualFailoverManager:
    def __init__(self, primary, replicas):
        self.primary = primary
        self.replicas = replicas
        self.promoted_replica = None
    
    def detect_primary_failure(self):
        """Check if primary is down"""
        try:
            self.primary.ping()
            return False
        except Exception:
            return True
    
    def select_best_replica(self):
        """Select replica with least lag"""
        best = None
        min_lag = float('inf')
        
        for replica in self.replicas:
            lag = replica.get_replication_lag()
            if lag < min_lag and replica.is_healthy():
                best = replica
                min_lag = lag
        
        return best
    
    def promote_replica(self, replica):
        """Promote replica to new primary"""
        print(f"Promoting {replica.name} to primary")
        
        # Step 1: Verify replica is caught up
        if replica.get_replication_lag() > 100:
            raise Exception("Replica too far behind")
        
        # Step 2: Stop replica reads
        replica.stop_read_replica_mode()
        
        # Step 3: Reset master info
        replica.reset_master()
        
        # Step 4: Update app config
        self.primary = replica
        self.promoted_replica = replica
        
        print(f"Failover complete: {replica.name} is now primary")
    
    def failover(self):
        """Execute complete failover"""
        if not self.detect_primary_failure():
            print("Primary is healthy, no failover needed")
            return
        
        print("Primary failure detected")
        replica = self.select_best_replica()
        
        if replica is None:
            raise Exception("No healthy replicas available")
        
        self.promote_replica(replica)

class Replica:
    def __init__(self, name):
        self.name = name
        self.replication_lag = 0  # milliseconds
        self.healthy = True
    
    def get_replication_lag(self):
        return self.replication_lag
    
    def is_healthy(self):
        return self.healthy
    
    def stop_read_replica_mode(self):
        print(f"{self.name}: Stopping read-only mode")
    
    def reset_master(self):
        print(f"{self.name}: Reset as master")
    
    def ping(self):
        if not self.healthy:
            raise Exception("Replica down")

# Test manual failover
primary = Replica("primary")
replicas = [
    Replica("replica-1"),
    Replica("replica-2"),
    Replica("replica-3")
]

manager = ManualFailoverManager(primary, replicas)

# Simulate failure
print("Primary fails:")
primary.healthy = False
replicas[0].replication_lag = 10  # 10ms behind
replicas[1].replication_lag = 50
replicas[2].replication_lag = 100

manager.failover()
```

---

## 📊 Replication Metrics

### Replication Lag (Seconds Behind Master)

```
Ideal: < 100ms (0.1 seconds)
Acceptable: < 1 second
Warning: 1-5 seconds
Critical: > 5 seconds

Causes of high lag:
- Network congestion
- Large writes (DDL, bulk insert)
- Slow replica disk I/O
- High read load on replica

Monitoring:
  SHOW SLAVE STATUS; (MySQL)
  SELECT now() - pg_last_wal_receive_lsn() (PostgreSQL)
```

### Recovery Time & Data Loss

```
Synchronous replication:
  RTO (Recovery Time): 1 minute (promote replica)
  RPO (Recovery Point): 0 (no data loss)
  Latency impact: +5-10ms per write

Asynchronous replication:
  RTO: 5 minutes (detect failure + promote)
  RPO: Up to 5 seconds of data
  Latency impact: Minimal (<1ms)

Semi-synchronous:
  RTO: 2-3 minutes
  RPO: < 1 second
  Latency: +2-3ms per write
```

### Availability Calculation

```
Single primary:
  Availability = 99.0% (9 hours downtime/year)
  
Master-Replica (async):
  With automatic failover: 99.9% (8.7 hours/year)
  
3-node Raft cluster:
  Survives 1 failure: 99.99% (52 minutes/year)
  
5-node Raft cluster:
  Survives 2 failures: 99.99% (52 minutes/year)
```

---

## ❓ Interview Q&A

**Q1: Design replication for e-commerce system (1M orders/day, 0 data loss)**

A:
- Requirement: No data loss (RPO = 0)
- Solution: Synchronous replication to 2 replicas
- Topology: Primary (US-East) + Replica 1 (US-West) + Replica 2 (EU)
- Write flow:
  1. Write to WAL on primary
  2. Send to replicas
  3. Wait for majority (2/3) ack
  4. Commit to client
- Trade-off: Writes slower (+10-20ms) but guaranteed consistency
- Failover: Automatic Raft-based promotion (< 1 minute)

**Q2: How to reduce replication lag from 5 seconds to < 100ms?**

A:
- Identify bottleneck:
  - Check replica CPU/memory (is it slow?)
  - Check network latency (is it distant?)
  - Check write throughput (are writes too large?)
  
- Solutions by cause:
  1. Slow replica: Add CPU/memory or parallelized replication
  2. Network: Use regional replica closer to source
  3. Large writes: Implement write batching, reduce DDL size
  
- Monitoring: SELECT Seconds_Behind_Master (MySQL)

**Q3: Split brain scenario - two nodes think they're leader, what happens?**

A:
- Problem: Primary fails, replicas don't know
- Old approach: Manual failover (ops team decides)
  - Risk: Both old and new primary accept writes → divergence
  
- Modern approach: Consensus (Raft/Paxos)
  - Requires majority (3 out of 5 nodes)
  - Minority leader steps down
  - Ensures single writer
  
- Protection: Use quorum writes
  - Write succeeds only if majority acknowledges
  - Prevents split brain by enforcing single writer

**Q4: Failover causes 100 failed orders to reprocess, how to prevent?**

A:
- Cause: Orders between checkpoint and failover lost
- Solution: Idempotent processing
  - Each order has unique ID
  - On failover, reprocess orders from checkpoint
  - If order already executed, skip silently
  
- Implementation:
  ```
  order_id = "order_12345"
  order_hash = MD5(order_id)
  SET order:$order_id:status = "processing"
  
  Execute order
  
  SET order:$order_id:status = "completed"
  
  On failover, check: IS order:$order_id:status EXISTS?
  If yes, skip reprocessing
  ```

**Q5: What if replica falls 1 hour behind during traffic spike?**

A:
- Monitor every 30 seconds
- At 1-hour lag, trigger alert
  
- Temporary fix:
  1. Disable read from this replica (temporarily)
  2. Let it catch up
  3. Re-enable when lag < 1 second
  
- Permanent fix:
  1. Increase replica resources
  2. Implement parallel replication (if supported)
  3. Archive old logs to separate storage

**Q6: Multi-master replication - how to handle write conflicts?**

A:
- Problem: A writes to US, B writes to EU, same key
  ```
  US: user:123:email = "alice@us.com"  (time: 10:00:00)
  EU: user:123:email = "alice@eu.com"  (time: 10:00:05)
  
  Both replicate, conflict!
  ```
  
- Resolution strategies:
  1. Last-write-wins: Keep later timestamp (10:00:05 wins)
  2. Application logic: Ask app which is correct
  3. Version vectors: Track causality, merge if possible
  4. Consensus: 3-way merge like Git
  
- Best: Avoid by routing writes to single region
  - User routed to US always
  - EU handles reads only (eventual consistency)

---

## 🧪 Practical Exercises

### Exercise 1: Implement Master-Replica with Lag Monitoring (Easy)

**Problem:** Build replication system for 100K orders/day. Track replica lag, alert if > 1 second.

**Solution:**

```python
import time
import threading
from collections import deque

class ReplicationSystem:
    def __init__(self):
        self.primary_log = []  # Write-ahead log
        self.replica_applied_lsn = 0  # Last applied log sequence number
        self.lag_history = deque(maxlen=100)
        self.start_time = time.time()
    
    def write(self, data):
        """Write to primary and append to log"""
        lsn = len(self.primary_log)
        entry = {
            'lsn': lsn,
            'data': data,
            'timestamp': time.time()
        }
        self.primary_log.append(entry)
        return lsn
    
    def replicate(self, batch_size=10):
        """Simulate async replication"""
        # Replica reads logs and applies them
        while self.replica_applied_lsn < len(self.primary_log):
            end_lsn = min(
                self.replica_applied_lsn + batch_size,
                len(self.primary_log)
            )
            
            for i in range(self.replica_applied_lsn, end_lsn):
                entry = self.primary_log[i]
                self.apply_to_replica(entry)
                self.replica_applied_lsn = i + 1
            
            time.sleep(0.01)  # Simulate replication delay
    
    def apply_to_replica(self, entry):
        """Apply write to replica"""
        pass  # In production: execute SQL
    
    def get_replication_lag(self):
        """Calculate lag in seconds"""
        if not self.primary_log:
            return 0
        
        latest_primary = self.primary_log[-1]['timestamp']
        lag = time.time() - latest_primary
        self.lag_history.append(lag)
        return lag
    
    def get_lag_stats(self):
        """Return lag statistics"""
        if not self.lag_history:
            return {'avg': 0, 'max': 0, 'p99': 0}
        
        lags = sorted(self.lag_history)
        return {
            'avg': sum(lags) / len(lags),
            'max': max(lags),
            'p99': lags[int(len(lags) * 0.99)]
        }
    
    def check_lag_alert(self, threshold=1.0):
        """Alert if lag exceeds threshold"""
        lag = self.get_replication_lag()
        if lag > threshold:
            print(f"ALERT: Replication lag {lag:.2f}s exceeds {threshold}s")
            return True
        return False

# Test
repl = ReplicationSystem()

# Write thread
def write_orders():
    for i in range(100):
        repl.write(f"order_{i}")
        time.sleep(0.01)

# Replication thread
def replicate():
    repl.replicate(batch_size=5)

write_thread = threading.Thread(target=write_orders)
repl_thread = threading.Thread(target=replicate)

write_thread.start()
repl_thread.start()

# Monitor lag
while repl_thread.is_alive():
    repl.check_lag_alert(threshold=1.0)
    time.sleep(0.1)

write_thread.join()
repl_thread.join()

stats = repl.get_lag_stats()
print(f"\nReplication lag stats:")
print(f"  Average: {stats['avg']:.3f}s")
print(f"  Max: {stats['max']:.3f}s")
print(f"  P99: {stats['p99']:.3f}s")
```

---

### Exercise 2: Automatic Failover with Health Checks (Medium)

**Problem:** Detect primary failure and automatically promote replica. Minimize downtime to < 1 minute.

**Solution:**

```python
import time
from enum import Enum

class NodeRole(Enum):
    PRIMARY = "primary"
    REPLICA = "replica"

class FailoverManager:
    def __init__(self):
        self.nodes = {
            'primary': {'healthy': True, 'lag': 0},
            'replica-1': {'healthy': True, 'lag': 10},
            'replica-2': {'healthy': True, 'lag': 50}
        }
        self.promoted = None
        self.failed_checks = {node: 0 for node in self.nodes}
    
    def health_check(self, node_name):
        """Perform health check on node"""
        node = self.nodes[node_name]
        
        # Simulate health check
        if node['healthy']:
            self.failed_checks[node_name] = 0
            return True
        else:
            self.failed_checks[node_name] += 1
            return False
    
    def should_failover(self):
        """Trigger failover after 3 failed checks"""
        for node in ['primary']:
            if self.failed_checks[node] >= 3:
                return True
        return False
    
    def select_best_replica(self):
        """Select replica with lowest lag"""
        best = None
        min_lag = float('inf')
        
        for node_name, node_data in self.nodes.items():
            if node_name != 'primary' and node_data['healthy']:
                if node_data['lag'] < min_lag:
                    best = node_name
                    min_lag = node_data['lag']
        
        return best
    
    def promote(self, replica_name):
        """Promote replica to primary"""
        print(f"Promoting {replica_name} to primary")
        
        # Update role
        self.promoted = replica_name
        self.nodes['primary']['healthy'] = False
        self.nodes[replica_name]['lag'] = 0  # Primary has no lag
        
        return replica_name

# Test failover
manager = FailoverManager()

print("Initial state:")
for node, data in manager.nodes.items():
    print(f"  {node}: healthy={data['healthy']}, lag={data['lag']}ms")

# Simulate primary failure
print("\nSimulating primary failure...")
manager.nodes['primary']['healthy'] = False

for check_num in range(5):
    for node in manager.nodes:
        manager.health_check(node)
    
    print(f"Check {check_num + 1}: failed_checks={manager.failed_checks['primary']}")
    
    if manager.should_failover():
        print("\nFailover triggered!")
        replica = manager.select_best_replica()
        manager.promote(replica)
        print(f"New primary: {manager.promoted}")
        break
    
    time.sleep(0.5)
```

---

### Exercise 3: Write-Ahead Logging Implementation (Medium)

**Problem:** Implement WAL to ensure no write is lost. Support crash recovery.

**Solution:**

```python
import json
import os

class WriteAheadLog:
    def __init__(self, log_file='wal.log'):
        self.log_file = log_file
        self.entries = []
        self.committed_lsn = 0
    
    def write_entry(self, data, lsn):
        """Append entry to WAL"""
        entry = {
            'lsn': lsn,
            'data': data,
            'timestamp': time.time()
        }
        
        # Write to disk immediately (durability)
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        
        self.entries.append(entry)
        return lsn
    
    def commit(self, lsn):
        """Mark LSN as committed"""
        self.committed_lsn = lsn
    
    def recover(self):
        """Recover from crash using WAL"""
        recovered = []
        
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                for line in f:
                    entry = json.loads(line.strip())
                    recovered.append(entry)
        
        return recovered

# Test crash recovery
import tempfile
import time

with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
    log_file = f.name

try:
    # Write phase
    wal = WriteAheadLog(log_file)
    
    print("Writing entries:")
    for i in range(5):
        wal.write_entry(f"order_{i}", i)
        print(f"  Wrote entry {i}")
    
    # Simulate crash
    print("\nSimulating crash...")
    
    # Recovery phase
    wal2 = WriteAheadLog(log_file)
    recovered = wal2.recover()
    
    print(f"\nRecovered {len(recovered)} entries:")
    for entry in recovered:
        print(f"  LSN {entry['lsn']}: {entry['data']}")
    
finally:
    os.unlink(log_file)
```

---

### Exercise 4: Multi-Master with Conflict Resolution (Hard)

**Problem:** Two regions can write independently. Handle conflicts when same record modified in both regions.

**Solution:**

```python
import time
from datetime import datetime

class VectorClock:
    """Track causality between writes"""
    def __init__(self, node_id):
        self.node_id = node_id
        self.clock = {}
    
    def increment(self):
        """Increment clock for this node"""
        self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1
    
    def merge(self, other_clock):
        """Merge with received clock"""
        for node_id, value in other_clock.items():
            self.clock[node_id] = max(
                self.clock.get(node_id, 0),
                value
            )
    
    def happens_before(self, other):
        """Check if this clock happened before other"""
        less_or_equal = all(
            self.clock.get(n, 0) <= other.clock.get(n, 0)
            for n in set(self.clock.keys()) | set(other.clock.keys())
        )
        less = any(
            self.clock.get(n, 0) < other.clock.get(n, 0)
            for n in set(self.clock.keys()) | set(other.clock.keys())
        )
        return less_or_equal and less
    
    def concurrent_with(self, other):
        """Check if concurrent (neither happens before)"""
        return not (
            self.happens_before(other) or other.happens_before(self)
        )

class MultiMasterDB:
    def __init__(self, region_id):
        self.region_id = region_id
        self.data = {}
        self.versions = {}  # track version with vector clock
        self.vclock = VectorClock(region_id)
    
    def write(self, key, value):
        """Local write"""
        self.vclock.increment()
        
        version = {
            'value': value,
            'vclock': self.vclock.clock.copy(),
            'timestamp': time.time(),
            'region': self.region_id
        }
        
        self.data[key] = value
        self.versions[key] = version
        
        return version
    
    def merge_write(self, key, remote_version):
        """Receive write from other region"""
        
        # If key doesn't exist locally, accept remote
        if key not in self.versions:
            self.data[key] = remote_version['value']
            self.versions[key] = remote_version
            return True
        
        local_version = self.versions[key]
        local_vc = VectorClock('local')
        local_vc.clock = local_version['vclock']
        
        remote_vc = VectorClock('remote')
        remote_vc.clock = remote_version['vclock']
        
        # Case 1: Remote is causally later
        if local_vc.happens_before(remote_vc):
            self.data[key] = remote_version['value']
            self.versions[key] = remote_version
            return True
        
        # Case 2: Local is causally later
        if remote_vc.happens_before(local_vc):
            return False  # Keep local
        
        # Case 3: Concurrent writes (conflict)
        if local_vc.concurrent_with(remote_vc):
            # Last-write-wins
            if remote_version['timestamp'] > local_version['timestamp']:
                self.data[key] = remote_version['value']
                self.versions[key] = remote_version
                print(f"CONFLICT on {key}: Remote {remote_version['value']} wins (newer)")
                return True
            else:
                print(f"CONFLICT on {key}: Local {self.data[key]} wins (older timestamp)")
                return False

# Test multi-master
us_db = MultiMasterDB('us-east')
eu_db = MultiMasterDB('eu')

print("=== Scenario 1: Sequential writes (no conflict) ===")
us_ver = us_db.write('user:123:email', 'alice@us.com')
print(f"US wrote: {us_db.data['user:123:email']}")

eu_db.merge_write('user:123:email', us_ver)
print(f"EU merged: {eu_db.data['user:123:email']}")

print("\n=== Scenario 2: Concurrent writes (conflict) ===")
us_db2 = MultiMasterDB('us-east')
eu_db2 = MultiMasterDB('eu')

# Both write to same key
time.sleep(0.01)
us_ver2 = us_db2.write('product:456:price', '100')
time.sleep(0.01)
eu_ver2 = eu_db2.write('product:456:price', '95')

print(f"US wrote: {us_db2.data['product:456:price']}")
print(f"EU wrote: {eu_db2.data['product:456:price']}")

# Replicate to each other
print(f"\nUS receives EU write:")
eu_db2.merge_write('product:456:price', us_ver2)
print(f"EU data: {eu_db2.data['product:456:price']}")

print(f"\nEU receives US write:")
us_db2.merge_write('product:456:price', eu_ver2)
print(f"US data: {us_db2.data['product:456:price']}")
```

---

## 🎯 When to Use Each Strategy

| Requirement | Strategy | Tradeoff |
|-------------|----------|----------|
| **0 data loss** | Synchronous + Quorum | Slow writes (+10-20ms) |
| **Fast writes** | Async + Last-write-wins | May lose data |
| **HA + Consistency** | Semi-sync + Raft | Medium latency |
| **Multi-region** | Multi-master with CRDTs | Eventual consistency |
| **Disaster recovery** | Cascading replicas | Higher lag |

---

**Last updated:** 2026-05-22
