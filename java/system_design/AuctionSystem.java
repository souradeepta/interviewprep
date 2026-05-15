import java.util.*;
/**
 * AuctionSystem - [Brief description]
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
public class AuctionSystem{Map<Integer,int[]>bids=new HashMap<>();void bid(int aid,int u,int amt){bids.put(aid,new int[]{u,amt});}public static void main(String[]a){AuctionSystem aus=new AuctionSystem();aus.bid(1,1,100);}}
