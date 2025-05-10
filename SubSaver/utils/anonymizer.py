import pandas as pd
import re
import hashlib

def anonymize_data(df):
    """Anonymize sensitive data in transaction dataframe"""
    # Create a copy to avoid modifying the original
    df_anon = df.copy()
    
    # Anonymize account numbers
    if 'account' in df_anon.columns:
        df_anon['account'] = df_anon['account'].apply(anonymize_account_number)
    
    # Anonymize card numbers in description
    if 'description' in df_anon.columns:
        df_anon['description'] = df_anon['description'].apply(anonymize_card_numbers)
    
    # Remove any other PII from description
    if 'description' in df_anon.columns:
        df_anon['description'] = df_anon['description'].apply(remove_pii)
    
    return df_anon

def anonymize_account_number(account_num):
    """Replace account number with hashed version"""
    if not account_num or pd.isna(account_num):
        return account_num
    
    # Convert to string
    account_str = str(account_num)
    
    # Keep only last 4 digits if it's a typical account number
    if len(account_str) >= 4:
        return 'XXXX-' + account_str[-4:]
    else:
        # Hash if it's too short
        return hashlib.sha256(account_str.encode()).hexdigest()[:8]

def anonymize_card_numbers(text):
    """Replace credit card numbers with masked version"""
    if not text or pd.isna(text):
        return text
    
    # Pattern for credit card numbers (simplified)
    cc_pattern = r'\b(?:\d[ -]*?){13,16}\b'
    
    def mask_cc(match):
        cc = match.group(0)
        # Remove spaces and dashes
        cc_clean = re.sub(r'[ -]', '', cc)
        # Keep only last 4 digits
        return f"XXXX-XXXX-XXXX-{cc_clean[-4:]}"
    
    return re.sub(cc_pattern, mask_cc, text)

def remove_pii(text):
    """Remove other personally identifiable information"""
    if not text or pd.isna(text):
        return text
    
    # Remove email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)
    
    # Remove phone numbers (various formats)
    text = re.sub(r'\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b', '[PHONE]', text)
    
    # Remove SSN
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', text)
    
    return text