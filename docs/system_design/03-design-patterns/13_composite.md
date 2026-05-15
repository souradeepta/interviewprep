# Composite Pattern

## Overview
Composes objects into tree structures. Clients treat individual and composite objects uniformly.

## Problem Statement
Need to represent part-whole hierarchies (trees). Want clients to treat individual and composite objects the same way.

## Solution
Create common interface for leaf and composite objects. Composites contain children.

## When to Use

**Use Composite when:**
- Object hierarchies (trees, menus, file systems)
- Clients should ignore difference between leaf and composite
- Recursive structure (part contains parts)
- Part-whole relationships

**Examples:**
- File system (directory contains files and directories)
- UI components (panel contains buttons, panels, textboxes)
- Menu systems (menu contains items and submenus)
- Organization structure (department contains employees and subdepartments)

## Real-World Scenarios

**File System:**
```
File: leaf node
Directory: composite, contains files and directories
Both have: name, size, delete()
Clients don't care: are they operating on file or directory?
```

**UI Component Tree:**
```
Button, Label: leaf
Panel, Window: composite
All have: render(), setVisible()
Render panel → renders all children recursively
```

## Implementation Patterns

### Component with Children
```python
class Component:
    def operation(self):
        pass

class Leaf(Component):
    def __init__(self, name):
        self.name = name

    def operation(self):
        return f"Leaf {self.name}"

class Composite(Component):
    def __init__(self, name):
        self.name = name
        self.children = []

    def add(self, child):
        self.children.append(child)

    def operation(self):
        results = [f"Composite {self.name}"]
        for child in self.children:
            results.append(f"  {child.operation()}")
        return "\n".join(results)

# Usage
root = Composite("Root")
root.add(Leaf("Leaf1"))
child = Composite("Child")
child.add(Leaf("Leaf2"))
root.add(child)
print(root.operation())
```

## Trade-Offs

**Pros:**
- Treat leaves and composites uniformly
- Easy to add new component types
- Clear tree structure
- Recursive structure elegant

**Cons:**
- Design too general (lost type safety)
- Extra indirection
- Leaf behavior restricted (can't have children)

## Production Considerations

- Consider immutability (once added to tree, don't move)
- Handle cycles (prevent parent being child of self)
- Consider copy/clone for tree manipulation
- Provide iteration utilities (traverse tree)
- Document tree constraints
