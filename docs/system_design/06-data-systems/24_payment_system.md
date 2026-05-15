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


## Scenario

Payment Processing System is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

## Users

- **Backend Engineers**: Responsible for implementing and maintaining this system component in production environments. They need to understand the architecture, trade-offs, failure modes, and operational considerations.
- **DevOps/SRE Teams**: Monitor system health, manage scaling policies, handle incidents, and ensure reliability SLAs are met. They need insights into performance characteristics, bottlenecks, and failure recovery mechanisms.
- **Data Engineers**: Design data pipelines and analytics around this system, requiring deep understanding of data flow, consistency guarantees, and throughput characteristics.
- **System Architects**: Make high-level architectural decisions that impact company infrastructure, requiring comprehensive understanding of capabilities, limitations, and scalability boundaries.
- **Security Teams**: Understand security implications, potential vulnerabilities, and compliance requirements for this component.

## PRD

**Functional Requirements:**
- Correct behavior under all specified operating conditions
- Reliable operation with explicit failure modes
- Data consistency or eventual consistency guarantees as specified
- Clear mechanisms for error handling and recovery
- Monitoring and observability hooks

**Non-Functional Requirements:**
- **Performance**: Sub-100ms P99 latency for standard operations; measure and track tail latencies
- **Availability**: 99.99%+ uptime with automatic failover and graceful degradation
- **Scalability**: Support 10-100x current load with minimal architectural modifications
- **Consistency**: Specify whether strong, eventual, or causal consistency is required
- **Cost Efficiency**: Minimize operational cost per unit of throughput; consider compute, memory, and network costs
- **Operational Simplicity**: Reduce complexity to minimize human error and operational toil

**Constraints:**
- Resource limits (memory for caches, disk for databases, network bandwidth)
- Deployment constraints (cloud provider limits, regulatory requirements)
- Latency budgets (maximum acceptable delay for operations)

## Flow

The typical operational flow for this system involves these key phases:

1. **Request Arrival**: Client/upstream system sends request with required parameters and context
2. **Validation & Routing**: System validates request format, authentication, and routes to correct handler/shard/instance
3. **Core Processing**: Execute the main algorithm, database query, or business logic on the data/state
4. **State Management**: Update internal state (caches, indexes, counters, logs) with proper atomicity and locking
5. **Response Generation**: Format results and return to requester with relevant metadata (timing, version info)
6. **Observability**: Record metrics (latency, throughput, errors), logs (for debugging), and traces (for performance analysis)

This flow repeats thousands or millions of times per second in production. Each operation's efficiency compounds across the entire system, making careful optimization essential. Bottlenecks at any phase can cascade to impact overall system performance.

## Code Explanation

The provided implementations demonstrate key architectural concepts and design patterns:

**Python Implementation**: Uses built-in Python structures and standard library features to express the core logic clearly. Python emphasizes readability and conciseness—each operation's purpose should be obvious without extensive comments. You'll see different implementation approaches (e.g., using OrderedDict vs. manual linked lists) that represent trade-offs between convenience and fine-grained control.

**Java Implementation**: Shows how to implement the same logic with explicit memory management and type safety. Java's strong typing forces clear interface design; you'll see how generics, null safety, mutable state, and thread safety are handled. This implementation style is closer to production systems at scale.

**Key Implementation Patterns**:
- **Initialization**: Setting up core data structures, thread pools, or connection pools with specified capacity and configuration
- **Read Operations**: Fetching data while maintaining O(1) or O(log n) access, updating metadata (access times, hit counts, etc.)
- **Write Operations**: Inserting/updating data while handling eviction policies, balancing tree structures, or replicating state
- **Edge Cases**: Handling capacity limits, concurrent access, data consistency, and error conditions
- **Performance Optimization**: Using techniques like batch operations, lazy evaluation, or caching to reduce latency

Each line of code represents a deliberate choice about performance characteristics, memory usage, safety guarantees, and implementation complexity. Understanding these trade-offs is essential for using this component effectively in production systems.

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

### Architecture Diagram

```mermaid
graph TB
    User["User"]
    PaymentGateway["Payment Gateway"]
    Processor["Processor"]
    Bank["Bank"]
    Ledger["Ledger"]

    User -->|Payment| PaymentGateway
    PaymentGateway -->|Process| Processor
    Processor -->|Authorize| Bank
    PaymentGateway -->|Log| Ledger
```

### Flow Diagram

```mermaid
stateDiagram-v2
    [*] --> Initiated
    Initiated --> Validating
    Validating --> Authorized: Valid
    Authorized --> Captured
    Captured --> Settled: Success
    Captured --> Failed
    Settled --> [*]
    Failed --> [*]
```

## Complexity

| Operation | Time |
|-----------|------|
| Process payment | O(network) |
| Confirm | O(1) DB |
| Retry | Exponential backoff |

## Python Implementation

```python
from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum
from decimal import Decimal
import uuid

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

@dataclass
class Payment:
    payment_id: str
    user_id: str
    amount: Decimal
    currency: str
    status: PaymentStatus = PaymentStatus.PENDING

class PaymentService:
    def __init__(self):
        self._payments: Dict[str, Payment] = {}
        self._balances: Dict[str, Decimal] = {}

    def deposit(self, user_id: str, amount: Decimal):
        self._balances[user_id] = self._balances.get(user_id, Decimal(0)) + amount

    def process_payment(self, user_id: str, amount: Decimal, currency: str) -> Payment:
        payment_id = str(uuid.uuid4())[:8]
        payment = Payment(payment_id, user_id, amount, currency)
        balance = self._balances.get(user_id, Decimal(0))
        if balance >= amount:
            self._balances[user_id] = balance - amount
            payment.status = PaymentStatus.COMPLETED
        else:
            payment.status = PaymentStatus.FAILED
        self._payments[payment_id] = payment
        return payment

    def refund(self, payment_id: str) -> bool:
        payment = self._payments.get(payment_id)
        if payment and payment.status == PaymentStatus.COMPLETED:
            self._balances[payment.user_id] = self._balances.get(payment.user_id, Decimal(0)) + payment.amount
            payment.status = PaymentStatus.REFUNDED
            return True
        return False

# Usage
svc = PaymentService()
svc.deposit("user1", Decimal("100.00"))
p = svc.process_payment("user1", Decimal("25.00"), "USD")
print(p.status, p.amount)  # PaymentStatus.COMPLETED 25.00
```

## Java Implementation

```java
import java.math.BigDecimal;
import java.util.*;

public class PaymentService {
    enum Status { PENDING, COMPLETED, FAILED, REFUNDED }
    record Payment(String id, String userId, BigDecimal amount, Status status) {}

    private Map<String, BigDecimal> balances = new HashMap<>();
    private Map<String, Payment> payments = new HashMap<>();

    public void deposit(String userId, BigDecimal amount) {
        balances.merge(userId, amount, BigDecimal::add);
    }

    public Payment processPayment(String userId, BigDecimal amount) {
        String id = UUID.randomUUID().toString().substring(0, 8);
        BigDecimal balance = balances.getOrDefault(userId, BigDecimal.ZERO);
        Status status = balance.compareTo(amount) >= 0 ? Status.COMPLETED : Status.FAILED;
        if (status == Status.COMPLETED)
            balances.put(userId, balance.subtract(amount));
        Payment p = new Payment(id, userId, amount, status);
        payments.put(id, p);
        return p;
    }
}
```
