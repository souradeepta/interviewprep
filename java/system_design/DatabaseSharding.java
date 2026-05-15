import java.util.*;
/**
 * DatabaseSharding - [Brief description]
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
public class DatabaseSharding{class Shard{Map<String,Object>data=new HashMap<>();}Shard[]shards;DatabaseSharding(int n){shards=new Shard[n];for(int i=0;i<n;i++)shards[i]=new Shard();}void put(String k,Object v){shards[k.hashCode()%shards.length].data.put(k,v);}public static void main(String[]a){DatabaseSharding ds=new DatabaseSharding(3);ds.put("x",1);}}
