# TCP vs UDP

## Problem Statement

Compare TCP (Transmission Control Protocol) and UDP (User Datagram Protocol) — understand when to use each and how TCP achieves reliable delivery.

**Key questions:**
- How does TCP guarantee delivery and order?
- What does TCP's 3-way handshake add?
- When is UDP the better choice?

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

## Common Questions & Answers

**Q: What is the TIME_WAIT state?** A: After active closer sends final ACK, waits 2×MSL (max segment lifetime, ~60s) to handle delayed duplicates. Prevents port reuse confusion.

**Q: TCP head-of-line blocking?** A: If packet N is lost, packets N+1, N+2... wait in buffer. HTTP/2 over TCP still suffers this. QUIC/HTTP/3 solves it per-stream.

**Q: What is Nagle's algorithm?** A: Buffers small TCP writes until ACK received for outstanding data. Reduces chattiness. Disable with `TCP_NODELAY` for latency-sensitive apps.

**Q: How does TCP handle packet reordering?** A: Sequence numbers allow receiver to reorder. Buffer out-of-order segments until gap fills.

**Q: UDP vs TCP for video streaming?** A: Real-time: UDP (tolerate loss, not delay). VOD: TCP (reliable, adaptive bitrate over HTTP/DASH).

**Q: What is SCTP?** A: Stream Control Transmission Protocol — multi-homing, multi-streaming, message-oriented. Used in telecom. Less common than TCP/UDP.

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

## Follow-up Questions

1. How does QUIC (HTTP/3) combine UDP reliability?
2. What is BBR congestion control and why does Google use it?
3. How does TCP Fast Open (TFO) eliminate the handshake RTT?
4. Design a reliable messaging protocol over UDP.
5. How do firewalls handle UDP differently from TCP?

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
