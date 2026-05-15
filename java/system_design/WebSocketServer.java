import java.util.*;
/**
 * WebSocketServer - [Brief description]
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
public class WebSocketServer{Map<Integer,String>clients=new HashMap<>();void connect(int id){clients.put(id,"connected");}void send(int id,String msg){System.out.println("Sent: "+msg);}public static void main(String[]a){WebSocketServer ws=new WebSocketServer();ws.connect(1);}}
