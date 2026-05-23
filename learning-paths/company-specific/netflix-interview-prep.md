# Netflix Interview Preparation

Specialized guide for Netflix SDE interviews.

---

## 🎬 Netflix Focus

**Core Business:** Video streaming, recommendation engine

**What Netflix Cares About:**
1. **Scalability** — Millions concurrent users, billions requests/day
2. **Performance** — Sub-second latency for recommendations
3. **Reliability** — 99.99% uptime, seamless playback
4. **Data-driven decisions** — A/B testing, metrics everywhere

---

## 📋 Interview Format

| Round | Focus | Notes |
|-------|-------|-------|
| Phone | Medium coding + system design | 60 min |
| Onsite | 2-3 coding rounds | 45-60 min each |
| System Design | Streaming/recommendation systems | 45-60 min |
| Behavioral | Impact, ownership, scale thinking | 30-45 min |

---

## 🎯 Key Topics for Netflix

### Tier 1: Must Know

**Recommendation Systems (30%)**
- Collaborative filtering
- Content-based filtering
- Hybrid approaches
- A/B testing recommendations

**Streaming Infrastructure (25%)**
- Video encoding/transcoding
- CDN optimization
- Buffering strategies
- Bandwidth optimization

**Database Design (20%)**
- Handling billions of events
- Time-series data (watch history)
- Caching strategies
- Denormalization patterns

**Distributed Systems (15%)**
- Eventual consistency
- CAP theorem tradeoffs
- Failure handling
- Data replication

**Coding Patterns (10%)**
- Array/string optimization
- Graph algorithms (social graphs, related content)

---

## 💡 Netflix-Specific Problems

**Problem 1: Design Recommendation System**
```
Requirements:
- Personalized recommendations for 250M users
- <500ms latency
- Real-time updates on user behavior
- A/B testing capability

Approach:
- Pre-computed recommendations (offline)
- Cache in Redis (hot items)
- Hybrid: Batch + real-time
- Feature flags for A/B tests
```

**Problem 2: Design Video Streaming**
```
Requirements:
- Adaptive bitrate (adjust quality based on network)
- Handle 100M concurrent streams
- Minimize buffering

Approach:
- Multiple bitrate versions (480p, 720p, 1080p)
- CDN for edge caching
- Monitor bandwidth, adjust quality
- Predictive buffering
```

---

## 📊 Preparation Timeline

### 4 Weeks

**Week 1:**
- Coding patterns (arrays, graphs, DP) — 20 problems
- Basic system design concepts

**Week 2:**
- Recommendation systems (collaborative filtering, ML basics)
- Database design (sharding, caching)

**Week 3:**
- Streaming systems (encoding, CDN, buffering)
- Distributed systems (consistency, replication)

**Week 4:**
- Mock interviews (2-3)
- Netflix-specific system designs (2-3)
- Behavioral stories

---

## 🎯 Interview Tips

**What interviewers look for:**
- Thinking at Netflix scale (millions of users)
- Understanding trade-offs (quality vs. latency)
- Data-driven decisions (metrics, A/B testing)
- Practical knowledge (CDN, caching strategies)

**Good answers incorporate:**
- Back-of-envelope calculations
- Multiple approaches with trade-offs
- Monitoring/observability
- Resilience patterns

---

## 📚 Resources

- [System Design: Recommendation Systems](../../docs/03-system-design/)
- [ML Fundamentals](../../docs/04-ai-ml-llms/01-ml-fundamentals.md)
- [Database Design](../../docs/01-interview-frameworks/database-fundamentals.md)
- [Caching Patterns](../../docs/03-system-design/01-caching/)

---

**Last updated:** 2026-05-22
