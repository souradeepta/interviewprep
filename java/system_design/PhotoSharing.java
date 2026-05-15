import java.util.*;
public class PhotoSharing{class Photo{byte[]data;}Map<Integer,Photo>photos=new HashMap<>();void upload(int id,byte[]data){Photo p=new Photo();p.data=data;photos.put(id,p);}public static void main(String[]a){PhotoSharing ps=new PhotoSharing();ps.upload(1,new byte[]{1,2,3});}}
