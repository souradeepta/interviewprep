# WebSocket Server

## Problem Statement
Design a bidirectional communication server for real-time applications.

**Operations:**
- `connect(client_id)` — Establish connection
- `send(client_id, message)` — Send to client
- `broadcast(message)` — Send to all
- `join(client_id, room)` — Join room

## Design

### Connection Management

```
In-memory map: client_id -> WebSocket
Connection pooling: Limit concurrent
Heartbeat: Detect stale connections
Graceful shutdown: Clean disconnects
```

### Message Routing

```
Direct: To specific client
Room: To all in room
Broadcast: To all clients
Fan-out: Queue for subscribers
```

### Scalability

```
Redis pub-sub: Distribute across servers
Message queue: Buffer spikes
Sticky sessions: Client stays on same server
Vertical scaling: Increase connections per server
```

## Complexity

| Operation | Time |
|-----------|------|
| Connect | O(1) |
| Send | O(1) |
| Broadcast | O(n) |
| Join room | O(1) |
