import java.util.*;
/**
 * Notifications - [Brief description]
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
public class Notifications{Map<Integer,List<String>>notifs=new HashMap<>();void send(int u,String m){notifs.computeIfAbsent(u,k->new ArrayList<>()).add(m);}public static void main(String[]a){Notifications n=new Notifications();n.send(1,"Hi");}}
