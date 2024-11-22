from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import os

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CREDENTIALS_PATH = 'credentials/oauth_credentials.json'

def setup_oauth():
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"""
        Veuillez suivre ces étapes :
        1. Allez sur https://console.cloud.google.com/apis/credentials
        2. Cliquez sur "CREATE CREDENTIALS" > "OAuth client ID"
        3. Sélectionnez "Desktop app"
        4. Téléchargez le fichier JSON
        5. Placez-le dans {CREDENTIALS_PATH}
        """)
        return False
    
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    creds = flow.run_local_server(port=0)
    print("Authentification réussie!")
    return True

if __name__ == "__main__":
    setup_oauth() 