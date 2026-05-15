import java.util.*;
public class TimeSeriesDB{Map<String,List<Object[]>>data=new HashMap<>();void write(String m,long ts,int v){data.computeIfAbsent(m,k->new ArrayList<>()).add(new Object[]{ts,v});}public static void main(String[]a){TimeSeriesDB ts=new TimeSeriesDB();ts.write("cpu",1000,50);}}
