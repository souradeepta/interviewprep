# Estimation Techniques: Capacity Planning & Scalability Math

**Level:** L3-L5
**Time to read:** ~20 min

Master the art of estimating system capacity, scaling requirements, and identifying bottlenecks.

---

## Back-of-the-Envelope Estimation

The ability to estimate order of magnitude without calculators is critical in system design interviews.

### Power-of-10 Thinking

```
1 = 10^0
10 = 10^1
100 = 10^2
1K = 10^3
1M = 10^6
1B = 10^9
1T = 10^12
```

### Important Numbers to Memorize

| Metric | Value | Notes |
|--------|-------|-------|
| **Data size** | | |
| 1 byte | 1 character | |
| 1 KB | 10^3 bytes | 1000 bytes |
| 1 MB | 10^6 bytes | 1 million bytes |
| 1 GB | 10^9 bytes | 1 billion bytes, typical server RAM |
| 1 TB | 10^12 bytes | 1 trillion bytes, large hard drive |
| **Latency** | | |
| 1 nanosecond | 10^-9 seconds | CPU cycle |
| 1 microsecond | 10^-6 seconds | |
| 1 millisecond | 10^-3 seconds | Typical network packet |
| **Throughput** | | |
| 1 Mbps | ~125 KB/sec | Slow internet |
| 100 Mbps | ~12.5 MB/sec | Fast datacenter |
| 1 Gbps | ~125 MB/sec | Very fast datacenter |
| **Time intervals** | | |
| 1 second | Can process ~1000s of operations | |
| 1 hour | 3600 seconds | |
| 1 day | 86,400 seconds | |
| 1 year | 31,536,000 seconds ≈ 31.5M seconds | |

---

## Common Estimation Patterns

### QPS Estimation (Queries Per Second)

**Example: Twitter-like system with 100M DAU**

```
Daily Active Users (DAU): 100M
Average time on app: 2 hours
Average posts/user/day: 3
Average reads/user/day: 50 (reading feed)

Writes per second:
- Posts: 100M users * 3 posts/day / 86400 seconds/day
  = 300M posts/day / 86400
  = 3.5K QPS

Reads per second:
- Feed reads: 100M users * 50 reads/day / 86400
  = 5B reads/day / 86400
  = 58K QPS

Peak QPS = average * 2-3x (during peak hours)
Estimated peak: 
- Writes: 3.5K * 3 = 10.5K QPS
- Reads: 58K * 3 = 174K QPS
```

### Storage Estimation

**Example: Same Twitter system**

```
Posts:
- 3.5K posts/second * 86400 seconds/day = 302M posts/day
- Average post size: 1 KB (text + metadata)
- 302M posts/day * 1 KB = 302 GB/day
- 302 GB/day * 365 days = 110 TB/year

User profiles:
- 100M users * 1 KB per profile = 100 GB

Media (images, videos):
- 30% of posts have media
- Average media size: 500 KB
- 302M posts/day * 30% * 500 KB = 45 TB/day
- 45 TB/day * 365 days = 16.4 PB/year ← Most storage!

Total 1-year storage estimate: ~16.5 PB
```

### Bandwidth Estimation

**Example: Same Twitter system**

```
Download (reads):
- 174K QPS reads (peak)
- Average response: 50 KB (feed page with 20 posts)
- 174K * 50 KB = 8.7 GB/sec bandwidth
- 8.7 GB/s * 8 bits/byte = 69.6 Gbps

Upload (writes):
- 10.5K QPS writes (peak)
- Average post size: 5 KB
- 10.5K * 5 KB = 52.5 MB/sec = 0.4 Gbps

Total: ~70 Gbps (will need very fast datacenter connection)
```

### Database Size Estimation

**Example: Single database server**

```
Typical server specs:
- RAM: 256 GB
- Disk: 20 TB (with replication: 60 TB total with 3x replica)
- QPS capacity: ~5K-10K (depends on complexity)

Twitter estimation:
- 302M posts/day
- If keeping 2 years of data: 220B posts
- With replication: need massive sharding
```

---

## Scaling Calculations

### Server Count Estimation

```
QPS: 174K peak
Capacity per server: 1K QPS (conservative)
Servers needed: 174K / 1K = 174 servers

Add redundancy (N+1 failover): 174 * 1.2 = 209 servers

Add for upgrade/maintenance: 209 * 1.1 = 230 servers
```

### Load Balancer Distribution

```
Load balancer distributes evenly:
230 servers, 174K QPS
QPS per server: 174K / 230 = 756 QPS (below 1K capacity ✓)
```

### Database Sharding

```
Posts table: 220B rows (2 years of data)
Each shard: 500GB data (working set fits in RAM)

Shards needed: 220B rows * 1 KB/row / 500 GB
              = 220 TB / 500 GB
              = 440 shards

Write load distributed: 10.5K QPS / 440 shards = 24 QPS per shard ✓
```

### Cache Hit Ratio Impact

```
Without cache:
- 174K read QPS to database
- Database can handle 5K QPS max
- Bottleneck! ✗

With 80% cache hit ratio:
- 174K QPS * 80% = 139K QPS to cache (fast ✓)
- 174K QPS * 20% = 35K QPS to database (still too high)

With 95% cache hit ratio:
- 174K QPS * 95% = 165K QPS to cache (fast ✓)
- 174K QPS * 5% = 8.7K QPS to database (manageable with replication ✓)
```

---

## Latency Estimation

### End-to-End Request Latency

```
User request for feed:

1. Load Balancer: 1 ms
2. API Server (deserialize, auth): 5 ms
3. Cache lookup: 1 ms (cache miss goes to #4)
4. Database query: 20 ms
5. Response serialization: 2 ms
6. Network round trip to user: 50 ms

Total: 1 + 5 + 1 + 20 + 2 + 50 = 79 ms (good)

With cache hit (95% of requests):
1 + 5 + 1 + 50 = 57 ms ✓

Worst case (cache miss):
1 + 5 + 1 + 20 + 2 + 50 = 79 ms ✓

P99 target met (< 200 ms): ✓
```

### Network Latency by Region

```
Intra-datacenter: 1 ms
US East to West: 50 ms
US to Europe: 150 ms
US to Asia: 200 ms
Australia to US: 300 ms
```

---

## Capacity Planning Formula

### Simple Capacity Formula

```
Servers needed = (QPS * operations_per_request) / (capacity_per_server)
```

### Example

```
QPS: 10K (peak)
Operations per request: 100 (average)
Total operations: 10K * 100 = 1M operations/sec

Capacity per server: 100K operations/sec
Servers: 1M / 100K = 10 servers
```

### With Overhead

```
Servers needed = (QPS * ops_per_request / capacity_per_server) * safety_factor

Safety factor breakdown:
- 1.2 = 20% for failover/redundancy
- 1.1 = 10% for garbage collection pauses
- 1.1 = 10% for page cache misses
- Total: ~1.5x

Example:
10 servers * 1.5 = 15 servers total
```

---

## Estimation Scenarios

### Growth Planning

```
Current state (Year 0):
- 10M DAU
- 10K peak QPS
- 10 servers

Year 1: 2x growth
- 20M DAU
- 20K peak QPS
- 20 servers

Year 2: 3x growth
- 60M DAU
- 60K peak QPS
- 60 servers

Planning: Ensure infrastructure can scale to 3x without major redesign
```

### Cost Estimation

```
Server cost: $5,000 per server per year (on-premise) or $2/hour (cloud)
15 servers: 15 * $5,000 = $75,000/year

Cloud (4 weeks peak, 2 weeks normal):
- Peak: 15 servers * $2/hour * 168 hours/week * 4 weeks = $20,160
- Normal: 5 servers * $2/hour * 168 hours/week * 48 weeks = $40,320
- Total: $60,480/year

Savings with cloud: $75,000 - $60,480 = $14,520/year
Plus infrastructure costs, ops team, etc.
```

---

## Estimation Red Flags

| Mistake | Impact |
|---------|--------|
| **Forgetting to scale for peak** | Design fails during peak hours |
| **Overestimating server capacity** | Not enough servers at launch |
| **Not accounting for replication** | Storage estimate 3x off |
| **Forgetting network overhead** | Bandwidth bottleneck |
| **Single point of failure** | No redundancy = downtime |
| **Not leaving headroom** | No room for growth |

---

## Estimation Checklist

- ✓ Know key numbers (bytes, latency, throughput)
- ✓ Estimate QPS from DAU
- ✓ Calculate storage requirements
- ✓ Estimate bandwidth needs
- ✓ Plan sharding strategy
- ✓ Account for redundancy (N+1, replication)
- ✓ Leave headroom (1.5x+ capacity)
- ✓ Verify database can handle write QPS
- ✓ Verify cache hit ratio solves read bottleneck
- ✓ Consider geographic distribution
- ✓ Plan for growth trajectory (1x, 2x, 3x)
- ✓ Validate estimates are reasonable

---

## Quick Reference: Order of Magnitude

```
1 server can handle:
- 1K-5K QPS (simple CRUD)
- 1M stored objects
- 1 GB/sec disk throughput

1 database can handle:
- 1K-5K write QPS
- 10K-100K read QPS (with caching)

1 cache server (Redis/Memcached):
- 100K-1M QPS
- 256 GB - 1 TB data

Network:
- 1 Gbps = 125 MB/sec
- Typical API response = 1-100 KB
- Typical storage = 1 KB - 10 MB
```

