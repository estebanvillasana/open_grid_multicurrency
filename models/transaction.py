from datetime import datetime
from data.repositories.database import DatabaseConnection


class Transaction:
    """
    Represents a financial transaction in the system.
    """
    def __init__(self, id=None, name="", description="", account_id=None, 
                 transaction_type="Expense", category_id=None, sub_category_id=None, 
                 date=None, value=0.0):
        self.id = id
        self.name = name
        self.description = description
        self.account_id = account_id
        self.transaction_type = transaction_type
        self.category_id = category_id
        self.sub_category_id = sub_category_id
        self.date = date if date else datetime.now().strftime("%Y-%m-%d")
        self.value = value
    
    @classmethod
    def from_db_row(cls, row):
        """Create a Transaction object from a database row."""
        if not row:
            return None
        
        return cls(
            id=row['id'],
            name=row['transaction_name'],
            description=row['transaction_description'],
            account_id=row['account_id'],
            transaction_type=row['transaction_type'],
            category_id=row['transaction_category'],
            sub_category_id=row['transaction_sub_category'],
            date=row['transaction_date'],
            value=row['transaction_value']
        )
    
    def to_dict(self):
        """Convert the Transaction object to a dictionary for database operations."""
        return {
            'transaction_name': self.name,
            'transaction_description': self.description,
            'account_id': self.account_id,
            'transaction_type': self.transaction_type,
            'transaction_category': self.category_id,
            'transaction_sub_category': self.sub_category_id,
            'transaction_date': self.date,
            'transaction_value': self.value
        }
    
    def save(self):
        """Save the transaction to the database."""
        db = DatabaseConnection()
        
        if self.id is None:
            # Insert new transaction
            self.id = db.insert('transactions', self.to_dict())
        else:
            # Update existing transaction
            db.update('transactions', self.to_dict(), f"id = {self.id}")
        
        return self.id
    
    def delete(self):
        """Delete the transaction from the database."""
        if self.id is None:
            return False
        
        db = DatabaseConnection()
        db.delete('transactions', f"id = {self.id}")
        return True
    
    @staticmethod
    def get_all():
        """Get all transactions from the database."""
        db = DatabaseConnection()
        rows = db.fetch_all("SELECT * FROM transactions ORDER BY transaction_date DESC")
        return [Transaction.from_db_row(row) for row in rows]
    
    @staticmethod
    def get_by_id(transaction_id):
        """Get a transaction by its ID."""
        db = DatabaseConnection()
        row = db.fetch_one("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
        return Transaction.from_db_row(row)
    
    @staticmethod
    def get_by_account(account_id):
        """Get all transactions for a specific account."""
        db = DatabaseConnection()
        rows = db.fetch_all(
            "SELECT * FROM transactions WHERE account_id = ? ORDER BY transaction_date DESC", 
            (account_id,)
        )
        return [Transaction.from_db_row(row) for row in rows]
    
    @staticmethod
    def get_by_category(category_id):
        """Get all transactions for a specific category."""
        db = DatabaseConnection()
        rows = db.fetch_all(
            "SELECT * FROM transactions WHERE transaction_category = ? ORDER BY transaction_date DESC", 
            (category_id,)
        )
        return [Transaction.from_db_row(row) for row in rows]
