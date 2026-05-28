# Security Fundamentals — Building Secure Systems

**Level:** L4-L5
**Time to read:** ~10 min

Essential security concepts for all engineers.

---

## 🔒 Core Principles

**Confidentiality:** Only authorized access (encryption)
**Integrity:** Data not tampered (hashing, signatures)
**Availability:** Service always accessible (DDoS protection)

---

## 🔐 Authentication vs. Authorization

### Authentication
"Who are you?" — Verify identity

```
Methods:
- Password: Username + password
- MFA: Password + phone code/authenticator
- OAuth: Delegate to Google/GitHub
- JWT: Self-contained tokens
- Biometric: Fingerprint, face
```

### Authorization
"Can you do this?" — Check permissions

```
Approaches:
- Role-based: User has admin/user/viewer role
- Attribute-based: Decisions based on attributes
- Access control lists: Explicit permissions

Example:
- Authentication: User logs in as alice
- Authorization: alice has viewer role, can't delete
```

---

## 🔑 Encryption

### Symmetric Encryption
Same key for encrypt/decrypt (AES)
- Fast, good for data at rest
- Challenge: Key distribution

### Asymmetric Encryption
Public/private key pair (RSA)
- Slower, good for key exchange
- Enables digital signatures

### TLS/SSL
Encryption for data in transit
```
Handshake: Exchange keys
Encrypted: All data encrypted
Certificate: Verify server identity
```

---

## 🛡️ Common Vulnerabilities

**SQL Injection:**
```
❌ query = f"SELECT * FROM users WHERE id={user_input}"
✅ query = "SELECT * FROM users WHERE id=?", params=[user_input]
```

**XSS (Cross-Site Scripting):**
```
Escape user input before displaying
```

**CSRF (Cross-Site Request Forgery):**
```
Validate request origin (same-site cookies, tokens)
```

**Password Storage:**
```
❌ Store plaintext
✅ Hash with bcrypt/argon2
```

---

## 🚨 Security Best Practices

**Defense in depth:** Multiple layers
**Least privilege:** Minimal necessary permissions
**Secure by default:** Secure settings out of the box
**Regular updates:** Patch vulnerabilities
**Monitoring:** Log suspicious activity
**Encryption:** Data at rest + in transit

---

## ❓ Interview Q&A

**Q: How would you secure an API?**
A: TLS, authentication (JWT/OAuth), authorization (roles), rate limiting, input validation, logging.

**Q: Difference between hashing and encryption?**
A: Hashing is one-way (passwords). Encryption is two-way (data protection).

**Q: How to prevent SQL injection?**
A: Use parameterized queries. Never concatenate user input into SQL.

---

**Last updated:** 2026-05-22
