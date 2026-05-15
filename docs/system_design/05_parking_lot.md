# Parking Lot System

## Problem Statement

Design a parking lot system with multiple levels, different spot sizes, and availability tracking.

**Requirements:**
- Multiple levels/floors
- Different vehicle types (compact, regular, large)
- Find available spot
- Parking/unparking
- Availability display

## Design

### Object Model

```
ParkingLot
  ├── Level[]
      ├── Spot[] (each marked by size, occupied status)
      └── availableSpots tracking

Vehicle types: COMPACT, REGULAR, LARGE (in increasing size)
Spot sizes: match vehicle types
```

### Key Classes

```
Vehicle: type, license_plate
Spot: number, level, size, occupied, parked_vehicle
Level: floor_number, spots[], available_counts
ParkingLot: levels, display()
```

### Find Available Spot Algorithm

```
for each level:
  for each spot in level:
    if spot.size >= vehicle.size and not occupied:
      return spot
return None  // No spot available
```

### State Tracking

```
For each spot size, track available count:
  available_compact = 3
  available_regular = 7
  available_large = 2

Update on park/unpark operations
```

## Complexity

| Operation | Time | Space |
|-----------|------|-------|
| findSpot | O(n) where n=total spots | O(1) |
| parkVehicle | O(1) | O(1) |
| unparkVehicle | O(1) | O(1) |
| getAvailability | O(1) | O(1) |
| Space | — | O(n) |

## Edge Cases

1. No spots available
2. Vehicle type larger than all available spots
3. Unpark from wrong spot
4. Multiple vehicles with same license plate
