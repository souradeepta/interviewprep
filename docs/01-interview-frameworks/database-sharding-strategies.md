# Database Sharding Strategies: Horizontal Scaling of Data

Master sharding approaches for distributing data across multiple database servers.

---

## Sharding Fundamentals

**Problem:** Single database server can't handle data volume or QPS.

**Solution:** Split data across multiple "shards" (smaller databases).

```
Before:
┌──────────────────────────┐
│ All 100M users in DB     │
│ All 10B posts in DB      │
│ All 500B events in DB    │
└──────────────────────────┘

After:
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Shard 0      │  │ Shard 1      │  │ Shard 2      │
│ Users 0-30M  │  │ Users 30-60M │  │ Users 60-100M│
│ Posts 0-3B   │  │ Posts 3-6B   │  │ Posts 6-10B  │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## Sharding Key Selection

**Sharding key:** Column used to determine which shard.

### Option 1: User ID (Most Common)

```
Shard number = hash(user_id) % num_shards

Example:
user_id = 123 → hash(123) % 3 = 0 → Shard 0
user_id = 456 → hash(456) % 3 = 1 → Shard 1
user_id = 789 → hash(789) % 3 = 2 → Shard 2

Pro: All user data colocated, most queries single-shard
Con: Uneven distribution if user_ids skewed
```

### Option 2: Range-Based (Time)

```
Shard 0: 2024-01-01 to 2024-01-31
Shard 1: 2024-02-01 to 2024-02-29
Shard 2: 2024-03-01 to 2024-03-31

Pro: Easy to archive old shards
Con: Hot shards (current month gets all writes)
```

### Option 3: Geographic Location

```
Shard USA:    users in North America
Shard EU:     users in Europe
Shard APAC:   users in Asia-Pacific

Pro: Data locality, compliance (GDPR)
Con: Cross-region queries expensive
```

---

## Consistent Hashing

**Problem:** Adding/removing shards requires rebalancing all data.

**Solution:** Consistent hashing minimizes remapping.

```
Without consistent hashing:
3 shards: hash(key) % 3
Add 4th shard: hash(key) % 4
Result: All keys need remapping (100% churn)

With consistent hashing:
- Ring of 2^32 positions
- Each shard owns a range on the ring
- Adding shard only remaps ~1/n keys

Example:
Original: Shard 0, 1, 2
Add Shard 3: Only 25% of keys remapped
```

---

## Sharding Challenges

### Hot Shards

```
Problem: Shard 0 gets 90% of traffic
Solution:
1. Increase replica count on Shard 0
2. Read-heavy cache in front
3. Partition further (sharding of sharding)
```

### Non-Uniform Distribution

```
Problem: User ID 1 has 1M records, User ID 2 has 1 record
Solution:
1. Detect hot users
2. Create micro-shards for hot users
3. Dynamic repartitioning
```

### Cross-Shard Queries

```
Problem: "Get all orders by all users in region"
requires querying all shards

Solution:
1. Scatter-gather: Query all shards, merge results
2. Denormalization: Store region info in orders table
3. Dedicated index shard for cross-shard lookups
```

---

## Shard Mapping

```python
# Option 1: Hardcoded
shard_0_db = connect("db0.example.com")
shard_1_db = connect("db1.example.com")

# Option 2: Service (Recommended)
class ShardingService:
    def get_shard(self, user_id):
        shard_number = hash(user_id) % self.num_shards
        return self.shard_config[shard_number]

# Option 3: Zookeeper/Consul
registry.lookup(f"shard:{user_id % num_shards}")
```

---

## Shard Rebalancing

**Problem:** Adding shards requires moving data.

```
Process:
1. Add new shard to cluster
2. Copy ~25% of data from each old shard to new shard
3. Verify integrity
4. Switch reads/writes to new configuration
5. Decommission old distribution (keep for fallback)
```

**Downtime:** Usually 0 with proper implementation (dual writes)

---

## When NOT to Shard

- **< 10GB total data** — Single DB sufficient
- **< 1000 QPS** — Single DB can handle
- **Complex joins** — Sharding breaks joins
- **Frequent schema changes** — Harder across shards

---

## Sharding Checklist

- ✓ Identified sharding key (based on access patterns)
- ✓ Consistent hashing or stable mapping
- ✓ Plan for uneven distribution (hot shards)
- ✓ Cross-shard query strategy (scatter-gather)
- ✓ Rebalancing strategy when adding shards
- ✓ Shard count decision (2^n typically)
- ✓ Monitoring per-shard metrics
- ✓ Failover per shard (not global)
- ✓ Read replicas per shard
- ✓ Tested sharding logic on small examples

