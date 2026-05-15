# Memento Pattern

## Overview
Captures and externalizes object's internal state without violating encapsulation.

## Problem Statement
Need to save/restore object state (undo, snapshots). Can't expose internal structure.

## Solution
Create memento object containing state. Originator creates memento, caretaker stores it.

## When to Use

**Use Memento when:**
- Save/restore object state (undo/redo, snapshots)
- Can't expose internal structure (encapsulation)
- Need multiple save points
- Transaction rollback

**Examples:**
- Text editor undo/redo (save text state at each keystroke)
- Game save/load (save game state)
- Database transaction rollback (save state, rollback on error)
- Form undo (save form state, restore on cancel)

## Real-World Scenarios

**Game Save/Load:**
```
Game state: player position, health, inventory, level
Save game: memento captures entire state
Load game: restore from memento
Multiple save slots: multiple mementos
```

**Text Editor:**
```
Each keystroke creates memento
Undo: restore previous memento
Redo: restore next memento
Limited history: keep last 100 mementos
```

## Implementation Patterns

### Memento Pattern
```python
class Memento:
    def __init__(self, state):
        self.state = state

class Originator:
    def __init__(self):
        self.state = None

    def set_state(self, state):
        self.state = state

    def save_memento(self):
        return Memento(self.state)

    def restore_memento(self, memento):
        self.state = memento.state

class Caretaker:
    def __init__(self):
        self.history = []

    def save(self, originator):
        self.history.append(originator.save_memento())

    def restore(self, originator, index):
        originator.restore_memento(self.history[index])

# Usage
originator = Originator()
caretaker = Caretaker()

originator.set_state("State 1")
caretaker.save(originator)

originator.set_state("State 2")
caretaker.save(originator)

originator.set_state("State 3")
# Restore to state 2
caretaker.restore(originator, 1)
print(originator.state)  # State 2
```

## Trade-Offs

**Pros:**
- Preserves encapsulation (internal state hidden)
- Save/restore state cleanly
- Undo/redo support
- Multiple save points

**Cons:**
- Memory overhead (storing state copies)
- Performance (copying large state)
- Serialization complexity (complex objects)
- Versioning (state format changes)

## Production Considerations

- Limit memento history (memory constraints)
- Compress old mementos (save space)
- Handle state evolution (version mementos)
- Lazy snapshots (defer copy until modified)
- Serialize mementos (persistence, replication)
