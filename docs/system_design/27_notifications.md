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

## Complexity

| Operation | Time |
|-----------|------|
| Send | O(1) queue |
| Deliver | O(1) per channel |
| Get notifications | O(k) |
