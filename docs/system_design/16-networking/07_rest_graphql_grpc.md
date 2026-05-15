# REST vs GraphQL vs gRPC

## Problem Statement

Compare and choose between REST, GraphQL, and gRPC for different API use cases in distributed systems.

## Scenario

REST vs GraphQL vs gRPC is a critical component in modern distributed systems. In real-world applications, allowing clients to request exactly the data they need. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

## Users

- **Backend Engineers**: Responsible for implementing and maintaining this system component in production environments. They need to understand the architecture, trade-offs, failure modes, and operational considerations.
- **DevOps/SRE Teams**: Monitor system health, manage scaling policies, handle incidents, and ensure reliability SLAs are met. They need insights into performance characteristics, bottlenecks, and failure recovery mechanisms.
- **Data Engineers**: Design data pipelines and analytics around this system, requiring deep understanding of data flow, consistency guarantees, and throughput characteristics.
- **System Architects**: Make high-level architectural decisions that impact company infrastructure, requiring comprehensive understanding of capabilities, limitations, and scalability boundaries.
- **Security Teams**: Understand security implications, potential vulnerabilities, and compliance requirements for this component.

## PRD

### Functional Requirements
- Core operations work correctly
- Explicit error handling
- Consistency guarantees defined
- Monitoring and observability

### Non-Functional Requirements
- Performance targets met
- Availability SLA achieved
- Scalability headroom
- Cost efficient

### Success Metrics
- Benchmarks met
- Uptime targets met
- Resource budgets
- No data loss


## Flow

The typical operational flow for this system involves these key phases:

1. **Request Arrival**: Client/upstream system sends request with required parameters and context
2. **Validation & Routing**: System validates request format, authentication, and routes to correct handler/shard/instance
3. **Core Processing**: Execute the main algorithm, database query, or business logic on the data/state
4. **State Management**: Update internal state (caches, indexes, counters, logs) with proper atomicity and locking
5. **Response Generation**: Format results and return to requester with relevant metadata (timing, version info)
6. **Observability**: Record metrics (latency, throughput, errors), logs (for debugging), and traces (for performance analysis)

This flow repeats thousands or millions of times per second in production. Each operation's efficiency compounds across the entire system, making careful optimization essential. Bottlenecks at any phase can cascade to impact overall system performance.


## Code Explanation (Detailed)

### Implementation Approach
The code demonstrates core patterns and trade-offs.

### Key Operations
Each operation shows algorithm and performance characteristics.

### Concurrency and Atomicity
Locking strategies, race condition prevention.

### Edge Cases
Boundary conditions and error handling.

### Performance Optimization
Techniques for reducing latency and throughput.

## Architecture Diagram

```mermaid
graph TB
    Client[Client]

    subgraph REST["REST - Multiple Endpoints"]
        R1[GET /users/1]
        R2[GET /users/1/posts]
        R3[GET /posts/1/comments]
    end

    subgraph GraphQL["GraphQL - Single Endpoint"]
        GQL["POST /graphql\nquery{user(id:1){name posts{title comments{text}}}}"]
    end

    subgraph gRPC["gRPC - Generated Stubs"]
        G1["UserService.GetUser(req)"]
        G2["PostService.ListPosts(req)"]
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
    GQL->>US: GetUser(1) [parallel]
    GQL->>PS: ListPostsByUser(1) [parallel]
    US-->>GQL: {name: "Alice"}
    PS-->>GQL: [{title: "Hello"}, ...]
    GQL-->>C: {user: {name: "Alice", posts: [...]}}
    Note over C,GQL: One HTTP call vs 2 REST calls
```

## Design

### REST Principles

```
Resources   - Nouns, not verbs (/users, /posts)
HTTP verbs  - GET (safe), POST, PUT, PATCH, DELETE
Stateless   - No server-side session
Cacheable   - GET responses can be cached (ETags, Cache-Control)
HATEOAS     - Links to related resources in response (optional)

Problems:
  Over-fetching - endpoint returns unused fields
  Under-fetching - N+1 requests for related data
```

### GraphQL

```
Single endpoint:   POST /graphql
Schema SDL:        type User { id: ID!, name: String!, posts: [Post!]! }
Client controls:   Specify exact fields needed
Resolvers:         Per-field data fetching functions
DataLoader:        Batch + cache resolver calls within request

Benefits: No over/under fetching, strongly typed, introspection
Problems: Caching harder (all POST), N+1 resolver problem, complex tooling
```

### gRPC

```
Interface Definition Language (IDL):
  .proto files define service + message types
  Code generation for 10+ languages

Transport: HTTP/2 (multiplexing, headers compression)
Encoding:  Protocol Buffers (binary, 3-10x smaller than JSON)
Streaming: Unary, server-streaming, client-streaming, bidirectional

Benefits: High performance, type safety, streaming, cross-language
Problems: Not human-readable, limited browser support (need grpc-web proxy)
```

### Comparison

| Feature | REST | GraphQL | gRPC |
|---|---|---|---|
| Protocol | HTTP/1.1 | HTTP/1.1 | HTTP/2 |
| Serialization | JSON | JSON | Protobuf (binary) |
| Type system | None (OpenAPI optional) | Strongly typed | Strongly typed |
| Caching | Native HTTP (GET) | Complex (POST) | Not built-in |
| Streaming | SSE/WebSocket | Subscriptions | Native |
| Browser support | Native | Native | grpc-web only |
| Payload size | Large | Medium | Small |
| Best for | Public APIs | Mobile/complex | Internal services |

## Back-of-Envelope Calculations

```
Payload size (user + 10 posts):
  REST (over-fetching): ~5KB per call, 2 calls = 10KB
  GraphQL (exact fields): ~1KB
  gRPC (binary): ~300 bytes
  Savings: gRPC saves ~97% bandwidth vs REST

Mobile app homepage (5 API calls -> 1 GraphQL):
  5 REST calls x 100ms RTT = 500ms sequential (or parallel with overhead)
  1 GraphQL query = 100ms
  Improvement: 5x for sequential

gRPC vs REST throughput:
  JSON serialization: ~300 MB/s
  Protobuf serialization: ~1.5 GB/s (5x faster)
  At 100K req/sec x 1KB: gRPC saves 1.2GB/s CPU work

GraphQL operation complexity:
  Unlimited depth queries can be abusive (SELECT * of your data)
  Mitigation: query depth limit (10), complexity scoring, persisted queries
```

## Design Choices

| Scenario | Recommendation | Reason |
|---|---|---|
| Public API | REST | Simple, well-understood, cacheable |
| Mobile with complex data | GraphQL | One request, exact fields |
| Internal microservices | gRPC | Performance, type safety |
| Real-time feeds | GraphQL subscriptions | Unified schema |
| File uploads | REST (multipart) | Simpler than gRPC streaming |
| Low-latency trading | gRPC | Binary, streaming |

## Python Implementation

```python
# REST with Flask-style routing
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

@dataclass
class Post:
    post_id: int
    title: str
    user_id: int

@dataclass
class User:
    user_id: int
    name: str
    email: str

# Simulated data store
users_db: Dict[int, User] = {1: User(1, "Alice", "alice@example.com")}
posts_db: Dict[int, List[Post]] = {1: [Post(1, "Hello World", 1), Post(2, "Second post", 1)]}

# REST pattern
class RESTUserAPI:
    def get_user(self, user_id: int) -> Optional[dict]:
        user = users_db.get(user_id)
        return asdict(user) if user else None

    def get_user_posts(self, user_id: int) -> List[dict]:
        return [asdict(p) for p in posts_db.get(user_id, [])]

# GraphQL resolver pattern
class GraphQLResolver:
    def resolve_user(self, user_id: int, fields: List[str]) -> dict:
        user = users_db.get(user_id)
        if not user:
            return {}
        result = {}
        if "name" in fields:
            result["name"] = user.name
        if "email" in fields:
            result["email"] = user.email
        if "posts" in fields:
            result["posts"] = [{"title": p.title} for p in posts_db.get(user_id, [])]
        return result

    def execute(self, query: dict) -> dict:
        result = {}
        if "user" in query:
            uid = query["user"]["id"]
            fields = query["user"].get("fields", ["name"])
            result["user"] = self.resolve_user(uid, fields)
        return result

# gRPC stub simulation
@dataclass
class GetUserRequest:
    user_id: int

@dataclass
class UserResponse:
    user_id: int
    name: str

@dataclass
class ListPostsRequest:
    user_id: int

@dataclass
class PostsResponse:
    posts: List[dict]

class UserServiceStub:
    def GetUser(self, req: GetUserRequest) -> UserResponse:
        user = users_db.get(req.user_id)
        return UserResponse(user.user_id, user.name) if user else UserResponse(0, "")

    def ListPosts(self, req: ListPostsRequest) -> PostsResponse:
        return PostsResponse([asdict(p) for p in posts_db.get(req.user_id, [])])

# Usage comparison
rest = RESTUserAPI()
gql = GraphQLResolver()
grpc = UserServiceStub()

# REST: 2 round trips
user = rest.get_user(1)
posts = rest.get_user_posts(1)
print("REST:", user["name"], len(posts), "posts")

# GraphQL: 1 round trip
result = gql.execute({"user": {"id": 1, "fields": ["name", "posts"]}})
print("GraphQL:", result["user"]["name"], len(result["user"]["posts"]), "posts")

# gRPC: separate service calls, binary protocol
u = grpc.GetUser(GetUserRequest(1))
p = grpc.ListPosts(ListPostsRequest(1))
print("gRPC:", u.name, len(p.posts), "posts")
```

## Java Implementation

```java
import java.util.*;

public class APIComparison {
    record User(int id, String name, String email) {}
    record Post(int id, String title, int userId) {}

    static Map<Integer, User> users = Map.of(1, new User(1, "Alice", "alice@example.com"));
    static Map<Integer, List<Post>> posts = Map.of(1, List.of(
        new Post(1, "Hello", 1), new Post(2, "World", 1)
    ));

    // REST pattern
    static User getUser(int id) { return users.get(id); }
    static List<Post> getUserPosts(int userId) { return posts.getOrDefault(userId, List.of()); }

    // GraphQL resolver pattern
    static Map<String, Object> resolveUser(int id, List<String> fields) {
        User u = users.get(id);
        if (u == null) return Map.of();
        Map<String, Object> result = new HashMap<>();
        if (fields.contains("name")) result.put("name", u.name());
        if (fields.contains("posts")) result.put("posts", getUserPosts(id));
        return result;
    }

    // gRPC-style stub
    record GetUserReq(int userId) {}
    record GetUserResp(int id, String name) {}
    static GetUserResp rpcGetUser(GetUserReq req) {
        User u = users.get(req.userId());
        return u != null ? new GetUserResp(u.id(), u.name()) : new GetUserResp(0, "");
    }

    public static void main(String[] args) {
        System.out.println("REST user: " + getUser(1).name());
        System.out.println("GraphQL: " + resolveUser(1, List.of("name", "posts")));
        System.out.println("gRPC: " + rpcGetUser(new GetUserReq(1)));
    }
}
```

## Complexity

| Metric | REST | GraphQL | gRPC |
|---|---|---|---|
| Payload size | Large (over-fetch) | Medium (exact) | Small (binary) |
| Round trips (complex page) | N | 1 | N (parallel) |
| Schema validation | Manual | Automatic | Automatic |
| Throughput | Medium | Medium | High |

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

