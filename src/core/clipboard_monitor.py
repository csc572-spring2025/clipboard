"""
Clipboard monitoring functionality.
"""

import os
import time
import threading
import datetime
import pyperclip

from ..utils.categorizer import ContentCategorizer


class ClipboardMonitor:
    """
    Monitors clipboard for new content and emits signals when content changes.
    """
    
    def __init__(self, signals):
        """
        Initialize the clipboard monitor.
        
        Args:
            signals: ClipboardSignals instance for emitting new content signals
        """
        self.signals = signals
        self.monitoring_active = False
        self.monitor_thread = None
        self.categorizer = ContentCategorizer()
    
    def start_monitoring(self):
        """Start clipboard monitoring in a separate thread."""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_clipboard)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop clipboard monitoring."""
        self.monitoring_active = False
    
    def _monitor_clipboard(self):
        """
        Internal method that runs in a separate thread to monitor clipboard changes.
        """
        # Create logs directory if it doesn't exist
        if not os.path.exists("clipboard_logs"):
            os.makedirs("clipboard_logs")
        
        previous_content = pyperclip.paste()
        seen_entries = {previous_content}
        
        while self.monitoring_active:
            try:
                current_content = pyperclip.paste()
                
                if (current_content != previous_content and 
                    current_content not in seen_entries):
                    
                    timestamp = datetime.datetime.now()
                    formatted_time = timestamp.strftime("%I:%M %p")
                    
                    content_type = self.categorizer.categorize_content(current_content)
                    
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