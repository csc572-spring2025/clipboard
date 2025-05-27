"""
Main window for the clipboard manager application.
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QLineEdit, QScrollArea, 
                            QFrame, QMessageBox, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ..core.signals import ClipboardSignals
from ..core.clipboard_monitor import ClipboardMonitor
from ..core.data_manager import ClipboardDataManager
from .system_tray import ClipboardSystemTray
from .components import UIComponents


class ClipboardManager(QMainWindow):
    """
    Main window for the entire clipboard manager application.
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clipboard")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        
        # Initialize core components
        self.clipboard_items = []
        self.data_manager = ClipboardDataManager("clipboard_data.json")
        self.clipboard_items = self.data_manager.load_clipboard_data()
        
        # Initialize signals and monitoring
        self.signals = ClipboardSignals()
        self.signals.new_clipboard_content.connect(self.add_clipboard_item)
        self.clipboard_monitor = ClipboardMonitor(self.signals)
        
        # Initialize UI components
        self.ui_components = UIComponents()
        
        # Setup UI
        self.setup_ui()
        
        # Setup system tray
        self.system_tray = ClipboardSystemTray(self)
        
        # Display existing clipboard items
        self.display_clipboard_items()
        
        # Start clipboard monitoring
        self.clipboard_monitor.start_monitoring()
    
    def setup_ui(self):
        """Setup the main user interface."""
        # Main page
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Setup sidebar
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar)
        
        # Setup content area
        content_area = self.create_content_area()
        main_layout.addWidget(content_area)
    
    def create_sidebar(self):
        """Create and return the sidebar widget."""
        sidebar = QWidget()
        sidebar.setMaximumWidth(270)
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Title
        title_label = QLabel("Clipboard")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        sidebar_layout.addWidget(title_label)
        
        # Create filter buttons
        self.all_btn = self.ui_components.create_sidebar_button("All", "≡")
        self.code_btn = self.ui_components.create_sidebar_button("Code", "⌨")
        self.latex_btn = self.ui_components.create_sidebar_button("LaTeX", "𝐄")
        self.quotes_btn = self.ui_components.create_sidebar_button("Quotes", "❝")
        self.plaintext_btn = self.ui_components.create_sidebar_button("Plaintext", "≡")
        
        # Connect filter buttons
        self.all_btn.clicked.connect(lambda: self.filter_items("All"))
        self.code_btn.clicked.connect(lambda: self.filter_items("Code"))
        self.latex_btn.clicked.connect(lambda: self.filter_items("LaTeX"))
        self.quotes_btn.clicked.connect(lambda: self.filter_items("Quotes"))
        self.plaintext_btn.clicked.connect(lambda: self.filter_items("Plaintext"))
        
        # Add buttons to sidebar
        sidebar_layout.addWidget(self.all_btn)
        sidebar_layout.addWidget(self.code_btn)
        sidebar_layout.addWidget(self.latex_btn)
        sidebar_layout.addWidget(self.quotes_btn)
        sidebar_layout.addWidget(self.plaintext_btn)
        
        # Clear all button
        clear_btn = QPushButton("Clear All")
        clear_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 10px;
                font-size: 16px;
                background-color: transparent;
                color: #ECABF5;
                border: 1px solid #ECABF5;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        clear_btn.clicked.connect(self.show_clear_popup)
        sidebar_layout.addWidget(clear_btn)
        
        # Placeholder for slider
        slider_frame = QFrame()
        slider_frame.setFrameShape(QFrame.StyledPanel)
        slider_frame.setMinimumHeight(30)
        sidebar_layout.addWidget(slider_frame)
        sidebar_layout.addStretch()
        
        return sidebar
    
    def create_content_area(self):
        """Create and return the content area widget."""
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        
        # Search layout
        search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #333;
                border-radius: 5px;
                padding: 8px;
                font-size: 16px;
            }
        """)
        self.search_bar.textChanged.connect(self.search_items)
        search_layout.addWidget(self.search_bar)
        content_layout.addLayout(search_layout)
        
        # Clipboard items area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar::handle:vertical {
                border: 1px outset gray;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #dedede;
            }
            QScrollBar::handle:horizontal {
                border: 1px outset gray;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #dedede;
            }
        """)
        
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.addStretch()
        
        scroll_area.setWidget(self.items_widget)
        content_layout.addWidget(scroll_area)
        
        return content_area
    
    def show_clear_popup(self):
        """Show confirmation popup for clearing clipboard history."""
        msg = QMessageBox()
        msg.setWindowTitle("Clear Copy History")
        msg.setText("Are you sure you want to clear your copy history?")
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        result = msg.exec_()
        if result == QMessageBox.Ok:
            self.clear_clipboard_history()
    
    def add_clipboard_item(self, item):
        """
        Add new clipboard item to the top of the UI list.
        
        Args:
            item (dict): Clipboard item to be added
        """
        self.clipboard_items.insert(0, item)
        self.data_manager.save_clipboard_data(self.clipboard_items)
        item_widget = self.ui_components.create_clipboard_item(item)
        self.items_layout.insertWidget(0, item_widget)
    
    def display_clipboard_items(self):
        """Render all clipboard items in memory to the UI."""
        self.clear_items_layout()
        for item in self.clipboard_items:
            item_widget = self.ui_components.create_clipboard_item(item)
            self.items_layout.insertWidget(0, item_widget)
    
    def filter_items(self, filter_type):
        """
        Filter items based on type.
        
        Args:
            filter_type (str): The type to filter by
        """
        self.clear_items_layout()
        for item in self.clipboard_items:
            if filter_type == "All" or item["type"] == filter_type:
                item_widget = self.ui_components.create_clipboard_item(item)
                self.items_layout.insertWidget(0, item_widget)
    
    def search_items(self):
        """Filter items based on text entered in search bar."""
        search_text = self.search_bar.text().lower()
        self.clear_items_layout()
        
        for item in self.clipboard_items:
            if search_text in item["content"].lower():
                item_widget = self.ui_components.create_clipboard_item(item)
                self.items_layout.insertWidget(0, item_widget)
    
    def clear_items_layout(self):
        """Clear all widgets from the items layout."""
        while self.items_layout.count() > 1:
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def clear_clipboard_history(self):
        """Clear clipboard history."""
        self.clipboard_items.clear()
        self.clear_items_layout()
        self.data_manager.save_clipboard_data(self.clipboard_items)
    
    def closeEvent(self, event):
        """
        Override default close behavior to hide the window instead of quitting.
        
        Args:
            event: QCloseEvent triggered when the window is closed
        """
        event.ignore()
        self.hide()
    
    def quit_application(self):
        """Handle application quit."""
        self.data_manager.save_clipboard_data(self.clipboard_items)
        self.clipboard_monitor.stop_monitoring()
        QApplication.quit() 