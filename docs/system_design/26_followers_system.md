# Followers/Following System

## Problem Statement
Design a social graph system tracking follower relationships.

**Operations:**
- `follow(user_a, user_b)` — A follows B
- `unfollow(user_a, user_b)` — A unfollows B
- `getFollowers(user_id)` — Get all followers
- `getFollowing(user_id)` — Get all following
- `areFriends(user_a, user_b)` — Mutual follow?

## Design

### Graph Representation

```
Adjacency list: user_id -> Set[followers]
Bidirectional edges: Both directions stored
Indexing: O(1) lookup
```

### Caching Strategy

```
Hot users: Cache followers/following
LRU eviction: Limited memory
Precompute for common queries
```

### Timeline Generation

```
User follows set → Merge posts
Ordered by timestamp
Paginated results
Caching top pages
```

## Complexity

| Operation | Time |
|-----------|------|
| Follow | O(1) |
| Unfollow | O(1) |
| Get followers | O(k) where k=followers |
| Check mutual | O(min(a,b)) |
