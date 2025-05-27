"""
UI components for the clipboard manager.
"""

from PyQt5.QtWidgets import (QPushButton, QLabel, QFrame, QVBoxLayout, 
                            QHBoxLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
import pyperclip


class UIComponents:
    """
    Factory class for creating UI components.
    """
    
    @staticmethod
    def create_sidebar_button(text, icon_img):
        """
        Create a sidebar button with consistent styling.
        
        Args:
            text (str): The label for the button
            icon_img (str): Icon image for the button (currently unused)
            
        Returns:
            QPushButton: Styled button ready to be added to the sidebar
        """
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
        btn.setCursor(Qt.PointingHandCursor)
        return btn
    
    @staticmethod
    def create_clipboard_item(item):
        """
        Create a QFrame representing a clipboard item with formatted information.
        
        Args:
            item (dict): Dictionary with keys: type, content, time, timestamp, chars
            
        Returns:
            QFrame: Styled frame containing the clipboard item
        """
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
        
        # Content and copy button
        top_layout = QHBoxLayout()
        
        # Assign icon based on type
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
        
        # Style content of the item
        content_label = QLabel(item["content"])
        content_label.setStyleSheet("font-size: 16px;")
        content_label.setWordWrap(True)
        top_layout.addWidget(content_label, 1)
        
        # Create and style the "Copy" button
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
        
        # Layout type, time, and char length info
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