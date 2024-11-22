import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_CREDENTIALS_FILE = os.getenv('GOOGLE_CREDENTIALS_FILE')
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    MODEL_NAME = os.getenv('MODEL_NAME', 'llama2')
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))