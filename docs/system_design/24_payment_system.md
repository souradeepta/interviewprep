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

## Complexity

| Operation | Time |
|-----------|------|
| Process payment | O(network) |
| Confirm | O(1) DB |
| Retry | Exponential backoff |
