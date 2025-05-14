import os
import pytz
import streamlit as st
from agent import calendar_agent
from datetime import datetime
from dotenv import load_dotenv
from swarm import Swarm
from pathlib import Path

def initialize_session_states():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'calendar_context' not in st.session_state:
        st.session_state.calendar_context = {
            'selected_calendar': None,
            'date_focus': datetime.now().date(),
            'timezone': pytz.timezone('America/Los_Angeles')
        }

def main():
    load_dotenv(dotenv_path=Path("credentials/.env"))
    swarm_client = Swarm()
    agent = calendar_agent
    
    st.set_page_config(
        page_title="Agent Tilda - Calendar Assistant",
        page_icon="📅",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    with open('styles.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
    initialize_session_states()
    
    st.markdown(
        """
        <div class="header-container">
            <h1 class="tilda-header">(╭ರ_•́) ~ Agent Tilda</h1>
            <p class="tilda-subtitle">Your Calendar Assistant</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            avatar = '⭐' if message['role'] == 'user' else '☀️'
            with st.chat_message(message['role'], avatar=avatar):
                st.markdown(message['content'])
    
    if not st.session_state.messages:
        with st.chat_message('assistant', avatar='🌞'):
            welcome_msg = (
                "Hello! I'm Agent Tilda, your calendar assistant. I can help you:"
                "\n- View your calendar events."
                "\n- Schedule new events."
                "\n- Update existing events."
                "\n- Delete events you no longer need."
                "\n- List all your calendars."
                "\n- Create new calendars."
                "\n\nHow can I assist with your calendar today?"
            )
            st.markdown(welcome_msg)
    
    if prompt := st.chat_input('What would you like to do with your calendar?'):
        st.session_state.messages.append({'role': 'user', 'content': prompt})
        
        with st.chat_message('user', avatar='🌟'):
            st.markdown(prompt)
        
        with st.chat_message('assistant', avatar='🌞'):
            with st.spinner('Thinking...'):
                try:
                    response = swarm_client.run(
                        agent=agent,
                        debug=False,
                        messages=st.session_state.messages
                    )
                    
                    st.markdown(response.messages[-1]['content'])
                    
                    st.session_state.messages.append({
                        'role': 'assistant', 
                        'content': response.messages[-1]['content']
                    })
                except Exception as e:
                    error_message = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({
                        'role': 'assistant', 
                        'content': error_message
                    })

if __name__ == '__main__':
    main()
