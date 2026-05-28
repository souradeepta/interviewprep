# Ride-Sharing Platform

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

A ride-sharing platform like Uber or Lyft must match riders requesting trips with nearby available
drivers in real-time, track driver locations continuously, compute dynamic pricing, and manage the
full trip lifecycle from request through payment. The core engineering challenges are geospatial:
querying "which drivers are within 1km of this rider?" must work in milliseconds over millions of
moving data points.

This is a systems design problem that tests knowledge of geospatial indexing (geohash, S2 cells),
real-time location streaming, matching algorithms, and surge pricing. It is a favorite at Uber,
Lyft, DoorDash, and any company where geospatial + real-time coordination matters.

## Functional Requirements

- Drivers send location updates every 5 seconds while the app is active
- Riders request a ride from a given pickup location
- Platform matches rider to the nearest available driver within 30 seconds
- Compute and display ETA to pickup and destination
- Calculate fare based on distance + time + surge multiplier
- Manage trip lifecycle: requested → accepted → driver_en_route → in_progress → completed
- Riders and drivers can rate each other after trip completion

## Non-Functional Requirements

- **Scale:** 5M drivers active simultaneously; 10M rides/day; 1M location updates/sec from drivers
- **Latency:** Match found within 5s of request; location update ingestion P99 < 100ms
- **Availability:** 99.99%; location tracking must survive datacenter failures
- **Consistency:** Trip state machine is strongly consistent; driver location is eventually consistent (5s staleness acceptable)

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Location updates:
  5M drivers × 1 update/5s = 1M updates/sec
  Each update: { driver_id, lat, lon, timestamp } = 64 bytes
  1M × 64 bytes = 64 MB/sec write throughput

Ride requests:
  10M rides/day ÷ 86400 = 116 ride requests/sec average
  Peak (rush hour, 5× average): 580 ride requests/sec

Driver location storage:
  5M drivers × 64 bytes = 320 MB for all current driver locations (fits in Redis)
  Geospatial index: Redis GEOADD → stores as 52-bit geohash integer
  Query: GEORADIUS "drivers" <lon> <lat> 1000 m ASC COUNT 20 → returns 20 nearest drivers

Match rate:
  Typical city: drivers in a 1km radius = 5-50; pick nearest available
  If no driver in 1km, expand to 2km, then 5km (backoff search)

Trip data:
  10M rides/day × 365 × 3 years × 500 bytes = 5.5 TB
  Route points: 30-min average ride × 1 GPS point/5s = 360 points × 64 bytes = 23 KB/trip
  10M trips/day × 23KB = 230 GB/day of route data → store in S3, not RDBMS
```

### Architecture Diagram

```
[Driver App]                          [Rider App]
     │  (location update every 5s)          │  (request ride)
     │                                      │
     ▼                                      ▼
[Location Service]               [Ride Request Service]
  - Kafka (1M msgs/sec)            - Validate request
  - Consumer: update Redis         - Compute initial ETA
    GEOADD                         - Call matching service
     │                                      │
     ▼                                      ▼
[Redis Geo Cluster]              [Matching Service]
  - GEORADIUS queries               - GEORADIUS → candidate drivers
  - 5M driver positions             - Filter: available, right vehicle type
  - 320MB total                     - Rank: ETA model scoring
     │                              - Send offer to top driver
     │                              - Driver accepts/declines (30s timeout)
     ▼                                      │
[Driver State Service]                      ▼
  - AVAILABLE | BUSY | OFFLINE    [Trip Service (PostgreSQL)]
  - Redis hash: driver_id → state   - Trip lifecycle state machine
  - Updated on accept/complete      - Strong consistency via DB
                                    - Publishes events → Kafka

[ETA Service]
  - Road network graph (OSRM, or Google Maps API)
  - Computes driver-to-pickup ETA + pickup-to-destination ETA
  - Pre-cached for common city routes

[Pricing Service]
  - Base fare + per-mile + per-minute rates
  - Surge: (demand / supply) in geohash cell, smoothed over 5min
  - Communicates surge multiplier to rider before acceptance

[Payment Service]
  - Charge rider card on file after trip completion
  - Transfer to driver (minus platform fee) weekly
```

### Data Model

```sql
-- Drivers
CREATE TABLE drivers (
    driver_id   BIGINT PRIMARY KEY,
    name        VARCHAR(256),
    phone       VARCHAR(20),
    vehicle_id  BIGINT,
    rating      DECIMAL(3,2) DEFAULT 5.0,
    status      VARCHAR(20) DEFAULT 'offline'  -- offline|available|busy
);

-- Riders
CREATE TABLE riders (
    rider_id   BIGINT PRIMARY KEY,
    name       VARCHAR(256),
    phone      VARCHAR(20),
    rating     DECIMAL(3,2) DEFAULT 5.0,
    payment_method_id VARCHAR(64)
);

-- Trips (source of truth)
CREATE TABLE trips (
    trip_id       BIGINT PRIMARY KEY,
    rider_id      BIGINT NOT NULL,
    driver_id     BIGINT,                -- null until matched
    status        VARCHAR(30) NOT NULL,  -- requested|accepted|driver_en_route|in_progress|completed|cancelled
    pickup_lat    DECIMAL(10,7),
    pickup_lon    DECIMAL(10,7),
    dest_lat      DECIMAL(10,7),
    dest_lon      DECIMAL(10,7),
    fare_cents    INT,                   -- computed at completion
    surge_multiplier DECIMAL(4,2) DEFAULT 1.0,
    requested_at  TIMESTAMP DEFAULT NOW(),
    started_at    TIMESTAMP,
    completed_at  TIMESTAMP
);

-- Route points (S3 preferred; DB schema for reference)
CREATE TABLE trip_route_points (
    trip_id    BIGINT,
    seq        INT,
    lat        DECIMAL(10,7),
    lon        DECIMAL(10,7),
    recorded_at TIMESTAMP,
    PRIMARY KEY (trip_id, seq)
);

-- Redis (driver real-time state):
-- GEOADD drivers_geo <lon> <lat> <driver_id>   -- position
-- HSET driver_status:<driver_id> status available vehicle_type uberx
-- TTL driver_status:<driver_id> 30   -- expires if driver goes offline
```

### API Design

```
# Driver app
POST /v1/drivers/location
  Body: { "driver_id": "123", "lat": 37.7749, "lon": -122.4194, "bearing": 180 }
  Response: { "status": "ok" }

PUT  /v1/drivers/{id}/status    -- Body: { "status": "available" | "offline" }

# Rider app
POST /v1/rides/estimate
  Body: { "pickup": {"lat": 37.7749, "lon": -122.4194},
          "destination": {"lat": 37.7855, "lon": -122.4072} }
  Response: { "eta_sec": 240, "fare_estimate_cents": 1250, "surge_multiplier": 1.5 }

POST /v1/rides
  Body: { "pickup": {...}, "destination": {...}, "vehicle_type": "uberx" }
  Response: { "trip_id": "abc", "status": "requested", "driver_eta_sec": 180 }

GET  /v1/rides/{trip_id}
  Response: { "trip_id": "...", "status": "driver_en_route",
              "driver_location": {"lat": 37.77, "lon": -122.41},
              "driver_eta_sec": 120 }

POST /v1/rides/{trip_id}/cancel   -- rider cancels before pickup
POST /v1/rides/{trip_id}/rate     -- Body: { "rating": 5, "comment": "..." }
```

### Basic Scaling

- **Redis Geo for driver locations:** `GEOADD` + `GEORADIUS` on a Redis Geo sorted set. All 5M driver positions fit in ~320MB. `GEORADIUS` completes in O(N + log M) where N = results, M = total entries — typically < 1ms.
- **Kafka for location ingestion:** 1M updates/sec → Kafka topic partitioned by driver_id hash. Consumers update Redis. Kafka decouples ingestion from geospatial index updates.
- **Trip state machine in PostgreSQL:** Trip table has status column with valid transitions enforced in application code. PostgreSQL provides the ACID guarantee needed for strong consistency.
- **ETA caching:** Pre-compute ETAs for the top-100 most common routes in each city. Cache in Redis with 5-minute TTL. Real-time ETA for uncommon routes via OSRM or Google Maps Distance Matrix API.

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Location update pipeline:
  1M updates/sec → Kafka
  Kafka: 1M msgs/sec × 64 bytes = 64 MB/sec
  20 Kafka brokers handle this with headroom (each sustains ~50 MB/sec)
  Kafka consumers: 20 consumer instances, each updating Redis at 50K updates/sec
  Redis GEOADD throughput: single node ~100K ops/sec
  Redis cluster: 10 shards by geohash prefix → 10× throughput = 1M ops/sec

Geohash-based matching (city sharding):
  Divide world into geohash level-4 cells (~40km × 20km)
  Assign each cell to a Redis shard
  Matching query: GEORADIUS within the cell + adjacent cells
  Adjacent cells for 1km search: max 9 cells to check (3×3 grid around request point)
  Result: matching always hits the same 1-9 Redis shards regardless of scale

Surge pricing computation:
  Geohash level-7 cells (~150m × 150m) for fine-grained supply/demand
  Every 30s: count available drivers and pending requests per cell
  Surge = max(1.0, demand_count / supply_count) smoothed with EMA(α=0.3)
  Storage: 5M cells × 2 counts × 4 bytes = 40MB in Redis (trivial)
  Update: batch Kafka consumer aggregates counts every 30s

ETA model:
  Real-time features: driver speed/heading, traffic speed per road segment, time-of-day
  Road network: H3 hexagonal grid (Uber's library) for routing
  Inference: pre-trained gradient boosted model (LightGBM); ~1ms inference
  Features served from Redis (road speed per segment, updated every 60s from GPS traces)

Driver supply forecasting:
  ML model predicts driver availability 15-30 min ahead by city zone
  Used for: proactive driver incentives ("surge in 20min in downtown — head there now")
  Training data: historical GPS traces + weather + events calendar
  Inference: hourly batch job; results pushed to driver app as notifications
```

### Failure Modes

```
Scenario 1: Redis geo cluster node fails (driver location data lost for 1 shard)
  - 1/10 of driver locations become unavailable
  - Matching requests for that geohash area fail with "no drivers available"
  - Recovery: Redis Cluster auto-promotion of replica to leader (< 10s)
  - During 10s gap: matching service returns "no drivers" → rider retries → re-matched
  - Prevention: Redis AOF persistence + RDB snapshots; replica in different AZ

Scenario 2: Driver location update storm after app resume
  - 5M drivers simultaneously reconnect after a global push notification
  - 5M location updates arrive at once (vs 1M/sec steady state)
  - 5× spike overwhelms Kafka → producer gets timeout errors
  - Fix: Kafka producer has internal buffer (512MB); absorbs 5-10s bursts
  - Fix: exponential backoff + jitter on driver app reconnect
  - Fix: connection spreading: stagger reconnects by driver_id hash % 60 seconds

Scenario 3: Matching times out (no driver accepts in 30s)
  - Matching service sends offer to top driver; no response in 10s → next driver
  - After 3 attempts, expand search radius from 1km → 2km → 5km
  - After 30s total: ride request cancelled; rider notified; offer retry option
  - Monitoring: track "match rate" per city per hour; alert if < 80%

Scenario 4: Payment processing fails after trip completion
  - Trip marked "completed" but payment fails (card declined)
  - Driver already paid out (if immediate transfer model) or not yet
  - Fix: asynchronous payment with retry (3 attempts, 24h window)
  - Fix: driver payout after payment confirmation, not trip completion
  - Fix: offline payment fallback (cash) in markets where card failure is common

Scenario 5: GPS spoofing (driver fakes location to game surge pricing)
  - Driver reports location in high-surge area while physically elsewhere
  - Detection: speed check — if reported location implies >200 km/h travel → anomaly
  - Detection: beacon cross-check (WiFi/cell tower triangulation vs GPS)
  - Response: flag for manual review; temporary restriction from surge zones
```

### Consistency Boundaries

```
Driver location:
  Eventual consistency (5s staleness acceptable)
  Redis updated asynchronously via Kafka consumer
  Matching uses slightly stale locations — acceptable (driver moved <50m in 5s)

Trip state machine:
  Strong consistency required (rider and driver must see same trip state)
  All state transitions through PostgreSQL with optimistic locking
  State machine: requested → accepted → driver_en_route → in_progress → completed
  Each transition is a PostgreSQL UPDATE with WHERE status = 'previous_state'
  If transition fails (concurrent update), return current state to caller

Fare calculation:
  Strong consistency: fare computed from actual GPS trace at trip completion
  Immutable once computed (stored in trips.fare_cents)
  Surge multiplier locked at ride request time (shown to rider before acceptance)

Geohash-based matching consistency:
  Driver state can be stale by up to 30s (Redis TTL + Kafka lag)
  On offer sent, Matching Service calls Driver State Service to confirm driver still available
  This provides linearizability for the "match" action even if location is stale
```

### Cost Model

```
Infrastructure for 5M active drivers + 10M rides/day:

Kafka (location ingestion):
  20 brokers × m6i.4xlarge ($0.768/hr × 20) = $11,059/month
  Storage: 1M msgs/sec × 64 bytes × 86400s × 7day retention = 38.7 TB
  38.7TB × 3× replication = 116TB → 20 nodes × 6TB = feasible

Redis Geo cluster (driver locations):
  10 shards × 3 replicas = 30 Redis nodes
  r6g.xlarge (32GB) × 30 = $0.207/hr × 30 = $4,482/month

PostgreSQL (trips):
  Primary + 2 replicas: db.r6g.4xlarge = $0.960/hr × 3 = $2,074/month
  5.5 TB over 3 years → $0.115/GB/month (Aurora gp3) = $633/month

Matching + ETA services:
  30 × c6i.2xlarge ($0.340/hr × 30) = $7,344/month

Surge + analytics (Kafka Streams):
  5 × m6i.2xlarge = $0.384/hr × 5 = $1,382/month

Route storage (S3):
  230 GB/day × 90 days × $0.023/GB = $477/month

Total: ~$27K/month core infrastructure
Per-ride cost: 10M rides/day × 30 = 300M rides/month
  $27,000 / 300M = $0.00009/ride (infrastructure only, not including maps API costs)
Dominant cost: Kafka (location ingestion) — optimize by reducing update frequency when idle
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **Redis GEORADIUS** | Sub-ms query, simple, 320MB for 5M drivers | No persistence, single data structure per cluster, geographic boundary issues | Real-time driver matching (primary choice) |
| **PostgreSQL PostGIS** | SQL joins (driver + status), persistent, complex queries | Higher latency (5-20ms), harder to scale writes for 1M updates/sec | Offline analytics, historical trip queries |
| **S2 geometry (Google)** | Hierarchical cells, accurate area computation, used by Google Maps | Complex library, not built into standard datastores | Global routing, complex polygon queries |
| **H3 (Uber)** | Hexagonal grids (uniform neighbors), good for aggregation/surge | ~10% area distortion at poles, newer library | Surge pricing, supply/demand aggregation per zone |
| **Quadtree** | Variable-resolution, efficient for sparse areas | Complex to shard/update dynamically, re-balance on data skew | Game engines, map tile rendering |

## Follow-up Questions (escalating difficulty)

1. **(L3)** Why is a geospatial index needed instead of just querying all drivers by lat/lon?
   → A query like `WHERE ABS(lat - rider_lat) < 0.01 AND ABS(lon - rider_lon) < 0.01` requires a full table scan without an index. With 5M drivers, that's 5M rows scanned per match request. A geospatial index (Redis GEORADIUS or PostGIS) limits the search to drivers in the relevant spatial cell — O(log N + K) instead of O(N).

2. **(L3)** What is geohash and how does it enable proximity queries?
   → Geohash encodes a (lat, lon) coordinate into a short string by recursively bisecting the world into a 4×8 grid. Nearby locations share a common prefix. A geohash prefix of length 5 covers ~5km × 5km. Expanding or shrinking the prefix changes the search radius. Redis uses 52-bit geohash integers internally for its GEORADIUS command.

3. **(L4)** How do you handle the driver location update for 1M drivers/sec without a hot-key problem?
   → Shard the Redis Geo cluster by geohash prefix (e.g., geohash characters 0-7 → shard 0, 8-F → shard 1, etc.). This distributes updates across shards by geographic region. Each shard receives ~100K updates/sec (well within Redis's 500K ops/sec capacity per node). Kafka partitions by driver_id hash, and each consumer writes to the relevant Redis shard.

4. **(L4)** How do you compute surge pricing dynamically?
   → Divide each city into H3 hexagonal cells (level-9, ~170m diameter). Every 30 seconds, count available drivers and ride requests in each cell. Surge multiplier = max(1.0, demand / supply). Apply exponential moving average (α=0.3) to smooth sudden spikes. Apply surge contagion: adjacent cells with high demand pull surge to neighbors. Cap surge at 3.0× (regulatory requirement in some cities).

5. **(L5)** Walk through the complete matching flow from ride request to driver acceptance.
   → Rider requests ride with (pickup_lat, pickup_lon, vehicle_type). Matching Service calls Redis GEORADIUS on the geohash cell for that location, fetching 20 nearest drivers. Filters by: vehicle_type match, driver status == available, driver not already in a match attempt. Ranks by ETA (LightGBM model: current position → road speed → estimated arrival). Sends WebSocket push to top driver with trip details. Driver has 10 seconds to accept/decline. On accept: PostgreSQL UPDATE trips SET driver_id=?, status='accepted' WHERE trip_id=? AND status='requested'; driver marked BUSY in Redis. If decline or timeout: move to next candidate. If all 20 candidates exhausted: expand radius by 2× and retry.

6. **(L5)** How do you prevent the "phantom driver" problem where a matched driver is actually far away despite appearing close in the index?
   → Driver locations in Redis can be up to 5s stale. Solution: when Matching Service selects a driver candidate, it calls Driver Location Service for a fresh location confirmation (bypassing the stale Redis value). If confirmed location is >2km from what Redis showed, discard candidate and move to next. Also: Matching Service tracks the timestamp of last location update; drivers with updates older than 30s are excluded from matching regardless of their Redis position (likely offline or in a tunnel).

7. **(L5+)** Design the surge pricing system to be fair across city zones: high-income areas should not always have more supply than low-income areas purely due to driver preference.
   → Current problem: drivers migrate to high-surge zones (downtown), leaving outer areas under-served. Solutions: (1) Zone-based incentive bonuses: drivers in under-served zones receive guaranteed minimum surge floor ($2.00 minimum bonus per ride regardless of surge calculation). (2) Supply forecasting: ML model predicts which zones will go under-served 20 minutes ahead; proactive driver routing incentives pushed before surge triggers. (3) Rider-side pricing smoothing: riders in low-supply zones can "lock in" a fare for 10 minutes (platform absorbs surge risk). All three require careful economic modeling — naive surge incentives can create oscillations (all drivers rush to same zone simultaneously).

## Anti-patterns / Things NOT to Say

- **"Store all driver locations in a single SQL table with lat/lon columns"** — At 1M updates/sec to a single PostgreSQL table, write throughput far exceeds what a single DB can handle (~10K writes/sec practical limit). Even with partitioning, you'd need 100 partitions and complex routing logic. Redis Geo handles this trivially with sub-millisecond reads.
- **"Use WebSockets for driver location updates"** — WebSocket connections are stateful and expensive to maintain at 5M concurrent connections on a single service. Use UDP for location updates (driver app fires and forgets; one dropped packet is fine) or HTTPS POST with keep-alive (HTTP/2 multiplexed). Reserve WebSocket/SSE for push from server → client (trip status updates, new rider requests).
- **"Recalculate surge pricing every second"** — Surge calculation requires aggregating supply/demand across thousands of hexagonal cells. At 1-second intervals, this is a huge computational load for marginal accuracy improvement. 30-second intervals with EMA smoothing provide surge stability and prevent driver micro-oscillations (drivers won't relocate in 30s anyway).
- **"The matching algorithm should always pick the closest driver"** — The closest driver by Euclidean distance may be in heavy traffic with a 15-minute ETA. A driver 500m further with a clear road may have a 3-minute ETA. Always rank by ETA (road network time), not Euclidean distance. This is Uber's primary matching criterion.

## Python Implementation (sketch)

```python
import math
import time
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

@dataclass
class Location:
    lat: float
    lon: float

@dataclass
class Driver:
    driver_id: int
    location: Location
    status: str = "available"  # available | busy | offline
    updated_at: float = field(default_factory=time.time)

def haversine_km(a: Location, b: Location) -> float:
    """Straight-line distance in km between two GPS coordinates."""
    R = 6371.0
    lat1, lon1 = math.radians(a.lat), math.radians(a.lon)
    lat2, lon2 = math.radians(b.lat), math.radians(b.lon)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(h))

class LocationService:
    """In-memory simulation of Redis Geo for driver locations."""

    def __init__(self, stale_threshold_sec: float = 30.0):
        self._drivers: Dict[int, Driver] = {}
        self._lock = threading.Lock()
        self.stale_threshold = stale_threshold_sec

    def update(self, driver_id: int, lat: float, lon: float) -> None:
        with self._lock:
            if driver_id not in self._drivers:
                self._drivers[driver_id] = Driver(driver_id, Location(lat, lon))
            else:
                d = self._drivers[driver_id]
                d.location = Location(lat, lon)
                d.updated_at = time.time()

    def set_status(self, driver_id: int, status: str) -> None:
        with self._lock:
            if driver_id in self._drivers:
                self._drivers[driver_id].status = status

    def nearby(self, center: Location, radius_km: float,
               limit: int = 20) -> List[Tuple[float, Driver]]:
        """Return (distance_km, driver) pairs within radius, sorted by distance."""
        now = time.time()
        results = []
        with self._lock:
            for d in self._drivers.values():
                if d.status != "available":
                    continue
                if now - d.updated_at > self.stale_threshold:
                    continue  # exclude stale locations
                dist = haversine_km(center, d.location)
                if dist <= radius_km:
                    results.append((dist, d))
        results.sort(key=lambda x: x[0])
        return results[:limit]


class MatchingService:
    """Simple nearest-driver matching with radius backoff."""

    SEARCH_RADII_KM = [1.0, 2.0, 5.0, 10.0]
    OFFER_TIMEOUT_SEC = 10

    def __init__(self, location_svc: LocationService):
        self.location_svc = location_svc
        self._accepted: Dict[int, int] = {}  # trip_id → driver_id

    def match(self, trip_id: int, pickup: Location) -> Optional[int]:
        """Try to find and lock a driver. Returns driver_id or None."""
        for radius in self.SEARCH_RADII_KM:
            candidates = self.location_svc.nearby(pickup, radius_km=radius, limit=10)
            if not candidates:
                continue
            for dist_km, driver in candidates:
                # Simulate sending offer and waiting for acceptance
                eta_min = (dist_km / 30) * 60  # 30 km/h average city speed
                print(f"  Offering trip {trip_id} to driver {driver.driver_id} "
                      f"({dist_km:.2f}km, ETA ~{eta_min:.0f}min)")
                # In production: send push notification, wait for WebSocket response
                import random
                if random.random() > 0.3:  # 70% acceptance rate
                    self.location_svc.set_status(driver.driver_id, "busy")
                    self._accepted[trip_id] = driver.driver_id
                    return driver.driver_id
                print(f"  Driver {driver.driver_id} declined.")
            print(f"  Expanding search to {radius*2}km...")
        return None


class SurgePricing:
    """Simple supply/demand surge calculation per geohash prefix."""

    def __init__(self):
        self._demand: Dict[str, int] = {}  # geohash4 → pending request count
        self._supply: Dict[str, int] = {}  # geohash4 → available driver count

    @staticmethod
    def _geohash4(lat: float, lon: float) -> str:
        """Crude 4-char geohash approximation (bucket by 1-degree cells)."""
        return f"{int(lat):+04d}{int(lon):+04d}"

    def record_request(self, pickup: Location) -> None:
        k = self._geohash4(pickup.lat, pickup.lon)
        self._demand[k] = self._demand.get(k, 0) + 1

    def record_supply(self, loc: Location) -> None:
        k = self._geohash4(loc.lat, loc.lon)
        self._supply[k] = self._supply.get(k, 0) + 1

    def surge_multiplier(self, pickup: Location) -> float:
        k = self._geohash4(pickup.lat, pickup.lon)
        d = self._demand.get(k, 0)
        s = self._supply.get(k, 1)  # avoid division by zero
        return min(3.0, max(1.0, d / s))


# Demo
if __name__ == "__main__":
    loc_svc = LocationService(stale_threshold_sec=30)
    surge = SurgePricing()

    # Register 5 drivers near San Francisco
    for i in range(5):
        lat = 37.7749 + (i * 0.005)
        lon = -122.4194 + (i * 0.003)
        loc_svc.update(driver_id=i, lat=lat, lon=lon)
        surge.record_supply(Location(lat, lon))

    pickup = Location(lat=37.776, lon=-122.418)
    surge.record_request(pickup)
    surge.record_request(pickup)  # high demand

    s = surge.surge_multiplier(pickup)
    print(f"Surge multiplier at pickup: {s:.2f}×")

    matcher = MatchingService(loc_svc)
    driver_id = matcher.match(trip_id=1001, pickup=pickup)
    if driver_id:
        print(f"Matched trip 1001 to driver {driver_id}")
    else:
        print("No driver found — ride cancelled")
```
