interface Database { void connect(); void query(String q); }
class MySQL implements Database { public void connect() { System.out.println("MySQL"); } public void query(String q) { System.out.println("Execute: " + q); } }
class PostgreSQL implements Database { public void connect() { System.out.println("PostgreSQL"); } public void query(String q) { System.out.println("Execute: " + q); } }
class DBFactory { public static Database create(String type) { return type.equals("mysql") ? new MySQL() : new PostgreSQL(); } }
public class FactoryPattern { public static void main(String[] a) { Database db = DBFactory.create("mysql"); db.connect(); db.query("SELECT *"); } }
