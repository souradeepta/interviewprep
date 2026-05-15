import java.util.*;
/**
 * RecommendationEngine - [Brief description]
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
public class RecommendationEngine{Map<Integer,Set<Integer>>likes=new HashMap<>();void like(int u,int i){likes.computeIfAbsent(u,k->new HashSet<>()).add(i);}public static void main(String[]a){RecommendationEngine re=new RecommendationEngine();re.like(1,1);}}
