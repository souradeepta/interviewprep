# Networking Fundamentals — HTTP, TCP/IP, DNS, and Beyond

**Level:** L4-L5
**Time to read:** ~20 min

Essential networking concepts for system design and backend interviews.

---

## 🌐 The Network Stack (OSI Model)

```
Layer 7: Application (HTTP, FTP, DNS, SMTP)
Layer 6: Presentation (Encryption, compression)
Layer 5: Session (Connection management)
Layer 4: Transport (TCP, UDP)
Layer 3: Network (IP)
Layer 2: Data Link (MAC addresses, switches)
Layer 1: Physical (Cables, fiber, wireless)
```

**Interview focus:** Layers 3-7 (Network, Transport, Application)

---

## 🔗 TCP/IP Protocol

### TCP (Transmission Control Protocol)

Reliable, ordered, connection-based:

```
Three-way handshake (connection setup):
1. Client → Server: SYN (can you hear me?)
2. Server → Client: SYN-ACK (yes, I can)
3. Client → Server: ACK (great, let's talk)

Data transmission:
Client → Server: Data (+ sequence number)
Server → Client: ACK (confirm receipt)

Connection teardown:
Client → Server: FIN (done talking)
Server → Client: ACK (ok, closing)
```

**Characteristics:**
- Reliable (guaranteed delivery)
- Ordered (data arrives in order)
- Connection-oriented (setup/teardown)
- Slower than UDP

**Use cases:**
- HTTP/HTTPS
- Email
- File transfer (FTP)
- Banking, anything requiring reliability

### UDP (User Datagram Protocol)

Unreliable, unordered, connectionless:

```
Client → Server: Packet (fire and forget)
No acknowledgment, no ordering
```

**Characteristics:**
- Unreliable (packets may be lost)
- Unordered (may arrive out of order)
- Connectionless (no setup)
- Fast

**Use cases:**
- Video streaming (loss tolerable)
- Voice calls (low latency > reliability)
- Online gaming
- DNS queries

---

## 🌍 IP (Internet Protocol)

### IPv4 Address

```
192.168.1.100:8080

192.168.1.0 = network
100 = host on that network
8080 = port (0-65535)

Private ranges (internal):
10.0.0.0 - 10.255.255.255
172.16.0.0 - 172.31.255.255
192.168.0.0 - 192.168.255.255
```

### Ports

```
0-1023: System/well-known
- 80: HTTP
- 443: HTTPS
- 22: SSH
- 25: SMTP
- 3306: MySQL
- 5432: PostgreSQL

1024-65535: User ports
- 8080, 8888: Common for dev servers
- 3000: Node.js default
- 5000: Python Flask default
```

### Routing

```
Packet → Router → Look up destination IP → 
Forward to next hop → Repeat until destination
```

---

## 🔐 HTTP/HTTPS

### HTTP (HyperText Transfer Protocol)

Request-response protocol:

```
Request:
GET /api/users/1 HTTP/1.1
Host: api.example.com
Authorization: Bearer token123

Response:
HTTP/1.1 200 OK
Content-Type: application/json
{
  "id": 1,
  "name": "Alice"
}
```

**Methods:**
- GET: Retrieve data
- POST: Create data
- PUT: Replace data
- PATCH: Partial update
- DELETE: Remove data
- HEAD: Like GET, no body

**Status Codes:**
```
2xx: Success
- 200: OK
- 201: Created

3xx: Redirection
- 301: Moved permanently
- 304: Not modified

4xx: Client error
- 400: Bad request
- 401: Unauthorized
- 404: Not found

5xx: Server error
- 500: Internal error
- 503: Service unavailable
```

### HTTPS (HTTP Secure)

HTTP + TLS/SSL encryption:

```
HTTPS connection setup:
1. TCP handshake (3 steps)
2. TLS handshake (exchange certificates, establish encryption key)
3. HTTP communication (encrypted)

Certificates:
- Server presents certificate (signed by trusted CA)
- Client verifies certificate
- If valid: Trust and proceed
- If not: Security warning
```

**Benefits:**
- Encrypted (eavesdropping prevented)
- Authenticated (server identity verified)
- Integrity (data not tampered)

---

## 🔍 DNS (Domain Name System)

Translates names to IP addresses:

```
User: "What's the IP of google.com?"

DNS Lookup:
1. Computer checks local cache
2. If not found, query DNS resolver (ISP)
3. DNS resolver queries root nameserver
4. Root points to TLD (.com) nameserver
5. TLD points to authoritative nameserver
6. Authoritative returns: google.com = 142.250.185.46
7. Result cached locally
8. Browser connects to 142.250.185.46
```

**DNS Record Types:**
```
A: Maps domain to IPv4 address
google.com → 142.250.185.46

AAAA: Maps domain to IPv6 address
google.com → 2607:f8b0:4004:80b::200e

CNAME: Alias
www.google.com → google.com

MX: Mail server
example.com → mail.example.com

NS: Nameserver
example.com → ns1.example.com

TXT: Text records
SPF, DKIM for email verification
```

---

## 📡 Connection Optimization

### Keep-Alive

```
Without keep-alive:
Request 1 → Response → Connection close
Request 2 → TCP handshake → Response → Connection close
Total: 3 handshakes, slow

With keep-alive (HTTP/1.1 default):
Request 1 → Response → Connection stays open
Request 2 → Response → Connection stays open
Total: 1 handshake, faster
```

### HTTP Pipelining

```
Without pipelining:
Request 1 → Response 1 → Request 2 → Response 2

With pipelining:
Request 1 → Request 2 → Response 1 → Response 2
(Requests sent without waiting for response)
```

### HTTP/2 Multiplexing

```
All requests/responses over single connection
- Interleaved (mix of requests and responses)
- Binary framing (more efficient)
- Headers compressed
Result: Faster than HTTP/1.1
```

---

## 🔄 Network Concepts

### Latency

```
Time to send one packet from source to destination

Formula:
Round-trip time (RTT) = 2 × latency

Example:
User in SF → Server in VA
Latency ≈ 50ms (cross-country)
RTT ≈ 100ms (one request-response cycle)

Sources:
- Distance (speed of light ~200km/ms)
- Routing (not always direct)
- Network conditions (congestion)
```

### Bandwidth

```
Data capacity of connection (bits/second)

Example:
1 Mbps: 1 megabit per second
= 125 KB/second

Time to transfer 1GB:
1,000 MB / 0.125 MB/sec = 8000 seconds ≈ 2 hours

Practical:
- Home: 10-100 Mbps
- Mobile: 5-100 Mbps
- Data center: 1-100 Gbps
```

### Throughput

```
Actual data transferred (often less than bandwidth)

Bandwidth: 100 Mbps (theoretical max)
Throughput: 80 Mbps (actual, due to overhead)

Efficiency = Throughput / Bandwidth = 80%
```

---

## 🛡️ Network Security

### Firewalls

```
Rules:
- Allow: HTTP (port 80), HTTPS (port 443), SSH (port 22)
- Deny: Everything else by default

Network firewall: Controls traffic between networks
Host firewall: Controls traffic on single machine
```

### VPN (Virtual Private Network)

```
Purpose: Encrypt traffic, hide IP

User → VPN Gateway → Internet
User's traffic encrypted, appears from VPN IP
Useful for:
- Remote work (company network access)
- Privacy (hide ISP activity)
- Bypassing geo-restrictions (limited value)
```

---

## ❓ Interview Q&A

**Q: Explain the difference between TCP and UDP.**
A: TCP is reliable, ordered, connection-based (email, HTTP). UDP is fast, unreliable, connectionless (video, gaming). Choose based on whether you need reliability or speed.

**Q: What happens when you type a URL?**
A: DNS lookup → Connect to server (TCP) → Send HTTP request → Server responds → Browser renders. Connection optimization with keep-alive.

**Q: How does HTTPS work?**
A: TLS handshake establishes encryption key, then HTTP communication is encrypted. Prevents eavesdropping and man-in-the-middle attacks.

**Q: What's latency vs. bandwidth?**
A: Latency is delay (milliseconds). Bandwidth is capacity (megabits/second). Both matter for performance.

**Q: How would you optimize a slow API call?**
A: Check latency (network issue?) vs. bandwidth (huge response?). Solutions: Caching, CDN, compression, batching, connection pooling.

---

## ✅ Checklist

- [ ] Understand TCP vs. UDP
- [ ] Know IP addresses and ports
- [ ] Understand HTTP methods and status codes
- [ ] Know HTTPS and TLS
- [ ] Understand DNS lookup process
- [ ] Know latency vs. bandwidth
- [ ] Understand keep-alive and connection optimization
- [ ] Know network security basics (firewall, VPN)

---

**Last updated:** 2026-05-22
