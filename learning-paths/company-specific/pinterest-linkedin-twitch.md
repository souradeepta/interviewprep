# Pinterest, LinkedIn, & Twitch Interview Prep

**Level:** L3-L5
**Time to read:** ~10 min

---

## 📌 Pinterest Interview Prep

### Focus: Recommendation & Search at Scale

**Key Topics:**
- Graph algorithms (user interest graph)
- Ranking systems (personalized feed)
- Real-time indexing (new pins searchable in seconds)

### System Design: Pinterest Feed

```
Requirements:
- 500M monthly users
- Personalized pin recommendations
- Real-time updates

Components:
- Graph of user interests
- ML ranking model
- Cache for hot pins
- Notification system (followers see pins)
```

---

## 💼 LinkedIn Interview Prep

### Focus: Professional Network & Search

**Key Topics:**
- Graph algorithms (connection finding, degrees of separation)
- Full-text search (job search, people search)
- Recommendation engine (job recommendations)

### System Design: LinkedIn Profile Search

```
Requirements:
- 900M+ users
- Complex filtering (location, skill, company)
- Real-time indexing

Approach:
- Elasticsearch for full-text search
- Filters via SQL database
- Cache popular searches
- Ranking by relevance + connections

Challenge: Balancing relevance vs. discovery
```

---

## 🎮 Twitch Interview Prep

### Focus: Real-Time Streaming & Chat

**Key Topics:**
- Real-time systems (chat, viewers, streamer stats)
- WebSocket & event streaming
- Distributed caching (viewer state across regions)

### System Design: Twitch Live Chat

```
Requirements:
- Millions of concurrent chats
- <1 second latency
- Moderation + filtering

Approach:
- WebSocket for real-time
- Kafka for chat events
- Redis for user state
- Content moderation (NLP + rules)
- Rate limiting per user

Scale: 10k messages/second per stream
```

---

## 🍕 DoorDash Interview Prep

### Focus: Logistics & Real-Time Optimization

**Key Topics:**
- Geospatial algorithms
- Optimization problems (assigning orders to drivers)
- Real-time tracking

### System Design: Order Assignment

```
Requirements:
- 1M+ daily orders
- <1 minute assignment latency
- Route optimization

Approach:
- Geohash for driver proximity
- ML for delivery time estimation
- Greedy matching or optimization solver
- Dynamic routing (can reassign in transit)

Challenge: NP-hard problem (need heuristics)
```

---

## 📊 Difficulty Tier

**Hard (expect all topics):**
- LinkedIn: Complex graph + search
- Twitch: Real-time at massive scale

**Medium (focused topics):**
- Pinterest: Good balance
- DoorDash: Real-time + optimization

---

**Last updated:** 2026-05-22
