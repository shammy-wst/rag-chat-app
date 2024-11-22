import streamlit as st
from pathlib import Path
import shutil
from rag_handler import RAGHandler
from drive_handler import GoogleDriveHandler
import os

st.set_page_config(page_title="RAG Chat App", layout="wide")

# Constantes
TEMP_DIR = Path("storage/temp")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def init_session_state():
    if 'drive_handler' not in st.session_state:
        st.session_state.drive_handler = GoogleDriveHandler()
    if 'rag_handler' not in st.session_state:
        st.session_state.rag_handler = RAGHandler()
    if 'pdf_files' not in st.session_state:
        st.session_state.pdf_files = []
    if 'selected_pdfs' not in st.session_state:
        st.session_state.selected_pdfs = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'processed_pdfs' not in st.session_state:
        st.session_state.processed_pdfs = False
    if 'use_rag' not in st.session_state:
        st.session_state.use_rag = True
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.7

def save_uploaded_file_temp(uploaded_file):
    """Sauvegarde temporairement un fichier uploadé"""
    temp_path = TEMP_DIR / uploaded_file.name
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return temp_path

def cleanup_temp_files():
    """Nettoie les fichiers temporaires"""
    for file in TEMP_DIR.glob("*"):
        if file.is_file():
            file.unlink()

def main():
    st.title("RAG Chat Application")
    
    init_session_state()
    
    # Sidebar pour la gestion des PDFs
    with st.sidebar:
        st.header("Gestion des PDFs")
        
        # Bouton de rafraîchissement
        if st.button("🔄 Rafraîchir les PDFs"):
            st.session_state.pdf_files = st.session_state.drive_handler.list_public_pdfs()
        
        # Zone d'upload
        uploaded_file = st.file_uploader(
            "📄 Uploader un PDF",
            type=['pdf']
        )
        
        if uploaded_file:
            if st.button("⬆️ Publier dans le bucket"):
                with st.spinner("Publication en cours..."):
                    # Sauvegarde temporaire
                    temp_path = save_uploaded_file_temp(uploaded_file)
                    
                    # Upload vers Google Drive
                    if st.session_state.drive_handler.upload_pdf(str(temp_path)):
                        st.success("✅ PDF publié avec succès!")
                        # Rafraîchir la liste
                        st.session_state.pdf_files = st.session_state.drive_handler.list_public_pdfs()
                    else:
                        st.error("❌ Erreur lors de la publication")
                    
                    # Nettoyage
                    cleanup_temp_files()
        
        # Liste des PDFs disponibles
        st.subheader("PDFs dans le bucket")
        
        if not st.session_state.pdf_files:
            st.info("Aucun PDF disponible. Cliquez sur Rafraîchir ou uploadez-en un!")
        else:
            selected_pdfs = []
            for pdf in st.session_state.pdf_files:
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.checkbox(f"📄 {pdf['name']}", key=pdf['id']):
                        selected_pdfs.append(pdf)
                with col2:
                    st.markdown(f"[🔗]({pdf['webViewLink']})")
            
            st.session_state.selected_pdfs = selected_pdfs
            
            col1, col2 = st.columns(2)
            
            # Bouton de traitement
            if selected_pdfs and col1.button("🔄 Traiter"):
                with st.spinner("Traitement des PDFs..."):
                    # Téléchargement temporaire pour le traitement
                    pdf_paths = []
                    for pdf in selected_pdfs:
                        temp_path = TEMP_DIR / pdf['name']
                        # TODO: Ajouter la méthode download_pdf dans drive_handler
                        if st.session_state.drive_handler.download_pdf(pdf['id'], str(temp_path)):
                            pdf_paths.append(str(temp_path))
                    
                    if pdf_paths:
                        st.session_state.rag_handler.process_pdfs(pdf_paths)
                        st.session_state.processed_pdfs = True
                        st.success("🎉 Base de connaissances créée!")
                        cleanup_temp_files()
                    else:
                        st.error("❌ Erreur lors du téléchargement des PDFs")
            
            # Bouton de suppression
            if selected_pdfs and col2.button("🗑️ Supprimer"):
                with st.spinner("Suppression..."):
                    for pdf in selected_pdfs:
                        if st.session_state.drive_handler.delete_pdf(pdf['id']):
                            st.success(f"✅ {pdf['name']} supprimé!")
                        else:
                            st.error(f"❌ Erreur lors de la suppression de {pdf['name']}")
                    # Rafraîchir la liste
                    st.session_state.pdf_files = st.session_state.drive_handler.list_public_pdfs()
        
        # Toggle pour RAG
        st.session_state.use_rag = st.toggle("🔍 Utiliser RAG", value=True)
        if st.session_state.use_rag:
            st.info("Mode RAG : Les réponses seront basées sur les documents uploadés")
        else:
            st.warning("Mode standard : Les réponses seront générées sans contexte")
        
        st.session_state.temperature = st.slider(
            "🌡️ Température",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="Contrôle la créativité du modèle"
        )

    # Zone de chat
    st.header("💬 Chat")
    
    # Affichage de l'historique
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Zone de saisie
    if prompt := st.chat_input("Posez votre question..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        if not st.session_state.processed_pdfs:
            with st.chat_message("assistant"):
                st.write("⚠️ Veuillez d'abord traiter des PDFs.")
        else:
            with st.chat_message("assistant"):
                with st.spinner("Réflexion en cours..."):
                    if st.session_state.use_rag:
                        response = st.session_state.rag_handler.get_response(
                            prompt,
                            [(msg["role"], msg["content"]) for msg in st.session_state.chat_history[:-1]]
                        )
                    else:
                        response = st.session_state.rag_handler.get_direct_response(prompt)
                    
                    if isinstance(response, dict):
                        st.write(response["answer"])
                        with st.expander("Sources"):
                            for source in response["sources"]:
                                st.write(f"📄 {source.get('source', 'Document inconnu')}")
                    else:
                        st.write(response)
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
