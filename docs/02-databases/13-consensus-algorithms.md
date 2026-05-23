# Consensus Algorithms — Raft, Paxos, and Byzantine Fault Tolerance

Achieving agreement in distributed systems despite failures.

---

## ⚖️ Consensus Algorithm Comparison

```
Algorithm    | Complexity | Fault Tolerance | Use Case
─────────────|────────────|─────────────────|──────────
Raft         | Medium     | N-1 failures    | Distributed databases
Paxos        | Hard       | N-1 failures    | Google systems
PBFT         | Very High  | N-3 failures    | Byzantine failures
PoW          | Very High  | 51% resistance  | Blockchain
```

---

## 🏗️ How Raft Works

```
Leader Election:
├─ All nodes start as Followers
├─ Election timeout triggers voting
├─ Candidate that gets majority wins
└─ Becomes Leader for term

Log Replication:
├─ Leader receives client requests
├─ Appends to log
├─ Sends to followers
├─ Waits for majority acknowledgment
└─ Then applies to state machine

Failure Handling:
├─ Leader fails: New election
├─ Followers catch up from leader
└─ Guarantees: Consistency, leadership
```

---

## 🧪 Practical Exercises

### Exercise: Implement Raft Node (Hard)

**Problem:**
Build consensus with leader election, log replication, and failure recovery

**Solution:**

```python
class RaftNode:
    def __init__(self, node_id, peers):
        self.node_id = node_id
        self.peers = peers
        self.state = 'FOLLOWER'  # Follower, Candidate, Leader
        self.term = 0
        self.voted_for = None
        self.log = []
        self.commit_index = 0
        self.election_timer = None
    
    def request_vote(self, candidate_term, candidate_id):
        if candidate_term > self.term:
            self.term = candidate_term
            self.voted_for = candidate_id
            return True
        return False
    
    def start_election(self):
        self.state = 'CANDIDATE'
        self.term += 1
        self.voted_for = self.node_id
        votes = 1  # Vote for self
        
        # Request votes from peers
        for peer in self.peers:
            if peer.request_vote(self.term, self.node_id):
                votes += 1
        
        # Did we win?
        if votes > len(self.peers) // 2:
            self.become_leader()
    
    def become_leader(self):
        self.state = 'LEADER'
        self.heartbeat_timer = set_timer(100)  # Send heartbeats
    
    def append_entries(self, leader_term, entries):
        if leader_term > self.term:
            self.term = leader_term
            self.state = 'FOLLOWER'
            self.log.extend(entries)
            return True
        return False
```

---

**Last updated:** 2026-05-22
