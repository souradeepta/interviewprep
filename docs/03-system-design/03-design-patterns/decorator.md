# Decorator Pattern

**Level:** L4
**Time to read:** ~15 min

## Problem Statement

You have an HTTP handler function. You need to add authentication, rate limiting, and logging — but not always in the same combination. Subclassing creates a combinatorial explosion (`AuthLoggingHandler`, `RateLimitAuthHandler`, etc.). Decorator wraps objects in layers at runtime, composing behavior without modifying the original class or creating a subclass for every combination.

## Structure

```
  Component (interface)
  ┌─────────────────────┐
  │ + handle(request)   │
  └─────────────────────┘
           ▲
  ┌────────┴────────────────────────────┐
  │                                     │
ConcreteHandler              BaseDecorator
(actual logic)               ┌──────────────────────────┐
                             │ - wrapped: Component      │
                             │ + handle(request)         │──► delegates to wrapped
                             └──────────────────────────┘
                                       ▲
                          ┌────────────┼────────────┐
                          │            │             │
                    AuthDecorator  RateLimit    LogDecorator
                    (checks token) Decorator   (logs timing)

  Composed at runtime (outermost first):
  LogDecorator
    └─► RateLimitDecorator
          └─► AuthDecorator
                └─► ConcreteHandler
```

## Python Implementation

```python
from abc import ABC, abstractmethod
from time import time
from functools import wraps
from typing import Callable
import threading

# --- Object-oriented Decorator (GoF pattern) ---

class Handler(ABC):
    @abstractmethod
    def handle(self, request: dict) -> dict:
        pass

class APIHandler(Handler):
    def handle(self, request: dict) -> dict:
        return {"status": 200, "data": f"Hello, {request.get('user', 'world')}"}

class HandlerDecorator(Handler):
    def __init__(self, wrapped: Handler):
        self._wrapped = wrapped

    def handle(self, request: dict) -> dict:
        return self._wrapped.handle(request)

class AuthDecorator(HandlerDecorator):
    VALID_TOKENS = {"token-abc", "token-xyz"}

    def handle(self, request: dict) -> dict:
        token = request.get("token")
        if token not in self.VALID_TOKENS:
            return {"status": 401, "error": "Unauthorized"}
        return self._wrapped.handle(request)

class RateLimitDecorator(HandlerDecorator):
    def __init__(self, wrapped: Handler, max_per_minute: int = 60):
        super().__init__(wrapped)
        self._max = max_per_minute
        self._counts: dict[str, list] = {}
        self._lock = threading.Lock()

    def handle(self, request: dict) -> dict:
        ip = request.get("ip", "unknown")
        now = time()
        with self._lock:
            calls = [t for t in self._counts.get(ip, []) if now - t < 60]
            if len(calls) >= self._max:
                return {"status": 429, "error": "Rate limit exceeded"}
            calls.append(now)
            self._counts[ip] = calls
        return self._wrapped.handle(request)

class LogDecorator(HandlerDecorator):
    def handle(self, request: dict) -> dict:
        start = time()
        response = self._wrapped.handle(request)
        elapsed_ms = (time() - start) * 1000
        print(f"[Log] {request.get('ip')} → status={response['status']} ({elapsed_ms:.1f}ms)")
        return response

# Compose the middleware stack — order matters!
handler = LogDecorator(
    RateLimitDecorator(
        AuthDecorator(APIHandler()),
        max_per_minute=100
    )
)

print(handler.handle({"ip": "1.2.3.4", "token": "token-abc", "user": "Alice"}))
print(handler.handle({"ip": "1.2.3.4", "token": "bad-token"}))

# --- Python's @decorator syntax (function decorator = same pattern) ---
def require_auth(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapper(request: dict, *args, **kwargs):
        if request.get("token") not in {"token-abc"}:
            return {"status": 401, "error": "Unauthorized"}
        return fn(request, *args, **kwargs)
    return wrapper

@require_auth
def get_profile(request: dict) -> dict:
    return {"user": request.get("user")}
```

## Real-World Uses

- **Python `@functools.wraps` / `@lru_cache`:** `lru_cache` wraps a function in a caching decorator, preserving the original signature — classic GoF Decorator using Python's function syntax.
- **Flask/FastAPI middleware:** `@app.before_request` and `@app.after_request` hooks compose auth, CORS, compression as decorators on the request pipeline.
- **Java I/O streams:** `new BufferedReader(new InputStreamReader(new FileInputStream("file")))` — each wraps the previous, adding buffering, character decoding, file access as layers.
- **Django REST Framework permissions:** `@permission_classes([IsAuthenticated, IsAdminUser])` stacks permission checks as decorators on view functions.

## When to Apply

**Apply Decorator when:**
- You need to add behavior to objects dynamically, without subclassing
- Different combinations of features are needed (auth + logging but not rate limiting)
- You want to respect Open/Closed: extend behavior without modifying original class
- You're building middleware, pipelines, or plugin systems

**Do NOT use when:**
- The decorator stack becomes deeply nested and hard to debug — consider a pipeline/chain instead
- You need to add behavior to all instances of a class permanently — modify the class directly or use a mixin
- Order of decoration matters but isn't enforced — document or enforce ordering explicitly
- Python function decorators are all you need — don't create a full class hierarchy for simple wrappers

## Common Interview Questions

**Q1. What's the difference between Decorator and Inheritance for adding behavior?**
Inheritance adds behavior at compile time for all instances of a subclass. Decorator adds behavior to specific object instances at runtime. Decorator avoids the subclass explosion when you have N features that can combine in 2^N ways.

**Q2. How does Python's `@decorator` syntax relate to the GoF Decorator pattern?**
It's the same concept applied to functions. `@lru_cache def f(): ...` is equivalent to `f = lru_cache(f)` — `lru_cache` returns a wrapper object that delegates to `f`. The difference is Python decorators usually wrap callables, not class instances.

**Q3. How do you preserve function metadata through decorators?**
Use `@functools.wraps(fn)` inside the wrapper. Without it, `wrapper.__name__` becomes `"wrapper"` instead of the original function name, breaking introspection, logging, and docs.

**Q4. Design a caching decorator with TTL.**
```python
from time import time
def ttl_cache(seconds: int):
    def decorator(fn):
        cache = {}
        @wraps(fn)
        def wrapper(*args):
            key = args
            if key in cache and time() - cache[key][1] < seconds:
                return cache[key][0]
            result = fn(*args)
            cache[key] = (result, time())
            return result
        return wrapper
    return decorator

@ttl_cache(seconds=60)
def get_user(user_id: int): ...
```

**Q5. How does Decorator differ from Proxy?**
Both wrap an object. Proxy controls access (caching, security, lazy loading) and usually has the same interface as the real subject. Decorator adds/extends behavior and is typically stackable. A caching proxy returns cached results without calling the real object; a caching decorator adds caching to the existing call chain.

## Related Patterns

- **Proxy:** Same wrapper structure, different intent — Proxy controls access, Decorator extends behavior.
- **Chain of Responsibility:** Similar chaining, but each handler decides whether to pass the request on. Decorator always delegates.
- **Composite:** Treats individual objects and compositions uniformly; Decorator wraps one object with additional behavior.
- See `docs/03-system-design/03-design-patterns/14_decorator.md` for I/O stream and middleware examples with benchmarks.
