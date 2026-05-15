# Leaderboard System

## Problem Statement
Design a system tracking and displaying user rankings in real-time.

**Operations:**
- `updateScore(user_id, points)` — Add points
- `getLeaderboard(page)` — Get top rankings
- `getUserRank(user_id)` — Get user position
- `getUserScore(user_id)` — Get user score

## Design

### Data Structure

```
Sorted set: {score -> [user_ids]}
Or: Redis sorted set (ZSET)
Time-based: Multiple leaderboards (daily, weekly, all-time)
```

### Caching Strategy

```
Top 100 cached (hot)
User's position: On-demand calculation
Periodic refresh: Avoid stale cache
```

### Handling Ties

```
Secondary sort: Timestamp (who reached first)
Tertiary sort: User ID (deterministic)
Consistent ordering
```


## Architecture Diagram

```
┌───────────────────────────────┐
│   Real-time Leaderboard      │
│  Sorted Set (Redis)           │
│  - O(log n) insert            │
│  - O(n) rank (shard)          │
│  Ranking Queries              │
│  - Top 100: ZREVRANGE         │
│  - User rank: ZREVRANK        │
│  Snapshots (hourly)           │
│  - MySQL for persistence      │
└───────────────────────────────┘
```

## Common Questions & Answers

**Q: Tie-breaking?** A: Tiebreaker: timestamp (first wins). Secondary score. Stable rank.

**Q: Update frequency?** A: Real-time (slow refresh) vs batch (fast query). Trade consistency vs throughput.

**Q: Seasonal reset?** A: Archive old, new board starts fresh. Keep history for 'all-time'.

**Q: Regional sharding?** A: Shard by region. Global from shards. No global consensus needed.

## Back-of-Envelope Calculations

10M players, 1 Hz update = 1M updates/sec. Redis: ZADD O(log n). Throughput: 1M easily. Query: top-100 = 1ms.
## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Redis Sorted Set | O(log n), simple | No persistence |
| DB index | Persistent | Slower |
| Sharded Set | Scalable | Complex |

## Follow-up Interview Questions

1. Prevent cheating? 2. Mobile (low bandwidth)? 3. Competitive leagues? 4. Bottleneck at 10x? 5. Real-time visualization?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

## Complexity

| Operation | Time |
|-----------|------|
| Update score | O(log n) |
| Get leaderboard | O(k log n) |
| Get rank | O(log n) |
