import java.util.*;
public class APIGateway{Map<String,String>routes=new HashMap<>();void register(String p,String s){routes.put(p,s);}String route(String p){return routes.getOrDefault(p,null);}public static void main(String[]a){APIGateway g=new APIGateway();g.register("/users","svc");}}
