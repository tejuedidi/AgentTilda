from swarm import Agent
from prompts import agent_tilda_prompt
from api import *
MODEL = 'gpt-4o-mini'

calendar_agent = Agent(
    name='Agent Tilda',
    model = MODEL,
    instructions=agent_tilda_prompt,
    functions=[
        create_calendar, list_calendars, list_events_on_day, insert_events, delete_event_by_title, update_event
    ]
)
