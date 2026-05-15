# Flyweight Pattern

## Overview
Uses sharing to support large numbers of fine-grained objects efficiently.

## Problem Statement
Creating many similar objects causes memory bloat. Objects share common state.

## Solution
Separate intrinsic (shared) state from extrinsic (per-object) state. Share intrinsic state via flyweight pool.

## When to Use

**Use Flyweight when:**
- Many similar objects causing memory issues
- Most state can be shared (intrinsic)
- Can externalize per-object state (extrinsic)
- Performance critical (memory savings important)

**Examples:**
- Text editor: characters share font, size, style (intrinsic); position is extrinsic
- Game: particles share sprite, behavior; position, velocity extrinsic
- Web browser: DOM nodes share tag type, properties; children extrinsic
- Database: connection pool reuses connections

## Real-World Scenarios

**Text Editor Characters:**
```
Million character document
Sharing: font object, style object, color object
Per-character: position, is_bold flag
Without sharing: 1M char objects × large size = huge memory
With sharing: 1M small objects + few shared objects
```

**Game Sprites:**
```
1000 particles (snow, rain)
Sharing: sprite image, animation frames
Per-particle: position, velocity, lifetime
Sharing reduces memory significantly
```

## Implementation Patterns

### Intrinsic/Extrinsic Separation
```python
class Flyweight:
    def __init__(self, intrinsic_state):
        self.intrinsic = intrinsic_state

    def operation(self, extrinsic_state):
        return f"{self.intrinsic} at {extrinsic_state}"

class FlyweightFactory:
    def __init__(self):
        self.pool = {}

    def get_flyweight(self, key):
        if key not in self.pool:
            self.pool[key] = Flyweight(key)
        return self.pool[key]

# Usage
factory = FlyweightFactory()
fw1 = factory.get_flyweight("shared_state")
fw2 = factory.get_flyweight("shared_state")
# fw1 and fw2 are same object (shared)

print(fw1.operation("position_a"))
print(fw2.operation("position_b"))
```

## Trade-Offs

**Pros:**
- Massive memory savings (if many objects)
- Performance improvement (less allocation)
- Centralized shared state (easier to manage)

**Cons:**
- Complex (intrinsic/extrinsic separation)
- CPU overhead (lookup in pool)
- Thread safety (shared state)
- Only worth if many objects

## Production Considerations

- Profile memory usage before optimizing (is it worth it?)
- Make intrinsic state immutable (thread safety)
- Use weak references if possible (garbage collect unused)
- Document intrinsic vs. extrinsic state clearly
- Consider cache eviction policy (what if pool too large?)
