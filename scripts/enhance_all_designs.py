#!/usr/bin/env python3
"""
Comprehensive enhancement of all system design docs with implementations and diagrams.
"""

import os
import re
import glob

base_path = "/home/sbisw/github/datastructures/docs/system_design"

# Concept-specific implementations
concept_implementations = {
    "auction_system": {
        "python": """```python
from dataclasses import dataclass
from enum import Enum
import time
from typing import Optional

class AuctionStatus(Enum):
    OPEN = "open"
    ACTIVE = "active"
    CLOSED = "closed"
    SETTLED = "settled"

@dataclass
class Bid:
    user_id: int
    amount: float
    timestamp: float

class AuctionSystem:
    def __init__(self):
        self.auctions = {}
        self.bids = {}

    def create_auction(self, auction_id: int, item: str, start_price: float, duration: int):
        self.auctions[auction_id] = {
            'item': item,
            'start_price': start_price,
            'end_time': time.time() + duration,
            'status': AuctionStatus.OPEN,
            'highest_bid': start_price,
            'highest_bidder': None
        }
        self.bids[auction_id] = []

    def place_bid(self, auction_id: int, user_id: int, amount: float) -> bool:
        if auction_id not in self.auctions:
            return False

        auction = self.auctions[auction_id]
        if time.time() > auction['end_time']:
            return False

        if amount <= auction['highest_bid']:
            return False

        auction['highest_bid'] = amount
        auction['highest_bidder'] = user_id
        self.bids[auction_id].append(Bid(user_id, amount, time.time()))
        return True

    def finalize_auction(self, auction_id: int) -> Optional[dict]:
        if auction_id not in self.auctions:
            return None

        auction = self.auctions[auction_id]
        if auction['highest_bidder']:
            auction['status'] = AuctionStatus.SETTLED
            return {
                'winner': auction['highest_bidder'],
                'amount': auction['highest_bid']
            }
        return None
```""",
        "java": """```java
import java.util.*;

class AuctionSystem {
    enum AuctionStatus { OPEN, ACTIVE, CLOSED, SETTLED }

    static class Bid {
        int userId;
        double amount;
        long timestamp;

        Bid(int userId, double amount, long timestamp) {
            this.userId = userId;
            this.amount = amount;
            this.timestamp = timestamp;
        }
    }

    static class Auction {
        String item;
        double highestBid;
        int highestBidder;
        long endTime;
        AuctionStatus status;
        List<Bid> bids = new ArrayList<>();
    }

    private Map<Integer, Auction> auctions = new HashMap<>();

    public void createAuction(int id, String item, double startPrice, long duration) {
        Auction a = new Auction();
        a.item = item;
        a.highestBid = startPrice;
        a.highestBidder = -1;
        a.endTime = System.currentTimeMillis() + duration;
        a.status = AuctionStatus.OPEN;
        auctions.put(id, a);
    }

    public boolean placeBid(int auctionId, int userId, double amount) {
        Auction a = auctions.get(auctionId);
        if (a == null || System.currentTimeMillis() > a.endTime) return false;
        if (amount <= a.highestBid) return false;

        a.highestBid = amount;
        a.highestBidder = userId;
        a.bids.add(new Bid(userId, amount, System.currentTimeMillis()));
        return true;
    }

    public Map<String, Object> finalizeAuction(int auctionId) {
        Auction a = auctions.get(auctionId);
        if (a == null) return null;

        a.status = AuctionStatus.SETTLED;
        Map<String, Object> result = new HashMap<>();
        result.put("winner", a.highestBidder);
        result.put("amount", a.highestBid);
        return result;
    }
}
```"""
    },
    "payment_system": {
        "python": """```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class TransactionStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"

@dataclass
class Transaction:
    id: str
    user_id: int
    amount: float
    status: TransactionStatus
    timestamp: float

class PaymentGateway:
    def __init__(self):
        self.transactions = {}
        self.balances = {}

    def deposit(self, user_id: int, amount: float) -> bool:
        if user_id not in self.balances:
            self.balances[user_id] = 0
        self.balances[user_id] += amount
        return True

    def process_payment(self, user_id: int, recipient_id: int, amount: float) -> Optional[str]:
        if self.balances.get(user_id, 0) < amount:
            return None  # Insufficient funds

        txn_id = str(hash(f"{user_id}{recipient_id}{amount}"))
        txn = Transaction(txn_id, user_id, amount,
                         TransactionStatus.PENDING, __import__('time').time())

        self.balances[user_id] -= amount
        self.balances[recipient_id] = self.balances.get(recipient_id, 0) + amount
        txn.status = TransactionStatus.SUCCESS
        self.transactions[txn_id] = txn
        return txn_id

    def refund(self, txn_id: str) -> bool:
        if txn_id not in self.transactions:
            return False

        txn = self.transactions[txn_id]
        self.balances[txn.user_id] += txn.amount
        txn.status = TransactionStatus.REFUNDED
        return True
```""",
        "java": """```java
import java.util.*;

class PaymentGateway {
    enum TransactionStatus { PENDING, SUCCESS, FAILED, REFUNDED }

    static class Transaction {
        String id;
        int userId;
        double amount;
        TransactionStatus status;
        long timestamp;

        Transaction(String id, int userId, double amount) {
            this.id = id;
            this.userId = userId;
            this.amount = amount;
            this.status = TransactionStatus.PENDING;
            this.timestamp = System.currentTimeMillis();
        }
    }

    private Map<Integer, Double> balances = new HashMap<>();
    private Map<String, Transaction> transactions = new HashMap<>();

    public void deposit(int userId, double amount) {
        balances.put(userId, balances.getOrDefault(userId, 0.0) + amount);
    }

    public String processPayment(int userId, int recipientId, double amount) {
        if (balances.getOrDefault(userId, 0.0) < amount) {
            return null;
        }

        String txnId = UUID.randomUUID().toString();
        Transaction txn = new Transaction(txnId, userId, amount);

        balances.put(userId, balances.get(userId) - amount);
        balances.put(recipientId, balances.getOrDefault(recipientId, 0.0) + amount);
        txn.status = TransactionStatus.SUCCESS;
        transactions.put(txnId, txn);
        return txnId;
    }

    public boolean refund(String txnId) {
        Transaction txn = transactions.get(txnId);
        if (txn == null) return false;

        balances.put(txn.userId, balances.getOrDefault(txn.userId, 0.0) + txn.amount);
        txn.status = TransactionStatus.REFUNDED;
        return true;
    }
}
```"""
    },
    "leaderboard": {
        "python": """```python
from dataclasses import dataclass
from typing import List

@dataclass
class ScoreEntry:
    user_id: int
    score: int
    timestamp: float

class Leaderboard:
    def __init__(self):
        self.scores = {}  # user_id -> score

    def update_score(self, user_id: int, score: int):
        self.scores[user_id] = max(self.scores.get(user_id, 0), score)

    def get_rank(self, user_id: int) -> int:
        if user_id not in self.scores:
            return -1
        rank = 1
        for uid, score in self.scores.items():
            if score > self.scores[user_id]:
                rank += 1
        return rank

    def get_top_k(self, k: int) -> List[tuple]:
        sorted_scores = sorted(self.scores.items(),
                              key=lambda x: x[1], reverse=True)
        return sorted_scores[:k]

    def get_range(self, start_rank: int, end_rank: int) -> List[tuple]:
        sorted_scores = sorted(self.scores.items(),
                              key=lambda x: x[1], reverse=True)
        return sorted_scores[start_rank-1:end_rank]
```""",
        "java": """```java
import java.util.*;

class Leaderboard {
    static class ScoreEntry implements Comparable<ScoreEntry> {
        int userId;
        int score;

        ScoreEntry(int userId, int score) {
            this.userId = userId;
            this.score = score;
        }

        public int compareTo(ScoreEntry other) {
            return Integer.compare(other.score, this.score);
        }
    }

    private Map<Integer, Integer> scores = new HashMap<>();

    public void updateScore(int userId, int score) {
        scores.put(userId, Math.max(scores.getOrDefault(userId, 0), score));
    }

    public int getRank(int userId) {
        if (!scores.containsKey(userId)) return -1;
        int rank = 1;
        int userScore = scores.get(userId);
        for (int score : scores.values()) {
            if (score > userScore) rank++;
        }
        return rank;
    }

    public List<ScoreEntry> getTopK(int k) {
        List<ScoreEntry> entries = new ArrayList<>();
        scores.forEach((uid, score) -> entries.add(new ScoreEntry(uid, score)));
        Collections.sort(entries);
        return entries.subList(0, Math.min(k, entries.size()));
    }
}
```"""
    },
    "notification_system": {
        "python": """```python
from dataclasses import dataclass
from typing import List, Set
from enum import Enum

class NotificationType(Enum):
    LIKE = "like"
    COMMENT = "comment"
    FOLLOW = "follow"
    MESSAGE = "message"

@dataclass
class Notification:
    id: str
    user_id: int
    actor_id: int
    type: NotificationType
    content: str
    read: bool
    timestamp: float

class NotificationSystem:
    def __init__(self):
        self.notifications = {}  # user_id -> [Notification]
        self.subscriptions = {}  # user_id -> Set of subscribed users

    def subscribe(self, follower_id: int, user_id: int):
        if follower_id not in self.subscriptions:
            self.subscriptions[follower_id] = set()
        self.subscriptions[follower_id].add(user_id)

    def send_notification(self, user_id: int, actor_id: int,
                         notif_type: NotificationType, content: str):
        if user_id not in self.notifications:
            self.notifications[user_id] = []

        notif = Notification(
            str(hash(f"{user_id}{actor_id}{notif_type}")),
            user_id, actor_id, notif_type, content, False,
            __import__('time').time()
        )
        self.notifications[user_id].append(notif)

    def get_notifications(self, user_id: int, limit: int = 10) -> List[Notification]:
        return self.notifications.get(user_id, [])[-limit:]

    def mark_as_read(self, user_id: int, notif_id: str) -> bool:
        for notif in self.notifications.get(user_id, []):
            if notif.id == notif_id:
                notif.read = True
                return True
        return False
```""",
        "java": """```java
import java.util.*;

class NotificationSystem {
    enum NotificationType { LIKE, COMMENT, FOLLOW, MESSAGE }

    static class Notification {
        String id;
        int userId;
        int actorId;
        NotificationType type;
        String content;
        boolean read;
        long timestamp;

        Notification(String id, int userId, int actorId,
                    NotificationType type, String content) {
            this.id = id;
            this.userId = userId;
            this.actorId = actorId;
            this.type = type;
            this.content = content;
            this.read = false;
            this.timestamp = System.currentTimeMillis();
        }
    }

    private Map<Integer, List<Notification>> notifications = new HashMap<>();
    private Map<Integer, Set<Integer>> subscriptions = new HashMap<>();

    public void subscribe(int followerId, int userId) {
        subscriptions.computeIfAbsent(followerId, k -> new HashSet<>())
                    .add(userId);
    }

    public void sendNotification(int userId, int actorId,
                                NotificationType type, String content) {
        notifications.computeIfAbsent(userId, k -> new ArrayList<>())
                    .add(new Notification(UUID.randomUUID().toString(),
                                         userId, actorId, type, content));
    }

    public List<Notification> getNotifications(int userId, int limit) {
        List<Notification> list = notifications.getOrDefault(userId,
                                                            new ArrayList<>());
        return list.subList(Math.max(0, list.size() - limit), list.size());
    }

    public boolean markAsRead(int userId, String notifId) {
        for (Notification n : notifications.getOrDefault(userId,
                                                        new ArrayList<>())) {
            if (n.id.equals(notifId)) {
                n.read = true;
                return true;
            }
        }
        return false;
    }
}
```"""
    }
}

def find_implementation_section(content):
    """Find the Implementation section in markdown."""
    match = re.search(r'## Implementation.*?(?=\n## |\Z)', content, re.DOTALL)
    return match

def update_implementations(filepath):
    """Update implementation sections with real code."""
    filename = os.path.basename(filepath).lower()

    for concept, impl in concept_implementations.items():
        if concept in filename:
            with open(filepath, 'r') as f:
                content = f.read()

            # Replace placeholder implementations
            content = re.sub(
                r'```python\n# Working implementation[^\n]*\n[^`]*```',
                impl['python'],
                content
            )

            content = re.sub(
                r'```java\n// Object-oriented implementation[^\n]*\n[^`]*```',
                impl['java'],
                content
            )

            with open(filepath, 'w') as f:
                f.write(content)

            return True

    return False

def add_uml_diagrams(filepath):
    """Add UML diagrams to files."""
    filename = os.path.basename(filepath).lower()

    uml_map = {
        "auction": """## UML Diagram

```
┌────────────────────────┐
│      Auction           │
├────────────────────────┤
│- id: int               │
│- status: AuctionStatus │
│- highestBid: double    │
│- endTime: long         │
├────────────────────────┤
│+ placeBid(bid)         │
│+ finalize(): Winner     │
└────────────────────────┘
         △
         │ contains
         │
┌────────────────────────┐
│        Bid             │
├────────────────────────┤
│- userId: int           │
│- amount: double        │
│- timestamp: long       │
└────────────────────────┘
```""",
        "payment": """## UML Diagram

```
┌────────────────────────┐
│   PaymentGateway       │
├────────────────────────┤
│- transactions: Map     │
│- balances: Map         │
├────────────────────────┤
│+ processPayment()      │
│+ refund()              │
│+ getBalance()          │
└────────────────────────┘
         │
         │ creates
         ↓
┌────────────────────────┐
│    Transaction         │
├────────────────────────┤
│- id: String            │
│- amount: double        │
│- status: TxnStatus     │
│- timestamp: long       │
└────────────────────────┘
```""",
        "leaderboard": """## UML Diagram

```
┌────────────────────────┐
│    Leaderboard         │
├────────────────────────┤
│- scores: Map           │
├────────────────────────┤
│+ updateScore()         │
│+ getRank()             │
│+ getTopK()             │
│+ getRange()            │
└────────────────────────┘
         │
         │ tracks
         ↓
┌────────────────────────┐
│   ScoreEntry           │
├────────────────────────┤
│- userId: int           │
│- score: int            │
│- timestamp: long       │
└────────────────────────┘
```"""
    }

    for key, diagram in uml_map.items():
        if key in filename:
            with open(filepath, 'r') as f:
                content = f.read()

            if diagram not in content and "## Implementation" in content:
                content = content.replace("## Implementation",
                                        diagram + "\n\n## Implementation")
                with open(filepath, 'w') as f:
                    f.write(content)
            return True

    return False

# Process all files
updated_impl = 0
updated_uml = 0

for filepath in glob.glob(f"{base_path}/*/*_*.md"):
    if update_implementations(filepath):
        updated_impl += 1
        print(f"✓ Implementation: {os.path.basename(filepath)}")

    if add_uml_diagrams(filepath):
        updated_uml += 1
        print(f"✓ UML Diagram: {os.path.basename(filepath)}")

print(f"\n✅ Updated {updated_impl} files with implementations")
print(f"✅ Added UML diagrams to {updated_uml} files")
