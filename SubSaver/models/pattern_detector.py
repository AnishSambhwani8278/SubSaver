import pandas as pd
import numpy as np
from datetime import datetime
import re

class SubscriptionDetector:
    def __init__(self):
        # Common subscription keywords
        self.subscription_keywords = [
            'subscription', 'member', 'monthly', 'annual', 'recurring',
            'netflix', 'spotify', 'hulu', 'disney+', 'amazon prime',
            'apple', 'google', 'microsoft', 'adobe', 'dropbox', 'icloud',
            'hbo', 'youtube', 'paramount', 'peacock', 'crunchyroll',
            'gym', 'fitness', 'audible', 'patreon', 'onlyfans',
            'vpn', 'domain', 'hosting', 'website', 'cloud'
        ]
        
        # Common subscription categories
        self.categories = {
            'streaming': ['netflix', 'hulu', 'disney+', 'hbo', 'paramount+', 'peacock', 'youtube premium'],
            'music': ['spotify', 'apple music', 'tidal', 'pandora', 'deezer'],
            'cloud': ['dropbox', 'google one', 'icloud', 'onedrive', 'box'],
            'software': ['adobe', 'microsoft', 'autodesk', 'notion', 'canva pro'],
            'gaming': ['xbox', 'playstation', 'nintendo', 'steam', 'epic games'],
            'fitness': ['gym', 'peloton', 'fitness', 'strava', 'beachbody'],
            'news': ['nyt', 'wsj', 'washington post', 'economist', 'new yorker'],
            'other': []
        }
    
    def detect_subscriptions(self, transactions_df):
        """Detect recurring subscription charges in transaction data"""
        # Ensure date column is datetime
        transactions_df['date'] = pd.to_datetime(transactions_df['date'])
        
        # Find potential subscriptions based on keywords
        potential_subs = self._find_keyword_matches(transactions_df)
        
        # Find recurring patterns (same amount, regular intervals)
        recurring_patterns = self._find_recurring_patterns(transactions_df)
        
        # Combine both approaches
        subscriptions = pd.concat([potential_subs, recurring_patterns]).drop_duplicates()
        
        # Categorize subscriptions
        subscriptions['category'] = subscriptions['description'].apply(self._categorize_subscription)
        
        # Calculate monthly cost for each subscription
        subscriptions = self._calculate_monthly_cost(subscriptions)
        
        return subscriptions
    
    def _find_keyword_matches(self, df):
        """Find transactions matching subscription keywords"""
        mask = df['description'].str.lower().apply(
            lambda x: any(keyword in x.lower() for keyword in self.subscription_keywords)
        )
        return df[mask].copy()
    
    def _find_recurring_patterns(self, df):
        """Find transactions that occur at regular intervals with the same amount"""
        # Group by description and amount
        grouped = df.groupby(['description', 'amount'])
        
        recurring = []
        for (desc, amount), group in grouped:
            if len(group) >= 2:  # At least 2 occurrences
                # Sort by date
                sorted_group = group.sort_values('date')
                
                # Calculate days between transactions
                dates = sorted_group['date'].tolist()
                intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                
                # Check if intervals are consistent (within 5 days tolerance)
                if len(intervals) >= 1:
                    avg_interval = sum(intervals) / len(intervals)
                    is_consistent = all(abs(interval - avg_interval) <= 5 for interval in intervals)
                    
                    # Monthly subscriptions (25-35 days) or annual (350-380 days)
                    is_subscription_period = (25 <= avg_interval <= 35) or (350 <= avg_interval <= 380)
                    
                    if is_consistent and is_subscription_period:
                        recurring.append(sorted_group.iloc[0])
        
        return pd.DataFrame(recurring) if recurring else pd.DataFrame(columns=df.columns)
    
    def _categorize_subscription(self, description):
        """Categorize subscription based on description"""
        description = description.lower()
        
        for category, keywords in self.categories.items():
            if any(keyword in description for keyword in keywords):
                return category
        
        return 'other'
    
    def _calculate_monthly_cost(self, subscriptions_df):
        """Calculate estimated monthly cost for each subscription"""
        # Copy to avoid modifying original
        df = subscriptions_df.copy()
        
        # Group by description to find frequency
        grouped = df.groupby('description')
        
        results = []
        for desc, group in grouped:
            if len(group) >= 2:
                # Sort by date
                sorted_group = group.sort_values('date')
                
                # Calculate average interval in days
                dates = sorted_group['date'].tolist()
                if len(dates) >= 2:
                    intervals = [(dates[i+1] - dates[i]).days for i in range(len(dates)-1)]
                    avg_interval = sum(intervals) / len(intervals)
                    
                    # Calculate monthly cost based on interval
                    amount = sorted_group['amount'].iloc[-1]  # Most recent charge
                    
                    if 25 <= avg_interval <= 35:  # Monthly
                        monthly_cost = amount
                        frequency = 'monthly'
                    elif 350 <= avg_interval <= 380:  # Annual
                        monthly_cost = amount / 12
                        frequency = 'annual'
                    else:  # Other intervals
                        monthly_cost = amount * (30 / avg_interval)
                        frequency = f'every {round(avg_interval)} days'
                    
                    # Add to results
                    row = sorted_group.iloc[-1].copy()  # Use most recent transaction
                    row['monthly_cost'] = monthly_cost
                    row['frequency'] = frequency
                    row['last_charge'] = sorted_group['date'].max()
                    results.append(row)
                else:
                    # Single occurrence - assume monthly
                    row = group.iloc[0].copy()
                    row['monthly_cost'] = row['amount']
                    row['frequency'] = 'unknown'
                    row['last_charge'] = row['date']
                    results.append(row)
            else:
                # Single occurrence - assume monthly
                row = group.iloc[0].copy()
                row['monthly_cost'] = row['amount']
                row['frequency'] = 'unknown'
                row['last_charge'] = row['date']
                results.append(row)
        
        return pd.DataFrame(results)