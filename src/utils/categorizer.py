"""
Content categorization utilities for clipboard items.
"""


class ContentCategorizer:
    """
    Handles categorization of clipboard content into different types.
    """
    
    @staticmethod
    def categorize_content(content):
        """
        Categorizes content based on patterns and indicators.
        
        Args:
            content (str): The clipboard content to categorize
            
        Returns:
            str: The category label ('Code', 'LaTeX', 'Quotes', or 'Plaintext')
        """
        content = content.strip()
        
        # Check for code
        code_indicators = [
            "def ", "function", "class ", "{", "};", "import ", 
            "from ", "public ", "private ", "#include"
        ]
        for indicator in code_indicators:
            if indicator in content:
                return "Code"
        
        # Check for LaTeX
        latex_indicators = [
            "\\begin{", "\\end{", "\\frac", "\\sum", 
            "\\int", "\\lim", "\\mathbb"
        ]
        for indicator in latex_indicators:
            if indicator in content:
                return "LaTeX"
        
        # Check for quotes
        if ((content.startswith('"') and content.endswith('"')) or 
            (content.startswith("'") and content.endswith("'"))):
            return "Quotes"
        
        # Default to plaintext
        return "Plaintext" 