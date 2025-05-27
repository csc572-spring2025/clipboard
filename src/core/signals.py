"""
Signal handling for clipboard events.
"""

from PyQt5.QtCore import pyqtSignal, QObject


class ClipboardSignals(QObject):
    """
    Signal class for clipboard events.
    When emitted, this signal sends clipboard item info as a dictionary.
    """
    new_clipboard_content = pyqtSignal(dict) 