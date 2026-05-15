# Facade Pattern

## Overview
Provides unified simplified interface to complex subsystem.

## Problem Statement
Subsystem complex with many interdependent classes. Clients need simple way to use subsystem.

## Solution
Create facade providing simple interface. Facade delegates to subsystem classes.

## When to Use

**Use Facade when:**
- Subsystem complex, need simplified interface
- Decouple clients from subsystem classes
- Layering subsystems (provide interface per layer)
- Simplify dependency graph

**Examples:**
- Order processing system (hide complex order/payment/shipping logic)
- Build system (hide compiler, linker, optimizer details)
- Database abstraction layer (hide SQL details)
- HTTP client library (hide connection pooling, retry logic)

## Real-World Scenarios

**Order Processing Facade:**
```
CreateOrderFacade:
  - Validate order
  - Reserve inventory
  - Process payment
  - Create shipment
Clients just call: createOrder(orderData)
Don't know about all the steps
```

**Library API Facade:**
```
Compiler internals complex
Scanner, Parser, Optimizer, CodeGenerator all interdependent
CompilerFacade.compile(source) → object
Clients use simple interface
```

## Implementation Patterns

### Simplified Interface
```python
class ComplexSubsystemA:
    def complex_operation_1(self):
        return "A1"

class ComplexSubsystemB:
    def complex_operation_2(self):
        return "B2"

class Facade:
    def __init__(self):
        self.subsystem_a = ComplexSubsystemA()
        self.subsystem_b = ComplexSubsystemB()

    def simple_operation(self):
        # Hide complex coordination
        result = self.subsystem_a.complex_operation_1()
        result += " " + self.subsystem_b.complex_operation_2()
        return result

# Usage
facade = Facade()
print(facade.simple_operation())  # Simple interface hides complexity
```

## Trade-Offs

**Pros:**
- Simplifies complex subsystems
- Decouples clients from subsystem
- Single entry point (easier to understand)
- Easier testing (mock facade)

**Cons:**
- Facade becomes dumping ground (too many methods)
- Hides useful subsystem details sometimes
- Not all clients need simplified interface
- Extra layer (indirection, performance)

## Production Considerations

- Keep facade focused (one responsibility)
- Don't add methods that don't relate to subsystem
- Consider multiple facades for different client groups
- Document what facade hides
- Version facade carefully (clients depend on interface)
