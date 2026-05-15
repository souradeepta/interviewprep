# News Feed System

## Problem Statement
Design a social media news feed that generates personalized timelines for users based on their followers and following.

**Operations:**
- `post(user_id, content)` — Create new post
- `getFeed(user_id)` — Get personalized timeline
- `follow(user_id, target_id)` — Follow user
- `like(user_id, post_id)` — Like post

## Design

### Fanout Strategies

**Fanout-on-Write:**
```
Post created → Push to all followers' feeds immediately
Pros: Fast reads, simple implementation
Cons: Expensive for users with many followers
```

**Fanout-on-Read:**
```
Post created → Stored centrally
Get feed → Merge posts from all follows
Pros: Scalable for heavy posters
Cons: Slow reads, aggregation overhead
```

**Hybrid:**
```
Fanout-on-write for active users
Fanout-on-read for celebrities
```

### Data Structure

```
users: {user_id -> User}
posts: {post_id -> Post}
followers: {user_id -> Set[follower_ids]}
feeds: {user_id -> [post_ids]} (cache)
```


## Architecture Diagram

```
┌──────────────────────────────────────────┐
│      News Feed Service                   │
│  ┌──────────────────────────────────────┐  │
│  │ User Request: getFeed(userId)        │  │
│  │                                      │  │
│  │ 1. Get followed users (Redis)        │  │
│  │ 2. Fetch posts from cache/DB         │  │
│  │ 3. Rank by timestamp/engagement      │  │
│  │ 4. Return top 20 posts               │  │
│  └──────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

## Common Questions & Answers

**Q: Why multi-layer caching?** A: L1 (Redis): hot data, 1hr. L2 (Memcached): warm data. L3 (DB): persistent. Reduces load.

**Q: Feed freshness?** A: TTL 1hr + event-based invalidation on post. Trade: cache hit vs freshness.

**Q: Ranking complexity?** A: Timestamp (simple), engagement score (time-decay), ML ranking. Simple fast, ML better UX.

**Q: Scaling to billions?** A: Shard by userId. Each shard manages subset feeds. Replicate for HA. Cache miss hits only shard.

## Back-of-Envelope Calculations

1B users, 1K friends avg, 10 posts/day: 10K posts/user/day. Cache 90% hit rate: 5ms latency. Storage: 1B users × 100KB = 100TB distributed.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Pull model | Fresh data, simple | O(followers) latency |
| Push model | Fast O(1) | Complex, high storage |
| Hybrid | Balances both | More complex |

## Follow-up Interview Questions

1. Real-time feed updates (WebSocket)? 2. Millions of followers handling? 3. Trending topics in feed? 4. Cache invalidation bottleneck at 10x. 5. High-value content prioritization?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

### Architecture Diagram

```mermaid
graph TB
    User["User"]
    PostService["Post Service"]
    FeedService["Feed Service"]
    Cache["Cache<br/>Redis"]
    DB["Database"]

    User -->|Create Post| PostService
    PostService -->|Store| DB
    User -->|Get Feed| FeedService
    FeedService -->|Check| Cache
    Cache -->|Miss| DB
    FeedService -->|Return| User
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant PS as Post Service
    participant FS as Feed Service
    participant C as Cache

    U->>PS: Create Post
    PS->>DB: Save
    U->>FS: Get Feed
    FS->>C: Check Cache
    alt Hit
        C-->>FS: Feed
    else Miss
        FS->>DB: Query
        DB-->>FS: Results
        FS->>C: Update
    end
    FS-->>U: Feed
```

## Complexity

| Operation | Fanout-Write | Fanout-Read |
|-----------|--------------|-------------|
| post | O(n) where n=followers | O(1) |
| getFeed | O(k) where k=feed_size | O(n*k) |
| Space | O(users*posts) | O(posts) |
