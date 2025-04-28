import os
import pandas as pd
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.config import CREDENTIALS_PATH, TOKEN_PATH, SHEET_ID, RANGE_NAME, DATE_COL

# If modifying these scopes, delete the token.json file.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def get_credentials():
    """Get valid user credentials from storage or initiate OAuth2 flow."""
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_info(eval(open(TOKEN_PATH).read()), SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(TOKEN_PATH, 'w') as token:
            token.write(str(creds.to_json()))
    
    return creds


def fetch_data():
    """Fetch data from Google Sheet and return as DataFrame."""
    try:
        creds = get_credentials()
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SHEET_ID,
                                    range=RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return pd.DataFrame()

        # First row is headers
        headers = values[0]
        df = pd.DataFrame(values[1:], columns=headers)
        
        # Convert date strings to datetime objects
        if DATE_COL in df.columns:
            df[DATE_COL] = pd.to_datetime(df[DATE_COL])
            df = df.sort_values(by=DATE_COL)  # Sort by date
        
        return df

    except HttpError as err:
        print(f"An error occurred: {err}")
        return pd.DataFrame()


def get_data_range(df, days=30):
    """Get data for the last specified number of days."""
    if DATE_COL not in df.columns or df.empty:
        return df
    
    latest_date = df[DATE_COL].max()
    start_date = latest_date - pd.Timedelta(days=days)
    
    return df[df[DATE_COL] >= start_date]
