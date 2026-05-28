# Database Fundamentals — RDBMS, NoSQL, and Query Optimization

**Level:** L4-L5
**Time to read:** ~20 min

Core database concepts every engineer should know.

---

## 🏗️ Database Types

### Relational Databases (RDBMS)

**Structure:** Tables with rows and columns

```sql
Users Table:
id | name    | email
1  | Alice   | alice@example.com
2  | Bob     | bob@example.com

Orders Table:
id | user_id | amount | date
10 | 1       | $50    | 2024-01-15
11 | 1       | $30    | 2024-01-20
```

**Query Language:** SQL
```sql
SELECT u.name, COUNT(o.id) as order_count
FROM Users u
LEFT JOIN Orders o ON u.id = o.user_id
GROUP BY u.id
```

**Advantages:**
- ACID guarantees (transactions)
- Schema enforced (data integrity)
- Joins for relationships
- Good for structured data

**Disadvantages:**
- Scaling harder (vertical mostly)
- Rigid schema
- Not ideal for semi-structured data

**Examples:** PostgreSQL, MySQL, SQL Server, Oracle

---

### NoSQL Databases

**Types:**

**Document (MongoDB, Firebase):**
```json
{
  "_id": 1,
  "name": "Alice",
  "email": "alice@example.com",
  "orders": [
    {"amount": 50, "date": "2024-01-15"},
    {"amount": 30, "date": "2024-01-20"}
  ]
}
```

Pros: Flexible schema, nested data
Cons: No joins, denormalization

**Key-Value (Redis, Memcached):**
```
key: value
"user:1" → {"name": "Alice", "email": "..."}
"cache:product:100" → {"price": 29.99, ...}
```

Pros: Fast, simple
Cons: No querying, in-memory (can lose data)

**Time-Series (InfluxDB, Prometheus):**
```
timestamp | metric | value
2024-01-15 10:00:00 | cpu_usage | 75%
2024-01-15 10:01:00 | cpu_usage | 82%
```

Pros: Optimized for time-based data
Cons: Limited query types

**Graph (Neo4j):**
```
(Alice) --[KNOWS]--> (Bob)
(Alice) --[LIKES]--> (Product: Laptop)
(Bob) --[LIKES]--> (Product: Laptop)
```

Pros: Relationship queries fast
Cons: Complex setup, niche use

---

## 🔑 Database Design Principles

### Normalization (RDBMS)

**Goal:** Minimize redundancy, maintain consistency

**1NF (First Normal Form):**
- Atomic values (no lists in cells)
```
❌ Bad:
users(id, name, phone_numbers)
where phone_numbers = ["123", "456"]

✅ Good:
users(id, name)
phones(user_id, phone_number)
```

**2NF (Second Normal Form):**
- Remove partial dependencies
```
❌ Bad:
orders(order_id, user_id, user_name, amount)

✅ Good:
users(user_id, name)
orders(order_id, user_id, amount)
```

**3NF (Third Normal Form):**
- Remove transitive dependencies
```
❌ Bad:
users(user_id, name, city, state, country)

✅ Good:
users(user_id, name, city_id)
cities(city_id, name, state, country)
```

---

## 📊 Indexing Strategy

### Why Indexes?

```
Table scan: O(n)
SELECT * FROM users WHERE id=100
Scans all 1M rows, finds 1 match

Index on id: O(log n)
Lookup in B-tree index, O(log n) comparisons
Returns match immediately
```

### Index Types

**Primary Key Index:**
```sql
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);
-- Automatically creates index on id
```

**Secondary Index:**
```sql
CREATE INDEX idx_email ON users(email);
-- Fast lookup by email
```

**Composite Index:**
```sql
CREATE INDEX idx_user_date ON orders(user_id, date);
-- Fast for (user_id, date) and user_id alone
-- Not fast for date alone
```

**Full-Text Index:**
```sql
CREATE FULLTEXT INDEX idx_content ON articles(content);
-- Fast text search
```

### Index Trade-offs

```
Pros:
- Query speed (10-100x faster)
- Range queries fast

Cons:
- Write slower (must update index)
- Memory overhead (store index)
- Index maintenance cost

When to index:
- Frequently queried columns
- Filter or join columns
- Avoid: rarely queried, small tables
```

---

## 🔄 Query Optimization

### Execution Plan

```sql
EXPLAIN SELECT u.name, COUNT(o.id)
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id;

Output shows:
- Seq Scan on users (1M rows)
- Hash Join on orders
- HashAggregate
- Total cost: 50000

Optimization:
- Add index on orders(user_id)
- New cost: 5000 (10x faster!)
```

### Common Optimization Patterns

**1. Use indexes strategically**
```sql
-- Slow (no index on email)
SELECT * FROM users WHERE email = 'alice@example.com';

-- Fast (with index)
CREATE INDEX idx_email ON users(email);
SELECT * FROM users WHERE email = 'alice@example.com';
```

**2. Select only needed columns**
```sql
-- Slow
SELECT * FROM users;

-- Fast
SELECT id, name FROM users;
```

**3. Join order matters**
```sql
-- Filter before joining
SELECT u.name, o.amount
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.country = 'US'  -- Filter first

-- vs wrong order (slower)
SELECT u.name, o.amount
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE o.amount > 100  -- Filter joins all then filters
```

**4. Avoid N+1 queries**
```python
# Slow: N+1 queries
users = db.query("SELECT * FROM users");
for user in users:
    orders = db.query(f"SELECT * FROM orders WHERE user_id={user.id}")
    # N queries + 1 initial query

# Fast: Single query with join
query = """
SELECT u.id, u.name, COUNT(o.id)
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id
"""
```

---

## 🔒 Transactions & ACID

### ACID Guarantees

**Atomicity:** All or nothing
```sql
BEGIN TRANSACTION;
UPDATE users SET balance = balance - 50 WHERE id=1;
UPDATE users SET balance = balance + 50 WHERE id=2;
COMMIT;  -- Both updates or neither

-- If error in middle, ROLLBACK both
```

**Consistency:** Data remains valid
```sql
-- Constraint: balance >= 0
UPDATE users SET balance = balance - 1000 WHERE id=1;
-- If would make balance < 0, transaction fails
```

**Isolation:** Concurrent transactions don't interfere
```sql
Transaction 1:
BEGIN; SET balance = 100; COMMIT;

Transaction 2:
BEGIN; READ balance; COMMIT;

Isolation levels:
- READ UNCOMMITTED: Dirty reads possible
- READ COMMITTED: No dirty reads
- REPEATABLE READ: No dirty/phantom reads
- SERIALIZABLE: Complete isolation (slowest)
```

**Durability:** Committed data persists
```sql
COMMIT;  -- Written to disk
-- Power fails, data still there
```

---

## 📊 Database Design Example

**Problem:** Design a user-post social media system

```sql
-- Users table
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_username ON users(username);

-- Posts table
CREATE TABLE posts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX idx_user_posts ON posts(user_id, created_at);

-- Likes table
CREATE TABLE likes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    post_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, post_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);
CREATE INDEX idx_post_likes ON likes(post_id);

-- Query examples
SELECT p.id, p.content, COUNT(l.id) as like_count
FROM posts p
LEFT JOIN likes l ON p.id = l.post_id
WHERE p.user_id = 1
ORDER BY p.created_at DESC
LIMIT 10;
```

---

## ❓ Interview Q&A

**Q: SQL vs. NoSQL, when to use each?**
A: SQL for structured, relational data with ACID needs (users, orders). NoSQL for flexible, unstructured data, rapid scaling, simple queries (documents, logs).

**Q: How do indexes work?**
A: Indexes create sorted structures (usually B-trees) on columns. Lookups O(log n) instead of O(n) scan. Trade-off: slower writes.

**Q: What's the difference between joins and denormalization?**
A: Joins: query-time combination of tables (normalize). Denormalization: store redundant data (faster queries, harder consistency).

**Q: What's a transaction?**
A: Group of operations that are atomic (all or none). Provides ACID guarantees. Start with BEGIN, end with COMMIT or ROLLBACK.

---

## ✅ Checklist

- [ ] Know RDBMS vs. NoSQL trade-offs
- [ ] Understand normalization (1NF, 2NF, 3NF)
- [ ] Know indexing strategies and trade-offs
- [ ] Can optimize SQL queries
- [ ] Understand ACID transactions
- [ ] Know when to denormalize
- [ ] Can design a simple database schema
- [ ] Understand query execution plans

---

**Last updated:** 2026-05-22
