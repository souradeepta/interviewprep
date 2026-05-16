# Distributed Systems Patterns: Building Reliable Systems at Scale

Essential patterns and techniques for building resilient, scalable distributed systems.

---

## Distributed Systems Design Patterns

### 1. Replication

**Purpose:** Increase availability and durability by copying data across multiple servers.

**Strategies:**

```
Master-Slave Replication:
Master ────────→ Slave 1
       ────────→ Slave 2
       ────────→ Slave 3

Writes: Only to master
Reads: Master or slaves (eventual consistency)
Failure: If master fails, promote slave to master
Pros: Simple, easy failover
Cons: Slaves lag behind master, single write point
```

```
Master-Master Replication:
Master 1 ←───────→ Master 2
        ←───────→ Master 3

Writes: Any master
Conflict resolution: Last-write-wins, vector clocks, or app-level
Pros: No single point of failure for writes
Cons: Complex conflict resolution
```

### 2. Sharding/Partitioning

**Purpose:** Distribute data across multiple servers to increase throughput and storage.

```
Shard by User ID:
User 1-100M → Server 1 (stores all data for these users)
User 101-200M → Server 2
User 201-300M → Server 3

Routing: Hash(user_id) % num_shards → shard location
Pros: Scales linearly with data
Cons: Rebalancing when adding servers, hotspots (some shards busier)
```

### 3. Caching

**Purpose:** Reduce load on database by serving frequently accessed data from memory.

```
Request flow with caching:
Client → LoadBalancer → API Server → Check Cache
                                    → Miss? Query DB → Update Cache
                                    → Hit? Return Cache

Cache invalidation strategies:
- TTL (Time-To-Live): Expire after N seconds
- Write-through: Update DB and cache together
- Event-based: Invalidate on specific events
```

### 4. Message Queues

**Purpose:** Decouple services, handle asynchronous workloads, ensure delivery.

```
Producer → [Queue] → Consumer

Benefits:
- Producer doesn't wait for consumer
- Load leveling (queue buffers burst traffic)
- Retry on failure (message stays in queue)
- Service decoupling (producer doesn't know consumer)

Queue types:
- FIFO (Kafka, RabbitMQ): Order preserved
- Priority queue: Process urgent first
- Dead-letter queue: Messages that failed
```

### 5. Service Discovery

**Purpose:** Automatically find healthy service instances.

```
Without service discovery:
Server1: 1.2.3.4
Server2: 1.2.3.5
(hardcoded in config - breaks when server replaces)

With service discovery:
Client queries ServiceRegistry (Consul, Eureka)
ServiceRegistry returns: [1.2.3.4, 1.2.3.5, 1.2.3.6]
LoadBalancer picks one
```

### 6. API Gateway

**Purpose:** Single entry point for clients, routing, authentication, rate limiting.

```
Client → API Gateway (auth, rate limit, route)
                    → Service 1
                    → Service 2
                    → Service 3

Gateway handles:
- Request routing to correct service
- Rate limiting (prevent abuse)
- Authentication/authorization
- Response aggregation
- Error handling
```

### 7. Circuit Breaker

**Purpose:** Fail fast when service is down, prevent cascading failures.

```
States:
CLOSED (normal):
  Request → Service (success) → CLOSED
  Request → Service (fail) → HALF_OPEN

HALF_OPEN (testing if service recovered):
  Test request → Service (success) → CLOSED
  Test request → Service (fail) → OPEN

OPEN (fast fail):
  Request → Immediately reject (don't call service)
  After timeout → HALF_OPEN

Example: After 5 consecutive failures, open circuit
         After 30 seconds, try HALF_OPEN (1 test request)
         If that succeeds, close circuit
```

### 8. Retry with Exponential Backoff

**Purpose:** Handle transient failures, don't overwhelm service.

```
Retry strategy:
Attempt 1: immediate
Attempt 2: wait 1s + jitter (±0.1s)
Attempt 3: wait 2s + jitter
Attempt 4: wait 4s + jitter
Attempt 5: wait 8s + jitter
Attempt 6: wait 16s + jitter
Give up after 6 attempts

Jitter: Add random delay to prevent thundering herd
(if 1000 clients retry at exact same time, server gets hammered)
```

### 9. Idempotency

**Purpose:** Safe to retry operations without duplicate effects.

```
Non-idempotent:
POST /accounts/{id}/transfer amount=100
If network fails and client retries:
  Transfer 1: $100 transferred
  Transfer 2: $100 transferred (duplicate!)
Account goes down $200 instead of $100

Idempotent:
POST /accounts/{id}/transfer amount=100 idempotencyKey=uuid-123
Server checks: did we process uuid-123 before?
  First call: process and cache result with uuid-123
  Retry: find cached result, return same response (don't re-process)
  Safe to retry without duplication
```

### 10. Two-Phase Commit (2PC)

**Purpose:** Coordinate transaction across multiple databases.

```
Phase 1 (Prepare):
Coordinator → Service1: "Can you commit this transaction?"
Service1: "Yes, I've locked resources and am ready"
Coordinator → Service2: "Can you commit?"
Service2: "Yes, ready"

Phase 2 (Commit):
Coordinator → Service1: "COMMIT"
Coordinator → Service2: "COMMIT"

If any service says "No" in Phase 1:
Coordinator → All: "ABORT"
All services rollback

Drawback: Blocking (services hold locks during 2 phases)
Better for: Payment systems that need strong ACID
```

### 11. Event Sourcing

**Purpose:** Store all state changes as immutable events, rebuild state by replaying.

```
Traditional approach:
Current state in DB: {user_id: 1, balance: 500, status: active}

Event sourcing approach:
Immutable event log:
- Event 1: UserCreated(id=1, balance=1000)
- Event 2: MoneyTransferred(from_user=1, to_user=2, amount=100)
- Event 3: MoneyTransferred(from_user=1, to_user=3, amount=400)

Current state = replay all events = balance 500

Benefits: Full audit trail, temporal queries (state at any point in time)
Drawback: Event log grows unbounded, more complex queries
```

### 12. SAGA Pattern (Distributed Transactions)

**Purpose:** Coordinate transactions across services without 2PC blocking.

```
Order workflow (3 services):
1. OrderService: create order
2. PaymentService: charge card
3. ShippingService: ship goods

Scenario: Payment fails

SAGA implementation:
1. OrderService creates order (state: pending)
2. PaymentService tries to charge
3. PaymentService fails
4. PaymentService publishes "PaymentFailed" event
5. OrderService listens and updates order (state: cancelled)
6. Compensating transaction: no need to ship

If shipping was already done:
- OrderService publishes "OrderCancelled"
- ShippingService listens and processes return

Benefits: No blocking locks, services remain loosely coupled
Drawback: Eventual consistency, complex failure handling
```

---

## Consensus Algorithms

### Raft

**Purpose:** Elect leader and replicate log across servers.

```
States:
- Leader: accepts writes, replicates to followers
- Follower: receives replicated logs from leader
- Candidate: running for leader election

Election process:
1. Follower timeout waiting for heartbeat from leader
2. Follower becomes candidate, requests votes
3. Servers vote for first candidate they see
4. Candidate with majority votes becomes leader
5. New leader sends heartbeats to prevent election

Log replication:
Leader appends entry → sends to followers → followers acknowledge
Leader commits when majority acknowledge

Failure handling:
If leader dies → followers detect timeout → new election → new leader
If partition: old leader can't get majority → can't write
             new leader elected on other side of partition
             Both sides merge when network heals
```

### Paxos

**Purpose:** Similar to Raft, but more complex. Rarely used in practice.

(Details omitted for brevity; Raft is preferred for interviews)

---

## Consistency Models

### Strict Consistency

```
Write x=1 on Server A
Read x on Server B
Result: 100% of reads get x=1

Impossible to achieve in distributed systems (requires infinite speed)
```

### Strong Consistency

```
Write x=1 on Server A → acknowledge to client → wait for all replicas
Read x on Server B → wait for latest from any server
Result: Client sees latest write

Cost: Slower writes (wait for replication)
Example: Google Spanner, consensus-based systems
```

### Eventual Consistency

```
Write x=1 on Server A → acknowledge immediately
Replicate to Server B (asynchronously)
Read x on Server B → might get old value briefly

After 100ms: all servers have x=1

Cost: Cheap writes (no wait for replication)
Tradeoff: Temporary inconsistency
Example: Dynamo, Cassandra, eventual consistency databases
```

### Causal Consistency

```
Strict ordering for causally related operations:
- Write x=1
- Read x → must see 1
- Update x to 2 based on reading 1
- Read x from anywhere → must see 2 (or 1, but not before 1)

Unrelated operations can be out of order
Example: Version vectors, logical clocks
```

---

## Failure Modes & Recovery

| Failure | Impact | Recovery |
|---------|--------|----------|
| **Network partition** | Services can't communicate | Wait for partition to heal, circuit breaker |
| **Server crash** | Service unavailable | Failover to replica, health check |
| **Disk failure** | Data loss | Replication, backup to another AZ |
| **Database overload** | Slow queries, timeout | Scale replicas, cache, shard |
| **Message loss** | Missing data | Replay from log, persist to durable storage |
| **Byzantine failure** | Corrupted data | Byzantine fault tolerance (3f+1 replicas for f failures) |

---

## Distributed Systems Checklist

- ✓ Identified consistency requirements (strict vs eventual)
- ✓ Replication strategy defined (master-slave, master-master)
- ✓ Sharding strategy if data too large
- ✓ Caching layer with invalidation strategy
- ✓ Message queue for async workloads
- ✓ Service discovery for dynamic environments
- ✓ API gateway for routing and auth
- ✓ Circuit breaker for fault tolerance
- ✓ Retry logic with exponential backoff
- ✓ Idempotency keys for safe retries
- ✓ Monitoring and alerting
- ✓ Disaster recovery plan (backup, failover)
- ✓ Testing for failure scenarios (chaos engineering)
- ✓ Consensus algorithm if strong consistency needed
- ✓ Data durability guarantees (persistence to disk)

