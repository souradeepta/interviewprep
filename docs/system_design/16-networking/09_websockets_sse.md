# WebSockets and Server-Sent Events

## Problem Statement

Design real-time communication channels — WebSockets for bidirectional messaging, SSE for server-to-client push.

## Scenario

WebSockets and Server-Sent Events is a critical component in modern distributed systems. In real-world applications, capturing state changes as immutable events for audit trails. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

## Users

- **Backend Engineers**: Responsible for implementing and maintaining this system component in production environments. They need to understand the architecture, trade-offs, failure modes, and operational considerations.
- **DevOps/SRE Teams**: Monitor system health, manage scaling policies, handle incidents, and ensure reliability SLAs are met. They need insights into performance characteristics, bottlenecks, and failure recovery mechanisms.
- **Data Engineers**: Design data pipelines and analytics around this system, requiring deep understanding of data flow, consistency guarantees, and throughput characteristics.
- **System Architects**: Make high-level architectural decisions that impact company infrastructure, requiring comprehensive understanding of capabilities, limitations, and scalability boundaries.
- **Security Teams**: Understand security implications, potential vulnerabilities, and compliance requirements for this component.

## PRD

**Functional Requirements:**
- Correct behavior under all specified operating conditions
- Reliable operation with explicit failure modes
- Data consistency or eventual consistency guarantees as specified
- Clear mechanisms for error handling and recovery
- Monitoring and observability hooks

**Non-Functional Requirements:**
- **Performance**: Sub-100ms P99 latency for standard operations; measure and track tail latencies
- **Availability**: 99.99%+ uptime with automatic failover and graceful degradation
- **Scalability**: Support 10-100x current load with minimal architectural modifications
- **Consistency**: Specify whether strong, eventual, or causal consistency is required
- **Cost Efficiency**: Minimize operational cost per unit of throughput; consider compute, memory, and network costs
- **Operational Simplicity**: Reduce complexity to minimize human error and operational toil

**Constraints:**
- Resource limits (memory for caches, disk for databases, network bandwidth)
- Deployment constraints (cloud provider limits, regulatory requirements)
- Latency budgets (maximum acceptable delay for operations)

## Flow

The typical operational flow for this system involves these key phases:

1. **Request Arrival**: Client/upstream system sends request with required parameters and context
2. **Validation & Routing**: System validates request format, authentication, and routes to correct handler/shard/instance
3. **Core Processing**: Execute the main algorithm, database query, or business logic on the data/state
4. **State Management**: Update internal state (caches, indexes, counters, logs) with proper atomicity and locking
5. **Response Generation**: Format results and return to requester with relevant metadata (timing, version info)
6. **Observability**: Record metrics (latency, throughput, errors), logs (for debugging), and traces (for performance analysis)

This flow repeats thousands or millions of times per second in production. Each operation's efficiency compounds across the entire system, making careful optimization essential. Bottlenecks at any phase can cascade to impact overall system performance.

## Code Explanation

The provided implementations demonstrate key architectural concepts and design patterns:

**Python Implementation**: Uses built-in Python structures and standard library features to express the core logic clearly. Python emphasizes readability and conciseness—each operation's purpose should be obvious without extensive comments. You'll see different implementation approaches (e.g., using OrderedDict vs. manual linked lists) that represent trade-offs between convenience and fine-grained control.

**Java Implementation**: Shows how to implement the same logic with explicit memory management and type safety. Java's strong typing forces clear interface design; you'll see how generics, null safety, mutable state, and thread safety are handled. This implementation style is closer to production systems at scale.

**Key Implementation Patterns**:
- **Initialization**: Setting up core data structures, thread pools, or connection pools with specified capacity and configuration
- **Read Operations**: Fetching data while maintaining O(1) or O(log n) access, updating metadata (access times, hit counts, etc.)
- **Write Operations**: Inserting/updating data while handling eviction policies, balancing tree structures, or replicating state
- **Edge Cases**: Handling capacity limits, concurrent access, data consistency, and error conditions
- **Performance Optimization**: Using techniques like batch operations, lazy evaluation, or caching to reduce latency

Each line of code represents a deliberate choice about performance characteristics, memory usage, safety guarantees, and implementation complexity. Understanding these trade-offs is essential for using this component effectively in production systems.

## Architecture Diagram

```mermaid
graph TB
    C1[Client 1] -->|WebSocket| WS1[WS Server 1]
    C2[Client 2] -->|WebSocket| WS1
    C3[Client 3] -->|WebSocket| WS2[WS Server 2]
    WS1 -->|Publish| Redis[Redis Pub/Sub]
    WS2 -->|Subscribe| Redis
    Redis -->|Fan-out| WS1
    Redis -->|Fan-out| WS2
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant S as WebSocket Server

    C->>S: HTTP GET /ws Upgrade: websocket Connection: Upgrade
    S-->>C: 101 Switching Protocols
    Note over C,S: Full-duplex connection established

    C->>S: {"type":"join","room":"chat-1"}
    S-->>C: {"type":"ack","room":"chat-1"}
    S-->>C: {"type":"message","text":"Hello from Bob!"}
    C->>S: {"type":"message","room":"chat-1","text":"Hi!"}
    C->>S: Close frame (opcode 0x8)
    S-->>C: Close frame
```

## Design

### WebSocket vs SSE vs Long Polling

| Feature | WebSocket | SSE | Long Polling |
|---|---|---|---|
| Direction | Bidirectional | Server to client | Server to client |
| Protocol | WS upgrade (TCP) | HTTP | HTTP |
| Auto-reconnect | Manual | Automatic | Manual |
| Browser support | All modern | All (no IE) | All |
| Proxy friendly | Sometimes blocked | Yes (port 80/443) | Yes |
| Use case | Chat, games, collab | Notifications, feeds | Legacy fallback |

### Scaling Strategy

```
Problem: WebSocket connections are stateful (tied to one server)

Solution 1 - Redis Pub/Sub:
  Each server subscribes to channels
  Message published to Redis -> all servers receive -> fan out to local clients
  Latency: +1-2ms for Redis hop

Solution 2 - Kafka:
  Messages on topic partitioned by room/user
  Each server consumes its partitions
  Better for ordered, durable delivery

Solution 3 - Sticky load balancing:
  Same user always hits same server (cookie/IP hash)
  Simpler but server failure breaks all sessions
```

### SSE Auto-Reconnect

```
Server sends: id: 42\nevent: update\ndata: {"count":5}\n\n
Client stores: Last-Event-ID=42
On disconnect: browser auto-reconnects
On reconnect:  sends header Last-Event-ID: 42
Server can:    replay missed events
```

## Common Questions & Answers

**Q: How many WebSocket connections per server?** A: Each is a TCP socket (file descriptor). Linux tunable via `ulimit`. With event-driven I/O (epoll): 100K-1M connections per server with sufficient RAM (~50KB per connection).

**Q: WebSocket vs HTTP/2 server push?** A: HTTP/2 push is unidirectional and was deprecated. WebSocket is true bidirectional. For notifications only, SSE over HTTP/2 is simpler.

**Q: How to handle message ordering?** A: Single server: FIFO guaranteed. Multi-server: include sequence numbers, use Kafka partition per user for guaranteed ordering.

**Q: What is the WebSocket ping/pong?** A: Heartbeat mechanism. Server sends Ping frame, client must respond with Pong. Keepalive every 30s prevents NAT/firewall from closing idle connections.

**Q: SSE vs WebSocket for notifications?** A: For notifications (server pushes only): SSE is simpler, uses standard HTTP, auto-reconnect built-in. Use WebSocket only when client also needs to send messages.

## Back-of-Envelope Calculations

```
WebSocket memory per server:
  Each connection: ~50KB (kernel send/recv buffers)
  100K connections: 5GB RAM
  Message: 256 bytes x 100K connections = 25MB per broadcast

Redis Pub/Sub throughput:
  Single Redis: ~100K msg/sec
  1M subscribers across 10 servers: 1M/10 = 100K deliveries per server
  Redis handles 10 servers subscribing: 100K msg/sec x 10 = 1M/sec fan-out

Heartbeat overhead:
  30s interval x 100K connections = 3,333 pings/sec
  Negligible: <1 Mbps for ping/pong frames

SSE vs WebSocket memory:
  SSE: standard HTTP connection, same memory as HTTP keepalive (~8KB)
  WebSocket: ~50KB (larger kernel buffers for bidirectional)
  SSE is 6x more memory efficient for receive-only clients
```

## Design Choices

| Scenario | Choice | Reason |
|---|---|---|
| Chat application | WebSocket | Bidirectional messaging |
| Live notifications | SSE | Simple, auto-reconnect |
| Collaborative editor | WebSocket | Low latency, OT/CRDT sync |
| Stock price ticker | SSE | Server push only |
| Multiplayer game | WebSocket or UDP | Lowest latency |
| Dashboard updates | SSE | Simple, standard HTTP |

## Follow-up Questions

1. How would you implement presence (online/offline status) at scale?
2. How does Socket.IO handle WebSocket fallback to polling?
3. Design a chat system guaranteeing message ordering across servers.
4. How do you implement backpressure for slow WebSocket clients?
5. How do you handle WebSocket connections behind a load balancer?

## Python Implementation

```python
import asyncio
import json
from typing import Dict, Set, Optional, Callable
from collections import defaultdict

class WSConnection:
    def __init__(self, conn_id: str, user_id: str):
        self.conn_id = conn_id
        self.user_id = user_id
        self._outbox: asyncio.Queue = asyncio.Queue()
        self.rooms: Set[str] = set()

    async def send(self, msg: dict):
        await self._outbox.put(json.dumps(msg))

    async def recv(self) -> Optional[str]:
        try:
            return await asyncio.wait_for(self._outbox.get(), timeout=30.0)
        except asyncio.TimeoutError:
            return None  # Timeout -> send ping

class WSServer:
    def __init__(self):
        self._conns: Dict[str, WSConnection] = {}
        self._rooms: Dict[str, Set[str]] = defaultdict(set)

    def connect(self, conn_id: str, user_id: str) -> WSConnection:
        c = WSConnection(conn_id, user_id)
        self._conns[conn_id] = c
        return c

    def disconnect(self, conn_id: str):
        c = self._conns.pop(conn_id, None)
        if c:
            for room in c.rooms:
                self._rooms[room].discard(conn_id)

    def join(self, conn_id: str, room: str):
        c = self._conns[conn_id]
        c.rooms.add(room)
        self._rooms[room].add(conn_id)

    async def broadcast(self, room: str, msg: dict, exclude: str = None):
        tasks = [
            self._conns[cid].send(msg)
            for cid in self._rooms.get(room, set())
            if cid != exclude and cid in self._conns
        ]
        await asyncio.gather(*tasks)

    async def handle(self, conn_id: str, raw: str):
        data = json.loads(raw)
        if data["type"] == "join":
            self.join(conn_id, data["room"])
            await self._conns[conn_id].send({"type": "ack", "room": data["room"]})
        elif data["type"] == "message":
            await self.broadcast(data["room"], {
                "type": "message", "from": conn_id, "text": data["text"]
            }, exclude=conn_id)

# SSE implementation
class SSEBroker:
    def __init__(self):
        self._clients: Dict[str, asyncio.Queue] = {}
        self._seq = 0

    def subscribe(self, client_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._clients[client_id] = q
        return q

    def unsubscribe(self, client_id: str):
        self._clients.pop(client_id, None)

    async def publish(self, event: str, data: dict):
        self._seq += 1
        frame = f"id: {self._seq}\nevent: {event}\ndata: {json.dumps(data)}\n\n"
        await asyncio.gather(*[q.put(frame) for q in self._clients.values()])

# Demo
async def demo():
    server = WSServer()
    c1 = server.connect("c1", "alice")
    c2 = server.connect("c2", "bob")
    server.join("c1", "general")
    server.join("c2", "general")

    await server.handle("c1", json.dumps({"type": "message", "room": "general", "text": "Hello!"}))
    msg = await c2.recv()
    print(json.loads(msg))  # {"type": "message", "from": "c1", "text": "Hello!"}

asyncio.run(demo())
```

## Java Implementation

```java
import java.util.*;
import java.util.concurrent.*;
import java.util.function.Consumer;

public class WSServer {
    record Conn(String id, String userId, BlockingQueue<String> outbox, Set<String> rooms) {}

    private Map<String, Conn> conns = new ConcurrentHashMap<>();
    private Map<String, Set<String>> rooms = new ConcurrentHashMap<>();

    public Conn connect(String id, String userId) {
        Conn c = new Conn(id, userId, new LinkedBlockingQueue<>(), ConcurrentHashMap.newKeySet());
        conns.put(id, c);
        return c;
    }

    public void join(String connId, String room) {
        conns.get(connId).rooms().add(room);
        rooms.computeIfAbsent(room, k -> ConcurrentHashMap.newKeySet()).add(connId);
    }

    public void broadcast(String room, String msg, String exclude) {
        rooms.getOrDefault(room, Set.of()).stream()
            .filter(id -> !id.equals(exclude))
            .map(conns::get).filter(Objects::nonNull)
            .forEach(c -> c.outbox().offer(msg));
    }

    public void disconnect(String connId) {
        Conn c = conns.remove(connId);
        if (c != null) c.rooms().forEach(r -> rooms.getOrDefault(r, Set.of()).remove(connId));
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Connect/disconnect | O(1) |
| Join room | O(1) |
| Broadcast to room | O(n) subscribers |
| Send to connection | O(1) queue push |
| Memory per connection | ~50KB (kernel buffers) |
