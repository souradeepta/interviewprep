import java.util.*;
/**
 * SearchEngine - [Brief description]
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
public class SearchEngine{Map<String,List<Integer>>idx=new HashMap<>();void indexDoc(int did,String txt){for(String w:txt.split(" "))idx.computeIfAbsent(w,k->new ArrayList<>()).add(did);}List<Integer>search(String q){return idx.getOrDefault(q,new ArrayList<>());}public static void main(String[]a){SearchEngine se=new SearchEngine();se.indexDoc(1,"python");System.out.println(se.search("python"));}}
