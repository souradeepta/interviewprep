# Adapter Pattern

## Problem Statement

Convert the interface of a class into another interface clients expect. Adapter lets classes work together that couldn't otherwise because of incompatible interfaces.

**Use Cases:**
- Third-party library integration
- Legacy code integration
- Interface translation (USB-C to USB-A adapter)
- Incompatible libraries/APIs

## Design

### Class Diagram

```
        Client (expects Target interface)
             │
             ├─→ Adapter
                    │
                    └─→ delegates to Adaptee
```

### Key Components

```
Target: Interface client expects
Adapter: Implements Target, wraps Adaptee
Adaptee: Existing interface to adapt
Client: Uses Adapter through Target interface
```

### Adapter Implementation

```
class Adapter implements Target {
  private Adaptee adaptee;
  
  public void targetMethod() {
    // Translate to Adaptee's interface
    adaptee.adapteeMethod();
  }
}
```

## Types

```
Class Adapter: Uses inheritance (less flexible)
Object Adapter: Uses composition (more flexible) - preferred
```

## Trade-offs

| Pro | Con |
|-----|-----|
| Makes incompatible work | Extra indirection |
| Single Responsibility | May require multiple adapters |
| Open/Closed principle | Complexity |
| Reuses existing code | Don't overuse |

## Complexity

| Operation | Time |
|-----------|------|
| adapt | O(1) |
| delegate | O(1) |
