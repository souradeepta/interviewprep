# Payment System Design: Building Safe Financial Transactions

Master payment system architecture for handling money safely and reliably.

---

## Payment System Requirements

```
ACID properties (strict):
- Atomicity: All or nothing (money goes to account OR doesn't)
- Consistency: Account balance always valid
- Isolation: Concurrent transactions don't interfere
- Durability: Committed transaction survives crashes

Idempotency:
- Same payment twice = processed once
- Network retry safe

PCI Compliance:
- No credit card storage (use payment processor)
- Encryption for data in transit and at rest
- Regular security audits
```

---

## Payment Flow

### Simplified Flow

```
User initiates payment
  ↓
API reserves amount (pessimistic lock)
  ↓
Call payment processor (Stripe, PayPal)
  ↓
If success: Commit transaction
  ↓
If failure: Rollback and refund
```

### Detailed Flow

```python
def process_payment(user_id, amount, order_id):
    try:
        # 1. Validate user and amount
        if amount < 0 or amount > MAX_AMOUNT:
            raise ValueError("Invalid amount")
        
        # 2. Reserve funds (pessimistic lock)
        user = db.lock_user(user_id)
        if user.balance < amount:
            raise InsufficientFundsError()
        
        # 3. Create payment record
        payment = db.create_payment(
            user_id=user_id,
            amount=amount,
            status='pending',
            idempotency_key=str(uuid4())  # For retries
        )
        
        # 4. Call payment processor
        result = payment_processor.charge(
            amount=amount,
            card_token=user.card_token,
            idempotency_key=payment.idempotency_key
        )
        
        # 5. Update payment status
        if result.success:
            db.update_payment(payment.id, status='completed')
            db.deduct_balance(user_id, amount)
            db.create_order(user_id, order_id, payment.id)
            return {'success': True, 'payment_id': payment.id}
        else:
            db.update_payment(payment.id, status='failed', error=result.error)
            return {'success': False, 'error': result.error}
    
    except Exception as e:
        # Automatic rollback from transaction
        db.update_payment(payment.id, status='error', error=str(e))
        raise
```

---

## Idempotency for Retries

**Problem:** Network fails after charging but before response
- User sees failure, retries
- Payment processor charged twice

**Solution:** Idempotency key

```python
# First request
result = payment_processor.charge(
    amount=100,
    idempotency_key="txn-123-abc"
)
# Response: success

# Network fails, client retries with SAME key
result = payment_processor.charge(
    amount=100,
    idempotency_key="txn-123-abc"  # Same key
)
# Response: success (cached from first request, no double charge!)
```

---

## Handling Refunds

```python
def refund_payment(payment_id, refund_amount):
    payment = db.get_payment(payment_id)
    
    if payment.status != 'completed':
        raise ValueError("Only completed payments can be refunded")
    
    # Call payment processor
    result = payment_processor.refund(
        charge_id=payment.processor_charge_id,
        amount=refund_amount,
        idempotency_key=str(uuid4())  # Different key from original charge
    )
    
    if result.success:
        db.create_refund(
            payment_id=payment_id,
            amount=refund_amount,
            status='completed'
        )
        db.add_to_balance(payment.user_id, refund_amount)
        return {'success': True}
    else:
        raise PaymentProcessorError(result.error)
```

---

## Handling Failures

### Processor Is Down

```
Option 1: Queue request
- Store pending payment in DB
- Retry later (exponential backoff)
- Notify user transaction is processing

Option 2: Fail immediately
- Refund user
- Let them retry later

Choose: Option 1 (better UX)
```

### Network Timeout

```
Status unknown: Did processor charge or not?

Solution: Poll processor status
- After N seconds, query processor with idempotency key
- If charged: Mark as completed
- If not: Retry charging
```

### Reconciliation

```
Daily reconciliation:
- Get all "pending" payments from DB
- Query processor for status
- Update DB to match processor state
- Alert if discrepancies
```

---

## Payment System Architecture

```
┌──────────────────────────────────┐
│ Payment API (rate-limited, logged)│
└──────────┬───────────────────────┘
           │
           ↓
┌──────────────────────────────────┐
│ Payment Service                  │
│ - Validation                     │
│ - Idempotency key handling       │
│ - Transaction management         │
└──────────┬───────────────────────┘
           │
      ┌────┴────┐
      ↓         ↓
   [DB]      [Queue]
      │         │
      │         └→ Retry handler (exponential backoff)
      │
┌─────────────────────────────────────┐
│ Payment Processor Integration        │
│ (Stripe, PayPal, Square, etc.)     │
└─────────────────────────────────────┘
      │
      ↓
[Logs] [Monitoring] [Alerts]
```

---

## PCI Compliance

```
DO:
✓ Use payment processor (never store raw card data)
✓ Encrypt payment data in transit (TLS)
✓ Tokenize cards (store tokens, not numbers)
✓ Audit logs for all payment operations
✓ Regular security audits

DON'T:
✗ Store credit card numbers
✗ Store CVV/CVC codes
✗ Send cards over HTTP
✗ Log full card numbers
✗ Skimp on security
```

---

## Payment System Checklist

- ✓ ACID transactions for payment
- ✓ Idempotency keys for retries
- ✓ Pessimistic locking (reserve funds)
- ✓ Payment processor integration (no card storage)
- ✓ Refund handling and reconciliation
- ✓ Retry logic with exponential backoff
- ✓ Handling processor failures (queue, retry later)
- ✓ Monitoring and alerting
- ✓ Audit logging for all transactions
- ✓ PCI compliance (no card data)
- ✓ 3D Secure / 2FA support
- ✓ Rate limiting and fraud detection

