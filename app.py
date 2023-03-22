# For virtual environments, remember to use source .venv/bin/activate
# NOTE: don't include credentials.json and token.json in github push
from __future__ import print_function

import os.path
import random
import sys
import confidential

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
# NOTE: include variables SPREADSHEET_ID and RANGE_NAME in a separate python
# file called "confidential.py". Also ensure that you have a credentials.json
# file.

def obtain_credentials():
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def obtain_sheet_info(creds, sheetID):
    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheetID,
                                    range=confidential.RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return

        # print('Name, Major:')
        # for row in values:
        #     # Print columns A and E, which correspond to indices 0 and 4.
        #     print('%s, %s' % (row[0], row[1]))
    except HttpError as err:
        print(err)
    
    return values

def build_raffle_dict(dict, values, uteids):
    for row in values:
        if row[2] not in dict:
            dict[row[2]] = {
                "first_name": row[0],
                "last_name": row[1],
                "email": row[3]
            }
            uteids.append(row[2])

def perform_raffle(dict, uteids):
    index = random.randint(0, len(uteids))
    selected_eid = uteids.pop(index)
    member_info = dict.pop(selected_eid)

    print(selected_eid)
    print(member_info)

def main():
    args = sys.argv[1:]

    # Obtain the credentials from the credentials.json file
    creds = obtain_credentials()

    # Create a dictionary with participant information from sheets
    raffle_dict = {}
    uteids = []

    for sheetID in confidential.SPREADSHEET_IDS:
        # Use the credentials to obtain participant information from Google Sheets
        values = obtain_sheet_info(creds, sheetID)
        build_raffle_dict(raffle_dict, values, uteids)

    # Perform the raffle with the dictionary and array of uteids
    num_raffles = 1
    if(len(args) > 0):
        num_raffles = int(args[0])
    
    while(num_raffles > 0):
        perform_raffle(raffle_dict, uteids)
        num_raffles -= 1


if __name__ == '__main__':
    main()