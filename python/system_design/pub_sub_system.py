"""Pub-Sub System - Publish-Subscribe messaging"""

from collections import defaultdict
from typing import Callable


class PubSubSystem:
    """Publish-Subscribe message system"""

    def __init__(self):
        self.topics = defaultdict(list)  # topic -> list of callbacks
        self.subscribers = defaultdict(set)  # subscriber_id -> set of topics

    def subscribe(self, topic: str, subscriber_id: str, callback: Callable):
        """Subscribe to a topic"""
        self.topics[topic].append((subscriber_id, callback))
        self.subscribers[subscriber_id].add(topic)
        print(f"Subscriber '{subscriber_id}' subscribed to topic '{topic}'")

    def unsubscribe(self, topic: str, subscriber_id: str):
        """Unsubscribe from a topic"""
        self.topics[topic] = [
            (sid, cb) for sid, cb in self.topics[topic] if sid != subscriber_id
        ]
        self.subscribers[subscriber_id].discard(topic)
        print(f"Subscriber '{subscriber_id}' unsubscribed from topic '{topic}'")

    def publish(self, topic: str, message):
        """Publish message to topic"""
        if topic not in self.topics or not self.topics[topic]:
            print(f"No subscribers for topic '{topic}'")
            return

        print(f"Publishing to topic '{topic}': {message}")
        for subscriber_id, callback in self.topics[topic]:
            callback(subscriber_id, message)

    def get_subscribers(self, topic: str) -> int:
        """Get number of subscribers for topic"""
        return len(self.topics[topic])


class Subscriber:
    """Sample subscriber"""

    def __init__(self, name: str):
        self.name = name

    def on_message(self, subscriber_id: str, message):
        """Handle received message"""
        print(f"  [{self.name}] Received: {message}")


if __name__ == "__main__":
    pubsub = PubSubSystem()

    sub1 = Subscriber("Alice")
    sub2 = Subscriber("Bob")
    sub3 = Subscriber("Charlie")

    print("=== Subscriptions ===")
    pubsub.subscribe("news", "alice", sub1.on_message)
    pubsub.subscribe("news", "bob", sub2.on_message)
    pubsub.subscribe("sports", "bob", sub2.on_message)
    pubsub.subscribe("sports", "charlie", sub3.on_message)

    print("\n=== Publishing ===")
    pubsub.publish("news", "Breaking: Python 3.12 released")
    print()
    pubsub.publish("sports", "World Cup Finals Starting")

    print("\n=== Unsubscribe ===")
    pubsub.unsubscribe("news", "bob")
    pubsub.publish("news", "New framework announcement")