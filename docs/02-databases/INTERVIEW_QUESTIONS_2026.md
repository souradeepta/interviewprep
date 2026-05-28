# 30+ Database Interview Questions from 2026

**Level:** L3-L5
**Time to read:** ~20 min

Real database interview questions from DataCamp, FAANG, and major tech companies (2026).

---

## Foundational Questions (Guides 1-3: SQL, NoSQL, Graph)

**Q1: What is a Database Management System (DBMS)?**
Answer: A DBMS is software that manages data storage, retrieval, update, and deletion. It acts as an intermediary between users and the database, handling data modeling, manipulation, and security.

**Q2: Explain the ACID properties in database transactions**
Answer: 
- Atomicity: Transaction is "all or nothing"
- Consistency: Data moves from one valid state to another
- Isolation: Concurrent transactions don't interfere
- Durability: Committed data survives failures
(See guide 01-sql-advanced.md for detailed explanation)

**Q3: What are the different types of database keys?**
Answer: Primary key (unique identifier), foreign key (reference to another table), unique key (unique but nullable), candidate key (potential primary key), composite key (multiple columns)

**Q4: What is normalization, and why is it important?**
Answer: Normalization (1NF through 5NF+) reduces data redundancy and improves data integrity by organizing data into logical tables. 1NF eliminates repeating groups, 2NF removes partial dependencies, 3NF removes transitive dependencies.

**Q5: Explain the difference between DELETE, DROP, and TRUNCATE**
Answer:
- DELETE: Remove rows (can be rolled back, slower)
- TRUNCATE: Remove all rows (faster, minimal logging)
- DROP: Remove table structure (DDL, cannot be rolled back in all systems)

**Q6: What's the difference between INNER JOIN and OUTER JOIN?**
Answer: INNER JOIN returns only matching rows from both tables. OUTER JOIN (LEFT, RIGHT, FULL) includes non-matching rows from one or both tables filled with NULL.

---

## Performance & Optimization (Guides 14-18: Indexing, Query Planning)

**Q7: What is an index, and how does it improve performance?**
Answer: An index is a data structure (B-tree, hash, bitmap) that enables fast lookups without full table scans. Trade-off: faster reads but slower writes (index maintenance cost).

**Q8: Explain different types of indexes and when to use each**
Answer:
- B-tree: General purpose (range queries work)
- Hash: Point queries only (O(1) lookup)
- Bitmap: Low-cardinality columns (status, type)
- Full-text: Search queries
- Covering: All needed columns in index
(See guide 18-indexing-deep-dive.md for detailed comparison)

**Q9: What's the difference between a clustered and non-clustered index?**
Answer: Clustered index determines physical row order (one per table, includes all columns). Non-clustered index is a separate structure pointing to rows (can have many, doesn't include all columns unless covering).

**Q10: How do you optimize a slow query?**
Answer:
1. Run EXPLAIN ANALYZE to see execution plan
2. Identify bottleneck (seq scan, inefficient join)
3. Add appropriate indexes
4. Rewrite query if needed (avoid functions in WHERE)
5. Consider materialized views or caching
(See guide 17-query-planning.md for detailed optimization strategies)

**Q11: How do you handle deadlocks in a database?**
Answer: Deadlock occurs when two transactions wait for each other. Solutions: Lock timeout (abort one transaction), ordered locking (consistent lock order), isolation level adjustment, or distributed transaction handling (Saga pattern).

**Q12: What's the purpose of database constraints?**
Answer: Constraints enforce data integrity: PRIMARY KEY (unique identifier), FOREIGN KEY (referential integrity), UNIQUE (uniqueness), CHECK (value validation), NOT NULL (required field).

---

## Scaling & Distribution (Guides 19-20: Sharding, CDC)

**Q13: Explain database sharding and its trade-offs**
Answer: Sharding splits data across multiple databases by a shard key. 
- Hash sharding: Uniform distribution, but 90% rehashing on shard addition
- Range sharding: Simple, but hot partitions
- Consistent hashing: Only K/N keys rehash
Trade-off: Solves scale but adds operational complexity (see guide 19-sharding-advanced.md)

**Q14: Explain database partitioning**
Answer: Partitioning divides a table within a single database (vertical = columns, horizontal = rows). Vertical partitioning separates wide tables. Horizontal partitioning groups rows by range/hash for better performance.

**Q15: How do you handle very large datasets?**
Answer:
1. Sharding: Distribute across databases
2. Denormalization: Reduce joins
3. Caching: Redis/Memcached layer
4. Data warehousing: Columnar format (Snowflake)
5. Archiving: Move old data to cold storage

**Q16: Explain database replication and its types**
Answer: 
- Master-replica (async): Primary writes, replicas read (eventual consistency)
- Master-master (multi-master): Both write (conflict resolution needed)
- Semi-synchronous: Compromise between speed and safety
(See guide 15-database-replication.md for detailed patterns)

---

## Concurrency & Consistency (Guides 2, 12-13, 21)

**Q17: What are database transactions and isolation levels?**
Answer: Transaction = unit of work (atomic). Isolation levels control concurrency:
- READ UNCOMMITTED: Dirty reads possible
- READ COMMITTED: Prevents dirty reads
- REPEATABLE READ: Prevents phantom reads
- SERIALIZABLE: Complete isolation (slowest)
(See guide 01-sql-advanced.md)

**Q18: Explain MVCC (Multi-Version Concurrency Control)**
Answer: MVCC allows concurrent reads without blocking writes. Each transaction sees a snapshot at start time. Writers create new versions, readers see their snapshot version. Enables high concurrency with read-heavy workloads.

**Q19: Explain pessimistic vs. optimistic locking**
Answer:
- Pessimistic: Lock immediately (exclusive lock, prevents conflicts, but lower concurrency)
- Optimistic: Check version on update (no lock, higher concurrency, but conflicts need retry)
Use pessimistic for high-conflict scenarios, optimistic for low-conflict.

**Q20: What's the CAP theorem?**
Answer: Choose 2 of 3:
- Consistency: All nodes see same data
- Availability: System always responsive  
- Partition tolerance: Survives network split
Most systems choose AP (availability + partition) for web scale, sacrificing immediate consistency.

---

## Data Management (Guides 11, 16, 26)

**Q21: How do you approach database migration from one system to another?**
Answer: Use expand-contract pattern:
1. Expand: Add new schema/table, dual-write
2. Migrate: Background job copies data
3. Contract: Stop old writes, retire old schema
Benefits: Zero downtime, rollback at any phase (see guide 26-migration-strategies.md)

**Q22: Explain the concept of a view in databases**
Answer: View is a virtual table based on a query. Benefits: Simplifies complex queries, provides security (hide columns), abstracts schema changes. Can be materialized (pre-computed) for performance.

**Q23: What are materialized views?**
Answer: Pre-computed views stored as physical tables. Benefits: Instant query results (no computation), good for dashboards. Trade-off: Stale data (refresh periodically), extra storage.

**Q24: What are stored procedures and their advantages?**
Answer: Pre-compiled SQL code stored in database. Advantages: Reusable, faster execution (compiled), security (restrict direct table access), reduced network traffic. Disadvantage: Harder to version control.

---

## Real-World Scenarios (Guides 7, 22-30)

**Q25: What's the difference between read replicas and write replicas?**
Answer:
- Read replica: Serves read-only traffic, reduces load on primary
- Write replica: Accepts writes (multi-master, more complex)
Read replicas scale read throughput but add replication lag. Use for read-heavy applications.

**Q26: How do you detect and fix hot shards in a sharded database?**
Answer: Hot shard = one shard receiving 3x+ average load.
Detection: Monitor ops/sec per shard
Fixes: 
1. Move hot user to dedicated shard
2. Re-shard by different key
3. Add caching layer
4. Split hot shard into multiple
(See guide 19-sharding-advanced.md for detailed solutions)

**Q27: Explain the N+1 query problem and how you solve it**
Answer: Fetching 1 parent + N children requires N+1 queries.
Example: Get user → 1 query, then for each user get their orders → N queries
Solutions: 
1. JOIN query: 1 query instead of N+1
2. Eager loading: Load children in batch
3. DataLoader: Batch requests automatically

**Q28: How would you design a caching layer for a database?**
Answer: Caching strategy depends on workload:
- Cache-aside: App checks cache, falls back to DB
- Write-through: Write to both cache and DB
- Write-behind: Write to cache, batch to DB
Key decisions: TTL (1 hour for mutable data), eviction (LRU), invalidation strategy
(See guide 07-caching-stores.md)

**Q29: What's the difference between eager and lazy loading?**
Answer:
- Eager: Load related data immediately (prevents N+1)
- Lazy: Load on demand (wastes DB calls if not all data needed)
Choice: Eager better for known access patterns, lazy for optional relations.

**Q30: Explain the difference between relational and document databases**
Answer:
- Relational (SQL): Structured schema, ACID, joins, normalized
- Document (NoSQL): Flexible schema, eventual consistency, embedded data
Choose SQL for transactional consistency, NoSQL for flexibility and scale
(See guides 01-sql-advanced.md and 02-nosql-advanced.md for detailed comparison)

---

## Advanced Topics (Guides 5, 8, 12, 20, 25, 28, 30)

**Q31: How do you handle database backup and point-in-time recovery?**
Answer:
- Full backup: Complete snapshot (large, slow, baseline)
- Incremental: Only changes (small, fast, depends on full)
- Continuous: Real-time transaction log (RPO=0)
Recovery: Restore full + replay transaction logs to target time
(See guide 16-backup-recovery.md)

**Q32: What strategies would you use to reduce database replication lag?**
Answer: Lag = time for changes to propagate to replicas.
Causes: Network latency, large writes, slow replica
Solutions:
1. Faster network (local datacenter)
2. Async replication (trade consistency)
3. Optimize writes (batch, smaller rows)
4. Upgrade replica hardware
5. Parallel replication (if supported)

**Q33: Explain connection pooling and its benefits**
Answer: Pool maintains N open connections, reuses them for requests.
Benefits: Avoids connection overhead (expensive), limits total connections, queues requests
Sizing: pool_size = (cores * 2) + spindles (typically 10-50 connections)
(See guide 25-connection-pooling.md)

**Q34: How do you encrypt sensitive data in a database?**
Answer: Multiple layers:
1. Encryption at rest: Disk encryption (AWS KMS, transparent)
2. Encryption in transit: TLS for connections
3. Column-level: Encrypt PII (email, SSN, card) before storing
4. End-to-end: App encrypts before sending to DB
Trade-off: Encryption at rest has minimal impact, but column-level prevents indexing
(See guide 28-database-security.md)

**Q35: Explain Change Data Capture (CDC) and use cases**
Answer: CDC captures all database changes (insert/update/delete) and streams them.
Use cases: 
- Replication to another database
- Analytics (sync to data warehouse)
- Cache invalidation
- Event-driven workflows
Approaches: Log-based (fast, native), query-based (simple, laggy), trigger-based (reliable)
(See guide 20-change-data-capture.md for implementation details)

---

## Sources

Based on research from:
- [DataCamp: Top 40 DBMS Interview Questions in 2026](https://www.datacamp.com/blog/dbms-interview-questions)
- [SQL Interview Questions for Experienced Professionals: A 2026 Guide](https://interviewkickstart.com/blogs/interview-questions/sql-interview-questions-for-experienced-professionals)
- [GitHub: Databases Interview Questions](https://github.com/Devinterview-io/databases-interview-questions)
- [System Design Interview Guide 2026 - Design Gurus](https://www.designgurus.io/blog/system-design-interview-questions)
- [Hello Interview: Database Indexing for System Design](https://www.hellointerview.com/learn/system-design/core-concepts/db-indexing)
- [FAANG Data Engineer Interview Questions 2026](https://interviewkickstart.com/blogs/interview-questions/data-engineer-interview-questions-for-faang-interviews)

---

**Last updated:** 2026-05-22

**How to use:** Each question is mapped to relevant guides (e.g., "See guide 01-sql-advanced.md"). Use these questions to test your knowledge against the comprehensive guides in this directory.
