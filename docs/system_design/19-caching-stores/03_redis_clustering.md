# Redis Clustering

## Problem Statement

Design a horizontally scalable Redis cluster that distributes data across multiple nodes using consistent hashing, handles node failures automatically, and enables transparent client routing.

## Architecture Diagram

```mermaid
graph TB
    subgraph Cluster["Redis Cluster (6 nodes)"]
        subgraph Shard0["Shard 0 (slots 0-5460)"]
            M0["Master 0\n192.168.1.10"]
            S0["Slave 0\n192.168.1.11"]
        end
        subgraph Shard1["Shard 1 (slots 5461-10922)"]
            M1["Master 1\n192.168.1.12"]
            S1["Slave 1\n192.168.1.13"]
        end
        subgraph Shard2["Shard 2 (slots 10923-16383)"]
            M2["Master 2\n192.168.1.14"]
            S2["Slave 2\n192.168.1.15"]
        end
    end

    Client -->|CLUSTER SLOTS| M0
    M0 -.->|replicate| S0
    M1 -.->|replicate| S1
    M2 -.->|replicate| S2
    M0 <-->|gossip| M1
    M1 <-->|gossip| M2
    M0 <-->|gossip| M2
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Client (smart)
    participant M0 as Master 0 (slots 0-5460)
    participant M1 as Master 1 (slots 5461-10922)

    C->>M0: GET user:1234
    Note over M0: CRC16("user:1234") % 16384 = 7531
    Note over M0: Slot 7531 NOT owned by me
    M0-->>C: MOVED 7531 192.168.1.12:6379
    C->>M1: GET user:1234 (retry to correct node)
    M1-->>C: "alice"

    Note over C: Smart client caches slot map
    C->>M1: GET user:5678 (direct, no MOVED)
    M1-->>C: "bob"
```

## Design

### Hash Slots

```
Redis Cluster divides key space into 16384 slots:
  slot = CRC16(key) % 16384

3 masters -> each owns ~5461 slots:
  Master 0: slots 0-5460
  Master 1: slots 5461-10922
  Master 2: slots 10923-16383

Hash tags:
  {user}.profile, {user}.sessions -> same slot
  CRC16 only hashes the content in {}
  Use for multi-key operations on same node

MGET across nodes: NOT supported
  Use pipelining with hash tags, or single-node operations
  Or: Lua scripts (EVAL) run on single node

Key -> slot calculation:
  "user:1234" -> CRC16 = 7531 -> Master 1
  "{user:1234}.profile" -> same as "{user:1234}" -> same slot
```

### Cluster Topology & Gossip

```
Gossip protocol:
  Each node knows about all other nodes
  Periodically exchange cluster state (PING/PONG)
  Failure detection: node marks peer as PFAIL (possible fail)
  Quorum: majority mark as PFAIL -> FAIL (confirmed)

Failover:
  Master fails -> slaves vote for promotion
  Replica with highest replication offset elected
  New master takes over all slots
  Cluster updates routing table
  
  Timeline:
    Detection: 30s (node_timeout default)
    Election: 1-2s
    Total: ~32s unavailability per shard

node_timeout: critical parameter
  Too low: false positives (network blip)
  Too high: long outage during real failure
  Recommended: 15-30s
```

### Resharding

```
Add new node:
  redis-cli --cluster add-node new_ip:6379 existing_ip:6379
  redis-cli --cluster rebalance existing_ip:6379

Slot migration:
  CLUSTER SETSLOT <slot> MIGRATING <dst>  (src)
  CLUSTER SETSLOT <slot> IMPORTING <src>  (dst)
  MIGRATE host port key db timeout
  CLUSTER SETSLOT <slot> NODE <dst-nodeid>

During migration:
  Keys being moved: client gets ASK redirect (temporary)
  ASK vs MOVED: MOVED = permanent new location, ASK = try here for this request
```

## Common Questions & Answers

**Q: Why 16384 slots (not a power of 2 like 16384 = 2^14)?** A: 16384 slots fit in 2KB gossip messages (16384 bits = 2048 bytes). Large enough to rebalance without significant per-slot overhead. Trade-off between granularity and message size.

**Q: What is the difference between MOVED and ASK redirects?** A: MOVED: key permanently belongs to another node — update slot map, always go there. ASK: key temporarily migrating — try there for this one request only, don't update slot map. ASK is transient during resharding.

**Q: What operations don't work across cluster nodes?** A: Multi-key commands (MGET, MSET, SUNION) require all keys on same slot. Transactions (MULTI/EXEC) only work within a single slot. Pub/Sub: messages only reach subscribers on same shard (use a separate Redis instance for pub/sub).

**Q: How does Redis Cluster handle split-brain?** A: Nodes require quorum (>N/2 masters reachable) to continue serving writes. If a partition isolates minority masters: they stop accepting writes. Prevents split-brain writes. Minority partition stays in read-only mode.

**Q: How many replicas should each master have?** A: Minimum 1 replica per master. For critical data: 2 replicas. With 1 replica: can lose 1 master per shard without data loss. Cluster minimum: 3 masters + 3 replicas = 6 nodes.

## Back-of-Envelope Calculations

```
Cluster capacity:
  3 masters x 32GB RAM each = 96GB total
  With 1 replica each: 96GB usable (replicas don't add capacity)
  Per key overhead ~60B: 96GB / 60B = ~1.6B keys

Write throughput:
  1 master: ~500K ops/s
  3 masters: ~1.5M ops/s (keys distributed evenly)

Replication lag:
  Async replication: < 1ms intra-DC
  Cross-AZ: 1-5ms lag
  Worst case data loss on failover: 1-5ms of writes

Gossip overhead:
  30 nodes cluster: each node talks to a few random nodes/sec
  Gossip message size: 2KB
  30 nodes x 1 gossip/s x 2KB = 60KB/s (trivial)

Resharding time:
  100GB shard -> add new master
  MIGRATE throughput: ~1GB/s
  Time: 100 seconds for full shard migration
  During migration: no downtime (ASK redirects)
```

## Design Choices

| Topology | Capacity | HA | Complexity |
|---|---|---|---|
| Single master | 1x | No | Low |
| Master + replica | 1x | Read HA | Low |
| Sentinel (3 nodes) | 1x | Write HA | Medium |
| Cluster (3+3 nodes) | 3x | Write HA | High |
| Cluster + replicas | Nx | Full HA | High |

## Follow-up Questions

1. How does Redis Cluster handle a network partition (split-brain prevention)?
2. How do you perform a rolling upgrade of a Redis Cluster without downtime?
3. How does consistent hashing differ from Redis's slot-based approach?
4. How do you migrate from Redis Sentinel to Redis Cluster?
5. What is the difference between cluster-enabled mode and standalone Redis?

## Python Implementation

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import hashlib
import time
from collections import defaultdict

CLUSTER_SLOTS = 16384

def crc16(data: str) -> int:
    crc = 0
    for byte in data.encode():
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF
    return crc

def key_to_slot(key: str) -> int:
    if "{" in key and "}" in key:
        start = key.index("{") + 1
        end = key.index("}")
        if start < end:
            key = key[start:end]
    return crc16(key) % CLUSTER_SLOTS

@dataclass
class RedisNode:
    node_id: str
    host: str
    port: int
    is_master: bool = True
    master_id: Optional[str] = None
    slots: List[range] = field(default_factory=list)
    store: Dict[str, Any] = field(default_factory=dict)
    replication_offset: int = 0
    alive: bool = True

    def owns_slot(self, slot: int) -> bool:
        return self.is_master and any(slot in r for r in self.slots)

class ClusterTopology:
    def __init__(self):
        self._nodes: Dict[str, RedisNode] = {}
        self._slot_to_master: Dict[int, str] = {}

    def add_node(self, node: RedisNode):
        self._nodes[node.node_id] = node
        if node.is_master:
            for slot_range in node.slots:
                for slot in slot_range:
                    self._slot_to_master[slot] = node.node_id

    def get_master_for_slot(self, slot: int) -> Optional[RedisNode]:
        node_id = self._slot_to_master.get(slot)
        if node_id:
            return self._nodes.get(node_id)
        return None

    def get_replicas_for_master(self, master_id: str) -> List[RedisNode]:
        return [n for n in self._nodes.values() if n.master_id == master_id and not n.is_master]

    def failover(self, failed_master_id: str) -> Optional[str]:
        replicas = self.get_replicas_for_master(failed_master_id)
        if not replicas:
            return None
        # Elect replica with highest offset
        best = max(replicas, key=lambda r: r.replication_offset)
        failed_master = self._nodes[failed_master_id]
        failed_master.alive = False

        # Promote replica
        best.is_master = True
        best.master_id = None
        best.slots = failed_master.slots
        for slot_range in best.slots:
            for slot in slot_range:
                self._slot_to_master[slot] = best.node_id

        print(f"[Cluster] Failover: {best.node_id} promoted to master (was replica of {failed_master_id})")
        return best.node_id

class RedisClusterClient:
    def __init__(self, topology: ClusterTopology):
        self._topology = topology
        self._slot_cache: Dict[int, str] = {}

    def _get_node(self, key: str) -> Optional[RedisNode]:
        slot = key_to_slot(key)
        master = self._topology.get_master_for_slot(slot)
        if master and master.alive:
            return master
        print(f"  [Client] Slot {slot}: no alive master -> CLUSTERDOWN")
        return None

    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        node = self._get_node(key)
        if not node:
            return False
        node.store[key] = (value, time.time() + ex if ex else None)
        node.replication_offset += 1
        # Replicate to replicas (async)
        self._replicate(node, "SET", key, value)
        return True

    def get(self, key: str) -> Optional[Any]:
        node = self._get_node(key)
        if not node:
            return None
        entry = node.store.get(key)
        if entry is None:
            return None
        value, expiry = entry
        if expiry and time.time() > expiry:
            del node.store[key]
            return None
        return value

    def _replicate(self, master: RedisNode, cmd: str, *args):
        replicas = self._topology.get_replicas_for_master(master.node_id)
        for replica in replicas:
            if cmd == "SET":
                replica.store[args[0]] = master.store.get(args[0])
                replica.replication_offset = master.replication_offset

    def cluster_info(self) -> dict:
        topology = self._topology._nodes
        return {
            "total_nodes": len(topology),
            "masters": sum(1 for n in topology.values() if n.is_master and n.alive),
            "replicas": sum(1 for n in topology.values() if not n.is_master and n.alive),
        }

# Setup cluster
topology = ClusterTopology()
nodes = [
    RedisNode("m0", "10.0.0.1", 6379, is_master=True, slots=[range(0, 5461)]),
    RedisNode("m1", "10.0.0.2", 6379, is_master=True, slots=[range(5461, 10923)]),
    RedisNode("m2", "10.0.0.3", 6379, is_master=True, slots=[range(10923, 16384)]),
    RedisNode("s0", "10.0.0.4", 6379, is_master=False, master_id="m0"),
    RedisNode("s1", "10.0.0.5", 6379, is_master=False, master_id="m1"),
    RedisNode("s2", "10.0.0.6", 6379, is_master=False, master_id="m2"),
]
for n in nodes:
    topology.add_node(n)

client = RedisClusterClient(topology)

# Demonstrate key routing
print("=== Key Routing Demo ===")
keys = ["user:1234", "session:abc", "counter:page", "{user:1234}.profile"]
for key in keys:
    slot = key_to_slot(key)
    master = topology.get_master_for_slot(slot)
    print(f"  '{key}' -> slot {slot} -> {master.node_id} ({master.host})")

# Read/write
print("\n=== Read/Write ===")
client.set("user:1234", {"name": "Alice"})
print(f"GET user:1234 = {client.get('user:1234')}")

# Simulate failover
print("\n=== Failover ===")
new_master = topology.failover("m1")
print(f"Cluster info after failover: {client.cluster_info()}")
```

## Java Implementation

```java
import java.util.*;

public class RedisCluster {
    static int keyToSlot(String key) {
        if (key.contains("{") && key.contains("}")) {
            int s = key.indexOf('{') + 1, e = key.indexOf('}');
            if (s < e) key = key.substring(s, e);
        }
        int crc = 0;
        for (byte b : key.getBytes()) {
            crc ^= (b & 0xFF) << 8;
            for (int i = 0; i < 8; i++) crc = (crc & 0x8000) != 0 ? (crc << 1) ^ 0x1021 : crc << 1;
            crc &= 0xFFFF;
        }
        return crc % 16384;
    }

    record Node(String id, int slotStart, int slotEnd, Map<String, Object> store) {
        boolean owns(int slot) { return slot >= slotStart && slot <= slotEnd; }
    }

    static class Cluster {
        List<Node> nodes;
        Cluster(List<Node> nodes) { this.nodes = nodes; }

        Node nodeFor(String key) {
            int slot = keyToSlot(key);
            return nodes.stream().filter(n -> n.owns(slot)).findFirst().orElse(null);
        }

        void set(String key, Object value) {
            Node n = nodeFor(key);
            if (n != null) n.store().put(key, value);
        }

        Object get(String key) {
            Node n = nodeFor(key);
            return n != null ? n.store().get(key) : null;
        }
    }

    public static void main(String[] args) {
        var cluster = new Cluster(List.of(
            new Node("m0", 0, 5460, new HashMap<>()),
            new Node("m1", 5461, 10922, new HashMap<>()),
            new Node("m2", 10923, 16383, new HashMap<>())
        ));

        String[] keys = {"user:1234", "session:abc", "counter"};
        for (String k : keys) {
            System.out.printf("'%s' -> slot %d -> %s%n", k, keyToSlot(k), cluster.nodeFor(k).id());
        }

        cluster.set("user:1234", "Alice");
        System.out.println("GET user:1234 = " + cluster.get("user:1234"));
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Key slot calculation | O(key length) |
| Route to correct node | O(1) (slot map lookup) |
| MOVED redirect handling | O(1) |
| Cluster gossip | O(log n) per message |
| Failover election | O(replicas) |
