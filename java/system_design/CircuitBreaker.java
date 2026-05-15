import java.util.*;
/**
 * CircuitBreaker - [Brief description]
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
public class CircuitBreaker{enum State{CLOSED,OPEN,HALF_OPEN}State state=State.CLOSED;int failures=0;void fail(){failures++;if(failures>=5)state=State.OPEN;}public static void main(String[]a){CircuitBreaker cb=new CircuitBreaker();for(int i=0;i<5;i++)cb.fail();}}
