# Strategy Pattern

**Level:** L4
**Time to read:** ~15 min

## Problem Statement

A payment service must support CreditCard, PayPal, and Crypto. A naive implementation puts all logic in one `process_payment()` method with growing `if/elif` branches. Adding a new payment method requires modifying the core class, violating Open/Closed Principle and making testing painful. Strategy externalizes each algorithm into its own class and lets the context swap implementations at runtime without changing its own code.

## Structure

```
         Context
        ┌──────────────────────────┐
        │ - strategy: Strategy     │◄── set at runtime
        │ + set_strategy(s)        │
        │ + execute(amount)        │──calls──► strategy.pay(amount)
        └──────────────────────────┘

         Strategy (interface)
        ┌──────────────────────┐
        │ + pay(amount) → bool │
        └──────────────────────┘
               ▲
    ┌──────────┼──────────────┐
    │          │              │
┌───────┐ ┌────────┐ ┌────────────┐
│Credit │ │ PayPal │ │   Crypto   │
│ Card  │ │Strategy│ │  Strategy  │
│pay()  │ │ pay()  │ │   pay()    │
└───────┘ └────────┘ └────────────┘
```

## Python Implementation

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class PaymentResult:
    success: bool
    transaction_id: str
    message: str

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount: float, currency: str = "USD") -> PaymentResult:
        pass

    @abstractmethod
    def validate(self) -> bool:
        pass

class CreditCardStrategy(PaymentStrategy):
    def __init__(self, card_number: str, cvv: str, expiry: str):
        self._card = card_number[-4:]   # store only last 4
        self._cvv = cvv
        self._expiry = expiry

    def validate(self) -> bool:
        return len(self._cvv) == 3

    def pay(self, amount: float, currency: str = "USD") -> PaymentResult:
        if not self.validate():
            return PaymentResult(False, "", "Invalid CVV")
        # real impl: call card processor API
        return PaymentResult(True, f"CC-{self._card}-{amount}", f"Charged ${amount} to *{self._card}")

class PayPalStrategy(PaymentStrategy):
    def __init__(self, email: str, access_token: str):
        self._email = email
        self._token = access_token

    def validate(self) -> bool:
        return "@" in self._email and bool(self._token)

    def pay(self, amount: float, currency: str = "USD") -> PaymentResult:
        if not self.validate():
            return PaymentResult(False, "", "Invalid PayPal credentials")
        return PaymentResult(True, f"PP-{self._email}-{amount}", f"PayPal: ${amount} from {self._email}")

class CryptoStrategy(PaymentStrategy):
    def __init__(self, wallet_address: str, coin: str = "BTC"):
        self._wallet = wallet_address
        self._coin = coin

    def validate(self) -> bool:
        return len(self._wallet) >= 26

    def pay(self, amount: float, currency: str = "USD") -> PaymentResult:
        # real impl: convert USD→crypto, broadcast tx
        return PaymentResult(True, f"CRYPTO-{self._wallet[:8]}", f"0.00{amount} {self._coin} sent")

class PaymentProcessor:
    def __init__(self, strategy: Optional[PaymentStrategy] = None):
        self._strategy = strategy

    def set_strategy(self, strategy: PaymentStrategy) -> None:
        self._strategy = strategy

    def checkout(self, amount: float) -> PaymentResult:
        if not self._strategy:
            raise RuntimeError("No payment strategy configured")
        return self._strategy.pay(amount)

# Usage — swap strategy at runtime
processor = PaymentProcessor()

processor.set_strategy(CreditCardStrategy("4111111111111234", "123", "12/26"))
print(processor.checkout(99.99))

processor.set_strategy(PayPalStrategy("user@example.com", "tok_abc123"))
print(processor.checkout(49.50))

# Python's built-in Strategy: sorted(key=...) is exactly this pattern
data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
by_age = sorted(data, key=lambda x: x["age"])    # strategy = sort by age
by_name = sorted(data, key=lambda x: x["name"])  # strategy = sort by name
```

## Real-World Uses

- **Python `sorted(key=...)`:** The `key` function IS the Strategy — caller injects the comparison algorithm without modifying `sorted`.
- **scikit-learn estimators:** `model = Pipeline([("scaler", StandardScaler()), ("clf", SVC())])` — swap `SVC()` for `RandomForestClassifier()` with no other changes.
- **Compression codecs:** `zlib`, `lz4`, `zstd` all implement the same compress/decompress interface; the caller selects based on speed vs. ratio trade-off.
- **HTTP client retry policies:** Exponential backoff, fixed delay, and jitter strategies implement the same `wait(attempt)` interface; the client picks at construction time.

## When to Apply

**Apply Strategy when:**
- You have a family of algorithms that do the same job differently
- You need to swap algorithms at runtime (user choice, config flags, A/B test)
- You want to isolate algorithm logic for independent testing
- A class has multiple conditional branches selecting behavior — refactor each branch to a Strategy

**Do NOT use when:**
- There are only 2 variants and they rarely change — a simple flag or subclass is less overhead
- Algorithms share no common interface — forced abstraction hurts readability
- The "strategy" is a single function — in Python, just pass a callable (Strategy is already built in via first-class functions)

## Common Interview Questions

**Q1. How does Strategy differ from Template Method?**
Strategy uses composition — the algorithm is injected. Template Method uses inheritance — the base class defines the skeleton, subclasses fill in steps. Strategy is more flexible at runtime; Template Method is simpler when the skeleton never changes.

**Q2. In Python, do you even need the Strategy pattern?**
Often no — Python's first-class functions cover simple cases (`sorted(key=fn)`). Use explicit Strategy classes when the "strategy" has state (credentials, config) or multiple methods, and you want type checking and discoverability.

**Q3. How would you implement Strategy with a config file?**
Use a registry (dict mapping names to classes): `STRATEGIES = {"cc": CreditCardStrategy, "paypal": PayPalStrategy}`. Load the key from config, instantiate the class. This is the plugin pattern — open for extension without code changes.

**Q4. What's the Open/Closed benefit of Strategy?**
Adding a new algorithm means creating a new class, not modifying existing ones. The `PaymentProcessor` context never changes when you add `CryptoStrategy`. This is Open/Closed: open for extension, closed for modification.

**Q5. Design payment retries with Strategy.**
```python
class RetryStrategy(ABC):
    @abstractmethod
    def wait(self, attempt: int) -> float: pass

class ExponentialBackoff(RetryStrategy):
    def wait(self, attempt: int) -> float:
        return min(2 ** attempt, 60)   # cap at 60s
```
The HTTP client holds a `RetryStrategy` and calls `time.sleep(strategy.wait(attempt))` between retries.

## Related Patterns

- **Template Method:** Inheritance-based alternative; use when the algorithm skeleton is fixed.
- **Command:** Encapsulates a request as an object; Strategy encapsulates the how, Command encapsulates the what.
- **Factory:** Often used to instantiate Strategies — `StrategyFactory.create("paypal")` returns the right implementation.
- See `docs/03-system-design/03-design-patterns/28_strategy.md` for additional sorting/routing examples.
