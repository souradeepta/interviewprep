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

## Complexity

| Operation | Time |
|-----------|------|
| Update score | O(log n) |
| Get leaderboard | O(k log n) |
| Get rank | O(log n) |
