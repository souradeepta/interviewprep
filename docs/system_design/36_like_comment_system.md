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

## Complexity

| Operation | Time |
|-----------|------|
| Like | O(1) |
| Comment | O(1) |
| Get count | O(1) cached |
| Get comments | O(k) |
