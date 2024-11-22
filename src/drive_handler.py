from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import pickle
from config import Config

class GoogleDriveHandler:
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    TOKEN_PATH = 'credentials/token.pickle'

    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        if os.path.exists(self.TOKEN_PATH):
            with open(self.TOKEN_PATH, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.GOOGLE_CREDENTIALS_FILE, self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open(self.TOKEN_PATH, 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('drive', 'v3', credentials=self.creds)

    def list_pdfs(self):
        results = self.service.files().list(
            q="mimeType='application/pdf'",
            pageSize=10,
            fields="nextPageToken, files(id, name)"
        ).execute()
        return results.get('files', [])

    def download_pdf(self, file_id, output_path):
        try:
            file = self.service.files().get_media(fileId=file_id)
            content = file.execute()
            
            with open(output_path, 'wb') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
