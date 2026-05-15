# Bridge Pattern

## Overview
Decouples abstraction from implementation so they vary independently.

## Problem Statement
Class hierarchy explosion: different abstractions × different implementations. Changes propagate across hierarchy.

## Solution
Separate abstraction (high-level) from implementation (low-level). Let them vary independently.

## When to Use

**Use Bridge when:**
- Class hierarchy would explode (abstraction × implementation)
- Want to avoid permanent binding between abstraction and implementation
- Share implementation across multiple objects
- Changes in implementation shouldn't affect clients

**Examples:**
- UI widgets on different OS (abstraction: Button, implementation: Windows Button vs. Mac Button)
- Database drivers (abstraction: Database, implementation: MySQL vs. PostgreSQL)
- Graphics rendering (abstraction: Shape, implementation: OpenGL vs. DirectX)
- Device drivers (abstraction: Device, implementation: different hardware)

## Real-World Scenarios

**Cross-Platform UI:**
```
Abstract: Window, Button, Textbox
Implementation: WindowsRenderer, MacRenderer
Window delegates to renderer (bridge)
Button delegates to renderer
Same abstraction works on Windows or Mac
```

**Database Abstraction:**
```
Abstract: DatabaseConnection (query, insert, delete)
Implementation: MySQLDriver, PostgresDriver
Connection uses appropriate driver
Same client code on different databases
```

## Implementation Patterns

### Abstract with Implementor
```python
# Implementor (abstraction)
class Device:
    def on(self): pass
    def off(self): pass

class TV(Device):
    def on(self):
        return "TV is on"

class Radio(Device):
    def on(self):
        return "Radio is on"

# Abstraction
class RemoteControl:
    def __init__(self, device: Device):
        self.device = device

    def power_on(self):
        return self.device.on()

# Usage
tv = TV()
remote = RemoteControl(tv)
print(remote.power_on())  # TV is on
```

## Trade-Offs

**Pros:**
- Decouples abstraction from implementation
- Reduced class explosion
- Easy to add new abstractions or implementations
- Single responsibility (abstraction vs. implementation)

**Cons:**
- Extra indirection (complexity)
- Overkill for simple class hierarchies
- Requires upfront design (not for legacy code)

## Production Considerations

- Use when you know abstraction and implementation will vary
- Design abstraction/implementor interfaces carefully
- Document separation of concerns (what's abstraction, what's implementation)
- Test with multiple implementations
