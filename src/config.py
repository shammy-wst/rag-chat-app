import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Chemin vers les credentials OAuth (pas les credentials par défaut)
    GOOGLE_CREDENTIALS_FILE = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'credentials',
        'oauth_credentials.json'
    )
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    MODEL_NAME = os.getenv('MODEL_NAME', 'llama2')
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))