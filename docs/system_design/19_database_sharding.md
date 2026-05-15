# Database Sharding

## Problem Statement
Design a sharding strategy for horizontally scaling database across multiple nodes.

**Requirements:**
- Distribute data evenly
- Route queries to correct shard
- Minimal data movement on scale
- Handle shard failures

## Design

### Sharding Keys

```
User ID: Good for user-centric apps
Timestamp: Good for time-series data
Geographic: Good for region-based queries
Composite: Combination for better distribution
```

### Consistent Hashing

```
Hash key → Ring of servers
Add/remove server: Minimal rehashing
Virtual nodes: Better distribution
```

### Cross-shard Queries

```
Scatter-gather: Query all shards
Merge results
Use fan-out pattern
```

## Trade-offs

| Strategy | Pros | Cons |
|----------|------|------|
| Range | Simple joins | Uneven distribution |
| Hash | Even distribution | Hard to scale |
| Consistent hash | Scale-friendly | Complex implementation |
