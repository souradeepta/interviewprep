# Database Security & Encryption

Protect sensitive data at rest, in transit, and at the column level. Implement access control, audit logging, and secrets management for compliance-ready systems.

---

## ⚖️ Encryption Strategy Trade-offs

| Method | Query Overhead | Security Level | Protects Against | Indexable | Best For |
|--------|----------------|----------------|------------------|-----------|---------|
| **Encryption at rest** | ~0% | Medium | Stolen disks, backup breaches | Yes | Baseline compliance |
| **TLS in transit** | 2–5% latency | High | Network sniffing, MITM | N/A | All DB connections |
| **Column-level (app)** | 5–15% | Very High | DB admin, SQL injection result | No (unless hashed) | PII, SSN, card numbers |
| **Transparent Data Encryption** | 5–10% | High | Disk-level theft | Yes | Full-database protection |
| **Searchable encryption** | 20–50% | Very High | Everything | Partial | Healthcare, legal |

### Access Control Model Comparison

| Model | Granularity | Complexity | Enforced By | Bypass Risk |
|-------|-------------|------------|-------------|-------------|
| **Network firewall** | Host/IP | Low | Infra | VPN breach |
| **DB user privileges** | Table/Column | Medium | DB engine | Superuser |
| **Row-Level Security** | Row | High | DB engine | Superuser bypass |
| **App-layer checks** | Arbitrary | Very High | App code | Code bugs |
| **Column encryption** | Cell | Highest | Cryptography | Key compromise |

---

## 🏗️ Architecture Patterns

### Pattern 1: Defense in Depth (5 Layers)

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: Application Layer                                  │
│  - Input validation, parameterized queries (SQL injection)  │
│  - RBAC checks before any DB call                           │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Network Layer                                      │
│  - VPC private subnet (DB not publicly accessible)          │
│  - Security group: only app servers on port 5432            │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: Authentication                                     │
│  - Separate DB user per microservice (least privilege)      │
│  - Rotate passwords via Vault/AWS Secrets Manager           │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Authorization (DB engine)                         │
│  - GRANT only needed tables/columns                         │
│  - Row-Level Security for tenant isolation                  │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Encryption                                        │
│  - TLS 1.3 in transit, AES-256 at rest                     │
│  - Column-level encryption for PII                          │
└─────────────────────────────────────────────────────────────┘
```

### Pattern 2: Column-Level Encryption Pipeline

```
Write path:
  App → AES-256-GCM(plaintext, DEK) → [ciphertext stored in DB]
              ↑
       DEK encrypted with KEK (stored in AWS KMS)
       App fetches DEK at startup (cached for session)

Read path:
  DB → [ciphertext] → App → AES-256-GCM.decrypt(ciphertext, DEK) → plaintext

Key rotation:
  1. Fetch new DEK from KMS
  2. Re-encrypt all ciphertext values with new DEK
  3. Rotate KEK in KMS (invalidates old DEK ciphertexts)
```

### Pattern 3: Audit Logging Architecture

```
Every SQL query → Trigger / pgaudit → Audit log table / SIEM

Audit record fields:
  - user        (DB username)
  - tenant      (app.current_tenant session variable)
  - action      (SELECT, INSERT, UPDATE, DELETE)
  - table       (orders, users)
  - row_ids     (affected row PKs)
  - query_hash  (normalized SQL fingerprint)
  - timestamp   (microsecond precision)
  - ip_address  (client IP from connection)
```

---

## 📊 Security Implementation

```python
import os, base64, hmac, hashlib, json, time
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import secrets

# ── Column-Level Encryption ──────────────────────────────────────────────────

class ColumnEncryptor:
    """
    AES-256-GCM column encryption.
    Each value gets a random 12-byte nonce; ciphertext is nonce + tag + data.
    """

    def __init__(self, key: Optional[bytes] = None):
        # 256-bit key (in production, fetch from KMS, not env)
        self._key = key or os.urandom(32)
        self._aes = AESGCM(self._key)

    def encrypt(self, plaintext: str, associated_data: bytes = b"") -> str:
        """Returns base64-encoded nonce+ciphertext."""
        nonce = os.urandom(12)
        ct = self._aes.encrypt(nonce, plaintext.encode(), associated_data)
        return base64.b64encode(nonce + ct).decode()

    def decrypt(self, token: str, associated_data: bytes = b"") -> str:
        """Decrypts base64-encoded nonce+ciphertext."""
        raw = base64.b64decode(token)
        nonce, ct = raw[:12], raw[12:]
        return self._aes.decrypt(nonce, ct, associated_data).decode()

    def encrypt_record(self, record: dict, pii_fields: list) -> dict:
        """Encrypt specified fields in a dict."""
        result = dict(record)
        for field in pii_fields:
            if field in result and result[field] is not None:
                aad = f"{field}:{record.get('id', '')}".encode()
                result[field] = self.encrypt(str(result[field]), aad)
        return result

    def decrypt_record(self, record: dict, pii_fields: list) -> dict:
        """Decrypt specified fields."""
        result = dict(record)
        for field in pii_fields:
            if field in result and result[field] is not None:
                try:
                    aad = f"{field}:{record.get('id', '')}".encode()
                    result[field] = self.decrypt(result[field], aad)
                except Exception:
                    result[field] = "[DECRYPTION_FAILED]"
        return result


# Demo
encryptor = ColumnEncryptor()
PII_FIELDS = ["email", "ssn", "card_number"]

original = {
    "id": 42,
    "name": "Alice Smith",
    "email": "alice@example.com",
    "ssn": "123-45-6789",
    "card_number": "4111111111111111",
    "created_at": "2026-01-01",
}

encrypted = encryptor.encrypt_record(original, PII_FIELDS)
print("Stored (encrypted):")
print(f"  email: {encrypted['email'][:40]}...")
print(f"  name:  {encrypted['name']}")  # Not in PII_FIELDS, unchanged

decrypted = encryptor.decrypt_record(encrypted, PII_FIELDS)
print("\nRetrieved (decrypted):")
print(f"  email: {decrypted['email']}")
print(f"  ssn:   {decrypted['ssn']}")
```

---

## 🔐 Audit Logging

```python
import threading
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, List
from enum import Enum

class DBAction(Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN  = "LOGIN"
    SCHEMA = "SCHEMA"

@dataclass
class AuditRecord:
    action: str
    table_name: str
    db_user: str
    tenant_id: Optional[str]
    affected_ids: List[int]
    query_fingerprint: str
    ip_address: str
    timestamp: float = field(default_factory=time.time)
    session_id: Optional[str] = None

class AuditLogger:
    """
    Thread-safe audit log with append-only semantics.
    In production: writes to a separate audit DB or SIEM (Splunk, Datadog).
    """

    def __init__(self, sink=None):
        self._log: List[AuditRecord] = []
        self._lock = threading.Lock()
        self._sink = sink  # Optional external writer

    def log(self, record: AuditRecord):
        with self._lock:
            self._log.append(record)
        if self._sink:
            self._sink(asdict(record))

    def query(
        self,
        tenant_id: Optional[str] = None,
        action: Optional[str] = None,
        since: Optional[float] = None,
    ) -> List[AuditRecord]:
        with self._lock:
            results = list(self._log)
        if tenant_id:
            results = [r for r in results if r.tenant_id == tenant_id]
        if action:
            results = [r for r in results if r.action == action]
        if since:
            results = [r for r in results if r.timestamp >= since]
        return results

    def anomaly_report(self) -> dict:
        """Detect: bulk deletes, off-hours access, new IPs."""
        with self._lock:
            records = list(self._log)

        deletes = [r for r in records if r.action == "DELETE"]
        bulk_deletes = [r for r in deletes if len(r.affected_ids) > 100]

        user_ips: dict = {}
        for r in records:
            user_ips.setdefault(r.db_user, set()).add(r.ip_address)

        return {
            "bulk_deletes": len(bulk_deletes),
            "users_with_multiple_ips": {u: list(ips) for u, ips in user_ips.items() if len(ips) > 1},
            "total_records": len(records),
        }


# Demo
audit = AuditLogger()

audit.log(AuditRecord(
    action="INSERT",
    table_name="users",
    db_user="app_service",
    tenant_id="acme",
    affected_ids=[1001],
    query_fingerprint="INSERT INTO users (email, ...) VALUES ($1, ...)",
    ip_address="10.0.1.5",
))

audit.log(AuditRecord(
    action="DELETE",
    table_name="orders",
    db_user="admin",
    tenant_id=None,
    affected_ids=list(range(1, 500)),   # Bulk delete — suspicious
    query_fingerprint="DELETE FROM orders WHERE created_at < $1",
    ip_address="203.0.113.99",           # External IP — very suspicious
))

print(audit.anomaly_report())
```

---

## 🔧 PostgreSQL Security Configuration

```sql
-- 1. Least-privilege user per service
CREATE ROLE orders_service WITH LOGIN PASSWORD 'strong-random-password';
GRANT CONNECT ON DATABASE production TO orders_service;
GRANT USAGE ON SCHEMA public TO orders_service;
GRANT SELECT, INSERT, UPDATE ON orders, order_items TO orders_service;
-- NO DELETE, NO DROP, NO ALTER

-- 2. TLS enforcement (pg_hba.conf)
-- hostssl all all 0.0.0.0/0 scram-sha-256
-- host    all all 0.0.0.0/0 reject   ← reject non-TLS

-- 3. Audit logging via pgaudit extension
CREATE EXTENSION IF NOT EXISTS pgaudit;
-- postgresql.conf:
-- pgaudit.log = 'write, ddl'
-- pgaudit.log_catalog = off
-- pgaudit.log_relation = on
-- log_connections = on
-- log_disconnections = on

-- 4. Connection limits per role
ALTER ROLE orders_service CONNECTION LIMIT 50;  -- Prevent accidental runaway

-- 5. Password policies
ALTER ROLE orders_service VALID UNTIL '2027-01-01';  -- Expiry

-- 6. Revoke dangerous defaults
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE production FROM PUBLIC;

-- 7. Masking view for analysts (no direct PII access)
CREATE VIEW orders_analytics AS
    SELECT
        id,
        tenant_id,
        amount,
        created_at,
        -- Mask PII: show only first 3 chars
        LEFT(email, 3) || '***' || SUBSTRING(email FROM POSITION('@' IN email)) AS email_masked
    FROM orders;
GRANT SELECT ON orders_analytics TO analyst_role;
-- Do NOT grant orders_service or analyst_role on the base orders table for email
```

---

## ❓ Interview Q&A

**Q1: How do you encrypt PII (email, SSN, card numbers) in a database?**

A: Three-layer approach:
1. **Transport**: TLS 1.3 between app and DB (non-negotiable baseline)
2. **At rest**: Enable AWS RDS encryption (AES-256) — free, <1% overhead, protects backups
3. **Column-level**: AES-256-GCM for PII columns; app encrypts before INSERT, decrypts after SELECT; 32-byte key stored in AWS KMS, not in code

Trade-off: encrypted columns can't be indexed or searched by value. Mitigate with:
- Store hash of email (HMAC-SHA256 with pepper) in a separate `email_hash` column for lookups
- Full-text search via tokenized hash search (for partial matching)

**Q2: Database credentials were leaked in a GitHub commit. Walk me through your incident response.**

A: In order:
1. **Rotate immediately** — change DB password in 5 minutes; AWS Secrets Manager auto-propagates to app
2. **Audit access logs** — `SELECT * FROM pg_stat_activity` now; query `pg_log` for any connections from unknown IPs
3. **Check data exfiltration** — large SELECT statements, unusual table scans (pg_stat_statements)
4. **Revoke compromised role** — `REVOKE ALL ... FROM compromised_user`, create new role
5. **Post-incident**: move all secrets to Vault/Secrets Manager; add git-secrets pre-commit hook to scan for credentials; mandatory code review for config files

**Q3: How do you implement column-level encryption without breaking existing queries?**

A: Expand-contract with transparent encryption layer:
1. Add `email_encrypted` column alongside `email`
2. Deploy app v1.5: dual-write (clear + encrypted), dual-read (try encrypted first, fall back to clear)
3. Backfill: encrypt all existing `email` values into `email_encrypted`
4. Deploy app v2: read-only from `email_encrypted`
5. Mask `email` column: `ALTER TABLE users ALTER COLUMN email SET DEFAULT NULL; UPDATE users SET email = NULL`
6. Drop `email` column after 30-day grace period

**Q4: How do you prevent SQL injection at the database level (defense beyond parameterized queries)?**

A: Layered:
1. **Parameterized queries** (app layer) — primary defense
2. **Stored procedures** (DB layer) — inject can't add new SQL tokens
3. **DB firewall** (Imperva, PgBouncer query filter) — blocks known injection patterns
4. **Least-privilege roles** — even successful injection only accesses `app_user` tables
5. **Statement timeout** — `SET statement_timeout = '5s'` — kills long-running injected queries like sleep attacks
6. **pg_audit** logging — alerts on anomalous query patterns

**Q5: How do you pass a security audit for SOC 2 Type II regarding database access?**

A: Four control categories:
1. **Access control**: All roles use least privilege, quarterly access reviews, no shared credentials
2. **Encryption**: TLS in transit, AES-256 at rest, column-level for PII, KMS key rotation
3. **Monitoring**: `pgaudit` logs all DML; alerts for: off-hours access, new IPs, bulk deletes, >1,000 row reads
4. **Change management**: All DDL changes via reviewed migration scripts; no direct prod DB access for engineers; bastion host + break-glass procedure with auto-alert

---

## 🧪 Practical Exercises

### Exercise 1: SQL Injection Detector (Easy)

**Problem:** Detect common SQL injection patterns in user input.

```python
import re

INJECTION_PATTERNS = [
    r"(?i)(union\s+select)",
    r"(?i)(drop\s+table)",
    r"(?i)(insert\s+into)",
    r"(?i)(;\s*delete)",
    r"'[^']*'--",           # Classic comment injection
    r"(?i)(xp_cmdshell)",   # MSSQL exec
    r"(?i)(exec\s*\()",
    r"(?i)(benchmark\s*\()",  # MySQL time injection
    r"(?i)(sleep\s*\()",
    r"0x[0-9a-f]{4,}",      # Hex encoding
]

def detect_injection(user_input: str) -> dict:
    matches = []
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input):
            matches.append(pattern)
    return {
        "input": user_input[:100],
        "is_safe": len(matches) == 0,
        "matched_patterns": matches,
        "risk": "HIGH" if matches else "OK",
    }

tests = [
    "alice@example.com",                              # Safe
    "' OR '1'='1",                                    # Classic injection
    "1; DROP TABLE users; --",                        # Destructive
    "1 UNION SELECT * FROM credit_cards --",         # Data extraction
    "1 AND SLEEP(5)",                                 # Blind time injection
]

for t in tests:
    result = detect_injection(t)
    print(f"[{result['risk']}] {result['input'][:50]}")
    if result['matched_patterns']:
        print(f"       Patterns: {result['matched_patterns']}")
```

---

### Exercise 2: Secrets Rotation Simulator (Medium)

**Problem:** Rotate DB credentials without application downtime.

```python
import time
import threading

class SecretsManager:
    """Simulates AWS Secrets Manager with dual-active credentials during rotation."""

    def __init__(self):
        self._current = {"username": "app_user", "password": "old-password-abc"}
        self._pending = None
        self._lock = threading.RLock()
        self._rotation_in_progress = False

    def get_secret(self) -> dict:
        with self._lock:
            return dict(self._current)

    def begin_rotation(self, new_password: str):
        """
        AWS rotation flow:
        1. createSecret — create new version
        2. setSecret    — push to DB
        3. testSecret   — verify new works
        4. finishSecret — mark new as AWSCURRENT
        """
        with self._lock:
            self._rotation_in_progress = True
            self._pending = {"username": "app_user", "password": new_password}
            print(f"Rotation started: new password staged")

        # Simulate async rotation phases
        def rotate():
            time.sleep(0.1)  # setSecret: update DB user password
            with self._lock:
                self._current = self._pending  # finishSecret
                self._pending = None
                self._rotation_in_progress = False
            print("Rotation complete: new credentials active")

        threading.Thread(target=rotate, daemon=True).start()

    def is_rotating(self) -> bool:
        return self._rotation_in_progress


class DBConnectionPool:
    """Pool that auto-refreshes credentials on rotation."""

    def __init__(self, secrets: SecretsManager):
        self.secrets = secrets
        self._creds = secrets.get_secret()

    def get_connection_string(self) -> str:
        # On each borrow, check if rotation changed credentials
        current = self.secrets.get_secret()
        if current != self._creds:
            self._creds = current
            print(f"  [Pool] Credentials rotated — reconnecting with new password")
        return f"postgres://{self._creds['username']}:{self._creds['password']}@db:5432/prod"


# Demo: rotation with zero downtime
sm = SecretsManager()
pool = DBConnectionPool(sm)

print("Before rotation:", pool.get_connection_string())
sm.begin_rotation("new-strong-password-xyz")
time.sleep(0.2)
print("After rotation:", pool.get_connection_string())
```

---

### Exercise 3: Database Access Anomaly Detector (Hard)

**Problem:** Analyze audit logs to detect suspicious access patterns.

```python
from collections import defaultdict
from typing import List

class AnomalyDetector:
    """
    Rules:
    1. Off-hours access (outside 8 AM–8 PM)
    2. New IP address for existing user
    3. Bulk read (> 10,000 rows in one query)
    4. Rapid fire queries (> 100 queries in 10s from same user)
    5. Access after password rotation
    """

    def __init__(self, known_ips: dict = None):
        self.known_ips = known_ips or {}  # user → set of known IPs
        self._user_timestamps = defaultdict(list)

    def analyze(self, records: List[AuditRecord]) -> List[dict]:
        alerts = []

        for record in records:
            ts = record.timestamp
            hour = int((ts % 86400) // 3600)  # UTC hour from epoch

            # Rule 1: Off-hours
            if hour < 8 or hour >= 20:
                alerts.append({
                    "type": "OFF_HOURS_ACCESS",
                    "user": record.db_user,
                    "hour_utc": hour,
                    "table": record.table_name,
                })

            # Rule 2: New IP
            known = self.known_ips.setdefault(record.db_user, set())
            if record.ip_address not in known:
                alerts.append({
                    "type": "NEW_IP_ADDRESS",
                    "user": record.db_user,
                    "ip": record.ip_address,
                    "known_ips": list(known),
                })
                known.add(record.ip_address)

            # Rule 3: Bulk read
            if record.action == "SELECT" and len(record.affected_ids) > 10_000:
                alerts.append({
                    "type": "BULK_READ",
                    "user": record.db_user,
                    "rows": len(record.affected_ids),
                    "table": record.table_name,
                })

            # Rule 4: Rapid fire
            self._user_timestamps[record.db_user].append(ts)
            recent = [t for t in self._user_timestamps[record.db_user] if ts - t < 10]
            if len(recent) > 100:
                alerts.append({
                    "type": "RAPID_FIRE_QUERIES",
                    "user": record.db_user,
                    "count_in_10s": len(recent),
                })

        return alerts


# Demo
detector = AnomalyDetector(known_ips={"app_service": {"10.0.1.5"}})

suspicious_records = [
    AuditRecord("SELECT", "users", "admin", None, list(range(50000)),
                "SELECT * FROM users", "198.51.100.99",    # New IP
                timestamp=time.time() - 3600 * 14),         # 2 AM UTC
    AuditRecord("DELETE", "orders", "app_service", "acme", list(range(500)),
                "DELETE FROM orders WHERE ...", "10.0.1.5"),
]

alerts = detector.analyze(suspicious_records)
for a in alerts:
    print(f"🚨 {a['type']}: {a}")
