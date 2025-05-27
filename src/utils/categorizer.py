"""
Content categorization utilities for clipboard items.
"""

import re


class ContentCategorizer:
    """
    Handles categorization of clipboard content into different types.
    """
    
    @staticmethod
    def categorize_content(content):
        """
        Categorizes content based on regex patterns and indicators.
        
        Args:
            content (str): The clipboard content to categorize
            
        Returns:
            str: The category label ('Code and Math', 'URL', 'Plaintext', or 'Miscellaneous')
        """
        if not content or content is None:
            return "Miscellaneous"
        
        content = str(content).strip()
        
        # Check for empty content
        if re.match(r"^\s*$", content):
            return "Miscellaneous"
        
        # Check for URLs
        if re.search(r"https?://\S+|www\.\S+", content):
            return "URL"
        
        # Check for code patterns
        if re.search(r"(def |function |public |class |#include|import )", content):
            return "Code and Math"
        
        # Check for math/code expressions (mathematical operators without sentence endings)
        if re.search(r"[\d\w\s]*[\^=+\-*/\\]+[\d\w\s]*", content) and not re.search(r"[.!?]$", content):
            return "Code and Math"
        
        # Check if it's regular text (contains common sentence patterns)
        if re.search(r"[.!?]$", content) or len(content.split()) > 3:
            return "Plaintext"
        
        # Default to miscellaneous for everything else
        return "Miscellaneous" 