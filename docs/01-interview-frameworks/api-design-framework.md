# API Design Framework: REST, GraphQL, & RPC

**Level:** L4-L5
**Time to read:** ~20 min

Comprehensive guide to designing APIs that scale, are maintainable, and follow industry standards.

---

## API Design Decision Tree

```mermaid
graph TD
    A["What type of API?"] --> B{"Client types?"}
    
    B -->|Web browser<br/>Mobile app<br/>Third-party| C["REST API<br/>HTTP endpoints"]
    B -->|Real-time<br/>Complex queries<br/>Multiple clients| D["GraphQL<br/>Query language"]
    B -->|Internal services<br/>High performance| E["gRPC<br/>Protocol buffers"]
    B -->|Simple RPC<br/>Legacy system| F["JSON-RPC<br/>XML-RPC"]
    
    C --> C1["Design with REST principles"]
    D --> D1["Design schema with types"]
    E --> E1["Design protocol buffer"]
    F --> F1["Design method contracts"]
    
    style C fill:#4287f5,color:#fff
    style D fill:#42c742,color:#fff
    style E fill:#ff9800,color:#000
```

---

## REST API Design

### Core Principles

**Resource-Oriented:**
- Identify resources (users, posts, comments)
- Each resource has a unique URL
- Example: `/users/{id}`, `/posts`, `/comments/{id}`

**Standard HTTP Methods:**
- **GET** → Read (idempotent)
- **POST** → Create (not idempotent)
- **PUT** → Replace entire resource
- **PATCH** → Partial update
- **DELETE** → Remove (idempotent)

**Status Codes:**
- `200 OK` → Success, response has body
- `201 Created` → Resource created, include Location header
- `204 No Content` → Success, no body
- `400 Bad Request` → Client error in request
- `401 Unauthorized` → Missing/invalid auth
- `403 Forbidden` → Authenticated but no permission
- `404 Not Found` → Resource doesn't exist
- `409 Conflict` → Conflict (e.g., duplicate key)
- `429 Too Many Requests` → Rate limited
- `500 Internal Server Error` → Server error

### REST API Design Template

```
# User API

## Create User
POST /api/v1/users
Content-Type: application/json

Request:
{
  "name": "Alice",
  "email": "alice@example.com",
  "role": "admin"
}

Response: 201 Created
Location: /api/v1/users/123
{
  "id": 123,
  "name": "Alice",
  "email": "alice@example.com",
  "role": "admin",
  "created_at": "2024-01-15T10:30:00Z"
}

## Get User
GET /api/v1/users/{id}

Response: 200 OK
{
  "id": 123,
  "name": "Alice",
  ...
}

## Update User (Partial)
PATCH /api/v1/users/{id}
Content-Type: application/json

Request:
{
  "role": "user"
}

Response: 200 OK
{
  "id": 123,
  "name": "Alice",
  "role": "user",
  ...
}

## Delete User
DELETE /api/v1/users/{id}

Response: 204 No Content

## List Users
GET /api/v1/users?page=1&limit=20&filter=active

Response: 200 OK
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 500
  }
}
```

### REST Best Practices

| Practice | Example |
|----------|---------|
| **Use nouns, not verbs** | ✓ `/users/{id}/posts` not `✗ /getUser/{id}` |
| **Plural resource names** | ✓ `/users` not `✗ /user` |
| **Versioning in URL** | ✓ `/api/v1/users` or in header `Accept: application/vnd.api+json;version=1` |
| **Consistent naming** | ✓ `created_at` or `createdAt` (pick one and stick) |
| **Pagination for lists** | ✓ `?page=2&limit=50` or cursor-based `?cursor=abc123` |
| **Filtering & sorting** | ✓ `?filter=active&sort=name&order=asc` |
| **Sparse fieldsets** | ✓ `?fields=id,name,email` (return only these) |
| **Idempotent POST** | Use idempotency key in header for retry safety |

### REST Error Response Format

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "User email is required",
    "details": {
      "field": "email",
      "reason": "required"
    }
  }
}
```

---

## GraphQL API Design

### Core Concepts

**Schema:**
```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
  createdAt: DateTime!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  comments: [Comment!]!
}

type Query {
  user(id: ID!): User
  users(first: Int, after: String): UserConnection!
  posts: [Post!]!
}

type Mutation {
  createUser(name: String!, email: String!): User!
  updateUser(id: ID!, name: String): User
  deleteUser(id: ID!): Boolean!
}

type Subscription {
  userCreated: User!
  postLiked(postId: ID!): LikeEvent!
}
```

**Query Example:**
```graphql
query GetUserWithPosts {
  user(id: "123") {
    name
    email
    posts {
      title
      comments {
        content
        author {
          name
        }
      }
    }
  }
}
```

### GraphQL Best Practices

| Practice | Rationale |
|----------|-----------|
| **Nullable vs Non-nullable** | `String!` = required. `[Post!]!` = non-empty list of posts. Pick carefully. |
| **Global object ID** | Every object has `id: ID!` for consistency |
| **Connections for pagination** | Use `UserConnection` with edges/cursor for Relay-style pagination |
| **Batch queries to avoid N+1** | Use dataloader to batch database queries |
| **Scalar types** | `DateTime`, `JSON`, `URL` for custom types |
| **Input types for mutations** | `input CreateUserInput { name: String! }` instead of 10 params |
| **Deprecation** | Mark old fields with `@deprecated(reason: "Use newField")` |

### GraphQL vs REST

| Aspect | GraphQL | REST |
|--------|---------|------|
| **Over-fetching** | Avoid (request only needed fields) | Common (get all fields) |
| **Under-fetching** | Avoid (single query for related data) | Common (need multiple requests) |
| **Caching** | Harder (single endpoint) | Easy (cache by URL) |
| **Complexity** | Higher (need to optimize queries) | Simple (straightforward) |
| **Real-time** | Subscriptions built-in | Requires WebSocket + polling |

---

## gRPC API Design

### Protocol Buffer Schema

```protobuf
syntax = "proto3";

package api.v1;

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc CreateUser(CreateUserRequest) returns (User);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
}

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
  int64 created_at = 4;  // Unix timestamp
}

message GetUserRequest {
  int64 id = 1;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message ListUsersRequest {
  int32 page = 1;
  int32 limit = 2;
}

message ListUsersResponse {
  repeated User users = 1;
  int32 total = 2;
}
```

### gRPC Best Practices

| Practice | Rationale |
|----------|-----------|
| **Use int64 for IDs** | Avoid overflow issues |
| **Unix timestamps** | Language-agnostic for dates |
| **Repeated for lists** | `repeated User users` for array |
| **Well-known types** | Use `google.protobuf.Timestamp` for dates |
| **Backwards compatible** | Only add fields, never remove. New clients/old servers should work. |
| **Service versioning** | `package api.v1` in schema |

### When to Use Each API Type

| API Type | Best For | Example |
|----------|----------|---------|
| **REST** | Web, mobile, public APIs, simple CRUD | Twitter API, GitHub API |
| **GraphQL** | Complex data relationships, real-time, flexible queries | Shopify, GitHub GraphQL |
| **gRPC** | Internal services, high performance, microservices | Payment processing, messaging |
| **Webhook** | Event notifications, asynchronous | GitHub webhooks, Stripe events |

---

## API Versioning Strategy

### URL-Based Versioning

```
GET /api/v1/users
GET /api/v2/users
```

**Pros:** Easy to understand, explicitly shows version
**Cons:** Duplicate code between versions, maintenance burden

### Header-Based Versioning

```
GET /api/users
Accept: application/vnd.api+json;version=2
```

**Pros:** Single URL, cleaner
**Cons:** Harder to test, not obvious which version

### Deprecation Strategy

```
1. Release new endpoint (/api/v2)
2. Mark old endpoint as deprecated (6 months notice)
3. In headers: Deprecation: true, Sunset: 2024-12-31
4. Sunset period: clients must migrate
5. Remove old endpoint
```

---

## API Security

### Authentication

**API Key:**
```
Authorization: Bearer sk_live_abcd1234efgh5678
```

**OAuth 2.0:**
```
Authorization: Bearer {access_token}
```

**mTLS (Internal):**
- Client certificate validation

### Authorization

```python
# Check scope/permission
if 'write:users' not in request.auth.scopes:
    return 403 Forbidden
```

### Rate Limiting Headers

```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1234567890
```

### CORS (Cross-Origin)

```
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, PUT
Access-Control-Allow-Credentials: true
```

---

## API Documentation

### Minimum Documentation

- Resource schemas (what fields, types)
- Endpoints (method, path, parameters)
- Response examples
- Error codes explained
- Rate limits
- Authentication method
- Changelog/deprecation notices

### Tools

- **OpenAPI/Swagger** → Interactive REST docs
- **GraphQL Playground** → Interactive GraphQL explorer
- **Postman** → API testing and documentation
- **Stripe/GitHub docs** → Gold standard for clarity

---

## API Design Checklist

- ✓ Resource-oriented (nouns, not verbs)
- ✓ Consistent naming (camelCase or snake_case)
- ✓ Proper HTTP methods and status codes
- ✓ Pagination for list endpoints
- ✓ Filtering and sorting support
- ✓ Versioning strategy documented
- ✓ Error responses have codes and messages
- ✓ Authentication and authorization clear
- ✓ Rate limiting documented
- ✓ Deprecation timeline for breaking changes
- ✓ Examples for each endpoint
- ✓ Performance characteristics documented
- ✓ Backward compatibility in new versions

