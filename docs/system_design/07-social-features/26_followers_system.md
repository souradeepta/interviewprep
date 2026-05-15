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


## Architecture Diagram

```
┌──────────────────────────────────────┐
│   Social Graph (Followers)           │
│  ┌──────────────────────────────────┐  │
│  │ Following Graph                  │  │
│  │ - user → [follower_ids] (Redis)  │  │
│  │ - O(1) add/remove follower       │  │
│  │ Follower Graph                   │  │
│  │ - user → [following_ids]         │  │
│  │ - Bidirectional relationship     │  │
│  └──────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## Common Questions & Answers

**Q: Graph consistency?** A: Keep both directions in sync. Atomic update or eventual consistency?

**Q: Large follower lists?** A: Pagination (fetch first 1000). Truncate in feed (show top K).

**Q: Block/mute user?** A: Add to blocklist, filter from feed/notifications.

**Q: Mutual follow detection?** A: Check if A in B's followers AND B in A's followers.

## Back-of-Envelope Calculations

1B users, avg 500 followers. Storage: 500B avg followers per user = 500GB Redis. Queries: is_follower O(1), get_followers O(n).

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| In-memory (Redis) | Fast, simple | Memory cost |
| Graph DB (Neo4j) | Complex queries | Slower |
| Materialized view | Pre-computed | Update lag |

## Follow-up Interview Questions

1. Handle celebrity (10M followers) efficiently? 2. Viral following (growth spike)? 3. Follow suggestion algorithm? 4. Privacy (hide followers)? 5. Analytics (who unfollowed)?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

### Architecture Diagram

```mermaid
graph TB
    User["User"]
    FollowService["Follow Service"]
    Graph["Graph DB"]
    Cache["Cache"]

    User -->|Follow/Unfollow| FollowService
    FollowService -->|Store| Graph
    FollowService -->|Cache| Cache
```

### Flow Diagram

```mermaid
flowchart TD
    A["Follow Request"] --> B["Check if exists"]
    B --> C{"Already following?"}
    C -->|Yes| D["Error"]
    C -->|No| E["Add Edge"]
    E --> F["Update Cache"]
    F --> G["Confirm"]
```

## Complexity

| Operation | Time |
|-----------|------|
| Follow | O(1) |
| Unfollow | O(1) |
| Get followers | O(k) where k=followers |
| Check mutual | O(min(a,b)) |
