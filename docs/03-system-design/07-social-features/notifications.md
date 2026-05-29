# Notifications System

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

A notifications system bridges the gap between events happening on a platform and users becoming
aware of those events. When someone likes your post, comments on your photo, or sends you a message,
you expect to know about it across all your devices — in the app, via push notification, and perhaps
via email. At 500M DAU generating 10 notifications per user per day, the system must process 5B
notifications per day (57K/sec) with multi-channel delivery, per-user preferences, deduplication,
and delivery tracking.

The design must handle fan-out (one event → notifications for many recipients), channel routing
(in-app vs. push vs. email vs. SMS), template rendering, delivery retries with backoff, and digest
batching — all without overwhelming users who may have configured "quiet hours."

## Functional Requirements

- Trigger a notification from a platform event (like, comment, follow, message)
- Deliver via the appropriate channel(s): push (APNS/FCM), email, SMS, in-app feed
- Respect per-user notification preferences (opt-out per type, quiet hours, digest mode)
- Track delivery status (sent, delivered, opened)
- Support notification batching (email digest: "5 people liked your posts")

## Non-Functional Requirements

- **Scale:** 500M DAU; 10 notifications/user/day = 5B/day = 57K/sec; 500M push/day
- **Latency:** P99 < 5 sec from event to push delivery; email within 1 min; SMS within 30 sec
- **Availability:** 99.9%; notification loss acceptable for non-critical types (like); guaranteed
  delivery required for critical types (account security alerts, payment confirmations)
- **Consistency:** At-least-once delivery; deduplicate at display layer for user-visible duplicates

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Daily notifications:  5B/day = 57,870/sec
Push channel:         500M/day = 5,787/sec (FCM/APNS combined)
Email channel:        50M/day  = 579/sec (opt-in only, lower volume)
SMS channel:          5M/day   = 58/sec (critical alerts only)
In-app feed:          5B/day   = all notifications also in feed

Notification record:  ~500 bytes (type, actor, target, channel, status, template vars)
Storage/day:          5B * 500 bytes = 2.5 TB/day
Storage/30 days:      75 TB (hot); archive older to S3
Push APNs throughput: Apple APNs handles up to 1M tokens/sec; our 5,787/sec is trivial
FCM throughput:       Google FCM similarly unlimited at our scale
Template rendering:   ~1 ms/notification CPU; 57K/sec → 57K CPU-ms/sec = 57 vCPUs dedicated
```

### Architecture Diagram

```
  Platform Event: "user_99 liked user_42's photo_789"
        |
  +-----v-----------+
  | Event Publisher  |  ← post-svc, like-svc, comment-svc publish to Kafka
  +-----+-----------+
        |  Kafka: "notification.events" topic
  +-----v-----------+
  | Notification    |  ← Fan-out: determine recipients (usually just 1-2 users)
  | Dispatcher      |     Lookup preferences → filter opt-outs, quiet hours
  |                 |     Determine channels (push + in-app, or just in-app)
  +-----+-----+-----+
        |     |     |
   Push  Email  In-App
   Queue Queue  Feed
     |     |     |
  +--v-+  +v-+  +v-----------+
  |Push|  |SES|  | Feed Store |  ← each channel has its own queue and worker
  |Svc|  |/SG|  | (Redis +   |
  |   |  |   |  |  Postgres) |
  +---+  +---+  +------------+
     |     |
  APNs  Mailgun  ← external delivery providers
   FCM

Delivery tracking (async):
  APNs/FCM webhook → delivery_status update in notification_log table
```

### Data Model

```sql
-- Notification templates (static, managed by admins)
CREATE TABLE notification_templates (
    template_id     VARCHAR(64) PRIMARY KEY,  -- "like_photo", "new_follower", "payment_success"
    channel         ENUM('push','email','sms','inapp') NOT NULL,
    title_template  TEXT NOT NULL,  -- "{{actor_name}} liked your photo"
    body_template   TEXT NOT NULL,
    priority        ENUM('critical','high','normal','low') NOT NULL DEFAULT 'normal',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);

-- Per-user notification preferences
CREATE TABLE user_notification_preferences (
    user_id             BIGINT NOT NULL,
    notification_type   VARCHAR(64) NOT NULL,  -- "like", "comment", "follow"
    channel             ENUM('push','email','sms','inapp') NOT NULL,
    enabled             BOOLEAN NOT NULL DEFAULT TRUE,
    quiet_hours_start   TIME,    -- e.g., 22:00
    quiet_hours_end     TIME,    -- e.g., 08:00
    digest_mode         BOOLEAN NOT NULL DEFAULT FALSE,  -- batch into digest
    PRIMARY KEY (user_id, notification_type, channel)
);

-- Notification log (delivery record)
CREATE TABLE notification_log (
    notification_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_user_id BIGINT NOT NULL,
    actor_user_id     BIGINT,
    notification_type VARCHAR(64) NOT NULL,
    channel           ENUM('push','email','sms','inapp') NOT NULL,
    status            ENUM('PENDING','SENT','DELIVERED','FAILED','OPENED') NOT NULL DEFAULT 'PENDING',
    title             TEXT NOT NULL,
    body              TEXT NOT NULL,
    deep_link         VARCHAR(512),
    retry_count       INT NOT NULL DEFAULT 0,
    created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    sent_at           TIMESTAMP,
    delivered_at      TIMESTAMP,
    opened_at         TIMESTAMP,
    INDEX idx_recipient_created (recipient_user_id, created_at DESC),
    INDEX idx_status_created (status, created_at)  -- for retry job
) PARTITION BY RANGE (created_at);  -- monthly partitions

-- In-app notification feed (hot, read frequently)
-- Stored in Redis + Postgres for persistence
-- Redis: sorted set per user (score = created_at epoch)
-- Key: notif_feed:{user_id}  → max 100 recent notifications
```

### API Design

```
# Internal: trigger notification from platform event
POST /notifications/trigger   (internal-only, service-to-service)
  Body: {
    notification_type: "like_photo",
    actor_user_id: 99,
    recipient_user_id: 42,
    entity_id: "photo_789",
    entity_type: "photo",
    metadata: { photo_thumbnail_url: "..." }
  }
  Response: 202 { notification_id: "uuid", channels_queued: ["push","inapp"] }

# User-facing: get in-app notification feed
GET /notifications?limit=20&before=<cursor>
  Response: 200 {
    notifications: [
      { notification_id, type, title, body, is_read, deep_link, created_at },
      ...
    ],
    unread_count: 7,
    next_cursor: "uuid"
  }

# Mark as read
POST /notifications/read
  Body: { notification_ids: ["uuid1", "uuid2"] }
  Response: 200 { marked_read: 2 }

# User preferences
GET  /notifications/preferences
PUT  /notifications/preferences
  Body: { notification_type: "like", channel: "push", enabled: false }
  Response: 200 { updated: true }
```

### Basic Scaling

- **Kafka fan-out:** All notification triggers go into Kafka; consumers per channel (push consumer,
  email consumer, in-app consumer) process independently at their own rates
- **Per-channel workers:** Push workers call APNs/FCM; email workers call SES/SendGrid; each
  channel can scale independently based on its backlog
- **In-app feed in Redis:** Recent 100 notifications per user stored in Redis ZSET (score=timestamp);
  persistence in Postgres for older history; hot reads served from Redis
- **Preference cache:** User preferences cached in Redis (TTL=5 min); checked before every
  notification dispatch to filter out opt-out users early

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
Kafka (notification.events topic):
  57K events/sec * 1 KB = 57 MB/sec ingest
  Partitions: 57 MB / 100 MB per partition = 1 partition; use 20 for consumer parallelism
  Retention: 7 days → 57 MB/sec * 86400 * 7 = 34.5 TB

Dispatcher service:
  57K events/sec; per event: lookup recipient prefs (Redis, 1 ms) + route to channels
  20 goroutines/threads can handle 57K events/sec at 1 ms each
  CPU: 4 vCPUs per dispatcher instance; 5 instances for redundancy

Push worker (APNs/FCM):
  5,787 push/sec; APNs HTTP/2 supports multiplexed connections (1000+ concurrent requests)
  One push worker handles 1K pushes/sec → 6 workers needed
  Retry: exponential backoff (1s, 2s, 4s, max 3 retries); failed device tokens pruned

Email worker (SES):
  579 emails/sec; SES rate limit 14 emails/sec/connection by default; 100+ connections needed
  SendGrid/SES bulk: supports up to 10K emails/sec with proper account limits
  Digest rendering: batch up to 50 events into one email (Handlebars/Jinja2 template)

Notification log DB (Postgres):
  57K writes/sec → partitioned by month; each partition ~2.5 TB (30 days)
  Writes: primary partition is hot; use columnar append (TOAST for large bodies)
  Reads: mostly point lookup by notification_id or range scan by (user_id, created_at DESC)
  Archive: partitions older than 30 days moved to S3 as Parquet; access via Athena

Redis (in-app feed + preferences):
  500M users * 100 notifications * 200 bytes = 10 TB → NOT all in RAM
  Solution: only active users' feeds in Redis (ZADD with TTL/eviction policy)
  Active users (DAU = 500M): 500M * 100 * 200 bytes = 10 TB → shard across 40 Redis nodes
  Preferences: 500M users * 500 bytes = 250 GB → cache hot users only (LRU eviction)
```

### Failure Modes

```
FAILURE: APNs returns "invalid device token" (user uninstalled app)
  Response: APNs returns 400 BadDeviceToken or 410 Unregistered
  Action:   Remove device token from device_tokens table; stop sending to that token
  If not cleaned up: device token list grows, waste 10-30% of push budget on dead tokens

FAILURE: Notification storm (viral event → 10M notifications in 1 min)
  Scenario: celebrity posts → 10M followers each get a notification
  Detection: Kafka consumer lag spikes > 1M messages
  Mitigation: Rate limit per recipient: max 50 notifications/sec from dispatcher
              Digest mode auto-triggers: if user would receive > 5 notifications in 10 sec,
              bundle into one: "99 and 5 others liked your post"
              Priority queues: critical notifications (security alerts) skip the queue

FAILURE: Email provider (SES) temporary outage
  Detection:  HTTP 5xx rate > 10% from SES client
  Mitigation: Circuit breaker → route email queue to Mailgun (secondary provider)
              Failed emails stay in Kafka; consumer pauses → Kafka retains for 7 days
              Resume delivery when SES recovers (at-least-once via Kafka offset management)

FAILURE: Notification log DB overloaded
  Symptom:    Write latency > 100 ms P99 (normally < 5 ms)
  Mitigation: Batch inserts (100 rows per INSERT instead of 1 per INSERT): 100× fewer commits
              Write to Redis queue first; async DB write worker drains queue
              If still overloaded: drop low-priority (like, comment) log entries; keep critical
```

### Consistency Boundaries

```
PUSH DELIVERY GUARANTEE:
  At-least-once: Kafka consumer commits offset only after successful push or DLQ placement
  APNs/FCM guarantee: once they accept the message (200 OK), they deliver to device
  End-to-end: we guarantee exactly-once trigger → APNs accepts it → APNs delivers it once
  Push can still not appear if: device offline (APNs caches last push per app), token invalid

IN-APP FEED CONSISTENCY:
  Redis ZSET is authoritative for recent 100 notifications
  Postgres is authoritative for historical notifications
  Consistency issue: Redis can be ahead of Postgres (written first) or behind (if Redis fails)
  Resolution: write to Postgres first → then Redis; if Redis write fails, next read rebuilds
              from Postgres (expensive but rare fallback)

PREFERENCE CONSISTENCY:
  Preferences cached in Redis (TTL=5 min)
  User disables email at 12:00 → may receive emails until 12:05 (cache TTL)
  Critical preference changes (opt-out of all): write-through cache invalidation immediately
  Non-critical (quiet hours): tolerate 5 min lag → much simpler

RATE LIMITING CONSISTENCY:
  Per-user rate limit stored in Redis (INCR + EXPIRE pattern)
  Multi-region: rate limit only in local region → cross-region, user may receive 2× rate limit
  Accept: slight over-notification in multi-region is better than cross-region coordination cost
```

### Cost Model

```
Kafka (notification events, 7-day retention):
  34.5 TB; 5-broker MSK: $50K/yr

Push workers (6 instances, c6g.xlarge):
  6 * $0.136/hr * 8760 = $7,145/yr
  APNs/FCM: FREE (no per-push cost from Apple/Google)

Email via SES:
  50M emails/day * 365 * $0.10/1000 emails = $1,825/yr
  (SES is $0.10/1000 emails after free tier)

SMS via Twilio:
  5M SMS/day * 365 * $0.0075/SMS = $13,688/yr per country (varies widely)

Notification log DB (Postgres RDS, 30-day hot storage):
  db.r6g.8xlarge + 3 TB NVMe: $15K/yr compute + $12K/yr storage = $27K/yr
  S3 archive: 75 TB * 30 days rolling → 2.25 PB * $0.023/GB = $52K/yr

Redis (40 nodes, r6g.2xlarge):
  40 * $0.485/hr * 8760 = $170K/yr (dominant compute cost)

Total: ~$320K/yr for 500M DAU
Per-user: $0.00064/user/year ($0.000053/user/month)
Per notification: $320K / 1.825 trillion notifications = $0.000000175/notification
```

---

## Trade-off Comparison

| Approach | Pros | Cons | Best For |
|----------|------|------|----------|
| Fan-out on write (pre-computed per-user feeds) | Fast read (O(1) per user); low read latency | Write amplification for celebrities (100M writes per post); massive storage | Platforms where most users have < 10K followers; read-heavy apps |
| Fan-out on read (pull model) | No write amplification; works for any follower count | Slower reads (fetch + merge on read); complex caching | Platforms with celebrities (Twitter hybrid); write-heavy apps |
| Kafka per-channel topics | Channel-independent scaling; replay on failure; durable | More Kafka topics to manage; per-channel consumer groups; latency | Large-scale multi-channel notification systems |
| Direct DB queue (polling) | Simple; no extra infra; ACID | DB polling overhead; doesn't scale past ~1K notifications/sec | Small platforms, early stage |

## Follow-up Questions (escalating difficulty)

1. **(L3)** What is fan-out in the context of notifications?
   → Fan-out is the process of taking one event (e.g., "user A posted a photo") and generating
   notifications for all N recipients (user A's 10K followers). Fan-out on write creates N
   notification records immediately at event time. Fan-out on read creates 1 event record and
   generates each user's feed dynamically when they open the app.

2. **(L3)** How do you handle a user's quiet hours preference?
   → At dispatch time, check the user's quiet_hours_start and quiet_hours_end in their preferences
   (cached in Redis). If the current time (in user's timezone) falls within quiet hours: delay the
   notification to quiet_hours_end by scheduling a delayed delivery (Redis sorted set with score=
   send_at timestamp; a scheduler polls and sends when ready).

3. **(L4)** How do you implement notification batching / digests?
   → Instead of sending "Alice liked your photo" and "Bob liked your photo" as two separate
   notifications, batch them: "Alice, Bob, and 3 others liked your photo." Implementation:
   buffer notification events per recipient per type for N seconds (e.g., 30 sec window).
   After window closes: if count > threshold (e.g., > 2), render digest template; else send
   individual notifications. Use Redis sorted set to buffer events per user.

4. **(L4)** How do you handle stale device tokens (user uninstalled the app)?
   → APNs returns HTTP 410 (Unregistered) or 400 (BadDeviceToken) when you push to an invalid
   token. Process APNs responses asynchronously: delete invalid tokens from device_tokens table.
   Also use APNs feedback service (hourly) to bulk-retrieve stale tokens. Without cleanup,
   invalid tokens waste push budget and inflate analytics.

5. **(L5)** How would you design rate limiting to prevent notification overload for a user who
   receives 1000 "like" notifications in 1 minute?
   → Per-user rate limiting per notification type: in Redis, maintain counter `rate:{user_id}:
   {type}` with TTL=60s. On each notification: INCR counter. If > threshold (e.g., 10/minute
   for "like"), switch to digest mode for this user-type pair. Rate limit decision made in
   dispatcher before routing to channel queues. Use a sliding window (Redis sorted set with
   event timestamps, ZREMRANGEBYSCORE to remove old events) for precise rate limiting.

6. **(L5)** How do you guarantee delivery for critical notifications (account hacked, fraud alert)?
   → Critical notifications use a separate high-priority Kafka topic (processed before normal
   topics). For each critical notification: retry up to 10 times with exponential backoff.
   Multi-channel: simultaneously attempt push + SMS + email (don't wait for push to fail before
   trying SMS). Store in notification_log with priority='critical'; reconciliation job checks
   every 5 min for critical notifications stuck in PENDING for > 60 sec.

7. **(L5+)** How does a large platform handle the "celebrity problem" — a single event triggering
   100M notifications — without overwhelming the notification pipeline?
   → Tiered fan-out: (1) Pre-compute follower list in chunks of 10K; (2) Dispatch chunk-level
   tasks to Kafka (10K tasks of 10K each); (3) Each task worker generates 10K notifications
   per second; (4) Total time: 100M / 10K TPS = 10,000 seconds ≈ 2.7 hours for full fan-out.
   Accept: celebrity post notifications are delayed up to hours for late-cohort followers.
   Prioritize: users who recently opened the app get notifications first. Drop low-priority
   (like) notifications if pipeline is > 10 minutes behind; send in-app only for stale likes.

## Anti-patterns / Things NOT to Say

- **"Call APNs/FCM synchronously in the user's request flow"** — Push delivery takes 200 ms-2s
  and can fail. Blocking the user's API call on push delivery degrades UX and creates tight
  coupling. Always dispatch notifications asynchronously via a queue.
- **"Send a push notification for every event, always"** — Users quickly disable push if they
  receive hundreds of notifications per day (notification fatigue). Implement rate limiting,
  digest batching, and respect quiet hours. Quality > quantity.
- **"Store all 5B daily notifications in memory (Redis)"** — 5B * 500 bytes = 2.5 TB of RAM —
  impossibly expensive. Store only the hot in-app feed (100 recent items per active user) in
  Redis; archive everything else to Postgres/S3.
- **"Fan-out to 100M followers synchronously when celebrity posts"** — 100M writes in one
  synchronous operation would take hours and block the post API. Fan-out must be asynchronous,
  chunked, and rate-limited. Use Kafka for async fan-out with backpressure.
- **"One Kafka topic for all notification types and channels"** — Mixing high-priority (security
  alerts) with low-priority (like) in one topic means a surge of likes delays security alerts.
  Use separate topics (or at minimum separate consumer groups with priority) per urgency level.

## Python Implementation (sketch)

```python
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from typing import Optional

class Channel(str, Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    INAPP = "inapp"

class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

@dataclass
class NotificationEvent:
    notification_type: str        # "like_photo", "new_follower"
    actor_user_id: int
    recipient_user_id: int
    entity_id: str
    metadata: dict = field(default_factory=dict)

@dataclass
class UserPrefs:
    enabled_channels: set[Channel] = field(
        default_factory=lambda: {Channel.PUSH, Channel.INAPP}
    )
    quiet_hours: Optional[tuple[int, int]] = None  # (start_hour, end_hour) UTC
    digest_types: set[str] = field(default_factory=set)

class NotificationDispatcher:
    """Routes notification events to appropriate channels, respecting preferences."""

    TEMPLATES = {
        "like_photo":   {"title": "{actor} liked your photo", "priority": Priority.LOW},
        "new_follower": {"title": "{actor} followed you",     "priority": Priority.NORMAL},
        "security_alert": {"title": "Security alert",         "priority": Priority.CRITICAL},
    }

    def __init__(self):
        self._prefs: dict[int, UserPrefs] = {}
        self._rate_counters: dict[str, int] = defaultdict(int)
        self._rate_window_start: dict[str, float] = {}
        self._queued: list[dict] = []  # simulates Kafka

    def set_preferences(self, user_id: int, prefs: UserPrefs) -> None:
        self._prefs[user_id] = prefs

    def _is_quiet_hours(self, prefs: UserPrefs) -> bool:
        if not prefs.quiet_hours:
            return False
        current_hour = int(time.strftime("%H", time.gmtime()))
        start, end = prefs.quiet_hours
        return start <= current_hour < end

    def _check_rate_limit(self, user_id: int, notif_type: str, limit: int = 10) -> bool:
        """Returns True if within rate limit (allow), False if exceeded."""
        key = f"{user_id}:{notif_type}"
        now = time.time()
        if now - self._rate_window_start.get(key, 0) > 60:
            self._rate_counters[key] = 0
            self._rate_window_start[key] = now
        self._rate_counters[key] += 1
        return self._rate_counters[key] <= limit

    def dispatch(self, event: NotificationEvent) -> list[dict]:
        prefs = self._prefs.get(event.recipient_user_id, UserPrefs())
        template = self.TEMPLATES.get(event.notification_type, {})
        priority = template.get("priority", Priority.NORMAL)

        # Rate limit check (skip for critical)
        if priority != Priority.CRITICAL:
            if not self._check_rate_limit(event.recipient_user_id, event.notification_type):
                return []  # rate limited → drop or digest

        # Quiet hours check (skip for critical)
        if priority != Priority.CRITICAL and self._is_quiet_hours(prefs):
            return []  # would queue for later in production

        dispatched = []
        for channel in prefs.enabled_channels:
            notif = {
                "notification_id": str(uuid.uuid4()),
                "recipient": event.recipient_user_id,
                "channel": channel.value,
                "type": event.notification_type,
                "title": template.get("title", "").format(actor=event.actor_user_id),
                "priority": priority.value,
            }
            self._queued.append(notif)  # → Kafka in production
            dispatched.append(notif)
        return dispatched


# Usage
dispatcher = NotificationDispatcher()
dispatcher.set_preferences(42, UserPrefs(
    enabled_channels={Channel.PUSH, Channel.INAPP},
    quiet_hours=(22, 8)
))

event = NotificationEvent(
    notification_type="like_photo",
    actor_user_id=99,
    recipient_user_id=42,
    entity_id="photo_789"
)
result = dispatcher.dispatch(event)
print(f"Dispatched to {len(result)} channels: {[n['channel'] for n in result]}")
```
