# Wallet System

## Problem Statement
Design an e-wallet for storing and transferring money.

**Operations:**
- `deposit(user_id, amount)` — Add money
- `withdraw(user_id, amount)` — Remove money
- `transfer(from_id, to_id, amount)` — Transfer
- `getBalance(user_id)` — Check balance

## Design

### Balance Tracking

```
Current balance: User's account
Transaction ledger: Immutable log
Reconciliation: Daily settlement
```

### Consistency Guarantees

```
Serializable isolation: All transactions ordered
Atomic operations: All-or-nothing
Double-entry bookkeeping: Debit = Credit
```

### Currency Exchange

```
Exchange rate cache (hourly refresh)
Quote validity window (30s)
Lock rate during transaction
Settlement in base currency
```

### Disputes & Chargebacks

```
Transaction immutable
Reversal creates new transaction
Audit trail
Chargeback protection: Crypto signature
```


## Scenario

Wallet System is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
│   Digital Wallet              │
│  Account Balance              │
│  - Redis (real-time)          │
│  - DB (persistent, immutable) │
│  - Strongly consistent        │
│  Transaction Log              │
│  - Append-only, audit trail   │
│  Transfers & Settlement       │
│  - P2P (A to B)               │
│  - Atomic (all or nothing)    │
└───────────────────────────────┘
```

## Common Questions & Answers

**Q: Balance consistency?** A: Strong consistency: lock during update (safe). Eventual: optimistic lock (faster).

**Q: Negative balance?** A: Prevent (check before debit) or allow (overdraft limit, risky).

**Q: Lost txn recovery?** A: Write-ahead log, replay on restart. Idempotency prevents double-posting.

## Back-of-Envelope Calculations

100M users, $100 avg = $10B. Txns: 100K/sec. Balance updates: 100M × 8B = 800MB. Log: 100K/sec × 200B = 20MB/sec.
## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Redis | Fast, atomic | Limited capacity |
| DB | Persistent | Slower |
| Blockchain | Immutable | Slow |

## Follow-up Interview Questions

1. Concurrent deposits/withdrawals? 2. Loyalty points? 3. Wallet-to-bank transfers? 4. Settlement bottleneck? 5. Compliance audit?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

### Architecture Diagram

```mermaid
graph TB
    User["User"]
    Wallet["Wallet Service"]
    Balance["Balance"]
    Transaction["Transaction Log"]

    User -->|Add Funds| Wallet
    User -->|Spend| Wallet
    Wallet -->|Update| Balance
    Wallet -->|Record| Transaction
```

### Flow Diagram

```mermaid
flowchart TD
    A["User Action"] --> B{"Type?"}
    B -->|Add| C["Deposit"]
    B -->|Spend| D["Charge"]
    C --> E["Update Balance"]
    D --> E
    E --> F["Log Transaction"]
    F --> G["Return Status"]
```

## Complexity

| Operation | Time |
|-----------|------|
| Deposit | O(1) |
| Withdraw | O(1) |
| Transfer | O(1) |
| Check balance | O(1) |

## Python Implementation

```python
from dataclasses import dataclass
from typing import Dict, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

class TxnType(Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER = "transfer"

@dataclass
class Transaction:
    txn_id: str
    user_id: str
    amount: Decimal
    txn_type: TxnType
    timestamp: datetime = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()

class WalletService:
    def __init__(self):
        self._balances: Dict[str, Decimal] = {}
        self._history: Dict[str, List[Transaction]] = {}
        self._txn_count = 0

    def _new_txn_id(self) -> str:
        self._txn_count += 1
        return f"TXN-{self._txn_count}"

    def credit(self, user_id: str, amount: Decimal) -> Transaction:
        self._balances[user_id] = self._balances.get(user_id, Decimal(0)) + amount
        txn = Transaction(self._new_txn_id(), user_id, amount, TxnType.CREDIT)
        self._history.setdefault(user_id, []).append(txn)
        return txn

    def transfer(self, from_id: str, to_id: str, amount: Decimal) -> bool:
        if self._balances.get(from_id, Decimal(0)) < amount:
            return False
        self._balances[from_id] -= amount
        self._balances[to_id] = self._balances.get(to_id, Decimal(0)) + amount
        txn = Transaction(self._new_txn_id(), from_id, amount, TxnType.TRANSFER)
        self._history.setdefault(from_id, []).append(txn)
        return True

    def balance(self, user_id: str) -> Decimal:
        return self._balances.get(user_id, Decimal(0))

# Usage
wallet = WalletService()
wallet.credit("alice", Decimal("100"))
wallet.credit("bob", Decimal("50"))
wallet.transfer("alice", "bob", Decimal("30"))
print(wallet.balance("alice"), wallet.balance("bob"))  # 70 80
```

## Java Implementation

```java
import java.math.BigDecimal;
import java.util.*;

public class WalletService {
    private Map<String, BigDecimal> balances = new HashMap<>();
    private int txnCount = 0;

    public void credit(String userId, BigDecimal amount) {
        balances.merge(userId, amount, BigDecimal::add);
    }

    public boolean transfer(String from, String to, BigDecimal amount) {
        BigDecimal fromBal = balances.getOrDefault(from, BigDecimal.ZERO);
        if (fromBal.compareTo(amount) < 0) return false;
        balances.put(from, fromBal.subtract(amount));
        balances.merge(to, amount, BigDecimal::add);
        return true;
    }

    public BigDecimal balance(String userId) {
        return balances.getOrDefault(userId, BigDecimal.ZERO);
    }
}
```
