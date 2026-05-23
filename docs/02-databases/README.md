# Database Systems — Complete Reference

Comprehensive guide to modern database systems for interviews and production.

---

## 📚 Database Categories

### 🗄️ **Relational Databases (SQL)**
- PostgreSQL, MySQL, Oracle, SQL Server
- ACID guarantees, normalization, joins
- Best for: Structured data, transactions, relationships

**[SQL Deep Dive](01-sql-advanced.md)** — Advanced queries, optimization, transactions

---

### 📄 **Document Databases (NoSQL)**
- MongoDB, Firebase, CouchDB, DynamoDB
- Flexible schema, horizontal scaling
- Best for: JSON documents, rapid iteration, scale-out

**[NoSQL Comprehensive Guide](02-nosql-advanced.md)** — Data modeling, consistency models, scaling

---

### 🔗 **Graph Databases**
- Neo4j, ArangoDB, JanusGraph
- Relationship queries fast (not joins)
- Best for: Social graphs, recommendations, knowledge graphs

**[Graph Databases](03-graph-databases.md)** — Graph queries, ACID on graphs, traversals

---

### 📊 **Columnar Databases**
- ClickHouse, Snowflake, BigQuery, Redshift
- Compress similar data, fast aggregations
- Best for: Analytics, data warehousing, OLAP

**[Columnar Databases](04-columnar-databases.md)** — Column families, compression, analytics

---

### ⏱️ **Time-Series Databases**
- InfluxDB, Prometheus, TimescaleDB, VictoriaMetrics
- Optimized for time-indexed data
- Best for: Metrics, monitoring, IoT, financial data

**[Time-Series Databases](05-timeseries-databases.md)** — Bucketing, retention, downsampling

---

### 🔍 **Search Engines**
- Elasticsearch, Solr, Meilisearch, Algolia
- Full-text search, ranking, faceted search
- Best for: Search, logging, real-time analytics

**[Search Engines & Full-Text Search](06-search-engines.md)** — Inverted indexes, ranking, aggregations

---

### 📤 **Cache Databases**
- Redis, Memcached, Dragonfly
- In-memory, blazingly fast
- Best for: Caching, sessions, real-time data

**[Caching & In-Memory Stores](07-caching-stores.md)** — Eviction, persistence, clustering

---

### 🎯 **Vector Databases**
- Pinecone, Weaviate, Milvus, Qdrant
- Similarity search, embeddings
- Best for: RAG, semantic search, recommendations

**[Vector Databases](08-vector-databases.md)** — Embedding search, indexing, distance metrics

---

### 🔀 **Query Language: GraphQL**
- API query language, multiple sources
- Strongly typed, composable
- Best for: APIs, flexibility, client-driven queries

**[GraphQL Fundamentals](09-graphql.md)** — Schema design, resolvers, N+1 problems

---

### 🏛️ **Data Warehousing & Lakehouses**
- Snowflake, Redshift, Delta Lake, Iceberg
- OLAP, analytics, big data
- Best for: Data analytics, business intelligence

**[Data Warehousing & Lakehouses](10-warehousing-lakehouses.md)** — Architecture, ETL, optimization

---

## 🎯 Database Selection Guide

| Use Case | Best Option | Runner-Up |
|----------|------------|-----------|
| **Transactional** | PostgreSQL | MySQL |
| **Flexible documents** | MongoDB | Firebase |
| **Scale to 1B+ rows** | DynamoDB | Cassandra |
| **Analytics** | Snowflake | BigQuery |
| **Search** | Elasticsearch | Meilisearch |
| **Graphs/relationships** | Neo4j | ArangoDB |
| **Time-series metrics** | Prometheus | InfluxDB |
| **Caching** | Redis | Memcached |
| **Semantic search** | Pinecone | Weaviate |
| **APIs** | GraphQL | REST |

---

## 📊 Interview Path

### Beginner (Week 1)
1. SQL basics (indexes, joins, transactions)
2. NoSQL vs. SQL (when use each)
3. Database selection for scenario

### Intermediate (Weeks 2-3)
4. Advanced SQL (window functions, CTEs, optimization)
5. MongoDB data modeling
6. Caching strategy (Redis)
7. Elasticsearch basics

### Advanced (Weeks 4+)
8. System design: pick database for 1M users
9. Distributed databases (Cassandra, DynamoDB)
10. Time-series, vector databases
11. GraphQL API design

---

## 🔑 Key Concepts by Database Type

### Relational (SQL)
- **Normalization:** Minimize redundancy
- **ACID:** Transactions
- **Indexes:** Fast queries
- **Joins:** Combine tables

### Document (NoSQL)
- **Schema flexibility:** Evolve over time
- **Sharding:** Horizontal scaling
- **Replication:** High availability
- **Eventual consistency:** Trade-off for scale

### Graph
- **Nodes & edges:** Relationship representation
- **Graph algorithms:** Shortest path, PageRank
- **Pattern matching:** Complex queries
- **Traversals:** Navigate relationships

### Columnar
- **Compression:** Similar data together
- **Aggregations:** Fast SUM, AVG, COUNT
- **Partitioning:** Organize by time/region
- **OLAP:** Analytics queries

### Time-Series
- **Time bucketing:** Group by interval
- **Downsampling:** Aggregate old data
- **Retention:** Delete old data automatically
- **Cardinality:** Label combinations

---

## 💡 Common Interview Questions

**Q: Design database for 1M users, 1M events/day**
→ SQL with read replicas for analytics

**Q: Real-time feed for billions of events**
→ NoSQL (MongoDB/DynamoDB) with caching (Redis)

**Q: Social network with friend recommendations**
→ Graph database (Neo4j) for relationships, recommendations

**Q: Monitoring system for 1000 servers**
→ Time-series DB (Prometheus) for metrics, Elasticsearch for logs

**Q: E-commerce product search**
→ Elasticsearch for search, SQL for transactions

---

## 🧪 Hands-On Practice

### SQL
- 10+ complex queries (window functions, CTEs)
- Index optimization
- Transaction isolation levels

### NoSQL
- MongoDB aggregation pipeline
- DynamoDB access patterns
- Sharding strategy

### Advanced
- Design database schema for real system
- Query optimization with EXPLAIN plans
- Caching strategy for hot data

---

## 📚 Resources by Topic

| Topic | Guide | Difficulty |
|-------|-------|-----------|
| SQL basics | 01-sql-advanced.md | Medium |
| NoSQL modeling | 02-nosql-advanced.md | Medium-Hard |
| Graphs | 03-graph-databases.md | Hard |
| Analytics | 04-columnar-databases.md | Medium |
| Metrics | 05-timeseries-databases.md | Medium |
| Search | 06-search-engines.md | Medium |
| Caching | 07-caching-stores.md | Medium |
| Embeddings | 08-vector-databases.md | Hard |
| APIs | 09-graphql.md | Medium |
| Warehousing | 10-warehousing-lakehouses.md | Hard |

---

## ✅ Self-Assessment

By the end of this section, you should be able to:

- [ ] Explain SQL vs. NoSQL trade-offs
- [ ] Design database schema for given requirements
- [ ] Write complex SQL queries (joins, aggregations, window functions)
- [ ] Explain MongoDB data modeling and indexing
- [ ] Design sharding strategy for 1B-row table
- [ ] Explain graph database use cases
- [ ] Design caching strategy (Redis)
- [ ] Understand Elasticsearch basics
- [ ] Explain GraphQL schema design
- [ ] Pick right database for scenario

---

**Last updated:** 2026-05-22

**Total guides:** 10 comprehensive database guides  
**Coverage:** Relational, NoSQL, graphs, columnar, time-series, search, caching, vectors, GraphQL, warehousing
