# Database Indexing Strategy: Optimizing Query Performance

**Level:** L4-L5
**Time to read:** ~20 min

Master indexing strategies for fast database queries.

---

## Index Fundamentals

**What is an index?** Data structure (usually B-tree) for fast lookups.

```
Without index: Full table scan O(n)
┌─────────────────────┐
│ id │ email │ name   │
├────┼───────┼────────┤
│ 1  │ a@... │ Alice  │
│ 2  │ b@... │ Bob    │
│ 3  │ c@... │ Carol  │
└─────────────────────┘
Scan all 3 million rows to find email

With index: B-tree lookup O(log n)
email index:
    a@... → row 1
    b@... → row 2
    c@... → row 3
Jump directly to row 1
```

---

## Single-Column Indexes

```sql
CREATE INDEX idx_email ON users(email);

-- Now this query is fast:
SELECT * FROM users WHERE email = 'alice@example.com';
```

**When to use:**
- Frequent WHERE clauses
- Equality checks (=)
- Foreign key columns

---

## Composite Indexes

```sql
-- For queries: WHERE status = ? AND created_at > ?
CREATE INDEX idx_status_created ON posts(status, created_at);

-- Good for:
-- WHERE status = 'published' AND created_at > '2024-01-01'
-- WHERE status = 'published'  (prefix match)

-- Not good for:
-- WHERE created_at > '2024-01-01'  (doesn't use index)
-- WHERE status = ? OR created_at > ?  (use separate indexes)
```

**Index ordering matters:**
```
Composite index (column1, column2):
- ✓ WHERE col1 = ? AND col2 = ?
- ✓ WHERE col1 = ?
- ❌ WHERE col2 = ?  (doesn't use index)
```

---

## Index Types

### B-Tree (Most Common)

```
Best for: =, <, >, BETWEEN, LIKE prefix
Example: 
  CREATE INDEX idx_name ON users(name);
  SELECT * FROM users WHERE name LIKE 'Al%';  # Uses index
```

### Hash Index

```
Best for: = only
Example:
  CREATE INDEX idx_email ON users USING HASH (email);
  SELECT * FROM users WHERE email = 'alice@example.com';  # Fast
  SELECT * FROM users WHERE email LIKE 'alice%';  # Doesn't use index
```

### Full-Text Index

```
Best for: Text search
Example:
  CREATE FULLTEXT INDEX idx_content ON articles(content);
  SELECT * FROM articles WHERE MATCH(content) AGAINST('database' IN BOOLEAN MODE);
```

### Spatial Index

```
Best for: Geographic queries
Example:
  CREATE SPATIAL INDEX idx_location ON restaurants(location);
  SELECT * FROM restaurants WHERE ST_CONTAINS(area, location);
```

---

## When NOT to Index

| Scenario | Reason |
|----------|--------|
| **Low cardinality** (gender, status) | Index too large, not selective |
| **Rarely queried** | Maintenance cost > benefit |
| **Frequently updated** | Write cost high |
| **Small tables** | Full scan faster than index |
| **Very large indexes** | Memory overhead |

---

## Index Maintenance Cost

```
Writing (INSERT, UPDATE, DELETE):
- ❌ Must update all indexes
- Slow writes with many indexes

Reading (SELECT):
- ✓ Fast with indexes
- But only if used

Balance: 5-7 indexes per table typically optimal
```

---

## Analyzing Query Performance

```sql
-- Explain query plan
EXPLAIN SELECT * FROM posts WHERE status = 'published' AND created_at > '2024-01-01';

Output:
id  select_type  table  type   key              rows  filtered
1   SIMPLE       posts  range  idx_status_created  1000  50

"type=range" = Using index range scan (good)
"key=idx_status_created" = Using that index
"rows=1000" = Estimated 1000 rows examined
```

---

## Index Design Checklist

```sql
-- Create indexes on:
-- 1. WHERE clause columns
CREATE INDEX idx_user_id ON orders(user_id);
CREATE INDEX idx_status ON orders(status);

-- 2. JOIN columns
CREATE INDEX idx_user_id_fk ON orders(user_id);

-- 3. ORDER BY columns
CREATE INDEX idx_created_at ON posts(created_at DESC);

-- 4. GROUP BY columns
CREATE INDEX idx_category ON products(category);

-- Don't create indexes on:
-- - Low cardinality (gender, boolean)
-- - Rarely used columns
-- - Updated frequently
```

---

## Monitoring Indexes

```sql
-- Find unused indexes
SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- Find slow queries
SHOW slow_query_log_file;
SELECT query_time, query FROM slow_log WHERE query_time > 1;

-- Analyze index size
SELECT schemaname, tablename, indexname, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes;
```

---

## Indexing Checklist

- ✓ Identified slow queries (use EXPLAIN)
- ✓ Indexed WHERE clause columns
- ✓ Indexed JOIN keys
- ✓ Indexed ORDER BY if needed
- ✓ Composite index columns in right order
- ✓ Avoided low cardinality columns
- ✓ Avoided over-indexing
- ✓ Monitored index usage
- ✓ Removed unused indexes
- ✓ Tested query plan with EXPLAIN

