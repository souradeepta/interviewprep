# Auction System

## Problem Statement
Design an auction platform with bidding, time management, and winner determination.

**Operations:**
- `createAuction(item, start_price, end_time)` — Create
- `placeBid(user_id, auction_id, amount)` — Bid
- `getHighestBid(auction_id)` — Current highest
- `finalizeAuction(auction_id)` — Determine winner

## Design

### Bid Validation

```
Amount > current highest
User not seller
Auction still active
User has sufficient funds
```

### Winner Selection

```
Highest bidder wins
Sealed-bid: Don't reveal other bids
Open-bid: Public bidding
Auto-bidding: Proxy bidder
```

### Settlement

```
Charge winner
Refund other bidders
Payment processing
Shipment generation
```

### Scalability

```
Auction sharding: By auction_id
Bid queue: Handle spikes
Real-time updates: WebSocket bids
```

## Complexity

| Operation | Time |
|-----------|------|
| Place bid | O(1) |
| Get highest | O(1) |
| Finalize | O(1) |
