# Adapter Pattern

**Level:** L4
**Time to read:** ~15 min

## Problem Statement

Your new system expects a clean REST-style interface: `payment.charge(amount, currency)`. You must integrate a legacy SOAP payment gateway whose API looks like `gateway.processTransaction(xml_payload)`. Rewriting the legacy system is out of scope, and modifying your new code to know about SOAP couples it to a vendor-specific format. Adapter wraps the incompatible interface and translates calls so the legacy code works inside the new system without modification to either side.

## Structure

```
  Target Interface (what your system expects)
  ┌─────────────────────────────────────┐
  │ PaymentGateway                      │
  │ + charge(amount, currency) → Result │
  │ + refund(tx_id, amount) → Result    │
  └─────────────────────────────────────┘
             ▲ implements
  ┌──────────┴──────────────────────────┐
  │ SOAPGatewayAdapter                  │
  │ - adaptee: LegacySOAPGateway        │◄──── wraps
  │ + charge(amount, currency)          │         │
  │    → builds XML                     │         ▼
  │    → calls adaptee.processTransaction│   LegacySOAPGateway
  │    → parses XML response            │   (incompatible interface)
  │ + refund(tx_id, amount)             │   + processTransaction(xml)
  └─────────────────────────────────────┘   + cancelTransaction(xml)

  Object Adapter (composition)    Class Adapter (multiple inheritance)
  ────────────────────────────    ────────────────────────────────────
  Adapter holds adaptee ref       Adapter inherits from both Target
  Preferred in Python             and Adaptee (avoid in Python)
```

## Python Implementation

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from xml.etree import ElementTree as ET
import uuid

# --- Target Interface (what our system expects) ---
@dataclass
class PaymentResult:
    success: bool
    transaction_id: str
    error: str = ""

class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: float, currency: str) -> PaymentResult:
        pass

    @abstractmethod
    def refund(self, transaction_id: str, amount: float) -> PaymentResult:
        pass

# --- Adaptee (legacy system we cannot modify) ---
class LegacySOAPGateway:
    """Third-party SOAP gateway — incompatible interface, cannot be changed."""

    def processTransaction(self, xml_payload: str) -> str:
        # Real impl: send SOAP envelope to vendor endpoint
        # Stub: parse XML and return mock SOAP response
        root = ET.fromstring(xml_payload)
        amount = root.findtext("amount", "0")
        tx_id = f"LEGACY-{uuid.uuid4().hex[:8].upper()}"
        return f"""<response><status>SUCCESS</status><txId>{tx_id}</txId><amount>{amount}</amount></response>"""

    def cancelTransaction(self, xml_payload: str) -> str:
        root = ET.fromstring(xml_payload)
        tx_id = root.findtext("txId", "unknown")
        return f"""<response><status>REFUNDED</status><txId>{tx_id}</txId></response>"""

# --- Adapter (bridges the gap) ---
class SOAPGatewayAdapter(PaymentGateway):
    def __init__(self, legacy_gateway: LegacySOAPGateway):
        self._gateway = legacy_gateway

    def charge(self, amount: float, currency: str) -> PaymentResult:
        # Translate: REST params → SOAP XML
        xml = f"<transaction><amount>{amount}</amount><currency>{currency}</currency></transaction>"
        raw_response = self._gateway.processTransaction(xml)
        return self._parse_response(raw_response)

    def refund(self, transaction_id: str, amount: float) -> PaymentResult:
        xml = f"<cancelRequest><txId>{transaction_id}</txId><amount>{amount}</amount></cancelRequest>"
        raw_response = self._gateway.cancelTransaction(xml)
        return self._parse_response(raw_response)

    def _parse_response(self, xml: str) -> PaymentResult:
        """Translate SOAP XML response → our clean PaymentResult."""
        root = ET.fromstring(xml)
        status = root.findtext("status", "")
        tx_id = root.findtext("txId", "")
        success = status in ("SUCCESS", "REFUNDED")
        return PaymentResult(success=success, transaction_id=tx_id,
                             error="" if success else f"SOAP error: {status}")

# --- Usage: caller only sees the clean interface ---
def process_order(gateway: PaymentGateway, total: float) -> None:
    result = gateway.charge(total, "USD")
    if result.success:
        print(f"Charged ${total} — TX: {result.transaction_id}")
    else:
        print(f"Failed: {result.error}")

legacy = LegacySOAPGateway()
adapter = SOAPGatewayAdapter(legacy)
process_order(adapter, 149.99)   # Works — caller has no idea it's SOAP

# --- Python's built-in Adapter: io.StringIO ---
import io
def read_lines(file_like) -> list[str]:
    """Expects a file-like object."""
    return file_like.readlines()

# Adapt a raw string to file interface — no subclassing needed
lines = read_lines(io.StringIO("line one\nline two\nline three"))
print(lines)
```

## Real-World Uses

- **Python `io.StringIO` / `io.BytesIO`:** Adapts in-memory strings/bytes to the file-like interface — any function expecting `file.read()` works with in-memory data without modification.
- **SQLAlchemy dialects:** Each database dialect (`psycopg2`, `mysqlclient`, `cx_Oracle`) is an Adapter translating SQLAlchemy's unified query interface to the vendor-specific wire protocol.
- **ORM DataMappers:** Hibernate / Django ORM adapt SQL row tuples to Python objects and back — `ResultSet` (Adaptee) → domain model (Target).
- **Legacy API wrappers:** `requests` wrapping `urllib`, Boto3 wrapping raw AWS REST endpoints, gRPC generated stubs wrapping HTTP/2 frames.

## When to Apply

**Apply Adapter when:**
- You need to use a class with an incompatible interface (third-party library, legacy system)
- You want to create a reusable class that cooperates with unrelated or unforeseen classes
- You're building a unified interface over multiple vendor implementations (payment gateways, storage providers, notification services)

**Do NOT use when:**
- You control both interfaces — refactor the original class instead
- The interfaces are so different that adaptation requires significant business logic — Facade or a full rewrite may be more appropriate
- You're adapting more than 1-2 methods — if the entire API differs, consider a proper abstraction layer (anti-corruption layer in DDD)

## Common Interview Questions

**Q1. What's the difference between Adapter, Facade, and Proxy?**
- **Adapter:** Makes incompatible interfaces compatible (translation layer).
- **Facade:** Simplifies a complex subsystem behind a single simpler interface (not necessarily incompatible).
- **Proxy:** Same interface as real object; controls access (lazy load, security, caching).

**Q2. Object Adapter vs. Class Adapter — which do you prefer in Python?**
Object Adapter (composition) is almost always preferred. It doesn't require multiple inheritance, allows the adaptee to be swapped at runtime, and is easier to test (inject a mock). Class Adapter (inheriting from both Target and Adaptee) creates tight coupling.

**Q3. How do you test code that uses an Adapter?**
Inject a mock/stub Adaptee into the Adapter in tests, or mock the Adapter itself. Because the Adapter implements the Target interface, you can substitute a `FakeGateway(PaymentGateway)` in unit tests without any SOAP/network calls.

**Q4. Describe the anti-corruption layer (DDD) and how it relates to Adapter.**
An anti-corruption layer is an Adapter at the bounded-context boundary — it translates between two domain models (e.g., your internal `Order` model and the vendor's `PurchaseOrder` XML schema). It prevents the external model's concepts from leaking into your domain. Conceptually it's Adapter at architectural scale.

**Q5. Design a multi-provider notification adapter.**
```python
class NotificationService(ABC):
    @abstractmethod
    def send(self, to: str, message: str) -> bool: pass

class TwilioAdapter(NotificationService):
    def __init__(self, client): self._client = client  # Twilio SDK
    def send(self, to, message):
        self._client.messages.create(to=to, body=message, from_="+1...")
        return True

class SendGridAdapter(NotificationService):
    def __init__(self, sg): self._sg = sg
    def send(self, to, message):
        msg = Mail(to_emails=to, plain_text_content=message)
        self._sg.send(msg)
        return True
```
Caller uses `NotificationService.send()` — no SDK leakage.

## Related Patterns

- **Facade:** Adapter translates interface; Facade simplifies interface. Often used together at system boundaries.
- **Proxy:** Same wrapper structure; Proxy preserves the interface, Adapter changes it.
- **Bridge:** Both separate abstraction from implementation, but Bridge is designed upfront for extensibility; Adapter retrofits incompatible existing code.
- See `docs/03-system-design/03-design-patterns/11_adapter.md` for additional examples including database dialect adapters.
