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

## Complexity

| Operation | Time |
|-----------|------|
| Deposit | O(1) |
| Withdraw | O(1) |
| Transfer | O(1) |
| Check balance | O(1) |
