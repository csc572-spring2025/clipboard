# Clipboard Manager - Refactored Structure

This is the refactored version of the original `backgroundapp.py` file, split into multiple modules for better organization, maintainability, and separation of concerns.

## Project Structure

```
clipboard/
├── main.py                     # Main entry point (replaces backgroundapp.py)
├── src/                        # Source code package
│   ├── __init__.py
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── signals.py          # PyQt signals for clipboard events
│   │   ├── clipboard_monitor.py # Background clipboard monitoring
│   │   └── data_manager.py     # Data persistence (JSON file handling)
│   ├── ui/                     # User interface components
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main application window (refactored ClipboardManager)
│   │   ├── components.py       # UI component factory methods
│   │   └── system_tray.py      # System tray functionality
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       └── categorizer.py      # Content categorization logic
├── requirements.txt            # Python dependencies
└── clipboard_data.json        # Clipboard history data file
```

## Key Refactoring Changes

### 1. Separation of Concerns

- **Core Logic**: Moved to `src/core/` directory
- **UI Components**: Moved to `src/ui/` directory
- **Utilities**: Moved to `src/utils/` directory

### 2. Class Extraction

The original monolithic `ClipboardManager` class has been split into:

- **`ClipboardSignals`** (`src/core/signals.py`): Handles PyQt signals
- **`ClipboardMonitor`** (`src/core/clipboard_monitor.py`): Background clipboard monitoring
- **`ClipboardDataManager`** (`src/core/data_manager.py`): Data persistence
- **`ClipboardSystemTray`** (`src/ui/system_tray.py`): System tray functionality
- **`UIComponents`** (`src/ui/components.py`): UI component factory methods
- **`ContentCategorizer`** (`src/utils/categorizer.py`): Content categorization logic
- **`ClipboardManager`** (`src/ui/main_window.py`): Main window (simplified)

### 3. Benefits of Refactoring

1. **Modularity**: Each component has a single responsibility
2. **Maintainability**: Easier to modify individual components
3. **Testability**: Components can be tested in isolation
4. **Reusability**: Components can be reused in other parts of the application
5. **Readability**: Smaller, focused files are easier to understand

## Running the Application

To run the refactored application:

```bash
python main.py
```

The application maintains all the original functionality:

- Clipboard monitoring and history
- Content categorization (Code, LaTeX, Quotes, Plaintext)
- Search functionality
- Filter by content type
- System tray integration
- Data persistence

## Original vs Refactored

- **Original**: Single file (`backgroundapp.py`) with 497 lines
- **Refactored**: Multiple focused modules with clear separation of concerns

The refactored version is more professional, maintainable, and follows Python best practices for project organization.
