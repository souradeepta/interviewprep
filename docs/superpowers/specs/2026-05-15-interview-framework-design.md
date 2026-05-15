# Design: Hierarchical Interview Framework for Pattern Matching & System Design

**Date:** 2026-05-15  
**Objective:** Make the datastructures repo more comprehensive for interview prep by adding two key resources:
1. Problem-to-Pattern Matcher — structured index mapping problem types to best-fit DS/algorithms
2. System Design Interview Framework — step-by-step guide with checklists and common follow-ups

**Format:** Markdown guides in `/docs` organized hierarchically, linked from main README.

---

## Goals

1. **Problem Matcher:** Help interviewees recognize problem types and immediately know which data structure/algorithm to use
2. **System Design Frameworks:** Provide a systematic approach to talking through system design interviews
3. **Comprehensive Reference:** Single source of truth for all interview prep patterns and frameworks
4. **Keyed to Repo:** Cross-link to existing Python/Java implementations and system designs for hands-on learning

---

## Architecture

### Directory Structure

```
docs/
├── patterns/
│   ├── README.md                              # Navigation hub
│   ├── problem-to-pattern-matcher.md          # Master index of all problem types
│   ├── array-and-string-problems.md           # Sliding window, prefix sum, two pointers, etc.
│   ├── linked-list-problems.md                # Fast/slow pointers, cycle detection, reversals
│   ├── stack-and-queue-problems.md            # Monotonic stacks, BFS/DFS via queues
│   ├── tree-problems.md                       # BST, traversals, LCA, subtree matching
│   ├── graph-problems.md                      # DFS, BFS, Dijkstra, topological sort, MST
│   ├── dynamic-programming-problems.md        # Knapsack, LIS, DP table patterns
│   ├── greedy-problems.md                     # Activity selection, huffman coding
│   ├── bit-manipulation-problems.md           # Bit tricks, XOR, subsets
│   ├── design-problems.md                     # LRU, LFU, Trie-based, custom DS
│   ├── math-and-geometry-problems.md          # GCD, primes, coordinate geometry
│   └── advanced-patterns.md                   # Segment tree, Fenwick, DSU, Treap, Heavy-Light
│
└── frameworks/
    ├── README.md                              # Navigation hub
    ├── system-design-interview-guide.md       # Phase-by-phase flow + checklist
    ├── common-follow-ups.md                   # Interviewer questions by system type
    └── design-patterns-reference.md           # 23 GoF patterns mapped to systems
```

---

## Content Specification

### Patterns Directory

#### **`README.md`** (Navigation Hub)
- Welcome and how to use the pattern matcher
- Quick links to all pattern categories
- Example: "Stuck on an array problem? Check array-and-string-problems.md"
- Links to frameworks directory for system design prep

#### **`problem-to-pattern-matcher.md`** (Master Index)
A searchable table with columns:
- Problem Type (e.g., "Sliding Window", "Binary Search")
- Best-Fit Data Structure(s)
- Key Algorithms
- Example Problem(s)
- Link to detailed category guide

**Scope:** 50+ problem types across all categories  
**Example row:**
```
| Sliding Window | Deque, HashMap | Two-pointer iteration | "Longest substring without repeating chars" | See array-and-string-problems.md |
```

#### **Category Files** (one per category)

Each file (e.g., `array-and-string-problems.md`) follows this structure:

```markdown
# Array & String Problems

## Problem Type 1: Sliding Window
**When to use:** Fixed or variable-size window over contiguous elements

**Best DS:** 
- Deque (for max/min in window)
- HashMap (for element frequency)

**Key Algorithms:**
- Two-pointer expansion/contraction
- Hash-based frequency tracking

**Example Problems:**
1. "Longest substring without repeating characters"
   - Approach: HashMap to track char positions, two pointers for window
   - Your repo: `python/basic/hashmap.py`
   - Complexity: O(n) time, O(min(n, alphabet_size)) space

2. "Max sum of subarray of size k"
   - Approach: Sliding window with running sum
   - Complexity: O(n) time, O(1) space

**Variations:**
- Fixed window size
- Variable window size
- Multiple pointers

**Follow-ups:**
- What if array is not contiguous? (still valid)
- What if you need to return indices? (track start/end)

---

## Problem Type 2: Prefix Sum
**When to use:** Range sum queries, cumulative value problems

... (similar structure)
```

**Categories covered:**
1. Array & String (sliding window, prefix sum, two pointers, sorting, rotation, etc.)
2. Linked List (fast/slow pointers, cycle detection, merging, reversing, reordering)
3. Stack & Queue (monotonic stack, parentheses, BFS, DFS)
4. Tree (BST operations, traversals, LCA, subtree problems, serialization)
5. Graph (DFS, BFS, Dijkstra, topological sort, MST, union-find)
6. Dynamic Programming (knapsack variants, LIS, longest palindrome, coordinate DP)
7. Greedy (activity selection, interval scheduling, huffman)
8. Bit Manipulation (XOR tricks, bitmask DP, subsets)
9. Design (LRU, LFU, Trie-based, custom data structures)
10. Math & Geometry (GCD, primes, modular arithmetic, coordinate geometry)
11. Advanced Patterns (segment tree, Fenwick tree, DSU, Treap, Heavy-Light, etc.)

**Each category:** 4-7 problem types, ~150-300 words total

---

### Frameworks Directory

#### **`README.md`** (Navigation Hub)
- Overview of system design interview framework
- Links to step-by-step guide and common follow-ups
- How to use during practice with agents

#### **`system-design-interview-guide.md`** (Step-by-Step Flow)

**Structure:**

```markdown
# System Design Interview Framework

## Phase 1: Requirements & Clarification (5-10 minutes)
**Goal:** Scope the system and agree on constraints before designing

**Key Questions to Ask:**
- How many users? (DAU, MAU)
- What are the core features? (prioritize)
- What scale are we targeting? (concurrent users, QPS)
- Any specific SLAs? (latency, availability)
- Geo-distributed?

**Template:**
"I'll ask some clarifying questions to scope the problem..."
- Users: ___ million/billion?
- Core features: ___ (e.g., read, write, search)
- Read:Write ratio: ___:1
- Latency requirement: ___ ms

---

## Phase 2: High-Level Architecture (10-15 minutes)
**Goal:** Sketch the major components and data flow

**Components to consider:**
- Load balancer (distribute traffic)
- API servers (stateless layer)
- Database (storage, consistency model)
- Cache layer (reduce DB load)
- Message queue (async processing)
- Search index (for queries)
- External services (payment, analytics)

**Template Sketch:**
```
[Users] ---> [Load Balancer] ---> [API Servers] 
                                       |
                                   [Cache]
                                       |
                                  [Database]
                                  
[Message Queue] ---> [Workers]
```

**Key decisions:**
- Monolithic or microservices?
- Synchronous or asynchronous operations?
- Consistency model (strong/eventual)?

---

## Phase 3: Deep Dive (15-20 minutes)
**Goal:** Design 2-3 critical components in detail

**Choose your deep dives based on the system:**
- If read-heavy → caching strategy, indexing
- If write-heavy → partitioning, replication
- If low-latency → CDN, async processing
- If high-availability → failover, replication

**Example Deep Dive: Caching Strategy**
- Cache layer: Redis or Memcached?
- Cache invalidation strategy (TTL, LRU, write-through?)
- Cache hit ratio target?

---

## Phase 4: Trade-offs & Scaling (10-15 minutes)
**Goal:** Discuss alternatives and handle scale increases

**Key trade-off questions:**
- Consistency vs. Availability vs. Partition tolerance (CAP theorem)
- Consistency models (strong, eventual, causal)
- Monolith vs. microservices
- Synchronous vs. asynchronous

**Scaling scenarios:**
- "What happens if load 10x?"
- "How do you handle a single point of failure?"
- "What if DB write throughput maxes out?"

---

## Comprehensive Checklist

Use this during your design to ensure you cover all bases:

**Architecture & Components**
- [ ] Load balancing strategy (round-robin, consistent hashing, weighted)
- [ ] API gateway or load balancer at entry
- [ ] Database choice (SQL, NoSQL, hybrid)
- [ ] Cache layer (where, invalidation strategy)
- [ ] Message queue for async (Kafka, RabbitMQ, SQS)
- [ ] Search index if needed (Elasticsearch)
- [ ] CDN for static content

**Data & Storage**
- [ ] Schema design (normalization, denormalization)
- [ ] Primary key strategy
- [ ] Partitioning/sharding strategy
- [ ] Replication (master-slave, master-master)
- [ ] Backup and recovery strategy
- [ ] Data retention policy

**API & Protocol**
- [ ] REST, gRPC, or other?
- [ ] Authentication & authorization
- [ ] Rate limiting & throttling
- [ ] API versioning strategy

**Reliability & Observability**
- [ ] Failure modes and fallback strategies
- [ ] Monitoring & alerting (metrics to track)
- [ ] Logging strategy
- [ ] Distributed tracing
- [ ] Health checks and self-healing

**Performance**
- [ ] Latency targets (P50, P99)
- [ ] Throughput targets (QPS)
- [ ] Connection pooling
- [ ] Batch processing where applicable
- [ ] Optimization opportunities

**Security**
- [ ] Data encryption (in transit, at rest)
- [ ] SQL injection prevention
- [ ] Rate limiting against abuse
- [ ] Audit logging

---

## Timeline

Typical 45-60 min interview:
- Phase 1: 5-10 min
- Phase 2: 10-15 min
- Phase 3: 15-20 min
- Phase 4: 10-15 min
- Buffer for clarifications: 5 min
```

#### **`common-follow-ups.md`** (Interviewer Questions by System)

Maps each system in your repo to likely follow-up questions:

```markdown
# Common System Design Follow-ups

## Social Network / Feed System
**Initial design topics:** Feed generation, caching, ranking

**Likely follow-ups:**
- "How do you handle 100M users? Which component needs sharding first?"
- "A feed generation takes 5 seconds. How do you optimize?"
- "How do you ensure users see posts from friends in real-time?"
- "What if a user's feed suddenly becomes stale? How do you recover?"
- "How do you prevent abuse (spam, fake accounts)?"

## Payment System
**Initial design topics:** Transaction safety, idempotency, reconciliation

**Likely follow-ups:**
- "How do you ensure exactly-once semantics?"
- "What if the payment service goes down mid-transaction?"
- "How long can it take to process a payment? What are the tradeoffs?"
- "How do you handle refunds?"
- "How do you detect and prevent fraud?"

... (for each of your 35+ systems)
```

#### **`design-patterns-reference.md`** (GoF Patterns)

Map Gang of Four patterns to where they appear in your system designs:

```markdown
# Design Patterns Reference

## Creational Patterns

### Singleton
**Definition:** Ensure a class has only one instance and provide a global access point

**Used in systems:**
- Connection pools (database connections)
- Logger instance
- Cache manager

**Your repo:** `python/system_design/rate_limiter.py`, `python/system_design/load_balancer.py`

### Factory
**Definition:** Create objects without specifying exact classes

**Used in systems:**
- Message queue implementations (choose Kafka vs. RabbitMQ)
- Load balancer strategies (round-robin, consistent hash)

**Your repo:** `python/system_design/factory_pattern.py`, `python/system_design/load_balancer.py`

... (other patterns)
```

---

## Integration with Existing Repo

### Updates to Main README.md
Add a section linking to the interview frameworks:
```markdown
## Interview Prep Resources

- **[Problem-to-Pattern Matcher](docs/patterns/README.md)** — Recognize problem types and pick the right data structure
- **[System Design Interview Guide](docs/frameworks/README.md)** — Step-by-step framework for designing systems
```

### Updates to Existing Docs
- Link from `SYSTEM_DESIGN_GUIDE.md` to `frameworks/system-design-interview-guide.md`
- Link from `INTERVIEW_ALGORITHMS_SUMMARY.md` to `patterns/README.md`

### Linking Strategy
- Each problem type links to your Python/Java implementations
- Each system design in repo is referenced from `common-follow-ups.md`
- Each pattern file links back to master index

---

## Success Criteria

1. **Pattern Matcher:**
   - Covers 50+ problem types
   - Each type has clear DS/algorithm recommendation
   - Each links to relevant code in repo

2. **System Design Framework:**
   - 4-phase flow applicable to most systems
   - Comprehensive checklist covers all major concerns
   - Common follow-ups provided for 35+ systems

3. **Usability:**
   - Clear navigation from main README
   - Cross-links between patterns and frameworks
   - Searchable via GitHub's markdown search

4. **Maintainability:**
   - Structure allows adding new patterns easily
   - Links to code prevent stale references
   - Organized hierarchically for clarity

---

## Scope Boundaries

**In scope:**
- 50+ problem types with DS/algorithm mappings
- 4-phase system design framework
- Comprehensive checklist
- Common follow-up questions for systems in repo
- GoF design patterns reference

**Out of scope:**
- Video tutorials or visual diagrams (text-based guides only)
- New code implementations (link to existing repo code)
- Company-specific preparation guides
- LeetCode problem solution code (reference only)

---

## Next Steps

1. Write detailed spec document (this file) ✓
2. Implement pattern categories (start with arrays, trees, graphs)
3. Write system design interview guide with phases & checklist
4. Populate common follow-ups for each system
5. Update README and create navigation hubs
6. Link from patterns to code in repo

