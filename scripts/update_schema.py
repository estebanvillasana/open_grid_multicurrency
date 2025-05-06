import os
import sqlite3
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.repositories.database import DatabaseConnection


def update_schema():
    """
    Update the database schema to allow NULL values for category and subcategory.
    """
    print("Updating database schema...")
    
    # Get database connection
    db = DatabaseConnection()
    conn = db.get_connection()
    
    try:
        # Create a new transactions table with the updated schema
        conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_name TEXT,
            transaction_description TEXT,
            account_id INTEGER NOT NULL,
            transaction_type TEXT NOT NULL,
            transaction_category INTEGER,
            transaction_sub_category INTEGER,
            transaction_date TEXT NOT NULL,
            transaction_value NUMERIC,
            CONSTRAINT FK_transactions_bank_accounts FOREIGN KEY (account_id) REFERENCES bank_accounts(id),
            CONSTRAINT FK_transactions_categories_2 FOREIGN KEY (transaction_category) REFERENCES categories(id),
            CONSTRAINT FK_transactions_sub_categories_3 FOREIGN KEY (transaction_sub_category) REFERENCES sub_categories(id)
        )
        """)
        
        # Copy data from the old table to the new one
        conn.execute("""
        INSERT INTO transactions_new 
        SELECT * FROM transactions
        """)
        
        # Drop the old table
        conn.execute("DROP TABLE transactions")
        
        # Rename the new table to the original name
        conn.execute("ALTER TABLE transactions_new RENAME TO transactions")
        
        # Commit the changes
        conn.commit()
        
        print("Database schema updated successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error updating schema: {e}")
        return False
    
    return True


if __name__ == "__main__":
    update_schema()
