import json
import os
import pytz
from datetime import datetime, timedelta, time
from dateutil.parser import parse
from google_apis import create_service
from googleapiclient.errors import HttpError

cred_file = os.path.join(os.getcwd(), 'credential.json')

def gcal_client(cred_file):
    """
    Constructs a Google Calendar API Client.

    Parameter:
    - cred_file (str): The path to the credential file.
    """
    API_NAME = 'calendar'
    API_VER = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/calendar.events']
    service = create_service(cred_file, API_NAME, API_VER, SCOPES)
    return service

gcal_service = gcal_client(cred_file)

def create_calendar(calendar_name, description=None, time_zone='America/Los_Angeles'):
    """
    Creates new calendar once.

    Parameter:
    - calendar_name (str): The name of new calendar to create.
    - description (str): An optional description to include in calendar.
    - time_zone (str): Time zone for calendar.
    """
    new_calendar = {'summary': calendar_name, 'timeZone': time_zone}

    if description:
        new_calendar['description'] = description
    try:
        return gcal_service.calendars().insert(body=new_calendar).execute()
    except HttpError as error:
        print(f'Error creating calendar: {error}')
        return None

def list_calendars():
    """
    Lists users calendar.
    """
    all_calendars = []
    next_page_token = None
    try:
        while True:
            calendar_list = gcal_service.calendarList().list(pageToken=next_page_token).execute()
            all_calendars.extend(calendar_list.get('items', []))
            next_page_token = calendar_list.get('nextPageToken')
            if not next_page_token:
                break
    except HttpError as error:
        print(f'Error listing calendars: {error}')
        return []

    return [
        {
            'id': cal.get('id'),
            'name': cal.get('summary', ''),
            'description': cal.get('description', '')
        } for cal in all_calendars
    ]

def calID_via_name(name):
    """
    Resolve a calendar name (as seen in Google Calendar UI) to its calendar ID.
    """
    calendars = list_calendars()
    for cal in calendars:
        cal_name = cal.get('name', '').strip()
        # print(f"Checking calendar: '{cal_name}' against '{name.strip()}'")
        if name.strip().lower() == cal_name.lower():
            print(f"Calendar '{name}' matched with ID: {cal['id']}")
            return cal['id']
    print(f"Calendar named '{name}' not found.")
    return None

def list_events_on_day(calendar_name, date_str, timezone='America/Los_Angeles'):
    """
    List all events on a specific date from all calendars.
    
    Parameter:
    - calendar_name (str): The name of calendar to parse through to find event.
    - date_str (str): Date string in 'YYYY-MM-DD' or 'MM-DD-YYYY' format.
    - time_zone (str): Time zone for calendar.
    """
    cal_id = calID_via_name(calendar_name)
    if not cal_id:
        print(f"Calendar '{calendar_name}' not found.")
        return []

    tz = pytz.timezone(timezone)
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d") # Format YYYY-MM-DD
    except ValueError:
        date = datetime.strptime(date_str, "%m-%d-%Y") # Format MM-DD-YYYY
    start_of_day = tz.localize(datetime.combine(date, datetime.min.time()))
    end_of_day = tz.localize(datetime.combine(date, datetime.max.time()))

    time_min = start_of_day.isoformat()
    time_max = end_of_day.isoformat()

    events_result = gcal_service.events().list(
        calendarId=cal_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    # print(f"Found {len(events)} events on {date_str} in '{calendar_name}' calendar.")
    
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f"{start} - {event.get('summary', '(No Title)')}")
    
    return events

def insert_events(calendar_name, title, start_time, end_time, description=None):
    """
    Inserts an event in calendar.

    Parameter:
    - calendar_name (str): The name of calendar to insert into.
    - title (str): The name of the event.
    - start_time (str): The start time of the event.
    - end_time (str): The end time of the event.
    - description (str): An optional description to include in event.
    """
    if not calendar_name:
        calendar_name = "Tilda"

    calendar_id = calID_via_name(calendar_name)
    if not calendar_id:
        new_calendar = create_calendar("Tilda", description=f"Auto-created calendar: {calendar_name}")
        calendar_id = new_calendar.get('id') if new_calendar else None

    if not calendar_id:
        print(f"Failed to create or find calendar '{calendar_name}'")
        return None

    event = {
        'summary': title,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'America/Los_Angeles'
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'America/Los_Angeles'
        }
    }

    try:
        created_event = gcal_service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"Event created!")
    except HttpError as e:
        print(f"Failed to insert event: {e}")
        return None

def delete_event_by_title(title, event_date=None):
    """
    Delete an event by title (and optional date) across all calendars.
    
    Parameters:
    - title (str): The title of the event to match.
    - event_date (str or datetime): An optional filter for events by date.
    """
    calendars = list_calendars()
    matched = False

    if isinstance(event_date, str):
        event_date = datetime.strptime(event_date, '%Y-%m-%d')
    if event_date:
        time_min = event_date.isoformat() + "Z"
    else:
        time_min = datetime.utcnow().isoformat() + "Z"

    for cal in calendars:
        calendar_id = cal['id']
        try:
            events_result = gcal_service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                maxResults=50,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = events_result.get('items', [])
            for event in events:
                event_title = event.get('summary', '').strip().lower()
                if title.strip().lower() == event_title:
                    event_start = event.get('start', {}).get('dateTime', '') or event.get('start', {}).get('date', '')
                    print(f"Deleting '{event_title}' from calendar '{cal['name']}' on {event_start}")
                    gcal_service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
                    matched = True
                    break 

        except Exception as e:
            print(f"Failed checking calendar {calendar_id}: {e}")

    if not matched:
        print(f"No event titled '{title}' found.")
    return matched

def update_event(original_title, event_date=None, new_title=None, new_start=None, new_end=None, new_description=None):
    """
    Update an event by its title (and optional date) across all calendars.

    Parameters:
    - original_title (str): The current title of the event.
    - event_date (str or datetime): An optional filter to a specific date ('YYYY-MM-DD').
    - new_title (str): An optional new title for the event.
    - new_start (str or datetime): An optional new start datetime in ISO format.
    - new_end (str or datetime): An optional new end datetime in ISO format.
    - new_description (str): An optional new description.
    """
    calendars = list_calendars()
    matched = False

    if isinstance(event_date, str):
        event_date = datetime.strptime(event_date, "%Y-%m-%d")
    time_min = event_date.isoformat() + "Z" if event_date else datetime.utcnow().isoformat() + "Z"

    for cal in calendars:
        calendar_id = cal["id"]
        try:
            events_result = gcal_service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                maxResults=50,
                singleEvents=True,
                orderBy="startTime"
            ).execute()

            events = events_result.get("items", [])
            for event in events:
                event_title = event.get("summary", "").strip().lower()
                if event_title == original_title.strip().lower():
                    print(f"Found event '{original_title}' in calendar '{cal['name']}'")

                    if new_title:
                        event["summary"] = new_title
                    if new_description is not None:
                        event["description"] = new_description
                    if new_start:
                        event["start"]["dateTime"] = new_start
                    if new_end:
                        event["end"]["dateTime"] = new_end

                    updated_event = gcal_service.events().update(
                        calendarId=calendar_id,
                        eventId=event["id"],
                        body=event
                    ).execute()

                    print(f"Updated event!")
                    matched = True
                    break

        except Exception as e:
            print(f"Error checking calendar '{calendar_id}': {e}")

    if not matched:
        print(f"No event titled '{original_title}' found.")
    return matched
