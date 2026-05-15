import java.util.*;
/**
 * PhotoSharing - [Brief description]
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
public class PhotoSharing{class Photo{byte[]data;}Map<Integer,Photo>photos=new HashMap<>();void upload(int id,byte[]data){Photo p=new Photo();p.data=data;photos.put(id,p);}public static void main(String[]a){PhotoSharing ps=new PhotoSharing();ps.upload(1,new byte[]{1,2,3});}}
