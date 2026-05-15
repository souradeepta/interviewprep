import java.util.*;
/**
 * NewsFeed - [Brief description]
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
public class NewsFeed{Map<Integer,List<Integer>>f=new HashMap<>();Map<Integer,String>p=new HashMap<>();void post(int u,String c){p.put(u,c);for(int x:f.getOrDefault(u,new ArrayList<>()))System.out.println(x);}void follow(int u,int t){f.computeIfAbsent(t,k->new ArrayList<>()).add(u);}public static void main(String[]a){NewsFeed n=new NewsFeed();n.follow(1,2);n.post(2,"Hi");}}
