# Saugat Dashboard

A Python application to visualize daily routine data from Google Sheets.

## Features

- Connect to Google Sheets API to fetch daily routine data
- Generate visualizations for various metrics (sleep, wake up time, weight, etc.)
- Interactive dashboard to track habits and health metrics
- Trend analysis over time

## Setup

1. Create a Google Cloud Project and enable the Google Sheets API
2. Create credentials (OAuth 2.0 Client ID) and download the JSON file
3. Save the credentials file as `credentials/credentials.json`
4. Install dependencies using uv (recommended) or pip:

```bash
# Using uv (faster Python package installer)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Or using traditional pip
pip install -e .
```

5. Configure your Google Sheet ID in the `.env` file (copy from `.env.example`)

## Usage

```bash
# Run the Streamlit dashboard
streamlit run src/app.py
```

## Development

This project uses uv for dependency management. To add or update dependencies:

```bash
# Add a new dependency
uv pip install package_name

# Update dependencies with uv
uv pip sync

# Format code with ruff
uv pip install ruff
ruff format .
```

## Data Format

Your Google Sheet should have columns like:
- Date
- Wake Up
- Sleep
- Weight
- And any other daily metrics you want to track

Each row represents data for a single day.
