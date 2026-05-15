interface Coffee { int cost(); String desc(); }
class SimpleCoffee implements Coffee { public int cost() { return 200; } public String desc() { return "Coffee"; } }
abstract class CoffeeDecorator implements Coffee { protected Coffee c; CoffeeDecorator(Coffee c) { this.c = c; } }
class Milk extends CoffeeDecorator { Milk(Coffee c) { super(c); } public int cost() { return c.cost() + 50; } public String desc() { return c.desc() + ", milk"; } }
class Sugar extends CoffeeDecorator { Sugar(Coffee c) { super(c); } public int cost() { return c.cost() + 25; } public String desc() { return c.desc() + ", sugar"; } }
public class DecoratorPattern { public static void main(String[] a) { Coffee c = new Sugar(new Milk(new SimpleCoffee())); System.out.println(c.desc() + ": " + c.cost()); } }
