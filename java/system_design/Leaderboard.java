import java.util.*;
/**
 * Leaderboard - [Brief description]
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
public class Leaderboard{Map<Integer,Integer>scores=new HashMap<>();void update(int u,int pts){scores.put(u,scores.getOrDefault(u,0)+pts);}public static void main(String[]a){Leaderboard lb=new Leaderboard();lb.update(1,100);System.out.println(scores);}}
