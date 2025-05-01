""" The main app runner file"""
import os
import sys

# Add parent directory to path if running as standalone script
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import streamlit as st

from src.config import DATE_COL, DEFAULT_DATE_RANGE, WAKE_UP_COL, WEIGHT_COL
from src.data_processor import calculate_rolling_averages, calculate_sleep_duration, clean_data
from src.google_sheets import fetch_data, get_data_range
from src.visualization import create_dashboard_charts

# Page configuration
st.set_page_config(page_title="Daily Routine Dashboard", page_icon="📊", layout="wide")

# Title and description
st.title("Daily Routine Dashboard")
st.markdown(
    """This dashboard visualizes your daily routine data from Google Sheets to help you track your habits and health metrics.
    Connect your Google Sheet to see insights about your sleep, weight, and other daily activities."""
)

# Sidebar for controls
st.sidebar.header("Controls")

# Function to load and process data
def load_data():
    with st.spinner("Fetching data from Google Sheets..."):
        data = fetch_data()
        if data.empty:
            st.error("No data found or error connecting to Google Sheets. Please check your configuration.")
            return None
        
        # Process the data
        data = clean_data(data)
        data = calculate_sleep_duration(data)
        
        # Calculate rolling averages for numeric columns
        numeric_columns = data.select_dtypes(include=['number']).columns.tolist()
        data = calculate_rolling_averages(data, numeric_columns)
        
        return data

# Check if credentials exist
creds_exist = os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                         'credentials', 'credentials.json'))

if not creds_exist:
    st.warning(
        "Google Sheets API credentials not found. Please follow the setup instructions in the README.md file."
    )
    st.info(
        """To set up your Google Sheets connection:
        1. Create a Google Cloud Project
        2. Enable the Google Sheets API
        3. Create OAuth 2.0 credentials
        4. Download the credentials JSON file
        5. Save it as 'credentials/credentials.json' in the project directory
        """
    )
else:
    # Load the data
    data = load_data()
    
    if data is not None and not data.empty:
        # Date range selector
        date_range = st.sidebar.slider(
            "Date Range (days)",
            min_value=7,
            max_value=365,
            value=DEFAULT_DATE_RANGE,
            step=1,
            help="Select the number of days to display in the charts"
        )
        
        # Filter data by date range
        filtered_data = get_data_range(data, days=date_range)
        
        # Display basic stats
        st.sidebar.subheader("Data Summary")
        st.sidebar.info(f"Data range: {filtered_data[DATE_COL].min().strftime('%Y-%m-%d')} to {filtered_data[DATE_COL].max().strftime('%Y-%m-%d')}")
        st.sidebar.info(f"Total days recorded: {len(filtered_data)}")
        
        # Generate charts
        charts = create_dashboard_charts(filtered_data)
        
        # Sleep section
        st.header("Sleep Patterns")
        
        # Create a row for the wake-up pattern chart
        if 'wake_up_pattern' in charts and charts['wake_up_pattern'] is not None:
            st.subheader("Wake-up Time Trends")
            st.plotly_chart(charts['wake_up_pattern'], use_container_width=True)
        
        # Create a row for the sleep pattern chart
        if 'sleep_pattern' in charts and charts['sleep_pattern'] is not None:
            st.subheader("Sleep Time Trends")
            st.plotly_chart(charts['sleep_pattern'], use_container_width=True)
            
        # Create a row for sleep duration
        if 'sleep_duration' in charts and charts['sleep_duration'] is not None:
            st.subheader("Sleep Duration")
            st.plotly_chart(charts['sleep_duration'], use_container_width=True)
        
        # Display sleep stats
        if 'sleep_stats' in charts and charts['sleep_stats'] is not None:
            st.write(charts['sleep_stats'])
        
        # Weight section
        st.header("Weight Tracking")
        
        if 'weight_trend' in charts and charts['weight_trend'] is not None:
            st.plotly_chart(charts['weight_trend'], use_container_width=True)
        
        st.subheader("Weight Statistics")
        if filtered_data is not None and WEIGHT_COL in filtered_data.columns:
            # Only include rows where weight is not null
            weight_df = filtered_data[filtered_data[WEIGHT_COL].notna()]
            
            if not weight_df.empty:
                current_weight = weight_df.iloc[-1][WEIGHT_COL]
                avg_weight = weight_df[WEIGHT_COL].mean()
                min_weight = weight_df[WEIGHT_COL].min()
                max_weight = weight_df[WEIGHT_COL].max()
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Current Weight", f"{current_weight}")
                with col2:
                    st.metric("Average Weight", f"{avg_weight:.1f}")
                with col3:
                    st.metric("Min Weight", f"{min_weight}")
                with col4:
                    st.metric("Max Weight", f"{max_weight}")
                
                # Calculate weight change over the period
                first_weight = weight_df.iloc[0][WEIGHT_COL]
                weight_change = current_weight - first_weight
                
                st.metric("Weight Change Over Period", f"{weight_change}")
        
        # Overview section
        st.header("Daily Routine Overview")
        
        # Get stats for wake-up consistency
        if WAKE_UP_COL in filtered_data.columns:
            try:
                # Convert wake-up times to datetime and extract hour
                wake_times = pd.to_datetime(filtered_data[WAKE_UP_COL], 
                                           format='%I:%M %p', 
                                           errors='coerce')
                wake_times = wake_times.dt.hour + wake_times.dt.minute / 60
                
                # Calculate consistency (standard deviation of wake-up times)
                wake_consistency = wake_times.std()
                
                st.metric(
                    "Wake-up Consistency",
                    f"{wake_consistency:.2f} hours",
                    help="Lower values indicate more consistent wake-up times"
                )
                
                # Most common wake-up time
                most_common_wake = filtered_data[WAKE_UP_COL].mode()[0] \
                    if not filtered_data[WAKE_UP_COL].mode().empty else "N/A"
                st.metric("Most Common Wake-up Time", most_common_wake)
                
            except Exception as e:
                st.error(f"Error calculating wake-up stats: {e}")
        
        # Data section
        st.header("Raw Data")
        st.dataframe(filtered_data)
        
        # Option to download data as CSV
        if not filtered_data.empty:
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name="daily_routine_data.csv",
                mime="text/csv",
            )
    else:
        st.info("No data available. Please check your Google Sheets connection.")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    """This dashboard helps you visualize and track your daily routine data from Google Sheets. 
    It provides insights about your sleep patterns, weight trends, and other health metrics."""
)

def main():
    # This function serves as an entry point for the package
    # The actual app is run by streamlit
    print("To run the dashboard, use: streamlit run src/app.py")
    
if __name__ == "__main__":
    # When run directly, the Streamlit command will take over
    pass
