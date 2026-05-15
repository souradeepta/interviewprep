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


## Architecture Diagram

```
┌──────────────────────────────────────┐
│   Sharded Database Architecture      │
│  ┌──────────────────────────────────┐  │
│  │ Sharding Key: user_id            │  │
│  │ Shard 1: user_id % 4 == 0        │  │
│  │ Shard 2: user_id % 4 == 1        │  │
│  │ Shard 3: user_id % 4 == 2        │  │
│  │ Shard 4: user_id % 4 == 3        │  │
│  │                                  │  │
│  │ Directory: user_id → shard_id    │  │
│  └──────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant Client
    participant Router
    participant Shard1 as Shard 1
    participant Shard2 as Shard 2
    participant Shard3 as Shard 3
    participant Shard4 as Shard 4

    Client->>Router: get(user_id=42)
    Router->>Router: shard_id = hash(42) % 4 = 2
    Router->>Shard2: get(user_id=42)
    Shard2-->>Router: user_data
    Router-->>Client: return user_data
```

## Common Questions & Answers

**Q: Shard key selection?** A: Choose high-cardinality (user_id good, gender bad). Enables even distribution.

**Q: Hot shard problem?** A: Uneven distribution if key skewed (celebrities). Solution: split hot shard, re-shard.

**Q: Cross-shard queries?** A: Expensive, scatter-gather to all shards. Avoid if possible.

**Q: Re-sharding complexity?** A: Double shards: migrate half of each to new shards. Zero-downtime hard, plan carefully.

## Back-of-Envelope Calculations

1B users, 4 shards: 250M per shard. Each shard: single master + replicas. Queries: shard_id = hash(user_id) % 4. Cross-shard: 4x latency.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Range sharding | Easy range queries | Uneven distribution |
| Hash sharding | Even distribution | Range queries hard |
| Directory-based | Flexible, dynamic | Extra lookup latency |

## Follow-up Interview Questions

1. Dynamic re-sharding without downtime? 2. Handling growth (1B → 10B)? 3. Cross-shard transactions? 4. Load imbalance detection? 5. Disaster recovery per shard?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

## Trade-offs

| Strategy | Pros | Cons |
|----------|------|------|
| Range | Simple joins | Uneven distribution |
| Hash | Even distribution | Hard to scale |
| Consistent hash | Scale-friendly | Complex implementation |
