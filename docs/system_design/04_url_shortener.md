# URL Shortener

## Problem Statement

Design a service to shorten long URLs. Convert long URL to short unique identifier, support reverse mapping.

**Operations:**
- `shorten(long_url)` -> short_code
- `expand(short_code)` -> long_url

**Constraints:**
- Short codes should be unique
- Fixed-length short codes (6-8 chars)
- Support distributed generation

## Design

### Encoding Approach

```
Use Base62 (a-z, A-Z, 0-9)

Counter: 1 -> 1
Counter: 62 -> 10
Counter: 3844 -> 100

ID generation: Atomic counter or distributed ID service
```

**Complexity:** O(log n) to encode/decode counter

### Collision Handling

1. **Distributed IDs (Recommended)**
   - Use Snowflake-like ID generator (timestamp + machine_id + counter)
   - Guarantees uniqueness across servers
   - No collisions

2. **Hash-based**
   - Hash URL, take first N chars
   - Handle collisions by appending random suffix

### Data Structure

```
HashMap:
  {short_code -> long_url}
  {long_url -> short_code}  (optional, for dedup)
```

## Trade-offs

| Approach | Pro | Con |
|----------|-----|-----|
| Atomic Counter | Simple, predictable | Central bottleneck |
| Distributed ID | Scalable, distributed | Complex, more state |
| Hash + Random | No coordination | Collision handling |

## Complexity

| Operation | Time | Space |
|-----------|------|-------|
| shorten | O(log n) | O(1) |
| expand | O(1) | O(1) |
| Space | — | O(n) |
