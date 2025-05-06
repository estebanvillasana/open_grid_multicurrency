# Open Grid Multicurrency - Personal Finance Tracker

A desktop personal finance tracker application designed for individual use, with an emphasis on multi-currency support and rapid, spreadsheet-style data entry.

## Features

- **Transactions Table**: Editable grid (like a spreadsheet) using PyQt6's `QTableWidget`, custom delegates, and undo/redo functionality.
- **Bank Accounts**: Manage accounts, currencies, balances, and metadata.
- **Multi-Currency Engine**: Each transaction stores both the original currency and a converted amount in the user's selected main currency.
- **Exchange Rate Integration**: Connects to a REST API to fetch currency rates (cached to avoid repeated requests).
- **Default Values**: Set defaults for fast entry of recurring types, categories, or currencies.
- **Excel-like Data Entry**: Quick and smooth data entry similar to Excel, Notion, or Airtable.

## Project Structure

- `main.py`: Launch point
- `gui/screens/`: Each screen is a standalone module (e.g., `transactions_screen.py`, `accounts_screen.py`)
- `gui/widgets/`: Custom PyQt components (combo boxes, styled tables, etc.)
- `gui/style/`: CSS-like styling for the application
- `core/`: Business logic (transaction validation, category handling, etc.)
- `data/`: Database logic and storage (SQLite)
- `models/`: Data models (e.g., `Transaction`, `Account`)
- `services/`: External APIs (currency exchange)
- `user_data_default_directory/`: User's selected folder with `.db`, JSONs, backups

## Requirements

- Python 3.6+
- PyQt6
- SQLite3

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/open_grid_multicurrency.git
   cd open_grid_multicurrency
   ```

2. Install dependencies:
   ```
   pip install PyQt6
   ```

3. Run the application:
   ```
   python main.py
   ```

## Usage

### Adding Transactions

1. Fill in the transaction details in the form at the top of the Transactions screen.
2. Click "Add Transaction" to add the transaction to the database.

### Editing Transactions

1. Double-click on a cell in the transaction grid to edit it directly.
2. Select a row and click "Edit Transaction" to load it into the form for editing.
3. Make your changes and click "Update Transaction" to save.

### Deleting Transactions

1. Select a row in the transaction grid.
2. Click "Delete" to remove the transaction.

### Saving Changes

1. After making changes directly in the grid, click "Save Changes" to commit them to the database.
2. Click "Discard Changes" to revert to the last saved state.

## Future Enhancements

- CSV Import: Support for uploading CSV files and mapping fields to internal structures.
- Settings Page: Choose currencies, main currency, wallet name, and data folder location.
- Summary Views: Reports and a simple dashboard.
- Mobile Sync: Synchronization with mobile devices.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
# open_grid_multicurrency
