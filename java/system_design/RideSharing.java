import java.util.*;
public class RideSharing{class Ride{int rid;String status="searching";}Map<Integer,Ride>rides=new HashMap<>();Ride request(int rid){Ride r=new Ride();r.rid=rid;rides.put(rid,r);return r;}public static void main(String[]a){RideSharing rs=new RideSharing();rs.request(1);}}
