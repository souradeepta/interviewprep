import java.util.*;
/**
 * Ecommerce - [Brief description]
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
public class Ecommerce{Map<Integer,Integer>cart=new HashMap<>();void addCart(int p,int q){cart.put(p,q);}void checkout(){System.out.println("Order placed: "+cart.size());}public static void main(String[]a){Ecommerce e=new Ecommerce();e.addCart(1,5);e.checkout();}}
