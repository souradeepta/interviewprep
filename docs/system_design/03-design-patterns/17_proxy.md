# Proxy Pattern

## Overview
Provides surrogate for another object to control access to it.

## Problem Statement
Need to control access to object (lazy loading, access control, logging). Creating object expensive or requires permissions.

## Solution
Create proxy with same interface. Proxy controls access to real object.

## When to Use

**Use Proxy when:**
- Control access (permissions, access control)
- Lazy initialization (defer expensive creation)
- Logging/monitoring access
- Cache expensive operations
- Remote object (network proxy)

**Examples:**
- Lazy-loaded images in documents
- Database access control (proxy checks permissions)
- Remote objects over network (RPC proxy)
- Caching proxy (remember previous results)
- Logging proxy (track all accesses)

## Real-World Scenarios

**Image Proxy (Lazy Loading):**
```
Document contains 100 images
Loading all images on startup is slow
ImageProxy loads image only when displayed
User scrolls to image → proxy loads it then
```

**Database Proxy (Access Control):**
```
Database requires authentication
DatabaseProxy checks credentials
If valid, delegates to real database
If invalid, throws PermissionDenied
```

## Implementation Patterns

### Protection/Access Control Proxy
```python
class Subject:
    def request(self):
        pass

class RealSubject(Subject):
    def request(self):
        return "RealSubject response"

class Proxy(Subject):
    def __init__(self, user_role):
        self.user_role = user_role
        self.real_subject = None

    def request(self):
        if self.user_role == "admin":
            if self.real_subject is None:
                self.real_subject = RealSubject()
            return self.real_subject.request()
        else:
            raise PermissionError("Access denied")

# Usage
admin_proxy = Proxy("admin")
print(admin_proxy.request())  # Works

user_proxy = Proxy("user")
# print(user_proxy.request())  # Raises PermissionError
```

### Virtual Proxy (Lazy Loading)
```python
class ExpensiveObject:
    def __init__(self):
        print("Creating expensive object...")

    def operation(self):
        return "Expensive operation result"

class Proxy:
    def __init__(self):
        self.real_object = None

    def operation(self):
        if self.real_object is None:
            self.real_object = ExpensiveObject()  # Create on first use
        return self.real_object.operation()

# Usage
proxy = Proxy()
# Object not created yet
result = proxy.operation()  # Creates object on demand
```

## Trade-Offs

**Pros:**
- Control access (security, permissions)
- Lazy loading (defer expensive operations)
- Transparency (same interface as real object)
- Add logging, caching, monitoring

**Cons:**
- Extra indirection (performance overhead)
- Complexity (another object to manage)
- May mask real object behavior
- Thread safety (shared proxy)

## Production Considerations

- Make proxy as transparent as possible (clients shouldn't notice)
- Consider thread safety (synchronize access)
- Document proxy type (protection, virtual, logging, etc.)
- Monitor proxy overhead (is it worth it?)
- Test proxy thoroughly (failure cases)
