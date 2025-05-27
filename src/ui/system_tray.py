"""
System tray functionality for the clipboard manager.
"""

from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon


class ClipboardSystemTray:
    """
    Handles system tray icon and its context menu.
    """
    
    def __init__(self, parent_window):
        """
        Initialize the system tray.
        
        Args:
            parent_window: The main window instance
        """
        self.parent_window = parent_window
        self.tray_icon = None
        self.setup_system_tray()
    
    def setup_system_tray(self):
        """Initialize the system tray icon and its menu."""
        self.tray_icon = QSystemTrayIcon(self.parent_window)
        self.tray_icon.setIcon(QIcon.fromTheme("edit-copy"))
        
        tray_menu = QMenu()
        
        # Add show option
        show_action = QAction("Show", self.parent_window)
        show_action.triggered.connect(self.parent_window.show)
        
        # Add hide option
        hide_action = QAction("Hide", self.parent_window)
        hide_action.triggered.connect(self.parent_window.hide)
        
        # Add quit option
        quit_action = QAction("Quit", self.parent_window)
        quit_action.triggered.connect(self.parent_window.quit_application)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.activated.connect(self.tray_icon_activated)
    
    def tray_icon_activated(self, reason):
        """
        Handle tray icon activation events.
        
        Args:
            reason: The event that triggered the activation
        """
        if reason == QSystemTrayIcon.DoubleClick:
            if self.parent_window.isVisible():
                self.parent_window.hide()
            else:
                self.parent_window.show()
                self.parent_window.activateWindow() 