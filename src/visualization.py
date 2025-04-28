import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

from src.config import DATE_COL, WAKE_UP_COL, SLEEP_COL, WEIGHT_COL, VIS_DATE_FORMAT


def time_to_decimal(t):
    """Convert datetime.time to decimal hours."""
    if pd.isna(t):
        return np.nan
    return t.hour + t.minute/60 + t.second/3600


def plot_time_series(df, column, title, y_label, rolling_window=7, figsize=(12, 6)):
    """Generate a time series plot for a given column."""
    if df.empty or column not in df.columns:
        return None
    
    fig = px.line(df, x=DATE_COL, y=column, title=title)
    
    # Add rolling average if data is numeric
    if pd.api.types.is_numeric_dtype(df[column]):
        rolling_avg = df[column].rolling(window=rolling_window, min_periods=1).mean()
        fig.add_scatter(x=df[DATE_COL], y=rolling_avg, mode='lines', 
                        name=f'{rolling_window}-day Average', line=dict(width=2, dash='dash'))
    
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title=y_label,
        legend_title_text='Legend',
        template='plotly_white'
    )
    
    return fig


def plot_sleep_wake_patterns(df, figsize=(12, 8)):
    """Plot sleep and wake up times on a 24-hour cycle."""
    if df.empty or SLEEP_COL not in df.columns or WAKE_UP_COL not in df.columns:
        return None
    
    # Convert time objects to decimal hours for plotting
    df = df.copy()
    df['wake_decimal'] = df[WAKE_UP_COL].apply(time_to_decimal)
    df['sleep_decimal'] = df[SLEEP_COL].apply(time_to_decimal)
    
    # Create figure
    fig = go.Figure()
    
    # Add wake up times
    fig.add_trace(go.Scatter(
        x=df[DATE_COL], y=df['wake_decimal'],
        mode='lines+markers',
        name='Wake Up Time',
        line=dict(color='orange', width=2),
        marker=dict(size=8)
    ))
    
    # Add sleep times
    fig.add_trace(go.Scatter(
        x=df[DATE_COL], y=df['sleep_decimal'],
        mode='lines+markers',
        name='Sleep Time',
        line=dict(color='blue', width=2),
        marker=dict(size=8)
    ))
    
    # Set y-axis to show time format
    fig.update_layout(
        title='Sleep and Wake Up Patterns',
        xaxis_title='Date',
        yaxis_title='Time (24-hour)',
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(0, 25, 2)),
            ticktext=[f'{i:02d}:00' for i in range(0, 25, 2)]
        ),
        template='plotly_white'
    )
    
    return fig


def plot_sleep_duration(df, figsize=(12, 6)):
    """Plot sleep duration over time."""
    if df.empty or 'Sleep Duration (hours)' not in df.columns:
        return None
    
    fig = px.bar(
        df, x=DATE_COL, y='Sleep Duration (hours)',
        title='Sleep Duration Over Time',
        labels={'Sleep Duration (hours)': 'Hours of Sleep'},
        color='Sleep Duration (hours)',
        color_continuous_scale='RdYlGn',  # Red for low, green for high
    )
    
    # Add a reference line for ideal sleep (e.g., 8 hours)
    fig.add_shape(
        type="line",
        x0=df[DATE_COL].min(),
        y0=8,
        x1=df[DATE_COL].max(),
        y1=8,
        line=dict(color="red", width=2, dash="dash"),
    )
    
    fig.add_annotation(
        x=df[DATE_COL].max(),
        y=8.2,
        text="Ideal: 8 hours",
        showarrow=False,
        font=dict(color="red")
    )
    
    fig.update_layout(template='plotly_white')
    
    return fig


def plot_weight_trend(df, figsize=(12, 6)):
    """Plot weight trend over time."""
    if df.empty or WEIGHT_COL not in df.columns:
        return None
    
    # Create the figure
    fig = px.scatter(
        df, x=DATE_COL, y=WEIGHT_COL,
        trendline='lowess',  # Add a trend line
        title='Weight Trend Over Time',
        labels={WEIGHT_COL: 'Weight (kg/lbs)'},
    )
    
    # Add 7-day moving average
    rolling_avg = df[WEIGHT_COL].rolling(window=7, min_periods=1).mean()
    fig.add_scatter(x=df[DATE_COL], y=rolling_avg, mode='lines', 
                    name='7-day Average', line=dict(width=2, color='green'))
    
    fig.update_layout(template='plotly_white')
    
    return fig


def plot_habit_calendar(df, column, title, colorscale='YlGn'):
    """Create a calendar heatmap for habits or metrics."""
    if df.empty or column not in df.columns:
        return None
    
    # Prepare data for calendar heatmap
    df = df.copy()
    df['year'] = df[DATE_COL].dt.year
    df['month'] = df[DATE_COL].dt.month
    df['day'] = df[DATE_COL].dt.day
    df['weekday'] = df[DATE_COL].dt.weekday
    
    # Convert column to numeric if it's not already
    if not pd.api.types.is_numeric_dtype(df[column]):
        df[column] = df[column].astype(bool).astype(int)
    
    # Create calendar data
    fig = px.imshow(
        df.pivot_table(
            index='weekday', 
            columns='day', 
            values=column,
            aggfunc='mean'
        ),
        labels=dict(x="Day of Month", y="Day of Week", color=column),
        x=sorted(df['day'].unique()),
        y=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
        color_continuous_scale=colorscale,
        title=title
    )
    
    fig.update_layout(template='plotly_white')
    
    return fig


def plot_streak_chart(df, column, target_value=None, condition='greater_than'):
    """Create a visualization of current streaks for a metric."""
    if df.empty or column not in df.columns or 'current_streak' not in df.columns:
        return None
    
    # Get the latest streak
    latest_streak = df['current_streak'].iloc[-1] if not df.empty else 0
    
    # Create a gauge chart for current streak
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=latest_streak,
        title={'text': f"Current Streak: {column}"},
        gauge={
            'axis': {'range': [0, max(10, latest_streak * 1.2)]},
            'bar': {'color': "green"},
            'steps': [
                {'range': [0, 3], 'color': "lightgray"},
                {'range': [3, 7], 'color': "lightblue"},
                {'range': [7, 14], 'color': "royalblue"},
                {'range': [14, 30], 'color': "blue"},
                {'range': [30, max(10, latest_streak * 1.2)], 'color': "darkblue"}
            ],
        }
    ))
    
    fig.update_layout(
        title=f"{column} Streak - Days in a Row",
        template='plotly_white'
    )
    
    return fig


def create_dashboard_charts(df):
    """Create all dashboard charts from the data."""
    if df.empty:
        return {}
    
    charts = {}
    
    # Sleep metrics
    if SLEEP_COL in df.columns and WAKE_UP_COL in df.columns:
        charts['sleep_pattern'] = plot_sleep_wake_patterns(df)
        
        if 'Sleep Duration (hours)' in df.columns:
            charts['sleep_duration'] = plot_sleep_duration(df)
            
            # Sleep duration time series
            charts['sleep_duration_trend'] = plot_time_series(
                df, 'Sleep Duration (hours)', 'Sleep Duration Trend', 'Hours of Sleep')
    
    # Weight trend
    if WEIGHT_COL in df.columns:
        charts['weight_trend'] = plot_weight_trend(df)
    
    return charts
