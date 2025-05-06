import sys
from PyQt6.QtWidgets import (
    QMainWindow, QApplication, QTabWidget, QVBoxLayout, QWidget, QMenuBar, QMenu, QStatusBar
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon

from gui.screens.transactions_screen import TransactionsScreen


class MainWindow(QMainWindow):
    """
    Main application window that contains all screens.
    """
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Open Grid Multicurrency - Personal Finance Tracker")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Create and add screens
        self.transactions_screen = TransactionsScreen()
        self.tab_widget.addTab(self.transactions_screen, "Transactions")

        # Create menu bar
        self.create_menu_bar()

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def create_menu_bar(self):
        """Create the application menu bar."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")

        # File > New Transaction
        new_transaction_action = QAction("New Transaction", self)
        new_transaction_action.setShortcut("Ctrl+N")
        new_transaction_action.triggered.connect(self.on_new_transaction)
        file_menu.addAction(new_transaction_action)

        # File > Import
        import_action = QAction("Import from CSV...", self)
        import_action.triggered.connect(self.on_import)
        file_menu.addAction(import_action)

        file_menu.addSeparator()

        # File > Exit
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")

        # Edit > Undo
        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.on_undo)
        edit_menu.addAction(undo_action)

        # Edit > Redo
        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.on_redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        # Edit > Save Changes
        save_action = QAction("Save Changes", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_save_changes)
        edit_menu.addAction(save_action)

        # View menu
        view_menu = menu_bar.addMenu("View")

        # View > Refresh
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.on_refresh)
        view_menu.addAction(refresh_action)

        # Help menu
        help_menu = menu_bar.addMenu("Help")

        # Help > About
        about_action = QAction("About", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def on_new_transaction(self):
        """Handle new transaction action."""
        if self.tab_widget.currentWidget() == self.transactions_screen:
            self.transactions_screen.add_new_transaction()

    def on_import(self):
        """Handle import action."""
        # TODO: Implement CSV import functionality
        self.status_bar.showMessage("Import functionality not implemented yet")

    def on_undo(self):
        """Handle undo action."""
        current_widget = self.tab_widget.currentWidget()
        if hasattr(current_widget, 'undo'):
            current_widget.undo()

    def on_redo(self):
        """Handle redo action."""
        current_widget = self.tab_widget.currentWidget()
        if hasattr(current_widget, 'redo'):
            current_widget.redo()

    def on_refresh(self):
        """Handle refresh action."""
        current_widget = self.tab_widget.currentWidget()
        if hasattr(current_widget, 'refresh'):
            current_widget.refresh()

    def on_save_changes(self):
        """Handle save changes action."""
        current_widget = self.tab_widget.currentWidget()
        if hasattr(current_widget, 'save_changes'):
            current_widget.save_changes()
            self.status_bar.showMessage("Changes saved successfully")

    def on_about(self):
        """Handle about action."""
        # TODO: Implement about dialog
        self.status_bar.showMessage("Open Grid Multicurrency - Personal Finance Tracker")
