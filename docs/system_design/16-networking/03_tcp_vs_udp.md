# TCP vs UDP

## Problem Statement

Compare TCP (Transmission Control Protocol) and UDP (User Datagram Protocol) — understand when to use each and how TCP achieves reliable delivery.

**Key questions:**
- How does TCP guarantee delivery and order?
- What does TCP's 3-way handshake add?
- When is UDP the better choice?

## Scenario

TCP vs UDP is a critical component in modern distributed systems. In real-world applications, handling complex business logic at scale with high reliability. For example, major tech companies like Netflix, Uber, and Airbnb rely on similar solutions to handle millions of concurrent users and requests. The challenge is achieving this while maintaining sub-100ms latency, 99.99% availability, and gracefully handling 10x traffic spikes during peak demand. This component provides the foundational capability to solve these challenges reliably and efficiently at global scale.

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
graph TB
    subgraph TCP
        A[Sender] -->|SYN| B[Receiver]
        B -->|SYN-ACK| A
        A -->|ACK + Data| B
        B -->|ACK| A
        A -->|Retransmit on timeout| B
    end

    subgraph UDP
        C[Sender] -->|Datagram 1| D[Receiver]
        C -->|Datagram 2| D
        C -->|Datagram 3| D
        Note1[No ACK, no ordering, no retransmit]
    end
```

## TCP 3-Way Handshake

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server

    C->>S: SYN (seq=x)
    S->>C: SYN-ACK (seq=y, ack=x+1)
    C->>S: ACK (ack=y+1)
    Note over C,S: Connection established — data transfer begins

    C->>S: FIN (seq=a)
    S->>C: ACK (ack=a+1)
    S->>C: FIN (seq=b)
    C->>S: ACK (ack=b+1)
    Note over C,S: 4-way teardown — TIME_WAIT waits 2×MSL
```

## Design

### TCP Reliability Mechanisms

```
Sequence numbers    — Order packets, detect gaps
ACKs                — Receiver confirms receipt
Retransmission      — Sender resends unACKed packets (RTO timer)
Flow control        — Receiver advertises window size (rwnd)
Congestion control  — Sender limits rate based on network feedback
  Slow start        — Increase cwnd exponentially until ssthresh
  AIMD              — Additive increase, multiplicative decrease on loss
Nagle's algorithm   — Buffer small writes to reduce packet count
```

### TCP vs UDP Comparison

| Feature | TCP | UDP |
|---|---|---|
| Connection | Yes (3-way handshake) | No |
| Reliability | Guaranteed delivery | Best effort |
| Ordering | Yes | No |
| Flow control | Yes (window) | No |
| Congestion control | Yes | No |
| Header size | 20-60 bytes | 8 bytes |
| Latency | Higher | Lower |
| Throughput | High (but variable) | Potentially higher |
| Use cases | HTTP, email, file transfer | DNS, video, gaming, VoIP |

### TCP Congestion Control States

```
Slow Start:        cwnd doubles each RTT until ssthresh
Congestion Avoidance: cwnd += 1 per RTT (linear)
Fast Retransmit:   3 duplicate ACKs → retransmit immediately
Fast Recovery:     ssthresh = cwnd/2, cwnd = ssthresh + 3
```

## Back-of-Envelope Calculations

```
TCP 3-way handshake overhead:
  1.5 RTT before data (SYN, SYN-ACK, ACK+data)
  At 100ms RTT: 150ms wasted per new connection
  Solution: connection pooling, HTTP keep-alive, HTTP/2 multiplexing

TCP window size impact on throughput:
  Throughput = window_size / RTT
  Window = 65535 bytes (default), RTT = 100ms
  Throughput = 65535 / 0.1 = 655 KB/s = ~5.2 Mbps
  With window scaling (1MB window): 1MB / 0.1s = 80 Mbps

Retransmission timeout (RTO):
  RTO = SRTT + 4 × RTTVAR (Jacobson's algorithm)
  Typical: 200ms–1s, doubles on each timeout (exponential backoff)
  Max retries: ~15 (Linux default), total timeout: ~30 minutes

UDP packet loss tolerance:
  VoIP: tolerate up to 5% loss with PLC (packet loss concealment)
  Video: up to 2% loss (FEC can recover ~5% with 20% overhead)
  DNS: retry at application layer after timeout
```

## Design Choices

| Scenario | Choice | Reason |
|---|---|---|
| File download | TCP | Need complete, ordered data |
| DNS query | UDP | Single request/response, retry at app layer |
| Video call | UDP | Latency > reliability; late packet = useless |
| Game state | UDP | Frequent updates; old state irrelevant |
| Database replication | TCP | Consistency requires reliability |
| Live video (HLS/DASH) | TCP | Buffered, HTTP-based adaptive streaming |

## Python Implementation

```python
import socket
import struct
import threading
from typing import Optional

class TCPServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 9090):
        self._host = host
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self):
        self._sock.bind((self._host, self._port))
        self._sock.listen(5)
        print(f"TCP server listening on {self._host}:{self._port}")
        while True:
            conn, addr = self._sock.accept()
            threading.Thread(target=self._handle, args=(conn, addr), daemon=True).start()

    def _handle(self, conn: socket.socket, addr):
        with conn:
            while data := conn.recv(1024):
                print(f"[TCP] Received from {addr}: {data.decode()}")
                conn.sendall(b"ACK: " + data)

class UDPServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 9091):
        self._host = host
        self._port = port
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start(self):
        self._sock.bind((self._host, self._port))
        print(f"UDP server listening on {self._host}:{self._port}")
        while True:
            data, addr = self._sock.recvfrom(1024)
            print(f"[UDP] Received from {addr}: {data.decode()}")
            self._sock.sendto(b"ACK: " + data, addr)

class ReliableUDP:
    """Simple reliable UDP — sequence numbers + ACKs."""
    SEQ_FMT = "!I"  # 4-byte sequence number

    def __init__(self, sock: socket.socket):
        self._sock = sock
        self._seq = 0
        self._expected_seq = 0

    def send(self, data: bytes, addr: tuple):
        packet = struct.pack(self.SEQ_FMT, self._seq) + data
        self._sock.sendto(packet, addr)
        self._seq += 1

    def receive(self) -> tuple[Optional[bytes], tuple]:
        raw, addr = self._sock.recvfrom(4096)
        seq = struct.unpack(self.SEQ_FMT, raw[:4])[0]
        payload = raw[4:]
        if seq == self._expected_seq:
            self._expected_seq += 1
            ack = struct.pack(self.SEQ_FMT, seq)
            self._sock.sendto(ack, addr)
            return payload, addr
        return None, addr  # out-of-order — drop

# TCP connection teardown states
TCP_STATES = ["LISTEN", "SYN_SENT", "SYN_RECEIVED", "ESTABLISHED",
              "FIN_WAIT_1", "FIN_WAIT_2", "TIME_WAIT", "CLOSE_WAIT", "LAST_ACK", "CLOSED"]

def simulate_tcp_handshake():
    state = "LISTEN"
    print(f"Server: {state}")
    state = "SYN_RECEIVED"
    print(f"Server (got SYN, sent SYN-ACK): {state}")
    state = "ESTABLISHED"
    print(f"Server (got ACK): {state}")
    return state

print(simulate_tcp_handshake())  # ESTABLISHED
```

## Java Implementation

```java
import java.io.*;
import java.net.*;
import java.util.concurrent.*;

public class TCPUDPComparison {

    // TCP Echo Server
    static class TCPServer implements Runnable {
        private int port;
        TCPServer(int port) { this.port = port; }

        public void run() {
            try (ServerSocket ss = new ServerSocket(port)) {
                System.out.println("TCP listening on " + port);
                while (true) {
                    Socket conn = ss.accept();
                    new Thread(() -> {
                        try (BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
                             PrintWriter out = new PrintWriter(conn.getOutputStream(), true)) {
                            String line;
                            while ((line = in.readLine()) != null) {
                                System.out.println("[TCP] " + line);
                                out.println("ACK: " + line);
                            }
                        } catch (IOException e) { e.printStackTrace(); }
                    }).start();
                }
            } catch (IOException e) { e.printStackTrace(); }
        }
    }

    // UDP Echo Server
    static class UDPServer implements Runnable {
        private int port;
        UDPServer(int port) { this.port = port; }

        public void run() {
            try (DatagramSocket sock = new DatagramSocket(port)) {
                System.out.println("UDP listening on " + port);
                byte[] buf = new byte[1024];
                while (true) {
                    DatagramPacket pkt = new DatagramPacket(buf, buf.length);
                    sock.receive(pkt);
                    String msg = new String(pkt.getData(), 0, pkt.getLength());
                    System.out.println("[UDP] " + msg);
                    byte[] reply = ("ACK: " + msg).getBytes();
                    sock.send(new DatagramPacket(reply, reply.length, pkt.getAddress(), pkt.getPort()));
                }
            } catch (IOException e) { e.printStackTrace(); }
        }
    }

    public static void main(String[] args) {
        ExecutorService pool = Executors.newFixedThreadPool(2);
        pool.submit(new TCPServer(9090));
        pool.submit(new UDPServer(9091));
    }
}
```

## Complexity

| Metric | TCP | UDP |
|---|---|---|
| Connection setup | 1.5 RTT | 0 |
| Header overhead | 20-60 bytes/packet | 8 bytes/packet |
| Throughput (ideal) | ~80% of link | ~95% of link |
| Retransmission delay | 1+ RTT (RTO) | Application-defined |

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

