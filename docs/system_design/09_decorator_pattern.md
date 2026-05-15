# Decorator Pattern

## Problem Statement

Attach additional responsibilities to an object dynamically. Decorators provide a flexible alternative to subclassing for extending functionality.

**Use Cases:**
- Adding features to UI components (scrollbar, border)
- I/O streams (BufferedInputStream, DataInputStream)
- Coffee ordering (add milk, sugar, whipped cream)
- Middleware/middleware chains

## Design

### Class Diagram

```
        Component (interface)
        ├── operation()
        │
        ├── ConcreteComponent (base)
        │
        └── Decorator (wraps Component)
            ├── operation() -> delegate + enhancement
            │
            ├── ConcreteDecoratorA
            └── ConcreteDecoratorB
```

### Key Components

```
Component: Interface defining operations
ConcreteComponent: Base object
Decorator: Implements Component, holds reference to Component
ConcreteDecorator: Adds functionality before/after delegation
```

### Wrapping Behavior

```
Component original = new ConcreteComponent();
Component decorated = new DecoratorA(original);
decorated = new DecoratorB(decorated);

decorated.operation():  // DecoratorB behavior + DecoratorA + Original
```

## Trade-offs

| Pro | Con |
|-----|-----|
| Dynamic composition | More objects |
| Avoids class explosion | Complex debugging |
| Open/Closed principle | Order matters |
| Single responsibility | Increased complexity |

## Complexity

| Operation | Time |
|-----------|------|
| decorate | O(1) |
| operation | O(n) where n=decorators |
