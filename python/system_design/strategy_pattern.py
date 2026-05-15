"""Strategy Pattern - Runtime algorithm switching"""

from abc import ABC, abstractmethod


class PaymentStrategy(ABC):
    """Payment strategy interface"""

    @abstractmethod
        """pay implementation.

        Time: O(n)
        Space: O(1)
        """
    def pay(self, amount: float) -> bool:
        raise NotImplementedError


class CreditCardPayment(PaymentStrategy):
    """Credit card payment strategy"""

        """__init__ implementation.

        Time: O(n)
        Space: O(1)
        """
    def __init__(self, card_number: str, cvv: str):
        self.card_number = card_number
        self.cvv = cvv

        """pay implementation.

        Time: O(n)
        Space: O(1)
        """
    def pay(self, amount: float) -> bool:
        print(f"Processing credit card payment of ${amount}")
        print(f"  Card: {self.card_number[-4:]}")
        return True


class PayPalPayment(PaymentStrategy):
    """PayPal payment strategy"""

        """__init__ implementation.

        Time: O(n)
        Space: O(1)
        """
    def __init__(self, email: str):
        self.email = email

        """pay implementation.

        Time: O(n)
        Space: O(1)
        """
    def pay(self, amount: float) -> bool:
        print(f"Processing PayPal payment of ${amount}")
        print(f"  Email: {self.email}")
        return True


class BitcoinPayment(PaymentStrategy):
    """Bitcoin payment strategy"""

        """__init__ implementation.

        Time: O(n)
        Space: O(1)
        """
    def __init__(self, address: str):
        self.address = address

        """pay implementation.

        Time: O(n)
        Space: O(1)
        """
    def pay(self, amount: float) -> bool:
        print(f"Processing Bitcoin payment of ${amount}")
        print(f"  Address: {self.address}")
        return True


class ShoppingCart:
    """Context that uses payment strategy"""

        """__init__ implementation.

        Time: O(n)
        Space: O(1)
        """
    def __init__(self):
        self.items = []
        self.payment_strategy = None

        """add_item implementation.

        Time: O(n)
        Space: O(1)
        """
    def add_item(self, price: float):
        self.items.append(price)

        """set_payment_strategy implementation.

        Time: O(n)
        Space: O(1)
        """
    def set_payment_strategy(self, strategy: PaymentStrategy):

    """

    [Brief description of what this function does]


    Args:

        [param]: description


    Returns:

        [description of return value]


    Time: O([complexity])

    Space: O([complexity])

    """
        self.payment_strategy = strategy

        """checkout implementation.

        Time: O(n)
        Space: O(1)
        """
    def checkout(self) -> bool:
        total = sum(self.items)
        if not self.payment_strategy:
            print("No payment strategy selected")
            return False
        return self.payment_strategy.pay(total)


if __name__ == "__main__":
    cart = ShoppingCart()
    cart.add_item(29.99)
    cart.add_item(15.50)

    print("=== Credit Card ===")
    cart.set_payment_strategy(CreditCardPayment("1234-5678-9012-3456", "123"))
    cart.checkout()

    cart2 = ShoppingCart()
    cart2.add_item(99.99)

    print("\n=== PayPal ===")
    cart2.set_payment_strategy(PayPalPayment("user@example.com"))
    cart2.checkout()

    print("\n=== Bitcoin ===")
    cart2.set_payment_strategy(BitcoinPayment("1A1z7agoat2LWSR2k4SSQwDjggyziQS91g"))
    cart2.checkout()