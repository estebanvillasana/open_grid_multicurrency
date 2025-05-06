from data.repositories.database import DatabaseConnection
from models.transaction import Transaction


class TransactionRepository:
    """
    Repository for handling transaction data operations.
    """
    
    @staticmethod
    def get_transactions_with_details():
        """
        Get all transactions with related details (account, category, subcategory).
        """
        db = DatabaseConnection()
        query = """
            SELECT 
                t.*,
                a.account,
                a.account_type,
                c.currency_symbol,
                cat.category,
                subcat.sub_category
            FROM 
                transactions t
            LEFT JOIN 
                bank_accounts a ON t.account_id = a.id
            LEFT JOIN 
                currencies c ON a.currency_id = c.id
            LEFT JOIN 
                categories cat ON t.transaction_category = cat.id
            LEFT JOIN 
                sub_categories subcat ON t.transaction_sub_category = subcat.id
            ORDER BY 
                t.transaction_date DESC
        """
        rows = db.fetch_all(query)
        
        transactions = []
        for row in rows:
            transaction = Transaction.from_db_row(row)
            transaction.account_name = row['account']
            transaction.account_type = row['account_type']
            transaction.currency_symbol = row['currency_symbol']
            transaction.category_name = row['category']
            transaction.sub_category_name = row['sub_category'] if row['sub_category'] else ""
            transactions.append(transaction)
        
        return transactions
    
    @staticmethod
    def get_transaction_with_details(transaction_id):
        """
        Get a specific transaction with related details.
        """
        db = DatabaseConnection()
        query = """
            SELECT 
                t.*,
                a.account,
                a.account_type,
                c.currency_symbol,
                cat.category,
                subcat.sub_category
            FROM 
                transactions t
            LEFT JOIN 
                bank_accounts a ON t.account_id = a.id
            LEFT JOIN 
                currencies c ON a.currency_id = c.id
            LEFT JOIN 
                categories cat ON t.transaction_category = cat.id
            LEFT JOIN 
                sub_categories subcat ON t.transaction_sub_category = subcat.id
            WHERE
                t.id = ?
        """
        row = db.fetch_one(query, (transaction_id,))
        
        if not row:
            return None
        
        transaction = Transaction.from_db_row(row)
        transaction.account_name = row['account']
        transaction.account_type = row['account_type']
        transaction.currency_symbol = row['currency_symbol']
        transaction.category_name = row['category']
        transaction.sub_category_name = row['sub_category'] if row['sub_category'] else ""
        
        return transaction
    
    @staticmethod
    def get_transactions_by_account_with_details(account_id):
        """
        Get all transactions for a specific account with related details.
        """
        db = DatabaseConnection()
        query = """
            SELECT 
                t.*,
                a.account,
                a.account_type,
                c.currency_symbol,
                cat.category,
                subcat.sub_category
            FROM 
                transactions t
            LEFT JOIN 
                bank_accounts a ON t.account_id = a.id
            LEFT JOIN 
                currencies c ON a.currency_id = c.id
            LEFT JOIN 
                categories cat ON t.transaction_category = cat.id
            LEFT JOIN 
                sub_categories subcat ON t.transaction_sub_category = subcat.id
            WHERE
                t.account_id = ?
            ORDER BY 
                t.transaction_date DESC
        """
        rows = db.fetch_all(query, (account_id,))
        
        transactions = []
        for row in rows:
            transaction = Transaction.from_db_row(row)
            transaction.account_name = row['account']
            transaction.account_type = row['account_type']
            transaction.currency_symbol = row['currency_symbol']
            transaction.category_name = row['category']
            transaction.sub_category_name = row['sub_category'] if row['sub_category'] else ""
            transactions.append(transaction)
        
        return transactions
