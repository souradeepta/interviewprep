# API Design & REST Principles — Building Scalable Interfaces

**Level:** L4-L5
**Time to read:** ~10 min

Designing APIs that are intuitive, scalable, and maintainable.

---

## 🌐 REST Principles

**Resource-oriented:** URLs represent resources
```
GET /users/123
POST /users
PUT /users/123
DELETE /users/123
```

**Stateless:** Each request is independent
```
Server doesn't store client context
Information in request (token, body)
```

**Cacheable:** Responses can be cached
```
GET: Cacheable by default
POST: Not cacheable
```

---

## 📊 HTTP Status Codes

```
2xx: Success
- 200: OK
- 201: Created
- 204: No Content

3xx: Redirection
- 301: Moved Permanently
- 304: Not Modified

4xx: Client Error
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found

5xx: Server Error
- 500: Internal Error
- 503: Service Unavailable
```

---

## 📋 Request/Response Design

### Pagination

```
GET /users?page=1&limit=20

Response:
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1000
  }
}
```

### Filtering & Sorting

```
GET /users?status=active&sort=-created_at
```

### Versioning

```
Option 1: URL
/api/v1/users
/api/v2/users

Option 2: Header
Accept: application/vnd.api+json;version=1

Option 3: No versioning (backwards compatible)
```

---

## 🔑 Error Handling

```
✅ Good error response:
{
  "error": {
    "code": "INVALID_EMAIL",
    "message": "Email format is invalid",
    "status": 400
  }
}

❌ Bad:
{
  "error": "Invalid email"
}
```

---

## ⚡ Performance Considerations

**Pagination:** Avoid returning all data
**Filtering:** Let client specify fields
**Caching:** Cache headers, CDN
**Compression:** gzip responses
**Rate limiting:** Prevent abuse

---

## 🔐 Security

```
API Key: Simple, less secure
OAuth: Standard, more secure
JWT: Self-contained, no server lookup
mTLS: Mutual certificate verification
```

---

## ❓ Interview Q&A

**Q: Design an API for a social network.**
A: Define resources (users, posts, likes). Use REST principles. Pagination for feeds. Authentication (JWT). Rate limiting.

**Q: How to handle API versioning?**
A: Prefer URL versioning (explicit). Keep old versions 1+ years. Deprecation notices.

**Q: How to optimize API for mobile?**
A: Pagination, field selection, compression, caching, batch endpoints.

---

**Last updated:** 2026-05-22
