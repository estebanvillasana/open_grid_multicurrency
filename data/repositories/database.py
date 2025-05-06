import sqlite3
import os
from pathlib import Path


class DatabaseConnection:
    """
    Handles database connections and operations for the financial tracker.
    """
    _instance = None
    
    def __new__(cls, db_path=None):
        """Singleton pattern to ensure only one database connection exists."""
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = None
            cls._instance.db_path = db_path
        return cls._instance
    
    def connect(self, db_path=None):
        """Connect to the SQLite database."""
        if db_path:
            self.db_path = db_path
        
        if not self.db_path:
            # Default to the user_data_default_directory if no path is provided
            self.db_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                'user_data_default_directory',
                'financial_tracker.db'
            )
        
        # Ensure the directory exists
        Path(os.path.dirname(self.db_path)).mkdir(parents=True, exist_ok=True)
        
        # Connect to the database
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        
        return self.connection
    
    def get_connection(self):
        """Get the current database connection or create a new one."""
        if self.connection is None:
            self.connect()
        return self.connection
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query, params=None):
        """Execute a query and return the results."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            return cursor
        except Exception as e:
            conn.rollback()
            raise e
    
    def fetch_all(self, query, params=None):
        """Execute a query and fetch all results."""
        cursor = self.execute_query(query, params)
        return cursor.fetchall()
    
    def fetch_one(self, query, params=None):
        """Execute a query and fetch one result."""
        cursor = self.execute_query(query, params)
        return cursor.fetchone()
    
    def insert(self, table, data):
        """Insert data into a table."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        cursor = self.execute_query(query, tuple(data.values()))
        return cursor.lastrowid
    
    def update(self, table, data, condition):
        """Update data in a table."""
        set_clause = ', '.join([f"{column} = ?" for column in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        
        self.execute_query(query, tuple(data.values()))
    
    def delete(self, table, condition):
        """Delete data from a table."""
        query = f"DELETE FROM {table} WHERE {condition}"
        self.execute_query(query)
