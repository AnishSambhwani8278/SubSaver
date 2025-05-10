import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import calendar
import numpy as np

class SubscriptionVisualizer:
    def __init__(self, theme='light'):
        self.theme = theme
        self._set_theme()
    
    def _set_theme(self):
        """Set visualization theme"""
        if self.theme == 'dark':
            plt.style.use('dark_background')
            self.colors = px.colors.qualitative.Dark24
            self.background_color = 'rgb(17, 17, 17)'
            self.text_color = 'white'
            self.grid_color = 'rgba(255, 255, 255, 0.1)'
        else:
            plt.style.use('default')
            self.colors = px.colors.qualitative.Set3
            self.background_color = 'white'
            self.text_color = 'black'
            self.grid_color = 'rgba(0, 0, 0, 0.1)'
    
    def monthly_spending_summary(self, subscriptions_df):
        """Create monthly subscription spending summary"""
        # Calculate total monthly spending
        total_monthly = subscriptions_df['monthly_cost'].sum()
        
        # Group by category
        by_category = subscriptions_df.groupby('category')['monthly_cost'].sum().reset_index()
        by_category = by_category.sort_values('monthly_cost', ascending=False)
        
        # Create pie chart
        fig = px.pie(
            by_category, 
            values='monthly_cost', 
            names='category',
            title=f'Monthly Subscription Spending: ${total_monthly:.2f}',
            color_discrete_sequence=self.colors
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            paper_bgcolor=self.background_color,
            plot_bgcolor=self.background_color,
            font_color=self.text_color
        )
        
        return fig
    
    def subscription_breakdown(self, subscriptions_df):
        """Create detailed subscription breakdown"""
        # Sort by monthly cost
        df = subscriptions_df.sort_values('monthly_cost', ascending=False)
        
        # Create bar chart
        fig = px.bar(
            df,
            y='description',
            x='monthly_cost',
            color='category',
            title='Subscription Cost Breakdown',
            labels={'description': 'Subscription', 'monthly_cost': 'Monthly Cost ($)'},
            color_discrete_sequence=self.colors
        )
        
        # Add cost labels
        fig.update_traces(texttemplate='$%{x:.2f}', textposition='outside')
        
        # Update layout
        fig.update_layout(
            xaxis_title='Monthly Cost ($)',
            yaxis_title='',
            yaxis=dict(
                categoryorder='total ascending',
                gridcolor=self.grid_color
            ),
            paper_bgcolor=self.background_color,
            plot_bgcolor=self.background_color,
            font_color=self.text_color,
            xaxis=dict(gridcolor=self.grid_color)
        )
        
        return fig
    
    def annual_projection(self, subscriptions_df):
        """Create annual spending projection"""
        # Calculate annual cost for each subscription
        df = subscriptions_df.copy()
        df['annual_cost'] = df['monthly_cost'] * 12
        
        # Total annual cost
        total_annual = df['annual_cost'].sum()
        
        # Create waterfall chart to show contribution of each subscription
        df = df.sort_values('annual_cost', ascending=False)
        
        # Prepare data for waterfall chart
        measure = ['relative'] * len(df) + ['total']
        x = list(df['description']) + ['Total Annual Cost']
        y = list(df['annual_cost']) + [total_annual]
        text = [f'${val:.2f}' for val in y]
        
        # Create waterfall chart
        fig = go.Figure(go.Waterfall(
            name='Annual Subscription Cost',
            orientation='v',
            measure=measure,
            x=x,
            y=y,
            text=text,
            textposition='outside',
            connector={'line': {'color': 'rgb(63, 63, 63)'}}
        ))
        
        fig.update_layout(
            title=f'Annual Subscription Cost: ${total_annual:.2f}',
            showlegend=False,
            paper_bgcolor=self.background_color,
            plot_bgcolor=self.background_color,
            font_color=self.text_color,
            xaxis=dict(gridcolor=self.grid_color),
            yaxis=dict(gridcolor=self.grid_color)
        )
        
        return fig
    
    def savings_opportunities(self, subscriptions_df):
        """Identify potential savings opportunities"""
        # Find duplicate service categories (e.g., multiple streaming services)
        category_counts = subscriptions_df.groupby('category').size().reset_index(name='count')
        duplicate_categories = category_counts[category_counts['count'] > 1]['category'].tolist()
        
        savings_opportunities = []
        
        # Check for duplicate categories
        if duplicate_categories:
            for category in duplicate_categories:
                category_subs = subscriptions_df[subscriptions_df['category'] == category]
                savings_opportunities.append({
                    'type': 'duplicate_category',
                    'category': category,
                    'subscriptions': category_subs['description'].tolist(),
                    'monthly_cost': category_subs['monthly_cost'].sum(),
                    'recommendation': f'Consider consolidating {category} subscriptions'
                })
        
        # Check for unused or infrequently used subscriptions (would require usage data)
        # This is a placeholder for future implementation
        
        # Check for annual vs monthly savings
        monthly_subs = subscriptions_df[subscriptions_df['frequency'] == 'monthly']
        for _, sub in monthly_subs.iterrows():
            # Typical annual discount is 15-20%
            potential_annual_savings = sub['monthly_cost'] * 12 * 0.15
            if potential_annual_savings > 20:  # Only suggest if savings > $20
                savings_opportunities.append({
                    'type': 'annual_discount',
                    'subscription': sub['description'],
                    'monthly_cost': sub['monthly_cost'],
                    'annual_savings': potential_annual_savings,
                    'recommendation': f'Switch to annual billing to save ~${potential_annual_savings:.2f}/year'
                })
        
        return savings_opportunities