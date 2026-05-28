# Microservices Architecture: Design and Implementation Patterns

**Level:** L5
**Time to read:** ~20 min

Master microservices design for scalable, maintainable systems.

---

## Microservices Definition

Breaking monolith into independently deployable services.

```
Monolith:
┌─────────────────────────────────┐
│ User Service │ Order Service    │
│ Payment      │ Notification     │
└─────────────────────────────────┘
Shared DB, single deployment

Microservices:
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ User Service │  │ Order Service│  │ Payment      │
│ (DB1)        │  │ (DB2)        │  │ (DB3)        │
└──────────────┘  └──────────────┘  └──────────────┘
Independent deployment, separate data stores
```

---

## Service Boundaries

### How to Split?

**✓ Good boundaries:**
- User service: User profiles, auth, preferences
- Order service: Orders, checkout flow
- Payment service: Payment processing, refunds
- Notification service: Email, SMS, push

**✗ Bad boundaries:**
- User DB query service (too fine-grained)
- Utility service (shared functions, increases coupling)
- One service per function (excessive overhead)

---

## Communication Patterns

### Synchronous (Request-Reply)

```python
# Service A calls Service B directly
class OrderService:
    def __init__(self, payment_service):
        self.payment_service = payment_service
    
    def create_order(self, user_id, items):
        # Synchronously charge payment
        payment_result = self.payment_service.charge(user_id, total)
        if not payment_result.success:
            return {"error": "Payment failed"}
        
        return self.save_order(user_id, items)
```

**Pros:** Simple, immediate feedback
**Cons:** Tight coupling, cascading failures

### Asynchronous (Message Queue)

```python
# Service A publishes event, Service B listens
class OrderService:
    def create_order(self, user_id, items):
        order = self.save_order(user_id, items)
        # Publish event
        queue.publish("order.created", {"order_id": order.id, "user_id": user_id})
        return order

class PaymentService:
    def __init__(self, queue):
        queue.subscribe("order.created", self.on_order_created)
    
    def on_order_created(self, event):
        self.charge(event["user_id"], event["order_id"])
```

**Pros:** Loose coupling, resilient
**Cons:** Eventual consistency, harder to debug

---

## Data Management

### Database Per Service

```
User Service → User DB (PostgreSQL)
Order Service → Order DB (PostgreSQL)
Payment Service → Payment DB (MongoDB)
```

**Benefits:**
- Each service scales independently
- Different DB optimized per service

**Challenges:**
- No transactional joins across services
- Distributed transactions (saga pattern)

### Shared Database (Anti-pattern)

```
❌ All services → Shared DB
```

Problems:
- Strong coupling
- Can't scale services independently
- Schema changes break all services

---

## Handling Distributed Transactions

### Saga Pattern

```
Order Created
    ↓
[Order Service] publishes "OrderCreated"
    ↓
[Payment Service] charges → publishes "PaymentProcessed"
    ↓
[Shipping Service] ships → publishes "OrderShipped"
    ↓
[Notification Service] notifies user

If Payment fails:
[Payment Service] publishes "PaymentFailed"
    ↓
[Order Service] publishes "OrderCancelled" (compensation)
    ↓
[Shipping Service] cancels shipment
```

---

## Service Discovery

### How do services find each other?

**Hardcoding (Bad):**
```python
payment_service = PaymentService("192.168.1.5:8080")  # ❌ Breaks if IP changes
```

**Service Registry (Good):**
```python
registry = ServiceRegistry("consul://localhost:8500")
payment_service_url = registry.lookup("payment-service")  # ✓ Dynamic
```

---

## Deployment Patterns

### Blue-Green Deployment

```
Current (Blue)  → Serve traffic
New (Green)     → Test
Switch traffic to Green when ready
Keep Blue for quick rollback
```

### Canary Deployment

```
1% traffic → New version (canary)
Monitor error rate, latency
If OK: 10% → 50% → 100%
If not: rollback immediately
```

---

## Challenges & Solutions

| Challenge | Solution |
|-----------|----------|
| **Network latency** | Cache results, batch requests |
| **Service failure** | Circuit breaker, fallback, timeout |
| **Distributed tracing** | Correlation IDs, trace headers |
| **Data consistency** | Eventual consistency, saga pattern |
| **Operational complexity** | Container orchestration (K8s), monitoring |

---

## Microservices Checklist

- ✓ Service boundaries based on business domains
- ✓ Each service has own data store
- ✓ Communication via API/queue (not shared DB)
- ✓ Service discovery mechanism
- ✓ Distributed tracing with correlation IDs
- ✓ Circuit breaker for service failures
- ✓ Saga pattern for distributed transactions
- ✓ Monitoring and observability
- ✓ Container-based deployment (Docker)
- ✓ Auto-scaling per service

