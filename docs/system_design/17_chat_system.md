# Chat System

## Problem Statement
Design a real-time messaging system supporting one-to-one and group chat.

**Operations:**
- `sendMessage(from, to, text)` — Send message
- `getMessages(user_id, thread_id)` — Get conversation
- `createGroup(members)` — Create group
- `updateGroupMembers(group_id, members)` — Modify group

## Design

### Message Storage

```
One-to-one: Bilateral storage (both users get copy)
Group: Centralized, sync to members
Indexing: (user_id, timestamp) for fast retrieval
```

### Delivery Guarantees

```
At-least-once: Message queued until ACK
Message status: Sent, Delivered, Read
Retry on failure: Exponential backoff
```

### Notifications

```
Online: WebSocket push
Offline: Store and push when online
Badges: Unread count per user
```

## Complexity

| Operation | Time |
|-----------|------|
| Send message | O(1) |
| Get messages | O(k) where k=messages |
| Group update | O(n) where n=members |
