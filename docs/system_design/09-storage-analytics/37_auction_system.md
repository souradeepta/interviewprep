# Auction System

## Problem Statement
Design an auction platform with bidding, time management, and winner determination.

**Operations:**
- `createAuction(item, start_price, end_time)` — Create
- `placeBid(user_id, auction_id, amount)` — Bid
- `getHighestBid(auction_id)` — Current highest
- `finalizeAuction(auction_id)` — Determine winner


## Code Explanation (Detailed)

### Implementation Approach
The code demonstrates core patterns and trade-offs.

### Key Operations
Each operation shows algorithm and performance characteristics.

### Concurrency and Atomicity
Locking strategies, race condition prevention.

### Edge Cases
Boundary conditions and error handling.

### Performance Optimization
Techniques for reducing latency and throughput.

## Design

### Bid Validation

```
Amount > current highest
User not seller
Auction still active
User has sufficient funds
```

### Winner Selection

```
Highest bidder wins
Sealed-bid: Don't reveal other bids
Open-bid: Public bidding
Auto-bidding: Proxy bidder
```

### Settlement

```
Charge winner
Refund other bidders
Payment processing
Shipment generation
```

### Scalability

```
Auction sharding: By auction_id
Bid queue: Handle spikes
Real-time updates: WebSocket bids
```


## Scenario

Auction System is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

## Users

- **Backend Engineers**: Responsible for implementing and maintaining this system component in production environments. They need to understand the architecture, trade-offs, failure modes, and operational considerations.
- **DevOps/SRE Teams**: Monitor system health, manage scaling policies, handle incidents, and ensure reliability SLAs are met. They need insights into performance characteristics, bottlenecks, and failure recovery mechanisms.
- **Data Engineers**: Design data pipelines and analytics around this system, requiring deep understanding of data flow, consistency guarantees, and throughput characteristics.
- **System Architects**: Make high-level architectural decisions that impact company infrastructure, requiring comprehensive understanding of capabilities, limitations, and scalability boundaries.
- **Security Teams**: Understand security implications, potential vulnerabilities, and compliance requirements for this component.

## PRD

### Functional Requirements
- Core operations work correctly
- Explicit error handling
- Consistency guarantees defined
- Monitoring and observability

### Non-Functional Requirements
- Performance targets met
- Availability SLA achieved
- Scalability headroom
- Cost efficient

### Success Metrics
- Benchmarks met
- Uptime targets met
- Resource budgets
- No data loss


## Flow

The typical operational flow for this system involves these key phases:

1. **Request Arrival**: Client/upstream system sends request with required parameters and context
2. **Validation & Routing**: System validates request format, authentication, and routes to correct handler/shard/instance
3. **Core Processing**: Execute the main algorithm, database query, or business logic on the data/state
4. **State Management**: Update internal state (caches, indexes, counters, logs) with proper atomicity and locking
5. **Response Generation**: Format results and return to requester with relevant metadata (timing, version info)
6. **Observability**: Record metrics (latency, throughput, errors), logs (for debugging), and traces (for performance analysis)

This flow repeats thousands or millions of times per second in production. Each operation's efficiency compounds across the entire system, making careful optimization essential. Bottlenecks at any phase can cascade to impact overall system performance.

## Architecture Diagram

```
┌──────────────────────────────────────┐
│   Auction/Bidding System             │
│  ┌──────────────────────────────────┐  │
│  │ Auction State Machine            │  │
│  │ - Open, Active, Closed, Settled  │  │
│  │ Current Bid Tracking             │  │
│  │ - Redis sorted set (price)       │  │
│  │ Bid Validation                   │  │
│  │ - > current, min increment       │  │
│  │ Winner Determination             │  │
│  │ - Highest bid at close time      │  │
│  └──────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## Back-of-Envelope Calculations

eBay: 10M concurrent auctions, 100K bids/sec. Bid validation O(1). State transition O(1). Close processing: batch hourly, 100K winners.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Simple highest-bid | Easy, fast | No auto-bidding |
| Proxy bid auction | Fair, encourages bidding | More state |
| Dutch auction | Price decreases | Different mechanics |

## Follow-up Interview Questions

1. Shill bidding detection (fake bids)? 2. Reserve price (hidden minimum)? 3. Multiple winners (buy-it-now)? 4. Dispute resolution? 5. International (currency conversion)?

## UML Diagram

```
┌────────────────────────┐
│      Auction           │
├────────────────────────┤
│- id: int               │
│- status: AuctionStatus │
│- highestBid: double    │
│- highestBidder: int    │
│- endTime: long         │
├────────────────────────┤
│+ placeBid(bid)         │
│+ finalize(): Winner     │
└────────────────────────┘
         △
         │ contains
         │
┌────────────────────────┐
│        Bid             │
├────────────────────────┤
│- userId: int           │
│- amount: double        │
│- timestamp: long       │
└────────────────────────┘
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant API
    participant AuctionSvc as Auction Service
    participant BidSvc as Bid Service
    participant DB
    participant Payment

    User->>API: Create Auction
    API->>AuctionSvc: Create
    AuctionSvc->>DB: Store

    User->>API: Place Bid
    API->>BidSvc: Validate Bid
    BidSvc->>DB: Check Current Highest
    BidSvc->>DB: Store Bid

    Note over User,Payment: At Auction End
    AuctionSvc->>DB: Finalize
    AuctionSvc->>Payment: Process Payment
    Payment-->>User: Confirmation
```

## Implementation

### Python Implementation

```python
from dataclasses import dataclass
from enum import Enum
import time
from typing import Optional

class AuctionStatus(Enum):
    OPEN = "open"
    ACTIVE = "active"
    CLOSED = "closed"
    SETTLED = "settled"

@dataclass
class Bid:
    user_id: int
    amount: float
    timestamp: float

class AuctionSystem:
    def __init__(self):
        self.auctions = {}
        self.bids = {}

    def create_auction(self, auction_id: int, item: str, start_price: float, duration: int):
        self.auctions[auction_id] = {
            'item': item,
            'start_price': start_price,
            'end_time': time.time() + duration,
            'status': AuctionStatus.OPEN,
            'highest_bid': start_price,
            'highest_bidder': None
        }
        self.bids[auction_id] = []

    def place_bid(self, auction_id: int, user_id: int, amount: float) -> bool:
        if auction_id not in self.auctions:
            return False
        auction = self.auctions[auction_id]
        if time.time() > auction['end_time']:
            return False
        if amount <= auction['highest_bid']:
            return False
        auction['highest_bid'] = amount
        auction['highest_bidder'] = user_id
        self.bids[auction_id].append(Bid(user_id, amount, time.time()))
        return True

    def finalize_auction(self, auction_id: int) -> Optional[dict]:
        if auction_id not in self.auctions:
            return None
        auction = self.auctions[auction_id]
        if auction['highest_bidder']:
            auction['status'] = AuctionStatus.SETTLED
            return {
                'winner': auction['highest_bidder'],
                'amount': auction['highest_bid']
            }
        return None
```

### Java Implementation

```java
import java.util.*;

class AuctionSystem {
    enum AuctionStatus { OPEN, ACTIVE, CLOSED, SETTLED }

    static class Bid {
        int userId;
        double amount;
        long timestamp;

        Bid(int userId, double amount, long timestamp) {
            this.userId = userId;
            this.amount = amount;
            this.timestamp = timestamp;
        }
    }

    static class Auction {
        String item;
        double highestBid;
        int highestBidder;
        long endTime;
        AuctionStatus status;
        List<Bid> bids = new ArrayList<>();
    }

    private Map<Integer, Auction> auctions = new HashMap<>();

    public void createAuction(int id, String item, double startPrice, long duration) {
        Auction a = new Auction();
        a.item = item;
        a.highestBid = startPrice;
        a.highestBidder = -1;
        a.endTime = System.currentTimeMillis() + duration;
        a.status = AuctionStatus.OPEN;
        auctions.put(id, a);
    }

    public boolean placeBid(int auctionId, int userId, double amount) {
        Auction a = auctions.get(auctionId);
        if (a == null || System.currentTimeMillis() > a.endTime) return false;
        if (amount <= a.highestBid) return false;

        a.highestBid = amount;
        a.highestBidder = userId;
        a.bids.add(new Bid(userId, amount, System.currentTimeMillis()));
        return true;
    }

    public Map<String, Object> finalizeAuction(int auctionId) {
        Auction a = auctions.get(auctionId);
        if (a == null) return null;

        a.status = AuctionStatus.SETTLED;
        Map<String, Object> result = new HashMap<>();
        result.put("winner", a.highestBidder);
        result.put("amount", a.highestBid);
        return result;
    }
}
```

## Example Scenario Walkthrough

**Scenario**: eBay user auction flow

1. Seller creates auction: `createAuction(123, "iPhone 15", 500, 86400)` — 24-hour duration
2. Bidder A places bid: `placeBid(123, user_A, 550)` — Success, A is highest
3. Bidder B places bid: `placeBid(123, user_B, 520)` — Failed, less than current 550
4. Bidder B places bid: `placeBid(123, user_B, 600)` — Success, B is highest
5. At auction close time: `finalizeAuction(123)` — Winner: user_B, amount: 600
6. Payment processing and shipment initiated

## Complexity

| Operation | Time |
|-----------|------|
| Place bid | O(1) |
| Get highest | O(1) |
| Finalize | O(1) |

## Common Questions & Answers

**Q: What is caching and why do we need it?**

A: Caching stores frequently accessed data in fast storage (memory) to reduce latency and load on slower backends (database). Trade space (cache) for speed (latency). Critical for systems serving millions of requests per second.

**Q: What are the main cache eviction policies?**

A: LRU (least recently used), LFU (least frequently used), FIFO (first in first out), TTL (time-based), Random, and ARC (adaptive replacement). Choose based on access patterns: LRU for temporal, LFU for frequency, TTL for time-sensitive data.

**Q: What is cache hit rate and cache miss rate?**

A: Hit rate = successful_finds / total_accesses. Miss rate = 1 - hit rate. P(hit) = hits / (hits + misses). Target 80%+ hit rates for effective caching. Too-small cache gives low hit rate (wasted resources). Too-large cache uses more memory than needed.

**Q: How do you handle cache invalidation when backend data changes?**

A: Use TTL (time-based expiration), active invalidation (notify cache on write), cache-aside pattern (client checks backend), or write-through (update both). Active invalidation is fastest but complex. TTL is simplest but has stale data window.

**Q: What is the cache-aside pattern?**

A: Application checks cache first. On miss, fetch from backend, update cache, then return. Simple to implement. Risk: race condition where multiple threads fetch same miss simultaneously (thundering herd problem).

**Q: What is write-through caching?**

A: Writes go to both cache and backend simultaneously (synchronously). Ensures consistency: read always gets latest. Cost: write latency includes backend write. Safer than write-back but slower.

**Q: What is write-back (write-behind) caching?**

A: Writes go to cache only; backend updated asynchronously later (batch or periodic). Fast writes. Risk: data loss if cache fails before flushing. Need durability guarantees (persistence, replication).

**Q: How do you choose cache size?**

A: Estimate working set (frequently accessed data volume). Add 20-30% buffer for margin. Monitor hit rate: if < 80%, increase size. If > 95%, might be oversized (waste). Use tools like cachegrind to profile.

**Q: What's the difference between client-side and server-side caching?**

A: Client cache (browser): reduces network round-trips, entirely controlled by client. Server cache (memory, Redis): shared across clients, controlled by server. Multi-level caching often best.

**Q: How do you measure cache effectiveness?**

A: Hit rate (primary metric), latency reduction (P99 latency with vs. without cache), backend load reduction, and memory cost per cache entry. Calculate ROI: cost of cache vs. benefit (reduced latency, backend load).

## Follow-up Questions & Answers

**Q: How do you prevent the thundering herd problem in caches?**

A: When popular key expires, many threads fetch from backend simultaneously causing spike. Solutions: probabilistic early expiration (refresh before TTL), request coalescing (single thread rebuilds, others wait), or bloom filters (detect non-existent keys fast).

**Q: How would you implement multi-level cache hierarchy?**

A: Use L1 (fast, small, in-process), L2 (medium, local machine), L3 (large, remote, Redis). Check L1, miss→L2, miss→L3, miss→backend. On write: update all levels. Trade space for speed across levels.

**Q: Can you implement read-through caching (automatic population)?**

A: Yes, cache loader/resolver called on miss. Transparent to application. Backend automatically uses cache layer. More complex than cache-aside but cleaner separation.

**Q: How do you handle hot keys in distributed caches?**

A: Hot key = key accessed by many threads/clients. Replicate hot keys on multiple cache nodes. Use local in-process caches for very hot keys. Monitor and detect hot keys automatically.

**Q: What's the difference between warm and cold cache startup?**

A: Cold cache: empty at start, misses until populated (slow ramp-up). Warm cache: pre-loaded from previous state (RDB/snapshot). Warm startup is critical for production (instant performance).

**Q: How would you measure cache effectiveness for business metrics?**

A: Track hit rate, P99 latency (with/without cache), backend QPS reduction, revenue impact. Calculate cache size vs. cost savings. A/B test to prove business value.

**Q: What happens when cache size is insufficient for working set?**

A: Constant evictions = high miss rate = ineffective cache. Solution: increase cache size, improve eviction policy, reduce working set, or use better hardware (faster storage).

**Q: How do you debug cache issues in production?**

A: Monitor hit rate continuously. Profile cache keys (which keys are accessed). Check for cache stampedes (sudden miss spike). Use distributed tracing to see cache path.

**Q: How would you implement a persistent cache?**

A: Combine memory cache (fast) with persistent backend (database, RocksDB, LevelDB). Write-back pattern: batch updates to persistent store. Trade latency for durability.

**Q: Can you use caching for write-heavy workloads?**

A: Write caching is risky (consistency issues). Use carefully: write-through for safety, write-back for speed. Good for batch writes (aggregate before writing). Monitor durability guarantees.

