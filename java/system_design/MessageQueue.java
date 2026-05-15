import java.util.*;
public class MessageQueue{class Topic{Queue<String>q=new LinkedList<>();}Map<String,Topic>topics=new HashMap<>();void createTopic(String t){topics.put(t,new Topic());}void publish(String t,String m){topics.get(t).q.add(m);}public static void main(String[]a){MessageQueue mq=new MessageQueue();mq.createTopic("t1");mq.publish("t1","msg");}}
