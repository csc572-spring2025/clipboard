"""
Data management for clipboard history persistence using SQLite.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class ClipboardDataManager:
    """
    Handles loading and saving clipboard data to/from SQLite database.
    """
    
    def __init__(self, db_file="clipboard_data.db"):
        """
        Initialize the data manager with SQLite database.
        
        Args:
            db_file (str): Path to the SQLite database file
        """
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize the database and create tables if they don't exist."""
        with sqlite3.connect(self.db_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clipboard_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    type TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    time_formatted TEXT NOT NULL,
                    char_count INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_type ON clipboard_items(type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON clipboard_items(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_content ON clipboard_items(content)")
            
            conn.commit()
    
    def save_clipboard_item(self, item: Dict) -> bool:
        """
        Save a single clipboard item to the database.
        
        Args:
            item (dict): Clipboard item with keys: type, content, time, timestamp, chars
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.execute("""
                    INSERT INTO clipboard_items (content, type, timestamp, time_formatted, char_count)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    item["content"],
                    item["type"],
                    item["timestamp"],
                    item["time"],
                    len(item["content"])
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving clipboard item: {e}")
            return False
    
    def load_clipboard_data(self, limit: Optional[int] = None) -> List[Dict]:
        """
        Load clipboard history from database.
        
        Args:
            limit (int, optional): Maximum number of items to return
            
        Returns:
            list: List of clipboard items, ordered by most recent first
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row  # Enable column access by name
                
                query = """
                    SELECT content, type, timestamp, time_formatted, char_count
                    FROM clipboard_items 
                    ORDER BY created_at DESC
                """
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor = conn.execute(query)
                rows = cursor.fetchall()
                
                return [
                    {
                        "content": row["content"],
                        "type": row["type"],
                        "timestamp": row["timestamp"],
                        "time": row["time_formatted"],
                        "chars": f"{row['char_count']} characters"
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"Error loading clipboard data: {e}")
            return []
    
    def search_clipboard_items(self, search_term: str) -> List[Dict]:
        """
        Search clipboard items by content.
        
        Args:
            search_term (str): Term to search for in content
            
        Returns:
            list: List of matching clipboard items
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT content, type, timestamp, time_formatted, char_count
                    FROM clipboard_items 
                    WHERE content LIKE ?
                    ORDER BY created_at DESC
                """, (f"%{search_term}%",))
                
                rows = cursor.fetchall()
                
                return [
                    {
                        "content": row["content"],
                        "type": row["type"],
                        "timestamp": row["timestamp"],
                        "time": row["time_formatted"],
                        "chars": f"{row['char_count']} characters"
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"Error searching clipboard items: {e}")
            return []
    
    def filter_by_type(self, content_type: str) -> List[Dict]:
        """
        Filter clipboard items by type.
        
        Args:
            content_type (str): Type to filter by
            
        Returns:
            list: List of clipboard items of the specified type
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute("""
                    SELECT content, type, timestamp, time_formatted, char_count
                    FROM clipboard_items 
                    WHERE type = ?
                    ORDER BY created_at DESC
                """, (content_type,))
                
                rows = cursor.fetchall()
                
                return [
                    {
                        "content": row["content"],
                        "type": row["type"],
                        "timestamp": row["timestamp"],
                        "time": row["time_formatted"],
                        "chars": f"{row['char_count']} characters"
                    }
                    for row in rows
                ]
        except Exception as e:
            print(f"Error filtering clipboard items: {e}")
            return []
    
    def clear_all_items(self) -> bool:
        """
        Clear all clipboard items from the database.
        
        Returns:
            bool: True if cleared successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.execute("DELETE FROM clipboard_items")
                conn.commit()
                return True
        except Exception as e:
            print(f"Error clearing clipboard items: {e}")
            return False
    
    def get_item_count(self) -> int:
        """
        Get the total number of clipboard items.
        
        Returns:
            int: Number of items in the database
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM clipboard_items")
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error getting item count: {e}")
            return 0
    
    def save_clipboard_data(self, clipboard_items: List[Dict]):
        """
        Legacy method for compatibility - saves all items (used for bulk operations).
        
        Args:
            clipboard_items (list): List of clipboard items to save
        """
        # This could be used for bulk operations or migration
        try:
            with sqlite3.connect(self.db_file) as conn:
                # Clear existing data first
                conn.execute("DELETE FROM clipboard_items")
                
                # Insert all items
                for item in clipboard_items:
                    conn.execute("""
                        INSERT INTO clipboard_items (content, type, timestamp, time_formatted, char_count)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        item["content"],
                        item["type"],
                        item["timestamp"],
                        item["time"],
                        len(item["content"])
                    ))
                
                conn.commit()
        except Exception as e:
            print(f"Error saving clipboard data: {e}")