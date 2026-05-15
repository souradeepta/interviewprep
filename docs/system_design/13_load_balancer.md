# Load Balancer

## Problem Statement

Implement a load balancer to distribute requests across multiple backend servers using various strategies.

**Requirements:**
- Multiple balancing strategies (Round Robin, Least Connections, Random)
- Server health tracking
- Request distribution
- Server selection is O(1)

## Design

### Balancing Strategies

```
Round Robin:     1 → 2 → 3 → 1 → 2 → 3
                 Rotate through servers sequentially

Least Connections:  Track active connections per server
                    Route to server with fewest connections

Random:          Pick random server from available pool
                 Simple, no state needed

IP Hash:         Hash client IP, always same server
                 Session persistence
```

### Data Structure

```
servers: [Server1, Server2, Server3]
current_index: int (for round robin)
connections: {server_id -> active_count}
```

### Operations

```
selectServer():
  - Round Robin: return servers[current_index++ % len(servers)]
  - Least Conn: return server with min(connections[server])
  - Random: return random server
  - IP Hash: return servers[hash(client_ip) % len(servers)]

route(request):
  server = selectServer()
  return server.handle(request)
```

## Trade-offs

| Algorithm | Pro | Con |
|-----------|-----|-----|
| Round Robin | Simple, fair | No connection awareness |
| Least Conn | Connection-aware | Track overhead |
| Random | No state | Less optimal |
| IP Hash | Session persistence | Uneven distribution |

## Complexity

| Operation | Time |
|-----------|------|
| selectServer (RR) | O(1) |
| selectServer (LC) | O(n) where n=servers |
| selectServer (Random) | O(1) |
| route | O(select + handle) |
