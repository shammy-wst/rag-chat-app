from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)

# Assurez-vous que le dossier credentials existe
if not os.path.exists('credentials'):
    os.makedirs('credentials')

# Les scopes dont nous avons besoin
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def generate_token():
    try:
        print("Début de la génération du token...")
        
        # Autoriser HTTP pour le développement local
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        
        # Vérifier que le fichier de credentials existe
        credentials_path = 'credentials/oauth_credentials.json'
        if not os.path.exists(credentials_path):
            print(f"Erreur: Le fichier {credentials_path} n'existe pas!")
            return False
            
        print("Création du flow OAuth...")
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path,
            SCOPES,
            redirect_uri='http://localhost:3000'
        )
        
        print("Lancement du serveur local...")
        creds = flow.run_local_server(
            port=3000,
            prompt='consent',
            success_message='Token généré avec succès!'
        )
        
        print("Sauvegarde du token...")
        token_path = 'credentials/token.pickle'
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
            
        print(f"Token généré avec succès et sauvegardé dans {token_path}!")
        return True
        
    except Exception as e:
        print(f"Erreur lors de la génération du token: {str(e)}")
        print(f"Type d'erreur: {type(e)}")
        import traceback
        print(f"Traceback complet: {traceback.format_exc()}")
        return False

if __name__ == '__main__':
    print("Démarrage du script de génération de token...")
    success = generate_token()
    print(f"Résultat de la génération: {'Succès' if success else 'Échec'}") 