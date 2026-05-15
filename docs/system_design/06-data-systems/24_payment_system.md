# Payment Processing System

## Problem Statement
Design a payment system handling transactions securely and reliably.

**Requirements:**
- Process payments
- Handle failures
- Ensure idempotency
- PCI compliance
- Fraud detection

## Design

### Payment Flow

```
1. Initiate payment (amount, method)
2. Call payment gateway (Stripe, PayPal)
3. Get transaction ID
4. Confirm in business DB
5. Return receipt
```

### Idempotency

```
Idempotency key: Unique per transaction
Deduplicate retries
Idempotent gateway operations
```

### Failure Handling

```
Network failure: Retry with backoff
Gateway error: Mark as pending, retry
Insufficient funds: Return error
Reconciliation: Match gateway with DB
```

### Fraud Detection

```
Velocity checks: Rate limiting per user
Amount checks: Unusual amounts
Geographic checks: Unusual locations
3D Secure: For high-risk
```


## Architecture Diagram

```
┌───────────────────────────────┐
│   Payment Processing          │
│  Payment Gateway              │
│  - Stripe, PayPal, Square     │
│  - PCI DSS compliance         │
│  - TLS + vault encryption     │
│  Transaction Processing       │
│  - Authorize, Capture, Refund │
│  Reconciliation               │
│  - Match transactions         │
│  - Anomaly detection (ML)     │
└───────────────────────────────┘
```

## Common Questions & Answers

**Q: Retry on failure?** A: Exponential backoff (1s, 2s, 4s, 8s), max 3 attempts. Store txn ID for idempotency.

**Q: Idempotency?** A: UUID from client, stored server-side. Retried request returns same result.

**Q: PCI DSS?** A: Never store card details. Tokenization: gateway issues token.

**Q: Chargeback?** A: Track evidence (order, shipping). Respond to bank within deadline.

## Back-of-Envelope Calculations

1M txn/day, $1B volume. 98% success (2% retry). 2-5s per txn. Fraud: 0.1% (1K false positives, need review).
## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Gateway only | Simple | Less control |
| Custom processor | Full control | PCI burden |
| PSP | Balanced | Fees |

## Follow-up Interview Questions

1. Currency/forex risk? 2. Subscription billing? 3. Settlement timing? 4. Gateway bottleneck? 5. International methods?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

## Complexity

| Operation | Time |
|-----------|------|
| Process payment | O(network) |
| Confirm | O(1) DB |
| Retry | Exponential backoff |
