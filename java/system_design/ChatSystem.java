import java.util.*;
/**
 * ChatSystem - [Brief description]
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
public class ChatSystem{class Msg{int f,t;String txt;Msg(int f,int t,String txt){this.f=f;this.t=t;this.txt=txt;}}Map<Integer,Msg>msgs=new HashMap<>();void send(int f,int t,String txt){msgs.put(msgs.size(),new Msg(f,t,txt));}public static void main(String[]a){ChatSystem c=new ChatSystem();c.send(1,2,"Hi");}}
