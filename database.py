"""
Database management module for the Organization Management System
"""

from types import TracebackType
from mysql.connector import connect
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor

class DatabaseManager:
    connection: MySQLConnection
    cursor: MySQLCursor

    def close(self):
        """Close the database connection"""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("✓ Database connection closed")

    def __init__(self, /, *, host: str = 'localhost', database: str = 'studentorg', user: str = 'admin', password: str = 'admin'):
        self.connection = connect(
            host = host,
            database = database,
            user = user,
            password = password
        ) # type: ignore
        self.cursor = self.connection.cursor()
        print("✓ Database connection established")

    def __del__(self):
        """Ensure the database connection is closed when the object is deleted"""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()

    def __enter__(self):
        """Enter the runtime context related to this object"""
        return self
    
    def __exit__(self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None) -> bool | None:
        """Exit the runtime context related to this object"""
        self.close()
        if exc_type is not None:
            print(f"An error occurred: {exc_value}")
        return False
