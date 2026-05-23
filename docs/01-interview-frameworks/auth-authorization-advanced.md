# Authentication & Authorization — Advanced Patterns

Building secure identity systems.

---

## 🔑 Authentication Methods

### Password-Based

```
Pros: Simple, familiar
Cons: Users reuse passwords, forget them
Best practice: Hash with bcrypt/argon2, salt, pepper
```

### Multi-Factor Authentication (MFA)

```
Factor 1: Something you know (password)
Factor 2: Something you have (phone, hardware key)
Factor 3: Something you are (biometric)

Types:
- TOTP: Time-based (Google Authenticator)
- SMS: Text code
- Hardware key: Physical device (YubiKey)
- Push notification: App notification
```

### OAuth & OpenID Connect

```
OAuth: Delegate authentication to provider (Google, GitHub)
Flow:
1. User clicks "Login with Google"
2. Redirected to Google
3. User authorizes
4. Google redirects back with token
5. App verifies token with Google

Benefits: No passwords to store, SSO, phishing resistant
```

### JWT (JSON Web Tokens)

```json
Header: {"alg": "HS256"}
Payload: {"sub": "user123", "exp": 1234567890}
Signature: HMACSHA256(base64(header) + "." + base64(payload))

Stateless: No server session needed
Risk: Token can't be revoked easily (use short expiry)
```

---

## 👤 Authorization Patterns

### Role-Based Access Control (RBAC)

```
User → Role → Permissions
- User: alice
- Role: admin
- Permissions: read, write, delete
```

### Attribute-Based Access Control (ABAC)

```
Decision based on attributes:
- User attributes: department, level
- Resource attributes: classification, owner
- Environment: time, location

More fine-grained than RBAC
```

### Resource-Based Access Control

```
"Who can access this resource?"
Resource specifies permissions

Example:
- Document owner: can share
- Shared user: can view (read-only)
- Public: anyone can read
```

---

## 🔐 Session Management

### Cookie-Based Sessions

```
1. User logs in
2. Server creates session, stores in memory
3. Session ID in cookie
4. Browser sends cookie with each request

Pros: Familiar, works everywhere
Cons: Server-side storage, doesn't scale to 1000s of servers
```

### Token-Based Sessions (JWT)

```
1. User logs in
2. Server creates JWT with payload
3. Client stores token (localStorage, cookie)
4. Client sends token with each request

Pros: Stateless, scalable
Cons: Token can't be revoked instantly
```

---

## 🚨 Security Best Practices

**HTTPS Always:** Encrypt auth data in transit
**Short Expiry:** Tokens expire quickly (15 min)
**Refresh Tokens:** Long-lived token to get new access token
**Secure Cookies:** HTTPOnly (no JS access), Secure (HTTPS only), SameSite

---

## ❓ Interview Q&A

**Q: OAuth vs. JWT, when use each?**
A: OAuth for delegated auth (third-party login). JWT for stateless API auth. Often combined: OAuth to get JWT.

**Q: How to revoke a JWT token?**
A: Blacklist (track revoked tokens). Refresh token approach (short-lived JWTs). Short expiry (15 min).

**Q: Design authentication for microservices.**
A: Central auth service (OAuth/OIDC). Issue JWT. Verify JWT in each service. Shared key/certificate for verification.

---

**Last updated:** 2026-05-22
