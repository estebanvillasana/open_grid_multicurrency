from PyQt6.QtWidgets import (
    QStyledItemDelegate, QComboBox, QDateEdit, QLineEdit, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QDate, QModelIndex
from PyQt6.QtGui import QDoubleValidator, QColor, QBrush

from models.account import Account
from models.category import Category, SubCategory


class BaseRowColorDelegate(QStyledItemDelegate):
    """
    Base delegate class that handles row coloring based on row state.
    All other delegates should inherit from this class.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # Define colors - more elegant with less saturation
        self.new_row_color = QColor(213, 232, 250, 100)  # Soft blue for new rows
        self.modified_row_color = QColor(255, 248, 214, 100)  # Soft yellow for modified existing rows
        self.error_row_color = QColor(250, 220, 220, 180)  # Soft red for error rows
        self.error_field_color = QColor(255, 200, 200, 220)  # Slightly more intense red for error fields

        # Very subtle colors for transaction types
        self.income_color = QColor(230, 245, 230, 30)  # Very subtle green
        self.expense_color = QColor(245, 230, 230, 30)  # Very subtle red
        self.transfer_color = QColor(230, 240, 250, 30)  # Very subtle blue

        # Add row color
        self.add_row_color = QColor(220, 230, 240, 40)  # Very subtle blue-gray for add row

    def paint(self, painter, option, index):
        # Get the parent widget (TransactionGrid)
        grid = self.parent()

        # Get the row
        row = index.row()

        # Check if this is the "+" row (add row)
        name_col = 1  # Assuming name is in column 1
        name_item = grid.item(row, name_col)
        is_add_row = (name_item and name_item.data(Qt.ItemDataRole.UserRole) == "add_row_marker")

        # Save the original state
        painter.save()

        # Check if this is an error row - PRIORITY OVER ALL OTHER STYLING
        if hasattr(grid, 'error_rows') and row in grid.error_rows:
            # Fill with error row color - soft red
            painter.fillRect(option.rect, self.error_row_color)

            # Check if this specific field is causing the error
            if hasattr(grid, 'error_fields') and (row, index.column()) in grid.error_fields:
                # Use a more intense red for the specific error field
                painter.fillRect(option.rect, self.error_field_color)

                # Draw a red border around the error field for extra emphasis
                pen = painter.pen()
                pen.setColor(QColor(220, 100, 100))  # Slightly darker red for border
                pen.setWidth(2)  # Thicker border for better visibility
                painter.setPen(pen)
                painter.drawRect(option.rect)

        # Check if this is the "+" row (add row)
        elif is_add_row:
            # Use a light blue-gray color for the add row
            painter.fillRect(option.rect, self.add_row_color)

        # Check if this is a new row
        elif hasattr(grid, 'new_rows') and row in grid.new_rows:
            # Fill with new row color - soft blue
            painter.fillRect(option.rect, self.new_row_color)

        # Check if this is a modified existing row
        elif hasattr(grid, 'modified_rows') and row in grid.modified_rows:
            # Fill with modified row color - soft yellow
            painter.fillRect(option.rect, self.modified_row_color)

        # Otherwise, only color the Type column based on transaction type
        elif index.column() == 4:  # Type column
            transaction_type = index.data(Qt.ItemDataRole.DisplayRole)

            if transaction_type == "Expense":
                painter.fillRect(option.rect, self.expense_color)
            elif transaction_type == "Income":
                painter.fillRect(option.rect, self.income_color)
            elif transaction_type:  # Any other non-empty type
                painter.fillRect(option.rect, self.transfer_color)

        # Restore the original state
        painter.restore()

        # Call the base class to draw the item content
        super().paint(painter, option, index)


class RowColorDelegate(BaseRowColorDelegate):
    """
    Delegate for coloring rows based on their state (new, error, etc.)
    This is a simple wrapper around BaseRowColorDelegate for backward compatibility.
    """
    pass


class ComboBoxDelegate(BaseRowColorDelegate):
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


class AccountDelegate(BaseRowColorDelegate):
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


class CategoryDelegate(BaseRowColorDelegate):
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


class SubCategoryDelegate(BaseRowColorDelegate):
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


class DateDelegate(BaseRowColorDelegate):
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


class CurrencyDelegate(BaseRowColorDelegate):
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


class TransactionTypeDelegate(BaseRowColorDelegate):
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
