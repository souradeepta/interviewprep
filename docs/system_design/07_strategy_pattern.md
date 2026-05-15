# Strategy Pattern

## Problem Statement

Define a family of algorithms, encapsulate each one, and make them interchangeable. Strategy lets the algorithm vary independently from clients.

**Use Cases:**
- Payment methods (credit card, PayPal, Bitcoin)
- Sorting algorithms (select at runtime)
- Compression algorithms (zip, gzip, bzip2)
- File parsing strategies

## Design

### Class Diagram

```
        Strategy (interface)
        ├── execute()
        │
    ┌───┴───┬──────┐
    │       │      │
ConcreteStrategyA/B/C (implement execute differently)

Context
  ├── strategy: Strategy
  └── executeStrategy()
```

### Key Components

```
Strategy: Interface defining algorithm operations
ConcreteStrategy: Implements specific algorithm
Context: Holds reference to Strategy, delegates work
```

### Pattern Flow

```
1. Create concrete strategies
2. Context holds reference to strategy
3. At runtime, switch strategies
4. Context delegates to strategy.execute()
```

## Trade-offs

| Pro | Con |
|-----|-----|
| Runtime algorithm switching | Increased classes |
| Open/Closed principle | Overhead if few strategies |
| Avoids conditionals | Context must know strategy interface |
| Easy testing | Extra indirection |

## Complexity

| Operation | Time |
|-----------|------|
| setStrategy | O(1) |
| execute | O(1) |
