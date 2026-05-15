import java.util.*;
/**
 * RideSharing - [Brief description]
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
public class RideSharing{class Ride{int rid;String status="searching";}Map<Integer,Ride>rides=new HashMap<>();Ride request(int rid){Ride r=new Ride();r.rid=rid;rides.put(rid,r);return r;}public static void main(String[]a){RideSharing rs=new RideSharing();rs.request(1);}}
