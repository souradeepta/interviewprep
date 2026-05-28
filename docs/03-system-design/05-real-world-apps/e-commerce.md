# E-Commerce Platform

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

An e-commerce platform must handle product discovery, cart management, checkout, payment
processing, and order fulfillment at massive scale. The engineering challenges are more subtle than
pure throughput: inventory must never oversell (strong consistency for stock deduction), checkout
must be atomic across multiple services (payment + inventory + order creation), and flash sales
create burst load 1,000× above baseline.

This is a rich system design topic because it requires knowing when to use strong consistency
(inventory deduction) vs eventual consistency (catalog updates), how distributed sagas prevent
partial failures during checkout, and how to handle the thundering herd of a flash sale without
overselling or crashing the database.

## Functional Requirements

- Users can browse and search the product catalog
- Users can add items to cart, modify quantities, and remove items
- Checkout: validate cart, reserve inventory, process payment, create order
- Sellers can list products, set prices, and manage inventory levels
- Order management: track order status (placed → packed → shipped → delivered)
- Support flash sales: time-bounded discounts with strictly limited stock

## Non-Functional Requirements

- **Scale:** 10M DAU; 50K orders/day normal; flash sale burst: 10K orders/sec for 60 seconds
- **Latency:** Product search P99 < 200ms; cart operations < 50ms; checkout < 2s
- **Availability:** 99.99% for browsing; 99.999% for checkout (revenue-critical)
- **Consistency:** Strong consistency for inventory; eventual consistency for catalog, reviews, recommendations

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Normal load:
  10M DAU × 30 page views/day = 300M page views/day = 3,472 req/sec average
  10M DAU × 5 searches/day = 50M searches/day = 578 searches/sec

Flash sale burst:
  10K orders/sec × 60s = 600K orders in 1 minute
  Each order: reserve inventory (1 write) + charge payment (1 external call) + create order (1 write)
  Total writes: 1.8M writes in 60s = 30K writes/sec

Inventory atomicity (overselling prevention):
  10K concurrent users trying to buy the last 100 items
  Without locking: all 10K read stock=100, all decrement, stock goes to -9,900
  With optimistic lock (compare-and-swap): each user retries if stock changed
  Expected retries at 10K concurrent: ~100 retries per successful order → 1M DB operations for 100 orders
  Better: Redis DECR (atomic) → only 100 succeed, rest rejected immediately

Storage:
  Products: 10M products × 2KB = 20GB (fits in memory with Elasticsearch index)
  Orders: 50K orders/day × 365 × 5 years × 500 bytes = 45GB
  Cart: 10M active carts × 1KB = 10GB (Redis, TTL 7 days)
```

### Architecture Diagram

```
[Browser/App]
     │
     ▼
[API Gateway + CDN]
  (rate limiting, auth, caching static assets)
     │
     ├──────────────────────────────────────────────────────┐
     │                                                      │
     ▼                                                      ▼
[Product Service]                                   [Cart Service]
  - Elasticsearch for search                          - Redis (TTL 7d)
  - PostgreSQL for catalog (source of truth)          - Add/remove/update items
  - Redis for product detail cache                    - Validate against catalog
     │                                                      │
     │                                                      ▼
     │                                            [Checkout Service]
     │                                              - Validate cart items
     │                                              - Reserve inventory
     │                                              - Charge payment (saga)
     │                                              - Create order
     │                                                      │
     ▼                                                      ▼
[Inventory Service]                              [Order Service]
  - PostgreSQL (strong consistency)                - PostgreSQL
  - Redis for flash sale stock (atomic DECR)       - Status: placed→packed→shipped
  - Optimistic locking for normal orders           - Kafka: order events

[Payment Service]
  - Stripe/PayPal integration
  - Idempotency keys (prevent double-charge)

[Search] → Elasticsearch (product catalog, faceted search)
[CDN]    → Cloudfront (product images, static assets)
[Media]  → S3 (product images, compressed, CDN-backed)
```

### Data Model

```sql
-- Products
CREATE TABLE products (
    product_id   BIGINT PRIMARY KEY,
    seller_id    BIGINT NOT NULL,
    title        VARCHAR(500) NOT NULL,
    description  TEXT,
    price_cents  INT NOT NULL,
    category_id  INT,
    status       VARCHAR(20) DEFAULT 'active',  -- active|paused|deleted
    created_at   TIMESTAMP DEFAULT NOW()
);

-- Inventory (separate from products for strong consistency isolation)
CREATE TABLE inventory (
    product_id      BIGINT PRIMARY KEY REFERENCES products(product_id),
    available_qty   INT NOT NULL DEFAULT 0,  -- purchasable stock
    reserved_qty    INT NOT NULL DEFAULT 0,  -- held during checkout (not yet paid)
    version         INT NOT NULL DEFAULT 0   -- optimistic lock version
);

-- Orders
CREATE TABLE orders (
    order_id     BIGINT PRIMARY KEY,
    user_id      BIGINT NOT NULL,
    status       VARCHAR(30) NOT NULL,  -- placed|payment_pending|paid|packed|shipped|delivered|cancelled
    total_cents  INT NOT NULL,
    created_at   TIMESTAMP DEFAULT NOW(),
    updated_at   TIMESTAMP DEFAULT NOW()
);

-- Order line items
CREATE TABLE order_items (
    order_id   BIGINT REFERENCES orders(order_id),
    product_id BIGINT,
    quantity   INT NOT NULL,
    price_cents INT NOT NULL,  -- snapshot price at purchase time
    PRIMARY KEY (order_id, product_id)
);

-- Cart (stored in Redis as Hash; included here as logical schema)
-- Key: "cart:{user_id}"
-- Fields: { product_id: quantity, product_id: quantity, ... }
-- TTL: 7 days (auto-expire abandoned carts)

-- Idempotency keys (prevent double payment)
CREATE TABLE idempotency_keys (
    key          VARCHAR(64) PRIMARY KEY,  -- UUID from client
    resource_id  BIGINT,                  -- order_id created
    response     JSONB,                   -- cached response
    created_at   TIMESTAMP DEFAULT NOW()
);
```

### API Design

```
# Product browsing
GET /v1/products?q=laptop&category=electronics&price_min=500&page_size=20&cursor=<cursor>
  Response: { "products": [...], "next_cursor": "...", "total_count": 1420 }

GET /v1/products/{product_id}
  Response: { "product_id": "...", "title": "...", "price_cents": 99900,
              "available_qty": 42, "images": [...] }

# Cart
POST /v1/cart/items          -- Body: { "product_id": "123", "quantity": 2 }
PUT  /v1/cart/items/{id}     -- Body: { "quantity": 3 }
DELETE /v1/cart/items/{id}
GET  /v1/cart                -- current cart with live prices and stock check

# Checkout (idempotent with idempotency key)
POST /v1/orders
  Headers: Idempotency-Key: <uuid>
  Body: { "cart_id": "...", "shipping_address": {...}, "payment_method_id": "pm_xxx" }
  Response: { "order_id": "...", "status": "payment_pending", "total_cents": 19980 }

# Order management
GET /v1/orders/{order_id}
  Response: { "order_id": "...", "status": "shipped", "tracking_number": "1Z999AA1...",
              "estimated_delivery": "2026-06-01", "items": [...] }
```

### Basic Scaling

- **Catalog on Elasticsearch:** Product search (full-text, faceted, sorting) on Elasticsearch. PostgreSQL is source of truth; Elasticsearch index updated asynchronously via Kafka (CDC from PostgreSQL → Kafka → Elasticsearch indexer).
- **Cart in Redis:** Shopping cart is read/written on every product add; Redis provides sub-millisecond latency. TTL auto-expires abandoned carts after 7 days.
- **Inventory with optimistic locking:** `UPDATE inventory SET available_qty = available_qty - 1, version = version + 1 WHERE product_id = ? AND version = ? AND available_qty > 0` — returns 0 rows updated on conflict; caller retries. Works at normal load; flash sale requires Redis.
- **CDN for catalog images:** All product images stored in S3 + served via CloudFront. Product detail pages aggressively cache (TTL=60s) because catalog data changes infrequently.

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Flash sale: 10K orders/sec for 60 seconds
  Stock: 1,000 units available
  Reality: only 1,000 succeed; 599,000 fail (99.8% failure rate)

Inventory deduction strategy:
  Option A: PostgreSQL row-level lock
    At 10K concurrent, lock wait time → timeouts → connection pool exhausted
    PostgreSQL max practical writes: ~5K/sec on rds.r6g.4xlarge
    Result: 5K/s × 60s = 300K attempts, ~500ms avg wait, timeouts dominate
    NOT viable for flash sale

  Option B: Redis DECR (atomic, single-threaded per key)
    DECR product:stock:123 → returns new value; if < 0, INCR to rollback + reject
    Redis: 500K ops/sec single node; 10K decr/sec is trivial
    Result: 1,000 succeed immediately; 9,000 fail instantly (< 1ms latency for rejection)
    THEN: async saga: Redis stock decrement → Kafka → Payment Service → PostgreSQL order write

  Lua script for atomic check-and-decrement (Redis):
    local qty = redis.call('GET', KEYS[1])
    if tonumber(qty) <= 0 then return 0 end
    return redis.call('DECR', KEYS[1])

Flash sale CDN strategy:
  Product page for flash sale item: served from CDN (cached HTML with countdown timer)
  At t=0, CDN TTL expires → 10M users simultaneously fetch from origin
  Solution: CDN "stale-while-revalidate" → serve stale for 10s while refreshing
  Or: pre-push updated page to CDN edge nodes 5 minutes before sale starts

Database connections at peak:
  10K req/sec × 2ms avg DB time = 20 concurrent DB connections needed
  Connection pool: 50 connections per app server × 20 app servers = 1,000 connections
  RDS PostgreSQL: max_connections = 5,000 (r6g.4xlarge with 128GB) → sufficient
```

### Failure Modes

```
Scenario 1: Payment succeeds but order creation fails (partial saga)
  - User is charged but no order is created → worst possible outcome
  - Fix: distributed saga with compensation
    Step 1: Reserve inventory (decrement stock)
    Step 2: Charge payment → get charge_id
    Step 3: Create order record
    Step 4: Confirm inventory reservation (finalize)
  - If Step 3 fails: trigger compensation:
      - Refund payment (Stripe refund API)
      - Release inventory reservation (INCR stock)
  - Idempotency key on payment prevents double-charge on retry
  - All saga steps publish events to Kafka for audit trail

Scenario 2: Redis goes down during flash sale
  - Inventory counter in Redis is lost
  - Fallback: route to PostgreSQL with row-level locking (accept degraded throughput)
  - Alternative: Redis Cluster with 3 shards × 3 replicas (AOF persistence)
  - Flash sale stock data written to Redis with AOF fsync=always → durable even on crash

Scenario 3: Elasticsearch index falls behind during traffic spike
  - Product catalog updates take 5-30s to appear in search (Kafka lag)
  - Price changes may show stale price in search results
  - Fix: display prices from PostgreSQL at checkout (re-fetch); search results show approximate price
  - Fix: for seller-initiated price changes, Kafka CDC is near-real-time (<1s); acceptable staleness

Scenario 4: Overselling during Redis-PostgreSQL sync lag
  - Redis decremented to 0; async Kafka message to update PostgreSQL pending
  - Kafka consumer crashes → PostgreSQL never updated → Redis restarted (stock resets to PostgreSQL value)
  - Fix: Redis stock initialized from PostgreSQL at start; Kafka message committed only after PostgreSQL update
  - Fix: distributed lock (Redlock) around flash sale stock initialization to prevent double-initialization

Scenario 5: Cart price drift (user adds item, price changes before checkout)
  - Cart stores product_id + quantity; prices fetched from catalog
  - If price increases between cart-add and checkout: user sees higher price
  - Fix: at checkout, re-fetch live prices from product service; show price diff to user
  - Fix: lock price for 15 minutes after add-to-cart (price_locked_at, locked_price columns)
```

### Consistency Boundaries

```
Strong consistency required:
  Inventory deduction: must not oversell; Redis DECR atomic + PostgreSQL confirmation
  Payment processing: idempotency key + Stripe retry semantics
  Order creation: single PostgreSQL transaction (order + order_items)

Eventual consistency acceptable:
  Product catalog: price/description changes propagate in <5s via CDC Kafka → Elasticsearch
  Inventory display in catalog: show "In Stock" / "Low Stock" / "Out of Stock" with 30s staleness
  Order status updates: Kafka-driven status machine; eventual propagation to user (push notification)
  Recommendation engine: batch-updated nightly or hourly

Saga for checkout (distributed transaction alternative):
  No 2PC (too slow, not supported by Stripe)
  Saga: sequence of local transactions with compensating actions

  FORWARD: reserve_inventory → charge_payment → create_order → confirm_inventory
  COMPENSATE on failure at each step:
    failure at charge_payment: release_inventory_reservation
    failure at create_order:   refund_payment + release_inventory_reservation

  Saga orchestrator (Checkout Service) tracks state in PostgreSQL:
    saga_id, step, status (pending|done|failed|compensated)
```

### Cost Model

```
Infrastructure for 10M DAU + flash sales:

PostgreSQL (orders + products + inventory):
  Primary + 2 read replicas: db.r6g.4xlarge ($0.960/hr × 3) = $2,074/month
  Storage: 200GB gp3 = $16/month

Redis cluster (cart + flash sale inventory):
  3-node cluster: cache.r6g.xlarge ($0.207/hr × 3) = $447/month

Elasticsearch (product search):
  6 nodes × r6g.2xlarge ($0.504/hr × 6) = $2,177/month
  Storage: 200GB SSD for 10M products

App servers (Product, Cart, Checkout, Order services):
  Normal: 20 × c6i.2xlarge ($0.340/hr × 20) = $4,896/month
  Flash sale auto-scale: +40 instances for 10min = 40 × $0.340 × (10/60) = $23 (trivial)

Kafka (CDC, order events):
  6 brokers: 6 × m6i.xlarge ($0.192/hr × 6) = $831/month

CDN (CloudFront) + S3 (product images):
  10M products × 5 images × 200KB = 10TB storage = $230/month on S3
  CDN egress: 10M DAU × 20 images/session × 200KB = 40TB/day → expensive
  CDN offloads ~90% → origin egress 4TB/day × $0.09/GB × 30 = $10,800/month

Total: ~$21K/month at 10M DAU
Per-order cost: 50K orders/day × 30 days = 1.5M orders/month
  $21,000 / 1.5M orders = $0.014 per order (infrastructure cost only)
Dominant cost: CDN/S3 egress — use image compression (WebP), reduce image sizes
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **Optimistic locking (DB)** | No lock contention at low concurrency; simple | Retries at high concurrency; N×M contention for N items × M buyers | Normal inventory (<1K concurrent buyers per item) |
| **Redis DECR (atomic counter)** | Sub-millisecond; handles 500K ops/sec; no retries | Data loss risk without persistence; two-system sync complexity | Flash sales, high-concurrency stock deduction |
| **Pessimistic DB lock (SELECT FOR UPDATE)** | Guaranteed serialization; no retry logic | Serializes ALL buyers through 1 lock; throughput = 1 write/lock-time | Low-concurrency, high-value items (luxury goods) |
| **Distributed saga (Checkout)** | Handles partial failures; no distributed lock needed | Complex compensating transactions; eventual consistency across steps | Multi-service checkout with external payment |
| **2-Phase Commit (2PC)** | Atomic across all services | Blocks on coordinator failure; not supported by payment APIs | Same DB cluster only; never use across service boundaries |

## Follow-up Questions (escalating difficulty)

1. **(L3)** Why can't you use a simple SQL UPDATE to decrement inventory for a flash sale?
   → Under 10K concurrent buyers, all 10K transactions read stock=100, then all try to update. The DB serializes them, but each must wait for the previous lock release. At 10K concurrent: 10K lock acquisitions × 5ms each = 50 seconds of sequential waiting. Connection pool exhausts. Redis DECR is atomic and single-threaded; 10K concurrent DECR calls are processed at 500K ops/sec — completed in 20ms.

2. **(L3)** What is the cart-checkout race condition and how do you prevent it?
   → User adds last item to cart (stock=1), but another user buys it before checkout completes. Cart says "1 available" but checkout fails inventory deduction. Fix: don't trust cart's stale stock data; re-validate at checkout time with a fresh inventory read. Better: reserve inventory at "add to cart" time with a 15-minute TTL hold (converts to sold on purchase, released if cart abandoned).

3. **(L4)** Explain idempotency keys in payment processing.
   → A client-generated UUID sent with the payment request. If the network drops after the payment is processed but before the response is received, the client retries with the same key. The payment service returns the cached response for that key without charging again. Stripe's idempotency key is stored with the charge; retries within 24h with the same key return the original result.

4. **(L4)** How do you handle the "sold out but not really" problem when a buyer abandons checkout?
   → Inventory reservation during checkout must have a TTL (e.g., 15 minutes). If payment is not confirmed within 15 minutes, a background job (or Redis key expiry event) releases the reservation (increments available_qty). This prevents permanently holding stock for users who abandon checkout.

5. **(L5)** Walk through the distributed saga for a failed payment in checkout.
   → Step 1: Checkout Service decrements Redis stock counter (reservation). Step 2: calls Payment Service with idempotency key → payment API returns error (card declined). Checkout Service triggers compensation: INCR Redis stock counter to restore reservation. No PostgreSQL write happened yet (order not created), so no DB compensation needed. Saga state logged to PostgreSQL for observability. Total: 2 Redis ops + 1 payment API call → 50ms for the failed path.

6. **(L5)** How do you design the flash sale countdown so 10M users see it update in real-time without overloading the backend?
   → Client-side countdown timer (JavaScript, counts down from known start time). The start time is embedded in the page at load time (cached by CDN). No server polling needed — timer runs in-browser. At t=0, product page state changes from "waiting" to "buy now" — this can be triggered by: (a) page reload after timer hits zero, or (b) SSE/WebSocket push from a lightweight notification service. The inventory check happens only when user clicks "Buy" — not during the countdown.

7. **(L5+)** Design an inventory system that handles 10K orders/sec during a flash sale with no overselling and zero data loss, even if Redis crashes mid-sale.
   → Use Redis Cluster with AOF persistence (appendfsync=always) — every DECR is fsync'd to disk before returning. Stock initialized from PostgreSQL before sale starts. Each DECR publishes to a persistent Kafka topic. Kafka consumer writes confirmed deductions to PostgreSQL. If Redis crashes: restart with AOF replay → stock restored to correct state. Kafka consumer lag shows exactly how many deductions haven't been persisted to PostgreSQL. Reconciliation job on restart: PostgreSQL count vs Redis count; if mismatch, correct Redis. RTO: 30s (Redis AOF replay) + 10s (reconciliation) = 40s downtime for Redis crash.

## Anti-patterns / Things NOT to Say

- **"Use database transactions for the entire checkout flow"** — Checkout spans multiple services (inventory, payment, order). A distributed DB transaction across service boundaries requires 2PC, which is slow, fragile, and impossible when payment goes to Stripe (external API). Use the saga pattern with compensating transactions instead.
- **"Cache inventory counts in application memory"** — Application-local caches are not shared between instances. Two app servers both cache stock=5; both decrement to 4 in their local cache; stock never reaches 0 in either view. Inventory state must live in a single shared atomic store (Redis or database row with locking).
- **"Show real-time inventory counts on product listing pages"** — Fetching live inventory for every product in a search result (20 products per page, 578 searches/sec = 11,560 inventory reads/sec) adds 100ms+ latency to every search. Show bucketed labels ("In Stock", "Low Stock: <10 left", "Out of Stock") with 60s cache TTL. Exact count shown only on product detail page.
- **"Use eventual consistency for inventory"** — Eventual consistency for inventory means two buyers can simultaneously read stock=1, both proceed, and both receive confirmation while only one can actually get the item. The result is an oversold item and a failed fulfillment (or a refund). Inventory deduction must be strongly consistent — there is no business justification for eventual consistency on stock.
- **"A single monolithic checkout service handles everything atomically"** — In a monolith with a single DB, this works. At scale, checkout involves external services (payment provider, fraud detection, loyalty points). Each external call can fail independently. Treating them as one atomic unit is not achievable; the saga pattern handles partial failures explicitly.

## Python Implementation (sketch)

```python
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

@dataclass
class Product:
    product_id: int
    title: str
    price_cents: int

@dataclass
class CartItem:
    product_id: int
    quantity: int

@dataclass
class Order:
    order_id: str
    user_id: int
    items: list
    total_cents: int
    status: str = "placed"

class InventoryService:
    """Simulates Redis atomic DECR for inventory."""

    def __init__(self):
        self._stock: Dict[int, int] = {}
        self._lock = threading.Lock()  # simulates Redis single-threaded ops

    def set_stock(self, product_id: int, qty: int):
        with self._lock:
            self._stock[product_id] = qty

    def reserve(self, product_id: int, qty: int) -> bool:
        """Atomic check-and-decrement. Returns True if reserved."""
        with self._lock:
            current = self._stock.get(product_id, 0)
            if current >= qty:
                self._stock[product_id] = current - qty
                return True
            return False

    def release(self, product_id: int, qty: int):
        """Compensating action: restore reserved stock."""
        with self._lock:
            self._stock[product_id] = self._stock.get(product_id, 0) + qty

    def get_stock(self, product_id: int) -> int:
        with self._lock:
            return self._stock.get(product_id, 0)


class CheckoutService:
    """Saga-based checkout: inventory → payment → order."""

    def __init__(self, inventory: InventoryService):
        self.inventory = inventory
        self._orders: Dict[str, Order] = {}
        self._idempotency: Dict[str, Order] = {}

    def _simulate_payment(self, user_id: int, amount_cents: int) -> Tuple[bool, str]:
        """Simulate payment API; fails 10% of the time."""
        import random
        if random.random() < 0.10:
            return False, "card_declined"
        return True, f"charge_{uuid.uuid4().hex[:8]}"

    def checkout(self, user_id: int, cart: Dict[int, CartItem],
                 products: Dict[int, Product],
                 idempotency_key: str) -> Optional[Order]:
        # Idempotency: return cached result for duplicate requests
        if idempotency_key in self._idempotency:
            return self._idempotency[idempotency_key]

        # Saga Step 1: Reserve inventory for all items
        reserved = []
        for item in cart.values():
            if not self.inventory.reserve(item.product_id, item.quantity):
                # Compensate: release all already-reserved items
                for r_pid, r_qty in reserved:
                    self.inventory.release(r_pid, r_qty)
                print(f"Checkout failed: insufficient stock for product {item.product_id}")
                return None
            reserved.append((item.product_id, item.quantity))

        # Saga Step 2: Charge payment
        total = sum(
            products[item.product_id].price_cents * item.quantity
            for item in cart.values()
        )
        success, charge_id = self._simulate_payment(user_id, total)
        if not success:
            # Compensate Step 1: release inventory
            for r_pid, r_qty in reserved:
                self.inventory.release(r_pid, r_qty)
            print(f"Checkout failed: payment declined (compensation: stock released)")
            return None

        # Saga Step 3: Create order
        order_id = str(uuid.uuid4())
        order = Order(
            order_id=order_id,
            user_id=user_id,
            items=list(cart.values()),
            total_cents=total,
            status="paid"
        )
        self._orders[order_id] = order
        self._idempotency[idempotency_key] = order
        print(f"Order {order_id} created | total: ${total/100:.2f} | charge: {charge_id}")
        return order


# Demo: flash sale with limited stock
if __name__ == "__main__":
    inventory = InventoryService()
    inventory.set_stock(product_id=1, qty=5)  # only 5 units

    products = {1: Product(1, "Flash Sale Laptop", price_cents=99900)}

    checkout_svc = CheckoutService(inventory)
    results = {"success": 0, "fail": 0}
    lock = threading.Lock()

    def buyer(buyer_id: int):
        cart = {1: CartItem(product_id=1, quantity=1)}
        idem_key = f"buyer-{buyer_id}-{uuid.uuid4().hex}"
        order = checkout_svc.checkout(buyer_id, cart, products, idem_key)
        with lock:
            if order:
                results["success"] += 1
            else:
                results["fail"] += 1

    # Simulate 20 concurrent buyers for 5 items
    threads = [threading.Thread(target=buyer, args=(i,)) for i in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"\nResults: {results}")
    print(f"Remaining stock: {inventory.get_stock(1)}")
    # Expected: 5 success, 15 fail (or fewer if payment failures), stock = 0
```
