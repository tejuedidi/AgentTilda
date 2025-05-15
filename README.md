# Agent Tilda

## Overview
Agent Tilda is an AI-powered Google Calendar assistant designed to help users manage events, avoid scheduling conflicts, and stay organized through natural language interaction. This project leverages the Google Calendar API for event automation, the OpenAI API for intelligent responses, Streamlit for a user-friendly web interface, and OpenAI Swarm to coordinate multiple agents.

## Demo!
[![CapGen Demo](https://img.youtube.com/vi/_9ezgDNwE_M/0.jpg)](https://www.youtube.com/watch?v=_9ezgDNwE_M)

## How It Works
The app serves as an intelligent assistant that interacts with your Google Calendar using natural language commands:

1. The app authenticates with your Google account and retrieves access to your calendar data.
2. You interact with the assistant using natural language commands to perform tasks such as listing calendars or scheduling events.
3. The assistant processes your requests, engages in a conversational flow to clarify details, and suggests optimal times, helping you stay on top of your schedule and avoid conflicts.

## Features
* Calendar Management: List, create, and manage multiple Google Calendars.

* Smart Event Handling: Create, update, and delete events with natural language.

* Conflict Avoidance: Automatically checks for scheduling conflicts before creating or updating events.

* Daily Agenda Overview: Get a clean summary of all events scheduled for a specific day.

* Conversational Agent: Refine or request changes to your schedule through a natural language chat interface.

## Requirements
- Python 3
- Google Calendar API + Google OAuth 2.0 Client ID
- Streamlit
- OpenAI API (with Swarm Integration)
- dotenv

You can install the necessary dependencies and run the application with the following commands:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Limitations
Currently, users must explicitly provide the event title and/or date when updating or viewing events. The assistant relies on this input to accurately identify and retrieve the correct event.

## Future Improvements
* Voice command support to make the assistant more intuitive and accessible.
* Natural language date parsing (e.g., "next Friday" or "in two days") to improve flexibility.
* Support recurring events in the future, to support standard calendar workflows.
