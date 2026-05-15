import java.util.*;
/**
 * LogAggregator - [Brief description]
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
public class LogAggregator{List<String>logs=new ArrayList<>();void collect(String h,String m){logs.add(m);}List<String>search(String q){return logs.stream().filter(l->l.contains(q)).collect(Collectors.toList());}public static void main(String[]a){LogAggregator la=new LogAggregator();la.collect("h1","error");}}
