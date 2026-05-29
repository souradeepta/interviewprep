# Consensus Algorithm

**Level:** L3-L5+
**Time to read:** ~30 min

## Problem Statement

Distributed systems face the split-brain problem: if three database nodes lose contact with each other, each node might believe it is the only surviving node and start accepting writes. When the network heals, you have three conflicting versions of the data with no way to determine which is correct. This is catastrophic for systems that require a single consistent state.

Consensus algorithms ensure that a cluster of nodes agrees on a single value (or sequence of values) even in the presence of network partitions and node failures. The canonical applications are leader election (only one node is the primary), distributed log replication (all nodes have the same log), and configuration management (all nodes agree on the current cluster membership).

## Functional Requirements

- Elect exactly one leader among N nodes at any given time
- Replicate a log of commands to all nodes in the same order
- Tolerate up to F node failures without losing availability (requires N = 2F+1 nodes)
- Survive network partitions: minority partition must not accept writes
- Support configuration changes: add/remove nodes while the cluster remains available

## Non-Functional Requirements

- **Scale:** 3-9 nodes per cluster (consensus algorithms are not designed for hundreds of nodes)
- **Latency:** Leader election P99 < 2s; log replication P99 < 10ms per round-trip
- **Availability:** Tolerate F failures where N = 2F+1 (e.g., 3 nodes tolerates 1 failure)
- **Consistency:** Strong linearizable consistency — no stale reads if using leader reads

---

## Tier 1: L3-L4 Design (the basic interview answer)

### Back-of-Envelope

```
Cluster size and fault tolerance:
  - N=3: tolerates F=1 failure (quorum = 2/3)
  - N=5: tolerates F=2 failures (quorum = 3/5)
  - N=7: tolerates F=3 failures (quorum = 4/7)
  - General formula: F = (N-1)/2; quorum = N/2 + 1 (integer division)

Raft leader election timing:
  - Election timeout: random 150-300ms per node
  - Leader heartbeat interval: 50ms
  - If a follower doesn't hear from leader in [150-300ms]: starts election
  - Election: candidate sends RequestVote to all nodes
  - With 5 nodes, 1 WAN RTT of 50ms: election completes in 50ms + election_timeout
    = P99 election time: 300ms + 2 * 50ms = 400ms

Raft log replication throughput:
  - Leader receives command → appends to log → sends AppendEntries to all followers
  - Commit when quorum ACKs (N/2+1 nodes)
  - For N=3: commit when 1 follower ACKs (leader + 1 follower = quorum of 2)
  - LAN latency 1ms: throughput = 1,000 ops/sec per round-trip without pipelining
  - With pipelining (multiple in-flight AppendEntries): 100K+ ops/sec achievable

Snapshot size and compaction:
  - Without log compaction: log grows unboundedly (N years * 1M ops/day)
  - With snapshots: take state machine snapshot every 10K entries
    Snapshot size: depends on state machine (a key-value store: 1 GB snapshot)
    Time to install snapshot on a lagging follower: 1 GB / 1 Gbps = 8 seconds
```

### Architecture Diagram

```
Raft Cluster (N=5 nodes):

              +--------+
              | Node 1 |
              | LEADER |  <-- Accepts all writes; sends AppendEntries to followers
              +--------+
              /    |    \
             /     |     \
+--------+  /    Heartbeat  \  +--------+
| Node 2 |/       |          \| Node 5 |
|FOLLOWER|     +--------+     |FOLLOWER|
+--------+     | Node 3 |     +--------+
               |FOLLOWER|
               +--------+
               |
          +--------+
          | Node 4 |
          |FOLLOWER|
          +--------+

Leader Election (after Node 1 crashes):
1. Nodes 2,3,4,5 don't receive heartbeat for [150-300ms]
2. Node 3's random timer expires first (e.g., 163ms)
3. Node 3 increments term, becomes CANDIDATE, sends RequestVote
4. Nodes 2,4,5 grant vote (they haven't voted in this term)
5. Node 3 receives 3+ votes (quorum) → becomes new LEADER
6. Node 3 sends heartbeats; remaining nodes become FOLLOWERS
7. Node 1 recovers → receives heartbeat with higher term → becomes FOLLOWER

Log Replication:
Client
  |
  | Write command
  v
+--------+
| LEADER | 1. Appends entry to local log (term=5, index=42)
+--------+
  |   |
  |   | AppendEntries RPC (entries=[{term:5, index:42, cmd:...}])
  |   |
  v   v
Node2  Node3  (followers)
  |     |
  |     | ACK (follower log updated)
  |     |
  +-----+
  |
  v
LEADER: received quorum ACKs (2 of 4 followers = quorum of 3/5)
  → marks entry as COMMITTED
  → applies to state machine
  → responds to client with SUCCESS
  → next AppendEntries notifies followers of commit index
```

### Data Model

```
Raft node persistent state (must survive crashes):
  - current_term: int       // Monotonically increasing term number
  - voted_for: node_id|NULL // Candidate we voted for in current_term
  - log[]: []               // Ordered list of log entries

Log entry structure:
  - index: int              // Position in log (1-based)
  - term: int               // Leader's term when entry was created
  - command: bytes          // Opaque state machine command (e.g., "SET x=5")

Raft node volatile state (can be rebuilt on restart):
  - commit_index: int       // Highest log index known to be committed
  - last_applied: int       // Highest log index applied to state machine
  - next_index[peer]: int   // For leader: next log index to send to each follower
  - match_index[peer]: int  // For leader: highest log index known replicated to each follower

Raft RPCs:
  RequestVote(term, candidateId, lastLogIndex, lastLogTerm)
    → {term, voteGranted: bool}

  AppendEntries(term, leaderId, prevLogIndex, prevLogTerm, entries[], leaderCommit)
    → {term, success: bool}

  InstallSnapshot(term, leaderId, lastIncludedIndex, lastIncludedTerm, offset, data, done)
    → {term}

Paxos phases (for comparison):
  Phase 1a (Prepare): Proposer sends Prepare(n) to acceptors; n = ballot number
  Phase 1b (Promise): Acceptor responds with Promise(n, last_accepted_val)
  Phase 2a (Accept): Proposer sends Accept(n, value) to acceptors
  Phase 2b (Accepted): Acceptor responds Accepted(n, value); learner learns value
```

### API Design

```
# etcd-style consensus API (applications use this, not the Raft RPCs directly)

# Key-Value operations (state machine commands)
PUT /v3/kv/put
  Body: { key: "config/leader", value: "node-3", lease: 30 }
  Response: { revision: 42 }  (log index; all nodes agree on this sequence)

GET /v3/kv/range
  Body: { key: "config/leader" }
  Response: { kvs: [{ key, value, revision: 42, mod_revision: 42 }] }
  # Linearizable by default (always reads from leader)
  # Stale=true: may read from followers (lower latency, possibly stale)

DELETE /v3/kv/deleterange
  Body: { key: "config/leader" }

# Leader election (using leases)
POST /v3/lease/grant
  Body: { TTL: 30 }  # 30-second lease
  Response: { ID: 12345, TTL: 30 }

POST /v3/lease/keepalive
  Body: { ID: 12345 }  # Must be called before lease expires

# Watch (real-time notification on key changes)
POST /v3/watch
  Body: { key: "config/leader", watch_id: 1 }
  Response: stream of { events: [{ type: PUT|DELETE, kv: {...} }] }

# Cluster membership
GET /v3/cluster/member/list
  Response: { members: [{ ID, name, peerURLs, clientURLs, isLearner }] }
```

### Basic Scaling

- Use N=3 for most deployments: tolerates 1 failure, minimal overhead
- Use N=5 only when you need N=2 fault tolerance (e.g., multi-region deployments across 5 AZs)
- Never run consensus on the data plane — use it only for metadata (leader election, configuration, lock acquisition)
- Store state in the consensus cluster (etcd, ZooKeeper); run the actual data system (Redis, Kafka, your service) with leader elected by the consensus cluster

---

## Tier 2: L5+ Design (the staff interview answer)

### Capacity Planning (Real Numbers)

```
etcd cluster (typical Kubernetes control plane):
  - 3-node cluster: m5.xlarge each (4 vCPU, 16 GB RAM)
  - etcd data size: <8 GB recommended (etcd is not a general-purpose database)
  - Write throughput: etcd handles 10,000 writes/sec (sufficient for any reasonable metadata workload)
  - Read throughput: 100,000 reads/sec (cached on leader)
  - Cost: 3 * $0.192/hr = $0.576/hr = $415/month

Kafka leader election (ZooKeeper or KRaft):
  - ZooKeeper: 3-5 nodes, 8 GB RAM each (JVM overhead)
  - KRaft (built-in Raft since Kafka 3.3): no separate ZooKeeper needed
  - KRaft stores cluster metadata: broker configs, topic configs, partition assignments
  - 3 KRaft controller nodes (dedicated): m5.large each
  - Cost: 3 * $0.096/hr = $0.288/hr = $207/month (vs. ZooKeeper ~$1,000/month for larger clusters)

Leader lease optimization:
  - Standard Raft: every read must be confirmed with the leader (1 RTT per read)
  - Leader lease: leader holds a lease for 1-2 heartbeat periods (100-200ms)
    During the lease, reads are served locally without quorum confirmation
  - Improvement: read throughput increases from ~100K to ~1M reads/sec per leader
  - Safety: clocks must be synchronized within lease duration (use NTP/PTP, ±10ms)

Performance comparison (etcd/etcd-raft benchmark, 3-node, SSD, LAN):
  - Write throughput: 10K writes/sec (serialized through leader log)
  - Read throughput: 100K reads/sec (leader lease)
  - Latency (write): P50 = 2ms, P99 = 15ms
  - Latency (read):  P50 = 1ms, P99 = 5ms (with leader lease)
```

### Failure Modes

```
Failure: Leader fails during log replication (entries sent but not yet quorum-committed)
  Impact: In-flight log entries may or may not have been received by followers
  Resolution:
    - New leader elected; has the most up-to-date log (Raft's "election restriction":
      votes only granted to candidates with log as up-to-date as voter's)
    - New leader does NOT commit entries from previous terms directly
      (Raft requires a new entry in the current term to commit prior entries)
    - Uncommitted entries from old leader are either replicated to quorum by new leader
      or overwritten with the new leader's log (Raft log consistency guarantee)

Failure: Network partition creates two groups (e.g., nodes 1,2 | nodes 3,4,5 in 5-node cluster)
  Impact: One group has quorum (3/5), one doesn't (2/5)
  Resolution:
    - Minority partition (nodes 1,2): cannot elect a new leader (can't get 3 votes)
      → rejects writes with "no quorum" error; returns stale reads (or rejects linearizable reads)
    - Majority partition (nodes 3,4,5): elects a new leader, continues serving writes
    - When partition heals: minority nodes receive AppendEntries from new leader;
      if they have conflicting uncommitted entries, they are overwritten
    - Safety: no writes committed on the minority partition → no data loss, no split-brain

Failure: Clock skew causes leader lease to expire prematurely or too late
  Impact: Two nodes both believe they hold the leader lease simultaneously → split-brain reads
  Resolution:
    - Lease duration must be longer than maximum clock skew: lease = heartbeat_interval * 3
      With NTP (±50ms skew), set lease = 3 * 150ms = 450ms
    - With hardware clock (PTP, ±1ms skew): can use shorter lease = 3 * 50ms = 150ms
    - If clock synchronization cannot be guaranteed: don't use leader leases; use standard Raft reads
      (1 RTT confirmation per read — slower but always correct)

Failure: Log grows unboundedly (no snapshots taken)
  Impact: Node restart requires replaying entire log (could be millions of entries → minutes of downtime)
  Resolution:
    - Take state machine snapshots every K entries (e.g., K=10,000)
    - Snapshot = full copy of state machine at that log index
    - After snapshot: log entries before snapshot index can be discarded
    - For lagging follower (fell behind by >10K entries): leader sends InstallSnapshot RPC
      instead of AppendEntries — more efficient than replaying individual entries
```

### Consistency Boundaries

```
Raft guarantees:
  1. Leader completeness: the elected leader has all committed log entries
  2. Log matching: if two logs have the same index+term, all prior entries are identical
  3. State machine safety: if a server applies a log entry, no other server applies a
     different entry at the same index

Read models:
  - Linearizable reads (etcd default): every read reflects all writes acknowledged before the read
    Implementation: leader confirms it is still leader (reads log index) before serving read
    Latency: +1 RTT vs. stale read

  - Follower reads (stale): may return data up to replication lag behind
    Replication lag (LAN): typically <10ms; WAN: 50-200ms
    Use for: non-critical reads where slight staleness is acceptable (monitoring dashboards)
    Never use for: leader election results, lock status, critical configuration

  - "Quorum read" (used in Paxos): read from a quorum and take the most recent value
    More expensive than leader reads; not used in Raft (leader read is equivalent)

Paxos vs Raft vs ZAB:
  - Paxos (original): multi-decree Paxos is underspecified for practical implementation
    Each log slot is a separate Paxos instance → complex to implement correctly
  - Raft: designed to be understandable; leader-centric; strong separation of concerns
    (leader election, log replication, safety) → easier to implement correctly
  - ZAB (ZooKeeper Atomic Broadcast): similar to Raft but optimized for ZooKeeper's
    in-memory data model and watch notifications; primary-backup replication model
  - All three provide the same safety guarantees; differ in implementation complexity and performance

When to use each:
  - etcd (Raft): Kubernetes, service discovery, distributed locks
  - ZooKeeper (ZAB): Kafka metadata (legacy), HBase, Hadoop NameNode HA
  - CockroachDB/TiKV (Raft per-range): distributed SQL with per-shard consensus
  - Cassandra: Paxos for lightweight transactions (LWT) only; Gossip for membership
```

### Cost Model

```
etcd cluster (3 nodes, Kubernetes control plane):
  - 3 x m5.xlarge on-demand: $0.576/hr = $415/month
  - EBS gp3 (30 GB each): 3 * $2.40/month = $7.20/month
  - Total: ~$422/month for the consensus layer controlling a 1,000-node Kubernetes cluster

ZooKeeper (5 nodes, old Kafka deployment):
  - 5 x m5.large: $0.480/hr = $346/month
  - Total: ~$346/month + operational complexity

KRaft (3 Kafka controller nodes, replacing ZooKeeper):
  - 3 x m5.large: $0.288/hr = $207/month
  - Saves ~$140/month + eliminates ZooKeeper operational overhead
  - At 100+ Kafka clusters: $140 * 100 = $14,000/month savings by migrating to KRaft

Cost of consensus at scale (1,000-node distributed database):
  - Each range/shard requires a 3-node Raft group
  - CockroachDB with 1,000 shards: 1,000 * 3 = 3,000 Raft participants on ~100 nodes
  - The consensus overhead is multiplexed: each node participates in many Raft groups
    but the groups are independent → horizontal scaling without proportional overhead
  - Rule: keep consensus cluster small (3-9 nodes); use it for metadata only
    Never use a single Raft cluster for data storage at scale
```

---

## Trade-off Comparison

| Algorithm      | Understandability | Performance           | Fault Tolerance            | Production Use Cases          |
|----------------|-------------------|-----------------------|----------------------------|-------------------------------|
| Raft           | High              | High (10K writes/sec) | F=(N-1)/2 crash failures   | etcd, CockroachDB, TiKV, Consul |
| Paxos          | Low               | High (when implemented)| Same as Raft              | Google Chubby, Spanner        |
| ZAB            | Medium            | High                  | F=(N-1)/2                  | ZooKeeper, Kafka (legacy)      |
| Multi-Paxos    | Medium            | Very high (pipelining)| Same as Paxos              | Google Spanner (underlying)   |
| Viewstamped Replication | Medium  | High                  | F=(N-1)/2                  | TAPIR, academic systems        |
| Byzantine BFT  | Low               | Low (3N+1 nodes)      | Byzantine (malicious nodes)| Blockchain systems             |

## Follow-up Questions (escalating difficulty, 7 minimum)

1. **(L3)** What is the split-brain problem and why do consensus algorithms solve it?
   → Split-brain occurs when a network partition causes multiple nodes to believe they are the sole leader, each accepting writes independently. When the partition heals, you have two divergent versions of the data with no way to merge them correctly (e.g., both nodes processed a conflicting write to the same key). Consensus algorithms prevent split-brain by requiring a quorum (majority) of nodes to acknowledge any write before it is committed. A minority partition has fewer than quorum nodes and cannot commit writes — it simply stops accepting writes until connectivity is restored.

2. **(L3)** What is the quorum formula for a Raft cluster and why must it be a majority?
   → Quorum = floor(N/2) + 1 (majority). For N=3: quorum=2. For N=5: quorum=3. The majority requirement guarantees that any two quorums share at least one node — so the new leader's quorum always overlaps with the old leader's commit quorum. This overlap node has the committed entries, which the new leader can discover. If quorum were a minority (N/3), two non-overlapping quorums could exist, and the new leader might not have all committed entries, violating safety.

3. **(L3)** What is the difference between Paxos and Raft?
   → Both achieve the same safety guarantees. Paxos (original) is underspecified — it describes how to agree on a single value but leaves multi-value log replication, leader election, and membership changes to the implementer. This made it notoriously hard to implement correctly. Raft was designed to be understandable: it has a clear leader, a structured leader election protocol, and explicit safety rules for log consistency. Most modern systems (etcd, CockroachDB, Consul) use Raft because it is easier to implement correctly.

4. **(L4)** Explain Raft's log replication in detail. When does a log entry become committed?
   → The leader receives a client command, appends it to its log with the current term, and sends AppendEntries RPCs to all followers concurrently. Each follower appends the entry to its log and responds with success. When the leader receives success from a quorum (N/2+1 nodes, including itself), the entry is marked as committed. The leader applies the entry to its state machine, responds to the client, and notifies followers of the commit index in subsequent AppendEntries calls. Followers apply committed entries to their own state machines. Key safety: only entries from the CURRENT term can be directly committed. Entries from prior terms become committed implicitly when a current-term entry is committed after them in the log.

5. **(L5)** What is a leader lease and what are its risks?
   → By default, Raft reads require the leader to confirm quorum is still active (1 extra RTT). A leader lease allows the leader to serve reads locally without quorum confirmation: the leader holds a lease for a bounded time (e.g., 150ms); followers won't vote for a new leader until the lease expires. This makes reads faster (no RTT) but requires clocks to be synchronized within the lease duration. If a follower's clock is significantly ahead (e.g., by 200ms), it might grant a new leader before the old leader's lease expires, allowing two leaders to both believe they hold the lease simultaneously. Risk: if NTP is unreliable or nodes have high clock drift (>50ms), leader leases can cause stale reads. etcd uses leader leases with bounded clock drift assumptions (requires operator to configure correct lease duration relative to measured clock skew).

6. **(L5)** How does log compaction (snapshotting) work in Raft and why is it necessary?
   → Without compaction, the log grows forever. A new node joining or a crashed node recovering must replay every log entry since the beginning — for a long-lived cluster, this could take hours. Snapshotting: when the log reaches K entries (e.g., K=10,000), the leader takes a snapshot of the current state machine state and records the log index and term at the snapshot point. All log entries before the snapshot can be discarded. For a follower that is significantly behind (its last log index is before the snapshot), the leader sends an InstallSnapshot RPC with the complete state machine snapshot. The follower discards its log, loads the snapshot, and continues receiving AppendEntries from the current log position. Snapshot size and transfer time determine how long a recovering node is unavailable.

7. **(L5+)** How does etcd handle membership changes (adding or removing a node) without downtime?
   → Raft joint consensus handles membership changes: the cluster transitions through a joint configuration where both old and new configurations must each form a quorum for any write to commit. Example: removing node 5 from a 5-node cluster. During the transition, a write requires quorum from BOTH the old config (3/5) AND the new config (2/4). This prevents any window where two disjoint majorities from old and new configs could both commit — which would cause split-brain. The transition proceeds: leader appends the joint-config entry (must be committed under joint consensus), then appends the new-config entry (committed under new consensus). Once new-config is committed, the removed node is told to step down and stops receiving messages. etcd v3 uses a simplified single-step membership change that is safe for one node at a time (adding 1, removing 1) — the single-step approach is simpler to implement and sufficient for most operational needs.

## Anti-patterns / Things NOT to Say

- **"Consensus is needed for every read — always route to the leader"** — Routing every read through the leader is correct for linearizability but creates a bottleneck at scale. Use leader leases for local reads, follower reads for non-critical queries (monitoring, analytics), and reserve leader reads only for operations that require the most recent committed value. The distinction between read models is important at the L5+ level.
- **"Use a 2-node cluster for cost savings"** — A 2-node cluster provides no fault tolerance. With 2 nodes, quorum = 2/2 = both nodes. If either node fails, the cluster loses quorum and stops accepting writes — worse than a single node. Always use N=3 as the minimum: tolerates 1 failure, quorum = 2/3. A 2-node cluster is strictly worse than a 1-node system in the failure case.
- **"etcd can store terabytes of data"** — etcd is a consensus-backed key-value store optimized for metadata (cluster configuration, leader election, distributed locks), not data storage. The etcd documentation recommends keeping the database below 8 GB. Using etcd as a general-purpose database will degrade Raft performance (snapshot install time is proportional to state size) and is architecturally wrong. Use etcd for coordination; use a separate data system for application data.
- **"Run consensus on the hot data path"** — Consensus (Raft, Paxos) adds 1+ RTT of latency to every write. For a cache or message queue handling 100K writes/sec, routing every write through consensus is not practical. Use consensus for metadata operations (leader election, configuration, lock acquisition) that happen infrequently. For high-throughput data replication, use asynchronous replication with eventual consistency and separate consensus-based leader election to designate which node is primary.
- **"Byzantine fault tolerance is just stronger than crash fault tolerance"** — BFT (Byzantine Fault Tolerant) consensus tolerates malicious nodes that send arbitrary or conflicting messages. It requires 3F+1 nodes to tolerate F Byzantine failures, vs. 2F+1 for crash-only Raft/Paxos. BFT is used in blockchain and adversarial settings where you don't trust all nodes. In a datacenter where you control all nodes, crash fault tolerance is sufficient and far more efficient. Saying "use PBFT for our database" in a typical interview context shows a misunderstanding of the threat model.

## Python Implementation (sketch)

```python
import random
import time
import threading
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict

class NodeState(Enum):
    FOLLOWER  = "FOLLOWER"
    CANDIDATE = "CANDIDATE"
    LEADER    = "LEADER"

@dataclass
class LogEntry:
    index: int
    term: int
    command: str

@dataclass
class RaftNode:
    node_id: int
    peers: List[int]            # IDs of other nodes in cluster

    # Persistent state (survives restart)
    current_term: int = 0
    voted_for: Optional[int] = None
    log: List[LogEntry] = field(default_factory=list)

    # Volatile state
    state: NodeState = NodeState.FOLLOWER
    commit_index: int = 0
    last_applied: int = 0
    votes_received: int = 0

    # Leader volatile state
    next_index: Dict[int, int] = field(default_factory=dict)
    match_index: Dict[int, int] = field(default_factory=dict)

    # Timing
    last_heartbeat: float = field(default_factory=time.monotonic)
    election_timeout: float = field(default_factory=lambda: random.uniform(0.150, 0.300))

    _lock: threading.Lock = field(default_factory=threading.Lock)

    def quorum(self) -> int:
        return (len(self.peers) + 1) // 2 + 1  # Majority including self

    def start_election(self):
        """Called when election timeout fires. Become candidate, start election."""
        with self._lock:
            self.state = NodeState.CANDIDATE
            self.current_term += 1
            self.voted_for = self.node_id  # Vote for self
            self.votes_received = 1        # Count self-vote
            print(f"[Node {self.node_id}] Starting election for term {self.current_term}")

        last_log_index = len(self.log)
        last_log_term = self.log[-1].term if self.log else 0

        for peer in self.peers:
            self._send_request_vote(peer, self.current_term, last_log_index, last_log_term)

    def receive_request_vote(self, term: int, candidate_id: int,
                             last_log_index: int, last_log_term: int) -> dict:
        """Handle RequestVote RPC from a candidate."""
        with self._lock:
            if term < self.current_term:
                return {"term": self.current_term, "vote_granted": False}

            if term > self.current_term:
                self.current_term = term
                self.state = NodeState.FOLLOWER
                self.voted_for = None

            # Vote if: haven't voted this term AND candidate's log is at least as up-to-date
            my_last_term = self.log[-1].term if self.log else 0
            my_last_index = len(self.log)
            log_ok = (last_log_term > my_last_term or
                      (last_log_term == my_last_term and last_log_index >= my_last_index))

            if (self.voted_for is None or self.voted_for == candidate_id) and log_ok:
                self.voted_for = candidate_id
                self.last_heartbeat = time.monotonic()
                return {"term": self.current_term, "vote_granted": True}

            return {"term": self.current_term, "vote_granted": False}

    def receive_append_entries(self, term: int, leader_id: int,
                               prev_log_index: int, prev_log_term: int,
                               entries: List[LogEntry], leader_commit: int) -> dict:
        """Handle AppendEntries RPC (heartbeat or log replication) from leader."""
        with self._lock:
            if term < self.current_term:
                return {"term": self.current_term, "success": False}

            self.state = NodeState.FOLLOWER
            self.current_term = term
            self.last_heartbeat = time.monotonic()

            # Log consistency check
            if prev_log_index > 0:
                if len(self.log) < prev_log_index:
                    return {"term": self.current_term, "success": False}
                if self.log[prev_log_index - 1].term != prev_log_term:
                    # Truncate conflicting entries
                    self.log = self.log[:prev_log_index - 1]
                    return {"term": self.current_term, "success": False}

            # Append new entries
            for i, entry in enumerate(entries):
                pos = prev_log_index + i
                if pos < len(self.log):
                    if self.log[pos].term != entry.term:
                        self.log = self.log[:pos]  # Delete conflicting + following entries
                        self.log.append(entry)
                else:
                    self.log.append(entry)

            # Update commit index
            if leader_commit > self.commit_index:
                self.commit_index = min(leader_commit, len(self.log))
                self._apply_committed_entries()

            return {"term": self.current_term, "success": True}

    def _apply_committed_entries(self):
        """Apply committed log entries to state machine (called with lock held)."""
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            entry = self.log[self.last_applied - 1]
            self._apply_to_state_machine(entry.command)

    def _apply_to_state_machine(self, command: str):
        print(f"[Node {self.node_id}] Apply: {command}")

    def _send_request_vote(self, peer_id, term, last_log_index, last_log_term):
        pass  # Network I/O stub: real impl uses gRPC or HTTP

    def check_election_timeout(self):
        """Call periodically from a background thread on follower/candidate nodes."""
        if (self.state != NodeState.LEADER and
                time.monotonic() - self.last_heartbeat > self.election_timeout):
            self.start_election()
```
