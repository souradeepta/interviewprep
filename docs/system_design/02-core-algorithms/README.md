# 02. Core Algorithms

Apply algorithmic thinking to real-world problems with rate limiting, ID generation, and object modeling.

## Problems

### 3. Rate Limiter
**Problem**: Prevent API abuse by limiting request frequency per user.

**Algorithms**:
- Token Bucket: refill tokens over time, allow burst
- Sliding Window: strict rate limiting without burst
- Sliding Window Counter: efficient approximation

**Real-world Use**: API gateways, DDoS prevention, fair resource allocation

### 4. URL Shortener
**Problem**: Convert long URLs to short, memorable codes.

**Algorithms**:
- Counter-based: sequential IDs
- Snowflake: distributed ID generation
- Hash-based: collision detection and retry

**Real-world Use**: URL shortening services (bit.ly, tinyurl), distributed systems

### 5. Parking Lot
**Problem**: Design a system to manage parking across multiple levels with different spot sizes.

**Concepts**:
- Object-oriented design (Vehicle, Level, Spot)
- State management and transitions
- Efficient spot allocation (O(1) availability tracking)

**Real-world Use**: Smart parking systems, resource allocation

## Learning Outcomes

You'll learn:
1. ✅ How to apply algorithm design to real problems
2. ✅ Distributed ID generation at scale
3. ✅ Object-oriented system modeling
4. ✅ Handling concurrency and state
5. ✅ Back-of-envelope capacity planning

## Problem-Solving Approach

1. **Understand Constraints**: Rate limits, latency, capacity
2. **Choose Algorithm**: Analyze trade-offs
3. **Design Data Structures**: Optimize for operations
4. **Handle Edge Cases**: Overflow, collisions, failures
5. **Estimate Scale**: Can it handle 10x, 100x growth?

## Key Algorithms

| Problem | Primary | Alternative |
|---------|---------|-------------|
| Rate Limiter | Token Bucket | Sliding Window |
| URL Shortener | Snowflake ID | Counter + Base62 |
| Parking Lot | State Machine | Graph-based |

## Next Steps

- Implement each algorithm in your preferred language
- Test edge cases thoroughly
- Optimize for your specific constraints
- Move to **Design Patterns** for architectural thinking
