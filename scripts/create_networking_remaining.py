#!/usr/bin/env python3
"""Create remaining 11 networking concept files."""

import os

BASE = "docs/system_design/16-networking"
os.makedirs(BASE, exist_ok=True)

FILES = {
"05_load_balancer_l4_l7.md": """# Load Balancer: Layer 4 vs Layer 7

## Problem Statement

Design a load balancer that distributes incoming traffic across multiple backend servers to maximize availability and throughput.

**Requirements:**
- Distribute requests evenly
- Detect and route around unhealthy backends
- Support sticky sessions, SSL termination
- Handle 1M+ connections/sec

## Architecture Diagram

```mermaid
graph TB
    Client[Clients]
    LB4[L4 Load Balancer TCP/UDP]
    LB7[L7 Load Balancer HTTP/HTTPS]

    S1[Server 1]
    S2[Server 2]
    S3[Server 3]

    Client -->|TCP SYN| LB4
    LB4 -->|Forward TCP stream| LB7
    LB7 -->|Route by URL/Header/Cookie| S1
    LB7 --> S2
    LB7 --> S3
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant L7 as L7 LB nginx
    participant B1 as Backend 1
    participant B2 as Backend 2

    C->>L7: POST /api/orders (HTTP)
    L7->>L7: Parse URL, headers, cookie
    L7->>L7: Select backend (round-robin)
    L7->>B1: Forward request
    B1-->>L7: 201 Created
    L7-->>C: 201 Created

    Note over L7: Health check every 5s
    L7->>B2: GET /health
    B2-->>L7: 200 OK
```

## Design

### L4 vs L7 Comparison

| Feature | L4 (Transport) | L7 (Application) |
|---|---|---|
| Protocol | TCP/UDP | HTTP/HTTPS/gRPC |
| Visibility | IP + port only | URL, headers, cookies |
| SSL | Pass-through or terminate | Always terminate |
| Routing | IP/port hash | Content-based |
| Performance | Higher (no parsing) | Slightly lower |
| Sticky sessions | IP-hash | Cookie-based |
| Use case | Raw TCP, databases | Web APIs |

### Algorithms

```
Round Robin       — Even distribution, simple
Weighted RR       — Server capacity-aware
Least Connections — Route to backend with fewest active conns
IP Hash           — Same client → same backend (sticky)
Random            — Simple, surprisingly effective at scale
Least Response    — Route to fastest responding backend
```

### Health Checks

```
Active:  LB pings /health every N seconds
Passive: Monitor real traffic — mark down on errors
Types:   TCP connect, HTTP 200, custom script
Thresholds: 2 failures → mark down, 3 successes → mark up
```

## Common Questions & Answers

**Q: What is DSR (Direct Server Return)?** A: Backend sends response directly to client, bypassing LB. LB only handles inbound. Reduces LB bandwidth 10-100x for high-throughput (video, downloads).

**Q: Sticky sessions vs stateless?** A: Sticky (cookie/IP-hash) ties user to one backend — breaks on backend failure. Stateless (session in Redis/DB) is more resilient; prefer it.

**Q: How does AWS ELB work?** A: ALB (Application) = L7, NLB (Network) = L4. NLB handles millions of connections/sec, preserves source IP. ALB adds routing rules, WAF integration.

**Q: What is connection draining?** A: When removing a backend, LB stops sending new requests but lets existing connections complete (grace period: 30-300s). Prevents in-flight request failures.

## Back-of-Envelope Calculations

```
Load balancer capacity:
  Nginx: 50,000 concurrent connections per core
  HAProxy: 100,000 connections/sec per core
  AWS NLB: millions of connections/sec (managed)

Health check overhead:
  100 backends × 1 check/5s = 20 checks/sec (negligible)

Latency added by L7 LB:
  Parse HTTP headers: ~0.1ms
  Backend selection: ~0.01ms
  Total LB overhead: ~0.5ms

Bandwidth for L7 LB:
  Both inbound AND outbound flow through LB
  1M req/sec × 10KB avg = 10 GB/s through single LB
  DSR eliminates outbound: reduces to 1 GB/s (10KB request only)
```

## Design Choices

| Approach | Pros | Cons |
|---|---|---|
| L4 (NLB) | Ultra-high throughput | No content routing |
| L7 (ALB) | Smart routing, WAF | More CPU overhead |
| DSR | Saves LB bandwidth | Complex network config |
| Active health checks | Proactive | False positives possible |
| Consistent hashing | Minimize cache misses | Rebalancing on change |

## Follow-up Questions

1. How would you implement a global load balancer (GLB) across regions?
2. Design a LB that supports WebSocket connections.
3. How does Kubernetes' kube-proxy implement L4 load balancing?
4. How do you prevent a single backend from receiving too much traffic?
5. What is GSLB (Global Server Load Balancing)?

## Python Implementation

```python
from typing import List, Optional
from collections import defaultdict
import time
import random
import itertools

class Backend:
    def __init__(self, host: str, port: int, weight: int = 1):
        self.host = host
        self.port = port
        self.weight = weight
        self.healthy = True
        self.active_conns = 0
        self.failures = 0
        self.last_check = 0.0

    def address(self) -> str:
        return f"{self.host}:{self.port}"

class LoadBalancer:
    def __init__(self, algorithm: str = "round_robin"):
        self._backends: List[Backend] = []
        self._algorithm = algorithm
        self._rr_iter = None

    def add_backend(self, backend: Backend):
        self._backends.append(backend)
        self._rr_iter = itertools.cycle(self._backends)

    def healthy_backends(self) -> List[Backend]:
        return [b for b in self._backends if b.healthy]

    def select(self) -> Optional[Backend]:
        healthy = self.healthy_backends()
        if not healthy:
            return None

        if self._algorithm == "round_robin":
            for _ in range(len(self._backends)):
                b = next(self._rr_iter)
                if b.healthy:
                    return b

        if self._algorithm == "least_connections":
            return min(healthy, key=lambda b: b.active_conns)

        if self._algorithm == "weighted_random":
            weights = [b.weight for b in healthy]
            return random.choices(healthy, weights=weights)[0]

        if self._algorithm == "random":
            return random.choice(healthy)

        return healthy[0]

    def mark_down(self, backend: Backend):
        backend.healthy = False
        backend.failures += 1
        print(f"[LB] Backend {backend.address()} marked DOWN")

    def mark_up(self, backend: Backend):
        backend.healthy = True
        backend.failures = 0
        print(f"[LB] Backend {backend.address()} marked UP")

    def handle_request(self, path: str) -> str:
        backend = self.select()
        if not backend:
            return "503 Service Unavailable"
        backend.active_conns += 1
        try:
            response = f"200 OK from {backend.address()}"
        finally:
            backend.active_conns -= 1
        return response

# Usage
lb = LoadBalancer(algorithm="least_connections")
for i in range(1, 4):
    lb.add_backend(Backend(f"10.0.0.{i}", 8080, weight=i))

for _ in range(6):
    print(lb.handle_request("/api/data"))

lb.mark_down(lb._backends[0])
print(lb.handle_request("/api/data"))
```

## Java Implementation

```java
import java.util.*;
import java.util.concurrent.atomic.*;

public class LoadBalancer {
    record Backend(String host, int port, AtomicInteger conns, volatile boolean healthy) {
        Backend(String host, int port) { this(host, port, new AtomicInteger(0), true); }
        String address() { return host + ":" + port; }
    }

    private List<Backend> backends = new ArrayList<>();
    private AtomicInteger rrIndex = new AtomicInteger(0);

    public void addBackend(Backend b) { backends.add(b); }

    public Optional<Backend> selectLeastConnections() {
        return backends.stream().filter(b -> b.healthy())
            .min(Comparator.comparingInt(b -> b.conns().get()));
    }

    public Optional<Backend> selectRoundRobin() {
        List<Backend> healthy = backends.stream().filter(Backend::healthy).toList();
        if (healthy.isEmpty()) return Optional.empty();
        return Optional.of(healthy.get(rrIndex.getAndIncrement() % healthy.size()));
    }

    public String handle(String path) {
        return selectLeastConnections()
            .map(b -> {
                b.conns().incrementAndGet();
                String resp = "200 OK from " + b.address();
                b.conns().decrementAndGet();
                return resp;
            }).orElse("503 Service Unavailable");
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Round robin select | O(1) |
| Least connections | O(n) |
| Health check | O(backends) |
| Request routing | O(1) after selection |
""",

"06_reverse_proxy.md": """# Reverse Proxy

## Problem Statement

Design a reverse proxy that sits in front of backend servers to provide SSL termination, caching, compression, and request routing.

**Requirements:**
- Transparent to clients (looks like origin)
- SSL/TLS termination
- Request routing and rewriting
- Compression, caching, rate limiting

## Architecture Diagram

```mermaid
graph LR
    Client[Client]
    RP[Reverse Proxy nginx/HAProxy]
    API[API Service]
    Static[Static Assets Service]
    Auth[Auth Service]

    Client -->|HTTPS :443| RP
    RP -->|HTTP :8080 /api/*| API
    RP -->|HTTP :8081 /static/*| Static
    RP -->|HTTP :8082 /auth/*| Auth
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant RP as Reverse Proxy
    participant B as Backend

    C->>RP: HTTPS GET /api/users
    RP->>RP: Terminate TLS
    RP->>RP: Check rate limit
    RP->>RP: Route by path /api/* → backend:8080
    RP->>B: HTTP GET /api/users (X-Forwarded-For: client_ip)
    B-->>RP: 200 + JSON
    RP->>RP: Compress (gzip)
    RP->>RP: Add security headers
    RP-->>C: 200 + compressed response
```

## Design

### Nginx Configuration Patterns

```nginx
# SSL termination + proxy
server {
    listen 443 ssl;
    ssl_certificate /certs/cert.pem;
    ssl_certificate_key /certs/key.pem;

    location /api/ {
        proxy_pass http://api_backend;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header Host $host;
    }

    location /static/ {
        proxy_pass http://static_backend;
        proxy_cache_valid 200 1d;
        gzip on;
    }
}

upstream api_backend {
    least_conn;
    server 10.0.0.1:8080;
    server 10.0.0.2:8080;
}
```

### Reverse Proxy vs Forward Proxy

| | Reverse Proxy | Forward Proxy |
|---|---|---|
| Hides | Backend servers | Clients |
| Used by | Server operators | Clients/enterprises |
| Example | nginx, HAProxy | Squid, corporate proxy |
| Purpose | LB, SSL, caching | Content filtering, privacy |

## Common Questions & Answers

**Q: What headers does a reverse proxy add?** A: `X-Forwarded-For` (client IP), `X-Forwarded-Proto` (http/https), `X-Real-IP`, `X-Request-ID` (tracing).

**Q: How does nginx handle C10K?** A: Event-driven (epoll), async I/O. Single worker handles thousands of connections without per-connection threads.

**Q: What is proxy buffering?** A: Proxy buffers backend response in memory before sending to client. Frees backend connection faster. Disable for streaming/SSE.

**Q: Difference from API gateway?** A: Reverse proxy: lower-level routing, SSL, compression. API gateway: auth, rate limiting, request transformation, API versioning, developer portal.

## Back-of-Envelope Calculations

```
Nginx throughput:
  Single core: ~50K req/sec (simple proxying)
  4 cores: ~200K req/sec
  Memory: ~2.5KB per connection × 50K = 125MB

SSL termination overhead:
  Without AES-NI: 5-10% CPU per HTTPS request
  With AES-NI (modern CPUs): <1% overhead

Compression savings:
  JSON responses: 70-80% smaller with gzip
  1KB JSON → 200-300 bytes over wire
  100MB/s uncompressed → 20-30MB/s compressed

Connection reuse (keepalive):
  Without keepalive: TCP + TLS = 1.5 RTT per request
  With keepalive: 0 RTT for subsequent requests
  Reuse factor: 10 requests/connection saves 13.5 RTTs
```

## Design Choices

| Feature | Option A | Option B |
|---|---|---|
| SSL termination | At proxy | At backend (end-to-end) |
| Caching | At proxy (Nginx) | At CDN layer |
| Compression | At proxy | At backend |
| Auth | At API gateway | At backend |
| Buffering | On (default) | Off (streaming) |

## Follow-up Questions

1. How would you configure nginx for zero-downtime deployments?
2. How does HAProxy differ from nginx for load balancing?
3. What is mTLS and how does a reverse proxy support it?
4. How do you handle WebSocket connections through a reverse proxy?
5. Design a reverse proxy with per-client rate limiting.

## Python Implementation

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request as URLRequest
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
        backend = self._route(self.path)
        upstream_url = backend + self.path

        req = URLRequest(upstream_url)
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

        # Gzip compress
        accept_encoding = self.headers.get("Accept-Encoding", "")
        if "gzip" in accept_encoding:
            body = gzip.compress(body)
            self.send_response(status)
            self.send_header("Content-Encoding", "gzip")
        else:
            self.send_response(status)

        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Proxy", "python-reverse-proxy")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print(f"[PROXY] {self.path} → {self._route(self.path)}")

# Run: HTTPServer(("0.0.0.0", 443), ReverseProxyHandler).serve_forever()
```

## Java Implementation

```java
import com.sun.net.httpserver.*;
import java.io.*;
import java.net.*;
import java.util.Map;

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
            String backend = route(path);
            URL url = new URL(backend + path);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestProperty("X-Forwarded-For",
                exchange.getRemoteAddress().getAddress().getHostAddress());
            byte[] body = conn.getInputStream().readAllBytes();
            exchange.sendResponseHeaders(conn.getResponseCode(), body.length);
            exchange.getResponseBody().write(body);
            exchange.close();
        });
        server.start();
        System.out.println("Reverse proxy on :8080");
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Route matching | O(routes) |
| Proxy pass | O(1) + network |
| Compression | O(n) response size |
| SSL termination | O(1) amortized |
""",

"07_rest_graphql_grpc.md": """# REST vs GraphQL vs gRPC

## Problem Statement

Compare and choose between REST, GraphQL, and gRPC for different API use cases.

## Architecture Diagram

```mermaid
graph TB
    Client[Client]

    subgraph REST
        R[REST Server]
        R1[GET /users/1]
        R2[GET /users/1/posts]
        R3[GET /users/1/followers]
    end

    subgraph GraphQL
        GQL[GraphQL Server]
        Q1["query { user(id:1) { name posts { title } followers { name } } }"]
    end

    subgraph gRPC
        GR[gRPC Server]
        P1["UserService.GetUser(GetUserRequest{id:1})"]
    end

    Client --> REST
    Client --> GraphQL
    Client --> gRPC
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Mobile Client
    participant GQL as GraphQL Server
    participant US as User Service
    participant PS as Post Service

    C->>GQL: query { user(id:1) { name posts { title } } }
    GQL->>US: GetUser(1)
    US-->>GQL: {name: "Alice"}
    GQL->>PS: GetPostsByUser(1)
    PS-->>GQL: [{title: "Hello"}, ...]
    GQL-->>C: {user: {name: "Alice", posts: [...]}}
    Note over C,GQL: One round trip vs 2 REST calls
```

## Design

### REST

```
Principles: Resources, HTTP verbs, stateless, cacheable
GET    /users/{id}          → Get user
POST   /users               → Create user
PUT    /users/{id}          → Replace user
PATCH  /users/{id}          → Update user
DELETE /users/{id}          → Delete user

Problems:
  Over-fetching: endpoint returns more fields than needed
  Under-fetching: need N+1 requests for related data
```

### GraphQL

```
Single endpoint: POST /graphql
Client specifies exactly what data it needs
Schema defined in SDL (Schema Definition Language)
Resolvers fetch data per field

Benefits: No over/under fetching, strongly typed schema
Problems: Caching harder (POST), N+1 queries, complex tooling
```

### gRPC

```
Protocol Buffers: binary serialization (3-10x smaller than JSON)
HTTP/2: multiplexing, streaming
Bi-directional streaming supported
Strongly typed via .proto files
Code generation for 10+ languages

Benefits: High performance, streaming, strict contracts
Problems: Not human-readable, limited browser support
```

### Comparison

| Feature | REST | GraphQL | gRPC |
|---|---|---|---|
| Protocol | HTTP/1.1 | HTTP/1.1 | HTTP/2 |
| Serialization | JSON | JSON | Protobuf (binary) |
| Typing | None (OpenAPI optional) | Strongly typed | Strongly typed |
| Caching | HTTP cache (GET) | Complex | Not built-in |
| Streaming | SSE/WebSocket | Subscriptions | Native streaming |
| Browser support | Native | Native | Limited (grpc-web) |
| Performance | Medium | Medium | High |
| Learning curve | Low | Medium | Medium |
| Best for | Public APIs | Mobile, complex queries | Internal microservices |

## Common Questions & Answers

**Q: When to use REST over GraphQL?** A: Public APIs (simpler to document/consume), simple CRUD, when HTTP caching is important, small teams.

**Q: GraphQL N+1 problem?** A: Each resolver fires independently — 1 query for list + N queries for each item. Solution: DataLoader (batch + cache within request).

**Q: What makes gRPC fast?** A: HTTP/2 (multiplexing), Protobuf (binary, smaller, faster), connection reuse, streaming.

**Q: Can you mix them?** A: Yes. Public REST API + internal gRPC + mobile GraphQL is common pattern (BFF — Backend for Frontend).

**Q: GraphQL vs REST for real-time?** A: GraphQL subscriptions (WebSocket) vs REST + SSE or WebSocket. Both work; GraphQL has better tooling.

## Back-of-Envelope Calculations

```
Payload size comparison (user + 10 posts):
  REST (2 calls, over-fetching): 5KB
  GraphQL (1 call, exact fields): 1KB
  gRPC (binary): 300 bytes

Requests saved with GraphQL (mobile):
  Profile page: 5 REST calls → 1 GraphQL query
  At 1M users × 10 profile loads/day = 10M calls/day
  GraphQL saves 8M calls/day = 80% reduction

gRPC vs REST throughput:
  JSON parsing: ~300MB/s
  Protobuf parsing: ~1.5GB/s (5x faster)
  At 100K req/sec, 1KB each: 100MB/s (gRPC wins significantly)

GraphQL schema validation overhead:
  Schema parse: once at startup
  Query validation: ~1ms per query
  Acceptable for < 10K req/sec
```

## Design Choices

| Scenario | Recommendation |
|---|---|
| Public web API | REST |
| Mobile apps with complex data needs | GraphQL |
| Internal microservice communication | gRPC |
| Real-time features | GraphQL subscriptions / gRPC streaming |
| Simple CRUD | REST |
| High throughput internal | gRPC |

## Follow-up Questions

1. How do you version a REST API without breaking clients?
2. How does DataLoader solve the GraphQL N+1 problem?
3. What is gRPC server streaming vs client streaming vs bidirectional?
4. How do you secure a GraphQL API against introspection attacks?
5. Design a BFF (Backend for Frontend) pattern.

## Python Implementation

```python
# REST
from flask import Flask, jsonify, request

app = Flask(__name__)
users_db = {1: {"id": 1, "name": "Alice", "email": "alice@example.com"}}

@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = users_db.get(user_id)
    if not user:
        return jsonify({"error": "Not found"}), 404
    return jsonify(user)

@app.route("/users", methods=["POST"])
def create_user():
    data = request.json
    user_id = max(users_db.keys()) + 1
    users_db[user_id] = {"id": user_id, **data}
    return jsonify(users_db[user_id]), 201

# GraphQL (simplified resolver pattern)
class GraphQLResolver:
    def __init__(self):
        self.users = {1: {"id": 1, "name": "Alice"}}
        self.posts = {1: [{"title": "Hello"}, {"title": "World"}]}

    def resolve(self, query: dict) -> dict:
        result = {}
        if "user" in query:
            uid = query["user"]["id"]
            user = self.users.get(uid, {}).copy()
            if "posts" in query["user"].get("fields", []):
                user["posts"] = self.posts.get(uid, [])
            result["user"] = user
        return result

resolver = GraphQLResolver()
print(resolver.resolve({"user": {"id": 1, "fields": ["posts"]}}))

# gRPC-style (protocol buffer simulation)
from dataclasses import dataclass
from typing import List

@dataclass
class GetUserRequest:
    user_id: int

@dataclass
class UserResponse:
    id: int
    name: str

class UserServiceStub:
    def GetUser(self, request: GetUserRequest) -> UserResponse:
        return UserResponse(id=request.user_id, name="Alice")

stub = UserServiceStub()
resp = stub.GetUser(GetUserRequest(user_id=1))
print(resp)  # UserResponse(id=1, name='Alice')
```

## Java Implementation

```java
// REST endpoint (Spring-style)
public class UserController {
    private Map<Integer, Map<String, Object>> db = Map.of(
        1, Map.of("id", 1, "name", "Alice")
    );

    public Map<String, Object> getUser(int id) {
        return db.getOrDefault(id, Map.of("error", "not found"));
    }
}

// gRPC-style with protobuf simulation
public class UserServiceImpl {
    record GetUserRequest(int userId) {}
    record UserResponse(int id, String name) {}

    public UserResponse getUser(GetUserRequest req) {
        return new UserResponse(req.userId(), "Alice");
    }

    public static void main(String[] args) {
        UserServiceImpl svc = new UserServiceImpl();
        System.out.println(svc.getUser(new GetUserRequest(1)));
    }
}
```

## Complexity

| Metric | REST | GraphQL | gRPC |
|---|---|---|---|
| Request overhead | Medium (HTTP/1.1 headers) | Medium | Low (HTTP/2 + binary) |
| Server CPU | Low | Medium (resolver, validation) | Low |
| Network bytes | High (JSON, over-fetch) | Medium (exact fields) | Low (Protobuf) |
""",

"08_http2_http3_quic.md": """# HTTP/2, HTTP/3, and QUIC

## Problem Statement

Understand the evolution of HTTP protocols and how HTTP/3 (QUIC) solves fundamental TCP limitations for modern web applications.

## Architecture Diagram

```mermaid
graph TB
    subgraph HTTP1["HTTP/1.1"]
        H1C[Client]
        H1S[Server]
        H1C -->|Request 1| H1S
        H1S -->|Response 1| H1C
        H1C -->|Request 2 wait| H1S
    end

    subgraph HTTP2["HTTP/2"]
        H2C[Client]
        H2S[Server]
        H2C -->|Stream 1 + Stream 2 + Stream 3| H2S
        H2S -->|Multiplexed responses| H2C
    end

    subgraph HTTP3["HTTP/3 QUIC"]
        H3C[Client]
        H3S[Server]
        H3C -->|UDP datagrams per stream| H3S
        H3S -->|No HOL blocking| H3C
    end
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    Note over C,S: HTTP/2 Multiplexing
    C->>S: HEADERS frame (stream 1): GET /html
    C->>S: HEADERS frame (stream 3): GET /css
    C->>S: HEADERS frame (stream 5): GET /js
    S-->>C: DATA frame (stream 1): HTML
    S-->>C: DATA frame (stream 3): CSS
    S-->>C: DATA frame (stream 5): JS
    Note over C,S: All in-flight simultaneously on one TCP connection

    Note over C,S: HTTP/3 0-RTT Connection
    C->>S: QUIC Initial + ClientHello + GET /html (0-RTT)
    S-->>C: QUIC response (no TCP handshake needed)
```

## Design

### HTTP Evolution

```
HTTP/1.0 — New TCP connection per request
HTTP/1.1 — Keep-alive, pipelining (but HOL blocking)
HTTP/2   — Binary framing, multiplexing, header compression (HPACK),
           server push. Still over TCP (HOL blocking at TCP layer)
HTTP/3   — QUIC (UDP-based), per-stream reliability, 0-RTT connection,
           connection migration (IP change doesn't break connection)
```

### HTTP/2 Features

```
Multiplexing    — Multiple streams over single TCP connection
Header compression (HPACK) — Huffman + reference table, reduces header size 30-80%
Server Push     — Server sends resources before client requests (controversial, deprecated)
Stream priority — Weight-based priority for resource loading
Binary framing  — Efficient parsing, no text ambiguity
```

### QUIC (HTTP/3)

```
Built on UDP instead of TCP
Per-stream reliability — loss in stream A doesn't block stream B
0-RTT resumption — Send data immediately on reconnect
Connection IDs  — Connection survives IP change (mobile handoff)
Built-in TLS 1.3 — No separate TLS handshake
```

### Protocol Comparison

| Feature | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---|---|---|---|
| Transport | TCP | TCP | UDP (QUIC) |
| HOL blocking | Yes | TCP level | No |
| Connections | 6 per origin | 1 per origin | 1 per origin |
| Header compression | None | HPACK | QPACK |
| 0-RTT | No | No | Yes |
| Connection migration | No | No | Yes |
| TLS | Separate | Separate | Built-in |

## Common Questions & Answers

**Q: Why did HTTP/2 server push get deprecated?** A: Servers couldn't know what client already has cached. Chrome removed it in 2022; alternatives: 103 Early Hints, Link preload headers.

**Q: HOL blocking in HTTP/2?** A: Within a single TCP connection, if a packet is lost, all streams wait. HTTP/2 solved application-level HOL but not TCP-level. QUIC solves both.

**Q: What is 0-RTT and its risk?** A: Client sends data in first packet (no handshake). Risk: replay attacks — attacker replays the 0-RTT data. Mitigate: idempotent requests only, anti-replay tokens.

**Q: When not to use HTTP/2?** A: Lossy networks where multiplexing amplifies HOL blocking vs separate TCP connections. Low-latency APIs where a single request benefits from simple HTTP/1.1.

**Q: What is connection migration in QUIC?** A: Connection identified by connection ID (not IP:port). When device changes network (WiFi to 4G), QUIC continues the connection. TCP would break.

## Back-of-Envelope Calculations

```
Header compression savings:
  HTTP/1.1 headers: ~800 bytes average
  HTTP/2 HPACK: ~50-100 bytes after first request
  Savings: 85-90% on subsequent requests
  At 100K req/sec: 70MB/s saved just on headers

Connection reduction:
  HTTP/1.1: browser opens 6 TCP connections per origin
  HTTP/2: 1 connection per origin
  Saves: 5 × 1.5 RTT = 7.5 RTT handshakes per origin
  At 50ms RTT: saves 375ms initial load time

HTTP/3 latency improvement over lossy networks:
  1% packet loss, HTTP/2: all streams stall
  1% packet loss, HTTP/3: only affected stream stalls
  Real-world improvement: 3-15% faster page loads (Google data)

0-RTT savings:
  TLS 1.3 standard: 1 RTT
  0-RTT resumption: 0 RTT
  At 100ms RTT: saves 100ms per reconnect
```

## Design Choices

| Scenario | Protocol |
|---|---|
| Public web, many resources | HTTP/2 or HTTP/3 |
| High packet loss (mobile) | HTTP/3 |
| Simple API, low latency | HTTP/1.1 or HTTP/2 |
| Internal microservices | gRPC (HTTP/2) |
| File download | HTTP/2 or HTTP/1.1 |
| Real-time (streaming) | HTTP/2 push or WebSocket |

## Follow-up Questions

1. How does HPACK header compression prevent CRIME attacks?
2. How does connection migration in QUIC work at the packet level?
3. Design a content negotiation system that selects HTTP version.
4. How do CDNs support HTTP/3?
5. What is HTTP prioritization and how does it affect perceived page load?

## Python Implementation

```python
import asyncio
import ssl
from typing import Optional

# Simulate HTTP/2 multiplexing with asyncio streams
class HTTP2Stream:
    def __init__(self, stream_id: int):
        self.stream_id = stream_id
        self.headers: dict = {}
        self.body: bytes = b""
        self.state = "idle"

class HTTP2Connection:
    def __init__(self):
        self._streams: dict[int, HTTP2Stream] = {}
        self._next_id = 1

    def open_stream(self) -> HTTP2Stream:
        stream = HTTP2Stream(self._next_id)
        self._streams[self._next_id] = stream
        self._next_id += 2  # Client uses odd IDs
        return stream

    async def send_request(self, path: str, method: str = "GET") -> dict:
        stream = self.open_stream()
        stream.headers = {":method": method, ":path": path, ":scheme": "https"}
        stream.state = "open"
        # Simulate network delay
        await asyncio.sleep(0.01)
        stream.state = "half_closed"
        return {"stream_id": stream.stream_id, "path": path, "status": 200}

async def demonstrate_multiplexing():
    conn = HTTP2Connection()
    # Send 3 requests concurrently over single connection
    results = await asyncio.gather(
        conn.send_request("/html"),
        conn.send_request("/css"),
        conn.send_request("/js"),
    )
    for r in results:
        print(f"Stream {r['stream_id']}: {r['path']} → {r['status']}")

asyncio.run(demonstrate_multiplexing())

# HPACK header compression simulation
class HPackCompressor:
    STATIC_TABLE = {
        ":method: GET": 2,
        ":method: POST": 3,
        ":path: /": 4,
        ":scheme: https": 7,
        ":status: 200": 8,
        ":status: 404": 13,
    }

    def __init__(self):
        self._dynamic_table: list[tuple[str, str]] = []
        self._cached: dict[str, int] = {}

    def compress(self, headers: dict[str, str]) -> bytes:
        compressed = bytearray()
        for k, v in headers.items():
            key = f"{k}: {v}"
            if key in self.STATIC_TABLE:
                compressed.append(self.STATIC_TABLE[key])  # 1 byte!
            elif key in self._cached:
                compressed.append(self._cached[key])
            else:
                encoded = key.encode()
                compressed.extend([0x40, len(encoded)] + list(encoded))
                self._dynamic_table.append((k, v))
        return bytes(compressed)

hpack = HPackCompressor()
h = {":method": "GET", ":path": "/", ":scheme": "https"}
compressed = hpack.compress(h)
original = str(h).encode()
print(f"Original: {len(original)}B → Compressed: {len(compressed)}B ({len(compressed)/len(original)*100:.0f}%)")
```

## Java Implementation

```java
import java.util.concurrent.*;
import java.util.*;

public class HTTP2Simulation {
    record Stream(int id, String path, CompletableFuture<String> response) {}

    static class Connection {
        private Map<Integer, Stream> streams = new ConcurrentHashMap<>();
        private int nextId = 1;

        public Stream openStream(String path) {
            CompletableFuture<String> resp = CompletableFuture.supplyAsync(() -> {
                try { Thread.sleep(10); } catch (InterruptedException e) {}
                return "200 OK for " + path;
            });
            Stream s = new Stream(nextId, path, resp);
            streams.put(nextId, s);
            nextId += 2;
            return s;
        }
    }

    public static void main(String[] args) throws Exception {
        Connection conn = new Connection();
        // Multiplexed requests
        Stream s1 = conn.openStream("/html");
        Stream s2 = conn.openStream("/css");
        Stream s3 = conn.openStream("/js");

        CompletableFuture.allOf(s1.response(), s2.response(), s3.response()).join();
        System.out.println(s1.response().get());
        System.out.println(s2.response().get());
        System.out.println(s3.response().get());
    }
}
```

## Complexity

| Metric | HTTP/1.1 | HTTP/2 | HTTP/3 |
|---|---|---|---|
| RTTs to first byte | 2 (TCP+TLS) | 2 | 0 (0-RTT resume) |
| Concurrent streams | 6 connections | Unlimited | Unlimited |
| Header size | 200-800B | 20-100B | 20-100B |
| HOL blocking | Yes | TCP-level | No |
""",

"09_websockets_sse.md": """# WebSockets and Server-Sent Events

## Problem Statement

Design real-time communication channels between clients and servers — WebSockets for bidirectional, SSE for server-to-client push.

**Requirements:**
- Sub-100ms message delivery
- Support 100K+ concurrent connections per server
- Survive network interruptions (reconnect)
- Fan-out messages to multiple subscribers

## Architecture Diagram

```mermaid
graph TB
    C1[Client 1]
    C2[Client 2]
    C3[Client 3]

    WS[WebSocket Server]
    PS[PubSub Redis]
    WS2[WebSocket Server 2]

    C1 -->|WebSocket conn| WS
    C2 -->|WebSocket conn| WS
    C3 -->|WebSocket conn| WS2

    WS -->|Publish event| PS
    PS -->|Subscribe fan-out| WS
    PS -->|Subscribe fan-out| WS2
    WS -->|Push to C1, C2| C1
    WS2 -->|Push to C3| C3
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant S as WebSocket Server

    C->>S: HTTP GET /ws (Upgrade: websocket)
    S-->>C: 101 Switching Protocols
    Note over C,S: Connection upgraded — full-duplex

    C->>S: Frame: {"type": "subscribe", "room": "chat-1"}
    S-->>C: Frame: {"type": "ack"}

    Note over S: Another user sends message
    S-->>C: Frame: {"type": "message", "text": "Hello!"}
    C->>S: Frame: {"type": "message", "text": "Hi back!"}

    C->>S: Close frame
    S-->>C: Close frame
    Note over C,S: Graceful teardown
```

## Design

### WebSocket vs SSE vs Long Polling

| Feature | WebSocket | SSE | Long Polling |
|---|---|---|---|
| Direction | Bidirectional | Server→Client | Server→Client |
| Protocol | WS (TCP upgrade) | HTTP | HTTP |
| Browser support | All | All (no IE) | All |
| Reconnect | Manual | Automatic | Manual |
| Proxy/firewall | Sometimes blocked | Works fine | Works fine |
| Use case | Chat, games, collab | Notifications, feeds | Legacy fallback |

### WebSocket Frame Format

```
Fin(1) | RSV(3) | Opcode(4) | Mask(1) | Payload len(7) | Extended len | Masking key | Payload

Opcodes:
  0x0 Continuation  0x1 Text  0x2 Binary
  0x8 Close         0x9 Ping  0xA Pong
```

### Scaling WebSockets

```
Problem: Connection is sticky to server (stateful)
Solution 1: Redis Pub/Sub — servers subscribe, fan-out to local clients
Solution 2: Kafka — events on topic, each server consumer
Solution 3: Horizontal scaling with consistent hashing on connection ID
```

## Common Questions & Answers

**Q: Why are WebSockets tricky to scale?** A: Each connection is long-lived and tied to one server. Load balancing a new request is fine; existing connections must stay on same server.

**Q: How does SSE reconnect?** A: Browser automatically reconnects after disconnect. Server sends `id: <seq>` with each event; client sends `Last-Event-ID` header on reconnect.

**Q: WebSocket vs HTTP/2 server push?** A: HTTP/2 push is one-way (server to client), deprecated. WebSocket is true bidirectional. For notifications, SSE over HTTP/2 is often simpler.

**Q: How many WebSocket connections per server?** A: Each is a TCP connection + file descriptor. Linux default: 65535 FDs. With tuning (ulimit, epoll): 100K-1M connections per server.

**Q: How to handle message ordering?** A: Single server: FIFO guaranteed. Multi-server: include sequence numbers, timestamp; client reorders. Kafka partition per user for ordered fan-out.

## Back-of-Envelope Calculations

```
WebSocket server capacity:
  Each connection: ~50KB memory (kernel buffers)
  100K connections: 5GB RAM → need dedicated large instance
  Message throughput: 100K × 100 msg/sec = 10M msg/sec

Redis Pub/Sub fan-out:
  1M subscribers, message to all
  Redis fan-out: ~100K msg/sec per Redis instance
  Need Redis Cluster with 10+ shards for 1M msg/sec

SSE connection overhead:
  HTTP/1.1: 1 TCP connection per SSE client
  HTTP/2: multiple SSE streams per connection
  At 100K users: 100K TCP connections (HTTP/1.1) vs ~10K (HTTP/2)

Heartbeat (ping/pong) overhead:
  Every 30s ping: 100K connections × 1 ping/30s = 3,333 pings/sec
  Negligible overhead, keeps connections alive through NAT/firewalls
```

## Design Choices

| Scenario | Choice | Reason |
|---|---|---|
| Chat application | WebSocket | Bidirectional messages |
| Live notifications | SSE | Simple, auto-reconnect |
| Collaborative editing | WebSocket | Low latency, OT/CRDT |
| Stock ticker | SSE | Server push only |
| Multiplayer game | WebSocket/UDP | Lowest latency |
| Status updates | Long polling | Firewall-friendly fallback |

## Follow-up Questions

1. How would you implement presence (online/offline) at scale?
2. How does Socket.IO handle WebSocket fallback?
3. Design a chat system that guarantees message ordering across servers.
4. How do you implement backpressure for slow WebSocket clients?
5. How do you handle WebSocket connections behind a load balancer?

## Python Implementation

```python
import asyncio
import json
from typing import Dict, Set, Optional
from collections import defaultdict

class WebSocketConnection:
    def __init__(self, conn_id: str, user_id: str):
        self.conn_id = conn_id
        self.user_id = user_id
        self._messages: asyncio.Queue = asyncio.Queue()
        self.subscriptions: Set[str] = set()

    async def send(self, message: dict):
        await self._messages.put(json.dumps(message))

    async def receive(self) -> Optional[str]:
        try:
            return await asyncio.wait_for(self._messages.get(), timeout=30.0)
        except asyncio.TimeoutError:
            return None

class WebSocketServer:
    def __init__(self):
        self._connections: Dict[str, WebSocketConnection] = {}
        self._rooms: Dict[str, Set[str]] = defaultdict(set)

    def connect(self, conn_id: str, user_id: str) -> WebSocketConnection:
        conn = WebSocketConnection(conn_id, user_id)
        self._connections[conn_id] = conn
        print(f"[WS] Connected: {conn_id} (user={user_id})")
        return conn

    def disconnect(self, conn_id: str):
        conn = self._connections.pop(conn_id, None)
        if conn:
            for room in conn.subscriptions:
                self._rooms[room].discard(conn_id)
        print(f"[WS] Disconnected: {conn_id}")

    def join_room(self, conn_id: str, room: str):
        conn = self._connections[conn_id]
        conn.subscriptions.add(room)
        self._rooms[room].add(conn_id)

    async def broadcast(self, room: str, message: dict, exclude: Optional[str] = None):
        tasks = []
        for conn_id in self._rooms.get(room, set()):
            if conn_id == exclude:
                continue
            conn = self._connections.get(conn_id)
            if conn:
                tasks.append(conn.send(message))
        await asyncio.gather(*tasks)

    async def handle_message(self, conn_id: str, raw: str):
        data = json.loads(raw)
        msg_type = data.get("type")

        if msg_type == "join":
            self.join_room(conn_id, data["room"])
            conn = self._connections[conn_id]
            await conn.send({"type": "joined", "room": data["room"]})

        elif msg_type == "message":
            room = data.get("room")
            if room:
                await self.broadcast(room, {
                    "type": "message",
                    "from": conn_id,
                    "text": data["text"],
                }, exclude=conn_id)

# SSE implementation
class SSEServer:
    def __init__(self):
        self._clients: Dict[str, asyncio.Queue] = {}
        self._seq = 0

    def subscribe(self, client_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self._clients[client_id] = q
        return q

    def unsubscribe(self, client_id: str):
        self._clients.pop(client_id, None)

    async def publish(self, event: str, data: dict):
        self._seq += 1
        message = f"id: {self._seq}\\nevent: {event}\\ndata: {json.dumps(data)}\\n\\n"
        tasks = [q.put(message) for q in self._clients.values()]
        await asyncio.gather(*tasks)

    async def stream(self, client_id: str):
        q = self._clients.get(client_id)
        while q:
            yield await q.get()

# Usage simulation
async def demo():
    server = WebSocketServer()
    c1 = server.connect("c1", "alice")
    c2 = server.connect("c2", "bob")
    server.join_room("c1", "general")
    server.join_room("c2", "general")

    await server.handle_message("c1", json.dumps({
        "type": "message", "room": "general", "text": "Hello!"
    }))
    msg = await c2.receive()
    print(json.loads(msg))  # {'type': 'message', 'from': 'c1', 'text': 'Hello!'}

asyncio.run(demo())
```

## Java Implementation

```java
import java.util.*;
import java.util.concurrent.*;

public class WebSocketServer {
    record Connection(String id, String userId, BlockingQueue<String> outbox, Set<String> rooms) {}

    private Map<String, Connection> connections = new ConcurrentHashMap<>();
    private Map<String, Set<String>> rooms = new ConcurrentHashMap<>();

    public Connection connect(String connId, String userId) {
        Connection c = new Connection(connId, userId, new LinkedBlockingQueue<>(), ConcurrentHashMap.newKeySet());
        connections.put(connId, c);
        return c;
    }

    public void joinRoom(String connId, String room) {
        connections.get(connId).rooms().add(room);
        rooms.computeIfAbsent(room, k -> ConcurrentHashMap.newKeySet()).add(connId);
    }

    public void broadcast(String room, String message, String exclude) {
        rooms.getOrDefault(room, Set.of()).stream()
            .filter(id -> !id.equals(exclude))
            .map(connections::get).filter(Objects::nonNull)
            .forEach(c -> c.outbox().offer(message));
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Connect/disconnect | O(1) |
| Join room | O(1) |
| Broadcast to room | O(n) subscribers |
| Send to connection | O(1) |
| Memory per connection | ~50KB (kernel buffers) |
""",

"10_nat_ip_routing.md": """# NAT and IP Routing

## Problem Statement

Understand how Network Address Translation (NAT) enables private IP networks and how IP routing directs packets across the internet.

## Architecture Diagram

```mermaid
graph LR
    PC1["PC1\\n192.168.1.10"]
    PC2["PC2\\n192.168.1.11"]
    Router["NAT Router\\nPrivate: 192.168.1.1\\nPublic: 203.0.113.5"]
    ISP["ISP Router"]
    Internet["Internet"]
    Server["Server\\n93.184.216.34"]

    PC1 -->|Private IP| Router
    PC2 -->|Private IP| Router
    Router -->|NAT: rewrite src IP| ISP
    ISP --> Internet
    Internet --> Server
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant PC as PC 192.168.1.10
    participant NAT as NAT Router
    participant S as Server 93.184.216.34

    PC->>NAT: SYN src=192.168.1.10:5000 dst=93.184.216.34:80
    NAT->>NAT: Add NAT table entry: (192.168.1.10:5000 → 203.0.113.5:40001)
    NAT->>S: SYN src=203.0.113.5:40001 dst=93.184.216.34:80
    S-->>NAT: SYN-ACK dst=203.0.113.5:40001
    NAT->>NAT: Lookup: 203.0.113.5:40001 → 192.168.1.10:5000
    NAT-->>PC: SYN-ACK dst=192.168.1.10:5000
```

## Design

### NAT Table

```
Private IP:Port       Public IP:Port        Protocol  State
192.168.1.10:5000 → 203.0.113.5:40001   TCP       ESTABLISHED
192.168.1.11:6000 → 203.0.113.5:40002   TCP       ESTABLISHED
192.168.1.10:5001 → 203.0.113.5:40003   UDP       -
```

### IP Routing (Longest Prefix Match)

```
Routing table:
  10.0.0.0/8     → interface eth1
  10.0.1.0/24    → interface eth2   (more specific)
  192.168.0.0/16 → interface eth3
  0.0.0.0/0      → gateway (default route)

Lookup for 10.0.1.5:
  Matches: 10.0.0.0/8 (prefix=8)
  Matches: 10.0.1.0/24 (prefix=24) — LONGEST WIN
  Route via eth2
```

### Private IP Ranges (RFC 1918)

```
10.0.0.0/8      — 16M addresses
172.16.0.0/12   — 1M addresses
192.168.0.0/16  — 65K addresses
```

## Common Questions & Answers

**Q: What is CGNAT?** A: Carrier-Grade NAT — ISPs NAT multiple customers behind shared public IPs. Breaks peer-to-peer, complicates logging (IP alone doesn't identify user, need port too).

**Q: NAT traversal for P2P?** A: STUN (discover public IP:port), TURN (relay if STUN fails), ICE (tries both). Used by WebRTC.

**Q: What is a /24 subnet?** A: 255.255.255.0 mask = 24 bits network + 8 bits host = 256 addresses (254 usable). A /16 = 65536 addresses.

**Q: IPv4 vs IPv6?** A: IPv4: 4.3B addresses (exhausted). IPv6: 340 undecillion addresses, no NAT needed. Transition via dual-stack and tunneling.

**Q: What is CIDR?** A: Classless Inter-Domain Routing — replaces class A/B/C with variable-length prefix notation (10.0.0.0/22 = 1024 IPs).

## Back-of-Envelope Calculations

```
IPv4 exhaustion:
  Total: 2^32 = 4.3B addresses
  Reserved: ~600M (private, loopback, multicast)
  Usable public: ~3.7B
  Internet-connected devices: ~15B+ → NAT essential

NAT port capacity:
  65535 ports per public IP
  Typical connection duration: 60s (TCP) or 30s (UDP timeout)
  Connections/sec per IP: 65535/60 ≈ 1092/sec
  CGNAT: 100 users per IP → 10 connections/sec per user

Subnet planning:
  /24 = 256 IPs — small office
  /22 = 1024 IPs — medium company
  /16 = 65536 IPs — large enterprise
  /8  = 16M IPs — huge network (like 10.0.0.0/8)

Routing table size:
  BGP full table: ~950K routes (2024)
  Memory per route: ~200 bytes
  Total: 950K × 200B = 190MB per router
```

## Design Choices

| Approach | Pros | Cons |
|---|---|---|
| NAT44 (IPv4-IPv4) | Saves IPs, security boundary | Breaks P2P, CGNAT issues |
| IPv6 only | Abundant addresses, no NAT | Limited legacy support |
| Dual-stack | Compatibility | Complexity |
| CGNAT | Extends IPv4 life | Port exhaustion, logging issues |

## Follow-up Questions

1. How does NAT-PMP/UPnP allow devices to open ports in NAT?
2. How does BGP work and why is it called the "protocol that runs the internet"?
3. What is ECMP (Equal-Cost Multi-Path) routing?
4. How does SDN (Software Defined Networking) change routing?
5. Explain what happens when a packet crosses 5 router hops.

## Python Implementation

```python
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import random

@dataclass
class NATEntry:
    private_ip: str
    private_port: int
    public_ip: str
    public_port: int
    protocol: str

class NATRouter:
    def __init__(self, public_ip: str):
        self.public_ip = public_ip
        self._table: Dict[Tuple[str, int], NATEntry] = {}
        self._reverse: Dict[Tuple[str, int], NATEntry] = {}
        self._next_port = 40000

    def translate_outbound(self, src_ip: str, src_port: int,
                           dst_ip: str, dst_port: int, protocol: str = "TCP") -> Tuple[str, int]:
        key = (src_ip, src_port)
        if key not in self._table:
            pub_port = self._next_port
            self._next_port += 1
            entry = NATEntry(src_ip, src_port, self.public_ip, pub_port, protocol)
            self._table[key] = entry
            self._reverse[(self.public_ip, pub_port)] = entry
        return self.public_ip, self._table[key].public_port

    def translate_inbound(self, dst_ip: str, dst_port: int) -> Optional[Tuple[str, int]]:
        entry = self._reverse.get((dst_ip, dst_port))
        if entry:
            return entry.private_ip, entry.private_port
        return None

class IPRouter:
    def __init__(self):
        self._table: list[Tuple[str, int, str]] = []  # (network, prefix_len, next_hop)

    def add_route(self, network: str, prefix_len: int, next_hop: str):
        self._table.append((network, prefix_len, next_hop))
        self._table.sort(key=lambda r: -r[1])  # Sort by prefix length descending

    def _ip_to_int(self, ip: str) -> int:
        parts = ip.split(".")
        return sum(int(p) << (24 - 8*i) for i, p in enumerate(parts))

    def lookup(self, dst_ip: str) -> Optional[str]:
        dst = self._ip_to_int(dst_ip)
        for network, prefix_len, next_hop in self._table:
            net = self._ip_to_int(network)
            mask = ((1 << 32) - 1) ^ ((1 << (32 - prefix_len)) - 1)
            if dst & mask == net & mask:
                return next_hop
        return None

# Usage
nat = NATRouter("203.0.113.5")
pub_ip, pub_port = nat.translate_outbound("192.168.1.10", 5000, "93.184.216.34", 80)
print(f"NAT: 192.168.1.10:5000 → {pub_ip}:{pub_port}")

priv = nat.translate_inbound(pub_ip, pub_port)
print(f"Reverse NAT: {pub_ip}:{pub_port} → {priv[0]}:{priv[1]}")

router = IPRouter()
router.add_route("0.0.0.0", 0, "gateway")
router.add_route("10.0.0.0", 8, "eth1")
router.add_route("10.0.1.0", 24, "eth2")
print(router.lookup("10.0.1.5"))   # eth2 (longest prefix match)
print(router.lookup("10.0.2.5"))   # eth1
print(router.lookup("8.8.8.8"))    # gateway
```

## Java Implementation

```java
import java.util.*;

public class IPRouter {
    record Route(long network, int prefix, String nextHop) {}

    private List<Route> table = new ArrayList<>();

    public void addRoute(String network, int prefix, String nextHop) {
        table.add(new Route(ipToLong(network), prefix, nextHop));
        table.sort((a, b) -> b.prefix() - a.prefix()); // Longest prefix first
    }

    public Optional<String> lookup(String dst) {
        long dstLong = ipToLong(dst);
        return table.stream()
            .filter(r -> {
                long mask = r.prefix() == 0 ? 0 : (-1L << (32 - r.prefix())) & 0xFFFFFFFFL;
                return (dstLong & mask) == (r.network() & mask);
            })
            .map(Route::nextHop)
            .findFirst();
    }

    private long ipToLong(String ip) {
        String[] parts = ip.split("\\.");
        return Long.parseLong(parts[0]) << 24 | Long.parseLong(parts[1]) << 16
             | Long.parseLong(parts[2]) << 8  | Long.parseLong(parts[3]);
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| NAT lookup | O(1) hash map |
| Route lookup | O(routes) with LPM |
| CIDR subnet calc | O(1) |
| BGP convergence | O(routes × peers) |
""",

"11_connection_pooling.md": """# Connection Pooling

## Problem Statement

Design a connection pool to reuse expensive database/HTTP connections, reducing connection setup overhead for high-throughput services.

**Requirements:**
- Pre-warm pool of reusable connections
- Thread-safe borrow/return
- Health check and replace stale connections
- Configurable min/max pool size

## Architecture Diagram

```mermaid
graph TB
    App1[App Thread 1]
    App2[App Thread 2]
    App3[App Thread 3]

    Pool[Connection Pool min=2 max=10]
    C1[Conn 1 idle]
    C2[Conn 2 busy]
    C3[Conn 3 idle]

    DB[Database]

    App1 -->|borrow| Pool
    App2 -->|borrow| Pool
    App3 -->|borrow - wait| Pool

    Pool --- C1
    Pool --- C2
    Pool --- C3

    C1 -->|socket| DB
    C2 -->|socket| DB
    C3 -->|socket| DB
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant T as App Thread
    participant P as Pool
    participant DB as Database

    T->>P: borrow(timeout=5s)
    alt Idle connection available
        P-->>T: Return idle conn
    else Pool not at max
        P->>DB: New TCP connect + auth
        DB-->>P: Conn established
        P-->>T: Return new conn
    else Pool at max
        P->>P: Wait for return (up to timeout)
        P-->>T: Return released conn or TimeoutError
    end

    T->>DB: Execute query
    DB-->>T: Results
    T->>P: return(conn)
    P->>P: Health check conn
    P->>P: Add back to idle pool
```

## Design

### Pool Sizing Rules

```
min_size  — Pre-warm this many connections at startup
max_size  — Never exceed this (prevents DB overload)
idle_timeout — Close idle connections after N seconds
max_lifetime — Replace connection after N seconds (prevents stale state)
checkout_timeout — Raise error if can't borrow in N seconds

Rule of thumb:
  max_pool_size = (threads × avg_query_time_ms) / 1000
  Example: 100 threads, 10ms avg query → max = 1 connection
  But add overhead buffer: max = 10-20
```

### Health Check Strategies

```
Passive:  Try to use; if error, discard and retry
Active:   Ping (SELECT 1) before returning from pool
Periodic: Background thread pings all idle connections every 30s
```

## Common Questions & Answers

**Q: What happens at max pool size with more requests?** A: Threads wait (blocked) up to checkout_timeout, then get a TimeoutException. This is backpressure — prevents cascading failures.

**Q: What is connection leaking?** A: Thread borrows connection but never returns it (exception path skips return). Fix: always use try-with-resources / context manager.

**Q: Database max_connections vs pool max_size?** A: DB has global max connections (e.g., PostgreSQL default 100). Sum of all application pool max sizes must be < DB max. Allow headroom for admin tools.

**Q: pgBouncer vs application-level pooling?** A: pgBouncer is a proxy-level pool — transaction mode (connection released after each transaction, very efficient). App-level pool holds connection per thread.

## Back-of-Envelope Calculations

```
Without connection pooling:
  Each request: TCP connect (1 RTT) + DB auth (1 RTT) = 100ms overhead
  At 1000 req/sec: 1000 new connections/sec → DB overwhelmed

With pooling (pool=20):
  20 persistent connections to DB
  Checkout: ~0.01ms (queue lookup)
  Throughput: 20 conns × 100 queries/conn/sec = 2000 queries/sec

PostgreSQL limits:
  Default max_connections: 100
  Each idle connection: ~5MB RAM
  100 connections: 500MB overhead
  pgBouncer transaction mode: 1000 app connections → 20 DB connections
```

## Design Choices

| Approach | Pros | Cons |
|---|---|---|
| Fixed pool size | Predictable | Under/over provisioned |
| Dynamic sizing | Adapts to load | Complexity |
| Transaction-mode proxy (pgBouncer) | Very efficient | No prepared statements across tx |
| Session-mode proxy | Full session state | Less efficient |
| No pooling | Simple | Can't scale |

## Follow-up Questions

1. How would you implement a connection pool for HTTP (keep-alive)?
2. How do you detect and close zombie connections?
3. Design a pool that prioritizes connections by geographic region.
4. What happens to pooled connections when the DB restarts?
5. How does HikariCP achieve its benchmark performance?

## Python Implementation

```python
import threading
import queue
import time
from contextlib import contextmanager
from typing import Optional, Any

class MockDBConnection:
    _id_counter = 0

    def __init__(self):
        MockDBConnection._id_counter += 1
        self.id = MockDBConnection._id_counter
        self.created_at = time.time()
        self._alive = True

    def execute(self, sql: str) -> list:
        if not self._alive:
            raise ConnectionError("Connection is closed")
        return [{"result": f"row from conn {self.id}"}]

    def ping(self) -> bool:
        return self._alive

    def close(self):
        self._alive = False

class ConnectionPool:
    def __init__(self, min_size: int = 2, max_size: int = 10,
                 checkout_timeout: float = 5.0, max_lifetime: float = 3600.0):
        self._min_size = min_size
        self._max_size = max_size
        self._checkout_timeout = checkout_timeout
        self._max_lifetime = max_lifetime
        self._pool: queue.Queue = queue.Queue()
        self._total_conns = 0
        self._lock = threading.Lock()

        # Pre-warm
        for _ in range(min_size):
            self._create_and_add()

    def _create_connection(self) -> MockDBConnection:
        return MockDBConnection()

    def _create_and_add(self):
        conn = self._create_connection()
        self._pool.put(conn)
        with self._lock:
            self._total_conns += 1

    def _is_valid(self, conn: MockDBConnection) -> bool:
        if time.time() - conn.created_at > self._max_lifetime:
            return False
        return conn.ping()

    def borrow(self) -> MockDBConnection:
        try:
            conn = self._pool.get(timeout=0.001)
            if self._is_valid(conn):
                return conn
            conn.close()
            with self._lock:
                self._total_conns -= 1
        except queue.Empty:
            pass

        with self._lock:
            if self._total_conns < self._max_size:
                conn = self._create_connection()
                self._total_conns += 1
                return conn

        try:
            conn = self._pool.get(timeout=self._checkout_timeout)
            return conn if self._is_valid(conn) else self.borrow()
        except queue.Empty:
            raise TimeoutError(f"No connection available after {self._checkout_timeout}s")

    def release(self, conn: MockDBConnection):
        if self._is_valid(conn):
            self._pool.put(conn)
        else:
            conn.close()
            with self._lock:
                self._total_conns -= 1

    @contextmanager
    def connection(self):
        conn = self.borrow()
        try:
            yield conn
        finally:
            self.release(conn)

# Usage
pool = ConnectionPool(min_size=2, max_size=5)

def worker(thread_id: int):
    with pool.connection() as conn:
        result = conn.execute("SELECT 1")
        print(f"Thread {thread_id}: conn={conn.id}, result={result[0]}")

threads = [threading.Thread(target=worker, args=(i,)) for i in range(8)]
for t in threads: t.start()
for t in threads: t.join()
```

## Java Implementation

```java
import java.util.concurrent.*;
import java.util.*;

public class ConnectionPool {
    static class Conn {
        final int id;
        final long createdAt = System.currentTimeMillis();
        static int counter = 0;
        Conn() { this.id = ++counter; }
        boolean isValid() { return System.currentTimeMillis() - createdAt < 3600_000L; }
        List<Map<String, Object>> execute(String sql) {
            return List.of(Map.of("conn", id, "result", "row"));
        }
    }

    private final BlockingQueue<Conn> pool;
    private final int maxSize;
    private int totalConns = 0;
    private final Object lock = new Object();

    public ConnectionPool(int minSize, int maxSize) {
        this.maxSize = maxSize;
        this.pool = new LinkedBlockingQueue<>();
        for (int i = 0; i < minSize; i++) { pool.offer(new Conn()); totalConns++; }
    }

    public Conn borrow(long timeoutMs) throws Exception {
        Conn conn = pool.poll();
        if (conn != null && conn.isValid()) return conn;

        synchronized (lock) {
            if (totalConns < maxSize) { totalConns++; return new Conn(); }
        }
        conn = pool.poll(timeoutMs, TimeUnit.MILLISECONDS);
        if (conn == null) throw new TimeoutException("No connection available");
        return conn;
    }

    public void release(Conn conn) {
        if (conn.isValid()) pool.offer(conn);
        else synchronized (lock) { totalConns--; }
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Borrow (idle available) | O(1) |
| Borrow (create new) | O(connect_time) |
| Return | O(1) |
| Health check | O(1) |
| Pool exhausted wait | O(checkout_timeout) |
""",

"12_network_topology.md": """# Data Center Network Topology

## Problem Statement

Design network topology for a large-scale data center supporting hundreds of thousands of servers with high bandwidth, low latency, and redundancy.

## Architecture Diagram

```mermaid
graph TB
    Internet[Internet / WAN]

    subgraph Core["Core Layer"]
        CR1[Core Router 1]
        CR2[Core Router 2]
    end

    subgraph Spine["Spine Layer"]
        S1[Spine Switch 1]
        S2[Spine Switch 2]
        S3[Spine Switch 3]
        S4[Spine Switch 4]
    end

    subgraph Leaf1["Leaf Pod 1"]
        L1[Leaf 1a]
        L2[Leaf 1b]
        Server1[Server 1-8]
    end

    subgraph Leaf2["Leaf Pod 2"]
        L3[Leaf 2a]
        L4[Leaf 2b]
        Server2[Server 9-16]
    end

    Internet --> CR1
    Internet --> CR2
    CR1 --> S1
    CR1 --> S2
    CR2 --> S3
    CR2 --> S4
    S1 --> L1
    S1 --> L3
    S2 --> L1
    S2 --> L3
    S3 --> L2
    S3 --> L4
    S4 --> L2
    S4 --> L4
    L1 --> Server1
    L2 --> Server1
    L3 --> Server2
    L4 --> Server2
```

## Design

### Spine-Leaf Architecture

```
Why Spine-Leaf over traditional 3-tier?
  Traditional: Core → Aggregation → Access (oversubscription, STP loops)
  Spine-Leaf: Every leaf connected to every spine (ECMP, no STP)

Properties:
  Equal latency between any two servers: 2 hops
  Bandwidth: N spines × uplink bandwidth per leaf
  ECMP: Equal-cost multi-path — load balance across all spine paths
  Redundancy: N-1 spine failures tolerated
```

### Bandwidth Oversubscription

```
Downlink (to servers): 48 × 25Gbps = 1.2Tbps
Uplink (to spine):      8 × 100Gbps = 800Gbps
Oversubscription ratio: 1200/800 = 1.5:1 (acceptable for most workloads)

Google practice: ~2:1 oversubscription at leaf, 1:1 at spine
Facebook practice: ~4:1 at edge, 1:1 at core
```

### Link Aggregation (LACP/LAG)

```
Bond multiple physical links:
  2× 10Gbps → 1× 20Gbps logical link
  With LACP: active-active (both links active)
  Hash: src/dst MAC, IP, port → consistent per-flow path
```

## Common Questions & Answers

**Q: Why not use a tree topology?** A: Root is single point of failure + bottleneck. Spine-leaf provides full bisectional bandwidth.

**Q: What is bisectional bandwidth?** A: Bandwidth available when you split the network in half. Full bisection = no bottleneck; oversubscription < 1 means bottleneck exists.

**Q: How does East-West traffic differ from North-South?** A: North-South: external clients to servers (traditional). East-West: server-to-server within DC (microservices). Modern DCs have 80%+ East-West traffic.

**Q: What is ECMP?** A: Equal-Cost Multi-Path — multiple paths of equal cost, load balanced per-flow via hashing. Provides both bandwidth and redundancy.

**Q: How does Facebook's network differ from AWS?** A: Facebook: custom ASIC switches (Wedge), SONiC OS. AWS: custom silicon (Nitro), VPC overlay networking. Both use BGP at scale.

## Back-of-Envelope Calculations

```
Data center network design:
  1000 servers, each with 25Gbps NIC
  Total server bandwidth: 1000 × 25Gbps = 25Tbps

  With 2:1 oversubscription at leaf:
  Leaf uplinks: 25Tbps / 2 = 12.5Tbps total

  10 spine switches, 48 ports each at 400Gbps:
  Spine capacity: 10 × 48 × 400Gbps = 192Tbps (well above needed)

Cross-rack latency:
  Within rack: ~100μs
  Cross-leaf (same pod): ~300μs
  Cross-pod (spine traverse): ~500μs
  Cross-DC (WAN): 5-100ms

Failure domains:
  Single spine failure: 1/N spine capacity lost
  Single leaf failure: all servers in rack affected
  → Dual-home servers to 2 leaves (MLAG)
```

## Design Choices

| Topology | Pros | Cons |
|---|---|---|
| Spine-Leaf | Equal latency, ECMP | More cabling |
| Fat-Tree | Non-blocking | Complex routing |
| 3-tier | Legacy, familiar | STP, oversubscription |
| Mesh | Max redundancy | O(n²) cabling |

## Follow-up Questions

1. How does SR-IOV improve network performance for VMs?
2. What is VXLAN and why is it used in virtualized data centers?
3. How does AWS VPC implement network isolation?
4. What is SmartNIC/DPU and why is it used?
5. How do you design a network for GPU clusters (AI training)?

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from itertools import product

@dataclass
class Switch:
    name: str
    layer: str  # spine, leaf, core
    ports: int
    uplinks: List["Link"] = field(default_factory=list)
    downlinks: List["Link"] = field(default_factory=list)

@dataclass
class Server:
    name: str
    rack: str
    ip: str

@dataclass
class Link:
    src: str
    dst: str
    bandwidth_gbps: float

class SpineLeafTopology:
    def __init__(self, num_spines: int, num_leaves: int, servers_per_leaf: int):
        self.spines = [Switch(f"spine-{i}", "spine", ports=48) for i in range(num_spines)]
        self.leaves = [Switch(f"leaf-{i}", "leaf", ports=64) for i in range(num_leaves)]
        self.servers: Dict[str, List[Server]] = {}
        self.links: List[Link] = []

        self._build_topology(servers_per_leaf)

    def _build_topology(self, servers_per_leaf: int):
        # Every leaf connects to every spine
        for leaf, spine in product(self.leaves, self.spines):
            link = Link(leaf.name, spine.name, bandwidth_gbps=100)
            self.links.append(link)
            leaf.uplinks.append(link)
            spine.downlinks.append(link)

        # Attach servers to leaves
        server_id = 0
        for leaf in self.leaves:
            self.servers[leaf.name] = []
            for _ in range(servers_per_leaf):
                s = Server(f"server-{server_id}", leaf.name, f"10.0.{server_id//256}.{server_id%256}")
                self.servers[leaf.name].append(s)
                leaf.downlinks.append(Link(leaf.name, s.name, bandwidth_gbps=25))
                server_id += 1

    def hops_between(self, src_leaf: str, dst_leaf: str) -> int:
        if src_leaf == dst_leaf:
            return 0  # same rack
        return 2  # src_leaf → spine → dst_leaf

    def bisectional_bandwidth_gbps(self) -> float:
        spine_capacity = len(self.spines) * 100  # uplink per leaf
        leaf_capacity = sum(len(srvs) * 25 for srvs in self.servers.values())
        return min(spine_capacity * len(self.leaves) / 2, leaf_capacity / 2)

    def available_paths(self, src_leaf: str, dst_leaf: str) -> int:
        return len(self.spines)  # ECMP paths

    def summary(self) -> dict:
        total_servers = sum(len(s) for s in self.servers.values())
        return {
            "spines": len(self.spines),
            "leaves": len(self.leaves),
            "total_servers": total_servers,
            "links": len(self.links),
            "max_hops": 2,
            "ecmp_paths": len(self.spines),
            "bisectional_bw_gbps": self.bisectional_bandwidth_gbps(),
        }

# Usage
topo = SpineLeafTopology(num_spines=4, num_leaves=8, servers_per_leaf=48)
print(topo.summary())
print(f"Paths between leaf-0 and leaf-3: {topo.available_paths('leaf-0', 'leaf-3')}")
```

## Java Implementation

```java
import java.util.*;
import java.util.stream.*;

public class SpineLeafTopology {
    record Switch(String name, String layer, List<String> uplinks, List<String> downlinks) {}
    record Link(String src, String dst, int bandwidthGbps) {}

    private List<Switch> spines, leaves;
    private List<Link> links = new ArrayList<>();

    public SpineLeafTopology(int numSpines, int numLeaves) {
        spines = IntStream.range(0, numSpines)
            .mapToObj(i -> new Switch("spine-" + i, "spine", new ArrayList<>(), new ArrayList<>()))
            .collect(Collectors.toList());
        leaves = IntStream.range(0, numLeaves)
            .mapToObj(i -> new Switch("leaf-" + i, "leaf", new ArrayList<>(), new ArrayList<>()))
            .collect(Collectors.toList());

        for (Switch leaf : leaves)
            for (Switch spine : spines)
                links.add(new Link(leaf.name(), spine.name(), 100));
    }

    public int ecmpPaths() { return spines.size(); }
    public int hops(String srcLeaf, String dstLeaf) { return srcLeaf.equals(dstLeaf) ? 0 : 2; }
    public int totalLinks() { return links.size(); }
}
```

## Complexity

| Metric | Value |
|---|---|
| Hops any-to-any | 2 (same rack: 0) |
| ECMP paths | = number of spines |
| Topology links | leaves × spines |
| Failure tolerance | N-1 spines, dual-homed racks |
""",

"13_anycast_routing.md": """# Anycast Routing

## Problem Statement

Design a globally distributed service using Anycast — a routing scheme where the same IP address is announced from multiple locations, and traffic is automatically directed to the nearest one.

## Architecture Diagram

```mermaid
graph TB
    User1["User Tokyo"]
    User2["User London"]
    User3["User NYC"]

    PoP1["PoP Tokyo\\n1.1.1.1 announced"]
    PoP2["PoP London\\n1.1.1.1 announced"]
    PoP3["PoP NYC\\n1.1.1.1 announced"]
    BGP["BGP Internet Routing"]

    User1 -->|Nearest is Tokyo| PoP1
    User2 -->|Nearest is London| PoP2
    User3 -->|Nearest is NYC| PoP3
    PoP1 -->|Announce 1.1.1.1 via AS13335| BGP
    PoP2 -->|Announce 1.1.1.1 via AS13335| BGP
    PoP3 -->|Announce 1.1.1.1 via AS13335| BGP
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant User as User Tokyo
    participant ISP as ISP Router
    participant BGP as BGP Table
    participant PoP as Nearest PoP Tokyo

    User->>ISP: Packet to 1.1.1.1
    ISP->>BGP: Route lookup for 1.1.1.1
    BGP-->>ISP: Best path → AS13335 via Tokyo IX (shortest AS path)
    ISP->>PoP: Forward packet to Tokyo PoP
    PoP-->>User: Response from 1.1.1.1
    Note over User,PoP: Same IP, geographically nearest server
```

## Design

### Anycast vs Unicast vs Multicast vs Broadcast

```
Unicast    — 1:1 — one sender, one receiver (normal)
Anycast    — 1:nearest of N — same IP, nearest receiver handles
Multicast  — 1:group — one sender, group of receivers
Broadcast  — 1:all — one sender, all on network segment

Anycast use cases:
  DNS root servers (13 IP addresses, 1000+ physical servers)
  CDN PoPs (Cloudflare, Fastly)
  DDoS scrubbing centers
  NTP servers
```

### BGP Anycast Mechanism

```
Each PoP announces same /24 or /32 prefix to internet via BGP
ISPs choose path based on:
  1. Shortest AS path
  2. Local preference
  3. MED (Multi-Exit Discriminator)
  4. Geographic proximity (through IX peering)

When PoP fails:
  BGP withdraws route from that PoP
  Traffic automatically reroutes to next nearest PoP
  Convergence: 30-90 seconds
```

## Common Questions & Answers

**Q: How does Anycast differ from GeoDNS?** A: GeoDNS: DNS server returns different IP based on client's DNS resolver location. Anycast: single IP, routing happens in BGP layer. Anycast is transparent, GeoDNS requires DNS change.

**Q: What happens when Anycast PoP fails?** A: BGP withdraws the prefix. ISPs converge to next PoP (30-90s). During convergence, some packets may be lost or rerouted mid-connection.

**Q: Anycast for TCP?** A: Risky — TCP connections must stay on same PoP for session continuity. Fine for UDP (DNS). For TCP: use anycast only for initial connection, then redirect to unicast, or use very stable PoPs.

**Q: How does Cloudflare use Anycast?** A: Cloudflare announces ~1500 IP prefixes from 300+ PoPs globally using anycast. Same IP responds from geographically closest Cloudflare server.

**Q: Can Anycast load balance within a PoP?** A: Yes — at PoP level, ECMP or standard load balancer distributes to servers. Anycast handles the geo-routing layer.

## Back-of-Envelope Calculations

```
Cloudflare Anycast scale:
  200+ countries, 300+ cities
  Single DNS resolver IP (1.1.1.1): served from all PoPs
  Each PoP handles: 1T queries/day / 300 PoPs = 3.3B queries/PoP/day
  = 38,000 queries/sec per PoP

Latency comparison:
  Without Anycast: US user → single European DNS = 150ms
  With Anycast: US user → US PoP = 5ms
  Improvement: 30x

BGP convergence on failure:
  Route withdrawal: 30s (standard)
  With BFD (Bidirectional Forwarding Detection): 1-3s
  Traffic loss during convergence: minimal with BFD

DDoS absorption:
  1Tbps attack spread across 300 PoPs = 3.3Gbps per PoP
  Each PoP can absorb 10-100Gbps → attack absorbed
  This is why Cloudflare advertises "50Tbps network capacity"
```

## Design Choices

| Approach | Pros | Cons |
|---|---|---|
| Anycast | Automatic geo-routing, DDoS resilient | BGP convergence lag, TCP tricky |
| GeoDNS | Fine-grained control | Client location ≠ resolver location |
| Unicast + redirect | Simple | Extra hop |
| Anycast + connection ID | Handles TCP migrations | Complex implementation |

## Follow-up Questions

1. How does Cloudflare Argo Tunnel work with Anycast?
2. How do you test Anycast routing from different global locations?
3. What is IX (Internet Exchange) and how does peering help Anycast?
4. Design a system to monitor which Anycast PoP each region is using.
5. How does 1.1.1.1 achieve sub-10ms DNS resolution globally?

## Python Implementation

```python
from dataclasses import dataclass
from typing import List, Dict, Optional
import math

@dataclass
class PoP:
    name: str
    city: str
    lat: float
    lng: float
    anycast_ip: str
    capacity_rps: int
    healthy: bool = True
    current_load: int = 0

    def load_pct(self) -> float:
        return self.current_load / self.capacity_rps * 100

class AnycastRouter:
    def __init__(self, pops: List[PoP]):
        self._pops = {pop.name: pop for pop in pops}

    def _haversine(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
        return 2 * R * math.asin(math.sqrt(a))

    def route(self, client_lat: float, client_lng: float) -> Optional[PoP]:
        healthy = [p for p in self._pops.values() if p.healthy]
        if not healthy:
            return None
        return min(healthy, key=lambda p: self._haversine(client_lat, client_lng, p.lat, p.lng))

    def simulate_failure(self, pop_name: str):
        if pop_name in self._pops:
            self._pops[pop_name].healthy = False
            print(f"[ANYCAST] PoP {pop_name} down — traffic rerouting...")

    def bgp_summary(self) -> Dict[str, dict]:
        return {
            name: {"healthy": pop.healthy, "load": pop.load_pct()}
            for name, pop in self._pops.items()
        }

# Usage
pops = [
    PoP("nyc", "New York", 40.7128, -74.0060, "1.1.1.1", 100_000),
    PoP("lon", "London", 51.5074, -0.1278, "1.1.1.1", 100_000),
    PoP("tok", "Tokyo", 35.6762, 139.6503, "1.1.1.1", 100_000),
    PoP("syd", "Sydney", -33.8688, 151.2093, "1.1.1.1", 100_000),
]

router = AnycastRouter(pops)
user_london = (51.5, -0.1)
pop = router.route(*user_london)
print(f"London user → {pop.city}")  # London

router.simulate_failure("lon")
pop = router.route(*user_london)
print(f"London user (after failure) → {pop.city}")  # New York or another nearest
```

## Java Implementation

```java
import java.util.*;
import java.util.stream.*;

public class AnycastRouter {
    record PoP(String name, String city, double lat, double lng, boolean healthy) {}

    private List<PoP> pops;

    public AnycastRouter(List<PoP> pops) { this.pops = new ArrayList<>(pops); }

    public Optional<PoP> route(double clientLat, double clientLng) {
        return pops.stream().filter(PoP::healthy)
            .min(Comparator.comparingDouble(p -> haversine(clientLat, clientLng, p.lat(), p.lng())));
    }

    private double haversine(double lat1, double lng1, double lat2, double lng2) {
        double R = 6371;
        double dlat = Math.toRadians(lat2 - lat1);
        double dlng = Math.toRadians(lng2 - lng1);
        double a = Math.pow(Math.sin(dlat/2), 2)
            + Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2)) * Math.pow(Math.sin(dlng/2), 2);
        return 2 * R * Math.asin(Math.sqrt(a));
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Route to nearest PoP | O(P) — P = number of PoPs |
| BGP convergence | 30-90s (standard), 1-3s (BFD) |
| Failover detection | 30s BGP hold timer |
""",

"14_vpn_tunneling.md": """# VPN and Network Tunneling

## Problem Statement

Design a VPN (Virtual Private Network) system that creates encrypted tunnels to securely connect remote users and branch offices to a private network.

## Architecture Diagram

```mermaid
graph LR
    RemoteUser["Remote User\\n203.0.113.10"]
    VPN["VPN Gateway\\n198.51.100.1"]
    Corp["Corporate Network\\n10.0.0.0/8"]
    DB["Database\\n10.0.1.50"]

    RemoteUser -->|Encrypted Tunnel\\nIPSec/OpenVPN| VPN
    VPN -->|Decrypted traffic| Corp
    Corp --- DB
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Remote Client
    participant VG as VPN Gateway
    participant CN as Corp Network

    C->>VG: IKE Phase 1 — ISAKMP SA (auth + encrypt algorithms)
    VG-->>C: IKE Phase 1 response
    C->>VG: IKE Phase 2 — IPSec SA (tunnel keys)
    VG-->>C: IPSec tunnel established
    Note over C,VG: Client gets virtual IP 10.0.100.5

    C->>VG: Encrypted IP packet (dst=10.0.1.50)
    VG->>VG: Decrypt + strip VPN header
    VG->>CN: Plain IP packet to 10.0.1.50
    CN-->>VG: Response
    VG->>VG: Encrypt
    VG-->>C: Encrypted response
```

## Design

### VPN Protocols

```
IPSec (ESP/AH) — Industry standard, kernel-level, excellent performance
  Transport mode: encrypt payload only (host-to-host)
  Tunnel mode: encrypt entire IP packet (gateway-to-gateway)

OpenVPN — TLS-based, highly compatible, runs on UDP 1194 or TCP 443
  Cross-platform, userspace, ~100Mbps throughput

WireGuard — Modern, minimal code (~4K lines), ChaCha20 + Poly1305
  ~10Gbps throughput, built into Linux 5.6 kernel

SSL/TLS VPN (Clientless) — Browser-based, HTTPS port 443
  Works through most firewalls, no client install needed
```

### Split Tunneling

```
Full tunnel:   All traffic → VPN → internet
  Pro: Full corporate policy enforcement
  Con: VPN becomes bottleneck, higher latency

Split tunnel:  Corporate traffic → VPN, internet → direct
  Pro: Better performance, less VPN load
  Con: Corporate policy not enforced for internet traffic
```

### Key Exchange (WireGuard)

```
Static public keys distributed out-of-band
Session keys rotated every 180s (REKEY_AFTER_TIME)
ChaCha20-Poly1305 symmetric encryption
Curve25519 ECDH key exchange
BLAKE2s hash, HKDF key derivation
```

## Common Questions & Answers

**Q: IPSec vs WireGuard?** A: WireGuard: simpler, faster, modern crypto. IPSec: mature, more features (IKEv2, certificate auth), supported everywhere. WireGuard preferred for new deployments.

**Q: What is a Site-to-Site VPN?** A: Connects two networks (e.g., branch offices) via always-on tunnel between gateway routers. No per-user client needed.

**Q: What is Zero Trust vs VPN?** A: Traditional VPN: once connected, access all internal resources (castle-and-moat). Zero Trust: authenticate every request, least-privilege, network location doesn't grant trust.

**Q: How does NAT traversal work for VPN?** A: NAT-T (NAT Traversal) — encapsulate IPSec in UDP port 4500 to pass through NAT. WireGuard handles this natively.

**Q: VPN vs Leased line?** A: VPN: over public internet, encrypted, cheaper. Leased line: dedicated physical connection, guaranteed bandwidth, expensive, no encryption needed.

## Back-of-Envelope Calculations

```
WireGuard throughput:
  CPU cost: ~1μs per packet (1.5KB packet)
  1 core: 1M/1 = 1M packets/sec = 1.5M × 1500B = 12 Gbps
  Consumer hardware: 1-5 Gbps

Encryption overhead:
  ChaCha20: ~3 GB/s per core
  AES-256-GCM with AES-NI: ~5 GB/s per core
  Both: negligible at typical VPN speeds

Concurrent VPN sessions:
  Each WireGuard peer: ~1KB state
  100K users: 100MB RAM for peer state
  Handshake: once every 3 minutes (REKEY = 180s)
  100K users: 100K/180 = 556 rekeys/sec

Corporate VPN sizing:
  500 concurrent users × 5 Mbps avg = 2.5 Gbps
  2 VPN gateways × 2 Gbps = 4 Gbps capacity with failover
```

## Design Choices

| Protocol | Throughput | Latency | Complexity | Use case |
|---|---|---|---|---|
| WireGuard | 10 Gbps | <1ms | Low | Modern, cloud |
| OpenVPN | 100 Mbps | 2-5ms | Medium | Cross-platform |
| IPSec/IKEv2 | 5 Gbps | 1-2ms | High | Enterprise, iOS |
| SSTP | 100 Mbps | 5ms | Medium | Windows |

## Follow-up Questions

1. How do you implement Zero Trust Network Access (ZTNA) as an alternative to VPN?
2. Design a VPN that auto-reconnects on network change (mobile handoff).
3. How does Tailscale use WireGuard for mesh VPN?
4. How do you audit VPN access logs for compliance?
5. What is SD-WAN and how does it replace traditional VPN for branch offices?

## Python Implementation

```python
import os
import hashlib
import hmac
import struct
from typing import Optional, Tuple
from dataclasses import dataclass

@dataclass
class WireGuardPeer:
    public_key: bytes
    allowed_ips: list[str]
    endpoint: Optional[str] = None
    last_handshake: float = 0.0

class ChaCha20Poly1305:
    """Simplified simulation - use cryptography library in production."""
    @staticmethod
    def encrypt(key: bytes, nonce: bytes, plaintext: bytes, aad: bytes = b"") -> bytes:
        # Production: from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
        mac = hmac.new(key, plaintext + aad, hashlib.sha256).digest()[:16]
        ciphertext = bytes(b ^ k for b, k in zip(plaintext, (key * (len(plaintext)//len(key)+1))[:len(plaintext)]))
        return ciphertext + mac

    @staticmethod
    def decrypt(key: bytes, nonce: bytes, ciphertext: bytes, aad: bytes = b"") -> bytes:
        data, mac_recv = ciphertext[:-16], ciphertext[-16:]
        plaintext = bytes(b ^ k for b, k in zip(data, (key * (len(data)//len(key)+1))[:len(data)]))
        mac_calc = hmac.new(key, plaintext + aad, hashlib.sha256).digest()[:16]
        if not hmac.compare_digest(mac_recv, mac_calc):
            raise ValueError("MAC verification failed — packet tampered")
        return plaintext

class VPNGateway:
    def __init__(self, private_key: bytes = None):
        self._private_key = private_key or os.urandom(32)
        self._public_key = hashlib.sha256(self._private_key).digest()  # simplified ECDH
        self._peers: dict[bytes, WireGuardPeer] = {}
        self._session_keys: dict[bytes, bytes] = {}

    @property
    def public_key(self) -> bytes:
        return self._public_key

    def add_peer(self, peer: WireGuardPeer):
        self._peers[peer.public_key] = peer
        # Derive shared session key (simplified ECDH)
        shared = hashlib.sha256(self._private_key + peer.public_key).digest()
        self._session_keys[peer.public_key] = shared

    def encapsulate(self, peer_pubkey: bytes, payload: bytes) -> bytes:
        key = self._session_keys[peer_pubkey]
        nonce = os.urandom(12)
        ciphertext = ChaCha20Poly1305.encrypt(key, nonce, payload)
        header = struct.pack("!4sHH", b"WG\x00\x01", len(nonce), len(ciphertext))
        return header + nonce + ciphertext

    def decapsulate(self, peer_pubkey: bytes, packet: bytes) -> bytes:
        header_size = struct.calcsize("!4sHH")
        _, nonce_len, ct_len = struct.unpack("!4sHH", packet[:header_size])
        nonce = packet[header_size:header_size+nonce_len]
        ciphertext = packet[header_size+nonce_len:]
        key = self._session_keys[peer_pubkey]
        return ChaCha20Poly1305.decrypt(key, nonce, ciphertext)

# Usage
gw = VPNGateway()
client_key = os.urandom(32)
client_pubkey = hashlib.sha256(client_key).digest()

peer = WireGuardPeer(public_key=client_pubkey, allowed_ips=["10.0.100.0/24"])
gw.add_peer(peer)

payload = b"GET /internal-api HTTP/1.1\r\nHost: 10.0.1.50\r\n\r\n"
encrypted = gw.encapsulate(client_pubkey, payload)
decrypted = gw.decapsulate(client_pubkey, encrypted)
print(f"Original: {len(payload)}B → Encrypted: {len(encrypted)}B")
print(f"Decrypted matches: {decrypted == payload}")
```

## Java Implementation

```java
import javax.crypto.*;
import javax.crypto.spec.*;
import java.security.*;
import java.util.*;

public class VPNTunnel {
    private final SecretKey sessionKey;
    private final String peerId;

    public VPNTunnel(String peerId) throws Exception {
        this.peerId = peerId;
        KeyGenerator kg = KeyGenerator.getInstance("AES");
        kg.init(256);
        this.sessionKey = kg.generateKey();
    }

    public byte[] encrypt(byte[] payload) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        byte[] iv = new byte[12];
        new SecureRandom().nextBytes(iv);
        cipher.init(Cipher.ENCRYPT_MODE, sessionKey, new GCMParameterSpec(128, iv));
        byte[] ciphertext = cipher.doFinal(payload);
        byte[] result = new byte[iv.length + ciphertext.length];
        System.arraycopy(iv, 0, result, 0, iv.length);
        System.arraycopy(ciphertext, 0, result, iv.length, ciphertext.length);
        return result;
    }

    public byte[] decrypt(byte[] packet) throws Exception {
        byte[] iv = Arrays.copyOf(packet, 12);
        byte[] ciphertext = Arrays.copyOfRange(packet, 12, packet.length);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, sessionKey, new GCMParameterSpec(128, iv));
        return cipher.doFinal(ciphertext);
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Handshake | 1-2 RTTs |
| Encrypt/decrypt | O(n) payload size |
| Peer lookup | O(1) hash map |
| Key rotation | O(1) every 3 min |
""",

"15_bandwidth_latency.md": """# Bandwidth, Latency, and Network Math

## Problem Statement

Master the fundamental network performance metrics — bandwidth, latency, throughput, and how to use them for back-of-envelope capacity planning.

## Architecture Diagram

```mermaid
graph LR
    Client[Client]
    Link["Network Link\\n100 Mbps, 50ms RTT"]
    Server[Server]
    Client -->|Request 1KB| Link
    Link -->|Response 10KB| Server
    Note1["Latency: 50ms\\nBandwidth: 100Mbps\\nThroughput: min(BW, window/RTT)"]
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    Note over C,S: Latency = propagation + transmission + queuing + processing

    C->>S: Packet (1ms transmission at 10Mbps)
    Note over C: Propagation: 20ms (speed of light, 4000km)
    Note over S: Processing: 1ms
    S-->>C: Response (2ms transmission)
    Note over C: Total RTT = 20+1+20+2 = 43ms
```

## Design

### Latency Components

```
Total Latency = Propagation + Transmission + Queuing + Processing

Propagation delay   — Distance / speed of light in medium
                      Fiber: ~200,000 km/s (66% speed of light)
                      NYC to London (5500km): 27ms one-way

Transmission delay  — Packet size / link bandwidth
                      1500B packet on 1Gbps: 1500×8 / 10^9 = 12μs

Queuing delay       — Time waiting in router queue
                      Minimal when lightly loaded; spikes under congestion

Processing delay    — Router lookup, checksum, etc.
                      Modern hardware: <1μs
```

### Bandwidth-Delay Product (BDP)

```
BDP = Bandwidth × RTT

BDP = 100 Mbps × 100ms = 10Mb = 1.25 MB
→ To fully utilize the link, need 1.25MB in flight at once
→ TCP window must be >= BDP for full throughput

Example: Satellite link
  Bandwidth: 100 Mbps
  RTT: 600ms (geostationary)
  BDP = 7.5 MB → TCP window must be 7.5MB (need window scaling RFC 1323)
```

### Throughput vs Bandwidth

```
Bandwidth: Maximum capacity (what the link CAN carry)
Throughput: Actual data transferred (what it DOES carry)

Throughput = Bandwidth × Efficiency
Efficiency reduced by:
  - Protocol overhead (TCP headers ~5%, TLS ~2%)
  - Retransmissions (1% loss → ~5% throughput loss with naive TCP)
  - Window size limits (throughput = min(cwnd, rwnd) / RTT)
```

### Speed of Light Limits

```
Medium          Speed                  Latency per 1000km
Fiber optic     ~200,000 km/s          5ms
Copper          ~200,000 km/s          5ms
Air (radio)     ~300,000 km/s          3.3ms
Satellite (LEO) ~300,000 km/s + orbit  ~10-30ms (Starlink)
Satellite (GEO) ~300,000 km/s + 36000km orbit  ~250ms one-way
```

## Common Questions & Answers

**Q: Why can't we just increase bandwidth to reduce latency?** A: Bandwidth reduces transmission delay (negligible for small packets). Propagation delay dominates and is physics-limited.

**Q: What is Bufferbloat?** A: Oversized router buffers cause high latency under congestion. Packets queue for hundreds of ms. Solution: CoDel, FQ-CoDel active queue management.

**Q: How does TCP window size limit throughput?** A: Throughput ≤ window_size / RTT. Default window 65535B at 100ms RTT = 5.2 Mbps on a 1Gbps link. Fix: TCP window scaling (RWIN up to 1GB).

**Q: What is Jitter?** A: Variation in packet arrival times. Affects real-time applications (VoIP, video). Measured as standard deviation of RTT.

**Q: What is QoS?** A: Quality of Service — prioritize traffic types. VoIP packets get expedited forwarding; bulk downloads get best-effort.

## Back-of-Envelope Calculations

```
NYC to London RTT (realistic):
  Physical: 2 × (5,500km / 200,000km/s) = 55ms
  With routing overhead: ~75-85ms actual
  Google's measurement tool: avg 80ms

File transfer time:
  1GB file over 100Mbps link:
  Time = 1GB × 8 / 100Mbps = 80 seconds
  (Plus TCP slow start, TLS overhead: ~85s realistic)

API response latency budget (100ms target):
  Network (EU to US): 80ms  → must serve from same region!
  DB query: 5ms
  App processing: 10ms
  Total: 95ms → tight!

Streaming video bandwidth:
  4K HDR: 25 Mbps per stream
  100 concurrent viewers: 2.5 Gbps
  CDN edge capacity needed: 2.5 Gbps per serving region

Packet loss impact:
  0.1% loss → TCP throughput: 90% of ideal
  1% loss → TCP throughput: ~30% of ideal (severe)
  Formula: Throughput ≈ MSS / (RTT × √loss_rate)

Data center cross-rack latency:
  Within rack: 100μs
  Same pod (2 hops): 300μs
  Cross-pod (spine): 500μs
  Cross-DC (WAN): 5-100ms
```

## Design Choices

| Optimization | Effect | Trade-off |
|---|---|---|
| Edge caching (CDN) | Reduce propagation | Stale data risk |
| Connection pooling | Eliminate setup RTT | Memory for pool |
| TCP window scaling | Full link utilization | More memory |
| UDP / QUIC | Eliminate HOL blocking | Implement reliability |
| Compression | Reduce transmission time | CPU overhead |
| Binary protocols | Smaller payload | Debug complexity |

## Follow-up Questions

1. How would you design a system to achieve <1ms global latency?
2. What is RDMA and why do HPC and AI clusters use it?
3. How do game engines handle 60Hz updates over 100ms RTT?
4. Calculate the optimal TCP buffer size for a trans-Pacific connection.
5. What is the theoretical maximum throughput of a 400G ethernet link?

## Python Implementation

```python
import math
from dataclasses import dataclass
from typing import Optional

@dataclass
class NetworkLink:
    bandwidth_mbps: float
    propagation_ms: float  # one-way
    packet_loss_pct: float = 0.0

    @property
    def rtt_ms(self) -> float:
        return self.propagation_ms * 2

    def transmission_delay_ms(self, size_bytes: int) -> float:
        return (size_bytes * 8) / (self.bandwidth_mbps * 1_000) * 1000

    def total_latency_ms(self, packet_size_bytes: int = 1500) -> float:
        return self.propagation_ms + self.transmission_delay_ms(packet_size_bytes)

    def bandwidth_delay_product_bytes(self) -> float:
        return (self.bandwidth_mbps * 1_000_000 / 8) * (self.rtt_ms / 1000)

    def tcp_throughput_mbps(self, window_bytes: int = 65535) -> float:
        return min(
            self.bandwidth_mbps,
            (window_bytes * 8) / (self.rtt_ms / 1000) / 1_000_000
        )

    def tcp_throughput_with_loss_mbps(self, window_bytes: int = 65535) -> float:
        loss = self.packet_loss_pct / 100
        if loss == 0:
            return self.tcp_throughput_mbps(window_bytes)
        mss = 1460  # bytes
        return (mss * 8 / 1_000_000) / (self.rtt_ms / 1000 * math.sqrt(loss))

class CapacityPlanner:
    def __init__(self, link: NetworkLink):
        self.link = link

    def file_transfer_time(self, size_gb: float) -> float:
        bits = size_gb * 8 * 1_000_000_000
        return bits / (self.link.bandwidth_mbps * 1_000_000)

    def concurrent_streams(self, per_stream_mbps: float) -> int:
        return int(self.link.bandwidth_mbps / per_stream_mbps)

    def required_bandwidth_mbps(self, req_per_sec: int, avg_payload_kb: float) -> float:
        return req_per_sec * avg_payload_kb * 8 / 1000

    def latency_budget(self, total_ms: float) -> dict:
        remaining = total_ms - self.link.rtt_ms
        return {
            "network_ms": self.link.rtt_ms,
            "remaining_budget_ms": max(0, remaining),
            "feasible": remaining > 0,
        }

    def report(self) -> dict:
        return {
            "bandwidth_mbps": self.link.bandwidth_mbps,
            "rtt_ms": self.link.rtt_ms,
            "bdp_bytes": self.link.bandwidth_delay_product_bytes(),
            "tcp_throughput_default_window_mbps": self.link.tcp_throughput_mbps(),
            "tcp_throughput_scaled_window_mbps": self.link.tcp_throughput_mbps(8_388_608),  # 8MB
            "throughput_with_1pct_loss_mbps": self.link.tcp_throughput_with_loss_mbps(window_bytes=65535),
        }

# Usage: Trans-Atlantic link
link = NetworkLink(bandwidth_mbps=1000, propagation_ms=40, packet_loss_pct=0.1)
planner = CapacityPlanner(link)

report = planner.report()
for k, v in report.items():
    print(f"{k}: {v:.2f}")

print(f"\\n1GB file transfer: {planner.file_transfer_time(1):.1f}s")
print(f"4K streams (25Mbps): {planner.concurrent_streams(25)}")
print(f"Required BW for 1000 req/sec, 100KB: {planner.required_bandwidth_mbps(1000, 100):.0f} Mbps")
print(f"100ms latency budget: {planner.latency_budget(100)}")
```

## Java Implementation

```java
public class NetworkMath {
    record Link(double bandwidthMbps, double propagationMs, double lossPercent) {
        double rttMs() { return propagationMs * 2; }
        double bdpBytes() { return (bandwidthMbps * 1e6 / 8) * (rttMs() / 1000); }
        double tcpThroughputMbps(int windowBytes) {
            return Math.min(bandwidthMbps, (windowBytes * 8.0) / (rttMs() / 1000) / 1e6);
        }
        double transferTimeSec(double sizeGb) { return sizeGb * 8 * 1e9 / (bandwidthMbps * 1e6); }
    }

    public static void main(String[] args) {
        Link link = new Link(1000, 40, 0.1);
        System.out.printf("RTT: %.0fms%n", link.rttMs());
        System.out.printf("BDP: %.0f bytes%n", link.bdpBytes());
        System.out.printf("TCP throughput (default window): %.1f Mbps%n", link.tcpThroughputMbps(65535));
        System.out.printf("TCP throughput (8MB window): %.1f Mbps%n", link.tcpThroughputMbps(8_388_608));
        System.out.printf("1GB transfer: %.1f seconds%n", link.transferTimeSec(1));
    }
}
```

## Complexity

| Formula | Purpose |
|---|---|
| Propagation = dist / speed | Physical limit |
| Transmission = size / BW | Packet size matters |
| BDP = BW × RTT | Window sizing |
| Throughput = min(cwnd, rwnd) / RTT | TCP performance |
| Throughput ≈ MSS / (RTT × √loss) | Loss impact |
""",
}

def write_file(path: str, content: str):
    full_path = os.path.join(BASE, path)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"✓ {path}")

for filename, content in FILES.items():
    write_file(filename, content)

print(f"\n✅ Created {len(FILES)} networking concept files")
