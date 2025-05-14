import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def create_service(cred_file, api_name, api_version, *scopes):
    CLIENT_SECRET_FILE = cred_file
    API_SERVICE = api_name
    API_VER = api_version
    SCOPES = [scope for scope in scopes[0]]

    creds = None
    working_dir = os.getcwd()
    token_dir = 'tokens'
    token_file = f'{API_SERVICE}_token_{API_VER}.json'

    if not os.path.exists(os.path.join(working_dir, token_dir)):
        os.mkdir(os.path.join(working_dir, token_dir))

    if os.path.exists(os.path.join(working_dir, token_dir, token_file)):
        creds = Credentials.from_authorized_user_file(os.path.join(working_dir, token_dir, token_file), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(os.path.join(working_dir, token_dir, token_file), 'w') as token:
            token.write(creds.to_json())

    try:
        service = build(API_SERVICE, API_VER, credentials=creds, static_discovery=False)
        print(API_SERVICE, API_VER, 'service created successfully')
        return service
    except Exception as e:
        print(e)
        print(f'Failed to create service instance for {API_SERVICE}')
        os.remove(os.path.join(working_dir, token_dir, token_file))
        return None
