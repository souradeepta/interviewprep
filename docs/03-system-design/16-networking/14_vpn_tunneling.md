# VPN and Network Tunneling

## Problem Statement

Design a VPN system that creates encrypted tunnels to securely connect remote users and offices to private networks over the public internet.

## Scenario

VPN and Network Tunneling is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

## Users

- **Backend Engineers**: Responsible for implementing and maintaining this system component in production environments. They need to understand the architecture, trade-offs, failure modes, and operational considerations.
- **DevOps/SRE Teams**: Monitor system health, manage scaling policies, handle incidents, and ensure reliability SLAs are met. They need insights into performance characteristics, bottlenecks, and failure recovery mechanisms.
- **Data Engineers**: Design data pipelines and analytics around this system, requiring deep understanding of data flow, consistency guarantees, and throughput characteristics.
- **System Architects**: Make high-level architectural decisions that impact company infrastructure, requiring comprehensive understanding of capabilities, limitations, and scalability boundaries.
- **Security Teams**: Understand security implications, potential vulnerabilities, and compliance requirements for this component.

## PRD

### Functional Requirements
- Core operations work correctly
- Explicit error handling
- Consistency guarantees defined
- Monitoring and observability

### Non-Functional Requirements
- Performance targets met
- Availability SLA achieved
- Scalability headroom
- Cost efficient

### Success Metrics
- Benchmarks met
- Uptime targets met
- Resource budgets
- No data loss


## Flow

The typical operational flow for this system involves these key phases:

1. **Request Arrival**: Client/upstream system sends request with required parameters and context
2. **Validation & Routing**: System validates request format, authentication, and routes to correct handler/shard/instance
3. **Core Processing**: Execute the main algorithm, database query, or business logic on the data/state
4. **State Management**: Update internal state (caches, indexes, counters, logs) with proper atomicity and locking
5. **Response Generation**: Format results and return to requester with relevant metadata (timing, version info)
6. **Observability**: Record metrics (latency, throughput, errors), logs (for debugging), and traces (for performance analysis)

This flow repeats thousands or millions of times per second in production. Each operation's efficiency compounds across the entire system, making careful optimization essential. Bottlenecks at any phase can cascade to impact overall system performance.


## Code Explanation (Detailed)

### Implementation Approach
The code demonstrates core patterns and trade-offs.

### Key Operations
Each operation shows algorithm and performance characteristics.

### Concurrency and Atomicity
Locking strategies, race condition prevention.

### Edge Cases
Boundary conditions and error handling.

### Performance Optimization
Techniques for reducing latency and throughput.

## Architecture Diagram

```mermaid
graph LR
    Remote["Remote User\n203.0.113.10"]
    VGW["VPN Gateway\n198.51.100.1"]
    Corp["Corporate Network\n10.0.0.0/8"]
    DB["DB Server\n10.0.1.50"]

    Remote -->|"Encrypted IPSec/WireGuard tunnel"| VGW
    VGW -->|Decrypted plaintext| Corp
    Corp --- DB
```

## Flow Diagram

```mermaid
sequenceDiagram
    participant C as Remote Client
    participant VG as VPN Gateway
    participant CN as Corp Network

    C->>VG: IKE Phase 1 - auth + negotiate algorithms
    VG-->>C: IKE Phase 1 OK
    C->>VG: IKE Phase 2 - negotiate tunnel + derive session keys
    VG-->>C: IPSec SA established, client gets VIP 10.0.100.5

    C->>VG: Encrypt + encapsulate: {dst=10.0.1.50, payload=HTTP request}
    VG->>VG: Decrypt + remove VPN header
    VG->>CN: Plain IP packet to 10.0.1.50
    CN-->>VG: HTTP response
    VG->>VG: Encrypt
    VG-->>C: Encrypted response
```

## Design

### VPN Protocol Comparison

```
WireGuard (modern, recommended):
  - ~4000 lines of code (auditable), built into Linux 5.6+
  - ChaCha20-Poly1305 encryption, Curve25519 key exchange
  - Throughput: 10+ Gbps on modern hardware
  - Handshake: 1 RTT (no negotiation, fixed modern algorithms)

IPSec (enterprise standard):
  - Kernel-level, hardware offload support
  - IKEv2 for key exchange, ESP for data
  - Transport mode (host-to-host) vs tunnel mode (gateway-to-gateway)
  - Throughput: 5+ Gbps with AES-NI

OpenVPN (cross-platform):
  - TLS-based, runs on UDP 1194 or TCP 443 (firewall friendly)
  - Userspace, easier to configure
  - Throughput: ~500 Mbps (slower due to userspace)
```

### Split Tunneling

```
Full tunnel:  All traffic (including internet) through VPN
  Pros: Corporate policy enforcement for all traffic
  Cons: VPN becomes internet bottleneck, higher latency for non-corp

Split tunnel: Only corporate traffic through VPN, internet direct
  Pros: Lower latency for internet, less VPN bandwidth
  Cons: Corporate policy not enforced for internet traffic
  Route: 10.0.0.0/8 via VPN, 0.0.0.0/0 direct

Zero Trust (modern): No "trusted" VPN network
  Every request authenticated at application layer
  No lateral movement even if connected
```

## Back-of-Envelope Calculations

```
WireGuard throughput:
  ChaCha20 encryption: ~3 GB/s per core
  1 core: 3 GB/s = 24 Gbps
  Consumer device (2 cores for VPN): 6 Gbps
  Raspberry Pi 4: ~100 Mbps (ARM, no hardware crypto)

Connection establishment:
  WireGuard handshake: 1 RTT (vs IKEv2: 2 RTT, OpenVPN: TLS + 3-way = 4+ RTT)
  At 100ms RTT: WireGuard 100ms faster to establish

Corporate VPN sizing:
  500 concurrent users x 5 Mbps avg usage = 2.5 Gbps
  2 gateways x 2 Gbps each = 4 Gbps capacity with HA

Encryption overhead:
  AES-256-GCM with AES-NI: <1% CPU at 10 Gbps
  Without hardware acceleration: ~15% CPU
  Modern servers: negligible

WireGuard key rotation:
  Session keys: rotate every 3 minutes (180s REKEY_AFTER_TIME)
  100K peers: 100K/180 = 556 rekeys/sec (lightweight)
```

## Design Choices

| Protocol | Throughput | Complexity | Browser | Use Case |
|---|---|---|---|---|
| WireGuard | 10 Gbps | Low | No | Modern servers, cloud |
| IPSec/IKEv2 | 5 Gbps | High | No | Enterprise, iOS built-in |
| OpenVPN | 500 Mbps | Medium | No | Cross-platform, legacy |
| SSTP | 200 Mbps | Medium | No | Windows-native |
| SSL VPN (clientless) | 100 Mbps | Low | Yes | Browser-based access |

## Python Implementation

```python
import os
import hashlib
import hmac
import struct
from typing import Optional, Dict
from dataclasses import dataclass

def xor_bytes(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, (b * (len(a)//len(b)+1))[:len(a)]))

@dataclass
class WGPeer:
    public_key: bytes
    allowed_ips: list
    endpoint: Optional[str] = None

class WireGuardGateway:
    def __init__(self):
        self._private_key = os.urandom(32)
        self._public_key = hashlib.sha256(b"pubkey:" + self._private_key).digest()
        self._peers: Dict[bytes, WGPeer] = {}
        self._session_keys: Dict[bytes, bytes] = {}
        self._ip_pool_idx = 100

    @property
    def public_key(self) -> bytes:
        return self._public_key

    def add_peer(self, peer: WGPeer) -> str:
        # Derive shared secret via ECDH (simplified: sha256 of both keys)
        shared = hashlib.sha256(self._private_key + peer.public_key).digest()
        self._session_keys[peer.public_key] = shared
        self._peers[peer.public_key] = peer
        # Assign virtual IP
        vip = f"10.0.100.{self._ip_pool_idx}"
        self._ip_pool_idx += 1
        return vip

    def _mac(self, key: bytes, data: bytes) -> bytes:
        return hmac.new(key, data, hashlib.sha256).digest()[:16]

    def encrypt_packet(self, peer_pubkey: bytes, payload: bytes) -> bytes:
        key = self._session_keys[peer_pubkey]
        nonce = os.urandom(12)
        # XOR stream cipher (simplified; use AES-GCM in production)
        keystream = hashlib.sha256(key + nonce).digest()
        ciphertext = xor_bytes(payload, keystream[:len(payload)])
        mac = self._mac(key, nonce + ciphertext)
        header = struct.pack("!H", len(nonce))
        return header + nonce + ciphertext + mac

    def decrypt_packet(self, peer_pubkey: bytes, packet: bytes) -> Optional[bytes]:
        key = self._session_keys[peer_pubkey]
        nonce_len = struct.unpack("!H", packet[:2])[0]
        nonce = packet[2:2+nonce_len]
        ciphertext = packet[2+nonce_len:-16]
        mac_recv = packet[-16:]
        mac_calc = self._mac(key, nonce + ciphertext)
        if not hmac.compare_digest(mac_recv, mac_calc):
            print("[VPN] Packet authentication failed - dropping")
            return None
        keystream = hashlib.sha256(key + nonce).digest()
        return xor_bytes(ciphertext, keystream[:len(ciphertext)])

class SplitTunnelRouter:
    def __init__(self, vpn_routes: list, gateway_ip: str):
        self._vpn_routes = vpn_routes  # e.g., ["10.0.0.0/8"]
        self._gateway_ip = gateway_ip

    def route(self, dst_ip: str) -> str:
        for cidr in self._vpn_routes:
            network, prefix = cidr.split("/")
            if self._in_network(dst_ip, network, int(prefix)):
                return "vpn"
        return "direct"

    def _in_network(self, ip: str, network: str, prefix: int) -> bool:
        def to_int(addr):
            p = addr.split(".")
            return sum(int(x) << (24 - 8*i) for i, x in enumerate(p))
        mask = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
        return to_int(ip) & mask == to_int(network) & mask

# Usage
gw = WireGuardGateway()
peer_privkey = os.urandom(32)
peer_pubkey = hashlib.sha256(b"pubkey:" + peer_privkey).digest()
peer = WGPeer(public_key=peer_pubkey, allowed_ips=["10.0.100.0/24"])
vip = gw.add_peer(peer)
print(f"Peer assigned VIP: {vip}")

payload = b"HTTP/1.1 GET /internal-api\r\nHost: 10.0.1.50\r\n"
encrypted = gw.encrypt_packet(peer_pubkey, payload)
decrypted = gw.decrypt_packet(peer_pubkey, encrypted)
print(f"Encrypted: {len(encrypted)}B, decrypted matches: {decrypted == payload}")

router = SplitTunnelRouter(["10.0.0.0/8", "192.168.0.0/16"], "10.0.100.1")
print(router.route("10.0.1.50"))   # vpn
print(router.route("8.8.8.8"))     # direct
print(router.route("192.168.1.1")) # vpn
```

## Java Implementation

```java
import javax.crypto.*;
import javax.crypto.spec.*;
import java.security.*;
import java.util.*;

public class VPNGateway {
    private final Map<String, SecretKey> peerKeys = new HashMap<>();

    public void addPeer(String peerId) throws Exception {
        KeyGenerator kg = KeyGenerator.getInstance("AES");
        kg.init(256, new SecureRandom());
        peerKeys.put(peerId, kg.generateKey());
    }

    public byte[] encrypt(String peerId, byte[] payload) throws Exception {
        SecretKey key = peerKeys.get(peerId);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        byte[] iv = new byte[12];
        new SecureRandom().nextBytes(iv);
        cipher.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(128, iv));
        byte[] ct = cipher.doFinal(payload);
        byte[] result = new byte[12 + ct.length];
        System.arraycopy(iv, 0, result, 0, 12);
        System.arraycopy(ct, 0, result, 12, ct.length);
        return result;
    }

    public byte[] decrypt(String peerId, byte[] packet) throws Exception {
        SecretKey key = peerKeys.get(peerId);
        byte[] iv = Arrays.copyOf(packet, 12);
        byte[] ct = Arrays.copyOfRange(packet, 12, packet.length);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, key, new GCMParameterSpec(128, iv));
        return cipher.doFinal(ct);
    }
}
```

## Complexity

| Operation | Time |
|---|---|
| Handshake | 1 RTT (WireGuard), 2 RTT (IKEv2) |
| Encrypt/decrypt | O(n) payload bytes |
| Peer lookup | O(1) |
| Key rotation (WireGuard) | O(1) every 3 min |

## Common Questions & Answers

**Q: What is caching and why do we need it?**

A: Caching stores frequently accessed data in fast storage (memory) to reduce latency and load on slower backends (database). Trade space (cache) for speed (latency). Critical for systems serving millions of requests per second.

**Q: What are the main cache eviction policies?**

A: LRU (least recently used), LFU (least frequently used), FIFO (first in first out), TTL (time-based), Random, and ARC (adaptive replacement). Choose based on access patterns: LRU for temporal, LFU for frequency, TTL for time-sensitive data.

**Q: What is cache hit rate and cache miss rate?**

A: Hit rate = successful_finds / total_accesses. Miss rate = 1 - hit rate. P(hit) = hits / (hits + misses). Target 80%+ hit rates for effective caching. Too-small cache gives low hit rate (wasted resources). Too-large cache uses more memory than needed.

**Q: How do you handle cache invalidation when backend data changes?**

A: Use TTL (time-based expiration), active invalidation (notify cache on write), cache-aside pattern (client checks backend), or write-through (update both). Active invalidation is fastest but complex. TTL is simplest but has stale data window.

**Q: What is the cache-aside pattern?**

A: Application checks cache first. On miss, fetch from backend, update cache, then return. Simple to implement. Risk: race condition where multiple threads fetch same miss simultaneously (thundering herd problem).

**Q: What is write-through caching?**

A: Writes go to both cache and backend simultaneously (synchronously). Ensures consistency: read always gets latest. Cost: write latency includes backend write. Safer than write-back but slower.

**Q: What is write-back (write-behind) caching?**

A: Writes go to cache only; backend updated asynchronously later (batch or periodic). Fast writes. Risk: data loss if cache fails before flushing. Need durability guarantees (persistence, replication).

**Q: How do you choose cache size?**

A: Estimate working set (frequently accessed data volume). Add 20-30% buffer for margin. Monitor hit rate: if < 80%, increase size. If > 95%, might be oversized (waste). Use tools like cachegrind to profile.

**Q: What's the difference between client-side and server-side caching?**

A: Client cache (browser): reduces network round-trips, entirely controlled by client. Server cache (memory, Redis): shared across clients, controlled by server. Multi-level caching often best.

**Q: How do you measure cache effectiveness?**

A: Hit rate (primary metric), latency reduction (P99 latency with vs. without cache), backend load reduction, and memory cost per cache entry. Calculate ROI: cost of cache vs. benefit (reduced latency, backend load).

## Follow-up Questions & Answers

**Q: How do you prevent the thundering herd problem in caches?**

A: When popular key expires, many threads fetch from backend simultaneously causing spike. Solutions: probabilistic early expiration (refresh before TTL), request coalescing (single thread rebuilds, others wait), or bloom filters (detect non-existent keys fast).

**Q: How would you implement multi-level cache hierarchy?**

A: Use L1 (fast, small, in-process), L2 (medium, local machine), L3 (large, remote, Redis). Check L1, miss→L2, miss→L3, miss→backend. On write: update all levels. Trade space for speed across levels.

**Q: Can you implement read-through caching (automatic population)?**

A: Yes, cache loader/resolver called on miss. Transparent to application. Backend automatically uses cache layer. More complex than cache-aside but cleaner separation.

**Q: How do you handle hot keys in distributed caches?**

A: Hot key = key accessed by many threads/clients. Replicate hot keys on multiple cache nodes. Use local in-process caches for very hot keys. Monitor and detect hot keys automatically.

**Q: What's the difference between warm and cold cache startup?**

A: Cold cache: empty at start, misses until populated (slow ramp-up). Warm cache: pre-loaded from previous state (RDB/snapshot). Warm startup is critical for production (instant performance).

**Q: How would you measure cache effectiveness for business metrics?**

A: Track hit rate, P99 latency (with/without cache), backend QPS reduction, revenue impact. Calculate cache size vs. cost savings. A/B test to prove business value.

**Q: What happens when cache size is insufficient for working set?**

A: Constant evictions = high miss rate = ineffective cache. Solution: increase cache size, improve eviction policy, reduce working set, or use better hardware (faster storage).

**Q: How do you debug cache issues in production?**

A: Monitor hit rate continuously. Profile cache keys (which keys are accessed). Check for cache stampedes (sudden miss spike). Use distributed tracing to see cache path.

**Q: How would you implement a persistent cache?**

A: Combine memory cache (fast) with persistent backend (database, RocksDB, LevelDB). Write-back pattern: batch updates to persistent store. Trade latency for durability.

**Q: Can you use caching for write-heavy workloads?**

A: Write caching is risky (consistency issues). Use carefully: write-through for safety, write-back for speed. Good for batch writes (aggregate before writing). Monitor durability guarantees.


## System Overview

**Scale Metrics:**
- Throughput: Millions of operations per second
- Latency: Sub-millisecond to sub-second response times
- Data volume: Gigabytes to Petabytes
- Concurrent users: Millions to billions
- Availability: 99.99% to 99.999% uptime SLA

**Key Components:**
- Request handling and routing
- Data processing and storage
- Replication and consistency
- Failure detection and recovery
- Monitoring and alerting

## Architecture Diagrams

### System Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        C1["Client"]
        LB["Load Balancer"]
    end

    subgraph "Service Layer"
        S1["Service 1"]
        S2["Service 2"]
        S3["Service N"]
    end

    subgraph "Cache"
        CACHE["Redis/Memcached"]
    end

    subgraph "Storage"
        DB["Primary DB"]
        REP["Replicas"]
    end

    C1 --> LB
    LB --> S1
    LB --> S2
    LB --> S3
    S1 --> CACHE
    S2 --> CACHE
    S3 --> CACHE
    CACHE --> DB
    DB --> REP

    style C1 fill:#e1f5ff
    style S1 fill:#f3e5f5
    style CACHE fill:#fff3e0
    style DB fill:#e8f5e9
```

### Data Flow

```mermaid
graph LR
    A["Request"] --> B["Parse"]
    B --> C["Validate"]
    C --> D["Process"]
    D --> E["Cache"]
    E --> F["Store"]
    F --> G["Response"]

    style A fill:#c8e6c9
    style B fill:#ffccbc
    style C fill:#bbdefb
    style D fill:#f8bbd0
    style E fill:#ffe0b2
    style F fill:#d1c4e9
    style G fill:#c8e6c9
```

### Failover Mechanism

```mermaid
graph TB
    A["Primary Node"] -->|heartbeat| B["Health Checker"]
    C["Replica 1"] -->|heartbeat| B
    D["Replica 2"] -->|heartbeat| B
    B -->|failure detected| E["Coordinator"]
    E -->|elect new primary| F["New Primary"]
    F -->|start accepting| G["Clients"]

    style A fill:#ffcdd2
    style F fill:#c8e6c9
    style G fill:#fff9c4
```

### Consistency Models

```mermaid
graph TB
    subgraph "Strong Consistency"
        A1["Quorum Write"] --> A2["Read Latest"]
    end

    subgraph "Eventual Consistency"
        B1["Write Async"] --> B2["Replicate"]
        B2 --> B3["Read May Stale"]
    end

    subgraph "Causal Consistency"
        C1["Track Causality"] --> C2["Enforce Order"]
    end

    style A1 fill:#c8e6c9
    style B1 fill:#ffccbc
    style C1 fill:#bbdefb
```

### Scaling Strategy

```mermaid
graph TB
    subgraph "Vertical Scaling"
        V1["Bigger CPU"] --> V2["More RAM"]
        V2 --> V3["Faster Disk"]
    end

    subgraph "Horizontal Scaling"
        H1["Add Replicas"] --> H2["Shard Data"]
        H2 --> H3["Distributed Cache"]
    end

    subgraph "Result"
        R["Increased Capacity"]
    end

    V3 --> R
    H3 --> R

    style V1 fill:#bbdefb
    style H1 fill:#f8bbd0
    style R fill:#c8e6c9
```

## Implementation Examples

### Python Implementation

```python
# Python Implementation

from typing import Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration for the system."""
    timeout_ms: int = 5000
    retry_count: int = 3
    batch_size: int = 100
    max_connections: int = 1000

class Handler:
    """Main handler class for operations."""

    def __init__(self, config: Config):
        self.config = config
        self.metrics = {"success": 0, "failure": 0, "latency_ms": []}

    async def process(self, data: Any) -> Any:
        """Process request with error handling."""
        try:
            # Validate input
            self._validate(data)

            # Execute operation
            result = await self._execute(data)

            # Track metrics
            self.metrics["success"] += 1
            return result

        except Exception as e:
            logger.error(f"Processing failed: {e}")
            self.metrics["failure"] += 1
            raise

    def _validate(self, data: Any) -> None:
        """Validate input data."""
        if data is None:
            raise ValueError("Data cannot be None")

    async def _execute(self, data: Any) -> Any:
        """Execute core logic."""
        # Implement actual logic here
        return {"status": "success", "timestamp": datetime.now().isoformat()}

    def get_metrics(self) -> dict:
        """Return collected metrics."""
        return self.metrics

# Usage example
async def main():
    config = Config(timeout_ms=5000, batch_size=100)
    handler = Handler(config)
    result = await handler.process({"key": "value"})
    print(f"Result: {result}")
    print(f"Metrics: {handler.get_metrics()}")
```

### Java Implementation

```java
// Java Implementation

import java.util.*;
import java.util.concurrent.*;
import java.time.Instant;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SystemHandler {
    private static final Logger logger = LoggerFactory.getLogger(SystemHandler.class);

    private final Config config;
    private final Map<String, Long> metrics = new ConcurrentHashMap<>();
    private final ExecutorService executor;

    public static class Config {
        public int timeoutMs = 5000;
        public int retryCount = 3;
        public int batchSize = 100;
        public int maxConnections = 1000;

        public Config withTimeoutMs(int timeout) {
            this.timeoutMs = timeout;
            return this;
        }
    }

    public SystemHandler(Config config) {
        this.config = config;
        this.executor = Executors.newFixedThreadPool(
            Math.min(config.maxConnections, 10)
        );
        metrics.put("success", 0L);
        metrics.put("failure", 0L);
    }

    public <T> T process(Object data) throws Exception {
        try {
            // Validate input
            validate(data);

            // Execute operation
            Object result = execute(data);

            // Track metrics
            metrics.put("success", metrics.get("success") + 1);
            return (T) result;

        } catch (Exception e) {
            logger.error("Processing failed: {}", e.getMessage());
            metrics.put("failure", metrics.get("failure") + 1);
            throw e;
        }
    }

    private void validate(Object data) throws IllegalArgumentException {
        if (data == null) {
            throw new IllegalArgumentException("Data cannot be null");
        }
    }

    private Object execute(Object data) throws Exception {
        // Implement core logic
        return Map.of(
            "status", "success",
            "timestamp", Instant.now().toString()
        );
    }

    public Map<String, Long> getMetrics() {
        return new HashMap<>(metrics);
    }

    public void shutdown() {
        executor.shutdown();
    }

    public static void main(String[] args) throws Exception {
        Config config = new Config()
            .withTimeoutMs(5000);

        SystemHandler handler = new SystemHandler(config);
        Object result = handler.process(Map.of("key", "value"));
        System.out.println("Result: " + result);
        System.out.println("Metrics: " + handler.getMetrics());
        handler.shutdown();
    }
}
```

## Back-of-Envelope Calculations

### Traffic & Throughput
**Assumptions:**
- Daily active users: 100 million (100M)
- Requests per user per day: 50
- Peak hour traffic: 10% of daily (concentrated)
- Request distribution: 70% read, 30% write

**Calculations:**
```
Total daily requests = 100M users × 50 requests = 5 billion requests/day
Average RPS = 5B requests / 86400 seconds ≈ 57,870 RPS
Peak hour RPS = (5B / 86400) × (100 / 10) ≈ 578,700 RPS
Peak minute RPS = 578,700 / 60 ≈ 9,645 RPS

Read operations = 57,870 × 0.7 ≈ 40,509 RPS (average)
Write operations = 57,870 × 0.3 ≈ 17,361 RPS (average)
```

### Storage Requirements
**Assumptions:**
- Data per user: 1 KB (profile, settings)
- Data per transaction: 500 bytes
- Data retention: 3 years

**Calculations:**
```
User profile storage = 100M × 1 KB = 100 GB
Transaction data = 5B requests/day × 500 bytes × 365 × 3 = 2.74 PB
Total storage ≈ 2.75 PB
Replication factor: 3× → 8.25 PB raw storage

Backup storage (weekly snapshots): 8.25 PB × 52 weeks = 429 PB
```

### Network Bandwidth
**Assumptions:**
- Average request size: 2 KB
- Average response size: 5 KB
- Replication overhead: 2× (write to replicas)

**Calculations:**
```
Inbound bandwidth = 57,870 RPS × 2 KB = 115.74 MB/s
Outbound bandwidth = 57,870 RPS × 5 KB = 289.35 MB/s
Replication bandwidth = 17,361 RPS × 2 KB × 2 = 69.44 MB/s
Total peak bandwidth ≈ 474 MB/s ≈ 3.8 Tbps (peak hour)
```

### Compute Requirements
**Assumptions:**
- Processing time per request: 10 ms
- CPU efficiency: 1 core handles 50 RPS

**Calculations:**
```
CPUs needed for average traffic = 57,870 RPS / 50 = 1,158 cores
CPUs needed for peak traffic = 578,700 RPS / 50 = 11,574 cores
Overprovisioning factor: 1.5× → 17,361 cores total

Using 16 cores per server = 17,361 / 16 ≈ 1,085 servers
With 3:1 replication = 3,255 servers needed
Regional redundancy (3 regions) = 9,765 servers
```

### Latency Analysis (p99)
**Components:**
- Network latency: 5 ms
- Processing: 10 ms
- Storage access: 50 ms (disk), 1 ms (cache)
- Replication write: 20 ms

**Path Analysis:**
```
Cache hit path: 5 + 1 + 5 = 11 ms
Database read path: 5 + 10 + 50 + 5 = 70 ms
Write path: 5 + 10 + 20 + 5 = 40 ms
```

### Cost Estimation
**Monthly costs (approximate):**
```
Compute: 9,765 servers × $1,000/month = $9.765M
Storage: 8.25 PB × $10/GB/month = $82.5M
Bandwidth: 3.8 Tbps × $0.12/GB = $456M
Personnel: 100 engineers × $200K = $20M
Total: ~$568M/month
Cost per user: $5.68/month
```


## Interview Questions & Answers

### Q1: Design the System from Scratch

**Question:** Design a system that can handle 1 billion requests per day with sub-100ms latency.

**Answer Structure:**
1. **Clarify requirements**: DAU, request types, geographic distribution, consistency needs
2. **Back-of-envelope**: Calculate RPS (11.5K avg, 115K peak), storage, bandwidth
3. **High-level design**: Load balancing → services → cache → storage
4. **Deep dive**:
   - Horizontal scaling with sharding
   - Multi-region active-active with eventual consistency
   - Caching strategy (write-through for critical data)
   - Monitoring: metrics, logging, tracing
5. **Bottlenecks**: Identify and address each
6. **Trade-offs**: Consistency vs. availability, latency vs. cost

### Q2: Scaling Challenges

**Question:** You're growing from 10M to 1B users (100x). What breaks and how do you fix it?

**Answer:**
- **Database bottleneck**: Sharding by user ID, consistent hashing, shard rebalancing
- **Cache hit rate drops**: Larger working set, tiered caching (L1: local, L2: distributed)
- **Replication lag**: Write-through for consistency-critical data, eventual consistency elsewhere
- **Operational complexity**: Infrastructure-as-code, auto-scaling, chaos engineering
- **Cost**: Optimize resource utilization, use reserved instances, spot instances for batch

### Q3: Failure Scenarios

**Question:** Your primary database goes down. What happens? How do you recover?

**Answer:**
- **Detection**: Health check timeout (3-5 seconds)
- **Failover**: Automatic promotion of replica using Raft consensus
- **Impact**: Write requests fail for ~10 seconds, reads use replicas
- **Recovery**: Background sync of failed node, re-add to cluster
- **Lessons**: Circuit breakers prevent cascade, bulkhead limits blast radius

### Q4: Consistency Requirements

**Question:** Do you need strong or eventual consistency? Why?

**Answer:**
- **Strong consistency**: Critical for financial transactions, inventory, user auth
  - Implementation: Quorum writes, read-after-write
  - Cost: Higher latency (p99 100ms+), lower throughput

- **Eventual consistency**: Fine for user feeds, recommendations, analytics
  - Implementation: Async replication, read-repair
  - Benefit: Lower latency (p99 <10ms), higher throughput

- **Hybrid approach**: Consistency per operation type, not global

### Q5: Performance Optimization

**Question:** How would you reduce p99 latency from 100ms to 20ms?

**Answer:**
1. **Profile** (measure first): Identify bottleneck (storage, network, compute)
2. **Caching**: Multi-tier (L1 local, L2 distributed), bloom filters for misses
3. **Batching**: Group operations, reduce RPC overhead
4. **Connection pooling**: Reuse TCP connections, reduce handshake latency
5. **Async I/O**: Non-blocking operations, increase parallelism
6. **Database optimization**: Indexing, query optimization, read replicas
7. **Code optimization**: Reduce allocations, use faster algorithms
8. **Hardware**: SSD for storage, faster network interconnects

### Q6: Operational Concerns

**Question:** How do you deploy a new version with zero downtime?

**Answer:**
1. **Canary deployment**: Roll out to 1% of servers, monitor metrics
2. **Gradual rollout**: 1% → 10% → 50% → 100% as confidence increases
3. **Health checks**: Automated rollback if error rate exceeds threshold
4. **Database migration**: Schema changes with backward compatibility
5. **Feature flags**: Toggle features independently of deployment
6. **Monitoring**: Enhanced alerting during rollout, easy incident response


## Technology Stack Recommendations

| Layer | Technology | Why |
|-------|-----------|-----|
| Load Balancing | Nginx, HAProxy, AWS ALB | Distribute traffic, health checks |
| Service Framework | FastAPI (Python), Spring Boot (Java) | Async, built-in monitoring |
| Caching | Redis, Memcached | Sub-millisecond latency, distributed |
| Primary Storage | PostgreSQL, MySQL | ACID, complex queries, reliability |
| Analytics | Elasticsearch, Data Warehouse | Full-text search, time-series analysis |
| Streaming | Kafka, AWS Kinesis | Event processing, real-time |
| Observability | Prometheus, ELK Stack, Jaeger | Metrics, logs, traces |

## Lessons Learned

1. **Premature optimization kills projects**: Start simple, measure, then optimize
2. **Consistency is hard**: Eventually consistent systems are tricky to reason about
3. **Monitoring is non-negotiable**: You can't fix what you can't see
4. **Failure is not rare**: Plan for it, test it, automate recovery
5. **Cost grows with complexity**: Each component adds operational overhead

## Related Topics

- Database design and optimization
- Distributed consensus algorithms
- Load balancing strategies
- Caching mechanisms and patterns
- Monitoring and alerting systems
- Security and compliance


## Back-of-the-Envelope Calculations

**Latency Budget:**
- Speed of light NYC→London (5570km): 18.5ms one-way
- Realistic TCP latency: 70-100ms (routing overhead)
- TLS handshake: +1 RTT = 100-200ms
- With TLS session resumption: +0 RTT
- CDN edge node (50ms away): 5-10ms vs 100ms origin

**Throughput:**
- TCP window size: 65KB default → 65KB / 100ms = 5Mbps
- With window scaling (64MB): 64MB / 100ms = 5Gbps theoretical
- HTTP/2 multiplexing: eliminates HOL blocking per-stream
- HTTP/3 (QUIC): 0-RTT handshake, eliminates TCP HOL blocking
