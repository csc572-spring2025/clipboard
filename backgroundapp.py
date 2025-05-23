import sys
import os
import json
import time
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QListWidget, 
                            QLineEdit, QTabWidget, QScrollArea, QFrame,
                            QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QFont
import pyperclip
import datetime

class ClipboardSignals(QObject):
    new_clipboard_content = pyqtSignal(dict)

class ClipboardManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clipboard")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        
        self.clipboard_items = []
        self.data_file = "clipboard_data.json"
        self.load_clipboard_data()
        
        self.signals = ClipboardSignals()
        self.signals.new_clipboard_content.connect(self.add_clipboard_item)
        
        # main page
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # sidebar
        sidebar = QWidget()
        sidebar.setMaximumWidth(270)
        sidebar_layout = QVBoxLayout(sidebar)
        title_label = QLabel("Clipboard")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        sidebar_layout.addWidget(title_label)
        
        # buttons
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
        
        # filter buttons
        self.all_btn.clicked.connect(lambda: self.filter_items("All"))
        self.code_btn.clicked.connect(lambda: self.filter_items("Code"))
        self.latex_btn.clicked.connect(lambda: self.filter_items("LaTeX"))
        self.quotes_btn.clicked.connect(lambda: self.filter_items("Quotes"))
        self.plaintext_btn.clicked.connect(lambda: self.filter_items("Plaintext"))
        
        sidebar_layout.addWidget(self.all_btn)
        sidebar_layout.addWidget(self.code_btn)
        sidebar_layout.addWidget(self.latex_btn)
        sidebar_layout.addWidget(self.quotes_btn)
        sidebar_layout.addWidget(self.plaintext_btn)
        
        length_label = QLabel("Length")
        sidebar_layout.addWidget(length_label)
        slider_frame = QFrame()
        slider_frame.setFrameShape(QFrame.StyledPanel)
        slider_frame.setMinimumHeight(30)
        sidebar_layout.addWidget(slider_frame)
        sidebar_layout.addStretch()
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        
        # search bar
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
        
        # settings 
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(40, 40)
        settings_btn.setStyleSheet("background-color: transparent; font-size: 20px;")
        search_layout.addWidget(settings_btn)
        
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
        
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area)
        
        self.setup_system_tray()
        self.display_clipboard_items()
        
        # start clipboard monitoring in a separate thread
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self.monitor_clipboard)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def create_sidebar_button(self, text, icon_text):
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
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)
        return btn
    
    def create_clipboard_item(self, item):
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 8px;
                margin: 5px 0;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        
        # content and copy button
        top_layout = QHBoxLayout()
        
        # icon based on type
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
        
        content_label = QLabel(item["content"])
        content_label.setStyleSheet("font-size: 16px;")
        content_label.setWordWrap(True)
        top_layout.addWidget(content_label, 1)
        
        copy_btn = QPushButton("Copy")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 16px;
            }
        """)

        copy_btn.setCursor(Qt.PointingHandCursor)
        copy_btn.clicked.connect(lambda: pyperclip.copy(item["content"]))
        top_layout.addWidget(copy_btn)
        
        layout.addLayout(top_layout)
        
        # type and time info
        info_layout = QHBoxLayout()
        type_label = QLabel(item["type"])
        type_label.setStyleSheet("color: #888;")
        time_label = QLabel(item["time"])
        time_label.setStyleSheet("color: #888;")
        chars_label = QLabel(item["chars"])
        chars_label.setStyleSheet("color: #888;")
        
        info_layout.addWidget(type_label)
        info_layout.addWidget(time_label)
        info_layout.addStretch()
        info_layout.addWidget(chars_label)
        
        layout.addLayout(info_layout)
        
        return frame
    
    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("edit-copy"))  
        
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def closeEvent(self, event):
        event.ignore()
        self.hide()
    
    def quit_application(self):
        # save data before quitting
        self.save_clipboard_data()
        self.monitoring_active = False
        QApplication.quit()
    
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
    
    def add_clipboard_item(self, item):
        self.clipboard_items.insert(0, item)
        self.save_clipboard_data()
        item_widget = self.create_clipboard_item(item)
        self.items_layout.insertWidget(0, item_widget)
    
    def display_clipboard_items(self):
        while self.items_layout.count() > 1: 
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for item in self.clipboard_items:
            item_widget = self.create_clipboard_item(item)
            self.items_layout.insertWidget(0, item_widget)
    
    def filter_items(self, filter_type):
        while self.items_layout.count() > 1: 
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for item in self.clipboard_items:
            if filter_type == "All" or item["type"] == filter_type:
                item_widget = self.create_clipboard_item(item)
                self.items_layout.insertWidget(0, item_widget)
    
    def search_items(self):
        search_text = self.search_bar.text().lower()
        
        while self.items_layout.count() > 1: 
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for item in self.clipboard_items:
            if search_text in item["content"].lower():
                item_widget = self.create_clipboard_item(item)
                self.items_layout.insertWidget(0, item_widget)
    
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
    
    def save_clipboard_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.clipboard_items, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving clipboard data: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClipboardManager()
    window.show()
    sys.exit(app.exec_())