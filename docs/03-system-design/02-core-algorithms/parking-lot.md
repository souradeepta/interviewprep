# Parking Lot

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement
Design an object-oriented system for a parking lot. A vehicle enters, is assigned a spot, and exits when done. This problem tests class hierarchy design, spot assignment algorithms, and extensibility. At L3-L4, the focus is clean OOP: right abstractions, single-responsibility classes, and correct polymorphism. At L5+, the problem extends to a multi-lot system with real-time availability APIs, dynamic pricing, reservation systems, and high-frequency availability queries across 10,000+ spots.

## Functional Requirements
- Support multiple vehicle types: motorcycle, car, truck/bus
- Multiple spot types: compact, regular, large
- Vehicle enters: find nearest available compatible spot, issue ticket
- Vehicle exits: calculate fee based on duration, mark spot available
- Display real-time availability per floor/spot type
- Support reserved spots and monthly passes
- Operator can add/remove spots dynamically

## Non-Functional Requirements
- **Scale:** 500-spot single lot (L3-L4); 100-lot, 500K spots system (L5+)
- **Latency:** Spot lookup < 50 ms; availability display < 100 ms
- **Availability:** 99.9% for single lot; 99.99% for multi-lot SaaS
- **Consistency:** strong — double-booking a spot is unacceptable

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope
```
Single lot:
  - 500 spots × 5 floors = 2,500 spots total
  - Spot state: {available, occupied, reserved, maintenance} = 2 bits
  - Ticket data: spot_id + vehicle_plate + entry_time = ~50 bytes
  - Max concurrent tickets: 2,500 × 50 bytes = 125 KB — trivial

Find-nearest-spot time:
  - Linear scan: O(N) = O(2,500) = negligible (<< 1 ms)
  - Optimized: O(1) with per-type queues (maintain free lists)

Fee calculation:
  - hourly rate × ceil(duration_hours) + flat entry fee
  - Most complex: overnight/multi-day pricing, grace periods
```

### Architecture Diagram
```
  ┌─────────────────────────────────────────────────────────┐
  │                    ParkingLot                            │
  │                                                          │
  │  floors: List[Floor]                                     │
  │  available_spots: Dict[SpotType → Queue[Spot]]  ← O(1)  │
  │  active_tickets: Dict[plate → Ticket]                    │
  │  pricing: PricingStrategy                                │
  │                                                          │
  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐ │
  │  │   Floor 1    │   │   Floor 2    │   │   Floor N    │ │
  │  │  spots: [..]  │   │  spots: [..] │   │  spots: [..] │ │
  │  └──────────────┘   └──────────────┘   └──────────────┘ │
  └─────────────────────────────────────────────────────────┘

Class hierarchy:
  Vehicle (abstract)
    ├── Motorcycle  (fits: compact, regular, large)
    ├── Car         (fits: regular, large)
    └── Truck       (fits: large only)

  Spot (abstract)
    ├── CompactSpot   (motorcycles only if needed, or cars)
    ├── RegularSpot   (cars, motorcycles)
    └── LargeSpot     (trucks, cars, motorcycles)

  Ticket
    └── ActiveTicket → PaidTicket → ClosedTicket

  PricingStrategy (interface)
    ├── HourlyPricing
    ├── DailyCapPricing
    └── MonthlyPassPricing
```

### Data Model
```python
# Enums
SpotType   = Enum("SpotType",   ["COMPACT", "REGULAR", "LARGE"])
SpotStatus = Enum("SpotStatus", ["AVAILABLE", "OCCUPIED", "RESERVED", "MAINTENANCE"])
VehicleType = Enum("VehicleType", ["MOTORCYCLE", "CAR", "TRUCK"])

# Compatibility matrix (vehicle → acceptable spot types)
VEHICLE_SPOT_COMPATIBILITY = {
    VehicleType.MOTORCYCLE: [SpotType.COMPACT, SpotType.REGULAR, SpotType.LARGE],
    VehicleType.CAR:        [SpotType.REGULAR, SpotType.LARGE],
    VehicleType.TRUCK:      [SpotType.LARGE],
}

# Ticket
Ticket:
  ticket_id:  str (UUID)
  plate:      str
  spot:       Spot reference
  entry_time: datetime
  exit_time:  datetime | None
  fee:        Decimal | None
```

### API Design
```
park(vehicle) → Ticket | None
  - Find best available spot for vehicle type
  - Mark spot OCCUPIED
  - Create and return Ticket

exit(ticket_id) → Receipt
  - Calculate fee
  - Mark spot AVAILABLE
  - Return Receipt with fee breakdown

get_availability() → Dict[SpotType → int]
  - Return count of available spots per type

find_spot(vehicle) → Spot | None
  - Find nearest/best spot without reserving
  - Used for display/estimation
```

### Basic Scaling
- **Free list queues:** maintain `Dict[SpotType → deque[Spot]]` — O(1) assignment and release
- **Floor preference:** prefer ground floor for accessibility; sorted free list by (floor, spot_number)
- **Concurrent entry:** threading lock per spot assignment (fine-grained locking)
- **Persistence:** serialize to JSON on each state change for single-lot simplicity

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)
```
Multi-lot SaaS (100 lots, 500 spots each = 50K spots total):
  - Peak occupancy: 80% = 40K occupied spots
  - Availability queries: 100K/sec (mobile app polling, digital signs)
  - Entry/exit events: 10K/hour = 2.8 events/sec (low write rate)

DB sizing:
  - Spot state: 50K spots × 100 bytes = 5 MB (fits entirely in Redis)
  - Historical tickets: 50K spots × 20 turns/day × 100 bytes = 100 MB/day → 36 GB/year
  - DB: PostgreSQL (tickets, lots, pricing); Redis (real-time spot state)

API server sizing:
  - 100K availability queries/sec → 10 servers at 10K req/sec each
  - Entry/exit: 3 events/sec → single server is fine; scale for HA only
```

### Failure Modes
```
Double-booking (concurrent entry):
  - Two vehicles arrive simultaneously; both are assigned same spot
  - Fix: DB optimistic locking (version column + conditional UPDATE)
    UPDATE spots SET status='OCCUPIED', version=v+1
    WHERE spot_id=X AND status='AVAILABLE' AND version=v
  - Retry: if update returns 0 rows, find another spot
  - Fix: Redis SETNX for distributed lock: SET spot:{id} plate NX EX 30

Spot sensor failure (IoT):
  - Physical sensor reports spot available, but car is there (stuck sensor)
  - Manual override: attendant can mark spot via admin UI
  - Heartbeat: sensors send status every 30s; if silent 5 min → alert + manual mode

Payment system down:
  - Barrier still opens (fail-open) — don't trap cars for payment failure
  - Record debt in local DB; retry payment asynchronously
  - Grace period: 7 days to pay before license plate flagged

Lot controller crash (edge node):
  - Edge controller manages 500 spots locally
  - On crash: failover to cloud controller (slower but operational)
  - State recovery: last known spot states from DB + sensor re-scan on restart
```

### Consistency Boundaries
```
Spot assignment (strong consistency):
  - Only one transaction can claim a spot
  - PostgreSQL: SELECT FOR UPDATE + UPDATE in same transaction
  - Redis: Lua script for atomic check-and-set

Availability display (eventual OK):
  - Cache spot availability in Redis with 5-second TTL
  - Mobile app shows "~47 spots available" (approximate is fine)
  - Exact count on entry gate display (bypass cache)

Pricing (strong consistency for billing):
  - Fee calculation at exit must use entry_time from DB (not cache)
  - No rounding until final display; use Decimal throughout
  - Receipt is immutable after generation

Reservations (strong + time-bound):
  - Reserved spot held for 15 minutes after scheduled time
  - After grace period: release to walk-in pool automatically
  - Reservation state machine: PENDING → CONFIRMED → ACTIVE → COMPLETED | EXPIRED
```

### Cost Model
```
Single-lot system (self-hosted):
  - 1× small EC2 (t3.medium): $0.05/hr = $36/mo
  - 1× RDS PostgreSQL (db.t3.small): $0.034/hr = $24/mo
  - Total: ~$60/mo

100-lot SaaS platform:
  - 10× app servers (c5.xlarge): $0.17/hr × 10 = $1,224/mo
  - 1× Redis (r6g.large, 13 GB): $108/mo
  - 1× PostgreSQL (db.r5.xlarge): $0.48/hr = $346/mo
  - Total: ~$1,678/mo = $16.78/lot/month
  - Revenue at $100/lot/month: 6× margin
```

---

## Trade-off Comparison

| Spot Assignment Strategy | Time | Best For |
|--------------------------|------|----------|
| Linear scan | O(N) | < 100 spots, simple |
| Free list per type (deque) | O(1) | All sizes, recommended |
| Min-heap by distance | O(log N) | Minimize walking distance |
| Floor-first sorted free list | O(1) | Ground-floor preference |
| Reservation + walk-in split | O(1) each | Large lots with reservations |

| Pricing Model | Complexity | Guest Experience | Revenue | Use When |
|---------------|------------|-----------------|---------|----------|
| Flat hourly | Low | Simple, predictable | Medium | Basic lots |
| Daily cap | Medium | Fair for long stays | High | Urban commuters |
| Dynamic (demand-based) | High | Unpredictable | Highest | Airports, events |
| Monthly pass | Low | Zero friction for regulars | Predictable | Office lots |
| Validation (merchant comped) | Medium | Discounted for customers | Indirect | Mall/retail |

---

## Follow-up Questions (5-10, escalating)

1. **(L3)** What are the main classes in a parking lot system?
   > ParkingLot, Floor, Spot (with subtypes), Vehicle (with subtypes), Ticket, PricingStrategy. Key insight: Spot and Vehicle are separate hierarchies connected by a compatibility matrix, not inheritance.

2. **(L3)** How do you find the nearest available spot efficiently?
   > Maintain a `dict[SpotType → deque[Spot]]` free list. `park(vehicle)` pops from the deque for the vehicle's required spot type — O(1). Add preferred ordering (ground floor first) by inserting in priority order.

3. **(L4)** Two cars arrive at the same time. How do you prevent double-booking?
   > DB: `SELECT FOR UPDATE` acquires row-level lock, then UPDATE; only one transaction succeeds. Redis: `SETNX spot:{id} {vehicle_plate}` is atomic; second caller gets 0 (spot taken). Application: retry with next available spot.

4. **(L4)** How would you add a reservation system that holds spots for 15 minutes?
   > Add `reserved_until: datetime` field to Spot. Reservation creates DB record + schedules expiry job (cron or Redis TTL). On `park()`: check `reserved_for == vehicle.plate` OR `reserved_until < now()`. Background job releases expired reservations every minute.

5. **(L4)** Design the fee calculation for a lot with hourly rates, daily caps, and overnight surcharges.
   > Strategy pattern: `PricingStrategy.calculate(entry_time, exit_time) → Decimal`. Implementations: `HourlyWithDailyCap` computes `min(hourly_rate × ceil(hours), daily_cap) × days`. `OvernightSurcharge` adds flat fee if duration spans midnight. Compose via `CompositePricing([HourlyWithDailyCap(), OvernightSurcharge()])`.

6. **(L5)** Design a multi-lot system where a user can find the nearest lot with available spots.
   > Each lot exposes availability via REST/gRPC. Central availability aggregator polls all lots every 10s, stores in Redis as geohashed keys (GEOADD). Mobile app sends location → `GEORADIUS` returns nearest lots → filter by `available_spots > 0`. Updates pushed via WebSocket on entry/exit events. Eventual consistency: availability count may lag 10s — acceptable.

7. **(L5)** How do you implement dynamic pricing that increases rates during peak demand?
   > Demand metric: current_occupancy / total_capacity. Price multiplier tiers: 0–50% → 1×, 50–75% → 1.5×, 75–90% → 2×, 90–100% → 3×. Computed every 5 minutes, stored in Redis. Displayed on entry gate before vehicle commits to park. Receipts store the rate locked at entry_time (fairness).

8. **(L5+)** Design the IoT sensor integration for 50K physical parking sensors updating spot state in real time.
   > Each sensor sends MQTT message on state change to edge controller (Raspberry Pi per floor). Edge controller batches updates every 100ms → publishes to cloud Kafka topic `spot-events`. Consumer updates Redis spot state (O(1) per spot). Sensor health: heartbeat every 30s; alert if silent > 3 min. False positive handling: require 2 consecutive state changes to update DB (debounce). Total event rate: 50K spots × 2 events/spot/day avg = ~1.2 events/sec — very low load.

---

## Anti-patterns / Things NOT to Say

- **"I'll make Spot a subclass of Vehicle"** — wrong inheritance; they're independent hierarchies related by compatibility, not is-a relationship.
- **"I'll scan all spots every time someone parks"** — O(N) is fine for 100 spots but shows lack of thinking; mention free list queues.
- **"ParkingLot is a singleton"** — Singleton pattern makes unit testing hard and multi-lot systems impossible; use dependency injection.
- **"I'll use a global variable for pricing"** — pricing changes per lot, per time of day, per spot type; inject PricingStrategy as a dependency.
- **Not handling the case where the lot is full** — `park()` must return None or raise an exception with a clear message; forgetting this is a common bug.
- **Mutable ticket after payment** — tickets should be immutable once payment is finalized; use a new PaidTicket/Receipt object rather than modifying the original.

---

## Python Implementation

```python
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
from collections import deque
from typing import Optional
import uuid


# ── Enums ──────────────────────────────────────────────────────────────────

class VehicleType(Enum):
    MOTORCYCLE = auto()
    CAR        = auto()
    TRUCK      = auto()

class SpotType(Enum):
    COMPACT  = auto()
    REGULAR  = auto()
    LARGE    = auto()

class SpotStatus(Enum):
    AVAILABLE   = auto()
    OCCUPIED    = auto()
    RESERVED    = auto()
    MAINTENANCE = auto()


# ── Compatibility matrix ───────────────────────────────────────────────────

COMPATIBLE_SPOTS: dict[VehicleType, list[SpotType]] = {
    VehicleType.MOTORCYCLE: [SpotType.COMPACT, SpotType.REGULAR, SpotType.LARGE],
    VehicleType.CAR:        [SpotType.REGULAR, SpotType.LARGE],
    VehicleType.TRUCK:      [SpotType.LARGE],
}


# ── Core domain classes ────────────────────────────────────────────────────

@dataclass
class Vehicle:
    plate:        str
    vehicle_type: VehicleType

    def compatible_spot_types(self) -> list[SpotType]:
        return COMPATIBLE_SPOTS[self.vehicle_type]


@dataclass
class Spot:
    spot_id:   str
    floor:     int
    number:    int
    spot_type: SpotType
    status:    SpotStatus = SpotStatus.AVAILABLE

    def is_available(self) -> bool:
        return self.status == SpotStatus.AVAILABLE

    def assign(self) -> None:
        if not self.is_available():
            raise RuntimeError(f"Spot {self.spot_id} is not available")
        self.status = SpotStatus.OCCUPIED

    def release(self) -> None:
        self.status = SpotStatus.AVAILABLE

    def __repr__(self) -> str:
        return f"Spot({self.spot_id}, {self.spot_type.name}, {self.status.name})"


@dataclass
class Ticket:
    ticket_id:  str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    plate:      str = ""
    spot:       Optional[Spot] = None
    entry_time: datetime = field(default_factory=datetime.now)
    exit_time:  Optional[datetime] = None
    fee:        Optional[Decimal] = None

    def duration_hours(self) -> float:
        end = self.exit_time or datetime.now()
        return (end - self.entry_time).total_seconds() / 3600


# ── Pricing strategies ─────────────────────────────────────────────────────

class PricingStrategy:
    def calculate(self, ticket: Ticket) -> Decimal:
        raise NotImplementedError


class HourlyPricing(PricingStrategy):
    def __init__(self, rate_per_hour: Decimal, daily_cap: Optional[Decimal] = None):
        self.rate = rate_per_hour
        self.daily_cap = daily_cap

    def calculate(self, ticket: Ticket) -> Decimal:
        import math
        hours = ticket.duration_hours()
        days = math.ceil(hours / 24)
        remaining_hours = hours % 24
        fee = Decimal(days - 1) * (self.daily_cap or self.rate * 24)
        hourly_fee = self.rate * Decimal(str(math.ceil(remaining_hours or 24)))
        if self.daily_cap:
            hourly_fee = min(hourly_fee, self.daily_cap)
        return (fee + hourly_fee).quantize(Decimal("0.01"))


# ── Floor ──────────────────────────────────────────────────────────────────

class Floor:
    def __init__(self, floor_number: int):
        self.floor_number = floor_number
        self.spots: list[Spot] = []

    def add_spot(self, spot_type: SpotType, count: int = 1) -> None:
        for i in range(count):
            spot_id = f"F{self.floor_number}-{spot_type.name[0]}{len(self.spots)+1:03d}"
            self.spots.append(Spot(spot_id, self.floor_number, len(self.spots)+1, spot_type))


# ── Parking Lot ────────────────────────────────────────────────────────────

class ParkingLot:
    """
    O(1) spot assignment via per-type free queues.
    Thread-safety: add locking per queue for concurrent use.
    """

    def __init__(self, name: str, pricing: PricingStrategy):
        self.name = name
        self.pricing = pricing
        self.floors: list[Floor] = []
        # free_spots[spot_type] = deque of available spots (ordered by preference)
        self._free_spots: dict[SpotType, deque[Spot]] = {st: deque() for st in SpotType}
        self._tickets: dict[str, Ticket] = {}   # ticket_id → Ticket

    # ── Setup ──────────────────────────────────────────────────────────────

    def add_floor(self, floor: Floor) -> None:
        self.floors.append(floor)
        for spot in floor.spots:
            if spot.is_available():
                self._free_spots[spot.spot_type].append(spot)

    # ── Core operations ────────────────────────────────────────────────────

    def park(self, vehicle: Vehicle) -> Optional[Ticket]:
        """Find best available spot and issue a ticket. Returns None if lot full."""
        spot = self._find_spot(vehicle)
        if spot is None:
            return None
        spot.assign()
        ticket = Ticket(plate=vehicle.plate, spot=spot)
        self._tickets[ticket.ticket_id] = ticket
        return ticket

    def exit(self, ticket_id: str) -> dict:
        """Process exit: calculate fee, release spot, close ticket."""
        if ticket_id not in self._tickets:
            raise KeyError(f"Ticket {ticket_id} not found")
        ticket = self._tickets[ticket_id]
        if ticket.exit_time is not None:
            raise RuntimeError("Ticket already processed")
        ticket.exit_time = datetime.now()
        ticket.fee = self.pricing.calculate(ticket)
        ticket.spot.release()
        self._free_spots[ticket.spot.spot_type].appendleft(ticket.spot)  # return to front
        return {
            "ticket_id": ticket.ticket_id,
            "plate": ticket.plate,
            "spot": ticket.spot.spot_id,
            "duration_hours": round(ticket.duration_hours(), 2),
            "fee": float(ticket.fee),
        }

    def availability(self) -> dict[str, int]:
        return {st.name: len(q) for st, q in self._free_spots.items()}

    # ── Private ────────────────────────────────────────────────────────────

    def _find_spot(self, vehicle: Vehicle) -> Optional[Spot]:
        for spot_type in vehicle.compatible_spot_types():
            if self._free_spots[spot_type]:
                return self._free_spots[spot_type].popleft()
        return None


# ── Demo ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    pricing = HourlyPricing(rate_per_hour=Decimal("3.00"), daily_cap=Decimal("25.00"))
    lot = ParkingLot("Downtown Garage", pricing=pricing)

    # Setup: 2 floors
    f1 = Floor(1)
    f1.add_spot(SpotType.COMPACT,  count=5)
    f1.add_spot(SpotType.REGULAR,  count=10)
    f1.add_spot(SpotType.LARGE,    count=3)
    f2 = Floor(2)
    f2.add_spot(SpotType.REGULAR,  count=8)
    f2.add_spot(SpotType.LARGE,    count=4)
    lot.add_floor(f1)
    lot.add_floor(f2)

    print("Initial availability:", lot.availability())

    car  = Vehicle("ABC-123", VehicleType.CAR)
    moto = Vehicle("XYZ-999", VehicleType.MOTORCYCLE)
    semi = Vehicle("TRK-007", VehicleType.TRUCK)

    t1 = lot.park(car);  print(f"Car parked: {t1.ticket_id} → {t1.spot}")
    t2 = lot.park(moto); print(f"Moto parked: {t2.ticket_id} → {t2.spot}")
    t3 = lot.park(semi); print(f"Truck parked: {t3.ticket_id} → {t3.spot}")

    print("After parking:", lot.availability())

    # Simulate 2.5-hour stay
    from datetime import timedelta
    t1.entry_time = datetime.now() - timedelta(hours=2.5)
    receipt = lot.exit(t1.ticket_id)
    print(f"\nReceipt: {receipt}")
    print("After exit:", lot.availability())
```
