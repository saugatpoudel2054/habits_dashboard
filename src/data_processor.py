import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.config import DATE_COL, WAKE_UP_COL, SLEEP_COL, WEIGHT_COL


def clean_data(df):
    """Clean and preprocess the data."""
    if df.empty:
        return df
    
    # Make a copy to avoid modifying the original dataframe
    df = df.copy()
    
    # Store original string values for consistent display
    if WAKE_UP_COL in df.columns:
        # Convert time strings to datetime.time objects
        df['wake_up_time'] = pd.to_datetime(df[WAKE_UP_COL], format='%I:%M %p', errors='coerce').dt.time
        # Keep original string format for display consistency
        df[WAKE_UP_COL] = df[WAKE_UP_COL]
    
    if SLEEP_COL in df.columns:
        # For sleep time, convert to datetime.time objects
        df['sleep_time'] = pd.to_datetime(df[SLEEP_COL], format='%I:%M %p', errors='coerce').dt.time
        # Keep original string format for display consistency
        df[SLEEP_COL] = df[SLEEP_COL]
    
    # Convert weight to numeric
    if WEIGHT_COL in df.columns:
        df[WEIGHT_COL] = pd.to_numeric(df[WEIGHT_COL], errors='coerce')
    
    return df


def calculate_sleep_duration(df):
    """Calculate sleep duration between previous day's sleep time and current day's wake up time."""
    if df.empty or 'sleep_time' not in df.columns or 'wake_up_time' not in df.columns:
        return df
    
    df = df.copy()
    
    # Make sure data is sorted by date
    if DATE_COL in df.columns:
        df = df.sort_values(by=DATE_COL)
    
    # Create a shifted column with previous day's sleep time
    df['prev_day_sleep_time'] = df['sleep_time'].shift(1)
    
    # Function to calculate hours between previous day's sleep and current day's wake up
    def calc_duration(prev_sleep, wake):
        if pd.isna(prev_sleep) or pd.isna(wake):
            return np.nan
        
        # Create datetime objects for calculation
        sleep_dt = datetime.combine(datetime.today().date(), prev_sleep)
        wake_dt = datetime.combine(datetime.today().date(), wake)
        
        # If wake time is earlier than sleep time (should be rare in this approach),
        # we still handle it by adding a day to wake time
        if wake_dt < sleep_dt:
            wake_dt = wake_dt + timedelta(days=1)
        
        # Calculate duration in hours
        duration = (wake_dt - sleep_dt).total_seconds() / 3600
        return duration
    
    # Apply the calculation function
    df['Sleep Duration (hours)'] = df.apply(
        lambda row: calc_duration(row['prev_day_sleep_time'], row['wake_up_time']), axis=1)
    
    return df


def calculate_rolling_averages(df, columns, window=7):
    """Calculate rolling averages for specified columns."""
    if df.empty:
        return df
    
    df = df.copy()
    
    for col in columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            df[f'{col} ({window}-day avg)'] = df[col].rolling(window=window, min_periods=1).mean()
    
    return df


def get_streaks(df, column, target_value=None, condition='greater_than'):
    """Calculate streaks for a specific metric.
    
    Args:
        df: DataFrame containing the data
        column: Column to calculate streaks for
        target_value: Target value for comparison
        condition: 'greater_than', 'less_than', 'equal', or 'not_equal'
    
    Returns:
        DataFrame with streak information
    """
    if df.empty or column not in df.columns:
        return df
    
    df = df.copy()
    
    # Define the condition function
    if condition == 'greater_than':
        cond = lambda x: x > target_value
    elif condition == 'less_than':
        cond = lambda x: x < target_value
    elif condition == 'equal':
        cond = lambda x: x == target_value
    elif condition == 'not_equal':
        cond = lambda x: x != target_value
    else:
        raise ValueError(f"Invalid condition: {condition}")
    
    # Create a boolean series
    met_target = df[column].apply(cond) if target_value is not None else df[column].notna()
    
    # Calculate streaks
    streak_id = (met_target != met_target.shift(1)).cumsum()
    df['current_streak'] = met_target.groupby(streak_id).cumsum() * met_target
    
    # Reset streak to 0 for non-consecutive days
    date_diff = df[DATE_COL].diff().dt.days
    streak_breaks = (date_diff > 1) & (date_diff.notna())
    if streak_breaks.any():
        break_idx = df.index[streak_breaks]
        for idx in break_idx:
            streak_id_val = streak_id.iloc[idx]
            df.loc[df.index >= idx, 'current_streak'] = met_target.loc[df.index >= idx].groupby(
                streak_id.loc[df.index >= idx]).cumsum() * met_target.loc[df.index >= idx]
    
    return df
