'''
Implements the user interface for the clipboard app using PyQT
Features:
- Scrollable display
- Filter on the sidebar for different content types
- Search bar that lets you search the content of each clipboard item
- Storing clipboard history
- Option to clear clipboard history
'''

import sys
import os
import json
import time
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QListWidget, 
                            QLineEdit, QTabWidget, QScrollArea, QFrame,
                            QSystemTrayIcon, QMenu, QAction, QMessageBox)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QFont
import pyperclip
import datetime

# when emitted, this signal sends a the clipboard item info as a dictionary
class ClipboardSignals(QObject):
    new_clipboard_content = pyqtSignal(dict)

# main window for the entire application
class ClipboardManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clipboard")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        
        self.clipboard_items = []
        self.data_file = "clipboard_data.json" # path to save clipboard data
        self.load_clipboard_data() # load history
        
        self.signals = ClipboardSignals()
        self.signals.new_clipboard_content.connect(self.add_clipboard_item)
        
        # main page
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # sidebar for filters
        sidebar = QWidget()
        sidebar.setMaximumWidth(270)
        sidebar_layout = QVBoxLayout(sidebar)
        title_label = QLabel("Clipboard")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        sidebar_layout.addWidget(title_label)
        
        # create buttons on the sidebar
        self.all_btn = self.create_sidebar_button("All", "≡")
        self.code_btn = self.create_sidebar_button("Code", "⌨")
        self.latex_btn = self.create_sidebar_button("LaTeX", "𝐄")
        self.quotes_btn = self.create_sidebar_button("Quotes", "❝")
        self.plaintext_btn = self.create_sidebar_button("Plaintext", "≡")

        # turns mouse into a pointer
        self.all_btn.setCursor(Qt.PointingHandCursor)
        self.code_btn.setCursor(Qt.PointingHandCursor)
        self.latex_btn.setCursor(Qt.PointingHandCursor)
        self.quotes_btn.setCursor(Qt.PointingHandCursor)
        self.plaintext_btn.setCursor(Qt.PointingHandCursor)
        
        # activate filter buttons
        self.all_btn.clicked.connect(lambda: self.filter_items("All"))
        self.code_btn.clicked.connect(lambda: self.filter_items("Code"))
        self.latex_btn.clicked.connect(lambda: self.filter_items("LaTeX"))
        self.quotes_btn.clicked.connect(lambda: self.filter_items("Quotes"))
        self.plaintext_btn.clicked.connect(lambda: self.filter_items("Plaintext"))
        
        # add buttons to the sidebar
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
        clear_btn.clicked.connect(self.show_popup)
        sidebar_layout.addWidget(clear_btn)
        
        # create a QLabel (non-interactive components that can display text and/or an image) and a placeholder for the slider
        # length_label = QLabel("Length") # length currently does nothing
        # sidebar_layout.addWidget(length_label)
        slider_frame = QFrame()
        slider_frame.setFrameShape(QFrame.StyledPanel)
        slider_frame.setMinimumHeight(30)
        sidebar_layout.addWidget(slider_frame)
        sidebar_layout.addStretch()

        # create content area for search bar and clipboard items
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        
        # create search layout: search bar
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
        
        # # settings button (currently does nothing)
        # settings_btn = QPushButton("⚙")
        # settings_btn.setFixedSize(40, 40)
        # settings_btn.setStyleSheet("background-color: transparent; font-size: 20px;")
        # search_layout.addWidget(settings_btn)
        
        # add search layout into the main layout of the app
        content_layout.addLayout(search_layout)
        
        # clipboard items area

        # scroll area and scroll
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
        
        # add sidebar and content area to the main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area)
        
        self.setup_system_tray()
        self.display_clipboard_items()
        
        # start clipboard monitoring in a separate thread
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def show_popup(self):
        msg = QMessageBox()
        msg.setWindowTitle("Clear Copy History")
        msg.setText("Are you sure you want to clear your copy history?")

        # clear_button = msg.addButton("Clear", QMessageBox.ActionRole)
        msg.setIcon(QMessageBox.Warning) # Optional: Set icon
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel) # Optional: Add buttons

        # Additional options (optional):
        # msg.setInformativeText("More details can be added here.")
        # msg.setDetailedText("Detailed information if needed.")

        result = msg.exec_() # Show the popup and get the user's choice

        if result == QMessageBox.Ok:
            self.clear_clipboard_history()
    
    # returns a button that is ready to be added to the sidebar
    # params: text (the label for the button)
    def create_sidebar_button(self, text, icon_img):
        btn = QPushButton(f" {text}")
        btn.setIcon(QIcon())  
        btn.setIconSize(QSize(24, 24))
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 10px;
                font-size: 16px;
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        return btn
    
    # returns a QFrame that represents a clipboard item, with properly formatted information
    # params: item (a dictionary with keys: type of content, content itself, time (formatted), time (nonformatted, in ISO), character length)
    def create_clipboard_item(self, item):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 8px;
                margin: 5px 0;
                padding: 5px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # content and copy button
        top_layout = QHBoxLayout()
        
        # assign icon based on type
        icon_label = QLabel()
        if item["type"] == "Code":
            icon_label.setText("⌨")
        elif item["type"] == "LaTeX":
            icon_label.setText("𝐄")
        elif item["type"] == "Quotes":
            icon_label.setText("❝")
        else:
            icon_label.setText("≡")
        
        icon_label.setStyleSheet("font-size: 32px; color: #888;")
        top_layout.addWidget(icon_label)
        
        # style content of the item
        content_label = QLabel(item["content"])
        content_label.setStyleSheet("font-size: 16px;")
        content_label.setWordWrap(True)
        top_layout.addWidget(content_label, 1)
        
        # create and style the "Copy" button
        copy_btn = QPushButton("Copy")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #FFF;
                color: #333;
            }
        """)

        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(lambda: pyperclip.copy(item["content"]))
        top_layout.addWidget(copy_btn)
        
        layout.addLayout(top_layout)
        
        # layout type, time, and char length info
        info_layout = QHBoxLayout()
        type_label = QLabel(item["type"])
        type_label.setStyleSheet("color: #888;")
        time_label = QLabel(item["time"])
        time_label.setStyleSheet("color: #888;")
        chars_label = QLabel(item["chars"])
        chars_label.setStyleSheet("color: #888;")
        
        info_layout.addWidget(type_label)
        info_layout.addWidget(time_label)
        info_layout.addWidget(chars_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        return frame
    
    # initializes the system tray icon and its menu
    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("edit-copy"))  
        
        tray_menu = QMenu() # create a context menu (menus opened by right-click)
        # add a show option
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        # add a hide option
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        # add a quit option
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)    # attach content menu to tray icon
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    # triggers when the tray icon is interacted with: responds to right-click
    # params: reason (the event that the tray icon is responding to)
    def tray_icon_activated(self, reason):
        # if right-clicked and menu is shown, hide it; else, show the menu
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    # overrides default close behavior to hide the window instead of quitting
    # params: event (QCloseEvent, or the event triggered when the window is closed)
    def closeEvent(self, event):
        event.ignore()
        self.hide()
    
    # dictates behavior when the app is quitted
    def quit_application(self):
        # save data before quitting
        self.save_clipboard_data()
        self.monitoring_active = False # stop monitoring background thread
        QApplication.quit()
    
    # checks the clipboard for new content copied
    def monitor_clipboard(self):
        if not os.path.exists("clipboard_logs"):
            os.makedirs("clipboard_logs")
        
        previous_content = pyperclip.paste()
        seen_entries = {previous_content}
        
        while self.monitoring_active:
            try:
                current_content = pyperclip.paste()
                
                if current_content != previous_content and current_content not in seen_entries:
                    timestamp = datetime.datetime.now()
                    formatted_time = timestamp.strftime("%I:%M %p")
                    

                    content_type = self.categorize_content(current_content)
                    
                    item = {
                        "type": content_type,
                        "content": current_content,
                        "time": formatted_time,
                        "timestamp": timestamp.isoformat(),
                        "chars": f"{len(current_content)} characters"
                    }
                    

                    self.signals.new_clipboard_content.emit(item)
                    

                    previous_content = current_content
                    seen_entries.add(current_content)
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error in clipboard monitoring: {e}")
                time.sleep(1)
    
    # categorization logic
    # returns category label
    # params: content (raw text copied to the clipboard)
    def categorize_content(self, content):
        # super simple categorization that doesn't really work but can be updated
        content = content.strip()
        
        # Check for code
        code_indicators = ["def ", "function", "class ", "{", "};", "import ", "from ", "public ", "private ", "#include"]
        for indicator in code_indicators:
            if indicator in content:
                return "Code"
        
        # Check for LaTeX
        latex_indicators = ["\\begin{", "\\end{", "\\frac", "\\sum", "\\int", "\\lim", "\\mathbb"]
        for indicator in latex_indicators:
            if indicator in content:
                return "LaTeX"
        
        # Check for quotes
        if (content.startswith('"') and content.endswith('"')) or (content.startswith("'") and content.endswith("'")):
            return "Quotes"
        
        # Default to plaintext
        return "Plaintext"
    
    # add new clipboard item to the top of the UI list
    # params: item (clipboard item to be added)
    def add_clipboard_item(self, item):
        self.clipboard_items.insert(0, item)
        self.save_clipboard_data()
        item_widget = self.create_clipboard_item(item)
        self.items_layout.insertWidget(0, item_widget)
    
    # renders all clipboard items in memory to the UI
    def display_clipboard_items(self):
        while self.items_layout.count() > 1: 
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for item in self.clipboard_items:
            item_widget = self.create_clipboard_item(item)
            self.items_layout.insertWidget(0, item_widget)
    
    # filters items based on type
    # params: filter_type (the type to filter by)
    def filter_items(self, filter_type):
        while self.items_layout.count() > 1: 
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for item in self.clipboard_items:
            if filter_type == "All" or item["type"] == filter_type:
                item_widget = self.create_clipboard_item(item)
                self.items_layout.insertWidget(0, item_widget)
    
    # filters items based on text entered in search bar
    def search_items(self):
        search_text = self.search_bar.text().lower() # changes search entry to lowercase so it's case-insensitive
        
        while self.items_layout.count() > 1: 
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # for each clipboard item, if the search entry matches a substring in the item content
        for item in self.clipboard_items: 
            if search_text in item["content"].lower():
                item_widget = self.create_clipboard_item(item)
                self.items_layout.insertWidget(0, item_widget)
    
    # loads clipboard history from JSON file and adds it to self.clipboard_items
    def load_clipboard_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.clipboard_items = json.load(f)
            else:
                self.clipboard_items = []
        except Exception as e:
            print(f"Error loading clipboard data: {e}")
            self.clipboard_items = []
    
    # saves self.clipboard_items to a JSON file
    def save_clipboard_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.clipboard_items, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving clipboard data: {e}")

    # clears clipboard history
    def clear_clipboard_history(self):
        self.clipboard_items.clear()  # Clear the internal list

        # Remove all widgets from the UI layout
        while self.items_layout.count() > 1:
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.save_clipboard_data()  # Update the saved data file

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClipboardManager()
    window.show()
    sys.exit(app.exec_())