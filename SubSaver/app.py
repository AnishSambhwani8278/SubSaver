import streamlit as st
import pandas as pd
import numpy as np
import os
import tempfile
from datetime import datetime

# Import project modules
from parsers.csv_parser import CSVParser
from parsers.pdf_parser import PDFParser
from models.pattern_detector import SubscriptionDetector
from utils.visualizer import SubscriptionVisualizer
from services.cancellation import CancellationService

# Set page configuration
st.set_page_config(
    page_title="SubSaver - Smart Subscription Manager",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'subscriptions' not in st.session_state:
    st.session_state.subscriptions = None
if 'transactions' not in st.session_state:
    st.session_state.transactions = None
if 'flagged_subscriptions' not in st.session_state:
    st.session_state.flagged_subscriptions = []
if 'canceled_subscriptions' not in st.session_state:
    st.session_state.canceled_subscriptions = []

# App title and description
st.title("SubSaver - Smart Subscription Manager")
st.markdown("""
💰 **Identify, track, and manage your recurring subscriptions to save money!**

Upload your bank or credit card statement to automatically detect subscriptions.
All processing happens locally - your financial data never leaves your computer.
""")

# Sidebar for file upload and settings
with st.sidebar:
    st.header("Upload Statement")
    uploaded_file = st.file_uploader("Choose a bank/credit card statement", type=['csv', 'pdf'])
    
    if uploaded_file is not None:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Parse file based on type
        try:
            if uploaded_file.name.endswith('.csv'):
                parser = CSVParser()
                st.session_state.transactions = parser.parse(tmp_file_path)
            else:  # PDF
                parser = PDFParser()
                st.session_state.transactions = parser.parse(tmp_file_path)
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
            # Detect subscriptions
            detector = SubscriptionDetector()
            st.session_state.subscriptions = detector.detect_subscriptions(st.session_state.transactions)
            
            st.success(f"Found {len(st.session_state.subscriptions)} potential subscriptions!")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    # Settings
    st.header("Settings")
    theme = st.selectbox("Theme", ["dark", "light"], index=0)

# Main content area
if st.session_state.subscriptions is not None and not st.session_state.subscriptions.empty:
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Subscriptions", "Savings", "Cancellation"])
    
    # Initialize visualizer
    visualizer = SubscriptionVisualizer(theme=theme)
    
    # Dashboard tab
    with tab1:
        st.header("Subscription Dashboard")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        monthly_total = st.session_state.subscriptions['monthly_cost'].sum()
        annual_total = monthly_total * 12
        
        with col1:
            st.metric("Monthly Spending", f"${monthly_total:.2f}")
        
        with col2:
            st.metric("Annual Spending", f"${annual_total:.2f}")
        
        with col3:
            st.metric("Active Subscriptions", len(st.session_state.subscriptions))
        
        # Monthly spending by category
        st.subheader("Monthly Spending by Category")
        monthly_chart = visualizer.monthly_spending_summary(st.session_state.subscriptions)
        st.plotly_chart(monthly_chart, use_container_width=True)
        
        # Subscription breakdown
        st.subheader("Subscription Breakdown")
        breakdown_chart = visualizer.subscription_breakdown(st.session_state.subscriptions)
        st.plotly_chart(breakdown_chart, use_container_width=True)
    
    # Subscriptions tab
    with tab2:
        st.header("Your Subscriptions")
        
        # Display subscriptions table
        display_df = st.session_state.subscriptions[['description', 'amount', 'frequency', 'monthly_cost', 'category', 'last_charge']].copy()
        display_df = display_df.rename(columns={
            'description': 'Subscription',
            'amount': 'Last Charge',
            'frequency': 'Billing Cycle',
            'monthly_cost': 'Monthly Cost',
            'category': 'Category',
            'last_charge': 'Last Charged'
        })
        
        # Format currency columns
        display_df['Last Charge'] = display_df['Last Charge'].apply(lambda x: f"${x:.2f}")
        display_df['Monthly Cost'] = display_df['Monthly Cost'].apply(lambda x: f"${x:.2f}")
        
        # Capitalize category and billing cycle
        display_df['Category'] = display_df['Category'].str.capitalize()
        display_df['Billing Cycle'] = display_df['Billing Cycle'].str.capitalize()
        
        st.dataframe(display_df, use_container_width=True)
        
        # Export options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Export to CSV"):
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"subscriptions_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("Export to Excel"):
                # This would require additional libraries like openpyxl
                st.info("Excel export functionality coming soon!")
    
    # Savings tab
    with tab3:
        st.header("Savings Opportunities")
        
        # Get savings opportunities
        savings_opps = visualizer.savings_opportunities(st.session_state.subscriptions)
        
        if savings_opps:
            total_potential_savings = sum([opp.get('annual_savings', opp.get('monthly_cost', 0) * 12) for opp in savings_opps])
            
            st.metric("Potential Annual Savings", f"${total_potential_savings:.2f}")
            
            # Display savings opportunities
            st.subheader("Recommended Actions")
            for i, opp in enumerate(savings_opps):
                with st.expander(f"{i+1}. {opp['recommendation']}"):
                    if opp['type'] == 'duplicate_category':
                        st.write(f"**Category:** {opp['category'].capitalize()}")
                        st.write(f"**Subscriptions:** {', '.join(opp['subscriptions'])}")
                        st.write(f"**Monthly Cost:** ${opp['monthly_cost']:.2f}")
                        st.write(f"**Annual Cost:** ${opp['monthly_cost'] * 12:.2f}")
                    elif opp['type'] == 'annual_discount':
                        st.write(f"**Subscription:** {opp['subscription']}")
                        st.write(f"**Current Monthly Cost:** ${opp['monthly_cost']:.2f}")
                        st.write(f"**Annual Savings:** ${opp['annual_savings']:.2f}")
                    
                    # Flag subscription for review
                    if st.button(f"Flag for Review", key=f"flag_{i}"):
                        if opp not in st.session_state.flagged_subscriptions:
                            st.session_state.flagged_subscriptions.append(opp)
                            st.success("Added to your review list!")
        else:
            st.info("No savings opportunities identified. Your subscription management is already optimized!")
    
    # Cancellation tab
    with tab4:
        st.header("Subscription Management")
        
        # Initialize cancellation service
        cancellation_service = CancellationService()
        
        # Tabs for different actions
        cancel_tab, templates_tab, tracking_tab = st.tabs(["Cancel Subscription", "Email Templates", "Cancellation Tracking"])
        
        # Cancel subscription tab
        with cancel_tab:
            st.subheader("Cancel a Subscription")
            
            # Select subscription to cancel
            if not st.session_state.subscriptions.empty:
                subscription_names = st.session_state.subscriptions['description'].tolist()
                selected_sub = st.selectbox("Select subscription to cancel", subscription_names)
                
                # Get subscription details
                sub_details = st.session_state.subscriptions[st.session_state.subscriptions['description'] == selected_sub].iloc[0]
                
                # Display details
                st.write(f"**Category:** {sub_details['category'].capitalize()}")
                st.write(f"**Monthly Cost:** ${sub_details['monthly_cost']:.2f}")
                st.write(f"**Annual Cost:** ${sub_details['monthly_cost'] * 12:.2f}")
                
                # Cancellation options
                st.subheader("Cancellation Options")
                
                # Get cancellation methods
                cancellation_methods = cancellation_service.get_cancellation_methods(selected_sub)
                
                if cancellation_methods:
                    method = st.radio("How would you like to cancel?", cancellation_methods)
                    
                    if method == "Email":
                        email_template = cancellation_service.generate_email_template(selected_sub)
                        st.text_area("Email Template", email_template, height=200)
                        st.button("Copy to Clipboard")
                    
                    elif method == "Phone":
                        phone_script = cancellation_service.generate_phone_script(selected_sub)
                        st.text_area("Phone Script", phone_script, height=200)
                        st.button("Copy to Clipboard")
                    
                    elif method == "Online Form":
                        cancellation_url = cancellation_service.get_cancellation_url(selected_sub)
                        st.write(f"**Cancellation URL:** [Click here to cancel]({cancellation_url})")
                    
                    # Mark as canceled
                    if st.button("Mark as Canceled"):
                        canceled_sub = {
                            'description': selected_sub,
                            'monthly_cost': sub_details['monthly_cost'],
                            'annual_savings': sub_details['monthly_cost'] * 12,
                            'canceled_date': datetime.now().strftime('%Y-%m-%d'),
                            'method': method
                        }
                        
                        st.session_state.canceled_subscriptions.append(canceled_sub)
                        st.success(f"🎉 {selected_sub} marked as canceled! You'll save ${sub_details['monthly_cost'] * 12:.2f} per year.")
                else:
                    st.info("No specific cancellation information available for this subscription.")
            else:
                st.info("No subscriptions available to cancel.")
        
        # Email templates tab
        with templates_tab:
            st.subheader("Cancellation Email Templates")
            
            template_categories = ["Standard Cancellation", "Request Refund", "Pause Subscription", "Negotiate Better Rate"]
            selected_template = st.selectbox("Select template type", template_categories)
            
            template = cancellation_service.get_template(selected_template)
            st.text_area("Template", template, height=300)
            
            if st.button("Copy Template"):
                st.success("Template copied to clipboard!")
        
        # Tracking tab
        with tracking_tab:
            st.subheader("Cancellation Tracking")
            
            if st.session_state.canceled_subscriptions:
                # Calculate total savings
                total_savings = sum([sub['annual_savings'] for sub in st.session_state.canceled_subscriptions])
                st.metric("Total Annual Savings", f"${total_savings:.2f}")
                
                # Display canceled subscriptions
                canceled_data = []
                for sub in st.session_state.canceled_subscriptions:
                    canceled_data.append({
                        "Subscription": sub['description'],
                        "Monthly Savings": f"${sub['annual_savings']/12:.2f}",
                        "Annual Savings": f"${sub['annual_savings']:.2f}",
                        "Canceled Date": sub['canceled_date'],
                        "Method": sub['method']
                    })
                
                canceled_df = pd.DataFrame(canceled_data)
                st.dataframe(canceled_df, use_container_width=True)
                
                # Export options
                if st.button("Export Cancellation Report"):
                    csv = canceled_df.to_csv(index=False)
                    st.download_button(
                        label="Download Report",
                        data=csv,
                        file_name=f"cancellation_report_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            else:
                st.info("You haven't canceled any subscriptions yet.")

else:
    # Show instructions when no data is loaded
    st.info("👈 Please upload a bank or credit card statement to get started.")
    
    # Sample data option for demo
    if st.button("Load Sample Data"):
        # Create sample transaction data
        sample_data = {
            'date': pd.date_range(start='2023-01-01', periods=50, freq='D'),
            'description': [
                'NETFLIX.COM', 'GROCERY STORE', 'GAS STATION', 'SPOTIFY USA',
                'RESTAURANT', 'AMAZON PRIME', 'COFFEE SHOP', 'HULU.COM',
                'GROCERY STORE', 'NETFLIX.COM', 'GYM MEMBERSHIP', 'UTILITY BILL',
                'SPOTIFY USA', 'RESTAURANT', 'GAS STATION', 'COFFEE SHOP',
                'AMAZON PRIME', 'GROCERY STORE', 'HULU.COM', 'RESTAURANT',
                'NETFLIX.COM', 'GAS STATION', 'COFFEE SHOP', 'GYM MEMBERSHIP',
                'SPOTIFY USA', 'GROCERY STORE', 'UTILITY BILL', 'RESTAURANT',
                'HULU.COM', 'COFFEE SHOP', 'AMAZON PRIME', 'GAS STATION',
                'GROCERY STORE', 'NETFLIX.COM', 'RESTAURANT', 'COFFEE SHOP',
                'SPOTIFY USA', 'GYM MEMBERSHIP', 'GROCERY STORE', 'GAS STATION',
                'HULU.COM', 'RESTAURANT', 'COFFEE SHOP', 'AMAZON PRIME',
                'GROCERY STORE', 'NETFLIX.COM', 'UTILITY BILL', 'GAS STATION',
                'SPOTIFY USA', 'RESTAURANT'
            ],
            'amount': np.random.uniform(5, 200, size=50)
        }
        
        # Create DataFrame
        st.session_state.transactions = pd.DataFrame(sample_data)
        
        # Detect subscriptions
        detector = SubscriptionDetector()
        st.session_state.subscriptions = detector.detect_subscriptions(st.session_state.transactions)
        
        st.success(f"Loaded sample data with {len(st.session_state.subscriptions)} subscriptions!")
        st.rerun()