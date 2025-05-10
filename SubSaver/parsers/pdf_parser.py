import pdfplumber
import pandas as pd
import re
from utils.anonymizer import anonymize_data

class PDFParser:
    def __init__(self):
        self.data = None
        
    def parse(self, file_path):
        """Extract transaction data from PDF bank statements"""
        try:
            transactions = []
            
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    # Extract transaction data using regex patterns
                    # This is a simplified example - real implementation would be more robust
                    date_pattern = r'\d{1,2}/\d{1,2}/\d{2,4}'
                    amount_pattern = r'\$\d+\.\d{2}'
                    
                    # Process each line to extract transactions
                    lines = text.split('\n')
                    for line in lines:
                        # Skip header/footer lines
                        if self._is_transaction_line(line):
                            # Extract date, description, amount
                            date = self._extract_date(line, date_pattern)
                            amount = self._extract_amount(line, amount_pattern)
                            description = self._extract_description(line, date, amount)
                            
                            if date and amount and description:
                                transactions.append({
                                    'date': date,
                                    'description': description,
                                    'amount': amount
                                })
            
            # Convert to DataFrame
            self.data = pd.DataFrame(transactions)
            
            # Anonymize sensitive data
            self.data = anonymize_data(self.data)
            
            return self.data
        except Exception as e:
            raise Exception(f"Error parsing PDF file: {str(e)}")
    
    def _is_transaction_line(self, line):
        """Determine if a line contains transaction data"""
        # Implement logic to identify transaction lines
        # This will vary based on bank statement formats
        return bool(re.search(r'\d{1,2}/\d{1,2}', line) and re.search(r'\$\d+\.\d{2}', line))
    
    def _extract_date(self, line, pattern):
        """Extract transaction date from line"""
        match = re.search(pattern, line)
        return match.group(0) if match else None
    
    def _extract_amount(self, line, pattern):
        """Extract transaction amount from line"""
        match = re.search(pattern, line)
        if match:
            amount_str = match.group(0).replace('$', '')
            return float(amount_str)
        return None
    
    def _extract_description(self, line, date, amount):
        """Extract transaction description from line"""
        # Remove date and amount from line to get description
        description = line
        if date:
            description = description.replace(date, '')
        if amount:
            description = description.replace(f"${amount}", '')
        
        # Clean up extra spaces and special characters
        description = re.sub(r'\s+', ' ', description).strip()
        return description