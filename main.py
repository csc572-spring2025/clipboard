#!/usr/bin/env python3
"""
Main entry point for the Clipboard Manager application.

This is the refactored version of backgroundapp.py, split into multiple
modules for better organization and maintainability.

Features:
- Scrollable display
- Filter on the sidebar for different content types
- Search bar that lets you search the content of each clipboard item
- Storing clipboard history
- Option to clear clipboard history
"""

import sys
from PyQt5.QtWidgets import QApplication

from src.ui.main_window import ClipboardManager


def main():
    """Main function to start the clipboard manager application."""
    app = QApplication(sys.argv)
    window = ClipboardManager()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 