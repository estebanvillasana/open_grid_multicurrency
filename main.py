import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QFile, QTextStream

from gui.screens.main_window import MainWindow
from data.repositories.database import DatabaseConnection


def main():
    """
    Main entry point for the application.
    """
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Open Grid Multicurrency")

    # Set up database connection
    db_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'user_data_default_directory',
        'financial_tracker.db'
    )
    db = DatabaseConnection()
    db.connect(db_path)

    # Load application style
    style_file = QFile(os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'gui',
        'style',
        'style.qss'
    ))
    if style_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
        stream = QTextStream(style_file)
        app.setStyleSheet(stream.readAll())
        style_file.close()

    # Enable item view styling in the QTableWidget
    app.setAttribute(Qt.ApplicationAttribute.AA_UseStyleSheetPropagationInWidgetStyles, True)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
