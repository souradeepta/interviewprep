import java.util.*;
/**
 * WalletSystem - [Brief description]
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
public class WalletSystem{Map<Integer,Integer>balances=new HashMap<>();void deposit(int u,int amt){balances.put(u,balances.getOrDefault(u,0)+amt);}int getBalance(int u){return balances.getOrDefault(u,0);}public static void main(String[]a){WalletSystem ws=new WalletSystem();ws.deposit(1,100);}}
