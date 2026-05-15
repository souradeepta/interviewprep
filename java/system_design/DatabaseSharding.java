import java.util.*;
public class DatabaseSharding{class Shard{Map<String,Object>data=new HashMap<>();}Shard[]shards;DatabaseSharding(int n){shards=new Shard[n];for(int i=0;i<n;i++)shards[i]=new Shard();}void put(String k,Object v){shards[k.hashCode()%shards.length].data.put(k,v);}public static void main(String[]a){DatabaseSharding ds=new DatabaseSharding(3);ds.put("x",1);}}
