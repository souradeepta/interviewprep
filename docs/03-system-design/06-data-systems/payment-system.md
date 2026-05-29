# Payment System

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

A payment system processes money movement: charging a customer's card, crediting a merchant, and
recording the transaction for reconciliation. Unlike most web services, payment operations must be
exactly-once — a user should never be charged twice for the same purchase, and a merchant should
never receive funds twice for the same order. Network timeouts, retries, and partial failures make
this surprisingly hard: when a payment API call times out, was the charge applied or not?

The design must handle idempotent retries, two-phase payment (authorize → capture), refunds, and
reconciliation against external PSP (payment service provider) records, while maintaining PCI-DSS
compliance for cardholder data.

## Functional Requirements

- Initiate payment: charge a customer's payment method for an order
- Authorize and later capture (two-phase, for shipping workflows)
- Refund a payment (full or partial)
- Query payment status by payment_id
- Reconcile payments against PSP (Stripe, Adyen) ledger nightly

## Non-Functional Requirements

- **Scale:** 10K transactions/sec peak (Black Friday); 1K transactions/sec average
- **Latency:** P99 < 3 seconds end-to-end (PSP latency dominates); internal < 100 ms
- **Availability:** 99.99%; payment is a critical path — downtime = lost revenue
- **Consistency:** Exactly-once: a customer is charged exactly once per order; strong consistency
  within a payment (no partial state visible)

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Transactions/sec:  1K avg, 10K peak
Storage/transaction: ~2 KB (payment record + audit events)
Storage/day:       1K * 86400 * 2 KB      = 172 GB/day
Storage/year:      172 * 365              = 62 TB/year (retain 7 years for compliance)
Idempotency keys:  1 per transaction; TTL 24h; 1K/sec * 86400 = 86.4M keys/day
                   Redis: 86.4M * 64 bytes (key+value) = 5.5 GB/day (small)
PSP API calls:     1K/sec → most PSPs rate-limit at 100-1K req/sec per account
                   Solution: multiple PSP accounts / regions; circuit breaker per account
Reconciliation:    Daily: compare our DB records vs PSP settlement file
                   Typical mismatch rate < 0.01%; flag for manual review
```

### Architecture Diagram

```
  Client (Mobile App / Web)
        |
  POST /payments (with idempotency_key header)
        |
  +-----v--------------+
  | Payment API        |  ← validates request, checks idempotency
  | Gateway (stateless)|
  +-----+-----+--------+
        |     |
        |   Check idempotency_key in Redis
        |     ↓ (cache miss: first attempt)
  +-----v--------------+
  | Payment Service    |
  | (write to DB first)|
  +-----+-----+--------+
        |         |
   DB write     PSP API call (Stripe/Adyen)
   status=PENDING  |
        |         | response: success / fail
        |     +---v-----------+
        |     | PSP Gateway   |  (Stripe, Adyen, PayPal)
        |     +---------------+
        |         |
  Update DB status (COMPLETED / FAILED)
  Set idempotency_key in Redis (TTL=24h)
        |
     Response to Client

Reconciliation Job (nightly):
  Pull PSP settlement file → compare with our payments DB → flag mismatches → alert
```

### Data Model

```sql
-- Core payments table
CREATE TABLE payments (
    payment_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id          BIGINT NOT NULL,
    user_id           BIGINT NOT NULL,
    amount_cents      BIGINT NOT NULL CHECK (amount_cents > 0),
    currency          CHAR(3) NOT NULL,            -- "USD", "EUR"
    status            ENUM('PENDING','AUTHORIZED','CAPTURED','FAILED',
                           'REFUNDED','PARTIALLY_REFUNDED') NOT NULL DEFAULT 'PENDING',
    idempotency_key   VARCHAR(128) NOT NULL UNIQUE,
    psp_name          VARCHAR(64) NOT NULL,         -- "stripe", "adyen"
    psp_transaction_id VARCHAR(256),               -- set after PSP response
    psp_auth_code     VARCHAR(128),
    created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    captured_at       TIMESTAMP,
    refunded_at       TIMESTAMP,
    metadata_json     JSON,
    INDEX idx_order_id (order_id),
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_status (status)
);

-- Immutable audit log (append-only)
CREATE TABLE payment_events (
    event_id     BIGSERIAL PRIMARY KEY,
    payment_id   UUID NOT NULL REFERENCES payments(payment_id),
    event_type   VARCHAR(64) NOT NULL,  -- "INITIATED","AUTHORIZED","CAPTURED","FAILED","REFUNDED"
    actor        VARCHAR(128),          -- "user_42", "system", "reconciliation_job"
    metadata     JSON,
    created_at   TIMESTAMP NOT NULL DEFAULT NOW(),
    INDEX idx_payment_events_payment (payment_id, created_at)
);

-- Refunds (child of payment)
CREATE TABLE refunds (
    refund_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id      UUID NOT NULL REFERENCES payments(payment_id),
    amount_cents    BIGINT NOT NULL,
    status          ENUM('PENDING','COMPLETED','FAILED') NOT NULL DEFAULT 'PENDING',
    psp_refund_id   VARCHAR(256),
    reason          VARCHAR(256),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### API Design

```
# Initiate payment (idempotency_key REQUIRED)
POST /payments
  Headers: Idempotency-Key: <client-generated UUID>
  Body: {
    order_id: 78901,
    user_id: 42,
    amount_cents: 4999,
    currency: "USD",
    payment_method_token: "pm_abc123"   -- tokenized by PSP SDK on client
  }
  Response: 201 {
    payment_id: "pay_uuid",
    status: "CAPTURED",
    amount_cents: 4999,
    psp_transaction_id: "ch_stripe_abc"
  }

# Get payment status
GET /payments/{payment_id}
  Response: 200 { payment_id, status, amount_cents, created_at, ... }

# Authorize (hold funds without capture)
POST /payments/{payment_id}/authorize
  Response: 200 { status: "AUTHORIZED", psp_auth_code: "AUTH123" }

# Capture authorized payment (at shipping time)
POST /payments/{payment_id}/capture
  Body: { amount_cents: 4999 }   -- may be <= authorized amount
  Response: 200 { status: "CAPTURED", captured_at: "..." }

# Refund
POST /payments/{payment_id}/refunds
  Headers: Idempotency-Key: <UUID>
  Body: { amount_cents: 4999, reason: "customer_request" }
  Response: 201 { refund_id, status: "COMPLETED", amount_cents: 4999 }
```

### Basic Scaling

- **Idempotency:** Every create/mutate request requires a client-supplied `Idempotency-Key`; server
  checks Redis before processing; if key exists, return cached response (no duplicate charge)
- **DB transactions:** Payment status update (PENDING → CAPTURED) and event log insert happen in
  one DB transaction; never show partial state externally
- **PSP fallback:** Configure primary PSP (Stripe) and secondary PSP (Adyen); if primary
  returns 5xx, retry on secondary using same idempotency key with `psp_name` prefix
- **Circuit breaker:** If PSP error rate > 5% in 30 sec, trip circuit breaker; queue payments
  internally and retry when PSP recovers

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
DB node sizing (payments table, write-heavy):
  Writes: 1K TPS (avg) * 3 rows/transaction (payment + 2 events) = 3K writes/sec
  Reads: 5K QPS (status checks) — mostly from primary + cache
  Node: db.r6g.2xlarge (8 vCPU, 64 GB RAM) — handles 5K writes/sec in Postgres with WAL
  Read replica: 1 replica for status check queries
  Disk: 62 TB * 7 years = 434 TB → partition by year; archive to S3 Glacier after 2 years

Redis (idempotency store):
  1K new keys/sec * 86400 sec * 128 bytes = 11 GB/day, but TTL=24h → rolling 11 GB
  Node: cache.r6g.large (16 GB RAM) → ample headroom
  Persistence: RDB snapshot every 5 min (lose max 5 min of idempotency state on crash)

PSP API rate limits:
  Stripe: 100 RPS per API key per account (can request higher limits)
  At 10K TPS peak: need 100 Stripe accounts or use Stripe Treasury + higher limits
  Alternative: maintain payment queue; PSP proxy service pools connections across accounts
  Hedge: split traffic: 70% Stripe, 30% Adyen → no single PSP failure takes down system

Reconciliation storage:
  PSP sends settlement file daily: ~1M transactions/day * 500 bytes = 500 MB/day
  Store in S3; Spark job compares with payments DB; produces mismatch report
```

### Failure Modes

```
FAILURE: PSP timeout (most common failure)
  Scenario:    POST to Stripe times out after 30 sec — was charge applied or not?
  Mitigation:  Idempotency key: retry with SAME Idempotency-Key → if Stripe processed it,
               returns same charge_id; if not, processes fresh. Never lose or change the key.
  After 3 retries: mark payment as PENDING_RESOLUTION; trigger reconciliation within 5 min
               (check PSP webhook or poll PSP for charge status)

FAILURE: DB write fails AFTER PSP charge succeeds (partial failure)
  Scenario:    Stripe charges customer; our DB write fails → customer charged, no order record
  Prevention:  Write payment record (status=PENDING) to DB BEFORE calling PSP
               If DB write fails: don't call PSP; return 500 to client
               If PSP call fails: update DB status=FAILED; safe to retry
  Recovery:    Reconciliation job detects PSP charge with no matching DB record → alert + refund

FAILURE: Double charge (network retry submits payment twice)
  Prevention:  Idempotency key checked in Redis BEFORE DB write + PSP call
               Atomic: SET NX (set if not exists) in Redis with payment_id as value
               If NX fails (key exists): return cached response without hitting PSP
  Risk:        Redis crashes between idempotency key deletion and PSP call
  Mitigation:  Set idempotency key in Redis BEFORE PSP call (not after); if PSP call fails,
               key exists but payment record shows FAILED — retry is safe

FAILURE: Refund after PSP already refunded (double refund)
  Prevention:  Refund idempotency key: store refund_id + status in DB; check before calling PSP
               PSP also deduplicates refunds by their own idempotency key
```

### Consistency Boundaries

```
EXACTLY-ONCE GUARANTEE (application-level):
  1. Client generates idempotency_key (UUID) per payment attempt
  2. Server: SET NX "idem:{key}" in Redis (atomic check-and-set)
     - If already set: return cached response (no PSP call)
     - If not set: proceed
  3. Write DB row (status=PENDING) with idempotency_key (UNIQUE constraint)
  4. Call PSP with SAME idempotency_key as PSP-level idempotency header
  5. Update DB row: status=CAPTURED; store psp_transaction_id
  6. Return response; also cache in Redis value for future duplicate detection

AUTHORIZATION vs CAPTURE:
  AUTHORIZED: PSP holds funds (up to 7 days); merchant has not received money
  CAPTURED:   Money transferred to merchant; cannot cancel (only refund)
  State machine: PENDING → AUTHORIZED → CAPTURED
                          ↓
                        FAILED

PCI-DSS DATA ISOLATION:
  Raw card numbers (PAN): NEVER stored in our systems; tokenized client-side by PSP.js
  Tokens (pm_abc123): safe to store; can only be used with our merchant account
  Audit logs: stored in separate, network-isolated PCI-scope database
  Access: payment service has no direct DB access to card data; reads tokens only
```

### Cost Model

```
Infrastructure:
  DB (Postgres RDS Multi-AZ): db.r6g.2xlarge $0.576/hr * 8760 = $5,046/yr
  Read replica:               db.r6g.xlarge  $0.288/hr * 8760 = $2,523/yr
  Redis (idempotency):        cache.r6g.large $0.155/hr * 8760 = $1,358/yr
  App servers (ECS):          10× c6g.xlarge $0.136/hr * 8760  = $11,913/yr
  Storage (RDS + S3):         62 TB/yr hot + archive            = $7,440/yr
  Total infrastructure:                                          = $28,280/yr

PSP fees (Stripe standard):
  1K TPS avg → 86.4M transactions/day → 31.5B/yr
  Stripe: $0.029 + $0.30 per transaction = $0.329 avg
  At $10 avg order: fee ≈ 3.3% of revenue — PSP fee >> infrastructure cost

Per transaction infrastructure cost: $28,280 / 31.5B = $0.0000009 (< 0.1 cent/transaction)
Dominant cost: PSP processing fee (~$0.329/transaction)

Optimization levers:
  1. Negotiate lower Stripe rates at volume (custom pricing at 1M+ transactions/month)
  2. Route low-risk transactions to cheaper PSP (Adyen ≈ 0.3% + $0.10 vs Stripe 2.9% + $0.30)
  3. ACH bank transfers (1% capped at $5) for high-value B2B orders → 90% fee reduction
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| Synchronous charge (authorize + capture in one step) | Simple; immediate feedback; one PSP call | No pre-authorization; can't adjust amount after order changes | Digital goods, instant delivery, low-value transactions |
| Two-phase (authorize → capture at fulfillment) | Funds reserved; can adjust capture amount; no charge if order fails | Complex; authorization expires after 7 days; more PSP calls | Physical goods with shipping delay, subscription billing |
| Asynchronous (queue → process) | Decoupled from PSP; handles PSP downtime gracefully | Delayed confirmation; complex status tracking; UX shows "processing" | High-volume B2B, batch invoice payments |
| Saga pattern for distributed payment | Works across microservices; no distributed lock | Complex compensating transactions; eventual consistency; harder to debug | Multi-service order flow (payment + inventory + fulfillment) |

## Follow-up Questions (escalating difficulty)

1. **(L3)** Why is idempotency so important in payment systems?
   → Network failures are inevitable. When a payment request times out, the client doesn't know
   if the charge was applied. Without idempotency, a retry creates a duplicate charge. With an
   idempotency key, the server recognizes the retry and returns the original result — the customer
   is never charged twice.

2. **(L3)** What is the difference between authorization and capture?
   → Authorization: PSP checks that the card is valid and the funds are available, then "holds"
   the funds (reduces available balance). No money moves yet. Capture: money is actually
   transferred to the merchant. Two-phase is used for physical goods where you don't want to
   charge until you ship; authorization expires after ~7 days.

3. **(L4)** How do you handle a PSP timeout? Walk through the full recovery flow.
   → Write payment record (status=PENDING) before calling PSP. If PSP times out after 30 sec:
   (1) Retry with same idempotency key — PSP returns original result if it was processed.
   (2) If 3 retries fail: mark PENDING_RESOLUTION. (3) Start reconciliation: poll PSP API or
   wait for PSP webhook. (4) Update status from PSP ground truth. Never mark FAILED unless
   PSP explicitly says so.

4. **(L4)** How does reconciliation work and what mismatches do you look for?
   → PSP sends a daily settlement file listing all processed charges and their statuses. Our
   reconciliation job: (1) Parse PSP file. (2) For each PSP transaction, find matching record
   in our DB by psp_transaction_id. (3) Flag: in PSP but not in DB (possible double charge
   we didn't record), in DB but not in PSP (our record thinks charge succeeded but PSP has
   no record — need refund investigation), amount mismatch. Typically < 0.01% mismatch rate.

5. **(L5)** How do you prevent race conditions when two requests try to create a payment for
   the same order simultaneously?
   → Multiple defenses: (1) Unique constraint on (order_id, status) — only one PENDING or
   CAPTURED payment per order. (2) Idempotency key unique constraint — if two requests arrive
   simultaneously with different keys, only one DB INSERT succeeds; other gets unique violation.
   (3) Application-level: SELECT FOR UPDATE on order row before creating payment (advisory lock).
   Defense in depth: each layer catches a different race condition.

6. **(L5)** Explain the write-before-call pattern and why order matters.
   → Write DB record (status=PENDING) BEFORE calling PSP. If PSP call succeeds: update to
   CAPTURED. If PSP call fails: update to FAILED. Why this order? If we call PSP first and
   DB write fails: customer is charged but no record exists — money lost. Writing first ensures
   a record exists for every PSP interaction, making reconciliation possible even after a
   catastrophic failure.

7. **(L5+)** How would you implement fraud detection without blocking the payment critical path?
   → Real-time scoring: run lightweight fraud rules (velocity checks, geolocation mismatch,
   device fingerprint) synchronously in < 50 ms. For transactions above a risk threshold, run
   async ML model scoring (sends event to Kafka → fraud-ml-service → result in ~200 ms). For
   those above high-risk threshold: async review with 24h hold (capture delayed). Never block
   the PSP auth call on the ML model — decouple via event-driven post-authorization fraud review.

## Anti-patterns / Things NOT to Say

- **"Store the credit card number in our database"** — PCI-DSS prohibits storing raw PANs
  (primary account numbers) without extensive security controls. Use PSP tokenization: PSP
  collects card details client-side, returns a token. We store only the token.
- **"Just retry on failure"** — Retrying without idempotency keys creates duplicate charges.
  Retries must use the same idempotency key so the PSP (and our own system) can recognize and
  deduplicate the retry.
- **"Use auto-increment ID as the idempotency key"** — Auto-increment IDs are sequential and
  predictable. Idempotency keys should be client-generated UUIDs (unpredictable, unique per
  request). Using order_id as idempotency key means a retry for a different payment on the
  same order would incorrectly be treated as a duplicate.
- **"Mark payment as FAILED after PSP timeout"** — You don't know if the PSP processed the
  charge. Marking it FAILED and retrying could double-charge the customer. Mark as
  PENDING_RESOLUTION and reconcile against PSP before deciding.
- **"Handle reconciliation manually"** — At 1K TPS, you have 86M transactions/day. Manual
  reconciliation is impossible. Build automated reconciliation with alerting for mismatches;
  manual review only for flagged exceptions.

## Python Implementation (sketch)

```python
import uuid
import time
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    CAPTURED = "CAPTURED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

@dataclass
class Payment:
    payment_id: str
    order_id: int
    amount_cents: int
    currency: str
    status: PaymentStatus
    idempotency_key: str
    psp_transaction_id: Optional[str] = None

class IdempotencyStore:
    """Simulates Redis-based idempotency key store."""
    def __init__(self):
        self._store: dict[str, dict] = {}

    def set_if_absent(self, key: str, value: dict, ttl_sec: int = 86400) -> bool:
        """Returns True if key was set (first time), False if already exists."""
        if key in self._store:
            return False
        self._store[key] = {"value": value, "expires_at": time.time() + ttl_sec}
        return True

    def get(self, key: str) -> Optional[dict]:
        entry = self._store.get(key)
        if entry and entry["expires_at"] > time.time():
            return entry["value"]
        return None

class FakePSP:
    """Simulates a payment service provider."""
    def charge(self, amount_cents: int, token: str, idempotency_key: str) -> dict:
        # Simulate ~95% success rate
        return {"success": True, "psp_transaction_id": f"ch_{uuid.uuid4().hex[:8]}"}

class PaymentService:
    def __init__(self):
        self._idem_store = IdempotencyStore()
        self._psp = FakePSP()
        self._db: dict[str, Payment] = {}

    def create_payment(
        self, order_id: int, amount_cents: int, currency: str,
        payment_method_token: str, idempotency_key: str
    ) -> Payment:
        # Step 1: Check idempotency cache
        cached = self._idem_store.get(idempotency_key)
        if cached:
            return self._db[cached["payment_id"]]  # return identical response

        # Step 2: Write PENDING record BEFORE calling PSP
        payment = Payment(
            payment_id=str(uuid.uuid4()),
            order_id=order_id,
            amount_cents=amount_cents,
            currency=currency,
            status=PaymentStatus.PENDING,
            idempotency_key=idempotency_key,
        )
        self._db[payment.payment_id] = payment

        # Step 3: Atomic idempotency key set (SET NX)
        acquired = self._idem_store.set_if_absent(
            idempotency_key, {"payment_id": payment.payment_id}
        )
        if not acquired:
            # Race: another request set the key simultaneously
            cached = self._idem_store.get(idempotency_key)
            return self._db[cached["payment_id"]]

        # Step 4: Call PSP
        try:
            result = self._psp.charge(amount_cents, payment_method_token, idempotency_key)
            if result["success"]:
                payment.status = PaymentStatus.CAPTURED
                payment.psp_transaction_id = result["psp_transaction_id"]
            else:
                payment.status = PaymentStatus.FAILED
        except Exception:
            payment.status = PaymentStatus.PENDING  # Reconcile later
        return payment


# Usage
svc = PaymentService()
idem_key = str(uuid.uuid4())
p1 = svc.create_payment(78901, 4999, "USD", "pm_abc123", idem_key)
p2 = svc.create_payment(78901, 4999, "USD", "pm_abc123", idem_key)  # duplicate
assert p1.payment_id == p2.payment_id, "Duplicate charge prevented"
print(f"Payment {p1.payment_id}: {p1.status}, PSP: {p1.psp_transaction_id}")
```
