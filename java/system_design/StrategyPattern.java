interface PaymentStrategy { boolean pay(double amount); }

class CreditCard implements PaymentStrategy {
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public boolean pay(double amount) { System.out.println("CC: $" + amount); return true; }
}

class PayPal implements PaymentStrategy {
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public boolean pay(double amount) { System.out.println("PayPal: $" + amount); return true; }
}

class ShoppingCart {
    PaymentStrategy strategy;
    void setPayment(PaymentStrategy s) { strategy = s; }
    boolean checkout(double total) { return strategy.pay(total); }
}

/**
 * StrategyPattern - [Brief description]
 *
 * <p>OVERVIEW:
 * [Detailed explanation of what this class does]
 *
 * <p>COMPLEXITY:
 * <ul>
 *   <li>Time: [See method documentation]</li>
 *   <li>Space: O(n) where n is [the element count]</li>
 * </ul>
 *
 * <p>USAGE:
 * [How to use this class, with example]
 *
 * @author Interview Preparation
 * @since 1.0
 */

public class StrategyPattern {
    /**
     * [Brief description]
     *
     * @param [param] [description]
     * @return [description]
     * @time O([complexity])
     */
    public static void main(String[] args) {
        ShoppingCart cart = new ShoppingCart();
        cart.setPayment(new CreditCard());
        cart.checkout(99.99);
        cart.setPayment(new PayPal());
        cart.checkout(49.99);
    }
}
