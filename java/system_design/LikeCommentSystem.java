import java.util.*;
public class LikeCommentSystem{Map<Integer,Integer>likes=new HashMap<>();void like(int pid){likes.put(pid,likes.getOrDefault(pid,0)+1);}int getLikes(int pid){return likes.getOrDefault(pid,0);}public static void main(String[]a){LikeCommentSystem lcs=new LikeCommentSystem();lcs.like(1);System.out.println(lcs.getLikes(1));}}
