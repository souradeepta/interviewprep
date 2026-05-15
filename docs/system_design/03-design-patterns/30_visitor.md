# Visitor Pattern

## Overview
Represents operation on elements without changing their classes.

## Problem Statement
Need to perform many different operations on objects in complex structure. Adding operations requires modifying many classes.

## Solution
Create visitor for each operation. Objects accept visitor.

## When to Use

**Use Visitor when:**
- Many unrelated operations on object structure
- Object classes rarely change, operations often change
- Want to avoid polluting classes with many operations
- Object structure complex (tree, graph)

**Examples:**
- AST (abstract syntax tree) operations (pretty-print, compile, optimize)
- File system operations (delete, copy, archive files and directories)
- Report generation from data structure
- Type checking in compiler

## Real-World Scenarios

**Compiler AST:**
```
Nodes: BinOp, UnOp, Literal
Operations: compile, optimize, print
Visitor: CompileVisitor, OptimizeVisitor, PrintVisitor
Each visitor knows how to handle each node type
Easy to add new operations
```

## Implementation Patterns

### Visitor Pattern Example
```python
class Visitor:
    pass

class Element:
    def accept(self, visitor):
        pass

class ConcreteElementA(Element):
    def accept(self, visitor):
        return visitor.visit_element_a(self)

class ConcreteElementB(Element):
    def accept(self, visitor):
        return visitor.visit_element_b(self)

class ConcreteVisitor(Visitor):
    def visit_element_a(self, element):
        return "Visiting A"

    def visit_element_b(self, element):
        return "Visiting B"

# Usage
elements = [ConcreteElementA(), ConcreteElementB()]
visitor = ConcreteVisitor()
for element in elements:
    print(element.accept(visitor))
```

## Trade-Offs

**Pros:** Separate operations from structure, easy to add operations, single responsibility

**Cons:** Breaks encapsulation, hard to add new element types, complex to understand

## Production Considerations

- Use when operations >> element types
- Document visitor hierarchy
- Handle all element types in each visitor
- Consider double dispatch implications
