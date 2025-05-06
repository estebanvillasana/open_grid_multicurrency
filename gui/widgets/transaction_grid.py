from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QComboBox, QDateEdit, QLineEdit, QStyledItemDelegate, QMessageBox,
    QApplication
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QObject, QMimeData, QTimer
from PyQt6.QtGui import QColor, QBrush, QKeySequence, QFont
import csv
import io



from models.transaction import Transaction
from models.account import Account
from models.category import Category, SubCategory
from data.repositories.transaction_repository import TransactionRepository
from gui.widgets.custom_delegates import (
    AccountDelegate, CategoryDelegate, SubCategoryDelegate,
    DateDelegate, CurrencyDelegate, TransactionTypeDelegate,
    RowColorDelegate
)


class TransactionGrid(QTableWidget):
    """
    Grid widget for displaying and editing transactions in a spreadsheet-like interface.
    """
    # Signals
    transaction_selected = pyqtSignal(object)
    transaction_edited = pyqtSignal(object)
    validation_failed = pyqtSignal(list)  # Signal to emit validation errors

    # Column indices
    COL_ID = 0
    COL_NAME = 1
    COL_DESCRIPTION = 2
    COL_ACCOUNT = 3
    COL_TYPE = 4
    COL_VALUE = 5
    COL_CATEGORY = 6
    COL_SUBCATEGORY = 7
    COL_DATE = 8

    # Colors - Updated for a more elegant look with less saturation
    ADD_ROW_COLOR = QColor(220, 230, 240, 40)  # Very subtle blue-gray for add row
    NEW_ROW_COLOR = QColor(213, 232, 250, 100)  # Soft blue for new rows
    MODIFIED_ROW_COLOR = QColor(255, 248, 214, 100)  # Soft yellow for modified existing rows
    ERROR_ROW_COLOR = QColor(250, 220, 220, 180)  # Soft red for error rows
    ERROR_FIELD_COLOR = QColor(255, 200, 200, 220)  # Slightly more intense red for error fields
    INCOME_COLOR = QColor(230, 245, 230, 30)  # Very subtle green
    EXPENSE_COLOR = QColor(245, 230, 230, 30)  # Very subtle red
    TRANSFER_COLOR = QColor(230, 240, 250, 30)  # Very subtle blue

    def __init__(self):
        super().__init__()

        # Configure table
        self.setColumnCount(9)
        self.setHorizontalHeaderLabels([
            "ID", "Transaction", "Description", "Account", "Type",
            "Value", "Category", "Sub Category", "Date"
        ])

        # Set column widths
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        self.setColumnWidth(self.COL_ID, 50)
        self.setColumnWidth(self.COL_NAME, 150)
        self.setColumnWidth(self.COL_DESCRIPTION, 200)
        self.setColumnWidth(self.COL_ACCOUNT, 120)
        self.setColumnWidth(self.COL_TYPE, 80)
        self.setColumnWidth(self.COL_VALUE, 100)
        self.setColumnWidth(self.COL_CATEGORY, 150)
        self.setColumnWidth(self.COL_SUBCATEGORY, 150)
        self.setColumnWidth(self.COL_DATE, 100)

        # Set row height to improve color visibility
        self.verticalHeader().setDefaultSectionSize(30)

        # Configure selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)  # Allow multi-select

        # Hide ID column
        self.setColumnHidden(self.COL_ID, True)

        # Enable editing
        self.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked |
                            QAbstractItemView.EditTrigger.EditKeyPressed)

        # Enable clipboard support
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)

        # Connect signals
        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.itemChanged.connect(self.on_item_changed)

        # Set up custom delegates for editing
        self.setup_delegates()

        # Track changes for undo/redo
        self.undo_stack = []
        self.redo_stack = []
        self.changes = {}  # Dictionary to track changes: {row_id: Transaction}
        self.new_rows = []  # List to track new rows that haven't been saved yet
        self.modified_rows = []  # List to track existing rows that have been modified
        self.error_rows = []  # List to track rows with validation errors
        self.error_fields = set()  # Set to track specific fields causing errors: {(row, col)}

    def setup_delegates(self):
        """Set up custom delegates for editing different column types."""
        # Row color delegate for all columns
        self.row_color_delegate = RowColorDelegate(self)
        self.setItemDelegate(self.row_color_delegate)

        # Account delegate
        self.setItemDelegateForColumn(self.COL_ACCOUNT, AccountDelegate(self))

        # Transaction type delegate
        self.setItemDelegateForColumn(self.COL_TYPE, TransactionTypeDelegate(self))

        # Value delegate
        self.setItemDelegateForColumn(self.COL_VALUE, CurrencyDelegate(self))

        # Category delegate
        self.setItemDelegateForColumn(self.COL_CATEGORY, CategoryDelegate(self))

        # Subcategory delegate
        self.setItemDelegateForColumn(self.COL_SUBCATEGORY, SubCategoryDelegate(self))

        # Date delegate
        self.setItemDelegateForColumn(self.COL_DATE, DateDelegate(self))

    def load_transactions(self, transactions):
        """Load transactions into the grid."""
        # Disconnect signals temporarily to prevent triggering events during loading
        self.itemChanged.disconnect(self.on_item_changed)

        # Store any unsaved new rows
        unsaved_transactions = []
        for row in self.new_rows:
            if row < self.rowCount():
                transaction = self.get_transaction_from_row(row)
                # Only keep rows that have actual data (not just the "+" marker)
                name_item = self.item(row, self.COL_NAME)
                is_add_row = (name_item and name_item.data(Qt.ItemDataRole.UserRole) == "add_row_marker")

                if transaction and not is_add_row and transaction.name and transaction.name != "+":
                    unsaved_transactions.append(transaction)

        # Clear existing data
        self.setRowCount(0)
        self.changes.clear()
        self.new_rows.clear()
        self.modified_rows.clear()
        self.error_rows.clear()
        self.error_fields.clear()

        # Add existing transactions to the grid
        for i, transaction in enumerate(transactions):
            self.insertRow(i)
            self.populate_row(i, transaction)

        # Add unsaved transactions back to the grid
        row = self.rowCount()
        for transaction in unsaved_transactions:
            self.insertRow(row)

            # Create ID item
            id_item = QTableWidgetItem("")
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            id_item.setData(Qt.ItemDataRole.UserRole, transaction)
            self.setItem(row, self.COL_ID, id_item)

            # Add other fields
            self.setItem(row, self.COL_NAME, QTableWidgetItem(transaction.name))
            self.setItem(row, self.COL_DESCRIPTION, QTableWidgetItem(transaction.description or ""))

            # Account
            account_item = QTableWidgetItem("")
            if transaction.account_id:
                # Try to get account name
                account = Account.get_by_id(transaction.account_id)
                if account:
                    account_item = QTableWidgetItem(account.name)
            account_item.setData(Qt.ItemDataRole.UserRole, transaction.account_id)
            self.setItem(row, self.COL_ACCOUNT, account_item)

            # Type
            self.setItem(row, self.COL_TYPE, QTableWidgetItem(transaction.transaction_type or ""))

            # Value
            self.setItem(row, self.COL_VALUE, QTableWidgetItem(str(transaction.value or "")))

            # Category
            category_item = QTableWidgetItem("")
            if transaction.category_id:
                # Try to get category name
                category = Category.get_by_id(transaction.category_id)
                if category:
                    category_item = QTableWidgetItem(category.name)
            category_item.setData(Qt.ItemDataRole.UserRole, transaction.category_id)
            self.setItem(row, self.COL_CATEGORY, category_item)

            # Subcategory
            subcategory_item = QTableWidgetItem("")
            if transaction.sub_category_id:
                # Try to get subcategory name
                subcategory = SubCategory.get_by_id(transaction.sub_category_id)
                if subcategory:
                    subcategory_item = QTableWidgetItem(subcategory.name)
            subcategory_item.setData(Qt.ItemDataRole.UserRole, transaction.sub_category_id)
            self.setItem(row, self.COL_SUBCATEGORY, subcategory_item)

            # Date
            self.setItem(row, self.COL_DATE, QTableWidgetItem(transaction.date or ""))

            # Add to new rows list
            self.new_rows.append(row)

            # Highlight as a new row
            self.highlight_new_row(row)

            # Schedule another highlight after a short delay to ensure it's applied
            QTimer.singleShot(100, lambda r=row: self.highlight_new_row(r))

            row += 1

        # Add an empty row at the end for direct data entry
        self.add_empty_row()

        # Reconnect signals
        self.itemChanged.connect(self.on_item_changed)

    def populate_row(self, row, transaction):
        """Populate a row with transaction data."""
        # ID column
        id_item = QTableWidgetItem(str(transaction.id))
        id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make ID non-editable
        id_item.setData(Qt.ItemDataRole.UserRole, transaction)  # Store transaction object
        self.setItem(row, self.COL_ID, id_item)

        # Name column
        name_item = QTableWidgetItem(transaction.name)
        self.setItem(row, self.COL_NAME, name_item)

        # Description column
        desc_item = QTableWidgetItem(transaction.description)
        self.setItem(row, self.COL_DESCRIPTION, desc_item)

        # Account column
        account_item = QTableWidgetItem(getattr(transaction, 'account_name', ''))
        account_item.setData(Qt.ItemDataRole.UserRole, transaction.account_id)
        self.setItem(row, self.COL_ACCOUNT, account_item)

        # Type column
        type_item = QTableWidgetItem(transaction.transaction_type)
        self.setItem(row, self.COL_TYPE, type_item)

        # Value column
        value_item = QTableWidgetItem(str(transaction.value))
        self.setItem(row, self.COL_VALUE, value_item)

        # Category column
        category_item = QTableWidgetItem(getattr(transaction, 'category_name', ''))
        category_item.setData(Qt.ItemDataRole.UserRole, transaction.category_id)
        self.setItem(row, self.COL_CATEGORY, category_item)

        # Subcategory column
        subcategory_item = QTableWidgetItem(getattr(transaction, 'sub_category_name', ''))
        subcategory_item.setData(Qt.ItemDataRole.UserRole, transaction.sub_category_id)
        self.setItem(row, self.COL_SUBCATEGORY, subcategory_item)

        # Date column
        date_item = QTableWidgetItem(transaction.date)
        self.setItem(row, self.COL_DATE, date_item)

        # Color the row based on transaction type
        self.color_row(row, transaction.transaction_type)

    def color_row(self, row, transaction_type):
        """Color a row based on transaction type."""
        # With our delegate, we don't need to manually color rows
        # The delegate will handle coloring based on row state
        # Just update the specific row to trigger the delegate's paint method
        for col in range(self.columnCount()):
            index = self.model().index(row, col)
            if index.isValid():
                self.update(index)

    def add_empty_row(self):
        """Add an empty row for a new transaction."""
        row = self.rowCount()
        self.insertRow(row)

        # Create a new transaction object with minimal defaults
        transaction = Transaction()
        transaction.name = ""  # Empty name
        transaction.description = ""
        transaction.account_id = None
        transaction.transaction_type = ""
        transaction.category_id = None
        transaction.sub_category_id = None
        transaction.date = ""
        transaction.value = 0.0

        # ID column
        id_item = QTableWidgetItem("")
        id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Make ID non-editable
        id_item.setData(Qt.ItemDataRole.UserRole, transaction)  # Store transaction object
        self.setItem(row, self.COL_ID, id_item)

        # Name column with "+" indicator
        name_item = QTableWidgetItem("+")
        name_item.setData(Qt.ItemDataRole.UserRole, "add_row_marker")  # Mark this as the add row
        # Make the "+" more noticeable
        font = QFont()
        font.setBold(True)
        font.setPointSize(10)
        name_item.setFont(font)
        self.setItem(row, self.COL_NAME, name_item)

        # Empty cells for other columns
        for col in range(2, self.columnCount()):
            self.setItem(row, col, QTableWidgetItem(""))

        # Apply special styling to the add row
        self.highlight_add_row(row)

        # Select the new row
        self.selectRow(row)

    def highlight_add_row(self, row):
        """Apply special styling to the add row (+ row)."""
        # The delegate will handle the coloring
        # Just make sure the row is updated
        for col in range(self.columnCount()):
            index = self.model().index(row, col)
            if index.isValid():
                self.update(index)

    def highlight_new_row(self, row):
        """Apply special styling to new rows that haven't been saved yet."""
        # Add to new rows list if not already there
        if row not in self.new_rows:
            self.new_rows.append(row)

        # Make first cell show "NEW" if it's not already
        name_item = self.item(row, self.COL_NAME)
        if name_item and not name_item.text().startswith("NEW: ") and name_item.text() != "+":
            self.blockSignals(True)
            name_item.setText("NEW: " + name_item.text())
            self.blockSignals(False)

        # Force update each cell in the row to apply the delegate's coloring
        for col in range(self.columnCount()):
            index = self.model().index(row, col)
            if index.isValid():
                self.update(index)

        # Also force a full repaint to ensure all cells are updated
        self.repaint()

        # Schedule additional updates to ensure the highlighting persists
        # This helps with rendering issues where the highlight might not be applied consistently
        QTimer.singleShot(100, lambda r=row: self.refresh_row_styling(r))
        QTimer.singleShot(500, lambda r=row: self.refresh_row_styling(r))

    def highlight_modified_row(self, row):
        """Apply special styling to existing rows that have been modified."""
        # Add to modified rows list if not already there
        if row not in self.modified_rows:
            self.modified_rows.append(row)

        # Remove from other styling lists to avoid conflicts
        if row in self.new_rows:
            self.new_rows.remove(row)

        # Make first cell show "MODIFIED" if it's not already
        name_item = self.item(row, self.COL_NAME)
        if name_item and not name_item.text().startswith("MODIFIED: ") and not name_item.text().startswith("NEW: "):
            original_text = name_item.text()
            self.blockSignals(True)
            name_item.setText("MODIFIED: " + original_text)
            self.blockSignals(False)

        # Force update each cell in the row to apply the delegate's coloring
        for col in range(self.columnCount()):
            index = self.model().index(row, col)
            if index.isValid():
                self.update(index)

        # Also force a full repaint to ensure all cells are updated
        self.repaint()

        # Schedule additional updates to ensure the highlighting persists
        QTimer.singleShot(100, lambda r=row: self.refresh_row_styling(r))
        QTimer.singleShot(500, lambda r=row: self.refresh_row_styling(r))

    def highlight_error_row(self, row, error_message=None):
        """Apply error styling to rows that failed validation."""
        # Add to error rows list if not already there
        if row not in self.error_rows:
            self.error_rows.append(row)

        # Remove from new_rows list if it's there to avoid styling conflicts
        if row in self.new_rows:
            self.new_rows.remove(row)

        # Remove from modified_rows list if it's there to avoid styling conflicts
        if row in self.modified_rows:
            self.modified_rows.remove(row)

        # Identify which fields are causing the error
        if error_message:
            # Clear previous error fields for this row
            self.error_fields = {(r, c) for r, c in self.error_fields if r != row}

            # Add specific error fields based on the error message
            if "Name is required" in error_message:
                self.error_fields.add((row, self.COL_NAME))
            if "Account is required" in error_message:
                self.error_fields.add((row, self.COL_ACCOUNT))
            if "Type is required" in error_message:
                self.error_fields.add((row, self.COL_TYPE))
            if "Date is required" in error_message:
                self.error_fields.add((row, self.COL_DATE))

        # Create a very visible error style
        error_bg = QBrush(self.ERROR_ROW_COLOR)  # Use the class constant for consistency
        error_fg = QBrush(QColor(50, 50, 50))   # Dark text for better readability on light red

        # Apply direct styling to all cells in the row
        self.blockSignals(True)
        for col in range(self.columnCount()):
            item = self.item(row, col)
            if item:
                # Set tooltip
                item.setToolTip(error_message if error_message else "Validation error")

                # Apply direct styling
                item.setBackground(error_bg)
                item.setForeground(error_fg)

                # If this is a specific error field, make it more visible
                if (row, col) in self.error_fields:
                    error_field_bg = QBrush(self.ERROR_FIELD_COLOR)
                    item.setBackground(error_field_bg)

                    # Make text bold for extra emphasis on error fields
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
        self.blockSignals(False)

        # Force update each cell in the row to apply the styling
        for col in range(self.columnCount()):
            index = self.model().index(row, col)
            if index.isValid():
                self.update(index)

        # Also force a full repaint to ensure all cells are updated
        self.repaint()

        # Schedule multiple updates to ensure styling persists
        QTimer.singleShot(100, lambda r=row: self.update_error_row_styling(r))
        QTimer.singleShot(500, lambda r=row: self.update_error_row_styling(r))
        QTimer.singleShot(1000, lambda r=row: self.update_error_row_styling(r))
        QTimer.singleShot(2000, lambda r=row: self.update_error_row_styling(r))
        QTimer.singleShot(3000, lambda r=row: self.update_error_row_styling(r))

    def refresh_row_styling(self, row):
        """Refresh the styling for a row after a delay.
        This helps ensure the styling is applied consistently."""
        if row < self.rowCount():
            # Force update each cell in the row
            for col in range(self.columnCount()):
                index = self.model().index(row, col)
                if index.isValid():
                    self.update(index)

            # Force a repaint
            self.repaint()

    def update_error_row_styling(self, row):
        """Update the styling for an error row after a delay.
        This helps ensure the error styling is applied even if other events interfere."""
        if row in self.error_rows and row < self.rowCount():
            # Create a very visible error style
            error_bg = QBrush(self.ERROR_ROW_COLOR)  # Use the class constant for consistency
            error_fg = QBrush(QColor(50, 50, 50))   # Dark text for better readability on light red

            # Re-apply direct styling to all cells in the row
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item:
                    # Apply direct styling
                    item.setBackground(error_bg)
                    item.setForeground(error_fg)

                    # If this is a specific error field, make it more visible
                    if (row, col) in self.error_fields:
                        error_field_bg = QBrush(self.ERROR_FIELD_COLOR)
                        item.setBackground(error_field_bg)

                        # Make text bold for extra emphasis on error fields
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)

            # Force update the row
            for col in range(self.columnCount()):
                index = self.model().index(row, col)
                if index.isValid():
                    self.update(index)

            # Force a repaint
            self.repaint()

    def get_selected_transaction(self):
        """Get the currently selected transaction."""
        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return None

        row = selected_rows[0].row()
        id_item = self.item(row, self.COL_ID)

        if id_item:
            return id_item.data(Qt.ItemDataRole.UserRole)

        return None

    def delete_selected_transaction(self):
        """Delete the selected transactions."""
        from PyQt6.QtWidgets import QMessageBox

        selected_rows = self.selectionModel().selectedRows()
        if not selected_rows:
            return

        # Sort rows in descending order to avoid index shifting when removing rows
        rows = sorted([index.row() for index in selected_rows], reverse=True)

        # Confirm deletion if there are multiple rows or if it's an existing transaction
        if len(rows) > 1 or (len(rows) == 1 and self.item(rows[0], self.COL_ID) and
                             self.item(rows[0], self.COL_ID).data(Qt.ItemDataRole.UserRole) and
                             self.item(rows[0], self.COL_ID).data(Qt.ItemDataRole.UserRole).id):
            confirm = QMessageBox.question(
                self,
                "Confirm Deletion",
                f"Are you sure you want to delete {len(rows)} transaction(s)?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if confirm != QMessageBox.StandardButton.Yes:
                return

        # Delete each selected row
        for row in rows:
            id_item = self.item(row, self.COL_ID)

            if id_item:
                transaction = id_item.data(Qt.ItemDataRole.UserRole)

                # Check if this is a new row
                if row in self.new_rows:
                    self.new_rows.remove(row)
                else:
                    # Add to undo stack
                    self.undo_stack.append(('delete', transaction))

                    # Delete from database
                    if transaction.id:
                        transaction.delete()

                # Remove from grid
                self.removeRow(row)

        # Make sure we always have an empty row at the end
        if self.rowCount() == 0 or not self.new_rows:
            self.add_empty_row()

    def clear_new_rows(self):
        """Clear all new (unsaved) rows."""
        # Remove rows in reverse order to avoid index issues
        for row in sorted(self.new_rows, reverse=True):
            if row < self.rowCount():
                self.removeRow(row)

        self.new_rows.clear()

    def save_all_changes(self):
        """Save all changes to the database."""
        # We'll clear error rows only after successful validation

        validation_errors = []
        # Save changes to existing transactions
        for transaction in self.changes.values():
            validation_result = self.validate_transaction(transaction)
            if validation_result[0]:
                transaction.save()
            else:
                # Find the row for this transaction
                for row in range(self.rowCount()):
                    id_item = self.item(row, self.COL_ID)
                    if (id_item and id_item.data(Qt.ItemDataRole.UserRole) and
                        id_item.data(Qt.ItemDataRole.UserRole).id == transaction.id):
                        self.highlight_error_row(row, validation_result[1])
                        validation_errors.append((row, validation_result[1]))
                        break

        # Save new rows
        saved_rows = []
        for row in self.new_rows:
            if row < self.rowCount():
                # Skip the "+" row
                name_item = self.item(row, self.COL_NAME)
                is_add_row = (name_item and name_item.data(Qt.ItemDataRole.UserRole) == "add_row_marker")

                if not is_add_row:
                    transaction = self.get_transaction_from_row(row)

                    # Remove "NEW: " prefix before saving
                    if transaction.name and transaction.name.startswith("NEW: "):
                        transaction.name = transaction.name[5:]  # Remove the "NEW: " prefix
                        name_item = self.item(row, self.COL_NAME)
                        if name_item:
                            name_item.setText(transaction.name)

                    # Validate transaction
                    validation_result = self.validate_transaction(transaction)
                    if validation_result[0]:
                        # Save to database
                        transaction.save()
                        saved_rows.append(row)
                    else:
                        # Highlight as error
                        self.highlight_error_row(row, validation_result[1])
                        validation_errors.append((row, validation_result[1]))

        # Update the new_rows list to remove saved rows
        self.new_rows = [row for row in self.new_rows if row not in saved_rows]

        # Clear changes dictionary
        self.changes.clear()

        # If there are validation errors, apply direct styling and emit signal
        if validation_errors:
            # Apply direct styling to all rows with validation errors
            for row, error_msg in validation_errors:
                if row < self.rowCount():
                    # Use our highlight_error_row method to ensure consistent styling
                    self.highlight_error_row(row, error_msg)

                    # Schedule additional updates to ensure styling persists
                    QTimer.singleShot(100, lambda r=row: self.update_error_row_styling(r))
                    QTimer.singleShot(500, lambda r=row: self.update_error_row_styling(r))

            # Force update visually
            self.update()
            self.repaint()

            # Emit validation errors
            self.validation_failed.emit(validation_errors)
            return False  # Return False to indicate not all rows were saved

        # All validation passed - now we can clear all styling
        self.error_rows.clear()
        self.error_fields.clear()
        self.modified_rows.clear()

        # Refresh the grid
        from data.repositories.transaction_repository import TransactionRepository
        self.load_transactions(TransactionRepository.get_transactions_with_details())

        return True  # Return True to indicate all rows were saved successfully

    def validate_transaction(self, transaction):
        """Validate that a transaction has all required fields.

        Returns:
            tuple: (is_valid, error_message)
        """
        # Check for required fields
        if not transaction.name or not transaction.name.strip():
            return (False, "Name is required")

        if not transaction.account_id:
            return (False, "Account is required")

        if not transaction.transaction_type:
            return (False, "Type is required")

        if not transaction.date:
            return (False, "Date is required")

        # All required fields are present
        return (True, "")

    def get_transaction_from_row(self, row):
        """Extract transaction data from a row."""
        if row >= self.rowCount():
            return None

        # Get existing transaction or create new one
        id_item = self.item(row, self.COL_ID)
        transaction = id_item.data(Qt.ItemDataRole.UserRole) if id_item else Transaction()

        # Update transaction with current row data
        name_item = self.item(row, self.COL_NAME)
        if name_item:
            transaction.name = name_item.text()

        desc_item = self.item(row, self.COL_DESCRIPTION)
        if desc_item:
            transaction.description = desc_item.text()

        account_item = self.item(row, self.COL_ACCOUNT)
        if account_item:
            transaction.account_id = account_item.data(Qt.ItemDataRole.UserRole)

        type_item = self.item(row, self.COL_TYPE)
        if type_item:
            transaction.transaction_type = type_item.text()

        value_item = self.item(row, self.COL_VALUE)
        if value_item:
            try:
                transaction.value = float(value_item.text())
            except ValueError:
                transaction.value = 0.0

        category_item = self.item(row, self.COL_CATEGORY)
        if category_item:
            transaction.category_id = category_item.data(Qt.ItemDataRole.UserRole)

        subcategory_item = self.item(row, self.COL_SUBCATEGORY)
        if subcategory_item:
            transaction.sub_category_id = subcategory_item.data(Qt.ItemDataRole.UserRole)

        date_item = self.item(row, self.COL_DATE)
        if date_item:
            transaction.date = date_item.text()

        return transaction

    def on_selection_changed(self):
        """Handle selection changes in the grid."""
        transaction = self.get_selected_transaction()
        if transaction:
            self.transaction_selected.emit(transaction)

    def on_item_changed(self, item):
        """Handle when an item is edited in the grid."""
        row = item.row()
        col = item.column()

        # Get the transaction for this row
        transaction = self.get_transaction_from_row(row)

        # Check if this is the "+" row (last row)
        name_item = self.item(row, self.COL_NAME)
        is_add_row = (name_item and name_item.data(Qt.ItemDataRole.UserRole) == "add_row_marker")

        # If this is the "+" row and user started typing
        if is_add_row and item.text().strip() and item.text() != "+":
            # This is now a data entry row

            # Remove the "add_row_marker" flag
            name_item.setData(Qt.ItemDataRole.UserRole, None)

            # If editing the name column, update it with the entered text
            if col == self.COL_NAME and item.text() == "+":
                # Clear the + sign but keep focus on this cell
                item.setText("")

            # Mark this as a new row (not the add row anymore)
            if row not in self.new_rows:
                self.new_rows.append(row)

            # Apply the highlight to show this is a new, unsaved row
            self.highlight_new_row(row)

            # Force update to ensure the highlighting is visible
            self.update()
            self.repaint()

            # Explicitly set the background color again after a short delay
            # This helps ensure the color is applied even if other events interfere
            QTimer.singleShot(100, lambda: self.highlight_new_row(row))

            # Make sure we have a new "+" row at the end
            # Check if we already have an add row marker
            has_add_row = False
            for r in range(self.rowCount()):
                item = self.item(r, self.COL_NAME)
                if item and item.data(Qt.ItemDataRole.UserRole) == "add_row_marker":
                    has_add_row = True
                    break

            if not has_add_row:
                self.add_empty_row()

        # If this is already a new row (but not the "+" row)
        elif row in self.new_rows and not is_add_row:
            # Apply the highlight to show this is a new, unsaved row
            self.highlight_new_row(row)

            # Force update to ensure the highlighting is visible
            self.update()
            self.repaint()

            # Explicitly set the background color again after a short delay
            # This helps ensure the color is applied even if other events interfere
            QTimer.singleShot(100, lambda: self.highlight_new_row(row))

            # We'll keep error styling until validation passes
            # Error styling will be cleared when save_all_changes is called

        # Otherwise, if it's an existing transaction, add to changes dictionary
        elif transaction and transaction.id:
            self.changes[transaction.id] = transaction

            # Add to modified rows list if not already there
            if row not in self.modified_rows and row not in self.error_rows:
                self.modified_rows.append(row)

            # Apply the highlight to show this is a modified row
            self.highlight_modified_row(row)

            # Update the row color based on transaction type
            type_item = self.item(row, self.COL_TYPE)
            if type_item and type_item.text():
                self.color_row(row, type_item.text())

            # We'll keep error styling until validation passes
            # Error styling will be cleared when save_all_changes is called

        # Emit signal
        self.transaction_edited.emit(transaction)

    def undo(self):
        """Undo the last action."""
        if not self.undo_stack:
            return

        action = self.undo_stack.pop()
        self.redo_stack.append(action)

        action_type, data = action

        if action_type == 'delete':
            # Restore deleted transaction
            transaction = data
            transaction.save()

            # Refresh the grid
            self.load_transactions(TransactionRepository.get_transactions_with_details())

    def redo(self):
        """Redo the last undone action."""
        if not self.redo_stack:
            return

        action = self.redo_stack.pop()
        self.undo_stack.append(action)

        action_type, data = action

        if action_type == 'delete':
            # Delete the transaction again
            transaction = data
            transaction.delete()

            # Refresh the grid
            self.load_transactions(TransactionRepository.get_transactions_with_details())

    def keyPressEvent(self, event):
        """Handle key press events for copy-paste functionality."""
        # Handle Ctrl+C (Copy)
        if event.key() == Qt.Key.Key_C and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.copy_selection_to_clipboard()
        # Handle Ctrl+V (Paste)
        elif event.key() == Qt.Key.Key_V and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.paste_from_clipboard()
        else:
            # Pass other key events to the parent class
            super().keyPressEvent(event)

    def copy_selection_to_clipboard(self):
        """Copy selected cells to clipboard in a format that can be pasted into Excel."""
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return

        clipboard_text = io.StringIO()
        csv_writer = csv.writer(clipboard_text, delimiter='\t', lineterminator='\n')

        # Get all selected rows
        selected_rows = sorted(set(index.row() for index in self.selectedIndexes()))

        for row in selected_rows:
            row_data = []
            for col in range(1, self.columnCount()):  # Skip ID column
                if not self.isColumnHidden(col):
                    item = self.item(row, col)
                    if item:
                        row_data.append(item.text())
                    else:
                        row_data.append("")
            csv_writer.writerow(row_data)

        # Get the application clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(clipboard_text.getvalue())

    def paste_from_clipboard(self):
        """Paste data from clipboard into the grid."""
        clipboard = QApplication.clipboard()
        text = clipboard.text()

        if not text:
            return

        # Parse the clipboard text
        rows = []
        for line in text.split('\n'):
            if line.strip():
                rows.append(line.split('\t'))

        if not rows:
            return

        # Get the starting cell for paste
        current_row = self.currentRow()
        if current_row < 0:
            current_row = self.rowCount() - 1  # Default to last row

        # Ask for confirmation if pasting multiple rows
        if len(rows) > 1:
            confirm = QMessageBox.question(
                self,
                "Confirm Paste",
                f"Are you sure you want to paste {len(rows)} rows of data?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if confirm != QMessageBox.StandardButton.Yes:
                return

        # Disconnect signals temporarily to prevent triggering events during pasting
        self.itemChanged.disconnect(self.on_item_changed)

        # Paste the data
        for i, row_data in enumerate(rows):
            row_index = current_row + i

            # If we're at the last row and it's not empty, add a new row
            if row_index >= self.rowCount() - 1:
                self.add_empty_row()

            # Paste each cell
            for j, cell_data in enumerate(row_data):
                # Skip ID column and adjust column index
                col_index = j + 1  # +1 because we skip the ID column

                if col_index < self.columnCount() and not self.isColumnHidden(col_index):
                    item = self.item(row_index, col_index)
                    if item:
                        item.setText(cell_data)

        # Reconnect signals
        self.itemChanged.connect(self.on_item_changed)

        # Update all rows that were modified
        for i in range(len(rows)):
            row_index = current_row + i
            if row_index < self.rowCount():
                # Get the transaction for this row and update it
                transaction = self.get_transaction_from_row(row_index)

                # If this is a new row, highlight it
                if row_index in self.new_rows:
                    self.highlight_new_row(row_index)
                # Otherwise, update the row color based on transaction type
                elif transaction.transaction_type:
                    self.color_row(row_index, transaction.transaction_type)

                # Add to changes dictionary if it's an existing transaction
                if transaction.id and row_index not in self.new_rows:
                    self.changes[transaction.id] = transaction
