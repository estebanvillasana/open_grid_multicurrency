from data.repositories.database import DatabaseConnection


class Category:
    """
    Represents a transaction category in the system.
    """
    def __init__(self, id=None, name="", category_type="Expense"):
        self.id = id
        self.name = name
        self.category_type = category_type
    
    @classmethod
    def from_db_row(cls, row):
        """Create a Category object from a database row."""
        if not row:
            return None
        
        return cls(
            id=row['id'],
            name=row['category'],
            category_type=row['type']
        )
    
    def to_dict(self):
        """Convert the Category object to a dictionary for database operations."""
        return {
            'category': self.name,
            'type': self.category_type
        }
    
    def save(self):
        """Save the category to the database."""
        db = DatabaseConnection()
        
        if self.id is None:
            # Insert new category
            self.id = db.insert('categories', self.to_dict())
        else:
            # Update existing category
            db.update('categories', self.to_dict(), f"id = {self.id}")
        
        return self.id
    
    def delete(self):
        """Delete the category from the database."""
        if self.id is None:
            return False
        
        db = DatabaseConnection()
        db.delete('categories', f"id = {self.id}")
        return True
    
    @staticmethod
    def get_all():
        """Get all categories from the database."""
        db = DatabaseConnection()
        rows = db.fetch_all("SELECT * FROM categories ORDER BY category")
        return [Category.from_db_row(row) for row in rows]
    
    @staticmethod
    def get_by_id(category_id):
        """Get a category by its ID."""
        db = DatabaseConnection()
        row = db.fetch_one("SELECT * FROM categories WHERE id = ?", (category_id,))
        return Category.from_db_row(row)
    
    @staticmethod
    def get_by_type(category_type):
        """Get all categories of a specific type."""
        db = DatabaseConnection()
        rows = db.fetch_all(
            "SELECT * FROM categories WHERE type = ? ORDER BY category", 
            (category_type,)
        )
        return [Category.from_db_row(row) for row in rows]


class SubCategory:
    """
    Represents a transaction sub-category in the system.
    """
    def __init__(self, id=None, name="", category_id=None):
        self.id = id
        self.name = name
        self.category_id = category_id
    
    @classmethod
    def from_db_row(cls, row):
        """Create a SubCategory object from a database row."""
        if not row:
            return None
        
        return cls(
            id=row['id'],
            name=row['sub_category'],
            category_id=row['category_id']
        )
    
    def to_dict(self):
        """Convert the SubCategory object to a dictionary for database operations."""
        return {
            'sub_category': self.name,
            'category_id': self.category_id
        }
    
    def save(self):
        """Save the sub-category to the database."""
        db = DatabaseConnection()
        
        if self.id is None:
            # Insert new sub-category
            self.id = db.insert('sub_categories', self.to_dict())
        else:
            # Update existing sub-category
            db.update('sub_categories', self.to_dict(), f"id = {self.id}")
        
        return self.id
    
    def delete(self):
        """Delete the sub-category from the database."""
        if self.id is None:
            return False
        
        db = DatabaseConnection()
        db.delete('sub_categories', f"id = {self.id}")
        return True
    
    @staticmethod
    def get_all():
        """Get all sub-categories from the database."""
        db = DatabaseConnection()
        rows = db.fetch_all("SELECT * FROM sub_categories ORDER BY sub_category")
        return [SubCategory.from_db_row(row) for row in rows]
    
    @staticmethod
    def get_by_id(subcategory_id):
        """Get a sub-category by its ID."""
        db = DatabaseConnection()
        row = db.fetch_one("SELECT * FROM sub_categories WHERE id = ?", (subcategory_id,))
        return SubCategory.from_db_row(row)
    
    @staticmethod
    def get_by_category(category_id):
        """Get all sub-categories for a specific category."""
        db = DatabaseConnection()
        rows = db.fetch_all(
            "SELECT * FROM sub_categories WHERE category_id = ? ORDER BY sub_category", 
            (category_id,)
        )
        return [SubCategory.from_db_row(row) for row in rows]
