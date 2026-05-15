# Factory Pattern

## Problem Statement

Define an interface for creating an object, but let subclasses decide which class to instantiate. Factory pattern lets a class defer instantiation.

**Use Cases:**
- Creating objects without specifying exact classes
- Database abstraction (MySQL, PostgreSQL factories)
- UI frameworks (button, dialog creation)
- Shape creation (circle, square, rectangle)

## Design

### Class Diagram

```
        Creator (Factory)
        └── create(): Product
             │
    ┌────────┴────────┐
    │                 │
ConcreteCreatorA    ConcreteCreatorB
  └── create()      └── create()
       ↓                 ↓
ProductA            ProductB
```

### Key Components

```
Product: Interface for objects created
ConcreteProduct: Concrete implementations
Creator: Interface declaring factory method
ConcreteCreator: Implements factory method returning specific product
```

### Factory Method

```
public Product create(String type) {
  if (type == "A") return new ConcreteProductA();
  if (type == "B") return new ConcreteProductB();
  return null;
}
```

## Trade-offs

| Pro | Con |
|-----|-----|
| Decouples creation | Extra classes |
| Centralizes logic | Conditionals in factory |
| Easy to extend | More complex |
| Follows OCP | Overhead for simple cases |

## Complexity

| Operation | Time |
|-----------|------|
| create | O(1) |
