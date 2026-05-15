# Decorator Pattern

## Overview
Attaches additional responsibilities to object dynamically. Provides flexible alternative to subclassing.

## Problem Statement
Need to add features to objects, but subclassing causes class explosion. Want to stack features (multiple decorators on one object).

## Solution
Create decorator wrapping original object. Decorator has same interface. Adds functionality before/after delegating.

## When to Use

**Use Decorator when:**
- Add features dynamically without subclassing
- Features combinable (stack multiple decorators)
- Avoid class explosion (many subclasses)
- Object identity important (wrapped object still accessible)

**Examples:**
- I/O streams with compression and encryption
- UI components with scrolling, borders, shadows
- Logging and caching wrappers around functions
- Cost calculation (base + decorators add features)

## Real-World Scenarios

**Stream Decoration:**
```
FileInputStream reads from file
Add BufferedInputStream (buffering)
Add CompressInputStream (decompression)
Add EncryptedInputStream (decryption)
Stack decorators: file -> encrypted -> compressed -> buffered
```

**UI Decoration:**
```
Button base
Add BorderDecorator (adds border)
Add ShadowDecorator (adds shadow)
Button with border and shadow
```

## Implementation Patterns

### Decorator Wrapper
```python
class Component:
    def operation(self):
        pass

class ConcreteComponent(Component):
    def operation(self):
        return "ConcreteComponent"

class Decorator(Component):
    def __init__(self, component):
        self.component = component

    def operation(self):
        return self.component.operation()

class ConcreteDecoratorA(Decorator):
    def operation(self):
        return f"DecoratorA({self.component.operation()})"

class ConcreteDecoratorB(Decorator):
    def operation(self):
        return f"DecoratorB({self.component.operation()})"

# Usage
obj = ConcreteComponent()
obj = ConcreteDecoratorA(obj)
obj = ConcreteDecoratorB(obj)
print(obj.operation())  # DecoratorB(DecoratorA(ConcreteComponent))
```

## Trade-Offs

**Pros:**
- Add features without subclassing
- Stack features (flexible combinations)
- Single responsibility (each decorator one feature)
- Runtime configuration (add features dynamically)

**Cons:**
- Many small objects (memory overhead)
- Ordering matters (decorators applied in order)
- Hard to remove decorator from middle of stack
- Extra indirection (performance)

## Production Considerations

- Use for cross-cutting concerns (logging, caching, security)
- Consider order of decorators (does it matter?)
- Document decorator stack (what decorators applied)
- Consider composition over deep nesting
- Test with different decorator combinations
