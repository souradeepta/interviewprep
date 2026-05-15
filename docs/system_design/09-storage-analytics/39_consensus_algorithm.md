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


## Architecture Diagram

```
┌──────────────────────────────────────┐
│   Distributed Consensus (Raft)       │
│  ┌──────────────────────────────────┐  │
│  │ Leader Election                  │
│  │ - Followers vote for leader      │  │
│  │ - Majority wins                  │  │
│  │ Log Replication                  │  │
│  │ - Leader appends entries         │  │
│  │ - Followers replicate            │  │
│  │ Safety                           │  │
│  │ - Majority ack = committed       │  │
│  └──────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## Common Questions & Answers

**Q: Leader election timeout tuning?** A: Too short: election flaps. Too long: recovery slow. Typical: 150-300ms.

**Q: Partition tolerance—split brain?** A: Minority partition can't elect leader (needs majority). Minority read-only until merge.

**Q: Log compaction?** A: Snapshot at intervals, discard old log. Speeds up recovery.

**Q: Performance impact?** A: Write latency = wait for majority replication (synchronous). Read faster (leader only). Throughput limited by leader.

## Back-of-Envelope Calculations

ZooKeeper: 5-node cluster, 1000 txn/sec. Election: 150-300ms. Replication: 10-20ms per node × 3 = 30-60ms total latency impact.

## Design Choice Comparison

| Approach | Pros | Cons |
|----------|------|------|
| Raft | Simple, understandable | Slower writes |
| Paxos | More complex, faster | Harder to implement |
| Eventual consistency | Fast, no consensus | Inconsistent state possible |

## Follow-up Interview Questions

1. Add node to cluster dynamically? 2. Remove node safely (no data loss)? 3. Cross-datacenter replication? 4. Linearizability guarantee? 5. Performance at 1000s of nodes?

## Example Scenario Walkthrough

[Describe a concrete example with step-by-step execution]

## Complexity

| Operation | Time |
|-----------|------|
| Normal case | O(log n) |
| Leader failure | O(election timeout) |
| Network partition | Blocked |
