# Transaction Ledger

## Problem Statement
Design an immutable financial ledger for tracking all transactions.

**Requirements:**
- Append-only log
- Double-entry bookkeeping
- Audit trail
- Reconciliation

## Design

### Double-Entry Bookkeeping

```
Every transaction: Debit one account, Credit another
Sum(debits) = Sum(credits)
Immutable: Never update, append corrections
```

### Ledger Structure

```
Timestamp
From account
To account
Amount
Type (transfer, fee, etc.)
Reference (order_id, etc.)
Status (pending, confirmed)
```

### Settlement

```
Pending: Awaiting confirmation
Confirmed: Finalized
Reversed: Correction entry
Reconciliation: Match with external
```

### Integrity

```
Hash chain: Link entries
Signatures: Cryptographic proof
Read-only: Prevent tampering
```

## Complexity

| Operation | Time |
|-----------|------|
| Append | O(1) |
| Query | O(log n) |
| Reconcile | O(n) |
