# Pub-Sub System

## Problem Statement

Implement a publish-subscribe messaging system where publishers send messages to topics and subscribers receive them asynchronously.

**Requirements:**
- Topics (channels for messages)
- Publish messages to topics
- Subscribe to topics
- Async message delivery
- Multiple subscribers per topic

## Design

### Architecture

```
Publisher ---→ Topic ---→ Subscriber1
                  │    ---→ Subscriber2
                  └-------→ Subscriber3
```

### Key Components

```
Topic: Channel holding subscribers and message queue
Publisher: Publishes messages to topics
Subscriber: Receives messages from subscribed topics
Message: Data being published
```

### Data Structure

```
topics: {topic_name -> [subscribers, message_queue]}
subscribers: {subscriber_id -> subscribed_topics[]}
```

### Operations

```
subscribe(subscriber, topic):
  topics[topic].subscribers.add(subscriber)

publish(topic, message):
  for each subscriber in topics[topic].subscribers:
    subscriber.receive(message)

receive(subscriber, message):
  subscriber.onMessage(message)
```

## Trade-offs

| Async | Sync |
|-------|------|
| Non-blocking, scalable | Simpler, immediate |
| Ordering challenges | Blocking calls |
| Decoupled publishers/subs | Tight coupling |

## Complexity

| Operation | Time |
|-----------|------|
| subscribe | O(1) |
| unsubscribe | O(1) |
| publish | O(n) where n=subscribers |
| Space | O(t+s+m) where t=topics, s=subscribers, m=messages |
