from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QPushButton, QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from datetime import datetime

from models.account import Account
from models.category import Category, SubCategory
from models.transaction import Transaction


class TransactionForm(QGroupBox):
    """
    Form for adding or editing transactions.
    """
    # Signal emitted when a transaction is added
    transaction_added = pyqtSignal(object)

    def __init__(self):
        super().__init__("Add Transaction")

        # Create form layout
        self.layout = QFormLayout(self)

        # Create form fields
        self.create_form_fields()

        # Create buttons
        self.create_buttons()

        # Load initial data
        self.refresh_dropdowns()

        # Current transaction being edited (None for new transactions)
        self.current_transaction = None

    def create_form_fields(self):
        """Create form fields for the transaction form."""
        # First row: Name and Value
        first_row = QHBoxLayout()

        # Name field
        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        first_row.addWidget(self.name_label)
        first_row.addWidget(self.name_input, 1)

        # Value field
        self.value_label = QLabel("Value:")
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("0.00")
        first_row.addWidget(self.value_label)
        first_row.addWidget(self.value_input, 1)

        self.layout.addRow(first_row)

        # Second row: Type and Account
        second_row = QHBoxLayout()

        # Type field
        self.type_label = QLabel("Type:")
        self.type_input = QComboBox()
        self.type_input.addItems(["Expense", "Income"])
        self.type_input.currentTextChanged.connect(self.on_type_changed)
        second_row.addWidget(self.type_label)
        second_row.addWidget(self.type_input, 1)

        # Account field
        self.account_label = QLabel("Account:")
        self.account_input = QComboBox()
        second_row.addWidget(self.account_label)
        second_row.addWidget(self.account_input, 1)

        self.layout.addRow(second_row)

        # Third row: Category and Subcategory
        third_row = QHBoxLayout()

        # Category field
        self.category_label = QLabel("Category:")
        self.category_input = QComboBox()
        self.category_input.currentIndexChanged.connect(self.on_category_changed)
        third_row.addWidget(self.category_label)
        third_row.addWidget(self.category_input, 1)

        # Subcategory field
        self.subcategory_label = QLabel("Sub Category:")
        self.subcategory_input = QComboBox()
        third_row.addWidget(self.subcategory_label)
        third_row.addWidget(self.subcategory_input, 1)

        self.layout.addRow(third_row)

        # Fourth row: Description
        self.description_label = QLabel("Description:")
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(60)
        self.layout.addRow(self.description_label, self.description_input)

        # Fifth row: Date
        self.date_label = QLabel("Date:")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.layout.addRow(self.date_label, self.date_input)

    def create_buttons(self):
        """Create buttons for the transaction form."""
        button_layout = QHBoxLayout()

        # Add Transaction button
        self.add_button = QPushButton("Add Transaction")
        self.add_button.setObjectName("add_button")
        self.add_button.clicked.connect(self.add_transaction)
        button_layout.addWidget(self.add_button)

        # Defaults button
        self.defaults_button = QPushButton("Defaults")
        self.defaults_button.setObjectName("defaults_button")
        self.defaults_button.clicked.connect(self.load_defaults)
        button_layout.addWidget(self.defaults_button)

        # We'll add the cancel button later if needed
        self.cancel_button = None

        self.layout.addRow(button_layout)

    def add_cancel_button(self, callback):
        """Add a cancel button to the form."""
        if self.cancel_button is None:
            # Create a new button
            self.cancel_button = QPushButton("Cancel")
            self.cancel_button.setObjectName("cancel_button")
            self.cancel_button.clicked.connect(callback)

            # Find the button layout - it's the last row in the form
            for i in range(self.layout.rowCount()):
                item = self.layout.itemAt(i)
                if item and item.layout():
                    # Check if this layout contains our add_button
                    layout_has_add_button = False
                    for j in range(item.layout().count()):
                        widget = item.layout().itemAt(j).widget()
                        if widget == self.add_button:
                            layout_has_add_button = True
                            break

                    if layout_has_add_button:
                        # Add the cancel button to this layout
                        item.layout().addWidget(self.cancel_button)
                        break

            # Initially hide the cancel button (only show in edit mode)
            self.cancel_button.hide()

    def refresh_dropdowns(self):
        """Refresh all dropdown menus with current data."""
        # Refresh accounts dropdown
        self.account_input.clear()
        accounts = Account.get_all()
        for account in accounts:
            self.account_input.addItem(account.name, account.id)

        # Refresh categories dropdown based on current type
        self.refresh_categories()

    def refresh_categories(self):
        """Refresh categories dropdown based on current transaction type."""
        transaction_type = self.type_input.currentText()

        self.category_input.clear()
        # Add empty option for category
        self.category_input.addItem("", None)
        categories = Category.get_by_type(transaction_type)
        for category in categories:
            self.category_input.addItem(category.name, category.id)

        # Refresh subcategories based on selected category
        self.refresh_subcategories()

    def refresh_subcategories(self):
        """Refresh subcategories dropdown based on current category."""
        category_id = self.category_input.currentData()

        self.subcategory_input.clear()
        self.subcategory_input.addItem("", None)  # Add empty option

        if category_id:
            subcategories = SubCategory.get_by_category(category_id)
            for subcategory in subcategories:
                self.subcategory_input.addItem(subcategory.name, subcategory.id)

    def on_type_changed(self, transaction_type):
        """Handle when transaction type is changed."""
        self.refresh_categories()

    def on_category_changed(self, index):
        """Handle when category is changed."""
        self.refresh_subcategories()

    def load_defaults(self):
        """Load default values from settings."""
        # TODO: Implement loading defaults from settings
        pass

    def load_transaction(self, transaction):
        """Load an existing transaction into the form for editing."""
        self.current_transaction = transaction

        # Set form values
        self.name_input.setText(transaction.name)
        self.value_input.setText(str(transaction.value))

        # Set transaction type
        index = self.type_input.findText(transaction.transaction_type)
        if index >= 0:
            self.type_input.setCurrentIndex(index)

        # Set account
        index = self.account_input.findData(transaction.account_id)
        if index >= 0:
            self.account_input.setCurrentIndex(index)

        # Set category
        index = self.category_input.findData(transaction.category_id)
        if index >= 0:
            self.category_input.setCurrentIndex(index)

        # Set subcategory
        index = self.subcategory_input.findData(transaction.sub_category_id)
        if index >= 0:
            self.subcategory_input.setCurrentIndex(index)

        # Set description
        self.description_input.setText(transaction.description)

        # Set date
        date = QDate.fromString(transaction.date, "yyyy-MM-dd")
        self.date_input.setDate(date)

        # Change button text
        self.add_button.setText("Update Transaction")

        # Show cancel button in edit mode
        if self.cancel_button:
            self.cancel_button.show()

    def clear_form(self):
        """Clear all form fields."""
        self.current_transaction = None

        self.name_input.clear()
        self.value_input.clear()
        self.type_input.setCurrentIndex(0)
        self.account_input.setCurrentIndex(0)
        self.category_input.setCurrentIndex(0)
        self.subcategory_input.setCurrentIndex(0)
        self.description_input.clear()
        self.date_input.setDate(QDate.currentDate())

        # Reset button text
        self.add_button.setText("Add Transaction")

        # Hide cancel button in add mode
        if self.cancel_button:
            self.cancel_button.hide()

    def add_transaction(self):
        """Add or update a transaction based on form data."""
        # Get form values
        name = self.name_input.text()
        value_text = self.value_input.text()
        transaction_type = self.type_input.currentText()
        account_id = self.account_input.currentData()
        category_id = self.category_input.currentData()
        subcategory_id = self.subcategory_input.currentData()
        description = self.description_input.toPlainText()
        date = self.date_input.date().toString("yyyy-MM-dd")

        # Validate form
        if not name:
            # TODO: Show error message
            return

        try:
            value = float(value_text) if value_text else 0.0
        except ValueError:
            # TODO: Show error message
            return

        if not account_id:
            # TODO: Show error message
            return

        # Category is now optional
        # if not category_id:
        #     # TODO: Show error message
        #     return

        # Create or update transaction
        if self.current_transaction:
            # Update existing transaction
            transaction = self.current_transaction
            transaction.name = name
            transaction.value = value
            transaction.transaction_type = transaction_type
            transaction.account_id = account_id
            transaction.category_id = category_id
            transaction.sub_category_id = subcategory_id
            transaction.description = description
            transaction.date = date
        else:
            # Create new transaction
            transaction = Transaction(
                name=name,
                description=description,
                account_id=account_id,
                transaction_type=transaction_type,
                category_id=category_id,
                sub_category_id=subcategory_id,
                date=date,
                value=value
            )

        # Save transaction to database
        transaction.save()

        # Clear form
        self.clear_form()

        # Emit signal
        self.transaction_added.emit(transaction)
