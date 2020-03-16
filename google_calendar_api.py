from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

import pickle
import json
import os.path

SCOPES = ['https://www.googleapis.com/auth/calendar']

CREDENTIALS_FILE = 'credentials.json'

class GoogleCalendarClient:
    """ Client for Google Calendar API """
    def __init__(
            self,
            generate_creds=False,
            calendar_id="primary"):
        """
        Args:
            generate_creds (bool): if True, generate new credentials.
            calendar_id: Id of calendar where events are add to.
        """
        self._default_calendar_id = self._current_calendar_id = calendar_id

        if generate_creds or (not os.path.exists('token.pkl')):
            self.get_credentials()
        self.load_credentials()

    def get_credentials(self):
        """ Generate credentials 
        """
        flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
        credentials = flow.run_console()
        pickle.dump(credentials, open('token.pkl', "wb"))

    def load_credentials(self):
        """ Load credentials
        """
        self._credentials = pickle.load(open('token.pkl', 'rb'))
        self._service = build("calendar", "v3", credentials=self._credentials)

    def load_calendar(self, calendar_name):
        """ Load calendar id from name.
        if calendar doesn't exists, create one.
        Args:
            calendar_name (str): name of exists calendar.
        """
        assert(calendar_name is not None)
        page_token = None
        while True:
            calendar_list = self._service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                if calendar_list_entry['summary'] == calendar_name:
                    self._current_calendar_id = calendar_list_entry['id']
                    return

            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break

        self.insert_calendar(calendar_name)

    def insert_calendar(self, summary):
        """ Create new calendar
        Args:
            summary (str): brief about calendar.
        Return:
            json: Infomation about new created calendar.
        """
        calendar = {
            'summary': summary
        }
        created_calendar = self._service.calendars().insert(body=calendar).execute()

        self._current_calendar_id = created_calendar['id']
        return created_calendar

    def delete_calendar(self):
        """ Delete current calendar
        Return:
            True: if current calendar is not default
        """
        if self._current_calendar_id == self._default_calendar_id:
            return False
        self._service.calendars().delete(calendarId=self._current_calendar_id).execute()
        self._current_calendar_id = self._default_calendar_id
        return True

    def insert_event(
            self,
            event_entry=None):
        """ Insert new event to current calendar
        Args:
            event_entry = {
                "summary": summary,
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
        Returns:
            Id of event.
        """
        if event_entry is None:
            raise ValueError("Missing event entry!")

        event_entry = self._service.events().insert(calendarId=self._current_calendar_id,
                                    body=event_entry).execute()
        return event_entry.get('id')
    
    def update_event(self, event_id, event_entry):
        """ Update exists event infomation 
        Args:
            event_id: id of edited event
        """
        event = self._service.events().update(calendarId=self._current_calendar_id, 
                                                eventId=event_id, 
                                                body=event_entry,).execute()

    def get_event(self, event_id):
        """ Get event information from existed event using event id 
        """
        event = self._service.events().get(calendarId=self._current_calendar_id, eventId=event_id).execute()
        return event
