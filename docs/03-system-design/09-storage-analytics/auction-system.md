# Auction System

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

Online auction platforms (eBay, Sotheby's, real-time advertising) must handle intense bid bursts at auction close — 1,000+ bids/sec on a single item in the final seconds — while ensuring correctness: the highest valid bid wins, no two bidders believe they won, and the winning bid is processed for payment atomically. The system must also prevent bid sniping (last-second bids that other bidders have no time to respond to) and detect fraudulent bid patterns.

## Functional Requirements

- Sellers create auctions with start price, reserve price, and closing time
- Buyers submit bids; each bid must be higher than the current highest bid by a minimum increment
- Bidders can see current highest bid in near-real-time
- System determines the winner when the auction closes
- Winner is charged the winning bid amount; auction result is final and auditable
- Support sealed-bid and open-bid auction formats

## Non-Functional Requirements

- **Scale:** 10M active auctions; 1,000 bids/sec average; 50,000 bids/sec peak (close-time storm)
- **Latency:** Bid submission P99 < 200ms; current price read P99 < 20ms
- **Availability:** 99.99% — auction close must succeed exactly once
- **Consistency:** Strong for bid ordering and winner determination; eventual for live price display

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Active auctions: 10M
Bids/sec average: 1,000
Bids/sec at close (storm): 50,000 (50x spike for top auctions)
Auction close rate: assume avg duration 7 days → 10M / (7 * 86400) = ~16 auctions closing/sec
Peak close storm: top 100 auctions closing simultaneously → 500 bids/sec per auction

Bid storage:
  - Each bid: 50 bytes (auction_id + user_id + amount + timestamp + status)
  - 1,000/sec * 86400 = 86.4M bids/day → 4.3 GB/day → 1.6 TB/year (moderate)

Current price reads:
  - Each auction page: reads current_price every 3 seconds while open
  - 10M auctions * avg 10 active viewers = 100M viewers * 1 read/3s = 33M reads/sec
  - Must serve from Redis, not DB (DB cannot sustain 33M reads/sec)

Winner determination:
  - Happens once per auction: MAX(amount) WHERE auction_id = X AND status = 'VALID'
  - 16 closings/sec → 16 queries/sec → trivial for DB
```

### Architecture Diagram

```
Bid Submission Flow:
Client
  |
  | POST /bids  (bid_amount, auction_id, user_id)
  v
+------------------+
| Bid Validation   |  <-- Check: auction open? amount > current_bid + min_increment?
| Service          |      user not banned? user balance sufficient?
+------------------+
  |
  | Validate against current highest bid
  v
+------------------+       +------------------+
| Redis            | <---> | Bid DB           |
| ZADD auction:{id}|       | (append-only)    |
| score=bid_amount |       | bids table       |
+------------------+       +------------------+
  |
  | Publish BidAccepted / BidRejected event
  v
+------------------+
| Kafka            |  --> Live Price Service (WebSocket push to browsers)
|                  |  --> Notification Service (email outbid alert)
|                  |  --> Fraud Detection Service
+------------------+

Auction Close Flow:
+------------------+
| Auction Scheduler|  <-- Triggers at closing_time
+------------------+
  |
  | ZREVRANGE auction:{id} 0 0 (highest bidder from Redis sorted set)
  v
+------------------+
| Auction Close    |  <-- Determine winner, check reserve, trigger payment
| Service          |
+------------------+
  |
  v
+------------------+
| Payment Service  |  <-- Charge winning bid amount
+------------------+

Live Price View:
Client <---- WebSocket ---- Live Price Service ---- Kafka consumer
```

### Data Model

```sql
-- Auctions: one row per auction
CREATE TABLE auctions (
    auction_id    UUID PRIMARY KEY,
    seller_id     BIGINT NOT NULL,
    title         VARCHAR(500),
    description   TEXT,
    start_price   NUMERIC(12,2) NOT NULL,
    reserve_price NUMERIC(12,2),       -- NULL = no reserve
    current_price NUMERIC(12,2),       -- Denormalized for fast read
    bid_increment NUMERIC(12,2) DEFAULT 1.00,
    status        VARCHAR(20) DEFAULT 'PENDING',  -- PENDING, ACTIVE, CLOSED, CANCELLED
    format        VARCHAR(20) DEFAULT 'OPEN',     -- OPEN, SEALED
    opens_at      TIMESTAMPTZ NOT NULL,
    closes_at     TIMESTAMPTZ NOT NULL,
    closing_extended BOOLEAN DEFAULT FALSE,       -- Anti-snipe extension
    winner_id     BIGINT,
    winning_amount NUMERIC(12,2),
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Bids: append-only (no updates, no deletes — audit trail)
CREATE TABLE bids (
    bid_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auction_id   UUID REFERENCES auctions(auction_id),
    bidder_id    BIGINT NOT NULL,
    amount       NUMERIC(12,2) NOT NULL,
    status       VARCHAR(20) DEFAULT 'PENDING',  -- PENDING, WINNING, OUTBID, INVALID, RETRACTED
    placed_at    TIMESTAMPTZ DEFAULT NOW(),
    ip_address   INET,
    device_id    VARCHAR(100),
    INDEX (auction_id, amount DESC),
    INDEX (bidder_id, placed_at DESC)
);

-- Auction results: written exactly once when auction closes
CREATE TABLE auction_results (
    auction_id       UUID PRIMARY KEY REFERENCES auctions(auction_id),
    winner_id        BIGINT,
    winning_bid_id   UUID REFERENCES bids(bid_id),
    winning_amount   NUMERIC(12,2),
    reserve_met      BOOLEAN,
    total_bids       INT,
    payment_status   VARCHAR(20) DEFAULT 'PENDING',  -- PENDING, CHARGED, FAILED, WAIVED
    closed_at        TIMESTAMPTZ DEFAULT NOW()
);
```

### API Design

```
POST /v1/auctions
  Body: { title, start_price, reserve_price?, closes_at, format: "OPEN" }
  Response: { auction_id, status: "PENDING" }

GET /v1/auctions/{auction_id}
  Response: { auction_id, title, current_price, closes_at, total_bids, time_remaining_ms }

POST /v1/auctions/{auction_id}/bids
  Body: { amount: 125.00 }
  Response: { bid_id, status: "WINNING"|"OUTBID"|"INVALID", current_price: 125.00,
              message?: "You are the highest bidder" }

GET /v1/auctions/{auction_id}/bids?cursor=<...>&limit=20
  Response: { bids: [{ bidder_id (masked), amount, placed_at }], next_cursor }

GET /v1/auctions/{auction_id}/result
  Response: { winner_id (masked), winning_amount, reserve_met, total_bids }

GET /v1/users/{user_id}/bids?status=winning&cursor=<...>
  Response: { bids: [{ auction_id, amount, status, auction_title }], next_cursor }

WebSocket: /v1/auctions/{auction_id}/live
  Server pushes: { type: "NEW_BID", current_price: 130.00, bids_count: 47 }
  Server pushes: { type: "AUCTION_EXTENDED", new_close_time: "..." }
  Server pushes: { type: "AUCTION_CLOSED", winner_masked_id: "u***123", amount: 250.00 }
```

### Basic Scaling

- Store current highest bid in Redis sorted set `auction:{id}` with score = bid amount; the winner is always `ZREVRANGE ... 0 0`
- Use optimistic locking for bid submission: read current highest, validate, write; retry on conflict
- Separate "current price" reads (Redis, <1ms) from bid submission writes (DB + Redis)
- Auction close is scheduled via a job queue (SQS DelayedMessage or Celery beat) — fire exactly once at closing_time

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Bid submission at peak (50K bids/sec):
  - Redis ZADD: 50K/sec → 50 nodes each handling 1K/sec (trivial per-node)
  - DB writes: 50K rows/sec to bids table (Cassandra or sharded PostgreSQL)
  - Kafka events: 50K * 2 (BidAccepted + price update) = 100K events/sec
    10 Kafka partitions → 10K events/sec/partition (within limits)

Redis cluster for auction state:
  - 10M active auctions * 1 sorted set (avg 100 bids/set) = 10M * 100 * 50B = 50 GB
  - 5-node Redis cluster with RF=2: 10 GB per node → r6g.xlarge (32 GB RAM each)
  - Cost: 5 * $0.335/hr = $1.68/hr = $1,209/month

Bid DB (Cassandra, 5 nodes, RF=3):
  - 1.6 TB/year * RF=3 = 4.8 TB; 5 nodes * 1 TB = 5 TB capacity
  - Write throughput: 50K/sec → 10K/sec per node (within Cassandra's 30K/sec per node)
  - Partition key: auction_id → each auction's bids co-located on same token ring range
  - Cost: 5 * i3.xlarge $0.312/hr = $1.56/hr = $1,123/month

WebSocket servers for live price:
  - 10M auctions * avg 10 concurrent viewers = 100M WebSocket connections
  - WebSocket connections per server: 100K per server
  - Servers needed: 100M / 100K = 1,000 WebSocket servers
  - Each server: c5.large $0.085/hr → 1,000 * $0.085 = $85/hr = $61,200/month
  - Reduce by: fan-out via topic subscriptions → Kafka consumer → push server
    Users watching same auction share 1 Kafka consumer; price update fan-out per server
```

### Failure Modes

```
Failure: Bid storm at close (1,000 bids/sec on single auction in last 60 seconds)
  Impact: Redis becomes hot for that auction's sorted set; DB write contention
  Mitigation:
    - Redis sorted set handles 100K ZADD/sec per shard — 1,000/sec is well within limits
    - DB write buffering: batch-insert bids every 100ms rather than one row at a time
      At 1,000/sec, batch of 100 bids → 10 batch inserts/sec → 10x write reduction
    - Rate limit: max 1 bid per user per 1 second per auction (prevents bot flooding)
    - If a user submits bid faster than 1/sec: accept into pending queue, process sequentially

Failure: Duplicate auction close (scheduler fires twice, or fails and retries)
  Impact: Two auction_results rows; winner charged twice
  Mitigation:
    - INSERT INTO auction_results ... ON CONFLICT (auction_id) DO NOTHING
      Only first close wins; second close is silently idempotent
    - Atomic: close transitions auction status from ACTIVE → CLOSED using:
      UPDATE auctions SET status='CLOSED' WHERE auction_id=X AND status='ACTIVE'
      Rows affected = 1 → proceed. Rows affected = 0 → already closed, stop.
    - Close service acquires distributed lock (Redis SETNX) for auction_id before processing

Failure: Anti-snipe window extension race
  Impact: Extension happens after a bid at T-29s; close already committed at T-30s
  Mitigation:
    - Anti-snipe logic inside the bid submission path (not a separate service)
    - On bid submission: if closes_at - now < 5 minutes AND bid is valid:
        UPDATE auctions SET closes_at = closes_at + INTERVAL '5 minutes',
          closing_extended = TRUE
        WHERE auction_id = X AND status = 'ACTIVE'
    - This is inside the bid transaction; either both the bid and the extension commit or neither does
    - Audit log: all extensions recorded with bid_id that triggered them

Failure: Winner cannot pay (insufficient funds, declined card)
  Impact: Highest bidder is the winner but payment fails
  Mitigation:
    - Payment pre-authorization at bid submission for auctions above $100:
      Authorize but not capture the bid amount; update authorization if outbid
    - On auction close: capture the pre-auth for the winner
    - If payment fails: attempt 3 retries over 24 hours; notify winner
    - After 24 hours: cancel the winner's result; offer to next-highest bidder
    - Re-run payment flow for next bidder; mark original winner as non-paying bidder (ban if repeated)
```

### Consistency Boundaries

```
Bid ordering (must be strongly consistent):
  - The highest bid must win; ties broken by placement timestamp
  - Use Redis ZADD NX (only add if not exists) for initial bid, ZADD XX GT (only update if
    new score is greater) for outbid scenarios
  - DB is the source of truth; Redis is a fast cache of the current state
  - On Redis failure: fall back to DB for bid validation (slower but correct)

Sealed bid vs open bid:
  - Open bid: current highest bid visible to all bidders in real-time
  - Sealed bid: bidders see only their own bids; highest is revealed at close
  - Sealed bid implementation: omit current_price from auction data until status=CLOSED
    Redis sorted set is NOT readable by bidders; only the close service reads it

Reserve price enforcement:
  - Reserve is private; bidders don't see it
  - On close: if winning_amount < reserve_price → auction fails (no winner)
  - "Reserve not met" returned in auction_results.reserve_met = FALSE
  - Some platforms reveal "reserve not met" signal to bidders (encourages higher bids)

Current price staleness for live viewers:
  - Acceptable: 1-2 second delay between bid submission and price update on viewers' screens
  - WebSocket push latency: bid → Kafka → WebSocket server → client = ~500ms P95
  - If WebSocket connection drops: client polls GET /auctions/{id} every 5 seconds
  - Polling provides eventual consistency fallback; WebSocket provides near-real-time experience
```

### Cost Model

```
Redis cluster (auction state): $1,209/month
Cassandra (bids): $1,123/month
Auction DB (PostgreSQL, auctions + results): $500/month
WebSocket servers (1,000 c5.large): $61,200/month
Kafka: $2,000/month
Fraud detection (ML inference on bids): $3,000/month
Payment processor (Stripe 2.9% + $0.30 per winning transaction):
  - At 10M auctions/month * $100 avg winning bid: $10B GMV * 2.9% = $290M/month (payment processor revenue!)
  - Platform fee: 10% of GMV = $100M/month

Total infra cost: ~$70K/month
Revenue: ~$100M/month (eBay-style marketplace)
Infrastructure as % of revenue: 0.07%
```

---

## Trade-off Comparison

| Approach                         | Pros                                              | Cons                                              | Best For                          |
|----------------------------------|---------------------------------------------------|---------------------------------------------------|-----------------------------------|
| Open auction (English)           | Transparent; drives highest prices               | Susceptible to sniping; bid storms                | eBay-style consumer auctions      |
| Sealed-bid first price           | No sniping; simple close logic                   | Bidders must guess competition; may underbid      | Government contracts, ad auctions |
| Sealed-bid second price (Vickrey)| Incentive-compatible; truthful bidding dominant  | Hard to explain to users                          | Ad auction systems (Google Ads)  |
| Dutch auction (descending price) | Fast close; no bid storms                        | Seller may undervalue; complex UX                 | Fresh produce, perishable goods   |
| Reserve price                    | Protects seller from undervaluing                | May leave auctions unsold; reduces participation  | High-value items (art, real estate)|
| Anti-snipe window extension      | Fairer; all bidders can respond to late bids     | Extends auction unpredictably; user frustration   | Consumer auctions (eBay does this)|

## Follow-up Questions (escalating difficulty, 7 minimum)

1. **(L3)** What is bid sniping and how does an auction extension prevent it?
   → Bid sniping is placing a winning bid in the last seconds of an auction, giving competitors no time to respond. Anti-snipe extension: if a valid bid is placed within 5 minutes of closing, the auction closing time is automatically extended by 5 minutes. This ensures every bid triggers a fresh response window. eBay uses this technique. The extension continues each time a new bid arrives within the extension window; the auction closes only after 5 minutes of inactivity.

2. **(L3)** Why must the bids table be append-only (no updates, no deletes)?
   → The bids table is a financial audit trail. If a bid could be updated or deleted, a malicious operator could remove evidence of a bid that should have won, or alter the amount. Regulatory compliance (financial records, dispute resolution) requires an immutable log. Status changes (WINNING → OUTBID) are expressed by marking the bid's status field, not by deleting the old bid. The winning determination reads MAX(amount) from the immutable log.

3. **(L4)** How do you prevent the same auction from being closed twice?
   → Use an atomic compare-and-swap: `UPDATE auctions SET status='CLOSED' WHERE auction_id=X AND status='ACTIVE'`. If the auction is already CLOSED, this UPDATE affects 0 rows, and the close service stops processing. Additionally, `INSERT INTO auction_results ON CONFLICT (auction_id) DO NOTHING` ensures the result is written only once. Use a distributed lock (Redis SETNX with TTL) before starting the close process to prevent concurrent close attempts.

4. **(L4)** How do you handle 1,000 bids/second on a single auction in the final minute?
   → Redis sorted set handles 100K ZADD/sec per shard — 1,000/sec per auction is well within limits. DB write batching: buffer 100ms of bids and insert as a batch (10 inserts/sec vs 1,000 inserts/sec). Rate limit bidders: max 1 bid per user per second per auction (queue excess bids, process sequentially). If the bid rate hits Redis limits (unlikely at 1,000/sec): shard the sorted set across N keys and aggregate the maximum at close time. Critical: never block bid acceptance on DB write latency — accept to Redis first, flush to DB asynchronously.

5. **(L5)** In a sealed-bid auction, how do you ensure bid confidentiality and reveal results atomically at close?
   → Bids are stored in the DB with `status='SUBMITTED'` and `amount` encrypted with the auction's public key (the corresponding private key is held by the close service or in a hardware security module). During the auction: the sorted set in Redis is NOT populated (sealed bids). At close time: the close service decrypts all bid amounts, determines the winner, writes auction_results in a single transaction, then publishes the result. No intermediate read of the sorted set is possible because it doesn't exist until close. The DB row for each bid has `amount_encrypted` (visible to all) and `amount_decrypted` (NULL until close, written by the close service only).

6. **(L5)** How do you detect fraudulent bidding patterns (shill bidding, bid manipulation)?
   → Shill bidding: seller uses alt accounts to drive up the price. Detection signals: bidder account age < 7 days; bidder's bid history shows 90% of bids are on this seller's auctions; bidder never wins (only bids up competitors). Implement: for each bid, compute a fraud score using: (1) device fingerprint similarity to seller (same browser fingerprint = strong signal), (2) IP proximity to seller (same subnet), (3) bid pattern (bidding exactly 1 increment above competition), (4) win rate (<1% win rate = shill candidate). Feed these signals to a real-time ML model (Kafka → Flink → fraud score → bid status). Bids above fraud threshold: held in PENDING status for 60-second manual review window; if not cleared, marked INVALID.

7. **(L5+)** Design a real-time bidding (RTB) system for ad auctions that must complete in <10ms.
   → RTB differs from consumer auctions: it is sealed-bid, Vickrey (second-price), runs in 10ms total (impression request → highest bidder determined → ad served), and processes millions of auctions per second. Architecture: publisher sends bid request to ad exchange; exchange broadcasts to 100+ DSPs (demand-side platforms) in parallel via UDP multicast (not TCP — no handshake overhead); DSPs respond with sealed bid within 8ms; exchange selects highest bid, charges second price, returns winning creative in remaining 2ms. No Redis sorted set needed — the exchange collects responses in an in-memory priority queue, waits for 8ms window, selects max. No persistent bid storage during RTB — only the winner is logged. Scale: Google processes 10 million RTB auctions per second on dedicated FPGA-accelerated infrastructure.

## Anti-patterns / Things NOT to Say

- **"Store the current highest bid by running SELECT MAX(amount) FROM bids on every page load"** — At 33M page loads/sec per auction, this query would destroy any relational database. The current highest bid must be cached in Redis (sorted set), updated atomically on every bid submission, and served from cache on every read. Only at auction close does the DB participate in winner determination.
- **"Allow bid retraction at any time to be user-friendly"** — Bid retractions are a fraud vector: a shill bidder drives up the price, then retracts at the last second leaving a lower bid as the winner. Real auction platforms allow retraction only under extreme circumstances (bid placed by mistake, significant misdescription) and only before a competing bid arrives. Implement retraction with a strict policy: only allowed within 60 seconds of bid placement, only if no subsequent bid has been placed, and logged permanently.
- **"Use a database-level sequence for bid ordering to determine ties"** — Database sequences are node-local and may not reflect true temporal ordering in distributed systems. Two bids placed at T=14:23:45.100 and T=14:23:45.101 from different datacenters may receive sequence numbers in unpredictable order. Use placement_timestamp with microsecond precision; in case of true ties (same millisecond), use the lower bid ID as tiebreaker — document this policy and apply it consistently.
- **"Auction close time is a precise point — use a scheduler that fires at exactly closing_time"** — Schedulers fire with jitter (1-500ms). At the exact closing_time, there may still be bids in-flight (submitted before closing_time, still being processed). The close service must wait for the bid processing queue to drain before determining the winner. Implement: close_time_plus_grace = closing_time + 2 seconds; start winner determination at closing_time_plus_grace. Bids submitted after closing_time are rejected at the validation layer.

## Python Implementation (sketch)

```python
import uuid
import time
from decimal import Decimal
from dataclasses import dataclass
from typing import Optional
import redis

r = redis.Redis(host="redis", decode_responses=True)

@dataclass
class BidResult:
    bid_id: str
    status: str        # WINNING, OUTBID, INVALID, RATE_LIMITED
    current_price: Decimal
    message: str

ANTI_SNIPE_WINDOW_SEC = 300   # 5 minutes
ANTI_SNIPE_EXTENSION_SEC = 300

class AuctionBidService:
    """Handles bid submission with Redis sorted set + DB persistence."""

    def __init__(self, db, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client

    def place_bid(self, auction_id: str, bidder_id: int, amount: Decimal) -> BidResult:
        """Place a bid. Returns result immediately after Redis update."""
        # Step 1: Validate auction is still open (from Redis cache)
        auction = self._get_auction_cached(auction_id)
        if auction["status"] != "ACTIVE":
            return BidResult("", "INVALID", Decimal(0), "Auction is not active")

        now = time.time()
        if now > auction["closes_at"]:
            return BidResult("", "INVALID", Decimal(0), "Auction has closed")

        # Step 2: Validate bid amount > current_highest + min_increment
        current_highest = self._get_current_price(auction_id)
        min_increment = Decimal(str(auction["bid_increment"]))
        if amount < current_highest + min_increment:
            return BidResult(
                "", "INVALID", current_highest,
                f"Bid must be at least {current_highest + min_increment}"
            )

        # Step 3: Rate limit check (max 1 bid/user/auction/second)
        rate_key = f"bidrate:{auction_id}:{bidder_id}"
        if not self.redis.set(rate_key, 1, nx=True, ex=1):
            return BidResult("", "RATE_LIMITED", current_highest, "Too many bids — please wait 1 second")

        # Step 4: Update Redis sorted set atomically
        bid_id = str(uuid.uuid4())
        score = float(amount)
        pipeline = self.redis.pipeline()
        pipeline.zadd(f"auction:{auction_id}", {bid_id: score})
        # Anti-snipe: extend close time if bid in final window
        seconds_remaining = auction["closes_at"] - now
        if seconds_remaining < ANTI_SNIPE_WINDOW_SEC:
            new_close = auction["closes_at"] + ANTI_SNIPE_EXTENSION_SEC
            pipeline.hset(f"auction:meta:{auction_id}", "closes_at", new_close)
        pipeline.execute()

        # Step 5: Async write to DB (don't block bid response on DB latency)
        self._async_write_bid(bid_id, auction_id, bidder_id, amount)

        return BidResult(bid_id, "WINNING", amount, "You are the highest bidder")

    def close_auction(self, auction_id: str) -> dict:
        """Determine winner. Idempotent — safe to call multiple times."""
        lock_key = f"close_lock:{auction_id}"
        if not self.redis.set(lock_key, 1, nx=True, ex=60):
            return {"status": "already_closing"}

        try:
            # Atomic: transition ACTIVE → CLOSED
            rows_affected = self.db.execute(
                "UPDATE auctions SET status='CLOSED' WHERE auction_id=%s AND status='ACTIVE'",
                auction_id
            )
            if rows_affected == 0:
                return {"status": "already_closed"}

            # Determine winner from Redis sorted set
            top = self.redis.zrevrange(f"auction:{auction_id}", 0, 0, withscores=True)
            if not top:
                return {"status": "no_bids"}

            winning_bid_id, winning_amount = top[0]
            auction = self._get_auction_cached(auction_id)
            reserve = Decimal(str(auction.get("reserve_price") or 0))
            reserve_met = Decimal(str(winning_amount)) >= reserve

            result = {
                "auction_id": auction_id,
                "winning_bid_id": winning_bid_id,
                "winning_amount": winning_amount,
                "reserve_met": reserve_met
            }
            # Idempotent insert
            self.db.execute(
                "INSERT INTO auction_results ... ON CONFLICT (auction_id) DO NOTHING",
                result
            )
            return result
        finally:
            self.redis.delete(lock_key)

    def _get_current_price(self, auction_id: str) -> Decimal:
        top = self.redis.zrevrange(f"auction:{auction_id}", 0, 0, withscores=True)
        if top:
            return Decimal(str(top[0][1]))
        return Decimal("0.00")

    def _get_auction_cached(self, auction_id: str) -> dict:
        return {}  # Stub: real impl reads from Redis hash or DB

    def _async_write_bid(self, bid_id, auction_id, bidder_id, amount):
        pass  # Stub: Kafka producer sends to bids.write topic → DB consumer
```
