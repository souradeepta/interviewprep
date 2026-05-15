import java.util.*;
/**
 * FollowersSystem - [Brief description]
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
public class FollowersSystem{Map<Integer,Set<Integer>>followers=new HashMap<>();void follow(int u,int t){followers.computeIfAbsent(t,k->new HashSet<>()).add(u);}public static void main(String[]a){FollowersSystem fs=new FollowersSystem();fs.follow(1,2);}}
