from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
import os
import pickle
from config import Config
import logging
import io

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GoogleDriveHandler:
    SCOPES = [
        'https://www.googleapis.com/auth/drive',  # Accès complet à Drive
        'https://www.googleapis.com/auth/drive.file',  # Accès aux fichiers créés par l'app
        'https://www.googleapis.com/auth/drive.metadata.readonly'  # Lecture des métadonnées
    ]
    TOKEN_PATH = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'credentials',
        'token.pickle'
    )
    PUBLIC_FOLDER_NAME = "RAG-Chat-Public-PDFs"

    def __init__(self):
        self.creds = None
        self.service = None
        self.public_folder_id = None
        self._authenticate()
        self._ensure_public_folder_exists()

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

    def _ensure_public_folder_exists(self):
        """Crée ou récupère le dossier public"""
        try:
            # Cherche si le dossier existe déjà
            results = self.service.files().list(
                q=f"name='{self.PUBLIC_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder'",
                spaces='drive',
                fields='files(id)'
            ).execute()
            files = results.get('files', [])

            if files:
                self.public_folder_id = files[0]['id']
                logger.debug(f"Dossier public trouvé: {self.public_folder_id}")
            else:
                # Crée le dossier
                folder_metadata = {
                    'name': self.PUBLIC_FOLDER_NAME,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()
                self.public_folder_id = folder['id']
                logger.debug(f"Dossier public créé: {self.public_folder_id}")

            # Rend le dossier public
            self._make_public(self.public_folder_id)

        except Exception as e:
            logger.error(f"Erreur lors de la création du dossier public: {e}")
            raise

    def _make_public(self, file_id):
        """Rend un fichier ou dossier public"""
        try:
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            logger.debug(f"Fichier/dossier {file_id} rendu public")
        except Exception as e:
            logger.error(f"Erreur lors de la modification des permissions: {e}")

    def upload_pdf(self, file_path):
        """Upload un PDF dans le dossier public"""
        try:
            file_metadata = {
                'name': os.path.basename(file_path),
                'parents': [self.public_folder_id]
            }
            media = MediaFileUpload(
                file_path,
                mimetype='application/pdf',
                resumable=True
            )
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            # Rend le fichier public
            self._make_public(file['id'])
            
            return file['id']
        except Exception as e:
            logger.error(f"Erreur lors de l'upload: {e}")
            return None

    def list_public_pdfs(self):
        """Liste tous les PDFs dans le dossier public"""
        try:
            results = self.service.files().list(
                q=f"'{self.public_folder_id}' in parents and mimeType='application/pdf'",
                spaces='drive',
                fields="files(id, name, webViewLink)"
            ).execute()
            return results.get('files', [])
        except Exception as e:
            logger.error(f"Erreur lors de la liste des PDFs: {e}")
            return []

    def delete_pdf(self, file_id):
        """Supprime un PDF du dossier public"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression: {e}")
            return False

    def download_pdf(self, file_id, output_path):
        """Télécharge un PDF depuis le dossier public"""
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            fh.seek(0)
            with open(output_path, 'wb') as f:
                f.write(fh.read())
                f.flush()
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement: {e}")
            return False
