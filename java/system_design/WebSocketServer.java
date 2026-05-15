import java.util.*;
public class WebSocketServer{Map<Integer,String>clients=new HashMap<>();void connect(int id){clients.put(id,"connected");}void send(int id,String msg){System.out.println("Sent: "+msg);}public static void main(String[]a){WebSocketServer ws=new WebSocketServer();ws.connect(1);}}
