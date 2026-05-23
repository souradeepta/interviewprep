# GraphQL — Modern API Query Language

Building flexible APIs.

---

## 📝 Schema Design

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!  # One-to-many
  friends: [User!]!  # Many-to-many
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
  posts(limit: Int): [Post!]!
}

type Mutation {
  createUser(name: String!, email: String!): User!
  createPost(title: String!, content: String!): Post!
}
```

---

## 🎯 Queries

```graphql
# Only request needed fields
{
  user(id: "123") {
    name
    email
    posts {
      title
      comments {
        content
      }
    }
  }
}
```

**Benefits:**
- No over-fetching (only get what you need)
- No under-fetching (one query gets all data)
- Client specifies shape of data

---

## 🔄 Resolvers

```javascript
const resolvers = {
  Query: {
    user: (parent, args) => {
      return db.users.findById(args.id);
    }
  },
  User: {
    posts: (parent) => {
      return db.posts.findByUserId(parent.id);
    }
  }
};
```

---

## ⚠️ Common Issues

### N+1 Problem

```graphql
# Query: Get 100 users and their posts

Without optimization:
- Query users: 1
- Query posts for each user: 100
- Total: 101 queries!

Solution:
- Batch query: Get all posts for 100 users in 1 query
- DataLoader: Automatically batch
```

### Deeply Nested Queries

```graphql
# Could cause expensive recursion
{
  user {
    friends {
      friends {
        friends {  # How deep?
          name
        }
      }
    }
  }
}

Solutions:
- Depth limit
- Complexity scoring
- Timeout
```

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
