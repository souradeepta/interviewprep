# Strategy Pattern

## Overview
Defines family of algorithms, encapsulates each, makes them interchangeable.

## Problem Statement
Multiple algorithms for same operation. Choice at runtime. Avoid giant if/else blocks.

## Solution
Define strategy interface. Concrete strategies implement algorithm. Context uses strategy.

## When to Use

**Use Strategy when:**
- Multiple algorithms for operation
- Choose algorithm at runtime
- Avoid conditional logic (if/else)
- Algorithms vary by context
- Want to avoid modifying context when algorithms change

**Examples:**
- Payment methods (credit card, PayPal, Apple Pay)
- Sorting algorithms (quicksort, mergesort, heapsort)
- Compression algorithms (gzip, bzip2, 7zip)
- Route planning (shortest, fastest, scenic)
- Caching strategies (LRU, LFU, TTL)

## Real-World Scenarios

**Payment Processing:**
```
PaymentStrategy interface: process_payment()
CreditCardStrategy: charges card
PayPalStrategy: redirects to PayPal
ApplePayStrategy: uses Apple Pay
Payment processor uses appropriate strategy
```

**Sorting:**
```
Strategy interface: sort(array)
QuickSort: partitions and sorts
MergeSort: divides and merges
HeapSort: builds heap and sorts
Caller doesn't know which, just calls sort()
```

## When NOT to Use

Avoid when: single algorithm, algorithm complex and varied.

## Implementation Patterns

### Strategy Example
```python
class PaymentStrategy:
    def pay(self, amount):
        pass

class CreditCardStrategy(PaymentStrategy):
    def pay(self, amount):
        return f"Charged ${amount} to credit card"

class PayPalStrategy(PaymentStrategy):
    def pay(self, amount):
        return f"Redirected to PayPal: ${amount}"

class PaymentProcessor:
    def __init__(self, strategy):
        self.strategy = strategy

    def process(self, amount):
        return self.strategy.pay(amount)

# Usage
processor = PaymentProcessor(CreditCardStrategy())
print(processor.process(100))  # Credit card

processor = PaymentProcessor(PayPalStrategy())
print(processor.process(100))  # PayPal
```

## Trade-Offs

**Pros:** Eliminate conditionals, easy to add strategies, runtime selection

**Cons:** Many strategy classes, overhead for few strategies

## Production Considerations

- Strategy registry (dynamically select strategies)
- Strategy composition (combine strategies)
- Performance comparison (benchmark strategies)
- Version strategies (evolve algorithm)
