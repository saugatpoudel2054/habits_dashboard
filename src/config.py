import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Project base directory
BASE_DIR = Path(__file__).parent.parent

# Google Sheets configuration
SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
RANGE_NAME = os.getenv('SHEET_RANGE', 'Sheet1!A:Z')  # Default range

# Credentials
CREDENTIALS_PATH = BASE_DIR / 'credentials' / 'credentials.json'
TOKEN_PATH = BASE_DIR / 'credentials' / 'token.json'

# Data columns (customize based on your sheet structure)
DATE_COL = 'Date'
WAKE_UP_COL = 'Wake Up'
SLEEP_COL = 'Sleep'
WEIGHT_COL = 'Weight'

# Add more column names as needed
# Example: EXERCISE_COL = 'Exercise'

# Visualization settings
VIS_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_DATE_RANGE = 30  # Last 30 days by default
