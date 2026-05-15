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

## Complexity

| Operation | Time | Space |
|-----------|------|-------|
| Search products | O(log n) | O(1) |
| Add to cart | O(1) | O(1) |
| Checkout | O(1) | O(1) |
| Check inventory | O(1) | O(1) |
