# GraphQL — Modern API Query Language

**Level:** L4-L5
**Time to read:** ~30 min

Strongly typed, flexible API query language with client-driven data fetching.

---

## ⚖️ GraphQL vs. REST

```
Feature              | GraphQL      | REST
─────────────────────|──────────────|────────────────────
Data Fetching        | Client-driven| Server-defined
Over-fetching        | No           | Yes (get all fields)
Under-fetching       | No           | Yes (need multiple calls)
Versioning           | Not needed   | v1, v2, v3 endpoints
Type Safety          | Strong       | Documents/guessing
Learning Curve       | Steeper      | Easier
Caching              | Harder       | Simple (HTTP)
Real-time            | Subscriptions| Polling or WebSocket

When GraphQL:
├─ Multiple clients (mobile, web, tv)
├─ Flexible data requirements
├─ Avoid versioning overhead
├─ Strong type system helpful
└─ Complex nested data

When REST:
├─ Simple CRUD operations
├─ Standard HTTP caching
├─ Team familiar with REST
├─ Public APIs (caching important)
└─ Stateless semantics
```

---

## 📝 Schema Design

### Basic Schema

```graphql
# Scalar types
scalar DateTime

# Enum
enum UserRole {
  ADMIN
  MODERATOR
  USER
}

# Type definition
type User {
  id: ID!                    # Non-null
  name: String!
  email: String!
  role: UserRole!
  createdAt: DateTime!
  posts: [Post!]!           # One-to-many
  friends: [User!]!         # Many-to-many
  profile: UserProfile      # Optional
}

type UserProfile {
  bio: String
  avatar: String
  followers: Int!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!             # Many-to-one
  comments: [Comment!]!
  likedBy: [User!]!
  publishedAt: DateTime!
}

type Comment {
  id: ID!
  content: String!
  author: User!
  post: Post!
  createdAt: DateTime!
}

# Query root
type Query {
  user(id: ID!): User
  users(limit: Int, offset: Int): [User!]!
  posts(authorId: ID, limit: Int): [Post!]!
}

# Mutation root
type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): Boolean!
  createPost(input: CreatePostInput!): Post!
}

# Input types (for mutations)
input CreateUserInput {
  name: String!
  email: String!
  role: UserRole
}

input UpdateUserInput {
  name: String
  email: String
  role: UserRole
}

input CreatePostInput {
  title: String!
  content: String!
  authorId: ID!
}

# Subscription (real-time)
type Subscription {
  postCreated: Post!
  userCommented(postId: ID!): Comment!
}
```

---

## 🎯 Query Examples

### Over-fetching Prevention

```graphql
# REST: GET /api/users/123
# Returns ALL fields (over-fetching)
{
  id: "123",
  name: "Alice",
  email: "alice@example.com",
  createdAt: "2024-01-01",
  updatedAt: "2024-05-22",
  role: "USER",
  bio: "...",
  avatar: "...",
  followers: 1000,
  following: 500,
  posts: [...]  # Even this!
}

# GraphQL: Only request needed fields
query GetUserProfile($userId: ID!) {
  user(id: $userId) {
    name
    email
  }
}

# Response (only requested fields)
{
  "data": {
    "user": {
      "name": "Alice",
      "email": "alice@example.com"
    }
  }
}
```

### Under-fetching Prevention

```graphql
# REST: Multiple calls needed
GET /api/users/123        → {user data}
GET /api/users/123/posts  → {posts}
GET /api/users/123/friends → {friends}
Total: 3 requests

# GraphQL: Single query
query GetUserComplete($userId: ID!) {
  user(id: $userId) {
    name
    email
    posts(limit: 10) {
      title
      publishedAt
    }
    friends(limit: 5) {
      name
      email
    }
  }
}

# All data in 1 request
```

---

## 🔄 Resolvers

### Basic Resolvers

```javascript
const resolvers = {
  Query: {
    user: (parent, args, context) => {
      // parent = undefined (root)
      // args = {id: "123"}
      // context = {db, auth, ...}
      return context.db.users.findById(args.id);
    },
    users: (parent, args, context) => {
      return context.db.users.find({})
        .limit(args.limit)
        .offset(args.offset);
    }
  },
  User: {
    posts: (parent, args, context) => {
      // parent = {id: "123", name: "Alice", ...}
      return context.db.posts.find({authorId: parent.id});
    },
    friends: (parent, args, context) => {
      return context.db.users.find({_id: {$in: parent.friendIds}});
    }
  },
  Mutation: {
    createUser: (parent, args, context) => {
      const newUser = {
        id: generateId(),
        ...args.input,
        createdAt: new Date()
      };
      context.db.users.insert(newUser);
      return newUser;
    }
  }
};
```

### Context Pattern

```javascript
// Initialize context
const context = {
  db: database,
  auth: authService,
  dataloader: DataLoader,
  userId: req.user.id
};

// Use in resolver
Query: {
  me: (parent, args, context) => {
    // Access authenticated user
    return context.db.users.findById(context.userId);
  }
}
```

---

## ⚠️ Common Issues & Solutions

### N+1 Query Problem

```graphql
# Query: Get 100 users and their posts
query GetUsersWithPosts {
  users(limit: 100) {
    id
    name
    posts {
      title
    }
  }
}

Without optimization:
├─ Query users: 1 DB query
├─ Query posts for user 1: 1 DB query
├─ Query posts for user 2: 1 DB query
├─ ...
├─ Query posts for user 100: 1 DB query
└─ Total: 101 DB queries! (N+1 problem)

Solution: DataLoader (Batching)

const userLoader = new DataLoader(async (userIds) => {
  // userIds = [1, 2, 3, ...] (all users requested)
  // Fetch all posts in SINGLE query
  return db.posts.find({userId: {$in: userIds}});
});

User: {
  posts: (parent) => {
    return userLoader.load(parent.id);
  }
}

With DataLoader:
├─ Query users: 1 DB query
├─ Query all user posts: 1 batched DB query
└─ Total: 2 DB queries (optimal!)
```

### Deeply Nested Queries (DoS Risk)

```graphql
# Dangerous query (unbounded recursion)
query DeeplyNested {
  user {
    friends {
      friends {
        friends {
          friends {
            friends {  # How deep can it go?
              name
            }
          }
        }
      }
    }
  }
}

This can:
├─ Cause exponential DB queries: 5^5 = 3125 queries!
├─ Exhaust server resources
├─ Take minutes to execute
└─ Be used for DoS attacks

Solutions:

1. Depth Limit (Simple):
   ├─ Max 5 levels deep
   ├─ Server enforces in middleware
   ├─ Reject queries > depth
   └─ Easy to implement

2. Complexity Scoring (Better):
   ├─ Each field has complexity score
   ├─ Query total = 5 + 5×5 + 5×5×5 + ... = 3905
   ├─ Reject if > max (e.g., 1000)
   └─ More sophisticated

3. Timeout (Fallback):
   ├─ Kill query if > 5 seconds
   ├─ Return error to client
   └─ Prevents hanging

Implementation:
```javascript
// Depth limit
const maxDepth = 5;
function getQueryDepth(query) {
  return countSelections(query.selectionSet);
}
if (getQueryDepth(query) > maxDepth) {
  throw new Error('Query too deep');
}

// Complexity scoring
const complexityMap = {
  User: 1,
  friends: 3,    // Friends expensive
  posts: 2,      // Posts moderate
  comments: 2,   // Comments moderate
};
```
```

### Circular References

```graphql
# Circular reference:
# User → posts → author (User) → posts → author...

type User {
  posts: [Post!]!
}

type Post {
  author: User!     # Circular!
}

# Query can be written safely:
query Safe {
  user {
    posts {
      title
      author {
        name  # Stop here (no infinite recursion)
      }
    }
  }
}

# But this requires:
├─ Developer discipline
├─ GraphQL doesn't prevent it
└─ Only resolved when requested
```

---

## 🔐 Security Considerations

### Query Complexity & DoS
```javascript
// Rate limiting by complexity
const calculateComplexity = (query) => {
  // Field weights
  const weights = {
    user: 1,
    posts: 3,       (expensive query)
    comments: 2,
  };
  // Sum complexity of all fields
};

// Reject if too complex
if (calculateComplexity(query) > MAX_COMPLEXITY) {
  throw new Error('Query too complex');
}
```

### Authentication & Authorization
```javascript
// Middleware
const resolvers = {
  Query: {
    user: (parent, args, context) => {
      // Check authentication
      if (!context.auth.isAuthenticated) {
        throw new Error('Not authenticated');
      }
      // Check authorization
      if (!context.auth.canViewUser(args.id)) {
        throw new Error('Not authorized');
      }
      return context.db.users.findById(args.id);
    }
  }
};
```

---

## ❓ Comprehensive Interview Q&A

**Q: Design GraphQL schema for social network (users, posts, comments)**

A:
```graphql
# See schema design section above for complete example

Key decisions:
├─ Scalar types: DateTime for timestamps
├─ Enums: UserRole, PostStatus
├─ Input types: For mutations
├─ Relationships: User → Posts, User → Friends
├─ Query root: user, users, posts, feed
├─ Mutation root: create/update/delete operations
└─ Subscription: Real-time updates (optional)

Performance considerations:
├─ Pagination: users(limit, offset) or cursor-based
├─ Filtering: posts(authorId, published)
├─ Sorting: Not in schema, handle in resolver
└─ Caching: User agent must handle

Resolver patterns:
├─ DataLoader for N+1 prevention
├─ Context for authentication
├─ Error handling for consistency
└─ Monitoring for slow resolvers
```

**Q: How to prevent N+1 queries?**

A:
```
DataLoader implementation:

Step 1: Create loader
const postLoader = new DataLoader(async (userIds) => {
  // userIds = [1, 2, 3] (batched!)
  // Single DB query for all
  const posts = await db.query(
    'SELECT * FROM posts WHERE userId IN ($1)',
    [userIds]
  );
  // Return posts grouped by userId
  return userIds.map(id => posts.filter(p => p.userId === id));
});

Step 2: Use in resolver
User: {
  posts: (parent) => postLoader.load(parent.id)
}

Benefits:
├─ Single query for 100 users' posts
├─ Transparent to resolver code
├─ Works with circular references
└─ Automatic batching

Pitfall: Don't call DB directly in resolver
❌ BAD:
User: {
  posts: (parent) => db.posts.find({userId: parent.id})
}

✅ GOOD:
User: {
  posts: (parent) => postLoader.load(parent.id)
}
```

**Q: Cache strategy for GraphQL**

A:
```
Challenge: HTTP caching hard (POST requests)

Solutions:

1. Query Caching:
   ├─ Cache entire response by query string
   ├─ Invalidate on mutations
   ├─ Example: Cache GET /graphql?query=...

2. Field-level Caching:
   ├─ Cache user data (1 hour)
   ├─ Cache posts (30 minutes)
   ├─ Cache comments (5 minutes)
   ├─ In resolver:
     User: {
       posts: (parent, args, context) => {
         return context.cache.get(`posts:${parent.id}`, () =>
           db.posts.find({userId: parent.id})
         );
       }
     }

3. CDN:
   ├─ Persisted queries (hash instead of full query)
   ├─ Cache by query hash
   ├─ Reduces query size, enables caching

4. DataLoader:
   ├─ Request-level cache
   ├─ Prevents N+1 in single request
   ├─ Cleared on each request

Recommendation:
├─ Use DataLoader for N+1 prevention
├─ Cache expensive fields (1-hour TTL)
├─ Invalidate on mutations
├─ Use persisted queries for CDN caching
```

---

## 💡 Interview Tips

**What interviewer is really asking:**
- "GraphQL schema design" → Do you understand types, relationships, inputs?
- "N+1 problem" → Do you know DataLoader, batching?
- "Security" → Do you think about complexity limits, DoS?
- "Caching" → Do you understand field-level vs. query caching?

**How to answer:**
1. **Schema:** Types, relationships, query/mutation root
2. **Resolver:** Implementation, authentication, error handling
3. **Performance:** DataLoader for N+1, pagination, complexity limits
4. **Security:** Authorization, DoS prevention, input validation
5. **Caching:** Field-level caching, DataLoader, persisted queries

---

**Last updated:** 2026-05-22

---

## ✅ Best Practices

**Pagination:** Always paginate lists
**Errors:** Consistent error handling
**Caching:** Set proper cache headers
**Validation:** Server-side validation

---

## ❓ Interview Q&A

**Q: Design GraphQL API for social app**
A: User, Post, Comment types. Resolve N+1 with DataLoader. Paginate feeds. Add error handling.

**Q: How to prevent deeply nested queries?**
A: Depth limit, complexity scoring, timeout.

---

**Last updated:** 2026-05-22
