# Prototype Pattern

## Overview
Creates new objects by copying prototype rather than creating from scratch.

## Problem Statement
Creating objects is expensive (deep copy of complex state, expensive initialization). Want to clone existing objects efficiently.

## Solution
Make objects cloneable. Clone prototype instead of creating new.

## When to Use

**Use Prototype when:**
- Object creation is expensive (database queries, network calls)
- Need independent copies of complex objects
- Avoid subclassing for variations (clone and modify)
- Object state is large or complex (copy more efficient than recreate)

**Examples:**
- Clone database records (copy with modifications)
- Undo/redo system (store snapshots of state)
- Genetic algorithms (mutate copies of solutions)
- Caching: clone cached objects (prevent external modifications)

## Real-World Scenarios

**Document Cloning:**
```
User creates complex document with formatting, styles, content.
Clone document for versioning (creates independent copy).
Each version modified independently.
Original document unaffected.
```

**Configuration Snapshot:**
```
System has complex configuration object.
Clone configuration for testing (modify without affecting live).
Revert to prototype if test fails.
```

## When NOT to Use

**Avoid when:**
- Simple objects (constructor fine)
- Cloning complex (circular references, external resources)
- Performance not concern

## Implementation Patterns

### Python Clone
```python
import copy

class User:
    def __init__(self, name, email, roles):
        self.name = name
        self.email = email
        self.roles = roles  # list of roles

    def clone(self):
        return copy.deepcopy(self)

user1 = User("Alice", "alice@example.com", ["admin", "user"])
user2 = user1.clone()  # independent copy
user2.roles.append("superuser")
# user1.roles unchanged
```

### Prototype Registry
```python
class PrototypeRegistry:
    def __init__(self):
        self.prototypes = {}

    def register(self, key, prototype):
        self.prototypes[key] = prototype

    def clone(self, key):
        return self.prototypes[key].clone()

# Usage
registry = PrototypeRegistry()
registry.register("admin", User("admin", "admin@example.com", ["admin"]))
registry.register("user", User("user", "user@example.com", ["user"]))

# Create new users by cloning
new_admin = registry.clone("admin")
new_admin.name = "Alice"  # Independent object
```

## Trade-Offs

**Pros:**
- Efficient creation (copy cheap, creation expensive)
- Avoids subclassing (clone and modify)
- Works well with complex objects
- Supports snapshot/undo

**Cons:**
- Cloning complex (circular references, external resources)
- May copy unnecessary state (memory overhead)
- Shallow vs. deep copy considerations
- Not suitable for classes with external dependencies

## Production Considerations

- Use deep copy for complex objects (prevent shared references)
- Handle external resources carefully (database connections, file handles)
- Consider copy-on-write optimization (delay copy until modification)
- Document clone semantics (what's copied, what's shared)
- Test cloning thoroughly (nested objects, collections)
