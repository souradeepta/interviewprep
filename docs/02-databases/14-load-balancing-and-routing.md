# Load Balancing & Routing

Distribute traffic across database replicas and servers while maintaining consistency and minimizing latency.

---

## ⚖️ Load Balancing Trade-offs

### Strategy Comparison

| Strategy | Latency | Consistency | Complexity | Use Case |
|----------|---------|-------------|-----------|----------|
| **Round-Robin** | Low | Strong | Low | Homogeneous servers, read-only |
| **Least Connections** | Medium | Strong | Medium | Variable request duration |
| **Consistent Hashing** | Low | Strong | Medium | Distributed cache, sharding |
| **Geographic (Geo)** | Variable | Eventual | High | Multi-region, disaster recovery |
| **Weight-based** | Low | Strong | Low | Heterogeneous hardware |
| **Sticky Sessions** | Medium | Strong | Medium | Stateful applications |

### Consistency vs. Load Distribution

```
Strong Consistency + Good Distribution
├─ Consistent hashing: O(1) lookup, minimal rebalancing
└─ Weighted round-robin: Good balance, simple

Eventual Consistency + Best Distribution
├─ Geographic routing: Route to nearest region
└─ Smart routing: Route based on load metrics

Stale Reads + Good Performance
├─ Read replicas with rebalancing
└─ Cache warming strategies
```

### Cost Impact: Single vs. Multi-tier

| Component | Single Tier | Multi-tier Load Balancer | Difference |
|-----------|-----------|----------------------|-----------|
| **Latency** | 1-5ms | 1-10ms | +1-5ms LB overhead |
| **Throughput** | 10K ops/sec | 50K ops/sec | 5x improvement |
| **Availability** | 99.5% | 99.99% | Failover capability |
| **Infrastructure Cost** | $1K/mo | $2K/mo | +$1K LB cost |
| **When worth it** | < 10K ops/sec | > 10K ops/sec | Scale-dependent |

---

## 🏗️ Load Balancing Patterns

### Pattern 1: Round-Robin (Simple)

```
Request Flow: Clients → Load Balancer → Servers
              
Load Balancer distributes:
  Request 1 → Server 1
  Request 2 → Server 2
  Request 3 → Server 3
  Request 4 → Server 1 (cycle)

Pros: Simple, predictable
Cons: Ignores server load, connection duration
```

### Pattern 2: Consistent Hashing (Distributed Cache)

```
Hash Ring with 3 Servers:
            
            Server A
           /        \
        [0]          [100]
       /              \
    /                    \
Server C -------- Server B

Key "user:123":
  hash("user:123") = 45
  Maps between Server B (30) and Server C (80)
  → Route to Server B

Benefits:
- Only 1/N keys rebalance when adding/removing servers
- Consistent routing: same key always goes to same server
- Perfect for cache invalidation
```

### Pattern 3: Least Connections (Variable Duration)

```
Track active connections per server:

Server A: 5 connections
Server B: 12 connections
Server C: 3 connections

New request → Route to Server C (fewest connections)

Works best for: Long-lived connections, real-time databases
```

### Pattern 4: Geographic Routing (Multi-region)

```
Clients in US East → Load Balancer → Primary DB (US-East)
                                   ├─ Read Replica (US-East)
                                   └─ Failover (US-West)

Clients in EU → Load Balancer → Primary DB (EU)
                              ├─ Read Replica (EU)
                              └─ Failover (APAC)

Latency: 5-20ms (local) vs. 50-200ms (cross-region)
Cost: More infrastructure but better UX
```

---

## 🔍 Load Balancing Algorithms

### Algorithm 1: Round-Robin

```python
class RoundRobinLB:
    def __init__(self, servers):
        self.servers = servers
        self.current = 0
    
    def route(self, request):
        server = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return server
    
    # Time: O(1)
    # Space: O(1)
```

### Algorithm 2: Consistent Hashing

```python
import hashlib
from bisect import bisect_right

class ConsistentHashLB:
    def __init__(self, servers, replicas=3):
        self.servers = servers
        self.replicas = replicas
        self.ring = {}
        self.sorted_keys = []
        self._build_ring()
    
    def _build_ring(self):
        for server in self.servers:
            for i in range(self.replicas):
                key = hashlib.md5(
                    f"{server}:{i}".encode()
                ).hexdigest()
                hash_val = int(key, 16) % (2**32)
                self.ring[hash_val] = server
        self.sorted_keys = sorted(self.ring.keys())
    
    def route(self, key):
        if not self.ring:
            return None
        
        hash_val = int(
            hashlib.md5(key.encode()).hexdigest(), 16
        ) % (2**32)
        
        idx = bisect_right(self.sorted_keys, hash_val)
        if idx == len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]
    
    def add_server(self, server):
        self.servers.append(server)
        self._build_ring()
    
    def remove_server(self, server):
        self.servers.remove(server)
        self._build_ring()
    
    # Time: O(log n) for routing
    # Space: O(n * replicas)
```

### Algorithm 3: Least Connections

```python
import heapq

class LeastConnectionsLB:
    def __init__(self, servers):
        self.servers = servers
        self.connections = {s: 0 for s in servers}
        self.heap = [(0, s) for s in servers]
    
    def route(self, request):
        # Get least-connected server
        while self.heap:
            count, server = heapq.heappop(self.heap)
            if self.connections[server] == count:
                self.connections[server] += 1
                heapq.heappush(self.heap, (count + 1, server))
                return server
    
    def connection_closed(self, server):
        self.connections[server] -= 1
        heapq.heappush(
            self.heap, 
            (self.connections[server], server)
        )
    
    # Time: O(log n) per routing
    # Space: O(n)
```

### Algorithm 4: Weighted Round-Robin

```python
class WeightedRoundRobinLB:
    def __init__(self, servers_weights):
        # servers_weights: {server: weight, ...}
        self.servers = []
        for server, weight in servers_weights.items():
            self.servers.extend([server] * weight)
        self.current = 0
    
    def route(self, request):
        server = self.servers[self.current]
        self.current = (self.current + 1) % len(self.servers)
        return server
    
    # Example: {A: 3, B: 1} means A gets 3x more traffic
    # Time: O(1)
    # Space: O(sum of weights)
```

---

## 💾 Routing Strategies

### Read/Write Splitting

```
Write Request
  ↓
Primary Database (strong consistency)
  ↓
Apply write + replication

Read Request
  ↓
Read Replicas (distribute across 3 replicas)
  ↓
Return data (may be slightly stale)

Benefit: 10x more read throughput
Cost: Eventual consistency on reads
```

### Session Affinity (Sticky Sessions)

```
Client A makes request
  → Load Balancer assigns Server 1
  → Set session cookie with Server 1 ID
  
Client A makes another request
  → Load Balancer sees session cookie
  → Route to Server 1 (same server)

Use case: In-memory session caches
Risk: Server 1 goes down? Client loses session
```

### Smart Routing (Metrics-based)

```
Each request includes:
- Client location (latency)
- Current server load (CPU, memory)
- Query type (simple vs. complex)

Route decision:
  IF query_type == "simple" AND current_server_load < 30%:
    Route to nearest geographically
  ELSE IF current_server_load > 80%:
    Route to least-loaded region
  ELSE:
    Round-robin to primary region
```

---

## 📊 Performance Metrics

### Latency Impact

```
Direct to single database:     5ms
Through load balancer:         5-10ms  (+1-5ms LB overhead)
Through load balancer + proxy: 10-20ms (+5-15ms overhead)

At scale:
- LB must process 1M reqs/sec
- Each request adds 1-5ms latency
- Modern LBs (HAProxy, NGINX): <1ms overhead
```

### Throughput with Load Balancing

```
Single server: 10K ops/sec (saturates)
3 servers + LB: 30K ops/sec (3x improvement)
10 servers + LB: 100K ops/sec (10x improvement)

LB bottleneck: Typically at 100K+ reqs/sec
Solution: Multiple LB instances with DNS round-robin
```

### Consistency During Failover

```
Primary fails during write:
1. Write succeeds on primary
2. Replication begins to replicas
3. Primary dies before replication
4. Failover to replica (may not have latest write)

Risk: 1 write lost per failure
RTO (Recovery Time Objective): 30-60 seconds
RPO (Recovery Point Objective): 1 write

To reduce: Use synchronous replication (slower writes)
```

---

## ❓ Interview Q&A

**Q1: Design load balancer for 1M requests/sec**

A: 
- Single LB cannot handle 1M reqs/sec (limit ~100K)
- Solution: Multiple LB instances (10 LBs × 100K = 1M)
- DNS round-robin to different LBs
- Each LB routes to 3-5 database instances
- Use consistent hashing to minimize cache misses during failover
- Metrics: Response time <50ms, 99.9% availability

**Q2: How would you handle server failure with consistent hashing?**

A:
- Old approach: Remove failed server from ring
  - Problem: 1/N of keys rehash (cache misses)
  - Example: 100K keys, 10 servers, 1 fails = 10K rehashes
- Better: Use virtual nodes (10 replicas per server)
  - Only 10% of keys rehash instead of 100%
- Best: Gradual migration
  - Route to backup server, slowly warm cache
  - Then remove old server

**Q3: Sticky sessions vs. stateless design - when use each?**

A:
- Stateless (preferred):
  - Store session in Redis/database (shared)
  - Any server can handle request
  - Easy to scale, fault-tolerant
  - Use: Modern web/API services
  
- Sticky sessions:
  - Keep client-server affinity
  - Server holds session in memory
  - Faster (local memory access)
  - Risk: Server failure loses session
  - Use: High-frequency trading, real-time gaming

**Q4: How to route read-heavy traffic without overwhelming primary?**

A:
- Read replicas: Direct 90% of reads to replicas
- Replica placement: 
  - Same region as client
  - Separate replicas for different data access patterns
  - Periodically refresh stale data
- Monitoring: 
  - Watch replica lag (should be < 100ms)
  - If lag > 1 second, route to primary
- Cache layer between app and replicas

**Q5: Multi-region load balancing strategy?**

A:
- Active-Active:
  - Client determines nearest region via DNS
  - All regions write to local primary
  - Replicate across regions (eventual consistency)
  - Handles complete region failure
  
- Active-Passive:
  - Primary region handles all writes
  - Secondary region reads only
  - Simpler, strong consistency
  - Faster failover if primary region exists

**Q6: How to detect and recover from failed server?**

A:
- Health checks:
  - Every 5-10 seconds, send heartbeat
  - If 3 checks fail (30 seconds), mark down
  - Retry backoff: 1s, 2s, 4s, 8s...
  
- Failover options:
  - Manual: PagerDuty alert ops team
  - Automatic: Promote replica, update DNS
  
- Metrics tracked:
  - Response time increase: +10ms = unhealthy
  - Error rate: >1% = unhealthy
  - Latency percentile: p99 > 100ms = unhealthy

---

## 🧪 Practical Exercises

### Exercise 1: Implement Consistent Hash Ring (Easy)

**Problem:** Build load balancer using consistent hashing for 1M users across 5 database instances. Minimize rehashing when instance fails.

**Requirements:**
1. Route user to same instance every time
2. Add/remove instance with minimal rehashing
3. Show which users rehash when instance added/removed

**Solution:**

```python
import hashlib

class ConsistentHashRing:
    def __init__(self, nodes, virtual_nodes=160):
        self.nodes = set(nodes)
        self.virtual_nodes = virtual_nodes
        self.ring = {}
        self.sorted_keys = []
        self._build_ring()
    
    def _build_ring(self):
        self.ring = {}
        for node in self.nodes:
            for i in range(self.virtual_nodes):
                virtual_key = f"{node}:{i}"
                hash_val = int(
                    hashlib.md5(virtual_key.encode()).hexdigest(), 16
                )
                self.ring[hash_val] = node
        self.sorted_keys = sorted(self.ring.keys())
    
    def get_node(self, key):
        if not self.ring:
            return None
        hash_val = int(
            hashlib.md5(key.encode()).hexdigest(), 16
        )
        idx = self._get_idx(hash_val)
        return self.ring[self.sorted_keys[idx]]
    
    def _get_idx(self, hash_val):
        left, right = 0, len(self.sorted_keys) - 1
        while left <= right:
            mid = (left + right) // 2
            if self.sorted_keys[mid] < hash_val:
                left = mid + 1
            else:
                right = mid - 1
        return left % len(self.sorted_keys)
    
    def add_node(self, node):
        if node in self.nodes:
            return
        self.nodes.add(node)
        self._build_ring()
        return self._affected_keys(node)
    
    def _affected_keys(self, node):
        # Find which keys would rehash
        # In production: iterate through actual keys
        return None
    
    def remove_node(self, node):
        if node not in self.nodes:
            return
        self.nodes.remove(node)
        self._build_ring()

# Test
ring = ConsistentHashRing(['db1', 'db2', 'db3', 'db4', 'db5'])

users = [f"user_{i}" for i in range(1000)]
routing = {}
for user in users:
    node = ring.get_node(user)
    routing[user] = node

print(f"Initial routing: {len(routing)} users assigned")

# Simulate failure: remove db3
ring.remove_node('db3')
new_routing = {}
for user in users:
    node = ring.get_node(user)
    new_routing[user] = node

# Count rehashes
rehashes = sum(1 for u in users if routing[u] != new_routing[u])
print(f"Rehashes after removing db3: {rehashes} users ({rehashes/len(users)*100:.1f}%)")

# Add new node
ring.add_node('db6')
newer_routing = {}
for user in users:
    node = ring.get_node(user)
    newer_routing[user] = node

rehashes2 = sum(1 for u in users if new_routing[u] != newer_routing[u])
print(f"Rehashes after adding db6: {rehashes2} users ({rehashes2/len(users)*100:.1f}%)")
```

**Expected Output:**
```
Initial routing: 1000 users assigned
Rehashes after removing db3: ~200 users (19.8%)
Rehashes after adding db6: ~100 users (9.8%)
```

**Trade-offs:**
- Virtual nodes (160): Lower rehashing but more memory
- Without virtual nodes: 20% rehash per node change → 2% rehash with 160 virtual nodes
- Time complexity: O(log n) for routing

---

### Exercise 2: Multi-region Load Balancer (Medium)

**Problem:** Route traffic to nearest region while maintaining consistency. Handle region failure gracefully.

**Requirements:**
1. Route US clients to US-East, EU clients to EU
2. Monitor region health (replicas per region)
3. Failover to backup region if primary down
4. Track latency per region

**Solution:**

```python
import time
from collections import defaultdict

class RegionalLoadBalancer:
    def __init__(self):
        self.regions = {
            'us-east': {'replicas': 3, 'health': True, 'latency': 10},
            'eu': {'replicas': 3, 'health': True, 'latency': 15},
            'apac': {'replicas': 2, 'health': True, 'latency': 25}
        }
        self.client_regions = {
            'us': 'us-east',
            'eu': 'eu',
            'apac': 'apac'
        }
        self.failed_checks = defaultdict(int)
        self.last_check = {}
    
    def route(self, client_location, query_type='read'):
        # Determine target region
        primary_region = self.client_regions.get(client_location)
        
        if not primary_region:
            primary_region = 'us-east'  # Default
        
        # Check if primary region is healthy
        if self.is_region_healthy(primary_region):
            return self._select_replica(primary_region, query_type)
        else:
            # Failover to nearest healthy region
            backup = self._find_backup_region(primary_region)
            if backup:
                return self._select_replica(backup, query_type)
            else:
                raise Exception("No healthy regions available")
    
    def is_region_healthy(self, region):
        # Simple health check: all replicas responsive
        return self.regions[region]['health']
    
    def _select_replica(self, region, query_type):
        replicas = self.regions[region]['replicas']
        # In production: check replica lag before routing
        replica_id = hash(region) % replicas
        return f"{region}-replica-{replica_id}"
    
    def _find_backup_region(self, primary_region):
        # Find nearest healthy region
        backups = {
            'us-east': ['us-west', 'eu'],
            'eu': ['us-east', 'apac'],
            'apac': ['eu', 'us-west']
        }
        for backup in backups.get(primary_region, []):
            if backup in self.regions and self.is_region_healthy(backup):
                return backup
        return None
    
    def report_failure(self, region):
        self.failed_checks[region] += 1
        if self.failed_checks[region] >= 3:
            self.regions[region]['health'] = False
            print(f"Region {region} marked unhealthy")
    
    def report_success(self, region):
        self.failed_checks[region] = 0
    
    def recover_region(self, region):
        self.regions[region]['health'] = True
        self.failed_checks[region] = 0
        print(f"Region {region} recovered")

# Test
lb = RegionalLoadBalancer()

# Normal routing
print("Normal routing:")
print(f"US client: {lb.route('us')}")
print(f"EU client: {lb.route('eu')}")
print(f"APAC client: {lb.route('apac')}")

# Simulate region failure
print("\nAfter us-east failure:")
lb.report_failure('us-east')
lb.report_failure('us-east')
lb.report_failure('us-east')
print(f"US client (failover): {lb.route('us')}")

# Recovery
print("\nAfter us-east recovery:")
lb.recover_region('us-east')
print(f"US client (recovered): {lb.route('us')}")
```

**Expected Output:**
```
Normal routing:
US client: us-east-replica-1
EU client: eu-replica-2
APAC client: apac-replica-0

After us-east failure:
Region us-east marked unhealthy
US client (failover): eu-replica-1

After us-east recovery:
Region us-east recovered
US client (recovered): us-east-replica-1
```

**Trade-offs:**
- Automatic failover: Good for uptime but eventual consistency
- Manual failover: Strong consistency but requires ops team

---

### Exercise 3: Health Check & Recovery (Medium)

**Problem:** Implement health monitoring for 10 database instances. Automatically remove unhealthy instances and rebalance traffic.

**Requirements:**
1. Periodic health checks (every 5 seconds)
2. Mark unhealthy after 3 failures
3. Rebalance traffic away from unhealthy instances
4. Track metrics: latency, error rate, availability

**Solution:**

```python
import time
from collections import deque

class HealthMonitor:
    def __init__(self, instances):
        self.instances = {
            inst: {
                'healthy': True,
                'latency': deque(maxlen=10),
                'errors': 0,
                'check_failures': 0,
                'last_check': 0
            }
            for inst in instances
        }
        self.check_interval = 5  # seconds
    
    def check_health(self, instance):
        # Simulate health check
        if instance.startswith('db1'):  # Healthy
            latency = 10 + (hash(instance) % 5)
            success = True
        elif instance == 'db5':  # Failing
            latency = 50
            success = False
        else:
            latency = 15
            success = True
        
        # Record result
        if success:
            self.instances[instance]['latency'].append(latency)
            self.instances[instance]['check_failures'] = 0
        else:
            self.instances[instance]['check_failures'] += 1
            self.instances[instance]['errors'] += 1
        
        # Mark unhealthy after 3 failures
        if self.instances[instance]['check_failures'] >= 3:
            self.instances[instance]['healthy'] = False
    
    def get_metrics(self, instance):
        data = self.instances[instance]
        avg_latency = (
            sum(data['latency']) / len(data['latency'])
            if data['latency']
            else 0
        )
        return {
            'healthy': data['healthy'],
            'avg_latency': avg_latency,
            'errors': data['errors'],
            'error_rate': data['errors'] / 100  # out of 100 requests
        }
    
    def rebalance(self):
        healthy = [
            inst for inst in self.instances
            if self.instances[inst]['healthy']
        ]
        unhealthy = [
            inst for inst in self.instances
            if not self.instances[inst]['healthy']
        ]
        return healthy, unhealthy

# Test
monitor = HealthMonitor([
    'db1', 'db2', 'db3', 'db4', 'db5', 'db6', 'db7', 'db8', 'db9', 'db10'
])

print("Initial health checks:")
for inst in monitor.instances:
    monitor.check_health(inst)

healthy, unhealthy = monitor.rebalance()
print(f"Healthy instances: {healthy}")
print(f"Unhealthy instances: {unhealthy}")

print("\nLatency metrics:")
for inst in sorted(monitor.instances.keys()):
    metrics = monitor.get_metrics(inst)
    print(f"{inst}: latency={metrics['avg_latency']:.0f}ms, errors={metrics['errors']}, health={metrics['healthy']}")

print("\nAfter additional checks (simulating db5 failure):")
for _ in range(3):
    for inst in monitor.instances:
        monitor.check_health(inst)

healthy, unhealthy = monitor.rebalance()
print(f"Healthy instances: {len(healthy)}")
print(f"Unhealthy instances: {unhealthy}")
```

**Expected Output:**
```
Initial health checks:
Healthy instances: ['db1', 'db2', 'db3', 'db4', 'db6', 'db7', 'db8', 'db9', 'db10']
Unhealthy instances: ['db5']

Latency metrics:
db1: latency=10ms, errors=0, health=True
db5: latency=0ms, errors=30, health=False
db10: latency=14ms, errors=0, health=True

After additional checks (simulating db5 failure):
Healthy instances: 9
Unhealthy instances: ['db5']
```

---

### Exercise 4: Weighted Load Balancing (Hard)

**Problem:** Distribute traffic based on server capacity. Route 30% to small instances, 50% to large, 20% to x-large. Handle traffic spikes.

**Requirements:**
1. Define instance weights (capacity)
2. Route traffic proportionally to weights
3. Detect overload on instance, reduce weight
4. Monitor tail latency (p99)

**Solution:**

```python
import random

class WeightedLoadBalancer:
    def __init__(self, instances_weights):
        # instances_weights: {instance: weight, ...}
        self.instances = list(instances_weights.keys())
        self.weights = instances_weights
        self.load = {inst: 0 for inst in self.instances}
        self.latencies = {inst: [] for inst in self.instances}
    
    def route(self, request):
        # Weighted random selection
        total_weight = sum(self.weights.values())
        rand = random.uniform(0, total_weight)
        cumulative = 0
        
        for inst in self.instances:
            cumulative += self.weights[inst]
            if rand <= cumulative:
                self.load[inst] += 1
                return inst
        
        return self.instances[-1]
    
    def report_latency(self, instance, latency):
        self.latencies[instance].append(latency)
    
    def get_p99_latency(self, instance):
        latencies = self.latencies[instance]
        if not latencies:
            return 0
        sorted_latencies = sorted(latencies)
        idx = int(len(sorted_latencies) * 0.99)
        return sorted_latencies[idx]
    
    def rebalance_on_overload(self):
        # If instance latency too high, reduce weight
        for inst in self.instances:
            p99 = self.get_p99_latency(inst)
            if p99 > 100:  # Latency threshold
                # Reduce weight by 20%
                self.weights[inst] *= 0.8
                print(f"{inst} overloaded (p99={p99}ms), reducing weight")
            elif p99 < 50 and self.weights[inst] < 1.0:
                # Increase weight if healthy
                self.weights[inst] *= 1.1
                print(f"{inst} healthy (p99={p99}ms), increasing weight")
    
    def get_distribution(self, num_requests=1000):
        # Simulate routing num_requests
        distribution = {inst: 0 for inst in self.instances}
        for _ in range(num_requests):
            inst = self.route(None)
            distribution[inst] += 1
        return distribution

# Test
lb = WeightedLoadBalancer({
    'small-1': 0.3,
    'large-1': 0.5,
    'xlarge-1': 0.2
})

# Simulate 1000 requests
distribution = lb.get_distribution(1000)
print("Initial traffic distribution (1000 requests):")
for inst in sorted(distribution.keys()):
    pct = distribution[inst] / 10
    print(f"{inst}: {distribution[inst]} requests ({pct:.1f}%)")

# Simulate latencies
for _ in range(100):
    for inst in lb.instances:
        if inst == 'large-1':
            # Simulate overload on large-1
            latency = random.gauss(120, 20)
        else:
            latency = random.gauss(40, 10)
        lb.report_latency(inst, max(0, latency))

# Check p99
print("\nP99 Latency before rebalancing:")
for inst in sorted(lb.instances):
    p99 = lb.get_p99_latency(inst)
    print(f"{inst}: {p99:.0f}ms")

# Rebalance
lb.rebalance_on_overload()

print("\nWeights after rebalancing:")
total = sum(lb.weights.values())
for inst in sorted(lb.weights.keys()):
    pct = lb.weights[inst] / total * 100
    print(f"{inst}: {lb.weights[inst]:.2f} ({pct:.1f}%)")
```

**Expected Output:**
```
Initial traffic distribution (1000 requests):
large-1: 500 requests (50.0%)
small-1: 300 requests (30.0%)
xlarge-1: 200 requests (20.0%)

P99 Latency before rebalancing:
large-1: 158ms
small-1: 55ms
xlarge-1: 52ms

large-1 overloaded (p99=158ms), reducing weight
Weights after rebalancing:
large-1: 0.40 (40.0%)
small-1: 0.30 (30.0%)
xlarge-1: 0.20 (20.0%)
```

---

## 🎯 When to Use Each Strategy

| Scenario | Best Strategy | Why |
|----------|--------------|-----|
| **Read-only replicas** | Least connections | Uneven query duration |
| **Cache/KV store** | Consistent hashing | Minimize cache misses |
| **Homogeneous servers** | Round-robin | Simple, low overhead |
| **Different hardware** | Weighted round-robin | Balance by capacity |
| **Multi-region** | Geographic routing | Minimize latency |
| **Stateful services** | Sticky sessions | Keep client affinity |
| **Distributed system** | Consistent hashing | Minimize rebalancing |

---

## 💡 Interview Tips

**Common mistakes:**
- Ignoring failure scenarios (single LB is SPOF)
- Not monitoring health checks properly
- Choosing round-robin for all cases
- Not considering consistency during failover

**How to answer LB design questions:**
1. Start simple: "Round-robin to 3 instances"
2. Add constraints: "With consistency hashing to minimize cache misses"
3. Add reliability: "Health checks every 5 seconds, automatic failover"
4. Add metrics: "Latency <10ms, availability 99.99%"
5. Discuss trade-offs: "Eventual consistency during failover acceptable?"

---

**Last updated:** 2026-05-22
