interface Payment { boolean pay(double a); }
class LegacySystem { boolean process(int cents) { return true; } }
class Adapter implements Payment { LegacySystem sys; Adapter(LegacySystem s) { sys = s; } public boolean pay(double a) { return sys.process((int)(a*100)); } }
public class AdapterPattern { public static void main(String[] a) { Payment p = new Adapter(new LegacySystem()); System.out.println("Pay: " + p.pay(29.99)); } }
