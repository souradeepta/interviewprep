import java.util.*;
/**
 * LikeCommentSystem - [Brief description]
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
public class LikeCommentSystem{Map<Integer,Integer>likes=new HashMap<>();void like(int pid){likes.put(pid,likes.getOrDefault(pid,0)+1);}int getLikes(int pid){return likes.getOrDefault(pid,0);}public static void main(String[]a){LikeCommentSystem lcs=new LikeCommentSystem();lcs.like(1);System.out.println(lcs.getLikes(1));}}
