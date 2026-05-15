import java.util.*;
public class LogAggregator{List<String>logs=new ArrayList<>();void collect(String h,String m){logs.add(m);}List<String>search(String q){return logs.stream().filter(l->l.contains(q)).collect(Collectors.toList());}public static void main(String[]a){LogAggregator la=new LogAggregator();la.collect("h1","error");}}
