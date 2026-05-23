# API Pagination & Filtering

Design efficient pagination and filtering for large datasets without causing performance degradation.

---

## ⚖️ Pagination Strategy Trade-offs

| Strategy | Offset | Memory | Consistency | Use Case |
|----------|--------|--------|---|---|
| **Offset** | 1000 | Low | Poor (breaks on deletes) | Web UI |
| **Cursor** | O(1) | Low | Good | Mobile apps, APIs |
| **Keyset** | O(1) | Low | Good | Analytics |
| **Seek** | O(log n) | Medium | Good | Stream processing |

---

## 🏗️ Pagination Patterns

### Offset-based Pagination
```sql
SELECT * FROM orders OFFSET 1000 LIMIT 10;
-- Problems: Skips 1000 rows, slow at high offsets
```

### Cursor-based Pagination
```sql
SELECT * FROM orders 
WHERE id > :cursor
ORDER BY id
LIMIT 10;
-- Benefits: O(1), handles inserts well
```

### Keyset Pagination
```sql
SELECT * FROM orders
WHERE (date, id) > (:cursor_date, :cursor_id)
ORDER BY date, id
LIMIT 10;
-- Benefits: Efficient range query
```

---

## ❓ Interview Q&A

**Q1: Offset pagination slow at page 10000 - solution?**

A:
- Problem: OFFSET 100000 skips 100K rows (expensive)
- Solution: Switch to cursor-based
  ```
  Instead of: SELECT * FROM orders OFFSET 100000 LIMIT 10
  Use: SELECT * FROM orders WHERE id > :last_id LIMIT 10
  ```

**Q2: Data changes during pagination - handle?**

A:
- Problem: User on page 2, data inserted on page 1 → page 2 shifts
- Solution: Snapshot isolation or cursor-based with immutable cursor

---

**Last updated:** 2026-05-22
