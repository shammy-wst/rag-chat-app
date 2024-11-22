from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os
import pickle
from config import Config
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GoogleDriveHandler:
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    TOKEN_PATH = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'credentials',
        'token.pickle'
    )

    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        logger.debug("Début de l'authentification...")
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

        if not os.path.exists(Config.GOOGLE_CREDENTIALS_FILE):
            logger.error(f"Fichier de credentials non trouvé: {Config.GOOGLE_CREDENTIALS_FILE}")
            raise FileNotFoundError(
                f"Credentials file not found at {Config.GOOGLE_CREDENTIALS_FILE}"
            )

        logger.debug(f"Vérification du token dans {self.TOKEN_PATH}")
        if os.path.exists(self.TOKEN_PATH):
            logger.debug("Token trouvé, chargement...")
            with open(self.TOKEN_PATH, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            logger.debug("Token invalide ou expiré")
            if self.creds and self.creds.expired and self.creds.refresh_token:
                logger.debug("Rafraîchissement du token...")
                self.creds.refresh(Request())
            else:
                logger.debug("Création d'un nouveau flow OAuth...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    Config.GOOGLE_CREDENTIALS_FILE, 
                    self.SCOPES
                )
                logger.debug("Lancement du serveur local...")
                self.creds = flow.run_local_server(
                    port=0,
                    success_message='Authentification réussie!'
                )

            logger.debug("Sauvegarde du nouveau token...")
            with open(self.TOKEN_PATH, 'wb') as token:
                pickle.dump(self.creds, token)

        logger.debug("Construction du service Google Drive...")
        self.service = build('drive', 'v3', credentials=self.creds)
        logger.debug("Authentification terminée avec succès")

    def list_pdfs(self):
        try:
            results = self.service.files().list(
                q="mimeType='application/pdf'",
                pageSize=10,
                fields="nextPageToken, files(id, name)"
            ).execute()
            return results.get('files', [])
        except Exception as e:
            print(f"Erreur lors de la liste des PDFs: {e}")
            return []

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
