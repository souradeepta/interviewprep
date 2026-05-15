# Like/Comment System

## Problem Statement
Design a system for social interactions (likes, comments) at scale.

**Operations:**
- `like(user_id, post_id)` — Like post
- `unlike(user_id, post_id)` — Unlike post
- `comment(user_id, post_id, text)` — Add comment
- `deleteComment(comment_id)` — Delete comment
- `getLikeCount(post_id)` — Get like count

## Design

### Like Counter

```
Atomic increment: Redis INCR
Batch write: Eventually consistent
Denormalized: Cache in post doc
Eventual consistency: Async update to DB
```

### Comment Storage

```
Ordered by timestamp
Indexed by post_id
Pagination: Get top K comments
Sorting: Top comments (likes)
```

### Real-time Updates

```
WebSocket push: New likes/comments
Counter update: Client + server
Caching: Popular posts cached
```


## Architecture Diagram

```
┌──────────────────────────────────────┐
│   Like/Comment Engine                │
│  ┌──────────────────────────────────┐  │
│  │ Like Counter                     │  │
│  │ - Redis atomic increment         │  │
│  │ - Persist to DB (async)          │  │
│  │ Comments                         │  │
│  │ - Threaded (parent_id)           │  │
│  │ - Sorted by time/score           │  │
│  │ Notification on engagement       │  │
│  │ - Publish event (Kafka)          │  │
│  └──────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## Common Questions & Answers

**Q: Double-like prevention?** A: Check if user already liked (set membership). If yes, unlike. If no, add to set.

**Q: Like count accuracy vs speed?** A: Cache in Redis (fast but stale), sync to DB hourly (accurate). Acceptable lag.

**Q: Comment moderation?** A: ML classifier (toxicity), manual review for borderline. Hide pending review.

**Q: Comment ordering—best first?** A: By score (likes - reports). Time-decay: recent higher. Controversial (mixed opinions) interesting.

## Back-of-Envelope Calculations

1B items, 1K likes avg = 1T likes. Like updates: 10 req/sec per item = 100K global. Cache 1B items × 4B = 4GB Redis.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Count-only | Simple, fast | No like history |
| Set-based (track users) | De-duplicate, per-user prefs | Higher memory |
| Sorted set (scored) | Complex ranking | More storage |

## Follow-up Interview Questions

1. Spam like detection? 2. Sort comments optimally? 3. Like propagation (friend feed update)? 4. Sensitivity (hide counts)? 5. Verification (real accounts)?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

## Complexity

| Operation | Time |
|-----------|------|
| Like | O(1) |
| Comment | O(1) |
| Get count | O(1) cached |
| Get comments | O(k) |
