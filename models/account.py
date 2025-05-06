from data.repositories.database import DatabaseConnection


class Account:
    """
    Represents a bank account in the system.
    """
    def __init__(self, id=None, name="", account_type="Bank Account", 
                 details="", currency_id=None, initial_value=0.0):
        self.id = id
        self.name = name
        self.account_type = account_type
        self.details = details
        self.currency_id = currency_id
        self.initial_value = initial_value
    
    @classmethod
    def from_db_row(cls, row):
        """Create an Account object from a database row."""
        if not row:
            return None
        
        return cls(
            id=row['id'],
            name=row['account'],
            account_type=row['account_type'],
            details=row['account_details'],
            currency_id=row['currency_id'],
            initial_value=row['account_initial_value'] if row['account_initial_value'] else 0.0
        )
    
    def to_dict(self):
        """Convert the Account object to a dictionary for database operations."""
        return {
            'account': self.name,
            'account_type': self.account_type,
            'account_details': self.details,
            'currency_id': self.currency_id,
            'account_initial_value': self.initial_value
        }
    
    def save(self):
        """Save the account to the database."""
        db = DatabaseConnection()
        
        if self.id is None:
            # Insert new account
            self.id = db.insert('bank_accounts', self.to_dict())
        else:
            # Update existing account
            db.update('bank_accounts', self.to_dict(), f"id = {self.id}")
        
        return self.id
    
    def delete(self):
        """Delete the account from the database."""
        if self.id is None:
            return False
        
        db = DatabaseConnection()
        db.delete('bank_accounts', f"id = {self.id}")
        return True
    
    @staticmethod
    def get_all():
        """Get all accounts from the database."""
        db = DatabaseConnection()
        rows = db.fetch_all("SELECT * FROM bank_accounts ORDER BY account")
        return [Account.from_db_row(row) for row in rows]
    
    @staticmethod
    def get_by_id(account_id):
        """Get an account by its ID."""
        db = DatabaseConnection()
        row = db.fetch_one("SELECT * FROM bank_accounts WHERE id = ?", (account_id,))
        return Account.from_db_row(row)
    
    @staticmethod
    def get_by_currency(currency_id):
        """Get all accounts for a specific currency."""
        db = DatabaseConnection()
        rows = db.fetch_all(
            "SELECT * FROM bank_accounts WHERE currency_id = ? ORDER BY account", 
            (currency_id,)
        )
        return [Account.from_db_row(row) for row in rows]
    
    @staticmethod
    def get_with_currency_info():
        """Get all accounts with their currency information."""
        db = DatabaseConnection()
        query = """
            SELECT 
                ba.*, 
                c.currency, 
                c.currency_code, 
                c.currency_symbol
            FROM 
                bank_accounts ba
            JOIN 
                currencies c ON ba.currency_id = c.id
            ORDER BY 
                ba.account
        """
        rows = db.fetch_all(query)
        accounts = []
        
        for row in rows:
            account = Account.from_db_row(row)
            account.currency_name = row['currency']
            account.currency_code = row['currency_code']
            account.currency_symbol = row['currency_symbol']
            accounts.append(account)
        
        return accounts
