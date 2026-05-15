# Command Pattern

## Overview
Encapsulates request as object, allowing parametrization and queuing.

## Problem Statement
Want to decouple object that invokes operation from object that performs it. Need to queue requests, undo/redo, log requests.

## Solution
Encapsulate request as command object. Command object contains receiver and operation.

## When to Use

**Use Command when:**
- Decouple requester from executor (MVC architecture)
- Queue requests (batch processing, scheduling)
- Undo/redo functionality
- Macro commands (sequence of commands)
- Logging/persistence of operations

**Examples:**
- GUI buttons (each button is command)
- Text editor undo/redo stack
- Job queue (commands executed later)
- Macro systems (record and replay commands)
- Transaction logs (persist operations)

## Real-World Scenarios

**Text Editor Undo/Redo:**
```
User types: creates TypeCommand
User deletes: creates DeleteCommand
User pastes: creates PasteCommand
Stack commands in history
Undo: pop command, execute inverse
Redo: pop from undo stack, re-execute
```

**Button Commands:**
```
Save button: executes SaveCommand
Open button: executes OpenCommand
Print button: executes PrintCommand
Each command knows what to do when clicked
```

## Implementation Patterns

### Command with Undo
```python
class Command:
    def execute(self):
        pass

    def undo(self):
        pass

class AddCommand(Command):
    def __init__(self, receiver, value):
        self.receiver = receiver
        self.value = value

    def execute(self):
        self.receiver.add(self.value)

    def undo(self):
        self.receiver.remove(self.value)

class Invoker:
    def __init__(self):
        self.history = []

    def execute_command(self, command):
        command.execute()
        self.history.append(command)

    def undo(self):
        if self.history:
            command = self.history.pop()
            command.undo()

# Usage
receiver = List()
invoker = Invoker()

invoker.execute_command(AddCommand(receiver, 5))
invoker.execute_command(AddCommand(receiver, 10))
invoker.undo()  # Removes 10
```

## Trade-Offs

**Pros:**
- Decouple invoker from executor
- Support undo/redo
- Queue/schedule operations
- Compose commands (macro)
- Log operations (persistence)

**Cons:**
- Many command classes (can proliferate)
- Extra indirection (performance)
- Complex state management (undo with shared state)
- Memory overhead (command history)

## Production Considerations

- Limit undo history (memory constraints)
- Handle undo conflicts (what if state changed externally?)
- Macro commands: group related commands
- Serialize commands (persistence, replication)
- Test undo/redo extensively (edge cases)
