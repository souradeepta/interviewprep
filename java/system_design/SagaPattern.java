import java.util.*;
/**
 * SagaPattern - [Brief description]
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
public class SagaPattern{List<String>steps=new ArrayList<>();void addStep(String s){steps.add(s);}void execute(){System.out.println("Executing: "+steps);}public static void main(String[]a){SagaPattern s=new SagaPattern();s.addStep("debit");s.execute();}}
