# Real-Time Systems: Building Low-Latency Interactive Applications

**Level:** L4-L5
**Time to read:** ~20 min

Master real-time communication patterns for live updates and streaming.

---

## Real-Time Communication Protocols

### HTTP Long Polling

```
Client                    Server
  │                         │
  ├──────── GET /data ─────→│
  │                         │
  │                    Wait for data
  │                         │
  │←───────── response ────────┤
  │                         │
  ├──────── GET /data ─────→│  (repeat)
  │                         │
```

**Pros:** Simple, works everywhere
**Cons:** High latency (polling interval), wasteful (many empty responses)

### WebSocket

```
Client                    Server
  │                         │
  ├─────── Upgrade ────────→│
  │                         │
  │←────────────────────────┤
  │         (full duplex)    │
  │←─────── Data stream ────┤
  │                         │
  ├─────── Data ───────────→│
  │                         │
```

**Pros:** True bidirectional, low latency, efficient
**Cons:** Requires WebSocket support, stateful connection

### Server-Sent Events (SSE)

```
Client                    Server
  │                         │
  ├──── GET /events ───────→│
  │                         │
  │←─── Event stream ──────┤
  │  (HTML5, unidirectional)│
  │                         │
  │←─── Another event ─────┤
  │                         │
```

**Pros:** Simple, automatic reconnect, one-way (no uploads)
**Cons:** Text-only, unidirectional

---

## WebSocket Architecture

### Connection Management

```python
from fastapi import WebSocket

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await websocket.accept()
    
    # Add to active connections
    manager.connect(client_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            # Broadcast to all or specific users
            await manager.broadcast(f"User {client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
```

### Scaling WebSockets

```
Problem: One server can handle ~10K concurrent WebSocket connections
Solution: Multiple servers + message broker

User1 → Server1 (WebSocket)
              ├─ Redis Pub/Sub ─ Server2
User2 → Server2 (WebSocket)
              └─ Kafka
User3 → Server3 (WebSocket)

Message from User1 → Server1 → Pub/Sub → Other Servers → Connected users
```

---

## Real-Time Use Cases

### 1. Chat System

```
User A sends message
  ↓
Server stores in DB
  ↓
Server publishes to Redis (channel: chat:{room_id})
  ↓
All connected users in room receive via WebSocket
  ↓
Offline users get from DB history
```

### 2. Live Notifications

```
Event (new order, comment, like)
  ↓
Publish to Kafka/Redis
  ↓
Notification service processes
  ↓
Send to all connected devices via WebSocket
  ↓
Mobile push for offline users
```

### 3. Live Leaderboard

```
Score updates (gaming, competition)
  ↓
Update Redis leaderboard (sorted set)
  ↓
Publish update event
  ↓
All connected users see live rank changes
```

---

## Latency Considerations

```
WebSocket connection: ~1ms (overhead)
Message transmission: 1-10ms (network)
Processing: 10-100ms (application)
Database write: 5-20ms
Broadcast to 100 users: 20-50ms
Total: 50-180ms (acceptable for real-time)

Target: P99 latency < 500ms
```

---

## Handling Scale

### Concurrent Connections

```
Server capacity:
- Memory: 100MB per connection × capacity
- CPU: Limited by message broadcasting
- Network: Limited by bandwidth

For 1M concurrent users:
- 1000 servers (1K connections each)
- 100GB+ RAM total
- Message broker for broadcast (Redis, Kafka)
```

### Message Ordering

```
Problem: Messages arrive out of order
Solution:
1. Sequence number per user
2. Client reorders on receive
3. Server processes in order per connection
```

---

## Real-Time System Checklist

- ✓ Chose right protocol (WebSocket for low latency)
- ✓ Connection management (connect/disconnect)
- ✓ Heartbeat/keepalive to detect dead connections
- ✓ Message broker for multi-server broadcast
- ✓ Persistence (store messages for offline users)
- ✓ Scalability plan (horizontal scaling of WebSocket servers)
- ✓ Monitoring: connection count, message latency
- ✓ Graceful degradation (fallback to polling if needed)
- ✓ Security (auth, rate limiting, message validation)
- ✓ Testing: concurrent connections, latency under load

