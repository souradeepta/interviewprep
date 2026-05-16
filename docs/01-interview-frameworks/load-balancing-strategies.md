# Load Balancing Strategies: Distributing Traffic Efficiently

Master load balancing algorithms and distribution strategies.

---

## Load Balancing Algorithms

### Round Robin

```
Server 1 ← Request 1
Server 2 ← Request 2
Server 3 ← Request 3
Server 1 ← Request 4
...
```

**Pros:** Simple, fair distribution
**Cons:** Doesn't account for server capacity, ignores connections

```python
class RoundRobinLB:
    def __init__(self, servers):
        self.servers = servers
        self.index = 0
    
    def get_server(self):
        server = self.servers[self.index]
        self.index = (self.index + 1) % len(self.servers)
        return server
```

### Weighted Round Robin

```
Server 1 (capacity 100) ← 50% of requests
Server 2 (capacity 50)  ← 25% of requests
Server 3 (capacity 50)  ← 25% of requests
```

**Pros:** Accounts for different capacities
**Cons:** Still doesn't account for current load

### Least Connections

```
Server 1: 10 active connections ← New request
Server 2: 20 active connections
Server 3: 15 active connections
```

**Pros:** Better than round robin for long-lived connections
**Cons:** Doesn't account for connection weight

```python
class LeastConnectionsLB:
    def __init__(self, servers):
        self.servers = servers
        self.connections = {s: 0 for s in servers}
    
    def get_server(self):
        return min(self.servers, key=lambda s: self.connections[s])
```

### IP Hash

```
Hash(client_ip) % num_servers = server_id
Same client always goes to same server
```

**Pros:** Session affinity (sticky sessions)
**Cons:** Uneven distribution if IPs cluster

### Least Response Time

```
Choose server with (connections / avg_response_time)
Accounts for both load and performance
```

---

## Load Balancing Layers

### Layer 4 (Transport)

```
Load Balancer at TCP/UDP level
- Routes based on IP, ports
- Very fast (< 1ms overhead)
- Hardware-based (e.g., F5, Citrix)

Example: Client → 80 → LB → distributes to port 80 on servers
```

### Layer 7 (Application)

```
Load Balancer at HTTP level
- Routes based on URL, hostnames, headers
- More flexible but slower (1-10ms overhead)
- Software-based (e.g., nginx, HAProxy)

Example: 
/api/users → Server 1
/api/orders → Server 2
/api/payments → Server 3
```

---

## Session Persistence

### No Persistence (Stateless)

```
Request 1 → Server A
Request 2 → Server B
Request 3 → Server C

Each request independent
Requires shared session store (Redis)
```

### Sticky Sessions (Source IP)

```
Client 1.2.3.4 → Server A (for all requests)
Client 5.6.7.8 → Server B (for all requests)

Issue: If Server A goes down, client's sessions lost
```

### Distributed Session Store

```
All servers share session data in Redis
Any server can handle any request
Recommended approach
```

---

## Health Checks

```python
# Active health check
def health_check(server):
    try:
        response = requests.get(f"http://{server}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

# Remove unhealthy servers
healthy_servers = [s for s in servers if health_check(s)]
```

---

## Graceful Shutdown

```
Load Balancer receives shutdown signal
↓
Stop accepting new requests for server
↓
Wait for existing connections to finish (drain period)
↓
Close server
```

```python
@app.on_event("shutdown")
async def graceful_shutdown():
    # Stop accepting new requests
    lb.mark_shutting_down(server)
    
    # Wait for existing requests (max 30 seconds)
    await asyncio.sleep(30)
    
    # Force close any remaining
    server.close()
```

---

## Load Balancing Challenges

| Challenge | Solution |
|-----------|----------|
| **Single point of failure** | HA pair of load balancers |
| **Asymmetric load** | Use consistent hashing or least connections |
| **Session affinity** | Sticky sessions or distributed store |
| **Stale health checks** | Regular checks, fast failover |
| **Traffic spikes** | Auto-scaling, rate limiting |

---

## Recommended Setup

```
                    ┌── LB Primary
                    │
        Client ───→ LB Health Check ← (heartbeat)
                    │
                    └── LB Secondary (standby)

Each LB distributes to:
- Server 1 (health check OK)
- Server 2 (health check OK)
- Server 3 (health check failed → skip)
```

---

## Load Balancing Checklist

- ✓ Chose correct algorithm (round robin, least connections, IP hash)
- ✓ Health checks configured
- ✓ Session persistence strategy (stateless recommended)
- ✓ Graceful shutdown for deployments
- ✓ HA setup for load balancers
- ✓ Monitoring of distribution balance
- ✓ Tested with server failure
- ✓ Timeout settings appropriate
- ✓ Sticky sessions if needed
- ✓ Rate limiting to prevent abuse

