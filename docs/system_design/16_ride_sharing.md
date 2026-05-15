# Ride-Sharing System

## Problem Statement
Design an Uber-like system matching riders with drivers in real-time.

**Operations:**
- `requestRide(rider_location)` — Request ride
- `acceptRide(driver_id, ride_id)` — Driver accepts
- `updateLocation(user_id, location)` — Live location
- `completeRide(ride_id)` — Complete trip

## Design

### Matching Algorithm

```
Spatial indexing: Grid or quadtree
For rider request:
  1. Find nearby drivers (radius search)
  2. Calculate ETA
  3. Send offers
  4. Accept first responder
```

### Real-time Tracking

```
Pub-sub for location updates
WebSocket for live position
Redis for driver availability cache
```

### Payment

```
Calculate distance + time
Apply surge pricing
Process payment
Generate receipt
```

## Complexity

| Operation | Time |
|-----------|------|
| Find drivers | O(log n) |
| Calculate ETA | O(1) |
| Update location | O(1) |
| Complete ride | O(1) |
