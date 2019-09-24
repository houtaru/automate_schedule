from __future__ import print_function
from datetime import datetime, timedelta
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle
SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = 'credentials.json'

def get_calendar_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the firs:cst
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials avaiable, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service

def insertEvent(subject, location, description, start_time, end_time, timezone, day):
    service = get_calendar_service()
    calendarID = 'ken229l5r6jo778tqim1mhmpms@group.calendar.google.com' # APCS Schedule Calendar ID
    
    event = {
        "summary": subject,
        "location": location,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": timezone
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": timezone
        },
        "recurrence": [
            "RRULE:FREQ=WEEKLY;UNTIL=20191214;BYDAY=" + day[0:2].upper(),
        ],
        "reminders": {
            "useDefault": False,
            "overrides": [
                {'method': 'popup', 'minutes': 20},
            ]
        }   
    }
    event_result = service.events().insert(calendarId=calendarID, body=event).execute() # insert event     
    return event_result
