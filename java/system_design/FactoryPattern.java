interface Database { void connect(); void query(String q); }
/**
 * [Brief description]
 *
 * @param [param] [description]
 * @return [description]
 * @time O([complexity])
 */
class MySQL implements Database { public void connect() { System.out.println("MySQL"); } public void query(String q) { System.out.println("Execute: " + q); } }
/**
 * [Brief description]
 *
 * @param [param] [description]
 * @return [description]
 * @time O([complexity])
 */
class PostgreSQL implements Database { public void connect() { System.out.println("PostgreSQL"); } public void query(String q) { System.out.println("Execute: " + q); } }
/**
 * [Brief description]
 *
 * @param [param] [description]
 * @return [description]
 * @time O([complexity])
 */
class DBFactory { public static Database create(String type) { return type.equals("mysql") ? new MySQL() : new PostgreSQL(); } }
/**
 * FactoryPattern - [Brief description]
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
public class FactoryPattern { public static void main(String[] a) { Database db = DBFactory.create("mysql"); db.connect(); db.query("SELECT *"); } }
