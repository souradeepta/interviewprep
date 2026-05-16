# Interview & System Design Frameworks

Comprehensive guide to mastering technical interviews, system design, and building scalable systems.

---

## Interview Frameworks

### 🎯 Coding Interview Framework
**File:** [coding-interview-framework.md](coding-interview-framework.md)

Master the 45-minute algorithmic problem-solving interview with a proven 5-phase approach.

- **Phase 1: Clarify & Verify (5 min)** — Ask about constraints, edge cases, optimization targets
- **Phase 2: Think Aloud (2-3 min)** — Discuss brute force, identify patterns, propose optimization
- **Phase 3: Code Cleanly (25-30 min)** — Write readable code with good naming and structure
- **Phase 4: Test & Verify (5-8 min)** — Run test cases, verify correctness, trace through
- **Phase 5: Complexity & Discussion (5-10 min)** — Explain complexity, discuss improvements

Best practices for each phase, common mistakes to avoid, and problem-solving patterns.

### 🎤 Behavioral Interview Framework
**File:** [behavioral-interview-framework.md](behavioral-interview-framework.md)

Master behavioral/competency interviews using the STAR method and structured storytelling.

- **STAR Method** — Situation, Task, Action, Result structure for every story
- **Question Categories** — Teamwork, problem-solving, leadership, learning, impact
- **Story Preparation** — How to prepare 8-10 compelling stories covering 5-6 categories
- **Interview Tips** — Communication patterns, red flags to avoid, green flags to show

Common behavioral questions across 5 major categories with example STAR responses.

### 📊 Interview Grading Rubric
**File:** [interview-grading-rubric.md](interview-grading-rubric.md)

Understand what interviewers are looking for and how they score candidates.

- **Coding Interview Rubric** — 6 criteria on 4-point scale (understanding, approach, code, testing, complexity, optimization)
- **System Design Rubric** — 6 criteria (requirements, architecture, deep dive, scaling, trade-offs, communication)
- **Behavioral Rubric** — 5 criteria (story structure, ownership, impact, learning, cultural fit)
- **Scoring Thresholds** — What scores = hire vs no hire at different companies

Understand red flags and green flags that significantly impact your score.

---

## System Design Frameworks

### 🏗️ System Design Interview Guide
**File:** [system-design-interview-guide.md](system-design-interview-guide.md)

Proven 4-phase framework for designing systems during 45-60 minute technical interviews.

- **Phase 1: Requirements & Clarification (5-10 min)** — Scope the problem, agree on constraints
- **Phase 2: High-Level Architecture (10-15 min)** — Sketch major components and data flow
- **Phase 3: Deep Dive (15-20 min)** — Design 2-3 critical components in detail
- **Phase 4: Trade-offs & Scaling (10-15 min)** — Discuss alternatives and handle scale increases

Templates, decision frameworks, and best practices for each phase.

### 🔧 API Design Framework
**File:** [api-design-framework.md](api-design-framework.md)

Design robust, scalable APIs using REST, GraphQL, and gRPC patterns.

- **REST API Design** — Resource-oriented, standard methods, status codes, best practices
- **GraphQL** — Schema design, avoiding N+1, caching challenges, when to use vs REST
- **gRPC** — Protocol buffers, performance optimization, internal service communication
- **Versioning** — URL vs header-based, deprecation strategies
- **Security** — Authentication (API keys, OAuth), authorization, rate limiting, CORS

Decision tree for choosing API type and detailed design templates.

### 💾 Data Modeling Framework
**File:** [data-modeling-framework.md](data-modeling-framework.md)

Design database schemas that scale, are normalized, and handle real-world requirements.

- **SQL Normalization** — 1NF through BCNF with examples and when to denormalize
- **SQL Schema Design** — Primary keys, indexes, foreign keys, composite indexes
- **NoSQL Design** — Document structure, when to denormalize, indexing strategies
- **Many-to-Many** — Junction tables, denormalization trade-offs
- **Sharding Strategies** — By user ID, by range, by geography, partition selection

Indexing strategies, soft deletes, event sourcing, and CQRS patterns.

### 🔍 Distributed Systems Patterns
**File:** [distributed-systems-patterns.md](distributed-systems-patterns.md)

Essential patterns for building resilient, scalable distributed systems at scale.

- **Replication** — Master-slave, master-master, consistency tradeoffs
- **Sharding/Partitioning** — Distribute data across servers, hotspot mitigation
- **Caching** — Cache-aside, write-through, write-behind strategies
- **Message Queues** — Decouple services, handle async workloads, ensure delivery
- **Service Discovery** — Automatic service finding, health checks
- **Circuit Breaker** — Fail fast, prevent cascading failures
- **Retry Logic** — Exponential backoff, idempotency for safe retries
- **Consensus** — Raft algorithm for leader election and log replication

12 essential patterns with detailed explanations and trade-offs.

### ⚡ Performance Optimization Framework
**File:** [performance-optimization-framework.md](performance-optimization-framework.md)

Systematic approach to identifying bottlenecks, measuring performance, and optimizing systems.

- **Phase 1: Measure & Profile** — APM tools, profiling, metric targets
- **Phase 2: Identify Bottleneck** — CPU, memory, disk I/O, network, database
- **Phase 3: Optimize Specific Layer** — Algorithm, database, caching, network optimization
- **Phase 4: Re-measure & Verify** — Benchmarking before/after, Amdahl's law
- **Phase 5: Deploy & Monitor** — Canary rollout, monitoring dashboard, alerting

Common bottlenecks by layer and optimization techniques with concrete examples.

### 📐 Estimation Techniques
**File:** [estimation-techniques.md](estimation-techniques.md)

Master back-of-the-envelope estimation for capacity planning and scalability math.

- **Power-of-10 Thinking** — Memorize key numbers (bytes, latency, throughput)
- **QPS Estimation** — Calculate queries per second from DAU and usage patterns
- **Storage Estimation** — Calculate database and media storage requirements
- **Bandwidth Estimation** — Estimate network throughput needs
- **Server Count** — Calculate servers needed for QPS, add redundancy and headroom
- **Scaling Formulas** — Calculate impact of caching, sharding, replication
- **Cost Analysis** — On-premise vs cloud, capacity planning timeline

Common estimation scenarios and order-of-magnitude reference table.

### 📋 Design Patterns Reference
**File:** [design-patterns-reference.md](design-patterns-reference.md)

Gang of Four design patterns and where they appear in real system designs.

- **Creational Patterns** — Singleton, Factory, Abstract Factory
- **Structural Patterns** — Adapter, Decorator, Facade, Proxy
- **Behavioral Patterns** — Observer, Strategy, Command, Iterator, Template Method

Where each pattern appears in system design with concrete examples.

### 📝 Common System Design Follow-ups
**File:** [common-follow-ups.md](common-follow-ups.md)

Expected interviewer follow-up questions for 20+ system design problems.

- **Social systems** — News feed, followers, like/comment, photo sharing
- **Commerce systems** — E-commerce, payment, auction, wallet
- **Real-time systems** — Chat, notifications, live stream
- **Infrastructure** — Rate limiter, load balancer, API gateway

Likely follow-ups with suggested answers showing deep thinking.

---

## How to Use These Frameworks

### 📚 Before Interviews

1. **1 week before coding interview:**
   - Read [Coding Interview Framework](coding-interview-framework.md)
   - Practice 3-5 medium problems with the 5-phase approach
   - Review common mistakes section

2. **1 week before system design interview:**
   - Read [System Design Interview Guide](system-design-interview-guide.md)
   - Design 2 systems end-to-end (2-3 hours each)
   - Review [Distributed Systems Patterns](distributed-systems-patterns.md) for deep dive ideas
   - Skim [Estimation Techniques](estimation-techniques.md) for back-of-envelope calculations

3. **1 week before behavioral interviews:**
   - Read [Behavioral Interview Framework](behavioral-interview-framework.md)
   - Prepare 8-10 STAR stories covering 6 categories
   - Do mock behavioral interview with friend
   - Review red flags and green flags

### 🎓 During Interview Preparation

- Use [API Design Framework](api-design-framework.md) to design REST/GraphQL APIs
- Use [Data Modeling Framework](data-modeling-framework.md) for schema design discussions
- Use [Performance Optimization Framework](performance-optimization-framework.md) for deep dives
- Check [Interview Grading Rubric](interview-grading-rubric.md) to understand what "excellent" looks like

### 🏢 When Designing New Systems

- Start with [System Design Interview Guide](system-design-interview-guide.md) 4-phase framework
- Use [Distributed Systems Patterns](distributed-systems-patterns.md) to choose patterns
- Use [Estimation Techniques](estimation-techniques.md) for capacity planning
- Use [Performance Optimization Framework](performance-optimization-framework.md) for scaling

---

## Complete Framework List

| Framework | Focus | Duration | Difficulty |
|-----------|-------|----------|-----------|
| Coding Interview | Algorithms, problem-solving | 45 min | Medium |
| Behavioral Interview | Storytelling, communication | 45 min | Easy |
| System Design Interview | Architecture, scalability | 60 min | Hard |
| API Design | REST/GraphQL design | Reference | Medium |
| Data Modeling | Database schema design | Reference | Medium |
| Distributed Systems | Patterns, fault tolerance | Reference | Hard |
| Performance Optimization | Profiling, bottleneck identification | Reference | Hard |
| Estimation Techniques | Capacity planning math | Reference | Medium |
| Design Patterns | Gang of Four patterns | Reference | Medium |
| Grading Rubric | Understanding evaluation | Reference | Easy |
| Common Follow-ups | Expected interviewer questions | Reference | Easy |

---

## Example Systems

This repo includes 35+ system design implementations in `python/system_design/`:

- **Social:** News feed, followers, likes, comments, photo sharing
- **Commerce:** E-commerce, auction, payment, wallet
- **Real-Time:** Chat, notifications, live streaming
- **Distributed:** Consensus, transactions, saga pattern
- **Infrastructure:** Load balancer, rate limiter, circuit breaker, API gateway
- **Data:** Search, recommendations, time series, log aggregation
- **Advanced:** Parking lot, leaderboard, ride sharing, message queue, pub/sub

---

## Quick Start

**New to interviews?**
1. Start with [Coding Interview Framework](coding-interview-framework.md)
2. Then [Behavioral Interview Framework](behavioral-interview-framework.md)

**Preparing for system design?**
1. Read [System Design Interview Guide](system-design-interview-guide.md)
2. Study [Distributed Systems Patterns](distributed-systems-patterns.md)
3. Master [Estimation Techniques](estimation-techniques.md)

**Want to understand what interviewers look for?**
- Read [Interview Grading Rubric](interview-grading-rubric.md)

**Building actual systems?**
- Use [API Design Framework](api-design-framework.md) for API design
- Use [Data Modeling Framework](data-modeling-framework.md) for database schema
- Use [Performance Optimization Framework](performance-optimization-framework.md) for scaling
- Refer to [Distributed Systems Patterns](distributed-systems-patterns.md) for architecture patterns
