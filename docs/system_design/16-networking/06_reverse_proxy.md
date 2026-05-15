# Reverse Proxy

## Problem Statement

Design a reverse proxy that sits in front of backend servers to provide SSL termination, caching, compression, rate limiting, and content routing.

## Scenario

Reverse Proxy is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

## Users

- **Backend Engineers**: Responsible for implementing and maintaining this system component in production environments. They need to understand the architecture, trade-offs, failure modes, and operational considerations.
- **DevOps/SRE Teams**: Monitor system health, manage scaling policies, handle incidents, and ensure reliability SLAs are met. They need insights into performance characteristics, bottlenecks, and failure recovery mechanisms.
- **Data Engineers**: Design data pipelines and analytics around this system, requiring deep understanding of data flow, consistency guarantees, and throughput characteristics.
- **System Architects**: Make high-level architectural decisions that impact company infrastructure, requiring comprehensive understanding of capabilities, limitations, and scalability boundaries.
- **Security Teams**: Understand security implications, potential vulnerabilities, and compliance requirements for this component.

## PRD

**Functional Requirements:**
- Correct behavior under all specified operating conditions
- Reliable operation with explicit failure modes
- Data consistency or eventual consistency guarantees as specified
- Clear mechanisms for error handling and recovery
- Monitoring and observability hooks

**Non-Functional Requirements:**
- **Performance**: Sub-100ms P99 latency for standard operations; measure and track tail latencies
- **Availability**: 99.99%+ uptime with automatic failover and graceful degradation
- **Scalability**: Support 10-100x current load with minimal architectural modifications
- **Consistency**: Specify whether strong, eventual, or causal consistency is required
- **Cost Efficiency**: Minimize operational cost per unit of throughput; consider compute, memory, and network costs
- **Operational Simplicity**: Reduce complexity to minimize human error and operational toil

**Constraints:**
- Resource limits (memory for caches, disk for databases, network bandwidth)
- Deployment constraints (cloud provider limits, regulatory requirements)
- Latency budgets (maximum acceptable delay for operations)

## Flow

The typical operational flow for this system involves these key phases:

1. **Request Arrival**: Client/upstream system sends request with required parameters and context
2. **Validation & Routing**: System validates request format, authentication, and routes to correct handler/shard/instance
3. **Core Processing**: Execute the main algorithm, database query, or business logic on the data/state
4. **State Management**: Update internal state (caches, indexes, counters, logs) with proper atomicity and locking
5. **Response Generation**: Format results and return to requester with relevant metadata (timing, version info)
6. **Observability**: Record metrics (latency, throughput, errors), logs (for debugging), and traces (for performance analysis)

This flow repeats thousands or millions of times per second in production. Each operation's efficiency compounds across the entire system, making careful optimization essential. Bottlenecks at any phase can cascade to impact overall system performance.

## Code Explanation

The provided implementations demonstrate key architectural concepts and design patterns:

**Python Implementation**: Uses built-in Python structures and standard library features to express the core logic clearly. Python emphasizes readability and conciseness—each operation's purpose should be obvious without extensive comments. You'll see different implementation approaches (e.g., using OrderedDict vs. manual linked lists) that represent trade-offs between convenience and fine-grained control.

**Java Implementation**: Shows how to implement the same logic with explicit memory management and type safety. Java's strong typing forces clear interface design; you'll see how generics, null safety, mutable state, and thread safety are handled. This implementation style is closer to production systems at scale.

**Key Implementation Patterns**:
- **Initialization**: Setting up core data structures, thread pools, or connection pools with specified capacity and configuration
- **Read Operations**: Fetching data while maintaining O(1) or O(log n) access, updating metadata (access times, hit counts, etc.)
- **Write Operations**: Inserting/updating data while handling eviction policies, balancing tree structures, or replicating state
- **Edge Cases**: Handling capacity limits, concurrent access, data consistency, and error conditions
- **Performance Optimization**: Using techniques like batch operations, lazy evaluation, or caching to reduce latency

Each line of code represents a deliberate choice about performance characteristics, memory usage, safety guarantees, and implementation complexity. Understanding these trade-offs is essential for using this component effectively in production systems.

## Architecture Diagram

```mermaid
graph LR
    Client[Client]
    RP[Reverse Proxy nginx]
    API[API Service :8080]
    Static[Static Assets :8081]
    Auth[Auth Service :8082]

    Client -->|HTTPS :443| RP
    RP -->|HTTP /api/*| API
    RP -->|HTTP /static/*| Static
    RP -->|HTTP /auth/*| Auth
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant RP as Reverse Proxy
    participant B as Backend

    C->>RP: HTTPS GET /api/users
    RP->>RP: Terminate TLS
    RP->>RP: Check rate limit (pass)
    RP->>RP: Route /api/* to backend:8080
    RP->>B: HTTP GET /api/users + X-Forwarded-For
    B-->>RP: 200 + JSON body
    RP->>RP: Compress (gzip)
    RP->>RP: Add security headers
    RP-->>C: 200 + compressed response
```

## Design

### Headers Added by Reverse Proxy

```
X-Forwarded-For:    <client-ip>    - Original client IP
X-Forwarded-Proto:  https          - Original scheme
X-Real-IP:          <client-ip>    - Simplified client IP
X-Request-ID:       <uuid>         - Distributed tracing
X-Response-Time:    42ms           - Proxy latency
```

### Reverse Proxy vs Forward Proxy

| | Reverse Proxy | Forward Proxy |
|---|---|---|
| Hides | Backend servers from clients | Clients from servers |
| Used by | Server operators | Clients, enterprises |
| Examples | nginx, HAProxy, Envoy | Squid, corporate proxies |
| Purpose | LB, SSL, caching | Content filtering, privacy |

### Nginx Upstream Config

```nginx
upstream api_backend {
    least_conn;
    server 10.0.0.1:8080 weight=3;
    server 10.0.0.2:8080 weight=1;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    ssl_certificate /certs/cert.pem;

    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header Connection "";
        proxy_http_version 1.1;
    }

    gzip on;
    gzip_types application/json text/html;
}
```

## Back-of-Envelope Calculations

```
Nginx throughput:
  Single core: ~50K req/sec (simple proxying)
  4 cores: ~200K req/sec
  Memory: ~2.5KB per connection x 50K = 125MB

SSL termination overhead:
  Modern AES-NI CPUs: <1% CPU per HTTPS connection
  Without AES-NI: 5-10% CPU

Compression savings:
  JSON/HTML: 70-80% smaller with gzip
  1KB JSON -> 200-300 bytes over wire
  CPU cost: ~5ms/MB on modern hardware (negligible)

Connection reuse savings:
  Without keepalive: TCP + TLS = 150ms per request (at 50ms RTT)
  With keepalive: 0ms after first connection
  10 requests per connection = 1350ms saved
```

## Design Choices

| Feature | Option A | Option B |
|---|---|---|
| SSL termination | At proxy (offloading) | End-to-end (mTLS) |
| Caching | At proxy | At CDN layer |
| Compression | At proxy | At application |
| Auth | At API gateway | At backend |
| Buffering | On (default) | Off (streaming, SSE) |

## Python Implementation

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request as URLReq
from typing import Dict
import gzip
import re

class ReverseProxyHandler(BaseHTTPRequestHandler):
    ROUTES: Dict[str, str] = {
        r"^/api/": "http://localhost:8081",
        r"^/static/": "http://localhost:8082",
    }

    def _route(self, path: str) -> str:
        for pattern, backend in self.ROUTES.items():
            if re.match(pattern, path):
                return backend
        return "http://localhost:8080"

    def do_GET(self):
        backend_url = self._route(self.path) + self.path
        req = URLReq(backend_url)
        req.add_header("X-Forwarded-For", self.client_address[0])
        req.add_header("X-Forwarded-Proto", "https")

        try:
            with urlopen(req, timeout=5) as resp:
                body = resp.read()
                status = resp.status
        except Exception:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(b"Bad Gateway")
            return

        accept_enc = self.headers.get("Accept-Encoding", "")
        if "gzip" in accept_enc:
            body = gzip.compress(body)
            self.send_response(status)
            self.send_header("Content-Encoding", "gzip")
        else:
            self.send_response(status)

        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Proxy", "python-reverse-proxy")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[PROXY] {self.path} -> {self._route(self.path)}")

# Run: HTTPServer(("0.0.0.0", 8080), ReverseProxyHandler).serve_forever()
```

## Java Implementation

```java
import com.sun.net.httpserver.*;
import java.io.*;
import java.net.*;
import java.util.Map;
import java.util.regex.*;

public class ReverseProxy {
    private static final Map<String, String> ROUTES = Map.of(
        "/api/", "http://localhost:8081",
        "/static/", "http://localhost:8082"
    );

    static String route(String path) {
        return ROUTES.entrySet().stream()
            .filter(e -> path.startsWith(e.getKey()))
            .map(Map.Entry::getValue)
            .findFirst().orElse("http://localhost:8080");
    }

    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);
        server.createContext("/", exchange -> {
            String path = exchange.getRequestURI().getPath();
            URL url = new URL(route(path) + path);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestProperty("X-Forwarded-For",
                exchange.getRemoteAddress().getAddress().getHostAddress());
            byte[] body = conn.getInputStream().readAllBytes();
            exchange.sendResponseHeaders(conn.getResponseCode(), body.length);
            exchange.getResponseBody().write(body);
            exchange.close();
        });
        server.start();
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Route matching | O(routes) |
| Proxy pass | O(1) + network I/O |
| Gzip compression | O(n) response size |
| SSL termination | O(1) amortized |

## Common Questions & Answers

**Q: What is caching and why do we need it?**

A: Caching stores frequently accessed data in fast storage (memory) to reduce latency and load on slower backends (database). Trade space (cache) for speed (latency). Critical for systems serving millions of requests per second.

**Q: What are the main cache eviction policies?**

A: LRU (least recently used), LFU (least frequently used), FIFO (first in first out), TTL (time-based), Random, and ARC (adaptive replacement). Choose based on access patterns: LRU for temporal, LFU for frequency, TTL for time-sensitive data.

**Q: What is cache hit rate and cache miss rate?**

A: Hit rate = successful_finds / total_accesses. Miss rate = 1 - hit rate. P(hit) = hits / (hits + misses). Target 80%+ hit rates for effective caching. Too-small cache gives low hit rate (wasted resources). Too-large cache uses more memory than needed.

**Q: How do you handle cache invalidation when backend data changes?**

A: Use TTL (time-based expiration), active invalidation (notify cache on write), cache-aside pattern (client checks backend), or write-through (update both). Active invalidation is fastest but complex. TTL is simplest but has stale data window.

**Q: What is the cache-aside pattern?**

A: Application checks cache first. On miss, fetch from backend, update cache, then return. Simple to implement. Risk: race condition where multiple threads fetch same miss simultaneously (thundering herd problem).

**Q: What is write-through caching?**

A: Writes go to both cache and backend simultaneously (synchronously). Ensures consistency: read always gets latest. Cost: write latency includes backend write. Safer than write-back but slower.

**Q: What is write-back (write-behind) caching?**

A: Writes go to cache only; backend updated asynchronously later (batch or periodic). Fast writes. Risk: data loss if cache fails before flushing. Need durability guarantees (persistence, replication).

**Q: How do you choose cache size?**

A: Estimate working set (frequently accessed data volume). Add 20-30% buffer for margin. Monitor hit rate: if < 80%, increase size. If > 95%, might be oversized (waste). Use tools like cachegrind to profile.

**Q: What's the difference between client-side and server-side caching?**

A: Client cache (browser): reduces network round-trips, entirely controlled by client. Server cache (memory, Redis): shared across clients, controlled by server. Multi-level caching often best.

**Q: How do you measure cache effectiveness?**

A: Hit rate (primary metric), latency reduction (P99 latency with vs. without cache), backend load reduction, and memory cost per cache entry. Calculate ROI: cost of cache vs. benefit (reduced latency, backend load).

## Follow-up Questions & Answers

**Q: How do you prevent the thundering herd problem in caches?**

A: When popular key expires, many threads fetch from backend simultaneously causing spike. Solutions: probabilistic early expiration (refresh before TTL), request coalescing (single thread rebuilds, others wait), or bloom filters (detect non-existent keys fast).

**Q: How would you implement multi-level cache hierarchy?**

A: Use L1 (fast, small, in-process), L2 (medium, local machine), L3 (large, remote, Redis). Check L1, miss→L2, miss→L3, miss→backend. On write: update all levels. Trade space for speed across levels.

**Q: Can you implement read-through caching (automatic population)?**

A: Yes, cache loader/resolver called on miss. Transparent to application. Backend automatically uses cache layer. More complex than cache-aside but cleaner separation.

**Q: How do you handle hot keys in distributed caches?**

A: Hot key = key accessed by many threads/clients. Replicate hot keys on multiple cache nodes. Use local in-process caches for very hot keys. Monitor and detect hot keys automatically.

**Q: What's the difference between warm and cold cache startup?**

A: Cold cache: empty at start, misses until populated (slow ramp-up). Warm cache: pre-loaded from previous state (RDB/snapshot). Warm startup is critical for production (instant performance).

**Q: How would you measure cache effectiveness for business metrics?**

A: Track hit rate, P99 latency (with/without cache), backend QPS reduction, revenue impact. Calculate cache size vs. cost savings. A/B test to prove business value.

**Q: What happens when cache size is insufficient for working set?**

A: Constant evictions = high miss rate = ineffective cache. Solution: increase cache size, improve eviction policy, reduce working set, or use better hardware (faster storage).

**Q: How do you debug cache issues in production?**

A: Monitor hit rate continuously. Profile cache keys (which keys are accessed). Check for cache stampedes (sudden miss spike). Use distributed tracing to see cache path.

**Q: How would you implement a persistent cache?**

A: Combine memory cache (fast) with persistent backend (database, RocksDB, LevelDB). Write-back pattern: batch updates to persistent store. Trade latency for durability.

**Q: Can you use caching for write-heavy workloads?**

A: Write caching is risky (consistency issues). Use carefully: write-through for safety, write-back for speed. Good for batch writes (aggregate before writing). Monitor durability guarantees.

