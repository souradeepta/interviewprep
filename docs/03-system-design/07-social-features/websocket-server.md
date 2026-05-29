# WebSocket Server

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

HTTP is request-response: the client must ask, and the server answers. For real-time features —
chat, live notifications, collaborative editing, trading tickers, multiplayer game state — the
server must push data to the client without being asked. WebSockets provide a persistent, full-
duplex TCP connection that stays open, allowing the server to push messages the instant they are
available with < 10 ms delivery latency.

The design challenge is managing 10 million concurrent persistent connections across a cluster of
servers: a message to user X must reach whichever server currently holds X's connection, even
if the user reconnects to a different node. This requires a connection registry, a pub/sub
fan-out layer, and careful handling of backpressure, reconnection, and graceful deployment.

## Functional Requirements

- Establish a WebSocket connection and keep it alive (heartbeat/ping-pong)
- Server pushes messages to a specific user (unicast) or a topic (broadcast)
- Client sends messages to the server (bidirectional)
- Guarantee ordered delivery within a connection
- Handle client reconnection with message buffering (don't lose messages during brief disconnect)

## Non-Functional Requirements

- **Scale:** 10M concurrent WebSocket connections; 100K messages/sec published
- **Latency:** P99 < 100 ms from publish to client delivery (including fan-out)
- **Availability:** 99.9%; a server restart should not lose more than 30 sec of messages;
  clients reconnect automatically within 5 sec
- **Consistency:** At-least-once delivery; ordered delivery within a user's connection session

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Connections:      10M concurrent WebSocket connections
Memory per conn:  ~10 KB (kernel socket buffer + application state)
Total RAM:        10M * 10 KB = 100 GB for connection state
                  Deploy on 20 nodes with 8 GB per node for connections (plus OS overhead)

Messages/sec:     100K published messages/sec
Avg fan-out:      10 recipients per message (chat room, topic)
Total deliveries: 100K * 10 = 1M message deliveries/sec
Message size:     avg 500 bytes
Delivery throughput: 1M * 500 bytes = 500 MB/sec (across all nodes)

Per-node load:    10M connections / 20 nodes = 500K connections/node
                  Each node handles 500K * 1 heartbeat/30sec = 16.7K heartbeats/sec
                  At 500 bytes/heartbeat: 8.3 MB/sec heartbeat overhead per node (trivial)

Linux kernel tuning: default file descriptors = 1024; set to 1M+ per process
                     each WebSocket connection = 1 file descriptor
```

### Architecture Diagram

```
  Client (Browser / Mobile)
        |  WebSocket upgrade
  +-----v-----------+
  | Load Balancer   |  ← L7, WebSocket-aware, sticky sessions (optional)
  | (ALB or nginx)  |
  +-----+-----------+
        |
  +-----------+  +-----------+  +-----------+
  | WS Node 1 |  | WS Node 2 |  | WS Node N |   ← 20 nodes, 500K conns each
  | (Node.js  |  |           |  |           |
  |  Golang)  |  |           |  |           |
  +-----------+  +-----------+  +-----------+
        |              |              |
        +------+-------+------+-------+
               |
  +------------v-----------+
  | Redis Pub/Sub (channel  |  ← messages fan out to all WS nodes subscribed to topic
  | per user / per room)    |
  +------------+------------+
               |
  +------------v-----------+
  | Message Buffer / Store  |  ← Kafka or Redis Streams, for reconnect replay
  +------------------------+

Connection Registry:
  Key: conn:{user_id}  → ws_node_host:port
  Stored in Redis; TTL = 30 sec (refreshed by heartbeat)
  Used for: targeted push to specific user on specific node
```

### Data Model

```
# Connection registry (Redis, TTL-based)
Key:   conn:{user_id}     Value: "ws-node-2:8080"    TTL: 30s (refreshed on heartbeat)
Key:   conn:{conn_id}     Value: "{user_id, node, connected_at, last_ack_seq}"

# Room/topic subscriptions (Redis SET per room)
Key:   room:{room_id}:subscribers  → SET of user_ids
Key:   user:{user_id}:rooms        → SET of room_ids

# Message buffer (Redis Stream or Kafka — for reconnect replay)
# Redis Stream per user: last 100 messages, TTL=5min
Key:   stream:{user_id}  → Redis Stream entries
Entry: { msg_id, payload, timestamp }

# Message schema (wire format, JSON over WebSocket frame)
{
  "type": "message" | "ack" | "ping" | "pong" | "presence",
  "seq": 12345,             -- monotonically increasing per sender
  "room_id": "room_abc",    -- optional, for room messages
  "to_user_id": 42,         -- optional, for DMs
  "payload": { ... },
  "sent_at_ms": 1717000000000
}
```

### API Design

```
# WebSocket connection (HTTP Upgrade)
GET /ws
  Headers:
    Upgrade: websocket
    Connection: Upgrade
    Sec-WebSocket-Key: <base64>
    Authorization: Bearer <JWT>
  Response: 101 Switching Protocols
  → Connection upgraded; client receives messages pushed by server

# Messages sent over WebSocket (bidirectional, JSON frames)
Client → Server:
  { "type": "subscribe", "room_id": "room_abc" }
  { "type": "message", "room_id": "room_abc", "seq": 1, "payload": { "text": "hello" } }
  { "type": "message", "to_user_id": 99, "seq": 2, "payload": { "text": "hey" } }
  { "type": "ack", "last_seq": 47 }   -- acknowledge received up to seq 47
  { "type": "ping" }

Server → Client:
  { "type": "message", "seq": 47, "room_id": "room_abc", "payload": { ... } }
  { "type": "ack", "last_seq": 2 }
  { "type": "pong" }
  { "type": "presence", "user_id": 99, "status": "online" }

# REST API (for non-WS clients or server-side publish)
POST /publish
  Body: { "to_user_id": 42, "payload": { "type": "notification", "text": "..." } }
  Response: 200 { "delivered": true, "online": true }
  OR 200 { "delivered": false, "online": false, "queued": true }
```

### Basic Scaling

- **Connection stickiness:** Use IP-hash or cookie-based sticky sessions at the load balancer;
  client always reconnects to same node cluster (not strictly required with pub/sub fan-out, but
  reduces Redis lookups)
- **Redis Pub/Sub for fan-out:** Each WS node subscribes to Redis channels for the rooms/users
  it serves; when a message is published to `channel:room_abc`, all nodes subscribed to that
  channel receive it and push to their local connections
- **Connection registry in Redis:** TTL-based heartbeat refresh; allows any node to look up which
  node holds a given user's connection for targeted delivery
- **Reconnect buffering:** Store last N messages per user in Redis Stream (TTL=5 min); on
  reconnect, client sends `last_seq_received` and server replays missed messages

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
WS node sizing (Go or Node.js, high-concurrency):
  Target: 500K connections per node
  RAM: 500K * 10 KB (socket state + buffers) = 5 GB; use r6g.2xlarge (64 GB RAM) for headroom
  CPU: mostly I/O-bound; Go goroutines or Node.js event loop handles 500K idle conns on 4 vCPUs
       Message processing: 500K conns * 1 msg/sec * 1 μs/msg = 0.5 CPU-sec/sec = 0.5 vCPUs
  Net: 500K * 1 msg/sec * 500 bytes + 500K * 1 heartbeat/30sec * 100 bytes = 252 MB/sec per node
       r6g.2xlarge has 10 Gbps NIC = 1.25 GB/sec → well within limit

Linux tuning required:
  /etc/sysctl.conf:
    net.core.somaxconn = 65535
    net.ipv4.tcp_max_syn_backlog = 65535
    fs.file-max = 2000000         -- system-wide file descriptors
  /etc/security/limits.conf:
    * soft nofile 1000000         -- per-process file descriptors
    * hard nofile 1000000

Redis Pub/Sub sizing:
  100K messages/sec * 10 fan-out = 1M Redis pub/sub deliveries/sec
  Redis Pub/Sub throughput: ~500K messages/sec per node (single-threaded)
  Use Redis Cluster: 3 masters → 1M / 3 = 333K per master → within limit
  WS nodes subscribe to rooms they serve: avoid subscribing to ALL channels (fan-out storm)

Message buffer (Redis Streams):
  100K msg/sec * 500 bytes * 300 sec (5 min buffer) = 15 GB total → 5 GB per 3-node cluster
  Per-user stream: max 100 entries (MAXLEN) → storage bounded
  Redis Streams supports consumer groups for replay: efficient O(1) range reads
```

### Failure Modes

```
FAILURE: WebSocket node crashes (500K connections lost)
  Detection:    Connections drop; clients receive TCP RST
  Client:       Reconnect logic: exponential backoff starting 100 ms, max 30 sec
                Reconnect with last_seq_received header to request replay
  Server:       New node accepts connections; connection registry updated in Redis
  Message loss: Messages published while client disconnected are in Redis buffer (5 min window)
                On reconnect: server reads stream from last_ack_seq → replays missed messages
  Recovery:     Typical reconnect: < 5 sec; all messages within buffer window delivered

FAILURE: Redis Pub/Sub node crashes
  Detection:    WS nodes detect Redis connection failure within 2 sec
  Mitigation:   Redis Cluster auto-failover: replica promoted in < 30 sec
  During failover: WS nodes cannot publish/receive for 30 sec
  Mitigation:   WS nodes buffer outbound messages locally (in-process queue, max 1000 messages)
                Flush buffer when Redis reconnects
  Message loss: messages published during 30-sec window may be lost for offline clients
  Accept:       Real-time feature; 30-sec outage acknowledged; non-critical messages lost

FAILURE: Connection draining during deployment (rolling restart)
  Naive approach: kill node → 500K clients reconnect simultaneously → thundering herd on remaining nodes
  Solution:     Graceful drain: (1) Mark node "draining" in load balancer → no new connections
                (2) Send close frame to all connected clients with code 1001 (Going Away) + hint URL
                (3) Clients reconnect immediately to other nodes (load balancer distributes)
                (4) Wait 30 sec for all clients to reconnect, then terminate process
  Result:       Zero-message-loss deployment; reconnects spread over 30 sec (no thundering herd)

FAILURE: Back-pressure (client can't consume messages as fast as server publishes)
  Detection:    Client send buffer > threshold (e.g., > 100 messages queued unacked)
  Mitigation:   Pause publishing to that connection; wait for ACKs to clear backlog
                If buffer grows beyond limit (e.g., > 1000 messages): close connection with 1008 (Policy Violation)
                Client reconnects; replays from last ack
  Long-term:    Reduce fan-out (don't send to clients that are clearly slow consumers)
```

### Consistency Boundaries

```
ORDERED DELIVERY (within a connection):
  Each message has a monotonically increasing seq number per (sender, channel)
  Receiver verifies: if received seq != expected seq → gap detected → request replay
  WS is a TCP stream → ordering guaranteed by TCP within a connection
  After reconnect: TCP stream is new; use seq numbers to detect and fill gaps

AT-LEAST-ONCE vs EXACTLY-ONCE:
  At-least-once (default): server publishes → Redis Pub/Sub → WS node → client push
    If push fails: message stays in Redis buffer → reconnect triggers replay
    Risk: if client ACKs before processing → message not replayed on crash → at-most-once
    If client ACKs after processing → guaranteed at-least-once

  Exactly-once (harder):
    Client sends idempotency key with every message → server deduplicates
    Redis SET NX {idem_key} TTL=5min → if key exists, skip processing
    Use for financial messages, game state updates where duplicates cause bugs

PRESENCE CONSISTENCY:
  User A connects → conn:{A} set in Redis (TTL=30s)
  User A disconnects → conn:{A} key expires after 30 sec (not immediate!)
  Window: up to 30 sec where A appears online but isn't
  Fast notification: WebSocket server explicitly DEL conn:{A} on clean disconnect
  Can't guarantee: process crash → key expires after TTL (30 sec stale presence)
  Accept: 30-sec presence staleness is fine for chat; not acceptable for trading systems
```

### Cost Model

```
WS server nodes (20× r6g.2xlarge, 8 vCPU + 64 GB RAM):
  20 * $0.405/hr * 8760 = $70,956/yr

Redis cluster (6-node r6g.xlarge for pub/sub + streams):
  6 * $0.227/hr * 8760 = $11,939/yr

Load balancer (ALB, WebSocket-aware):
  1M new connections/day * $0.008/LCU ≈ $50/day = $18,250/yr

Network (data transfer):
  10M connections * 1 msg/sec * 500 bytes = 5 GB/sec
  Intra-AZ: free; inter-AZ: $0.01/GB
  Assuming 30% cross-AZ: 1.5 GB/sec * $0.01 * 86400 * 365 = $473K/yr  ← significant
  Optimization: deploy all WS nodes in same AZ as Redis → minimize cross-AZ traffic

Total: ~$575K/yr for 10M concurrent connections
Per connection: $575K / (10M * 8760) = $0.0000066/connection-hour

Compare to AWS API Gateway WebSocket:
  $1/million messages; 10M conns * 1 msg/sec * 86400 * 365 = 315 trillion messages/yr
  Cost: $315M/yr → 547× more expensive than self-managed at this scale
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| WebSocket (TCP persistent) | Full-duplex; low latency; wide browser support; efficient for frequent messages | Persistent connections use resources even when idle; complex load balancing; sticky session complications | Chat, live feeds, collaborative editing, gaming |
| Server-Sent Events (SSE) | Simple (HTTP); automatic reconnect built-in; no special LB config; works with HTTP/2 | Server-to-client only (unidirectional); no binary messages; HTTP overhead per connection | Live dashboards, notifications, read-only real-time streams |
| Long Polling (HTTP) | Simple; works everywhere; no persistent connection; easy to scale horizontally | High latency (1 extra round trip); more HTTP overhead; server holds connections open | Legacy clients, fallback when WS is blocked by firewalls |
| WebRTC Data Channel | Peer-to-peer (no server relay needed); ultra-low latency; UDP-based | Complex setup (signaling server still needed); not suitable for server-push; browser only | Real-time gaming, video chat, P2P file sharing |

## Follow-up Questions (escalating difficulty)

1. **(L3)** What is the WebSocket handshake process?
   → Client sends an HTTP GET request with `Upgrade: websocket` header. Server responds with
   `101 Switching Protocols`. The TCP connection is then promoted from HTTP to WebSocket protocol.
   From this point, both sides can send framed binary or text messages at any time without the
   HTTP request-response cycle.

2. **(L3)** Why can't you just use regular HTTP polling instead of WebSockets?
   → Polling: client sends a request every N seconds. Problems: (1) Latency = N seconds worst
   case; (2) Each poll is a full HTTP request (headers, TLS overhead); (3) 1M clients * 1 poll/sec
   = 1M HTTP requests/sec even when there's nothing new — wasted resources. WebSocket: one
   TCP connection, server pushes when available, < 10 ms latency, minimal overhead.

3. **(L4)** If user X is connected to node A and a message is published on node B, how does it
   reach X?
   → Node B looks up `conn:{X}` in Redis → finds "node A". Options: (1) Node B sends message
   to node A via Redis Pub/Sub (`PUBLISH user:{X} <message>`) → node A subscribed to this
   channel → pushes to X's connection. (2) Node B makes HTTP call to node A's internal API.
   Redis Pub/Sub is preferred: decoupled, no direct service-to-service dependency.

4. **(L4)** How do you handle 500K clients reconnecting simultaneously when a node crashes?
   → Thundering herd problem. Mitigation: (1) Exponential backoff with jitter on client reconnect:
   `delay = base_delay * 2^attempt + random(0, 500ms)` — spreads reconnects over time. (2)
   Load balancer distributes reconnects across remaining nodes automatically. (3) Rate limit
   new connection accepts per node (e.g., max 5K new connections/sec) to prevent overload.

5. **(L5)** How do you implement graceful deployment (rolling restart) without dropping connections?
   → (1) Mark node as "draining" in load balancer (stop sending new connections). (2) Send
   WebSocket close frame `1001 Going Away` with reconnect hint to all 500K clients. (3) Clients
   immediately reconnect to other nodes (load balancer distributes). (4) Node waits up to
   60 sec for all clients to reconnect, then shuts down. Result: clients experience a
   disconnect/reconnect (< 5 sec) but no message loss (buffer in Redis covers the gap).

6. **(L5)** How do you implement backpressure when a client's send buffer is full?
   → Each WebSocket connection has a kernel send buffer (default: 4 KB, tunable to 256 KB).
   When full: the write() syscall blocks (or returns EAGAIN for non-blocking I/O). In an async
   event loop: if write would block, stop reading from the pub/sub queue for this connection.
   Maintain an application-level per-connection queue with a high-water mark. If queue exceeds
   limit: send PAUSE signal to publisher (or just drop low-priority messages for this client);
   resume when queue drains below low-water mark.

7. **(L5+)** How would you scale to 100M concurrent WebSocket connections (10× current design)?
   → 100M connections * 10 KB = 1 TB of RAM for connections. Options:
   (1) Scale to 200 nodes (500K connections each) — linear scaling works for stateless WS nodes.
   (2) Co-locate WS nodes with Redis to minimize latency (same AZ, same rack if possible).
   (3) Shard connection registry: hash user_id → Redis shard for O(1) lookup without hot key.
   (4) Replace Redis Pub/Sub with Kafka for fan-out (Redis Pub/Sub bottlenecks at ~1M deliveries/sec;
   Kafka handles 10M+/sec with proper partitioning).
   (5) Accept some connection loss: instead of storing all state in Redis, allow nodes to serve as
   authoritative for their own connections; publish to Kafka for cross-node delivery; lose messages
   only for clients who are mid-reconnect (within 5-sec window).

## Anti-patterns / Things NOT to Say

- **"Store WebSocket connection objects in a database"** — Connection objects are live kernel
  sockets — in-memory, node-local, ephemeral. You can store metadata (user_id → node mapping)
  in Redis, but the connection itself lives only in the process that accepted it. Storing
  connections in DB is meaningless.
- **"WebSocket works just like HTTP — just keep the connection open"** — WebSocket requires
  specific load balancer support (L7 proxy mode for HTTP upgrades, TCP mode for established
  connections). Many older load balancers time out idle connections after 60 sec. You need
  application-level heartbeats (ping/pong every 30 sec) AND LB idle timeout set to > 60 sec.
- **"Use a single Redis channel for all 10M users"** — Broadcasting to one channel means all
  10M WS nodes receive every message even if only 1 user on that node needs it. Use per-user
  and per-room channels: subscribe only to channels relevant to users on that node.
- **"Reconnect immediately on disconnect"** — All 500K clients on a crashed node reconnecting
  simultaneously is a thundering herd. Always use exponential backoff with jitter: `delay =
  min(30s, base_delay * 2^attempt) + random jitter`. Without jitter: periodic synchronized
  spikes overwhelm the remaining nodes.
- **"WebSocket guarantees delivery"** — WebSocket provides ordering and framing on top of TCP.
  TCP guarantees in-order delivery within a session. When the connection drops: in-flight
  messages are lost. You must implement application-level acknowledgment + sequence numbers
  + server-side message buffer to guarantee at-least-once delivery across reconnects.

## Python Implementation (sketch)

```python
import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Connection:
    conn_id: str
    user_id: int
    writer: asyncio.StreamWriter
    last_seq_sent: int = 0
    last_ack_received: int = 0
    pending: list[dict] = field(default_factory=list)  # unACKed messages

class ConnectionRegistry:
    """In-memory registry; use Redis in production with TTL heartbeats."""

    def __init__(self):
        self._by_user: dict[int, Connection] = {}
        self._by_conn: dict[str, Connection] = {}

    def register(self, conn: Connection) -> None:
        self._by_user[conn.user_id] = conn
        self._by_conn[conn.conn_id] = conn

    def unregister(self, conn_id: str) -> None:
        conn = self._by_conn.pop(conn_id, None)
        if conn:
            self._by_user.pop(conn.user_id, None)

    def get_by_user(self, user_id: int) -> Optional[Connection]:
        return self._by_user.get(user_id)

class WebSocketServer:
    def __init__(self):
        self.registry = ConnectionRegistry()
        self._rooms: dict[str, set[int]] = {}       # room_id → set of user_ids

    async def handle_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        import uuid
        conn_id = str(uuid.uuid4())
        user_id = 42  # In production: validate JWT from HTTP upgrade headers
        conn = Connection(conn_id=conn_id, user_id=user_id, writer=writer)
        self.registry.register(conn)
        print(f"[+] User {user_id} connected (conn {conn_id})")

        try:
            while True:
                data = await asyncio.wait_for(reader.read(4096), timeout=30.0)
                if not data:
                    break
                msg = json.loads(data.decode())
                await self._handle_message(conn, msg)
        except asyncio.TimeoutError:
            # No data for 30 sec → send ping
            await self._send(conn, {"type": "ping"})
        except Exception as e:
            print(f"[-] User {user_id} error: {e}")
        finally:
            self.registry.unregister(conn_id)
            writer.close()
            print(f"[-] User {user_id} disconnected")

    async def _handle_message(self, conn: Connection, msg: dict) -> None:
        msg_type = msg.get("type")
        if msg_type == "subscribe":
            room_id = msg["room_id"]
            self._rooms.setdefault(room_id, set()).add(conn.user_id)
        elif msg_type == "message":
            if "room_id" in msg:
                await self._publish_to_room(conn.user_id, msg["room_id"], msg["payload"])
            elif "to_user_id" in msg:
                await self._publish_to_user(msg["to_user_id"], msg["payload"])
        elif msg_type == "ack":
            conn.last_ack_received = msg.get("last_seq", conn.last_ack_received)
            conn.pending = [m for m in conn.pending if m["seq"] > conn.last_ack_received]
        elif msg_type == "pong":
            pass  # heartbeat ack, update last_seen

    async def _send(self, conn: Connection, payload: dict) -> None:
        conn.last_seq_sent += 1
        payload["seq"] = conn.last_seq_sent
        conn.pending.append(payload)
        data = json.dumps(payload).encode() + b"\n"
        conn.writer.write(data)
        await conn.writer.drain()

    async def _publish_to_room(self, from_user: int, room_id: str, content: dict) -> None:
        user_ids = self._rooms.get(room_id, set())
        for uid in user_ids:
            if uid == from_user:
                continue
            target = self.registry.get_by_user(uid)
            if target:
                await self._send(target, {"type": "message", "room_id": room_id,
                                          "from": from_user, "payload": content})

    async def _publish_to_user(self, user_id: int, content: dict) -> None:
        target = self.registry.get_by_user(user_id)
        if target:
            await self._send(target, {"type": "message", "payload": content})
        # else: buffer in Redis for reconnect delivery (not shown)


# Start server (in production: use uvicorn/websockets/fastapi-ws)
async def main():
    server = WebSocketServer()
    srv = await asyncio.start_server(server.handle_connection, "0.0.0.0", 8765)
    print("WebSocket server on ws://localhost:8765")
    async with srv:
        await srv.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
```
