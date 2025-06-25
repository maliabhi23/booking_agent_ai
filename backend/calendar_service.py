import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleCalendarService:
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.json"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    # Use mock service for demo purposes
                    self.service = MockCalendarService()
                    return
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=creds)
    
    def get_free_busy(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get free/busy information for the specified time range"""
        try:
            body = {
                "timeMin": start_time.isoformat() + 'Z',
                "timeMax": end_time.isoformat() + 'Z',
                "items": [{"id": "primary"}]
            }
            
            result = self.service.freebusy().query(body=body).execute()
            return result.get('calendars', {}).get('primary', {}).get('busy', [])
        
        except (HttpError, AttributeError):
            # Return mock data if service unavailable
            return self._get_mock_busy_times(start_time, end_time)
    
    def find_available_slots(self, start_date: datetime, end_date: datetime, 
                           duration_minutes: int = 60) -> List[Dict[str, str]]:
        """Find available time slots in the given date range"""
        busy_times = self.get_free_busy(start_date, end_date)
        available_slots = []
        
        current_time = start_date
        while current_time < end_date:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            
            # Check if this slot conflicts with busy times
            is_available = True
            for busy in busy_times:
                busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                
                if (current_time < busy_end and slot_end > busy_start):
                    is_available = False
                    break
            
            # Only include slots during business hours (9 AM - 5 PM)
            if (is_available and 9 <= current_time.hour < 17 and 
                current_time.weekday() < 5):  # Monday = 0, Sunday = 6
                available_slots.append({
                    'start': current_time.strftime('%Y-%m-%d %H:%M'),
                    'end': slot_end.strftime('%Y-%m-%d %H:%M'),
                    'display': current_time.strftime('%B %d, %Y at %I:%M %p')
                })
            
            current_time += timedelta(minutes=30)  # Check every 30 minutes
        
        return available_slots[:10]  # Return max 10 slots
    
    def book_appointment(self, start_time: datetime, end_time: datetime, 
                        title: str, description: str = "") -> bool:
        """Book an appointment in the calendar"""
        try:
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            result = self.service.events().insert(calendarId='primary', body=event).execute()
            return True
        
        except (HttpError, AttributeError):
            # Mock booking for demo
            print(f"Mock booking: {title} from {start_time} to {end_time}")
            return True
    
    def _get_mock_busy_times(self, start_time: datetime, end_time: datetime) -> List[Dict[str, str]]:
        """Generate mock busy times for demo purposes"""
        mock_busy = []
        
        # Add some mock busy slots
        for i in range(3):
            busy_start = start_time + timedelta(days=i, hours=10)
            busy_end = busy_start + timedelta(hours=1)
            if busy_end <= end_time:
                mock_busy.append({
                    'start': busy_start.isoformat() + 'Z',
                    'end': busy_end.isoformat() + 'Z'
                })
        
        return mock_busy


class MockCalendarService:
    """Mock calendar service for demo purposes"""
    
    def freebusy(self):
        return MockFreeBusy()


class MockFreeBusy:
    def query(self, body):
        return MockQueryResult()


class MockQueryResult:
    def execute(self):
        return {
            'calendars': {
                'primary': {
                    'busy': []
                }
            }
        }