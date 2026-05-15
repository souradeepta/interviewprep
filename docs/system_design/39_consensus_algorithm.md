# Consensus Algorithm (Raft/Paxos)

## Problem Statement
Design a consensus algorithm for distributed systems to agree on state.

**Requirements:**
- Agreement: All nodes decide same value
- Liveness: Eventually make decision
- Safety: No two values decided
- Fault tolerance: Work with failures

## Design

### Raft Algorithm

```
Leader election: Timeout-based voting
Log replication: Leader sends to followers
Commitment: Majority replication
Safety: No data loss
```

### State Transitions

```
Follower → Candidate: Timeout
Candidate → Leader: Win election (majority votes)
Leader → Follower: Newer term seen
```

### Log Entry States

```
Replicated: On majority of servers
Committed: Leader commits, followers apply
Applied: State machine executes
```

### Handling Failures

```
Leader failure: Election elects new leader
Network partition: Minority can't decide
Log divergence: Force follower logs to match
```

## Complexity

| Operation | Time |
|-----------|------|
| Normal case | O(log n) |
| Leader failure | O(election timeout) |
| Network partition | Blocked |
