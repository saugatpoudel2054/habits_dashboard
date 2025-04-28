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
    
    # Convert time strings to datetime.time objects
    if WAKE_UP_COL in df.columns:
        df[WAKE_UP_COL] = pd.to_datetime(df[WAKE_UP_COL], format='%H:%M', errors='coerce').dt.time
    
    if SLEEP_COL in df.columns:
        df[SLEEP_COL] = pd.to_datetime(df[SLEEP_COL], format='%H:%M', errors='coerce').dt.time
    
    # Convert weight to numeric
    if WEIGHT_COL in df.columns:
        df[WEIGHT_COL] = pd.to_numeric(df[WEIGHT_COL], errors='coerce')
    
    return df


def calculate_sleep_duration(df):
    """Calculate sleep duration between sleep time and wake up time."""
    if df.empty or SLEEP_COL not in df.columns or WAKE_UP_COL not in df.columns:
        return df
    
    df = df.copy()
    
    # Function to calculate hours between sleep and wake up
    def calc_duration(sleep, wake):
        if pd.isna(sleep) or pd.isna(wake):
            return np.nan
        
        # Create datetime objects for calculation
        sleep_dt = datetime.combine(datetime.today().date(), sleep)
        wake_dt = datetime.combine(datetime.today().date(), wake)
        
        # If wake time is earlier than sleep time, it means sleep was yesterday
        if wake_dt < sleep_dt:
            wake_dt = wake_dt + timedelta(days=1)
        
        # Calculate duration in hours
        duration = (wake_dt - sleep_dt).total_seconds() / 3600
        return duration
    
    # Apply the calculation function
    df['Sleep Duration (hours)'] = df.apply(
        lambda row: calc_duration(row[SLEEP_COL], row[WAKE_UP_COL]), axis=1)
    
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
