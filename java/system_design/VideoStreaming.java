import java.util.*;
public class VideoStreaming{class Video{String[]bitrates;}Map<Integer,Video>videos=new HashMap<>();void upload(int id){Video v=new Video();v.bitrates=new String[]{"480p","720p","1080p"};videos.put(id,v);}public static void main(String[]a){VideoStreaming vs=new VideoStreaming();vs.upload(1);}}
