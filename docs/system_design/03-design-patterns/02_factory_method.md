# Factory Method Pattern

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
