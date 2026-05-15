import java.util.*;
/**
 * TransactionLedger - [Brief description]
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
public class TransactionLedger{class Entry{int f,t,amt;Entry(int f,int t,int a){this.f=f;this.t=t;this.amt=a;}}List<Entry>entries=new ArrayList<>();void append(int f,int t,int a){entries.add(new Entry(f,t,a));}public static void main(String[]a){TransactionLedger tl=new TransactionLedger();tl.append(1,2,100);}}
