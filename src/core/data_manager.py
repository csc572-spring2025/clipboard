"""
Data management for clipboard history persistence.
"""

import json
import os


class ClipboardDataManager:
    """
    Handles loading and saving clipboard data to/from JSON files.
    """
    
    def __init__(self, data_file="clipboard_data.json"):
        """
        Initialize the data manager.
        
        Args:
            data_file (str): Path to the JSON file for storing clipboard data
        """
        self.data_file = data_file
    
    def load_clipboard_data(self):
        """
        Load clipboard history from JSON file.
        
        Returns:
            list: List of clipboard items, empty list if file doesn't exist or error occurs
        """
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            print(f"Error loading clipboard data: {e}")
            return []
    
    def save_clipboard_data(self, clipboard_items):
        """
        Save clipboard items to JSON file.
        
        Args:
            clipboard_items (list): List of clipboard items to save
        """
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(clipboard_items, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving clipboard data: {e}") 