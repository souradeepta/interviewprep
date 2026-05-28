# Chat System

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

A chat system must deliver messages between users in real-time, preserve message history, maintain
consistent read receipts, and show online presence — all at scale. WhatsApp serves 2B users, Slack
serves 18M daily active users, and Discord serves 500M registered users. The core challenge is
bidirectional real-time communication: unlike HTTP request/response, chat requires the server to
push messages to clients without the client polling.

In interviews, chat tests knowledge of WebSocket connection management, message fan-out for group
chats, cursor-based pagination for message history, and the trade-off between strong ordering (every
recipient sees messages in the same order) vs high availability.

## Functional Requirements

- Users can send 1:1 direct messages
- Users can create group conversations (up to 1,000 members)
- Messages are stored and retrievable as conversation history
- Delivery receipts: sent, delivered, read
- Online presence: show when users were last active
- Push notifications for offline users

## Non-Functional Requirements

- **Scale:** 100M DAU; 50 messages/user/day = 5B messages/day; store 5 years of history
- **Latency:** Message delivery P99 < 100ms for online recipients; P99 < 5s for offline (push)
- **Availability:** 99.99%; message loss is unacceptable
- **Consistency:** Messages within a conversation must be totally ordered (no two recipients see different orderings)

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Message volume:
  100M DAU × 50 messages/day = 5B messages/day
  5B ÷ 86400 = 57,870 messages/sec average
  Peak (5× average): ~290,000 messages/sec

Group chat fan-out:
  Average group size: 20 members
  Max group size: 1,000 members
  57,870 messages/sec × 20 avg recipients = 1.16M delivery events/sec

Storage:
  Each message: 300 bytes avg (text + metadata)
  5B × 300 bytes = 1.5 TB/day
  5 years: 1.5 TB × 365 × 5 = 2.7 PB (need object storage tiering)

Active WebSocket connections:
  100M DAU; assuming 30% online simultaneously = 30M connections
  30M WebSocket connections at 10KB RAM/connection = 300GB RAM across connection servers
  1,000 connection servers × 300MB each (30K connections/server) = manageable

Read receipts:
  Each message → N read receipt events (one per recipient when they see it)
  5B messages/day × 20 avg recipients = 100B receipt events/day (too many to store individually)
  Solution: store cursor position (last_read_message_id) per user per conversation
```

### Architecture Diagram

```
[Client A]                           [Client B] [Client C]
    │ WebSocket                          │ WebSocket
    │                                    │
    ▼                                    ▼
[Connection Service Tier]
  ┌──────────────────────────────────────────────────────┐
  │  WS-Server-1   WS-Server-2   WS-Server-3   ...      │
  │  (30K conns)   (30K conns)   (30K conns)            │
  │       │               │               │             │
  │  Route53 (DNS-based user pinning or LB sticky)      │
  └────────────────────┬─────────────────────────────────┘
                       │ (message received from Client A)
                       ▼
             ┌──────────────────┐
             │  Message Service │
             │  - Validate      │
             │  - Assign msg_id │
             │  - Persist to DB │
             │  - Enqueue fan-out│
             └────────┬─────────┘
                      │
          ┌───────────┼─────────────┐
          ▼           ▼             ▼
   [Cassandra    [Kafka topic:    [Presence
    messages]     chat_fanout]    Service]
                      │
                      ▼
             ┌──────────────────┐
             │  Fan-out Service │
             │  - Lookup members│
             │  - For each online│
             │    recipient:    │
             │    push via WS   │
             │  - For offline:  │
             │    push notify   │
             └──────────────────┘
                      │
             [Push Notification Service]
               APNs (iOS) / FCM (Android)

[Presence Service]
  Redis hash: user_id → { status: online, last_seen: epoch }
  TTL: 60s (renewed by client heartbeat every 30s)
```

### Data Model

```sql
-- Users
CREATE TABLE users (
    user_id    BIGINT PRIMARY KEY,
    username   VARCHAR(64) UNIQUE,
    phone      VARCHAR(20),
    created_at TIMESTAMP
);

-- Conversations (1:1 and group)
CREATE TABLE conversations (
    conv_id      BIGINT PRIMARY KEY,
    type         VARCHAR(10),  -- 'direct' | 'group'
    name         VARCHAR(256), -- null for direct; group name for group
    created_by   BIGINT,
    created_at   TIMESTAMP
);

-- Conversation members
CREATE TABLE conv_members (
    conv_id    BIGINT,
    user_id    BIGINT,
    joined_at  TIMESTAMP,
    PRIMARY KEY (conv_id, user_id)
);
CREATE INDEX idx_conv_members_user ON conv_members(user_id); -- "what convs is user in?"

-- Messages (Cassandra-style wide row model for efficient cursor pagination)
-- Partition key: conv_id; clustering key: msg_id DESC (newest first)
CREATE TABLE messages (
    conv_id    BIGINT,
    msg_id     BIGINT,    -- Snowflake ID (time-ordered; provides global ordering within conv)
    sender_id  BIGINT,
    body       TEXT,
    msg_type   VARCHAR(20) DEFAULT 'text',  -- text|image|video|file
    media_url  VARCHAR(512),
    status     VARCHAR(20) DEFAULT 'sent',  -- sent|delivered|read
    created_at TIMESTAMP,
    PRIMARY KEY ((conv_id), msg_id)
) WITH CLUSTERING ORDER BY (msg_id DESC);

-- Read receipts (per-user cursor, not per-message)
CREATE TABLE read_receipts (
    conv_id         BIGINT,
    user_id         BIGINT,
    last_read_msg_id BIGINT,  -- last message this user has seen
    updated_at      TIMESTAMP,
    PRIMARY KEY (conv_id, user_id)
);
```

### API Design

```
# Send message
POST /v1/conversations/{conv_id}/messages
  Body: { "body": "Hello!", "msg_type": "text" }
  Response: { "msg_id": "7109823456789", "status": "sent", "created_at": "..." }

# Retrieve conversation history (cursor-based, newest first)
GET /v1/conversations/{conv_id}/messages?limit=50&before_msg_id=<cursor>
  Response: {
    "messages": [
      { "msg_id": "...", "sender_id": "...", "body": "...", "created_at": "..." },
      ...
    ],
    "has_more": true,
    "next_cursor": "<msg_id of oldest in this batch>"
  }

# List conversations (inbox)
GET /v1/conversations?limit=20&before_cursor=<cursor>
  Response: { "conversations": [ { "conv_id": "...", "last_message": {...}, "unread_count": 3 } ... ] }

# Mark messages as read
POST /v1/conversations/{conv_id}/read
  Body: { "last_read_msg_id": "7109823456789" }
  Response: { "status": "ok" }

# WebSocket: real-time message delivery
WS /ws?token=<jwt>
  Server → Client events:
    { "type": "new_message", "conv_id": "...", "message": { ... } }
    { "type": "read_receipt", "conv_id": "...", "user_id": "...", "last_read_msg_id": "..." }
    { "type": "presence", "user_id": "...", "status": "online" | "offline" }
  Client → Server:
    { "type": "heartbeat" }
    { "type": "typing", "conv_id": "..." }
```

### Basic Scaling

- **WebSocket servers:** Stateful (each server holds open connections). Use consistent hashing or sticky sessions (IP hash at LB) so reconnecting clients land on the same server. 30M connections ÷ 30K per server = 1,000 servers.
- **Cassandra for messages:** Wide-row model partitioned by conv_id. All messages in a conversation stored together → efficient range queries (newest N messages). Time-ordered Snowflake IDs provide monotonic ordering within a partition.
- **Fan-out via Kafka:** Message service publishes to Kafka; fan-out workers look up online members and push via WebSocket publish-subscribe bus (Redis Pub/Sub to connection server). Offline members queued for push notification.
- **Presence in Redis:** Client sends heartbeat every 30s. Redis key "presence:{user_id}" with 60s TTL. Expiry = user went offline. Presence events published to Redis Pub/Sub for interested connections.

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
WebSocket connection management:
  30M concurrent connections
  Each WS connection: ~10KB RAM (socket buffer + connection state)
  30M × 10KB = 300GB RAM total across WS servers
  Per server: c6i.8xlarge (32 vCPU, 64GB RAM) → 6,400 connections/GB = 409,600 conns/server
  Servers needed: 30M / 409,600 ≈ 75 servers (leave 50% headroom → 150 WS servers)

Message write throughput to Cassandra:
  290K messages/sec peak × 300 bytes = 87 MB/sec
  Cassandra: single node sustains ~20K writes/sec with replication
  Nodes: 290K / 20K = 15 Cassandra nodes (with RF=3 → 45 physical nodes)

Fan-out throughput:
  290K messages/sec × 20 avg recipients = 5.8M fan-out events/sec
  Kafka: 30 partitions × 200K events/sec/partition = 6M events/sec (sufficient)
  Fan-out workers: 30 × c6i.2xlarge; each pushes 200K notifications/sec (Redis Pub/Sub)

Cassandra storage (5 years):
  2.7 PB total (5B msgs/day × 300B × 365 × 5)
  With RF=3: 8.1 PB raw
  45 nodes × 30TB SSD = 1.35PB → need ~200 nodes for 5 years OR tiered storage

Tiered storage optimization:
  Hot (< 30 days): Cassandra (fast random reads)
  Warm (30d - 1yr): S3 (object storage, query via Athena if needed)
  Cold (> 1yr): S3 Glacier (retrieval cost accepted for historical access)
  Cassandra holds only ~30 days: 45 TB/day × 30 = 1.35 PB → 45 nodes manageable
```

### Failure Modes

```
Scenario 1: WebSocket server dies (takes down 30K active connections)
  - 30K clients lose connection; client app detects TCP close
  - Client reconnects within 1-5s (exponential backoff + jitter)
  - Client re-subscribes to its conversations
  - Messages sent during the 1-5s outage: buffered in Kafka → delivered on reconnect
  - Guarantee: "delivered" receipt only sent after WS delivery confirmed + DB written
  - Prevention: load balancer health checks; auto-replace dead WS servers

Scenario 2: Kafka fan-out lag (message delivery delayed)
  - Kafka consumer lag grows → recipients see messages late
  - Detection: monitor Kafka consumer lag per partition; alert if lag > 1M events
  - Mitigation: scale fan-out consumer group; add partitions to Kafka topic
  - During lag: sender sees "sent" checkmark; recipient sees delivery checkmark only after fan-out

Scenario 3: Message ordering violation in group chat
  - Client A sends message at T=1, Client B sends at T=1.001
  - Two recipients on different WS servers might see B before A (race condition)
  - Fix: Snowflake ID assignment happens on Message Service (single writer per conv_id partition)
  - Cassandra stores by msg_id (Snowflake) order → all readers see same order
  - Total order within conversation guaranteed by single-partition assignment (hash by conv_id)

Scenario 4: Read receipt storm in large group
  - 1,000-member group receives a message
  - All 1,000 members open the app and send read receipts simultaneously
  - 1,000 read receipt writes/message × 57,870 messages/sec = 57M receipt events/sec
  - Fix: don't store individual read receipts; store last_read_msg_id per (conv_id, user_id)
  - Fix: batch read receipts (debounce: send max 1 receipt/user/conv/5s)
  - Fix: for large groups (>100 members), disable individual read receipts; show only aggregate count

Scenario 5: Group chat with 10M members (broadcast scenario)
  - Fan-out-on-write to 10M WebSocket connections is prohibitively expensive
  - Solution: fan-out-on-read (broadcast model)
    - Store message once in Cassandra
    - Each client polls "any new messages since my last_read_msg_id?" on reconnect
    - For real-time: shared channel with Kafka → clients subscribe to conv_id topic
    - No per-recipient fan-out; clients consume the shared topic directly
  - This is the Discord model for server channels with millions of members
```

### Consistency Boundaries

```
Message ordering (total order within conversation):
  Snowflake ID generated on Message Service when message is persisted
  Snowflake = 41 bits timestamp + 10 bits machine ID + 12 bits sequence
  Within same millisecond: sequence number provides tie-breaking
  Cassandra partition by conv_id: all messages for one conversation on one set of nodes
  Result: total order guaranteed within a conversation

Cross-conversation ordering: not required (conversations are independent)

Delivery guarantees:
  At-least-once: message written to Cassandra before fan-out
    If fan-out fails: client reconnect triggers "fetch messages since last_received_id"
    → missed messages delivered on reconnect (cursor-based catch-up)
  Exactly-once display: client deduplicates by msg_id (Snowflake)
    If same message delivered twice: second delivery is no-op (idempotent)

E2E encryption sketch (Signal protocol):
  Key exchange: X3DH (Extended Triple Diffie-Hellman) → shared secret per conversation
  Message encryption: Double Ratchet algorithm (forward secrecy per message)
  Server stores: encrypted ciphertext only; cannot read message content
  Key material: stored only on client devices
  Consequence: server cannot search message content; no server-side spam filtering
```

### Cost Model

```
Infrastructure for 100M DAU, 5B messages/day:

WebSocket servers (150 nodes):
  c6i.8xlarge ($1.088/hr × 150) = $119,808/month
  (Largest cost; driven by persistent connection RAM)

Kafka (fan-out messaging):
  30 brokers × m6i.4xlarge ($0.768/hr × 30) = $16,589/month

Cassandra cluster (30-day hot message storage):
  45 nodes × i4i.4xlarge ($1.196/hr × 45) = $38,488/month
  2 PB over 5 years with tiering; Cassandra holds only 1.35 PB (30 days)

S3 (warm + cold message archive):
  1.35 PB → S3 Standard (warm): 1 PB × $0.023/GB = $23,000/month
  Old data → S3 Glacier: 1.35 PB × $0.004/GB = $5,400/month

Redis cluster (presence + pub/sub):
  10 nodes × r6g.2xlarge ($0.378/hr × 10) = $2,722/month

Push notification services (APNs/FCM): free (provider service)

PostgreSQL (users, conversations, members):
  3 nodes (primary + 2 read replicas): db.r6g.4xlarge × 3 = $2,074/month

Total: ~$208K/month
Per-user cost: $208,000 / 100,000,000 = $0.002/user/month
Dominant cost: WebSocket servers (persistent connection RAM)
Optimization: reduce WS server count with virtual threads (Java 21) or Go goroutines
  Go handles 1M goroutines (connections) per server → reduce from 150 to 30 servers
  Go savings: 120 servers × $1.088 × 730hr = $95K/month
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **WebSocket (persistent)** | Bidirectional, low latency, server push | Stateful servers (sticky sessions needed), high RAM for connections | Real-time chat, gaming, live collaboration |
| **Server-Sent Events (SSE)** | Simple (HTTP), server push, automatic reconnect | Unidirectional (server → client only); client sends messages via separate HTTP POST | Notifications, feed updates, one-way live data |
| **Long-polling** | Works through proxies/firewalls that block WS, no special setup | High latency (one round-trip per message), server connection held open | Fallback for restricted corporate networks |
| **Fan-out-on-write (group)** | Instant delivery to all recipients | Write amplification for large groups (1K members × 57K msgs/sec) | Small groups (<100 members) |
| **Fan-out-on-read (broadcast)** | Single write regardless of group size | Client must poll/subscribe; no guaranteed instant delivery | Large groups (>1K members), channels, Discord servers |

## Follow-up Questions (escalating difficulty)

1. **(L3)** Why do chat systems use WebSockets instead of regular HTTP requests?
   → Regular HTTP is request-initiated (client polls server). For real-time chat, the server must push messages to clients as they arrive — impossible with HTTP polling without high latency or constant connections. WebSocket provides a persistent bidirectional TCP connection; the server can push at any time without a preceding client request. This reduces latency from polling_interval/2 average to near-zero.

2. **(L3)** How do you store messages so they can be paginated efficiently?
   → Use a NoSQL wide-row model (Cassandra) with conversation_id as the partition key and message_id (Snowflake timestamp) as the clustering key. This collocates all messages for one conversation on the same node. Pagination: `WHERE conv_id = ? AND msg_id < ? LIMIT 50` — efficient index scan, no offset needed.

3. **(L4)** How do you guarantee message ordering in a group chat when multiple servers are writing simultaneously?
   → Assign Snowflake IDs at the Message Service level (not the client). Messages are partitioned in Kafka by conv_id, ensuring a single ordered consumer writes all messages for one conversation. Cassandra stores by msg_id (monotonically increasing) and all readers read the same ordering. Clients display by msg_id order, ignoring client-side timestamps (which can be skewed by clock drift).

4. **(L4)** How do you handle the "unread count" badge on the app icon?
   → Per user per conversation, store last_read_msg_id. Unread count = number of messages with msg_id > last_read_msg_id. At read time: `SELECT COUNT(*) FROM messages WHERE conv_id = ? AND msg_id > ?`. For the total badge count (sum across all conversations): maintain a Redis counter per user (increment on new message, decrement on read). Redis counter provides O(1) lookup; DB query is fallback for correctness verification.

5. **(L5)** How does the Signal protocol provide end-to-end encryption without the server being able to decrypt messages?
   → Signal uses X3DH key exchange: client publishes bundle of public keys (identity key, signed prekey, one-time prekeys) to server. Sender fetches recipient's key bundle, derives a shared secret using Elliptic Curve Diffie-Hellman — a shared secret neither party's private key nor the server can compute independently. Messages encrypted with the Double Ratchet algorithm: each message uses a new key derived from the previous, providing forward secrecy (past messages can't be decrypted even if current key is compromised). Server stores and forwards only the encrypted ciphertext.

6. **(L5)** How do you handle message delivery to a user who is offline?
   → Three-layer delivery: (1) WebSocket push if user is online (fan-out service looks up presence in Redis → finds active WS server → pushes via Redis Pub/Sub to that server → user receives instantly). (2) If user is offline: Push Notification Service sends APNs (iOS) or FCM (Android) with message preview. (3) On app open: client sends "last_received_msg_id" → server returns all messages since that cursor (catch-up fetch). This ensures no messages are lost regardless of online status.

7. **(L5+)** Design the chat system to handle a 10M-member public channel (Discord server model) without fanout-on-write.
   → Public channels use a shared Kafka topic (one topic per channel, partitioned by message). Members don't receive individual fan-out writes; instead, they subscribe to the channel's Kafka topic offset directly via a Kafka consumer per WebSocket server cluster (not per user). When a WS server handles a connection for a user in a channel, it subscribes to that channel's topic. On new message: Kafka consumer gets it → pushes to all connected users subscribed to that channel on this server. Message storage: single write to Cassandra; no per-user fan-out. Read-on-demand: clients paginate via cursor from Cassandra. This is how Discord's "read states" system works — each client tracks its own last-seen offset per channel.

## Anti-patterns / Things NOT to Say

- **"Store a separate read receipt record for every (message, user) pair"** — With 5B messages/day × 20 recipients = 100B read receipt records/day. At 100 bytes each = 10TB/day of receipt data. Completely unscalable. Use cursor-based receipts: store only last_read_msg_id per (user, conversation). Unread count is derived from the cursor position, not from counting individual receipt rows.
- **"Use HTTP long-polling for real-time chat"** — Long-polling requires the server to hold an HTTP connection open (consuming a thread per user on most servers). At 30M concurrent users, that's 30M blocked threads. WebSocket connections are event-driven (no thread held per connection); 30M WebSocket connections use ~300GB RAM, not 30M threads. Long-polling is only a fallback for restricted networks.
- **"Use a relational DB with sequential IDs for message ordering"** — Sequential integer IDs from a single PostgreSQL sequence become a write bottleneck at 290K messages/sec. Auto-increment IDs require a global lock per insert. Use Snowflake IDs (distributed ID generation with embedded timestamps) — no coordination needed, naturally time-ordered, 4096 IDs/ms/machine.
- **"Fan-out-on-write for 1,000-member groups is fine"** — 1,000-member group at 290K messages/sec = 290M fan-out writes/sec. This exceeds the write capacity of any Redis cluster. Use fan-out-on-read (shared channel subscription) for groups above 100 members. WhatsApp limits group size to 1,024; Discord uses the broadcast model for large servers.

## Python Implementation (sketch)

```python
import time
import threading
import queue
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Callable

def snowflake_id(machine_id: int = 1) -> int:
    """Time-ordered unique ID: 41-bit ms timestamp + 10-bit machine + 12-bit seq."""
    ts = int(time.time() * 1000) & ((1 << 41) - 1)
    seq = getattr(snowflake_id, '_seq', 0)
    snowflake_id._seq = (seq + 1) & ((1 << 12) - 1)
    return (ts << 22) | (machine_id << 12) | snowflake_id._seq

@dataclass
class Message:
    msg_id: int
    conv_id: int
    sender_id: int
    body: str
    created_at: float = field(default_factory=time.time)

class ConversationStore:
    """In-memory Cassandra simulation: messages per conversation."""

    def __init__(self):
        # conv_id -> list of messages sorted by msg_id
        self._messages: Dict[int, List[Message]] = {}
        self._lock = threading.Lock()

    def save(self, msg: Message) -> None:
        with self._lock:
            self._messages.setdefault(msg.conv_id, []).append(msg)

    def get_history(self, conv_id: int, before_msg_id: Optional[int] = None,
                    limit: int = 50) -> List[Message]:
        with self._lock:
            msgs = self._messages.get(conv_id, [])
            if before_msg_id is not None:
                msgs = [m for m in msgs if m.msg_id < before_msg_id]
            return sorted(msgs, key=lambda m: m.msg_id, reverse=True)[:limit]

class PresenceService:
    """Redis TTL-based presence simulation."""

    def __init__(self, ttl_sec: float = 60.0):
        self._presence: Dict[int, float] = {}  # user_id → last_heartbeat epoch
        self._ttl = ttl_sec
        self._lock = threading.Lock()

    def heartbeat(self, user_id: int) -> None:
        with self._lock:
            self._presence[user_id] = time.time()

    def is_online(self, user_id: int) -> bool:
        with self._lock:
            last = self._presence.get(user_id, 0)
            return (time.time() - last) < self._ttl

class ConnectionServer:
    """Simulates a WebSocket server node with connected clients."""

    def __init__(self, server_id: int, presence: PresenceService):
        self.server_id = server_id
        self.presence = presence
        # user_id → callback (simulates WebSocket send)
        self._connections: Dict[int, Callable[[Message], None]] = {}
        self._lock = threading.Lock()

    def connect(self, user_id: int, callback: Callable[[Message], None]) -> None:
        with self._lock:
            self._connections[user_id] = callback
        self.presence.heartbeat(user_id)
        print(f"[Server {self.server_id}] User {user_id} connected")

    def disconnect(self, user_id: int) -> None:
        with self._lock:
            self._connections.pop(user_id, None)

    def deliver(self, user_id: int, msg: Message) -> bool:
        with self._lock:
            cb = self._connections.get(user_id)
        if cb:
            cb(msg)
            return True
        return False

    def connected_users(self) -> Set[int]:
        with self._lock:
            return set(self._connections.keys())

class MessageService:
    """Orchestrates message storage, ordering, and fan-out."""

    def __init__(self, store: ConversationStore, presence: PresenceService):
        self.store = store
        self.presence = presence
        # conv_id -> set of member user_ids
        self._members: Dict[int, Set[int]] = {}
        # server_id -> ConnectionServer
        self._servers: Dict[int, "ConnectionServer"] = {}
        # user_id -> server_id (routing table)
        self._routing: Dict[int, int] = {}
        self._lock = threading.Lock()

    def register_server(self, server: "ConnectionServer") -> None:
        self._servers[server.server_id] = server

    def register_connection(self, user_id: int, server_id: int) -> None:
        with self._lock:
            self._routing[user_id] = server_id

    def add_member(self, conv_id: int, user_id: int) -> None:
        self._members.setdefault(conv_id, set()).add(user_id)

    def send(self, conv_id: int, sender_id: int, body: str) -> Message:
        msg = Message(
            msg_id=snowflake_id(),
            conv_id=conv_id,
            sender_id=sender_id,
            body=body
        )
        self.store.save(msg)  # persist first
        self._fanout(msg)
        return msg

    def _fanout(self, msg: Message) -> None:
        members = self._members.get(msg.conv_id, set())
        for user_id in members:
            if user_id == msg.sender_id:
                continue
            server_id = self._routing.get(user_id)
            if server_id and self.presence.is_online(user_id):
                server = self._servers.get(server_id)
                if server:
                    delivered = server.deliver(user_id, msg)
                    if not delivered:
                        print(f"  → Push notification sent to offline user {user_id}")
            else:
                print(f"  → Push notification queued for user {user_id} (offline)")


# Demo
if __name__ == "__main__":
    store = ConversationStore()
    presence = PresenceService(ttl_sec=60)
    svc = MessageService(store, presence)

    # Two WebSocket servers
    ws1 = ConnectionServer(server_id=1, presence=presence)
    ws2 = ConnectionServer(server_id=2, presence=presence)
    svc.register_server(ws1)
    svc.register_server(ws2)

    received_by: Dict[int, List[str]] = {2: [], 3: [], 4: []}

    # Connect users
    ws1.connect(1, lambda m: None)              # sender
    ws1.connect(2, lambda m: received_by[2].append(m.body))
    ws2.connect(3, lambda m: received_by[3].append(m.body))
    # User 4 is offline

    for uid in [1, 2, 3]:
        svc.register_connection(uid, 1 if uid <= 2 else 2)
        presence.heartbeat(uid)

    # Group conversation with 4 members
    conv_id = 101
    for uid in [1, 2, 3, 4]:
        svc.add_member(conv_id, uid)

    # User 1 sends messages
    for i in range(3):
        msg = svc.send(conv_id, sender_id=1, body=f"Hello group! (msg {i+1})")
        time.sleep(0.001)

    print(f"\nReceived by user 2: {received_by[2]}")
    print(f"Received by user 3: {received_by[3]}")
    history = store.get_history(conv_id, limit=10)
    print(f"Conversation history ({len(history)} msgs): {[m.body for m in reversed(history)]}")
```
