# Ebay Auction System

## System Overview

**Scale Metrics:**
- **Users:** millions
- **Daily Active Users:** millions
- **Requests Per Second (Peak):** 100K+
- **Data Storage:** Petabytes

**Key Challenge:** Scale and reliability at global scale

## Problem Statement

### Functional Requirements
- Core service operations must be reliable and correct
- Multi-region deployment with local consistency
- Clear error handling and recovery mechanisms
- Comprehensive monitoring and observability
- Authentication and authorization
- API versioning for backward compatibility

### Non-Functional Requirements
- **Latency:** P99 latency < 100ms for primary operations
- **Availability:** 99.99% uptime (four nines)
- **Throughput:** Handle peak load with 2-5x headroom
- **Consistency:** Eventual consistency with strong guarantees for critical data
- **Scalability:** Horizontal scaling to handle 10x growth
- **Cost Efficiency:** Optimize per-request operational cost

### Success Metrics
- Request latency P99 < target milliseconds
- Availability > 99.99%
- Zero data loss on committed transactions
- System remains responsive under 10x normal load
- Cost per request optimized

## Architecture

### High-Level Design

```
[Client] → [API Gateway] → [Load Balancer] → [Service Tier]
                                                    ↓
                    [Cache Layer] ← → [Primary DB] [Replica DBs]
                                                    ↓
                    [Message Queue] → [Async Workers] → [Data Lake]
                                                    ↓
                            [Search Index] [Analytics] [ML Pipeline]
```

### Core Components

#### Request Path (Primary Operations)
1. **API Gateway**: Rate limiting, authentication, request routing
   - Tech: Custom service or Kong/AWS API Gateway
   - Handles TLS termination and request validation

2. **Load Balancer**: Distribute across multiple instances
   - Tech: Internal or cloud-native (AWS ELB, Google Cloud LB)
   - Health checks and automatic failover

3. **Service Tier**: Business logic execution
   - Stateless design for easy horizontal scaling
   - Circuit breakers for downstream failures
   - Bulkhead pattern for resource isolation

4. **Cache Layer**: Reduce database load
   - Tech: Redis or Memcached
   - TTL-based expiration with write-through pattern
   - Cache warming and preloading strategies

5. **Primary Database**: Authoritative data store
   - Tech: PostgreSQL, MySQL, or specialized datastores
   - Strong ACID guarantees for critical data
   - Binary replication for consistency

6. **Read Replicas**: Distribute read load
   - Asynchronous replication with lag
   - Load balancing across replicas
   - Automatic promotion on primary failure

#### Data Processing Path
1. **Message Queue**: Decouple real-time and batch processing
   - Tech: RabbitMQ, Kafka, or AWS SQS
   - Guarantees: at-least-once or exactly-once semantics

2. **Async Workers**: Process background jobs
   - Consumer pools for parallel processing
   - Retry logic with exponential backoff
   - Dead-letter queues for failed messages

3. **Data Lake**: Store historical data
   - Tech: S3, HDFS, or BigQuery
   - Columnar format (Parquet) for analytics

4. **Search Index**: Enable rich queries
   - Tech: Elasticsearch, Solr, or Algolia
   - Real-time or near-real-time indexing

5. **Analytics Pipeline**: Generate insights
   - Tech: Spark, Presto, or BigQuery
   - Scheduled or on-demand processing

### Data Flow Scenarios

#### Scenario 1: Read Operation
1. Client requests data from API
2. API Gateway validates and routes request
3. Service checks Redis cache
4. Cache hit: Return cached data (P99 < 10ms)
5. Cache miss: Query read replica
6. Service updates cache and returns data
7. Log metrics: latency, cache hit ratio

#### Scenario 2: Write Operation
1. Client submits write request
2. API validates request and checks permissions
3. Service acquires write lock or uses transactions
4. Primary database executes write with durability
5. Synchronously update critical caches
6. Publish event to message queue
7. Acknowledge success to client
8. Async workers process side effects

#### Scenario 3: Cache Invalidation
1. Update committed to database
2. Synchronously invalidate cache entry
3. Publish invalidation event
4. Other services invalidate locally cached copies
5. Next request recomputes and caches fresh value

## Scalability Strategies

### Database Scaling

**Vertical Scaling (Temporary):**
- Increase CPU, RAM, storage on primary instance
- Enables 3-5x growth before hitting physical limits
- Requires downtime for most systems

**Horizontal Scaling (Long-term):**
1. **Read Replicas**: Distribute SELECT queries
   - Multiple read-only replicas in primary region
   - Cross-region replicas for geo-distribution
   - Route reads intelligently based on consistency requirements

2. **Sharding by Tenant/User ID**:
   - Partition data by user_id hash
   - Each shard handles subset of users
   - Reduces hot spots and load per instance

3. **Sharding by Time**:
   - New tables/shards for recent data
   - Old data archived to cold storage
   - Improves query performance on recent data

4. **Sharding by Geography**:
   - Regional shards for local consistency
   - Asynchronous sync between regions
   - Reduces latency for local operations

**Managing Hot Shards:**
- Identify shards with uneven load distribution
- Further subdivide hot shards
- Use consistent hashing for even distribution
- Monitor and rebalance periodically

### Cache Scaling

**Cache Tier Expansion:**
- Add Redis/Memcached nodes
- Use consistent hashing for key distribution
- Replicate hot keys across nodes
- Monitor hit ratio and adjust TTLs

**Multi-Level Caching:**
1. Local in-process cache (milliseconds)
2. Distributed cache (milliseconds, shared)
3. CDN cache (for static content, seconds)

### Service Tier Scaling

**Horizontal Scaling:**
- Stateless design enables easy replication
- Load balancer distributes across instances
- Add instances to handle peak load
- Auto-scaling based on CPU/memory metrics

**Optimizing for Throughput:**
- Connection pooling to databases
- Batch requests where possible
- Async I/O for external calls
- Worker thread pools sized appropriately

### Search Index Scaling

**Index Partitioning:**
- Shard index by document ID ranges
- Each shard on separate Elasticsearch node
- Query fans out to all shards
- Combine results at API layer

**Index Tiering:**
- Hot shard with latest data (in memory)
- Warm shard with older data
- Cold storage archive
- Move data between tiers as it ages

## High Availability & Reliability

### Replication Strategies

**Master-Slave (Primary-Replica):**
- Writes go to primary only
- Replicas lag behind by milliseconds to minutes
- Failover: promote replica to primary
- Trade-off: temporary inconsistency

**Multi-Master (Active-Active):**
- Writes distributed across multiple primaries
- Requires conflict resolution mechanism
- Higher availability, complex consistency
- Example: Cassandra, DynamoDB

**Quorum-Based:**
- Write to majority of replicas
- Read from minimum replicas
- Ensures consistency and availability
- Tunable consistency-availability trade-off

### Failover Mechanisms

**Automatic Detection:**
- Health checks every 5-10 seconds
- Multiple health check endpoints
- Circuit breakers for failing dependencies

**Failover Actions:**
1. Detect primary failure (3 failed health checks)
2. Elect new primary from healthy replicas
3. Update DNS to point to new primary
4. Notify monitoring and alert oncall
5. Queue database replication catchup
6. Gradual traffic shift to new primary

**Time to Recovery:**
- Detection: 30-60 seconds
- Promotion: 10-20 seconds
- DNS propagation: 30 seconds to 5 minutes
- Total RTO (Recovery Time Objective): < 2 minutes

### Disaster Recovery

**Backup Strategy:**
- Continuous binary log backups (WAL)
- Point-in-time recovery capability
- Daily snapshots replicated to different region
- Test restores monthly

**Recovery Scenarios:**
1. **Single Server Failure**: Promote replica (RTO < 2min, RPO < 1sec)
2. **Region Failure**: Failover to backup region (RTO < 10min, RPO < 5min)
3. **Datacenter Failure**: Activate warm standby (RTO < 5min, RPO < 1min)
4. **Data Corruption**: Restore from backups (RTO < 30min, RPO < 1hour)

## Data Consistency

### Consistency Models

**Strong Consistency:**
- Every read returns latest write
- Achieved through: synchronous replication or quorum reads
- Cost: higher latency, reduced availability
- Used for: financial transactions, critical state

**Eventual Consistency:**
- Replicas converge to same state over time
- Lower latency, higher availability
- May read stale data temporarily
- Used for: caches, user profiles, feeds

**Causal Consistency:**
- Causally dependent operations are ordered
- Other operations may be concurrent
- Middle ground between strong and eventual
- Used for: social feeds, comment threads

### Transaction Management

**ACID Transactions:**
- Atomicity: All-or-nothing
- Consistency: Valid state before and after
- Isolation: Concurrent transactions don't interfere
- Durability: Committed data persists

**Handling Distributed Transactions:**
1. **Two-Phase Commit (2PC)**: Coordinator pattern
   - Phase 1: All participants vote to commit/abort
   - Phase 2: Coordinator commands commit/abort
   - Blocking if coordinator fails

2. **Saga Pattern**: Long-running transactions
   - Each step is local transaction
   - Compensating transactions for rollback
   - No blocking, more resilient

3. **Event Sourcing**: Event log as source of truth
   - Store immutable events
   - Replay events to rebuild state
   - Natural audit trail

## Performance Optimization

### Latency Reduction

**Network Optimization:**
- Use HTTP/2 multiplexing
- Gzip compression for responses
- CDN for static content
- Keep-alive connections
- Local caches in edge locations

**Database Optimization:**
- Indexes on frequently queried columns
- Query execution plan analysis (EXPLAIN)
- Connection pooling
- Read replicas for reads
- Query result caching

**Caching Strategy:**
- Cache hot data (80/20 rule)
- TTL-based expiration
- Write-through pattern
- Preload on cache miss (never fully cold)
- Monitor hit ratio (target > 95%)

**Async Processing:**
- Move non-critical work to background
- Use message queues
- Background workers pick up jobs
- Results delivered via webhooks or polling

### Throughput Optimization

**Batch Operations:**
- Combine multiple operations into single request
- Reduces network round trips
- Example: bulk insert/update
- Must balance with latency

**Connection Pooling:**
- Maintain pool of database connections
- Reuse connections for multiple queries
- Avoid connection establishment overhead
- Monitor pool saturation

**Load Distribution:**
- Even distribution across shards
- Consistent hashing for key placement
- Identify and split hot shards
- Monitor per-instance QPS

## Security

### Authentication & Authorization

**Authentication:**
- OAuth2 for third-party apps
- JWT tokens for API access
- Session tokens with expiry
- MFA for sensitive operations

**Authorization:**
- Role-based access control (RBAC)
- Fine-grained permissions
- Audit all authorization decisions
- Principle of least privilege

### Data Protection

**In Transit:**
- TLS 1.3 for all connections
- Certificate pinning for mobile apps
- VPN for internal services

**At Rest:**
- Encryption with customer-managed keys
- Separate keys per customer/region
- Key rotation policies
- Hardware security modules (HSM)

**Sensitive Data:**
- Tokenization of payment card data
- Hashing of passwords with salt
- Personally identifiable data separation
- PII masking in logs

### Compliance

**Regulatory Requirements:**
- GDPR: Data residency, right to deletion
- PCI-DSS: Payment card security
- HIPAA: Healthcare data privacy
- SOC 2: Security controls audit

**Security Practices:**
- Regular penetration testing
- Bug bounty program
- Security incident response plan
- Regular security training

## Failure Handling & Resilience

### Common Failure Modes

**Network Failures:**
- Service A → Service B communication fails
- Mitigation: Timeouts, retries, circuit breakers
- Recovery: Automatic failover, degraded mode

**Database Failures:**
- Primary database becomes unavailable
- Mitigation: Replicas, sharding, backup systems
- Recovery: Automatic promotion, switchover

**Cache Failures:**
- Cache system unavailable (Redis crash)
- Mitigation: Cache redundancy, graceful degradation
- Impact: Increased database load, latency spike

**Load Spike:**
- 10x normal traffic suddenly
- Mitigation: Auto-scaling, rate limiting
- Recovery: Queue surge load, process gradually

### Resilience Patterns

**Timeouts:**
- All external calls have timeouts
- Default: 5-30 seconds depending on criticality
- Prevents cascading hangs
- Client times out and retries

**Retries:**
- Automatic retry on transient failures
- Exponential backoff: 100ms, 200ms, 400ms, 800ms
- Max retries: 3-5 depending on operation
- Idempotent operations for safe retries

**Circuit Breaker:**
- Monitor failure rate of dependency
- Open circuit on high failure rate
- Stop sending requests (fail fast)
- Half-open: test with single request
- Closed: resume normal operation

**Bulkhead Pattern:**
- Isolate critical resources
- Separate thread pools for different services
- Failure in one service doesn't affect others
- Prevents cascading failures

**Graceful Degradation:**
- Return partial results instead of failing
- Disable non-critical features
- Serve from cache even if stale
- Return cached results on primary failure

## Technology Stack Decision Matrix

| Component | Technology | Justification |
|-----------|-----------|---|
| **Language** | Java/Go/Python | Strong ecosystem, performance, team expertise |
| **API Framework** | Spring/Gin/Flask | Mature, well-tested, rich middleware |
| **Database** | PostgreSQL/MySQL | ACID guarantees, proven at scale, operational maturity |
| **Cache** | Redis | In-memory, rich data structures, pub-sub support |
| **Message Queue** | Kafka | Distributed, replay capability, exactly-once semantics |
| **Search** | Elasticsearch | Full-text search, near-real-time indexing |
| **Container** | Docker | Consistent deployment, resource isolation |
| **Orchestration** | Kubernetes | Auto-scaling, self-healing, multi-region |
| **Monitoring** | Prometheus + Grafana | Metrics, alerting, visualization |
| **Logging** | ELK/Loki | Centralized logs, structured, queryable |
| **Tracing** | Jaeger/Zipkin | Distributed tracing, latency analysis |


## Back-of-Envelope Calculations

### Traffic Metrics

**Daily Activity:**
- DAU: N/A
- RPS (Peak): N/A
- Average RPS: N/A / 3 = N/A / 3

**Data Volume (Daily):**
- Baseline calculation using RPS:
- Peak RPS: N/A
- Average RPS: Peak / 3
- Requests/day: Average RPS × 86400 seconds
- Data/request: varies by system type

### Storage Calculation

**Database Storage:**
- Current data: Based on daily growth rates
- Indexing overhead: +30% for indexes and metadata
- Backup copies: 3 replicas + daily snapshots
- Total: Current × replication factor

**Cache Layer:**
- Working set size: ~20% of total data
- Hot data: ~1-2% of total data
- Cache nodes needed: Working Set / (Node Capacity)

**CDN/Static Content:**
- Media distribution: Multi-tier caching
- Edge cache: Regional distribution
- Archive storage: Cold data tiered to S3

### Bandwidth Calculation

**Ingress:**
- Peak upload bandwidth: Peak RPS × avg request size
- Peak = 3× average
- Network redundancy: 2+ diverse paths

**Egress:**
- Download bandwidth: Streaming/serving data
- Peak surge: 5-10× during viral events
- CDN reduces origin bandwidth by 80-90%

### Cost Estimation

**Compute:**
- Load balanced instances: Peak RPS / 10K RPS per instance
- Redundancy: 2x for failover
- Reserved capacity: 20% headroom
- Cost: $0.30-0.50 per instance per hour

**Database:**
- Instance cost: $0.50-2.00 per hour
- Primary + replicas: 3-5 instances
- Storage: $0.10 per GB per month

**Networking:**
- Egress: $0.12 per GB
- CDN: $0.085 per GB
- Peak egress bandwidth drives costs

**Total Monthly Cost:**
- Compute: N/A RPS → Cost scales with traffic
- Database: Depends on data volume
- Networking: Depends on CDN usage
- Typical range: $1M - $10M+ per month

### Latency Budget

**Total P99 latency target: 100-500ms (varies by system)**

Budget breakdown:
- Network round trip: 10-50ms
- API Gateway processing: 5-10ms
- Service processing: 20-50ms
- Database query: 10-50ms
- Cache lookup: 1-5ms
- Response serialization: 5-10ms
- Network return: 10-50ms

### Availability Targets

**99.99% availability:**
- Downtime per year: 52 minutes
- Downtime per month: 4.38 minutes
- Downtime per day: 8.64 seconds

**Implies:**
- No single point of failure
- Multi-region redundancy
- Automated failover < 2 minutes RTO
- RPO < 1 minute for critical data


## Sample Code & API Specifications

### API Endpoints

[System-specific API endpoints to be documented]

### Rate Limits

[Rate limiting configuration]

### Authentication

[Authentication method]

### Sample Request/Response

[Code examples]


## AWS Architecture

### AWS Architecture Diagram

```mermaid
graph TB
    Users["End Users"]
    CloudFront["CloudFront<br/>CDN"]
    ALB["Application Load Balancer<br/>Auto Scaling"]
    ECS["ECS Fargate<br/>Service Instances"]
    RDS[("RDS Aurora<br/>Primary + Replicas")]
    RDSRead[("RDS Read Replica<br/>Multi-AZ")]
    ElastiCache["ElastiCache<br/>Redis Cluster"]
    DynamoDB["DynamoDB<br/>Distributed NoSQL"]
    S3["S3<br/>Object Storage"]
    SQS["SQS<br/>Message Queue"]
    Kinesis["Kinesis<br/>Streaming"]
    Lambda["Lambda<br/>Functions"]
    CloudWatch["CloudWatch<br/>Monitoring"]
    Route53["Route53<br/>DNS"]

    Users -->|Request| Route53
    Route53 -->|Route| CloudFront
    CloudFront -->|Cache Hit/Miss| ALB
    ALB -->|Distribute| ECS
    ECS -->|Query| ElastiCache
    ECS -->|Read| RDSRead
    ECS -->|Write| RDS
    ECS -->|NoSQL| DynamoDB
    ECS -->|Store| S3
    ECS -->|Queue| SQS
    SQS -->|Trigger| Lambda
    Lambda -->|Write| RDS
    Lambda -->|Publish| Kinesis
    Kinesis -->|Stream| Lambda
    ECS -->|Metrics| CloudWatch
    Lambda -->|Metrics| CloudWatch
    RDS -->|Metrics| CloudWatch

    style CloudFront fill:#FF9900
    style ALB fill:#FF9900
    style ECS fill:#FF9900
    style RDS fill:#527FFF
    style RDSRead fill:#527FFF
    style ElastiCache fill:#E74C3C
    style DynamoDB fill:#527FFF
    style S3 fill:#92C83E
    style SQS fill:#FF9900
    style Kinesis fill:#FF9900
    style Lambda fill:#FF9900
    style CloudWatch fill:#759C3E
    style Route53 fill:#FF9900
```




## Implementation Examples

## Python Implementation

### Installation

```bash
pip install fastapi uvicorn sqlalchemy redis pydantic python-dotenv
```

### Core Models

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class User(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime

class Post(BaseModel):
    id: str
    user_id: str
    content: str
    likes: int = 0
    comments: int = 0
    created_at: datetime

class Comment(BaseModel):
    id: str
    post_id: str
    user_id: str
    content: str
    created_at: datetime
```

### API Implementation

```python
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from redis import Redis
import os
import logging

app = FastAPI(title="Ebay Auction System", version="1.0.0")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=20, max_overflow=40)
SessionLocal = sessionmaker(bind=engine)

# Cache setup
cache = Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
    socket_keepalive=True,
    socket_keepalive_options={{
        1: 1,  # TCP_KEEPIDLE
        2: 1,  # TCP_KEEPINTVL
        3: 3,  # TCP_KEEPCNT
    }}
)

logger = logging.getLogger(__name__)

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication
async def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = authorization.replace("Bearer ", "")
    # Verify token against auth service
    user_id = cache.get(f"token:{token}")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user_id

# API Endpoints
@app.post("/api/v1/posts", status_code=201)
async def create_post(post: Post, user_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    '''Create a new post'''
    try:
        # Store in database
        db_post = PostModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            content=post.content,
            created_at=datetime.utcnow()
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)

        # Invalidate feed cache
        cache.delete(f"feed:{user_id}")

        logger.info(f"Post created: {db_post.id} by {user_id}")
        return db_post
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail="Failed to create post")

@app.get("/api/v1/posts/{post_id}")
async def get_post(post_id: str, db: Session = Depends(get_db)):
    '''Get post details'''
    # Try cache first
    cached = cache.get(f"post:{post_id}")
    if cached:
        return json.loads(cached)

    # Query database
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Cache for 1 hour
    cache.setex(f"post:{post_id}", 3600, json.dumps(post.to_dict()))

    return post

@app.get("/api/v1/users/{user_id}/feed")
async def get_feed(user_id: str, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    '''Get user feed with pagination'''
    cache_key = f"feed:{user_id}:{limit}:{offset}"

    # Try cache
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)

    # Get user's following list
    following = db.query(Follow).filter(Follow.follower_id == user_id).all()
    following_ids = [f.following_id for f in following] + [user_id]

    # Get posts from following
    posts = db.query(PostModel).filter(
        PostModel.user_id.in_(following_ids)
    ).order_by(PostModel.created_at.desc()).offset(offset).limit(limit).all()

    result = {{
        "posts": [p.to_dict() for p in posts],
        "nextOffset": offset + limit,
        "hasMore": len(posts) == limit
    }}

    # Cache for 5 minutes
    cache.setex(cache_key, 300, json.dumps(result))

    return result

@app.post("/api/v1/posts/{post_id}/like", status_code=200)
async def like_post(post_id: str, user_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    '''Like a post'''
    try:
        # Check if already liked
        existing = db.query(Like).filter(
            Like.post_id == post_id,
            Like.user_id == user_id
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Already liked")

        # Add like
        like = Like(
            id=str(uuid.uuid4()),
            post_id=post_id,
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.add(like)
        db.commit()

        # Invalidate cache
        cache.delete(f"post:{post_id}")

        return {{"status": "liked"}}
    except Exception as e:
        logger.error(f"Error liking post: {e}")
        raise HTTPException(status_code=500, detail="Failed to like post")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, workers=4)
```

### Database Models

```python
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class PostModel(Base):
    __tablename__ = "posts"

    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"), index=True)
    content = Column(String(5000))
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_user_id_created', 'user_id', 'created_at'),
    )

    def to_dict(self):
        return {{
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "likes": self.likes,
            "comments": self.comments,
            "created_at": self.created_at.isoformat()
        }}

class Like(Base):
    __tablename__ = "likes"

    id = Column(String(50), primary_key=True)
    post_id = Column(String(50), ForeignKey("posts.id"), index=True)
    user_id = Column(String(50), ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_post_user', 'post_id', 'user_id', unique=True),
    )
```

### Caching Layer

```python
from functools import wraps
from typing import Callable
import json

class CacheManager:
    def __init__(self, redis_client, ttl: int = 3600):
        self.redis = redis_client
        self.ttl = ttl

    def cached(self, key_prefix: str):
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{{key_prefix}}:{{':'.join(map(str, args))}}:{{':'.join(f'{{k}}={{v}}' for k,v in kwargs.items())}}"

                # Try cache
                cached = self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)

                # Execute function
                result = await func(*args, **kwargs)

                # Cache result
                self.redis.setex(cache_key, self.ttl, json.dumps(result))

                return result
            return wrapper
        return decorator

    def invalidate(self, pattern: str):
        '''Invalidate cache by pattern'''
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
```


## Java Implementation

### Maven Dependencies

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <version>3.0.0</version>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
    <version>3.0.0</version>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
    <version>3.0.0</version>
</dependency>
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.5.0</version>
</dependency>
<dependency>
    <groupId>redis.clients</groupId>
    <artifactId>jedis</artifactId>
    <version>4.3.0</version>
</dependency>
```

### Data Models

```java
package com.example.ebay_auction_system.model;

import lombok.Data;
import lombok.AllArgsConstructor;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@Entity
@Table(name = "posts", indexes = {{
    @Index(name = "idx_user_id_created", columnList = "user_id,created_at")
}})
public class Post {{
    @Id
    private String id;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(name = "content", nullable = false, length = 5000)
    private String content;

    @Column(name = "likes", columnDefinition = "integer default 0")
    private Integer likes = 0;

    @Column(name = "comments", columnDefinition = "integer default 0")
    private Integer comments = 0;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
}}

@Data
@AllArgsConstructor
@Entity
@Table(name = "likes", uniqueConstraints = {{
    @UniqueConstraint(columnNames = {{"post_id", "user_id"}}, name = "uk_post_user")
}}, indexes = {{
    @Index(name = "idx_post_id", columnList = "post_id"),
    @Index(name = "idx_user_id", columnList = "user_id")
}})
public class Like {{
    @Id
    private String id;

    @Column(name = "post_id", nullable = false)
    private String postId;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
}}
```

### Repository Layer

```java
package com.example.ebay_auction_system.repository;

import com.example.ebay_auction_system.model.Post;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface PostRepository extends JpaRepository<Post, String> {{
    Optional<Post> findById(String id);

    @Query(value = "SELECT p FROM Post p WHERE p.userId = :userId ORDER BY p.createdAt DESC LIMIT :limit OFFSET :offset")
    List<Post> findUserPosts(@Param("userId") String userId, @Param("limit") int limit, @Param("offset") int offset);

    @Query(value = "SELECT p FROM Post p WHERE p.userId IN :userIds ORDER BY p.createdAt DESC LIMIT :limit OFFSET :offset")
    List<Post> findFeedPosts(@Param("userIds") List<String> userIds, @Param("limit") int limit, @Param("offset") int offset);
}}
```

### Service Layer

```java
package com.example.ebay_auction_system.service;

import com.example.ebay_auction_system.model.Post;
import com.example.ebay_auction_system.repository.PostRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
@Slf4j
public class PostService {{
    private final PostRepository postRepository;
    private final RedisTemplate<String, Object> redisTemplate;

    private static final int CACHE_TTL = 3600; // 1 hour

    public Post createPost(String userId, String content) {{
        try {{
            Post post = new Post();
            post.setId(UUID.randomUUID().toString());
            post.setUserId(userId);
            post.setContent(content);
            post.setCreatedAt(LocalDateTime.now());
            post.setLikes(0);
            post.setComments(0);

            Post savedPost = postRepository.save(post);

            // Invalidate user's feed cache
            redisTemplate.delete("feed:" + userId + ":*");

            log.info("Post created: {} by {}", savedPost.getId(), userId);
            return savedPost;
        }} catch (Exception e) {{
            log.error("Error creating post", e);
            throw new RuntimeException("Failed to create post", e);
        }}
    }}

    public Post getPost(String postId) {{
        // Try cache first
        String cacheKey = "post:" + postId;
        Post cached = (Post) redisTemplate.opsForValue().get(cacheKey);
        if (cached != null) {{
            return cached;
        }}

        // Query database
        Optional<Post> post = postRepository.findById(postId);
        if (post.isEmpty()) {{
            throw new RuntimeException("Post not found");
        }}

        Post result = post.get();

        // Cache for 1 hour
        redisTemplate.opsForValue().set(cacheKey, result, CACHE_TTL, TimeUnit.SECONDS);

        return result;
    }}

    public List<Post> getUserFeed(String userId, int limit, int offset) {{
        String cacheKey = "feed:" + userId + ":" + limit + ":" + offset;

        // Try cache
        @SuppressWarnings("unchecked")
        List<Post> cached = (List<Post>) redisTemplate.opsForValue().get(cacheKey);
        if (cached != null) {{
            return cached;
        }}

        // TODO: Get user's following list
        List<String> followingIds = new ArrayList<>();
        followingIds.add(userId); // Include user's own posts

        // Get feed
        List<Post> feed = postRepository.findFeedPosts(followingIds, limit, offset);

        // Cache for 5 minutes
        redisTemplate.opsForValue().set(cacheKey, feed, 300, TimeUnit.SECONDS);

        return feed;
    }}

    public void likePost(String postId, String userId) {{
        try {{
            // Check if already liked
            // TODO: Check Like table

            // Add like (insert into Like table)
            // TODO: Save like

            // Update like count
            Post post = getPost(postId);
            post.setLikes(post.getLikes() + 1);
            postRepository.save(post);

            // Invalidate cache
            redisTemplate.delete("post:" + postId);

            log.info("Post {} liked by {}", postId, userId);
        }} catch (Exception e) {{
            log.error("Error liking post", e);
            throw new RuntimeException("Failed to like post", e);
        }}
    }}
}}
```

### REST Controller

```java
package com.example.ebay_auction_system.controller;

import com.example.ebay_auction_system.model.Post;
import com.example.ebay_auction_system.service.PostService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
@Slf4j
public class PostController {{
    private final PostService postService;

    @PostMapping("/posts")
    public ResponseEntity<Post> createPost(
            @RequestBody Post post,
            @RequestHeader("Authorization") String authHeader) {{
        try {{
            String userId = extractUserIdFromToken(authHeader);
            Post created = postService.createPost(userId, post.getContent());
            return ResponseEntity.status(HttpStatus.CREATED).body(created);
        }} catch (Exception e) {{
            log.error("Error creating post", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }}
    }}

    @GetMapping("/posts/{{postId}}")
    public ResponseEntity<Post> getPost(@PathVariable String postId) {{
        try {{
            Post post = postService.getPost(postId);
            return ResponseEntity.ok(post);
        }} catch (Exception e) {{
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }}
    }}

    @GetMapping("/users/{{userId}}/feed")
    public ResponseEntity<List<Post>> getUserFeed(
            @PathVariable String userId,
            @RequestParam(defaultValue = "20") int limit,
            @RequestParam(defaultValue = "0") int offset) {{
        try {{
            List<Post> feed = postService.getUserFeed(userId, limit, offset);
            return ResponseEntity.ok(feed);
        }} catch (Exception e) {{
            log.error("Error fetching feed", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }}
    }}

    @PostMapping("/posts/{{postId}}/like")
    public ResponseEntity<String> likePost(
            @PathVariable String postId,
            @RequestHeader("Authorization") String authHeader) {{
        try {{
            String userId = extractUserIdFromToken(authHeader);
            postService.likePost(postId, userId);
            return ResponseEntity.ok("{{"status":"liked"}}");
        }} catch (Exception e) {{
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }}
    }}

    private String extractUserIdFromToken(String authHeader) {{
        // TODO: Verify token and extract user ID
        return "user123";
    }}
}}
```

### Configuration

```java
package com.example.ebay_auction_system.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.StringRedisSerializer;

@Configuration
public class RedisConfig {{
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory) {{
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);

        StringRedisSerializer stringSerializer = new StringRedisSerializer();
        template.setKeySerializer(stringSerializer);
        template.setHashKeySerializer(stringSerializer);
        template.setValueSerializer(stringSerializer);

        return template;
    }}
}}
```


## Infrastructure as Code (Terraform)

### Terraform Infrastructure as Code

```hcl
# Provider configuration
terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = var.aws_region

  default_tags {{
    tags = {{
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      CreatedAt   = timestamp()
    }}
  }}
}}

# VPC and Networking
resource "aws_vpc" "main" {{
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {{
    Name = "${{var.project_name}}-vpc"
  }}
}}

resource "aws_subnet" "public" {{
  count                   = length(var.availability_zones)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {{
    Name = "${{var.project_name}}-public-subnet-${{count.index + 1}}"
  }}
}}

resource "aws_subnet" "private" {{
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {{
    Name = "${{var.project_name}}-private-subnet-${{count.index + 1}}"
  }}
}}

# Security Groups
resource "aws_security_group" "alb" {{
  name        = "${{var.project_name}}-alb-sg"
  description = "Security group for ALB"
  vpc_id      = aws_vpc.main.id

  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  ingress {{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
}}

resource "aws_security_group" "ecs" {{
  name        = "${{var.project_name}}-ecs-sg"
  description = "Security group for ECS tasks"
  vpc_id      = aws_vpc.main.id

  ingress {{
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
}}

# RDS Database
resource "aws_db_subnet_group" "main" {{
  name       = "${{var.project_name}}-db-subnet"
  subnet_ids = aws_subnet.private[*].id

  tags = {{
    Name = "${{var.project_name}}-db-subnet-group"
  }}
}}

resource "aws_rds_cluster" "main" {{
  cluster_identifier      = "${{var.project_name}}-cluster"
  engine                  = "aurora-postgresql"
  engine_version          = "15.2"
  database_name           = var.db_name
  master_username         = var.db_username
  master_password         = random_password.db_password.result
  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [aws_security_group.database.id]
  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  skip_final_snapshot     = false
  final_snapshot_identifier = "${{var.project_name}}-final-snapshot-${{formatdate("YYYY-MM-DD-hhmm", timestamp())}}"
  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = {{
    Name = "${{var.project_name}}-rds"
  }}
}}

resource "aws_rds_cluster_instance" "main" {{
  count              = var.db_instance_count
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = var.db_instance_class
  engine              = aws_rds_cluster.main.engine
  engine_version      = aws_rds_cluster.main.engine_version
  publicly_accessible = false

  tags = {{
    Name = "${{var.project_name}}-rds-instance-${{count.index + 1}}"
  }}
}}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "main" {{
  name       = "${{var.project_name}}-cache-subnet"
  subnet_ids = aws_subnet.private[*].id
}}

resource "aws_elasticache_cluster" "main" {{
  cluster_id           = "${{var.project_name}}-cache"
  engine               = "redis"
  node_type            = var.cache_node_type
  num_cache_nodes      = var.cache_node_count
  parameter_group_name = aws_elasticache_parameter_group.main.name
  engine_version       = "7.0"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.cache.id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  automatic_failover_enabled = true

  tags = {{
    Name = "${{var.project_name}}-redis"
  }}
}}

# ECS Cluster and Service
resource "aws_ecs_cluster" "main" {{
  name = "${{var.project_name}}-cluster"

  setting {{
    name  = "containerInsights"
    value = "enabled"
  }}
}}

resource "aws_ecs_task_definition" "main" {{
  family                   = var.project_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{{
    name      = var.project_name
    image     = var.docker_image
    essential = true
    portMappings = [{{
      containerPort = var.container_port
      hostPort      = var.container_port
      protocol      = "tcp"
    }}]
    environment = [
      {{
        name  = "DB_HOST"
        value = aws_rds_cluster.main.endpoint
      }},
      {{
        name  = "CACHE_HOST"
        value = aws_elasticache_cluster.main.cache_nodes[0].address
      }},
      {{
        name  = "ENVIRONMENT"
        value = var.environment
      }}
    ]
    secrets = [
      {{
        name      = "DB_PASSWORD"
        valueFrom = aws_secretsmanager_secret_version.db_password.arn
      }}
    ]
    logConfiguration = {{
      logDriver = "awslogs"
      options = {{
        awslogs-group         = aws_cloudwatch_log_group.ecs.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "ecs"
      }}
    }}
  }}])
}}

resource "aws_ecs_service" "main" {{
  name            = "${{var.project_name}}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = var.desired_task_count
  launch_type     = "FARGATE"
  network_configuration {{
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }}
  load_balancer {{
    target_group_arn = aws_lb_target_group.main.arn
    container_name   = var.project_name
    container_port   = var.container_port
  }}

  depends_on = [
    aws_lb_listener.main,
    aws_iam_role_policy.ecs_task_execution_role_policy
  ]

  tags = {{
    Name = "${{var.project_name}}-service"
  }}
}}

# Application Load Balancer
resource "aws_lb" "main" {{
  name               = "${{var.project_name}}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false

  tags = {{
    Name = "${{var.project_name}}-alb"
  }}
}}

resource "aws_lb_target_group" "main" {{
  name        = "${{var.project_name}}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {{
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 30
    path                = "/"
    matcher             = "200"
  }}

  tags = {{
    Name = "${{var.project_name}}-tg"
  }}
}}

resource "aws_lb_listener" "main" {{
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {{
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }}
}}

# CloudWatch Monitoring
resource "aws_cloudwatch_log_group" "ecs" {{
  name              = "/ecs/${{var.project_name}}"
  retention_in_days = 7

  tags = {{
    Name = "${{var.project_name}}-logs"
  }}
}}

# Variables
variable "aws_region" {{
  default = "us-east-1"
}}

variable "project_name" {{
  default = "my-app"
}}

variable "environment" {{
  default = "production"
}}

variable "vpc_cidr" {{
  default = "10.0.0.0/16"
}}

variable "availability_zones" {{
  default = ["us-east-1a", "us-east-1b"]
}}

variable "docker_image" {{
  default = "my-account.dkr.ecr.us-east-1.amazonaws.com/my-app:latest"
}}

variable "container_port" {{
  default = 8080
}}

variable "db_name" {{
  default = "myapp"
}}

variable "db_username" {{
  default = "postgres"
}}

variable "db_instance_class" {{
  default = "db.r6g.large"
}}

variable "db_instance_count" {{
  default = 2
}}

variable "cache_node_type" {{
  default = "cache.r6g.large"
}}

variable "cache_node_count" {{
  default = 2
}}

variable "task_cpu" {{
  default = "1024"
}}

variable "task_memory" {{
  default = "2048"
}}

variable "desired_task_count" {{
  default = 3
}}

# Outputs
output "alb_dns_name" {{
  value = aws_lb.main.dns_name
}}

output "rds_endpoint" {{
  value = aws_rds_cluster.main.endpoint
}}

output "redis_endpoint" {{
  value = aws_elasticache_cluster.main.cache_nodes[0].address
}}
```

## Product Requirements Document (PRD)

### Overview

Ebay Auction System is a mission-critical system serving N/A users globally.
This PRD defines requirements for scaling, reliability, and performance at this unprecedented scale.

### Functional Requirements



### Non-Functional Requirements

**Performance:**
- Latency: N/A
- Throughput: N/A
- Concurrent users: N/A DAU, N/A RPS peak

**Reliability:**
- Availability: N/A
- Data durability: 99.999999% (8 nines)
- RTO (Recovery Time Objective): < 2 minutes
- RPO (Recovery Point Objective): < 1 minute

**Scalability:**
- N/A
- Horizontal scaling for all tiers
- Auto-scaling based on metrics
- Handle 10x load spikes gracefully

**Consistency:**
- Model: N/A
- Critical data: Strong ACID guarantees
- Non-critical data: Eventual consistency acceptable

### User Roles & Personas

**End Users:**
- Need: Fast, reliable access to services
- Pain point: Downtime, slow response times
- Success metric: P99 latency < target, 99.99% uptime

**Business Stakeholders:**
- Need: Revenue generation, market expansion
- Pain point: Scale limitations, operational costs
- Success metric: Supports 10x growth, cost per user decreases

**Operations/SRE:**
- Need: System visibility and control
- Pain point: Complex failure modes, unclear blame
- Success metric: MTTR < 5 minutes, clear root causes

**Developers:**
- Need: Simple APIs, good documentation
- Pain point: Operational complexity, debugging
- Success metric: Easy to understand, debug, and extend

### Success Metrics

**Technical Metrics:**
- P50 latency: < 50ms
- P99 latency: P99 < 100ms
- P99.9 latency: < 1s
- Availability: > 99.99%
- Error rate: < 0.1%
- Cache hit ratio: > 95%
- Database replication lag: < 1 second

**Business Metrics:**
- Daily active users: N/A
- Monthly active users: N/A
- Request success rate: > 99.9%
- Customer satisfaction: > 4.5/5

**Operational Metrics:**
- Mean time to resolution: < 30 minutes
- Deployment frequency: Daily
- Change failure rate: < 5%
- Incident response time: < 15 minutes

### Constraints & Assumptions

**Constraints:**
- Global latency: Can't reduce network physics
- Data center failover: 30-60s detection + 1-2min failover
- Budget: Must optimize cost per request
- Compliance: GDPR, SOC2, PCI-DSS requirements

**Assumptions:**
- Team has Kubernetes expertise
- Access to managed database services
- Multi-region deployment possible
- Cloud budget is flexible for auto-scaling

### Out of Scope (Phase 1)

- Blockchain/crypto integration
- Quantum-resistant encryption
- Machine learning model training (covered separately)
- Mobile app optimization (covered separately)

### Success Criteria

1. System operates at scale: N/A users
2. Maintains SLOs: N/A latency, 99.99% availability
3. Cost per request: $0.0001 or lower
4. Team can troubleshoot issues < 30 minutes
5. Can scale 10x in < 1 week
6. Zero data loss in any failure scenario


## Architecture & Flow Diagrams

### System Architecture

```mermaid
graph TB
    Client["Client/User"]
    Gateway["API Gateway<br/>Rate Limit, Auth"]
    LB["Load Balancer"]
    Service["Service Tier<br/>Business Logic"]
    Cache["Cache Layer<br/>Redis/Memcached"]
    Primary["Primary DB<br/>ACID Guarantees"]
    Replica["Read Replica<br/>Async Sync"]
    Queue["Message Queue<br/>Kafka/RabbitMQ"]
    Workers["Async Workers<br/>Background Jobs"]
    Index["Search Index<br/>Elasticsearch"]
    Lake["Data Lake<br/>S3/HDFS"]
    Analytics["Analytics Pipeline<br/>Spark/Presto"]

    Client -->|Request| Gateway
    Gateway -->|Route| LB
    LB -->|Distribute| Service
    Service -->|Check Cache| Cache
    Service -->|Query| Replica
    Service -->|Write| Primary
    Primary -->|Replicate| Replica
    Service -->|Publish Event| Queue
    Queue -->|Consume| Workers
    Workers -->|Index| Index
    Workers -->|Archive| Lake
    Lake -->|Process| Analytics
    Cache -->|Return| Service
    Index -->|Search Results| Service
    Service -->|Response| Gateway
    Gateway -->|Return| Client

    style Gateway fill:#ff9999
    style LB fill:#ff9999
    style Service fill:#99ccff
    style Cache fill:#99ff99
    style Primary fill:#ffcc99
    style Replica fill:#ffcc99
    style Queue fill:#cc99ff
    style Workers fill:#cc99ff
    style Index fill:#ffff99
    style Lake fill:#99ffff
    style Analytics fill:#99ffff
```

### Data Flow: Read vs Write

```mermaid
graph LR
    subgraph Read["Read Operation (Fast Path)"]
        R1["Request"] --> R2{"Cache Hit?"}
        R2 -->|Yes| R3["Return from Cache<br/>P99 < 10ms"]
        R2 -->|No| R4["Query Replica<br/>P99 < 50ms"]
        R4 --> R5["Update Cache"]
        R5 --> R3
    end

    subgraph Write["Write Operation (Consistency Path)"]
        W1["Request"] --> W2["Validate & Auth"]
        W2 --> W3["Write to Primary<br/>Sync Durability"]
        W3 --> W4["Update Cache<br/>Write-Through"]
        W4 --> W5["Publish Event"]
        W5 --> W6["Acknowledge Client"]
        W5 --> W7["Async Workers<br/>Background Processing"]
    end

    style Read fill:#e1f5e1
    style Write fill:#fff4e1
    style R3 fill:#90EE90
    style W6 fill:#FFD700
```

### Failover & Recovery Flow

```mermaid
graph TD
    Normal["System Operating Normally"]
    Detect["Detect Primary Failure<br/>3 failed checks = 30-60s"]
    Promote["Promote Read Replica<br/>to Primary<br/>10-20s"]
    DNS["Update DNS<br/>Propagate<br/>30s-5min"]
    Recovery["System Recovers<br/>RTO &lt; 2 minutes"]
    Verify["Verify Data<br/>Consistency"]
    Monitor["Monitor Catchup<br/>Apply WAL"]
    Restore["Restore from Backup<br/>Point-in-time Recovery<br/>RTO &lt; 30min"]

    Normal -->|Health Check Fails| Detect
    Detect --> Promote
    Promote --> DNS
    DNS --> Recovery
    Recovery --> Verify
    Verify --> Monitor
    Monitor --> Normal
    Normal -->|Data Corruption| Restore
    Restore --> Verify

    style Normal fill:#90EE90
    style Detect fill:#FFB6C1
    style Promote fill:#FF69B4
    style DNS fill:#FF69B4
    style Recovery fill:#FFD700
    style Verify fill:#87CEEB
    style Monitor fill:#87CEEB
    style Restore fill:#FF69B4
```

### Scaling Strategies

```mermaid
graph TD
    Load["Increasing Load"]
    CS1["Add Redis Nodes"]
    CS2["Consistent Hashing"]
    CS3["Replicate Hot Keys"]
    SS1["Horizontal Scaling"]
    SS2["Stateless Instances"]
    SS3["Auto-scaling Groups"]
    DS1["Read Replicas"]
    DS2["Sharding by User ID"]
    DS3["Split Hot Shards"]
    ES1["Index Sharding"]
    ES2["Multiple Nodes"]
    ES3["Tiered Indexes"]
    Scale["System Scales<br/>10x Capacity"]

    Load -->|Cache Tier| CS1
    CS1 --> CS2
    CS2 --> CS3
    Load -->|Service Tier| SS1
    SS1 --> SS2
    SS2 --> SS3
    Load -->|Database Tier| DS1
    DS1 --> DS2
    DS2 --> DS3
    Load -->|Search Tier| ES1
    ES1 --> ES2
    ES2 --> ES3
    CS3 --> Scale
    SS3 --> Scale
    DS3 --> Scale
    ES3 --> Scale

    style Load fill:#FFB6C1
    style Scale fill:#90EE90
    style CS3 fill:#87CEEB
    style SS3 fill:#87CEEB
    style DS3 fill:#87CEEB
    style ES3 fill:#87CEEB
```

### Data Consistency Patterns

```mermaid
graph TB
    Write["Write to Primary Database<br/>Sync Durability Guarantee"]
    Choice{"Consistency<br/>Level Needed?"}
    Strong["Synchronous Replication<br/>Wait for all replicas<br/>Higher latency, higher reliability"]
    Eventual["Asynchronous Replication<br/>Don't wait for replicas<br/>Low latency, temporary inconsistency"]
    Causal["Track causal dependencies<br/>Causally related ops ordered<br/>Balance latency and consistency"]
    Replicate["Replicate to All Nodes<br/>Confirm before ACK"]
    ReplicateA["Replicate to All Nodes<br/>ACK immediately"]
    ReplicateC["Replicate with Version Info<br/>Maintain causal order"]
    Data["All replicas<br/>have latest data<br/>RPO = 0"]
    DataA["Replicas lag<br/>behind primary<br/>RPO = seconds"]
    DataC["Causally dependent<br/>operations ordered<br/>RPO = seconds"]

    Write --> Choice
    Choice -->|Strong| Strong
    Choice -->|Eventual| Eventual
    Choice -->|Causal| Causal
    Strong --> Replicate
    Eventual --> ReplicateA
    Causal --> ReplicateC
    Replicate --> Data
    ReplicateA --> DataA
    ReplicateC --> DataC

    style Write fill:#FFD700
    style Choice fill:#FFA500
    style Strong fill:#FF6B6B
    style Eventual fill:#4ECDC4
    style Causal fill:#95E1D3
```


## Capacity Planning

### Traffic Projection
- Current: 100K RPS
- 50% YoY growth
- Peak: 2-3x average
- Capacity planning: 5-10x headroom for growth

### Resource Estimation

**Compute:**
- 1 instance per 10K RPS (based on profiling)
- 100K RPS → 10 instances in production
- 20% reserved for failover
- Total: 12 instances minimum

**Memory:**
- Application: 2-4GB per instance
- Cache layer: 100GB (hot working set)
- Database: 500GB (indexes + data)
- Total: ~1TB for typical workload

**Storage:**
- Current data: 10TB
- Backup retention: 30 days
- Growth: 50% YoY
- Budget: 50TB (with expansion headroom)

### Cost Analysis

**Computation Cost:**
- 12 instances × $0.50/hour × 730 hours = $4,380/month
- Scaling: Auto-scale to 30 instances peak = $10,950/month

**Database Cost:**
- Primary (2-CPU, 16GB): $500/month
- Replicas (3x): $1,500/month
- Backups (30 days): $200/month
- Total: $2,200/month

**Network Cost:**
- Egress (100TB/month): $800/month
- CDN (50TB/month): $400/month
- Total: $1,200/month

**Storage Cost:**
- Active storage (10TB): $200/month
- Archive (100TB): $100/month
- Total: $300/month

**Total Monthly Cost: ~$8,000-15,000**
**Per-Request Cost: ~$0.001-0.005**

## Lessons Learned

1. **Cache Invalidation is Hard**: Keeping caches consistent with data is ongoing challenge. Strategies: TTL-based expiration, event-driven invalidation, cache warming.

2. **Scaling Write Path is Critical**: Read scaling via replicas is easy; write scaling requires sharding or partitioning. Plan sharding strategy early.

3. **Operational Complexity Grows Non-Linearly**: Each new component adds monitoring, alerting, and failure scenarios. Simplicity is valuable.

4. **Network Failures are Common**: Assume network is unreliable; use timeouts, retries, and circuit breakers everywhere.

5. **One Customer Can Break Entire System**: Unguarded queries from single customer can starve resources. Implement per-customer quotas and limits.

6. **Monitoring is Non-Optional**: Cannot operate system without visibility. Invest heavily in metrics, logs, and traces.

## Common Interview Questions

1. **How would you scale the write path to handle 10x growth?**
   - Discuss sharding strategy, key selection, rebalancing
   - Trade-offs: consistency, operational complexity
   - Example scenarios: user-id sharding, time-based partitioning

2. **Describe the flow when primary database fails.**
   - Detection mechanism and timeline
   - Replica promotion logic
   - Data consistency considerations
   - RTO and RPO targets

3. **How do you handle cache inconsistency?**
   - Scenarios: stale cache, cache eviction, partial updates
   - Strategies: TTL, event-driven invalidation, double-write
   - Trade-offs between consistency and performance

4. **Design a circuit breaker for external API calls.**
   - State machine: closed, open, half-open
   - Failure detection metrics
   - Recovery backoff strategy
   - Metrics/monitoring

5. **How would you handle a 10x traffic spike?**
   - Auto-scaling mechanisms
   - Rate limiting strategy
   - Queue overflow handling
   - Graceful degradation decisions

6. **Explain your replication strategy.**
   - Master-slave vs multi-master
   - Consistency guarantees and gaps
   - Failover process
   - Operational implications

7. **Design the data pipeline for analytics.**
   - Streaming vs batch trade-offs
   - Data schema and partitioning
   - Freshness vs cost trade-off
   - Example queries and performance

## Related Systems

- **Instagram-Scale Photo Sharing**: Similar image storage, feed generation, search
- **LinkedIn Recommendations**: Batch processing, ML pipeline, social graph
- **YouTube Video Platform**: Content delivery, recommendation engine, real-time metrics
- **Spotify Music Streaming**: Personalization, offline sync, cross-device experience
- **Twitter Feed**: Timeline generation, hot shard handling, real-time updates

---

**Last Updated:** 2026-05-15
**Difficulty:** Hard
**Time to Design:** 45-60 minutes
**Time to Implement:** 2-3 weeks


## Back-of-the-Envelope Calculations

**System Load Estimation:**
- 1M daily active users × 10 requests/day = 10M requests/day
- Peak QPS = 10M / 86400 × 3 (peak factor) ≈ 350 QPS
- API server capacity: 1000 QPS/server → 1 server sufficient at peak
- With 2x redundancy: 2 servers minimum

**Storage Estimation:**
- 1M users × 10KB average data = 10GB structured data
- Annual growth: 10GB × 365 = 3.65TB/year
- With 3x replication: 11TB/year
- SSD cost ($0.10/GB): $1,100/year

**Bandwidth:**
- 350 QPS × 10KB response = 3.5MB/sec outbound
- Monthly egress: 3.5MB × 86400 × 30 = 9TB/month
## Follow-up Questions

1. **How would you handle this at 10x the scale described?**
   - What breaks first? (typically: single DB, single cache node, single region)
   - What architectural changes are required?

2. **What are the consistency vs. availability trade-offs in your design?**
   - Where did you accept eventual consistency?
   - Which operations require strong consistency and why?

3. **How would you debug a sudden latency spike in production?**
   - What metrics would you look at first?
   - What's your runbook for the top 3 likely causes?

4. **How does your design handle partial failures?**
   - What happens if one component is slow (not down)?
   - How do you prevent cascading failures?

5. **What would you change if you had to build this in one week vs. six months?**
   - What corners can safely be cut initially?
   - What must be right from day one?

6. **How would you migrate from the current design to a better one without downtime?**
   - What's the strangler-fig or blue-green strategy here?
   - How do you validate correctness during migration?