# Builder Pattern

## Overview
Constructs complex objects step by step. Separates construction from representation.

## Problem Statement
Objects have many optional parameters. Constructors become unwieldy (telescoping constructor anti-pattern). Want to build objects incrementally with clear steps.

## Solution
Use builder to construct object step by step. Fluent interface for readability.

## When to Use

**Use Builder when:**
- Objects have many optional parameters (readable API)
- Complex construction with multiple steps (logical separation)
- Same construction process creates different representations (variations)
- Want immutable objects (set all fields before building)

**Examples:**
- HTTP request building: method, headers, body, timeout, retries
- SQL query building: SELECT, FROM, WHERE, ORDER BY, LIMIT
- Configuration objects: many settings, most optional
- HTML DOM building: nested elements with attributes

## Real-World Scenarios

**HTTP Request Builder:**
```
HttpRequest req = new HttpRequest.Builder()
    .method("GET")
    .url("https://api.example.com/users")
    .header("Authorization", "Bearer token")
    .timeout(5000)
    .retries(3)
    .build();

Clear what's being configured.
Optional parameters have defaults.
```

**Query Builder (SQL):**
```
Query query = new Query.Builder()
    .select("name", "email")
    .from("users")
    .where("age > 18")
    .orderBy("name")
    .limit(10)
    .build();

Builds SQL dynamically.
Each step is clear.
```

## When NOT to Use

**Avoid when:**
- Few parameters (constructor fine)
- All parameters required (no benefit over constructor)
- Simple immutable objects (overhead)

## Implementation Patterns

### Fluent Builder
```python
class User:
    def __init__(self, name, email, age, role, active):
        self.name = name
        self.email = email
        self.age = age
        self.role = role
        self.active = active

class UserBuilder:
    def __init__(self):
        self.name = None
        self.email = None
        self.age = None
        self.role = "user"
        self.active = True

    def with_name(self, name):
        self.name = name
        return self

    def with_email(self, email):
        self.email = email
        return self

    def with_age(self, age):
        self.age = age
        return self

    def with_role(self, role):
        self.role = role
        return self

    def build(self):
        return User(self.name, self.email, self.age,
                   self.role, self.active)

# Usage
user = UserBuilder()     .with_name("Alice")     .with_email("alice@example.com")     .with_age(30)     .build()
```

### Inner Builder (Java)
```java
public class Request {
    public static class Builder {
        private String url;
        private String method = "GET";
        private Map<String, String> headers = new HashMap<>();

        public Builder url(String url) {
            this.url = url;
            return this;
        }

        public Builder method(String method) {
            this.method = method;
            return this;
        }

        public Builder header(String key, String value) {
            headers.put(key, value);
            return this;
        }

        public Request build() {
            return new Request(url, method, headers);
        }
    }
}

// Usage
Request req = new Request.Builder()
    .url("https://api.example.com")
    .method("POST")
    .header("Content-Type", "application/json")
    .build();
```

## Trade-Offs

**Pros:**
- Readable API (clear construction steps)
- Handles optional parameters elegantly
- Immutable objects (once built)
- Different representations from same process

**Cons:**
- More classes (builder + object)
- Overhead for simple objects
- Extra memory during construction

## Production Considerations

- Use builder for complex objects (API requests, configs)
- Make builders thread-safe if needed (synchronized or thread-local)
- Consider default values (what should be preset)
- Validate state in build() method (not during construction)
- Document required vs. optional parameters
