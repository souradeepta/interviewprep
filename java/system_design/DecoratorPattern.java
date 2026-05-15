interface Coffee { int cost(); String desc(); }
/**
 * [Brief description]
 *
 * @param [param] [description]
 * @return [description]
 * @time O([complexity])
 */
class SimpleCoffee implements Coffee { public int cost() { return 200; } public String desc() { return "Coffee"; } }
abstract class CoffeeDecorator implements Coffee { protected Coffee c; CoffeeDecorator(Coffee c) { this.c = c; } }
/**
 * [Brief description]
 *
 * @param [param] [description]
 * @return [description]
 * @time O([complexity])
 */
class Milk extends CoffeeDecorator { Milk(Coffee c) { super(c); } public int cost() { return c.cost() + 50; } public String desc() { return c.desc() + ", milk"; } }
/**
 * [Brief description]
 *
 * @param [param] [description]
 * @return [description]
 * @time O([complexity])
 */
class Sugar extends CoffeeDecorator { Sugar(Coffee c) { super(c); } public int cost() { return c.cost() + 25; } public String desc() { return c.desc() + ", sugar"; } }
/**
 * DecoratorPattern - [Brief description]
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

/**
 * [Brief description]
 *
 * @param [param] [description]
 * @return [description]
 * @time O([complexity])
 */
public class DecoratorPattern { public static void main(String[] a) { Coffee c = new Sugar(new Milk(new SimpleCoffee())); System.out.println(c.desc() + ": " + c.cost()); } }
