# Change Data Capture (CDC)

**Level:** L4-L5
**Time to read:** ~30 min

Stream database changes to downstream systems in real-time for replication, analytics, and event-driven architectures.

---

## ⚖️ CDC Approach Trade-offs

### CDC Method Comparison

| Method | Latency | Complexity | Overhead | Best For |
|--------|---------|-----------|----------|----------|
| **Query-based** | 5-60 sec | Low | High | Low-frequency changes |
| **Log-based** | Sub-second | Medium | Low | High-volume changes |
| **Query rewrite** | 10-30 sec | High | Medium | Complex schemas |
| **Trigger-based** | < 1 sec | High | High | Critical data |
| **Event log** | Sub-second | Medium | Low | Audit, replay |

### Latency vs. Load

```
Query-based CDC:
  ├─ Poll every 60 seconds
  ├─ Latency: 0-60 seconds (average 30s)
  ├─ Load: 1 query/minute
  ├─ Database impact: Minimal
  
Log-based CDC:
  ├─ Stream logs instantly
  ├─ Latency: 0-100ms
  ├─ Load: Stream of events
  ├─ Database impact: Moderate (log I/O)
  
Trigger-based CDC:
  ├─ Synchronous with writes
  ├─ Latency: < 1ms
  ├─ Load: Every write spawns trigger
  ├─ Database impact: High (trigger overhead)
```

---

## 🏗️ CDC Patterns

### Pattern 1: Query-based (Polling)

```
Loop every 60 seconds:
  1. SELECT * FROM users WHERE updated_at > last_checkpoint
  2. For each row: Send to Kafka
  3. Update checkpoint

Problems:
  ├─ Latency: 60 seconds (stale data)
  ├─ Expensive: Full table scans
  ├─ Missed deletes: Only captures SELECTs
```

### Pattern 2: Log-based (MySQL Binlog)

```
MySQL Binlog:
  ├─ Binary log contains all writes
  ├─ Debezium reads binlog in real-time
  ├─ Converts to CDC events
  
Example:
  Binlog: INSERT INTO users VALUES (1, 'Alice')
  ↓
  CDC Event: {op: 'insert', user_id: 1, name: 'Alice', ts: 123456}
  ↓
  Kafka Topic: 'mysql.users'
```

### Pattern 3: Event Log (Event Sourcing)

```
Instead of updating records, append events:

User created:
  Event: {type: 'user_created', user_id: 1, name: 'Alice', ts: 123456}

User updated:
  Event: {type: 'user_updated', user_id: 1, name: 'Bob', ts: 123457}

Event log:
  ├─ Immutable audit trail
  ├─ Can replay to any point in time
  ├─ Natural CDC (events ARE changes)
```

### Pattern 4: Trigger-based

```
CREATE TRIGGER user_changes AFTER INSERT/UPDATE/DELETE ON users
BEGIN
  IF NEW.id IS NOT NULL THEN
    INSERT INTO _cdc_log (op, user_id, data) VALUES ('insert', NEW.id, ...);
  ELSE
    INSERT INTO _cdc_log (op, user_id, data) VALUES ('delete', OLD.id, ...);
  END;
END;

Every write triggers log entry (synchronous)
Latency: < 1ms
Cost: Trigger overhead on every write
```

---

## 📊 CDC Implementation

### Log-based CDC with Debezium

```python
# Debezium reads MySQL binlog and publishes to Kafka

class CDCConnector:
    def __init__(self, database, kafka_broker):
        self.database = database
        self.kafka_broker = kafka_broker
        self.last_lsn = None
        self.topic_map = {}
    
    def read_binlog(self):
        """Read database binary log"""
        # In production: Use Debezium connector
        # For simulation: Track changes
        pass
    
    def stream_changes(self, table_name):
        """Stream changes for table to Kafka"""
        changes = self._get_changes_since_lsn(table_name)
        
        for change in changes:
            # Convert to CDC event
            event = {
                'op': change['operation'],  # 'insert', 'update', 'delete'
                'table': table_name,
                'data': change['data'],
                'ts': change['timestamp'],
                'lsn': change['lsn']
            }
            
            # Publish to Kafka
            topic = f"{self.database}.{table_name}"
            self._publish_to_kafka(topic, event)
            
            # Update checkpoint
            self.last_lsn = change['lsn']
    
    def _get_changes_since_lsn(self, table_name):
        """Get changes since last LSN (log sequence number)"""
        return []
    
    def _publish_to_kafka(self, topic, event):
        """Publish event to Kafka"""
        pass

# Usage
cdc = CDCConnector('orders_db', 'localhost:9092')

# Stream orders table to Kafka
# cdc.stream_changes('orders')
```

### Query-based CDC (Polling)

```python
import time
from datetime import datetime, timedelta

class QueryBasedCDC:
    def __init__(self, database, poll_interval=60):
        self.database = database
        self.poll_interval = poll_interval
        self.last_checkpoint = None
    
    def poll_changes(self, table_name, ts_column='updated_at'):
        """Poll for changes every interval"""
        while True:
            checkpoint = self.last_checkpoint or (datetime.now() - timedelta(days=1))
            
            # Query changes since checkpoint
            query = f"""
            SELECT * FROM {table_name}
            WHERE {ts_column} > '{checkpoint}'
            ORDER BY {ts_column}
            """
            
            changes = self._execute_query(query)
            
            for row in changes:
                # Publish change
                self._publish_change(table_name, row)
                
                # Update checkpoint
                self.last_checkpoint = row[ts_column]
            
            time.sleep(self.poll_interval)
    
    def _execute_query(self, query):
        """Execute query on database"""
        return []
    
    def _publish_change(self, table, row):
        """Publish to downstream system"""
        pass

# Usage
# cdc = QueryBasedCDC('orders_db', poll_interval=60)
# cdc.poll_changes('orders', ts_column='updated_at')
```

---

## ❓ Interview Q&A

**Q1: Real-time sync of 10TB database to analytics system. Design CDC.**

A:
- Requirement: Low latency (< 1 second), high throughput (1M writes/sec)
- Solution: Log-based CDC
  ```
  Primary DB → Binlog → Debezium → Kafka → Data Warehouse
  
  Benefits:
    - Latency: 100-500ms
    - Throughput: Can handle 1M+ events/sec
    - No query overhead on primary
    - Built-in replication
  ```
- Implementation:
  1. Enable binlog on MySQL
  2. Deploy Debezium connector (reads binlog)
  3. Kafka topic per table
  4. Spark/Flink consumes and writes to warehouse
- Monitoring:
  - Kafka lag (target < 100ms)
  - Binlog position (not falling behind)
  - Data validation (count records in source vs. warehouse)

**Q2: CDC adds 5% latency to writes, how to reduce?**

A:
- Cause: Log-based CDC reading binlog synchronously
- Solutions:
  1. Async CDC reads:
     - CDC reads binlog asynchronously
     - Doesn't block writes
     - Risk: Slight lag (acceptable)
  
  2. Reduce Kafka batch size:
     - Smaller batches = faster delivery
     - Trade: More frequent sends (higher CPU)
  
  3. Optimize Debezium:
     - Tune batch.size and linger.ms
     - Default: 16KB batches, 100ms wait
     - Faster: 1KB batches, 10ms wait
  
  4. Local Kafka (same machine):
     - Reduce network latency
     - Kafka close to database

**Q3: Downstream consumer crashed - how to recover without data loss?**

A:
- Problem: Kafka → Warehouse sync stopped
  - Lost 1 hour of data
  
- Solution: Kafka retention + checkpointing
  - Kafka retains 7 days of events
  - Consumer stores checkpoint: "Processed up to LSN 12345"
  
- Recovery:
  ```
  1. Fix consumer code
  2. Restart consumer
  3. Consumer reads checkpoint: LSN 12345
  4. Seeks to Kafka offset for LSN 12345
  5. Processes remaining 1 hour of data
  6. Updates checkpoint
  ```

**Q4: Delete events - how to handle in data warehouse?**

A:
- Problem: Source database: DELETE FROM users WHERE id = 123
  - CDC publishes: {op: 'delete', user_id: 123}
  - Warehouse receives delete event
  - Delete user record
  - But: Aggregate queries already counted this user!
  
- Solution 1: Soft deletes
  - Never DELETE, just set is_deleted = true
  - CDC publishes update event
  - Warehouse updates record
  - Aggregations check is_deleted
  
- Solution 2: Temporal tables
  - Keep history of all versions
  - Track valid_from, valid_to timestamps
  - Query at any point in time
  
- Solution 3: Delete markers
  - Keep delete records in separate table
  - Use left anti-join to exclude deleted IDs
  - Can recover if delete was accidental

**Q5: Cross-database CDC - multiple sources to single warehouse**

A:
- Problem: Have 5 databases, aggregate to data warehouse
  ```
  Orders DB → CDC → Kafka
  Payments DB → CDC → Kafka
  Users DB → CDC → Kafka
  ...
  ↓
  Data Warehouse
  ```
  
- Solution:
  1. Kafka multi-tenancy:
     - Topic per (database, table)
     - orders.orders, payments.payments, users.users
  
  2. Schema registry:
     - Track schema changes
     - Handle schema evolution
  
  3. Timestamp synchronization:
     - Ensure clocks synchronized across databases
     - Use LSN/version not timestamp
  
  4. Idempotency:
     - Use composite key (database_id, table, row_id)
     - Insert/update idempotent (don't duplicate if reprocessed)

---

## 🧪 Practical Exercises

### Exercise 1: Query-based CDC Implementation (Easy)

**Problem:** Sync user table changes to Kafka every 60 seconds.

**Solution:**

```python
import time
import json
from datetime import datetime, timedelta

class QueryBasedCDC:
    def __init__(self, poll_interval=60):
        self.poll_interval = poll_interval
        self.last_checkpoint = datetime.now() - timedelta(hours=1)
        self.kafka_messages = []
    
    def poll_changes(self, table_data):
        """Poll for changes"""
        # Get current checkpoint
        checkpoint = self.last_checkpoint
        
        # Find changed records (those updated after checkpoint)
        changes = []
        for record in table_data:
            if record['updated_at'] > checkpoint:
                changes.append(record)
        
        # Publish changes
        for record in changes:
            event = {
                'table': 'users',
                'op': record.get('_operation', 'update'),
                'data': record,
                'ts': record['updated_at'].isoformat()
            }
            self.kafka_messages.append(event)
            self.last_checkpoint = max(self.last_checkpoint, record['updated_at'])
        
        return len(changes)
    
    def get_published_events(self):
        """Get all published events"""
        return self.kafka_messages

# Test
cdc = QueryBasedCDC()

# Simulate table data with timestamps
users = [
    {'id': 1, 'name': 'Alice', 'updated_at': datetime.now() - timedelta(seconds=30), '_operation': 'insert'},
    {'id': 2, 'name': 'Bob', 'updated_at': datetime.now() - timedelta(seconds=10), '_operation': 'update'},
    {'id': 3, 'name': 'Charlie', 'updated_at': datetime.now() - timedelta(days=1), '_operation': 'update'},
]

print("Polling for changes:")
changes = cdc.poll_changes(users)
print(f"Found {changes} changes")

events = cdc.get_published_events()
print(f"\nPublished {len(events)} events to Kafka:")
for event in events:
    print(f"  {event['op'].upper()}: user {event['data']['id']} - {event['data']['name']}")
```

---

### Exercise 2: Log-based CDC with LSN Tracking (Medium)

**Problem:** Stream 1M database changes reliably using binlog LSN. Handle crashes.

**Solution:**

```python
import json
from collections import deque

class LogBasedCDC:
    def __init__(self, max_batch_size=100):
        self.binlog = deque()  # Simulated binlog
        self.lsn = 0
        self.checkpoint = 0
        self.max_batch_size = max_batch_size
    
    def add_to_binlog(self, operation, data):
        """Add write to binlog"""
        self.lsn += 1
        entry = {
            'lsn': self.lsn,
            'op': operation,  # 'insert', 'update', 'delete'
            'data': data,
            'ts': 123456789  # Timestamp
        }
        self.binlog.append(entry)
        return self.lsn
    
    def read_since_checkpoint(self):
        """Read binlog entries since last checkpoint"""
        entries = []
        for entry in list(self.binlog):
            if entry['lsn'] > self.checkpoint:
                entries.append(entry)
                if len(entries) >= self.max_batch_size:
                    break
        return entries
    
    def stream_changes(self):
        """Stream changes with checkpoint management"""
        while True:
            # Read batch of changes
            batch = self.read_since_checkpoint()
            
            if not batch:
                return  # No more changes
            
            # Process batch
            for entry in batch:
                event = {
                    'lsn': entry['lsn'],
                    'op': entry['op'],
                    'data': entry['data']
                }
                
                # Publish to Kafka
                self._publish(event)
                
                # Update checkpoint after processing
                self.checkpoint = entry['lsn']
    
    def _publish(self, event):
        """Publish event (simulated)"""
        pass
    
    def get_checkpoint(self):
        """Get current checkpoint (for recovery)"""
        return self.checkpoint

# Test
cdc = LogBasedCDC()

# Simulate writes
print("Simulating database writes:")
cdc.add_to_binlog('insert', {'id': 1, 'name': 'Alice'})
cdc.add_to_binlog('insert', {'id': 2, 'name': 'Bob'})
cdc.add_to_binlog('update', {'id': 1, 'name': 'Alicia'})

print(f"Added 3 entries to binlog (LSN 1-3)")

# Stream changes
print(f"\nBefore streaming: checkpoint = {cdc.get_checkpoint()}")
cdc.stream_changes()
print(f"After streaming: checkpoint = {cdc.get_checkpoint()}")

# Simulate crash and recovery
print(f"\nSimulating crash and recovery...")
print(f"Checkpoint saved: {cdc.checkpoint}")

# New reader starts (reads since checkpoint)
cdc.add_to_binlog('delete', {'id': 2})
remaining = cdc.read_since_checkpoint()
print(f"Recovered reader found {len(remaining)} entries since checkpoint")
```

---

### Exercise 3: Event Sourcing with Replay (Hard)

**Problem:** Build immutable event log. Support replaying to recover state.

**Solution:**

```python
import json
from datetime import datetime

class EventSourcingStore:
    def __init__(self):
        self.event_log = []
        self.snapshots = {}  # user_id → snapshot
    
    def record_event(self, aggregate_id, event_type, data):
        """Record immutable event"""
        event = {
            'version': len(self.event_log) + 1,
            'aggregate_id': aggregate_id,
            'event_type': event_type,
            'data': data,
            'ts': datetime.now().isoformat()
        }
        self.event_log.append(event)
        return event['version']
    
    def get_events(self, aggregate_id, since_version=0):
        """Get all events for aggregate"""
        return [
            e for e in self.event_log
            if e['aggregate_id'] == aggregate_id and e['version'] > since_version
        ]
    
    def replay(self, aggregate_id, to_version=None):
        """Replay events to rebuild state"""
        # Check snapshot (optimization)
        if aggregate_id in self.snapshots:
            snapshot = self.snapshots[aggregate_id]
            state = snapshot['state'].copy()
            since_version = snapshot['version']
        else:
            state = {}
            since_version = 0
        
        # Replay events
        events = self.get_events(aggregate_id, since_version)
        for event in events:
            if to_version and event['version'] > to_version:
                break
            state = self._apply_event(state, event)
        
        return state
    
    def _apply_event(self, state, event):
        """Apply event to state"""
        if event['event_type'] == 'user_created':
            state['id'] = event['data']['user_id']
            state['name'] = event['data']['name']
            state['balance'] = 0
        
        elif event['event_type'] == 'balance_increased':
            state['balance'] = state.get('balance', 0) + event['data']['amount']
        
        elif event['event_type'] == 'balance_decreased':
            state['balance'] = state.get('balance', 0) - event['data']['amount']
        
        return state
    
    def create_snapshot(self, aggregate_id, version):
        """Create snapshot for faster replay"""
        state = self.replay(aggregate_id, to_version=version)
        self.snapshots[aggregate_id] = {
            'version': version,
            'state': state,
            'ts': datetime.now().isoformat()
        }

# Test
store = EventSourcingStore()

# Record events
print("Recording events:")
store.record_event('user_1', 'user_created', {'user_id': 1, 'name': 'Alice'})
store.record_event('user_1', 'balance_increased', {'amount': 100})
store.record_event('user_1', 'balance_decreased', {'amount': 30})
print("  3 events recorded")

# Replay to current state
print(f"\nReplaying user_1:")
state = store.replay('user_1')
print(f"  Current state: {state}")

# Replay to specific version (point-in-time)
print(f"\nReplaying user_1 to version 2 (after balance_increased):")
state_v2 = store.replay('user_1', to_version=2)
print(f"  State at version 2: {state_v2}")

# Create snapshot for faster recovery
print(f"\nCreating snapshot at version 2:")
store.create_snapshot('user_1', 2)
print(f"  Snapshot created (future replays start here)")

# Verify snapshot works
state_from_snapshot = store.replay('user_1')
print(f"  Replayed from snapshot: {state_from_snapshot}")
```

---

**Last updated:** 2026-05-22
