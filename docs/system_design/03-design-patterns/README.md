# Gang of Four Design Patterns

Complete documentation of all 23 Gang of Four design patterns with practical examples and decision guide.

## Creational Patterns (5)
Create objects without exposing creation logic.

### 1. [Singleton](01_singleton.md)
**When:** Need exactly one instance (logger, connection pool, configuration)
**Key Benefit:** Single instance globally accessible
**Trade-off:** Hard to test, hides dependencies

### 2. [Factory Method](02_factory_method.md)
**When:** Object type determined at runtime (database drivers, file parsers)
**Key Benefit:** Decouple creation from usage
**Trade-off:** Many subclasses, extra abstraction layer

### 3. [Abstract Factory](03_abstract_factory.md)
**When:** Create families of related objects (UI themes, database families)
**Key Benefit:** Ensure consistency within family, swap families easily
**Trade-off:** Complex, hard to extend families

### 4. [Builder](04_builder.md)
**When:** Objects have many optional parameters (HTTP request, SQL query)
**Key Benefit:** Readable construction, handles optional parameters elegantly
**Trade-off:** Extra classes, overhead for simple objects

### 5. [Prototype](05_prototype.md)
**When:** Object creation expensive, need independent copies (cloning, snapshots)
**Key Benefit:** Efficient creation via copying
**Trade-off:** Cloning complex with circular references

## Structural Patterns (7)
Compose objects into larger structures while keeping them flexible.

### 6. [Adapter](11_adapter.md)
**When:** Integrate incompatible interfaces (legacy code, third-party libraries)
**Key Benefit:** Use existing code without modification
**Trade-off:** Extra layer, may mask poor design

### 7. [Bridge](12_bridge.md)
**When:** Decouple abstraction from implementation (UI widgets on different OS)
**Key Benefit:** Avoid class explosion, vary independently
**Trade-off:** Extra indirection, complex upfront design

### 8. [Composite](13_composite.md)
**When:** Part-whole hierarchies (file system, UI components, menus)
**Key Benefit:** Treat individual and composite objects uniformly
**Trade-off:** Lost type safety, extra indirection

### 9. [Decorator](14_decorator.md)
**When:** Add features dynamically without subclassing (logging, caching, streams)
**Key Benefit:** Stack features, avoid class explosion
**Trade-off:** Many small objects, ordering matters

### 10. [Facade](15_facade.md)
**When:** Simplify complex subsystem (order processing, build system)
**Key Benefit:** Simple interface, decouple clients from subsystem
**Trade-off:** Facade becomes dumping ground, hides details

### 11. [Flyweight](16_flyweight.md)
**When:** Many similar objects causing memory bloat (text editor characters, game particles)
**Key Benefit:** Massive memory savings via sharing
**Trade-off:** Complex, CPU overhead for lookup

### 12. [Proxy](17_proxy.md)
**When:** Control access to objects (lazy loading, access control, logging)
**Key Benefit:** Lazy initialization, transparent access control
**Trade-off:** Extra indirection, added complexity

## Behavioral Patterns (11)
Communicate between objects, distribute responsibility, encapsulate behavior.

### 13. [Chain of Responsibility](21_chain_of_responsibility.md)
**When:** Multiple handlers, request passed until handled (logging levels, approval workflow)
**Key Benefit:** Decouple sender from receiver, flexible handler ordering
**Trade-off:** Request may go unhandled, hard to debug

### 14. [Command](22_command.md)
**When:** Encapsulate request as object (GUI buttons, undo/redo, job queue)
**Key Benefit:** Queue requests, undo/redo, macro commands
**Trade-off:** Many command classes, extra indirection

### 15. [Interpreter](31_interpreter.md)
**When:** Interpret custom language or syntax (expression evaluator, DSL)
**Key Benefit:** Represent language as data, extensible grammar
**Trade-off:** Complex for complex grammars, performance overhead

### 16. [Iterator](23_iterator.md)
**When:** Sequential access without exposing structure (traverse collection, tree)
**Key Benefit:** Hide internal structure, multiple concurrent iterations
**Trade-off:** Extra object overhead, modification during iteration issues

### 17. [Mediator](24_mediator.md)
**When:** Many interconnected objects (dialog with controls, chat room)
**Key Benefit:** Decoupled communication, centralized control
**Trade-off:** Mediator becomes complex, hard to understand flow

### 18. [Memento](25_memento.md)
**When:** Save/restore state (undo/redo, snapshots, transactions)
**Key Benefit:** Preserve encapsulation, save multiple states
**Trade-off:** Memory overhead, serialization complexity

### 19. [Observer](26_observer.md)
**When:** One-to-many dependency (MVC, event systems, reactive programming)
**Key Benefit:** Loose coupling, dynamic subscriptions
**Trade-off:** Notification order unpredictable, memory leaks if not detached

### 20. [State](27_state.md)
**When:** Behavior varies by state (order workflow, connection states)
**Key Benefit:** Eliminate conditionals, encapsulate state behavior
**Trade-off:** Many classes, overkill for few states

### 21. [Strategy](28_strategy.md)
**When:** Multiple algorithms, choose at runtime (payment methods, sorting, compression)
**Key Benefit:** Eliminate conditionals, easy to add algorithms
**Trade-off:** Many strategy classes, overhead for single algorithm

### 22. [Template Method](29_template_method.md)
**When:** Similar algorithms with different details (data processing, report generation)
**Key Benefit:** Code reuse, control flow in base class
**Trade-off:** Rigid structure, subclasses limited to hooks

### 23. [Visitor](30_visitor.md)
**When:** Many operations on complex structure (AST operations, file system operations)
**Key Benefit:** Add operations without changing classes
**Trade-off:** Breaks encapsulation, hard to add new element types

## Decision Guide

### Choose by Problem Type

**"I need to create objects"**
→ Singleton, Factory Method, Abstract Factory, Builder, Prototype

**"I need to compose or adapt objects"**
→ Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy

**"I need objects to communicate"**
→ Chain of Responsibility, Command, Iterator, Mediator, Observer

**"I need to define object behavior"**
→ Interpreter, State, Strategy, Template Method, Visitor, Memento

### Choose by Symptom

**"Too many if/else statements"**
→ Strategy (algorithm choice), State (behavior by state), Visitor (operation choice)

**"Classes too tightly coupled"**
→ Observer, Mediator, Facade, Adapter, Bridge

**"Too many subclasses"**
→ Decorator, Strategy, State, Composite, Flyweight

**"Need to add functionality without modifying existing code"**
→ Decorator, Visitor, Template Method, Observer

**"Need to save/restore/undo state"**
→ Memento, Command, Prototype

**"Need flexible object creation"**
→ Factory Method, Abstract Factory, Builder, Prototype

## Real-World Application Examples

**E-Commerce System:**
- Builder: order configuration (items, shipping, payment)
- Strategy: payment methods (credit card, PayPal, Apple Pay)
- State: order workflow (pending, paid, shipped, delivered)
- Observer: notify inventory on order, notify user on status change
- Composite: product catalog (categories contain products and subcategories)
- Mediator: shopping cart mediates between product, inventory, order

**Text Editor:**
- Command: undo/redo stack (each edit is command)
- Memento: save document snapshots
- Composite: document structure (section contains paragraphs and images)
- Decorator: add formatting (bold, italic, underline)
- Flyweight: share font objects for efficiency
- Iterator: traverse document elements

**Web Framework:**
- Factory Method: create different request handlers
- Adapter: integrate third-party libraries
- Facade: simplify API for developers
- Observer: event listeners (click, change, submit)
- Strategy: different validation rules
- Template Method: HTTP request processing pipeline
- Chain of Responsibility: middleware chain

## Design Patterns vs. Anti-Patterns

**Good use:** Solves real problem, reduces complexity, improves maintainability
**Overuse:** Over-engineering, unnecessary abstraction, added complexity

**Rule of Three:**
Don't introduce pattern until you need it for 3+ similar cases.

**YAGNI (You Aren't Gonna Need It):**
Don't add patterns speculatively. Add when you need them.

## Related Patterns

Many patterns work together:
- Strategy often paired with State
- Decorator similar to Strategy
- Builder similar to Template Method
- Observer used in Mediator
- Command often with Memento for undo
- Factory Method often with Strategy/State

## Learning Path

**Beginner:** Observer, Factory Method, Singleton
**Intermediate:** Strategy, Decorator, Adapter
**Advanced:** Visitor, Mediator, Memento

**Practice:** Implement patterns in your language, recognize patterns in existing code.

## Further Reading

- "Design Patterns: Elements of Reusable Object-Oriented Software" by Gang of Four
- Pattern catalogs: refactoring.guru, sourcemaking.com
- Domain-specific patterns: cloud patterns, microservice patterns, enterprise patterns
