import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

from src.google_sheets import fetch_data, get_data_range
from src.data_processor import clean_data, calculate_sleep_duration, calculate_rolling_averages
from src.visualization import create_dashboard_charts
from src.config import DATE_COL, WAKE_UP_COL, SLEEP_COL, WEIGHT_COL, DEFAULT_DATE_RANGE

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
creds_exist = os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'credentials', 'credentials.json'))

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
        
        # Create tabs for different visualizations
        tabs = st.tabs(["Sleep", "Weight", "Overview", "Data"])
        
        # Generate charts
        charts = create_dashboard_charts(filtered_data)
        
        # Sleep tab
        with tabs[0]:
            st.subheader("Sleep Patterns")
            col1, col2 = st.columns(2)
            
            if 'sleep_pattern' in charts and charts['sleep_pattern'] is not None:
                with col1:
                    st.plotly_chart(charts['sleep_pattern'], use_container_width=True)
            
            if 'sleep_duration' in charts and charts['sleep_duration'] is not None:
                with col2:
                    st.plotly_chart(charts['sleep_duration'], use_container_width=True)
            
            if 'sleep_duration_trend' in charts and charts['sleep_duration_trend'] is not None:
                st.plotly_chart(charts['sleep_duration_trend'], use_container_width=True)
            
            # Sleep stats
            if 'Sleep Duration (hours)' in filtered_data.columns:
                st.subheader("Sleep Statistics")
                avg_sleep = filtered_data['Sleep Duration (hours)'].mean()
                max_sleep = filtered_data['Sleep Duration (hours)'].max()
                min_sleep = filtered_data['Sleep Duration (hours)'].min()
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Average Sleep", f"{avg_sleep:.2f} hours")
                col2.metric("Max Sleep", f"{max_sleep:.2f} hours")
                col3.metric("Min Sleep", f"{min_sleep:.2f} hours")
        
        # Weight tab
        with tabs[1]:
            st.subheader("Weight Tracking")
            
            if 'weight_trend' in charts and charts['weight_trend'] is not None:
                st.plotly_chart(charts['weight_trend'], use_container_width=True)
                
                # Weight stats
                if WEIGHT_COL in filtered_data.columns:
                    st.subheader("Weight Statistics")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    current_weight = filtered_data[WEIGHT_COL].iloc[-1]
                    avg_weight = filtered_data[WEIGHT_COL].mean()
                    min_weight = filtered_data[WEIGHT_COL].min()
                    max_weight = filtered_data[WEIGHT_COL].max()
                    
                    col1.metric("Current Weight", f"{current_weight:.1f}")
                    col2.metric("Average Weight", f"{avg_weight:.1f}")
                    col3.metric("Min Weight", f"{min_weight:.1f}")
                    col4.metric("Max Weight", f"{max_weight:.1f}")
                    
                    # Weight change
                    if len(filtered_data) > 1:
                        first_weight = filtered_data[WEIGHT_COL].iloc[0]
                        weight_change = current_weight - first_weight
                        st.metric(
                            "Weight Change Over Period", 
                            f"{weight_change:.1f}", 
                            delta=f"{weight_change:.1f}"
                        )
        
        # Overview tab - general stats and additional metrics
        with tabs[2]:
            st.subheader("Daily Routine Overview")
            
            # Get stats for wake-up consistency
            if WAKE_UP_COL in filtered_data.columns:
                wake_times = filtered_data[WAKE_UP_COL].dropna()
                if not wake_times.empty:
                    # Convert time objects to minutes since midnight for calculation
                    wake_minutes = wake_times.apply(lambda x: x.hour * 60 + x.minute)
                    avg_wake_time = datetime.min + timedelta(minutes=int(wake_minutes.mean()))
                    
                    st.metric("Average Wake-up Time", avg_wake_time.strftime("%H:%M"))
            
            # For other metrics, we can dynamically display them
            other_metrics = [col for col in filtered_data.columns 
                           if col not in [DATE_COL, WAKE_UP_COL, SLEEP_COL, WEIGHT_COL, 'Sleep Duration (hours)'] 
                           and pd.api.types.is_numeric_dtype(filtered_data[col])]
            
            if other_metrics:
                st.subheader("Other Metrics")
                for i in range(0, len(other_metrics), 3):  # Show 3 metrics per row
                    cols = st.columns(3)
                    for j, col in enumerate(other_metrics[i:i+3]):
                        if j < len(cols):
                            avg_val = filtered_data[col].mean()
                            cols[j].metric(f"Average {col}", f"{avg_val:.2f}")
        
        # Data tab - show the raw data
        with tabs[3]:
            st.subheader("Raw Data")
            st.dataframe(filtered_data)
            
            # Option to download the data
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="Download Data as CSV",
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
