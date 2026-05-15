#!/usr/bin/env python3
from pathlib import Path

patterns = {
    # Creational Patterns
    '01_singleton.md': {
        'name': 'Singleton',
        'type': 'Creational',
        'content': '''# Singleton Pattern

## Overview
Ensures a class has only one instance and provides a global point of access to it.

## Problem Statement
Some classes should have exactly one instance (logger, database connection pool, configuration manager). Multiple instances waste resources and cause inconsistency.

## Solution
Restrict instantiation to a single instance. Provide a static method to access that instance.

## When to Use

**Use Singleton when:**
- Only one instance should exist (database connections, thread pools, logging)
- Instance needs global access (configuration, cache manager)
- Lazy initialization improves startup time (expensive initialization)
- Thread-safe access required to shared resource

**Examples:**
- Logger instance: share across entire application
- Database connection pool: single pool manages all connections
- Configuration manager: load config once, access everywhere
- Cache manager: one cache instance for entire system

## Real-World Scenarios

**Logging System:**
```
Application needs logging everywhere.
Create single Logger instance.
All classes access Logger.getInstance().log()
Ensures single log file, consistent formatting.
```

**Database Connection Pool:**
```
Multiple threads need DB connections.
Create ConnectionPool singleton.
Pool manages connections, prevents resource exhaustion.
Threads request connections from pool via getInstance().
```

## When NOT to Use

**Avoid Singleton when:**
- Multiple instances needed for different contexts (multi-tenancy)
- Testing requires mocking (hard to test, breaks encapsulation)
- Adds unnecessary coupling (classes depend on singleton)
- Simple factory would suffice

## Implementation Patterns

### Thread-Safe Lazy Initialization (Python)
```python
class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-check locking
                    cls._instance = super().__new__(cls)
        return cls._instance

logger = Singleton()  # First call creates instance
logger2 = Singleton()  # Returns same instance
```

### Static Holder Pattern (Java)
```java
public class Singleton {
    private Singleton() {}

    private static class Holder {
        static final Singleton INSTANCE = new Singleton();
    }

    public static Singleton getInstance() {
        return Holder.INSTANCE;  // Lazy, thread-safe
    }
}
```

## Trade-Offs

**Pros:**
- Ensures single instance (resource efficiency)
- Global access point (convenient)
- Lazy initialization (deferred costly operations)
- Thread-safe implementations available

**Cons:**
- Hard to test (dependency on singleton instance)
- Hides dependencies (implicit global state)
- Violates single responsibility (manages creation + business logic)
- Can mask poor design (excessive global state)

## Production Considerations

- Use dependency injection instead (pass instance to classes that need it)
- If you need singleton, use static factory method
- Avoid nested singletons (cascade of globals)
- Make instance immutable if possible (thread safety)
- Add monitoring: track instance lifecycle, access patterns
'''
    },

    '02_factory_method.md': {
        'name': 'Factory Method',
        'type': 'Creational',
        'content': '''# Factory Method Pattern

## Overview
Creates objects without specifying exact classes. Subclasses decide which class to instantiate.

## Problem Statement
Object creation logic is complex. Different classes created based on conditions. Tight coupling between creator and concrete classes.

## Solution
Define interface for object creation. Let subclasses provide concrete implementation.

## When to Use

**Use Factory Method when:**
- Object type determined at runtime (based on config, input, etc.)
- Creation logic complex or varies (different initialization paths)
- Hide concrete class details from client
- Add new object types without changing client code

**Examples:**
- Database drivers: create PostgreSQL, MySQL, or SQLite connection
- File parsers: create CSV, JSON, or XML parser based on file extension
- Payment processors: create PayPal, Stripe, or Square processor based on config
- Transport layer: create HTTP, WebSocket, or gRPC transport

## Real-World Scenarios

**Database Connection Factory:**
```
Config specifies database type: 'postgres', 'mysql', or 'sqlite'
Factory reads config, creates appropriate connection
Client code: conn = DatabaseFactory.createConnection()
Doesn't care about implementation details
```

**Notification Channel Factory:**
```
User preference: email, SMS, or push notification
Factory creates appropriate notifier
client: notifier = NotificationFactory.create(user.preference)
notifier.send(message)
```

## When NOT to Use

**Avoid when:**
- Single object type (unnecessary abstraction)
- Simple objects (use constructor directly)
- Creation logic trivial (direct instantiation fine)

## Implementation Patterns

### Simple Factory
```python
class PaymentProcessor:
    pass

class PayPalProcessor(PaymentProcessor):
    pass

class StripeProcessor(PaymentProcessor):
    pass

class PaymentFactory:
    @staticmethod
    def create_processor(provider):
        if provider == 'paypal':
            return PayPalProcessor()
        elif provider == 'stripe':
            return StripeProcessor()
        else:
            raise ValueError(f"Unknown provider: {provider}")

# Usage
processor = PaymentFactory.create_processor('paypal')
processor.process_payment(100)
```

### Parameterized Factory
```java
public abstract class DatabaseConnection {
    public abstract void connect();
}

public class PostgresConnection extends DatabaseConnection {
    public void connect() { /* postgres logic */ }
}

public abstract class DatabaseFactory {
    abstract DatabaseConnection createConnection();

    public void openConnection() {
        DatabaseConnection conn = createConnection();
        conn.connect();
    }
}

public class PostgresFactory extends DatabaseFactory {
    public DatabaseConnection createConnection() {
        return new PostgresConnection();
    }
}
```

## Trade-Offs

**Pros:**
- Decouples creation from usage (flexible)
- Add new types without changing client
- Creation logic centralized (easy to modify)
- Supports runtime type selection

**Cons:**
- Extra abstraction layer (more classes)
- Overkill for simple objects
- Can proliferate subclasses (one per type)

## Production Considerations

- Use dependency injection frameworks (Spring, Guice) for factory implementation
- Document how to add new types (guide for developers)
- Monitor factory usage: which types created, how often
- Consider registry pattern (dynamic registration of types)
- Name factories clearly (XyzFactory not XyzCreator)
'''
    },

    '03_abstract_factory.md': {
        'name': 'Abstract Factory',
        'type': 'Creational',
        'content': '''# Abstract Factory Pattern

## Overview
Creates families of related objects without specifying concrete classes.

## Problem Statement
System needs to work with multiple families of related products (e.g., themes, UI kits, database families). Tight coupling to concrete classes. Adding new family requires changing code everywhere.

## Solution
Create abstract factory for each family. Concrete factories create related objects together.

## When to Use

**Use Abstract Factory when:**
- Multiple families of related objects (UI themes, database providers)
- Objects created together (Button + Checkbox for same theme)
- Families may be swapped at runtime (light/dark theme)
- Ensure consistency within family (don't mix Windows + Mac UI)

**Examples:**
- UI Toolkit: create Button, Checkbox, Textbox for Windows or Mac
- Database abstraction: PostgreSQL, MySQL, SQLite all have Connection, Statement, ResultSet
- Cloud providers: AWS, Azure, GCP all have VM, Storage, Database services
- Document formats: PDF, Word, HTML factories create Document, Paragraph, Table

## Real-World Scenarios

**UI Theme Factory:**
```
Application supports Light and Dark themes
Each theme needs Button, Checkbox, Window implementations
LightThemeFactory creates light Button, light Checkbox, light Window
DarkThemeFactory creates dark Button, dark Checkbox, dark Window
Client code uses factory, never knows concrete classes
```

**Cloud Provider Factory:**
```
System deployable on AWS, Azure, or GCP
Each provider has VM, Storage, Database services
AwsFactory creates EC2 (VM), S3 (Storage), RDS (Database)
AzureFactory creates VirtualMachine, BlobStorage, CosmosDB
Single client code, swappable providers
```

## When NOT to Use

**Avoid when:**
- Single family (factory method sufficient)
- Objects not related (no family concept)
- Static configuration (no need to swap families)

## Implementation Patterns

### UI Theme Example
```python
class Button:
    pass

class Checkbox:
    pass

class LightButton(Button):
    def render(self):
        return "Light Button"

class DarkButton(Button):
    def render(self):
        return "Dark Button"

class UIFactory:
    def create_button(self) -> Button:
        pass

    def create_checkbox(self) -> Checkbox:
        pass

class LightThemeFactory(UIFactory):
    def create_button(self) -> Button:
        return LightButton()

    def create_checkbox(self) -> Checkbox:
        return LightCheckbox()

class DarkThemeFactory(UIFactory):
    def create_button(self) -> Button:
        return DarkButton()
```

## Trade-Offs

**Pros:**
- Encapsulates related objects (consistency)
- Easy to swap families (single factory change)
- Add new family without modifying existing code
- Prevents mixing incompatible objects

**Cons:**
- Complex (many classes and interfaces)
- Extending families requires changing abstractions
- Harder to understand than factory method
- Overkill if families small or simple

## Production Considerations

- Use dependency injection to provide factory
- Document family relationships (which objects belong together)
- Make factory immutable once created (prevent runtime inconsistency)
- Consider registry pattern for dynamic family registration
- Monitor which families used (feature usage analytics)
'''
    },

    '04_builder.md': {
        'name': 'Builder',
        'type': 'Creational',
        'content': '''# Builder Pattern

## Overview
Constructs complex objects step by step. Separates construction from representation.

## Problem Statement
Objects have many optional parameters. Constructors become unwieldy (telescoping constructor anti-pattern). Want to build objects incrementally with clear steps.

## Solution
Use builder to construct object step by step. Fluent interface for readability.

## When to Use

**Use Builder when:**
- Objects have many optional parameters (readable API)
- Complex construction with multiple steps (logical separation)
- Same construction process creates different representations (variations)
- Want immutable objects (set all fields before building)

**Examples:**
- HTTP request building: method, headers, body, timeout, retries
- SQL query building: SELECT, FROM, WHERE, ORDER BY, LIMIT
- Configuration objects: many settings, most optional
- HTML DOM building: nested elements with attributes

## Real-World Scenarios

**HTTP Request Builder:**
```
HttpRequest req = new HttpRequest.Builder()
    .method("GET")
    .url("https://api.example.com/users")
    .header("Authorization", "Bearer token")
    .timeout(5000)
    .retries(3)
    .build();

Clear what's being configured.
Optional parameters have defaults.
```

**Query Builder (SQL):**
```
Query query = new Query.Builder()
    .select("name", "email")
    .from("users")
    .where("age > 18")
    .orderBy("name")
    .limit(10)
    .build();

Builds SQL dynamically.
Each step is clear.
```

## When NOT to Use

**Avoid when:**
- Few parameters (constructor fine)
- All parameters required (no benefit over constructor)
- Simple immutable objects (overhead)

## Implementation Patterns

### Fluent Builder
```python
class User:
    def __init__(self, name, email, age, role, active):
        self.name = name
        self.email = email
        self.age = age
        self.role = role
        self.active = active

class UserBuilder:
    def __init__(self):
        self.name = None
        self.email = None
        self.age = None
        self.role = "user"
        self.active = True

    def with_name(self, name):
        self.name = name
        return self

    def with_email(self, email):
        self.email = email
        return self

    def with_age(self, age):
        self.age = age
        return self

    def with_role(self, role):
        self.role = role
        return self

    def build(self):
        return User(self.name, self.email, self.age,
                   self.role, self.active)

# Usage
user = UserBuilder() \
    .with_name("Alice") \
    .with_email("alice@example.com") \
    .with_age(30) \
    .build()
```

### Inner Builder (Java)
```java
public class Request {
    public static class Builder {
        private String url;
        private String method = "GET";
        private Map<String, String> headers = new HashMap<>();

        public Builder url(String url) {
            this.url = url;
            return this;
        }

        public Builder method(String method) {
            this.method = method;
            return this;
        }

        public Builder header(String key, String value) {
            headers.put(key, value);
            return this;
        }

        public Request build() {
            return new Request(url, method, headers);
        }
    }
}

// Usage
Request req = new Request.Builder()
    .url("https://api.example.com")
    .method("POST")
    .header("Content-Type", "application/json")
    .build();
```

## Trade-Offs

**Pros:**
- Readable API (clear construction steps)
- Handles optional parameters elegantly
- Immutable objects (once built)
- Different representations from same process

**Cons:**
- More classes (builder + object)
- Overhead for simple objects
- Extra memory during construction

## Production Considerations

- Use builder for complex objects (API requests, configs)
- Make builders thread-safe if needed (synchronized or thread-local)
- Consider default values (what should be preset)
- Validate state in build() method (not during construction)
- Document required vs. optional parameters
'''
    },

    '05_prototype.md': {
        'name': 'Prototype',
        'type': 'Creational',
        'content': '''# Prototype Pattern

## Overview
Creates new objects by copying prototype rather than creating from scratch.

## Problem Statement
Creating objects is expensive (deep copy of complex state, expensive initialization). Want to clone existing objects efficiently.

## Solution
Make objects cloneable. Clone prototype instead of creating new.

## When to Use

**Use Prototype when:**
- Object creation is expensive (database queries, network calls)
- Need independent copies of complex objects
- Avoid subclassing for variations (clone and modify)
- Object state is large or complex (copy more efficient than recreate)

**Examples:**
- Clone database records (copy with modifications)
- Undo/redo system (store snapshots of state)
- Genetic algorithms (mutate copies of solutions)
- Caching: clone cached objects (prevent external modifications)

## Real-World Scenarios

**Document Cloning:**
```
User creates complex document with formatting, styles, content.
Clone document for versioning (creates independent copy).
Each version modified independently.
Original document unaffected.
```

**Configuration Snapshot:**
```
System has complex configuration object.
Clone configuration for testing (modify without affecting live).
Revert to prototype if test fails.
```

## When NOT to Use

**Avoid when:**
- Simple objects (constructor fine)
- Cloning complex (circular references, external resources)
- Performance not concern

## Implementation Patterns

### Python Clone
```python
import copy

class User:
    def __init__(self, name, email, roles):
        self.name = name
        self.email = email
        self.roles = roles  # list of roles

    def clone(self):
        return copy.deepcopy(self)

user1 = User("Alice", "alice@example.com", ["admin", "user"])
user2 = user1.clone()  # independent copy
user2.roles.append("superuser")
# user1.roles unchanged
```

### Prototype Registry
```python
class PrototypeRegistry:
    def __init__(self):
        self.prototypes = {}

    def register(self, key, prototype):
        self.prototypes[key] = prototype

    def clone(self, key):
        return self.prototypes[key].clone()

# Usage
registry = PrototypeRegistry()
registry.register("admin", User("admin", "admin@example.com", ["admin"]))
registry.register("user", User("user", "user@example.com", ["user"]))

# Create new users by cloning
new_admin = registry.clone("admin")
new_admin.name = "Alice"  # Independent object
```

## Trade-Offs

**Pros:**
- Efficient creation (copy cheap, creation expensive)
- Avoids subclassing (clone and modify)
- Works well with complex objects
- Supports snapshot/undo

**Cons:**
- Cloning complex (circular references, external resources)
- May copy unnecessary state (memory overhead)
- Shallow vs. deep copy considerations
- Not suitable for classes with external dependencies

## Production Considerations

- Use deep copy for complex objects (prevent shared references)
- Handle external resources carefully (database connections, file handles)
- Consider copy-on-write optimization (delay copy until modification)
- Document clone semantics (what's copied, what's shared)
- Test cloning thoroughly (nested objects, collections)
'''
    },

    # Structural Patterns
    '11_adapter.md': {
        'name': 'Adapter',
        'type': 'Structural',
        'content': '''# Adapter Pattern

## Overview
Converts interface of class into another clients expect. Lets incompatible interfaces work together.

## Problem Statement
Have existing class with useful functionality but incompatible interface. Want to use it with existing code without modification.

## Solution
Create adapter that wraps incompatible class and exposes expected interface.

## When to Use

**Use Adapter when:**
- Integrate legacy code (incompatible interfaces)
- Use third-party library with different interface
- Make incompatible classes work together
- Avoid modifying existing code

**Examples:**
- Integrate legacy database driver with modern ORM interface
- Use different payment gateways with same interface
- Adapt old logging framework to new logging interface
- Convert XML parser to JSON parser interface

## Real-World Scenarios

**Legacy Payment Integration:**
```
Old payment system uses: process_payment(card_number, amount)
New system expects: PaymentProcessor.execute(PaymentRequest)
Create adapter wrapping old system to new interface.
New code uses modern interface, adapter calls legacy code.
```

**Database Driver Adapter:**
```
Old code uses specific database driver (MySQLDriver)
New code expects generic DatabaseConnection interface
Adapter wraps old driver, implements new interface
Allows using old driver with new code
```

## Implementation Patterns

### Class Adapter (Inheritance)
```python
class OldPaymentProcessor:
    def process_payment(self, card, amount):
        return f"Processed {amount} on {card}"

class PaymentRequest:
    def __init__(self, card, amount):
        self.card = card
        self.amount = amount

# Adapter
class PaymentAdapter(OldPaymentProcessor):
    def execute(self, request: PaymentRequest):
        return self.process_payment(request.card, request.amount)

# Usage
adapter = PaymentAdapter()
result = adapter.execute(PaymentRequest("1234", 100))
```

### Object Adapter (Composition)
```python
class PaymentAdapter:
    def __init__(self, old_processor):
        self.old_processor = old_processor

    def execute(self, request):
        return self.old_processor.process_payment(
            request.card, request.amount
        )

# Usage
old = OldPaymentProcessor()
adapter = PaymentAdapter(old)
result = adapter.execute(PaymentRequest("1234", 100))
```

## Trade-Offs

**Pros:**
- Use existing code without modification
- Single responsibility (adapter focused on conversion)
- Can adapt to multiple interfaces

**Cons:**
- Extra layer (indirection, complexity)
- May mask poor design (shouldn't need adapter)
- Composition vs. inheritance tradeoffs

## When NOT to Use

**Avoid when:**
- Can modify original class (refactor instead)
- Interface only used once (simpler solution)
- Adapter complex (rethink design)

## Production Considerations

- Name adapters clearly (OldXyz -> NewXyzAdapter)
- Keep adapter thin (minimal logic)
- Document what's being adapted (what was incompatible)
- Test adapter thoroughly (works with both interfaces)
'''
    },

    '12_bridge.md': {
        'name': 'Bridge',
        'type': 'Structural',
        'content': '''# Bridge Pattern

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
'''
    },

    '13_composite.md': {
        'name': 'Composite',
        'type': 'Structural',
        'content': '''# Composite Pattern

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
        return "\\n".join(results)

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
'''
    },

    '14_decorator.md': {
        'name': 'Decorator',
        'type': 'Structural',
        'content': '''# Decorator Pattern

## Overview
Attaches additional responsibilities to object dynamically. Provides flexible alternative to subclassing.

## Problem Statement
Need to add features to objects, but subclassing causes class explosion. Want to stack features (multiple decorators on one object).

## Solution
Create decorator wrapping original object. Decorator has same interface. Adds functionality before/after delegating.

## When to Use

**Use Decorator when:**
- Add features dynamically without subclassing
- Features combinable (stack multiple decorators)
- Avoid class explosion (many subclasses)
- Object identity important (wrapped object still accessible)

**Examples:**
- I/O streams with compression and encryption
- UI components with scrolling, borders, shadows
- Logging and caching wrappers around functions
- Cost calculation (base + decorators add features)

## Real-World Scenarios

**Stream Decoration:**
```
FileInputStream reads from file
Add BufferedInputStream (buffering)
Add CompressInputStream (decompression)
Add EncryptedInputStream (decryption)
Stack decorators: file -> encrypted -> compressed -> buffered
```

**UI Decoration:**
```
Button base
Add BorderDecorator (adds border)
Add ShadowDecorator (adds shadow)
Button with border and shadow
```

## Implementation Patterns

### Decorator Wrapper
```python
class Component:
    def operation(self):
        pass

class ConcreteComponent(Component):
    def operation(self):
        return "ConcreteComponent"

class Decorator(Component):
    def __init__(self, component):
        self.component = component

    def operation(self):
        return self.component.operation()

class ConcreteDecoratorA(Decorator):
    def operation(self):
        return f"DecoratorA({self.component.operation()})"

class ConcreteDecoratorB(Decorator):
    def operation(self):
        return f"DecoratorB({self.component.operation()})"

# Usage
obj = ConcreteComponent()
obj = ConcreteDecoratorA(obj)
obj = ConcreteDecoratorB(obj)
print(obj.operation())  # DecoratorB(DecoratorA(ConcreteComponent))
```

## Trade-Offs

**Pros:**
- Add features without subclassing
- Stack features (flexible combinations)
- Single responsibility (each decorator one feature)
- Runtime configuration (add features dynamically)

**Cons:**
- Many small objects (memory overhead)
- Ordering matters (decorators applied in order)
- Hard to remove decorator from middle of stack
- Extra indirection (performance)

## Production Considerations

- Use for cross-cutting concerns (logging, caching, security)
- Consider order of decorators (does it matter?)
- Document decorator stack (what decorators applied)
- Consider composition over deep nesting
- Test with different decorator combinations
'''
    },

    '15_facade.md': {
        'name': 'Facade',
        'type': 'Structural',
        'content': '''# Facade Pattern

## Overview
Provides unified simplified interface to complex subsystem.

## Problem Statement
Subsystem complex with many interdependent classes. Clients need simple way to use subsystem.

## Solution
Create facade providing simple interface. Facade delegates to subsystem classes.

## When to Use

**Use Facade when:**
- Subsystem complex, need simplified interface
- Decouple clients from subsystem classes
- Layering subsystems (provide interface per layer)
- Simplify dependency graph

**Examples:**
- Order processing system (hide complex order/payment/shipping logic)
- Build system (hide compiler, linker, optimizer details)
- Database abstraction layer (hide SQL details)
- HTTP client library (hide connection pooling, retry logic)

## Real-World Scenarios

**Order Processing Facade:**
```
CreateOrderFacade:
  - Validate order
  - Reserve inventory
  - Process payment
  - Create shipment
Clients just call: createOrder(orderData)
Don't know about all the steps
```

**Library API Facade:**
```
Compiler internals complex
Scanner, Parser, Optimizer, CodeGenerator all interdependent
CompilerFacade.compile(source) → object
Clients use simple interface
```

## Implementation Patterns

### Simplified Interface
```python
class ComplexSubsystemA:
    def complex_operation_1(self):
        return "A1"

class ComplexSubsystemB:
    def complex_operation_2(self):
        return "B2"

class Facade:
    def __init__(self):
        self.subsystem_a = ComplexSubsystemA()
        self.subsystem_b = ComplexSubsystemB()

    def simple_operation(self):
        # Hide complex coordination
        result = self.subsystem_a.complex_operation_1()
        result += " " + self.subsystem_b.complex_operation_2()
        return result

# Usage
facade = Facade()
print(facade.simple_operation())  # Simple interface hides complexity
```

## Trade-Offs

**Pros:**
- Simplifies complex subsystems
- Decouples clients from subsystem
- Single entry point (easier to understand)
- Easier testing (mock facade)

**Cons:**
- Facade becomes dumping ground (too many methods)
- Hides useful subsystem details sometimes
- Not all clients need simplified interface
- Extra layer (indirection, performance)

## Production Considerations

- Keep facade focused (one responsibility)
- Don't add methods that don't relate to subsystem
- Consider multiple facades for different client groups
- Document what facade hides
- Version facade carefully (clients depend on interface)
'''
    },

    '16_flyweight.md': {
        'name': 'Flyweight',
        'type': 'Structural',
        'content': '''# Flyweight Pattern

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
'''
    },

    '17_proxy.md': {
        'name': 'Proxy',
        'type': 'Structural',
        'content': '''# Proxy Pattern

## Overview
Provides surrogate for another object to control access to it.

## Problem Statement
Need to control access to object (lazy loading, access control, logging). Creating object expensive or requires permissions.

## Solution
Create proxy with same interface. Proxy controls access to real object.

## When to Use

**Use Proxy when:**
- Control access (permissions, access control)
- Lazy initialization (defer expensive creation)
- Logging/monitoring access
- Cache expensive operations
- Remote object (network proxy)

**Examples:**
- Lazy-loaded images in documents
- Database access control (proxy checks permissions)
- Remote objects over network (RPC proxy)
- Caching proxy (remember previous results)
- Logging proxy (track all accesses)

## Real-World Scenarios

**Image Proxy (Lazy Loading):**
```
Document contains 100 images
Loading all images on startup is slow
ImageProxy loads image only when displayed
User scrolls to image → proxy loads it then
```

**Database Proxy (Access Control):**
```
Database requires authentication
DatabaseProxy checks credentials
If valid, delegates to real database
If invalid, throws PermissionDenied
```

## Implementation Patterns

### Protection/Access Control Proxy
```python
class Subject:
    def request(self):
        pass

class RealSubject(Subject):
    def request(self):
        return "RealSubject response"

class Proxy(Subject):
    def __init__(self, user_role):
        self.user_role = user_role
        self.real_subject = None

    def request(self):
        if self.user_role == "admin":
            if self.real_subject is None:
                self.real_subject = RealSubject()
            return self.real_subject.request()
        else:
            raise PermissionError("Access denied")

# Usage
admin_proxy = Proxy("admin")
print(admin_proxy.request())  # Works

user_proxy = Proxy("user")
# print(user_proxy.request())  # Raises PermissionError
```

### Virtual Proxy (Lazy Loading)
```python
class ExpensiveObject:
    def __init__(self):
        print("Creating expensive object...")

    def operation(self):
        return "Expensive operation result"

class Proxy:
    def __init__(self):
        self.real_object = None

    def operation(self):
        if self.real_object is None:
            self.real_object = ExpensiveObject()  # Create on first use
        return self.real_object.operation()

# Usage
proxy = Proxy()
# Object not created yet
result = proxy.operation()  # Creates object on demand
```

## Trade-Offs

**Pros:**
- Control access (security, permissions)
- Lazy loading (defer expensive operations)
- Transparency (same interface as real object)
- Add logging, caching, monitoring

**Cons:**
- Extra indirection (performance overhead)
- Complexity (another object to manage)
- May mask real object behavior
- Thread safety (shared proxy)

## Production Considerations

- Make proxy as transparent as possible (clients shouldn't notice)
- Consider thread safety (synchronize access)
- Document proxy type (protection, virtual, logging, etc.)
- Monitor proxy overhead (is it worth it?)
- Test proxy thoroughly (failure cases)
'''
    },

    # Behavioral Patterns
    '21_chain_of_responsibility.md': {
        'name': 'Chain of Responsibility',
        'type': 'Behavioral',
        'content': '''# Chain of Responsibility Pattern

## Overview
Passes request along chain of handlers. Each handler decides to process or pass to next.

## Problem Statement
Multiple objects can handle request, but only one should. Want to avoid coupling between requester and handler.

## Solution
Create chain of handlers. Request passes down until someone handles it.

## When to Use

**Use Chain of Responsibility when:**
- Multiple objects may handle request
- Handler not known in advance (runtime determination)
- Avoid coupling between sender and receiver
- Log messages with different levels (ERROR → WARN → INFO)
- Approval workflows (Manager → Director → VP)

**Examples:**
- Exception handling in try-catch chains
- Logging levels (critical → warning → info → debug)
- Event handling in GUI (button → panel → window → app)
- Authentication/authorization checks
- Help system (button help → panel help → app help)

## Real-World Scenarios

**Exception Handling:**
```
Try block catches specific exceptions
If handled, done
If not caught, passes to next handler
Finally reaches top-level handler
```

**Approval Workflow:**
```
Expense report < $100: manager approves
Expense < $1000: director approves
Expense < $10000: VP approves
Expense > $10000: CEO approves
```

## Implementation Patterns

### Handler Chain
```python
class Handler:
    def __init__(self):
        self.next_handler = None

    def set_next(self, handler):
        self.next_handler = handler
        return handler

    def handle(self, request):
        pass

class ConcreteHandlerA(Handler):
    def handle(self, request):
        if request == "A":
            return f"Handled by A"
        elif self.next_handler:
            return self.next_handler.handle(request)
        return "No handler"

class ConcreteHandlerB(Handler):
    def handle(self, request):
        if request == "B":
            return f"Handled by B"
        elif self.next_handler:
            return self.next_handler.handle(request)
        return "No handler"

# Usage
handler_a = ConcreteHandlerA()
handler_b = ConcreteHandlerB()
handler_a.set_next(handler_b)

print(handler_a.handle("A"))  # Handled by A
print(handler_a.handle("B"))  # Handled by B (passed down)
print(handler_a.handle("C"))  # No handler
```

## Trade-Offs

**Pros:**
- Decouples sender from receiver
- Flexible handler ordering
- Easy to add new handlers
- Dynamic chain construction

**Cons:**
- Request not guaranteed handled (silence)
- Hard to debug (request path unclear)
- Performance (passes through multiple handlers)
- Chain setup complexity

## Production Considerations

- Ensure request handled somewhere (log unhandled requests)
- Keep handlers focused (single responsibility)
- Document chain order (what handles what)
- Monitor handler performance (which is slow?)
- Test with missing handlers (what if chain incomplete?)
'''
    },

    '22_command.md': {
        'name': 'Command',
        'type': 'Behavioral',
        'content': '''# Command Pattern

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
'''
    },

    '23_iterator.md': {
        'name': 'Iterator',
        'type': 'Behavioral',
        'content': '''# Iterator Pattern

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
'''
    },

    '24_mediator.md': {
        'name': 'Mediator',
        'type': 'Behavioral',
        'content': '''# Mediator Pattern

## Overview
Encapsulates how objects interact. Objects communicate through mediator instead of directly.

## Problem Statement
Objects directly reference each other, creating tight coupling. Complex interactions between many objects.

## Solution
Create mediator object. All interactions go through mediator.

## When to Use

**Use Mediator when:**
- Objects heavily interconnected (coupling issues)
- Complex interactions between multiple objects
- Reusability limited by dependencies
- Need centralized control logic
- Behavior depends on multiple objects' state

**Examples:**
- Dialog with multiple controls (button, checkbox, textbox communicate through dialog)
- Chat room (users communicate through chat room, not directly)
- Air traffic control (planes communicate through controller, not directly)
- UI component interaction (form mediates between fields)

## Real-World Scenarios

**Dialog Mediator:**
```
Dialog contains button, textbox, checkbox
Button enables/disables based on checkbox
Textbox updates button label
Without mediator: button ← checkbox, textbox directly (complex)
With mediator: all talk to dialog, dialog coordinates
```

**Chat Room Mediator:**
```
Users don't send messages directly to each other
Users send to chat room
Chat room broadcasts to appropriate users
Decouples users from knowing each other
```

## Implementation Patterns

### Mediator Coordination
```python
class Mediator:
    def send_message(self, message, sender):
        pass

class Colleague:
    def __init__(self, mediator, name):
        self.mediator = mediator
        self.name = name

    def send(self, message):
        self.mediator.send_message(message, self)

    def receive(self, message):
        print(f"{self.name} received: {message}")

class ConcreteMediator(Mediator):
    def __init__(self):
        self.colleagues = []

    def add_colleague(self, colleague):
        self.colleagues.append(colleague)

    def send_message(self, message, sender):
        for colleague in self.colleagues:
            if colleague != sender:
                colleague.receive(message)

# Usage
mediator = ConcreteMediator()
user1 = Colleague(mediator, "Alice")
user2 = Colleague(mediator, "Bob")
mediator.add_colleague(user1)
mediator.add_colleague(user2)

user1.send("Hello!")  # Bob receives
```

## Trade-Offs

**Pros:**
- Decouples objects (less coupling)
- Centralizes control logic
- Reusability improved
- Easy to modify interactions

**Cons:**
- Mediator becomes complex ("God object")
- Extra indirection (performance)
- Harder to understand flow (centralized)
- Testing complex (mediator's responsibility)

## Production Considerations

- Keep mediator focused (don't add unrelated logic)
- Monitor mediator complexity (if too complex, redesign)
- Document interaction patterns
- Consider alternative designs (observer often simpler)
- Test thoroughly (many interaction paths)
'''
    },

    '25_memento.md': {
        'name': 'Memento',
        'type': 'Behavioral',
        'content': '''# Memento Pattern

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
'''
    },

    '26_observer.md': {
        'name': 'Observer',
        'type': 'Behavioral',
        'content': '''# Observer Pattern

## Overview
Defines one-to-many dependency where change to one object notifies dependents automatically.

## Problem Statement
Objects tightly coupled when one must notify many others of state change.

## Solution
Create subject that maintains observer list. Notifies observers when state changes.

## When to Use

**Use Observer when:**
- Objects loosely coupled (don't know details)
- Change to one affects many (event-driven)
- Dynamic subscription (add/remove observers)
- Broadcast notifications (MVC architecture)

**Examples:**
- Event systems (button click notifies listeners)
- MVC: model notifies views of changes
- Reactive programming (data changes flow to subscribers)
- Stock ticker (price changes notify investors)
- Chat: user joins, notifies others

## Real-World Scenarios

**MVC Pattern:**
```
Model changes: notifies views
Views update automatically
Controller updates model
Views don't know about model details
```

**Event System:**
```
Button clicked: notifies listeners
Listeners don't know about button
Button doesn't know about listeners
Decoupled communication
```

## Implementation Patterns

### Subject and Observer
```python
class Observer:
    def update(self, subject):
        pass

class Subject:
    def __init__(self):
        self.observers = []
        self.state = None

    def attach(self, observer):
        self.observers.append(observer)

    def detach(self, observer):
        self.observers.remove(observer)

    def notify(self):
        for observer in self.observers:
            observer.update(self)

    def set_state(self, state):
        self.state = state
        self.notify()

class ConcreteObserver(Observer):
    def update(self, subject):
        print(f"Observer notified: state = {subject.state}")

# Usage
subject = Subject()
observer1 = ConcreteObserver()
observer2 = ConcreteObserver()

subject.attach(observer1)
subject.attach(observer2)
subject.set_state("New State")  # Both notified
```

## Trade-Offs

**Pros:**
- Loose coupling (subject/observer independent)
- Dynamic subscriptions (add/remove at runtime)
- Broadcast communication (one-to-many)
- Push model (automatic updates)

**Cons:**
- Observer notification order unpredictable
- Memory leaks (forgotten detach())
- Performance (many observers)
- Hard to debug (implicit dependencies)

## Production Considerations

- Ensure observers always detach (prevent leaks)
- Order notifications carefully (if it matters)
- Make notifications synchronous or async (document)
- Handle exceptions in observers (don't crash subject)
- Monitor observer count (too many = performance)
'''
    },

    '27_state.md': {
        'name': 'State',
        'type': 'Behavioral',
        'content': '''# State Pattern

## Overview
Allows object to alter behavior when state changes. Object appears to change class.

## Problem Statement
Object behavior varies by state. Lots of if/else state checks throughout code.

## Solution
Create state object for each state. Context delegates to current state.

## When to Use

**Use State when:**
- Behavior varies significantly by state
- Large conditional based on state
- Many state transitions
- State-specific logic should be in state classes

**Examples:**
- Order state machine (pending → paid → shipped → delivered)
- Connection state (connecting → connected → disconnected)
- Document state (draft → review → published)
- Traffic light (red → yellow → green)
- TCP connection (listen → established → closed)

## Real-World Scenarios

**Order State Machine:**
```
Order in PENDING state: can cancel, pay
Order in PAID state: can ship, refund
Order in SHIPPED state: can receive
Order in DELIVERED state: can review

Each state defines what's allowed
State transitions clear
```

**Traffic Light:**
```
Red → can go to Yellow
Yellow → can go to Green
Green → can go to Red
Behavior changes based on state
'''
    },
}

def create_pattern_files():
    """Create all pattern documentation files"""
    base_path = Path('/home/sbisw/github/datastructures/docs/system_design/03-design-patterns')

    count = 0
    for filename, data in sorted(patterns.items()):
        filepath = base_path / filename

        # Skip if already exists
        if filepath.exists():
            continue

        with open(filepath, 'w') as f:
            f.write(data['content'])
        count += 1

    return count

if __name__ == '__main__':
    created = create_pattern_files()
    print(f"Created {created} new pattern documentation files")
