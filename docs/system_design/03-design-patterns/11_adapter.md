# Adapter Pattern

## Overview
Converts interface of class into another clients expect. Lets incompatible interfaces work together.

## Problem Statement
Have existing class with useful functionality but incompatible interface. Want to use it with existing code without modification.

## Solution
Create adapter that wraps incompatible class and exposes expected interface.

## When to Use

**Use Adapter when:**
- Integrate legacy code (incompatible interfaces)
- Use third-party library with different interface
- Make incompatible classes work together
- Avoid modifying existing code

**Examples:**
- Integrate legacy database driver with modern ORM interface
- Use different payment gateways with same interface
- Adapt old logging framework to new logging interface
- Convert XML parser to JSON parser interface

## Real-World Scenarios

**Legacy Payment Integration:**
```
Old payment system uses: process_payment(card_number, amount)
New system expects: PaymentProcessor.execute(PaymentRequest)
Create adapter wrapping old system to new interface.
New code uses modern interface, adapter calls legacy code.
```

**Database Driver Adapter:**
```
Old code uses specific database driver (MySQLDriver)
New code expects generic DatabaseConnection interface
Adapter wraps old driver, implements new interface
Allows using old driver with new code
```

## Implementation Patterns

### Class Adapter (Inheritance)
```python
class OldPaymentProcessor:
    def process_payment(self, card, amount):
        return f"Processed {amount} on {card}"

class PaymentRequest:
    def __init__(self, card, amount):
        self.card = card
        self.amount = amount

# Adapter
class PaymentAdapter(OldPaymentProcessor):
    def execute(self, request: PaymentRequest):
        return self.process_payment(request.card, request.amount)

# Usage
adapter = PaymentAdapter()
result = adapter.execute(PaymentRequest("1234", 100))
```

### Object Adapter (Composition)
```python
class PaymentAdapter:
    def __init__(self, old_processor):
        self.old_processor = old_processor

    def execute(self, request):
        return self.old_processor.process_payment(
            request.card, request.amount
        )

# Usage
old = OldPaymentProcessor()
adapter = PaymentAdapter(old)
result = adapter.execute(PaymentRequest("1234", 100))
```

## Trade-Offs

**Pros:**
- Use existing code without modification
- Single responsibility (adapter focused on conversion)
- Can adapt to multiple interfaces

**Cons:**
- Extra layer (indirection, complexity)
- May mask poor design (shouldn't need adapter)
- Composition vs. inheritance tradeoffs

## When NOT to Use

**Avoid when:**
- Can modify original class (refactor instead)
- Interface only used once (simpler solution)
- Adapter complex (rethink design)

## Production Considerations

- Name adapters clearly (OldXyz -> NewXyzAdapter)
- Keep adapter thin (minimal logic)
- Document what's being adapted (what was incompatible)
- Test adapter thoroughly (works with both interfaces)
