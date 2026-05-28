# Load Balancer

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

A load balancer distributes incoming network requests across a pool of backend servers so that no
single server becomes a bottleneck. Beyond simple round-robin distribution, modern load balancers
handle health checking, SSL termination, session affinity, connection draining, and increasingly
intelligent traffic management — canary deploys, geographic routing, and circuit breaking.

In interviews, load balancers appear at two levels: as a component in a larger system design ("add
a load balancer in front of your API tier") and as the primary design target ("design a load
balancer that handles 10M requests/sec globally"). L5+ candidates must explain the difference
between L4 and L7 load balancing, trade-offs between algorithms, and how global load balancing via
anycast/BGP works.

## Functional Requirements

- Distribute incoming requests across a pool of healthy backend servers
- Health-check backends continuously; automatically remove unhealthy servers
- Support multiple balancing algorithms (round-robin, least-connections, IP hash, weighted)
- Maintain session affinity (sticky sessions) when the application requires it
- Drain connections gracefully before removing a server (zero-downtime deploys)
- Support TLS termination so backends communicate over plain HTTP internally

## Non-Functional Requirements

- **Scale:** 10M requests/sec at peak; pool of up to 10,000 backend servers
- **Latency:** Load balancer adds < 1ms to request latency at P99; P50 < 0.2ms
- **Availability:** 99.999% (five nines); LB failure cannot cause downtime
- **Consistency:** Health state converges within 10s of a backend becoming unavailable

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Single LB throughput:
  L4 LB (TCP passthrough): ~10M packets/sec on 40Gbps NIC (commodity hardware)
  L7 LB (HTTP proxy): ~500K req/sec per core × 32 cores = ~16M req/sec (nginx on 32-core)
  At 10M req/sec, a single high-end L7 LB node can handle the load with headroom

Health check traffic:
  10,000 backends × 1 health check/5s = 2,000 health checks/sec
  Each check: TCP connect (or HTTP GET /health) → tiny overhead

Connection table (L4 state):
  Each active TCP connection: 256 bytes of state
  100K concurrent connections × 256 bytes = 25.6 MB (fits in RAM easily)
  10M concurrent connections × 256 bytes = 2.56 GB (needs tuning, still feasible)

For redundancy:
  2 LB nodes active-passive (heartbeat failover in < 1s via VRRP/keepalived)
  Or: 2 LB nodes active-active behind anycast VIP
```

### Architecture Diagram

```
                       ┌─────────────────────────────────────────┐
Internet/Clients       │          Load Balancer Cluster           │
                       │                                          │
[Client A] ──────────►│  VIP: 203.0.113.10                      │
[Client B] ──────────►│  ┌────────────┐     ┌────────────┐      │
[Client C] ──────────►│  │   LB-1     │     │   LB-2     │      │
                       │  │ (Primary)  │     │ (Standby)  │      │
                       │  │  nginx /   │     │  VRRP      │      │
                       │  │  HAProxy   │     │  failover  │      │
                       │  └──────┬─────┘     └────────────┘      │
                       │         │ (health-checked pool)          │
                       └─────────┼────────────────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
        ┌──────────┐       ┌──────────┐       ┌──────────┐
        │ App-1    │       │ App-2    │       │ App-3    │
        │ :8080    │       │ :8080    │       │ :8080    │
        │ ✓ HEALTH │       │ ✓ HEALTH │       │ ✗ DOWN   │  ← removed from pool
        └──────────┘       └──────────┘       └──────────┘

Health Check Loop (every 5s per backend):
  TCP connect to :8080 → success → mark UP
  HTTP GET /health → 200 OK → mark UP
  3 consecutive failures → mark DOWN → stop sending requests → alert
```

### Data Model

```python
# Backend pool model

class Backend:
    id: str                  # "app-1:8080"
    address: str             # "10.0.0.1"
    port: int                # 8080
    weight: int              # 1-100 (for weighted round-robin)
    state: str               # UP | DOWN | DRAINING
    active_connections: int  # used by least-connections algorithm
    health_fail_count: int   # consecutive health check failures
    last_checked: float      # epoch of last health check

class LoadBalancer:
    backends: List[Backend]        # all registered backends
    algorithm: str                 # round_robin | least_conn | ip_hash | weighted
    health_check_interval_sec: int # 5
    health_fail_threshold: int     # 3 consecutive failures → mark DOWN
    connection_table: Dict[str, Backend]  # client_id → backend (for sticky sessions)
    round_robin_counter: int       # atomic counter for RR
```

### API Design

```
# Management API (control plane)
POST   /backends          -- register a new backend { "address": "10.0.0.5", "port": 8080 }
DELETE /backends/{id}     -- remove backend (triggers graceful drain)
PUT    /backends/{id}     -- update weight, enable/disable

GET    /backends          -- list all backends with health status
GET    /backends/{id}     -- single backend: state, active_connections, health_fail_count
GET    /stats             -- rps, latency p50/p99, error rate per backend

# Data plane (transparent to clients; these are LB-to-backend calls)
# All client requests are proxied; clients only see the VIP (203.0.113.10)
```

### Basic Scaling

- **Active-passive redundancy:** Two LB nodes share a Virtual IP (VIP). Primary owns the VIP; secondary monitors via VRRP heartbeats every 1s. Failover < 2s. Keepalived implements this on Linux.
- **Algorithm selection:** Round-robin works for stateless backends with uniform request cost. Least-connections is better when request duration varies widely (avoids sending a slow request to an already-busy server). IP hash provides sticky sessions without shared state between LB nodes.
- **TLS termination at LB:** Offload TLS handshake CPU cost from backends; backends use plain HTTP internally. LB handles certificate rotation centrally.
- **DNS-based scaling:** For global scale, use multiple LB clusters in different regions with geo-DNS (Route53 latency routing) to direct clients to the nearest cluster.

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
L7 load balancer sizing (nginx/Envoy proxy):
  Single nginx worker: ~100K req/sec (simple reverse proxy, no heavy rewriting)
  32-core machine: 32 workers × 100K = ~3.2M req/sec
  For 10M req/sec: 4 active LB nodes × 3.2M = 12.8M (120% headroom)

Connection table memory:
  Envoy: 2KB state per active connection (stream state, headers, buffers)
  500K concurrent connections × 2KB = 1 GB RAM (fits on 8GB instance)

L4 vs L7 throughput:
  L4 (pure TCP passthrough, XDP/eBPF): 10-50M packets/sec, near line-rate
    - Kernel bypass via DPDK: 100M pps on 100Gbps NIC
    - State: only (src_ip, src_port, dst_ip, dst_port) → backend mapping
    - Cannot inspect HTTP headers, no path-based routing
  L7 (full HTTP proxy): 500K-3M req/sec per node
    - Can inspect URL, headers, body → flexible routing rules
    - Adds 0.2-1ms latency (TLS termination, header parsing)

Health check convergence:
  Interval: 5s, threshold: 3 failures → 15s to detect a dead backend
  To reduce to 5s: interval=2s, threshold=2 (trades false-positive risk)
  Active health check: LB → backend /health
  Passive health check: observe error rate on real traffic (5xx > 5% for 10s → mark down)
  Combine both: passive for fast detection, active for recovery confirmation

Weighted canary deploy math:
  Promote v2 with 5% weight: 5 weight / (95 + 5) = 5% of traffic to v2
  Monitor error rate on v2 for 10min; if < 0.1% errors, increase to 20%, then 50%, then 100%
  Rollback trigger: v2 error rate 5× baseline → immediately set v2 weight to 0
```

### Failure Modes

```
Scenario 1: Primary LB dies
  - VRRP: secondary detects missed heartbeat within 3s → takes over VIP → ARP announcement
  - Clients reconnect; TCP connections that were in-flight are dropped (clients retry)
  - Solution: for zero-drop failover, use anycast with multiple active LBs simultaneously

Scenario 2: Backend pool shrinks to 0 (all backends down)
  - LB has no healthy backends → returns 503 Service Unavailable
  - With circuit breaker: LB continues sending a fraction of traffic as probes (10%)
  - Prevention: keep minimum 1 backend in DRAINING state (never fully remove last backend)
  - Alert: PagerDuty when healthy backend count < 2

Scenario 3: Thundering herd after LB restart
  - On restart, LB connection table is empty; all sticky sessions lost
  - All clients get re-routed (may hit cold backends, cold caches)
  - Mitigation: store connection table in shared Redis (slower but survives restart)
  - Or: accept the cold start, ensure backends can handle the spike (auto-scale pre-warmed)

Scenario 4: Slow backend infects the LB
  - Backend responds but slowly (200ms p99 → 5s p99 due to DB overload)
  - LB queues requests waiting for backend → LB's own request queue fills
  - Mitigation: per-backend timeout (e.g., 1s) + retry on another backend
  - Active health check alone won't catch this (backend returns 200 OK but slowly)
  - Fix: track p99 latency per backend; remove from pool if p99 > 2× cluster median

Scenario 5: DDoS floods the LB VIP
  - Solution 1: anycast absorbs traffic across many PoPs globally (Cloudflare, Akamai model)
  - Solution 2: rate limiting at LB (token bucket per source IP)
  - Solution 3: SYN cookies to handle SYN floods without consuming connection table
  - Solution 4: upstream scrubbing center filters attack traffic before it reaches LB
```

### Consistency Boundaries

```
Health state consistency:
  In a multi-LB active-active setup, each LB runs its own health checks independently
  LB-1 may mark backend-3 as DOWN while LB-2 still has it as UP (race window: 5-15s)
  Fix: gossip protocol between LBs to share health state (similar to Serf/Consul)
  Or: centralized health check service (consul health agent) → all LBs read from it
  Trade-off: centralized = single source of truth but adds a dependency; decentralized = resilient but inconsistent

Session affinity models:
  IP hash: deterministic, no shared state between LBs; breaks if client changes IP (mobile)
  Cookie-based (L7): LB sets a cookie with hashed backend ID; consistent across IPs
    - Cookie: Set-Cookie: SERVERID=app-2; Path=/; HttpOnly
  Shared state: LB stores session → backend mapping in Redis; consistent but adds latency (+0.5ms)
  Best practice: design stateless backends — eliminate the need for session affinity entirely

Global load balancing consistency:
  DNS TTL = 30s → up to 30s of stale routing after a backend region fails
  Anycast: same VIP advertised from multiple PoPs; BGP convergence = 30-90s after failure
  HTTP redirect: LB in region A redirects to region B (sub-second) but adds 1 RTT to latency
  Recommendation: Anycast + health-check-aware BGP withdrawal for sub-30s regional failover
```

### Cost Model

```
Self-managed LB vs managed service:

Self-managed (nginx + keepalived on EC2):
  2 × c6i.8xlarge (32 vCPU, 64GB): $1.088/hr × 2 = $1,580/month
  EIP (Elastic IP for VIP): $3.60/month
  Network egress: at 10M req/sec × 2KB avg response = 20 GB/sec
    20 GB/sec × 86400 × 30 × $0.09/GB ≈ $4.6M/month (egress dominant cost)
  Management overhead: 2 engineers × $200K/yr / 12 = $33K/month

AWS ALB (Application Load Balancer):
  ALB pricing: $0.008/LCU-hour
  LCU = max(new connections, active connections, processed bytes, rule evaluations)
  At 10M req/sec: processed bytes dominates
    20 GB/sec × 3600 × 730hr/month = 52,560 TB → $0.008 × (52560 × 1000 GB / 1 LCU) ≈ complex
  Simplified: AWS ALB costs ~$0.05-0.10 per million HTTP requests at scale
    10M req/sec × 86400 × 30 = 25.9 trillion/month × $0.05/M = $1.3M/month
  No management overhead; auto-scales

Cloudflare / Akamai (global CDN + LB):
  Fixed pricing: ~$200-$5,000/month depending on plan + overage
  Handles DDoS, anycast, global routing, TLS
  Best price/performance for pure L7 global load balancing

Dominant cost driver: network egress (always)
Optimization: CDN offloads 60-80% of requests → reduces LB egress cost proportionally
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| **Round-Robin** | Simple, even distribution, no state | Ignores backend load; slow backends accumulate connections | Uniform stateless services (same request cost) |
| **Least Connections** | Adapts to request cost variance; fast backends get more load | Requires connection count per backend (slight state overhead) | Mixed workloads (cheap and expensive requests) |
| **IP Hash (consistent)** | Sticky sessions without cookies, deterministic | Skewed if clients share IPs (NAT); breaks on backend pool change | Session affinity, cache locality |
| **Consistent Hashing** | Minimal redistribution when backends added/removed | Complex implementation; requires virtual nodes for even distribution | Distributed caches, stateful services |
| **L4 (TCP passthrough)** | Line-rate throughput, lowest latency overhead | No HTTP-layer visibility; no path routing | High-throughput non-HTTP (databases, game servers) |
| **L7 (HTTP proxy)** | Path routing, header inspection, A/B testing, TLS offload | ~1ms added latency, higher CPU cost | Web apps, microservices, REST APIs |

## Follow-up Questions (escalating difficulty)

1. **(L3)** What happens to in-flight requests when a backend is removed from the pool?
   → Without connection draining, the LB immediately stops sending new requests to the backend, but existing connections are left open. With draining: the backend is set to DRAINING state; the LB stops routing new requests to it but allows existing connections to complete normally. After a drain timeout (e.g., 30s), the backend is forcefully removed.

2. **(L3)** Why is round-robin insufficient for a service with mixed request costs?
   → Round-robin assumes all requests take the same time. If 1% of requests are expensive (e.g., generating a report), those servers accumulate connections while still receiving new requests. Least-connections routes new requests to the server with fewest active connections, naturally avoiding already-loaded backends.

3. **(L4)** How does consistent hashing help when backends are added or removed?
   → In simple hash-based routing, adding 1 backend to a pool of N causes N/(N+1) of all traffic to reroute — catastrophic for cache locality. Consistent hashing places both backends and requests on a ring; adding a backend only reroutes traffic that was assigned to its immediate neighbor on the ring. With virtual nodes, only 1/N of traffic redistributes.

4. **(L4)** How would you implement zero-downtime backend deploys?
   → Three-step: (1) Add new-version backends to the pool at low weight (e.g., 5%). (2) Set old-version backends to DRAINING — stop new traffic but complete in-flight. (3) After drain timeout (30s), remove old backends. The LB never has a moment with zero healthy backends. This is the canary → progressive rollout pattern.

5. **(L5)** Explain anycast and how it provides geographic load balancing.
   → Anycast assigns the same IP address to multiple servers in different data centers and announces it via BGP. Clients connect to the same IP but BGP routing automatically directs them to the topologically nearest PoP (point of presence). On PoP failure, BGP withdraws the route; clients reconnect and are routed to the next nearest PoP. Convergence time: 30-90 seconds. Used by Cloudflare (200+ PoPs), all sharing a single /24 network.

6. **(L5)** How do you implement traffic shifting for a canary deploy at 1% granularity?
   → Weighted round-robin: backend pool has v1 at weight=99 and v2 at weight=1. LB distributes 99 of every 100 requests to v1, 1 to v2. For header-based canary: L7 LB routes requests with `X-Canary: true` header to v2; this requires cookie or user-ID-based bucketing upstream. Monitor error rate, latency, and business metrics on v2 traffic before increasing weight.

7. **(L5+)** Design a global load balancer that achieves sub-5-second failover across regions.
   → Combine: (1) Anycast VIP for instant BGP-level routing to nearest healthy PoP; (2) active health checks from each PoP to backends every 2s with threshold=2 failures (4s to detect); (3) BGP community strings to withdraw the failing region's route within 2s of health check failure; (4) regional LBs configured with cross-region fallback pools. Total: health detection 4s + BGP propagation 1s = ~5s. This is Cloudflare's architecture for their global load balancer product.

## Anti-patterns / Things NOT to Say

- **"Just add more load balancers"** — The LB itself can become a bottleneck or single point of failure. The correct answer is: make LBs stateless so you can add them behind a shared anycast VIP or use active-active with ECMP (Equal-Cost Multi-Path routing) so multiple LBs share the same VIP at the network layer.
- **"Use sticky sessions based on IP"** — IP-based sticky sessions break for mobile clients that switch networks, clients behind shared NAT (corporate firewalls where thousands of users share one IP), and when using IPv6 (address changes more often). Use cookie-based stickiness or better yet, eliminate session state from backends entirely.
- **"Health checks are just ping"** — ICMP ping only checks network reachability. A backend can respond to ping while its application is deadlocked or its database connections are exhausted. Use HTTP health check endpoints that verify application health (e.g., attempt a DB query), and monitor the error rate on live traffic (passive health check) as an additional signal.
- **"The load balancer is highly available because we have two of them"** — Having two LBs only helps if the failover actually works. VRRP failover must be tested regularly; keepalived has subtle split-brain failure modes. Additionally, two LBs on the same network segment can both be taken down by a switch failure. True HA requires LBs in different failure domains (different racks, AZs, or regions).
- **"L7 is always better than L4"** — L7 adds latency (TLS termination + HTTP parsing) and CPU overhead. For non-HTTP protocols (MySQL, Redis, game servers), L4 is the only option. For extremely high-throughput HTTP (10M+ req/sec), L4 with XDP/eBPF for connection routing outperforms L7 proxies.

## Python Implementation (sketch)

```python
import threading
import time
import random
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class BackendState(Enum):
    UP = "up"
    DOWN = "down"
    DRAINING = "draining"

@dataclass
class Backend:
    address: str
    port: int
    weight: int = 1
    state: BackendState = BackendState.UP
    active_connections: int = 0
    fail_count: int = 0

    @property
    def id(self) -> str:
        return f"{self.address}:{self.port}"

class LoadBalancer:
    """Simple L7 load balancer with pluggable algorithms and health checking."""

    def __init__(self, algorithm: str = "round_robin",
                 health_interval: float = 5.0, fail_threshold: int = 3):
        self.algorithm = algorithm
        self.health_interval = health_interval
        self.fail_threshold = fail_threshold
        self._backends: List[Backend] = []
        self._lock = threading.Lock()
        self._rr_index = 0
        # Start health check thread
        threading.Thread(target=self._health_loop, daemon=True).start()

    def add_backend(self, address: str, port: int, weight: int = 1) -> None:
        with self._lock:
            self._backends.append(Backend(address, port, weight))

    def remove_backend(self, address: str, port: int,
                       drain_sec: float = 30.0) -> None:
        with self._lock:
            for b in self._backends:
                if b.address == address and b.port == port:
                    b.state = BackendState.DRAINING
        # After drain window, remove entirely
        def _remove():
            time.sleep(drain_sec)
            with self._lock:
                self._backends = [
                    b for b in self._backends
                    if not (b.address == address and b.port == port)
                ]
        threading.Thread(target=_remove, daemon=True).start()

    def _healthy_backends(self) -> List[Backend]:
        return [b for b in self._backends if b.state == BackendState.UP]

    def select(self, client_ip: Optional[str] = None) -> Optional[Backend]:
        with self._lock:
            healthy = self._healthy_backends()
            if not healthy:
                return None
            if self.algorithm == "round_robin":
                b = healthy[self._rr_index % len(healthy)]
                self._rr_index += 1
                return b
            elif self.algorithm == "least_conn":
                return min(healthy, key=lambda b: b.active_connections)
            elif self.algorithm == "ip_hash":
                idx = hash(client_ip or "") % len(healthy)
                return healthy[idx]
            elif self.algorithm == "weighted":
                weights = [b.weight for b in healthy]
                return random.choices(healthy, weights=weights, k=1)[0]
            return healthy[0]

    def _simulate_health_check(self, backend: Backend) -> bool:
        """Simulate: randomly fail 10% of the time for demo."""
        return random.random() > 0.10

    def _health_loop(self) -> None:
        while True:
            time.sleep(self.health_interval)
            with self._lock:
                for b in self._backends:
                    if b.state == BackendState.DRAINING:
                        continue
                    ok = self._simulate_health_check(b)
                    if ok:
                        b.fail_count = 0
                        b.state = BackendState.UP
                    else:
                        b.fail_count += 1
                        if b.fail_count >= self.fail_threshold:
                            if b.state == BackendState.UP:
                                print(f"[LB] Backend {b.id} marked DOWN")
                            b.state = BackendState.DOWN

    def route_request(self, client_ip: str = "0.0.0.0") -> str:
        backend = self.select(client_ip)
        if backend is None:
            return "503 Service Unavailable"
        backend.active_connections += 1
        try:
            time.sleep(0.001)   # simulate 1ms forwarding
            return f"200 OK from {backend.id}"
        finally:
            backend.active_connections -= 1

    def stats(self) -> dict:
        with self._lock:
            return {b.id: {"state": b.state.value,
                           "conns": b.active_connections,
                           "fails": b.fail_count}
                    for b in self._backends}


# Demo
if __name__ == "__main__":
    lb = LoadBalancer(algorithm="least_conn", health_interval=2.0, fail_threshold=2)
    for i in range(1, 5):
        lb.add_backend(f"10.0.0.{i}", 8080, weight=1)

    results = []
    for i in range(20):
        resp = lb.route_request(client_ip=f"192.168.1.{i % 10}")
        results.append(resp)

    print("Responses:", results[:5], "...")
    print("Stats:", lb.stats())
```
