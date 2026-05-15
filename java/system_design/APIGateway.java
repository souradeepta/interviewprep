import java.util.*;
/**
 * APIGateway - [Brief description]
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
public class APIGateway{Map<String,String>routes=new HashMap<>();void register(String p,String s){routes.put(p,s);}String route(String p){return routes.getOrDefault(p,null);}public static void main(String[]a){APIGateway g=new APIGateway();g.register("/users","svc");}}
