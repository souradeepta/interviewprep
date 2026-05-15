"""Factory Pattern - Object creation abstraction"""

from abc import ABC, abstractmethod


class Database(ABC):
    """Database interface"""

    @abstractmethod
        """connect implementation.

        Time: O(n)
        Space: O(1)
        """
    def connect(self):
        raise NotImplementedError

    @abstractmethod
        """execute_query implementation.

        Time: O(n)
        Space: O(1)
        """
    def execute_query(self, query: str):
        raise NotImplementedError


class MySQLDatabase(Database):
    """MySQL database"""

        """connect implementation.

        Time: O(n)
        Space: O(1)
        """
    def connect(self):
        print("Connecting to MySQL database...")

        """execute_query implementation.

        Time: O(n)
        Space: O(1)
        """
    def execute_query(self, query: str):
        print(f"MySQL: Executing query: {query}")


class PostgreSQLDatabase(Database):
    """PostgreSQL database"""

        """connect implementation.

        Time: O(n)
        Space: O(1)
        """
    def connect(self):
        print("Connecting to PostgreSQL database...")

        """execute_query implementation.

        Time: O(n)
        Space: O(1)
        """
    def execute_query(self, query: str):
        print(f"PostgreSQL: Executing query: {query}")


class MongoDBDatabase(Database):
    """MongoDB database"""

        """connect implementation.

        Time: O(n)
        Space: O(1)
        """
    def connect(self):
        print("Connecting to MongoDB database...")

        """execute_query implementation.

        Time: O(n)
        Space: O(1)
        """
    def execute_query(self, query: str):
        print(f"MongoDB: Executing query: {query}")


class DatabaseFactory:
    """Factory for creating database instances"""

    @staticmethod
    def create_database(db_type: str) -> Database:
        """Create database instance based on type"""
        if db_type == "mysql":
            return MySQLDatabase()
        elif db_type == "postgresql":
            return PostgreSQLDatabase()
        elif db_type == "mongodb":
            return MongoDBDatabase()
        else:
            raise ValueError(f"Unknown database type: {db_type}")


if __name__ == "__main__":
    # Create MySQL database
    mysql_db = DatabaseFactory.create_database("mysql")
    mysql_db.connect()
    mysql_db.execute_query("SELECT * FROM users")

    print()

    # Create PostgreSQL database
    pg_db = DatabaseFactory.create_database("postgresql")
    pg_db.connect()
    pg_db.execute_query("SELECT * FROM products")

    print()

    # Create MongoDB database
    mongo_db = DatabaseFactory.create_database("mongodb")
    mongo_db.connect()
    mongo_db.execute_query("db.users.find({})")