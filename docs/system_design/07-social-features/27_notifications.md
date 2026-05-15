# Notifications System

## Problem Statement
Design a multi-channel notification system delivering alerts via email, SMS, push, and in-app.

**Operations:**
- `sendNotification(user_id, message, channels)` — Send notification
- `getNotifications(user_id)` — Get user notifications
- `markAsRead(notification_id)` — Mark read
- `setPreferences(user_id, channels, frequency)` — User preferences

## Design

### Multi-Channel Delivery

```
Email: SMTP service, batch processing
SMS: Third-party API (Twilio)
Push: FCM/APNs, device registration
In-app: Database, real-time via WebSocket
```

### Notification Queue

```
User preferences: Which channels enabled
Rate limiting: Max notifications per hour
Deduplication: Same message not sent twice
Retries: Failed channels retry
```

### Delivery Guarantee

```
At-least-once: Resend if no ACK
Tracking: Status per channel
Dead letter: Failed after retries
```


## Scenario

Notifications System is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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

```
┌──────────────────────────────────────┐
│   Notification Service               │
│  ┌──────────────────────────────────┐  │
│  │ Events: like, follow, mention    │  │
│  │ Channels: push, email, SMS       │  │
│  │ Delivery: queue-based (Kafka)    │  │
│  │ Preferences: user opt-in/out     │  │
│  └──────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## Common Questions & Answers

**Q: Notification delivery reliability?** A: Persistent queue, retry exponential backoff, dead letter queue.

**Q: Thundering herd (all wake at once)?** A: Stagger notifications across time window, use jitter.

**Q: Preference system?** A: Per notification type opt-in. Don't spam = healthy user experience.

**Q: Real-time vs digest?** A: Real-time for critical (comment reply), digest for daily summary.

## Back-of-Envelope Calculations

1B users, 10 notifications/day avg. Throughput: 100K notif/sec. Delivery: 1% hard bounce rate. Cost: $0.01 per push, $10M/month at scale.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Real-time push | Immediate, engaging | Battery drain, spam |
| Digest email | Non-intrusive | Lower engagement |
| Hybrid | Balances both | More complex |

## Follow-up Interview Questions

1. Handle notification fatigue (user unsubscribes)? 2. Personalization (frequency, time)? 3. Multi-device synchronization? 4. Delivery channel failure (fall back)? 5. Cost optimization?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

### Architecture Diagram

```mermaid
graph TB
    Event["Event"]
    NotificationService["Notification Service"]
    Queue["Task Queue"]
    Workers["Workers"]
    Channels["Email/SMS/Push"]

    Event -->|Create| NotificationService
    NotificationService -->|Enqueue| Queue
    Queue -->|Distribute| Workers
    Workers -->|Send| Channels
```

### Flow Diagram

```mermaid
sequenceDiagram
    participant E as Event
    participant NS as Service
    participant Q as Queue
    participant W as Worker
    participant C as Channel

    E->>NS: Notification Event
    NS->>Q: Enqueue
    Q-->>W: Task
    W->>C: Send
    C-->>User: Delivered
```

## Complexity

| Operation | Time |
|-----------|------|
| Send | O(1) queue |
| Deliver | O(1) per channel |
| Get notifications | O(k) |

## Python Implementation

```python
from dataclasses import dataclass
from typing import List, Dict, Callable
from enum import Enum
from datetime import datetime
import threading

class NotifChannel(Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"

@dataclass
class Notification:
    notif_id: str
    user_id: str
    title: str
    body: str
    channel: NotifChannel
    timestamp: datetime = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()

class NotificationService:
    def __init__(self):
        self._handlers: Dict[NotifChannel, Callable] = {}
        self._unread: Dict[str, List[Notification]] = {}
        self._counter = 0

    def register_handler(self, channel: NotifChannel, handler: Callable):
        self._handlers[channel] = handler

    def send(self, user_id: str, title: str, body: str, channel: NotifChannel):
        self._counter += 1
        notif = Notification(f"N-{self._counter}", user_id, title, body, channel)
        self._unread.setdefault(user_id, []).append(notif)
        handler = self._handlers.get(channel)
        if handler:
            threading.Thread(target=handler, args=(notif,), daemon=True).start()

    def get_unread(self, user_id: str) -> List[Notification]:
        return self._unread.get(user_id, [])

    def mark_read(self, user_id: str):
        self._unread[user_id] = []

# Usage
svc = NotificationService()
svc.register_handler(NotifChannel.IN_APP, lambda n: print(f"[IN-APP] {n.title}"))
svc.send("user1", "New follower", "Alice followed you", NotifChannel.IN_APP)
print(len(svc.get_unread("user1")))  # 1
```

## Java Implementation

```java
import java.util.*;
import java.util.concurrent.*;
import java.util.function.Consumer;

public class NotificationService {
    enum Channel { PUSH, EMAIL, SMS, IN_APP }
    record Notification(String id, String userId, String title, String body, Channel channel) {}

    private Map<Channel, Consumer<Notification>> handlers = new EnumMap<>(Channel.class);
    private Map<String, List<Notification>> unread = new HashMap<>();
    private int counter = 0;
    private ExecutorService executor = Executors.newCachedThreadPool();

    public void registerHandler(Channel ch, Consumer<Notification> handler) {
        handlers.put(ch, handler);
    }

    public void send(String userId, String title, String body, Channel ch) {
        Notification n = new Notification("N-" + (++counter), userId, title, body, ch);
        unread.computeIfAbsent(userId, k -> new ArrayList<>()).add(n);
        Consumer<Notification> h = handlers.get(ch);
        if (h != null) executor.submit(() -> h.accept(n));
    }

    public List<Notification> getUnread(String userId) {
        return unread.getOrDefault(userId, List.of());
    }
}
```
