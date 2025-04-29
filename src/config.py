""" Config module """
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Project base directory
BASE_DIR = Path(__file__).parent.parent

# Google Sheets configuration
SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

# Get range name and clean it up to remove any comments
range_env = os.getenv('SHEET_RANGE', 'Sheet1!A:Z')
if '#' in range_env:
    RANGE_NAME = range_env.split('#')[0].strip()
else:
    RANGE_NAME = range_env

# Print debug information
print(f"DEBUG - SHEET_ID: {SHEET_ID}")
print(f"DEBUG - RANGE_NAME: {RANGE_NAME}")

# Credentials
CREDENTIALS_PATH = BASE_DIR / 'credentials' / 'credentials.json'
TOKEN_PATH = BASE_DIR / 'credentials' / 'token.json'

# Data columns (customize based on your sheet structure)
DATE_COL = 'Date'
WAKE_UP_COL = 'Wake Up'
SLEEP_COL = 'Sleep'
WEIGHT_COL = 'Weight'

# Default date range for filtering data (in days)
DEFAULT_DATE_RANGE = 30

# Visualization settings
VIS_DATE_FORMAT = '%Y-%m-%d'  # Format for dates in visualizations

# Add more column names as needed
# Example: EXERCISE_COL = 'Exercise'
