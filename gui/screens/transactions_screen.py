from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QDateEdit, QGroupBox, QSplitter, QFrame,
    QMessageBox
)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QAction

from gui.widgets.transaction_grid import TransactionGrid
from gui.widgets.transaction_form import TransactionForm
from models.account import Account
from models.category import Category, SubCategory
from models.transaction import Transaction
from data.repositories.transaction_repository import TransactionRepository


class TransactionsScreen(QWidget):
    """
    Screen for displaying and managing transactions.
    """
    def __init__(self):
        super().__init__()

        # Create main layout
        self.layout = QVBoxLayout(self)
        
        # Create transaction form - we'll make this collapsible
        self.form_frame = QFrame()
        self.form_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.form_layout = QVBoxLayout(self.form_frame)
        
        self.transaction_form = TransactionForm()
        self.transaction_form.transaction_added.connect(self.on_transaction_added)
        self.form_layout.addWidget(self.transaction_form)
        
        # Add toggle button for the form
        self.toggle_form_button = QPushButton("Hide Form")
        self.toggle_form_button.setCheckable(True)
        self.toggle_form_button.clicked.connect(self.toggle_form)
        
        # Add buttons and grid to layout
        self.layout.addWidget(self.toggle_form_button)
        self.layout.addWidget(self.form_frame)

        # Create action buttons
        self.create_action_buttons()
        
        # Add status label for notifications
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: white; background-color: rgba(41, 128, 185, 0.7); padding: 5px; border-radius: 3px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setVisible(False)
        self.layout.addWidget(self.status_label)

        # Create transaction grid
        self.transaction_grid = TransactionGrid()
        self.transaction_grid.transaction_selected.connect(self.on_transaction_selected)
        self.transaction_grid.transaction_edited.connect(self.on_transaction_edited)
        self.transaction_grid.validation_failed.connect(self.on_validation_failed)
        self.layout.addWidget(self.transaction_grid, 1)  # Give the grid a stretch factor to use available space

        # Track edit mode
        self.edit_mode = False

        # Add a cancel edit button to the form
        self.transaction_form.add_cancel_button(self.cancel_edit_mode)

        # Load initial data
        self.refresh()
        
        # Add some spacing and styling
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)

    def toggle_form(self):
        """Toggle the visibility of the transaction form"""
        if self.form_frame.isVisible():
            self.form_frame.hide()
            self.toggle_form_button.setText("Show Form")
        else:
            self.form_frame.show()
            self.toggle_form_button.setText("Hide Form")

    def create_action_buttons(self):
        """Create action buttons for the transactions screen."""
        button_layout = QHBoxLayout()

        # Edit button
        self.edit_button = QPushButton("Edit Transaction")
        self.edit_button.setObjectName("edit_button")
        self.edit_button.clicked.connect(self.edit_selected_transaction)
        button_layout.addWidget(self.edit_button)

        # Delete button
        self.delete_button = QPushButton("Delete")
        self.delete_button.setObjectName("delete_button")
        self.delete_button.clicked.connect(self.delete_selected_transaction)
        button_layout.addWidget(self.delete_button)

        # Clear button
        self.clear_button = QPushButton("Clear New Rows")
        self.clear_button.setObjectName("clear_button")
        self.clear_button.clicked.connect(self.clear_new_rows)
        button_layout.addWidget(self.clear_button)

        # Spacer
        button_layout.addStretch()

        # Discard changes button
        self.discard_button = QPushButton("Discard Changes")
        self.discard_button.setObjectName("discard_button")
        self.discard_button.clicked.connect(self.discard_changes)
        button_layout.addWidget(self.discard_button)

        # Save changes button
        self.save_button = QPushButton("Save Changes")
        self.save_button.setObjectName("save_button")
        self.save_button.setStyleSheet("background-color: #3498db; color: white;")
        self.save_button.clicked.connect(self.save_changes)
        button_layout.addWidget(self.save_button)

        self.layout.addLayout(button_layout)

    def show_notification(self, message, color="#3498db", duration=3000):
        """Show a temporary notification to the user
        
        Args:
            message (str): Message to display
            color (str): Background color in hex format
            duration (int): How long to show the message in milliseconds
        """
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: white; background-color: {color}; padding: 5px; border-radius: 3px;")
        self.status_label.setVisible(True)
        
        # Hide the notification after a delay
        QTimer.singleShot(duration, lambda: self.status_label.setVisible(False))

    def on_validation_failed(self, errors):
        """Handle validation failures when saving
        
        Args:
            errors (list): List of tuples (row, error_message)
        """
        if not errors:
            return
            
        # Show a notification with the number of errors
        error_message = f"Could not save {len(errors)} transaction(s) due to missing required fields."
        self.show_notification(
            error_message,
            color="#e74c3c"  # Red color for error
        )
        
        # Always show a message box with details about the missing fields
        detailed_message = ""
        
        # Group errors by type for clearer messaging
        missing_name = []
        missing_account = []
        missing_type = []
        missing_date = []
        
        for row, message in errors:
            if "Name" in message:
                missing_name.append(row+1)  # +1 for human-readable row number
            elif "Account" in message:
                missing_account.append(row+1)
            elif "Type" in message:
                missing_type.append(row+1)
            elif "Date" in message:
                missing_date.append(row+1)
        
        # Build the detailed message
        if missing_name:
            detailed_message += f"Missing Name: Rows {', '.join(map(str, missing_name))}\n"
        if missing_account:
            detailed_message += f"Missing Account: Rows {', '.join(map(str, missing_account))}\n"
        if missing_type:
            detailed_message += f"Missing Type: Rows {', '.join(map(str, missing_type))}\n"
        if missing_date:
            detailed_message += f"Missing Date: Rows {', '.join(map(str, missing_date))}\n"
        
        # Show the detailed message box
        QMessageBox.warning(
            self,
            "Validation Errors",
            f"{error_message}\n\n{detailed_message}\n\nRows with errors are highlighted in red. Please fix the missing fields and try again."
        )
        
        # Focus on the first row with an error
        if errors:
            self.transaction_grid.selectRow(errors[0][0])

    def refresh(self):
        """Refresh the transactions data."""
        # Load transactions with details
        transactions = TransactionRepository.get_transactions_with_details()
        self.transaction_grid.load_transactions(transactions)

        # Update form dropdowns
        self.transaction_form.refresh_dropdowns()

    def add_new_transaction(self):
        """Add a new transaction row to the grid."""
        self.transaction_grid.add_empty_row()

    def edit_selected_transaction(self):
        """Edit the selected transaction."""
        selected_transaction = self.transaction_grid.get_selected_transaction()
        if selected_transaction:
            self.edit_mode = True
            self.transaction_form.load_transaction(selected_transaction)
            self.transaction_form.setTitle("Edit Transaction")
            
            # Make sure the form is visible
            if not self.form_frame.isVisible():
                self.toggle_form()

    def cancel_edit_mode(self):
        """Cancel edit mode and return to add mode."""
        self.edit_mode = False
        self.transaction_form.clear_form()
        self.transaction_form.setTitle("Add Transaction")

    def delete_selected_transaction(self):
        """Delete the selected transaction."""
        self.transaction_grid.delete_selected_transaction()
        self.show_notification("Transaction(s) deleted")

    def clear_new_rows(self):
        """Clear all new (unsaved) rows from the grid."""
        self.transaction_grid.clear_new_rows()
        self.show_notification("New rows cleared")

    def discard_changes(self):
        """Discard all changes and reload data."""
        self.refresh()
        self.show_notification("All changes discarded")

    def save_changes(self):
        """Save all changes to the database."""
        result = self.transaction_grid.save_all_changes()
        
        if result:
            # Show a success notification
            self.show_notification("All changes saved successfully", color="#27ae60")
            
            # Show a brief highlight on the save button to indicate success
            original_style = self.save_button.styleSheet()
            self.save_button.setStyleSheet("background-color: #27ae60; color: white;")
            
            # Use a timer to reset the style after a short delay
            QTimer.singleShot(1000, lambda: self.save_button.setStyleSheet(original_style))

    def on_transaction_added(self, transaction):
        """Handle when a transaction is added via the form."""
        self.refresh()
        self.show_notification("Transaction added successfully", color="#27ae60")

    def on_transaction_selected(self, transaction):
        """Handle when a transaction is selected in the grid."""
        # Only load the transaction into the form if we're in edit mode
        # This prevents the form from changing when just selecting rows in the grid
        if self.edit_mode:
            self.transaction_form.load_transaction(transaction)

    def on_transaction_edited(self, transaction):
        """Handle when a transaction is edited in the grid."""
        # This is handled by the grid itself
        pass

    def undo(self):
        """Undo the last action."""
        self.transaction_grid.undo()
        self.show_notification("Undo completed")

    def redo(self):
        """Redo the last undone action."""
        self.transaction_grid.redo()
        self.show_notification("Redo completed")
