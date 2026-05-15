import java.util.*;
/**
 * MessageQueue - [Brief description]
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
public class MessageQueue{class Topic{Queue<String>q=new LinkedList<>();}Map<String,Topic>topics=new HashMap<>();void createTopic(String t){topics.put(t,new Topic());}void publish(String t,String m){topics.get(t).q.add(m);}public static void main(String[]a){MessageQueue mq=new MessageQueue();mq.createTopic("t1");mq.publish("t1","msg");}}
