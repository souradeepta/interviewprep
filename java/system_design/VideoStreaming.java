import java.util.*;
/**
 * VideoStreaming - [Brief description]
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
public class VideoStreaming{class Video{String[]bitrates;}Map<Integer,Video>videos=new HashMap<>();void upload(int id){Video v=new Video();v.bitrates=new String[]{"480p","720p","1080p"};videos.put(id,v);}public static void main(String[]a){VideoStreaming vs=new VideoStreaming();vs.upload(1);}}
