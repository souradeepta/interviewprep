# Database Security & Encryption

Protect sensitive data with encryption, access control, and audit logging.

---

## ⚖️ Encryption Strategy Trade-offs

| Method | Performance | Security | Key Management | Cost |
|--------|-------------|----------|---|---|
| **At rest** | None | Medium | Cloud provider | Low |
| **In transit (TLS)** | Minimal | High | Cert management | Low |
| **End-to-end** | High | Very High | Complex | High |
| **Column-level** | Medium | High | App-managed | Medium |

---

## 🏗️ Security Patterns

### Pattern 1: Encryption at Rest

```
Database stored on disk encrypted:
  
Unencrypted: user_data.bin = [raw bytes]
Encrypted: user_data.bin = [encrypted bytes]
           
When accessed, database decrypts automatically
(key stored in key management service)

Protects against: Stolen drives, backup breaches
Cost: <1% performance
```

### Pattern 2: Encryption in Transit (TLS)

```
Database connections encrypted:
  
App → [TLS tunnel] → Database
      (encrypted traffic)

Protects against: Network eavesdropping
Cost: 2-5% latency increase
```

### Pattern 3: Row-level Access Control

```
User A can see:
  SELECT * FROM orders WHERE user_id = A

User B can see:
  SELECT * FROM orders WHERE user_id = B

Database enforces (not app):
  CREATE POLICY user_isolation ON orders
  USING (user_id = current_user_id)
```

---

## ❓ Interview Q&A

**Q1: Encrypt PII (email, SSN) - design**

A:
- Solution: Column-level encryption
  1. Identify PII columns (email, ssn, card)
  2. Encrypt with AES-256 before storing
  3. Decrypt on read (app-side or DB-side)
  4. Store key in KMS (AWS, GCP, Azure)
  
- Trade-offs:
  - Can't index encrypted columns (unhashed)
  - Decryption overhead
  - Benefits: Compliance, audit trail

**Q2: Database credentials leaked - containment**

A:
- Immediate:
  1. Rotate credentials (new password)
  2. Revoke old token
  3. Check logs (who accessed what)
  
- Prevention:
  1. Store creds in secret manager, not code
  2. Rotate quarterly
  3. Audit all access

---

**Last updated:** 2026-05-22
