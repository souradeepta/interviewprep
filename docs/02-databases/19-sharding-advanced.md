# Sharding Strategies Deep Dive

Scale databases horizontally by partitioning data across multiple instances while maintaining consistency.

---

## ⚖️ Sharding Strategy Trade-offs

### Sharding Method Comparison

| Method | Lookup | Rebalancing | Hotspots | Complexity |
|--------|--------|-------------|----------|-----------|
| **Range** | O(1) with metadata | Complex | Common | Low |
| **Hash** | O(1) with hash | Minimal | Possible | Low |
| **Directory** | O(log n) | Easy | No | High |
| **Geo** | O(1) geographic | Medium | No | Medium |
| **Consistent Hash** | O(log n) | Minimal | Possible | Medium |

### Scaling Impact

```
Single database:
  Max throughput: 100K ops/sec
  Data: 1TB
  
With 10 shards:
  Max throughput: 1M ops/sec (10x improvement)
  Data per shard: 100GB
  
With 100 shards:
  Max throughput: 10M ops/sec
  Data per shard: 10GB
  
But: More shards = more operational complexity
```

---

## 🏗️ Sharding Patterns

### Pattern 1: Range-based Sharding

```
Shard by user_id range:

Shard 1: user_id 0-999999
Shard 2: user_id 1000000-1999999
Shard 3: user_id 2000000-2999999

Lookup: For user_id = 1500000
  ├─ Check which range
  ├─ 1M-2M: Shard 2
  └─ Route to Shard 2

Problem: Uneven distribution
  ├─ Early users (0-100K) more active
  ├─ Shard 1 becomes hot
  ├─ Throughput bottleneck
```

### Pattern 2: Hash-based Sharding

```
Shard by hash(user_id) % num_shards:

For user_id = 12345:
  ├─ hash(12345) = 5873829
  ├─ 5873829 % 10 = 3
  └─ Shard 3

Benefits:
  ├─ Uniform distribution
  ├─ No hotspots (usually)
  └─ O(1) lookup

Problem: Rebalancing on shard addition
  ├─ 10 shards: hash() % 10
  ├─ Add shard: 11 shards: hash() % 11
  ├─ 90% of keys rehash (moved)
  └─ Expensive migration
```

### Pattern 3: Consistent Hashing

```
Hash ring with virtual nodes:

          User A
         /      \
      [0]        [100]
     /              \
   /                  \
User C -------- User B

Adding user D:
  ├─ Only affects keys between C and D
  ├─ Keys before C still go to C
  ├─ Keys after D still go to B
  └─ Minimal rehashing (1/n of keys)

Benefits:
  ├─ K/n keys rehash (not (n-1)/n)
  ├─ Scalable
  ├─ Suitable for distributed systems
```

### Pattern 4: Directory-based Sharding

```
Global shard directory:

user_id → shard_id mapping

Directory:
  1 → shard-us-east
  2 → shard-us-west
  3 → shard-eu
  ...
  1000000 → shard-apac

Lookup: SELECT shard_id FROM directory WHERE user_id = 123
  ├─ Query directory (1 extra lookup)
  ├─ Get shard_id
  └─ Route to correct shard

Benefits:
  ├─ Perfect distribution (no hotspots)
  ├─ Easy rebalancing
  ├─ Can move users without rehashing
  
Drawback:
  ├─ Directory is bottleneck
  └─ Extra query latency
```

---

## 📊 Hot Shard Problem

### Identifying Hot Shards

```
10 shards, 1M operations/sec:
  Expected per shard: 100K ops/sec
  
Actual distribution:
  Shard 1: 200K ops/sec (2x) ← HOT
  Shard 2: 150K ops/sec (1.5x)
  Shard 3: 50K ops/sec (0.5x) ← COLD
  ...
  
Hot shards cause:
  ├─ CPU spike (overload)
  ├─ Memory pressure
  ├─ Increased latency
  └─ Potential cascading failures
```

### Solutions to Hot Shards

```
Solution 1: Shard by different key
  ├─ Currently by user_id
  ├─ Change to shard by (user_id, timestamp)
  ├─ Spreads hot user across multiple shards
  └─ But: Query more shards per request

Solution 2: Cache hot data
  ├─ Put hot shard in cache (Redis)
  ├─ Route reads to cache
  └─ Writes still go to shard

Solution 3: Split hot shard
  ├─ Detect hot user_id (celebrity with 1M followers)
  ├─ Move to separate shard
  ├─ Dedicated shard for hot user
  └─ Others distributed normally

Solution 4: Replication
  ├─ Replicate hot shard to 3 instances
  ├─ Load balance reads across replicas
  └─ Writes go to primary
```

---

## ❓ Interview Q&A

**Q1: Design sharding for 1B users, 100K ops/sec, zero hotspots**

A:
- Requirement: No hotspots (uniform distribution)
- Solution: Hash-based with consistent hashing
  ```
  shard = consistent_hash(user_id)
  
  Virtual nodes: 100 per shard
  Benefit: 1% rebalancing per shard addition
  ```
- Alternative: Directory-based
  ```
  shard = directory[user_id]
  
  Benefits:
    - Perfect distribution
    - Easy rebalancing
    - Can detect/fix hotspots dynamically
  ```
- Monitoring:
  - Track ops/sec per shard
  - Alert if any shard > 1.2x average
  - Auto-rebalance or split hot shard

**Q2: Rebalancing 1B users across shards - data loss risk?**

A:
- Two-phase rebalancing:
  1. Dual-write phase:
     - New shard receives writes
     - Old shard also receives writes (temporarily)
     - Catch up new shard with historical data
  
  2. Cutover phase:
     - Stop writes to old shard
     - Verify new shard caught up
     - Redirect reads/writes to new shard
     - Retire old shard
  
- Risk mitigation:
  - Keep old shard for 24 hours (rollback window)
  - Verify checksums match
  - Gradual traffic shift (10% → 50% → 100%)

**Q3: User queries across 3 shards - how to optimize?**

A:
- Problem: Query needs user + orders + payments
  - User in shard 1 (user_id shard)
  - Orders in shard 2 (order_id shard)
  - Payments in shard 3 (payment_id shard)
  - Total: 3 shard queries + network latency
  
- Solution 1: Denormalization
  - Store user + recent orders in user shard
  - Reduces to 1 shard query
  
- Solution 2: Sharding key consistency
  - Shard all by user_id
  - User → Shard 1
  - Orders → Shard 1
  - Payments → Shard 1
  - All queries = 1 shard
  
- Solution 3: Cache
  - Cache user + orders in Redis
  - Check cache first (no shard query)
  - Hit rate: 90%+ typical

**Q4: Database can't handle rebalancing - too much I/O, solution?**

A:
- Problem: 1B users = 500GB per shard
  - Rebalancing = copying 500GB
  - Disk I/O limited (100MB/s)
  - Time = 5000 seconds = 80 minutes
  - But: Live traffic still flowing (concurrent writes)
  
- Solution 1: Throttle rebalancing
  - Copy at 10MB/s (not 100MB/s)
  - Less I/O impact on live traffic
  - Time: 800 minutes = 13 hours
  - Acceptable for maintenance window
  
- Solution 2: Parallel copy
  - Copy from 5 replicas in parallel
  - 5 × 10MB/s = 50MB/s total
  - Time: 160 minutes = 2.7 hours
  
- Solution 3: Incremental copy
  - Only copy changed data
  - Most data doesn't change
  - 10% of 500GB = 50GB
  - Time: 80 minutes

**Q5: Cross-shard transaction - how to handle?**

A:
- Problem: Transfer money from user A (shard 1) to user B (shard 2)
  ```
  User A (shard 1): balance -= 100
  User B (shard 2): balance += 100
  
  If shard 2 fails after step 1:
    → Money lost
  ```
  
- Solution 1: Saga pattern
  ```
  1. Debit from A: balance -= 100 (shard 1)
  2. Credit to B: balance += 100 (shard 2)
  3. If step 2 fails, compensate: balance += 100 (shard 1)
  ```
  
- Solution 2: Two-phase commit
  ```
  1. Prepare on both shards (lock rows)
  2. If both ready, commit on both
  3. If either fails, rollback both
  ```
  
- Better: Single shard design
  - Store A and B in same shard
  - Single transaction works
  - Avoid cross-shard complexity

---

## 🧪 Practical Exercises

### Exercise 1: Implement Hash-based Sharding (Easy)

**Problem:** Route 1M user_ids to 10 shards uniformly. Verify no hotspots.

**Solution:**

```python
import hashlib
from collections import defaultdict

class HashSharding:
    def __init__(self, num_shards=10):
        self.num_shards = num_shards
        self.shard_distribution = defaultdict(list)
    
    def get_shard(self, user_id):
        """Get shard for user_id using hash"""
        hash_val = int(
            hashlib.md5(str(user_id).encode()).hexdigest(),
            16
        )
        return hash_val % self.num_shards
    
    def distribute_users(self, num_users=1000000):
        """Distribute users and check for hotspots"""
        for user_id in range(num_users):
            shard = self.get_shard(user_id)
            self.shard_distribution[shard].append(user_id)
    
    def check_hotspots(self, threshold=1.2):
        """Check if any shard is overloaded"""
        expected = len(self.shard_distribution[0]) / len(self.shard_distribution)
        
        hotspots = []
        for shard_id, users in self.shard_distribution.items():
            load_ratio = len(users) / expected
            if load_ratio > threshold:
                hotspots.append((shard_id, load_ratio))
        
        return hotspots
    
    def print_distribution(self):
        """Print distribution statistics"""
        sizes = [len(users) for users in self.shard_distribution.values()]
        avg = sum(sizes) / len(sizes)
        max_size = max(sizes)
        min_size = min(sizes)
        
        print(f"Distribution (num_shards={self.num_shards}):")
        print(f"  Average per shard: {avg:.0f}")
        print(f"  Max: {max_size} ({max_size/avg:.2f}x)")
        print(f"  Min: {min_size} ({min_size/avg:.2f}x)")
        
        hotspots = self.check_hotspots()
        if hotspots:
            print(f"  Hotspots (>1.2x):")
            for shard, ratio in hotspots:
                print(f"    Shard {shard}: {ratio:.2f}x")

# Test
sharding = HashSharding(num_shards=10)
sharding.distribute_users(1000000)
sharding.print_distribution()

# Test with 100 shards
print("\n")
sharding100 = HashSharding(num_shards=100)
sharding100.distribute_users(1000000)
sharding100.print_distribution()
```

---

### Exercise 2: Consistent Hashing for Minimal Rebalancing (Medium)

**Problem:** Add new shard without rehashing all keys.

**Solution:**

```python
import hashlib
from bisect import bisect_right

class ConsistentHashSharding:
    def __init__(self, num_shards=10, virtual_nodes=10):
        self.num_shards = num_shards
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        self._build_ring()
    
    def _build_ring(self):
        """Build hash ring"""
        self.ring = {}
        for shard_id in range(self.num_shards):
            for v_node in range(self.virtual_nodes):
                key = f"shard_{shard_id}:{v_node}"
                hash_val = int(
                    hashlib.md5(key.encode()).hexdigest(),
                    16
                )
                self.ring[hash_val] = shard_id
        
        self.sorted_keys = sorted(self.ring.keys())
    
    def get_shard(self, user_id):
        """Get shard for user_id"""
        hash_val = int(
            hashlib.md5(str(user_id).encode()).hexdigest(),
            16
        )
        idx = bisect_right(self.sorted_keys, hash_val) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]
    
    def add_shard(self):
        """Add new shard and calculate rehashing"""
        old_distribution = {}
        for user_id in range(100000):
            shard = self.get_shard(user_id)
            old_distribution[user_id] = shard
        
        # Add shard
        self.num_shards += 1
        self._build_ring()
        
        # Calculate rehashing
        new_distribution = {}
        rehashed = 0
        for user_id in range(100000):
            new_shard = self.get_shard(user_id)
            new_distribution[user_id] = new_shard
            if old_distribution[user_id] != new_shard:
                rehashed += 1
        
        rehash_pct = rehashed / 100000 * 100
        return rehash_pct

# Test
sharding = ConsistentHashSharding(num_shards=10)

print("Consistent hashing rebalancing test:")
print(f"Initial shards: 10")

for i in range(3):
    rehash_pct = sharding.add_shard()
    print(f"After adding shard {11+i}: {rehash_pct:.1f}% keys rehashed")
```

---

### Exercise 3: Detect & Fix Hot Shards (Hard)

**Problem:** User queries reveal one shard is overloaded (3x traffic). Rebalance.

**Solution:**

```python
from collections import defaultdict
import random

class HotShardDetection:
    def __init__(self, num_shards=10):
        self.num_shards = num_shards
        self.shard_load = defaultdict(int)
        self.user_location = {}
        self.hot_threshold = 1.5  # 1.5x average = hot
    
    def simulate_workload(self, num_users=10000):
        """Simulate user workload (zipfian distribution)"""
        # Zipfian: few users very hot, many users cold
        # 1% of users = 50% of traffic
        
        # Hash users to shards
        for user_id in range(num_users):
            shard = hash(user_id) % self.num_shards
            self.user_location[user_id] = shard
            
            # Zipfian: popular users get more queries
            rank = user_id + 1
            query_count = int(100000 / (rank ** 1.2))
            self.shard_load[shard] += query_count
    
    def detect_hot_shards(self):
        """Find overloaded shards"""
        avg_load = sum(self.shard_load.values()) / self.num_shards
        hot_shards = []
        
        for shard_id, load in self.shard_load.items():
            ratio = load / avg_load
            if ratio > self.hot_threshold:
                hot_shards.append((shard_id, ratio, load))
        
        return sorted(hot_shards, key=lambda x: x[1], reverse=True)
    
    def identify_hot_users(self, hot_shard_id):
        """Find users causing the load"""
        users_in_shard = [
            uid for uid, shard in self.user_location.items()
            if shard == hot_shard_id
        ]
        
        # Estimate load per user (simplified)
        loads = {}
        for user_id in users_in_shard:
            rank = user_id + 1
            query_count = int(100000 / (rank ** 1.2))
            loads[user_id] = query_count
        
        # Top 10 hot users
        return sorted(loads.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def rebalance_hot_shard(self, hot_shard_id):
        """Split hot shard or move hot users"""
        hot_users = self.identify_hot_users(hot_shard_id)
        total_hot_load = sum(load for _, load in hot_users)
        
        print(f"Rebalancing shard {hot_shard_id}:")
        print(f"  Hot users (top 10): {sum(load for _, load in hot_users)} queries")
        
        # Solution: Move hot users to dedicated shard
        # Create new shard specifically for these users
        new_shard_id = self.num_shards
        self.num_shards += 1
        self.shard_load[new_shard_id] = total_hot_load
        
        for user_id, load in hot_users:
            self.user_location[user_id] = new_shard_id
            self.shard_load[hot_shard_id] -= load
        
        print(f"  Solution: Created dedicated shard {new_shard_id} for {len(hot_users)} hot users")
        return new_shard_id

# Test
detector = HotShardDetection(num_shards=10)
detector.simulate_workload(num_users=10000)

hot_shards = detector.detect_hot_shards()
if hot_shards:
    print(f"Detected {len(hot_shards)} hot shards:")
    for shard_id, ratio, load in hot_shards[:3]:
        print(f"  Shard {shard_id}: {ratio:.2f}x average load ({load} queries)")
    
    # Rebalance hottest
    hottest_shard = hot_shards[0][0]
    detector.rebalance_hot_shard(hottest_shard)
    
    # Check after rebalancing
    new_hot = detector.detect_hot_shards()
    print(f"\nAfter rebalancing:")
    if not new_hot:
        print("  No more hot shards!")
    else:
        print(f"  {len(new_hot)} shards still hot")
```

---

**Last updated:** 2026-05-22
