import java.util.*;
/**
 * ConsensusAlgorithm - [Brief description]
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
public class ConsensusAlgorithm{enum State{FOLLOWER,CANDIDATE,LEADER}State state=State.FOLLOWER;int term=0;void startElection(){state=State.CANDIDATE;term++;}public static void main(String[]a){ConsensusAlgorithm ca=new ConsensusAlgorithm();ca.startElection();}}
