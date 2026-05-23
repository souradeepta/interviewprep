# Distributed Transactions — 2PC, Sagas, and Consistency

Ensuring atomicity across multiple databases and services.

---

## ⚖️ Transaction Patterns Comparison

```
Pattern        | Consistency | Latency | Complexity | Use Case
───────────────|─────────────|─────────|────────────|──────────
2-Phase Commit | Strong      | High    | Very High  | Banking
Saga Pattern   | Eventual    | Medium  | Medium     | E-commerce
Event Sourcing | Eventual    | Low     | High       | Audit trail
CQRS           | Eventual    | Low     | High       | Complex domains
```

---

## 🏗️ Two-Phase Commit (2PC)

### How It Works

```
Phase 1 (Prepare):
├─ Coordinator asks all participants "can you commit?"
├─ Each locks resources, checks constraints
├─ Responds "yes" or "no"

Phase 2 (Commit/Abort):
├─ If all say "yes": Coordinator broadcasts COMMIT
├─ If any say "no": Coordinator broadcasts ABORT
└─ All rollback on ABORT
```

### Trade-offs

```
✓ Strong consistency (ACID)
✗ Blocking (locks held during prepare)
✗ Slow (network round-trips)
✗ Failure-prone (coordinator crash = stuck)
✗ Network partition breaks

Use when: Financial transactions (banking)
Avoid when: High latency or frequent failures
```

---

## 🎯 Saga Pattern (Preferred for Microservices)

### Choreography Saga

```
Order Service: Create order
  ↓ (publishes OrderCreated)
Payment Service: Charge payment
  ↓ (publishes PaymentProcessed)
Inventory Service: Reserve stock
  ↓ (publishes InventoryReserved)
Shipping Service: Prepare shipment
  ↓ (publishes ShippingPrepared)

If Inventory fails:
Payment Service: Refund (publishes PaymentRefunded)
Order Service: Cancel order
```

### Trade-offs

```
✓ No blocking (async)
✓ Scales horizontally
✓ Resilient to failures
✗ Eventual consistency (temp inconsistency)
✗ Complex compensation logic
✗ Hard to debug/test

Use when: Microservices, high-scale systems
```

---

## 🧪 Practical Exercises

### Exercise 1: Implement Saga for Order Processing (Medium)

**Problem:**
Process order with payment → inventory → shipping with compensating transactions

**Solution:**

```python
class OrderSaga:
    def __init__(self):
        self.order_id = generate_id()
        self.status = 'PENDING'
        self.steps = []
    
    def execute(self, order_data):
        try:
            # Step 1: Reserve stock
            inventory_result = inventory_service.reserve(
                order_data['items'],
                order_id=self.order_id
            )
            self.steps.append(('inventory_reserve', inventory_result))
            
            # Step 2: Process payment
            payment_result = payment_service.charge(
                order_data['total'],
                order_id=self.order_id
            )
            self.steps.append(('payment_charge', payment_result))
            
            # Step 3: Create shipment
            shipping_result = shipping_service.create(
                order_data,
                order_id=self.order_id
            )
            self.steps.append(('shipping_create', shipping_result))
            
            self.status = 'COMPLETED'
            return True
            
        except Exception as e:
            self.status = 'FAILED'
            self.compensate()
            return False
    
    def compensate(self):
        # Reverse steps in reverse order
        for step_name, result in reversed(self.steps):
            if step_name == 'shipping_create':
                shipping_service.cancel(result['id'])
            elif step_name == 'payment_charge':
                payment_service.refund(result['id'])
            elif step_name == 'inventory_reserve':
                inventory_service.release(result['id'])
```

---

## ❓ Interview Q&A

**Q: Design transaction for transfer between accounts in different databases**

A:
```
Option 1: 2PC (Blocking, strong consistency)
├─ Prepare: Lock both accounts
├─ Commit: Transfer atomically
└─ Risk: Deadlocks, slow

Option 2: Saga (Async, eventual consistency)
├─ Service A: Deduct from account
├─ Service B: Add to account
├─ Compensation: Reverse if B fails
└─ Risk: Temp inconsistency

Option 3: Event Sourcing
├─ Record: "Transfer initiated"
├─ Process: Deduct A, add B
├─ Audit: Full history
└─ Benefit: Replay, audit trail
```

---

**Last updated:** 2026-05-22
