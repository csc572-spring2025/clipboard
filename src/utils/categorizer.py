# Import necessary libraries
import pandas as pd # for reading and writing CSV files
import re  # for using regular expressions to match patterns in text


class ContentCategorizer:
    """
    Handles categorization of clipboard content into different types.
    """

    def __init__(self, input_csv, output_csv, column_name=None): #Initialize the categorizer with input/output CSV file paths, and an optional column name to process.
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.column_name = column_name

    def categorize_text(self, text): #Categorize a single piece of text based on simple rules. Categories include: URL, Code/Math, Quote, Empty, and Plaintext.
        if pd.isna(text):
            return "Unknown"
        
        text = str(text).strip()

        if re.search(r"https?://\S+|www\.\S+", text):
            return "URL"
        elif re.search(r"(def |function |public |class |#include|import )", text):
            return "Code/Math"
        elif re.search(r"[\d\w\s]*[\^=+\-*/\\]+[\d\w\s]*", text) and not re.search(r"[.!?]$", text):
            return "Code/Math"
        elif len(text.split()) < 10 and re.match(r"^['\"].*['\"]$", text.strip()):
            return "Quote"
        elif re.match(r"^\s*$", text):
            return "Empty"
        else:
            return "Plaintext"

    def process(self): # Read the input CSV, apply categorization to each row, and write the results to the output CSV.
        try:
            df = pd.read_csv(self.input_csv)
        except FileNotFoundError:
            print(f"Error: File '{self.input_csv}' not found.")
            return

        # Determine which column to use
        if self.column_name and self.column_name in df.columns:
            col_to_use = self.column_name
        else:
            col_to_use = df.columns[0]
            print(f"Warning: Using first column '{col_to_use}' for categorization.")

        # Apply categorization
        df['category'] = df[col_to_use].apply(self.categorize_text)
        df.to_csv(self.output_csv, index=False)
        print(f"Categorized data written to {self.output_csv}")


# Run the categorizer
if __name__ == "__main__":
    input_csv = "/Users/student/CSC572/clipboard-new/src/sample_test.csv"
    output_csv = "categorized_output.csv"

    # Optional: specify column name (set to None to auto-detect)
    column_name = None

    categorizer = ContentCategorizer(input_csv, output_csv, column_name)
    categorizer.process()
