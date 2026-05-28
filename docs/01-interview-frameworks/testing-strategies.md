# Testing Strategies: Unit, Integration, and E2E

**Level:** L4-L5
**Time to read:** ~20 min

Master testing approaches for building reliable systems.

---

## Testing Pyramid

```
        /\
       /E2E\
      /------\
     /Integration\
    /-----------\
   /   Unit Tests \
  /_______________\

Volume: Unit > Integration > E2E
Speed:  Unit > Integration > E2E
Cost:   Unit < Integration < E2E
```

---

## Unit Tests

**Scope:** Single function or class in isolation.

```python
def add(a, b):
    return a + b

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

# Run: pytest test_add.py
# Time: < 1ms
```

**Best Practices:**
- Test one thing per test
- Name clearly (test_add_positive_numbers)
- Mock external dependencies
- Aim for 80%+ code coverage

**Tools:** pytest (Python), Jest (JS), JUnit (Java)

---

## Integration Tests

**Scope:** Multiple components working together.

```python
def test_order_service_with_database():
    # Setup real database (or test DB)
    db = TestDatabase()
    order_service = OrderService(db)
    
    # Test workflow
    order = order_service.create_order(user_id=1, items=[...])
    assert order.id is not None
    assert db.get_order(order.id) == order

# Time: 10-100ms per test
```

**Best Practices:**
- Use test fixtures (setUp/tearDown)
- Test real interactions
- Use test database (not production)
- Clean up after tests

---

## End-to-End Tests

**Scope:** Full system from UI to database.

```python
def test_user_checkout_flow():
    # Start browser
    driver = webdriver.Chrome()
    
    # Navigate to site
    driver.get("https://example.com")
    
    # Add to cart
    driver.find_element("Add to Cart").click()
    
    # Checkout
    driver.find_element("Checkout").click()
    driver.find_element("Email").send_keys("user@example.com")
    driver.find_element("Pay").click()
    
    # Verify order created
    assert "Order confirmed" in driver.page_source

# Time: 5-30 seconds per test
```

**Best Practices:**
- Use page objects (abstraction)
- Test critical user flows
- Run on real/staging environments
- Keep count low (they're slow)

---

## Test Coverage

```python
# What to measure
# Method 1: Line coverage (% of lines executed)
# Target: 80%+ for critical code

# Method 2: Branch coverage (% of if/else branches)
# Better metric than line coverage

# Tool: pytest-cov
# pytest --cov=myapp tests/
```

**Coverage doesn't guarantee quality:**
```python
# 100% coverage but poor test
def test_add():
    add(2, 3)  # ✓ Covers line, but doesn't assert result

# Better test
def test_add():
    assert add(2, 3) == 5  # ✓ Covers line and verifies behavior
```

---

## Mocking & Stubbing

### Mock External Service

```python
from unittest.mock import Mock, patch

def test_order_with_payment_mocked():
    # Mock payment service
    payment_service = Mock()
    payment_service.charge.return_value = {"success": True}
    
    order_service = OrderService(payment_service)
    order = order_service.create_order(user_id=1, total=100)
    
    # Verify payment was called
    payment_service.charge.assert_called_once_with(1, 100)
    assert order is not None
```

### Mock Database

```python
@patch('myapp.database.get_user')
def test_user_service(mock_get_user):
    mock_get_user.return_value = {"id": 1, "name": "Alice"}
    
    user = user_service.get(1)
    assert user["name"] == "Alice"
```

---

## Continuous Integration

**Automated testing on every commit:**

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          pytest tests/
          coverage report --fail-under=80
      - name: Run E2E tests
        run: |
          docker-compose up -d
          pytest tests/e2e/
          docker-compose down
```

---

## Testing Pyramid in Practice

**For 100 lines of code:**
- 70-80 unit tests (< 1 second total)
- 15-20 integration tests (< 10 seconds total)
- 3-5 E2E tests (< 60 seconds total)

**Feedback loop:**
- Unit: Every commit (< 5 seconds)
- Integration: On PR (< 1 minute)
- E2E: Before merge (< 5 minutes)

---

## Testing Checklist

- ✓ Unit tests for critical logic
- ✓ Integration tests for workflows
- ✓ E2E tests for user flows
- ✓ Code coverage 80%+
- ✓ Test database (not production)
- ✓ Mocks for external services
- ✓ CI/CD runs tests on every commit
- ✓ Failing tests block merge
- ✓ Test names describe what they test
- ✓ Tests are deterministic (not flaky)

