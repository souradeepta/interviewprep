# E-Commerce Platform

## Problem Statement
Design an e-commerce system handling product catalog, shopping cart, orders, and inventory management.

**Requirements:**
- Product search and filtering
- Shopping cart
- Order processing
- Inventory tracking
- Payment integration

## Design

### Components

```
Product Service: Catalog, search, filtering
Cart Service: User carts, quantities
Order Service: Order creation, history
Payment Service: Transaction processing
Inventory Service: Stock tracking, reservations
```

### Inventory Management

```
Reserve on add-to-cart
Release if cart abandoned (timeout)
Confirm on checkout
Reduce stock on order completion
```

### Order Processing Flow

```
1. Reserve inventory
2. Process payment
3. Create shipment
4. Update inventory
5. Confirm order
```


## Architecture Diagram

```
┌───────────────────────────────────────┐
│   E-commerce Platform                 │
│  ┌───────────────────────────────────┐  │
│  │ Product Catalog (Elasticsearch)   │  │
│  │ - 100M products, <100ms search    │  │
│  │ Shopping Cart (Redis, 24hr TTL)   │  │
│  │ - <10ms read/write                │  │
│  │ Order Processing                  │  │
│  │ - Inventory, Payment, Fulfill     │  │
│  └───────────────────────────────────┘  │
└───────────────────────────────────────────┘
```

## Common Questions & Answers

**Q: Inventory consistency?** A: Pessimistic lock or optimistic versioning. Use saga pattern for order flow.

**Q: Cart timeout?** A: TTL 24hr, notify before expiry. Recover from backup.

**Q: Product search scaling?** A: Elasticsearch cluster, shard by product_id, cache popular.

**Q: Payment failure recovery?** A: Retry + exponential backoff, webhook from gateway, saga rollback.

## Back-of-Envelope Calculations

10M SKUs, 1M concurrent users, 1K orders/sec. Cart: 1M × 500B = 500GB Redis. Search: 100K QPS ES cluster. Payment: 1K req/sec (3-4 gateways).

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Monolithic | Simple, consistent | Poor scaling |
| Microservices | Scalable, independent | Complex coordination |
| Event-driven | Decoupled, responsive | Harder to debug |

## Follow-up Interview Questions

1. Flash sales (millions orders/sec)? 2. Real-time inventory across regions? 3. Fraud detection in payments? 4. Payment gateway bottleneck. 5. Return/refund workflow?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

### Architecture Diagram

```mermaid
graph TB
    User["User"]
    ProductService["Product Service"]
    CartService["Cart Service"]
    PaymentService["Payment Service"]
    OrderService["Order Service"]

    User -->|Browse| ProductService
    User -->|Add to Cart| CartService
    User -->|Checkout| PaymentService
    PaymentService -->|Create| OrderService
```

### Flow Diagram

```mermaid
flowchart TD
    A["Browse Products"] --> B["Add to Cart"]
    B --> C["Checkout"]
    C --> D["Payment"]
    D --> E{Success?}
    E -->|Yes| F["Create Order"]
    E -->|No| G["Retry"]
    F --> H["Confirmation"]
```

## Complexity

| Operation | Time | Space |
|-----------|------|-------|
| Search products | O(log n) | O(1) |
| Add to cart | O(1) | O(1) |
| Checkout | O(1) | O(1) |
| Check inventory | O(1) | O(1) |
