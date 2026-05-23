# SQL Deep Dive — Advanced Queries and Optimization

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

**Q: Write a query to find duplicate emails**
```sql
SELECT email
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

**Q: Optimize slow query with 1M rows**
A: Use EXPLAIN, add indexes on filter/join columns, consider partitioning, denormalize if needed.

---

**Last updated:** 2026-05-22
