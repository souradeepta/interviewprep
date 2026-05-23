# Uber, Stripe, & Airbnb Interview Prep

Specialized guides for ride-sharing, payments, and travel platforms.

---

## 🚗 Uber Interview Prep

### Focus Areas

**Real-time Systems (30%)**
- Uber at scale: 100M+ users, millions of concurrent drivers
- Real-time location tracking, matching
- Eventual consistency for scale

**Geospatial Algorithms (25%)**
- KD-trees for nearest neighbor search
- Geographic indexing
- Haversine distance calculations
- Regional partitioning (quadtrees, geohashing)

**Databases (20%)**
- Time-series data (trip history)
- Sharding strategies (by location, user)
- Caching (Redis for real-time data)

**Coding (25%)**
- Graph algorithms (shortest path)
- Heap (priority queues for matching)
- GeoHash implementation

### System Design: Ride Matching

```
Requirements:
- Match drivers to riders in <30 seconds
- Real-time location tracking
- Fair matching (no driver gaming)

Approach:
- Geohash to partition city
- Find drivers in nearby geohash cells
- ML ranking (ETA, rating, distance)
- Real-time updates via WebSocket

Challenges:
- Thundering herd (all requests at same time)
- Cold start (new driver, no history)
- Surge pricing fairness
```

---

## 💳 Stripe Interview Prep

### Focus Areas

**Distributed Transactions (30%)**
- Payment processing is critical
- ACID guarantees essential
- Two-phase commit, saga pattern

**Financial Data (25%)**
- Reconciliation (what payment processing completed)
- Audit logs (regulatory)
- Sharding by merchant ID

**Security (20%)**
- PCI compliance
- Tokenization vs. storing card numbers
- Rate limiting (prevent fraud)

**Coding (25%)**
- Concurrency (transactions, locks)
- Idempotency (same request twice = same result)
- Retry logic

### System Design: Payment Processing

```
Requirements:
- Process 1M payments/minute reliably
- <5% failure rate
- PCI compliance

Approach:
- Idempotent processing (idempotency key)
- Saga pattern for distributed transactions
- Event sourcing for audit trail
- Separate read/write paths (CQRS)
- Retry queue for failed payments

Challenges:
- Duplicate requests
- Race conditions
- Third-party failures (banks, payment networks)
- Fraud detection
```

---

## 🏨 Airbnb Interview Prep

### Focus Areas

**Search & Ranking (30%)**
- Billions of listing combinations
- Personalized search ranking
- Fast, relevant results

**Geospatial (20%)**
- Search by location, radius
- Clustering listings by area
- Efficient indexing

**Databases (20%)**
- Listings (mostly read, slowly updated)
- Bookings (critical path, ACID)
- Reviews (high volume, eventually consistent)

**Coding (30%)**
- Arrays, graphs (connection finding)
- Heaps (top-K problems)

### System Design: Booking System

```
Requirements:
- 1M bookings/day
- Real-time availability
- No double-booking

Approach:
- Calendar service (per-listing availability)
- Pessimistic locking (reserve before paying)
- Payment integration
- Notification system (host, guest)

Trade-offs:
- Strong consistency (no double-booking) vs. availability
- Real-time sync vs. eventual consistency
```

---

## 📊 Comparison

| Company | Emphasis | Key Algorithm |
|---------|----------|---------------|
| **Uber** | Real-time, geospatial | KD-tree, geohashing |
| **Stripe** | Distributed transactions | Saga pattern, idempotency |
| **Airbnb** | Search & ranking | Geohashing, ranking models |

---

**Last updated:** 2026-05-22
