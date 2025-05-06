from data.repositories.database import DatabaseConnection


class Currency:
    """
    Represents a currency in the system.
    """
    def __init__(self, id=None, name="", code="", symbol=""):
        self.id = id
        self.name = name
        self.code = code
        self.symbol = symbol
    
    @classmethod
    def from_db_row(cls, row):
        """Create a Currency object from a database row."""
        if not row:
            return None
        
        return cls(
            id=row['id'],
            name=row['currency'],
            code=row['currency_code'],
            symbol=row['currency_symbol']
        )
    
    def to_dict(self):
        """Convert the Currency object to a dictionary for database operations."""
        return {
            'currency': self.name,
            'currency_code': self.code,
            'currency_symbol': self.symbol
        }
    
    def save(self):
        """Save the currency to the database."""
        db = DatabaseConnection()
        
        if self.id is None:
            # Insert new currency
            self.id = db.insert('currencies', self.to_dict())
        else:
            # Update existing currency
            db.update('currencies', self.to_dict(), f"id = {self.id}")
        
        return self.id
    
    def delete(self):
        """Delete the currency from the database."""
        if self.id is None:
            return False
        
        db = DatabaseConnection()
        db.delete('currencies', f"id = {self.id}")
        return True
    
    @staticmethod
    def get_all():
        """Get all currencies from the database."""
        db = DatabaseConnection()
        rows = db.fetch_all("SELECT * FROM currencies ORDER BY currency")
        return [Currency.from_db_row(row) for row in rows]
    
    @staticmethod
    def get_by_id(currency_id):
        """Get a currency by its ID."""
        db = DatabaseConnection()
        row = db.fetch_one("SELECT * FROM currencies WHERE id = ?", (currency_id,))
        return Currency.from_db_row(row)
    
    @staticmethod
    def get_by_code(currency_code):
        """Get a currency by its code."""
        db = DatabaseConnection()
        row = db.fetch_one("SELECT * FROM currencies WHERE currency_code = ?", (currency_code,))
        return Currency.from_db_row(row)
