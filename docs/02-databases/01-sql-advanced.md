# SQL Deep Dive — Advanced Queries and Optimization

**Level:** L3-L5
**Time to read:** ~30 min

Master SQL for interviews and production systems.

---

## 🔧 Advanced Query Techniques

### Window Functions

Compute running totals, rankings, and comparisons:

```sql
-- Running sum of sales per day
SELECT 
    date,
    sales,
    SUM(sales) OVER (ORDER BY date) as running_total
FROM daily_sales;

-- Rank employees by salary within department
SELECT 
    name,
    salary,
    department,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) as rank
FROM employees;

-- Compare with previous day
SELECT 
    date,
    sales,
    LAG(sales) OVER (ORDER BY date) as prev_day_sales,
    sales - LAG(sales) OVER (ORDER BY date) as growth
FROM daily_sales;
```

**Common functions:**
- `ROW_NUMBER()` — Unique row number
- `RANK()` — Ranking (ties get same rank)
- `DENSE_RANK()` — Ranking (no gaps)
- `LAG()` / `LEAD()` — Previous/next row
- `FIRST_VALUE()` / `LAST_VALUE()` — First/last in window

---

### CTEs (Common Table Expressions)

Reusable subqueries for complex queries:

```sql
-- Find top spenders and their purchases
WITH top_customers AS (
    SELECT user_id, SUM(total) as lifetime_value
    FROM orders
    GROUP BY user_id
    HAVING SUM(total) > 1000
    ORDER BY SUM(total) DESC
    LIMIT 10
)
SELECT 
    tc.user_id,
    tc.lifetime_value,
    COUNT(o.id) as order_count,
    AVG(o.total) as avg_order
FROM top_customers tc
JOIN orders o ON tc.user_id = o.user_id
GROUP BY tc.user_id;
```

**Recursive CTE (hierarchies):**
```sql
WITH RECURSIVE org_hierarchy AS (
    -- Base case: top level
    SELECT id, name, manager_id, 1 as level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive case: each level
    SELECT e.id, e.name, e.manager_id, oh.level + 1
    FROM employees e
    JOIN org_hierarchy oh ON e.manager_id = oh.id
)
SELECT * FROM org_hierarchy
ORDER BY level, name;
```

---

## 🚀 Query Optimization

### EXPLAIN PLAN

Understand query execution:

```sql
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id)
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.country = 'US'
GROUP BY u.id;
```

**Output shows:**
- Seq Scan vs. Index Scan (full table vs. indexed)
- Join type (nested loop, hash join, merge join)
- Cost (relative)
- Actual time and rows

**Optimization:**
- Add index on frequently filtered columns
- Join order matters
- Filter before aggregating

### Index Strategies

```sql
-- Single column (most common)
CREATE INDEX idx_email ON users(email);

-- Composite (for AND queries)
CREATE INDEX idx_user_date ON orders(user_id, created_at);

-- Partial (filter subset)
CREATE INDEX idx_active_users ON users(id) 
WHERE active = true;

-- Expression (for computed values)
CREATE INDEX idx_lower_email ON users(LOWER(email));
```

**When to index:**
- Frequently filtered columns
- Join columns
- Avoid: Write-heavy tables, low cardinality (gender)

---

## 🔄 Transactions & Isolation

### Isolation Levels

```
READ UNCOMMITTED: Dirty reads possible
READ COMMITTED: No dirty reads (default)
REPEATABLE READ: Consistent read throughout
SERIALIZABLE: Complete isolation (slowest)
```

### ACID Guarantees

```sql
BEGIN TRANSACTION;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;  -- Both succeed or neither

-- If error in middle: ROLLBACK
```

---

## 📊 Aggregation & Analytics

### GROUP BY & HAVING

```sql
-- Find users with multiple orders
SELECT user_id, COUNT(*) as order_count
FROM orders
GROUP BY user_id
HAVING COUNT(*) > 1;

-- Complex: Revenue by region, month
SELECT 
    region,
    DATE_TRUNC('month', order_date) as month,
    SUM(total) as revenue,
    COUNT(*) as order_count,
    AVG(total) as avg_order
FROM orders
WHERE order_date > '2024-01-01'
GROUP BY region, DATE_TRUNC('month', order_date)
HAVING SUM(total) > 10000
ORDER BY month DESC, revenue DESC;
```

---

## ⚖️ Trade-offs & Design Decisions

### Normalization vs. Denormalization

```
Normalization (Normalized Form 3NF)
├─ Advantages:
│  ├─ No data duplication
│  ├─ Easier updates (change once, propagate)
│  └─ Smaller storage
│
├─ Disadvantages:
│  ├─ More joins required
│  ├─ Slower analytical queries
│  └─ Complex queries harder
│
└─ When: Transactional systems (OLTP)

Denormalization
├─ Advantages:
│  ├─ Fewer joins
│  ├─ Faster reads
│  └─ Better for analytics
│
├─ Disadvantages:
│  ├─ Data duplication
│  ├─ Update complexity (multi-table)
│  └─ Larger storage
│
└─ When: Analytical systems (OLAP)
```

### Index Trade-offs

```
Index Type | Speed | Write Penalty | Storage | Use Case
-----------|-------|---------------|---------|----------
No Index   | Slow  | Fast          | Low     | Rarely queried
Single Col | Fast  | Moderate      | Moderate| WHERE clause
Composite  | Fast* | Slower        | Higher  | Multi-column filters
Partial    | Fast  | Fast          | Low     | Filtered subset
Expression | Fast  | Slowest       | Moderate| Computed values

* Only if columns in index order
```

### Isolation Level Trade-offs

```
Level                  | Speed | Consistency | Use Case
-----------------------|-------|-------------|------------------
READ UNCOMMITTED       | Fast  | Poor        | Rare
READ COMMITTED         | Fast  | Good        | Default (most DBs)
REPEATABLE READ        | Slower| Very Good   | Financial transactions
SERIALIZABLE           | Slowest| Perfect    | Critical operations
```

---

## 🏗️ SQL Architecture Patterns

### Vertical Partitioning (Column Families)
```
Orders Table (Large):
├─ orders_metadata (id, user_id, date) — Frequently accessed
└─ orders_data (order_id, items, address) — Large, infrequent

SELECT id, user_id FROM orders_metadata  -- Fast
SELECT items FROM orders_data WHERE id=1 -- Separate query
```

### Horizontal Partitioning (Range-based)
```
orders_2024_q1: date >= 2024-01-01 AND date < 2024-04-01
orders_2024_q2: date >= 2024-04-01 AND date < 2024-07-01
orders_2024_q3: date >= 2024-07-01 AND date < 2024-10-01

-- Query only relevant partition
SELECT * FROM orders_2024_q3 WHERE date > '2024-08-01'
```

### Materialized Views (Pre-computed Aggregations)
```
-- Instead of:
SELECT user_id, COUNT(*) as order_count, SUM(total)
FROM orders
GROUP BY user_id

-- Create materialized view (refreshed nightly):
CREATE MATERIALIZED VIEW user_order_stats AS
SELECT user_id, COUNT(*) as order_count, SUM(total)
FROM orders
GROUP BY user_id

-- Query becomes instant
SELECT * FROM user_order_stats WHERE user_id = 123
```

---

## 🔍 Query Optimization Techniques

### 1. Index Strategy Diagram

```
Query: SELECT * FROM orders WHERE user_id = 5 AND total > 100

Plan A: No index
├─ Full table scan: O(n)
├─ Filter each row
└─ Cost: 1,000,000 comparisons

Plan B: Index on (user_id)
├─ Seek to user_id = 5: O(log n)
├─ Then filter total > 100
└─ Cost: 1,000 comparisons (better)

Plan C: Composite index (user_id, total)
├─ Seek to (user_id = 5, total > 100): O(log n)
├─ Returns exactly matching rows
└─ Cost: Instant (best)

Lesson: Composite indexes faster if columns in query order
```

### 2. Join Optimization

```
Inner Join (INNER)
SELECT o.id, u.name
FROM orders o
INNER JOIN users u ON o.user_id = u.id
WHERE o.total > 100

Execution Plans:
- Nested Loop: Good for small result sets
- Hash Join: Good for large result sets
- Merge Join: Good if both tables sorted
→ EXPLAIN shows which used

Optimization:
1. Filter first (WHERE before JOIN)
2. Index on join columns
3. Smaller table on right
```

---

## 📊 Common Patterns & Solutions

### Finding Running Metrics

```sql
-- Cumulative sales over time
SELECT 
    month,
    revenue,
    SUM(revenue) OVER (ORDER BY month) as cumulative_revenue,
    AVG(revenue) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as 3month_avg
FROM monthly_sales
ORDER BY month;
```

### De-duplication with Ranking

```sql
-- Keep only latest order per user
SELECT * FROM (
    SELECT 
        user_id, order_id, date,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY date DESC) as rn
    FROM orders
) t
WHERE rn = 1;
```

### Gap Detection

```sql
-- Find gaps in transaction IDs
WITH numbered AS (
    SELECT 
        id,
        id - ROW_NUMBER() OVER (ORDER BY id) as gap_group
    FROM transactions
)
SELECT 
    MIN(id) as gap_start,
    MAX(id) as gap_end
FROM numbered
GROUP BY gap_group
HAVING MAX(id) - MIN(id) > COUNT(*) - 1;
```

---

## ❓ Interview Q&A

**Q: Find second highest salary in each department**
```sql
SELECT 
    department,
    salary
FROM (
    SELECT 
        department,
        salary,
        ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rn
    FROM employees
) ranked
WHERE rn = 2;
```
**Follow-up:** What if you want 2nd highest without ties counted twice?  
→ Use `DENSE_RANK()` instead of `ROW_NUMBER()`

**Q: Write a query to find duplicate emails**
```sql
SELECT email, COUNT(*) as count
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```
**Follow-up:** Find users with duplicate emails and get full details?
```sql
SELECT u.* FROM users u
WHERE u.email IN (
    SELECT email FROM users
    GROUP BY email HAVING COUNT(*) > 1
);
```

**Q: Optimize slow query with 1M rows**
```
Steps:
1. Run EXPLAIN ANALYZE to see execution plan
2. Identify:
   - Seq Scan (indicates missing index)
   - Hash Join cost (indicates large intermediate result)
   - Nested Loop (slow for large joins)
3. Add indexes on:
   - WHERE clause columns
   - JOIN condition columns
   - ORDER BY columns
4. Consider:
   - Denormalization (cache aggregates)
   - Partitioning (query only relevant partition)
   - Materialized views (pre-compute aggregations)
```

**Q: How to handle 1 billion rows efficiently?**
```sql
-- Bad: Scans everything
SELECT COUNT(*) FROM orders;

-- Better: Use statistics
SELECT reltuples FROM pg_class WHERE relname = 'orders';

-- Partitioning: Only query needed partition
SELECT COUNT(*) FROM orders_2024_q3 WHERE date > '2024-08-01';

-- Pre-compute: Use materialized view
CREATE MATERIALIZED VIEW order_stats AS
SELECT DATE_TRUNC('day', date) as day, COUNT(*) as count
FROM orders GROUP BY 1;
```

**Q: Design schema for e-commerce with billions of orders**
```sql
-- Normalized (transactional)
CREATE TABLE orders (
    id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    total DECIMAL(10,2)
);
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);

CREATE TABLE order_items (
    id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT,
    price DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(id)
);
CREATE INDEX idx_items_order ON order_items(order_id);

-- Partitioning by date
CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
```

**Q: How to ensure ACID compliance in distributed system?**
```
1. Strong consistency: Use single database for transaction
2. Eventual consistency: Multi-step with compensation
   - Write to primary (succeeds)
   - Replicate to secondaries (async)
   - Handle race conditions (version numbers, timestamps)
3. Saga pattern: Compensating transactions
   - Step 1: Deduct from account A
   - Step 2: Add to account B
   - If step 2 fails: Compensate step 1
```

---

## 🧪 Practical Exercises & Solutions

### Exercise 1: Optimize Slow Query (Easy)

**Problem:**
```sql
-- This query is slow (~10 seconds on 1M rows)
SELECT u.id, u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.country = 'US'
  AND o.created_at >= '2024-01-01'
GROUP BY u.id, u.name;
```

**Task:** 
1. Show what the execution plan might look like
2. Identify the bottleneck
3. Propose indexes
4. Estimate improvement

**Solution:**

```sql
-- Step 1: Check execution plan
EXPLAIN ANALYZE
SELECT u.id, u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.country = 'US'
  AND o.created_at >= '2024-01-01'
GROUP BY u.id, u.name;

-- Output might show:
-- Seq Scan on users (full table scan = SLOW)
-- Hash Join (medium cost)
-- Total rows: 100K, Actual: 50K
-- Time: 9500ms

-- Step 2: Add indexes
CREATE INDEX idx_users_country ON users(country);
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- Step 3: Optimized query (same logic, better indexes)
SELECT u.id, u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.country = 'US'
  AND o.created_at >= '2024-01-01'
GROUP BY u.id, u.name;

-- New execution plan:
-- Index Scan on idx_users_country (fast lookup)
-- Index Seek on idx_orders_user_date (fast range scan)
-- Hash Join (same cost)
-- Time: 500ms (20x improvement!)

-- Step 4: Further optimization (if needed)
-- Pre-compute aggregates
CREATE MATERIALIZED VIEW user_order_stats AS
SELECT 
  u.id, 
  u.name,
  COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.country = 'US'
  AND o.created_at >= '2024-01-01'
GROUP BY u.id, u.name;

-- Now query is instant (100ms)
SELECT * FROM user_order_stats;
```

**Key Concepts:**
- Index on filtered column (country)
- Composite index on join + filter (user_id, created_at)
- Materialized view for pre-computation
- Expected improvement: 20x to 100x

---

### Exercise 2: Design Schema for Events (Medium)

**Problem:**
Design a schema for an event tracking system:
- 100M events/day
- 10 event types
- Need to query: events by user, by type, by time range
- 1-year retention
- Support aggregations (count, sum, average)

**Task:**
1. Design normalized schema
2. Propose indexes
3. Suggest partitioning
4. Write sample queries

**Solution:**

```sql
-- Schema Design
CREATE TABLE events (
  event_id BIGINT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  event_type VARCHAR(50) NOT NULL,
  event_timestamp TIMESTAMP NOT NULL,
  properties JSONB,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE event_types (
  event_type_id INT PRIMARY KEY,
  event_type_name VARCHAR(50) UNIQUE NOT NULL
);

-- Indexes (critical for performance)
CREATE INDEX idx_events_user_timestamp 
  ON events(user_id, event_timestamp DESC);

CREATE INDEX idx_events_type_timestamp 
  ON events(event_type, event_timestamp DESC);

CREATE INDEX idx_events_timestamp 
  ON events(event_timestamp DESC);

-- Partitioning by date (for 100M events/day)
CREATE TABLE events (...)
  PARTITION BY RANGE (DATE(event_timestamp)) (
    PARTITION p_2024_01 VALUES LESS THAN ('2024-02-01'),
    PARTITION p_2024_02 VALUES LESS THAN ('2024-03-01'),
    ...
    PARTITION p_future VALUES LESS THAN (MAXVALUE)
  );

-- Sample Queries

-- Query 1: Get user's events in time range
SELECT user_id, event_type, event_timestamp, properties
FROM events
WHERE user_id = 12345
  AND event_timestamp >= '2024-05-01'
  AND event_timestamp < '2024-05-02'
ORDER BY event_timestamp DESC;
-- Uses: idx_events_user_timestamp
-- Time: <100ms

-- Query 2: Aggregate events by type
SELECT 
  event_type,
  COUNT(*) as event_count,
  COUNT(DISTINCT user_id) as unique_users
FROM events
WHERE event_timestamp >= '2024-05-01'
  AND event_timestamp < '2024-05-02'
GROUP BY event_type;
-- Uses: idx_events_type_timestamp + partitioning
-- Time: ~1 second

-- Query 3: Recent events (last 100)
SELECT *
FROM events
WHERE event_timestamp >= NOW() - INTERVAL '1 hour'
ORDER BY event_timestamp DESC
LIMIT 100;
-- Uses: idx_events_timestamp
-- Time: <50ms

-- Query 4: Event funnel (users who did A then B)
WITH step_a AS (
  SELECT DISTINCT user_id
  FROM events
  WHERE event_type = 'page_view'
    AND event_timestamp >= '2024-05-01'
),
step_b AS (
  SELECT DISTINCT user_id
  FROM events
  WHERE event_type = 'click'
    AND event_timestamp >= '2024-05-01'
)
SELECT 
  (SELECT COUNT(*) FROM step_a) as step_a_users,
  (SELECT COUNT(*) FROM step_b) as step_b_users,
  (SELECT COUNT(*) FROM step_a WHERE user_id IN (SELECT user_id FROM step_b)) as funnel_users;

-- Query 5: Top events today
SELECT 
  event_type,
  COUNT(*) as count
FROM events
WHERE DATE(event_timestamp) = CURRENT_DATE
GROUP BY event_type
ORDER BY count DESC
LIMIT 10;
```

**Trade-offs:**
- Partitioning: Fast queries on recent data, slower on old data
- JSONB: Flexible properties, slower aggregations on properties
- Indexes: Speed up queries, slow down inserts

---

### Exercise 3: Handle Duplicate Orders (Medium)

**Problem:**
You have orders table with duplicate rows. How to:
1. Identify duplicates
2. Remove duplicates
3. Prevent future duplicates

**Solution:**

```sql
-- Table with duplicates
CREATE TABLE orders (
  order_id INT,
  user_id INT,
  amount DECIMAL,
  created_at TIMESTAMP
);

-- Insert sample data with duplicates
INSERT INTO orders VALUES
(1, 101, 100, '2024-05-01 10:00:00'),
(1, 101, 100, '2024-05-01 10:00:00'),  -- Duplicate!
(2, 102, 200, '2024-05-01 11:00:00'),
(2, 102, 200, '2024-05-01 11:00:00'),  -- Duplicate!
(3, 103, 300, '2024-05-01 12:00:00');

-- Identify duplicates
SELECT order_id, COUNT(*) as duplicate_count
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;

-- Remove duplicates (keep first occurrence)
DELETE FROM orders
WHERE ctid NOT IN (
  SELECT MIN(ctid)
  FROM orders
  GROUP BY order_id, user_id, amount
);

-- Or using ROW_NUMBER (more portable)
DELETE FROM orders
WHERE ctid IN (
  SELECT ctid
  FROM (
    SELECT 
      ctid,
      ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY created_at) as rn
    FROM orders
  ) t
  WHERE rn > 1
);

-- Prevent future duplicates: Add unique constraint
ALTER TABLE orders
ADD CONSTRAINT uk_order_id UNIQUE (order_id);

-- Or: Idempotent insert
INSERT INTO orders (order_id, user_id, amount, created_at)
VALUES (1, 101, 100, '2024-05-01 10:00:00')
ON CONFLICT (order_id) DO NOTHING;

-- Or: Handle with merge
INSERT INTO orders (order_id, user_id, amount, created_at)
VALUES (1, 101, 100, '2024-05-01 10:00:00')
ON CONFLICT (order_id) DO UPDATE SET
  amount = EXCLUDED.amount,
  created_at = EXCLUDED.created_at;
```

---

### Exercise 4: Complex Window Function (Hard)

**Problem:**
Calculate:
1. Running total of sales per day
2. Month-over-month growth
3. Moving average (7-day)

**Solution:**

```sql
-- Sample data
CREATE TABLE daily_sales (
  date DATE,
  region VARCHAR(50),
  sales DECIMAL
);

INSERT INTO daily_sales VALUES
('2024-04-01', 'North', 1000),
('2024-04-02', 'North', 1100),
('2024-04-03', 'North', 950),
-- ... more data

-- Exercise Solution
WITH daily_totals AS (
  SELECT 
    date,
    region,
    sales,
    -- 1. Running total (cumulative)
    SUM(sales) OVER (
      PARTITION BY region
      ORDER BY date
      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_total,
    
    -- 2. Day-over-day growth
    LAG(sales) OVER (
      PARTITION BY region
      ORDER BY date
    ) as prev_day_sales,
    
    -- 3. 7-day moving average
    AVG(sales) OVER (
      PARTITION BY region
      ORDER BY date
      ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) as moving_avg_7d,
    
    -- 4. Month-over-month comparison
    LAG(sales, 30) OVER (
      PARTITION BY region
      ORDER BY date
    ) as sales_30_days_ago
  FROM daily_sales
),
with_calculations AS (
  SELECT 
    date,
    region,
    sales,
    running_total,
    prev_day_sales,
    ROUND(((sales - prev_day_sales) / prev_day_sales * 100)::NUMERIC, 2) as pct_change_day,
    moving_avg_7d,
    sales_30_days_ago,
    ROUND(((sales - sales_30_days_ago) / sales_30_days_ago * 100)::NUMERIC, 2) as pct_change_month
  FROM daily_totals
)
SELECT *
FROM with_calculations
WHERE date >= '2024-04-20'
ORDER BY region, date;

-- Expected output:
-- date       | region | sales | running_total | pct_change_day | moving_avg_7d | pct_change_month
-- 2024-04-20 | North  | 1050  | 31500         | 5.00           | 1028.57       | 2.50
-- 2024-04-21 | North  | 1120  | 32620         | 6.67           | 1042.86       | 3.10
```

---

### Exercise 5: Recursive CTE for Hierarchy (Hard)

**Problem:**
Find all employees under a manager (multi-level hierarchy)

**Solution:**

```sql
-- Employees with manager hierarchy
CREATE TABLE employees (
  employee_id INT PRIMARY KEY,
  name VARCHAR(100),
  manager_id INT,
  salary DECIMAL,
  FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
);

INSERT INTO employees VALUES
(1, 'CEO', NULL, 500000),
(2, 'VP Engineering', 1, 300000),
(3, 'VP Sales', 1, 280000),
(4, 'Engineering Lead', 2, 200000),
(5, 'Senior Engineer', 4, 150000),
(6, 'Junior Engineer', 4, 100000),
(7, 'Sales Manager', 3, 120000),
(8, 'Sales Rep', 7, 80000);

-- Find all employees under VP Engineering (recursive)
WITH RECURSIVE org_hierarchy AS (
  -- Base case: Start with target manager
  SELECT 
    employee_id,
    name,
    manager_id,
    salary,
    1 as level
  FROM employees
  WHERE employee_id = 2  -- VP Engineering
  
  UNION ALL
  
  -- Recursive case: Find direct reports
  SELECT 
    e.employee_id,
    e.name,
    e.manager_id,
    e.salary,
    oh.level + 1
  FROM employees e
  INNER JOIN org_hierarchy oh ON e.manager_id = oh.employee_id
)
SELECT *
FROM org_hierarchy
ORDER BY level, name;

-- Output:
-- employee_id | name               | manager_id | salary | level
-- 2           | VP Engineering     | 1          | 300000 | 1
-- 4           | Engineering Lead   | 2          | 200000 | 2
-- 5           | Senior Engineer    | 4          | 150000 | 3
-- 6           | Junior Engineer    | 4          | 100000 | 3

-- Calculate total team size and salary budget
WITH RECURSIVE org_hierarchy AS (
  SELECT 
    employee_id,
    name,
    manager_id,
    salary,
    1 as level
  FROM employees
  WHERE employee_id = 2
  
  UNION ALL
  
  SELECT 
    e.employee_id,
    e.name,
    e.manager_id,
    e.salary,
    oh.level + 1
  FROM employees e
  INNER JOIN org_hierarchy oh ON e.manager_id = oh.employee_id
)
SELECT 
  COUNT(*) as team_size,
  SUM(salary) as total_salary_budget,
  AVG(salary) as avg_salary,
  MAX(level) as max_depth
FROM org_hierarchy;

-- Output:
-- team_size | total_salary_budget | avg_salary | max_depth
-- 4         | 650000              | 162500     | 3
```

---

## 💡 Interview Tips

**What the interviewer is really asking:**
- Q: "Optimize this query" → Do you know EXPLAIN, indexes, execution plans?
- Q: "Design schema for billions of rows" → Do you know partitioning, denormalization?
- Q: "Handle failures" → Do you understand ACID, transactions, replication?
- Q: "Trade-offs?" → Do you balance consistency, performance, complexity?

**How to answer:**
1. **Clarify:** Ask about scale, consistency requirements, read/write ratio
2. **Simple first:** Start with normalized schema, simple queries
3. **Optimize:** Add indexes, partitioning, caching as needed
4. **Trade-offs:** Discuss why each choice (consistency vs. performance)
5. **Verify:** Show execution plan improvements

---

**Last updated:** 2026-05-22
