# Notifications System

## Problem Statement
Design a multi-channel notification system delivering alerts via email, SMS, push, and in-app.

**Operations:**
- `sendNotification(user_id, message, channels)` — Send notification
- `getNotifications(user_id)` — Get user notifications
- `markAsRead(notification_id)` — Mark read
- `setPreferences(user_id, channels, frequency)` — User preferences

## Design

### Multi-Channel Delivery

```
Email: SMTP service, batch processing
SMS: Third-party API (Twilio)
Push: FCM/APNs, device registration
In-app: Database, real-time via WebSocket
```

### Notification Queue

```
User preferences: Which channels enabled
Rate limiting: Max notifications per hour
Deduplication: Same message not sent twice
Retries: Failed channels retry
```

### Delivery Guarantee

```
At-least-once: Resend if no ACK
Tracking: Status per channel
Dead letter: Failed after retries
```


## Architecture Diagram

```
┌──────────────────────────────────────┐
│   Notification Service               │
│  ┌──────────────────────────────────┐  │
│  │ Events: like, follow, mention    │  │
│  │ Channels: push, email, SMS       │  │
│  │ Delivery: queue-based (Kafka)    │  │
│  │ Preferences: user opt-in/out     │  │
│  └──────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## Common Questions & Answers

**Q: Notification delivery reliability?** A: Persistent queue, retry exponential backoff, dead letter queue.

**Q: Thundering herd (all wake at once)?** A: Stagger notifications across time window, use jitter.

**Q: Preference system?** A: Per notification type opt-in. Don't spam = healthy user experience.

**Q: Real-time vs digest?** A: Real-time for critical (comment reply), digest for daily summary.

## Back-of-Envelope Calculations

1B users, 10 notifications/day avg. Throughput: 100K notif/sec. Delivery: 1% hard bounce rate. Cost: $0.01 per push, $10M/month at scale.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Real-time push | Immediate, engaging | Battery drain, spam |
| Digest email | Non-intrusive | Lower engagement |
| Hybrid | Balances both | More complex |

## Follow-up Interview Questions

1. Handle notification fatigue (user unsubscribes)? 2. Personalization (frequency, time)? 3. Multi-device synchronization? 4. Delivery channel failure (fall back)? 5. Cost optimization?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

## Complexity

| Operation | Time |
|-----------|------|
| Send | O(1) queue |
| Deliver | O(1) per channel |
| Get notifications | O(k) |
