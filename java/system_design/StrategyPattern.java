interface PaymentStrategy { boolean pay(double amount); }

class CreditCard implements PaymentStrategy {
    public boolean pay(double amount) { System.out.println("CC: $" + amount); return true; }
}

class PayPal implements PaymentStrategy {
    public boolean pay(double amount) { System.out.println("PayPal: $" + amount); return true; }
}

class ShoppingCart {
    PaymentStrategy strategy;
    void setPayment(PaymentStrategy s) { strategy = s; }
    boolean checkout(double total) { return strategy.pay(total); }
}

public class StrategyPattern {
    public static void main(String[] args) {
        ShoppingCart cart = new ShoppingCart();
        cart.setPayment(new CreditCard());
        cart.checkout(99.99);
        cart.setPayment(new PayPal());
        cart.checkout(49.99);
    }
}
