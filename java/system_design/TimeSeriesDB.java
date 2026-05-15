import java.util.*;
/**
 * TimeSeriesDB - [Brief description]
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
public class TimeSeriesDB{Map<String,List<Object[]>>data=new HashMap<>();void write(String m,long ts,int v){data.computeIfAbsent(m,k->new ArrayList<>()).add(new Object[]{ts,v});}public static void main(String[]a){TimeSeriesDB ts=new TimeSeriesDB();ts.write("cpu",1000,50);}}
