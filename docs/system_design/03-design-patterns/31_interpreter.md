# Interpreter Pattern

## Overview
Defines grammar for language and interpreter to interpret sentences.

## Problem Statement
Need to interpret strings/commands in custom language. Want to represent language as data structure.

## Solution
Define grammar rules. Create interpreter for each rule. Build expression tree.

## When to Use

**Use Interpreter when:**
- Language (formal or informal) with rules
- Grammar relatively stable
- Interpretation performance not critical
- Want to represent language as data

**Examples:**
- SQL parser (parse SELECT statements)
- Configuration file interpreter (parse config syntax)
- Expression evaluator (parse mathematical expressions)
- Regular expression matcher
- Domain-specific language (DSL) interpreter

## Real-World Scenarios

**Expression Evaluator:**
```
Grammar: Expression := Term ('+' Term)*
         Term := Factor ('*' Factor)*
         Factor := Number | '(' Expression ')'

Parser builds expression tree
Evaluator traverses tree and calculates
```

## Implementation Patterns

### Expression Grammar
```python
class Expression:
    def interpret(self):
        pass

class Number(Expression):
    def __init__(self, value):
        self.value = value

    def interpret(self):
        return self.value

class Add(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def interpret(self):
        return self.left.interpret() + self.right.interpret()

class Multiply(Expression):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def interpret(self):
        return self.left.interpret() * self.right.interpret()

# Usage
# 3 + 2 * 4
expr = Add(Number(3), Multiply(Number(2), Number(4)))
print(expr.interpret())  # 11
```

## Trade-Offs

**Pros:** Represent language as data, extensible grammar, clear structure

**Cons:** Complex for complex grammars, performance overhead, hard to debug

## Production Considerations

- Use parser generators (flex, bison, ANTLR) for real languages
- Cache compiled expressions (memoization)
- Visitor pattern for operations on expressions
- Handle syntax errors gracefully
