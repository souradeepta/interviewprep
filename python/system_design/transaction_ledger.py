"""
Transaction Ledger Implementation
=================================

OVERVIEW:
This module provides a complete implementation of Transaction Ledger, a fundamental
data structure used in algorithms and system design.

PURPOSE & USE CASES:
- Core operation for many algorithm patterns
- Essential for interview preparation
- Real-world applications in production systems

KEY OPERATIONS:
- Time/Space complexity analysis included for each operation
- Design trade-offs explained
- Common pitfalls and edge cases documented

COMPLEXITY SUMMARY:
See individual class/function docstrings for detailed complexity analysis.

REFERENCES:
- Introduction to Algorithms (Cormen, Leiserson, Rivest, Stein)
- Algorithm Design Manual (Skiena)
- LeetCode and HackerRank problem patterns
"""

class LedgerEntry:
    """Represents a single transaction entry between two accounts."""

    def __init__(self, from_account, to_account, amount):
        """
        Initialize a ledger entry with from, to, and amount.

        Args:
            from_account: Source account identifier
            to_account: Destination account identifier
            amount: Transaction amount

        Time: O(1)
        Space: O(1)
        """
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount


class TransactionLedger:
    """Manages a collection of transaction entries and computes account balances."""

    def __init__(self):
        """Initialize empty ledger.

        Time: O(1)
        Space: O(1)
        """
        self.entries = []

    def append(self, from_account, to_account, amount):
        """
        Add a new transaction to the ledger.

        Args:
            from_account: Source account identifier
            to_account: Destination account identifier
            amount: Transaction amount

        Time: O(1)
        Space: O(1)
        """
        entry = LedgerEntry(from_account, to_account, amount)
        self.entries.append(entry)

    def get_balance(self, account):
        """
        Calculate net balance for an account.

        Sums all credits (where account is destination) minus debits (where
        account is source). Net positive balance means account has received
        more than it has sent.

        Args:
            account: Account identifier to calculate balance for

        Returns:
            Net balance (credits - debits)

        Time: O(n) where n is number of transactions
        Space: O(1)
        """
        debits = sum(e.amount for e in self.entries if e.from_account == account)
        credits = sum(e.amount for e in self.entries if e.to_account == account)
        return credits - debits


if __name__ == "__main__":
    # Example: Create ledger, add transaction, check balance
    ledger = TransactionLedger()
    ledger.append(1, 2, 100)  # Account 1 sends 100 to account 2
    print(ledger.get_balance(2))  # Output: 100 (account 2 received 100)