# Database Backup & Recovery

**Level:** L4-L5
**Time to read:** ~30 min

Protect data with automated backups and enable point-in-time recovery with minimal RTO/RPO.

---

## ⚖️ Backup Strategy Trade-offs

### Backup Types Comparison

| Type | Frequency | Time | Storage | Recovery | Cost |
|------|-----------|------|---------|----------|------|
| **Full** | Daily/Weekly | 30-60min | 100% | Fastest | High |
| **Incremental** | Daily | 5-10min | 20-30% | Medium | Low |
| **Differential** | Daily | 10-20min | 40-50% | Medium | Medium |
| **Continuous** | Per transaction | < 1s | 150% | Instant | Very High |
| **Snapshot** | Hourly | < 1s | 100% | Instant | High |

### RTO vs. RPO Trade-off

```
Financial system:
  RTO (Recovery Time): 1 hour
  RPO (Recovery Point): 5 minutes
  → Need continuous backup or hourly snapshots
  → Cost: $2K/month
  
Social media:
  RTO: 24 hours
  RPO: 1 hour
  → Daily full backup + hourly incremental
  → Cost: $200/month
  
E-commerce:
  RTO: 4 hours
  RPO: 15 minutes
  → 6 hourly snapshots + incremental
  → Cost: $500/month
```

### Storage Cost Optimization

```
1 TB database:
  ├─ Full backups (4): 4 TB
  ├─ Incremental daily (7): 1.4 TB
  └─ Total: 5.4 TB monthly
  
Cost per GB/month: $0.023 (S3 Standard)
Total: ~$125/month

But lifecycle policy:
  ├─ Keep weekly in S3: 2 TB ($46)
  ├─ Move monthly to Glacier: 8 TB ($3)
  └─ Delete after 1 year
  Total: ~$49/month (60% savings)
```

---

## 🏗️ Backup Patterns

### Pattern 1: Full + Incremental (Traditional)

```
Week 1:
  Monday:     Full backup (100% data)
  Tue-Sun:    Incremental (only changes)
  Recovery:   Restore Monday full, then apply Tue-Fri incremental

Week 2:
  Monday:     New full backup (prevent incremental chain)
  
Benefits:
  - Incremental is small and fast
  - Can recover to any point
  
Risks:
  - Chain dependency (if incremental corrupted, recovery fails)
  - Slow recovery (restore full + multiple increments)
```

### Pattern 2: Snapshot (Cloud-native)

```
Hourly snapshots:
  00:00 → Snapshot A (full copy)
  01:00 → Snapshot B (delta from A)
  02:00 → Snapshot C (delta from B)
  ...
  23:00 → Snapshot X (delta from W)

Recovery:
  - To 15:30: Use Snapshot P + apply transaction log
  - Instantaneous: Snapshot is already on disk
  
Benefits:
  - Instant recovery
  - Copy-on-write: only deltas stored
  - No chain dependency
```

### Pattern 3: Continuous Data Protection (Streaming)

```
Application → Transaction Log → Backup Stream
              
Every transaction:
  1. Write to database
  2. Write to transaction log
  3. Stream log to backup system
  
Recovery: Any point in time (restore from Snapshot T + replay logs)

Cost: High (streaming overhead)
Benefit: RPO = seconds
```

---

## 📊 Backup Implementation

### Full Backup

```python
import time
import os

class BackupSystem:
    def __init__(self, backup_dir):
        self.backup_dir = backup_dir
        self.metadata = {}
    
    def create_full_backup(self, database_name):
        """Create full database backup"""
        backup_id = f"backup_{int(time.time())}"
        backup_path = f"{self.backup_dir}/{backup_id}"
        os.makedirs(backup_path, exist_ok=True)
        
        start_time = time.time()
        
        # Simulate backup
        # In production: pg_dump, mysqldump, or cloud native backup
        data_size = self._get_database_size(database_name)
        time.sleep(data_size / 1000)  # 1GB per second
        
        duration = time.time() - start_time
        
        self.metadata[backup_id] = {
            'type': 'full',
            'database': database_name,
            'size_gb': data_size,
            'duration_sec': duration,
            'timestamp': start_time
        }
        
        return backup_id
    
    def create_incremental_backup(self, database_name, full_backup_id):
        """Create incremental backup"""
        backup_id = f"incremental_{int(time.time())}"
        
        start_time = time.time()
        
        # Only changed blocks
        full_size = self.metadata[full_backup_id]['size_gb']
        change_pct = 0.05  # 5% of data changed daily
        change_size = full_size * change_pct
        
        time.sleep(change_size / 100)  # Faster than full
        
        duration = time.time() - start_time
        
        self.metadata[backup_id] = {
            'type': 'incremental',
            'base': full_backup_id,
            'size_gb': change_size,
            'duration_sec': duration,
            'timestamp': start_time
        }
        
        return backup_id
    
    def _get_database_size(self, database_name):
        """Get database size in GB"""
        return 100  # Assume 100GB
    
    def restore(self, backup_id, timestamp=None):
        """Restore from backup"""
        backup = self.metadata[backup_id]
        
        if backup['type'] == 'full':
            print(f"Restoring from full backup {backup_id}")
            print(f"Time: {backup['duration_sec']:.0f}s")
            return True
        
        elif backup['type'] == 'incremental':
            # Need base backup
            base_id = backup['base']
            print(f"Restoring from incremental {backup_id}")
            print(f"Base backup: {base_id}")
            print(f"Total time: {backup['duration_sec']:.0f}s")
            return True

# Test
backup_sys = BackupSystem('/backups')

print("Full backup:")
full_id = backup_sys.create_full_backup('prod_db')
print(f"  ID: {full_id}")
print(f"  Size: {backup_sys.metadata[full_id]['size_gb']}GB")
print(f"  Duration: {backup_sys.metadata[full_id]['duration_sec']:.0f}s")

print("\nIncremental backup:")
inc_id = backup_sys.create_incremental_backup('prod_db', full_id)
print(f"  ID: {inc_id}")
print(f"  Size: {backup_sys.metadata[inc_id]['size_gb']:.1f}GB")
print(f"  Duration: {backup_sys.metadata[inc_id]['duration_sec']:.0f}s")

print("\nRestore test:")
backup_sys.restore(inc_id)
```

---

## ❓ Interview Q&A

**Q1: Design backup strategy for 10TB database, 0 RPO requirement**

A:
- Challenge: 0 RPO means no data loss
- Solution: Continuous backup
  - Primary → Transaction log stream → Backup system (real-time)
  - Keep 2 replicas (sync + async)
  - Daily snapshots for faster recovery
- RTO: < 1 hour (failover to replica)
- Cost: High (continuous streaming + multiple storage copies)

**Q2: How to reduce 24-hour backup window to 4 hours?**

A:
- Problem: 10TB full backup takes 24 hours
- Solution 1: Parallel backup
  - Split database into 4 shards
  - Backup each shard in parallel (4x faster)
  - Combine into single backup
  
- Solution 2: Incremental strategy
  - Full backup weekly (6 hours)
  - Daily incremental (1 hour)
  - Total window: 7 hours (better)
  
- Solution 3: Snapshot
  - Instant snapshot (< 5 minutes)
  - Store snapshots in S3 (durable)
  - RPO: 1 hour

**Q3: Backup failed halfway - recovery risks?**

A:
- Full backup failure:
  - Incomplete data, cannot recover
  - Solution: Verify checksum after backup
  - Keep previous full backup until new one succeeds
  
- Incremental failure:
  - Can recover to last successful full
  - Loss: Data since last full backup
  - Solution: Don't delete full backup until next full succeeds

**Q4: Storage cost is $50K/year - how to reduce?**

A:
- Current: Keep 1 year of daily backups = 365 × 10TB = 3650TB
- Cost reduction:
  1. Lifecycle policies:
     - First 30 days: S3 Standard ($0.023/GB)
     - 30-90 days: S3-IA ($0.0125/GB, 50% savings)
     - 90+ days: Glacier ($0.004/GB, 80% savings)
  
  2. Deduplication:
     - Incremental dedup: 70% reduction
     - 3650TB × 0.3 = 1095TB effective
  
  3. Compression:
     - Typical: 3:1 compression
     - 3650TB / 3 = 1217TB
  
  - Total: ~30-40% of original cost

---

## 🧪 Practical Exercises

### Exercise 1: Implement Incremental Backup (Easy)

**Problem:** Backup 1TB database daily. Keep 7 daily backups. Minimize storage using incrementals.

**Solution:**

```python
import hashlib
import time
from collections import defaultdict

class IncrementalBackup:
    def __init__(self):
        self.blocks = {}  # block_hash -> content
        self.backups = []  # [backup_id, changed_blocks]
        self.backup_time = {}
    
    def calculate_block_hash(self, block_data):
        """Calculate SHA256 of block"""
        return hashlib.sha256(block_data.encode()).hexdigest()
    
    def create_full_backup(self, database_blocks, backup_id):
        """Create full backup"""
        changed = 0
        for block_id, block_data in enumerate(database_blocks):
            block_hash = self.calculate_block_hash(block_data)
            if block_hash not in self.blocks:
                self.blocks[block_hash] = block_data
                changed += 1
        
        self.backups.append({
            'id': backup_id,
            'type': 'full',
            'changed_blocks': changed,
            'total_blocks': len(database_blocks)
        })
        self.backup_time[backup_id] = time.time()
        
        return changed
    
    def create_incremental_backup(self, database_blocks, backup_id, last_backup_id):
        """Create incremental backup"""
        changed = 0
        
        for block_id, block_data in enumerate(database_blocks):
            block_hash = self.calculate_block_hash(block_data)
            if block_hash not in self.blocks:
                self.blocks[block_hash] = block_data
                changed += 1
        
        self.backups.append({
            'id': backup_id,
            'type': 'incremental',
            'base': last_backup_id,
            'changed_blocks': changed,
            'total_blocks': len(database_blocks)
        })
        self.backup_time[backup_id] = time.time()
        
        return changed
    
    def get_backup_storage(self):
        """Calculate total backup storage"""
        unique_blocks = len(self.blocks)
        return unique_blocks  # In real: size in bytes

# Test
backup = IncrementalBackup()

# Simulate database (1000 blocks = 1TB)
print("Creating backups for 7 days:")
print(f"{'Day':<5} {'Type':<12} {'Changed':<10} {'Storage':<10}")
print("-" * 45)

last_backup_id = None
for day in range(1, 8):
    # Simulate 5% change per day
    database = [f"block_{day}_{i}" for i in range(1000)]
    
    if day == 1:
        changed = backup.create_full_backup(database, f"day_{day}")
        backup_type = "FULL"
    else:
        changed = backup.create_incremental_backup(
            database, f"day_{day}", f"day_{day-1}"
        )
        backup_type = "INCR"
    
    storage = backup.get_backup_storage()
    print(f"{day:<5} {backup_type:<12} {changed:<10} {storage:<10}")

total_storage = backup.get_backup_storage()
print(f"\nTotal unique blocks: {total_storage}")
print(f"Storage saved: {(1000*7 - total_storage)/(1000*7)*100:.1f}%")
```

---

### Exercise 2: Point-in-Time Recovery with Transaction Log (Medium)

**Problem:** Database crashes. Restore from backup + transaction log to last committed transaction.

**Solution:**

```python
import time
from collections import deque

class TransactionLog:
    def __init__(self):
        self.log = deque()
        self.committed_txn = 0
    
    def write_transaction(self, txn_id, operations):
        """Write transaction to log"""
        entry = {
            'txn_id': txn_id,
            'operations': operations,
            'timestamp': time.time(),
            'status': 'pending'
        }
        self.log.append(entry)
    
    def commit_transaction(self, txn_id):
        """Mark transaction as committed"""
        for entry in self.log:
            if entry['txn_id'] == txn_id:
                entry['status'] = 'committed'
                self.committed_txn = txn_id
                break
    
    def get_committed_transactions(self):
        """Get all committed transactions"""
        committed = []
        for entry in self.log:
            if entry['status'] == 'committed':
                committed.append(entry)
        return committed
    
    def get_transactions_since(self, start_txn):
        """Get transactions after checkpoint"""
        result = []
        for entry in self.log:
            if entry['txn_id'] > start_txn:
                result.append(entry)
        return result

class PointInTimeRecovery:
    def __init__(self):
        self.txn_log = TransactionLog()
        self.backup_txn = None
        self.checkpoint_time = None
    
    def simulate_crash(self):
        """Database crashes"""
        print("Database crash!")
        return self.txn_log.committed_txn
    
    def recover(self, target_txn):
        """Recover to specific transaction"""
        print(f"\nRecovery plan:")
        print(f"  1. Restore from backup (last checkpoint)")
        print(f"  2. Apply committed transactions {self.backup_txn} to {target_txn}")
        
        txns_to_replay = self.txn_log.get_transactions_since(self.backup_txn)
        print(f"  3. Replay {len(txns_to_replay)} transactions")
        
        for txn in txns_to_replay:
            if txn['txn_id'] <= target_txn:
                print(f"     - Applying txn {txn['txn_id']}: {txn['operations']}")
        
        print(f"  4. Database recovered to txn {target_txn}")

# Test
recovery = PointInTimeRecovery()

# Execute transactions
for i in range(1, 11):
    recovery.txn_log.write_transaction(i, [f"insert_{i}"])
    time.sleep(0.01)
    if i % 5 == 0:
        recovery.txn_log.commit_transaction(i)
        if i == 5:
            recovery.backup_txn = i  # Checkpoint at txn 5

# Crash at txn 9
last_committed = recovery.simulate_crash()
print(f"Last committed txn: {last_committed}")

# Recover to txn 9
recovery.recover(9)
```

---

### Exercise 3: Verify Backup Integrity (Hard)

**Problem:** Backups may be corrupted. Verify using checksum. Test recovery monthly.

**Solution:**

```python
import hashlib
import random

class BackupIntegrity:
    def __init__(self):
        self.backups = {}
        self.checksums = {}
    
    def create_backup(self, backup_id, data_blocks):
        """Create backup and calculate checksum"""
        # Store backup
        self.backups[backup_id] = data_blocks
        
        # Calculate checksum incrementally
        hasher = hashlib.sha256()
        for block in data_blocks:
            hasher.update(block.encode())
        
        self.checksums[backup_id] = hasher.hexdigest()
        return self.checksums[backup_id]
    
    def verify_backup(self, backup_id):
        """Verify backup integrity"""
        if backup_id not in self.backups:
            return False, "Backup not found"
        
        # Recalculate checksum
        hasher = hashlib.sha256()
        for block in self.backups[backup_id]:
            hasher.update(block.encode())
        
        current_hash = hasher.hexdigest()
        original_hash = self.checksums[backup_id]
        
        if current_hash != original_hash:
            return False, "Checksum mismatch - backup corrupted"
        
        return True, "Backup verified"
    
    def test_restore(self, backup_id):
        """Test restore procedure"""
        if backup_id not in self.backups:
            return False, "Backup not found"
        
        # Verify first
        is_valid, msg = self.verify_backup(backup_id)
        if not is_valid:
            return False, msg
        
        # Simulate restore
        data = self.backups[backup_id]
        
        # Verify restored data matches
        hasher = hashlib.sha256()
        for block in data:
            hasher.update(block.encode())
        
        if hasher.hexdigest() != self.checksums[backup_id]:
            return False, "Restore verification failed"
        
        return True, f"Restore test passed for {backup_id}"

# Test
integrity = BackupIntegrity()

print("Creating backups:")
backups = {}
for day in range(1, 4):
    backup_id = f"backup_day_{day}"
    data = [f"block_{i}" for i in range(100)]
    checksum = integrity.create_backup(backup_id, data)
    backups[backup_id] = data
    print(f"  {backup_id}: {checksum[:16]}...")

# Verify all
print("\nVerifying backups:")
for backup_id in backups:
    is_valid, msg = integrity.verify_backup(backup_id)
    print(f"  {backup_id}: {msg}")

# Simulate corruption
print("\nSimulating corruption:")
integrity.backups['backup_day_1'][0] = "corrupted_block"
is_valid, msg = integrity.verify_backup('backup_day_1')
print(f"  backup_day_1: {msg}")

# Monthly restore test
print("\nMonthly restore test:")
for backup_id in [b for b in backups if 'day_1' not in b]:
    is_valid, msg = integrity.test_restore(backup_id)
    print(f"  {backup_id}: {msg}")
```

---

**Last updated:** 2026-05-22
