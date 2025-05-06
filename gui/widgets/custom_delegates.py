from PyQt6.QtWidgets import (
    QStyledItemDelegate, QComboBox, QDateEdit, QLineEdit, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QDate, QModelIndex
from PyQt6.QtGui import QDoubleValidator

from models.account import Account
from models.category import Category, SubCategory


class ComboBoxDelegate(QStyledItemDelegate):
    """
    Delegate for displaying a combo box in a table cell.
    """
    def __init__(self, parent=None, items=None, item_data=None):
        super().__init__(parent)
        self.items = items or []
        self.item_data = item_data or []
    
    def createEditor(self, parent, option, index):
        """Create the combo box editor."""
        editor = QComboBox(parent)
        editor.addItems(self.items)
        
        # Set item data if available
        if self.item_data and len(self.item_data) == len(self.items):
            for i, data in enumerate(self.item_data):
                editor.setItemData(i, data)
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the editor data."""
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        if value:
            for i in range(editor.count()):
                if editor.itemText(i) == value:
                    editor.setCurrentIndex(i)
                    break
    
    def setModelData(self, editor, model, index):
        """Set the model data."""
        value = editor.currentText()
        data = editor.currentData()
        
        model.setData(index, value, Qt.ItemDataRole.EditRole)
        model.setData(index, data, Qt.ItemDataRole.UserRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update the editor geometry."""
        editor.setGeometry(option.rect)


class AccountDelegate(QStyledItemDelegate):
    """
    Delegate for displaying and editing account information.
    """
    def createEditor(self, parent, option, index):
        """Create the combo box editor."""
        editor = QComboBox(parent)
        
        # Load accounts
        accounts = Account.get_all()
        for account in accounts:
            editor.addItem(account.name, account.id)
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the editor data."""
        account_id = index.model().data(index, Qt.ItemDataRole.UserRole)
        
        if account_id:
            for i in range(editor.count()):
                if editor.itemData(i) == account_id:
                    editor.setCurrentIndex(i)
                    break
    
    def setModelData(self, editor, model, index):
        """Set the model data."""
        account_name = editor.currentText()
        account_id = editor.currentData()
        
        model.setData(index, account_name, Qt.ItemDataRole.EditRole)
        model.setData(index, account_id, Qt.ItemDataRole.UserRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update the editor geometry."""
        editor.setGeometry(option.rect)


class CategoryDelegate(QStyledItemDelegate):
    """
    Delegate for displaying and editing category information.
    """
    def createEditor(self, parent, option, index):
        """Create the combo box editor."""
        editor = QComboBox(parent)
        
        # Get transaction type from the same row
        model = index.model()
        type_index = model.index(index.row(), 4)  # Assuming type is in column 4
        transaction_type = model.data(type_index, Qt.ItemDataRole.EditRole)
        
        # Load categories based on transaction type
        categories = Category.get_by_type(transaction_type or "Expense")
        for category in categories:
            editor.addItem(category.name, category.id)
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the editor data."""
        category_id = index.model().data(index, Qt.ItemDataRole.UserRole)
        
        if category_id:
            for i in range(editor.count()):
                if editor.itemData(i) == category_id:
                    editor.setCurrentIndex(i)
                    break
    
    def setModelData(self, editor, model, index):
        """Set the model data."""
        category_name = editor.currentText()
        category_id = editor.currentData()
        
        model.setData(index, category_name, Qt.ItemDataRole.EditRole)
        model.setData(index, category_id, Qt.ItemDataRole.UserRole)
        
        # Also update subcategory cell to empty since category changed
        subcategory_index = model.index(index.row(), 7)  # Assuming subcategory is in column 7
        model.setData(subcategory_index, "", Qt.ItemDataRole.EditRole)
        model.setData(subcategory_index, None, Qt.ItemDataRole.UserRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update the editor geometry."""
        editor.setGeometry(option.rect)


class SubCategoryDelegate(QStyledItemDelegate):
    """
    Delegate for displaying and editing subcategory information.
    """
    def createEditor(self, parent, option, index):
        """Create the combo box editor."""
        editor = QComboBox(parent)
        
        # Get category ID from the same row
        model = index.model()
        category_index = model.index(index.row(), 6)  # Assuming category is in column 6
        category_id = model.data(category_index, Qt.ItemDataRole.UserRole)
        
        # Add empty option
        editor.addItem("", None)
        
        # Load subcategories based on category
        if category_id:
            subcategories = SubCategory.get_by_category(category_id)
            for subcategory in subcategories:
                editor.addItem(subcategory.name, subcategory.id)
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the editor data."""
        subcategory_id = index.model().data(index, Qt.ItemDataRole.UserRole)
        
        if subcategory_id:
            for i in range(editor.count()):
                if editor.itemData(i) == subcategory_id:
                    editor.setCurrentIndex(i)
                    break
    
    def setModelData(self, editor, model, index):
        """Set the model data."""
        subcategory_name = editor.currentText()
        subcategory_id = editor.currentData()
        
        model.setData(index, subcategory_name, Qt.ItemDataRole.EditRole)
        model.setData(index, subcategory_id, Qt.ItemDataRole.UserRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update the editor geometry."""
        editor.setGeometry(option.rect)


class DateDelegate(QStyledItemDelegate):
    """
    Delegate for displaying and editing dates.
    """
    def createEditor(self, parent, option, index):
        """Create the date editor."""
        editor = QDateEdit(parent)
        editor.setCalendarPopup(True)
        editor.setDisplayFormat("yyyy-MM-dd")
        return editor
    
    def setEditorData(self, editor, index):
        """Set the editor data."""
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        if value:
            date = QDate.fromString(value, "yyyy-MM-dd")
            if date.isValid():
                editor.setDate(date)
            else:
                editor.setDate(QDate.currentDate())
        else:
            editor.setDate(QDate.currentDate())
    
    def setModelData(self, editor, model, index):
        """Set the model data."""
        value = editor.date().toString("yyyy-MM-dd")
        model.setData(index, value, Qt.ItemDataRole.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update the editor geometry."""
        editor.setGeometry(option.rect)


class CurrencyDelegate(QStyledItemDelegate):
    """
    Delegate for displaying and editing currency values.
    """
    def createEditor(self, parent, option, index):
        """Create the currency editor."""
        editor = QDoubleSpinBox(parent)
        editor.setDecimals(2)
        editor.setMinimum(-1000000.00)
        editor.setMaximum(1000000.00)
        editor.setSingleStep(1.00)
        return editor
    
    def setEditorData(self, editor, index):
        """Set the editor data."""
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        try:
            editor.setValue(float(value) if value else 0.0)
        except (ValueError, TypeError):
            editor.setValue(0.0)
    
    def setModelData(self, editor, model, index):
        """Set the model data."""
        value = str(editor.value())
        model.setData(index, value, Qt.ItemDataRole.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update the editor geometry."""
        editor.setGeometry(option.rect)


class TransactionTypeDelegate(QStyledItemDelegate):
    """
    Delegate for displaying and editing transaction types.
    """
    def createEditor(self, parent, option, index):
        """Create the combo box editor."""
        editor = QComboBox(parent)
        editor.addItems(["Expense", "Income"])
        return editor
    
    def setEditorData(self, editor, index):
        """Set the editor data."""
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        if value:
            for i in range(editor.count()):
                if editor.itemText(i) == value:
                    editor.setCurrentIndex(i)
                    break
    
    def setModelData(self, editor, model, index):
        """Set the model data."""
        value = editor.currentText()
        model.setData(index, value, Qt.ItemDataRole.EditRole)
        
        # Also update category cell since transaction type changed
        category_index = model.index(index.row(), 6)  # Assuming category is in column 6
        model.setData(category_index, "", Qt.ItemDataRole.EditRole)
        model.setData(category_index, None, Qt.ItemDataRole.UserRole)
        
        # Also update subcategory cell
        subcategory_index = model.index(index.row(), 7)  # Assuming subcategory is in column 7
        model.setData(subcategory_index, "", Qt.ItemDataRole.EditRole)
        model.setData(subcategory_index, None, Qt.ItemDataRole.UserRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update the editor geometry."""
        editor.setGeometry(option.rect)
