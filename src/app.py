import streamlit as st
from drive_handler import GoogleDriveHandler
import os

st.set_page_config(page_title="RAG Chat App", layout="wide")

def init_session_state():
    if 'drive_handler' not in st.session_state:
        st.session_state.drive_handler = GoogleDriveHandler()
    if 'pdf_files' not in st.session_state:
        st.session_state.pdf_files = []

def main():
    st.title("RAG Chat Application")
    
    init_session_state()
    
    # Sidebar pour les contrôles
    with st.sidebar:
        st.header("Configuration")
        
        # Bouton pour rafraîchir la liste des PDFs
        if st.button("Rafraîchir les PDFs"):
            st.session_state.pdf_files = st.session_state.drive_handler.list_pdfs()
        
        # Affichage des PDFs disponibles
        st.subheader("PDFs disponibles")
        if st.session_state.pdf_files:
            for pdf in st.session_state.pdf_files:
                st.write(f"📄 {pdf['name']}")
        else:
            st.write("Aucun PDF trouvé")

    # Zone principale
    st.header("Chat")
    user_input = st.text_input("Votre question:")
    
    if user_input:
        st.write(f"Question: {user_input}")
        # Pour l'instant, on renvoie juste la question
        st.write("Réponse: En cours d'implémentation...")

if __name__ == "__main__":
    main()
