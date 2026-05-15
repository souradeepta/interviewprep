interface Payment { boolean pay(double a); }
class LegacySystem { boolean process(int cents) { return true; } }
/**
 * [Brief description]
 *
 * @param [param] [description]
 * @return [description]
 * @time O([complexity])
 */
class Adapter implements Payment { LegacySystem sys; Adapter(LegacySystem s) { sys = s; } public boolean pay(double a) { return sys.process((int)(a*100)); } }
/**
 * AdapterPattern - [Brief description]
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
public class AdapterPattern { public static void main(String[] a) { Payment p = new Adapter(new LegacySystem()); System.out.println("Pay: " + p.pay(29.99)); } }
