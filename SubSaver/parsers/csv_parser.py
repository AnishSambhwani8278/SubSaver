import pandas as pd
import re
from utils.anonymizer import anonymize_data

class CSVParser:
    def __init__(self):
        self.data = None
        
    def parse(self, file_path):
        """Parse a CSV bank statement file"""
        try:
            # Read CSV file
            self.data = pd.read_csv(file_path)
            
            # Detect common bank statement columns
            self._detect_columns()
            
            # Anonymize sensitive data
            self.data = anonymize_data(self.data)
            
            return self.data
        except Exception as e:
            raise Exception(f"Error parsing CSV file: {str(e)}")
    
    def _detect_columns(self):
        """Detect and standardize column names for different bank formats"""
        # Map common column names to standard names
        column_mapping = {
            # Date columns
            'date': ['date', 'transaction date', 'trans date', 'posted date'],
            # Description columns
            'description': ['description', 'transaction', 'details', 'merchant', 'name'],
            # Amount columns
            'amount': ['amount', 'transaction amount', 'debit', 'credit']
        }
        
        # Standardize column names
        new_columns = {}
        for col in self.data.columns:
            col_lower = col.lower()
            for standard, variations in column_mapping.items():
                if any(var in col_lower for var in variations):
                    new_columns[col] = standard
                    break
        
        # Rename detected columns
        if new_columns:
            self.data = self.data.rename(columns=new_columns)