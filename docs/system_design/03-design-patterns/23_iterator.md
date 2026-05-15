# Iterator Pattern

## Overview
Accesses elements of collection sequentially without exposing structure.

## Problem Statement
Clients need to iterate collections, but want to hide internal structure. Different collections need different iteration strategies.

## Solution
Create iterator for each collection type. Iterator handles traversal.

## When to Use

**Use Iterator when:**
- Need sequential access to elements
- Hide collection internal structure
- Support multiple concurrent iterations
- Different traversal strategies (forward, backward, depth-first)

**Examples:**
- Iterate list, tree, graph without exposing structure
- Multiple iterators on same collection
- Different iteration orders (ascending, descending)
- Lazy iteration (compute next on demand)

## Real-World Scenarios

**Tree Traversal:**
```
Tree: depth-first or breadth-first?
TreeIterator handles traversal logic
Client: for item in tree_iterator
Same interface regardless of traversal type
```

**Database Query Results:**
```
Iterator fetches next row on demand
Large result set (millions of rows)
Lazy: don't fetch all at once
```

## Implementation Patterns

### Generic Iterator
```python
class Iterator:
    def has_next(self):
        pass

    def next(self):
        pass

class ListIterator(Iterator):
    def __init__(self, collection):
        self.collection = collection
        self.index = 0

    def has_next(self):
        return self.index < len(self.collection)

    def next(self):
        if self.has_next():
            value = self.collection[self.index]
            self.index += 1
            return value
        return None

class Collection:
    def __init__(self):
        self.items = []

    def create_iterator(self):
        return ListIterator(self.items)

# Usage
col = Collection()
col.items = [1, 2, 3, 4, 5]
it = col.create_iterator()

while it.has_next():
    print(it.next())
```

## Trade-Offs

**Pros:**
- Hide collection structure
- Multiple concurrent iterations
- Different traversal strategies
- Decouples collection from iteration

**Cons:**
- Extra object overhead (iterator)
- May be overkill for simple collections
- Thread safety (modification during iteration)

## Production Considerations

- Support modification during iteration (fail-fast or copy)
- Document iteration order
- Performance: lazy vs. eager evaluation
- Handle empty collections
- Consider removing element during iteration
