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

## Complexity

| Operation | Time |
|-----------|------|
| Deposit | O(1) |
| Withdraw | O(1) |
| Transfer | O(1) |
| Check balance | O(1) |
