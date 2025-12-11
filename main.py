from backend import askBot
import streamlit as st
import os
import json
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import traceback

def get_sheet(sheet_name="logger"):
    """Loads Google Sheets credentials from environment for Render usage."""
    raw = os.getenv("GOOGLE_CREDS_JSON")
    if not raw:
        raise RuntimeError("GOOGLE_CREDS_JSON is missing in environment!")

    creds_dict = json.loads(raw.replace("\\\\n", "\\n"))  # ensures key is valid

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open(sheet_name).sheet1

def log_to_sheets(user_input: str):
    """Silent logger — only shows an error if logging fails."""
    try:
        sheet = get_sheet()
        sheet.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_input])

    except Exception:
        traceback.print_exc()  # Only shows when there's a failure

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    log_to_sheets(user_input)
    with st.chat_message('user'):
        st.text(user_input)

    response = askBot(user_input)
    st.session_state['message_history'].append({'role': 'assistant', 'content': response})

    with st.chat_message('assistant'):
        st.text(response)

